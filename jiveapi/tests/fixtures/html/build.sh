#!/bin/bash

pandoc --version &>/dev/null || { echo "ERROR: pandoc not in PATH; this script requires pandoc."; exit 1; }

for fname in *.md; do
  htmlname=${fname/%.md/.html}
  pandoc -s --highlight-style=pygments --ascii -f markdown -t html $fname -o $htmlname
done
