"""Noise Variance analysis detector (TIER 3)."""

import io
import logging
import numpy as np
from PIL import Image
import cv2
from forgery_detection.services.detectors.detector import Detector
from forgery_detection.config_loader import get_config

logger = logging.getLogger(__name__)


class NoiseVarianceDetector(Detector):
    """
    Checks for inconsistent noise patterns across image regions.

    Algorithm:
    1. Divide image into regions
    2. Compute noise variance (std dev) for each region
    3. Check for outliers (significantly different noise levels)
    4. Spliced regions may have different noise characteristics

    Note:
    - NOT PRNU (Photo Response Non-Uniformity) - that requires reference images
    - Simple variance checks only
    - JPEG compression destroys much sensor noise

    Limitations:
    - Most effective on RAW/uncompressed formats
    - JPEG compression can mask noise patterns
    """

    def __init__(self, grid_size=None):
        """
        Initialize Noise Variance detector.

        Args:
            grid_size: Divide image into grid_size x grid_size regions (optional, uses config if None)
        """
        config = get_config()
        self.grid_size = grid_size if grid_size is not None else config.get_int("noise_variance_detector.grid_size", 4)
        # CV thresholds
        self.cv_high_threshold = config.get_float("noise_variance_detector.cv_thresholds.high_threshold", 0.5)
        self.cv_high_score = config.get_float("noise_variance_detector.cv_thresholds.high_score", 0.8)
        self.cv_medium_threshold = config.get_float("noise_variance_detector.cv_thresholds.medium_threshold", 0.3)
        self.cv_medium_score = config.get_float("noise_variance_detector.cv_thresholds.medium_score", 0.4)
        self.cv_low_score = config.get_float("noise_variance_detector.cv_thresholds.low_score", 0.0)
        # Z-score outlier detection
        self.zscore_threshold = config.get_float("noise_variance_detector.zscore.threshold", 2.5)
        self.zscore_score = config.get_float("noise_variance_detector.zscore.score", 0.6)
        # Error handling
        self.error_default_score = config.get_float("noise_variance_detector.error_default_score", 0.0)
        # Visualization
        self.colormap = getattr(cv2, f"COLORMAP_{config.get('noise_variance_detector.colormap', 'JET')}")

    def analyze(self, image_bytes: bytes) -> float:
        """
        Analyze image for inconsistent noise patterns.

        Args:
            image_bytes: Raw image data

        Returns:
            Suspicion score 0.0-1.0
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Convert to numpy array (float for precision)
            img_array = np.array(img, dtype=np.float32)

            # Calculate regional noise variance
            regional_variances = self._calculate_regional_noise(img_array)

            # Check for outliers
            suspicion_score = self._detect_noise_outliers(regional_variances)

            return suspicion_score

        except Exception as e:
            logger.warning(
                f"NoiseVarianceDetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score {self.error_default_score}"
            )
            return self.error_default_score

    def _calculate_regional_noise(self, img_array: np.ndarray) -> list:
        """
        Calculate noise variance for each region.

        Args:
            img_array: Image as numpy array (H x W x 3)

        Returns:
            List of noise variance values for each region
        """
        height, width = img_array.shape[:2]
        region_h = height // self.grid_size
        region_w = width // self.grid_size

        regional_variances = []

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Extract region
                region = img_array[
                    i * region_h : (i + 1) * region_h, j * region_w : (j + 1) * region_w
                ]

                # Estimate noise using standard deviation
                # (Simple approach: noise = local std deviation)
                noise_estimate = np.std(region)
                regional_variances.append(noise_estimate)

        return regional_variances

    def _detect_noise_outliers(self, variances: list) -> float:
        """
        Detect outlier regions with significantly different noise.

        Args:
            variances: List of noise variance values

        Returns:
            Suspicion score 0.0-1.0
        """
        if not variances or len(variances) < 2:
            return 0.0

        variances_array = np.array(variances)

        # Calculate statistics
        mean_variance = np.mean(variances_array)
        std_variance = np.std(variances_array)

        if std_variance == 0.0:
            # Uniform noise - not suspicious
            return 0.0

        # Calculate coefficient of variation (CV)
        # CV = std / mean
        # High CV indicates inconsistent noise
        cv = std_variance / (mean_variance + 1e-6)

        # Normalize CV to 0-1 score
        # Natural images: CV typically < 0.3
        # Manipulated: CV may be > 0.5
        if cv > self.cv_high_threshold:
            suspicion_score = self.cv_high_score
        elif cv > self.cv_medium_threshold:
            suspicion_score = self.cv_medium_score
        else:
            suspicion_score = self.cv_low_score

        # Also check for extreme outliers using z-score
        z_scores = np.abs((variances_array - mean_variance) / (std_variance + 1e-6))
        max_z_score = np.max(z_scores)

        # Z-score > threshold is suspicious (more than N standard deviations away)
        if max_z_score > self.zscore_threshold:
            suspicion_score = max(suspicion_score, self.zscore_score)

        return min(suspicion_score, 1.0)

    def visualize_noise_map(self, image_bytes: bytes) -> Image.Image:
        """
        Generate visualization of noise variance map (for debugging).

        Args:
            image_bytes: Raw image data

        Returns:
            PIL Image showing noise variance heatmap
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))

            if img.mode != "RGB":
                img = img.convert("RGB")

            img_array = np.array(img, dtype=np.float32)
            height, width = img_array.shape[:2]

            # Calculate regional noise
            region_h = height // self.grid_size
            region_w = width // self.grid_size

            # Create heatmap
            heatmap = np.zeros((height, width), dtype=np.float32)

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    region = img_array[
                        i * region_h : (i + 1) * region_h, j * region_w : (j + 1) * region_w
                    ]
                    noise = np.std(region)

                    # Fill heatmap region
                    heatmap[
                        i * region_h : (i + 1) * region_h, j * region_w : (j + 1) * region_w
                    ] = noise

            # Normalize and convert to color map
            heatmap_norm = (
                (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-6)
            ) * 255
            heatmap_color = cv2.applyColorMap(heatmap_norm.astype(np.uint8), self.colormap)

            # Convert BGR to RGB
            heatmap_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

            return Image.fromarray(heatmap_rgb)

        except Exception as e:
            logger.warning(
                f"NoiseVarianceDetector failed to generate noise map: {type(e).__name__}: {e}. "
                f"Returning black placeholder"
            )
            return Image.new("RGB", (100, 100), color=(0, 0, 0))
