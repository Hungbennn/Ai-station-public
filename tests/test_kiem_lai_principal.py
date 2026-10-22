"""Kiểm lại dưới principal `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1; lát 3c D22): `don_sach` (giết mọi
tiến trình tram-kiem) TRƯỚC khi chép bản chép và TRƯỚC khi dọn. Không chạy sudo thật — `boc` đồng nhất, `don_sach`
giả."""
import os
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kiem_lai import kiem_lai
from tram.kiem.chay_lenh import _kill_nhom


@pytest.fixture
def m(tmp_path):
    k = dung_kho(tmp_path)
    env = tmp_path / "env.testing"
    env.write_text("DB_DATABASE=test\n")
    return k, DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(env, ".env.testing")), tmp_path


def chay(m, tep, *, lenh=("sh kiem.sh",), don_sach=None, chay_lenh=True, kill=_kill_nhom, boc=lambda a: a):
    k, da, tmp = m
    sha = k.day("tram/hr-1", tep, tu=k.main)
    fetch(k.kho)
    return kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=list(lenh), lenh_cho_phep=["sh kiem.sh"],
                    chay_lenh=chay_lenh, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=boc,
                    env_goc=os.environ, don_sach=don_sach, kill=kill)


def ban_chep(m) -> list[Path]:
    return sorted((m[2] / "kiem-ngoai").iterdir()) if (m[2] / "kiem-ngoai").exists() else []


def test_don_sach_truoc_khi_chep_va_truoc_khi_don(m):
    thay = []

    def don_sach():
        thay.append([(p.name.startswith("g-1-"), (p / "DA_CHAY").exists()) for p in ban_chep(m)])

    kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, don_sach=don_sach)
    assert kq.dat and thay == [[], [(True, True), (True, False)]] and ban_chep(m) == []    # bản chép + nhà của lượt


def test_con_tien_trinh_tram_kiem_thi_khong_chep_khong_chay(m):
    def don_sach():
        raise LoiBanChep("tram-kiem còn 1 tiến trình")

    with pytest.raises(LoiBanChep):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, don_sach=don_sach)
    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []


def test_spike_va_cham_cam_khong_don_sach(m):
    goi = []
    assert chay(m, {"docs/spikes/x.md": "kết luận"}, lenh=(), chay_lenh=False, don_sach=lambda: goi.append(1)).dat
    assert chay(m, {"package.json": "{}"}, don_sach=lambda: goi.append(1)).loi == "dong-file-cau-hinh" and goi == []

def test_kiem_lai_truyen_kill_principal(m, monkeypatch):
    from types import SimpleNamespace
    kill = lambda pid, sig: None
    goi = []
    def gia(*args, **kw):
        goi.append(kw["kill"])
        return SimpleNamespace(sang_lenh_kiem=lambda: {"ket_qua": "pass", "digest_log": "sha256:x"}, da_thu_hoi=True)
    monkeypatch.setattr("tram.giao_viec.kiem_lai.chay_mot_lenh", gia)
    assert chay(m, {"kiem.sh": "true\n"}, kill=kill).dat
    assert goi == [kill]

