"""Lát 1a-2: `tram du-an them` bước (1) — bản nháp du-an/<ten>.yaml (spec 0+1a §4.2, §4.7)."""
from pathlib import Path

import pytest
import yaml

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import LOAI_HANG_RAO, nap_du_an
from tram.cham_cot.luat_cung import kiem
from tram.du_an.cau_hinh_moi import RAO_MAC_DINH, kiem_ten, kiem_yaml, tao_yaml, ten_tu_repo


@pytest.mark.parametrize("ten_thu_muc, ten", [
    ("HR Codex", "hr-codex"), ("Đặt Tour  (v2)", "dat-tour-v2"), ("ben-station", "ben-station"), ("___", ""),
])
def test_ten_tu_repo(ten_thu_muc, ten):
    assert ten_tu_repo(Path("/x") / ten_thu_muc) == ten


@pytest.mark.parametrize("ten, hop_le", [
    ("hr-codex", True), ("2026", True), ("a" * 40, True), ("", False), ("-a", False), ("Hr", False),
    ("_tram", False), ("a" * 41, False), ("a b", False),
])
def test_kiem_ten(ten, hop_le):
    assert (kiem_ten(ten) is None) is hop_le


def nap(tmp_path, ten, noi_dung):
    (tmp_path / f"{ten}.yaml").write_text(noi_dung, encoding="utf-8")
    return nap_du_an(ten, thu_muc=tmp_path)


def test_ban_nhap_nap_duoc_bang_bo_nap_that(tmp_path):
    da = nap(tmp_path, "hr-codex", tao_yaml("hr-codex", Path("/Users/dai-ca/Developer/HR Codex")))
    assert da.ten == "hr-codex" and da.duong_dan == Path("/Users/dai-ca/Developer/HR Codex")
    assert da.gitnexus_repo is None and da.boi_canh == "" and da.nhanh_chinh == "main"
    assert set(da.hang_rao) == set(LOAI_HANG_RAO) and "hoa hồng" in da.hang_rao["tien"].tu_khoa


def test_ten_toan_so_van_la_chuoi_va_gitnexus(tmp_path):
    da = nap(tmp_path, "2026", tao_yaml("2026", Path("/r"), "hr-interview-copilot"))
    assert da.ten == "2026" and da.gitnexus_repo == "hr-interview-copilot"


def test_rao_mac_dinh_du_bon_loai_va_day_ve_cot_2(tmp_path):
    assert tuple(RAO_MAC_DINH) == LOAI_HANG_RAO
    da = nap(tmp_path, "x", tao_yaml("x", Path("/r")))
    b = Bead("x-1", "Đổi cách tính hoa hồng", "", "", "", "", "open", "task", (), (), "2026-10-15T00:00:00Z")
    assert kiem(b, da, {}).ep_cot_2


def test_ban_nhap_chua_bat_ghi():
    # D31: dự án mới chỉ đọc + quét thử; khoá do tram/cau_hinh/bat_ghi.py (Task 5) đọc — ở đây kiểm văn bản
    assert yaml.safe_load(tao_yaml("x", Path("/r")))["bat_ghi"] is False


def test_kiem_yaml_nem_loi_khi_sai_schema():
    kiem_yaml("x", tao_yaml("x", Path("/r")))
    with pytest.raises(ValueError):
        kiem_yaml("x", 'ten: "khac"\nduong_dan: "/r"\n')
