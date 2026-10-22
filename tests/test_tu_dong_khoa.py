"""TM-1: hai hàm tính cho lát sau — khoá chung trước mọi thao tác tự động (design D-2 năm dòng đầu, D-9, D97) và
đường dẫn cấm sinh từ ba lệnh (D89). Hàm thuần."""
import posixpath
from dataclasses import replace

import pytest

from tram.kiem.duong_dan_cam import duong_dan_cham_cam
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.file_cam import duong_dan_tu_lenh
from tram.tu_dong.khoa import NHAN_LY_DO, VIEC, ly_do_chan
from tram.tu_dong.luu import TamDung, TrangThaiTuDong

DU = replace(MAC_DINH, tu_merge=True, tu_deploy=True, lenh_deploy="d.sh", lenh_kiem_song="k.sh", lenh_lui="l.sh")
TD = TamDung("dai-ca/dashboard", "2026-10-18T02:00:00Z", "")


def _tt(cd=DU, du_an=None, tram=None):
    return TrangThaiTuDong(cd, "7", du_an, tram)


def test_du_dieu_kien_thi_khong_chan():
    for viec in VIEC:
        assert ly_do_chan(_tt(), viec=viec, bat_ghi=True, estop_bat=False) == []


def test_thu_tu_ly_do_estop_truoc_cong_tac_sau():
    tat = _tt(MAC_DINH, TD, TD)
    assert ly_do_chan(tat, viec="merge", bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat"]
    assert ly_do_chan(tat, viec="deploy", bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_deploy_tat", "thieu_lenh"]


def test_tung_cong_tac_chi_chan_viec_cua_no():
    assert ly_do_chan(_tt(replace(DU, tu_merge=False)), viec="deploy", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, tu_deploy=False)), viec="merge", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, lenh_lui="")), viec="merge", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, lenh_lui="")), viec="deploy", bat_ghi=True, estop_bat=False) == ["thieu_lenh"]


def test_deploy_tay_duoc_khi_tam_dung_khoa_khi_estop():
    """D97: nút Deploy của Đại ca bấm được khi dự án (hay toàn trạm) tạm dừng, công tắc tắt; khoá khi Estop."""
    tt = _tt(replace(DU, tu_merge=False, tu_deploy=False), TD, TD)
    assert ly_do_chan(tt, viec="deploy_tay", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(tt, viec="deploy_tay", bat_ghi=True, estop_bat=True) == ["estop"]
    assert ly_do_chan(_tt(MAC_DINH), viec="deploy_tay", bat_ghi=False, estop_bat=False) == ["bat_ghi", "thieu_lenh"]


def test_viec_la_va_nhan_du():
    with pytest.raises(ValueError):
        ly_do_chan(_tt(), viec="xoa", bat_ghi=True, estop_bat=False)
    assert set(NHAN_LY_DO) == {"estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat",
                               "tu_deploy_tat", "thieu_lenh"}


GOC = "/Users/Shared/repo-rn"                                        # gốc repo đáng tin của bên gọi (giả)
CO = {"scripts/deploy.sh": "file", "deploy/cau-hinh.yml": "file", "deploy": "dir", "scripts": "dir"}


def _repo(tok: str) -> tuple[str, str] | None:
    """Callback mẫu như TM-2/TM-3 dựng (hợp đồng D89): nhận token nguyên văn, chuẩn hoá từ gốc repo; ngoài gốc (kể cả
    thoát bằng `..`) hay chính gốc → None; có trong repo → (đường dẫn tương đối, loại)."""
    p = posixpath.normpath(tok if tok.startswith("/") else posixpath.join(GOC, tok))
    rel = p[len(GOC) + 1:] if p.startswith(GOC + "/") else ""
    return (rel, CO[rel]) if rel in CO else None


def test_duong_dan_cam_tu_ba_lenh():
    """Scenario "Agent sửa script deploy": file trong repo mà lệnh nhắc tới → mẫu cấm; thư mục → `thu-muc/**`. Tập
    bắt buộc (Codex C2): bên gọi kiểm nó KHÔNG kèm `cho_phep` — như dòng cuối."""
    cd = replace(MAC_DINH, lenh_deploy="sh ./scripts/deploy.sh --cau-hinh=deploy/cau-hinh.yml",
                 lenh_kiem_song="curl -fsS https://x.vn/song", lenh_lui="./deploy lui")
    them = duong_dan_tu_lenh(cd, _repo)
    assert them == ("deploy/**", "deploy/cau-hinh.yml", "scripts/deploy.sh")
    assert duong_dan_cham_cam(["scripts/deploy.sh", "deploy/a/b.sh", "src/app.py"], them=them) == [
        "deploy/a/b.sh", "scripts/deploy.sh"]


@pytest.mark.parametrize("lenh,mong", [
    (f"{GOC}/scripts/deploy.sh", ("scripts/deploy.sh",)),
    (f"bash --tep={GOC}/scripts/deploy.sh", ("scripts/deploy.sh",)),
    (f"{GOC}/deploy/../scripts/deploy.sh", ("scripts/deploy.sh",)),
    ("sh scripts/../deploy/cau-hinh.yml", ("deploy/cau-hinh.yml",)),
    (f"make -C {GOC}/deploy", ("deploy/**",)),
])
def test_duong_dan_tuyet_doi_hoac_vong_trong_repo_bi_cam(lenh, mong):
    """Codex Q1: gọi thẳng `/…/repo/scripts/deploy.sh` (hay vòng qua `..` mà vẫn trong repo) vẫn bảo vệ file đó."""
    assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy=lenh), _repo) == mong


@pytest.mark.parametrize("lenh", ["/Users/Shared/tram-deploy/deploy.sh", f"{GOC}-khac/scripts/deploy.sh",
                                  "sh ../scripts/deploy.sh", f"sh {GOC}/../repo-cu/scripts/deploy.sh", f"sh {GOC}",
                                  "~/deploy.sh", "sh scripts/*.sh", "sh -x", "sh 'thieu nhay", ""])
def test_bo_qua_token_ngoai_repo_hoac_la(lenh):
    """Tuyệt đối ngoài repo, `..` thoát gốc, chính gốc repo → callback trả None; `~`, glob, cờ, rỗng → không hỏi."""
    nhin = []
    assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy=lenh),
                             lambda p: nhin.append(p) or _repo(p)) == ()
    assert not any(not p or p.startswith(("~", "-")) or set(p) & set("*?[") for p in nhin)


def test_token_nguyen_van_toi_callback():
    """Hợp đồng D89: `file_cam` không tự bỏ đường tuyệt đối hay `..` — callback (biết gốc repo) quyết."""
    nhin = []
    duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy="/x/a.sh ../b.sh --f=/y/c ./d"), lambda p: nhin.append(p))
    assert nhin == ["/x/a.sh", "../b.sh", "/y/c", "./d"]


def test_ket_qua_callback_la_bi_bo():
    """Callback trả dạng lạ (gốc rỗng, tuyệt đối, `..`, chưa chuẩn hoá, loại khác) → không sinh mẫu nào."""
    for kq in [("", "dir"), ("/etc/x", "file"), ("../x", "file"), ("a/./b", "file"), ("a", "link"), "a", ("a",)]:
        assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy="a"), lambda p, kq=kq: kq) == ()
