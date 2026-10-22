"""Kiểm lại (spec 4 §6.2) — G1, G4, G9: mọi lệnh bắt buộc tại SHA công bố; không khớp/timeout/fail → không đạt."""
import os
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kiem_lai import kiem_lai

MAU = ["sh kiem.sh", "sh kiem.sh *", "sh cham.sh"]


@pytest.fixture
def m(tmp_path):
    k = dung_kho(tmp_path)
    env = tmp_path / "env.testing"
    env.write_text("DB_DATABASE=test\n")
    da = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(env, ".env.testing"))
    return k, da, tmp_path


def chay(m, tep, lenh, *, chay_lenh=True, da=None, cho=30):
    k, d, tmp = m
    sha = k.day("tram/hr-1", tep, tu=k.main)
    fetch(k.kho)
    return kiem_lai(k.kho, da or d, giao_id="g-1", commit=sha, lenh_kiem=lenh, lenh_cho_phep=MAU,
                    chay_lenh=chay_lenh, thu_muc=tmp / "kiem", thu_muc_log=tmp / "log", boc=lambda a: a,
                    env_goc=os.environ, thoi_gian_cho=cho)


def test_dat_khi_moi_lenh_pass_va_co_moi_truong_kiem(m):
    kq = chay(m, {"kiem.sh": 'grep -q DB_DATABASE=test .env.testing && [ "$APP_ENV" = testing ]\n'}, ["sh kiem.sh"])
    assert kq.dat and kq.ket_qua[0]["ket_qua"] == "pass" and kq.digest_log[0].startswith("sha256:")
    assert list((m[2] / "kiem").iterdir()) == []                          # bản chép kiểm đã dọn (3c)


def test_suite_bat_buoc_fail_du_lenh_khac_pass(m):
    kq = chay(m, {"kiem.sh": "exit 0\n", "cham.sh": "exit 1\n"}, ["sh kiem.sh", "sh cham.sh"])
    assert not kq.dat and [k["ket_qua"] for k in kq.ket_qua] == ["pass", "fail"]


@pytest.mark.parametrize("lenh", ["sh kiem.sh; rm -rf /", "sh kiem.sh $(id)", "sh khac.sh", "sh kiem.sh --x"])
def test_lenh_khong_khop_allowlist_khong_chay_va_khong_dat(m, lenh):
    kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, [lenh])
    assert not kq.dat and kq.ket_qua[0]["ket_qua"] == "fail"


def test_khong_co_lenh_bat_buoc_thi_khong_dat(m):
    assert not chay(m, {}, []).dat


def test_timeout_khong_dat(m):
    kq = chay(m, {"kiem.sh": "sleep 5\n"}, ["sh kiem.sh"], cho=0.5)
    assert not kq.dat and kq.ket_qua[0]["ket_qua"] == "fail"


def test_cham_duong_dan_cam_khong_chay_lenh_nao(m):
    k, _, tmp = m
    kq = chay(m, {"package.json": "{}", "kiem.sh": f"touch {tmp}/DA_CHAY\n"}, ["sh kiem.sh"])
    assert (kq.dat, kq.loi, kq.cham_cam) == (False, "dong-file-cau-hinh", ("package.json",))
    assert not (tmp / "DA_CHAY").exists()


def test_spike_tai_lieu_khong_chay_lenh(m):
    kq = chay(m, {"docs/spikes/x.md": "kết luận", "kiem.sh": "exit 1\n"}, [], chay_lenh=False)
    assert kq.dat and kq.ket_qua == ()


def test_thieu_moi_truong_kiem(m):
    k, d, tmp = m
    assert chay(m, {}, ["sh kiem.sh"], da=DuAn("hr-codex", Path("/r"), None, {})).loi == "thieu-moi-truong-kiem"
    hong = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(tmp / "khong-co", ".env.testing"))
    assert chay(m, {}, ["sh kiem.sh"], da=hong).loi == "thieu-moi-truong-kiem"


def test_dich_moi_truong_kiem_la_symlink_bi_tu_choi(m):
    k, d, tmp = m
    os.symlink("/tmp/ra-ngoai", k.dev / ".env.testing")
    kq = chay(m, {"kiem.sh": "exit 0\n"}, ["sh kiem.sh"])
    assert kq.loi == "thieu-moi-truong-kiem" and not kq.dat
