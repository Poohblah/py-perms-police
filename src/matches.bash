#!/bin/bash

set -f

usage='matches usage: matches path pattern'

[[ $# -ne 2 ]] && (echo $usage; exit 1)

matches=false

string="$1"

for pattern in $(eval echo $2); do
    if [[ $matches != true ]]; then
        [[ $string = $pattern ]] && matches=true
    fi
done

if [[ $matches = true ]]; then
    exit 0
else
    exit 1
fi
