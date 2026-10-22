"""R5 review đợt 5: biên nhận user (`addUser`) KHÁC hoàn tất nhà (`createhomedir`) — mỗi thứ một bản ghi sổ. Chạy lại
chỉ làm phần còn thiếu, giữ UID/GUID; nhà có sẵn mà không thuộc user của trạm là nhà lạ → từ chối, không ghi đè;
`addUser` tự tạo nhà thì nhận theo đúng UID. R4: đang có lần gỡ giữ khoá sổ thì cài không làm gì. `HeGia` — KHÔNG
sysadminctl/createhomedir/sudo thật."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.cai_dat_tho import lap_ke_hoach_tho
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.giao_viec.principal_kiem import tu_cach_ly


def ke_hoach(tmp_path, he):
    return lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che="user",
                            khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly("user:tram-kiem"),
                            thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=he.chay)


def su(kieu: str) -> dict[str, str]:
    return {m.ten: m.su for m in SoCai().muc().values() if m.kieu == kieu}        # bản ghi mới nhất của mỗi tên


def mat_dien():
    raise SystemExit("mất điện ngay trước createhomedir")


@pytest.mark.parametrize("hong", ["lenh-loi", "crash"])
def test_hong_giua_addUser_va_createhomedir_chay_lai_chi_tao_nha(tram_home_tam, tmp_path, hong):
    he = HeGia()
    if hong == "lenh-loi":
        he.hong.add("createhomedir -c -u tram-k-1")
    else:
        he.truoc["createhomedir -c -u tram-k-1"] = mat_dien
    with pytest.raises((LoiCaiDat, SystemExit)):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    truoc = dict(he.user["tram-k-1"])
    assert su("user")["tram-k-1"] == "da_tao" and "/Users/tram-k-1" not in he.thu_muc
    he.hong.clear(), he.truoc.clear(), he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)                   # chạy lại: chỉ bước còn thiếu
    assert he.user["tram-k-1"] == truoc and not any("-addUser" in x for x in he.lenh)
    assert "sudo createhomedir -c -u tram-k-1" in he.lenh and he.chu["/Users/tram-k-1"] == truoc["uid"]
    assert su("nha") == {"/Users/tram-k-1": "da_tao", "/Users/tram-tho": "da_tao"}


def test_nha_co_san_truoc_user_la_nha_la_tu_choi_cai(tram_home_tam, tmp_path):
    he = HeGia()
    he.them_nha("tram-k-1", 777)                     # nhà cũ (keepHome của user đã xoá), sổ không ghi
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        ke_hoach(tmp_path, he)
    assert he.lenh == [] and not SoCai().p.exists() and he.chu["/Users/tram-k-1"] == 777


def test_nha_la_xuat_hien_sau_khi_user_cua_tram_da_co_thi_khong_nhan(tram_home_tam, tmp_path):
    he = HeGia()
    he.hong.add("createhomedir -c -u tram-k-1")
    with pytest.raises(LoiCaiDat):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.hong.clear()
    he.them_nha("tram-k-1", 777)                     # có người khác tạo, chủ không phải UID của user trạm
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        ke_hoach(tmp_path, he)
    assert he.chu["/Users/tram-k-1"] == 777 and su("nha")["/Users/tram-k-1"] == "khong_tao"


def test_addUser_tu_tao_nha_thi_nhan_dung_uid(tram_home_tam, tmp_path):
    he = HeGia(add_tao_nha=True)                     # S6 đo: sysadminctl có tự tạo nhà hay không
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert not any(x.startswith("sudo createhomedir") for x in he.lenh)
    nha = [m for m in SoCai().muc().values() if m.kieu == "nha"]
    assert {m.su for m in nha} == {"da_tao"} and all(m.dinh_danh["uid"] == m.mong["uid"] for m in nha)


def test_dang_go_thi_cai_dat_tho_khong_lam_gi(tram_home_tam, tmp_path, monkeypatch, capsys):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text(f"cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path}/kiem\n")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
    monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=True)
    with SoCai().giu():
        assert lenh_tho._cai_dat_tho(args) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err


def test_crash_sau_addUser_tu_tao_nha_chay_lai_chi_lam_phan_thieu(tram_home_tam, tmp_path):
    he = HeGia(add_tao_nha=True)

    def chay(c, check=False, **kw):
        r = he.chay(c, check=check)
        if "-addUser tram-k-1" in " ".join(c):
            raise SystemExit("mất điện sau addUser, trước da_tao")
        return r
    with pytest.raises(SystemExit):
        thuc_hien(lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che="user",
                                   khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly("user:tram-kiem"),
                                   thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=chay), chay=chay)
    truoc = dict(he.user["tram-k-1"])
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)                   # du_dinh dở + nhà tự tạo: vẫn nhận đúng
    assert he.user["tram-k-1"] == truoc and su("user")["tram-k-1"] == "da_tao"
    assert su("nha")["/Users/tram-k-1"] == "da_tao"


def test_thu_muc_kiem_cua_nguoi_khac_sau_du_dinh_do_khong_bi_nhan(tram_home_tam, tmp_path):
    he = HeGia()
    he.truoc[f"/bin/mkdir -m 0755 {tmp_path}/kiem"] = mat_dien
    with pytest.raises(SystemExit):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.truoc.clear()
    he.thu_muc[f"{tmp_path}/kiem"], he.chu[f"{tmp_path}/kiem"] = 99, 777    # người khác tạo đúng đường dẫn đó
    with pytest.raises(LoiCaiDat):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert su("thu_muc")[f"{tmp_path}/kiem"] == "khong_tao" and he.chu[f"{tmp_path}/kiem"] == 777
