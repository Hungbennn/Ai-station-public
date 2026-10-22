"""`BoGiaoViec` với luồng feature (spec 4 §5.1, §5.3, §7.2): phiếu `spec` không claim; con chờ merge spec."""
from bead_gia import bead
from giao_viec_gia import bug, dung
from kho_phieu_gia import LUC
from su_kien_gia import sk
from test_phieu_yeu_cau import mo_ta
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.git_kiem import fetch
from tram.phieu.cap import cap_phieu

F = bead("hr-f", title="Hoa hồng tạm tính", issue_type="feature", labels=["can-spec"], description=mo_ta())
KHE_SPEC = (("claude-1", ("coder",)), ("claude-2", ("spec", "qc")))


def test_chon_spec_khong_claim_va_cap_duoc(tmp_path):
    t = dung(tmp_path, F, khe=KHE_SPEC)
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-1", None) is None                      # khe có vai spec đang rảnh → không lan
    dx = t.bo.chon("B/claude-2", None)
    assert (dx.bead_id, dx.buoc, dx.vai, dx.repo.nhanh, dx.repo.cha) == ("hr-f", "spec", "spec", "tram/spec-hr-f",
                                                                          t.k.main)
    assert t.g.so_lan("nhan_viec") == 0 and t.g.beads["hr-f"].status == "open"
    kq = cap_phieu(t.kho, "B/claude-2", dx, bay_gio=LUC, ch=CauHinhTram(), con_hop_le=t.bo.con_hop_le)
    assert kq.phieu is not None and kq.phieu.buoc == "spec"


def test_vai_spec_lan_khi_khong_khe_nao_co_vai_spec(tmp_path):
    t = dung(tmp_path, F)
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-1", None).buoc == "spec"


def test_het_dot_sua_spec_thi_con_hop_le_tu_choi(tmp_path):
    t = dung(tmp_path, F, khe=KHE_SPEC)
    fetch(t.k.kho)
    dx = t.bo.chon("B/claude-2", None)
    for i in range(2):
        sk(t.kho, "spec.tra_ve", {"gop_y": f"lần {i}"}, bead_id="hr-f")
    assert not t.bo.con_hop_le(dx) and t.bo.chon("B/claude-2", None) is None


def test_con_cua_feature_chi_giao_khi_spec_da_merge(tmp_path):
    f = bead("hr-f", issue_type="feature", labels=["theo-plan"])
    t = dung(tmp_path, f, bug("hr-f.1", parent="hr-f"))
    c = t.k.day("tram/spec-hr-f", {"docs/specs/x.md": "# x\n"}, tu=t.k.main)
    sk(t.kho, "spec.duyet", {"feature": "hr-f", "commit": c, "digest_bead": "sha256:x", "bead_moi": ["hr-f.1"]},
       bead_id="hr-f")
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-1", None) is None
    main = t.k.day("main", {}, tu=c)                                  # Đại ca merge PR spec
    fetch(t.k.kho)
    dx = t.bo.chon("B/claude-1", None)
    assert (dx.bead_id, dx.buoc, dx.repo.cha) == ("hr-f.1", "code", main)

def test_spec_doc_lai_doi_nhan_khong_claim(tmp_path):
    from dataclasses import replace
    from tram.api.bo_dem import BoDemBeads
    from tram.giao_viec.doc_beads import DocBeads
    t = dung(tmp_path, F, khe=KHE_SPEC)
    fetch(t.k.kho)
    t.bo.doc_beads = DocBeads(BoDemBeads(lambda ten: t.g, tuoi_toi_da=3600))
    t.bo.doc_beads.lay(t.da, t.g)
    t.g.beads[F.id] = replace(F, labels=("cho-duyet-spec",))
    assert t.bo.chon("B/claude-2", None) is None and t.g.so_lan("nhan_viec") == 0


def test_spec_khong_claim_va_doc_lai_khong_thay_noi_dung(tmp_path):
    t = dung(tmp_path, F, khe=KHE_SPEC)
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-2", None).buoc == "spec"
    assert t.g.so_lan("nhan_viec") == 0 and t.g.beads[F.id].status == "open"

