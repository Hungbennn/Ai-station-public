"""Nháp yêu cầu trên máy A (plan 4d 4D-3a): mã sinh một lần, giữ khi sửa, gắn với tên file; nháp ngoài repo; yêu cầu
mới chỉ qua `moi`. Thư mục tạm, không mạng, không `bd`."""
import json
import sys

import pytest
from test_phieu_yeu_cau import MAU

from tram.duong_dan import goc_repo

sys.path.insert(0, str(goc_repo() / "ky-nang" / "phong-van-yeu-cau"))
import nhap  # noqa: E402


def dien(p, **sua):
    """Như phiên Claude sửa nháp tại chỗ bằng công cụ Edit: đổi nội dung, giữ nguyên `ma_yeu_cau`."""
    d = json.loads(p.read_text(encoding="utf-8"))
    d.update({"tieu_de": "Hoa hồng tạm tính", "phieu": dict(MAU)}, **sua)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return p


def test_moi_sinh_ma_mot_lan_ten_file_la_ma_ngoai_repo(tmp_path):
    p = nhap.moi(tmp_path / "nhap", du_an="hr-codex")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert nhap.MA_RE.fullmatch(d["ma_yeu_cau"]) and p.name == d["ma_yeu_cau"] + ".json"
    assert (d["uu_tien"], d["phieu"]["du_an"], d["phieu"]["muc_tieu"]) == (2, "hr-codex", "")
    assert (p.parent.stat().st_mode & 0o777, p.stat().st_mode & 0o777) == (0o700, 0o600)
    assert nhap.moi(tmp_path / "nhap", du_an="hr-codex") != p


def test_sua_tai_cho_giu_ma(tmp_path):
    p = nhap.moi(tmp_path, du_an="hr-codex")
    ma = json.loads(p.read_text(encoding="utf-8"))["ma_yeu_cau"]
    yc = nhap.doc(dien(p))
    assert (yc["ma_yeu_cau"], yc["du_an"], yc["tieu_de"], yc["uu_tien"]) == (ma, "hr-codex", "Hoa hồng tạm tính", 2)
    assert nhap.doc(dien(p, tieu_de="Sửa lần hai"))["ma_yeu_cau"] == ma


def test_chep_sang_ten_khac_doi_hay_mat_ma_bi_tu_choi(tmp_path):
    p = dien(nhap.moi(tmp_path, du_an="hr-codex"))
    ban_sao = tmp_path / "ban-sao.json"
    ban_sao.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    d = json.loads(p.read_text(encoding="utf-8"))
    for sua in ({"ma_yeu_cau": "yc-" + "f" * 32}, {"ma_yeu_cau": d["ma_yeu_cau"].upper()}, {"ma_yeu_cau": None}):
        q = tmp_path / "x" / p.name
        q.parent.mkdir(exist_ok=True)
        q.write_text(json.dumps({**d, **sua}), encoding="utf-8")
        with pytest.raises(nhap.Loi, match="Mã yêu cầu"):
            nhap.doc(q)
    with pytest.raises(nhap.Loi, match="Mã yêu cầu"):
        nhap.doc(ban_sao)
    del d["ma_yeu_cau"]
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(nhap.Loi, match="bốn khoá"):
        nhap.doc(p)


def test_yeu_cau_moi_chon_ro_bang_moi_tu_nhap_cu(tmp_path):
    cu = dien(nhap.moi(tmp_path, du_an="hr-codex"), tieu_de="Bản cũ")
    moi = nhap.moi(tmp_path, tu=cu)
    a, b = nhap.doc(cu), nhap.doc(moi)
    assert a["ma_yeu_cau"] != b["ma_yeu_cau"] and (a["tieu_de"], a["phieu"]) == (b["tieu_de"], b["phieu"])
    with pytest.raises(nhap.Loi, match="--du-an"):
        nhap.moi(tmp_path)


def test_nhap_trong_repo_bi_tu_choi(tmp_path):
    (tmp_path / "repo" / ".git").mkdir(parents=True)
    with pytest.raises(nhap.Loi, match="ngoài repo"):
        nhap.moi(tmp_path / "repo" / "docs" / "nhap", du_an="hr-codex")
    p = dien(nhap.moi(tmp_path / "ngoai", du_an="hr-codex"))
    trong = tmp_path / "repo" / p.name
    trong.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(nhap.Loi, match="ngoài repo"):
        nhap.doc(trong)
    assert not (tmp_path / "repo" / "docs").exists()


@pytest.mark.parametrize("sua", [
    {"tieu_de": "--label cot:ai-lam"}, {"tieu_de": "Dòng 1\nDòng 2"}, {"tieu_de": " x"}, {"tieu_de": ""},
    {"tieu_de": "x" * 201}, {"uu_tien": "2"}, {"uu_tien": True}, {"uu_tien": 5}, {"phieu": []},
    {"phieu": {"muc_tieu": "x"}}, {"nhan": ["cot:ai-lam"]},
])
def test_nhap_sai_bi_chan_truoc_khi_goi_tram(tmp_path, sua):
    p = dien(nhap.moi(tmp_path, du_an="hr-codex"), **sua)
    with pytest.raises(nhap.Loi):
        nhap.doc(p)


def test_thu_muc_mac_dinh_theo_bien_moi_truong(monkeypatch, tmp_path):
    monkeypatch.setenv("PHONG_VAN_NHAP", str(tmp_path / "n"))
    assert nhap.thu_muc_mac_dinh() == tmp_path / "n"
