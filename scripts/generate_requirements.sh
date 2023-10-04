#!/bin/bash


# Directory of this script
DIR="$(dirname $(realpath $0))"

# Git repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Export environment details
conda list --export > "$REPO_ROOT/conda-requirements.txt"

# Convert to pip format
awk -F "=" '{print $1 "==" $2}' "$REPO_ROOT/conda-requirements.txt" > "$REPO_ROOT/requirements.txt"

chmod +x "$DIR/generate_requirements.sh"
