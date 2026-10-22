"""Xét `bao.xong` của phiếu spec (spec 4 §7.2): công bố, đường dẫn cấm, chỉ docs/**, ba file, JSON, bàn giao."""
import json
import os
from pathlib import Path

import pytest

from bead_gia import KHOI_BAN_GIAO
from feature_gia import PLAN, SPEC, ke_hoach, ke_hoach_json
from kho_kiem_gia import dung_kho
from kho_phieu_gia import dat_phieu, kho_tam
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.ke_hoach import digest_ke_hoach
from tram.giao_viec.xet_spec import doc_ke_hoach_tai, xet_xong_spec

DA = DuAn("hr-codex", Path("/r"), None, {})
TC = "Booking có giảm giá hiện đúng số tạm tính"
BG = "docs/handovers/2026-10-14-hr-f-spec.md"
KH = "docs/plans/hr-f.beads.json"


def tep_spec(**sua) -> dict:
    return {SPEC: "# Spec\n", PLAN: "# Plan\n", KH: ke_hoach_json(), BG: "bàn giao spec\n", **sua}


def bg_spec(commit, **kw):
    return {**KHOI_BAN_GIAO, "nhanh": "tram/spec-hr-f", "commit": commit, "pr": None, "file_ban_giao": BG,
            "doi_chieu_nghiem_thu": [{"tieu_chi": TC, "dat": True, "bang_chung": f"{SPEC} §3"}], **kw}


def day_spec(k, tep, tu=None) -> str:
    sha = k.day("tram/spec-hr-f", tep, tu=tu or k.main)
    fetch(k.kho)
    return sha


@pytest.fixture
def m(tmp_path):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    return k, dat_phieu(kho, bead_id="hr-f", buoc="spec", tieu_chi=[TC], cha=k.main)


def xet(m, sha, cong_bo="=", **bao):
    k, p = m
    return xet_xong_spec(k.kho, p, {"commit": sha, "ban_giao": bg_spec(sha), **bao}, sha if cong_bo == "=" else cong_bo,
                         DA)


def test_hop_le_kem_ke_hoach_va_digest(m):
    sha = day_spec(m[0], tep_spec())
    kl = xet(m, sha)
    assert (kl.ly_do, kl.loi, kl.commit) == (None, (), sha)
    assert [b.khoa for b in kl.ke_hoach.bead] == ["t1", "t2"] and kl.digest == digest_ke_hoach(ke_hoach_json())
    assert doc_ke_hoach_tai(m[0].kho, sha, "hr-f")[1] == kl.digest


def test_chua_cong_bo_va_commit_khac(m):
    sha = day_spec(m[0], tep_spec())
    assert xet(m, sha, cong_bo=None).ly_do == "chua-cong-bo"
    assert xet(m, sha, cong_bo="abcdef1").ly_do == "commit-khong-cong-bo"


@pytest.mark.parametrize("them, ly_do", [
    ({"docs/AGENTS.md": "x"}, "dong-file-cau-hinh"), ({".claude/settings.json": "{}"}, "dong-file-cau-hinh"),
    ({"src/tom_tat.py": "x = 9\n"}, "spec-ngoai-docs"), ({"package.json": "{}"}, "dong-file-cau-hinh"),
])
def test_dong_ngoai_docs(m, them, ly_do):
    kl = xet(m, day_spec(m[0], tep_spec(**them)))
    assert kl.ly_do == ly_do and kl.loi


@pytest.mark.parametrize("sua", [
    {KH: None}, {KH: json.dumps(ke_hoach(bead=[]))}, {KH: ke_hoach_json(feature="hr-khac")}, {SPEC: None},
    {KH: json.dumps({**ke_hoach(), "bead": [{**ke_hoach()["bead"][0], "nhan": ["cot:ai-lam"]}]})},
])
def test_ke_hoach_loi(m, sua):
    tep = {k: v for k, v in tep_spec(**sua).items() if v is not None}
    kl = xet(m, day_spec(m[0], tep))
    assert kl.ly_do == "ke-hoach-loi" and kl.ke_hoach is None and kl.loi


def test_file_spec_la_symlink_bi_tu_choi(m):
    k = m[0]
    tep = tep_spec()
    del tep[SPEC]
    (k.dev / "docs/specs").mkdir(parents=True, exist_ok=True)
    os.symlink("../../AGENTS.md", k.dev / SPEC)
    assert xet(m, day_spec(k, tep)).ly_do == "ke-hoach-loi"


@pytest.mark.parametrize("bao_kw", [{"loi_ban_giao": ["Thiếu đối chiếu"]}, {"ban_giao": {"hong": 1}}])
def test_ban_giao_loi(m, bao_kw):
    assert xet(m, day_spec(m[0], tep_spec()), **bao_kw).ly_do == "ban-giao-loi"


def test_ban_giao_thieu_tieu_chi_va_commit_lech(m):
    sha = day_spec(m[0], tep_spec())
    assert xet(m, sha, ban_giao=bg_spec(sha, doi_chieu_nghiem_thu=[])).ly_do == "ban-giao-loi"
    kl = xet(m, sha, ban_giao=bg_spec("abcdef1"))
    assert kl.ly_do == "ban-giao-loi" and "commit trong khối bàn giao khác SHA công bố" in kl.loi
