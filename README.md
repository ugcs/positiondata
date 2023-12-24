# PositionData Package

## Overview

The `PositionData` package is a comprehensive tool designed for processing positional CSV data, particularly useful for surveyors and geophysicists. It facilitates the efficient handling of geospatial data collected from various drone-based sensors. These sensors range from methane detectors to wind sensors, magnetometers, echo sounders, and more, each providing valuable scalar georeferenced readings essential for a wide array of applications.

For a detailed class reference and examples, please refer to the [Development Guide (DEVGUIDE.md)](DEVGUIDE.md).

To simply use the `PositionData` package, it can be installed from PyPI: [PositionData on PyPI](https://pypi.org/project/PositionData/).

Package is being maintained by [SPH Engineering](www.sphengineering.com) .

## Essential Development Tools

### Source Code

The source code for the `PositionData` package is located in the `PositionData` directory.

### Dependencies

All dependencies for the package are specified in the `requirements.txt` file and the respective section of `setup.py`. It is crucial to keep these files updated to manage the package's dependencies effectively.

### Unit Tests and Test Data

Unit tests and test data are located in the `tests` directory. These tests ensure the functionality and integrity of the package through various scenarios and data samples.

### Running Unit Tests

For development purposes, unit tests can be run using the following scripts:

- `test_units.sh`: A script for quick testing, which runs unit tests directly.
- `test_units_all_env.sh`: This script runs tests across all supported Python versions in Docker containers, ensuring compatibility and robustness.

### Releasing the Package

To release a new version of the package, use the `release.sh` script. This script automates the process of testing, building, tagging, and publishing the package to PyPI.

### Testing the PyPI Package

To test the current PyPI package across different Python versions, use the `test_pypi.sh` script. This script creates Docker containers for each Python version, installs the package from PyPI, and instantiates all classes to ensure everything is functioning as expected.
