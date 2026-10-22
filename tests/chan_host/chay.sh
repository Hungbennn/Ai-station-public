#!/bin/sh
# Chạy pytest với bộ chặn host (bs-2bd.1.18, AGENT_RULES §13). Tham số chuyển nguyên cho pytest. Ví dụ:
#   tests/chan_host/chay.sh -q                       # cả bộ
#   tests/chan_host/chay.sh -q tests/test_chu.py     # một file
# Lớp chặn: lệnh giả trong bin/ đứng đầu PATH (tên tương đối; `git` giả KHÔNG BAO GIỜ chạy `git push` thật — push
# dạng hẹp vào kho trong thư mục tạm được giả lập bằng day_gia.py, còn lại chặn); audithook (`-p chan_host` +
# `sitecustomize.py` cho Python con mang PYTHONPATH này) bắt cả đường tuyệt đối, bọc lệnh, chuỗi shell, và mọi `git`
# đẩy/alias không đi qua git giả; git chỉ nói chuyện với kho file cục bộ (GIT_ALLOW_PROTOCOL=file). KHÔNG phải sandbox:
# xem điểm mù ở chan_host.py. Nhật ký chặn $TRAM_CHAN_NHAT_KY (mặc định file tạm mới, xoá khi sạch): có dòng mới →
# thoát 3 dù test xanh. Điểm mù đã gặp (Python con không mang bộ chặn) và số lần push giả lập in ở cuối.
# D61: `TRAM_CHAN_CHAY_SH=1` là dấu của runner — `tests/conftest.py` từ chối (thoát 4) khi thiếu nó, plugin `chan_host`
# hay `git` giả đầu PATH, nên pytest trần không chạy được test nào.
GOC=$(cd "$(dirname "$0")" && pwd)
if [ "${TRAM_KIEM_DA_CHUAN_BI:-}" = 1 ]; then
  PY_LUOT="$PWD/.venv/bin/python"
  if [ ! -x "$PY_LUOT" ] || ! "$PY_LUOT" -I -c '
import pathlib, sys
sys.exit(0 if pathlib.Path(sys.base_prefix).resolve() ==
         pathlib.Path("/usr/local/tram/toolchains/python/3.12.15-20261009") else 2)
'; then
    echo 'Python lượt kiểm thiếu hoặc khác prefix đã ghim; không chạy uv/fallback.' >&2
    exit 2
  fi
  chay_pytest() { "$PY_LUOT" -B -m pytest "$@"; }
  chay_python() { "$PY_LUOT" -B "$@"; }
  PATH_THEM="$PWD/.venv/bin:"
  GIT_THAT=/opt/homebrew/Cellar/git/2.56.0_1/bin/git
else
  chay_pytest() { uv run pytest "$@"; }
  chay_python() { uv run python "$@"; }
  PATH_THEM=
  GIT_THAT=${TRAM_CHAN_GIT:-$(command -v git)}
fi
# Dùng đúng môi trường pytest; xdist chỉ là tiện ích cục bộ, không đổi bộ thư viện/lock của lượt kiểm.
# Đặt trước tham số người gọi để `-n 0` vẫn ghi đè được; TRAM_TEST_NHAN=0 cũng chạy tuần tự.
if UV_OFFLINE=1 chay_python -c 'import xdist' >/dev/null 2>&1; then
  set -- -n "${TRAM_TEST_NHAN:-6}" "$@"
fi
NK=${TRAM_CHAN_NHAT_KY:-}
TAM=
if [ -z "$NK" ]; then NK=$(mktemp -t tram-chan) && TAM=1; fi
MU=$(mktemp -t tram-chan-mu)
GIA=$(mktemp -t tram-chan-gia)
touch "$NK"
truoc=$(wc -l < "$NK" | tr -d ' ')
GOC_TAM=$(cd "${TMPDIR:-/tmp}" && pwd -P)
DUNG_SAN=$("$GIT_THAT" --list-cmds=builtins | tr '\n' ' ')          # lệnh con dựng sẵn của git: đọc một lần
TRAM_CHAN_CHAY_SH=1 TRAM_CHAN_NHAT_KY="$NK" TRAM_CHAN_MU="$MU" TRAM_CHAN_GIA="$GIA" TRAM_CHAN_GIT="$GIT_THAT" \
  TRAM_CHAN_DUNG_SAN="$DUNG_SAN" TRAM_CHAN_GOC_TAM="${TRAM_CHAN_GOC_TAM:-$GOC_TAM}" \
  GIT_ALLOW_PROTOCOL=file GIT_TERMINAL_PROMPT=0 PATH="$GOC/bin:$PATH_THEM$PATH" \
  TRAM_CHAN_PY="${PY_LUOT:-${TRAM_CHAN_PY:-python3}}" \
  PYTHONPATH="$GOC:$PWD${PYTHONPATH:+:$PYTHONPATH}" UV_OFFLINE=1 chay_pytest -p chan_host \
  -W "ignore:Module already imported so cannot be rewritten; chan_host" "$@"      # sitecustomize đã nạp trước
ma=$?
sau=$(wc -l < "$NK" | tr -d ' ')
echo "=== nhật ký chặn $NK: $((sau - truoc)) dòng mới;" \
  "điểm mù (Python con không mang bộ chặn): $(wc -l < "$MU" | tr -d ' ');" \
  "push giả lập (không push thật): $(wc -l < "$GIA" | tr -d ' ')"
if [ "$sau" -gt "$truoc" ]; then
  tail -n "$((sau - truoc))" "$NK"
  ma=3
elif [ -n "$TAM" ]; then
  rm -f "$NK"
fi
[ -s "$MU" ] && sort "$MU" | uniq -c | sort -rn | head -20
rm -f "$MU" "$GIA"
exit "$ma"
