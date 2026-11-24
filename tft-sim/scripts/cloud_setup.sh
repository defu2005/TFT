#!/usr/bin/env bash
# Cài môi trường cho agent cloud (Codex, Cursor). Chạy: bash tft-sim/scripts/cloud_setup.sh
# Idempotent: chạy lại không hỏng. Không chứa bí mật. Không sửa repo TFT.
# Kết quả: ~/work/tft_goat (ghim commit d5358e94), ~/work/venv (Python + torch CPU).
set -euo pipefail

SIM_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TFT_GOAT_PIN="d5358e9402569f745bea81b61c5aed0500c57d66"
WORK="${SIM_WORK:-$HOME/work}"
GOAT="$WORK/tft_goat"
VENV="$WORK/venv"

mkdir -p "$WORK"

# 1. TFT_GOAT: repo công khai, clone không cần đăng nhập; ghim đúng commit.
if [ ! -d "$GOAT/.git" ]; then
  git clone --quiet https://github.com/MielPopsssssss/tft_goat "$GOAT"
fi
git -C "$GOAT" fetch --quiet origin "$TFT_GOAT_PIN" 2>/dev/null || git -C "$GOAT" fetch --quiet origin
git -C "$GOAT" checkout --quiet --detach "$TFT_GOAT_PIN"
if [ "$(git -C "$GOAT" rev-parse HEAD)" != "$TFT_GOAT_PIN" ]; then
  echo "LOI: tft_goat khong o commit $TFT_GOAT_PIN" >&2
  exit 1
fi

# 2. Python: venv ngoài repo (không làm bẩn git).
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
. "$VENV/bin/activate"
pip install -q --upgrade pip
pip install -q numpy pydantic httpx riotwatcher gymnasium pettingzoo pytest
# Torch CPU trước; nếu index không truy cập được thì bản mặc định (nặng hơn).
pip install -q torch --index-url https://download.pytorch.org/whl/cpu \
  || pip install -q torch

# 3. Kiểm tra nhập được cả hai gói.
PYTHONPATH="$SIM_DIR/src:$GOAT/src" python -c "import tft_goat, tft_sim, torch, numpy; print('ok torch', torch.__version__, 'numpy', numpy.__version__)"

# Ghi file env với đường dẫn tuyệt đối; agent chỉ cần: . ~/work/env.sh
cat > "$WORK/env.sh" <<ENVEOF
. $VENV/bin/activate
export PYTHONPATH=$SIM_DIR/src:$GOAT/src
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ENVEOF
echo "Xong. Trước mỗi lệnh sim chạy: . $WORK/env.sh"
