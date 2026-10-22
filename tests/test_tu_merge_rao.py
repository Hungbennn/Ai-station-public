"""TM-2, Codex Q2 + C2 (D89 tại cửa merge; hợp đồng D89 TM-1 vòng 2): `loai_trong_repo` — token NGUYÊN VĂN → đường
dẫn trong repo theo cây Git (commit của PR hoặc nhánh chính), không thoát gốc qua `..`/symlink; `cham_file_lenh` —
diff chạm tập file ba lệnh dùng → `file_lenh`; không đọc được cây → `file_lenh_loi`. Git cục bộ thật, không mạng."""
import os
from dataclasses import replace
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tu_merge_rao import cham_file_lenh, doc_tep, loai_trong_repo
from tram.tu_dong.cai_dat import MAC_DINH

DA = DuAn("hr-codex", Path("/r"), None, {})


def _pr(tmp_path):
    """PR tạo `scripts/deploy.sh`, symlink `ngoai` → `/etc`, xoá `kiem.sh` (còn ở nhánh chính)."""
    k = dung_kho(tmp_path)
    k.day("tram/hr-1", {}, tu=k.main)
    os.symlink("/etc", k.dev / "ngoai")
    c = k.day("tram/hr-1", {"scripts/deploy.sh": "echo 1\n", "kiem.sh": None})
    fetch(k.kho)
    return k, c


def test_loai_trong_repo_theo_cay_git(tmp_path):
    k, c = _pr(tmp_path)
    loai = loai_trong_repo(k.kho, (DA.duong_dan, k.kho), (c, "origin/main"))
    assert loai("scripts/deploy.sh") == ("scripts/deploy.sh", "file")           # chỉ có ở commit PR (tạo mới)
    assert loai("./kiem.sh") == ("kiem.sh", "file")                              # PR xoá, nhánh chính còn
    assert loai("scripts") == ("scripts", "dir") and loai("Scripts/Deploy.SH") == ("scripts/deploy.sh", "file")
    assert loai("/r/src/tom_tat.py") == ("src/tom_tat.py", "file")              # tuyệt đối theo gốc dự án
    assert loai(f"{k.kho}/src/../kiem.sh") == ("kiem.sh", "file")                 # tuyệt đối theo kho kiểm
    for token in ("ngoai/passwd", "ngoai/../kiem.sh"):
        with pytest.raises(OSError, match="symlink"):
            loai(token)
    for ngoai in ("../kiem.sh", "src/../../kiem.sh", "/etc/passwd", "/rr/kiem.sh", "/r", ".", "scripts/khong.sh"):
        assert loai(ngoai) is None, ngoai


def test_cham_file_lenh(tmp_path):
    k, c = _pr(tmp_path)
    tep = doc_tep(k.kho, DA, c)

    def cham(**lenh):
        return cham_file_lenh(replace(MAC_DINH, **lenh), k.kho, DA, c, tep)
    assert cham() == () and cham(lenh_deploy="sh src/tom_tat.py") == ()        # chưa khai; file lệnh dùng không đổi
    assert cham(lenh_lui="sh ./kiem.sh") == ("file_lenh",)                       # PR xoá file lệnh dùng
    assert cham(lenh_kiem_song="make -C scripts") == ("file_lenh",)              # thư mục lệnh dùng
    assert cham(lenh_deploy="sh /r/ngoai/x.sh") == ("file_lenh_loi",)                # PR thêm symlink lệnh đi qua
    assert cham_file_lenh(replace(MAC_DINH, lenh_deploy="sh x.sh"), k.kho, DA, c, None) == ()   # đã `diff_loi`
    assert cham_file_lenh(replace(MAC_DINH, lenh_deploy="sh x.sh"), k.kho, DA, "f" * 40, tep) == ("file_lenh_loi",)

@pytest.mark.parametrize("lenh", ["sh lien-ket/deploy.sh", "sh lien-ket/../scripts/deploy.sh"])
def test_lenh_qua_symlink_khong_mien_dich_cua_link(tmp_path, lenh):
    k = dung_kho(tmp_path)
    os.symlink("scripts", k.dev / "lien-ket")
    goc = k.day("main", {"scripts/deploy.sh": "echo 1\n"}, tu=k.main)
    c = k.day("tram/hr-1", {"scripts/deploy.sh": "echo 2\n"}, tu=goc)
    fetch(k.kho)
    tep = doc_tep(k.kho, DA, c)
    assert "lien-ket" not in tep and "scripts/deploy.sh" in tep
    cd = replace(MAC_DINH, lenh_deploy=lenh)
    assert cham_file_lenh(cd, k.kho, DA, c, tep) == ("file_lenh_loi",)

