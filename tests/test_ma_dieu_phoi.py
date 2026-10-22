"""Mã điều phối riêng của hook máy A (D24; plan 2e Task 6, G2, G23): khoá băm riêng, lệnh hỏi ẩn, khác mã Đại ca,
KHÔNG đọc được memory (MCP phiên tay lẫn HTTP nội bộ của memory service)."""
from types import SimpleNamespace as NS

import pytest

from asgi_gia import goi
from mcp_gia import goi_cong_cu, goi_mcp, van_ban
from nho_gia import EmbedderGia, ky_uc
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.chu.ma_dieu_phoi import dat_ma_dieu_phoi, doc_bam, ghi_bam
from tram.nho import ma_dai_ca
from tram.nho.dich_vu import DichVuNho
from tram.nho.kho import KhoKyUc
from tram.nho.may_chu_mcp import tao_ung_dung
from tram.nho.nho_lai import BoDemDung
from tram.nho.ung_dung import CauHinhMcp
from tram.su_kien.kho import KhoSuKien

MA_DP, MA_DC = "d1" * 32, "c2" * 32                     # mã điều phối, mã Đại ca
CU = "# cấu hình trạm — Đại ca sửa tay\ndai_ca_logins: [dai-ca@example.com]\nten_may_b: may-b.tail.ts.net\n"


def test_khoa_rieng_giu_chu_thich_va_ma_dai_ca(tram_home_tam):
    p = tram_home_tam / "cau-hinh.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(CU, encoding="utf-8")
    assert doc_bam() is None
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    ghi_bam(ma_dai_ca.bam(MA_DP))
    assert doc_bam() == ma_dai_ca.bam(MA_DP) and ma_dai_ca.doc_bam() == ma_dai_ca.bam(MA_DC)
    ghi_bam("0" * 64)
    van_ban_moi = p.read_text(encoding="utf-8")
    assert van_ban_moi.startswith(CU) and van_ban_moi.count("dieu_phoi_ma_sha256") == 1 and doc_bam() == "0" * 64
    assert nap_cau_hinh_tram(p).ten_may_b == "may-b.tail.ts.net" and not list(p.parent.glob(".cau-hinh-*"))
    for hong in ("dieu_phoi_ma_sha256: 123\n", ": : :\n  - ["):
        p.write_text(hong, encoding="utf-8")
        assert doc_bam() is None
    with pytest.raises(ValueError):
        ghi_bam("khong-phai-hex")


def test_tu_choi_ma_trung_ma_dai_ca(tram_home_tam, capsys):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    with pytest.raises(ValueError, match="KHÁC mã Đại ca"):
        ghi_bam(ma_dai_ca.bam(MA_DC))
    nhap = iter([MA_DC, MA_DC])
    assert dat_ma_dieu_phoi(NS(dong_y=True), doc_an=lambda _: next(nhap), hoi=lambda _: "") == 1
    assert doc_bam() is None and MA_DC not in capsys.readouterr().out


def test_lenh_hoi_an_hai_lan_khong_in_ma_va_tu_choi_dau_vao_sai(tram_home_tam, capsys):
    for nhap, hoi in (([MA_DP, MA_DP], "khong"), ([MA_DP, MA_DP[:-1] + "x"], "dong-y"), (["ngan", "ngan"], "dong-y")):
        it = iter(nhap)
        assert dat_ma_dieu_phoi(NS(dong_y=False), doc_an=lambda _: next(it), hoi=lambda _: hoi) == 1
    assert doc_bam() is None and not (tram_home_tam / "cau-hinh.yaml").exists()
    nhap = iter([MA_DP, MA_DP])
    assert dat_ma_dieu_phoi(NS(dong_y=False), doc_an=lambda _: next(nhap), hoi=lambda _: "dong-y") == 0
    out = capsys.readouterr()
    assert doc_bam() == ma_dai_ca.bam(MA_DP) and MA_DP not in out.out + out.err and "Terminal.app" in out.out


def test_cli_chu_dat_ma_dieu_phoi_khong_nhan_ma_qua_argv(monkeypatch, tram_home_tam):
    from tram.cli import main, tao_parser
    nhap = iter([MA_DP, MA_DP])
    monkeypatch.setattr("getpass.getpass", lambda _: next(nhap))
    assert main(["chu", "dat-ma-dieu-phoi", "--dong-y"]) == 0 and doc_bam() == ma_dai_ca.bam(MA_DP)
    with pytest.raises(SystemExit):
        tao_parser().parse_args(["chu", "dat-ma-dieu-phoi", "--ma", MA_DP])


def test_ma_dieu_phoi_khong_doc_duoc_memory(tmp_path, tram_home_tam):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    ghi_bam(ma_dai_ca.bam(MA_DP))                       # cả hai băm cùng nằm trong ~/.tram/cau-hinh.yaml tạm
    e = EmbedderGia()
    kho = KhoKyUc(tmp_path / "l", so_chieu=e.so_chieu)
    kho.them(ky_uc("m-y", "/du-an/erp/nghiep-vu", vector=e.embed(["m-y"])[0], noi_dung="Nội dung m-y"))
    e.goi.clear()
    dv = DichVuNho(kho, e, lambda: KhoSuKien(tmp_path / "sk.db"), BoDemDung(), "tok-nho")
    app = tao_ung_dung(dv, CauHinhMcp(lambda g: None, ma_dai_ca.doc_bam, lambda t: t == "erp"))   # bộ đọc băm THẬT
    hoi = goi_cong_cu("nho_lai", {"truy_van": "nội dung"})
    dp, dc = goi_mcp(app, ("POST", "/mcp", hoi, {"Authorization": f"Bearer {MA_DP}", "X-Tram-Du-An": "erp"}),
                     ("POST", "/mcp", hoi, {"Authorization": f"Bearer {MA_DC}", "X-Tram-Du-An": "erp"}))
    assert dp.status == 401 and MA_DP not in dp.body.decode()
    assert van_ban(dc)[0] is False and "m-y" in van_ban(dc)[1]          # đối chứng: mã Đại ca vẫn đọc được
    than = {"truy_van": "nội dung", "vung_cap": ["/du-an/erp"]}
    assert goi(app, "POST", "/nho-lai", json_body=than,
               headers={"Authorization": f"Bearer {MA_DP}", "Host": "127.0.0.1:7710"}).status == 401
    assert e.goi == [["nội dung"]]                       # chỉ lời gọi của mã Đại ca chạm tới embedder
