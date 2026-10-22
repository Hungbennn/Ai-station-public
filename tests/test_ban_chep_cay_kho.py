"""R7 (3C-C, sau review đối kháng): cấu hình RIÊNG của kho kiểm không đổi được bản chép (filter, ignorecase); tên NFD
giữ nguyên cây, tệp `._*` bị từ chối; cây lệch là lỗi tất định → `kiem_lai` trả `cay-khac-nguon`, vòng tick tạo
escalation, không ghi `kiem.lai`, không thử lại mãi. `git` THẬT trong `tmp_path`."""
import unicodedata

import pytest

from giao_viec_gia import bug, dung
from su_kien_gia import ds, sk
from test_ban_chep_cay import chep
from test_kich_ban_4a1 import PASS, bao, xin
from test_xet_xong import F, bg
from tram.giao_viec.ban_chep import CayKhacNguon
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick


def test_filter_rieng_cua_kho_kiem_thi_tu_choi(tmp_path):
    with pytest.raises(CayKhacNguon, match="filter"):
        chep(tmp_path, {".gitattributes": ("100644", b"*.txt filter=x\n"), "a.txt": ("100644", b"abc\n")},
             cau_hinh_kho=("filter.x.smudge=tr a-z A-Z",))


@pytest.mark.parametrize("blob, cau_hinh", [(b"x\n", ("core.ignorecase=true",)), (b"x\r\n", ())])
def test_thuoc_tinh_khop_phan_biet_hoa_thuong_ca_hai_phia(tmp_path, blob, cau_hinh):
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.TXT text eol=crlf\n"), "a.txt": ("100644", blob)},
              cau_hinh_kho=cau_hinh)                               # `*.TXT` không khớp `a.txt` ở cả archive lẫn add
    assert (wt / "a.txt").read_bytes() == blob


def test_ten_nfd_giu_nguyen_cay(tmp_path):
    chep(tmp_path, {unicodedata.normalize("NFD", "chào.txt"): ("100644", b"x")})    # `chep` so mã cây hai phía


def test_tep_appledouble_bi_tar_nuot_thi_tu_choi(tmp_path):
    with pytest.raises(CayKhacNguon):                               # bsdtar coi `._*` là metadata: cây lệch, không lọt
        chep(tmp_path, {"._ghi-chu": ("100644", b"khong phai metadata")})


def test_tick_cay_lech_tao_escalation_khong_ghi_kiem_lai(tmp_path):
    t = dung(tmp_path, bug())
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    t.k.day(p.repo.nhanh, {"a.txt": "x\r\n"}, tu=p.repo.cha)                  # blob CRLF đã theo dõi từ trước
    sha = t.k.day(p.repo.nhanh, {".gitattributes": "* text=auto\n", F: "x"})  # rồi mới thêm text=auto
    sk(t.kho, "giao.cong_bo", {"bead_id": p.bead_id, "luot": p.luot, "commit": sha, "ref": p.repo.nhanh})
    bao(t, p, "xong", commit=sha, ban_giao=bg(sha, luot=p.luot, lenh_kiem=PASS))
    mot_vong_tick(t.bo)
    assert moi_nhat(ds(t.kho), "kiem.lai") is None
    esc = [b for b in t.g.beads.values() if b.issue_type == "decision"]
    assert len(esc) == 1 and "cay-khac-nguon" in esc[0].description
    mot_vong_tick(t.bo)
    assert len([b for b in t.g.beads.values() if b.issue_type == "decision"]) == 1   # không tạo trùng
