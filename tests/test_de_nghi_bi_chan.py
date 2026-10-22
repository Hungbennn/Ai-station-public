"""TC Task 7 (design D-6, D102; spec "Bị chặn ghi ngay, không thay escalation"): escalation của báo bí / cần hỏi vẫn
tạo như hôm nay dù nút bật hay tắt; nút bị chặn đang cho ghi → lý do được lọc trước khi vào escalation (Scenario "Lý
do bị chặn có bí mật"). Bộ giao việc trên bản giả (BdGia, kho phiếu tạm); không `bd` thật."""
from giao_viec_gia import bug, dung
from test_de_nghi_loc import KHOA
from test_kich_ban_4a1 import bao, xin
from tram.de_nghi.bi_chan import cau_hoi_esc, ma_escalation_cua
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, doi_cai_dat
from tram.de_nghi.loc import THAY_BI_MAT
from tram.giao_viec.escalation import ma_escalation
from tram.giao_viec.tick import mot_vong_tick

LY_DO = f"thiếu quyền đọc bảng hoá đơn, mật khẩu thử password={KHOA[7:]}"


def _esc(t):
    return next(b for b in t.g.beads.values() if b.issue_type == "decision")


def _bat(t, **nut):
    doi_cai_dat(t.kho.db, t.da.ten, CaiDatTuCapNhat(bat=True, **nut), tac_nhan="dai-ca/dashboard")


def test_nut_bi_chan_bat_thi_escalation_mang_cau_thay_the(tmp_path):
    t = dung(tmp_path, bug())
    _bat(t)
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    bao(t, p, "bi", ly_do="agent", noi_dung=LY_DO)
    mot_vong_tick(t.bo)
    esc = _esc(t)
    assert THAY_BI_MAT in esc.description and KHOA[7:] not in esc.description
    assert esc.id in [d.depends_on_id for d in t.g.beads["hr-1"].phu_thuoc]          # vẫn chặn việc như hôm nay


def test_nut_bi_chan_tat_thi_escalation_nhu_hom_nay(tmp_path):
    """Scenario "Nút bị chặn tắt": escalation vẫn được tạo, lý do như hôm nay (D111 sửa riêng)."""
    t = dung(tmp_path, bug())
    _bat(t, bi_chan=False)
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    bao(t, p, "can_hoi", noi_dung="Cần Đại ca cấp DB test", loai_hoi="can_quyet_dinh")
    mot_vong_tick(t.bo)
    assert "Cần Đại ca cấp DB test" in _esc(t).description and t.g.beads["hr-1"].notes == ""


def test_cau_hoi_esc_chi_loc_ly_do_cua_agent(tmp_path):
    t = dung(tmp_path, bug())
    _bat(t)
    assert cau_hoi_esc(t.kho.db, "hr-codex", "agent-can-hoi", LY_DO) == THAY_BI_MAT
    assert cau_hoi_esc(t.kho.db, "hr-codex", "dong-file-cau-hinh", LY_DO) == LY_DO       # câu của trạm: giữ
    assert cau_hoi_esc(t.kho.db, "du-an-khac", "agent-bi", LY_DO) == LY_DO                 # dự án chưa bật


def test_ma_escalation_cua_khop_luong_san_co():
    assert ma_escalation_cua("hr-codex", "hr-1", "bao.bi", 7, {"giao_id": "g-1"}) == ma_escalation(
        "hr-codex", "hr-1", "agent-bi", "g-1")
    assert ma_escalation_cua("hr-codex", "hr-1", "bao.can_hoi", 9, {"loai_hoi": "thao_tac_nguy_hiem"}) == \
        ma_escalation("hr-codex", "hr-1", "can-thao-tac-nguy-hiem", "hoi-9")
