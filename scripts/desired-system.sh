#! /usr/bin/env bash

set -euo pipefail

system-input

TOPLEVEL=$(jq -r '.nix_toplevel // empty' system-input.json)
TOPLEVEL_URL=$(jq -r '.nix_toplevel_url // empty' system-input.json)

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
