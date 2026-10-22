"""Đọc hàng đợi trong lúc chạy + kết thúc phiếu phía thợ (spec 3 §7.4–§7.7) — trạm trong bộ nhớ, remote cục bộ."""
import json
import subprocess
import sys
import threading
from contextlib import closing
from dataclasses import replace
from types import SimpleNamespace

from git_gia import git
from tho_chay_gia import FILE_BG, GOC, dung_may, khoi_bg, lay_phieu
from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.tho.chuan_bi import chuan_bi
from tram.tho.ket_thuc import ket_thuc_mem, ket_thuc_xong
from tram.tho.theo_doi import TheoDoi

TC = "Tên kết thúc 'ỷ' không mất byte"


def bao(pc, *args):
    env = {"PATH": "/usr/bin:/bin", "TRAM_GIAO_ID": pc.p.giao_id, "TRAM_HANG_DOI": str(pc.hang_doi),
           "PYTHONPATH": str(GOC), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    if git(pc.wt, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD":
        env.update(TRAM_GIT_QUA_QUAN_LY="1", TRAM_NHANH=pc.p.repo.nhanh)
    subprocess.run([sys.executable, "-c", "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))",
                    "bao", *args], cwd=pc.wt, env=env, check=True, capture_output=True)


def su_kien(m, loai):
    with closing(m.t.kho()) as kho:
        return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = ? ORDER BY id",
                                                          (loai,))]


def chuan_bi_phieu(tmp_path, monkeypatch, *, tu_xa=False, **kw):
    m = dung_may(tmp_path, monkeypatch, [], **kw)
    if tu_xa:
        m.nc.ch = replace(m.nc.ch, tram_api="https://may-b.example.test")
    return m, chuan_bi(m.nc, *lay_phieu(m))


def test_moc_cong_bo_va_giu_ban_giao_tam_can_hoi_dung_ngay(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch, tu_xa=True)
    (pc.wt / "a.txt").write_text("1")
    bao(pc, "--moc", "mốc 1")
    with open(pc.hang_doi, "a") as f:
        f.write("không phải json\n")
    bao(pc, "--can-hoi", "--loai", "can_quyet_dinh", "A hay B?")
    bao(pc, "--moc", "sau câu hỏi — bỏ")
    dung = threading.Event()
    td = TheoDoi(pc, m.nc, dung)
    td.mot_luot()
    assert dung.is_set() and td.can_hoi and len(td.loi) == 1 and pc.tt.vi_tri_hang_doi == 4
    assert len(su_kien(m, "bao.moc")) == 1 and su_kien(m, "bao.can_hoi")[0]["noi_dung"] == "A hay B?"
    assert su_kien(m, "giao.cong_bo")[0]["commit"] == git(pc.wt, "rev-parse", "HEAD")
    assert git(pc.wt, "ls-tree", "--name-only", "HEAD").split() == ["a.txt", "kiem_ok.py"]     # .env.testing không vào


def test_xong_chay_lenh_kiem_cong_bo_roi_bao_xong(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg(TC))
    bao(pc, "--xong", "--ban-giao", FILE_BG, "xong")
    (pc.wt / "con-sot.txt").write_text("sau xong")
    td = TheoDoi(pc, m.nc, threading.Event())
    td.mot_luot()
    assert ket_thuc_xong(pc, m.nc, td.xong) == "cong_bo"
    x = su_kien(m, "bao.xong")[0]
    assert x["loi_ban_giao"] == [] and x["commit"] == git(pc.wt, "rev-parse", "HEAD")
    assert git(pc.wt, "log", "-1", "--format=%s") == "xong: quản lý thợ chốt bản sửa" and x["ban_giao"]["luot"] == pc.p.luot


def test_qc_doc_khoi_qc_tieu_chi_false_ma_tra_ve_khong_loi(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch, buoc="qc")
    qc = {"qc": {"ket_luan": "tra_ve", "commit_code": m.b.cha, "phat_hien": []}}
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg(TC, dat=False) + f"\n<!-- qc -->\n{json.dumps(qc)}\n<!-- qc -->\n")
    bao(pc, "--xong", "--ban-giao", FILE_BG, "QC xong")
    td = TheoDoi(pc, m.nc, threading.Event())
    td.mot_luot()
    ket_thuc_xong(pc, m.nc, td.xong)
    assert su_kien(m, "bao.xong")[0]["loi_ban_giao"] == []


def test_dung_mem_khong_cong_bo_kip_giu_rac_va_noi_ro_snapshot(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    m.t.app.state.cong_bo = (CauHinhCongBo(), None, lambda d: m.b.tram)      # trạm chưa chốt phương án → 503
    monkeypatch.setattr("tram.tho.ket_thuc.time", SimpleNamespace(monotonic=lambda: 0.0))   # hạn chót đã qua
    (pc.wt / "do-dang.txt").write_text("x")
    ket_thuc_mem(pc, m.nc, "estop")
    bi = su_kien(m, "bao.bi")[0]
    assert bi["ly_do"] == "estop" and "rac/hr-1-" in bi["noi_dung"] and "không phải toàn bộ" in bi["noi_dung"]
    assert bi["ban_giao"]["loai"] == "tam" and git(pc.wt, "branch", "--list", "rac/*").strip()


def test_xong_ma_ref_bi_day_ngoai_luong_thi_bao_bi(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    git(m.b.tho, "push", "-q", "origin", f"{m.b.cha}:refs/heads/tram/hr-1")    # ai đó tạo ref công bố ngoài luồng
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg(TC))
    bao(pc, "--xong", "--ban-giao", FILE_BG, "xong")
    td = TheoDoi(pc, m.nc, threading.Event())
    td.mot_luot()
    assert ket_thuc_xong(pc, m.nc, td.xong) == "ngoai-luong"
    assert su_kien(m, "bao.bi")[0]["ly_do"] == "nhanh-bi-day-ngoai-luong" and su_kien(m, "bao.xong") == []


def test_agent_bi_day_wip_va_bao_bi_dung_request_id_cua_dong(tmp_path, monkeypatch):
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    (pc.wt / "dang.txt").write_text("1")
    bao(pc, "--bi", "Thiếu quyền đọc bảng X")
    dung = threading.Event()
    td = TheoDoi(pc, m.nc, dung)
    td.mot_luot()
    assert dung.is_set() and td.bi["loai"] == "bi"
    ket_thuc_mem(pc, m.nc, "agent", noi_dung=td.bi["noi_dung"], request_id=td.bi["request_id"])
    bi = su_kien(m, "bao.bi")[0]
    assert (bi["ly_do"], bi["noi_dung"], bi["request_id"]) == ("agent", "Thiếu quyền đọc bảng X", td.bi["request_id"])
    assert su_kien(m, "giao.cong_bo")[-1]["commit"] == bi["commit"] == git(pc.wt, "rev-parse", "HEAD")
