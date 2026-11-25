#!/usr/bin/env bash
# Dung moi truong de chay tft-sim trong session moi.
#   - clone engine tft_goat tai dung commit da ghim (khong dung nhanh main thoi),
#   - cai dependencies cua engine tu pyproject.toml (tru torch) cung pandas,
#   - in dong PYTHONPATH can export.
# Dung:  bash scripts/bootstrap_engine.sh [thu_muc_engine]
# Bien moi truong: TFT_GOAT_DIR (mac dinh ~/work/tft_goat), PYTHON (mac dinh python3)
set -euo pipefail

ENGINE_URL="https://github.com/MielPopsssssss/tft_goat"
ENGINE_REV="d5358e9402569f745bea81b61c5aed0500c57d66"
ENGINE_DIR="${1:-${TFT_GOAT_DIR:-$HOME/work/tft_goat}}"
SIM_SRC="$(cd "$(dirname "$0")/.." && pwd)/src"

if [ ! -d "$ENGINE_DIR/.git" ]; then
    mkdir -p "$(dirname "$ENGINE_DIR")"
    git clone --quiet "$ENGINE_URL" "$ENGINE_DIR"
fi
git -C "$ENGINE_DIR" fetch --quiet origin
git -C "$ENGINE_DIR" checkout --quiet --detach "$ENGINE_REV"
got="$(git -C "$ENGINE_DIR" rev-parse HEAD)"
if [ "$got" != "$ENGINE_REV" ]; then
    echo "LOI: engine o $got, can $ENGINE_REV" >&2
    exit 1
fi

# Cai dependencies cua engine tu pyproject.toml (ban dung cua engine, khong copy tay).
# Bo torch: chi goi agent/ va surrogate/ import; duong mo phong combat (selftest) khong can.
PY="${PYTHON:-python3}"
mapfile -t DEPS < <("$PY" -c '
import sys, tomllib
d = tomllib.load(open(sys.argv[1], "rb"))
for x in d["project"]["dependencies"]:
    if not x.startswith("torch"):
        print(x)
' "$ENGINE_DIR/pyproject.toml")
"$PY" -m pip install --quiet "${DEPS[@]}" pandas

echo "Engine: $ENGINE_DIR @ $got"
echo "Export truoc khi chay:"
echo "export PYTHONPATH=$ENGINE_DIR/src:$SIM_SRC"
