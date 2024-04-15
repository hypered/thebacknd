#! /usr/bin/env bash

# Build, sign, and cache the toplevel and binary.

nix-build -A toplevel --out-link result-toplevel
nix-build -A binary --out-link result-binary

nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-toplevel)
nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-binary)

set -a
source .env-nix-build
set +a

nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-toplevel)
nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-binary)
