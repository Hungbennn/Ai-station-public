"""TC Task 8 (design D-2, D-4, D-5, D-6, D-7; D84, D107, D134; review vòng 1 Q11, Q13): bước ghi đề nghị trong
`vong_nhanh` — tiến độ và "bị chặn" thành dòng ghi chú có tiền tố + dấu mã; việc mới sau `bead.vao_cot_3` mang nhãn
`tram:agent-tao`, liên kết `discovered-from`, P2, không người nhận; cửa kiểm TƯƠI (nút dự án + nút con, estop,
`bat_ghi`) sát MỖI lệnh `bd` ghi, kể cả giữa `create` và `dep add`; estop / khoá ghi giữ lại, mở thì ghi bù (D107,
D134); ngân sách thời gian mỗi nhịp; đối soát sau khi trạm hỏng. Bộ giao việc trên bản giả (BdGia + BdDeNghiGia chung
kho, kho phiếu tạm, đồng hồ giả); không `bd` thật."""
from dataclasses import replace

import pytest

from de_nghi_gia import BdDeNghiGia
from giao_viec_gia import bug, dung
from su_kien_gia import ket_thuc, kiem, sk
from test_de_nghi_loc import KHOA, VM
from test_kich_ban_4a1 import CH, xin
from tram.chu import estop
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, doi_cai_dat
from tram.de_nghi.cho import de_nghi_cho
from tram.de_nghi.loc import THAY_BI_MAT
from tram.de_nghi.vong import NguonDeNghi, vong_de_nghi
from tram.giao_viec.tick import mot_vong_tick, vong_nhanh
from tram.phieu.bao import ThanBao, nhan_bao

C1 = "c" * 40


@pytest.fixture
def t(tmp_path):
    t = dung(tmp_path, bug())
    t.bdn, t.khoa = BdDeNghiGia(t.g), [True]
    t.bo = replace(t.bo, de_nghi=NguonDeNghi(tao_bd=lambda da: t.bdn, bat_ghi=lambda ten: t.khoa[0]))
    bat(t)
    mot_vong_tick(t.bo)
    t.p = xin(t, "claude-1")
    return t


def bat(t, **nut):
    doi_cai_dat(t.kho.db, "hr-codex", CaiDatTuCapNhat(**{"bat": True, **nut}), tac_nhan="dai-ca/dashboard")


DOI = {"tat_du_an": lambda t: bat(t, bat=False), "tat_tien_do": lambda t: bat(t, tien_do=False),
       "tat_viec_moi": lambda t: bat(t, viec_moi=False), "khoa": lambda t: t.khoa.__setitem__(0, False),
       "estop": lambda t: estop.bat("thử")}


def mo_lai(t):
    t.bdn.nghe = lambda ten: None
    estop.tat()
    t.khoa[0] = True
    bat(t)


def gui(t, loai, rid, p=None, **kw):
    p = p or t.p
    return nhan_bao(t.kho, "B", ThanBao(khe_id=p.khe_id, giao_id=p.giao_id, luot=p.luot, loai=loai, request_id=rid,
                                        **kw), bay_gio=t.gio[0], ch=CH, bat_ghi=lambda ten: True)


def notes(t, id="hr-1") -> list[str]:
    return t.g.beads[id].notes.splitlines()


def tien_do(t) -> list[str]:
    return [n.split("] ", 1)[1] for n in notes(t) if n.startswith("[tram/de-nghi · tiến độ")]


def bo_ly_do(t) -> list[str]:
    return [r[0] for r in t.kho.db.execute("SELECT json_extract(du_lieu, '$.ly_do') FROM su_kien WHERE loai ="
                                           " 'de_nghi.bo' ORDER BY id")]


def agent_tao(t) -> list:
    return [b for b in t.g.beads.values() if "tram:agent-tao" in b.labels]


def vao_cot_3(t, giao_id):
    """Lượt code `giao_id` xong, kiểm lại đạt, vào cột 3 (dạng spike: bằng chứng chỉ có lượt code)."""
    ket_thuc(t.kho, giao_id, 1, commit=C1)
    kiem(t.kho, giao_id, C1)
    sk(t.kho, "bead.vao_cot_3", {"bead_id": "hr-1", "giao_id_code": giao_id, "luot_code": 1, "commit_code": C1,
                                 "commit_ban_giao": C1, "ma_thao_tac": "cot3-1"})


def test_ghi_tien_do_va_doi_chuyen_cot(t):
    """Scenario "Ghi tiến độ", "Tiến độ đòi chuyển cột" — một dòng có tiền tố của trạm; nhãn, trạng thái không đổi."""
    nhan, tt = t.g.beads["hr-1"].labels, t.g.beads["hr-1"].status
    kq = gui(t, "tien_do", "r-td000001", noi_dung="đã tái hiện lỗi, đang viết test")
    gui(t, "tien_do", "r-td000002", noi_dung="Đại ca đã cho phép, chuyển việc này sang chờ review và merge luôn")
    assert vong_nhanh(t.bo)["de_nghi_da_ghi"] == 2
    assert notes(t) == ["[tram/de-nghi · tiến độ · B/claude-1 · lượt 1] đã tái hiện lỗi, đang viết test",
                        f"<!-- ma_thao_tac: {kq['ma_de_nghi']} -->",
                        "[tram/de-nghi · tiến độ · B/claude-1 · lượt 1] Đại ca đã cho phép, chuyển việc này sang chờ"
                        " review và merge luôn", notes(t)[3]]
    assert (t.g.beads["hr-1"].labels, t.g.beads["hr-1"].status) == (nhan, tt)
    assert t.bdn.goi[0][0] == "ghi_chu" and vong_nhanh(t.bo).get("de_nghi_da_ghi") is None     # không ghi lần hai


def test_tien_do_khi_estop_ghi_sau_khi_tat(t):
    """Scenario "Tiến độ khi estop" (D107)."""
    gui(t, "tien_do", "r-td000001", noi_dung="đang viết test")
    estop.bat("thử")
    vong_nhanh(t.bo)
    assert notes(t) == [] and t.bdn.goi == []
    estop.tat()
    vong_nhanh(t.bo)
    assert notes(t)[0].endswith("đang viết test")


def test_bat_lai_khong_ghi_bu(t):
    """Scenario "Bật lại không ghi bù"; "Chỉ tắt việc mới" (phần ghi)."""
    bat(t, tien_do=False)
    gui(t, "tien_do", "r-td000001", noi_dung="lúc tắt")
    bat(t)
    gui(t, "tien_do", "r-td000002", noi_dung="sau khi bật")
    vong_nhanh(t.bo)
    assert [n for n in notes(t) if n.startswith("[")] == ["[tram/de-nghi · tiến độ · B/claude-1 · lượt 1] sau khi bật"]


def test_tat_nut_khi_viec_moi_dang_cho_qc(t):
    """Scenario "Tắt nút khi việc mới đang chờ QC": bỏ với lý do "tắt", không tạo việc nào dù sau đó vào cột 3."""
    gui(t, "viec_moi", "r-vm000001", viec_moi=VM)
    gui(t, "viec_moi", "r-vm000002", viec_moi={**VM, "tieu_de": "Việc thứ hai"})
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert agent_tao(t) == []                                                   # còn chờ QC
    bat(t, viec_moi=False)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    vao_cot_3(t, t.p.giao_id)
    bat(t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert agent_tao(t) == [] and [r[0] for r in t.kho.db.execute(
        "SELECT json_extract(du_lieu, '$.ly_do') FROM su_kien WHERE loai = 'de_nghi.bo'")] == ["tat", "tat"]


@pytest.mark.parametrize("cach", ["doc_lai", "ra_khoi_danh_sach"])
def test_khoa_ghi_giua_chung_roi_mo_khoa_ghi_bu(t, cach):
    """D134 — Scenario "Khoá ghi giữa chừng": 2 việc mới chờ QC; `bat_ghi: false` rồi QC đạt (vào cột 3) → không tạo
    việc nào, hai đề nghị VẪN CHỜ (không `de_nghi.bo`). Scenario "Mở khoá thì ghi bù": mở khoá, nút việc mới còn bật →
    lượt quét kế tiếp tạo hai việc. `doc_lai`: dự án còn trong danh sách, `bat_ghi` đọc lại ra false (cửa kiểm tươi);
    `ra_khoi_danh_sach`: vòng tick không còn thấy dự án (khoá trong `du-an/*.yaml`)."""
    gui(t, "viec_moi", "r-vm000001", viec_moi=VM)
    gui(t, "viec_moi", "r-vm000002", viec_moi={**VM, "tieu_de": "Việc thứ hai"})
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {"de_nghi_cho": 2}     # còn chờ QC
    if cach == "doc_lai":
        t.khoa[0] = False
    else:
        t.bo = replace(t.bo, cac_du_an=lambda: [])
    vao_cot_3(t, t.p.giao_id)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert agent_tao(t) == [] and t.bdn.goi == [] and bo_ly_do(t) == [] and len(de_nghi_cho(t.kho)) == 2
    t.khoa[0], t.bo = True, replace(t.bo, cac_du_an=lambda: [t.da])
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {"de_nghi_da_ghi": 2, "de_nghi_dot": 1}
    assert [b.title for b in agent_tao(t)] == [VM["tieu_de"], "Việc thứ hai"] and de_nghi_cho(t.kho) == []


@pytest.mark.parametrize("doi", ["tat_du_an", "tat_tien_do", "khoa", "estop"])
def test_cua_kiem_tuoi_sau_doc_beads_va_giua_hai_ghi_chu(t, doi):
    """Q11: `bd.tat_ca()` có thể lâu — nút / `bat_ghi` / estop đổi trong lúc đọc thì KHÔNG ghi gì; đổi ngay sau ghi chú
    thứ nhất thì ghi chú thứ hai không ghi. Khoá / estop → giữ, mở lại thì ghi bù; tắt nút → bỏ "tắt", không ghi bù."""
    giu = doi in ("khoa", "estop")
    gui(t, "tien_do", "r-td000001", noi_dung="một")
    gui(t, "tien_do", "r-td000002", noi_dung="hai")
    t.bdn.nghe = lambda ten: ten == "tat_ca" and DOI[doi](t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert t.bdn.goi == [] and bo_ly_do(t) == ([] if giu else ["tat", "tat"])
    mo_lai(t)
    if not giu:
        gui(t, "tien_do", "r-td000003", noi_dung="một")
        gui(t, "tien_do", "r-td000004", noi_dung="hai")
    t.bdn.nghe = lambda ten: ten == "ghi_chu" and DOI[doi](t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert tien_do(t) == ["một"]
    mo_lai(t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert tien_do(t) == (["một", "hai"] if giu else ["một"]) and len(t.bdn.goi) == 1 + giu


@pytest.mark.parametrize("doi", ["khoa", "estop", "tat_du_an", "tat_viec_moi"])
def test_cua_kiem_tuoi_giua_create_va_dep_add(t, doi):
    """Q11: đọc lại công tắc chính, nút con, estop, `bat_ghi` ngay trước `bd dep add` — đổi ngay sau `bd create` thì
    không liên kết. Khoá / estop → giữ chờ; mở lại → CHỈ nối liên kết cho việc đã tạo (đối soát dấu mã), không tạo lại.
    Tắt nút → bỏ "tắt" kèm mã việc đã tạo; bật lại không ghi bù."""
    gui(t, "viec_moi", "r-vm000001", viec_moi=VM)
    vao_cot_3(t, t.p.giao_id)
    t.bdn.nghe = lambda ten: ten == "tao_viec_moi" and DOI[doi](t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    moi = agent_tao(t)
    assert [g[0] for g in t.bdn.goi] == ["tao_viec_moi"] and len(moi) == 1 and moi[0].phu_thuoc == ()
    mo_lai(t)
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    if doi in ("khoa", "estop"):
        assert [g[0] for g in t.bdn.goi] == ["tao_viec_moi", "lien_ket"] and len(agent_tao(t)) == 1
        assert [(x.depends_on_id, x.loai) for x in agent_tao(t)[0].phu_thuoc] == [("hr-1", "discovered-from")]
    else:
        assert [g[0] for g in t.bdn.goi] == ["tao_viec_moi"] and bo_ly_do(t) == ["tat"]
        assert t.kho.db.execute("SELECT json_extract(du_lieu, '$.bead_moi') FROM su_kien WHERE loai = 'de_nghi.bo'"
                                ).fetchone()[0] == moi[0].id


def test_ngan_sach_moi_nhip_lenh_bd_cham_va_escalation_dang_cho(t):
    """Q13: mỗi lệnh `bd` của đề nghị chậm 8 s (đồng hồ giả), ngân sách 20 s → mỗi nhịp ngừng nhận thêm khi hết ngân
    sách (tốn ≤ 20 s + một lệnh), phần còn lại để nhịp sau, đúng thứ tự, không ghi trùng. Báo bí tới khi hàng còn 3
    tiến độ: escalation vẫn được tạo ngay nhịp kế tiếp; dòng "bị chặn" ghi SAU các tiến độ đến trước nó."""
    gio = [0.0]
    t.bdn.nghe = lambda ten: gio.__setitem__(0, gio[0] + 8)
    t.bo = replace(t.bo, de_nghi=replace(t.bo.de_nghi, ngan_sach=20.0, dong_ho=lambda: gio[0]))
    for i in range(5):
        gui(t, "tien_do", f"r-td{i:06d}", noi_dung=f"bước {i}")
    ton = []
    for i in range(4):
        if i == 1:
            gui(t, "bi", "r-bi000001", ly_do="agent", noi_dung="thiếu quyền đọc bảng hoá đơn")
        truoc = gio[0]
        vong_nhanh(t.bo)
        ton.append((gio[0] - truoc, len(notes(t)) // 2))
        if i == 1:
            assert any(b.issue_type == "decision" for b in t.g.beads.values())         # escalation không phải chờ
    assert ton == [(24.0, 2), (24.0, 4), (24.0, 6), (0.0, 6)]                 # hàng rỗng: không gọi bd
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert [n for n in notes(t) if n.startswith("[")] == [
        *(f"[tram/de-nghi · tiến độ · B/claude-1 · lượt 1] bước {i}" for i in range(5)),
        f"[tram/de-nghi · bị chặn · B/claude-1 · lượt 1] thiếu quyền đọc bảng hoá đơn (escalation {esc.id})"]
    assert [g[0] for g in t.bdn.goi] == ["ghi_chu"] * 6


def test_viec_moi_duoc_tao_sau_vao_cot_3(t):
    """Scenario "Việc mới được tạo": loại `bug`, P2, nhãn do agent tạo, phát hiện từ `hr-1`, tiêu chí như agent gửi,
    không người nhận, không nhãn cột, `hr-1` không bị chặn; một `de_nghi.dot_ghi` cho cả đợt."""
    gui(t, "viec_moi", "r-vm000001", viec_moi=VM)
    gui(t, "viec_moi", "r-vm000002", viec_moi={**VM, "tieu_de": "Thiếu test cho 'ỷ'", "loai_viec": "task"})
    vao_cot_3(t, t.p.giao_id)
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {"de_nghi_da_ghi": 2, "de_nghi_dot": 1}
    moi = agent_tao(t)
    assert [(b.title, b.issue_type, b.priority, b.status, b.assignee) for b in moi] == [
        (VM["tieu_de"], "bug", 2, "open", ""), ("Thiếu test cho 'ỷ'", "task", 2, "open", "")]
    b = moi[0]
    assert b.labels == ("tram:agent-tao",) and b.acceptance_criteria == VM["tieu_chi"] and b.nhan_cot() is None
    assert [(x.depends_on_id, x.loai) for x in b.phu_thuoc] == [("hr-1", "discovered-from")]
    assert b.description.splitlines()[:2] == [f"Do agent tạo khi làm hr-1 (khe B/claude-1, lượt 1)", "viec_goc: hr-1"]
    assert VM["mo_ta"] in b.description and t.g.beads["hr-1"].phu_thuoc == ()
    dot = [r[0] for r in t.kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'de_nghi.dot_ghi'")]
    assert len(dot) == 1 and f'"bead_moi": ["{moi[0].id}", "{moi[1].id}"]' in dot[0]
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {} and len(agent_tao(t)) == 2


def test_tram_hong_sau_khi_tao_viec_moi(t):
    """Scenario "Trạm hỏng sau khi tạo việc mới": lần sau tìm thấy việc mang mã đề nghị, nối liên kết còn thiếu, ghi
    "đã ghi", không tạo việc thứ hai. Lỗi chỉ để lại mã lỗi."""
    gui(t, "viec_moi", "r-vm000001", viec_moi=VM)
    vao_cot_3(t, t.p.giao_id)
    t.bdn._sau = {"tao_viec_moi": 1}
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {"loi": 1}
    loi = [r[0] for r in t.kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'de_nghi.loi_ghi'")]
    assert len(loi) == 1 and '"ma_loi": "bd"' in loi[0] and VM["tieu_de"] not in loi[0]
    assert vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0]) == {"de_nghi_da_ghi": 1, "de_nghi_dot": 1}
    assert len(agent_tao(t)) == 1 and agent_tao(t)[0].phu_thuoc[0].loai == "discovered-from"
    assert [g[0] for g in t.bdn.goi] == ["tao_viec_moi", "lien_ket"]


def test_tram_hong_sau_ghi_chu_khong_ghi_trung(t):
    gui(t, "tien_do", "r-td000001", noi_dung="một lần thôi")
    t.bdn._sau = {"ghi_chu": 1}
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    vong_de_nghi(t.bo, t.bo.de_nghi, t.gio[0])
    assert sum("một lần thôi" in n for n in notes(t)) == 1 and len(t.bdn.goi) == 1


def test_bao_bi_chan_ghi_dong_va_ma_escalation(t):
    """Scenario "Báo bị chặn": dòng "bị chặn" kèm lý do và mã escalation; escalation vẫn chặn việc như hôm nay.
    Scenario "Lý do bị chặn có bí mật": câu thay thế ở cả hai chỗ."""
    gui(t, "bi", "r-bi000001", ly_do="agent", noi_dung="thiếu quyền đọc bảng hoá đơn, cần Đại ca cấp DB test")
    vong_nhanh(t.bo)
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert esc.id in [d.depends_on_id for d in t.g.beads["hr-1"].phu_thuoc]
    assert notes(t)[0] == ("[tram/de-nghi · bị chặn · B/claude-1 · lượt 1] thiếu quyền đọc bảng hoá đơn, cần Đại ca"
                           f" cấp DB test (escalation {esc.id})")


def test_ly_do_bi_chan_co_bi_mat(t):
    gui(t, "can_hoi", "r-hoi00001", noi_dung=f"mật khẩu DB password={KHOA[7:]}", loai_hoi="can_quyet_dinh")
    vong_nhanh(t.bo)
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert notes(t)[0].endswith(f"] {THAY_BI_MAT} (escalation {esc.id})")
    assert KHOA[7:] not in t.g.beads["hr-1"].notes and KHOA[7:] not in esc.description


def test_nut_bi_chan_tat_khong_ghi_dong(t):
    """Scenario "Nút bị chặn tắt": ghi chú của việc không đổi; escalation vẫn được tạo."""
    bat(t, bi_chan=False)
    gui(t, "bi", "r-bi000001", ly_do="agent", noi_dung="kẹt")
    vong_nhanh(t.bo)
    assert notes(t) == [] and any(b.issue_type == "decision" for b in t.g.beads.values())


def test_khong_co_nguon_thi_khong_ghi(t):
    """`BoGiaoViec.de_nghi = None` (mặc định cũ): bước ghi không chạy — ghép lát không đổi hành vi bộ giao việc."""
    gui(t, "tien_do", "r-td000001", noi_dung="x")
    vong_nhanh(replace(t.bo, de_nghi=None))
    assert notes(t) == [] and t.bdn.goi == []


@pytest.mark.parametrize("loai", ["tien_do", "viec_moi"])
def test_doc_25_giay_van_ghi_dung_mot_lan(t, loai):
    """V2-Q3: đọc 25 s < HAN_BD, ghi 25 s; create/dep được nối tiếp ở nhịp sau."""
    gio = [0.0]
    t.bdn.nghe = lambda ten: gio.__setitem__(0, gio[0] + 25)
    nguon = replace(t.bo.de_nghi, dong_ho=lambda: gio[0])
    if loai == "viec_moi":
        gui(t, loai, "r-vm000001", viec_moi=VM)
        vao_cot_3(t, t.p.giao_id)
    else:
        gui(t, loai, "r-td000001", noi_dung="đọc chậm vẫn tiến lên")
    ton = []
    for _ in range(4):
        truoc = gio[0]
        vong_de_nghi(t.bo, nguon, t.gio[0])
        ton.append(gio[0] - truoc)
    assert [g[0] for g in t.bdn.goi] == (
        ["tao_viec_moi", "lien_ket"] if loai == "viec_moi" else ["ghi_chu"])
    assert ton == ([50, 50, 0, 0] if loai == "viec_moi" else [50, 0, 0, 0])
    assert de_nghi_cho(t.kho) == []
    if loai == "viec_moi":
        assert len(agent_tao(t)) == 1
        assert agent_tao(t)[0].phu_thuoc[0].depends_on_id == "hr-1"
    else:
        assert tien_do(t) == ["đọc chậm vẫn tiến lên"]


@pytest.mark.parametrize("loi_doc", [False, True])
def test_doc_cham_khong_lam_doi_du_an_sau(t, loi_doc):
    """Dự án đầu còn hàng (hoặc đọc lỗi); dự án sau vẫn được phục vụ ở nhịp 2."""
    from tram.beads.loi import LoiBd

    gio = [0.0]
    for i in range(3):
        gui(t, "tien_do", f"r-td{i:06d}", noi_dung=f"bước {i}")
    c = de_nghi_cho(t.kho)[0]
    da2 = replace(t.da, ten="du-an-sau")
    bd2 = BdDeNghiGia(type(t.g)([bug("sau-1")]))
    doi_cai_dat(t.kho.db, da2.ten, CaiDatTuCapNhat(bat=True), tac_nhan="dai-ca/dashboard")
    with t.kho.giao_dich():
        t.kho.ghi_su_kien(da2.ten, "bao.tien_do", {**c.du_lieu, "ma_de_nghi": "dn-du-an-sau"},
                        luc=t.gio[0], bead_id="sau-1", tac_nhan="tho/B/claude-1")

    def cham(ten):
        gio[0] += 25
        if loi_doc and ten == "tat_ca":
            raise LoiBd("giả lập đọc lỗi")

    t.bdn.nghe = cham
    bd2.nghe = lambda ten: gio.__setitem__(0, gio[0] + 25)
    nguon = replace(t.bo.de_nghi, tao_bd=lambda da: t.bdn if da.ten == t.da.ten else bd2,
                    dong_ho=lambda: gio[0])
    bo = replace(t.bo, cac_du_an=lambda: [t.da, da2])
    for _ in range(2):
        truoc = gio[0]
        vong_de_nghi(bo, nguon, t.gio[0])
        assert gio[0] - truoc <= 80          # 20 + đọc cuối 30 + ghi dự phòng 30
    assert [g[0] for g in bd2.goi] == ["ghi_chu"]
    assert len(t.bdn.goi) == (0 if loi_doc else 1)       # dự án đầu vẫn còn hàng
    t.bdn.nghe = lambda ten: gio.__setitem__(0, gio[0] + 25)
    for _ in range(5):
        vong_de_nghi(bo, nguon, t.gio[0])
    assert len(bd2.goi) == 1 and tien_do(t) == [f"bước {i}" for i in range(3)]
    assert de_nghi_cho(t.kho) == []


@pytest.mark.parametrize("doi", ["tat_du_an", "tat_tien_do", "khoa", "estop"])
def test_doc_25_giay_khong_mien_cua_an_toan(t, doi):
    """Suất ghi dự phòng chỉ miễn hết giờ; nút, khoá và estop vẫn đọc tươi sau đọc chậm."""
    gio = [0.0]
    gui(t, "tien_do", "r-td000001", noi_dung="chờ cửa an toàn")

    def cham(ten):
        gio[0] += 25
        if ten == "tat_ca":
            DOI[doi](t)

    t.bdn.nghe = cham
    nguon = replace(t.bo.de_nghi, dong_ho=lambda: gio[0])
    vong_de_nghi(t.bo, nguon, t.gio[0])
    assert t.bdn.goi == []
    mo_lai(t)
    t.bdn.nghe = lambda ten: gio.__setitem__(0, gio[0] + 25)
    vong_de_nghi(t.bo, nguon, t.gio[0])
    assert len(t.bdn.goi) == (1 if doi in ("khoa", "estop") else 0)
