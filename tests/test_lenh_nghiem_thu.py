"""CLI `tram giao nghiem-thu-kiem` (lát 3c S6; hợp đồng P1 H5): xác minh UID thực TRƯỚC mọi spawn; harness là TIẾN TRÌNH
CON dưới `chay_han_tong` (hạn `cho + 900`, kill gộp, dấu `kiem-lai.dong`, `don` dưới khoá) — không luồng + join.
`han_tong`/`xac_minh` giả: không sudo, không tiến trình con thật."""
import os
import sys
from types import SimpleNamespace

import pytest

from tram.cli import tao_parser
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.han_tong import HetHanTong


@pytest.fixture
def cau_hinh(tram_home_tam, tmp_path):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path.resolve()}/kiem\n")


def args(**kw):
    return SimpleNamespace(**{"tai_sinh": False, "cho": 300.0, "trong": False, "dau_ino": None, "cha": None, **kw})


def test_cha_chay_con_duoi_han_tong_va_dau_kiem_lai(cau_hinh, tram_home_tam):
    goi = []
    ma = lnt.lenh_nghiem_thu(args(tai_sinh=True), xac_minh=lambda *a: 777,
                             han_tong=lambda argv, **kw: goi.append((argv, kw)) or 0)
    (argv, kw), = goi
    assert ma == 0 and argv[:4] == [sys.executable, "-I", "-c", lnt.CHAY_CON]      # -I: không nạp mã ở cwd
    assert argv[4:] == ["giao", "nghiem-thu-kiem", "--trong", "--cho", "300.0", "--tai-sinh"]
    assert kw["han"] == 1200.0 and kw["dau"] == tram_home_tam / "kiem-lai.dong" and kw["don"].func is lnt._don


@pytest.mark.parametrize("sai", ["uid", "cho", "nan", "cau_hinh"])
def test_sai_uid_cho_ngan_hoac_thieu_cau_hinh_thi_ma_2_khong_spawn(tram_home_tam, tmp_path, request, sai):
    if sai != "cau_hinh":
        request.getfixturevalue("cau_hinh")

    def xac_minh(*a):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    goi = []
    cho = {"cho": 10.0, "nan": float("nan")}.get(sai, 300.0)
    ma = lnt.lenh_nghiem_thu(args(tai_sinh=True, cho=cho), han_tong=goi.append,
                             xac_minh=xac_minh if sai == "uid" else lambda *a: 777)
    assert ma == 2 and goi == []


def test_qua_han_tong_thi_do_va_bao_dung_trang_thai_dau(cau_hinh, tram_home_tam, capsys):
    def han_tong(argv, **kw):
        raise HetHanTong("harness quá hạn tổng 1200 s")
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=han_tong) == 1
    assert "dấu đã xoá" in capsys.readouterr().err
    (tram_home_tam / "kiem-lai.dong").touch()                     # dọn chưa xác nhận: dấu còn
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=han_tong) == 1
    assert "kiem-lai.dong CÒN" in capsys.readouterr().err


def test_don_thu_hoi_hai_luot_quan_sat_duoi_khoa_loi_thi_dong_cong(monkeypatch, tmp_path):
    goi = []
    c = CongLuot(tmp_path / "c.json", thu_hoi=lambda: goi.append("thu"), quan_sat=[lambda: goi.append("q")],
                 ngu=lambda s: goi.append(s))
    monkeypatch.setattr("tram.giao_viec.cong_that.dung_cong", lambda pk, goc, cac_du_an: goi.append(cac_du_an) or c)
    assert lnt._don(object(), tmp_path) is True and goi == [cac_du_an_quan_sat, "thu", "q", 5.0, "q"]
    c.quan_sat = [lambda: (_ for _ in ()).throw(OSError("launchd chưa đo"))]
    with pytest.raises(OSError):
        lnt._don(object(), tmp_path)
    assert c.trang_thai()["trang_thai"] == "dong"


def test_con_chi_chay_khi_giu_dung_dau_cua_cha(cau_hinh, tram_home_tam, monkeypatch):
    goi = []
    monkeypatch.setattr("tram.giao_viec.nghiem_thu_kiem.nghiem_thu", lambda *a, **kw: goi.append(kw) or [])
    cha = os.getppid()
    assert lnt.lenh_nghiem_thu(args(trong=True, dau_ino=1, cha=cha), xac_minh=lambda *a: 777) == 2   # không có dấu
    dau = tram_home_tam / "kiem-lai.dong"
    dau.touch()
    ino = dau.stat().st_ino
    for sai in ({"dau_ino": ino + 1, "cha": cha}, {"dau_ino": ino, "cha": cha + 1}, {"dau_ino": ino}):  # cũ/gọi tay
        assert lnt.lenh_nghiem_thu(args(trong=True, **sai), xac_minh=lambda *a: 777) == 2
    assert goi == []
    assert lnt.lenh_nghiem_thu(args(trong=True, dau_ino=ino, cha=cha), xac_minh=lambda *a: 777) == 0
    assert goi[0]["thu_hoi"].func.__name__ == "thu_hoi_theo_uid" and goi[0]["cong"].tep.name == "cong.json"
    assert any(getattr(q, "args", None) == (cac_du_an_quan_sat,) for q in goi[0]["cong"].quan_sat)   # env_kin đủ dự án


def test_cha_gan_inode_dau_vao_argv_con(cau_hinh, tram_home_tam, monkeypatch):
    kq, khoi = [], []
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: khoi.append(a))
    lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=lambda argv, **kw: kq.append(kw) or 0)
    (dau := tram_home_tam / "kiem-lai.dong").touch()
    kq[0]["khoi"](["con"], stdin=None)
    assert khoi == [["con", "--dau-ino", str(dau.stat().st_ino), "--cha", str(os.getpid())]]


def test_mo_cong_kiem_chi_tin_cong_uq_khong_quyet_dinh_bang_dau_local(monkeypatch, tmp_path, tram_home_tam):
    from tram.giao_viec import lenh
    from tram.quan_kiem import client
    calls = []
    monkeypatch.setattr(client, 'gui', lambda d: calls.append(d['op']) or {'cong': 'dong'})
    c = client.CongTuXa()
    monkeypatch.setattr(lenh, "_bo", lambda: (None, SimpleNamespace(cong=c)))
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()
    assert lenh._mo_cong(SimpleNamespace(dong_y=True)) == 1 and calls == ['trang-thai', 'mo']
    assert (tram_home_tam / "kiem-lai.dong").exists()


def test_parser():
    p = tao_parser().parse_args(["giao", "nghiem-thu-kiem", "--tai-sinh", "--cho", "300"])
    assert (p.ham.__name__, p.tai_sinh, p.cho, p.trong, p.dau_ino, p.cha) == ("lenh_nghiem_thu", True, 300.0, False,
                                                                                None, None)
