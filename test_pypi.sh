#!/bin/bash

# Check if expected package version argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <expected_package_version>"
    exit 1
fi

# Assign the expected package version to a variable
EXPECTED_VERSION=$1

# List of popular Python versions to test
PYTHON_VERSIONS=("3.9" "3.10" "3.11")

# Loop through each Python version
for PYTHON_VERSION in "${PYTHON_VERSIONS[@]}"
do
    echo "Testing with Python $PYTHON_VERSION"

    # Build the Docker image with the current Python version and expected package version
    docker build --build-arg PYTHON_VERSION=$PYTHON_VERSION --build-arg EXPECTED_VERSION=$EXPECTED_VERSION -t positiondata_test .

    # Run the Docker container
    docker run positiondata_test

    # Check if the container ran successfully
    if [ $? -ne 0 ]; then
        echo "Test failed for Python $PYTHON_VERSION"
        exit 1
    fi
done

echo "All tests passed successfully."
