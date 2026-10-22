"""bs-2bd.1.17: `tram chu go-dich-vu` chỉ gỡ dịch vụ có BIÊN NHẬN cài của trạm khớp sha256 plist. Ngay TRƯỚC bootout:
kiểm lại biên nhận/plist (đúng nội dung và định danh lúc hỏi) và job đang nạp đúng từ plist đó; bootout rồi đọc lại
`launchctl print` — chỉ "không tìm thấy" mới coi là đã vắng; cất plist độc quyền (không ghi đè), xoá giữ định danh
(không xoá nhầm file thay thế). Chỉ bộ chạy giả."""
import json
import os
import plistlib
import subprocess
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from tram.chu import cai_dat
from tram.chu.go_dich_vu import VANG, LoiGo, lap_ke_hoach_go, thuc_hien_go
from tram.su_kien import ban_sao

LUC = "2026-10-17T01:02:03Z"


@pytest.fixture
def nha(tmp_path, tram_home_tam, monkeypatch):
    """Cài `api` và `quet` bằng kế hoạch thật của `cai-dat` (ghi plist + biên nhận), không chạy launchctl."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cai_dat, "_canh_bao", lambda: [])
    monkeypatch.setattr("tram.chu.dich_vu_tram._du_an_bat_ghi", lambda: ([], []))
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["api", "quet"])
    kh.buoc, kh.lenh = [], []
    cai_dat.thuc_hien(kh)
    return tmp_path / "Library/LaunchAgents", tram_home_tam


def bo_chay(la, ma_sau=VANG, *, nap=True, nguon=None, khi_bootout=None):
    """launchctl giả. `print` trước bootout: job đang nạp từ `nguon` (mặc định đúng plist trạm) hoặc 113 khi `nap=False`;
    `print` sau bootout: `ma_sau`. Bootout luôn trả 0 — "thành công" không chứng minh job đã vắng."""
    goi, da_go = [], set()

    def chay(argv, **k):
        lenh, mien = argv[1], argv[2]
        goi.append((lenh, mien, k["timeout"]))
        nhan = mien.rsplit("/", 1)[1]
        if lenh == "bootout":
            da_go.add(nhan)
            if khi_bootout:
                khi_bootout(nhan)
            return NS(returncode=0, stdout="")
        if nhan in da_go:
            return NS(returncode=ma_sau, stdout="")
        if not nap:
            return NS(returncode=VANG, stdout="")
        p = nguon or la / f"{nhan}.plist"
        return NS(returncode=0, stdout=f"{mien} = {{\n\tactive count = 1\n\tpath = {p}\n\tstate = running\n}}\n")
    return chay, goi


def test_go_dung_bien_nhan_kiem_nguon_bootout_kiem_lai_roi_cat(nha):
    la, home = nha
    ds = lap_ke_hoach_go(["api", "quet", "api"], home=la.parents[1])
    chay, goi = bo_chay(la)
    assert thuc_hien_go(ds, uid=501, luc=LUC, chay=chay) == ["api", "quet"]
    assert [g[:2] for g in goi] == [("print", "gui/501/vn.tram.api"), ("bootout", "gui/501/vn.tram.api"),
                                    ("print", "gui/501/vn.tram.api"), ("print", "gui/501/vn.tram.quet"),
                                    ("bootout", "gui/501/vn.tram.quet"), ("print", "gui/501/vn.tram.quet")]
    assert all(g[2] == 30.0 for g in goi) and not list(la.iterdir()) and not list((home / "dich-vu").iterdir())
    assert sorted(p.name for p in (home / "go-dich-vu").iterdir()) == ["vn.tram.api-20261017T010203Z.plist",
                                                                         "vn.tram.quet-20261017T010203Z.plist"]


def test_job_chua_nap_thi_khong_bootout_van_cat(nha):
    la, home = nha
    chay, goi = bo_chay(la, nap=False)
    assert thuc_hien_go(lap_ke_hoach_go(["api"], home=la.parents[1]), uid=501, luc=LUC, chay=chay) == ["api"]
    assert [g[0] for g in goi] == ["print"] and not (la / "vn.tram.api.plist").exists()


@pytest.mark.parametrize("pha", ["plist-gia-co-chu-tram", "khong-bien-nhan", "khong-plist", "lien-ket"])
def test_khong_co_chung_cu_so_huu_thi_tu_choi_ca_ke_hoach(nha, pha, tmp_path):
    la, home = nha
    p = la / "vn.tram.quet.plist"
    if pha == "plist-gia-co-chu-tram":
        p.write_bytes(plistlib.dumps({"Label": "vn.tram.quet", "ProgramArguments": ["/u", "tram", "khac"]}))
    elif pha == "khong-bien-nhan":
        (home / "dich-vu/vn.tram.quet.json").unlink()
    elif pha == "khong-plist":
        p.unlink()
    else:
        (tmp_path / "that.plist").write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(tmp_path / "that.plist")
    with pytest.raises(LoiGo, match="không gỡ gì"):
        lap_ke_hoach_go(["api", "quet"], home=la.parents[1])                  # api hợp lệ cũng không gỡ


@pytest.mark.parametrize("pha", ["plist-doi", "plist-thay-cung-noi-dung", "mat-bien-nhan", "bien-nhan-doi"])
def test_chung_cu_doi_trong_luc_hoi_thi_khong_dung_gi(nha, pha):
    """R2-07: lập kế hoạch xong (CLI đang hỏi dong-y) thì plist/biên nhận bị đổi → 0 lệnh launchctl, không đổi file."""
    la, home = nha
    ds = lap_ke_hoach_go(["api"], home=la.parents[1])
    p, bn = la / "vn.tram.api.plist", home / "dich-vu/vn.tram.api.json"
    if pha == "plist-doi":
        p.write_bytes(plistlib.dumps({"Label": "vn.tram.api", "ProgramArguments": ["/khac"]}))
    elif pha == "plist-thay-cung-noi-dung":
        noi = p.read_bytes()
        p.unlink()
        p.write_bytes(noi)                                                  # cùng nội dung, khác file
    elif pha == "mat-bien-nhan":
        bn.unlink()
    else:
        bn.write_text(json.dumps({"nhan": "vn.tram.api"}))
    chay, goi = bo_chay(la)
    with pytest.raises(LoiGo, match="đổi trong lúc"):
        thuc_hien_go(ds, uid=501, luc=LUC, chay=chay)
    assert goi == [] and p.exists() and not (home / "go-dich-vu").exists()


def test_job_cung_nhan_nap_tu_nguon_khac_thi_khong_bootout(nha, tmp_path):
    la, home = nha
    chay, goi = bo_chay(la, nguon=tmp_path / "khac/vn.tram.api.plist")
    with pytest.raises(LoiGo, match="nguồn khác"):
        thuc_hien_go(lap_ke_hoach_go(["api"], home=la.parents[1]), uid=501, luc=LUC, chay=chay)
    assert [g[0] for g in goi] == ["print"] and (la / "vn.tram.api.plist").exists()


def test_plist_bi_thay_luc_dang_cat_thi_khong_xoa_ban_thay(nha, monkeypatch):
    """R2-07: file thay vào đúng tên plist trong lúc cất KHÔNG bị xoá (xoá giữ định danh)."""
    la, home = nha
    p, that = la / "vn.tram.api.plist", ban_sao.ghi_doc_quyen

    def ghi_roi_thay(*a, **k):
        kq = that(*a, **k)
        if p.exists():
            p.unlink()
        p.write_text("của người khác")
        return kq
    monkeypatch.setattr(ban_sao, "ghi_doc_quyen", ghi_roi_thay)
    thuc_hien_go(lap_ke_hoach_go(["api"], home=la.parents[1]), uid=501, luc=LUC, chay=bo_chay(la)[0])
    assert p.read_text() == "của người khác"
    assert [f.name for f in la.iterdir() if f.name.startswith(".")] == []                   # không sót tên tạm


@pytest.mark.parametrize("ma, ly_do", [(0, "vẫn còn nạp"), (5, "không xác định")])
def test_bootout_bi_tu_choi_hay_khong_ro_thi_dung_giu_plist(nha, ma, ly_do):
    la, home = nha
    ds = lap_ke_hoach_go(["api", "quet"], home=la.parents[1])
    chay, goi = bo_chay(la, ma)
    with pytest.raises(LoiGo, match=ly_do):
        thuc_hien_go(ds, uid=501, luc=LUC, chay=chay)
    assert len(goi) == 3 and (la / "vn.tram.api.plist").exists() and (home / "dich-vu/vn.tram.api.json").exists()
    assert not (home / "go-dich-vu").exists()                                   # quet không đụng tới


def test_print_truoc_bootout_khong_ro_thi_dung(nha):
    la, _ = nha

    def chay(argv, **k):
        return NS(returncode=5, stdout="")
    with pytest.raises(LoiGo, match="không xác định"):
        thuc_hien_go(lap_ke_hoach_go(["api"], home=la.parents[1]), uid=501, luc=LUC, chay=chay)
    assert (la / "vn.tram.api.plist").exists()


def test_launchctl_qua_han_thi_dung(nha):
    la, _ = nha
    ds = lap_ke_hoach_go(["api", "quet"], home=la.parents[1])

    def treo(argv, **k):
        raise subprocess.TimeoutExpired(argv, k["timeout"])
    with pytest.raises(subprocess.TimeoutExpired):
        thuc_hien_go(ds, uid=501, luc=LUC, chay=treo)
    assert (la / "vn.tram.api.plist").exists() and (la / "vn.tram.quet.plist").exists()


def test_rut_khong_ghi_de_file_tam_tu_lan_go_truoc(tmp_path):
    from tram.chu.chung_cu_go import _doc, rut
    p = tmp_path / "dv.plist"
    p.write_bytes(b"plist hien tai")
    tep = _doc(p)
    tam = tmp_path / f".{p.name}.go-{os.getpid()}"
    tam.write_bytes(b"ban can cuu cua lan truoc")
    with pytest.raises(LoiGo):
        rut(tep)
    assert p.read_bytes() == b"plist hien tai"
    assert tam.read_bytes() == b"ban can cuu cua lan truoc"


def test_ban_cat_trung_ten_khong_ghi_de(nha):
    la, home = nha
    cu = home / "go-dich-vu/vn.tram.api-20261017T010203Z.plist"
    cu.parent.mkdir(mode=0o700)
    cu.write_text("bản cất trước")
    ds = lap_ke_hoach_go(["api"], home=la.parents[1])
    thuc_hien_go(ds, uid=501, luc=LUC, chay=bo_chay(la)[0])
    assert cu.read_text() == "bản cất trước"
    moi = home / "go-dich-vu/vn.tram.api-20261017T010203Z-2.plist"
    assert plistlib.loads(moi.read_bytes())["Label"] == "vn.tram.api"


@pytest.mark.parametrize("sai", [[], None, ["tho"], ["api", "la"]])
def test_ten_sai_hay_khong_chon(tmp_path, sai):
    with pytest.raises(ValueError, match="dịch vụ"):
        lap_ke_hoach_go(sai, home=tmp_path)


def test_cli_cho_dong_y_va_tu_choi_khong_chung_cu(nha, monkeypatch, capsys):
    from tram.cli import main
    la, home = nha
    goi = []
    monkeypatch.setattr("tram.chu.go_dich_vu.thuc_hien_go", lambda ds, **k: goi.append(ds) or ["quet"])
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    assert main(["chu", "go-dich-vu", "--dich-vu", "quet"]) == 1 and goi == []
    assert "vn.tram.quet" in capsys.readouterr().out
    assert main(["chu", "go-dich-vu", "--dich-vu", "quet", "--dong-y"]) == 0 and len(goi) == 1
    assert main(["chu", "go-dich-vu", "--dong-y"]) == 2
    (home / "dich-vu/vn.tram.api.json").write_text(json.dumps({"nhan": "vn.tram.api"}))
    assert main(["chu", "go-dich-vu", "--dich-vu", "api", "--dong-y"]) == 2 and len(goi) == 1
    assert os.environ["HOME"] == str(la.parents[1])
