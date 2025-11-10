import argparse


class InputParser:
    def __init__(self):
        pass

    def parse(self, parser: argparse.ArgumentParser) -> argparse.Namespace:
        """CLI entry point for forgery detection."""

        parser.add_argument(
            "--forged_dir",
            required=True,
            help="Directory with forged images",
        )

        parser.add_argument(
            "--authentic_dir",
            required=True,
            help="Directory with authentic images",
        )

        parser.add_argument(
            "--criteria",
            default="balanced",
            help="Detection criteria: strict,balanced,aggressive or 'all' (default: balanced)",
        )

        parser.add_argument(
            "--report",
            default="report.md",
            help="Output markdown report filename (default: report.md, timestamp will be added automatically)",
        )

        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set logging level (default: INFO)",
        )

        parser.add_argument(
            "--config",
            default=None,
            help="Path to custom config file. Can be absolute path or filename in project root (default: config.yml)",
        )

        return parser.parse_args()
