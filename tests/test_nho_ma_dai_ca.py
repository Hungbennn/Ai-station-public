import hashlib
from types import SimpleNamespace as NS

import pytest

from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.nho.ma_dai_ca import bam, dat_ma_dai_ca, doc_bam, ghi_bam

MA = "a1" * 32
BAM = hashlib.sha256(MA.encode()).hexdigest()
CU = "# cấu hình trạm — Đại ca sửa tay\ndai_ca_logins: [dai-ca@example.com]\nten_may_b: may-b.tail.ts.net\n"


def test_bam_va_doc_khi_thieu_hong_hoac_sai_dang(tram_home_tam):
    assert bam(MA) == BAM and doc_bam() is None                       # chưa có file
    p = tram_home_tam / "cau-hinh.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    for van_ban in (": : :\n  - [", "- 1\n", "ma_dai_ca_sha256: 123\n", f"ma_dai_ca_sha256: {BAM.upper()}\n"):
        p.write_text(van_ban, encoding="utf-8")
        assert doc_bam() is None


def test_ghi_giu_chu_thich_va_khoa_khac_roi_thay_ban_cu(tram_home_tam):
    p = tram_home_tam / "cau-hinh.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(CU, encoding="utf-8")
    ghi_bam(BAM)
    assert p.read_text(encoding="utf-8") == CU + f'ma_dai_ca_sha256: "{BAM}"\n' and doc_bam() == BAM
    ghi_bam("0" * 64)
    assert p.read_text(encoding="utf-8").count("ma_dai_ca_sha256") == 1 and doc_bam() == "0" * 64
    ch = nap_cau_hinh_tram(p)
    assert ch.dai_ca_logins == ("dai-ca@example.com",) and ch.ten_may_b == "may-b.tail.ts.net"
    assert not list(p.parent.glob(".cau-hinh-*"))


def test_ghi_tao_file_khi_chua_co_va_tu_choi_gia_tri_hay_file_hong(tram_home_tam):
    ghi_bam(BAM)
    assert doc_bam() == BAM
    with pytest.raises(ValueError):
        ghi_bam("khong-phai-hex")
    p = tram_home_tam / "cau-hinh.yaml"
    p.write_text("- danh sách, không phải bảng\n", encoding="utf-8")
    with pytest.raises(ValueError, match="không đổi gì"):
        ghi_bam(BAM)
    assert p.read_text(encoding="utf-8") == "- danh sách, không phải bảng\n"


def test_lenh_hoi_an_hai_lan_khong_in_ma(tram_home_tam, capsys):
    nhap = iter([MA, MA])
    assert dat_ma_dai_ca(NS(dong_y=False), doc_an=lambda _: next(nhap), hoi=lambda _: "dong-y") == 0
    out = capsys.readouterr()
    assert doc_bam() == BAM and MA not in out.out + out.err and "Terminal.app" in out.out


@pytest.mark.parametrize("nhap, hoi", [([MA, MA], "khong"), ([MA, MA[:-1] + "x"], "dong-y"),
                                       (["ngan", "ngan"], "dong-y"), (["a b" * 20] * 2, "dong-y")])
def test_lenh_khong_dong_y_hoac_ma_sai_thi_khong_doi_gi(tram_home_tam, capsys, nhap, hoi):
    it = iter(nhap)
    assert dat_ma_dai_ca(NS(dong_y=False), doc_an=lambda _: next(it), hoi=lambda _: hoi) == 1
    assert doc_bam() is None and not (tram_home_tam / "cau-hinh.yaml").exists()
    assert MA not in capsys.readouterr().out


def test_cli_chu_dat_ma_dai_ca_khong_nhan_ma_qua_argv(monkeypatch, tram_home_tam):
    from tram.cli import main, tao_parser
    nhap = iter([MA, MA])
    monkeypatch.setattr("getpass.getpass", lambda _: next(nhap))
    assert main(["chu", "dat-ma-dai-ca", "--dong-y"]) == 0 and doc_bam() == BAM
    with pytest.raises(SystemExit):
        tao_parser().parse_args(["chu", "dat-ma-dai-ca", "--ma", MA])


def test_tu_choi_ma_trung_ma_dieu_phoi(tram_home_tam, capsys):      # bs-urj.17: chiều ngược của D24 / G23
    from tram.chu import ma_dieu_phoi
    from tram.nho.ma_dai_ca import KHOA_DIEU_PHOI
    assert KHOA_DIEU_PHOI == ma_dieu_phoi.KHOA                        # tầng nho không import tầng chu, test giữ khớp
    ma_dieu_phoi.ghi_bam(BAM)
    with pytest.raises(ValueError, match="KHÁC mã điều phối"):
        ghi_bam(BAM)
    nhap = iter([MA, MA])
    assert dat_ma_dai_ca(NS(dong_y=True), doc_an=lambda _: next(nhap), hoi=lambda _: "") == 1
    out = capsys.readouterr()
    assert doc_bam() is None and MA not in out.out + out.err and "KHÁC mã điều phối" in out.err
    assert ma_dieu_phoi.doc_bam() == BAM                               # băm điều phối giữ nguyên
    ghi_bam("0" * 64)                                                  # mã khác thì vẫn ghi được
    assert doc_bam() == "0" * 64 and ma_dieu_phoi.doc_bam() == BAM
    with pytest.raises(ValueError, match="KHÁC mã Đại ca"):           # chiều cũ không yếu đi
        ma_dieu_phoi.ghi_bam("0" * 64)
