"""Vòng tick hai pha (spec 4 §10 "ràng buộc lúc nối 4a-2"; G5): pha nhanh không cần Git/lệnh kiểm; pha Git xét
`bao.xong`, kiểm lại (dưới principal + thư mục kiểm cấu hình được), cột 3 có kiểm ref công bố trên remote."""
import subprocess

from giao_viec_gia import bug, dung
from kho_phieu_gia import LUC, dat_phieu
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_tick import GIU, chuan_bi_code_xong, loai
from test_xet_xong import F, bg
from tram.giao_viec import tick
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.tick import mot_vong_tick, vong_git, vong_nhanh
from tram.giao_viec.tick_pipeline import VIEC_GIT, day_pipeline
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.phieu.cong_viec import cong_viec_cho
from xu_ly_gia import ket_thuc_bang


def bi(t, bead_id="hr-1"):
    p = dat_phieu(t.kho, "B/claude-2", bead_id=bead_id)
    ket_thuc_bang(t.kho, p, "bi", ly_do="agent", noi_dung="vướng")


def qc_dat(t):
    """Bead hr-1 đã code (c), kiểm lại đạt, QC đạt (q) — ref công bố = q trên remote."""
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi(["Tên kết thúc 'ỷ' không mất byte"]))
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    return c, q


def test_pha_nhanh_khong_dung_git(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    bi(t)
    t.bo.kho_git = lambda d: (_ for _ in ()).throw(AssertionError("pha nhanh không được chạm kho kiểm"))
    assert vong_nhanh(t.bo)["cong_viec"] == 1
    assert "ly_do: agent-bi" in next(b for b in t.g.beads.values() if b.issue_type == "decision").description


def test_pha_git_xu_ly_xong_va_kiem_lai_pha_nhanh_thi_khong(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    assert "cong_viec" not in vong_nhanh(t.bo) and len(cong_viec_cho(t.kho)) == 1
    r = vong_git(t.bo)
    assert (r["cong_viec"], r["kiem_lai"]) == (1, 1) and loai(t, "kiem.lai")[0].du_lieu["dat"] is True


def test_fetch_qua_han_chi_dem_loi_khong_chan_escalation(tmp_path, monkeypatch):
    t = dung(tmp_path, bug(**GIU))
    bi(t)
    monkeypatch.setattr(tick, "fetch", lambda kg, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired("git", 1)))
    r = mot_vong_tick(t.bo)
    assert (r["cong_viec"], r["loi"]) == (1, 1) and t.g.so_lan("tao") == 1


def test_kiem_lai_dung_thu_muc_va_don_sach_cua_bo(tmp_path):
    t, goc = dung(tmp_path, bug(**GIU)), tmp_path / "kiem-ngoai"
    don = []
    t.bo.thu_muc_kiem, t.bo.don_sach = goc, lambda: don.append([p.name for p in goc.glob("*")])
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 2          # bản chép + nhà của lượt
    gid = loai(t, "giao.nhan")[0].du_lieu["giao_id"]
    assert all(n.startswith(gid + "-") for n in don[1]) and list(goc.iterdir()) == []


def test_cot_3_nhanh_bi_day_ngoai_luong(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    _, q = qc_dat(t)
    la = t.k.day("tram/hr-1", {"src/la.py": "x\n"}, tu=q)                # ai đó push thẳng lên nhánh công bố
    assert vong_git(t.bo)["nhanh_bi_day"] == 1 and "nhanh_bi_day" not in vong_git(t.bo)
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert "ly_do: nhanh-bi-day" in esc.description and la in esc.description
    assert t.g.beads["hr-1"].labels == ("cot:ai-lam",)


def test_cot_3_doc_lai_bead_bi_keo_thi_khong_ghi(tmp_path):
    from dataclasses import replace
    t = dung(tmp_path, bug(**GIU))
    qc_dat(t)
    cu = list(t.g.beads.values())
    t.g.beads["hr-1"] = replace(t.g.beads["hr-1"], labels=("cot:can-chot",))      # Đại ca kéo khi pha Git đang chạy
    from tram.giao_viec.git_kiem import fetch
    fetch(t.k.kho)
    assert day_pipeline(t.bo, t.kho, t.da, t.g, cu, set(), t.k.kho, LUC, viec=VIEC_GIT) == {}
    assert t.g.beads["hr-1"].labels == ("cot:can-chot",) and loai(t, "bead.vao_cot_3") == []


def test_thu_chi_ghi_su_kien_suy_tu_beads(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    e = tao_escalation(t.g, t.kho, "hr-codex", t.g.beads["hr-1"], ly_do="agent-bi", cau_hoi="?", giao_id="g-1",
                       nguon="g-1", luc=LUC)
    t.g.dong(e, "Làm cách B")
    bi(t)
    so = len(t.g.goi)
    r = mot_vong_tick(t.bo, thu=True)
    assert r == {"escalation_dong": 1, "chu_ky_moi": 1} and len(cong_viec_cho(t.kho)) == 1
    assert [g for g in t.g.goi[so:] if g[0] != "tat_ca"] == [] and len(ds(t.kho)) > 0
