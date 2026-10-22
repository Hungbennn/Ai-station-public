"""Feature đang "Spec chờ duyệt" cho test thao tác/API (CHỈ DÙNG TRONG TEST): nhánh spec trên remote cục bộ,
`spec.xong` + `giao.cong_bo` trong kho sự kiện, BdGia dùng chung cho dashboard và trạm."""
from dataclasses import dataclass
from pathlib import Path

from bd_gia import BdGia
from bead_gia import bead
from feature_gia import PLAN, SPEC, ke_hoach_json
from kho_kiem_gia import KhoGia, dung_kho
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.ke_hoach import digest_ke_hoach
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.duyet_spec import NguonSpec
from tram.thao_tac.kho import KhoThaoTac

V = "2026-10-13T01:00:00Z"
DA = "hr-codex"


@dataclass
class ChoDuyet:
    k: KhoGia
    g: BdGia
    nc: NguCanhGhi
    ns: NguonSpec
    commit: str
    digest: str


def ghi_spec_xong(kho: KhoSuKien, commit: str, digest: str, feature: str = "hr-f") -> None:
    kho.ghi(DA, "giao.cong_bo", {"bead_id": feature, "luot": 1, "commit": commit, "ref": f"tram/spec-{feature}"},
            bead_id=feature, tac_nhan="tram/giao-viec")
    kho.ghi(DA, "spec.xong", {"feature": feature, "nhanh": f"tram/spec-{feature}", "commit": commit,
                              "digest_bead": digest, "file": [SPEC, PLAN, f"docs/plans/{feature}.beads.json"],
                              "de_xuat": [], "giao_id": "g-1"}, bead_id=feature, tac_nhan="tram/giao-viec")


def cho_duyet(tmp_path: Path, *them, ke_hoach: str | None = None, **kw_bd) -> ChoDuyet:
    k = dung_kho(tmp_path)
    van_ban = ke_hoach or ke_hoach_json()
    c = k.day("tram/spec-hr-f", {SPEC: "# Spec\n", PLAN: "# Plan\n", "docs/plans/hr-f.beads.json": van_ban}, tu=k.main)
    fetch(k.kho)
    g = BdGia([bead("hr-f", title="Hoa hồng", issue_type="feature", labels=["cho-duyet-spec"]), *them], **kw_bd)
    db = tmp_path / "sk.db"
    nc = NguCanhGhi(bd=g, kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an=DA)
    dg = digest_ke_hoach(van_ban)
    ghi_spec_xong(nc.kho, c, dg)
    return ChoDuyet(k, g, nc, NguonSpec(g, k.kho, "main"), c, dg)
