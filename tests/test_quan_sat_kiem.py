"""3C-D3 (C01): quan sát bổ trợ do TRẠM tự chạy (không qua sudo, không tin lời `tram-kiem`): tiến trình theo UID thực
và hiệu lực; tệp của `tram-kiem` ở MỌI độ sâu trong vùng ghi-chung (ca Codex: tệp con trong thư mục cha 0777 của user
khác — `_sot -maxdepth 1` cũ bỏ sót). Thấy hoặc không quan sát được → ném (cổng đóng). `chay` giả, không chạy lệnh."""
import subprocess
from types import SimpleNamespace

from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.ngoai_le_uid import con_uid
from pathlib import Path

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import GOC_CHUNG, cron_at, goc_rong, tep_ngoai, tien_trinh

GOC = Path("/Users/Shared/tram-kiem")


def gia(*kq):
    goi, con = [], list(kq)

    def chay(argv, **kw):
        goi.append(argv)
        ma, ra = con.pop(0)
        return subprocess.CompletedProcess(argv, ma, ra, "")
    return chay, goi


def test_tien_trinh_tram_tu_dem_ca_uid_thuc_va_hieu_luc():
    tien_trinh("tram-kiem", chup=lambda: [], tim=lambda ten: SimpleNamespace(pw_uid=503),
               loc=lambda uid, chup, **kw: con_uid(uid, chup, ban="24G90", **kw))


@pytest.mark.parametrize("uid,ruid", [(503, 0), (0, 503), (503, 503)])
def test_tien_trinh_con_thi_nem(uid, ruid):
    with pytest.raises(LoiBanChep, match="còn tiến trình|còn 1"):
        tien_trinh("tram-kiem", chup=lambda: [TienTrinh(42, 2, 42, uid, ruid)],
                   tim=lambda ten: SimpleNamespace(pw_uid=503),
                   loc=lambda uid, chup, **kw: con_uid(uid, chup, ban="24G90", **kw))


def test_tep_ngoai_quet_moi_do_sau_bo_qua_goc_va_thu_muc_khong_doc_duoc():
    chay, goi = gia((0, ""))
    tep_ngoai("tram-kiem", GOC, chay=chay)
    a = goi[0]
    assert a[:2] == ["/usr/bin/find", "-x"] and a[2:2 + len(GOC_CHUNG)] == list(GOC_CHUNG)
    assert "-maxdepth" not in a and a[-4:] == ["-o", "-user", "tram-kiem", "-print"]
    assert ["-path", str(GOC), "-o", "-type", "d", "!", "-user", "tram-kiem", "!", "-perm", "-0005"] == \
        a[a.index("(") + 1:a.index(")")] and a[a.index(")") + 1] == "-prune"


@pytest.mark.parametrize("kq, khop", [((0, "/Users/Shared/chung-0777/sau/hon/tep\n"), "1 mục"),
                                      ((1, ""), "không quan sát"), ((0, "\n"), "không quan sát")])
def test_tep_ngoai_thay_tep_sau_trong_thu_muc_cha_khac_owner_hoac_find_loi(kq, khop):
    with pytest.raises(LoiBanChep, match=khop):
        tep_ngoai("tram-kiem", GOC, chay=gia(kq)[0])


def test_ten_user_la_bi_tu_choi_truoc_khi_chay():
    with pytest.raises(ValueError):
        tien_trinh("-x", chup=lambda: pytest.fail("không được chụp"))



def test_goc_rong_thay_ban_chep_hoac_nha_con_sot(tmp_path):
    goc_rong(tmp_path)
    (tmp_path / "g-1-ab.nha").mkdir()                              # nhà lượt (hoặc bản chép bị dời vào đó) còn sót
    with pytest.raises(LoiBanChep, match="1 mục"):
        goc_rong(tmp_path)
    with pytest.raises(LoiBanChep, match="không đọc"):
        goc_rong(tmp_path / "khong-co")


def test_cron_at_sach_khong_go_gi():
    pk = tu_cach_ly("user:tram-kiem")
    goi, kq = [], [(1, "", "crontab: no crontab for tram-kiem\n"), (0, "", ""), (0, "", "")]

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *kq.pop(0))
    cron_at(pk, chay=chay)
    assert goi == [pk.boc_lenh(["/usr/bin/crontab", "-l"]), pk.boc_lenh(["/usr/bin/atq"]),
                   ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]
    assert not any("-r" in a or "atrm" in " ".join(a) for a in goi)        # quan sát không xoá dấu vết


@pytest.mark.parametrize("kq", [[(0, "* * * * * sh x\n", "")], [(1, "", "crontab: tmp/tmp.1: Permission denied\n")],
                                [(1, "", "no crontab for tram-kiem"), (0, "3 Fri Oct 16 a tram-kiem\n", "")],
                                [(1, "", "no crontab for tram-kiem"), (0, "", ""), (0, "/usr/lib/cron/jobs/a01\n", "")],
                                [(1, "", "no crontab for tram-kiem"), (2, "", "")]])
def test_cron_at_co_lich_hoac_khong_xac_nhan_duoc_thi_nem(kq):
    con = list(kq)
    with pytest.raises(LoiBanChep):
        cron_at(tu_cach_ly("user:tram-kiem"), chay=lambda a, **kw: subprocess.CompletedProcess(a, *con.pop(0)))
