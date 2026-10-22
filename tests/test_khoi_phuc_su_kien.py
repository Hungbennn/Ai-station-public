"""bs-2bd.1.17: `tram chu khoi-phuc-su-kien <bản>` — đọc bản qua fd vào bộ nhớ, kiểm cấu trúc đúng kho của mã, khoá bảo
trì chứng minh không còn ai mở kho, sao lưu kho hiện tại độc quyền, thay trong một giao dịch, đọc lại kiểm khớp.
Chỉ TRAM_HOME tạm của test."""
import os
import sqlite3
import stat
import subprocess
import sys

import pytest

from tram.chu import khoi_phuc_su_kien as kp
from tram.chu.khoi_phuc_su_kien import LoiKhoiPhuc, khoi_phuc
from tram.su_kien import ban_sao
from tram.su_kien.kho import KhoSuKien
from tram.su_kien.phien_ban import PHIEN_BAN
from tram.su_kien.sao_luu import sao_luu

LUC = "2026-10-17T05:06:07Z"


def dem(p):
    db = sqlite3.connect(p)
    try:
        return db.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    finally:
        db.close()


@pytest.fixture
def nha(tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    kho = tram_home_tam / "su-kien.db"
    k = KhoSuKien(kho)
    k.ghi("hr", "a", {})
    ban = sao_luu(kho, tram_home_tam / "sao-luu", luc="2026-10-16T00:00:00Z")
    k.ghi("hr", "b", {})
    k.close()
    return kho, ban, tram_home_tam / "sao-luu"


def test_khoi_phuc_sao_luu_hien_tai_roi_thay(nha):
    kho, ban, sl = nha
    truoc = khoi_phuc(ban.name, kho, sl, luc=LUC)
    assert truoc == sl / "truoc-khoi-phuc-20261017T050607Z.db"
    assert dem(kho) == 1 and dem(truoc) == 2 and dem(ban) == 1
    assert all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in (kho, truoc))
    k = KhoSuKien(kho)                                                   # kho mở lại bình thường sau khôi phục
    k.close()


def _tao(sl, ten, noi_dung):
    p = sl / ten
    if isinstance(noi_dung, bytes):
        p.write_bytes(noi_dung)
    else:
        db = sqlite3.connect(p)
        db.executescript(noi_dung)
        db.close()
    return p


@pytest.mark.parametrize("ten, noi_dung", [
    ("rac.db", b"khong phai sqlite" * 10),
    ("khac.db", "CREATE TABLE t (x);"),
    ("chi-id.db", "CREATE TABLE su_kien (id INTEGER PRIMARY KEY);"),                 # có bảng su_kien nhưng sai cột
    ("bang-la.db", "CREATE TABLE su_kien (id INTEGER PRIMARY KEY, luc TEXT NOT NULL, du_an TEXT NOT NULL, bead_id "
                   "TEXT, loai TEXT NOT NULL, tac_nhan TEXT NOT NULL, du_lieu TEXT NOT NULL, token_vao INTEGER, "
                   "token_ra INTEGER, mo_hinh TEXT, thoi_gian_ms INTEGER); CREATE TABLE la (x);"),
    ("moi-hon.db", f"CREATE TABLE su_kien (id INTEGER PRIMARY KEY); PRAGMA user_version = {PHIEN_BAN + 1};"),
    ("rong-co-phien-ban.db", f"PRAGMA user_version = {PHIEN_BAN};"),                # SQLite hợp lệ, không bảng nào
    ("duoi.txt", "CREATE TABLE su_kien (id INTEGER PRIMARY KEY);")])
def test_ban_hong_hay_sai_cau_truc_thi_tu_choi_khong_dung_kho(nha, ten, noi_dung):
    kho, _, sl = nha
    _tao(sl, ten, noi_dung)
    with pytest.raises(LoiKhoiPhuc) as e:
        khoi_phuc(ten, kho, sl, luc=LUC)
    assert str(sl) not in str(e.value) and dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


def test_ban_lien_ket_mem_cung_hay_chinh_kho_thi_tu_choi(nha, tmp_path):
    kho, ban, sl = nha
    (tmp_path / "ngoai.db").write_bytes(ban.read_bytes())
    (sl / "mem.db").symlink_to(tmp_path / "ngoai.db")
    os.link(tmp_path / "ngoai.db", sl / "cung.db")
    os.link(kho, sl / "chinh-kho.db")
    for ten in ("mem.db", "cung.db", "chinh-kho.db", "../su-kien.db"):
        with pytest.raises(LoiKhoiPhuc):
            khoi_phuc(ten, kho, sl, luc=LUC)
    assert dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


def test_con_ket_noi_mo_kho_thi_tu_choi(nha):
    kho, ban, sl = nha
    k = KhoSuKien(kho)                                         # như api/nho đang chạy, đã đọc kho
    try:
        k.gan_day("hr", "a", 1)
        with pytest.raises(LoiKhoiPhuc, match="Còn tiến trình"):
            khoi_phuc(ban.name, kho, sl, luc=LUC)
    finally:
        k.close()
    assert dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


def test_tien_trinh_khac_mo_kho_thi_tu_choi(nha):
    kho, ban, sl = nha
    ma = ("import sqlite3, sys, time\nd = sqlite3.connect(sys.argv[1])\nd.execute('SELECT count(*) FROM su_kien')"
          ".fetchone()\nprint('mo', flush=True)\ntime.sleep(30)\n")
    con = subprocess.Popen([sys.executable, "-c", ma, str(kho)], stdout=subprocess.PIPE, text=True)
    try:
        assert con.stdout.readline().strip() == "mo"
        with pytest.raises(LoiKhoiPhuc, match="Còn tiến trình"):
            khoi_phuc(ban.name, kho, sl, luc=LUC)
    finally:
        con.terminate()
        con.wait(10)
    assert dem(kho) == 2


def test_ban_trung_ten_truoc_khoi_phuc_khong_bi_ghi_de(nha):
    kho, ban, sl = nha
    trung = sl / "truoc-khoi-phuc-20261017T050607Z.db"
    trung.write_bytes(ban.read_bytes())
    truoc = khoi_phuc(trung.name, kho, sl, luc=LUC)
    assert truoc.name == "truoc-khoi-phuc-20261017T050607Z-2.db" and dem(trung) == 1 and dem(kho) == 1


def test_sao_luu_kho_hien_tai_loi_thi_chua_doi_gi(nha, monkeypatch):
    kho, ban, sl = nha

    def hong(*a, **k):
        raise ban_sao.LoiBanSao("quá hạn")
    monkeypatch.setattr(ban_sao, "chup", hong)
    with pytest.raises(LoiKhoiPhuc, match="chưa đổi gì"):
        khoi_phuc(ban.name, kho, sl, luc=LUC)
    assert dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


@pytest.mark.parametrize("sai", ["chi-muc-thuong", "chi-muc-thieu-where"])
def test_chi_muc_cung_ten_sai_tinh_duy_nhat_hay_where_thi_tu_choi(nha, sai):
    """R2-06: `phieu_mot_bead` là ràng buộc UNIQUE có điều kiện chống cấp trùng phiếu — cùng tên mà khác thì từ chối."""
    from tram.phieu.luoc_do import LUOC_DO
    kho, ban, sl = nha
    p = sl / f"{sai}.db"
    p.write_bytes(ban.read_bytes())
    db = sqlite3.connect(p)
    db.executescript(LUOC_DO + "DROP INDEX phieu_mot_bead;")
    db.execute("CREATE INDEX phieu_mot_bead ON phieu(du_an, bead_id) WHERE trang_thai = 'hieu_luc'" if sai ==
               "chi-muc-thuong" else "CREATE UNIQUE INDEX phieu_mot_bead ON phieu(du_an, bead_id)")
    db.commit()
    db.close()
    with pytest.raises(LoiKhoiPhuc, match="không đúng cấu trúc"):
        khoi_phuc(p.name, kho, sl, luc=LUC)
    assert dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


@pytest.mark.parametrize("ap, khop", [("hong", "giữ nguyên"), ("khong-lam", "không khớp")])
def test_buoc_thay_loi_thi_kho_y_nguyen_va_chi_duong_lui(nha, monkeypatch, ap, khop):
    kho, ban, sl = nha

    def hong(nguon, db):
        raise sqlite3.OperationalError("đĩa đầy")
    monkeypatch.setattr(kp, "_ap_ban", hong if ap == "hong" else lambda nguon, db: None)
    with pytest.raises(LoiKhoiPhuc, match=khop) as e:
        khoi_phuc(ban.name, kho, sl, luc=LUC)
    assert dem(kho) == 2 and "truoc-khoi-phuc-20261017T050607Z.db" in str(e.value)


def test_loi_sau_khi_chep_xong_khong_bao_giu_nguyen(nha, monkeypatch):
    """R2-06: bước chép đã ghi vào kho rồi mới lỗi → KHÔNG được nói "kho giữ nguyên"; chỉ đường lui."""
    kho, ban, sl = nha
    that = kp._ap_ban

    def chep_roi_hong(nguon, db):
        that(nguon, db)
        raise sqlite3.OperationalError("lỗi sau khi chép")
    monkeypatch.setattr(kp, "_ap_ban", chep_roi_hong)
    with pytest.raises(LoiKhoiPhuc, match="KHÔNG còn như trước") as e:
        khoi_phuc(ban.name, kho, sl, luc=LUC)
    assert dem(kho) == 1 and "truoc-khoi-phuc-20261017T050607Z.db" in str(e.value)


def test_buoc_chep_qua_han_giua_cac_buoc_thi_kho_y_nguyen(nha, monkeypatch):
    """R2-06: bước chép có hạn; quá hạn giữa các bước → SQLite hoàn tác giao dịch của đích, kho kiểm lại y nguyên."""
    kho, ban, sl = nha
    dong_ho = iter(range(0, 10_000, 100))                               # mỗi lần hỏi +100 giây
    monkeypatch.setattr(kp, "SO_TRANG_AP", 1)
    monkeypatch.setattr(kp, "_dong_ho", lambda: next(dong_ho))
    with pytest.raises(LoiKhoiPhuc, match="giữ nguyên"):
        khoi_phuc(ban.name, kho, sl, luc=LUC)
    assert dem(kho) == 2


def test_where_doi_hoa_thuong_trong_chuoi_phai_tu_choi(nha):
    from tram.phieu.luoc_do import LUOC_DO
    kho, ban, sl = nha
    p = sl / "where-hoa.db"
    p.write_bytes(ban.read_bytes())
    db = sqlite3.connect(p)
    try:
        db.executescript(LUOC_DO + "DROP INDEX phieu_mot_bead;")
        db.execute("CREATE UNIQUE INDEX phieu_mot_bead ON phieu(du_an, bead_id) "
                   "WHERE trang_thai = 'HIEU_LUC'")
        db.commit()
    finally:
        db.close()
    with pytest.raises(LoiKhoiPhuc, match="không đúng cấu trúc"):
        khoi_phuc(p.name, kho, sl, luc=LUC)
    assert dem(kho) == 2 and not list(sl.glob("truoc-khoi-phuc-*"))


def test_chuan_hoa_sql_giu_nguyen_chuoi():
    from tram.chu.cau_truc_su_kien import _sql
    assert _sql("SELECT 'a--b' -- ghi chu\n") == _sql("select 'a--b'")
    assert _sql("SELECT 'a  b'") != _sql("select 'a b'")
    assert _sql("SELECT 'A'") != _sql("select 'a'")
    assert _sql("SELECT 'a''B'") != _sql("select 'a''b'")


@pytest.mark.parametrize("trang_thai", [sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED])
def test_chep_ban_ban_truoc_trang_dau_van_co_han(monkeypatch, trang_thai):
    class Nguon:
        def backup(self, db, *, pages, progress):
            progress(trang_thai, 0, 0)       # chưa đọc được kích thước kho, không phải SQLITE_DONE
            pytest.fail("đã hết hạn mà vẫn tiếp tục backup")
    moc = iter([0.0, 61.0])
    monkeypatch.setattr(kp, "_dong_ho", lambda: next(moc))
    with pytest.raises(ban_sao.LoiBanSao, match="quá hạn"):
        kp._ap_ban(Nguon(), None)


def test_cli_nhac_dung_dich_vu_ke_ca_nho_va_cho_dong_y(nha, monkeypatch, capsys):
    from tram.cli import main
    kho, ban, _ = nha
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    assert main(["chu", "khoi-phuc-su-kien", ban.name]) == 1 and dem(kho) == 2
    out = capsys.readouterr().out
    assert "go-dich-vu" in out and "--dich-vu nho" in out and ban.name in out
    assert main(["chu", "khoi-phuc-su-kien", ban.name, "--dong-y"]) == 0 and dem(kho) == 1
    assert main(["chu", "khoi-phuc-su-kien", "khong-co.db", "--dong-y"]) == 2
