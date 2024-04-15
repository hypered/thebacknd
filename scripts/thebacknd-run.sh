#! /usr/bin/env bash

# $1 can be /nix/store/xxxx-xyz-1.0.0/bin/xyz or /nix/store/xxxx-xyz-1.0.0.
# Maybe we should have distinct commands for deploying a toplevel and for
# running a binary.
FULL_PATH="$1"
STORE_PATH=$(echo ${FULL_PATH} | sed -e 's|\(/nix/store/[^/]\+\)/.\+|\1|')
if [ "$FULL_PATH" == "$STORE_PATH" ]; then
  param="nix_toplevel:$STORE_PATH"
else
  param="nix_binary:$FULL_PATH"
fi

doctl serverless functions invoke thebacknd/create --param "$param"
