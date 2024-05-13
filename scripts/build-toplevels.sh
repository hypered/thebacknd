#! /usr/bin/env bash

# Build, sign, and cache the toplevels and binaries.

nix-build -A toplevels.base --out-link result-toplevel-base
nix-build -A toplevels.example --out-link result-toplevel-example
nix-build -A binaries --out-link result-binaries

nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-toplevel-base)
nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-toplevel-example)
nix store sign \
  --recursive \
  --key-file signing-keys/cache-priv-key.pem \
  $(readlink ./result-binaries)

exit 0

set -a
source .env-nix-build
set +a

nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-toplevel-base)
nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-toplevel-example)
nix copy --to \
  's3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com' \
  $(readlink ./result-binaries)
