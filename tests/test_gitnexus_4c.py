"""Adapter gitnexus (lát 4c): đọc khoan dung, không chắc thì báo, chỉ hai lệnh đọc. gitnexus thật KHÔNG chạy."""
import json
from pathlib import Path

import pytest

from tram.giao_viec.gitnexus import GitnexusCli, LoiGitnexus

WT = Path("/tmp/wt-hr-1")
KQ = {"changed_symbols": [{"name": "tinhHoaHong", "filePath": "erp/app/Modules/Comp/Tinh.php"}],
      "affected_processes": [{"name": "Đặt tour",
                              "steps": [{"symbol": "x", "file": f"{WT}/erp/app/Modules/Fin/So.php"}]}],
      "summary": {"changed_count": 1, "risk_level": "high"}, "partial": False}


class Chay:
    def __init__(self, ma=0, ra=""):
        self.ma, self.ra, self.goi = ma, ra, []

    def __call__(self, argv, cwd):
        self.goi.append((argv, cwd))
        return self.ma, self.ra


def test_thay_doi_gom_file_cua_symbol_va_luong():
    c = Chay(ra=json.dumps(KQ))
    kq = GitnexusCli(c).thay_doi(WT, "b" * 40, "hr-interview-copilot")
    assert kq.tep == {"erp/app/Modules/Comp/Tinh.php", "erp/app/Modules/Fin/So.php"} and not kq.khong_chac
    argv, cwd = c.goi[0]
    assert argv[:2] == ["gitnexus", "detect-changes"] and cwd == WT
    assert "--scope" in argv and f"--base-ref={'b' * 40}" in argv and "--repo=hr-interview-copilot" in argv


@pytest.mark.parametrize("them", [{"partial": True}, {"truncated": True}])
def test_partial_hoac_truncated_la_khong_chac(them):
    assert GitnexusCli(Chay(ra=json.dumps({**KQ, **them}))).thay_doi(WT, "b", "r").khong_chac


def test_json_sau_dong_chu_van_doc_duoc():
    kq = GitnexusCli(Chay(ra="Loading index…\n" + json.dumps(KQ) + "\n")).thay_doi(WT, "b", "r")
    assert "erp/app/Modules/Comp/Tinh.php" in kq.tep
    for sai in ({}, {"summary": {}}, {"changed_symbols": "x", "affected_processes": []}):
        with pytest.raises(LoiGitnexus):
            GitnexusCli(Chay(ra=json.dumps(sai))).thay_doi(WT, "b", "r")


@pytest.mark.parametrize("ma,ra", [(1, json.dumps(KQ)), (0, "Changed: 3 symbols"),
                                   (0, json.dumps({"error": "no index"})),
                                   (0, "[1, 2]")])
def test_loi_hoac_khong_doc_duoc(ma, ra):
    with pytest.raises(LoiGitnexus):
        GitnexusCli(Chay(ma, ra)).thay_doi(WT, "b", "r")


def test_luong_lien_quan_va_truy_van_khong_thanh_tuy_chon():
    d = {"processes": [{"id": "p1", "name": "Hoàn tiền"}, {"id": "p2", "label": "Tóm tắt"}],
         "process_symbols": [{"process_id": "p1", "filePath": "erp/Fin/HoanTien.php"},
                             {"process_id": "p1", "filePath": "erp/Fin/HoanTien.php"},
                             {"process_id": "p2", "filePath": "src/tom_tat.py"}]}
    c = Chay(ra=json.dumps(d))
    assert GitnexusCli(c).luong("--help\nSửa   cắt UTF-8", "r") == [("Hoàn tiền", ("erp/Fin/HoanTien.php",)),
                                                                      ("Tóm tắt", ("src/tom_tat.py",))]
    assert "--query=--help Sửa cắt UTF-8" in c.goi[0][0] and c.goi[0][0][:2] == ["gitnexus", "query"]


def test_chi_hai_lenh_doc():
    with pytest.raises(LoiGitnexus):
        GitnexusCli(Chay())._gn("analyze")
