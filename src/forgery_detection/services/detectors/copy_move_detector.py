"""Copy-Move detection detector (TIER 2)."""

import io
import logging
import numpy as np
from PIL import Image
import cv2

from forgery_detection.services.detectors.detector import Detector
from forgery_detection.config_loader import get_config

logger = logging.getLogger(__name__)


class CopyMoveDetector(Detector):
    """
    Detects duplicated regions within the same image (copy-move forgery).

    Algorithm:
    1. Convert to grayscale
    2. Detect keypoints using ORB (Oriented FAST and Rotated BRIEF)
    3. Match similar keypoints
    4. Filter for spatially separated matches (copy-move)
    5. Score based on number of suspicious matches

    Advantages:
    - Works BETTER on uncompressed formats (TIFF/BMP)
    - Detects damage duplication and object removal

    Limitations:
    - Struggles with repetitive patterns (grids, bricks)
    - Computationally expensive for large images
    """

    def __init__(self, n_features=None, match_threshold=None, min_distance=None):
        """
        Initialize Copy-Move detector.

        Args:
            n_features: Number of ORB features to detect (optional, uses config if None)
            match_threshold: Ratio test threshold for good matches (optional, uses config if None)
            min_distance: Minimum pixel distance for copy-move (optional, uses config if None)
        """
        config = get_config()
        self.n_features = n_features if n_features is not None else config.get_int("copy_move_detector.n_features", 500)
        self.match_threshold = match_threshold if match_threshold is not None else config.get_float("copy_move_detector.match_threshold", 0.75)
        self.min_distance = min_distance if min_distance is not None else config.get_int("copy_move_detector.min_distance", 50)
        self.suspicious_matches_divisor = config.get_float("copy_move_detector.suspicious_matches_divisor", 20.0)
        self.max_visualized_matches = config.get_int("copy_move_detector.max_visualized_matches", 20)
        self.error_default_score = config.get_float("copy_move_detector.error_default_score", 0.0)

    def analyze(self, image_bytes: bytes) -> float:
        """
        Analyze image for copy-move forgery.

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
            img_array = np.array(img)

            # Convert to grayscale for feature detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # Detect copy-move regions
            suspicious_matches = self._detect_copy_move(gray)

            # Calculate suspicion score
            # More matches = higher suspicion
            # Normalize: 0 matches = 0.0, divisor+ matches = 1.0
            suspicion_score = min(suspicious_matches / self.suspicious_matches_divisor, 1.0)

            return suspicion_score

        except Exception as e:
            # Unable to perform copy-move detection
            logger.warning(
                f"CopyMoveDetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score {self.error_default_score}"
            )
            return self.error_default_score

    def _detect_copy_move(self, gray: np.ndarray) -> int:
        """
        Detect copy-move regions using ORB feature matching.

        Args:
            gray: Grayscale image array

        Returns:
            Number of suspicious copy-move matches
        """
        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=self.n_features)

        # Detect keypoints and compute descriptors
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        if descriptors is None or len(keypoints) < 2:
            return 0

        # Match descriptors with itself using BFMatcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        # Find matches
        try:
            matches = bf.knnMatch(descriptors, descriptors, k=2)
        except Exception:
            return 0

        # Apply ratio test (Lowe's ratio test)
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                # Skip self-matches (distance = 0)
                if m.distance > 0 and m.distance < self.match_threshold * n.distance:
                    good_matches.append(m)

        # Filter for spatially separated matches (copy-move, not repetitive pattern)
        suspicious_matches = 0
        for match in good_matches:
            pt1 = keypoints[match.queryIdx].pt
            pt2 = keypoints[match.trainIdx].pt

            # Calculate Euclidean distance
            distance = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

            # If points are far apart, it's suspicious (copy-move)
            # If points are very close, it might be natural repetitive pattern
            if distance > self.min_distance:
                suspicious_matches += 1

        return suspicious_matches

    def visualize_matches(self, image_bytes: bytes) -> Image.Image:
        """
        Generate visualization of copy-move matches (for debugging).

        Args:
            image_bytes: Raw image data

        Returns:
            PIL Image with matches drawn
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))

            if img.mode != "RGB":
                img = img.convert("RGB")

            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # Detect features and matches
            orb = cv2.ORB_create(nfeatures=self.n_features)
            keypoints, descriptors = orb.detectAndCompute(gray, None)

            if descriptors is None:
                return img

            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(descriptors, descriptors, k=2)

            # Filter matches
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance > 0 and m.distance < self.match_threshold * n.distance:
                        pt1 = keypoints[m.queryIdx].pt
                        pt2 = keypoints[m.trainIdx].pt
                        distance = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
                        if distance > self.min_distance:
                            good_matches.append(m)

            # Draw matches on image
            result = img_array.copy()
            for match in good_matches[:self.max_visualized_matches]:  # Limit for visibility
                pt1 = tuple(map(int, keypoints[match.queryIdx].pt))
                pt2 = tuple(map(int, keypoints[match.trainIdx].pt))
                cv2.line(result, pt1, pt2, (255, 0, 0), 2)
                cv2.circle(result, pt1, 5, (0, 255, 0), -1)
                cv2.circle(result, pt2, 5, (0, 0, 255), -1)

            return Image.fromarray(result)

        except Exception as e:
            logger.warning(
                f"CopyMoveDetector failed to visualize matches: {type(e).__name__}: {e}. "
                f"Returning black placeholder"
            )
            return Image.new("RGB", (100, 100), color=(0, 0, 0))
