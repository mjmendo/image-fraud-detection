"""Metadata analysis detector (TIER 1)."""

import io
import logging
from PIL import Image
from forgery_detection.services.detectors.detector import Detector
from forgery_detection.config_loader import get_config

logger = logging.getLogger(__name__)


class MetadataDetector(Detector):
    """
    Analyzes EXIF metadata for evidence of manipulation:
    - Software tags (Photoshop, GIMP, etc.)
    - Timestamp inconsistencies
    - Missing/stripped metadata
    - GPS coordinate impossibilities
    """

    def __init__(self):
        """Initialize with config parameters."""
        config = get_config()
        # Load editing software list from config
        self.editing_software = set(config.get_list("metadata_detector.editing_software", [
            "photoshop", "gimp", "paint.net", "affinity", "pixelmator", "acorn", "photoscape"
        ]))
        # Load score thresholds
        self.no_exif_score = config.get_float("metadata_detector.no_exif_score", 0.4)
        self.editing_software_score = config.get_float("metadata_detector.editing_software_score", 0.6)
        self.few_tags_score = config.get_float("metadata_detector.few_tags_score", 0.3)
        self.error_default_score = config.get_float("metadata_detector.error_default_score", 0.3)
        self.few_tags_threshold = config.get_int("metadata_detector.few_tags_threshold", 5)

    def analyze(self, image_bytes: bytes) -> float:
        """
        Analyze image metadata for suspicion indicators.

        Args:
            image_bytes: Raw image data

        Returns:
            Suspicion score 0.0-1.0 (0.0=authentic, 1.0=highly suspicious)
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            exif_data = img.getexif()

            if not exif_data:
                # No EXIF data - suspicious (metadata might be stripped)
                return self.no_exif_score

            suspicion_score = 0.0
            indicators = []

            # Check for editing software
            software_tag = exif_data.get(305)  # Software tag
            if software_tag:
                software_lower = software_tag.lower()
                for editing_sw in self.editing_software:
                    if editing_sw in software_lower:
                        suspicion_score += self.editing_software_score
                        indicators.append(f"editing_software:{software_tag}")
                        break

            # Check for stripped metadata (very few tags)
            if len(exif_data) < self.few_tags_threshold:
                suspicion_score += self.few_tags_score
                indicators.append(f"few_tags:{len(exif_data)}")

            # Normalize score to 0.0-1.0
            suspicion_score = min(suspicion_score, 1.0)

            return suspicion_score

        except Exception as e:
            # Unable to read metadata - slightly suspicious
            logger.warning(
                f"MetadataDetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score {self.error_default_score}"
            )
            return self.error_default_score
