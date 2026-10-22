import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

from nho_gia import EmbedderGia, ky_uc
from tram.nho.khoa import khoa_dich_vu, thu_muc_nho
from tram.nho.kho import KhoKyUc
from tram.nho.nhat_ky import NhatKy
from tram.nho.sao_luu import khoi_phuc_nho, sao_luu_nho

E = EmbedderGia()
LUC = datetime(2026, 10, 13, 3, 15, tzinfo=timezone.utc)


def mo(thu_muc):
    return KhoKyUc(thu_muc / "lancedb", so_chieu=E.so_chieu), NhatKy(thu_muc / "nhat-ky.db")


def test_sao_luu_roi_khoi_phuc_nhat_quan_ba_thu(tmp_path):
    nho, dich = tmp_path / "nho", tmp_path / "sao-luu"
    kho, nk = mo(nho)
    kho.them(ky_uc("m-1", vector=E.embed(["1"])[0]))
    nk.hoan_tat("5:1", 5)
    ban = sao_luu_nho(nho, dich, kho=kho, nhat_ky=nk, luc=LUC)
    assert ban.name == "nho-20261013-031500" and not list(dich.glob(".dang-chup-*"))
    kho.them(ky_uc("m-2", vector=E.embed(["2"])[0]))          # sau điểm chụp
    nk.hoan_tat("9:1", 9)
    nk.close()
    giu = khoi_phuc_nho(ban, nho, luc=LUC)
    kho2, nk2 = mo(nho)
    assert (kho2.dem(), nk2.moc(), nk2.lay("9:1")) == (1, 5, None)
    assert (giu / "lancedb").is_dir() and (giu / "nhat-ky.db").is_file()
    assert sorted(p.name for p in ban.iterdir()) == ["lancedb", "nhat-ky.db"]      # kiểm bản không ghi vào bản


def test_giu_toi_da_n_ban(tmp_path):
    nho, dich = tmp_path / "nho", tmp_path / "sao-luu"
    kho, nk = mo(nho)
    for i in range(4):
        sao_luu_nho(nho, dich, kho=kho, nhat_ky=nk, giu=2, luc=LUC + timedelta(days=i))
    assert [p.name for p in sorted(dich.iterdir())] == ["nho-20261015-031500", "nho-20261016-031500"]


def test_khoi_phuc_tu_choi_khi_dich_vu_dang_chay_hoac_ban_hong(tmp_path):
    nho = tmp_path / "nho"
    kho, nk = mo(nho)
    ban = sao_luu_nho(nho, tmp_path / "sl", kho=kho, nhat_ky=nk, luc=LUC)
    with khoa_dich_vu(nho) as duoc:
        assert duoc
        with pytest.raises(RuntimeError):
            khoi_phuc_nho(ban, nho, luc=LUC)
    with pytest.raises(ValueError):
        khoi_phuc_nho(tmp_path / "khong-co", nho, luc=LUC)


@pytest.mark.parametrize("pha", ["nhat_ky_rac", "nhat_ky_rong", "lancedb_rong"])
def test_khoi_phuc_ban_hong_thi_khong_dung_ban_hien_tai(tmp_path, pha):
    nho = tmp_path / "nho"
    kho, nk = mo(nho)
    kho.them(ky_uc("m-1", vector=E.embed(["1"])[0]))
    nk.hoan_tat("5:1", 5)
    ban = sao_luu_nho(nho, tmp_path / "sl", kho=kho, nhat_ky=nk, luc=LUC)
    nk.close()
    if pha == "nhat_ky_rac":
        (ban / "nhat-ky.db").write_bytes(b"khong phai sqlite" * 300)
    elif pha == "nhat_ky_rong":
        (ban / "nhat-ky.db").write_bytes(b"")
    else:
        shutil.rmtree(ban / "lancedb")
        (ban / "lancedb").mkdir()
    truoc = sorted(p.name for p in nho.iterdir())
    with pytest.raises(ValueError):
        khoi_phuc_nho(ban, nho, luc=LUC)
    assert sorted(p.name for p in nho.iterdir()) == truoc
    kho2, nk2 = mo(nho)
    assert (kho2.dem(), nk2.moc()) == (1, 5)


def test_sao_luu_don_ban_chup_do_dang_mo_coi(tmp_path):
    nho, dich = tmp_path / "nho", tmp_path / "sl"
    kho, nk = mo(nho)
    (dich / ".dang-chup-20261012-031500" / "lancedb").mkdir(parents=True)      # bị cắt ngang hôm trước
    (dich / ".dang-chup-20261014-000000").mkdir()                              # mới hơn — không phải của mình
    sao_luu_nho(nho, dich, kho=kho, nhat_ky=nk, luc=LUC)
    assert sorted(p.name for p in dich.iterdir()) == [".dang-chup-20261014-000000", "nho-20261013-031500"]


def test_flock_chan_ban_thu_hai_o_tien_trinh_khac(tmp_path):
    ma = ("import sys; from pathlib import Path; from tram.nho.khoa import khoa_dich_vu\n"
          "with khoa_dich_vu(Path(sys.argv[1])) as d: print(d)")
    with khoa_dich_vu(tmp_path) as duoc:
        assert duoc
        kq = subprocess.run([sys.executable, "-c", ma, str(tmp_path)], capture_output=True, text=True)
        assert kq.stdout.strip() == "False"
    kq = subprocess.run([sys.executable, "-c", ma, str(tmp_path)], capture_output=True, text=True)
    assert kq.stdout.strip() == "True"


def test_thu_muc_nho_trong_tram_home(tram_home_tam):
    assert thu_muc_nho() == tram_home_tam / "nho" and thu_muc_nho().is_dir()
