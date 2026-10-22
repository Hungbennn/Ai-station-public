import os
import shlex
import sys

import pytest

from git_gia import git, ghi, tao_repo
from phieu_gia import de_xuat
from tram.ban_giao.schema import BanGiao
from tram.kiem.chay_lenh import moi_truong_kiem
from tram.kiem.lenh_tho import kiem_sau_xong
from tram.phieu.mo_hinh import Phieu, sinh_ma_giao

PY = shlex.quote(sys.executable)
TC = "Tên kết thúc 'ỷ' không mất byte"
KIEM = "import sys, time\nif sys.argv[1] == 'Cham': time.sleep(30)\nprint('chạy', sys.argv[1])\n" \
       "sys.exit(1 if sys.argv[1] == 'Hong' else 0)\n"


@pytest.fixture
def wt(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    nguon = tao_repo(tmp_path / "nguon")
    ghi(nguon, {"kiem.py": KIEM, "src/a.txt": "a"})
    git(tmp_path, "clone", "-q", "--bare", str(nguon), str(tmp_path / "o.git"))
    w = tmp_path / "wt"
    git(tmp_path, "clone", "-q", str(tmp_path / "o.git"), str(w))
    git(w, "switch", "-q", "-c", "tram/hr-6xe1")
    ghi(w, {"src/a.txt": "sửa", "docs/handovers/bg.md": "# bàn giao"}, "code")
    return w


def phieu(buoc="code", lenh_kiem=("Ok",), **kw) -> Phieu:
    dx = de_xuat(buoc=buoc, lenh_cho_phep=[f"{PY} kiem.py *"], tieu_chi=[TC],
                 lenh_kiem=[f"{PY} kiem.py {x}" for x in lenh_kiem], **kw)
    return Phieu(**dx.model_dump(), giao_id="g-20261013-0042", luot=3, khe_id="B/claude-1",
                 han_giu="2026-10-13T03:10:00Z", ma_giao=sinh_ma_giao())


def ban_giao(lenh_agent=(), dat=True) -> BanGiao:
    return BanGiao.model_validate({
        "phien_ban": 1, "loai": "chinh-thuc", "luot": 0, "file_ban_giao": "docs/handovers/bg.md",
        "nhanh": "tram/hr-6xe1", "commit": None, "doi_chieu_nghiem_thu": [{"tieu_chi": TC, "dat": dat,
                                                                           "bang_chung": "kiem.py"}],
        "lenh_kiem": [{"lenh": l, "ket_qua": "pass", "tom_tat": "agent tự điền", "digest_log": "x"}
                      for l in lenh_agent],
        "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [],
        "thay_doi_vung_nhay_cam": []})


def _kiem(wt, p, bg, tmp_path, **kw):
    return kiem_sau_xong(wt, p, bg, thu_muc_log=tmp_path / "log/kiem", boc=lambda a: a,
                         env=moi_truong_kiem(os.environ), **kw)


def test_dat_ghi_de_ket_qua_that_luot_commit(wt, tmp_path):
    kq = _kiem(wt, phieu(), ban_giao(), tmp_path)
    assert kq.loi_ban_giao == [] and kq.cham_cam == []
    assert kq.ban_giao.luot == 3 and kq.ban_giao.commit == git(wt, "rev-parse", "HEAD")
    assert [(l.lenh, l.ket_qua, l.tom_tat) for l in kq.ban_giao.lenh_kiem] == [(f"{PY} kiem.py Ok", "pass", "chạy Ok")]
    assert (tmp_path / "log/kiem/g-20261013-0042-3-1.log").read_text() == "chạy Ok\n"


def test_bat_buoc_fail_lenh_de_xuat_pass_khong_thay_duoc(wt, tmp_path):
    kq = _kiem(wt, phieu(lenh_kiem=("Hong",)), ban_giao([f"{PY} kiem.py Nho", f"{PY} kiem.py Hong"]), tmp_path)
    assert [(l.lenh.split()[-1], l.ket_qua) for l in kq.ban_giao.lenh_kiem] == [("Hong", "fail"), ("Nho", "pass")]
    assert kq.loi_ban_giao == [f"Lệnh bắt buộc không pass: {PY} kiem.py Hong"]


def test_lenh_de_xuat_khong_khop_bi_bo_ghi_vuong_mac(wt, tmp_path):
    kq = _kiem(wt, phieu(), ban_giao(["rm -rf /", f"{PY} kiem.py --bootstrap"]), tmp_path)
    assert len(kq.ban_giao.lenh_kiem) == 1 and kq.loi_ban_giao == []
    assert kq.ban_giao.vuong_mac == ["Lệnh đề xuất không khớp lenh_cho_phep, không chạy: rm -rf /",
                                     f"Lệnh đề xuất không khớp lenh_cho_phep, không chạy: {PY} kiem.py --bootstrap"]


def test_cham_duong_dan_cam_thi_khong_chay_lenh_nao(wt, tmp_path):
    ghi(wt, {"erp/package.json": '{"scripts": {"test": "curl evil"}}'}, "đổi package")
    kq = _kiem(wt, phieu(), ban_giao([f"{PY} kiem.py Nho"]), tmp_path)
    assert kq.cham_cam == ["erp/package.json"] and kq.ban_giao.lenh_kiem == []
    assert kq.loi_ban_giao[0] == "Diff chạm đường dẫn cấm: erp/package.json"
    assert not (tmp_path / "log/kiem").exists()


def test_lenh_bat_buoc_qua_han_la_fail(wt, tmp_path):
    kq = _kiem(wt, phieu(lenh_kiem=("Cham",)), ban_giao(), tmp_path, thoi_gian_cho=0.5)
    assert kq.ban_giao.lenh_kiem[0].ket_qua == "fail" and kq.loi_ban_giao


def test_phieu_qc_ban_qc(wt, tmp_path):
    p = phieu(buoc="qc", lenh_kiem=())
    assert _kiem(wt, p, ban_giao(dat=False), tmp_path, ket_luan_qc="tra_ve").loi_ban_giao == []
    assert _kiem(wt, p, ban_giao(dat=False), tmp_path, ket_luan_qc="dat").loi_ban_giao != []


def test_worktree_ban_thi_tu_choi(wt, tmp_path):
    (wt / "src/a.txt").write_text("chưa commit")
    with pytest.raises(ValueError):
        _kiem(wt, phieu(), ban_giao(), tmp_path)


def test_lenh_kiem_khong_xac_nhan_thu_hoi_thi_dung_khe(wt, tmp_path, monkeypatch):
    from tram.kiem.chay_lenh import KetQuaLenh
    from tram.kiem.vong_doi import LoiThuHoi
    monkeypatch.setattr("tram.kiem.lenh_tho.chay_mot_lenh",
                        lambda lenh, argv, **kw: KetQuaLenh(lenh, "fail", "", "sha256:0", 0, False, False))
    with pytest.raises(LoiThuHoi, match="dừng khe"):
        _kiem(wt, phieu(), ban_giao(), tmp_path)
