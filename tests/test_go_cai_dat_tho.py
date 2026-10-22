"""`tram chu go-cai-dat-tho` (lát 3c R2, bead bs-urj.14; Codex F02): chỉ gỡ thứ sổ ghi `da_tao` và còn đúng định danh;
user có sẵn/addUser lỗi không bị xoá; đối soát crash; thư mục không rỗng chỉ cảnh báo; chạy lại rỗng. Cài bằng chính
`cai-dat-tho` trên `HeGia` — KHÔNG sudo/sysadminctl/launchctl thật."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.cai_dat_tho import DAEMON, SUDOERS, lap_ke_hoach_tho
from tram.chu.go_cai_dat_tho import lap_ke_hoach_go
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.cli import tao_parser
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI


def cai(tmp_path, he, *, co_che="sandbox", chay=None):
    kh = lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che=co_che,
                          khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly(f"{co_che}:tram-kiem"),
                          thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=chay or he.chay)
    thuc_hien(kh, chay=he.chay)


def ke_hoach_go(he, bao=None, **kw):
    return lap_ke_hoach_go(SoCai(), toi="hung", quan_sat=he.quan_sat, chay=he.chay,
                           bao=(bao if bao is not None else []).append, **kw)


def test_go_dung_thu_tu_het_sach_va_chay_lai_rong(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he)
    kh = ke_hoach_go(he)
    assert [m.split(":")[0] for m, _ in kh.buoc] == [
        "Đối soát sổ cài đặt (khép bản ghi dở do crash)", f"Gỡ tep {DAEMON} nếu còn đúng định danh trong sổ",
        f"Gỡ tep {HO_SO_KIEM} nếu còn đúng định danh trong sổ",
        f"Gỡ tep {MANIFEST_KIEM} nếu còn đúng định danh trong sổ", f"Gỡ tep {SUDOERS} nếu còn đúng định danh trong sổ",
        f"Gỡ thu_muc {tmp_path}/kiem nếu còn đúng định danh trong sổ",
        *(f"Gỡ user {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho")),
        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ",
        *(f"Gỡ nhom {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho"))]
    he.lenh.clear()
    thuc_hien(kh, chay=he.chay)
    assert (he.user, he.tep) == ({}, {}) and he.lenh[0] == "sudo launchctl bootout system/vn.tram.tho"
    assert set(he.thu_muc) == {"/Users/tram-k-1", "/Users/tram-tho"}                    # nhà giữ (-keepHome, D40)
    assert f"sudo -u tram-kiem /bin/rm -rf {tmp_path}/kiem" in he.lenh and "sudo sysadminctl -deleteUser tram-kiem " \
        "-keepHome" in he.lenh
    assert {m.su for m in SoCai().muc().values() if m.kieu != "nha"} == {"da_go"} and ke_hoach_go(he).buoc == []


def test_user_co_san_addUser_loi_khong_bi_xoa(tram_home_tam, tmp_path):
    he = HeGia()
    he.truoc["sysadminctl -addUser tram-kiem"] = lambda: he.them_user("tram-kiem")
    with pytest.raises(LoiCaiDat):
        cai(tmp_path, he, co_che="user")
    thuc_hien(ke_hoach_go(he), chay=he.chay)
    assert list(he.user) == ["tram-kiem"] and he.user["tram-kiem"]["ten_day_du"] == "người khác"


@pytest.mark.parametrize("sau", [True, False])
def test_crash_quanh_lenh_tao_doi_soat_roi_moi_go(tram_home_tam, tmp_path, sau):
    he = HeGia()

    def chay(c, check=False, **kw):
        if not sau and "-addUser" in c:
            raise SystemExit("mất điện trước lệnh")
        he.chay(c, check=check)
        if "-addUser" in c:
            raise SystemExit("mất điện sau lệnh, trước da_tao")
    with pytest.raises(SystemExit):
        cai(tmp_path, he, co_che="user", chay=chay)
    assert [m.su for m in SoCai().muc().values() if m.kieu == "user"] == ["du_dinh"]
    thuc_hien(ke_hoach_go(he), chay=he.chay)
    assert he.user == {} and [m.su for m in SoCai().muc().values() if m.kieu == "user"] == ["da_go" if sau else "khong_tao"]
    assert ke_hoach_go(he).buoc == []          # trước lệnh: chỉ đối soát khép bản ghi dở, không có gì để gỡ


def test_user_xoa_tao_lai_hoac_file_bi_sua_thi_khong_go(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he, co_che="user")
    he.user["tram-kiem"]["guid"] = "GUID-tao-lai"
    he.tep[str(SUDOERS)] = "da-bi-sua"
    thuc_hien(ke_hoach_go(he, bao), chay=he.chay)
    assert list(he.user) == ["tram-kiem"] and list(he.tep) == [str(SUDOERS)] and len(bao) == 3
    assert all("không khớp sổ" in b for b in bao[:2])
    assert "user vẫn còn" in bao[-1]


def test_thu_muc_khong_rong_chi_canh_bao_buoc_khac_van_chay(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he)
    he.tep[f"{THU_MUC_CAI}/cua-nguoi-khac"] = "x"
    thuc_hien(ke_hoach_go(he, bao), chay=he.chay)
    assert he.user == {} and str(THU_MUC_CAI) in he.thu_muc and "không rỗng" in bao[0]
    assert [m.split(":")[0] for m, _ in ke_hoach_go(he).buoc][1:] == [
        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ"]


def test_khong_go_user_dang_chay_lenh_va_xoa_nha(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    kh = lap_ke_hoach_go(SoCai(), toi="tram-tho", quan_sat=he.quan_sat, chay=he.chay, xoa_nha=True)
    thuc_hien(kh, chay=he.chay)
    assert list(he.user) == ["tram-tho"] and "sudo sysadminctl -deleteUser tram-kiem -keepHome" in he.lenh
    assert "sudo rm -rf /Users/tram-k-1" in he.lenh and "/Users/tram-tho" in he.thu_muc        # nhà của toi: giữ
    assert any("tram-tho: là tài khoản đang chạy" in c for c in kh.canh_bao)


def test_so_hong_thi_khong_go_gi(tram_home_tam, capsys):
    SoCai().p.parent.mkdir(parents=True)
    SoCai().p.write_text(json.dumps({"v": 2, "id": "x", "su": "da_tao"}) + "\n")
    assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "hỏng" in capsys.readouterr().err


def test_lenh_cli(tram_home_tam, tmp_path, monkeypatch, capsys):
    args = SimpleNamespace(xoa_nha=False, dong_y=False)
    assert lenh_tho._go_cai_dat_tho(args) == 0 and "chưa có sổ" in capsys.readouterr().out
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", he.quan_sat)
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
    assert lenh_tho._go_cai_dat_tho(args) == 1 and "sysadminctl -deleteUser tram-kiem" in capsys.readouterr().out
    assert tao_parser().parse_args(["chu", "go-cai-dat-tho", "--xoa-nha"]).ham.__name__ == "_go_cai_dat_tho"
