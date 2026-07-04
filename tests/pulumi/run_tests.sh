#!/bin/bash

set -Eeuo pipefail

# SC2155 Fix: Split declaration and assignment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly VENV_DIR="${SCRIPT_DIR}/.venv"
readonly REQUIREMENTS_TEST="${SCRIPT_DIR}/requirements_test.txt"
readonly SEPARATOR="======================================================================"

print_separator() {
    echo "${SEPARATOR}"
}

# SC2329 Fix: Shellcheck doesn't always trace trap references cleanly.
# Added a directive to tell it this function is used.
# shellcheck disable=SC2329
cleanup() {
    if declare -F deactivate >/dev/null 2>&1; then
        deactivate
    fi
}

trap cleanup EXIT

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed or not available in PATH."
    exit 1
fi

print_separator

if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Creating virtual environment at:"
    echo "  ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi

echo "Activating virtual environment..."

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
echo "Installing test dependencies..."
python -m pip install --upgrade pip --quiet
python -m pip install --requirement "${REQUIREMENTS_TEST}" --quiet
echo
printf "Running Pulumi Python tests\n"
printf "  Test Directory : %s\n\n" "${SCRIPT_DIR}"

pushd "${SCRIPT_DIR}" >/dev/null

if python -m pytest \
    . \
    -v \
    --cov=../../pulumi \
    --cov-report=term-missing \
    --tb=short
then
    popd >/dev/null
    echo
    echo "✅ Pulumi unit tests passed."
    print_separator
    exit 0
else
    exit_code=$?
    popd >/dev/null
    echo
    printf "❌ Pulumi unit tests failed.\n"
    printf "   Exit code : %d\n" "${exit_code}"
    print_separator
    exit "${exit_code}"
fi
