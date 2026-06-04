#!/bin/bash
# Script to run Pulumi Python tests

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${SCRIPT_DIR}/tests"

echo "======================================================================"
echo "Running Pulumi Python Tests with Coverage"
echo "======================================================================"
echo "Test Directory: ${TESTS_DIR}"
echo "======================================================================"

# Change to tests directory
cd "${TESTS_DIR}"

# Run pytest with coverage (terminal output only, no HTML)
if python3 -m pytest . -v --cov=.. --cov-report=term-missing --tb=short; then
    echo ""
    echo "======================================================================"
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo "======================================================================"
    exit 0
else
    EXIT_CODE=$?
    echo ""
    echo "======================================================================"
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo "   Exit code: ${EXIT_CODE}"
    echo "======================================================================"
    exit ${EXIT_CODE}
fi
