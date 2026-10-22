"""bs-78r.10 (dot6-Q02) — Q2: quota lỗi/quá hạn/không thu hồi không làm hỏng nhịp tim; token không lộ. Nhịp gửi qua
`khach` giả; app-server là bản GIẢ (python của user đang test) sau principal giả cùng user — không sudo thật."""
import functools
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.chay_cli.bo_cli import BO_CLI
from tram.chay_cli.codex.app_server import LoiAppServer, hoi_app_server
from tram.chay_cli.codex.bo import BoCodex
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.principal import ChuaCoPrincipal
from tram.tho.vong_khe import VongKhe

GIA = Path(__file__).parent / "du_lieu" / "codex" / "app_server_gia.py"
BI_MAT = ("SENTINEL-MAY-9c1e", "SENTINEL-OPENAI-44d2", "SENTINEL-SERVER-0b7f")


class PrincipalGia:
    """Cùng user đang test: thay `codex app-server` bằng app-server giả, tiêm biến điều khiển qua /usr/bin/env."""
    user = "tram-k-c-codex-1"

    def __init__(self, *bien: str):
        self.bien = list(bien)

    def boc(self, argv):
        return ["/usr/bin/env", *self.bien, sys.executable, str(GIA)] if argv[-1] == "app-server" else argv

    def kill_nhom(self, pgid, sig):
        kill_cuc_bo(pgid, sig)


def _vk(tmp_path, monkeypatch, hoi, principal):
    thu_tu = []
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: 600)   # UID thật: test_danh_tinh, G3
    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: thu_tu.append("hoi") or hoi(*a, **k)))
    k = KheCauHinh("codex-1", "codex", "user:x", tmp_path / "cfg", "Codex 1", ("coder",))
    gui = []
    khach = SimpleNamespace(goi=lambda m, u, than: thu_tu.append("nhip") or gui.append(than) or (200, {"phieu": None}))
    nc = NguCanhTho(CauHinhTho("C", "http://127.0.0.1:7700", (k,)), khach, goc=tmp_path / "tho-home",
                    principal_cua=principal)
    vk = VongKhe(nc, k)
    vk.hop = SimpleNamespace(gui=lambda _: None)
    vk.han_muc.da_xac_minh = True                       # nhịp xác minh UID riêng: test_han_muc_principal
    return vk, gui, thu_tu


def _nhip_hai_lan(vk):
    vk.nhip()
    vk.han_muc.lan_sau = 0.0
    return vk.nhip()


@pytest.mark.parametrize("loi", [LoiAppServer("x"), OSError("y"), RuntimeError("BI-MAT-LOI"), ChuaCoPrincipal("z")])
def test_quota_loi_nhip_van_gui_va_sau_khi_gui(tmp_path, monkeypatch, capsys, loi):
    def hoi(*a, **k):
        raise loi
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, hoi, lambda k, wt, ten: PrincipalGia())
    assert _nhip_hai_lan(vk) == {"phieu": None} and len(gui) == 2 and thu_tu[:2] == ["nhip", "hoi"]
    assert vk.so.doc_han_muc() is None and "BI-MAT-LOI" not in capsys.readouterr().out


def test_thieu_principal_khong_spawn_nhip_van_gui(tmp_path, monkeypatch):
    def khong_co(k, wt, ten):
        raise ChuaCoPrincipal("chưa khai")
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, lambda *a, **k: pytest.fail("không được hỏi quota"), khong_co)
    _nhip_hai_lan(vk)
    assert len(gui) == 2 and "hoi" not in thu_tu


def test_khong_thu_hoi_duoc_thi_dung_khe_khong_doc_lai(tmp_path, monkeypatch, capsys):
    def hoi(*a, **k):
        raise LoiThuHoi("x")
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, hoi, lambda k, wt, ten: PrincipalGia())
    _nhip_hai_lan(vk)
    assert gui and thu_tu.count("hoi") == 1 and vk.han_muc.khoa and vk.hong
    assert "dừng khe để kiểm principal" in capsys.readouterr().out


def test_app_server_treo_co_han_nhip_ke_tiep_van_gui(tmp_path, monkeypatch):
    vk, gui, _ = _vk(tmp_path, monkeypatch, functools.partial(hoi_app_server, thoi_gian_cho=0.5),
                     lambda k, wt, ten: PrincipalGia("CHE_DO=treo"))
    t0 = time.monotonic()
    _nhip_hai_lan(vk)
    assert len(gui) == 2 and time.monotonic() - t0 < 15 and vk.so.doc_han_muc() is None


def test_sentinel_token_khong_lo_qua_env_log_hay_nhip(tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("TRAM_THO_TOKEN", BI_MAT[0])
    monkeypatch.setenv("OPENAI_API_KEY", BI_MAT[1])
    env_con = tmp_path / "env-con.json"
    vk, gui, _ = _vk(tmp_path, monkeypatch, hoi_app_server,
                     lambda k, wt, ten: PrincipalGia("CHE_DO=lo", f"LO={BI_MAT[2]}", f"GHI_ENV={env_con}"))
    _nhip_hai_lan(vk)
    con = json.loads(env_con.read_text())
    assert not any(b in json.dumps(con["env"]) for b in BI_MAT[:2])
    assert not {"HOME", "USER", "TMPDIR", "TRAM_THO_TOKEN", "OPENAI_API_KEY"} & set(con["env"])
    ra = "".join(capfd.readouterr()) + json.dumps(gui)
    assert len(gui) == 2 and not any(b in ra for b in BI_MAT[:2]) and BI_MAT[2] not in json.dumps(gui)


def test_ghi_so_han_muc_loi_khong_lam_chet_nhip(tmp_path, monkeypatch):
    mau = json.loads((GIA.parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))["plus"]
    vk, gui, _ = _vk(tmp_path, monkeypatch, lambda *a, **k: mau, lambda k, wt, ten: PrincipalGia())
    monkeypatch.setattr(vk.so, "luu_han_muc", lambda hm: (_ for _ in ()).throw(OSError("đĩa đầy")))
    assert _nhip_hai_lan(vk) == {"phieu": None} and len(gui) == 2 and not vk.hong
