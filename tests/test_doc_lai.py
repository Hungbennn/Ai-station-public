"""Đọc lại Beads ngay trước cấp (4a-1 G3 → 4a-2) + bộ đệm beads cho bộ chọn (BoDemBeads).
Kéo cột xen kẽ: Đại ca kéo bead sang cột 2 sau khi bộ chọn lấy snapshot → không claim, không đề xuất."""
from dataclasses import replace

from giao_viec_gia import bug, dung
from tram.api.bo_dem import BoDemBeads
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.doc_lai import dau_bead
from tram.giao_viec.git_kiem import fetch


def co_dem(t, tuoi=3600.0):
    t.bo.doc_beads = DocBeads(BoDemBeads(lambda ten: t.g, tuoi_toi_da=tuoi), tuoi=tuoi)
    t.bo.doc_beads.lay(t.da, t.g)                       # mồi bộ đệm = snapshot cũ
    fetch(t.k.kho)
    return t


def keo(t, bead_id="hr-1", **kw):
    t.g.beads[bead_id] = replace(t.g.beads[bead_id], **kw)


def test_dau_bead_bo_qua_updated_at_va_notes():
    b = bug()
    assert dau_bead(b) == dau_bead(replace(b, updated_at="2027-01-01T00:00:00Z", notes="x"))
    assert dau_bead(b) != dau_bead(replace(b, labels=("cot:can-chot",)))
    assert dau_bead(b) != dau_bead(replace(b, acceptance_criteria="- khác"))


def test_keo_sang_cot_2_sau_snapshot_thi_khong_claim(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    keo(t, labels=("cot:can-chot",))
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0


def test_tieu_chi_doi_sau_snapshot_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    keo(t, acceptance_criteria="- Tiêu chí mới")
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0


def test_bead_chan_moi_mo_lai_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug(chan_boi=["hr-2"]), bug("hr-2", status="closed", labels=[])))
    keo(t, "hr-2", status="open")                       # bead chặn mở lại: bd ready trong bộ đệm đã cũ
    assert t.bo.chon("B/claude-1", None) is None


def test_keo_cot_giua_claim_va_cap_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    goc = t.g.nhan_viec
    t.g.nhan_viec = lambda i: (goc(i), keo(t, i, labels=("cot:can-chot",)))
    assert t.bo.chon("B/claude-1", None) is None
    assert t.g.beads["hr-1"].status == "in_progress"    # đã claim: bead ở lại cho Đại ca thấy (spec 4 §5.4)


def test_khong_doi_thi_de_xuat_va_danh_dau_bo_dem_cu(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    so = t.g.so_lan("tat_ca")
    dx = t.bo.chon("B/claude-1", None)
    assert dx.bead_id == "hr-1" and t.g.beads["hr-1"].status == "in_progress"
    assert t.g.so_lan("tat_ca") == so + 2               # đúng hai lần đọc lại (trước và sau claim)
    t.bo.doc_beads.lay(t.da, t.g)
    assert t.g.so_lan("tat_ca") == so + 3               # bộ đệm đã bị đánh dấu cũ → đọc mới


def test_bo_dem_khong_goi_bd_moi_lan_xin_viec(tmp_path):
    t = co_dem(dung(tmp_path, bug(labels=["cot:can-chot"])))
    so_list, so_ready = t.g.so_lan("tat_ca"), t.g.so_lan("san_sang")
    for _ in range(3):
        assert t.bo.chon("B/claude-1", None) is None
    assert (t.g.so_lan("tat_ca"), t.g.so_lan("san_sang")) == (so_list, so_ready)

def test_adr_regex_khong_mo_gate_khi_chua_co_adapter(tmp_path):
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="chưa có ADR-0083; đổi schema"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    assert not con_nguyen(t.g, da, t.g.beads["hr-1"])


def test_adr_adapter_phai_xac_minh_dung_repo_va_cong_viec(tmp_path):
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="đổi schema ADR-0083"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    b = t.g.beads["hr-1"]
    # CHỈ DÙNG TRONG TEST: kết quả adapter đã kiểm tồn tại/được duyệt/phạm vi.
    for hop_le in (False, True):
        assert con_nguyen(t.g, da, b, adr_hop_le=lambda d, x: hop_le and d == da and x == b) is hop_le


def test_quyet_dinh_blocks_da_dong_van_duoc_chot(tmp_path):
    from bead_gia import bead
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="đổi schema", chan_boi=["hr-d"]),
             bead("hr-d", issue_type="decision", status="closed"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    assert con_nguyen(t.g, da, t.g.beads["hr-1"])

