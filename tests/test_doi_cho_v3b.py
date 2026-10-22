"""Giữ đường import và cách khai CLI khi dời mã V3b; không chạy lệnh hệ thống."""
import argparse
from importlib import import_module


def test_ten_cu_la_cung_doi_tuong_o_noi_moi():
    cac_cap = [
        ("beads.bd", "beads.loi", ("LoiBd", "KhongThayBead")),
        ("ban_giao.schema", "ban_giao.mo_hinh", ("DoiChieu", "LenhKiem", "HuongDaBo")),
        ("cau_hinh.du_an", "cau_hinh.moi_truong_kiem", ("MoiTruongKiem",)),
        ("phieu.kho", "phieu.mo_hinh", ("LuotCu",)),
        ("su_kien.kho", "su_kien.mo_hinh", ("SuKien",)),
        ("nho.nhat_ky", "nho.mo_hinh", ("ThaoTacNho",)),
        ("giao_viec.ban_chep", "giao_viec.repo_ban_chep", ("ten_ban_chep",)),
        ("giao_viec.cong_that", "giao_viec.quan_sat_kiem", ("env_kin",)),
    ]
    for cu, moi, ten in cac_cap:
        a, b = import_module(f"tram.{cu}"), import_module(f"tram.{moi}")
        for t in ten:
            assert getattr(a, t) is getattr(b, t), (cu, moi, t)


def test_lenh_go_duong_cu_chuyen_dung_doi_so_va_ket_qua(monkeypatch):
    from tram.chu import go_cai_dat_tho, lenh_go_tho
    args, hoi, ket_qua = object(), object(), object()
    goi = []

    def gia(a, *, hoi):
        goi.append((a, hoi))
        return ket_qua

    monkeypatch.setattr(lenh_go_tho, "lenh_cli", gia)
    assert go_cai_dat_tho.lenh_cli(args, hoi=hoi) is ket_qua
    assert goi == [(args, hoi)]


def test_khai_nghiem_thu_cu_va_cli_giu_tham_so():
    from tram.giao_viec import lenh, lenh_nghiem_thu
    cu, cli = argparse.ArgumentParser(), argparse.ArgumentParser()
    lenh_nghiem_thu.them(cu.add_subparsers(required=True))
    lenh.them_lenh_giao(cli.add_subparsers(required=True))
    for p, dau in ((cu, []), (cli, ["giao"])):
        a = p.parse_args([*dau, "nghiem-thu-kiem"])
        assert (a.tai_sinh, a.cho, a.trong, a.dau_ino, a.cha) == (False, 300.0, False, None, None)
        assert a.ham is not lenh_nghiem_thu.lenh_nghiem_thu and a.ham(a) == 2
        a = p.parse_args([*dau, "nghiem-thu-kiem", "--tai-sinh", "--cho", "240",
                          "--trong", "--dau-ino", "12", "--cha", "34"])
        assert (a.tai_sinh, a.cho, a.trong, a.dau_ino, a.cha) == (True, 240.0, True, 12, 34)
        assert a.ham is not lenh_nghiem_thu.lenh_nghiem_thu and a.ham(a) == 2
