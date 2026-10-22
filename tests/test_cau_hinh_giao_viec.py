"""Khoá `giao_viec:` (4a-2) và adapter principal `tram-kiem` (chờ S6) — không chạy sudo thật. Lát 3c: principal
khai ở `cach_ly.tram_kiem` (MỘT nguồn); `giao_viec.principal_kiem` chỉ còn là khoá cũ để đối chiếu."""
import pytest

from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly

PK = "cach_ly:\n  tram_kiem: user:tram-kiem\n"
CU = "  principal_kiem:\n    ten: tram-kiem\n    boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]\n"


def _nap(tram_home, noi_dung: str) -> CauHinhGiaoViec:
    tram_home.mkdir(parents=True, exist_ok=True)
    (tram_home / "cau-hinh.yaml").write_text(noi_dung, encoding="utf-8")
    return nap_cau_hinh_giao_viec()


def test_thieu_file_hoac_thieu_khoa_la_tat(tram_home_tam):
    assert nap_cau_hinh_giao_viec() == CauHinhGiaoViec()
    cg = _nap(tram_home_tam, "dai_ca_logins: [a@b.c]\n")
    assert (cg.bat, cg.chu_ky_giay, cg.thu_muc_kiem, cg.principal_kiem) == (False, 120, None, None)


def test_doc_du_khoa(tram_home_tam, tmp_path):
    cg = _nap(tram_home_tam, PK + f"giao_viec:\n  bat: true\n  chu_ky_giay: 90\n  thu_muc_kiem: {tmp_path}/kiem\n")
    assert (cg.bat, cg.chu_ky_giay, cg.thu_muc_kiem) == (True, 90, tmp_path / "kiem")
    pk = cg.principal_kiem
    assert pk == tu_cach_ly("user:tram-kiem") and pk.ten == "tram-kiem"
    assert pk.boc_lenh(["sh", "kiem.sh"])[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"]


@pytest.mark.parametrize("noi_dung", [
    "giao_viec:\n  bat: 'co'\n",
    "giao_viec:\n  chu_ky_giay: 10\n",
    "giao_viec:\n  chu_ky_giay: 200\n",
    "giao_viec:\n  la: 1\n",
    "giao_viec:\n  bat: true\n",                                                     # bật mà chưa có principal
    "giao_viec:\n  thu_muc_kiem: tuong/doi\n",
    PK + "giao_viec:\n  bat: false\n",                                               # principal mà thiếu thư mục
    PK + "giao_viec:\n  thu_muc_kiem: {home}/kiem\n",                                # thư mục trong ~/.tram
    PK + "giao_viec:\n  thu_muc_kiem: /Users/Shared/a b\n",                          # ký tự không an toàn
    "giao_viec:\n  thu_muc_kiem: /Users/Shared/k\n" + CU,                            # chỉ có khoá cũ
    "cach_ly:\n  tram_kiem: tram-kiem\ngiao_viec:\n  thu_muc_kiem: /Users/Shared/k\n",     # thiếu user:/sandbox:
])
def test_sai_bao_loi(tram_home_tam, noi_dung):
    with pytest.raises(ValueError):
        _nap(tram_home_tam, noi_dung.replace("{home}", str(tram_home_tam)))


def test_principal_kiem_khong_con_trao_thu_quyen():
    """D22: không helper root, không ACL — `tram-kiem` sở hữu bản chép, chỉ còn `boc`, `kill_nhom`, `boc_luot`. 3C-D5:
    không còn `don_sach` (`crontab -r` + `pkill` ngầm xoá dấu vết trước khi quan sát)."""
    assert not any(hasattr(PrincipalKiem, x) for x in ("trao", "thu", "don_sach"))
    assert PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).co_che == "user"
