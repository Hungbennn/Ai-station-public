import hashlib
import re
from importlib.metadata import version
from pathlib import Path

import pytest

from mcp_gia import goi_cong_cu, goi_mcp, ket_qua, rpc, van_ban
from nho_gia import EmbedderGia, ky_uc
from tram.nho.dich_vu import DichVuNho
from tram.nho.kho import KhoKyUc
from tram.nho.may_chu_mcp import tao_ung_dung
from tram.nho.nho_lai import BoDemDung
from tram.nho.ung_dung import CauHinhMcp
from tram.su_kien.kho import KhoSuKien

MA, GID, MA_DAI_CA = "Abc_def-123456789012ab", "g-20261013-0042", "m" * 40
PHIEU = {"du_an": "hr-codex", "vai": "coder", "ma_giao": MA, "con_hieu_luc": True}
H_PHIEU = {"X-Tram-Giao-Id": GID, "X-Tram-Ma-Giao": MA}
H_TAY = {"Authorization": f"Bearer {MA_DAI_CA}", "X-Tram-Du-An": "erp"}
KHO = {"m-x": "/du-an/hr-codex/cach-lam", "m-y": "/du-an/erp/nghiep-vu", "m-v": "/vai/coder", "m-c": "/chung"}


@pytest.fixture
def mt(tmp_path):
    e = EmbedderGia()
    kho = KhoKyUc(tmp_path / "l", so_chieu=e.so_chieu)
    for i, pv in KHO.items():
        kho.them(ky_uc(i, pv, vector=e.embed([i])[0], noi_dung=f"Nội dung {i}"))
    e.goi.clear()
    dv = DichVuNho(kho, e, lambda: KhoSuKien(tmp_path / "sk.db"), BoDemDung(), "tok-nho")
    cfg = CauHinhMcp(lambda g: PHIEU if g == GID else None, lambda: hashlib.sha256(MA_DAI_CA.encode()).hexdigest(),
                     lambda t: t in ("hr-codex", "erp"))
    return tao_ung_dung(dv, cfg), dv


def post(than, headers):
    return ("POST", "/mcp", than, headers)


def ids(text: str) -> set[str]:
    return {i for i in KHO if f'"id": "{i}"' in text}


def test_khoi_tao_va_cong_cu_khong_co_tham_so_pham_vi(mt):
    app, _ = mt
    khoi, ds = goi_mcp(app, post(rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                    "clientInfo": {"name": "thu", "version": "0"}}), H_PHIEU),
                       post(rpc("tools/list", id=2), H_PHIEU))
    assert ket_qua(khoi)["serverInfo"]["name"] == "tram-nho"
    cc = {c["name"]: c["inputSchema"] for c in ket_qua(ds)["tools"]}
    assert set(cc) == {"nho_lai", "ghi_nho"}
    assert set(cc["nho_lai"]["properties"]) == {"truy_van"} and cc["nho_lai"]["required"] == ["truy_van"]
    assert set(cc["ghi_nho"]["properties"]) == {"noi_dung", "nhan"} and cc["ghi_nho"]["required"] == ["noi_dung"]


def test_nho_lai_qua_mcp_chi_trong_vung_cua_phieu_bo_qua_tham_so_thua(mt):
    app, _ = mt
    [r] = goi_mcp(app, post(goi_cong_cu("nho_lai", {"truy_van": "nội dung", "vung_cap": ["/du-an/erp"],
                                                     "du_an": "erp"}), H_PHIEU))
    loi, text = van_ban(r)
    assert not loi and ids(text) == {"m-x", "m-v", "m-c"} and "<du_lieu_khong_tin_cay>" in text


@pytest.mark.parametrize("h", [{}, {"Authorization": "Bearer tok-nho"}, {"Tailscale-User-Login": "dai-ca@example.com"},
                               {**H_PHIEU, "X-Tram-Ma-Giao": "Zbc_def-123456789012ab"},
                               {"Authorization": "Bearer tok-nho", "X-Tram-Du-An": "erp"}])
def test_khong_bang_chung_hop_le_401_cong_cu_khong_chay(mt, h):
    app, dv = mt
    [r] = goi_mcp(app, post(goi_cong_cu("nho_lai", {"truy_van": "x"}), h))
    assert r.status == 401 and "loi" in r.json() and dv.embedder.goi == []


def test_phien_tay_doc_duoc_ghi_bi_tu_choi(mt):
    app, dv = mt
    doc, ghi = goi_mcp(app, post(goi_cong_cu("nho_lai", {"truy_van": "nội dung"}), H_TAY),
                       post(goi_cong_cu("ghi_nho", {"noi_dung": "bài học"}, 2), H_TAY))
    assert van_ban(doc)[0] is False and ids(van_ban(doc)[1]) == {"m-y", "m-c"}
    loi, text = van_ban(ghi)
    assert loi and "chỉ đọc" in text and dv.mo_kho_sk().gan_day("erp", "nho.agent_ghi", 9) == []


def test_ghi_nho_qua_mcp_ghi_su_kien_cua_phieu(mt):
    app, dv = mt
    [r] = goi_mcp(app, post(goi_cong_cu("ghi_nho", {"noi_dung": "Chạy test bằng artisan", "nhan": ["test"]}), H_PHIEU))
    assert van_ban(r) == (False, "Đã nhận. Memory ghi vào dự án của phiếu ở vòng nạp kế tiếp (nhịp danh nghĩa 2 phút; "
                                 "lỗi/backlog có thể lâu hơn); nhánh do luật cứng quyết.")
    [s] = dv.mo_kho_sk().gan_day("hr-codex", "nho.agent_ghi", 9)
    assert s.du_lieu["giao_id"] == GID and s.du_lieu["vai"] == "coder"


def test_http_noi_bo_van_chay_va_bang_chung_mcp_khong_mo_duoc_no(mt):
    from asgi_gia import goi
    app, _ = mt
    than, h = {"truy_van": "nội dung", "vung_cap": ["/chung"]}, {"Host": "127.0.0.1:7710"}   # asgi_gia mặc định 7700
    assert goi(app, "POST", "/nho-lai", json_body=than, headers={**h, "Authorization": "Bearer tok-nho"}).status == 200
    assert goi(app, "POST", "/nho-lai", json_body=than, headers={**h, **H_PHIEU}).status == 401
    assert goi(app, "POST", "/nho-lai", json_body=than, headers={**h, **H_TAY}).status == 401


def test_sdk_ghim_phien_ban_va_chi_may_chu_mcp_import():
    assert version("mcp") == "1.30.0"
    goc = Path(__file__).resolve().parents[1] / "tram"
    co = sorted(str(p.relative_to(goc)) for p in goc.rglob("*.py")
                if re.search(r"^\s*(import mcp\b|from mcp[\s.])", p.read_text(encoding="utf-8"), re.M))
    assert co == ["nho/may_chu_mcp.py"]
