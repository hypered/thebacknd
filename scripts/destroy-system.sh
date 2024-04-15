#! /usr/bin/env bash

# Request thebacknd to destroy this virtual machine.
# This script is parameterized by the user data provided at VM
# creation time (through the --user-data option of doctl).

curl -s http://169.254.169.254/metadata/v1/user-data > user-data.json

cat user-data.json \
  | jq "{vm_id: .vm_id, vm_killcode: .vm_killcode}" \
  > destroy-system-parameters.json

curl -X POST \
  $(cat user-data.json | jq -r .destroy_url) \
  -H "Content-Type: application/json" \
  -d @destroy-system-parameters.json
