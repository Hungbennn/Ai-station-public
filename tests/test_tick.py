"""Vòng tick (spec 4 §10): idempotent, estop chỉ ghi sự kiện đọc được, escalation G5, kiểm lại, cột 3."""
from giao_viec_gia import bug, dung
from kho_phieu_gia import LUC, dat_phieu
from su_kien_gia import DA, cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_xet_xong import F, bg
from tram.chu import estop
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.phieu.cong_viec import cong_viec_cho
from xu_ly_gia import ket_thuc_bang

GIU = {"status": "in_progress", "assignee": "tram/giao-viec"}


def loai(t, l):
    return [s for s in ds(t.kho) if s.loai == l]


def test_escalation_dong_bang_bd_tay_mot_lan_va_mo_chu_ky(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    e = tao_escalation(t.g, t.kho, DA, t.g.beads["hr-1"], ly_do="agent-bi", cau_hoi="?", giao_id="g-1", nguon="g-1",
                       luc=LUC)
    t.g.dong(e, "Dùng mb_substr")
    assert mot_vong_tick(t.bo)["escalation_dong"] == 1 and "escalation_dong" not in mot_vong_tick(t.bo)
    d = loai(t, "escalation.dong")
    assert len(d) == 1 and d[0].du_lieu["tra_loi"] == "Dùng mb_substr" and d[0].du_lieu["bead_goc"] == "hr-1"
    assert [s.du_lieu["nguon_su_kien_id"] for s in loai(t, "ngan_sach.chu_ky_moi")] == [d[0].id]


def test_tra_ve_mo_chu_ky_va_bead_dong(tmp_path):
    t = dung(tmp_path, bug(**GIU), bug("hr-2", status="closed"))
    tv = sk(t.kho, "cot.tra_ve", {"gop_y": "thiếu"})
    nhan(t.kho, "g-9", 1, bead_id="hr-2")
    mot_vong_tick(t.bo)
    mot_vong_tick(t.bo)
    assert [s.du_lieu["nguon_su_kien_id"] for s in loai(t, "ngan_sach.chu_ky_moi")] == [tv]
    assert len([s for s in ds(t.kho, "hr-2") if s.loai == "bead.dong"]) == 1


def chuan_bi_code_xong(t, tep):
    sha = t.k.day("tram/hr-1", tep, tu=t.k.main)
    p = dat_phieu(t.kho, bead_id="hr-1", lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"],
                  tieu_chi=["Tên kết thúc 'ỷ' không mất byte"])
    nhan(t.kho, p.giao_id, p.luot)                     # dat_phieu không ghi giao.nhan như cap_phieu
    cong_bo(t.kho, p.luot, sha)
    lenh = [{"lenh": "sh kiem.sh", "ket_qua": "pass", "tom_tat": "", "digest_log": "sha256:1"}]
    ket_thuc_bang(t.kho, p, "xong", commit=sha, ban_giao=bg(sha, lenh_kiem=lenh))
    return sha


def test_cong_viec_roi_kiem_lai_trong_cung_vong(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    sha = chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    r = mot_vong_tick(t.bo)
    assert r["cong_viec"] == 1 and r["kiem_lai"] == 1 and cong_viec_cho(t.kho) == []
    kl = moi_nhat(ds(t.kho), "kiem.lai").du_lieu
    assert (kl["commit"], kl["dat"], kl["luot"]) == (sha, True, 1) and kl["ket_qua"][0]["ket_qua"] == "pass"
    assert "kiem_lai" not in mot_vong_tick(t.bo)                                  # đã kiểm → chờ QC


def test_chua_co_principal_kiem_thi_khong_chay_lenh(tmp_path):
    t = dung(tmp_path, bug(**GIU), boc=None)
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x"})
    assert mot_vong_tick(t.bo)["cho_boc"] == 1 and loai(t, "kiem.lai") == []


def test_estop_chi_ghi_su_kien_doc_duoc(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x"})
    estop.bat("thử")
    so = len(t.g.goi)
    assert "cong_viec" not in mot_vong_tick(t.bo) and len(cong_viec_cho(t.kho)) == 1
    assert [g for g in t.g.goi[so:] if g[0] != "tat_ca"] == []
    estop.tat()


def test_het_ngan_sach_tao_escalation_mot_lan(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    for i in range(3):
        qc(t.kho, f"g-{i}", "c", "q", ket_luan="tra_ve")
    assert mot_vong_tick(t.bo)["het_ngan_sach"] == 1
    assert "het_ngan_sach" not in mot_vong_tick(t.bo) and t.g.so_lan("tao") == 1
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert "ly_do: het-ngan-sach" in esc.description


def test_thieu_moi_truong_kiem_mot_escalation_moi_du_an(tmp_path):
    t = dung(tmp_path, bug(), bug("hr-2"), env=False)
    assert mot_vong_tick(t.bo)["escalation"] == 1
    mot_vong_tick(t.bo)
    assert t.g.so_lan("tao") == 1


def test_qc_dat_vao_cot_3(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi(["Tên kết thúc 'ỷ' không mất byte"]))
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    assert mot_vong_tick(t.bo)["cot_3"] == 1 and t.g.beads["hr-1"].labels == ("cot:cho-review",)


def test_loi_bd_mot_du_an_duoc_dem(tmp_path):
    t = dung(tmp_path, bug())
    t.g._truoc = {"tat_ca": 1}
    assert mot_vong_tick(t.bo) == {"loi": 1}
