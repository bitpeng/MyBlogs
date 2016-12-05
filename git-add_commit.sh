#!/usr/bin/env bash

set -ex
git status
sleep 5
if [ ! "$1x" = "x" ]; then
    git add --all
    git status
    sleep 5
    git commit -m "$1"
fi
