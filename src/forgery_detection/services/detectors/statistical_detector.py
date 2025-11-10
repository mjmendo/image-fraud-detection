"""Statistical analysis detector (TIER 2)."""

import io
import logging
import numpy as np
from PIL import Image
from forgery_detection.services.detectors.detector import Detector
from forgery_detection.config_loader import get_config

logger = logging.getLogger(__name__)


class StatisticalDetector(Detector):
    """
    Detects unnatural color/histogram patterns that suggest manipulation.

    Checks:
    - Histogram anomalies (unnatural color distributions)
    - Color channel correlation (R/G/B relationships)
    - Edge density differences (manipulated regions have different edge characteristics)
    """

    def __init__(self):
        """Initialize with config parameters."""
        config = get_config()
        # Component weights
        self.weight_histogram = config.get_float("statistical_detector.weights.histogram", 0.4)
        self.weight_correlation = config.get_float("statistical_detector.weights.correlation", 0.3)
        self.weight_edge = config.get_float("statistical_detector.weights.edge", 0.3)
        # Histogram anomaly detection
        self.gap_ratio_threshold = config.get_float("statistical_detector.histogram.gap_ratio_threshold", 0.3)
        self.gap_ratio_score = config.get_float("statistical_detector.histogram.gap_ratio_score", 0.2)
        self.max_peak_threshold = config.get_float("statistical_detector.histogram.max_peak_threshold", 0.1)
        self.max_peak_score = config.get_float("statistical_detector.histogram.max_peak_score", 0.2)
        self.num_channels = config.get_int("statistical_detector.histogram.num_channels", 3)
        # Color correlation thresholds
        self.very_suspicious_threshold = config.get_float("statistical_detector.correlation.very_suspicious_threshold", 0.5)
        self.very_suspicious_score = config.get_float("statistical_detector.correlation.very_suspicious_score", 0.8)
        self.somewhat_suspicious_threshold = config.get_float("statistical_detector.correlation.somewhat_suspicious_threshold", 0.7)
        self.somewhat_suspicious_score = config.get_float("statistical_detector.correlation.somewhat_suspicious_score", 0.4)
        # Edge density analysis
        self.edge_std_divisor = config.get_float("statistical_detector.edge.std_divisor", 50.0)
        self.edge_grid_size = config.get_int("statistical_detector.edge.grid_size", 3)
        # Error handling
        self.error_default_score = config.get_float("statistical_detector.error_default_score", 0.0)

    def analyze(self, image_bytes: bytes) -> float:
        """
        Analyze image for statistical anomalies.

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

            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)

            # Run statistical checks
            histogram_score = self._check_histogram_anomalies(img_array)
            correlation_score = self._check_color_correlation(img_array)
            edge_score = self._check_edge_density(img_array)

            # Weighted combination
            suspicion_score = (self.weight_histogram * histogram_score +
                             self.weight_correlation * correlation_score +
                             self.weight_edge * edge_score)

            return min(max(suspicion_score, 0.0), 1.0)

        except Exception as e:
            logger.warning(
                f"StatisticalDetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score {self.error_default_score}"
            )
            return self.error_default_score

    def _check_histogram_anomalies(self, img_array: np.ndarray) -> float:
        """
        Check for unnatural histogram patterns.

        Natural images have smooth, bell-curved histograms.
        Manipulated images may have gaps, spikes, or unnatural distributions.

        Args:
            img_array: Image as numpy array (H x W x 3)

        Returns:
            Suspicion score 0.0-1.0
        """
        suspicion = 0.0

        # Check each color channel
        for channel_idx in range(self.num_channels):
            channel = img_array[:, :, channel_idx].flatten()

            # Compute histogram
            hist, _ = np.histogram(channel, bins=256, range=(0, 256))

            # Check for gaps (missing intensity values)
            # Natural images rarely have large gaps
            zero_bins = np.sum(hist == 0)
            gap_ratio = zero_bins / 256.0

            if gap_ratio > self.gap_ratio_threshold:
                suspicion += self.gap_ratio_score

            # Check for spikes (unnatural peaks)
            # Normalize histogram
            hist_norm = hist / (np.sum(hist) + 1e-6)
            max_peak = np.max(hist_norm)

            if max_peak > self.max_peak_threshold:
                suspicion += self.max_peak_score

        # Normalize across channels
        return min(suspicion / self.num_channels, 1.0)

    def _check_color_correlation(self, img_array: np.ndarray) -> float:
        """
        Check for unnatural color channel relationships.

        Natural images have strong correlation between R, G, B channels.
        Manipulation (especially copy-paste) can disrupt this correlation.

        Args:
            img_array: Image as numpy array (H x W x 3)

        Returns:
            Suspicion score 0.0-1.0
        """
        # Flatten channels
        r = img_array[:, :, 0].flatten()
        g = img_array[:, :, 1].flatten()
        b = img_array[:, :, 2].flatten()

        # Compute correlations
        corr_rg = np.corrcoef(r, g)[0, 1]
        corr_rb = np.corrcoef(r, b)[0, 1]
        corr_gb = np.corrcoef(g, b)[0, 1]

        # Natural images typically have correlation > 0.7
        # Low correlation suggests manipulation
        avg_corr = (corr_rg + corr_rb + corr_gb) / 3.0

        if avg_corr < self.very_suspicious_threshold:
            return self.very_suspicious_score  # Very suspicious
        elif avg_corr < self.somewhat_suspicious_threshold:
            return self.somewhat_suspicious_score  # Somewhat suspicious
        else:
            return 0.0  # Normal correlation

    def _check_edge_density(self, img_array: np.ndarray) -> float:
        """
        Check for inconsistent edge density across regions.

        Manipulated regions often have different edge characteristics
        than the rest of the image.

        Args:
            img_array: Image as numpy array (H x W x 3)

        Returns:
            Suspicion score 0.0-1.0
        """
        # Convert to grayscale
        gray = np.mean(img_array, axis=2)

        # Simple edge detection using gradient
        grad_x = np.abs(np.diff(gray, axis=1))
        grad_y = np.abs(np.diff(gray, axis=0))

        # Pad to match original dimensions
        grad_x = np.pad(grad_x, ((0, 0), (0, 1)), mode="edge")
        grad_y = np.pad(grad_y, ((0, 1), (0, 0)), mode="edge")

        # Compute edge magnitude
        edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Divide image into regions and check edge density variance
        height, width = edge_magnitude.shape
        region_h = height // self.edge_grid_size
        region_w = width // self.edge_grid_size

        edge_densities = []
        for i in range(self.edge_grid_size):
            for j in range(self.edge_grid_size):
                region = edge_magnitude[
                    i * region_h : (i + 1) * region_h, j * region_w : (j + 1) * region_w
                ]
                density = np.mean(region)
                edge_densities.append(density)

        # High variance in edge density suggests manipulation
        edge_variance = np.var(edge_densities)
        edge_std = np.std(edge_densities)

        # Normalize (typical variance: 10-100 for natural images)
        suspicion_score = min(edge_std / self.edge_std_divisor, 1.0)

        return suspicion_score
