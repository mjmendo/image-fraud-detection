"""Reverse image search detector (TIER 1)."""

import io
import logging
from PIL import Image
import imagehash
from forgery_detection.services.detectors.detector import Detector

logger = logging.getLogger(__name__)


class ReverseSearchDetector(Detector):
    """
    TIER 1 Detector - Priority: HIGH - Weight: 30% (if match found)

    Generates perceptual hash for reverse image search:
    - Creates image "fingerprint" using pHash algorithm
    - Can be used to detect stock photos from internet
    - Can be used to detect duplicate claims (future database integration)

    NOTE: Web-based search (TinEye API) is optional/future enhancement.
    MVP only generates pHash for future use.
    """

    def analyze(self, image_bytes: bytes) -> float:
        """
        Generate perceptual hash for image.

        Args:
            image_bytes: Raw image data

        Returns:
            Suspicion score 0.0 (MVP: no search implemented)
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))

            # Generate perceptual hash (pHash algorithm)
            phash = imagehash.phash(img)
            phash_hex = str(phash)

            # MVP: No web search, no phash matching
            # Future: Could query TinEye API here and return 1.0 if match found
            suspicion_score = 0.0

            return suspicion_score

        except Exception as e:
            # Unable to generate hash
            logger.warning(
                f"ReverseSearchDetector failed to analyze image: {type(e).__name__}: {e}. "
                f"Returning default score 0.0"
            )
            return 0.0

    def compute_hash_distance(self, hash1: str, hash2: str) -> int:
        """
        Compute Hamming distance between two perceptual hashes.

        Useful for comparing images to detect duplicates.

        Args:
            hash1: First perceptual hash (hex string)
            hash2: Second perceptual hash (hex string)

        Returns:
            Hamming distance (0 = identical, higher = more different)
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return h1 - h2
        except Exception as e:
            logger.warning(
                f"ReverseSearchDetector failed to compute hash distance: {type(e).__name__}: {e}. "
                f"Returning large distance 999"
            )
            return 999  # Invalid hashes, return large distance
