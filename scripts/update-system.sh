#! /usr/bin/env bash

# This script takes a toplevel, and activates it. This is similar to the
# following blog post:
# https://vaibhavsagar.com/blog/2019/08/22/industrial-strength-deployments/.
#
# In other words, it moves from the `current-system` to the `desired-system`.

set -euo pipefail

curl -s http://169.254.169.254/metadata/v1/user-data > user-data.json

TOPLEVEL=$(jq -r '.nix_toplevel // empty' user-data.json)
TOPLEVEL_URL=$(jq -r '.nix_toplevel_url // empty' user-data.json)
BINARY=$(jq -r '.nix_binary // empty' user-data.json)

NIX_CACHE=$(jq -r '.nix_cache // empty' user-data.json)
NIX_TRUSTED_KEY=$(jq -r '.nix_trusted_key // empty' user-data.json)
export AWS_ACCESS_KEY_ID=$(jq -r '.nix_cache_key_id // empty' user-data.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.nix_cache_key_secret // empty' user-data.json)

# Force TOPLEVEL from the command-line argument.
if [ -n "${1-}" ]; then
  TOPLEVEL="$1"

elif [ -n "$TOPLEVEL" ]; then
  echo "Got a toplevel."

elif [ -n "$TOPLEVEL_URL" ]; then
  echo Querying URL for toplevel...
  curl -s -o toplevel.txt "$TOPLEVEL_URL"
  TOPLEVEL="$(cat toplevel.txt)"
  rm toplevel.txt

elif [ -n "$BINARY" ]; then
  echo "Got a binary."
  # Given a path that looks like /nix/store/xxxx-xyz-1.0.0/bin/xyz
  # extract the store path, restore it, then call the binary.
  echo Downloading binary closure...
  BINARY_CLOSURE=$(echo ${BINARY} | sed -e 's|\(/nix/store/[^/]\+\)/.\+|\1|')
  nix-store -r "${BINARY_CLOSURE}" \
    --option substituters "$NIX_CACHE" \
    --option trusted-public-keys "$NIX_TRUSTED_KEY"
  ${BINARY}
  exit 0
else
  echo "No toplevel or binary provided. Doing nothing."
  exit 0
fi

echo Toplevel is ${TOPLEVEL}.

echo Downloading toplevel closure...
nix-store -r "${TOPLEVEL}" \
  --option substituters "$NIX_CACHE" \
  --option trusted-public-keys "$NIX_TRUSTED_KEY" \

echo Activating copied toplevel...
nix-env --profile /nix/var/nix/profiles/system --set "${TOPLEVEL}"
/nix/var/nix/profiles/system/bin/switch-to-configuration switch
