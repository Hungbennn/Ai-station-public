from pathlib import Path

import pytest

from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an

MAU = """
ten: demo
duong_dan: /tmp/demo
gitnexus_repo: demo-repo
boi_canh: "ERP du lịch"
hang_rao:
  tien:
    tu_khoa: [hoa hồng]
    duong_dan: ["*app/Modules/Fin/*"]
  quyen:
    nhan: [quyen]
"""


def ghi(tmp_path, noi_dung, ten="demo"):
    (tmp_path / f"{ten}.yaml").write_text(noi_dung, encoding="utf-8")
    return tmp_path


def test_nap_du_an(tmp_path):
    d = nap_du_an("demo", thu_muc=ghi(tmp_path, MAU))
    assert d.duong_dan == Path("/tmp/demo")
    assert d.hang_rao["tien"].tu_khoa == ("hoa hồng",)
    assert d.hang_rao["quyen"].nhan == ("quyen",)
    assert d.hang_rao["quyen"].tu_khoa == ()
    assert d.boi_canh == "ERP du lịch"


def test_ghi_de_repo(tmp_path):
    d = nap_du_an("demo", thu_muc=ghi(tmp_path, MAU), repo=Path("/khac"))
    assert d.duong_dan == Path("/khac")


def test_tu_choi_loai_hang_rao_la(tmp_path):
    with pytest.raises(ValueError, match="la_lung"):
        nap_du_an("demo", thu_muc=ghi(tmp_path, MAU + "  la_lung: {}\n"))


def test_tu_choi_ten_lech(tmp_path):
    with pytest.raises(ValueError, match="ten"):
        nap_du_an("demo", thu_muc=ghi(tmp_path, MAU.replace("ten: demo", "ten: khac")))


def test_liet_ke(tmp_path):
    ghi(tmp_path, MAU)
    ghi(tmp_path, MAU.replace("ten: demo", "ten: b"), ten="b")
    assert liet_ke_du_an(tmp_path) == ["b", "demo"]


def test_file_du_an_mau_nap_duoc():
    d = nap_du_an("vi-du")
    assert set(d.hang_rao) == {"tien", "schema", "quyen", "khach_thay"}
