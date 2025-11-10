"""Image loading service for reading images from directories."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageLoader:
    """
    Service for loading images from labeled directories.
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    def load_labeled_images(
        self, forged_dir: str, authentic_dir: str
    ) -> list[tuple[str, bytes, str]]:
        """
        Load images from labeled directories.

        Args:
            forged_dir: Directory containing forged images
            authentic_dir: Directory containing authentic images

        Returns:
            List of tuples: (image_path, image_bytes, label)
            where label is "forged" or "authentic"
        """
        images = []

        # Load forged images
        forged_path = Path(forged_dir)
        if forged_path.exists():
            forged_count = 0
            for file_path in forged_path.iterdir():
                if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    images.append((str(file_path), image_bytes, "forged"))
                    forged_count += 1
            logger.debug(f"Loaded {forged_count} forged images from {forged_dir}")
        else:
            logger.warning(f"Forged directory does not exist: {forged_dir}")

        # Load authentic images
        authentic_path = Path(authentic_dir)
        if authentic_path.exists():
            authentic_count = 0
            for file_path in authentic_path.iterdir():
                if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    images.append((str(file_path), image_bytes, "authentic"))
                    authentic_count += 1
            logger.debug(f"Loaded {authentic_count} authentic images from {authentic_dir}")
        else:
            logger.warning(f"Authentic directory does not exist: {authentic_dir}")

        return images
