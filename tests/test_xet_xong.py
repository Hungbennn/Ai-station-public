"""Xét `bao.xong` (spec 4 §6.1, §6.3): SHA công bố, đường dẫn cấm trước (G9), luật chặt, QC chỉ thêm bàn giao (G10)."""
import json
from pathlib import Path

import pytest

from bead_gia import KHOI_BAN_GIAO
from kho_kiem_gia import dung_kho
from kho_phieu_gia import dat_phieu, kho_tam
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.khoi_qc import doc_khoi_qc
from tram.giao_viec.xet_xong import xet_xong_code, xet_xong_qc

TC = "Tên kết thúc 'ỷ' không mất byte"
LENH = "php artisan test --filter TomTatHoanTien"
DA = DuAn("hr-codex", Path("/r"), None, {})
F = "docs/handovers/2026-10-13-hr-1.md"


def bg(commit, *, dat=True, lenh="pass", **kw):
    return {**KHOI_BAN_GIAO, "nhanh": "tram/hr-1", "commit": commit, "pr": None, "file_ban_giao": F,
            "doi_chieu_nghiem_thu": [{"tieu_chi": TC, "dat": dat, "bang_chung": "test_y"}],
            "lenh_kiem": [{"lenh": LENH, "ket_qua": lenh, "tom_tat": "ok", "digest_log": "sha256:1"}], **kw}


@pytest.fixture
def m(tmp_path):
    k = dung_kho(tmp_path)
    return k, kho_tam(tmp_path)


def code(m, tep, *, buoc="code", tu=None, cha=None):
    k, kho = m
    sha = k.day("tram/hr-1", tep, tu=tu or k.main)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-1", buoc=buoc, **({"cha": cha} if cha else {}))
    return sha, p


def test_hop_le(m):
    sha, p = code(m, {"src/tom_tat.py": "x = 2\n", F: "bàn giao"})
    kl = xet_xong_code(m[0].kho, p, {"commit": sha, "ban_giao": bg(sha)}, sha, DA)
    assert kl.ly_do is None and kl.loi == () and kl.commit == sha


def test_chua_cong_bo_va_sha_cua_bead_khac(m):
    sha, p = code(m, {F: "x"})
    assert xet_xong_code(m[0].kho, p, {"commit": sha, "ban_giao": bg(sha)}, None, DA).ly_do == "chua-cong-bo"
    kl = xet_xong_code(m[0].kho, p, {"commit": "abcdef1", "ban_giao": bg("abcdef1")}, sha, DA)
    assert kl.ly_do == "commit-khong-cong-bo" and kl.commit is None


@pytest.mark.parametrize("tep", [{"erp/package.json": "{}"}, {"erp/AGENTS.md": "x"}, {".claude/settings.json": "{}"}])
def test_cham_duong_dan_cam_truoc_moi_thu(m, tep):
    sha, p = code(m, {**tep, F: "x"})
    kl = xet_xong_code(m[0].kho, p, {"commit": sha, "ban_giao": {"hong": 1}}, sha, DA)
    assert kl.ly_do == "dong-file-cau-hinh" and list(tep)[0] in kl.cham_cam


def test_doi_ten_sang_file_cam_va_ngoai_le_cu_the(m):
    k, _ = m
    sha, p = code(m, {"src/tom_tat.py": None, "CLAUDE.md": "x = 1\n", F: "x"})
    assert xet_xong_code(k.kho, p, {"commit": sha, "ban_giao": bg(sha)}, sha, DA).ly_do == "dong-file-cau-hinh"
    sha2 = k.day("tram/hr-1", {"erp/package.json": "{}"}, tu=k.main)
    fetch(k.kho)
    cho = DuAn("hr-codex", Path("/r"), None, {}, giao=CauHinhGiao(duong_dan_cam_cho_phep=("erp/package.json",)))
    assert xet_xong_code(k.kho, p, {"commit": sha2, "ban_giao": bg(sha2)}, sha2, cho).ly_do == "ban-giao-loi"


@pytest.mark.parametrize("bao_bg, loi_tho", [
    (dict(dat=False), []), (dict(lenh="fail"), []), (dict(lenh_kiem=[]), []), (dict(), ["Thiếu đối chiếu"]),
    (dict(file_ban_giao="docs/handovers/khong-co.md"), []),
])
def test_ban_giao_loi(m, bao_bg, loi_tho):
    sha, p = code(m, {"src/tom_tat.py": "x = 3\n", F: "x"})
    kl = xet_xong_code(m[0].kho, p, {"commit": sha, "ban_giao": bg(sha, **bao_bg), "loi_ban_giao": loi_tho}, sha, DA)
    assert kl.ly_do == "ban-giao-loi" and kl.loi


def test_commit_trong_khoi_khac_sha_cong_bo(m):
    sha, p = code(m, {F: "x"})
    kl = xet_xong_code(m[0].kho, p, {"commit": sha, "ban_giao": bg("abcdef1")}, sha, DA)
    assert kl.ly_do == "ban-giao-loi" and "commit trong khối bàn giao khác SHA công bố" in kl.loi


def khoi_qc(commit_code, ket_luan="dat", **kw):
    return "# QC\n<!-- qc -->\n" + json.dumps({"qc": {"ket_luan": ket_luan, "commit_code": commit_code,
                                                      "phat_hien": [], **kw}}) + "\n<!-- qc -->\n"


def qc(m, tep_qc):
    k, kho = m
    c = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=k.main)
    q = k.day("tram/hr-1", tep_qc, tu=c)
    fetch(k.kho)
    return c, q, dat_phieu(kho, bead_id="hr-1", buoc="qc", cha=c)


def bao_qc(q, **kw):
    return {"commit": q, "ban_giao": bg(q, lenh_kiem=[], **kw)}


def test_qc_dat_va_tra_ve(m):
    c, q, p = qc(m, {F: "x"})
    k = m[0]
    q2 = k.day("tram/hr-1", {F: khoi_qc(c)}, tu=c)
    fetch(k.kho)
    kq = xet_xong_qc(k.kho, p, bao_qc(q2), q2)
    assert (kq.ket_luan, kq.ly_do, kq.commit_qc) == ("dat", None, q2)
    sai = bao_qc(q2)
    sai["ban_giao"]["commit"] = c
    kq_sai = xet_xong_qc(k.kho, p, sai, q2)
    assert (kq_sai.ket_luan, kq_sai.ly_do) == ("tra_ve", "ban-giao-qc-loi")
    q3 = k.day("tram/hr-1", {F: khoi_qc(c, "tra_ve", phat_hien=[{"muc": "chan", "noi_dung": "thiếu 'ỷ'",
                                                                  "vi_tri": "a:1"}])}, tu=c)
    fetch(k.kho)
    kq = xet_xong_qc(k.kho, p, bao_qc(q3, doi_chieu_nghiem_thu=[{"tieu_chi": TC, "dat": False, "bang_chung": "b"}]),
                     q3)
    assert kq.ket_luan == "tra_ve" and kq.phat_hien[0]["noi_dung"] == "thiếu 'ỷ'"


def test_qc_doi_ma_khong_cong_nhan(m):
    c, q, p = qc(m, {F: "x", "src/tom_tat.py": "x = 9\n"})
    kq = xet_xong_qc(m[0].kho, p, bao_qc(q), q)
    assert (kq.ket_luan, kq.ly_do) == ("khong_cong_nhan", "qc-doi-ma")


@pytest.mark.parametrize("noi_dung", ["không có khối", khoi_qc("abcdef1"), "<!-- qc -->{hỏng}<!-- qc -->"])
def test_khoi_qc_loi_coi_nhu_tra_ve(m, noi_dung):
    c, q, p = qc(m, {F: noi_dung})
    kq = xet_xong_qc(m[0].kho, p, bao_qc(q), q)
    assert (kq.ket_luan, kq.ly_do) == ("tra_ve", "khoi-qc-loi")


def test_qc_dat_ma_tieu_chi_false_la_tra_ve(m):
    k = m[0]
    c, _, p = qc(m, {F: "x"})
    q = k.day("tram/hr-1", {F: khoi_qc(c)}, tu=c)
    fetch(k.kho)
    kq = xet_xong_qc(k.kho, p, bao_qc(q, doi_chieu_nghiem_thu=[{"tieu_chi": TC, "dat": False, "bang_chung": "b"}]), q)
    assert (kq.ket_luan, kq.ly_do) == ("tra_ve", "ban-giao-qc-loi")


def test_qc_chua_cong_bo_khong_ghi_ket_qua(m):
    c, q, p = qc(m, {F: "x"})
    assert xet_xong_qc(m[0].kho, p, bao_qc(q), None).ket_luan is None


def test_doc_khoi_qc_lay_khoi_cuoi():
    assert doc_khoi_qc(khoi_qc("abcdef1", "tra_ve") + khoi_qc("abcdef2")).commit_code == "abcdef2"
    assert doc_khoi_qc(None) is None
