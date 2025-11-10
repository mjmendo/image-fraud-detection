"""Report generation service for forgery detection results."""

from datetime import datetime
from PIL import Image
import io


class ReportGenerator:
    """Generates markdown reports for forgery detection analysis."""

    def __init__(self):
        """Initialize report generator."""
        self.editing_software = [
            "photoshop",
            "gimp",
            "paint.net",
            "affinity",
            "pixelmator",
            "acorn",
            "lightroom",
            "capture one",
            "darktable",
            "rawtherapee",
            "paint shop",
        ]

    def generate_evaluation_report(
        self,
        results_by_mode: dict[str, list[tuple[str, str, str]]],
        modes: list[str],
        thresholds: dict[str, float],
        weights: dict[str, float],
        image_details: list[dict],
    ) -> str:
        """
        Generate evaluation mode report.

        Args:
            results_by_mode: Classification results by mode
            modes: List of mode names
            thresholds: Threshold values by mode
            weights: Detector weights used
            image_details: Detailed scores for each image

        Returns:
            Markdown report string
        """
        report = []
        report.append("# Forgery Detection - Evaluation Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**Mode:** Evaluation (Ground Truth Labels Available)")
        report.append(f"\n**Total Images:** {len(image_details)}")
        report.append("\n---\n")

        # Configuration section
        report.append("## Configuration\n")
        report.append("### Detection Weights")
        report.append("| Detector | Weight |")
        report.append("|----------|--------|")
        for detector, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            report.append(f"| {detector.replace('_', ' ').title()} | {weight:.1%} |")

        report.append("\n### Classification Thresholds")
        report.append("| Mode | Threshold | Description |")
        report.append("|------|-----------|-------------|")
        report.append(
            f"| Strict | {thresholds['strict']:.2f} | High confidence required (fewer false positives) |"
        )
        report.append(f"| Balanced | {thresholds['balanced']:.2f} | Balanced approach (default) |")
        report.append(
            f"| Aggressive | {thresholds['aggressive']:.2f} | Flag more images (catches more forgeries) |"
        )

        report.append("\n---\n")

        # Performance metrics
        report.append("## Performance Metrics\n")
        for mode in modes:
            results = results_by_mode[mode]
            tp = sum(1 for _, pred, truth in results if pred == "forged" and truth == "forged")
            fp = sum(1 for _, pred, truth in results if pred == "forged" and truth == "authentic")
            fn = sum(1 for _, pred, truth in results if pred == "authentic" and truth == "forged")
            tn = sum(
                1 for _, pred, truth in results if pred == "authentic" and truth == "authentic"
            )

            total = len(results)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            accuracy = (tp + tn) / total if total > 0 else 0.0

            report.append(f"### {mode.upper()} Mode (threshold={thresholds[mode]:.2f})\n")
            report.append("| Metric | Value | Description |")
            report.append("|--------|-------|-------------|")
            report.append(f"| Total | {total} | Total images evaluated |")
            report.append(f"| True Positives (TP) | {tp} | Forged images correctly detected |")
            report.append(f"| False Positives (FP) | {fp} | Authentic images incorrectly flagged |")
            report.append(f"| False Negatives (FN) | {fn} | Forged images missed |")
            report.append(f"| True Negatives (TN) | {tn} | Authentic images correctly cleared |")
            report.append(
                f"| **Precision** | **{precision:.1%}** | Accuracy of forgery detections |"
            )
            report.append(f"| **Recall** | **{recall:.1%}** | Percentage of forgeries caught |")
            report.append(f"| **Accuracy** | **{accuracy:.1%}** | Overall correctness |")
            report.append("")

        # Individual image analysis - Compact table format
        report.append("## Individual Image Analysis\n")

        # Build table header dynamically based on modes
        header = "| Filename | Ground Truth | Score | Format | Metadata | ELA | Stat | Copy-Move | Noise |"
        separator = "|----------|--------------|-------|--------|----------|-----|------|-----------|-------|"
        for mode in modes:
            header += f" {mode.title()} |"
            separator += "---------|"
        header += " Flags |"
        separator += "------|"

        report.append(header)
        report.append(separator)

        for img_detail in image_details:
            # Get filename (shortened if too long)
            filename = img_detail["filename"].split("/")[-1]
            if len(filename) > 30:
                filename = "..." + filename[-27:]

            # Build basic columns
            row = f"| {filename} "
            row += f"| {img_detail['ground_truth'][:4].upper()} "
            row += f"| {img_detail['final_score']:.3f} "
            row += f"| {img_detail['format'].upper()} "

            # Detector scores
            scores = img_detail["detector_scores"]
            row += f"| {scores.get('metadata', 0):.2f} "
            row += f"| {scores.get('ela', 0):.2f} "
            row += f"| {scores.get('statistical', 0):.2f} "
            row += f"| {scores.get('copy_move', 0):.2f} "
            row += f"| {scores.get('noise_variance', 0):.2f} "

            # Predictions for each mode
            for mode in modes:
                pred = img_detail["predictions"][mode]
                truth = img_detail["ground_truth"]
                correct = "✓" if pred == truth else "✗"
                symbol = "🔴" if pred == "forged" else "🟢"
                row += f"| {symbol}{correct} "

            # Flags column
            flags = []
            exif = img_detail.get("exif_analysis", {})
            if exif.get("is_editing_software"):
                flags.append("SW")
            if exif.get("tags_count", 0) == 0:
                flags.append("NO-EXIF")
            elif exif.get("missing_critical"):
                flags.append("STRIPPED")

            flags_str = ",".join(flags) if flags else "-"
            row += f"| {flags_str} |"

            report.append(row)

        report.append("\n**Legend:**")
        report.append("- 🟢✓ = Correctly classified as authentic")
        report.append("- 🔴✓ = Correctly classified as forged")
        report.append("- ✗ = Misclassified")
        report.append(
            "- **Flags:** SW=Editing software detected, NO-EXIF=All metadata stripped, STRIPPED=Missing critical camera tags"
        )
        report.append("\n---\n")

        # Recommendations
        report.append("---\n")
        report.append("## Recommendations\n")

        # Check if metadata is driving scores
        high_metadata_count = sum(
            1 for img in image_details if img["detector_scores"].get("metadata", 0) > 0.5
        )
        if high_metadata_count > 0:
            report.append(
                f"- **Metadata signals detected** in {high_metadata_count} image(s). Consider increasing metadata weight for better detection.\n"
            )

        # Check recall issues
        for mode in modes:
            results = results_by_mode[mode]
            fn = sum(1 for _, pred, truth in results if pred == "authentic" and truth == "forged")
            if fn > 0:
                report.append(
                    f"- **{mode.title()} mode missed {fn} forgery(ies).** Consider lowering threshold or tuning weights.\n"
                )

        return "\n".join(report)

    def analyze_exif(self, image_bytes: bytes) -> dict:
        """
        Analyze EXIF metadata from image.

        Args:
            image_bytes: Raw image data

        Returns:
            Dictionary with EXIF analysis results
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            exif_data = img.getexif()

            result = {"tags_count": len(exif_data) if exif_data else 0}

            if not exif_data or len(exif_data) == 0:
                return result

            # Check for software tag
            software_tag = exif_data.get(305)
            if software_tag:
                result["software"] = software_tag
                software_lower = software_tag.lower()
                result["is_editing_software"] = any(
                    sw in software_lower for sw in self.editing_software
                )

            # Check for missing critical tags
            critical_tags = [271, 272, 306, 36867]  # Make, Model, DateTime, DateTimeOriginal
            missing = [tag for tag in critical_tags if tag not in exif_data]
            if missing:
                result["missing_critical"] = len(missing)

            return result

        except Exception:
            return {"tags_count": 0}
