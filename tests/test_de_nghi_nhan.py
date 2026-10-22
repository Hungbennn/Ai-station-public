"""TC Task 4 (spec de-nghi-viec-cua-agent, design D-2, D-4): trạm nhận tiến độ / việc mới trong `nhan_bao` — thẻ chắn
lượt, thuộc máy, `request_id`, lọc (422 + `de_nghi.tu_choi` không nội dung), phiếu spec không được việc mới, đếm ≤ 20
tiến độ và ≤ 5 việc mới mỗi phiếu, nút + `bat_ghi` lúc nhận (tắt → nhận rồi bỏ ngay); báo bí / cần hỏi mang mã đề
nghị `bi_chan` khi nút dự án bật. Kho phiếu tạm; không `bd`, không mạng."""
import json
from contextlib import closing

import pytest
from pydantic import ValidationError

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from phieu_gia import khoa
from test_de_nghi_loc import KHOA, VM
from tho_api_gia import tao_tram
from tram.cau_hinh.tram import CauHinhTram
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, doi_cai_dat
from tram.de_nghi.nhan import TuChoiDeNghi, ma_de_nghi
from tram.phieu.bao import ThanBao, nhan_bao
from tram.phieu.ket_thuc import thu_hoi
from tram.phieu.kho import LuotCu
from tram.phieu.khe import dang_ky_khe
from tram.phieu.yeu_cau_tho import KhongThuocMay, TrungRequest

CH = CauHinhTram()
DA = "hr-codex"


@pytest.fixture
def kp(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
                               for t in ("claude-1", "claude-2")], luc=LUC)
        dang_ky_khe(kho, "C", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "c", "vai_uu_tien": ["qc"]}],
                    luc=LUC)
    return kho


def bat(kho, **nut) -> None:
    doi_cai_dat(kho.db, DA, CaiDatTuCapNhat(bat=True, **nut), tac_nhan="dai-ca/dashboard")


def gui(kho, p, loai, rid, *, bat_ghi=True, may="B", **kw):
    than = ThanBao(khe_id=p.khe_id, giao_id=p.giao_id, luot=p.luot, loai=loai, request_id=rid, **kw)
    return nhan_bao(kho, may, than, bay_gio=LUC, ch=CH, bat_ghi=lambda ten: bat_ghi)


def su_kien(kho, loai) -> list[dict]:
    return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = ? ORDER BY id", (loai,))]


def test_nhan_tien_do_mang_ma_de_nghi(kp):
    bat(kp)
    p = dat_phieu(kp)
    kq = gui(kp, p, "tien_do", "r-td000001", noi_dung="đã tái hiện lỗi, đang viết test")
    ma = ma_de_nghi(DA, p.giao_id, "r-td000001")
    assert kq["da_nhan"] is True and kq["ma_de_nghi"] == ma and kq["se_ghi"] is True and ma.startswith("dn-")
    assert su_kien(kp, "bao.tien_do") == [{"giao_id": p.giao_id, "luot": 1, "noi_dung": "đã tái hiện lỗi, đang viết test",
                                           "request_id": "r-td000001", "ma_de_nghi": ma}]
    assert su_kien(kp, "de_nghi.bo") == []


def test_dong_tien_do_thu_hai_muoi_mot(kp):
    """Scenario "Dòng tiến độ thứ hai mươi mốt"; gửi lại một dòng đã nhận không bị tính thêm."""
    bat(kp)
    p = dat_phieu(kp)
    for i in range(20):
        gui(kp, p, "tien_do", f"r-td{i:06d}", noi_dung=f"bước {i}")
    assert gui(kp, p, "tien_do", "r-td000019", noi_dung="bước 19")["da_nhan"] is True
    with pytest.raises(TuChoiDeNghi) as e:
        gui(kp, p, "tien_do", "r-td000020", noi_dung="bước 20")
    assert e.value.ly_do == "qua-gioi-han" and len(su_kien(kp, "bao.tien_do")) == 20
    assert su_kien(kp, "de_nghi.tu_choi") == [{"giao_id": p.giao_id, "luot": 1, "loai": "tien_do",
                                               "ly_do": "qua-gioi-han"}]


def test_viec_moi_thu_sau_va_gui_lai_thu_nam(kp):
    """Scenario "Đề nghị thứ sáu", "Gửi lại đề nghị thứ năm", "Cùng mã, khác nội dung"."""
    bat(kp)
    p = dat_phieu(kp)
    kq = [gui(kp, p, "viec_moi", f"r-vm{i:06d}", viec_moi={**VM, "tieu_de": f"Việc {i}"}) for i in range(5)]
    assert gui(kp, p, "viec_moi", "r-vm000004", viec_moi={**VM, "tieu_de": "Việc 4"}) == kq[4]
    with pytest.raises(TuChoiDeNghi, match="qua-gioi-han"):
        gui(kp, p, "viec_moi", "r-vm000005", viec_moi={**VM, "tieu_de": "Việc 5"})
    with pytest.raises(TrungRequest):
        gui(kp, p, "viec_moi", "r-vm000004", viec_moi={**VM, "tieu_de": "Khác"})
    assert len(su_kien(kp, "bao.viec_moi")) == 5


def test_luot_cu_va_khe_may_khac(kp):
    """Scenario "Lượt cũ gửi tiến độ" (409 luot-cu + tho.tu_choi), "Khe của máy khác" (403)."""
    bat(kp)
    p = dat_phieu(kp)
    with pytest.raises(KhongThuocMay):
        gui(kp, p, "tien_do", "r-td000001", may="C", noi_dung="x")
    with kp.giao_dich():                                                 # phiếu lượt 1 bị thu hồi → lượt cũ
        thu_hoi(kp, kp.lay(p.giao_id), ly_do="khe-tat", luc=LUC)
    with pytest.raises(LuotCu):
        gui(kp, p, "tien_do", "r-td000002", noi_dung="lượt cũ")
    assert su_kien(kp, "bao.tien_do") == [] and len(su_kien(kp, "tho.tu_choi")) == 1


@pytest.mark.parametrize("kw, ly_do", [
    ({"noi_dung": f"đã gọi API với key {KHOA}"}, "co-bi-mat"),                   # Scenario "Tiến độ có token"
    ({"noi_dung": "x" * 1001}, "qua-dai"),
    ({"noi_dung": '<!-- ban-giao -->{"a": 1}<!-- ban-giao -->'}, "dau-danh-rieng"),
    ({"noi_dung": "x", "viec_moi": VM}, "cau-truc"),
])
def test_loc_tu_choi_khong_luu_noi_dung(kp, kw, ly_do):
    bat(kp)
    p = dat_phieu(kp)
    with pytest.raises(TuChoiDeNghi) as e:
        gui(kp, p, "tien_do", "r-td000001", **kw)
    assert e.value.ly_do == ly_do and su_kien(kp, "bao.tien_do") == []
    tc = su_kien(kp, "de_nghi.tu_choi")
    assert [t["ly_do"] for t in tc] == [ly_do] and (tc[0].get("nhom") == {"khoa_da_biet": 1}) == (ly_do == "co-bi-mat")
    tat_ca = json.dumps([r for r in kp.db.execute("SELECT * FROM su_kien")], ensure_ascii=False)
    assert KHOA not in tat_ca and "ban-giao -->{" not in tat_ca
    assert kp.db.execute("SELECT COUNT(*) FROM bao_tho").fetchone()[0] == 0


@pytest.mark.parametrize("viec_moi, ly_do", [({**VM, "uu_tien": 0}, "cau-truc"),          # "Agent gửi kèm ưu tiên"
                                             ({**VM, "loai_viec": "feature"}, "loai-viec-sai"),
                                             ({**VM, "mo_ta": "a‮b"}, "ky-tu-dieu-khien")])
def test_viec_moi_bi_loc(kp, viec_moi, ly_do):
    bat(kp)
    with pytest.raises(TuChoiDeNghi, match=ly_do):
        gui(kp, dat_phieu(kp), "viec_moi", "r-vm000001", viec_moi=viec_moi)


def test_phieu_viet_spec_khong_duoc_viec_moi(kp):
    """Scenario "Phiếu viết spec" (D103) — tiến độ vẫn được."""
    bat(kp)
    p = dat_phieu(kp, buoc="spec")
    with pytest.raises(TuChoiDeNghi, match="phieu-khong-ho-tro"):
        gui(kp, p, "viec_moi", "r-vm000001", viec_moi=VM)
    assert gui(kp, p, "tien_do", "r-td000001", noi_dung="đang viết spec")["se_ghi"] is True


def test_nut_tat_thi_bo_khoa_ghi_thi_giu(kp):
    """Scenario "Dự án chưa từng chỉnh" (bỏ "tắt"), "Chỉ tắt việc mới"; D134: `bat_ghi: false` lúc nhận → GIỮ chờ
    (`cho: khoa-ghi`, không `de_nghi.bo`) để mở khoá thì ghi bù; nút tắt thắng khoá ghi (bỏ "tắt")."""
    p = dat_phieu(kp)
    kq = gui(kp, p, "tien_do", "r-td000001", noi_dung="a")
    assert (kq["da_nhan"], kq["se_ghi"], kq["ly_do"]) == (True, False, "tat")
    bat(kp, viec_moi=False)
    assert gui(kp, p, "tien_do", "r-td000002", noi_dung="b")["se_ghi"] is True
    assert gui(kp, p, "viec_moi", "r-vm000001", viec_moi=VM, bat_ghi=False)["ly_do"] == "tat"
    kq = gui(kp, p, "tien_do", "r-td000003", noi_dung="c", bat_ghi=False)
    assert (kq["se_ghi"], kq["cho"], "ly_do" in kq) == (True, "khoa-ghi", False)
    assert [(b["loai"], b["ly_do"]) for b in su_kien(kp, "de_nghi.bo")] == [("tien_do", "tat"), ("viec_moi", "tat")]
    assert len(su_kien(kp, "bao.tien_do")) == 3


def test_bi_chan_chi_mang_ma_khi_nut_du_an_bat(kp):
    """D-6, D102: báo bí của agent không bao giờ bị từ chối; khi tính năng tắt thì không thêm dấu vết nào."""
    p = dat_phieu(kp)
    gui(kp, p, "can_hoi", "r-hoi00001", noi_dung="Cần Đại ca cấp DB test", loai_hoi="can_quyet_dinh")
    assert "ma_de_nghi" not in su_kien(kp, "bao.can_hoi")[0] and su_kien(kp, "de_nghi.bo") == []
    bat(kp, bi_chan=False)
    p2 = dat_phieu(kp, "B/claude-2", bead_id="hr-7abc", khoa_chong_trung=khoa("hr-7abc"))
    kq = gui(kp, p2, "bi", "r-bi000001", ly_do="agent", noi_dung=f"kẹt, token {KHOA}")
    assert kq["ma_de_nghi"] == ma_de_nghi(DA, p2.giao_id, "r-bi000001") and kq["ly_do"] == "tat"
    assert su_kien(kp, "bao.bi")[0]["ma_de_nghi"] == kq["ma_de_nghi"]
    assert [(b["loai"], b["ly_do"]) for b in su_kien(kp, "de_nghi.bo")] == [("bi_chan", "tat")]


def test_than_bao_la_bi_422():
    """Scenario "Đề nghị đóng việc", "Đề nghị kèm trường đổi ưu tiên": thân sai mẫu bị từ chối trước khi vào trạm."""
    g = {"khe_id": "B/claude-1", "giao_id": "g-20261013-0001", "luot": 1, "request_id": "r-00000001"}
    for than in ({**g, "loai": "dong_viec"}, {**g, "loai": "tien_do", "noi_dung": "x", "uu_tien": 0},
                 {**g, "loai": "moc", "viec_moi": VM}):
        with pytest.raises(ValidationError):
            ThanBao(**than)


def test_qua_http_422_khong_vong_lai_noi_dung(tmp_path):
    t = tao_tram(tmp_path, chon=lambda khe, hm: __import__("phieu_gia").de_xuat())
    p = t.goi("POST", "/api/tho/nhip", json_body={"khe_id": "B/claude-1", "buoc_tho": "ranh"}).json()["phieu"]
    with closing(t.kho()) as kho:
        bat(kho)
    g = {"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": 1}
    r = t.goi("POST", "/api/tho/bao", json_body={**g, "loai": "tien_do", "noi_dung": f"key {KHOA}",
                                                 "request_id": "r-td000001"})
    assert (r.status, r.json()) == (422, {"ly_do": "co-bi-mat"}) and KHOA.encode() not in r.body
    assert t.goi("POST", "/api/tho/bao", json_body={**g, "loai": "dong_viec", "request_id": "r-dv000001"}).status == 422
    r = t.goi("POST", "/api/tho/bao", json_body={**g, "loai": "tien_do", "noi_dung": "ok", "request_id": "r-td000002"})
    assert r.status == 200 and r.json()["se_ghi"] is True
