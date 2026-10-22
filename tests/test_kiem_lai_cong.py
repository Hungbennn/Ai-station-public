"""3C-D4 (C01, D45): kiểm lại đi qua cổng lượt và hồ sơ của lượt — lượt N để lại tàn dư (tệp con trong thư mục cha
khác owner, ngoài vùng cho ghi), lượt N lỗi giữa chừng → lượt N+1 bị từ chối TRƯỚC khi chép và nhận môi trường kiểm;
mọi lệnh của lượt đi qua `boc_luot(wt)`. git/tar/rm thật trong `tmp_path` (boc đồng nhất), quan sát giả, không sudo."""
import argparse
import os

import pytest

from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec import lenh
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.cong_that import thu_hoi_theo_uid
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kiem_lai import kiem_lai
from tram.giao_viec.noi_that import dung_bo_that
from tram.giao_viec.principal_kiem import tu_cach_ly


def cong(tmp):
    """Quan sát giả: tàn dư = tệp `TAN_DU` (đứng cho mục của tram-kiem trong thư mục cha 0777 của user khác)."""
    def q():
        if (tmp / "TAN_DU").exists():
            raise LoiBanChep("tram-kiem còn 1 mục ngoài bản chép (vùng ghi-chung, thư mục cha khác owner)")
    c = CongLuot(tmp / "cong.json", thu_hoi=lambda: None, quan_sat=[q], ngu=lambda s: None)
    c.mo_lai()
    return c


def chay(m, c, *, kiem="exit 0\n", boc_luot=lambda wt: lambda a: a):
    k, da, tmp = m
    sha = k.day("tram/hr-1", {"kiem.sh": kiem}, tu=k.main)
    fetch(k.kho)
    return kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"],
                    chay_lenh=True, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
                    env_goc=os.environ, cong=c, boc_luot=boc_luot)


def test_luot_n_de_tan_du_thi_luot_n1_khong_chep_khong_nhan_moi_truong(m):
    tmp, goi = m[2], []
    c = cong(tmp)
    with pytest.raises(CongDong, match="ngoài bản chép"):
        chay(m, c, kiem=f"touch {tmp}/TAN_DU\n")
    assert c.trang_thai()["trang_thai"] == "dong" and ban_chep(m) == []
    (tmp / "TAN_DU").unlink()                                      # tàn dư đã biến mất: cổng VẪN đóng tới khi mở lại
    with pytest.raises(CongDong, match="dong"):
        chay(m, c, kiem=f"touch {tmp}/N1_DA_CHAY\n", boc_luot=lambda wt: goi.append(wt) or (lambda a: a))
    assert goi == [] and not (tmp / "N1_DA_CHAY").exists() and ban_chep(m) == []


def test_moi_lenh_cua_luot_di_qua_boc_luot_khong_qua_boc_chung(m):
    da_boc, c = [], cong(m[2])

    def boc_luot(wt):
        return lambda a: da_boc.append((wt, a[0].rsplit("/", 1)[-1])) or a
    assert chay(m, c, boc_luot=boc_luot).dat and c.trang_thai()["trang_thai"] == "mo"
    assert len({wt for wt, _ in da_boc}) == 1 and {"mkdir", "tar", "env", "sh", "rm"} <= {x for _, x in da_boc}


def test_luot_loi_giua_chung_thi_dong_cong_va_chan_luot_sau(m):
    c = cong(m[2])
    with pytest.raises(LoiBanChep):
        chay(m, c, boc_luot=lambda wt: lambda a: ["/usr/bin/false"] if a[0] == "/usr/bin/tar" else a)
    assert c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"}
    with pytest.raises(CongDong):
        chay(m, c)


def test_bo_that_chi_co_cong_tu_xa_ke_ca_khi_khai_tram_kiem(tram_home_tam, tmp_path):
    pk = tu_cach_ly("user:tram-kiem")
    bo = dung_bo_that(CauHinhGiaoViec(thu_muc_kiem=tmp_path / "k", principal_kiem=pk), CauHinhTram())
    assert type(bo.cong).__name__ == 'CongTuXa' and bo.kiem_tu_xa is not None
    assert bo.boc_luot is None and bo.boc is None and bo.don_sach is None
    assert type(dung_bo_that(CauHinhGiaoViec(), CauHinhTram()).cong).__name__ == 'CongTuXa'


@pytest.mark.parametrize("tan_du, ma, sau", [(False, 0, "mo"), (True, 1, "dong")])
def test_lenh_mo_cong_kiem_chi_mo_khi_sach(monkeypatch, tmp_path, tan_du, ma, sau):
    c = cong(tmp_path)
    c.dong("lượt g-1: LoiBanChep")
    if tan_du:
        (tmp_path / "TAN_DU").touch()
    monkeypatch.setattr(lenh, "_bo", lambda: (None, argparse.Namespace(cong=c)))
    assert lenh._mo_cong(argparse.Namespace(dong_y=True)) == ma and c.trang_thai()["trang_thai"] == sau
