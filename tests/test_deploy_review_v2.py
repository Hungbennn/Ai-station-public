"""Phản ví dụ review vòng 2: biên HTTP/runner giả, Git và bàn giao thật; không gọi mạng/OS runner."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from git_gia import ghi, git
from test_lenh_tho import wt, phieu, ban_giao
from tram.tho.ket_thuc import ket_thuc_xong
from tram.tu_dong.cai_dat import MAC_DINH, sang_api

LOI_CAM = "Không xác minh được file lệnh tự động — không chạy kiểm; chờ trạm kiểm lại"


def ket_thuc(wt, tmp_path, monkeypatch, khach):
    import tram.tho.ket_thuc as kt
    from tram.cau_hinh.du_an_giao import CauHinhGiao
    p, bg = phieu(), ban_giao()
    pc = SimpleNamespace(p=p, wt=wt, principal=SimpleNamespace(boc=lambda a: a, kill_nhom=lambda *a: None))
    ch = SimpleNamespace(path_cli="/usr/bin:/bin", thoi_gian_cho_kiem_giay=1, han_chot_dung_mem_phut=1)
    nc = SimpleNamespace(khach=khach, goc=tmp_path, ch=SimpleNamespace(tren_may_b=False, chay=ch))
    giao = CauHinhGiao(duong_dan_cam_cho_phep=("scripts/deploy.sh", "kiem.py", "link"))
    monkeypatch.setattr(kt, "nap_du_an", lambda _: SimpleNamespace(giao=giao))
    monkeypatch.setattr(kt, "luu_wip", lambda *a: None)
    monkeypatch.setattr(kt, "_day", lambda *a: "cong_bo")
    baocao = []
    monkeypatch.setattr(kt, "bao", lambda pc, nc, than, *a: baocao.append(than))
    def cam_runner(*a, **kw):
        pytest.fail("runner đã được gọi trước khi xác minh D89")
    monkeypatch.setattr("tram.kiem.lenh_tho.chay_mot_lenh", cam_runner)
    assert ket_thuc_xong(pc, nc, {"ban_giao": bg.model_dump(), "request_id": "v2"}) == "cong_bo"
    assert len(baocao) == 1 and baocao[0]["loai"] == "xong"
    assert baocao[0]["ban_giao"]["lenh_kiem"] == []
    assert baocao[0]["commit"] == git(wt, "rev-parse", "HEAD")
    return baocao[0]


class Khach:
    def __init__(self, ma=200, data=None, loi=None):
        self.ma, self.data, self.loi = ma, data, loi

    def goi(self, *a, **kw):
        assert kw == {"xac_thuc": False}
        if self.loi:
            raise self.loi
        return self.ma, self.data


@pytest.mark.parametrize("khach", [
    Khach(500, {"response": "noi-dung-khong-duoc-lo"}),
    Khach(loi=RuntimeError("noi-dung-khong-duoc-lo")),
    Khach(data={"cai_dat": {"lenh": {"deploy": "sh scripts/deploy.sh"}}}),
    Khach(data={"cai_dat": {**sang_api(MAC_DINH), "tu_deploy": "false"}}),
    Khach(data={"cai_dat": sang_api(replace(MAC_DINH, lenh_deploy="sh '"))}),
])
def test_v2_c2_loi_doc_cau_hinh_dung_truoc_runner(wt, tmp_path, monkeypatch, khach):
    ghi(wt, {"scripts/deploy.sh": "exit 0\n"}, "sửa script được miễn")
    kq = ket_thuc(wt, tmp_path, monkeypatch, khach)
    assert LOI_CAM in kq["loi_ban_giao"]
    assert "noi-dung-khong-duoc-lo" not in str(kq)


def test_v2_c2_chi_cau_hinh_hop_le_rong_tra_tap_rong(wt):
    from tram.deploy.cam import cam_tu_lenh_tho
    assert cam_tu_lenh_tho(Khach(data={"cai_dat": sang_api(MAC_DINH)}), "hr", wt, "main") == ()


@pytest.mark.parametrize("doi", ["link", "dich", "link_cham_cham", "hoa_thuong"])
def test_v2_q1_duong_lenh_khong_duoc_lot_runner(wt, tmp_path, monkeypatch, doi):
    (wt / "scripts").mkdir()
    (wt / "scripts/deploy.sh").write_text("exit 0\n")
    (wt / "link").symlink_to("scripts", target_is_directory=True)
    git(wt, "add", ".")
    git(wt, "commit", "-qm", "cây gốc có link nội bộ")
    git(wt, "update-ref", "refs/remotes/origin/main", "HEAD")
    if doi == "link":
        (wt / "link").unlink()
        (wt / "link").symlink_to("./scripts", target_is_directory=True)
        git(wt, "add", ".")
        git(wt, "commit", "-qm", "đổi link, giữ đích")
    else:
        ghi(wt, {"scripts/deploy.sh": "exit 1\n"}, "đổi đích, giữ link")
    token = {"link_cham_cham": "link/../scripts/deploy.sh", "hoa_thuong": "Scripts/Deploy.SH"}.get(
        doi, "link/deploy.sh")
    cd = sang_api(replace(MAC_DINH, lenh_deploy=f"sh {token}"))
    kq = ket_thuc(wt, tmp_path, monkeypatch, Khach(data={"cai_dat": cd}))
    if doi == "hoa_thuong":
        assert "Diff chạm đường dẫn cấm: scripts/deploy.sh" in kq["loi_ban_giao"]
    else:
        assert LOI_CAM in kq["loi_ban_giao"]


@pytest.mark.parametrize("token", ["link/deploy.sh", "link/../scripts/deploy.sh"])
def test_v2_q1_doc_symlink_trong_commit_khong_theo_checkout(wt, tmp_path, token):
    from tram.deploy.cam import loai_trong_cay
    (wt / "link").symlink_to("scripts", target_is_directory=True)
    ghi(wt, {"scripts/deploy.sh": "exit 0\n"})
    bare = tmp_path / "kiem.git"
    git(tmp_path, "clone", "-q", "--bare", str(wt), str(bare))
    with pytest.raises(OSError, match="symlink"):
        loai_trong_cay((wt, bare), bare, "HEAD")(token)
