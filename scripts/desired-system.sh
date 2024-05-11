#! /usr/bin/env bash

set -euo pipefail

curl -s http://169.254.169.254/metadata/v1/user-data > user-data.json

TOPLEVEL=$(jq -r '.nix_toplevel // empty' user-data.json)
TOPLEVEL_URL=$(jq -r '.nix_toplevel_url // empty' user-data.json)

if [ -n "$TOPLEVEL" ]; then
  echo "Got a toplevel."

elif [ -n "$TOPLEVEL_URL" ]; then
  echo Querying URL for toplevel...
  curl -s -o toplevel.txt "$TOPLEVEL_URL"
  TOPLEVEL="$(cat toplevel.txt)"
  rm toplevel.txt

else
  echo "No toplevel or toplevel URL provided."
  exit 1
fi

echo ${TOPLEVEL}
