#!/usr/bin/env bash

scriptdir=$(dirname $0)
$(nix-build "$scriptdir"/../ --no-out-link -A runvm)/bin/run-nixos-vm
