#!/bin/bash
set -e # Exit on any command failure
echo "Looking for uv"
if ! [ -x "$(command -v uv)" ]; then
    echo 'uv is not installed. Installing'
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "Found uv installation"
fi

echo "Setting up the environment with uv"
uv venv .captsone --python 3.11
source .captsone/bin/activate
echo "Installing packages"
uv pip install -r setup/python_env/requirements.txt
uv pip install --pre prefect-dbt # Done separately, because --pre is not supported on per-package basis
echo "Installing pre-commit"
pre-commit install
echo "Now activate the environment by running source .captsone/bin/activate"
