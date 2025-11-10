"""Recipe selection service for format-specific detection techniques."""

class RecipeSelector:
    """
    Service for selecting format-specific detection technique recipes.

    Different image formats require different detection approaches:
    - JPEG: Can use ELA (compression artifacts)
    - TIFF/BMP: Prioritize copy-move (works better on lossless)
    - PNG: Similar to TIFF/BMP
    """

    RECIPES = {
        "jpeg": ["metadata", "reverse_search", "ela", "statistical", "copy_move"],
        "tiff": ["metadata", "reverse_search", "statistical", "copy_move", "noise_variance"],
        "bmp": ["metadata", "reverse_search", "statistical", "copy_move", "noise_variance"],
        "png": ["metadata", "reverse_search", "statistical", "copy_move", "noise_variance"],
    }

    def select(self, format_type: str) -> list[str]:
        """
        Select detection technique recipe for given format.

        Args:
            format_type: Image format ("jpeg" | "tiff" | "bmp" | "png")

        Returns:
            List of technique names to apply
        """
        return self.RECIPES.get(format_type, self.RECIPES["jpeg"])
