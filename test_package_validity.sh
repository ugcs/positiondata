#!/bin/bash

# Check if expected package version argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <expected_package_version>"
    exit 1
fi

# Assign the expected package version to a variable
EXPECTED_VERSION=$1

# Install the PositionData package
pip install PositionData

# Check the installed version against the expected version
INSTALLED_VERSION=$(pip show PositionData | grep Version | cut -d ' ' -f 2)
if [ "$INSTALLED_VERSION" != "$EXPECTED_VERSION" ]; then
    echo "Version mismatch: Expected $EXPECTED_VERSION, got $INSTALLED_VERSION"
    exit 1
fi

# Get the current Python version
PYTHON_VERSION=$(python --version)
echo "Running on $PYTHON_VERSION"

# Test Python script to instantiate classes
cat << EOF | python
from PositionData import PositionData, MethaneData, WindData, Trajectory
print("PositionData, MethaneData, WindData, Trajectory classes instantiated successfully.")
EOF

if [ $? -eq 0 ]; then
    echo "Integration test passed on $PYTHON_VERSION."
else
    echo "Integration test failed on $PYTHON_VERSION."
    exit 1
fi
