#! /usr/bin/env bash

# Request thebacknd to destroy this virtual machine.
# This script is parameterized by the user data provided at VM
# creation time (through the --user-data option of doctl).

system-input

cat system-input.json \
  | jq "{vm_id: .vm_id, vm_killcode: .vm_killcode}" \
  > destroy-system-parameters.json

curl -X POST \
  $(cat system-input.json | jq -r .destroy_url) \
  -H "Content-Type: application/json" \
  -d @destroy-system-parameters.json
