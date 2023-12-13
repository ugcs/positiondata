#!/bin/bash

# Directory containing the package
PACKAGE_DIR="."

# Full path to the dist directory
DIST_DIR="${PACKAGE_DIR}/dist"

echo "Cleaning /dist directory..."

# Check if the /dist directory exists
if [ -d "$DIST_DIR" ]; then
    # Remove the contents of the /dist directory
    rm -r "${DIST_DIR:?}"/*
else
    echo "Directory /dist does not exist. Creating it now."
    mkdir "$DIST_DIR"
fi

echo "/dist directory cleaned."

echo "Building the package..."
python setup.py sdist bdist_wheel

# Add your package building commands here
# e.g., python setup.py sdist bdist_wheel

echo "Package build complete."