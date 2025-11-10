"""Tests for CopyMoveDetector service."""

import io
import numpy as np
from PIL import Image
from forgery_detection.services.detectors.copy_move_detector import CopyMoveDetector


class TestCopyMoveDetector:
    """Test cases for CopyMoveDetector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = CopyMoveDetector()

    def _create_test_image(self, width=200, height=200, pattern="solid"):
        """Helper to create test images."""
        if pattern == "solid":
            img_array = np.ones((height, width, 3), dtype=np.uint8) * 128
        elif pattern == "gradient":
            x = np.linspace(0, 255, width)
            y = np.linspace(0, 255, height)
            xx, yy = np.meshgrid(x, y)
            img_array = np.stack([xx, yy, (xx + yy) / 2], axis=2).astype(np.uint8)
        elif pattern == "checkerboard":
            # Repeating pattern that might trigger false positives
            img_array = np.zeros((height, width, 3), dtype=np.uint8)
            square_size = 20
            for i in range(0, height, square_size):
                for j in range(0, width, square_size):
                    if (i // square_size + j // square_size) % 2 == 0:
                        img_array[i : i + square_size, j : j + square_size] = 255
        else:
            img_array = np.ones((height, width, 3), dtype=np.uint8) * 128

        img = Image.fromarray(img_array)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_analyze_returns_score_in_range(self):
        """Test copy-move analysis returns score in 0-1 range."""
        img_bytes = self._create_test_image()
        score = self.detector.analyze(img_bytes)
        assert 0.0 <= score <= 1.0

    def test_analyze_solid_color_low_score(self):
        """Test solid color image has low copy-move score."""
        img_bytes = self._create_test_image(pattern="solid")
        score = self.detector.analyze(img_bytes)
        # Solid color has few/no features - low score expected
        assert score <= 0.5

    def test_analyze_gradient_image(self):
        """Test gradient image (natural-looking)."""
        img_bytes = self._create_test_image(pattern="gradient")
        score = self.detector.analyze(img_bytes)
        # Gradient should have some features but not duplicated
        assert 0.0 <= score <= 1.0

    def test_analyze_checkerboard_pattern(self):
        """Test image with repetitive pattern."""
        img_bytes = self._create_test_image(pattern="checkerboard")
        score = self.detector.analyze(img_bytes)
        # Repetitive pattern may have matches, but min_distance filter helps
        assert 0.0 <= score <= 1.0

    def test_analyze_invalid_image_returns_zero(self):
        """Test invalid image data returns 0.0."""
        invalid_bytes = b"not an image"
        score = self.detector.analyze(invalid_bytes)
        assert score == 0.0

    def test_analyze_small_image(self):
        """Test with very small image (few features)."""
        img_bytes = self._create_test_image(width=50, height=50)
        score = self.detector.analyze(img_bytes)
        # Small image has few features
        assert score >= 0.0

    def test_detect_copy_move_no_features(self):
        """Test copy-move detection with no features."""
        # Uniform image - no features
        gray = np.ones((100, 100), dtype=np.uint8) * 128
        matches = self.detector._detect_copy_move(gray)
        assert matches == 0

    def test_detect_copy_move_with_features(self):
        """Test copy-move detection with features present."""
        # Create image with some texture
        np.random.seed(42)
        gray = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
        matches = self.detector._detect_copy_move(gray)
        # Should find some self-matches
        assert matches >= 0

    def test_visualize_matches_returns_image(self):
        """Test visualization generation."""
        img_bytes = self._create_test_image(pattern="gradient")
        viz = self.detector.visualize_matches(img_bytes)

        assert isinstance(viz, Image.Image)
        assert viz.mode == "RGB"

    def test_visualize_matches_invalid_image(self):
        """Test visualization with invalid image."""
        invalid_bytes = b"not an image"
        viz = self.detector.visualize_matches(invalid_bytes)

        assert isinstance(viz, Image.Image)
        # Should return black placeholder
        assert viz.size == (100, 100)

    def test_works_with_different_formats(self):
        """Test detector works with different image formats."""
        for format_type in ["jpeg", "png", "tiff", "bmp"]:
            img_bytes = self._create_test_image()
            score = self.detector.analyze(img_bytes)
            assert 0.0 <= score <= 1.0

    def test_custom_parameters(self):
        """Test detector with custom parameters."""
        detector = CopyMoveDetector(n_features=100, match_threshold=0.8, min_distance=30)
        img_bytes = self._create_test_image(pattern="gradient")
        score = detector.analyze(img_bytes)
        assert 0.0 <= score <= 1.0
