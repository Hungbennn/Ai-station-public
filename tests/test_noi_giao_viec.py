"""Nối bộ giao việc vào tram-api (spec 4 §13; 3a-1 G11): chỉ khi `giao_viec.bat`; router nhịp tim truyền
`con_hop_le`; lỗi phần 4 không làm hỏng nhịp tim. Không chạy `bd` thật: bộ giả, dự án trong thư mục tạm."""
import threading
from pathlib import Path

from api_gia import tao_pt
from giao_viec_gia import bug, dung
from phieu_gia import de_xuat
from tho_api_gia import tao_tram
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.giao_viec.noi_that import an_toan, dung_bo_that, noi_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}


def test_tat_thi_chi_gan_bo_giao(tmp_path):
    t = dung(tmp_path, bug())
    pt, luong = noi_giao_viec(tao_pt(tmp_path, {}), threading.Event(), cg=CauHinhGiaoViec(),
                              tao_bo=lambda cg, ch, bo_dem: t.bo)
    assert (pt.bo_giao, pt.chon_phieu, luong) == (t.bo, None, [])


def test_bat_thi_noi_chon_con_hop_le_va_hai_luong(tmp_path):
    t = dung(tmp_path, bug())
    t.bo.cac_du_an = lambda: []
    dung_ev, nhan = threading.Event(), []
    cg = CauHinhGiaoViec(bat=True, chu_ky_giay=30, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
    pt, luong = noi_giao_viec(tao_pt(tmp_path, {}), dung_ev, cg=cg,
                              tao_bo=lambda cg, ch, bo_dem: nhan.append(bo_dem) or t.bo)
    try:
        assert pt.bo_giao is t.bo and nhan[0] is not None
        assert pt.chon_phieu("B/claude-1", None) is None and pt.con_hop_le_phieu(de_xuat()) is False
        assert sorted(x.name for x in luong) == ["tram-giao-deploy", "tram-giao-git", "tram-giao-nhanh"]     # TM-3
    finally:
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong)


def test_loi_phan_4_khong_lam_hong_nhip(capsys):
    def no(*a):
        raise RuntimeError("bd treo")
    assert an_toan(no, None, "chon")("B/claude-1", None) is None and an_toan(no, False, "con_hop_le")(1) is False
    assert "[giao-viec] chon: RuntimeError" in capsys.readouterr().err


def test_router_nhip_truyen_con_hop_le(tmp_path):
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat())
    t.app.state.pt.con_hop_le_phieu = lambda d: False
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json() == {"tiep_tuc": True, "phieu": None}
    t.app.state.pt.con_hop_le_phieu = lambda d: True
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]["bead_id"] == "hr-6xe1"


def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
    (tmp_path / "du-an").mkdir()
    (tmp_path / "du-an" / "hr-x.yaml").write_text(f"ten: hr-x\nduong_dan: {tmp_path}\nbat_ghi: true\n")   # 1.22
    (tmp_path / "du-an" / "hong.yaml").write_text("ten: khac\nduong_dan: /x\n")
    (tmp_path / "du-an" / "_mau.yaml").write_text("ten: _mau\n")
    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
    bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
    assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
    assert bo.kiem_tu_xa is not None and bo.boc is None and bo.don_sach is None
    assert bo.cong.__class__.__name__ == "CongTuXa"
    assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
    assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
