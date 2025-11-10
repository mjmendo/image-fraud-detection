from forgery_detection.services.detectors.metadata_detector import MetadataDetector
from forgery_detection.services.detectors.reverse_search_detector import ReverseSearchDetector
from forgery_detection.services.detectors.ela_detector import ELADetector
from forgery_detection.services.detectors.statistical_detector import StatisticalDetector
from forgery_detection.services.detectors.copy_move_detector import CopyMoveDetector
from forgery_detection.services.detectors.noise_variance_detector import NoiseVarianceDetector
from forgery_detection.services.detectors.detector import Detector


class FileTypeRecipes:
    def __init__(self):
        self.detectors = self._load_detectors()

    def _load_detectors(self):
        return {
            "metadata": MetadataDetector(),  # High priority
            "reverse_search": ReverseSearchDetector(),  # High priority
            "ela": ELADetector(),  # JPEG only, High priority
            "statistical": StatisticalDetector(),  # Medium priority
            "copy_move": CopyMoveDetector(),  # Medium priority
            "noise_variance": NoiseVarianceDetector(),  # Low priority
        }

    def get_detectors_by_format(self, format_type: str) -> dict[str, Detector]:
        if format_type not in ["jpeg", "jpg"]:
            # Exclude ELA for non-JPEG formats
            detectors = {k: v for k, v in self.detectors.items() if k != "ela"}
            return detectors
        return self.detectors
