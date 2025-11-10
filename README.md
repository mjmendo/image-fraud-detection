# Image Forgery Challenge

This repository contains a project about a basic image forgery program for the insurance domain, specific to car damages domain.

## Context

The project is based on a challenge doc submitted, and follow-up Q&A. These can be found in [CHALLENGE.md](docs/CHALLENGE.md).

Based on the available information, I have conducted a research and written requirements and assumptions for a potential solution to the challenge. 

- Research: located in [RESEARCH.md](/docs/research/RESEARCH.md). It contains different sources, articles and notes about the problem domain.
- Requirements: requirements and assumptions are gathered in [REQUIREMENTS.md](/docs/REQUIREMENTS.md). These are driving the solution.
- Solution: implementation documentation is located at [SOLUTION.md](/docs/SOLUTION.md).

## Application

### Python Environment

- Python 3.9-3.12 (numpy has issues with 3.13)
- Poetry for dependency management
- Virtual environment in `venv/` directory
- Key dependencies: Pillow, numpy, opencv-python, imagehash

#### Project structure

```
src/forgery_detection/
├── main.py                   # CLI entry point
├── config.py                 # Application configuration (logging)
├── modes/                    # Detection modes
│   ├── evaluation_mode.py    # Evaluation mode (test with labeled data)
│   └── file_type_recipes.py  # Format-specific detector recipes
├── parsers/                  # CLI argument parsing
│   └── parsers.py            # Input argument parser
├── services/                 # Core services
│   ├── image_loader.py       # Image loading and validation
│   ├── format_detector.py    # Image format detection
│   ├── recipe_selector.py    # Format-specific recipe selection
│   ├── score_aggregator.py   # Weighted score calculation
│   ├── classifier.py         # Threshold-based classification
│   ├── report_generator.py   # Markdown report generation
│   └── detectors/            # Individual detection techniques
│       ├── detector.py       # Base detector class
│       ├── metadata_detector.py
│       ├── ela_detector.py
│       ├── statistical_detector.py
│       ├── copy_move_detector.py
│       ├── noise_variance_detector.py
│       └── reverse_search_detector.py
└── utils/                    # Utility functions
    └── console.py            # Console output formatting
```

## How to run

- Prerequisites
    - python3.9+
    - make
- Prepare local env

    ```bash
    make all
    ```

- Run application
    As stated in [the solution outcome](/docs/SOLUTION.md#outcome), only increasing metadata weight makes the script detect forgeries.

    - With provided images with default config

        ```bash
        poetry run detect-forgeries \
            --forged_dir images/provided/forged_images/ \
            --authentic_dir images/provided/authentic_images/ \
            --criteria all 
        ```

    - With casia2.0 dataset (sample)

        ```bash
        poetry run detect-forgeries \
            --forged_dir images/casia20/forged_images/ \
            --authentic_dir images/casia20/authentic_images/ \
            --criteria all 
        ```



