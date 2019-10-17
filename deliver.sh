#!/bin/bash
./package.sh
git status
git rm  -r --cached .
git add .
git commit -m "$1"
git push -u $2 $3