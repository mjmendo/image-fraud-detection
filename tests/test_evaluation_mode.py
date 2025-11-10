"""Tests for evaluation mode context preparation."""

import argparse
import re
from forgery_detection.modes.evaluation_mode import prepare_context


class TestPrepareContext:
    """Test cases for prepare_context function."""

    def test_prepare_context_basic(self):
        """Test context preparation with basic parameters."""
        args = argparse.Namespace(
            forged_dir="path/to/forged",
            authentic_dir="path/to/authentic",
            criteria="balanced",
            report="report.md",
        )
        context = prepare_context(args)

        assert context["forged_dir"] == "path/to/forged"
        assert context["authentic_dir"] == "path/to/authentic"
        assert context["criteria"] == "balanced"
        # Report should have timestamp: report-YYMMDD-HHMM.md
        assert re.match(r"report-\d{6}-\d{4}\.md", context["report"])

    def test_prepare_context_with_config(self):
        """Test context preparation with custom config."""
        args = argparse.Namespace(
            forged_dir="path/to/forged",
            authentic_dir="path/to/authentic",
            criteria="balanced",
            report="report.md",
            config="custom_config.yml",
        )
        context = prepare_context(args)

        assert context["config_file"] == "custom_config.yml"
        assert re.match(r"report-\d{6}-\d{4}\.md", context["report"])

    def test_prepare_context_with_all_optional_params(self):
        """Test context preparation with all optional parameters."""
        args = argparse.Namespace(
            forged_dir="path/to/forged",
            authentic_dir="path/to/authentic",
            criteria="all",
            report="custom-report.md",
            config="my_config.yml",
        )
        context = prepare_context(args)

        assert context["forged_dir"] == "path/to/forged"
        assert context["authentic_dir"] == "path/to/authentic"
        assert context["criteria"] == "all"
        # Custom report should also have timestamp: custom-report-YYMMDD-HHMM.md
        assert re.match(r"custom-report-\d{6}-\d{4}\.md", context["report"])
        assert context["config_file"] == "my_config.yml"

    def test_prepare_context_without_optional_params(self):
        """Test context preparation without optional parameters."""
        args = argparse.Namespace(
            forged_dir="path/to/forged",
            authentic_dir="path/to/authentic",
            criteria="balanced",
            report="report.md",
        )
        context = prepare_context(args)

        assert context["config_file"] == "config.yml (default)"
        assert re.match(r"report-\d{6}-\d{4}\.md", context["report"])

    def test_prepare_context_timestamp_format(self):
        """Test that timestamp is in correct format YYMMDD-HHMM."""
        args = argparse.Namespace(
            forged_dir="path/to/forged",
            authentic_dir="path/to/authentic",
            criteria="balanced",
            report="test.md",
        )
        context = prepare_context(args)

        # Extract timestamp from report name (test-YYMMDD-HHMM.md)
        match = re.match(r"test-(\d{6})-(\d{4})\.md", context["report"])
        assert match is not None, f"Report name doesn't match pattern: {context['report']}"

        date_part = match.group(1)  # YYMMDD
        time_part = match.group(2)  # HHMM

        # Verify date format (6 digits)
        assert len(date_part) == 6
        # Verify time format (4 digits)
        assert len(time_part) == 4

        # Verify hour is valid (00-23)
        hour = int(time_part[:2])
        assert 0 <= hour <= 23

        # Verify minute is valid (00-59)
        minute = int(time_part[2:])
        assert 0 <= minute <= 59
