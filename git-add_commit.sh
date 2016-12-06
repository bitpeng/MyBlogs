#!/usr/bin/env bash

set -ex
git status
if [ ! "$1x" = "x" ]; then
    sleep 5
    git add --all
    git status
    git commit -m "$1"
fi
