"""Kịch bản giả lập đầu-cuối luồng feature (spec 4 §16 mục 3, G6, G7, G11): phần 3 thật (nhịp tim, cấp phiếu, nhận
báo), thợ giả (commit + push nhánh spec, trạm ghi `giao.cong_bo` thay 3a-2), bộ giao việc + vòng tick, thao tác
Duyệt/Trả về của dashboard."""
import json

import pytest

from bead_gia import bead
from feature_gia import ke_hoach
from giao_viec_gia import dung
from su_kien_gia import ds, sk
from test_kich_ban_4a1 import bao, xin
from test_phieu_yeu_cau import mo_ta
from test_xet_spec import KH, bg_spec, tep_spec
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick
from tram.su_kien.kho import KhoSuKien
from tram.suy.phe_duyet import gom_phe_duyet
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.duyet_spec import NguonSpec
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import XungDot
from tram.thao_tac.phe_duyet import duyet, tra_ve

KHE = (("claude-1", ("coder",)), ("claude-2", ("spec", "qc")))
FEAT = bead("hr-f", title="Hoa hồng tạm tính", issue_type="feature", labels=["can-spec"], description=mo_ta())


def lam_spec(t, p, **sua):
    """Thợ giả của khe spec: commit spec + plan + *.beads.json + bàn giao lên nhánh spec từ `cha` của phiếu."""
    sha = t.k.day(p.repo.nhanh, tep_spec(**sua), tu=p.repo.cha)
    sk(t.kho, "giao.cong_bo", {"bead_id": p.bead_id, "luot": p.luot, "commit": sha, "ref": p.repo.nhanh},
       bead_id=p.bead_id)
    bao(t, p, "xong", commit=sha, ban_giao={**bg_spec(sha), "luot": p.luot})
    return sha


def dashboard(t, tmp_path):
    db = tmp_path / "su-kien.db"
    return NguCanhGhi(bd=t.g, kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr-codex"), NguonSpec(t.g, t.k.kho)


def muc_spec(nc, t):
    return next(m for m in gom_phe_duyet(["hr-codex"], {"hr-codex": list(t.g.beads.values())}, nc.kho)
                if m["loai"] == "spec")


def test_feature_spec_duyet_tao_con_va_con_cho_merge(tmp_path):
    t = dung(tmp_path, FEAT, khe=KHE)
    mot_vong_tick(t.bo)
    p = xin(t, "claude-2")
    assert (p.buoc, p.repo.nhanh, p.repo.cha) == ("spec", "tram/spec-hr-f", t.k.main)
    assert "phieu-yeu-cau" in p.goi_ngu_canh and t.g.beads["hr-f"].status == "open"
    sha = lam_spec(t, p)
    assert mot_vong_tick(t.bo)["spec_xong"] == 1 and t.g.beads["hr-f"].labels == ("cho-duyet-spec",)    # G6
    nc, ns = dashboard(t, tmp_path)
    ct = muc_spec(nc, t)["chi_tiet"]
    assert ct["commit"] == sha and [b["khoa"] for b in ct["de_xuat"]] == ["t1", "t2"]
    v = t.g.beads["hr-f"].updated_at
    with pytest.raises(XungDot):                                                                       # G11
        duyet(nc, "hr-f", ma="ma-kb-duyet-0", expected_version=v, expected_commit=t.k.main,
              digest_bead=ct["digest_bead"], nguon_spec=ns)
    duyet(nc, "hr-f", ma="ma-kb-duyet-1", expected_version=v, expected_commit=sha, digest_bead=ct["digest_bead"],
          nguon_spec=ns)
    assert t.g.beads["hr-f"].labels == ("theo-plan",) and t.g.so_lan("tao") == 2                     # G7
    for i in ("hr-f.1", "hr-f.2"):
        t.g.cap_nhat_nhan(i, them=["cot:ai-lam"])                                    # bộ quét 1a xếp cột 1
    mot_vong_tick(t.bo)
    assert xin(t, "claude-1") is None                                                # spec chưa merge (điều kiện 8)
    t.k.day("main", {}, tu=sha)                                                     # Đại ca merge PR spec
    mot_vong_tick(t.bo)
    p2 = xin(t, "claude-1")
    assert (p2.bead_id, p2.buoc) == ("hr-f.1", "code")                               # t2 còn chờ t1 (blocks)


def test_tra_ve_spec_giao_lai_tu_nhanh_spec_roi_het_dot(tmp_path):
    t = dung(tmp_path, FEAT, khe=KHE)
    mot_vong_tick(t.bo)
    nc, ns = dashboard(t, tmp_path)
    cha = t.k.main
    for lan in range(2):
        p = xin(t, "claude-2")
        assert p.buoc == "spec" and p.repo.cha == cha
        if lan:
            assert "Tách API và màn hình" in p.goi_ngu_canh
        cha = lam_spec(t, p, **{"docs/specs/2026-10-14-hoa-hong-tam-tinh.md": f"# Spec v{lan + 1}\n"})
        mot_vong_tick(t.bo)
        tra_ve(nc, "hr-f", gop_y="Tách API và màn hình", ma=f"ma-kb-trave-{lan}",
               expected_version=t.g.beads["hr-f"].updated_at, nguon_spec=ns)
    assert mot_vong_tick(t.bo)["spec_tra_ve_nhieu"] == 1 and xin(t, "claude-2") is None
    esc = next(b for b in t.g.beads.values() if "ly_do: spec-tra-ve-nhieu" in b.description)
    t.g.dong(esc.id, "Gộp lại một màn, làm tiếp")
    mot_vong_tick(t.bo)
    p3 = xin(t, "claude-2")
    assert p3.buoc == "spec" and p3.repo.cha == cha and "Gộp lại một màn" in p3.goi_ngu_canh


def test_injection_trong_beads_json_khong_doi_nhan(tmp_path):
    t = dung(tmp_path, FEAT, khe=KHE)
    mot_vong_tick(t.bo)
    p = xin(t, "claude-2")
    xau = ke_hoach()
    xau["bead"][0]["nhan"] = ["cot:cho-review"]
    lam_spec(t, p, **{KH: json.dumps(xau)})
    mot_vong_tick(t.bo)
    assert moi_nhat(ds(t.kho, "hr-f"), "giao.ket_thuc").du_lieu["ly_do"] == "ke-hoach-loi"
    assert t.g.beads["hr-f"].labels == ("can-spec",) and t.g.so_lan("tao") == 0
    p2 = xin(t, "claude-2")
    assert p2.buoc == "spec" and "cot:cho-review" in p2.goi_ngu_canh                 # lỗi ở lớp 4 để sửa
