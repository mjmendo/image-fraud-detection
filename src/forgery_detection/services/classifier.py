"""Classification service for threshold-based decisions."""

from forgery_detection.config_loader import get_config


class Classifier:
    """
    Service for classifying images as forged or authentic based on threshold.

    Supports 3 detection modes with different thresholds:
    - strict: 0.7 (precision-focused, minimize false positives)
    - balanced: 0.5 (target 80% TPR / 20% FPR) [DEFAULT]
    - aggressive: 0.3 (recall-focused, catch more fakes)
    """

    def __init__(self):
        """Initialize with thresholds from config."""
        config = get_config()
        self.thresholds: dict[str, float] = {
            "strict": config.get_float("classifier.modes.strict.threshold", 0.7),
            "balanced": config.get_float("classifier.modes.balanced.threshold", 0.5),
            "aggressive": config.get_float("classifier.modes.aggressive.threshold", 0.3),
        }

    def classify(self, score: float, criteria: str = "balanced") -> str:
        """
        Classify image based on suspicion score and criteria.

        Args:
            score: Suspicion score 0.0-1.0
            criteria: Detection criteria (strict | balanced | aggressive)

        Returns:
            forged or authentic
        """
        threshold = self.thresholds.get(criteria, 0.5)
        return "forged" if score >= threshold else "authentic"

    def get_threshold(self, criteria: str) -> float:
        """Get threshold value for a criteria."""
        return self.thresholds.get(criteria, 0.5)
