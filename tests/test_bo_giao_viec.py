"""Giao diện với phần 3 (spec 4 §13; 3a-1 G11): `chon(khe_id, han_muc)` ngoài giao dịch, `con_hop_le` trong."""
from giao_viec_gia import bug, dung
from kho_phieu_gia import LUC
from su_kien_gia import cong_bo, ket_thuc, kiem, nhan, sk
from tram.beads.bd import LoiBd
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.phieu.cap import cap_phieu
from xu_ly_gia import ket_thuc_bang

DG = digest_tieu_chi(["Tên kết thúc 'ỷ' không mất byte"])


def test_chon_code_va_nhan_viec_tren_beads(tmp_path):
    t = dung(tmp_path, bug(), bug("hr-2", labels=["cot:can-chot"]))
    fetch(t.k.kho)
    dx = t.bo.chon("B/claude-1", None)
    assert (dx.bead_id, dx.buoc, dx.repo.cha) == ("hr-1", "code", t.k.main)
    assert t.g.beads["hr-1"].status == "in_progress" and t.g.beads["hr-1"].assignee == "tram/giao-viec"
    kq = cap_phieu(t.kho, "B/claude-1", dx, bay_gio=LUC, ch=CauHinhTram(), con_hop_le=t.bo.con_hop_le)
    assert kq.phieu is not None and kq.phieu.luot == 1


def test_khong_co_viec_hoac_chua_co_kho_kiem(tmp_path):
    t = dung(tmp_path, bug(labels=["cot:can-chot"]))
    assert t.bo.chon("B/claude-1", None) is None
    t2 = dung(tmp_path / "b", bug())
    t2.bo.kho_git = lambda d: None
    assert t2.bo.chon("B/claude-1", None) is None and t2.g.so_lan("nhan_viec") == 0


def test_q14_khe_da_code_khong_nhan_qc(tmp_path):
    t = dung(tmp_path, bug(status="in_progress", assignee="tram/giao-viec"))
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    fetch(t.k.kho)
    nhan(t.kho, "g-1", 1, khe_id="B/claude-1")
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    kiem(t.kho, "g-1", c, digest=DG)
    assert t.bo.chon("B/claude-1", None) is None
    dx = t.bo.chon("B/claude-2", None)
    assert (dx.buoc, dx.vai, dx.repo.cha) == ("qc", "qc", c)


def test_bead_bi_nguoi_khac_nhan_giua_chung_thi_bo_qua(tmp_path):
    t = dung(tmp_path, bug())
    t.g.nhan_viec = lambda i: (_ for _ in ()).throw(LoiBd("issue already claimed by hung"))
    assert t.bo.chon("B/claude-1", None) is None


def test_da_nhan_tu_lan_truoc_thi_doi_soat_va_giao_tiep(tmp_path):
    t = dung(tmp_path, bug())
    goc = t.g.nhan_viec
    t.g.nhan_viec = lambda i: (goc(i), (_ for _ in ()).throw(LoiBd("timeout")))   # claim xong nhưng mất phản hồi
    assert t.bo.chon("B/claude-1", None).bead_id == "hr-1"


def test_cau_hoi_cho_tick_chan_ca_chon_va_cap(tmp_path):
    t = dung(tmp_path, bug())
    dx = t.bo.chon("B/claude-1", None)
    sk(t.kho, "bao.can_hoi", {"giao_id": "g-cu", "loai_hoi": "thao_tac_nguy_hiem", "noi_dung": "deploy?"})
    assert t.bo.chon("B/claude-1", None) is None
    assert not t.bo.con_hop_le(dx)


def test_con_hop_le(tmp_path):
    t = dung(tmp_path, bug())
    fetch(t.k.kho)
    dx = t.bo.chon("B/claude-1", None)
    assert t.bo.con_hop_le(dx)
    sk(t.kho, "escalation.tao", {"escalation_id": "hr-e", "bead_goc": "hr-1", "giao_id": None, "ly_do": "agent-bi",
                                 "ma_thao_tac": "esc-1"})
    assert not t.bo.con_hop_le(dx)
    sk(t.kho, "escalation.dong", {"escalation_id": "hr-e", "tra_loi": "ok"})
    assert t.bo.con_hop_le(dx)
    p = cap_phieu(t.kho, "B/claude-1", dx, bay_gio=LUC, ch=CauHinhTram()).phieu
    ket_thuc_bang(t.kho, p, "bi", ly_do="agent")
    assert not t.bo.con_hop_le(dx)                         # công việc chờ chưa xử lý
