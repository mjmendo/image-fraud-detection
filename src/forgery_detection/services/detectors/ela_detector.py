"""ELA (Error Level Analysis) detector (TIER 1)."""

import io
import logging
import numpy as np
from PIL import Image

from forgery_detection.services.detectors.detector import Detector
from forgery_detection.config_loader import get_config

logger = logging.getLogger(__name__)


class ELADetector(Detector):
    """
    Error Level Analysis (ELA) detects JPEG recompression artifacts.

    Algorithm:
    1. Resave JPEG at known quality (95%)
    2. Compute pixel-level differences between original and resaved
    3. Manipulated areas show different compression levels than authentic areas

    Known Limitations:
    - False positives in homogeneous areas (sky, walls)
    - False positives at high-contrast edges
    - Not reliable enough for legal purposes alone
    - Only works on JPEG format
    """

    def __init__(self):
        """Initialize with config parameters."""
        config = get_config()
        self.default_quality = config.get_int("ela_detector.default_quality", 95)
        self.scale_factor = config.get_int("ela_detector.scale_factor", 15)
        # Score calculation weights
        self.weight_mean = config.get_float("ela_detector.weights.mean", 0.3)
        self.weight_std = config.get_float("ela_detector.weights.std", 0.3)
        self.weight_variance = config.get_float("ela_detector.weights.variance", 0.4)
        # Normalization divisors
        self.mean_divisor = config.get_float("ela_detector.normalization.mean_divisor", 50.0)
        self.std_divisor = config.get_float("ela_detector.normalization.std_divisor", 40.0)
        self.variance_divisor = config.get_float("ela_detector.normalization.variance_divisor", 100.0)
        # Grid size
        self.grid_size = config.get_int("ela_detector.grid_size", 4)
        # Error handling
        self.error_default_score = config.get_float("ela_detector.error_default_score", 0.0)

    def analyze(self, image_bytes: bytes) -> float:
        """
        Perform Error Level Analysis on JPEG image.

        Note: ELA only works on JPEG format. For other formats, returns 0.0.

        Args:
            image_bytes: Raw image data

        Returns:
            Suspicion score 0.0-1.0
        """
        try:
            # Open original image
            original = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if original.mode != "RGB":
                original = original.convert("RGB")

            # Resave at known quality
            buffer = io.BytesIO()
            original.save(buffer, format="JPEG", quality=self.default_quality)
            buffer.seek(0)

            # Open resaved image
            resaved = Image.open(buffer)

            # Convert to numpy arrays
            original_array = np.array(original, dtype=np.float32)
            resaved_array = np.array(resaved, dtype=np.float32)

            # Compute absolute difference
            diff = np.abs(original_array - resaved_array)

            # Calculate ELA score based on difference patterns
            score = self._calculate_ela_score(diff)

            return score

        except Exception as e:
            # Unable to perform ELA
            logger.warning(
                f"ELADetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score {self.error_default_score}"
            )
            return self.error_default_score

    def _calculate_ela_score(self, diff: np.ndarray) -> float:
        """
        Calculate suspicion score from ELA difference map.

        High variance in differences suggests manipulation.
        Manipulated areas have different compression levels.

        Args:
            diff: Pixel-wise difference array (H x W x 3)

        Returns:
            Suspicion score 0.0-1.0
        """
        # Compute statistics of differences
        mean_diff = np.mean(diff)
        std_diff = np.std(diff)
        max_diff = np.max(diff)

        # Calculate variance across image regions
        # High variance suggests inconsistent compression (potential manipulation)
        height, width = diff.shape[:2]

        # Divide into grid of regions
        region_h = height // self.grid_size
        region_w = width // self.grid_size

        region_means = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                region = diff[i * region_h : (i + 1) * region_h, j * region_w : (j + 1) * region_w]
                region_means.append(np.mean(region))

        # Calculate variance across regions
        region_variance = np.var(region_means) if region_means else 0.0

        # Scoring heuristics (based on ELA research):
        # 1. High overall mean difference suggests editing
        # 2. High standard deviation suggests inconsistent compression
        # 3. High regional variance suggests localized manipulation

        # Normalize scores
        mean_score = min(mean_diff / self.mean_divisor, 1.0)
        std_score = min(std_diff / self.std_divisor, 1.0)
        variance_score = min(region_variance / self.variance_divisor, 1.0)

        # Weighted combination
        # Mean is less reliable (can be high in natural images)
        # Variance is more indicative of manipulation
        suspicion_score = (self.weight_mean * mean_score +
                          self.weight_std * std_score +
                          self.weight_variance * variance_score)

        return min(max(suspicion_score, 0.0), 1.0)

    def generate_ela_image(self, image_bytes: bytes, format_type: str) -> Image.Image:
        """
        Generate ELA visualization image (for debugging/analysis).

        Args:
            image_bytes: Raw image data
            format_type: Image format

        Returns:
            PIL Image showing ELA differences (scaled for visibility)
        """
        if format_type != "jpeg":
            # Return black image for non-JPEG
            return Image.new("RGB", (100, 100), color=(0, 0, 0))

        try:
            original = Image.open(io.BytesIO(image_bytes))

            if original.mode != "RGB":
                original = original.convert("RGB")

            buffer = io.BytesIO()
            original.save(buffer, format="JPEG", quality=self.default_quality)
            buffer.seek(0)
            resaved = Image.open(buffer)

            original_array = np.array(original, dtype=np.float32)
            resaved_array = np.array(resaved, dtype=np.float32)

            # Compute difference and scale for visibility
            diff = np.abs(original_array - resaved_array) * self.scale_factor
            diff = np.clip(diff, 0, 255).astype(np.uint8)

            return Image.fromarray(diff)

        except Exception as e:
            logger.warning(
                f"ELADetector failed to generate ELA image: {type(e).__name__}: {e}. "
                f"Returning black placeholder"
            )
            return Image.new("RGB", (100, 100), color=(0, 0, 0))
