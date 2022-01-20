#!/bin/bash

set -euC

this_dir=$(cd "$(dirname "$0")" && pwd -P)
root_dir=$(dirname "${this_dir}")
source "${this_dir}/config.sh"
dist_dir="${root_dir}/dist"
mkdir -p "${dist_dir}"
ankiaddon="${dist_dir}/${package}.ankiaddon"

function main() {
    rm -f -v "$ankiaddon"
    echo "Building ${package}.ankiaddon ..."
    cd "${root_dir}/src"
    zip -r ${ankiaddon} . -x "meta.json" "*.log" "__pycache__/*" ".mypy_cache/*"
    cd "${root_dir}"
    zip ${ankiaddon} "manifest.json" "README.md" "LICENSE"
    echo "Build done!"
}

main
