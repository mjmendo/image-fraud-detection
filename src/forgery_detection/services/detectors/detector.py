class Detector:
    """
    Base class for all detectors.
    """

    def analyze(self, image_bytes: bytes) -> float:
        """
        Analyze the image and return a score indicating likelihood of forgery.

        Args:
            image_bytes: Raw image data

        Returns:
            Suspicion score 0.0-1.0 (0.0=authentic, 1.0=highly suspicious)
        """
        raise NotImplementedError("Subclasses must implement this method.")
