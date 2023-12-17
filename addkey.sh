#!/bin/bash

# Start the ssh-agent in the background
eval "$(ssh-agent -s)"

# Get the path of the SSH key from the environment variable
SSH_KEY_PATH=${GITHUB_REPO_KEY}

# Check if the SSH key is already added
if ! ssh-add -l | grep -q $SSH_KEY_PATH; then
    echo "SSH key not found in agent. Adding it now..."
    ssh-add $SSH_KEY_PATH
else
    echo "SSH key already added."
fi
