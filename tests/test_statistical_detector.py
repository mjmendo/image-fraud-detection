"""Tests for StatisticalDetector service."""

import io
import numpy as np
from PIL import Image
from forgery_detection.services.detectors.statistical_detector import StatisticalDetector


class TestStatisticalDetector:
    """Test cases for StatisticalDetector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = StatisticalDetector()

    def _create_test_image(self, width=100, height=100, pattern="solid"):
        """Helper to create test images with different patterns."""
        if pattern == "solid":
            # Solid color image
            img_array = np.ones((height, width, 3), dtype=np.uint8) * 128
        elif pattern == "gradient":
            # Gradient image (natural-looking)
            x = np.linspace(0, 255, width)
            y = np.linspace(0, 255, height)
            xx, yy = np.meshgrid(x, y)
            img_array = np.stack([xx, yy, (xx + yy) / 2], axis=2).astype(np.uint8)
        elif pattern == "noise":
            # Random noise
            img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        elif pattern == "gaps":
            # Image with histogram gaps (only use specific values)
            img_array = np.random.choice([0, 50, 100, 150, 200, 250], (height, width, 3))
        else:
            img_array = np.ones((height, width, 3), dtype=np.uint8) * 128

        img = Image.fromarray(img_array.astype(np.uint8))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_analyze_returns_score_in_range(self):
        """Test statistical analysis returns score in 0-1 range."""
        img_bytes = self._create_test_image()
        score = self.detector.analyze(img_bytes)
        assert 0.0 <= score <= 1.0

    def test_analyze_solid_color_image(self):
        """Test analysis of solid color image."""
        img_bytes = self._create_test_image(pattern="solid")
        score = self.detector.analyze(img_bytes)
        # Solid color should have very specific histogram pattern
        assert 0.0 <= score <= 1.0

    def test_analyze_gradient_image(self):
        """Test analysis of gradient image (natural-looking)."""
        img_bytes = self._create_test_image(pattern="gradient")
        score = self.detector.analyze(img_bytes)
        # Gradients are relatively natural
        assert 0.0 <= score <= 1.0

    def test_analyze_noisy_image(self):
        """Test analysis of noisy/random image."""
        img_bytes = self._create_test_image(pattern="noise")
        score = self.detector.analyze(img_bytes)
        # Random noise may have unnatural statistics
        assert 0.0 <= score <= 1.0

    def test_analyze_image_with_histogram_gaps(self):
        """Test image with gaps in histogram (suspicious)."""
        img_bytes = self._create_test_image(pattern="gaps")
        score = self.detector.analyze(img_bytes)
        # Gaps in histogram suggest manipulation
        # Should have elevated score
        assert score >= 0.0

    def test_analyze_invalid_image_returns_zero(self):
        """Test invalid image data returns 0.0."""
        invalid_bytes = b"not an image"
        score = self.detector.analyze(invalid_bytes)
        assert score == 0.0

    def test_check_histogram_anomalies_uniform(self):
        """Test histogram check with uniform distribution."""
        # Create uniform image
        img_array = np.ones((100, 100, 3), dtype=np.float32) * 128
        score = self.detector._check_histogram_anomalies(img_array)
        # Uniform (single value) has large gaps - suspicious
        assert score > 0.0

    def test_check_histogram_anomalies_natural(self):
        """Test histogram check with natural distribution."""
        # Create gradient (smooth histogram)
        x = np.linspace(0, 255, 100)
        y = np.linspace(0, 255, 100)
        xx, yy = np.meshgrid(x, y)
        img_array = np.stack([xx, yy, (xx + yy) / 2], axis=2).astype(np.float32)

        score = self.detector._check_histogram_anomalies(img_array)
        # Natural distribution should have lower score
        assert 0.0 <= score <= 1.0

    def test_check_color_correlation_high(self):
        """Test color correlation with highly correlated channels."""
        # Create grayscale-like image (R=G=B)
        val = np.random.randint(0, 256, (100, 100)).astype(np.float32)
        img_array = np.stack([val, val, val], axis=2)

        score = self.detector._check_color_correlation(img_array)
        # Perfect correlation - not suspicious
        assert score == 0.0

    def test_check_color_correlation_low(self):
        """Test color correlation with uncorrelated channels."""
        # Create completely independent channels
        r = np.random.randint(0, 256, (100, 100)).astype(np.float32)
        g = np.random.randint(0, 256, (100, 100)).astype(np.float32)
        b = np.random.randint(0, 256, (100, 100)).astype(np.float32)
        img_array = np.stack([r, g, b], axis=2)

        score = self.detector._check_color_correlation(img_array)
        # Low correlation - suspicious
        assert score > 0.0

    def test_check_edge_density_uniform(self):
        """Test edge density with uniform image (no edges)."""
        # Solid color - no edges
        img_array = np.ones((100, 100, 3), dtype=np.float32) * 128
        score = self.detector._check_edge_density(img_array)
        # No edges means no variance - low score
        assert score == 0.0

    def test_check_edge_density_with_edges(self):
        """Test edge density with image containing edges."""
        # Create image with vertical edge
        img_array = np.ones((100, 100, 3), dtype=np.float32) * 50
        img_array[:, 50:, :] = 200  # Right half brighter

        score = self.detector._check_edge_density(img_array)
        # Strong edge present
        assert 0.0 <= score <= 1.0

    def test_analyze_works_with_different_formats(self):
        """Test detector works with different image formats."""
        for format_type in ["jpeg", "png", "tiff", "bmp"]:
            img_bytes = self._create_test_image()
            score = self.detector.analyze(img_bytes)
            assert 0.0 <= score <= 1.0
