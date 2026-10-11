#!/bin/bash
# Regenerate and render the Aperture 1976 wallpapers into ../backgrounds/.
set -euo pipefail
cd "$(dirname "$0")"
python3 -I make.py
for svg in *.svg; do
  name="${svg%.svg}"
  rsvg-convert -w 3840 -h 2400 "$svg" -o "/tmp/aperture-$name.png"
  magick "/tmp/aperture-$name.png" -quality 92 "../backgrounds/$name.jpg"
  rm "/tmp/aperture-$name.png"
  echo "rendered ../backgrounds/$name.jpg"
done
