"""Tests for FormatDetector service."""

from forgery_detection.services.format_detector import FormatDetector


class TestFormatDetector:
    """Test cases for FormatDetector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = FormatDetector()

    def test_detect_jpeg(self):
        """Test JPEG format detection."""
        jpeg_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"
        assert self.detector.detect(jpeg_bytes) == "jpeg"

    def test_detect_png(self):
        """Test PNG format detection."""
        png_bytes = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
        assert self.detector.detect(png_bytes) == "png"

    def test_detect_bmp(self):
        """Test BMP format detection."""
        bmp_bytes = b"\x42\x4D\x00\x00\x00\x00"
        assert self.detector.detect(bmp_bytes) == "bmp"

    def test_detect_tiff_little_endian(self):
        """Test TIFF format detection (little-endian)."""
        tiff_bytes = b"\x49\x49\x2A\x00"
        assert self.detector.detect(tiff_bytes) == "tiff"

    def test_detect_tiff_big_endian(self):
        """Test TIFF format detection (big-endian)."""
        tiff_bytes = b"\x4D\x4D\x00\x2A"
        assert self.detector.detect(tiff_bytes) == "tiff"

    def test_detect_unknown_format(self):
        """Test unknown format returns None."""
        unknown_bytes = b"\x00\x00\x00\x00"
        assert self.detector.detect(unknown_bytes) is None

    def test_detect_empty_bytes(self):
        """Test empty bytes returns None."""
        assert self.detector.detect(b"") is None

    def test_detect_insufficient_bytes(self):
        """Test insufficient bytes returns None."""
        assert self.detector.detect(b"\xFF") is None
