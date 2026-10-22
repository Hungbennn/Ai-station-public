from pathlib import Path

import pytest

from tram.beads.bd import Bd, KhongThayBead, LoiBd

MAU = Path(__file__).parent / "du_lieu" / "beads-mau.json"


class RunnerGia:
    def __init__(self, ra: str = ""):
        self.goi: list[list[str]] = []
        self.ra = ra

    def __call__(self, args):
        self.goi.append(list(args))
        return self.ra


def _bd(ra=""):
    r = RunnerGia(ra)
    return Bd(Path("/repo"), actor="dai-ca/dashboard", runner=r), r


def test_mot_doc_qua_bd_list():
    bd, r = _bd(MAU.read_text())
    b = bd.mot("hr-3")
    assert b.id == "hr-3" and "cot:ai-lam" in b.labels
    assert r.goi[0] == ["-C", "/repo", "list", "--json", "--all", "--limit", "0"]


def test_mot_khong_co_nem_khong_thay():
    bd, _ = _bd(MAU.read_text())
    with pytest.raises(KhongThayBead):
        bd.mot("hr-99")
    assert issubclass(KhongThayBead, LoiBd)


def test_tao_dung_co_va_tra_ma():
    bd, r = _bd("hr-77\n")
    assert bd.tao("Chốt: Giá tour", loai="decision", mo_ta="Hỏi: …") == "hr-77"
    assert r.goi[0] == ["-C", "/repo", "create", "Chốt: Giá tour", "-t", "decision", "-d", "Hỏi: …",
                        "--silent", "--actor", "dai-ca/dashboard"]


def test_tao_co_nhan():
    bd, r = _bd("hr-78")
    bd.tao("t", loai="task", mo_ta="m", nhan=["a", "b"])
    assert r.goi[0][-2:] == ["-l", "a,b"]


@pytest.mark.parametrize("ra", ["", "\n", "hai từ\n"])
def test_tao_dau_ra_la_nem_LoiBd(ra):
    bd, _ = _bd(ra)
    with pytest.raises(LoiBd):
        bd.tao("t", loai="decision", mo_ta="m")


def test_dong_va_them_phu_thuoc():
    bd, r = _bd()
    bd.dong("hr-5", "- câu trả lời bắt đầu bằng gạch")
    bd.them_phu_thuoc("hr-5", "hr-77")
    assert r.goi == [
        ["-C", "/repo", "close", "hr-5", "--reason", "- câu trả lời bắt đầu bằng gạch", "--actor", "dai-ca/dashboard"],
        ["-C", "/repo", "dep", "add", "hr-5", "hr-77", "--actor", "dai-ca/dashboard"],
    ]
