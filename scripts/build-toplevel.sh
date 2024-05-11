#! /usr/bin/env bash

# Build, sign, and cache the toplevel and binaries.

nix-build -A toplevel --out-link result-toplevel
nix-build -A binaries --out-link result-binaries

nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-toplevel)
nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-binaries)

set -a
source .env-nix-build
set +a

nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-toplevel)
nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-binaries)
