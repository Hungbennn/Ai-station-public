"""MỘT nguồn khai báo principal kiểm lại (lát 3c, bead bs-urj.12): `cach_ly.tram_kiem` là khoá chuẩn; khoá cũ
`giao_viec.principal_kiem` chỉ để đối chiếu. D22: không trao/thu quyền; thu hồi theo UID: `test_thu_hoi_uid.py`
(3C-D5). Không sudo — chỉ kiểm argv dựng ra."""
import fnmatch
from pathlib import Path

import pytest

from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
from tram.cau_hinh.principal_kiem import doc_principal_kiem
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.tho.principal import BIEN_GIU
from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem

CU = "giao_viec:\n  principal_kiem:\n    ten: {ten}\n    boc: [/bin/sh, -c]\n    trao_quyen: [/tmp/x]\n"


def ghi(tram_home, noi_dung: str):
    tram_home.mkdir(parents=True, exist_ok=True)
    (tram_home / "cau-hinh.yaml").write_text(noi_dung, encoding="utf-8")


def test_user_dung_argv_principal_3a2_khong_con_trao_quyen():
    pk = tu_cach_ly("user:tram-kiem")
    assert pk.boc == ("/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem", f"--preserve-env={','.join(BIEN_GIU)}", "--")
    assert pk.co_che == "user" and list(PrincipalKiem.__dataclass_fields__) == ["ten", "boc", "co_che"]


def test_sandbox_boc_qua_ho_so_co_dinh_cua_tram_kiem():
    pk = tu_cach_ly("sandbox:tram-thuc-thi")
    assert pk.ten == "tram-thuc-thi" and pk.co_che == "sandbox"
    assert pk.boc[-4:] == ("--", "/usr/bin/sandbox-exec", "-f", str(HO_SO_KIEM))


def test_chua_khai_gi_la_none(tram_home_tam):
    assert doc_principal_kiem() is None
    ghi(tram_home_tam, "cach_ly:\n  kenh_ghi: header\n")
    assert doc_principal_kiem() is None


def test_hai_khoa_trung_ten_thi_canh_bao_va_bo_argv_cu(tram_home_tam):
    ghi(tram_home_tam, "cach_ly:\n  tram_kiem: user:tram-kiem\n" + CU.format(ten="tram-kiem"))
    bao = []
    pk = doc_principal_kiem(bao=bao.append)
    assert pk == tu_cach_ly("user:tram-kiem") and "/bin/sh" not in pk.boc
    assert len(bao) == 1 and "khoá cũ" in bao[0]


@pytest.mark.parametrize("noi_dung, loi", [
    ("cach_ly:\n  tram_kiem: user:tram-kiem\n" + CU.format(ten="tram-khac"), "khác"),
    (CU.format(ten="tram-kiem"), "cach_ly.tram_kiem"),
    ("cach_ly:\n  tram_kiem: tram-kiem\n", "sai dạng"),
    ("cach_ly:\n  tram_kiem: user:tram-kiem\ngiao_viec:\n  principal_kiem: [tram-kiem]\n", "khoá cũ")])
def test_lech_hoac_sai_dang_la_loi_cau_hinh(tram_home_tam, noi_dung, loi):
    ghi(tram_home_tam, noi_dung)
    with pytest.raises(ValueError, match=loi):
        doc_principal_kiem()


def test_giao_viec_doc_qua_nguon_chung(tram_home_tam, tmp_path):
    ghi(tram_home_tam, f"cach_ly:\n  tram_kiem: sandbox:tram-kiem\ngiao_viec:\n  thu_muc_kiem: {tmp_path}/k\n")
    assert nap_cau_hinh_giao_viec().principal_kiem == doc_principal_kiem() == tu_cach_ly("sandbox:tram-kiem")


def test_thu_muc_kiem_symlink_bi_tu_choi(tram_home_tam, tmp_path):
    (tmp_path / "that").mkdir()
    (tmp_path / "lk").symlink_to(tmp_path / "that")
    ghi(tram_home_tam, f"cach_ly:\n  tram_kiem: user:tram-kiem\ngiao_viec:\n  thu_muc_kiem: {tmp_path}/lk\n")
    with pytest.raises(ValueError, match="THẬT"):
        nap_cau_hinh_giao_viec()


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che, monkeypatch):
    pk, goi = tu_cach_ly(f"{co_che}:tram-kiem"), []
    monkeypatch.setattr("tram.giao_viec.principal_kiem.chay_ngan", lambda argv, **kw: goi.append(argv) or (0, b""))
    pk.kill_nhom(123, 9)
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
    goi += [pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]), pk.boc_lenh(["/bin/kill", "-KILL", "-1"]),
            pk.boc_luot(Path("/k/g-1"))(["sh", "kiem.sh"])]
    qua_sudo = [a for a in goi if a[0] == "/usr/bin/sudo"]
    assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in qua_sudo) and len(qua_sudo) == 4
    assert all(mau == "ALL" or fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau) for a in qua_sudo)
