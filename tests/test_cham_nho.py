"""1a dùng memory 1b-1 (spec 1b §7 "1a dùng thế nào", §10): recall có timeout, lùi về cách cũ, nguon_bai_hoc."""
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace as NS

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.prompt import THE
from tram.cham_cot.quet import quet
from tram.nho.khach import LoiNhoKhach
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr-codex", Path("/r"), None, {}, "ERP")
VAI = ("3", "VAI")
DUNG = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}


def bead(id="hr-1", updated_at="2026-10-12T00:00:00Z"):
    return Bead(id, "Hiện hoa hồng tạm tính", "Màn sale", "", "", "", "open", "task", (), (), updated_at)


class ClientGia:
    def __init__(self):
        self.goi = []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.goi.append(kw)
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(DUNG))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


class NhoGia:
    def __init__(self, tra=None, loi=False):
        self.tra, self.loi, self.goi = tra or [], loi, []

    def __call__(self, truy_van, vung_cap):
        self.goi.append((truy_van, vung_cap))
        if self.loi:
            raise LoiNhoKhach("memory service tắt")
        return self.tra


def kho_co_su_kien(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr-codex", "cot.dai_ca_sua", {"tieu_de": "Cũ", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot",
                                          "ly_do_he": "x", "da_ghi": True}, bead_id="hr-9", tac_nhan="dai-ca")
    return k


def test_dung_memory_khi_co(tmp_path):
    nho = NhoGia([{"id": "m-1", "noi_dung": "Hoa hồng tính trên giá sau giảm giá",
                   "pham_vi": "/du-an/hr-codex/nghiep-vu"}])
    c = ClientGia()
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho_co_su_kien(tmp_path), client=c, vai=VAI, nho=nho)
    assert nho.goi == [("Hiện hoa hồng tạm tính\nMàn sale", ["/du-an/hr-codex", "/vai/cham-cot", "/chung"])]
    nd = c.goi[0]["messages"][0]["content"]
    khoi = nd[nd.index("## Bài học và quyết định đã ghi nhớ"):nd.index("## Quyết định đã chốt")]
    assert f"<{THE}>" in khoi and "giá sau giảm giá" in khoi and "Bead 'Cũ'" not in nd
    assert p.du_lieu["nguon_bai_hoc"] == "nho"


def test_memory_loi_thi_lui_ve_5_su_kien(tmp_path):
    c = ClientGia()
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho_co_su_kien(tmp_path), client=c, vai=VAI,
                      nho=NhoGia(loi=True))
    assert p.du_lieu["nguon_bai_hoc"] == "su_kien" and "Bead 'Cũ'" in c.goi[0]["messages"][0]["content"]


def test_chua_cai_memory_dung_cach_cu(tmp_path):
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho_co_su_kien(tmp_path), client=ClientGia(), vai=VAI)
    assert p.du_lieu["nguon_bai_hoc"] == "su_kien"


def test_quet_truyen_nho_va_ghi_nguon_bai_hoc_vao_su_kien(tmp_path):
    k, nho = KhoSuKien(tmp_path / "sk.db"), NhoGia([])
    bd = NS(tat_ca=lambda: [bead()], phien_ban=lambda i: "2026-10-12T00:00:00Z", cap_nhat_nhan=lambda *a, **kw: None)
    quet(DU_AN, bd=bd, kho=k, client=ClientGia(), vai=VAI, tat_ca=True, thu=True, nho=nho)
    assert len(nho.goi) == 1
    assert k.gan_day("hr-codex", "cham_cot.ket_qua", 1)[0].du_lieu["nguon_bai_hoc"] == "nho"


def test_1a_khong_nap_lancedb():
    ma = "import sys, tram.cli, tram.cham_cot.quet; assert 'lancedb' not in sys.modules, 'lancedb bị nạp'"
    kq = subprocess.run([sys.executable, "-c", ma], capture_output=True, text=True)
    assert kq.returncode == 0, kq.stderr


class NhoNem:
    def __init__(self, loi):
        self.loi = loi

    def __call__(self, truy_van, vung_cap):
        raise self.loi


def test_moi_loi_cua_nho_deu_lui_ve_cach_cu(tmp_path):
    """bs-hpc.7: AttributeError (JSON sai dạng), LoiVungCap (tên dự án sai) không được làm hỏng lượt chấm."""
    from tram.nho.pham_vi import LoiVungCap
    for loi in (AttributeError("'list' object has no attribute 'get'"), LoiVungCap("Tên không hợp lệ"),
                TypeError("x")):
        c = ClientGia()
        p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho_co_su_kien(tmp_path), client=c, vai=VAI,
                          nho=NhoNem(loi))
        assert p.du_lieu["nguon_bai_hoc"] == "su_kien" and "Bead 'Cũ'" in c.goi[0]["messages"][0]["content"]


def test_quet_khong_hong_khi_nho_tra_mang_rong(tmp_path):
    from tram.nho.khach import tao_nho_lai
    from test_nho_khach import mo_tra
    nho = tao_nho_lai(chay=lambda c, **k: NS(returncode=0, stdout="t"), mo=mo_tra([]))
    k = KhoSuKien(tmp_path / "sk.db")
    bd = NS(tat_ca=lambda: [bead()], phien_ban=lambda i: "2026-10-12T00:00:00Z", cap_nhat_nhan=lambda *a, **kw: None)
    quet(DU_AN, bd=bd, kho=k, client=ClientGia(), vai=VAI, tat_ca=True, thu=True, nho=nho)
    assert k.gan_day("hr-codex", "cham_cot.ket_qua", 1)[0].du_lieu["nguon_bai_hoc"] == "su_kien"
