"""3C-D7 Task 3 bản rút gọn (D117): kịch bản `docs/handovers/g3-bo-sung.sh` chạy với LỆNH GIẢ trong `tmp_path`
(`G3_GIA`): `sudo` giả chỉ cho chạy lệnh trong thư mục giả; `kill` giả chỉ tới `sleep` giả mà chính nó đã chạy "dưới
tram-kiem" (mô phỏng kill theo UID, không bao giờ tới tiến trình khác); `launchctl` giả giữ trạng thái miền trong tệp;
`ps` giả = bảng THẬT bỏ UID 503 + dòng giả của tram-kiem; `G3_PS_GIA=1` dùng bảng giả hoàn toàn khi sandbox chặn ps.
Chỉ kiểm cái đáng kiểm: tiền điều kiện, cổng dừng trước mọi
lệnh ghi, ghi lọt miền Đại ca → mã 4, dọn còn sót → không báo sạch, bị ngắt vẫn dọn."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.g3

GOC = Path(__file__).resolve().parents[1]
KB = Path(os.environ.get("D157_G3_SCRIPT", str(GOC / "docs/handovers/g3-bo-sung.sh")))
USER = (GOC / "tests" / "du_lieu" / "launchd" / "user-503.txt").read_text(encoding="utf-8")
TOI = str(os.getuid())
GIA = {
    "id": '[ "$1 $2" = "-u tram-kiem" ] && echo "${G3_UID_KIEM:-503}"\n',
    "sudo": r'''D=$(dirname "$0"); echo "sudo $*" >> "$D/nhat-ky"
if [ "$1" = -n ]; then shift 4
  case "$1" in
    "$D/launchctl") G3_LCTL_AI=tk; export G3_LCTL_AI; exec "$@";;
    /usr/bin/true) exit 0;;
    /bin/sleep) echo "$$ $PPID" > "$D/tk-sleep"; exec "$@";;
    /bin/kill) [ -f "$D/tk-sleep" ] && read p pp < "$D/tk-sleep" && { [ "$3" = -1 ] || [ "$3" = "$p" ]; } \
      && /bin/kill -KILL "$p" 2>/dev/null; exit 0;;
    /bin/mkdir|/usr/bin/tee|/bin/rm|/bin/test) case "$*" in *"$D"/goc/*) exec "$@";; esac;;
  esac; echo "TU-CHOI $*" >> "$D/nhat-ky"; exit 98
fi
if [ "$1 $2" = "$D/launchctl procinfo" ]; then
  /bin/sleep "${G3_TRE_PROCINFO:-0}"
  printf 'audit info\n\tsession id = %s\n' "${G3_ASID:-100003}"; exit "${G3_RC_PROCINFO:-0}"; fi
echo "TU-CHOI $*" >> "$D/nhat-ky"; exit 99
''',
    "ps": r'''D=$(dirname "$0"); che=$(cat "$D/ps-che-do" 2>/dev/null)
case "$che" in *1) rm -f "$D/ps-che-do";; esac
case "$che" in loi*) exit 1;; rac*) echo "khong phai bang"; exit 0;; rong*) exit 0;; esac
if [ "${G3_PS_GIA:-}" = 1 ]; then echo "$PPID 1 $G3_TOI $G3_TOI /bin/bash"
else /bin/ps -A -o pid=,ppid=,uid=,ruid=,comm= | awk '$3 != 503 && $4 != 503'; fi
[ -f "$D/tk-them" ] && { cat "$D/tk-them"; case "$(cat "$D/tk-them-mot" 2>/dev/null)" in 1) rm -f "$D/tk-them";; esac; }
[ -f "$D/tk-sleep" ] && read p pp < "$D/tk-sleep" && /bin/kill -0 "$p" 2>/dev/null && echo "$p $pp 503 503 /bin/sleep"
exit 0
''',
    "launchctl": r'''D=$(dirname "$0"); S="$D/lc"; mkdir -p "$S"
echo "launchctl $* ai=${G3_LCTL_AI:-toi}" >> "$D/nhat-ky"
f() { echo "$S/$(echo "$1" | tr / _)"; }
su_kien() { [ "${G3_PS#*@}" = "$1" ] && echo "${G3_PS%@*}" > "$D/ps-che-do"
  [ "${G3_TK_THEM#*@}" = "$1" ] && { echo "${G3_TK_DONG:-999999 1 503 503 /tmp/la}" > "$D/tk-them"
    echo "${G3_TK_THEM%@*}" > "$D/tk-them-mot"; }; :; }
case "$1" in
print) case "$2" in
  user/503) n=$(($(cat "$D/dem-user" 2>/dev/null || echo 0) + 1)); echo "$n" > "$D/dem-user"
    [ "$n" = "${G3_PRINT_LOI_LAN:-}" ] && exit 5
    awk -v t="$(f user/503)" -v lech="${G3_CO_VIEC_LECH:-}" '{print}
      /^\tservices = \{$/ {while ((getline l < t) > 0) {printf "\t\t       0      - \t%s\n", l; co = 1}}
      END {if (co && lech) print "\tthu lech = 1"}' "$D/user-503.txt"; exit 0;;
  gui/503) su_kien print-gui-tk
    [ -n "${G3_HONG_PS_SAU:-}" ] && for l in "$D"/out/g3b-*.log; do mkdir "${l%.log}-ps-sau.txt"; done
    echo "Could not print domain: 125: Domain does not support ${G3_GUI_LECH:+other }specified action" >&2; exit 125;;
  gui/"$G3_TOI") [ -f "$D/toi-da-nap" ] && [ -n "${G3_TOI_PRINT_LOI:-}" ] && exit 5
    printf 'gui/%s = {\n\ttype = login\n\thandle = 100003\n\tservices = {\n' "$G3_TOI"
    [ -f "$(f "$2")" ] && sed 's/^/\t\t       0      - \t/' "$(f "$2")"; printf '\t}\n}\n'; exit 0;;
  esac; exit 113;;
bootstrap) n=$(sed -n 's/.*<string>\(vn[^<]*\)<\/string>.*/\1/p' "$3"); m=$2
  case "$m" in user/503) rc=${G3_RC_USER:-0};;
    login/*) /bin/sleep "${G3_TRE_LOGIN:-0}"; rc=${G3_RC_LOGIN:-5}; m=gui/$G3_TOI; an=${G3_AN:-}
      # Cổng do test mở (không đoán bằng thời gian): giữ lần đo thứ nhất đứng yên ở đây tới khi test cho đi.
      i=0; while [ -n "${G3_CHO_TEP:-}" ] && [ ! -e "$G3_CHO_TEP" ] && [ $i -lt 200 ]; do /bin/sleep 0.1; i=$((i+1)); done
      [ -n "${G3_LOGIN_LOT:-}" ] && echo "$n" >> "$(f "$m")";;
    gui/"$G3_TOI") if [ "${G3_LCTL_AI:-toi}" = toi ]; then
      # Chủ miền: biên nhận phải có TRƯỚC khi ghi; plist riêng, kín, cùng chương trình vô hại.
      grep -qxF "nap $n $m toi" "$D"/out/*.receipt || exit 97
      [ "$(stat -f %OLp "${3%/*}")" = 700 ] && [ "${3#"$D"/goc/}" = "$3" ] || exit 97
      grep -q '<string>/usr/bin/true</string>' "$3" || exit 97
      touch "$D/toi-da-nap"; /bin/sleep "${G3_TRE_TOI:-0}"
      rc=${G3_RC_TOI:-0}; an=${G3_TOI_AN:-}
    else rc=${G3_RC_GUI:-5}; fi;; *) rc=113;; esac
  if [ "$rc" = 0 ]; then [ -n "${an:-}" ] || echo "$n" >> "$(f "$m")"
  else echo "Bootstrap failed: $rc: lỗi giả" >&2; fi; exit "$rc";;
bootout) su_kien bootout; [ -n "${G3_BOOTOUT_HONG:-}" ] && exit 0
  t=$(f "${2%/*}"); [ -f "$t" ] && { grep -vxF "${2##*/}" "$t" > "$t.x"; mv "$t.x" "$t"; }
  case "$2" in *.toi) rm -f "$D/toi-da-nap"; exit "${G3_TOI_GO_RC:-0}";; esac; exit 0;;
submit) echo "$3" >> "$(f "${G3_SUBMIT:-user/503}")"; [ -n "${G3_KHOA_BN:-}" ] && chmod 000 "$D"/out/*.receipt
  exit 0;;
remove) for t in "$S"/*; do [ -f "$t" ] && { grep -vxF "$2" "$t" > "$t.x"; mv "$t.x" "$t"; }; done; exit 0;;
esac; exit 64
''',
}


def dung(tmp_path: Path) -> Path:
    for ten, than in GIA.items():
        p = tmp_path / ten
        p.write_text("#!/bin/sh\n" + than, encoding="utf-8")
        p.chmod(0o755)
    py = tmp_path / "python-gia"
    py.write_text("#!/bin/sh\nexec " + __import__("shlex").quote(sys.executable) + " -I " +
                  __import__("shlex").quote(str(GOC / "tests/g3_d157_gia.py")) + ' "$@"\n')
    py.chmod(0o755)
    (tmp_path / "user-503.txt").write_text(USER, encoding="utf-8")
    (tmp_path / "goc").mkdir()
    return tmp_path


def moi_truong(d: Path, **env) -> dict:
    return {**os.environ, "G3_GIA": str(d), "G3_PY": str(d / "python-gia"), "G3_TOI": TOI, "G3_BAN": "24G90", "G3_PS": "",
            "G3_TK_THEM": "", **env}


def nhat_ky(d: Path) -> str:
    return (d / "nhat-ky").read_text(encoding="utf-8") if (d / "nhat-ky").exists() else ""


def chay(tmp_path, **env):
    d = dung(tmp_path)
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d, **env), stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=120)
    return r, nhat_ky(d)


def sach(d: Path) -> bool:
    lc = d / "lc"
    return all(not f.read_text().strip() for f in (lc.iterdir() if lc.exists() else ())) and \
        not any((d / "goc").iterdir()) and not list(d.glob("g3b-toi-*"))


def lenh_ghi_tk(nk: str) -> list[str]:
    return [l for l in nk.splitlines() if l.startswith("sudo ") and
            any(c in l for c in (" bootstrap login/", " bootstrap gui/", " submit "))]


@pytest.mark.parametrize("ma_user", ["0", "5"])
def test_chu_mien_doi_chung_dat_tram_kiem_user_chi_ghi_nhan(tmp_path, ma_user):
    r, nk = chay(tmp_path, G3_PS_GIA="1", G3_RC_USER=ma_user)
    assert r.returncode == 0 and "G3.9: ỨNG VIÊN ĐẠT" in r.stdout, r.stdout
    assert "đối chứng dương chủ miền: ĐẠT" in r.stdout and len(lenh_ghi_tk(nk)) == 3
    assert nk.index(f"bootstrap gui/{TOI}") < nk.index("bootstrap user/503") < nk.index("bootstrap login/")
    if ma_user == "5":
        assert "tram-kiem không nạp được job vào miền của chính nó (đo 5)" in r.stdout
    else:
        assert "khác lần đo 18/10" in r.stdout
        assert "bộ đọc ảnh có job: user/503: 1 dịch vụ launchd ngoài mốc" in r.stdout
        assert "bộ đọc sau gỡ: sạch" in r.stdout
    assert sach(tmp_path) and "DỌN: XONG" in r.stdout and "TU-CHOI" not in nk


@pytest.mark.parametrize("env", [{"G3_RC_TOI": "5"}, {"G3_TOI_AN": "1"},
                                  {"G3_TOI_PRINT_LOI": "1"}, {"G3_TOI_GO_RC": "5"}])
def test_chu_mien_doi_chung_loi_dung_truoc_tram_kiem_thu_ghi(tmp_path, env):
    r, nk = chay(tmp_path, G3_PS_GIA="1", **env)
    assert r.returncode == 1 and "G3.9 KHÔNG KẾT LUẬN" in r.stdout, r.stdout
    assert not lenh_ghi_tk(nk) and "bootstrap user/503" not in nk
    assert "ỨNG VIÊN" not in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path)


def test_ngat_giua_doi_chung_chu_mien_van_go_nhan(tmp_path):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)], env=moi_truong(d, G3_PS_GIA="1", G3_TRE_TOI="3"),
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while not (d / "toi-da-nap").exists():
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        p.send_signal(signal.SIGTERM)
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)
    assert p.returncode == 143 and "DỌN: XONG" in ra and sach(d), ra
    assert "đã gỡ vn.tram.g3b." in ra and f"khỏi gui/{TOI}" in ra
    assert not lenh_ghi_tk(nhat_ky(d))


def test_khong_gia_va_khong_terminal_thi_khong_chay_gi():
    e = {k: v for k, v in os.environ.items() if not k.startswith("G3_")}
    r = subprocess.run(["/bin/bash", str(KB)], env=e, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       timeout=30)
    assert r.returncode == 2 and "Không chạy" in r.stdout


def test_moi_dieu_kien_dat_chi_la_ung_vien_va_don_co_xac_nhan(tmp_path):
    r, nk = chay(tmp_path)
    assert r.returncode == 0, r.stdout
    for chu in ("ps-sau: 0 dòng", "xet_user user-3: sạch", "asid(procinfo)=100003 handle(gui/",
                "bộ đọc ảnh có job: user/503: 1 dịch vụ launchd ngoài mốc", "bộ đọc sau gỡ: sạch",
                "đối chứng dương chủ miền: ĐẠT", "G3.9: ỨNG VIÊN ĐẠT", "lần 5: 0 tiến trình", "DỌN: XONG"):
        assert chu in r.stdout, chu
    assert sach(tmp_path) and "TU-CHOI" not in nk and "sudo -n -H -u tram-kiem /bin/kill -KILL -1" in nk
    assert nk.index(f"bootstrap gui/{TOI}") < nk.index("bootstrap user/503") < nk.index("bootstrap login/100003")
    assert "bootstrap login/100003" in lenh_ghi_tk(nk)[0] and "bootstrap gui/" in lenh_ghi_tk(nk)[1]


def test_distnoted_cua_he_thong_khong_tinh_la_tien_trinh_tram_kiem(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999998 1 503 503 /usr/sbin/distnoted\n")      # macOS tự bật lại, ppid 1
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0 and "G3.9: ỨNG VIÊN ĐẠT" in r.stdout and "DỌN: XONG" in r.stdout, r.stdout


def test_dich_vu_apple_da_do_khong_tinh_ke_ca_khi_xuat_hien_giua_chung(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999997 1 503 503 /usr/libexec/trustd\n"
                               "999996 1 503 503 /System/Library/Frameworks/CoreServices.framework/Frameworks/"
                               "Metadata.framework/Versions/A/Support/mdworker_shared\n")
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0 and "G3.9: ỨNG VIÊN ĐẠT" in r.stdout and "DỌN: XONG" in r.stdout, r.stdout


def test_duong_dan_gia_dang_apple_van_bi_chan(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999995 1 503 503 /Users/Shared/tram-kiem/trustd\n")
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 1 and "không giết" in r.stdout and nhat_ky(d).count("bootstrap") == 0


def test_distnoted_khong_do_launchd_bat_van_bi_chan(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999998 4242 503 503 /usr/sbin/distnoted\n")
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 1 and "không giết" in r.stdout and nhat_ky(d).count("bootstrap") == 0


def test_tram_kiem_dang_co_tien_trinh_thi_dung_khong_giet_khong_lam_gi(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999999 1 503 503 /tmp/la\n")
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 1 and "999999 1 503 503 khac" in r.stdout and "không giết" in r.stdout
    assert nhat_ky(d) == "" and "DỌN: XONG" in r.stdout        # không một lệnh sudo/launchctl nào


@pytest.mark.parametrize("env, chu", [
    ({"G3_UID_KIEM": TOI}, "UID tram-kiem = 0 hoặc = UID vận hành"),
    ({"G3_PS": "rac1@print-gui-tk"}, "G3.8: không đọc được bảng tiến trình (lượt 1)"),
    ({"G3_PS": "loi1@print-gui-tk"}, "G3.8: không đọc được bảng tiến trình (lượt 1)"),
    ({"G3_PRINT_LOI_LAN": "3"}, "G3.8: print user-3 lỗi"),
    ({"G3_GUI_LECH": "1"}, "G3.8: print gui/503 khác dạng đã đo"),
    ({"G3_TK_THEM": "1@print-gui-tk"}, "G3.8: print sinh tiến trình dưới tram-kiem"),
    ({"G3_ASID": "1"}, "ASID không xác minh được")])
def test_buoc_do_khong_dat_thi_dung_truoc_moi_lenh_ghi_vao_mien_dai_ca(tmp_path, env, chu):
    r, nk = chay(tmp_path, **env)               # lỗi thoáng qua (…1): dọn sau đó sạch, không che lỗi đo
    assert r.returncode == 1 and "DỪNG: " + chu in r.stdout and "DỌN: XONG" in r.stdout, r.stdout
    assert "bootstrap login/" not in nk and "bootstrap gui/" not in nk and "submit" not in nk
    assert "ỨNG VIÊN" not in r.stdout and sach(tmp_path)
    assert "bootstrap" not in nk


def test_tram_kiem_nap_duoc_nhung_bo_doc_lech_thi_van_dung(tmp_path):
    r, nk = chay(tmp_path, G3_PS_GIA="1", G3_RC_USER="0", G3_CO_VIEC_LECH="1")
    assert r.returncode == 1 and "kiểm bộ đọc user/503 không đạt" in r.stdout, r.stdout
    assert not lenh_ghi_tk(nk) and "ỨNG VIÊN" not in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path)


def test_procinfo_loi_thi_khong_dung_asid_va_khong_bao_xong(tmp_path):
    r, nk = chay(tmp_path, G3_RC_PROCINFO="1")
    assert r.returncode == 3 and "procinfo mã 1 — không dùng ASID" in r.stdout and "bootstrap" not in nk
    assert "CHƯA XÁC NHẬN: procinfo" in r.stdout and "DỌN: XONG" not in r.stdout


@pytest.mark.parametrize("tin", [signal.SIGTERM, signal.SIGHUP, signal.SIGALRM])
def test_ngat_khi_procinfo_chua_xac_nhan_thi_khong_bao_xong(tmp_path, tin):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)],
                         env=moi_truong(d, G3_TRE_PROCINFO="3", G3_RC_PROCINFO="1"),
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while " procinfo " not in nhat_ky(d):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        p.send_signal(tin)                   # chỉ PID kịch bản do test tạo; procinfo giả sắp trả lỗi
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)
    assert p.returncode == 3 and "CHƯA XÁC NHẬN: procinfo" in ra, ra
    assert "DỌN: XONG" not in ra and "ỨNG VIÊN" not in ra
    assert "bootstrap" not in nhat_ky(d) and "submit" not in nhat_ky(d)
    assert sach(d)


@pytest.mark.parametrize("env, sau, cam", [
    ({"G3_RC_LOGIN": "0"}, "bootstrap login/", ("bootstrap gui/", "submit")),
    ({"G3_RC_LOGIN": "0", "G3_AN": "1"}, "bootstrap login/", ("bootstrap gui/", "submit")),   # thành công không nhãn
    ({"G3_LOGIN_LOT": "1"}, "bootstrap login/", ("bootstrap gui/", "submit")),
    ({"G3_RC_GUI": "0"}, "bootstrap gui/", ("submit",)),
    ({"G3_SUBMIT": f"gui/{TOI}"}, "submit", ())])
def test_ghi_lot_mien_dai_ca_thi_dung_ngay_ma_4_va_go(tmp_path, env, sau, cam):
    r, nk = chay(tmp_path, **env)
    assert r.returncode == 4 and "DỪNG S6" in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path), r.stdout
    for chu in cam:
        assert chu not in nk[nk.index(sau):], nk


@pytest.mark.parametrize("env, chu", [({"G3_TK_THEM": "0@bootout"}, "lần 1: 1 tiến trình"),
                                      ({"G3_TK_THEM": "0@bootout", "G3_TK_DONG": f"999999 1 503 {TOI} x"},
                                       "lần 1: 1 tiến trình"),
                                      ({"G3_TK_THEM": "0@bootout", "G3_TK_DONG": f"999999 1 {TOI} 503 x"},
                                       "lần 1: 1 tiến trình"),
                                      ({"G3_PS": "rac@bootout"}, "lần 1: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_PS": "loi@bootout"}, "lần 5: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_PS": "rong@bootout"}, "lần 1: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_BOOTOUT_HONG": "1"}, "CHƯA XÁC NHẬN gỡ")])
def test_don_con_sot_hay_khong_dem_duoc_thi_khong_bao_sach(tmp_path, env, chu):
    r, _ = chay(tmp_path, **env)
    assert r.returncode == 3 and chu in r.stdout and "DỌN: CHƯA XÁC NHẬN" in r.stdout, r.stdout
    assert "DỌN: XONG" not in r.stdout


def test_bi_ngat_giua_chung_van_don_va_xac_nhan(tmp_path):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)], env=moi_truong(d, G3_TRE_LOGIN="3"), stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while "bootstrap login/" not in nhat_ky(d):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        p.send_signal(signal.SIGTERM)          # chính tiến trình kịch bản do test tạo
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
    assert p.returncode == 143 and "bị ngắt (TERM)" in ra and "DỌN: XONG" in ra and sach(d), ra
    assert not any("bootstrap gui/" in l for l in lenh_ghi_tk(nhat_ky(d)))


def test_het_han_tong_thi_dung_va_don(tmp_path):
    """Đo thời gian THẬT. Sự thật của bash (R4-02, giới hạn đã biết): trap ALRM chỉ chạy khi lệnh đang chờ kết thúc —
    bootstrap giả trễ 12 s nên kịch bản dừng SAU ~12 s, không phải ở giây 6; vẫn trong độ trễ lệnh giả + biên độ."""
    t = time.monotonic()
    r, nk = chay(tmp_path, G3_TRE_LOGIN="12", G3_HAN_TONG="6")
    tg = time.monotonic() - t
    assert r.returncode == 142 and "HẠN TỔNG 6s hết" in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path)
    assert not any("bootstrap gui/" in l for l in lenh_ghi_tk(nk)) and 12 <= tg < 12 + 10, tg


def test_khoa_co_san_thi_khong_chay_gi(tmp_path):
    d = dung(tmp_path)
    (d / "out" / "g3b.khoa").mkdir(parents=True)
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 2 and "đang có lần đo khác hoặc khoá sót" in r.stdout and nhat_ky(d) == "", r.stdout
    assert (d / "out" / "g3b.khoa").is_dir()                  # khoá không phải của lần này: không gỡ


def test_hai_lan_chong_nhau_lan_sau_khong_sudo(tmp_path):
    d = dung(tmp_path)
    # bs-2bd.1.29: trước đây lần một chỉ trễ 5 s cố định — máy bận thì lần một chạy tiếp và ghi nhật ký trong lúc lần hai
    # chạy, `sau` lẫn dòng của lần một. Nay lần một đứng ở cổng tệp tới khi lần hai xong.
    cong = d / "cho-lan-mot"
    p = subprocess.Popen(["/bin/bash", str(KB)], env=moi_truong(d, G3_CHO_TEP=str(cong)), stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        # Chờ dòng của chính `launchctl` giả (ghi ngay trước cổng), không phải dòng `sudo` ghi trước nó — chờ dòng sudo
        # thì dòng launchctl có thể rơi vào `sau` khi máy bận.
        while not any(l.startswith("launchctl bootstrap login/") for l in nhat_ky(d).splitlines()):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        truoc = nhat_ky(d)
        r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=60)
        sau = nhat_ky(d)[len(truoc):]
        cong.touch()
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
    assert r.returncode == 2 and "đang có lần đo khác" in r.stdout and sau == "", sau
    assert p.returncode == 0 and "DỌN: XONG" in ra and not (d / "out" / "g3b.khoa").exists()


def test_khong_doc_duoc_bien_nhan_khi_don_thi_chua_xac_nhan(tmp_path):
    r, _ = chay(tmp_path, G3_KHOA_BN="1")
    assert r.returncode == 3 and "CHƯA XÁC NHẬN: không đọc được biên nhận" in r.stdout and "DỌN: XONG" not in r.stdout
    assert (tmp_path / "out" / "g3b.khoa").is_dir()           # dọn chưa xác nhận: giữ khoá


def test_khong_ghi_duoc_bang_tong_g38_thi_dung_truoc_moi_lenh_ghi(tmp_path):
    r, nk = chay(tmp_path, G3_HONG_PS_SAU="1")
    assert r.returncode == 1 and "G3.8: không ghi được bảng tổng ps-sau" in r.stdout and "bootstrap" not in nk
    assert "DỌN: XONG" in r.stdout and not (tmp_path / "out" / "g3b.khoa").exists()
