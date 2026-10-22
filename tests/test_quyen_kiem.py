"""Chuỗi phía cài đặt của `tram-kiem` theo D22 (lát 3c): `thu_muc_kiem`, dòng sudoers (runas CHỈ tram-kiem, không
root), hồ sơ sandbox cố định. Chỉ kiểm chuỗi — KHÔNG sudo, không visudo."""
import fnmatch
from pathlib import Path

import pytest

from tram.tho.principal import Principal
from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem, goc_hop_le


def test_goc_phai_la_duong_dan_that(tmp_path):
    (tmp_path / "that").mkdir()
    (tmp_path / "lien-ket").symlink_to(tmp_path / "that")
    goc = tmp_path.resolve()
    assert goc_hop_le(goc / "that") == str(goc / "that")
    for sai in (Path("tuong/doi"), Path("/"), goc / "lien-ket", goc / "a b", Path(f"{goc}/that/../that"),
                Path(f"{goc}/x'y"), Path(f"{goc}/x,y"), Path(f'{goc}/x"y')):
        with pytest.raises(ValueError):
            goc_hop_le(sai)


def _khop(dong: str, argv: list[str]) -> bool:
    """Mô phỏng khớp lệnh sudoers: phần sau `NOPASSWD:SETENV:` so với argv SAU `--` của `sudo` (fnmatch: `*` khớp cả
    `/` và dấu cách — đúng như sudoers)."""
    mau = dong.split("NOPASSWD:SETENV: ", 1)[1]
    lenh = argv[argv.index("--") + 1:]
    return mau == "ALL" or fnmatch.fnmatchcase(" ".join(lenh), mau)


def test_co_che_user_chi_runas_tram_kiem_khong_root():
    dong = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="user")
    assert dong == "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" and "root" not in dong


def test_co_che_sandbox_ghim_tien_to_ho_so_co_dinh():
    dong = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="sandbox")
    assert dong == f"hung ALL=(tram-kiem) NOPASSWD:SETENV: /usr/bin/sandbox-exec -f {HO_SO_KIEM} *"
    p = Principal("sandbox", "tram-kiem", HO_SO_KIEM)
    for argv in (["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"], ["/bin/rm", "-rf", "/k/g-1"], ["php", "a b"]):
        assert _khop(dong, p.boc(argv))
    assert not _khop(dong, Principal("user", "tram-kiem").boc(["/bin/rm", "-rf", "/k"]))     # bỏ sandbox: từ chối
    assert not _khop(dong, Principal("sandbox", "tram-kiem", Path("/tmp/x.sb")).boc(["/bin/sh"]))  # hồ sơ khác: từ chối


@pytest.mark.parametrize("kw", [dict(tram="hung", tram_kiem="hung", co_che="user"),
                                dict(tram="hung", tram_kiem="Tram Kiem", co_che="user"),
                                dict(tram="hung", tram_kiem="tram-kiem", co_che="root")])
def test_sai_dang_la_loi(kw):
    with pytest.raises(ValueError):
        dong_sudoers_kiem(**kw)
