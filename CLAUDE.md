# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Image forgery detection system for car insurance fraud, targeting a high true positive rate (80%+) while minimizing false positives (<20%). The solution uses a pipeline architecture with format-specific detection "recipes" that combine multiple forensic techniques.

## Common Commands

### Setup
```bash
make all           # Clean, setup venv, install dependencies, verify
make clean         # Remove venv and artifacts
```

### Testing
```bash
make test          # Run unit tests with pytest
make test-coverage # Run tests with coverage report (htmlcov/index.html)
```

### Development
```bash
make format        # Format code with black (line-length: 100)
make lint          # Lint code with ruff
```

### Running the Detector

**Basic usage:**
```bash
poetry run detect-forgeries \
    --forged_dir images/provided/forged_images/ \
    --authentic_dir images/provided/authentic_images/ \
    --criteria balanced
```

**Available options:**
- `--criteria`: Detection mode - `strict` | `balanced` | `aggressive` | `all` (default: balanced)
- `--report`: Output report filename (default: report.md, timestamp added automatically)
- `--log-level`: Logging level - `DEBUG` | `INFO` | `WARNING` | `ERROR` | `CRITICAL` (default: INFO)
- `--config`: Custom config file path (default: config.yml in project root)

**Note**: Report files automatically include a timestamp suffix (format: YYMMDD-HHMM.md)
- Example: `report.md` → `report-251109-1755.md`

**Using custom config file:**
```bash
# With absolute path
poetry run detect-forgeries \
    --forged_dir images/provided/forged_images/ \
    --authentic_dir images/provided/authentic_images/ \
    --config /path/to/custom_config.yml

# With filename only (searches in project root)
poetry run detect-forgeries \
    --forged_dir images/provided/forged_images/ \
    --authentic_dir images/provided/authentic_images/ \
    --config my_custom.yml
```

**Config file behavior:**
- If no `--config` is specified, uses default `config.yml` in project root
- If `--config` is an absolute path, loads from that exact location
- If `--config` is just a filename, tries current directory first, then project root
- All detector parameters (thresholds, weights, scores) are configured via the config file
- See `config.yml` for available parameters and detailed documentation

## Architecture

### Pipeline Flow
1. **Load** → Image loading and validation (`ImageLoader`)
2. **Detect Format** → Determine image format (`FormatDetector`)
3. **Select Recipe** → Choose detection method combination (`RecipeSelector`)
4. **Execute Detectors** → Run format-specific detection techniques in parallel
5. **Aggregate Scores** → Weighted score calculation (`ScoreAggregator`)
6. **Classify** → Threshold-based classification (`Classifier`)
7. **Report** → Generate metrics and markdown report (`ReportGenerator`)

### Format-Specific Detection Recipes

- **JPEG**: Metadata → Reverse Search* → ELA → Statistical → Copy-Move
- **TIFF/BMP**: Metadata → Reverse Search* → Statistical → Copy-Move → Noise Variance
- **PNG**: Metadata → Reverse Search* → Statistical → Copy-Move → Noise Variance

*Not implemented in current version

### Detection Techniques

Located in `src/forgery_detection/services/detectors/`:

- `metadata_detector.py` - EXIF metadata analysis (editing software detection)
- `ela_detector.py` - Error Level Analysis for JPEG compression artifacts
- `statistical_detector.py` - Statistical property analysis (mean, std, entropy)
- `copy_move_detector.py` - Duplicate region detection using feature matching
- `noise_variance_detector.py` - Noise consistency analysis across regions
- `reverse_search_detector.py` - Stub for reverse image search

### Detection Modes

Defined in `Classifier` (src/forgery_detection/services/classifier.py:18-22):

- **strict** (0.7 threshold): Precision-focused, minimize false positives
- **balanced** (0.5 threshold): Target 80% TPR / 20% FPR
- **aggressive** (0.3 threshold): Recall-focused, catch more fakes

### Score Aggregation

Weights defined in `ScoreAggregator` (src/forgery_detection/services/score_aggregator.py):
- Default: metadata=0.25, ela=0.20, statistical=0.15, copy_move=0.25, noise=0.15
- Optimal (per SOLUTION.md): metadata=0.40 for current datasets

## Key Findings

From SOLUTION.md:
- Current datasets (provided images + CASIA2.0 sample) are primarily detected via metadata analysis (95% had "photoshop" in EXIF)
- Aggressive mode with 40% metadata weight achieves: 99% recall, 95.2% precision, 97% accuracy
- Other detection techniques did not contribute significantly to current dataset (high-quality edits)
- Reverse search implementation would likely improve accuracy but contribution is unknown

## Testing Strategy

- Unit tests in `tests/` directory for each detector and service
- Test individual detectors: `poetry run pytest tests/test_metadata_detector.py -v`
- Coverage target: Check `htmlcov/index.html` after `make test-coverage`

## Project Structure

```
src/forgery_detection/
├── cli.py                    # CLI entry point
├── services/
│   ├── image_loader.py       # Image loading and validation
│   ├── format_detector.py    # Image format detection
│   ├── recipe_selector.py    # Format-specific recipe selection
│   ├── score_aggregator.py   # Weighted score calculation
│   ├── classifier.py         # Threshold-based classification
│   ├── report_generator.py   # Markdown report generation
│   └── detectors/            # Individual detection techniques
│       ├── metadata_detector.py
│       ├── ela_detector.py
│       ├── statistical_detector.py
│       ├── copy_move_detector.py
│       ├── noise_variance_detector.py
│       └── reverse_search_detector.py
```

## Python Environment

- Python 3.9-3.12 (numpy has issues with 3.13)
- Poetry for dependency management
- Virtual environment in `venv/` directory
- Key dependencies: Pillow, numpy, opencv-python, imagehash
