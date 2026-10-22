"""`tram giao kiem|tick|kho-kiem` (4a-2). Không chạy sudo, `bd` hay mạng thật: TRAM_REPO tạm (du-an/ rỗng hoặc trỏ
remote bare cục bộ). Mục principal kiểm lại: `test_kiem_principal.py` (3C-D6, H7)."""
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cli import main
from tram.giao_viec.kho_kiem_tao import lap_ke_hoach, thuc_hien
from tram.giao_viec.kiem_san_sang import kiem_du_an, kiem_giao_viec
from tram.tho.kiem_may import in_ket_qua


@pytest.fixture(autouse=True)
def bo_quan_ly_kiem_khong_ton_tai(monkeypatch):
    """Không đọc cấu hình hệ thống hay nối socket của daemon đã cài trên máy chạy test."""
    def gui_gia(*a, **kw):
        raise FileNotFoundError("bộ quản lý kiểm giả chưa được cài")

    monkeypatch.setattr("tram.quan_kiem.client.gui", gui_gia)


def muc(ds):
    return {m.muc: m.muc_do for m in ds}


def test_thieu_het_thi_do(tmp_path):
    ds = kiem_giao_viec(CauHinhGiaoViec(), [], goc_quyen=tmp_path)
    m = muc(ds)
    assert (m["giao_viec.bat"], m["file quyền coder"], m["Bộ quản lý kiểm"]) == ("vang", "do", "do")
    assert in_ket_qua(ds)[1] == 1


def test_du_an_kho_kiem_va_moi_truong(tmp_path):
    k = dung_kho(tmp_path)
    (tmp_path / "env.testing").write_text("DB_DATABASE=test\n")
    da = DuAn("hr-codex", k.dev, None, {}, moi_truong_kiem=MoiTruongKiem(tmp_path / "env.testing", ".env.testing"))
    assert muc(kiem_du_an(da)) == {"hr-codex: kho kiểm": "do", "hr-codex: moi_truong_kiem": "xanh",
                                   "hr-codex: lệnh kiểm mặc định": "vang"}
    thuc_hien(lap_ke_hoach(da), "main")
    assert muc(kiem_du_an(da))["hr-codex: kho kiểm"] == "xanh"


def test_cli_tick_va_kho_kiem(tmp_path, monkeypatch, capsys):
    k = dung_kho(tmp_path)
    (tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (tmp_path / "repo-tram" / "du-an" / "hr-x.yaml").write_text(f"ten: hr-x\nduong_dan: {k.dev}\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr("tram.giao_viec.noi_that.cac_du_an_that", lambda thu_muc=None: [])   # không chạy `bd` thật
    assert main(["giao", "tick"]) == 1 and "chỉ chạy được" in capsys.readouterr().out
    assert main(["giao", "tick", "--thu"]) == 0 and "pha nhanh: không có việc" in capsys.readouterr().out
    monkeypatch.setattr("builtins.input", lambda *_: "không")
    assert main(["giao", "kho-kiem", "hr-x"]) == 1 and "TẠO MỚI" in capsys.readouterr().out
    assert main(["giao", "kho-kiem", "hr-x", "--dong-y"]) == 0 and k.main in capsys.readouterr().out
    assert Path(tmp_path / "tram-home" / "kho-kiem" / "hr-x" / ".git").is_dir()
