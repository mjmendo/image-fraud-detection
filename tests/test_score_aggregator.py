"""Tests for ScoreAggregator service."""

from forgery_detection.services.score_aggregator import ScoreAggregator


class TestScoreAggregator:
    """Test cases for ScoreAggregator."""

    def setup_method(self):
        """Setup test fixtures."""
        self.aggregator = ScoreAggregator()

    def test_aggregate_all_techniques(self):
        """Test aggregating scores from all techniques."""
        scores = {
            "metadata": 0.5,
            "reverse_search": 0.8,  # Match found
            "ela": 0.6,
            "statistical": 0.4,
            "copy_move": 0.3,
            "noise_variance": 0.2,
        }
        result = self.aggregator.aggregate(scores, "jpeg")
        assert 0.0 <= result <= 1.0
        # Weighted average should be around 0.54
        assert 0.50 < result < 0.60

    def test_aggregate_no_reverse_search_match(self):
        """Test aggregating when reverse search finds no match."""
        scores = {
            "metadata": 0.5,
            "reverse_search": 0.0,  # No match
            "ela": 0.6,
        }
        result = self.aggregator.aggregate(scores, "jpeg")
        # Should not include reverse_search in weighting when score is 0
        assert 0.0 <= result <= 1.0

    def test_aggregate_non_jpeg_skips_ela(self):
        """Test that ELA is skipped for non-JPEG formats."""
        scores = {
            "metadata": 0.5,
            "ela": 0.9,  # Should be ignored for TIFF
            "statistical": 0.4,
        }
        result_tiff = self.aggregator.aggregate(scores, "tiff")
        result_jpeg = self.aggregator.aggregate(scores, "jpeg")
        # TIFF should skip ELA, JPEG should include it
        assert result_tiff < result_jpeg

    def test_aggregate_single_technique(self):
        """Test aggregating single technique score."""
        scores = {"metadata": 0.7}
        result = self.aggregator.aggregate(scores, "jpeg")
        # With only one technique, result should equal input
        assert result == 0.7

    def test_aggregate_empty_scores(self):
        """Test aggregating empty scores returns 0.0."""
        result = self.aggregator.aggregate({}, "jpeg")
        assert result == 0.0

    def test_aggregate_clamping(self):
        """Test that result is clamped to [0, 1]."""
        scores = {"metadata": 1.5}  # Over 1.0
        result = self.aggregator.aggregate(scores, "jpeg")
        assert result <= 1.0

        scores = {"metadata": -0.5}  # Below 0.0
        result = self.aggregator.aggregate(scores, "jpeg")
        assert result >= 0.0
