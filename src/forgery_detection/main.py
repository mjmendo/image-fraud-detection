"""
CLI entry point for forgery detection.

Implements forgery detection using a pipeline of service classes.
"""

import argparse
import logging
from forgery_detection.config import setup_logging
from forgery_detection.config_loader import get_config
from forgery_detection.parsers.parsers import InputParser
from forgery_detection.modes.evaluation_mode import EvaluationMode, prepare_context
from forgery_detection.utils.console import print_banner


def main():
    """Main entry point for the application."""
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description="Image Forgery Detection for Car Insurance Fraud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    args = InputParser().parse(parser)

    # Initialize config with custom path if provided (must happen before any detectors are created)
    get_config(args.config)

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    if args.config:
        logger.info(f"Using custom config file: {args.config}")
    else:
        logger.info("Using default config file: config.yml")

    # Print title banner
    print_banner("FORGERY DETECTION", "Image Analysis for Car Insurance Fraud")
    logger.info("Starting forgery detection application")

    if not args.authentic_dir:
        parser.error("--authentic_dir is required")

    # Run evaluation mode
    evaluation_mode = EvaluationMode()
    evaluation_mode.run_evaluation(prepare_context(args))

    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
