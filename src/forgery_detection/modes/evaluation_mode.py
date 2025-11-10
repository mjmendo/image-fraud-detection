import argparse
import logging
from datetime import datetime
from pathlib import Path
from forgery_detection.modes.file_type_recipes import FileTypeRecipes
from forgery_detection.services.format_detector import FormatDetector
from forgery_detection.services.image_loader import ImageLoader
from forgery_detection.services.classifier import Classifier
from forgery_detection.services.report_generator import ReportGenerator
from forgery_detection.services.score_aggregator import ScoreAggregator
from forgery_detection.utils.console import (
    print_section,
    print_table_row,
    format_percentage,
    format_metric,
    print_info,
)

logger = logging.getLogger(__name__)


def prepare_context(args: argparse.Namespace) -> dict:
    """Helper method: prepare context dictionary from args."""
    # Add timestamp to report filename
    timestamp = datetime.now().strftime("%y%m%d-%H%M")
    report_path = Path(args.report)
    report_name = report_path.stem + f"-{timestamp}" + report_path.suffix

    context = {
        "forged_dir": args.forged_dir,
        "authentic_dir": args.authentic_dir,
        "criteria": args.criteria,
        "report": report_name,
        "config_file": args.config if hasattr(args, "config") and args.config else "config.yml (default)",
    }

    return context


class EvaluationMode:
    "Evaluation mode for testing detector performance on labeled datasets. Enables a future 'prediction mode' for unlabeled images."

    def __init__(self):
        self.recipes = FileTypeRecipes()
        self.image_loader = ImageLoader()
        self.classifier = Classifier()
        self.format_detector = FormatDetector()
        self.score_aggregator = ScoreAggregator()
        self.report_generator = ReportGenerator()

    def _load_images(self, context: dict) -> list:
        # Load labeled images
        images = self.image_loader.load_labeled_images(
            context["forged_dir"], context["authentic_dir"]
        )
        logger.info(f"Loaded {len(images)} images")
        return images

    def _adjust_recipes(self, context: dict):
        # Adjust recipes based on criteria
        criteria = self._extract_criteria(context)
        criteria_thresholds = [
            f"{c} (threshold={self.classifier.get_threshold(c)})" for c in criteria
        ]
        print_info(f"\nTesting criteria: {', '.join(criteria_thresholds)}")

    def _extract_criteria(self, context: dict) -> list:
        # Load & Configure execution criteria
        if context["criteria"] == "all":
            return ["strict", "balanced", "aggressive"] # Refactor this!
        else:
            return [m.strip() for m in context["criteria"].split(",")]

    def _run_detectors(self, image_bytes, format_type):
        # Initialize detectors
        detectors = self.recipes.get_detectors_by_format(format_type)

        technique_scores = {}

        # Run each detector
        for name in detectors.keys():
            technique_scores[name] = detectors[name].analyze(image_bytes)

        return technique_scores

    def _generate_report(
        self, context: dict, criteria: list, image_details: list, results_by_mode: dict
    ):
        # Generate evaluation report
        logger.info("Generating report")
        report_content = self.report_generator.generate_evaluation_report(
            results_by_mode=results_by_mode,
            modes=criteria,
            thresholds=self.classifier.thresholds,
            weights=self.score_aggregator.weights,
            image_details=image_details,
        )
        # Save report to file
        with open(context["report"], "w") as f:
            f.write(report_content)
        logger.info(f"Report saved to: {context['report']}")

    def _print_results_summary(self, criteria: list, results_by_criteria: dict):
        """Print evaluation results summary with metrics for each criteria."""
        print_section("RESULTS BY CRITERIA")

        for c in criteria:
            results = results_by_criteria[c]
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

            print(f"\nMODE: {c.upper()} (threshold={self.classifier.get_threshold(c)})")
            print_table_row("Total:", str(total))
            print_table_row("TP:", format_metric("TP", tp))
            print_table_row("FP:", format_metric("FP", fp))
            print_table_row("FN:", format_metric("FN", fn))
            print_table_row("TN:", format_metric("TN", tn))
            print_table_row("Precision:", format_percentage(precision))
            print_table_row("Recall:", format_percentage(recall))
            print_table_row("Accuracy:", format_percentage(accuracy))

    def run_evaluation(self, context: dict):
        print_section("EVALUATION: Testing Detector")
        print_info("Loading images from:")
        print_table_row("Forged:", context["forged_dir"])
        print_table_row("Authentic:", context["authentic_dir"])
        print_table_row("Config:", context["config_file"])

        # Adjust recipes if needed
        self._adjust_recipes(context)

        # Load images
        images = self._load_images(context)
        criteria = self._extract_criteria(context)
        results_by_criteria = {c: [] for c in criteria}
        image_details = []

        # Process each image
        for image_path, image_bytes, true_label in images:
            # Detect format
            format_type = self.format_detector.detect(image_bytes)
            if not format_type:
                logger.warning(f"Skipping {image_path}: Unknown format")
                continue

            # Run detectors
            scores = self._run_detectors(image_bytes, format_type)

            # Aggregate scores
            final_score = self.score_aggregator.aggregate(scores, format_type)

            # EXIF analysis for report
            exif_analysis = self.report_generator.analyze_exif(image_bytes)

            # Classify with requested criteria
            image_classifications = {}
            for c in criteria:
                classification = self.classifier.classify(final_score, c)
                results_by_criteria[c].append((image_path, classification, true_label))
                image_classifications[c] = classification

            # Store image details for report
            image_details.append(
                {
                    "filename": image_path,
                    "ground_truth": true_label,
                    "format": format_type,
                    "final_score": final_score,
                    "detector_scores": scores.copy(),
                    "predictions": image_classifications,
                    "exif_analysis": exif_analysis,
                }
            )

        # Calculate and print metrics
        self._print_results_summary(criteria, results_by_criteria)

        # Generate evaluation report
        if context.get("report"):
            self._generate_report(
                context=context,
                criteria=criteria,
                image_details=image_details,
                results_by_mode=results_by_criteria,
            )
