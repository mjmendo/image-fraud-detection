"""Simple console output utilities using standard library only."""


def print_banner(title: str, subtitle: str = "", width: int = 70) -> None:
    """
    Print a centered banner with title and optional subtitle.

    Args:
        title: Main title text
        subtitle: Optional subtitle text
        width: Width of the banner (default: 70)
    """
    print("\n" + "=" * width)
    print(title.center(width))
    if subtitle:
        print(subtitle.center(width))
    print("=" * width + "\n")


def print_section(title: str, width: int = 70) -> None:
    """
    Print a section header.

    Args:
        title: Section title
        width: Width of the header (default: 70)
    """
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def print_table_row(label: str, value: str, label_width: int = 12) -> None:
    """
    Print a simple two-column table row.

    Args:
        label: Left column label
        value: Right column value
        label_width: Width for label column (default: 12)
    """
    print(f"  {label:<{label_width}} {value}")


def format_percentage(value: float) -> str:
    """Format a float as percentage string."""
    return f"{value:.1%}"


def format_metric(name: str, value: int) -> str:
    """Format a metric with its description."""
    descriptions = {
        "TP": "forged → detected",
        "FP": "authentic → flagged",
        "FN": "forged → missed",
        "TN": "authentic → cleared",
    }
    desc = descriptions.get(name, "")
    return f"{value:<8} ({desc})" if desc else str(value)


def print_info(message: str) -> None:
    """
    Print an informational message.

    Args:
        message: Message to print
    """
    print(message)
