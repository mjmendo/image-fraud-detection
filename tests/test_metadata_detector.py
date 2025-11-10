"""Tests for MetadataDetector service."""

import io
from PIL import Image
from forgery_detection.services.detectors.metadata_detector import MetadataDetector


class TestMetadataDetector:
    """Test cases for MetadataDetector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = MetadataDetector()

    def _create_test_image_with_exif(self, exif_data: dict = None, format="JPEG"):
        """
        Helper to create a test image with specific EXIF data.

        Args:
            exif_data: Dictionary of EXIF tag values (e.g., {305: "Photoshop"})
            format: Image format (JPEG, PNG, etc.)

        Returns:
            bytes: Image data with EXIF
        """
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        buffer = io.BytesIO()

        if exif_data and format == "JPEG":
            # Create EXIF data
            exif = Image.Exif()
            for tag, value in exif_data.items():
                exif[tag] = value
            img.save(buffer, format=format, exif=exif, quality=95)
        else:
            img.save(buffer, format=format, quality=95 if format == "JPEG" else None)

        return buffer.getvalue()

    # Test: No EXIF Data
    def test_analyze_no_exif_returns_suspicious_score(self):
        """Test image with no EXIF data returns 0.4 (suspicious)."""
        # PNG typically has no EXIF
        image_bytes = self._create_test_image_with_exif(format="PNG")
        score = self.detector.analyze(image_bytes)
        assert score == 0.4

    def test_analyze_jpeg_no_exif_returns_suspicious_score(self):
        """Test JPEG with stripped EXIF returns 0.4."""
        image_bytes = self._create_test_image_with_exif(exif_data={}, format="JPEG")
        score = self.detector.analyze(image_bytes)
        assert score == 0.4

    # Test: Editing Software Detection
    def test_analyze_photoshop_in_software_tag(self):
        """Test detection of Photoshop in software tag."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={305: "Adobe Photoshop CS6"}
        )
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6  # Should flag editing software

    def test_analyze_gimp_in_software_tag(self):
        """Test detection of GIMP in software tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={305: "GIMP 2.10.32"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_paint_net_in_software_tag(self):
        """Test detection of Paint.NET in software tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={305: "Paint.NET v4.2"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_affinity_in_software_tag(self):
        """Test detection of Affinity Photo in software tag."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={305: "Affinity Photo 2.0"}
        )
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_pixelmator_in_software_tag(self):
        """Test detection of Pixelmator in software tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={305: "Pixelmator Pro"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_acorn_in_software_tag(self):
        """Test detection of Acorn in software tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={305: "Acorn 7.2"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_photoscape_in_software_tag(self):
        """Test detection of Photoscape in software tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={305: "PhotoScape X"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_case_insensitive_software_detection(self):
        """Test software detection is case-insensitive."""
        # Test uppercase
        image_bytes = self._create_test_image_with_exif(exif_data={305: "PHOTOSHOP"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

        # Test mixed case
        image_bytes = self._create_test_image_with_exif(exif_data={305: "PhOtOsHoP"})
        score = self.detector.analyze(image_bytes)
        assert score >= 0.6

    def test_analyze_benign_software_not_flagged(self):
        """Test benign camera software not flagged."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                305: "Canon EOS Utility",  # Camera software
                271: "Canon",  # Make
                272: "Canon EOS 5D Mark IV",  # Model
                306: "2024:01:15 10:30:00",  # DateTime
                274: 1,  # Orientation
                282: 72.0,  # XResolution
                283: 72.0,  # YResolution
            }
        )
        score = self.detector.analyze(image_bytes)
        # Should not flag camera software, but has 7 tags so no "few tags" penalty
        assert score == 0.0

    # Test: Few EXIF Tags
    def test_analyze_few_exif_tags_suspicious(self):
        """Test images with <5 EXIF tags are suspicious."""
        # Only 4 tags (below threshold of 5)
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Canon",  # Make
                272: "Canon EOS",  # Model
                274: 1,  # Orientation
                306: "2024:01:15 10:30:00",  # DateTime
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.3  # Should add 0.3 for few tags

    def test_analyze_exactly_five_tags_not_flagged(self):
        """Test images with exactly 5 tags not flagged as few."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Canon",
                272: "Canon EOS",
                274: 1,
                306: "2024:01:15 10:30:00",
                305: "Camera Firmware",
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.0  # 5 tags is not "few"

    def test_analyze_many_exif_tags_not_suspicious(self):
        """Test images with many EXIF tags are not suspicious."""
        # Rich EXIF data (typical of unedited camera photo)
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Canon",  # Make
                272: "Canon EOS 5D",  # Model
                274: 1,  # Orientation
                306: "2024:01:15 10:30:00",  # DateTime
                305: "Firmware 1.0",  # Software
                282: 72.0,  # XResolution
                283: 72.0,  # YResolution
                296: 2,  # ResolutionUnit
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.0  # Rich metadata, no editing software

    # Test: Combined Indicators
    def test_analyze_editing_software_and_few_tags(self):
        """Test combined indicators: editing software + few tags."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                305: "Adobe Photoshop",  # Editing software (+0.6)
                271: "Canon",
                272: "Canon EOS",
            }  # Only 3 tags (+0.3)
        )
        score = self.detector.analyze(image_bytes)
        # Should be 0.6 (software) + 0.3 (few tags) = 0.9
        assert abs(score - 0.9) < 0.01  # Use approximate equality for float

    def test_analyze_score_normalized_to_one(self):
        """Test suspicion score is capped at 1.0."""
        # Create scenario that would exceed 1.0
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                305: "Photoshop",  # +0.6
                271: "Test",  # Only 2 tags, +0.3
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score <= 1.0
        assert abs(score - 0.9) < 0.01  # 0.6 + 0.3

    # Test: Edge Cases
    def test_analyze_invalid_image_data(self):
        """Test invalid image data returns 0.3."""
        invalid_bytes = b"not an image at all"
        score = self.detector.analyze(invalid_bytes)
        assert score == 0.3

    def test_analyze_empty_bytes(self):
        """Test empty bytes returns 0.3."""
        score = self.detector.analyze(b"")
        assert score == 0.3

    def test_analyze_corrupted_image(self):
        """Test partially corrupted image data."""
        # Create valid image then corrupt it
        valid_bytes = self._create_test_image_with_exif(exif_data={305: "Test"})
        corrupted_bytes = valid_bytes[:100]  # Truncate
        score = self.detector.analyze(corrupted_bytes)
        assert score == 0.3  # Exception handling returns 0.3

    def test_analyze_software_tag_none(self):
        """Test when software tag exists but is None."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Canon",
                272: "Canon EOS",
                274: 1,
                306: "2024:01:15 10:30:00",
                282: 72.0,
                283: 72.0,
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.0  # No software tag, enough tags

    def test_analyze_software_tag_empty_string(self):
        """Test when software tag is empty string."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                305: "",  # Empty software tag
                271: "Canon",
                272: "Canon EOS",
                274: 1,
                306: "2024:01:15 10:30:00",
                282: 72.0,
            }
        )
        score = self.detector.analyze(image_bytes)
        # Empty string won't match any editing software
        assert score == 0.0

    # Test: Realistic Scenarios
    def test_analyze_professional_forgery_metadata_stripped(self):
        """Test professional forgery with stripped metadata."""
        # Forger stripped all EXIF to hide traces
        image_bytes = self._create_test_image_with_exif(exif_data={})
        score = self.detector.analyze(image_bytes)
        assert score == 0.4  # Suspicious due to no EXIF

    def test_analyze_amateur_forgery_photoshop_metadata(self):
        """Test amateur forgery with Photoshop metadata intact."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                305: "Adobe Photoshop CC 2023",
                306: "2024:01:15 10:30:00",
                271: "Canon",  # Original camera make still present
            }
        )
        score = self.detector.analyze(image_bytes)
        # Photoshop detected + few tags
        assert abs(score - 0.9) < 0.01  # Use approximate equality

    def test_analyze_authentic_camera_photo(self):
        """Test authentic photo straight from camera."""
        # Rich EXIF typical of modern smartphone/camera
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Apple",  # Make
                272: "iPhone 14 Pro",  # Model
                305: "16.2",  # iOS version (not editing software)
                274: 1,  # Orientation
                306: "2024:01:15 10:30:00",  # DateTime
                282: 72.0,  # XResolution
                283: 72.0,  # YResolution
                296: 2,  # ResolutionUnit
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.0  # Authentic camera photo

    def test_analyze_phone_edited_with_native_app(self):
        """Test photo edited with phone's native editing app."""
        # Some phone apps don't add "editing software" to EXIF
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Apple",
                272: "iPhone 14 Pro",
                305: "16.2",  # Still shows iOS version
                274: 1,
                306: "2024:01:15 10:30:00",
                282: 72.0,
                283: 72.0,
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.0  # Native app edits may not be detected

    # Test: Boundary Conditions
    def test_analyze_exactly_four_tags(self):
        """Test boundary: exactly 4 tags (one below threshold)."""
        image_bytes = self._create_test_image_with_exif(
            exif_data={
                271: "Canon",
                272: "EOS",
                274: 1,
                306: "2024:01:15 10:30:00",
            }
        )
        score = self.detector.analyze(image_bytes)
        assert score == 0.3  # Should flag as few tags

    def test_analyze_one_tag_only(self):
        """Test minimal EXIF: only one tag."""
        image_bytes = self._create_test_image_with_exif(exif_data={274: 1})
        score = self.detector.analyze(image_bytes)
        assert score == 0.3  # Few tags

    def test_editing_software_constant_values(self):
        """Test that editing_software contains expected values."""
        expected_software = {
            "photoshop",
            "gimp",
            "paint.net",
            "affinity",
            "pixelmator",
            "acorn",
            "photoscape",
        }
        assert self.detector.editing_software == expected_software

    # Test: Return Value Range
    def test_analyze_always_returns_valid_range(self):
        """Test all analyze calls return scores in valid range [0.0, 1.0]."""
        test_cases = [
            self._create_test_image_with_exif(exif_data={}),
            self._create_test_image_with_exif(exif_data={305: "Photoshop"}),
            self._create_test_image_with_exif(
                exif_data={271: "Canon", 272: "EOS", 274: 1}
            ),
            b"invalid",
            b"",
        ]

        for image_bytes in test_cases:
            score = self.detector.analyze(image_bytes)
            assert 0.0 <= score <= 1.0, f"Score {score} out of valid range"
            assert isinstance(score, float), f"Score {score} is not a float"
