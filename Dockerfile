# Use an official Python runtime as a parent image
FROM python:${PYTHON_VERSION}

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the test script into the container
COPY test_positiondata.sh /usr/src/app

# Make the test script executable
RUN chmod +x /usr/src/app/test_positiondata.sh

# Run the test script when the container launches
CMD ["./test_positiondata.sh", "${EXPECTED_VERSION}"]