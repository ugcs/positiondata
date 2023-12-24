#!/bin/bash

# List of Python versions to test
PYTHON_VERSIONS=("3.9" "3.10" "3.11")

# Loop through each Python version
for PYTHON_VERSION in "${PYTHON_VERSIONS[@]}"
do
    echo "Running unit tests with Python $PYTHON_VERSION"

    # Build the Docker image for the current Python version
    docker build -f Dockerfile.units --build-arg PYTHON_VERSION=$PYTHON_VERSION -t positiondata_units:$PYTHON_VERSION .

    # Run the Docker container
    docker run positiondata_units:$PYTHON_VERSION

    # Check if the container ran successfully
    if [ $? -ne 0 ]; then
        echo "Unit tests failed for Python $PYTHON_VERSION"
        exit 1
    fi
done

echo "Unit tests passed for all Python versions."
