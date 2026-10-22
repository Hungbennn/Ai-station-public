"""TC Task 12 — mốc 4.1: kịch bản giả lập đầu-cuối (phần 3 thật: nhịp tim, cấp phiếu, nhận báo; thợ giả commit + push
lên remote Git cục bộ; bộ giao việc + vòng tick thật; `bd` giả). Nhánh chính: code → tiến độ → đề nghị 2 việc mới →
kiểm lại → QC đạt → cột 3 → 2 việc mới + 1 tin. Nhánh bị chặn: escalation + dòng ghi chú. Việc mới chạm hàng rào tiền
→ luật cứng 1a xếp cột 2, không phiếu nào được cấp cho nó."""
from dataclasses import replace

from de_nghi_gia import BdDeNghiGia
from giao_viec_gia import bug, dung
from test_kich_ban_4a1 import CH, PASS, khoi_qc, lam, xin
from test_xet_xong import F
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import soan_tin
from tram.cau_hinh.du_an import HangRao
from tram.cham_cot.luat_cung import kiem
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, doi_cai_dat
from tram.de_nghi.vong import NguonDeNghi
from tram.giao_viec.dieu_kien import ly_do_khong_giao
from tram.giao_viec.tick import mot_vong_tick
from tram.phieu.bao import ThanBao, nhan_bao
from tram.su_kien.kho import KhoSuKien

VM = {"tieu_de": "Hoàn tiền bị làm tròn sai ở tóm tắt", "mo_ta": "Gặp khi viết test cắt UTF-8.", "loai_viec": "bug",
      "tieu_chi": "- Làm tròn đúng 2 chữ số"}


def _tram(tmp_path):
    t = dung(tmp_path, bug())
    t.da = replace(t.da, hang_rao={"tien": HangRao(tu_khoa=("hoàn tiền",))})
    t.bdn = BdDeNghiGia(t.g)
    t.bo = replace(t.bo, cac_du_an=lambda: [t.da],
                   de_nghi=NguonDeNghi(tao_bd=lambda da: t.bdn, bat_ghi=lambda ten: True))
    doi_cai_dat(t.kho.db, "hr-codex", CaiDatTuCapNhat(bat=True), tac_nhan="dai-ca/dashboard")
    mot_vong_tick(t.bo)                                                           # fetch kho kiểm
    return t


def gui(t, p, loai, rid, **kw):
    return nhan_bao(t.kho, "B", ThanBao(khe_id=p.khe_id, giao_id=p.giao_id, luot=p.luot, loai=loai, request_id=rid,
                                        **kw), bay_gio=t.gio[0], ch=CH, bat_ghi=lambda ten: True)


def test_code_tien_do_viec_moi_qc_dat_cot_3(tmp_path):
    t = _tram(tmp_path)
    p1 = xin(t, "claude-1")
    assert "tram bao --tien-do" in p1.goi_ngu_canh and "tram bao --viec-moi" in p1.goi_ngu_canh
    gui(t, p1, "tien_do", "r-td000001", noi_dung="đã tái hiện lỗi, đang viết test")
    gui(t, p1, "viec_moi", "r-vm000001", viec_moi=VM)
    gui(t, p1, "viec_moi", "r-vm000002", viec_moi={**VM, "tieu_de": "Thiếu test cho tên rỗng", "loai_viec": "task"})
    mot_vong_tick(t.bo)
    assert t.g.beads["hr-1"].notes.splitlines()[0] == (
        "[tram/de-nghi · tiến độ · B/claude-1 · lượt 1] đã tái hiện lỗi, đang viết test")
    assert not [b for b in t.g.beads.values() if "tram:agent-tao" in b.labels]          # việc mới chờ QC
    c1 = lam(t, p1, {"src/tom_tat.py": "x = 2\n", F: "bàn giao"}, lenh_kiem=PASS)
    assert mot_vong_tick(t.bo)["kiem_lai"] == 1
    p2 = xin(t, "claude-2")
    lam(t, p2, {F: khoi_qc(c1, "dat")}, lenh_kiem=[])
    dem = mot_vong_tick(t.bo)
    assert dem["cot_3"] == 1 and t.g.beads["hr-1"].labels == ("cot:cho-review",)
    dem = mot_vong_tick(t.bo)                                                     # nhịp sau: tạo việc mới
    moi = [b for b in t.g.beads.values() if "tram:agent-tao" in b.labels]
    assert dem["de_nghi_da_ghi"] == 2 and dem["de_nghi_dot"] == 1 and len(moi) == 2
    tins = [x for s in KhoSuKien(tmp_path / "su-kien.db").sau_id(0, 1000) for x in tin_tu_su_kien(s, None)
            if x.loai == "viec_moi_agent"]
    assert soan_tin("viec_moi_agent", tins, None) == f"[tram] hr-codex · 2 việc mới do agent tạo ({moi[0].id}, {moi[1].id})"
    theo_id = {b.id: b for b in t.g.beads.values()}
    assert kiem(moi[0], t.da, theo_id).ep_cot_2 and not kiem(moi[1], t.da, theo_id).ep_cot_2      # hàng rào tiền
    assert ly_do_khong_giao(moi[0], theo_id, t.g.san_sang(), t.da) is not None
    assert xin(t, "claude-1") is None and xin(t, "claude-2") is None                      # không tự giao (D83)
    assert len(t.bdn.goi) == 1 + 2 * 2 and mot_vong_tick(t.bo).get("de_nghi_da_ghi") is None


def test_nhanh_bi_chan_escalation_va_dong_ghi_chu(tmp_path):
    t = _tram(tmp_path)
    p = xin(t, "claude-1")
    gui(t, p, "bi", "r-bi000001", ly_do="agent", noi_dung="thiếu quyền đọc bảng hoá đơn, cần Đại ca cấp DB test")
    mot_vong_tick(t.bo)
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert esc.id in [d.depends_on_id for d in t.g.beads["hr-1"].phu_thuoc]
    assert t.g.beads["hr-1"].notes.splitlines()[0] == (
        "[tram/de-nghi · bị chặn · B/claude-1 · lượt 1] thiếu quyền đọc bảng hoá đơn, cần Đại ca cấp DB test"
        f" (escalation {esc.id})")
    assert xin(t, "claude-1") is None                                                  # escalation chặn như hôm nay
