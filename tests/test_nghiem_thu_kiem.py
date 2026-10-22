"""Harness nghiệm thu S6 (lát 3c — thay r47 T12; hợp đồng P1 H5): đúng chuỗi `kiem_lai` qua cổng lượt + `boc_luot`,
mỗi khẳng định là một lệnh kiểm. Test: `boc` đồng nhất, cổng/thu hồi giả — khẳng định cách ly phải ĐỎ ở đây (không có
hồ sơ Seatbelt), chỉ xanh dưới principal thật (G4). Kịch bản cài lịch THẬT chỉ được kiểm nội dung: harness từ chối nó
khi UID thực là người vận hành, TRƯỚC khi spawn bất cứ gì. KHÔNG crontab/at/launchctl/kill -1 thật."""
import getpass

import pytest

from tram.giao_viec import nghiem_thu_kiem as ntk
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, kich_ban_tai_sinh
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem(getpass.getuser(), ())                          # boc đồng nhất: argv chạy thẳng dưới user test
KD = {k: v for k, v in KHANG_DINH.items() if k != "khong-chay-cong-cu-lich"}   # test không exec crontab thật


def chay(tmp_path, **kw):
    (goc := tmp_path / "kiem").mkdir(exist_ok=True)
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[], ngu=lambda s: None)
    c.mo_lai()
    thu = []
    luot = lambda wt: lambda a: ["/usr/bin/env", f"HOME={wt}.nha", f"TMPDIR={wt}.nha/tmp/", *a]   # boc_luot bỏ hồ sơ
    ds = ntk.nghiem_thu(PK, goc, cong=c, boc_luot=luot, thu_hoi=lambda: thu.append(1), khang_dinh=KD,
                        dau_goc=tmp_path, **kw)
    return {x.muc: x.muc_do for x in ds}, ds, thu, goc


def test_harness_la_chu_dau_chay_du_chuoi_va_bao_do_khi_khong_co_ho_so(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()                     # dấu của chính lần nghiệm thu này (CLI cha tạo)
    m, ds, thu, goc = chay(tmp_path)
    assert {k: v for k, v in m.items() if v == "xanh"} == {f"chuỗi kiểm lại: kiem/{k}.sh": "xanh" for k in (
        "danh-tinh", "repo-mot-commit", "moi-truong-khong-thanh-git", "nha-moi")}
    assert m["chuỗi kiểm lại: kiem/khong-doc-kho-tram.sh"] == m["chuỗi kiểm lại: kiem/khong-ghi-ngoai-luot.sh"] == "do"
    assert m["dọn: gốc bản chép rỗng sau thu hồi theo UID"] == "do"   # tệp ghi lọt ra gốc còn đó
    assert thu == [1, 1, 1] and in_ket_qua(ds)[1] == 1 and not list(tmp_path.glob("tram-nghiem-thu-dau-*"))


def test_kich_ban_that_bi_tu_choi_duoi_nguoi_van_hanh_truoc_khi_spawn(tmp_path, monkeypatch):
    kb = kich_ban_tai_sinh(tmp_path / "dau")
    assert all(x in kb for x in ("| crontab -", "| at now", "launchctl submit", "launchctl bootstrap", "setsid"))
    monkeypatch.setattr(ntk, "kiem_lai", lambda *a, **kw: pytest.fail("không được chạy lượt nào"))
    with pytest.raises(ValueError, match="UID thực"):
        chay(tmp_path, tai_sinh=True)
    with pytest.raises(ValueError, match="UID thực"):                # khẳng định exec crontab thật cũng vậy
        ntk.nghiem_thu(PK, tmp_path / "kiem", cong=None, boc_luot=None, thu_hoi=None, dau_goc=tmp_path)
    with pytest.raises(ValueError, match="≥ 240"):
        chay(tmp_path, tai_sinh=True, cho=float("nan"), kich_ban=lambda dau: "exit 0\n")
    assert not list(tmp_path.glob("tram-nghiem-thu-*")) and not list((tmp_path / "kiem").iterdir())


def kb_gia(**ma) -> str:
    """Kịch bản GIẢ chỉ `echo`: dấu probe từng nguồn theo `ma` (None = có bắt đầu, không có kết — treo/quá hạn)."""
    dong = ["echo kich-ban-bat-dau"]
    for n, m in ma.items():
        dong += [f"echo probe:{n}:bat-dau", *([] if m is None else [f"echo probe:{n}:ket:{m}"])]
    return "\n".join([*dong, "exit 0", ""])


def test_tai_sinh_lot_thi_do_tung_nguon_va_dau_chay_sau_thu_hoi(tmp_path):
    ngu = []

    def lich_chay_trong_luc_cho(s):                                # một lịch "lọt" chạy trong lúc chờ → phải ĐỎ
        ngu.append(s)
        next(tmp_path.glob("tram-nghiem-thu-dau-*")).joinpath("cron").touch()
    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lich_chay_trong_luc_cho,
                     kich_ban=lambda dau: kb_gia(cron=0, at=126, submit=126, launchd=126, setsid=0))
    assert ngu == [300] and m["tái sinh: hồ sơ chặn cài cron"] == "do"
    assert m["tái sinh: hồ sơ chặn cài at"] == m["tái sinh: hồ sơ chặn cài launchd"] == "vang"   # thất bại ≠ bị chặn
    assert m["tái sinh: quan sát đóng cổng khi lịch lọt"] == "do"     # cổng giả không đóng
    assert m["tái sinh: tiến trình setsid bị thu hồi ở ra()"] == "xanh"  # ra() của cổng giả không ném
    assert m["tái sinh: không gì chạy sau thu hồi"] == "do" and m["tái sinh: lần kiểm sau đạt"] == "do"
    assert m["tái sinh: đủ bằng chứng S6"] == "do"


@pytest.mark.parametrize("ma, mong, ss", [
    ({}, ["do"] * 4, "do"),                                         # chỉ `kich-ban-bat-dau`: cũ là bốn nguồn XANH
    (dict(cron=127, at=127, submit=127, launchd=127, setsid=127), ["vang"] * 4, "vang"),    # không có lệnh
    (dict(cron=None, at=126, submit=126, launchd=126, setsid=0), ["do", "vang", "vang", "vang"], "xanh")])  # treo
def test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat(tmp_path, ma, mong, ss):
    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: kb_gia(**ma))
    assert [m[f"tái sinh: hồ sơ chặn cài {n}"] for n in ("cron", "at", "submit", "launchd")] == mong
    assert m["tái sinh: tiến trình setsid bị thu hồi ở ra()"] == ss
    assert m["tái sinh: đủ bằng chứng S6"] == "do" and in_ket_qua(ds)[1] == 1


def test_kich_ban_that_moi_nguon_mot_khoi_probe(tmp_path):
    kb = kich_ban_tai_sinh(tmp_path / "dau")
    for n in ("cron", "at", "submit", "launchd", "setsid"):
        assert kb.count(f"echo probe:{n}:bat-dau;") == kb.count(f"echo probe:{n}:ket:$ma )") == 1
    assert "-da-cai" not in kb and kb.startswith("echo kich-ban-bat-dau\n") and kb.endswith("sleep 20\nexit 0\n")


def test_dong_ly_do_mang_byte_la_khong_vao_ket_qua_harness(tmp_path):
    """B01: kịch bản (hay mã agent) tự in `ly-do:` mang byte lạ + stderr — kết quả chỉ có mã thuộc `LY_DO`."""
    kb = kb_gia(cron=126, at=126, submit=126, launchd=126, setsid=0).replace(
        "echo probe:at:ket:126", "echo 'ly-do:at:BIMAT_OUT'\necho BIMAT_ERR >&2\necho probe:at:ket:126")
    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: kb)
    assert m["tái sinh: hồ sơ chặn cài at"] == "vang" and "BIMAT" not in in_ket_qua(ds)[0]
    assert "lý do khong-ro" in next(x.chi_tiet for x in ds if x.muc == "tái sinh: hồ sơ chặn cài at")


def test_tai_sinh_khong_thay_dau_bat_dau_thi_khong_xanh_gi(tmp_path):
    m, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: "exit 0\n")   # cổng đóng/không chạy
    assert m["tái sinh: lượt cài lịch đã chạy"] == "do"
    assert not any(k.startswith("tái sinh:") and v != "do" for k, v in m.items())
