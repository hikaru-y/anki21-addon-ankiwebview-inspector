#!/bin/bash

# This script requires administrator privileges

set -euC

export MSYS=winsymlinks:nativestrict

this_dir=$(cd "$(dirname "$0")" && pwd -P)
root_dir=$(dirname "${this_dir}")
source "${this_dir}/config.sh"
addons21_dir="/D/_anki/addons21"

# Windows -> POSIX
# appdata=$(echo "/${APPDATA}" | sed -e 's/\\/\//g' -e 's/://')

ln -f -s "${root_dir}/src/" "${addons21_dir}/${package}"
