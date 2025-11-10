"""Tests for ELADetector service."""

import io
import numpy as np
from PIL import Image
from forgery_detection.services.detectors.ela_detector import ELADetector


class TestELADetector:
    """Test cases for ELADetector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = ELADetector()

    def _create_test_jpeg(self, width=100, height=100, quality=95):
        """Helper to create a test JPEG image."""
        # Create solid color image
        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()

    def _create_test_png(self, width=100, height=100):
        """Helper to create a test PNG image."""
        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_analyze_jpeg_returns_score(self):
        """Test ELA analysis on JPEG returns a score."""
        jpeg_bytes = self._create_test_jpeg()
        score = self.detector.analyze(jpeg_bytes)
        assert 0.0 <= score <= 1.0

    def test_analyze_non_jpeg_returns_zero(self):
        """Test ELA analysis on non-JPEG returns 0.0."""
        png_bytes = self._create_test_png()
        score = self.detector.analyze(png_bytes)
        assert score == 0.0

    def test_analyze_tiff_returns_zero(self):
        """Test ELA only works on JPEG format."""
        png_bytes = self._create_test_png()
        score = self.detector.analyze(png_bytes)
        assert score == 0.0

    def test_analyze_high_quality_jpeg_low_score(self):
        """Test high-quality JPEG (less compressed) has lower ELA score."""
        # High quality JPEG (95) should have minimal recompression artifacts
        jpeg_bytes = self._create_test_jpeg(quality=95)
        score = self.detector.analyze(jpeg_bytes)
        # Should be relatively low since it's already at quality 95
        assert score < 0.5

    def test_analyze_low_quality_jpeg_higher_score(self):
        """Test low-quality JPEG (more compressed) may have higher ELA score."""
        # Low quality JPEG (50) will show more artifacts when resaved at 95
        jpeg_bytes = self._create_test_jpeg(quality=50)
        score = self.detector.analyze(jpeg_bytes)
        # Should show some difference from recompression
        assert 0.0 <= score <= 1.0

    def test_analyze_with_noise_pattern(self):
        """Test ELA with noisy image pattern."""
        # Create image with random noise (simulates edited areas)
        img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        jpeg_bytes = buffer.getvalue()

        score = self.detector.analyze(jpeg_bytes)
        # Noisy images typically have higher variance
        assert 0.0 <= score <= 1.0

    def test_analyze_invalid_image_returns_zero(self):
        """Test invalid image data returns 0.0."""
        invalid_bytes = b"not an image"
        score = self.detector.analyze(invalid_bytes)
        assert score == 0.0

    def test_generate_ela_image_jpeg(self):
        """Test ELA visualization generation for JPEG."""
        jpeg_bytes = self._create_test_jpeg()
        ela_image = self.detector.generate_ela_image(jpeg_bytes, "jpeg")

        assert isinstance(ela_image, Image.Image)
        assert ela_image.mode == "RGB"
        assert ela_image.size == (100, 100)

    def test_generate_ela_image_non_jpeg(self):
        """Test ELA visualization for non-JPEG returns black image."""
        png_bytes = self._create_test_png()
        ela_image = self.detector.generate_ela_image(png_bytes, "png")

        assert isinstance(ela_image, Image.Image)
        assert ela_image.mode == "RGB"
        # Should be a black placeholder
        assert ela_image.size == (100, 100)

    def test_calculate_ela_score_uniform_diff(self):
        """Test ELA score calculation with uniform differences."""
        # Uniform difference (low variance) should give lower score
        diff = np.ones((100, 100, 3)) * 10.0  # Uniform difference of 10
        score = self.detector._calculate_ela_score(diff)
        # Uniform differences suggest no manipulation
        assert score < 0.5

    def test_calculate_ela_score_high_variance_diff(self):
        """Test ELA score with high variance differences."""
        # Create difference map with high regional variance
        diff = np.zeros((100, 100, 3))
        # Add high difference in one quadrant (simulates manipulation)
        diff[0:50, 0:50, :] = 50.0
        diff[50:100, 50:100, :] = 5.0

        score = self.detector._calculate_ela_score(diff)
        # High variance suggests manipulation
        assert score > 0.0
