#! /usr/bin/env bash

# This script downloads the latest system built by our GitHub action, and
# activates it. This is similar to the following blog post:
# https://vaibhavsagar.com/blog/2019/08/22/industrial-strength-deployments/.
#
# In other words, it moves from the `current-system` to the `desired-system`.

set -euo pipefail

echo Querying target toplevel...
curl -s -o toplevel.txt https://f003.backblazeb2.com/file/hypered-store/toplevels/test.txt

TOPLEVEL="$(cat toplevel.txt)"
rm toplevel.txt

echo Toplevel is ${TOPLEVEL}.

echo Downloading toplevel closure...
nix-store -r "${TOPLEVEL}" \
  --option substituters \
    https://f003.backblazeb2.com/file/hypered-store/cache \
  --option trusted-public-keys \
    "f003.backblazeb2.com:M/LnuDSG/qZLu3PkzC+U8W0ndhK12mbpN0AW1IJn2ns="

echo Activating copied toplevel...
nix-env --profile /nix/var/nix/profiles/system --set "${TOPLEVEL}"
/nix/var/nix/profiles/system/bin/switch-to-configuration switch
