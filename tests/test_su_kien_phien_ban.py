"""bs-2bd.1.3: `su-kien.db` có số phiên bản cấu trúc (`PRAGMA user_version`); nâng trong khoá ghi, đọc lại phiên bản
trong khoá, sao lưu độc quyền 600 có hạn, lỗi thì kho y nguyên; kho mới hơn mã thì từ chối. Chỉ DB tạm (tmp_path)."""
import itertools
import os
import sqlite3
import stat
import threading
import time
from functools import partial
from pathlib import Path

import pytest

from tram.phieu.kho import KhoPhieu
from tram.su_kien import ban_sao
from tram.su_kien.ket_noi import mo_kho_su_kien
from tram.su_kien.kho import KhoSuKien
from tram.su_kien.phien_ban import PHIEN_BAN, LoiPhienBan, nang_cap, phien_ban
from tram.thao_tac.kho import KhoThaoTac
from tram.yeu_cau.so_nhan import SoNhan

CU = "CREATE TABLE su_kien (id INTEGER PRIMARY KEY, luc TEXT NOT NULL, du_an TEXT NOT NULL, bead_id TEXT, " \
     "loai TEXT NOT NULL, tac_nhan TEXT NOT NULL, du_lieu TEXT NOT NULL, token_vao INTEGER, token_ra INTEGER, " \
     "mo_hinh TEXT, thoi_gian_ms INTEGER)"
LEN_2 = {1: (), 2: ("ALTER TABLE su_kien ADD COLUMN thu TEXT",)}


def kho_cu(p, user_version=0, dong=1):
    """Kho viết trước lát này: có bảng, có dòng, user_version cho trước."""
    db = sqlite3.connect(p)
    db.execute(CU)
    db.executemany("INSERT INTO su_kien (luc, du_an, loai, tac_nhan, du_lieu) VALUES ('t', 'hr', 'x', 'a', ?)",
                   [("{}" + " " * 400,)] * dong)
    db.execute(f"PRAGMA user_version = {user_version}")
    db.commit()
    db.close()


def cot(p):
    db = sqlite3.connect(p)
    try:
        return [r[1] for r in db.execute("PRAGMA table_info(su_kien)")]
    finally:
        db.close()


def test_kho_moi_dong_dau_khong_sao_luu(tmp_path):
    db = mo_kho_su_kien(tmp_path / "su-kien.db")
    try:
        assert PHIEN_BAN >= 1 and phien_ban(db) == PHIEN_BAN
    finally:
        db.close()
    assert not (tmp_path / "sao-luu").exists()


def test_kho_cu_sao_luu_truoc_roi_nang(tmp_path):
    kho_cu(tmp_path / "su-kien.db")
    k = KhoSuKien(tmp_path / "su-kien.db")
    try:
        assert phien_ban(k._db) == PHIEN_BAN and len(k.gan_day("hr", "x", 5)) == 1
    finally:
        k.close()
    (ban,) = (tmp_path / "sao-luu").glob("truoc-nang-v0-v*.db")
    assert stat.S_IMODE(ban.stat().st_mode) == 0o600 and stat.S_IMODE((tmp_path / "sao-luu").stat().st_mode) == 0o700
    sl = sqlite3.connect(ban)
    assert sl.execute("PRAGMA user_version").fetchone()[0] == 0
    assert sl.execute("SELECT count(*) FROM su_kien").fetchone()[0] == 1
    sl.close()


@pytest.mark.parametrize("mo", [KhoSuKien, KhoPhieu, KhoThaoTac, SoNhan])
def test_kho_moi_hon_ma_bi_tu_choi_khong_ghi(tmp_path, mo):
    p = tmp_path / "su-kien.db"
    kho_cu(p, user_version=PHIEN_BAN + 1)
    with pytest.raises(LoiPhienBan) as e:
        mo(p)
    assert str(tmp_path) not in str(e.value)
    db = sqlite3.connect(p)
    assert db.execute("PRAGMA user_version").fetchone()[0] == PHIEN_BAN + 1
    assert [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")] == ["su_kien"]
    db.close()
    assert not (tmp_path / "sao-luu").exists()


def test_buoc_sau_ap_trong_giao_dich_va_mot_lan(tmp_path):
    kho_cu(tmp_path / "k.db", user_version=1)
    db = sqlite3.connect(tmp_path / "k.db")
    try:
        assert nang_cap(db, thu_muc_sao_luu=tmp_path / "sl", buoc=LEN_2, moi=2, luc="2026-10-17T00:00:00Z")
        assert nang_cap(db, thu_muc_sao_luu=tmp_path / "sl", buoc=LEN_2, moi=2) is None      # đến sau: không áp
        assert phien_ban(db) == 2 and "thu" in cot(tmp_path / "k.db")
    finally:
        db.close()
    assert [p.name for p in (tmp_path / "sl").iterdir()] == ["truoc-nang-v1-v2-20261017T000000Z.db"]


def test_buoc_loi_rollback_kho_y_nguyen(tmp_path):
    kho_cu(tmp_path / "k.db", user_version=1)
    buoc = {1: (), 2: ("ALTER TABLE su_kien ADD COLUMN thu TEXT", "CREATE TABLE hong (")}
    db = sqlite3.connect(tmp_path / "k.db")
    try:
        with pytest.raises(LoiPhienBan):
            nang_cap(db, thu_muc_sao_luu=tmp_path / "sl", buoc=buoc, moi=2)
        assert phien_ban(db) == 1 and "thu" not in cot(tmp_path / "k.db") and not db.in_transaction
    finally:
        db.close()
    assert len(list((tmp_path / "sl").iterdir())) == 1                   # bản sao lưu trước khi nâng vẫn còn


def test_thieu_buoc_la_loi_lap_trinh(tmp_path):
    db = sqlite3.connect(tmp_path / "k.db")
    try:
        with pytest.raises(LoiPhienBan):
            nang_cap(db, thu_muc_sao_luu=tmp_path / "sl", buoc={1: ()}, moi=2)
        assert phien_ban(db) == 0
    finally:
        db.close()


def _hai_tien_trinh(tmp_path, buoc_b, moi_b):
    """A giữ khoá ghi (đang chụp bản sao) trong lúc B mở cùng kho; nhả A rồi chờ B. Trả (kết quả A, kết quả B)."""
    p, sl = tmp_path / "k.db", tmp_path / "sl"
    kho_cu(p, user_version=0)
    a_giu, nha_a, kq = threading.Event(), threading.Event(), {}

    def chup_cham(src):
        a_giu.set()
        nha_a.wait(10)
        return ban_sao.chup(src)

    def chay(ten, **kw):
        db = sqlite3.connect(p, timeout=10)
        try:
            kq[ten] = nang_cap(db, thu_muc_sao_luu=sl, **kw)
        except LoiPhienBan as e:
            kq[ten] = e
        finally:
            db.close()
    a = threading.Thread(target=chay, args=("a",), kwargs={"buoc": LEN_2, "moi": 2, "chup": chup_cham})
    b = threading.Thread(target=chay, args=("b",), kwargs={"buoc": buoc_b, "moi": moi_b})
    a.start()
    assert a_giu.wait(10)
    b.start()
    time.sleep(0.3)                                  # B đã đọc nhanh (v0) và đang chờ khoá ghi
    nha_a.set()
    a.join(10)
    b.join(10)
    return kq["a"], kq["b"], list(sl.iterdir()), p


def test_hai_tien_trinh_cung_nang_chi_mot_ban_sao_mot_lan_ap(tmp_path):
    a, b, ban, p = _hai_tien_trinh(tmp_path, LEN_2, 2)
    assert a is not None and b is None and len(ban) == 1                 # B đọc lại trong khoá: đã v2, không áp lại
    assert cot(p).count("thu") == 1


def test_ben_kia_vua_nang_cao_hon_ma_thi_tu_choi(tmp_path):
    a, b, ban, p = _hai_tien_trinh(tmp_path, {1: ()}, 1)
    assert isinstance(b, LoiPhienBan) and "chỉ hiểu tới 1" in str(b) and len(ban) == 1


def test_kho_dang_bi_khoa_ghi_thi_loi_co_han(tmp_path):
    kho_cu(tmp_path / "k.db")
    giu = sqlite3.connect(tmp_path / "k.db", isolation_level=None)
    giu.execute("BEGIN IMMEDIATE")
    db = sqlite3.connect(tmp_path / "k.db", timeout=0.2)
    bat_dau = time.monotonic()
    try:
        with pytest.raises(LoiPhienBan, match="khoá ghi"):
            nang_cap(db, thu_muc_sao_luu=tmp_path / "sl")
        assert time.monotonic() - bat_dau < 5 and phien_ban(db) == 0
    finally:
        db.close()
        giu.execute("ROLLBACK")
        giu.close()
    assert not (tmp_path / "sl").exists()


def test_sao_luu_qua_han_bo_khong_de_ban_do(tmp_path):
    kho_cu(tmp_path / "k.db", dong=300)                                  # nhiều trang: chụp nhiều bước
    dong_ho = itertools.count()                                          # đồng hồ giả: mỗi lần hỏi +1 giây
    chup = partial(ban_sao.chup, han=3, so_trang=1, dong_ho=lambda: next(dong_ho))
    db = sqlite3.connect(tmp_path / "k.db")
    try:
        with pytest.raises(LoiPhienBan, match="hoàn tác"):
            nang_cap(db, thu_muc_sao_luu=tmp_path / "sl", chup=chup)
        assert phien_ban(db) == 0 and not db.in_transaction
    finally:
        db.close()
    assert not (tmp_path / "sl").exists()                                 # chụp hỏng trước khi tạo gì trên đĩa


def test_ban_sao_doc_quyen_khong_ghi_de_khong_theo_lien_ket(tmp_path):
    sl, ngoai = tmp_path / "sl", tmp_path / "ngoai.txt"
    ngoai.write_text("của người khác")
    sl.mkdir(mode=0o755)
    os.chmod(sl, 0o755)
    (sl / "b.db").symlink_to(ngoai)
    (sl / "b-2.db").write_text("bản cũ")
    p = ban_sao.ghi_doc_quyen(sl, "b", b"moi")
    assert p.name == "b-3.db" and p.read_bytes() == b"moi" and stat.S_IMODE(p.stat().st_mode) == 0o600
    assert ngoai.read_text() == "của người khác" and (sl / "b-2.db").read_text() == "bản cũ"
    assert stat.S_IMODE(sl.stat().st_mode) == 0o700                    # thư mục có sẵn 0755 → 700


def test_thu_muc_sao_luu_la_lien_ket_thi_tu_choi(tmp_path):
    (tmp_path / "that").mkdir()
    (tmp_path / "sl").symlink_to(tmp_path / "that")
    with pytest.raises(ban_sao.LoiBanSao) as e:
        ban_sao.ghi_doc_quyen(tmp_path / "sl", "b", b"x")
    assert str(tmp_path) not in str(e.value) and list((tmp_path / "that").iterdir()) == []


def test_cha_cua_thu_muc_sao_luu_la_lien_ket_thi_tu_choi(tmp_path):
    """R2-05: liên kết mềm ở thành phần CHA (không chỉ thành phần cuối) không kéo việc tạo/siết ra ngoài."""
    ngoai = tmp_path / "ngoai"
    ngoai.mkdir()
    os.chmod(ngoai, 0o755)
    (tmp_path / "goc").symlink_to(ngoai)
    with pytest.raises(ban_sao.LoiBanSao) as e:
        ban_sao.ghi_doc_quyen(tmp_path / "goc" / "sao-luu", "b", b"x")
    assert str(tmp_path) not in str(e.value)
    assert list(ngoai.iterdir()) == [] and stat.S_IMODE(ngoai.stat().st_mode) == 0o755


def test_chuoi_cha_nguoi_khac_ghi_duoc_thi_tu_choi(tmp_path):
    chung = tmp_path / "chung"
    chung.mkdir()
    os.chmod(chung, 0o777)
    with pytest.raises(ban_sao.LoiBanSao):
        ban_sao.ghi_doc_quyen(chung / "sao-luu", "b", b"x")
    assert list(chung.iterdir()) == []


def test_lien_ket_he_thong_tren_duong_van_dung_duoc(tmp_path):
    """`/var` của macOS là liên kết do root tạo trong `/`: đi theo được; thành phần thiếu tạo 700 qua fd cha."""
    if not str(tmp_path).startswith("/private/var/"):
        pytest.skip("cần tmp_path dưới /private/var")
    qua_var = Path("/var") / tmp_path.relative_to("/private/var")
    p = ban_sao.ghi_doc_quyen(qua_var / "moi" / "sao-luu", "b", b"x")
    assert (tmp_path / "moi/sao-luu/b.db").read_bytes() == b"x" and p.name == "b.db"
    assert stat.S_IMODE((tmp_path / "moi").stat().st_mode) == 0o700
