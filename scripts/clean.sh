#! /usr/bin/env bash

# The local `doctl serverless deploy .` process leaves files around. This
# script removes them.

rm -f \
  packages/thebacknd/create/thebacknd.py \
  packages/thebacknd/destroy-all/thebacknd.py \
  packages/thebacknd/destroy-old/thebacknd.py \
  packages/thebacknd/list/thebacknd.py

find packages/ -type f -name "__deployer__.zip" -delete
