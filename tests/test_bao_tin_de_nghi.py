"""TC Task 11 (spec cong-tac-de-nghi-viec, design D-9, D86, D132): một tin gộp cho mỗi đợt việc mới do agent tạo
(Scenario "Ba việc mới"); rơi vào giờ yên lặng thì gom, gửi buổi sáng (D132); không tin cho tiến độ (Scenario "Agent ghi
năm dòng tiến độ"); "bị chặn" chỉ có tin escalation sẵn có (Scenario "Báo bị chặn"); tin không chứa chữ của agent."""
from datetime import datetime, timedelta, timezone

from bead_gia import bead
from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.nguon import tin_tu_anh, tin_tu_su_kien
from tram.bao_tin.tin import LOAI_TIN, NHAN_LOAI, Tin, soan_tin
from tram.su_kien.mo_hinh import SuKien

URL = "https://may-b.tail.ts.net"
LUC = datetime(2026, 10, 18, 3, 0, tzinfo=timezone.utc)                  # 10:00 giờ VN — ngoài giờ yên lặng


def _sk(loai, du_lieu, bead_id="rn-12", tac_nhan="tram/de-nghi"):
    return SuKien("2026-10-18T03:00:00Z", "repo-nhap", bead_id, loai, tac_nhan, du_lieu, 1)


def test_ba_viec_moi_mot_tin_gop():
    sk = _sk("de_nghi.dot_ghi", {"bead_goc": "rn-12", "bead_moi": ["rn-20", "rn-21", "rn-22"], "vao_cot_3": 9})
    tins = tin_tu_su_kien(sk, None)
    assert "viec_moi_agent" in LOAI_TIN and NHAN_LOAI["viec_moi_agent"] == "việc mới do agent tạo"
    assert tins == [Tin("viec_moi_agent", "repo-nhap", m) for m in ("rn-20", "rn-21", "rn-22")]
    gui = BoChongOn(None).nhan(tins, LUC)
    assert len(gui) == 1 and soan_tin(gui[0].loai, list(gui[0].tins), URL) == (
        "[tram] repo-nhap · 3 việc mới do agent tạo (rn-20, rn-21, rn-22) → " + URL)
    assert tin_tu_su_kien(_sk("de_nghi.dot_ghi", {"bead_moi": ["rn-20", "--x", "a b", 3]}), None) == [
        Tin("viec_moi_agent", "repo-nhap", "rn-20")]


def test_tien_do_va_dau_vet_khong_co_tin():
    """Scenario "Agent ghi năm dòng tiến độ": không tin Telegram nào vì tiến độ."""
    ds = [_sk("bao.tien_do", {"noi_dung": f"dòng {i}", "ma_de_nghi": f"dn-{i}"}, tac_nhan="tho/B/claude-1")
          for i in range(5)]
    ds += [_sk(l, {"ma_de_nghi": "dn-1", "loai": "tien_do"}) for l in ("de_nghi.da_ghi", "de_nghi.bo",
                                                                       "de_nghi.loi_ghi", "de_nghi.tu_choi")]
    ds += [_sk("bao.viec_moi", {"viec_moi": {"tieu_de": "Bí mật X"}}, tac_nhan="tho/B/claude-1"),
           _sk("tu_cap_nhat.cai_dat", {"bat": True}, tac_nhan="dai-ca/dashboard")]
    assert [t for s in ds for t in tin_tu_su_kien(s, None)] == []


def test_bao_bi_chan_chi_mot_tin_escalation():
    """Scenario "Báo bị chặn": đúng một tin — tin escalation sẵn có — không chữ của agent; dòng "bị chặn" không có tin."""
    truoc = {"rn-12": {"nhan": ["cot:ai-lam"], "status": "in_progress"}}
    sau = [bead("rn-12", labels=["cot:ai-lam"], status="in_progress"),
           bead("rn-30", issue_type="decision", labels=["tram:escalation"], description="thiếu quyền đọc bảng")]
    tins = tin_tu_anh("repo-nhap", truoc, sau) + tin_tu_su_kien(
        _sk("de_nghi.da_ghi", {"ma_de_nghi": "dn-9", "loai": "bi_chan", "escalation_id": "rn-30"}), None)
    assert tins == [Tin("escalation", "repo-nhap", "rn-30")]
    vb = soan_tin("escalation", tins, URL)
    assert vb == "[tram] repo-nhap · 1 escalation bí (rn-30) → " + URL and "thiếu quyền" not in vb


def test_gio_yen_lang_gom_gui_buoi_sang():
    """D132: tin việc mới do agent tạo trong giờ yên lặng → gom (bền qua khởi động lại `tram-bao-tin`), hết giờ yên lặng
    gửi MỘT tin gộp — không bỏ như loại tin cũ."""
    dem = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)                     # 02:00 giờ VN
    sang = datetime(2026, 10, 18, 0, 5, tzinfo=timezone.utc)                     # 07:05 giờ VN
    bo = BoChongOn("23:00-07:00")
    for moi in (["rn-20", "rn-21"], ["rn-22"]):
        tins = tin_tu_su_kien(_sk("de_nghi.dot_ghi", {"bead_goc": "rn-12", "bead_moi": moi, "vao_cot_3": 9}), None)
        assert bo.nhan(tins, dem) == []
    assert bo.den_han(dem + timedelta(hours=1)) == []
    gui = BoChongOn("23:00-07:00", bo.trang_thai()).den_han(sang)
    assert [(g.loai, [t.bead_id for t in g.tins]) for g in gui] == [("viec_moi_agent", ["rn-20", "rn-21", "rn-22"])]
    assert soan_tin(gui[0].loai, list(gui[0].tins), URL) == (
        "[tram] repo-nhap · 3 việc mới do agent tạo (rn-20, rn-21, rn-22) → " + URL)
