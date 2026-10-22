"""V2-5 (dot7-Q04): manifest của hồ sơ Seatbelt — input bộ sinh + phiên bản + digest. Runtime sinh lại hồ sơ từ
manifest, không lấy hồ sơ đang kiểm làm mẫu của chính nó. Chỉ xử lý byte trong bộ nhớ — không đọc /usr/local."""
import json
from pathlib import Path

import pytest

from tram.tho import quyen_kiem
from tram.tho.quyen_kiem import KHOA_MANIFEST, PHIEN_BAN_HO_SO, ho_so_tram_kiem, ho_so_tu_manifest, manifest_ho_so


def dung(tmp_path):
    return manifest_ho_so(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                          goc=tmp_path.resolve(), cong=[7700, 3306])


def test_manifest_sinh_lai_dung_tung_byte_va_tat_dinh(tmp_path):
    hs, mf = dung(tmp_path)
    assert (hs, mf) == dung(tmp_path)
    m, lai = ho_so_tu_manifest(mf)
    assert lai == hs == ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                                        goc=tmp_path.resolve(), cong=[7700, 3306]).encode()
    assert tuple(sorted(m)) == KHOA_MANIFEST and m["phien_ban"] == PHIEN_BAN_HO_SO == 3
    assert m["goc"] == str(tmp_path.resolve()) and m["nha_quan_ly"] == "/Users/tram-tho"
    assert mf.endswith(b"}\n") and b"\n \"cong\"" in mf


def _sua(mf: bytes, **sua) -> bytes:
    m = json.loads(mf)
    for k, v in sua.items():
        if v is KeyError:
            m.pop(k)
        else:
            m[k] = v
    return json.dumps(m).encode()


@pytest.mark.parametrize("sua", [dict(phien_ban=1), dict(phien_ban=2), dict(phien_ban=PHIEN_BAN_HO_SO + 1),
                                 dict(phien_ban=True), dict(phien_ban="1"),
                                 dict(cong=[True]), dict(cong=[0]), dict(cong="7700"), dict(nha_quan_ly="/etc/BIMAT"),
                                 dict(nha_quan_ly='/Users/a"b'), dict(goc="BIMAT/tuong-doi"), dict(tram_home="BIMAT"),
                                 dict(tram_home='/Users/"BIMAT'), dict(sha256="0" * 64), dict(goc=KeyError),
                                 dict(them="BIMAT"), dict(sha256=None)])
def test_manifest_sai_thi_tu_choi_khong_lo_noi_dung(tmp_path, sua):
    with pytest.raises(ValueError, match="cài lại") as e:
        ho_so_tu_manifest(_sua(dung(tmp_path)[1], **sua))
    assert "BIMAT" not in str(e.value)


@pytest.mark.parametrize("du_lieu", [b"", b"[]", b"\xff\xfe", b'{"goc": "a", "goc": "b"}', b"BIMAT"])
def test_khong_phai_json_object_hoac_khoa_trung(du_lieu):
    with pytest.raises(ValueError, match="sai dạng") as e:
        ho_so_tu_manifest(du_lieu)
    assert "BIMAT" not in str(e.value)


def test_khoa_trung_trong_manifest_that_bi_tu_choi(tmp_path):
    mf = dung(tmp_path)[1]
    with pytest.raises(ValueError, match="sai dạng"):
        ho_so_tu_manifest(mf.replace(b'"cong": [', b'"cong": [7700], "cong": [', 1))


def test_bo_sinh_doi_ma_quen_tang_phien_ban_thi_dong(tmp_path, monkeypatch):
    mf = dung(tmp_path)[1]
    goc = quyen_kiem.ho_so_tram_kiem
    monkeypatch.setattr(quyen_kiem, "ho_so_tram_kiem", lambda **kw: goc(**kw) + "(allow network*)\n")
    with pytest.raises(ValueError, match="digest"):
        ho_so_tu_manifest(mf)
