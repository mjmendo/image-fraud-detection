"""Tests for Classifier service."""

from forgery_detection.services.classifier import Classifier


class TestClassifier:
    """Test cases for Classifier."""

    def setup_method(self):
        """Setup test fixtures."""
        self.classifier = Classifier()

    def test_classify_strict_mode_forged(self):
        """Test strict mode classifies high score as forged."""
        assert self.classifier.classify(0.8, "strict") == "forged"

    def test_classify_strict_mode_authentic(self):
        """Test strict mode classifies medium score as authentic."""
        assert self.classifier.classify(0.6, "strict") == "authentic"

    def test_classify_balanced_mode_forged(self):
        """Test balanced mode classifies medium-high score as forged."""
        assert self.classifier.classify(0.6, "balanced") == "forged"

    def test_classify_balanced_mode_authentic(self):
        """Test balanced mode classifies low score as authentic."""
        assert self.classifier.classify(0.3, "balanced") == "authentic"

    def test_classify_aggressive_mode_forged(self):
        """Test aggressive mode classifies low-medium score as forged."""
        assert self.classifier.classify(0.4, "aggressive") == "forged"

    def test_classify_aggressive_mode_authentic(self):
        """Test aggressive mode classifies very low score as authentic."""
        assert self.classifier.classify(0.2, "aggressive") == "authentic"

    def test_classify_boundary_strict(self):
        """Test boundary case for strict mode (exactly 0.7)."""
        assert self.classifier.classify(0.7, "strict") == "forged"
        assert self.classifier.classify(0.69, "strict") == "authentic"

    def test_classify_boundary_balanced(self):
        """Test boundary case for balanced mode (exactly 0.5)."""
        assert self.classifier.classify(0.5, "balanced") == "forged"
        assert self.classifier.classify(0.49, "balanced") == "authentic"

    def test_classify_boundary_aggressive(self):
        """Test boundary case for aggressive mode (exactly 0.3)."""
        assert self.classifier.classify(0.3, "aggressive") == "forged"
        assert self.classifier.classify(0.29, "aggressive") == "authentic"

    def test_get_threshold(self):
        """Test getting threshold values."""
        assert self.classifier.get_threshold("strict") == 0.7
        assert self.classifier.get_threshold("balanced") == 0.5
        assert self.classifier.get_threshold("aggressive") == 0.3

    def test_classify_default_mode(self):
        """Test classify uses balanced mode as default."""
        assert self.classifier.classify(0.6) == "forged"  # Above 0.5
        assert self.classifier.classify(0.4) == "authentic"  # Below 0.5
