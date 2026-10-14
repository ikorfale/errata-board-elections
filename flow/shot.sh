#!/bin/bash
# shot.sh flow_eN.svg -> flow_eN.png via headless chromium (rsvg ignores CSS variables); size read from the svg
set -e; f=$1; T=$HOME/snap/chromium/common/tmp; mkdir -p $T; cp "$f" $T/; b=$(basename "$f" .svg)
w=$(grep -o 'width="[0-9]*"' "$f" | head -1 | tr -dc 0-9); h=$(grep -o 'height="[0-9]*"' "$f" | head -1 | tr -dc 0-9)
timeout 90 chromium --headless --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=$w,$h --screenshot=$T/$b.png file://$T/$b.svg >/dev/null 2>&1
cp $T/$b.png "$(dirname "$f")/$b.png"; echo "$(dirname "$f")/$b.png"
