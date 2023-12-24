#!/bin/bash

echo "Running tests..."
./test_units_all_versions.sh

# Check if tests were successful
if [ $? -eq 0 ]; then
    echo "Tests passed successfully."

    # Extract dependencies from setup.py and requirements.txt
    SETUP_DEPS=$(python -c "import setuptools; setup = setuptools.setup; exec(open('setup.py').read()); print(repr(install_requires))")
    REQUIREMENTS_DEPS=$(cat requirements.txt | grep -vE 'setuptools|twine|wheel' | tr '\n' ' ')

    # Compare dependencies
    if [ "$SETUP_DEPS" != "$REQUIREMENTS_DEPS" ]; then
        echo "Dependency mismatch between setup.py and requirements.txt."
        exit 1
    fi

    # Extract version from setup.py
    VERSION=$(python setup.py --version)
    echo "Extracted version: $VERSION"

    # Tagging the repository
    echo "Tagging the repository with version $VERSION"
    git tag -a "v$VERSION" -m "Release version $VERSION"

    # Check if tagging was successful
    if [ $? -eq 0 ]; then
        git push origin "v$VERSION"

        # Building the package
        echo "Building the package..."
        ./build.sh

        # Check if build was successful
        if [ $? -eq 0 ]; then
            # Publishing to PyPI
            echo "Publishing the package to PyPI..."
            ./publish.sh

            echo "Release process completed successfully."
        else
            echo "Build failed. Release process aborted."
            exit 1
        fi
    else
        echo "Tagging failed. Release process aborted."
        exit 1
    fi
else
    echo "Tests failed. Release process aborted."
    exit 1
fi
