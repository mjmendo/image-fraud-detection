"""Tests for console output utilities."""

from forgery_detection.utils.console import (
    print_banner,
    print_section,
    print_table_row,
    format_percentage,
    format_metric,
    print_info,
)


class TestConsoleUtils:
    """Test cases for console utilities."""

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0.5) == "50.0%"
        assert format_percentage(0.123) == "12.3%"
        assert format_percentage(1.0) == "100.0%"

    def test_format_metric_with_description(self):
        """Test metric formatting with known descriptions."""
        assert "forged → detected" in format_metric("TP", 10)
        assert "authentic → flagged" in format_metric("FP", 5)
        assert "forged → missed" in format_metric("FN", 2)
        assert "authentic → cleared" in format_metric("TN", 20)

    def test_format_metric_without_description(self):
        """Test metric formatting for unknown metrics."""
        result = format_metric("Unknown", 42)
        assert "42" in result

    def test_print_banner_output(self, capsys):
        """Test banner printing."""
        print_banner("TEST TITLE", "Test Subtitle")
        captured = capsys.readouterr()

        assert "TEST TITLE" in captured.out
        assert "Test Subtitle" in captured.out
        assert "=" in captured.out

    def test_print_banner_no_subtitle(self, capsys):
        """Test banner printing without subtitle."""
        print_banner("TEST TITLE")
        captured = capsys.readouterr()

        assert "TEST TITLE" in captured.out
        assert "=" in captured.out

    def test_print_section_output(self, capsys):
        """Test section header printing."""
        print_section("TEST SECTION")
        captured = capsys.readouterr()

        assert "TEST SECTION" in captured.out
        assert "=" in captured.out

    def test_print_table_row_output(self, capsys):
        """Test table row printing."""
        print_table_row("Label:", "Value")
        captured = capsys.readouterr()

        assert "Label:" in captured.out
        assert "Value" in captured.out
        assert captured.out.startswith("  ")  # Should be indented

    def test_print_info_output(self, capsys):
        """Test info message printing."""
        print_info("Test message")
        captured = capsys.readouterr()

        assert "Test message" in captured.out
