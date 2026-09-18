#!/usr/bin/env bash
# Instructor only, before class. Linux x86-64. Uses the tested official build.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p tools
curl --fail --location --retry 2 \
 https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_x86_64_20260918.zip \
 -o tools/plink2.zip
unzip -o tools/plink2.zip -d tools
chmod +x tools/plink2
./tools/plink2 --version
# Use: export PLINK2="$PWD/tools/plink2"
