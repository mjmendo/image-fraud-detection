"""Tests for RecipeSelector service."""

from forgery_detection.services.recipe_selector import RecipeSelector


class TestRecipeSelector:
    """Test cases for RecipeSelector."""

    def setup_method(self):
        """Setup test fixtures."""
        self.selector = RecipeSelector()

    def test_select_jpeg_recipe(self):
        """Test JPEG recipe includes ELA."""
        recipe = self.selector.select("jpeg")
        assert "metadata" in recipe
        assert "reverse_search" in recipe
        assert "ela" in recipe
        assert "statistical" in recipe
        assert "copy_move" in recipe

    def test_select_tiff_recipe(self):
        """Test TIFF recipe includes noise_variance, no ELA."""
        recipe = self.selector.select("tiff")
        assert "metadata" in recipe
        assert "reverse_search" in recipe
        assert "statistical" in recipe
        assert "copy_move" in recipe
        assert "noise_variance" in recipe
        assert "ela" not in recipe

    def test_select_bmp_recipe(self):
        """Test BMP recipe same as TIFF."""
        recipe = self.selector.select("bmp")
        assert "noise_variance" in recipe
        assert "ela" not in recipe

    def test_select_png_recipe(self):
        """Test PNG recipe same as TIFF."""
        recipe = self.selector.select("png")
        assert "noise_variance" in recipe
        assert "ela" not in recipe

    def test_select_unknown_format_defaults_to_jpeg(self):
        """Test unknown format defaults to JPEG recipe."""
        recipe = self.selector.select("unknown")
        assert "ela" in recipe  # JPEG default includes ELA
