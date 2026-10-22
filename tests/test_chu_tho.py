"""Lệnh phía tài khoản trạm cho máy thợ (spec 3 §5.1, §7.3; Q15) — KHÔNG chạy sudo/launchctl/sysadminctl thật."""
import io
import plistlib
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import in_ke_hoach
from tram.chu.cai_dat_tho import DAEMON, lap_ke_hoach_tho
from tram.chu.kiem_cach_ly import kiem_cach_ly
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.phieu.kho import mo_kho_phieu
from tram.phieu.may import xac_thuc_may
from tram.tho.kiem_am import KetQuaThamDo


def ke_hoach(**kw):
    return lap_ke_hoach_tho(uv="/opt/homebrew/bin/uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho",
                            khe={"claude-1": "tram-k-b-claude-1", "claude-2": "tram-k-b-claude-2"},
                            co_che="user", kiem=tu_cach_ly("user:tram-kiem"),
                            thu_muc_kiem=Path("/Users/Shared/tram-kiem"), quan_sat=HeGia().quan_sat, **kw)


def test_ke_hoach_user_moi_khe_sudoers_launchd(tram_home_tam):
    kh = ke_hoach()
    sud = kh.tep[tram_home_tam / "cai-dat-tho" / "tram-tho.sudoers"].decode()
    assert "tram-tho ALL=(tram-k-b-claude-1,tram-k-b-claude-2) NOPASSWD:SETENV: ALL" in sud
    assert "hung ALL=(tram-kiem)" not in sud and "(root)" not in sud              # D159: chỉ Uq chạy kiểm
    pl = plistlib.loads(kh.tep[tram_home_tam / "cai-dat-tho" / "vn.tram.tho.plist"])
    assert pl["UserName"] == "tram-tho" and pl["ProgramArguments"][-3:] == ["tram", "tho", "chay"]
    buoc = [m for m, _ in kh.buoc]                                       # 3c R2: tài nguyên đi qua sổ
    assert sum("sudo sysadminctl -addUser" in x for x in buoc) == 4
    sud_b = next(x for x in buoc if x.startswith("[tạo] tep /etc/sudoers.d/tram-tho:"))
    assert sud_b.index("sudo visudo -cf") < sud_b.index("sudo install -m 0440")
    assert [" ".join(x) for x in kh.lenh] == ["sudo launchctl bootout system/vn.tram.tho",
                                              f"sudo launchctl bootstrap system {DAEMON}"]
    assert "CHƯA CHỐT" in in_ke_hoach(kh) and "nhan-token" in in_ke_hoach(kh)
    with pytest.raises(ValueError):
        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="h", quan_ly="q", khe={}, co_che="ca-hai")


def test_cai_dat_tho_khong_dong_y_thi_khong_lam_gi(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
    args = SimpleNamespace(khe=["claude-1=tram-k-b-claude-1"], quan_ly="tram-tho", co_che="sandbox", dong_y=False,
                           chi_tho=False, giu_tat=False)
    assert lenh_tho._cai_dat_tho(args) == 1 and "Không làm gì" in capsys.readouterr().out


def test_cap_token_may_chi_vao_ong(monkeypatch, capsys):
    tty = io.StringIO()
    tty.isatty = lambda: True
    monkeypatch.setattr("sys.stdout", tty)
    assert lenh_tho._cap_token_may(SimpleNamespace(may_id="B", dong_y=True)) == 2 and tty.getvalue() == ""
    ong = io.StringIO()
    monkeypatch.setattr("sys.stdout", ong)
    assert lenh_tho._cap_token_may(SimpleNamespace(may_id="B", dong_y=False)) == 1 and ong.getvalue() == ""
    assert lenh_tho._cap_token_may(SimpleNamespace(may_id="B", dong_y=True)) == 0
    with closing(mo_kho_phieu()) as kho:
        assert xac_thuc_may(kho, ong.getvalue().strip()) == "B"


def test_kiem_cach_ly_du_bo_duoi_sudo_va_canh_bao_kenh_header(tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("dai_ca_logins: [dai-ca@x]\nten_may_b: b.ts.net\n"
                                                 "cach_ly: {db_nghiep_vu: ['127.0.0.1:3306'],\n"
                                                 "          tram_kiem: user:tram-kiem}\n")
    da = {}

    def chay_td(ds, *, boc, env, kill):
        da["boc"], da["ten"] = boc(["/bin/cat", "x"]), [t.ten for t in ds]
        return [KetQuaThamDo(t.ten, "API" not in t.ten, "mã 0") for t in ds]
    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], chay_td=chay_td, xac_minh=lambda *a: 600)
    assert ma == 1 and "header GIẢ ĐƯỢC" in van_ban and "[CHUYỂN] rac: kiểm cách ly khe bằng `tram tho kiem`" in van_ban
    assert da["boc"] == tu_cach_ly("user:tram-kiem").boc_lenh(["/bin/cat", "x"])      # đúng argv của kiểm lại (3c)
    assert "kết nối DB nghiệp vụ 127.0.0.1:3306" in da["ten"] and "[ĐỎ] user:tram-kiem — API Duyệt" in van_ban
    assert kiem_cach_ly([], doc_pk=lambda: None)[1] == 1
    van_ban, ma = kiem_cach_ly(["user:tram-k-1"], doc_pk=lambda: None)                 # D54: chỉ khe → chưa kiểm gì
    assert ma == 1 and "[CHUYỂN] user:tram-k-1" in van_ban and "Chưa có principal kiểm lại" in van_ban
