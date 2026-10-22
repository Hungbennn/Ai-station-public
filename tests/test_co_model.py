from dataclasses import replace
from pathlib import Path
import json
import pytest
from tram.tho.cau_hinh import _khe
from tram.chay_cli.lenh_claude import argv_claude
from tram.chay_cli.stream import DocStream
from tram.tho.co_model import lenh_model, dung_model
from tram.chay_cli.giao_dien import KetQuaChay
from tram.chay_cli.bo_cli import BoClaude
from tram.han_muc.claude import NguonHanMucClaude
from tram.phieu.cap import cap_phieu
from tram.phieu.kho import KhoPhieu
from tram.phieu.khe import dang_ky_khe
from kho_phieu_gia import LUC
from phieu_gia import de_xuat
from test_cap_phieu import _kho, CH


def test_cau_hinh_va_argv():
    raw = dict(ten="c", cli="claude", thu_muc_cau_hinh="/tmp/c", ten_goi_nho="c", vai_uu_tien=["coder"])
    assert _khe(raw).models == ()
    assert _khe({**raw, "models": ["sonnet", "opus"]}).models == ("sonnet", "opus")
    for bad in ["opus", ["gpt"], [True]]:
        with pytest.raises(ValueError):
            _khe({**raw, "models": bad})
    a = argv_claude(settings=Path("/s"), mcp=None)
    assert "--model" not in a
    assert lenh_model(a, "claude", ("opus",), {"model": "opus"}) == [*a, "--model", "opus"]
    assert lenh_model(a, "codex", (), None) == a
    with pytest.raises(ValueError):
        lenh_model(a, "codex", ("opus",), {"model": "opus"})


@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_argv_ep_effort_canh_model(effort):
    a = argv_claude(settings=Path("/s"), mcp=None)
    assert lenh_model(a, "claude", ("opus",), {"model": "opus", "effort": effort}) == [
        *a, "--model", "opus", "--effort", effort]
    assert "--effort" not in a
    assert lenh_model(a, "claude", ("opus",), None) is a
    with pytest.raises(ValueError):
        lenh_model(a, "codex", ("opus",), {"model": "opus", "effort": effort})


def test_stream_khong_tin_init_neu_assistant_doi_model():
    doc = DocStream(NguonHanMucClaude(), khe_id="B/c")
    doc.an(json.dumps({"type": "system", "subtype": "init", "model": "claude-opus-4-6"}))
    doc.an(json.dumps({"type": "assistant", "message": {"id": "a", "model": "claude-sonnet-4-6"}}))
    kq = doc.ket_qua(ma_thoat=0, bi_dung=False, thoi_gian_ms=1, digest_log="")
    assert not dung_model({"model": "opus"}, kq)
    assert not dung_model({"model": "sonnet"}, kq)
    assert dung_model(None, kq)


@pytest.mark.parametrize("thuc,dat", [(None,False),("opus",False),("claude-opus-4-6",True),
                                     ("claude-sonnet-4-6",False),("claude-opus-fake",False)])
def test_xac_nhan(thuc, dat):
    kq = KetQuaChay(0, True, False, False, False, mo_hinh=thuc)
    assert dung_model({"model": "opus"}, kq) is dat


@pytest.mark.parametrize("them", [{}, {"effort": "xhigh"}])
def test_snapshot_va_rollback(tmp_path, monkeypatch, them):
    kho = _kho(tmp_path)
    co = {"model": "opus", "co": "lon", "ban_luat": "v1", **them}
    dx = de_xuat(co=co)
    assert cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH).ly_do == "cho-model"
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [dict(ten="claude-1", cli="claude", ten_goi_nho="c",
                                  vai_uu_tien=["coder"], models=["opus"])], luc=LUC)
    ghi = kho.ghi_su_kien
    def hong(*a, **kw):
        raise OSError("ghi hong")
    monkeypatch.setattr(kho, "ghi_su_kien", hong)
    with pytest.raises(OSError):
        cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH)
    assert kho.db.execute("SELECT count(*) FROM phieu").fetchone()[0] == 0
    assert kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 0
    monkeypatch.setattr(kho, "ghi_su_kien", ghi)
    p = cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH).phieu
    kho.close()
    with __import__("contextlib").closing(KhoPhieu(tmp_path / "su-kien.db")) as k:
        assert k.lay(p.giao_id).phieu.co == co
        d = json.loads(k.db.execute("SELECT du_lieu FROM su_kien WHERE loai='giao.nhan'").fetchone()[0])
        assert d["co"] == co and p.ma_giao not in json.dumps(d)


@pytest.mark.parametrize("co,co_cli", [
    (None, []),
    ({"model": "opus"}, ["--model", "opus"]),
    ({"model": "opus", "effort": "max"}, ["--model", "opus", "--effort", "max"]),
])
def test_moi_lan_chay_dung_effort_cua_phieu(tmp_path, monkeypatch, co, co_cli):
    import threading
    from tho_chay_gia import dung_may, lay_phieu
    from tho_gia import ChayCLIGia
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan

    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    tt.phieu["co"] = co
    pc = chuan_bi(m.nc, replace(k, models=("opus",)), so, hop, tt)
    kq = KetQuaChay(0, True, False, False, False, mo_hinh="claude-opus-4-6")
    cli = ChayCLIGia(kq, kq)
    m.nc.tao_cli = lambda *a, **kw: cli
    for _ in range(2):
        assert dung_model(pc.p.co, chay_mot_lan(pc, m.nc, threading.Event()))
    assert [g["argv"] for g in cli.da_goi] == [argv_claude(settings=pc.settings, mcp=pc.mcp) + co_cli] * 2
