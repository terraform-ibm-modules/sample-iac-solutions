#!/bin/bash
# Script to run Pulumi Python tests

set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQUIREMENTS_TEST="${SCRIPT_DIR}/requirements_test.txt"

echo "======================================================================"
# Create virtual environment if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing Dependencies"
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r "${REQUIREMENTS_TEST}" --quiet
echo ""
printf "Running pulumi python tests with coverage \n\t ==> Test Directory: ${SCRIPT_DIR}"

cd "${SCRIPT_DIR}"

# Run pytest with coverage (terminal output only, no HTML)
if python3 -m pytest . -v --cov=../../pulumi --cov-report=term-missing --tb=short; then
    echo ""
    echo "✅ Pulumi unit tests passed!"
    echo "======================================================================"
    deactivate
    exit 0
else
    EXIT_CODE=$?
    echo ""
    printf "❌ Some Pulumi unit tests failed! \n\t ==> Exit code: ${EXIT_CODE}"
    echo "======================================================================"
    deactivate
    exit ${EXIT_CODE}
fi
