"""bs-78r.10 (dot6-Q02) — Q1: quota khe rảnh đi `DocHanMucRanh → BoCodex.doc_han_muc_ranh → hoi_app_server` dưới
principal CỦA KHE. `hoi` là spy: không sudo/app-server thật nào được chạy; argv dựng bằng `Principal.boc` thật."""
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from tram.chay_cli.bo_cli import BO_CLI
from tram.chay_cli.codex.app_server import doc_han_muc_ranh
from tram.chay_cli.codex.bo import BoCodex
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_may import DauDo
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.principal import BIEN_GIU, SANDBOX_EXEC, SUDO
from tram.tho.so_khe import SoKhe
from tram.tho.vong_khe import VongKhe

MAU = json.loads((Path(__file__).parent / "du_lieu" / "codex" / "app_server_rate_limits.json").read_text())["plus"]


def _nc(tmp_path):
    k = [KheCauHinh("codex-1", "codex", "user:tram-k-c-codex-1", tmp_path / "cfg1", "Codex 1", ("coder",)),
         KheCauHinh("codex-2", "codex", "sandbox:tram-exec", tmp_path / "cfg2", "Codex 2", ("coder",)),
         KheCauHinh("codex-3", "codex", None, tmp_path / "cfg3", "Codex 3", ("coder",))]
    ch = CauHinhTho("C", "http://127.0.0.1:7700", tuple(k))
    khach = SimpleNamespace(goi=lambda m, u, than: (200, {"tiep_tuc": True, "phieu": None}))
    return NguCanhTho(ch, khach, goc=tmp_path / "tho-home", goc_wt=tmp_path / "wt"), k


def test_hai_khe_hai_co_che_dung_principal_env_kill_thieu_principal_khong_spawn(tmp_path, monkeypatch):
    goi, xm = [], []
    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda argv, *, env, kill: goi.append((argv, env, kill)) or MAU))
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda ten, boc, kill: xm.append((ten, boc([]))) or 600)
    for bien, gia_tri in (("HOME", "/Users/quan-ly"), ("USER", "quan-ly"), ("TMPDIR", "/var/folders/ql"),
                          ("TRAM_THO_TOKEN", "BI-MAT-MAY")):
        monkeypatch.setenv(bien, gia_tri)
    nc, k = _nc(tmp_path)
    for x in k:                                                            # đúng đường VongKhe.nhip của từng khe
        vk = VongKhe(nc, x)
        vk.hop = SimpleNamespace(gui=lambda _: None)
        vk.nhip()                                                          # nhịp 1: chỉ xác minh UID
        vk.nhip()                                                          # nhịp 2: hỏi app-server
    assert len(goi) == 2                                                   # codex-3 thiếu principal: không spawn
    (a1, e1, kill1), (a2, e2, kill2) = goi
    assert a1 == [SUDO, "-n", "-H", "-u", "tram-k-c-codex-1", f"--preserve-env={','.join(BIEN_GIU)}", "--", "codex",
                  "app-server"]
    ho_so = nc.goc / "sandbox" / "C" / "codex-2" / "han-muc.sb"
    assert a2[:5] == [SUDO, "-n", "-H", "-u", "tram-exec"] and a2[-5:] == [SANDBOX_EXEC, "-f", str(ho_so), "codex",
                                                                            "app-server"]
    assert (e1["CODEX_HOME"], e2["CODEX_HOME"]) == (str(k[0].thu_muc_cau_hinh), str(k[1].thu_muc_cau_hinh))
    assert all(set(e) == {"PATH", "LANG", "CODEX_HOME"} and e["PATH"] == nc.ch.chay.path_cli for e in (e1, e2))
    assert [x[0] for x in xm] == ["tram-k-c-codex-1", "tram-exec"] and xm[1][1][-3:] == [SANDBOX_EXEC, "-f", str(ho_so)]
    assert (kill1.__self__.user, kill2.__self__.user) == ("tram-k-c-codex-1", "tram-exec")
    hs = ho_so.read_text()
    for khac in (k[0], k[2]):                                              # wt=None không nới sang khe khác
        assert f'(deny file-read* file-write* (subpath "{khac.thu_muc_cau_hinh}"))' in hs
    assert f'(allow file-read* file-write* (subpath "{k[1].thu_muc_cau_hinh}"))' in hs
    assert [SoKhe("C", x.ten, nc.goc).doc_han_muc() is not None for x in k] == [True, True, False]


def test_kiem_3b_dung_principal_khe_va_bao_do_khi_khong_thu_hoi(tmp_path):
    nc, k = _nc(tmp_path)
    dd = DauDo(ping=lambda: {}, du_an=lambda: [], which=lambda c: None, con_trong=lambda p: 1,
               chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout="", stderr=""), thu_muc_kho=tmp_path)
    goi = []

    def doc(kid, thu_muc, *, bay_gio, principal, path, codex):
        goi.append((kid, principal))
        if kid.endswith("codex-2"):
            raise LoiThuHoi("x")
        return None
    ds = {m.muc: m.muc_do for m in bo_sung_3b(nc.ch, dd, [], doc_han_muc=doc, bay_gio=datetime.now(timezone.utc),
                                              principal_cua_=lambda ch, x: None if x.principal is None else x.ten,
                                              dang_nhap_=lambda *a, **kw: (None, "không kết luận"))}
    assert goi == [("C/codex-1", "codex-1"), ("C/codex-2", "codex-2"), ("C/codex-3", None)]
    assert [ds[f"C/codex-{i} hạn mức"] for i in (1, 2, 3)] == ["vang", "do", "vang"]


def test_kiem_3b_mac_dinh_khe_thieu_principal_khong_spawn(tmp_path):
    nc, k = _nc(tmp_path)
    goi = []

    def doc(kid, thu_muc, **kw):
        return doc_han_muc_ranh(kid, thu_muc, hoi=lambda *a, **x: goi.append(a), **kw)
    dd = DauDo(ping=lambda: {}, du_an=lambda: [], which=lambda c: None, con_trong=lambda p: 1,
               chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout="", stderr=""), thu_muc_kho=tmp_path)
    ds = {m.muc: m for m in bo_sung_3b(CauHinhTho("C", "http://127.0.0.1:7700", (k[2],)), dd, [], doc_han_muc=doc)}
    assert goi == [] and ds["C/codex-3 hạn mức"].muc_do == "vang" and "principal" in ds["C/codex-3 hạn mức"].chi_tiet


def test_uid_principal_chua_chung_minh_khong_hoi_quota(tmp_path, monkeypatch, capsys):
    from tram.kiem.danh_tinh import LoiDanhTinh
    goi = []
    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: goi.append(a) or MAU))
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))
    nc, k = _nc(tmp_path)
    vk = VongKhe(nc, k[0])
    vk.hop = SimpleNamespace(gui=lambda _: None)
    vk.nhip()
    vk.han_muc.lan_sau = 0.0
    vk.nhip()
    assert goi == [] and vk.han_muc.khoa and not vk.hong and "chưa chứng minh được UID" in capsys.readouterr().out


def test_cay_do_uid_khong_thu_hoi_duoc_thi_dung_khe(tmp_path, monkeypatch):
    from tram.kiem.vong_doi import LoiThuHoi
    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: _khong_duoc_hoi()))
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiThuHoi("x")))
    nc, k = _nc(tmp_path)
    vk = VongKhe(nc, k[0])
    vk.hop = SimpleNamespace(gui=lambda _: None)
    vk.nhip()
    assert vk.hong and vk.han_muc.khoa


def _khong_duoc_hoi():
    raise AssertionError("không được hỏi quota")
