"""TM-3 (tu-deploy "Mỗi lệnh có giới hạn thời gian", "Không lọt bí mật qua kết quả deploy"; D100; Codex C1): chạy
một lệnh của chuỗi deploy. Đầu ra đi qua ỐNG, được che trong RAM rồi mới ghi vào log 0600 — byte thô không bao giờ
chạm đĩa, kể cả khi lệnh còn đang chạy, bị ngắt hay quá hạn. Lệnh là script `sh` GIẢ trong thư mục tạm của test."""
import os
import shlex
import signal
import stat
import threading
import time
import tracemalloc

import pytest

from tram.deploy.lenh import DONG_CHE, HAN, KetQuaBuoc, chay_buoc, don_log_cu, moi_truong, thu_muc_log
from tram.duong_dan import tram_home

TOKEN = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
IN_TOKEN = 'printf "token=%s%s\\n" ghp_ A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8'    # file script không chứa nguyên token


def lenh(tmp_path, ten: str, than: str) -> str:
    f = tmp_path / "tram-deploy" / ten
    f.parent.mkdir(exist_ok=True)
    f.write_text(f"#!/bin/sh\n{than}\n")
    return f"/bin/sh {shlex.quote(str(f))}"


def chay(tmp_path, buoc: str, than: str, **kw) -> tuple[KetQuaBuoc, str]:
    tm = thu_muc_log("repo-nhap")
    kq = chay_buoc(buoc, lenh(tmp_path, f"{buoc}.sh", than), cwd=tmp_path, log=tm / "dp-1.log",
                   env=kw.pop("env", moi_truong(os.environ, "repo-nhap", "m5", "m4")))
    return kq, (tm / "dp-1.log").read_text()


def tren_dia(*goc) -> list[str]:
    """Mọi file dưới các gốc đang chứa nguyên chuỗi token."""
    return sorted(str(f) for g in goc for f in g.rglob("*") if f.is_file() and TOKEN.encode() in f.read_bytes())


def cho_file(f, han: float = 10.0) -> bool:
    het = time.monotonic() + han
    while not f.exists() and time.monotonic() < het:
        time.sleep(0.05)
    time.sleep(0.5)                                  # cho bộ đọc của trạm kịp nhận dòng vừa in
    return f.exists()


def song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_moi_truong_toi_thieu():
    goc = {"PATH": "/usr/bin:/bin", "HOME": "/Users/tram", "LANG": "vi_VN.UTF-8", "TRAM_NOI_BO_TOKEN": "x",
           "ANTHROPIC_API_KEY": "y", "PYTHONPATH": "/z"}
    assert moi_truong(goc, "repo-nhap", "m5", "") == {
        "PATH": "/usr/bin:/bin", "HOME": "/Users/tram", "LANG": "vi_VN.UTF-8", "TRAM_DU_AN": "repo-nhap",
        "TRAM_DEPLOY_COMMIT": "m5", "TRAM_DEPLOY_COMMIT_TRUOC": ""}


def test_dat_chay_trong_thu_muc_va_khong_mang_bien_cua_tram_api(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_NOI_BO_TOKEN", "bi-mat-cua-tram-api")
    kq, log = chay(tmp_path, "deploy", 'pwd; echo "commit=$TRAM_DEPLOY_COMMIT truoc=$TRAM_DEPLOY_COMMIT_TRUOC"; env')
    assert kq.dat and kq.ma_thoat == 0 and not kq.het_gio
    assert str(tmp_path) in log and "commit=m5 truoc=m4" in log and "bi-mat-cua-tram-api" not in log
    assert log.startswith("=== deploy\n") and f"\n=== deploy · mã thoát 0 · {kq.giay} giây\n" in log
    assert kq.su_kien() == {"buoc": "deploy", "ma_thoat": 0, "giay": kq.giay, "het_gio": False,
                            "digest_log": kq.digest_log}


def test_lenh_in_token_bi_che_log_0600(tmp_path):
    """Scenario "Lệnh deploy in ra token": sự kiện chỉ mã thoát/giây/digest; file log có chuỗi đó đã bị che; dòng in
    làm hai lần đọc (chưa xuống dòng) vẫn được che theo cả dòng."""
    kq, log = chay(tmp_path, "deploy", f'echo "dang day ban moi"\n{IN_TOKEN}\nprintf "Bearer ghp_A1b2C3d4E5f6"\n'
                                       '/bin/sleep 0.3\necho "G7h8I9j0K1l2M3n4O5p6Q7r8"\nexit 1')
    assert (kq.dat, kq.ma_thoat) == (False, 1)
    assert TOKEN not in log and log.count(DONG_CHE) == 2 and "dang day ban moi" in log and "ghp_" not in log
    assert TOKEN not in str(kq.su_kien())
    tm = thu_muc_log("repo-nhap")
    assert stat.S_IMODE((tm / "dp-1.log").stat().st_mode) == 0o600
    assert {stat.S_IMODE(p.stat().st_mode) for p in (tm, tm.parent)} == {0o700}
    assert [f.name for f in tm.rglob("*") if f.is_file()] == ["dp-1.log"]     # không có file tạm nào


def test_bi_mat_khong_cham_dia_khi_lenh_dang_chay_hay_qua_han(tmp_path, monkeypatch):
    """Codex C1: lệnh đã in token mà còn chạy (trạm chết đúng lúc này thì đĩa giữ gì?) → không file nào chứa token;
    mọi file trong thư mục log 0600 ngay lúc tạo, cả khi umask 000. Quá hạn → thu hồi cả nhóm, vẫn không lộ."""
    monkeypatch.setitem(HAN, "deploy", 4)
    co, kq, cu = tmp_path / "da-in", [], os.umask(0)
    try:
        lu = threading.Thread(target=lambda: kq.append(chay(tmp_path, "deploy",
                                                             f'{IN_TOKEN}\ntouch "{co}"\n/bin/sleep 30')))
        lu.start()
        assert cho_file(co)
        tep = [f for f in thu_muc_log("repo-nhap").rglob("*") if f.is_file()]
        assert tren_dia(tram_home(), tmp_path) == []
        assert tep and {stat.S_IMODE(f.stat().st_mode) for f in tep} == {0o600}
        lu.join(30)
    finally:
        os.umask(cu)
    ((k, log),) = kq
    assert k.het_gio and k.da_thu_hoi and not k.dat and k.giay < 15 and DONG_CHE in log and "quá hạn" in log
    assert tren_dia(tram_home(), tmp_path) == []


def test_ngat_giua_chung_thu_hoi_ca_nhom_khong_de_lai_bi_mat(tmp_path):
    """Codex C1: trạm bị ngắt (SIGINT/SIGTERM) khi lệnh đã in token → thu hồi cả nhóm; không file nào chứa token."""
    co, pid = tmp_path / "da-in", tmp_path / "pid"

    def ban() -> None:
        if cho_file(co):
            os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=ban, daemon=True).start()
    with pytest.raises(KeyboardInterrupt):
        chay(tmp_path, "deploy", f'{IN_TOKEN}\n/bin/sleep 30 &\necho $! > "{pid}"\ntouch "{co}"\nwait')
    assert tren_dia(tram_home(), tmp_path) == []
    con, het = int(pid.read_text()), time.monotonic() + 5
    while song(con) and time.monotonic() < het:
        time.sleep(0.1)
    assert not song(con)


def test_dau_ra_lon_co_tran_khong_giu_het_trong_ram(tmp_path):
    """Codex C1: một dòng 3 MB không xuống dòng + 20 MB dòng thường → log có trần, ghi rõ phần bỏ/cắt; RAM của trạm
    không giữ cả đầu ra."""
    than = ('/usr/bin/head -c 3000000 /dev/zero | /usr/bin/tr "\\000" a\necho\n'
            '/usr/bin/yes "dong binh thuong" | /usr/bin/head -c 20000000')
    tracemalloc.start()
    try:
        kq, log = chay(tmp_path, "deploy", than)
        dinh = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert kq.dat and dinh < 8 * 2 ** 20
    assert "bỏ một dòng dài quá" in log and " · đã cắt " in log.splitlines()[-1]
    assert (thu_muc_log("repo-nhap") / "dp-1.log").stat().st_size < 2 * 2 ** 20


def test_qua_han_giet_ca_nhom_tinh_la_hong(tmp_path, monkeypatch):
    """Scenario "Lệnh deploy treo" (hạn rút ngắn cho test): dừng cả nhóm tiến trình, tính là hỏng."""
    monkeypatch.setitem(HAN, "deploy", 1)
    kq, log = chay(tmp_path, "deploy", "/bin/sleep 30 &\n/bin/sleep 30")
    assert kq.het_gio and not kq.dat and kq.da_thu_hoi and kq.giay < 15
    assert "quá hạn" in log
    assert HAN == {"deploy": 1, "kiem_song": 120, "lui": 900, "kiem_song_sau_lui": 120, "git": 60}


def test_lenh_khong_tach_duoc_thi_khong_chay(tmp_path):
    kq = chay_buoc("lui", "sh 'thieu nhay", cwd=tmp_path, env={}, log=thu_muc_log("repo-nhap") / "dp-2.log")
    assert (kq.dat, kq.ma_thoat, kq.da_thu_hoi) == (False, None, True)


def test_don_log_cu(tmp_path):
    tm = thu_muc_log("repo-nhap")
    cu, moi = tm / "dp-cu.log", tm / "dp-moi.log"
    cu.write_text("x")
    moi.write_text("y")
    os.utime(cu, (0, 0))
    assert don_log_cu(tm) == 1 and not cu.exists() and moi.exists()
