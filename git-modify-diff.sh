#!/usr/bin/env bash

#set -ex
rst_modify=`git status | grep modif | awk '{print $2}' | grep ^source`
echo $rst_modify
for i in $rst_modify; do echo $i; done
for i in $rst_modify; do git diff $i; done
history | tail -30 | awk '{$1="";print $0}'
