from forgery_detection.config_loader import get_config


class ScoreAggregator:
    """
    Service for aggregating technique scores into final suspicion score.

    Weights:
    - metadata: 0.25
    - reverse_search: 0.30 if match found, 0.0 otherwise
    - ela: 0.20 (JPEG only)
    - statistical: 0.10
    - copy_move: 0.10
    - noise_variance: 0.05
    """

    def __init__(self):
        """Load weights from config."""
        config = get_config()
        self.weights = {
            "metadata": config.get_float("score_aggregator.default_weights.metadata", 0.25),
            "reverse_search": config.get_float("score_aggregator.default_weights.reverse_search", 0.30),
            "ela": config.get_float("score_aggregator.default_weights.ela", 0.20),
            "statistical": config.get_float("score_aggregator.default_weights.statistical", 0.10),
            "copy_move": config.get_float("score_aggregator.default_weights.copy_move", 0.10),
            "noise_variance": config.get_float("score_aggregator.default_weights.noise_variance", 0.05),
        }

    def aggregate(self, technique_scores: dict[str, float], format_type: str) -> float:
        """
        Aggregate technique scores into final score.

        Args:
            technique_scores: Dict of {technique_name: score}
            format_type: Image format (affects ELA availability)

        Returns:
            Final suspicion score 0.0-1.0
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for technique, score in technique_scores.items():
            if technique == "ela" and format_type != "jpeg":
                # ELA not applicable to non-JPEG formats
                continue

            if technique == "reverse_search" and score == 0.0:
                # No match found - don't include in weighting
                continue

            weight = self.weights.get(technique, 0.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0.0:
            return 0.0

        # Normalize by actual total weight used
        final_score = weighted_sum / total_weight
        return min(max(final_score, 0.0), 1.0)  # Clamp to [0, 1]
