"""bs-2bd.1.4: dữ liệu trạm chủ dưới ~/.tram chỉ chủ đọc được — thư mục 700, file 600; quyền đúng TỪ LÚC TẠO, đổi quyền
đi cây qua fd (không ra ngoài cây khi thư mục cha bị thay giữa chừng). Chỉ TRAM_HOME/tmp_path tạm của test."""
import os
import sqlite3
import stat
import threading

import pytest

from tram.chu.siet_quyen import TRANH, can_siet, di_cay, siet
from tram.su_kien import ban_sao
from tram.su_kien.ket_noi import LoiQuyenKho, mo_ket_noi
from tram.su_kien.sao_luu import sao_luu


def che_do(p):
    return stat.S_IMODE(p.stat().st_mode)


def test_kho_moi_600_ngay_khi_sqlite_tao_wal_shm(tmp_path, monkeypatch):
    p, thay = tmp_path / "moi.db", []
    goc = sqlite3.connect

    def connect(duong, *a, **k):                    # đúng lúc SQLite mở, file kho đã có và đã 600
        thay.append(che_do(p))
        return goc(duong, *a, **k)
    monkeypatch.setattr(sqlite3, "connect", connect)
    mat_na = os.umask(0o022)
    try:
        db = mo_ket_noi(p)
        db.execute("CREATE TABLE t (x)")
        db.execute("INSERT INTO t VALUES (1)")
        db.commit()
        assert thay == [0o600] and all(che_do(tmp_path / f"moi.db{d}") == 0o600 for d in ("", "-wal", "-shm"))
        db.close()
    finally:
        os.umask(mat_na)


def test_kho_cu_rong_quyen_siet_truoc_khi_mo(tmp_path):
    cu = tmp_path / "cu.db"
    db = sqlite3.connect(cu)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE t (x)")
    for d in ("", "-wal", "-shm"):
        os.chmod(f"{cu}{d}", 0o644)
    mo_ket_noi(cu).close()
    db.close()
    assert che_do(cu) == 0o600


def test_kho_la_lien_ket_mem_thi_khong_mo(tmp_path):
    that = tmp_path / "that.db"
    sqlite3.connect(that).close()
    os.chmod(that, 0o644)
    (tmp_path / "su-kien.db").symlink_to(that)
    with pytest.raises(LoiQuyenKho) as e:
        mo_ket_noi(tmp_path / "su-kien.db")
    assert str(tmp_path) not in str(e.value) and che_do(that) == 0o644


def test_ban_sao_luu_600_thu_muc_co_san_0755_thanh_700(tmp_path):
    nguon = tmp_path / "su-kien.db"
    mo_ket_noi(nguon).close()
    (tmp_path / "sao-luu").mkdir(mode=0o755)
    os.chmod(tmp_path / "sao-luu", 0o755)
    ban = sao_luu(nguon, tmp_path / "sao-luu", luc="2026-10-17T00:00:00Z")
    assert che_do(ban) == 0o600 and che_do(tmp_path / "sao-luu") == 0o700


def test_sao_luu_hong_giua_chung_khong_de_file(tmp_path, monkeypatch):
    nguon = tmp_path / "su-kien.db"
    mo_ket_noi(nguon).close()

    def hong(*a, **k):
        raise ban_sao.LoiBanSao("quá hạn")
    monkeypatch.setattr(ban_sao, "chup", hong)
    with pytest.raises(ban_sao.LoiBanSao):
        sao_luu(nguon, tmp_path / "sao-luu")
    assert not (tmp_path / "sao-luu").exists() or list((tmp_path / "sao-luu").iterdir()) == []


def test_nhieu_luong_cung_tao_kho_moi_khong_loi(tmp_path):
    """Đo 18/10: macOS trả ENOENT khi nhiều luồng cùng `O_CREAT|O_NOFOLLOW` một tên mới — mở kho phải thử lại."""
    loi = []

    def mo(p):
        try:
            mo_ket_noi(p).close()
        except Exception as e:                    # noqa: BLE001 — gom mọi lỗi để so
            loi.append(e)
    for i in range(20):
        ds = [threading.Thread(target=mo, args=(tmp_path / f"k{i}.db",)) for _ in range(3)]
        for t in ds:
            t.start()
        for t in ds:
            t.join(30)
    assert loi == []


def _db_ngoai(ngoai):
    """Một SQLite hợp lệ NGOÀI cây, 0644, nhật ký thường — nếu bị mở nhầm, đổi sang WAL sẽ ghi vào nó."""
    f = ngoai / "su-kien.db"
    db = sqlite3.connect(f)
    db.execute("CREATE TABLE t (x)")
    db.commit()
    db.close()
    os.chmod(f, 0o644)
    return f, f.read_bytes()


@pytest.mark.parametrize("duoi", ["", "-wal", "-shm"])
def test_kho_hay_tep_phu_la_lien_ket_cung_thi_khong_mo_khong_doi(tmp_path, ngoai, duoi):
    """R2-05: liên kết cứng tới file ngoài cây (O_NOFOLLOW không chặn được) → từ chối TRƯỚC khi chmod/ghi."""
    p = tmp_path / "kho" / "su-kien.db"
    p.parent.mkdir()
    if duoi:
        sqlite3.connect(p).close()
    os.link(ngoai / "cua-nguoi-khac.txt", f"{p}{duoi}")
    with pytest.raises(LoiQuyenKho, match="liên kết cứng") as e:
        mo_ket_noi(p)
    f = ngoai / "cua-nguoi-khac.txt"
    assert f.read_text() == "x" and che_do(f) == 0o644 and str(tmp_path) not in str(e.value)


@pytest.mark.parametrize("thay", ["kho", "cha"])
def test_thay_kho_hay_cha_giua_kiem_va_mo_thi_khong_dung(tmp_path, ngoai, monkeypatch, thay):
    """R2-05: kho hay thư mục cha bị thay bằng liên kết tới kho NGOÀI cây đúng lúc SQLite mở lại theo tên → phát hiện
    trước câu lệnh đầu tiên, đóng; kho ngoài giữ nguyên nội dung lẫn quyền."""
    goc = tmp_path / "goc"
    goc.mkdir()
    p, (f, truoc) = goc / "su-kien.db", _db_ngoai(ngoai)
    that = sqlite3.connect

    def connect(duong, *a, **k):
        if thay == "kho":
            os.rename(p, goc / "cu.db")
            p.symlink_to(f)
        else:
            os.rename(goc, tmp_path / "goc-cu")
            goc.symlink_to(ngoai)
        return that(duong, *a, **k)
    monkeypatch.setattr(sqlite3, "connect", connect)
    with pytest.raises(LoiQuyenKho, match="bị thay"):
        mo_ket_noi(p)
    assert f.read_bytes() == truoc and che_do(f) == 0o644 and not (ngoai / "su-kien.db-wal").exists()


def test_cha_cua_kho_la_lien_ket_hay_nguoi_khac_ghi_duoc_thi_khong_mo(tmp_path, ngoai):
    f, truoc = _db_ngoai(ngoai)
    (tmp_path / "lk").symlink_to(ngoai)
    with pytest.raises(LoiQuyenKho):
        mo_ket_noi(tmp_path / "lk" / "su-kien.db")
    assert f.read_bytes() == truoc and che_do(f) == 0o644
    chung = tmp_path / "chung"
    chung.mkdir()
    os.chmod(chung, 0o777)
    with pytest.raises(LoiQuyenKho):
        mo_ket_noi(chung / "su-kien.db")
    assert list(chung.iterdir()) == []


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / ".tram"
    for d in ("log", "sao-luu/nho-1/lancedb", *TRANH):
        (g / d).mkdir(parents=True)
    for f in ("cau-hinh.yaml", "su-kien.db", "log/api.log", "sao-luu/nho-1/lancedb/a.lance", "hang-doi/x.json"):
        (g / f).write_text("x")
    for p in [g, *g.rglob("*")]:
        os.chmod(p, 0o755 if p.is_dir() else 0o644)
    (g / "lien-ket").symlink_to(tmp_path)
    return g


@pytest.fixture
def ngoai(tmp_path):
    n = tmp_path / "ngoai"
    n.mkdir()
    (n / "cua-nguoi-khac.txt").write_text("x")
    os.chmod(n / "cua-nguoi-khac.txt", 0o644)
    os.chmod(n, 0o755)
    return n


def test_siet_toan_bo_tru_vung_tho_va_lien_ket(goc, tmp_path):
    truoc = che_do(tmp_path)
    ds, bo = can_siet(goc)
    assert {(p, moi) for p, _, moi in ds} >= {(".", 0o700), ("cau-hinh.yaml", 0o600), ("su-kien.db", 0o600),
                                              ("log", 0o700), ("sao-luu/nho-1/lancedb/a.lance", 0o600)}
    assert not any(p.split("/")[0] in TRANH for p, _, _ in ds) and any("lien-ket" in b for b in bo)
    assert che_do(goc / "cau-hinh.yaml") == 0o644                                         # xem trước: chưa đổi
    assert sorted(siet(goc)) == sorted(ds)
    assert che_do(goc) == 0o700 and che_do(goc / "cau-hinh.yaml") == 0o600
    assert che_do(goc / "sao-luu/nho-1/lancedb") == 0o700
    assert che_do(goc / "hang-doi") == 0o755 and che_do(goc / "hang-doi/x.json") == 0o644   # vùng principal đọc
    assert che_do(tmp_path) == truoc and can_siet(goc)[0] == []                           # không theo liên kết


@pytest.mark.parametrize("luc_doi", [".", "log"])
def test_thay_thu_muc_cha_bang_lien_ket_giua_chung_khong_ra_ngoai(goc, ngoai, luc_doi):
    """`luc_doi="."`: thay `log` trước khi đi tới nó → `log` là liên kết, bỏ qua; thư mục thật (giờ tên `log-that`) vẫn
    được siết như mục thường. `"log"`: thay ngay sau khi đã mở fd của `log` → đổi quyền đúng thư mục thật qua fd.
    Cả hai: không chạm `ngoai`."""
    def chen(rel):
        if rel == luc_doi:
            (goc / "log").rename(goc / "log-that")
            (goc / "log").symlink_to(ngoai)
    da_doi, bo = di_cay(goc, lam=True, chen=chen)
    assert che_do(ngoai) == 0o755 and che_do(ngoai / "cua-nguoi-khac.txt") == 0o644
    assert che_do(goc / "log-that/api.log") == 0o600
    ten = "log/api.log" if luc_doi == "log" else "log-that/api.log"
    assert ten in [p for p, _, _ in da_doi] and (luc_doi == "log" or any("log: liên kết mềm" in b for b in bo))


def test_lien_ket_cung_khong_doi_quyen(goc, ngoai):
    os.link(ngoai / "cua-nguoi-khac.txt", goc / "log" / "cung.txt")
    da_doi, bo = di_cay(goc, lam=True)
    assert che_do(ngoai / "cua-nguoi-khac.txt") == 0o644 and any("cung.txt" in b and "liên kết cứng" in b for b in bo)


def test_cli_liet_ke_roi_cho_dong_y(goc, monkeypatch, capsys):
    from tram.cli import main
    monkeypatch.setenv("TRAM_HOME", str(goc))
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    assert main(["chu", "siet-quyen"]) == 1
    out = capsys.readouterr().out
    assert "cau-hinh.yaml" in out and "0644 → 0600" in out and "lien-ket" in out
    assert che_do(goc / "cau-hinh.yaml") == 0o644
    assert main(["chu", "siet-quyen", "--dong-y"]) == 0 and che_do(goc / "cau-hinh.yaml") == 0o600
