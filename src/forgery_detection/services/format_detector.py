"""Format detection service for identifying image formats."""

from typing import Optional


class FormatDetector:
    """
    Service for detecting image format from magic bytes.

    Supports: JPEG, PNG, BMP, TIFF
    """

    # Magic byte signatures
    MAGIC_BYTES = {
        "jpeg": [b"\xFF\xD8\xFF"],
        "png": [b"\x89\x50\x4E\x47"],
        "bmp": [b"\x42\x4D"],
        "tiff": [b"\x49\x49\x2A\x00", b"\x4D\x4D\x00\x2A"],  # Little-endian, Big-endian
    }

    def detect(self, image_bytes: bytes) -> Optional[str]:
        """
        Detect image format from magic bytes.

        Args:
            image_bytes: Raw image data

        Returns:
            Format string: "jpeg" | "png" | "bmp" | "tiff" | None
        """
        if not image_bytes or len(image_bytes) < 4:
            return None

        # Check each format's magic bytes
        for format_name, signatures in self.MAGIC_BYTES.items():
            for signature in signatures:
                if image_bytes.startswith(signature):
                    return format_name

        return None
