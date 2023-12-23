#!/bin/bash

# Argument 1: Expected version of the PositionData package
EXPECTED_VERSION=$1

# Install the PositionData package
pip install PositionData

# Check the installed version against the expected version
INSTALLED_VERSION=$(pip show PositionData | grep Version | cut -d ' ' -f 2)
if [ "$INSTALLED_VERSION" != "$EXPECTED_VERSION" ]; then
    echo "Version mismatch: Expected $EXPECTED_VERSION, got $INSTALLED_VERSION"
    exit 1
fi

# Test Python script to instantiate classes
cat << EOF | python
from PositionData import PositionData, MethaneData, WindData, Trajectory
print("PositionData, MethaneData, WindData, Trajectory classes instantiated successfully.")
EOF

if [ $? -eq 0 ]; then
    echo "Integration test passed."
else
    echo "Integration test failed."
    exit 1
fi
