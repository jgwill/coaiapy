#!/usr/bin/env bash
set -e
ENV_NAME="testcoaiapy"
PACKAGE="coaiapy"

# Initialize conda for shell if available
if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo "conda is not available. Please install Miniconda or Anaconda." >&2
    exit 1
fi

# Create environment if it does not exist
if ! conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    conda create -y -n "$ENV_NAME" python=3.10
fi

# Activate environment
conda activate "$ENV_NAME"

# Install package from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "$PACKAGE"
