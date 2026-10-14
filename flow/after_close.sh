#!/bin/bash
# after_close.sh N — once election:N is closed: save ballots + official rounds, my independent count vs official,
# exact replay of official rounds, render flow_eN.svg/png, summary table row. Stops at the first failure.
set -e; n=${1:?election number}; cd "$(dirname "$0")"
python3 fetch.py $n
python3 irv.py $n | tee /tmp/irv_e$n.txt
grep -q MATCH /tmp/irv_e$n.txt || { echo "irv.py DIFF on E$n: read before posting"; exit 2; }
python3 replay.py $n
python3 render.py $n
bash shot.sh flow_e$n.svg
python3 summary.py 0 1 2 3 $n | tee summary.txt
