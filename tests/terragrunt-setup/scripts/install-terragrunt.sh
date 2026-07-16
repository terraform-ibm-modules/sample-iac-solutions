#!/bin/bash

set -o errexit
set -o pipefail

DIRECTORY=${1:-"/tmp"}

# renovate: datasource=github-tags depName=terraform-ibm-modules/common-bash-library
TAG="v0.5.0"

# Download common-bash-library from tag
curl --silent \
    --connect-timeout 5 \
    --max-time 10 \
    --retry 3 \
    --retry-delay 2 \
    --retry-connrefused \
    --fail \
    --show-error \
    --location \
    --output "${DIRECTORY}/common-bash.tar.gz" \
    "https://github.com/terraform-ibm-modules/common-bash-library/archive/refs/tags/${TAG}.tar.gz" >&2

mkdir -p "${DIRECTORY}/common-bash-library"
tar -xzf "${DIRECTORY}/common-bash.tar.gz" --strip-components=1 -C "${DIRECTORY}/common-bash-library" 2>&1 >&2
rm -f "${DIRECTORY}/common-bash.tar.gz"

# shellcheck disable=SC1091
source "${DIRECTORY}/common-bash-library/common/common.sh"

# Install terragrunt to /usr/local/bin (default), skip if already present
install_terragrunt >&2

rm -rf "${DIRECTORY}/common-bash-library"

# Return JSON for external data source
echo '{"status":"success"}'
