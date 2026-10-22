"""Tiếp nhận yêu cầu tạo feature (plan 4d 4D-1b): gửi lại cùng mã trả feature cũ, khác nội dung là xung đột ở MỌI
trạng thái, lệnh `bd` do B quyết. `bd` giả (file tạm), SQLite tạm."""
import pytest
from yeu_cau_gia import LOGIN, MA, BdTep, giu_cho, yc

from tram.beads.bd import Bd
from tram.giao_viec.feature import ly_do_khong_giao_spec
from tram.yeu_cau.dich_vu import tiep_nhan
from tram.yeu_cau.mau import dong_dau, mo_ta, tim_theo_dau
from tram.yeu_cau.so_nhan import SoNhan


@pytest.fixture
def mt(tmp_path):
    return SoNhan(tmp_path / "sk.db"), BdTep(tmp_path)


def test_tao_mot_lan_gui_lai_tra_feature_cu(mt):
    so, bd = mt
    kq = tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
    assert (kq.trang_thai, kq.bead_id) == ("da_tao", "hr-f1")
    assert tiep_nhan(so, bd, yc(), nguoi_gui="khac@example.com").bead_id == "hr-f1"
    assert tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN).trang_thai == "da_co" and bd.so_lan_tao() == 1
    (b,) = bd.tat_ca()
    assert (b.issue_type, b.labels, b.priority, b.title) == ("feature", ("can-spec",), 2, "Hoa hồng tạm tính")
    assert b.description.split("\n")[0] == dong_dau(MA) and ly_do_khong_giao_spec(b, {b.id}, "hr-codex") is None
    bn = so.lay(MA)
    assert (bn.trang_thai, bn.bead_id, bn.nguoi_gui, bn.du_an) == ("da_tao", "hr-f1", LOGIN, "hr-codex")


def _o_trang_thai(so, bd, tt):
    """Đưa mã MA về trạng thái `tt` bằng chính các bước của sổ (như một lần gửi trước đó)."""
    giu_cho(so, han=1e12, chu="c1")
    if tt in ("dang_tao", "khong_ro", "da_tao"):
        so.bat_dau_tao(MA, chu="c1", han=1e12)
    if tt == "khong_ro":
        so.chu_bao_loi(MA, chu="c1", ly_do="bd_loi")
    if tt == "da_tao":
        so.da_tao(MA, bd.them_dau())


@pytest.mark.parametrize("tt", ["nhan", "dang_tao", "khong_ro", "da_tao"])
@pytest.mark.parametrize("sua", [{"tieu_de": "Khác"}, {"uu_tien": 1}, {"phieu": {**yc().phieu.model_dump(),
                                                                                  "khong_lam": ["Khác"]}}])
def test_cung_ma_khac_noi_dung_la_xung_dot_o_moi_trang_thai(mt, tt, sua):
    so, bd = mt
    _o_trang_thai(so, bd, tt)
    truoc, so_bead = so.lay(MA), len(bd.tat_ca())
    kq = tiep_nhan(so, bd, yc(**sua), nguoi_gui=LOGIN)
    assert kq.trang_thai == "xung_dot" and so.lay(MA) == truoc
    assert bd.so_lan_tao() == 0 and len(bd.tat_ca()) == so_bead


def test_khac_du_an_cung_ma_la_xung_dot(mt):
    so, bd = mt
    tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
    p = {**yc().phieu.model_dump(), "du_an": "erp"}
    assert tiep_nhan(so, bd, yc(du_an="erp", phieu=p), nguoi_gui=LOGIN).trang_thai == "xung_dot"
    assert bd.so_lan_tao() == 1


def test_thu_tu_khoa_va_truong_mac_dinh_khong_doi_digest(mt):
    so, bd = mt
    tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
    dao = dict(reversed(list(yc().phieu.model_dump().items())))
    assert tiep_nhan(so, bd, yc(phieu=dao), nguoi_gui=LOGIN).trang_thai == "da_co"


def test_dau_o_dong_khac_hay_bead_khac_loai_khong_tinh(mt):
    so, bd = mt
    bd.them("mở đầu\n" + dong_dau(MA))
    bd.them_dau(loai="task")
    assert tim_theo_dau(bd.tat_ca(), MA) == []
    assert tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN).trang_thai == "da_tao" and bd.so_lan_tao() == 1


def test_lenh_bd_that_do_b_quyet_nhan_loai_actor_kho(tmp_path):
    goi = []

    def chay(argv):
        goi.append(list(argv))
        return "[]" if "list" in argv else "hr-f9\n"
    bd = Bd(tmp_path / "kho-b", actor="dai-ca/may-a", runner=chay)
    kq = tiep_nhan(SoNhan(tmp_path / "sk.db"), bd, yc(), nguoi_gui=LOGIN)
    assert (kq.trang_thai, kq.bead_id) == ("da_tao", "hr-f9")
    assert [g[2] for g in goi] == ["list", "create"]
    tao = goi[1]
    assert tao[:4] == ["-C", str(tmp_path / "kho-b"), "create", "Hoa hồng tạm tính"]
    assert tao[tao.index("-d") + 1] == mo_ta(yc()) and tao[tao.index("-t") + 1] == "feature"
    assert tao[tao.index("-l") + 1] == "can-spec" and tao.count("-l") == 1
    assert tao[tao.index("--actor") + 1] == "dai-ca/may-a" and tao[tao.index("-p") + 1] == "2"
