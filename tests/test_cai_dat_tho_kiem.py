"""`tram chu cai-dat-tho` (lát 3c): phần `tram-kiem` theo D22 (không dòng sudoers root, `tram-kiem` tự tạo thư mục gốc
bản chép) và cài CÓ SỔ theo R2 (du_dinh trước lệnh, da_tao kèm định danh sau quan sát; thứ có sẵn không bị nhận).
KHÔNG sudo/sysadminctl/launchctl thật — `HeGia` thay hệ thống."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import in_ke_hoach, thuc_hien
from tram.chu.cai_dat_tho import SUDOERS, lap_ke_hoach_tho
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI, ho_so_tu_manifest


def ke_hoach(tmp_path, he=None, chuoi="user:tram-kiem", co_che="user", khe=None):
    he = he or HeGia()
    return lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che=co_che,
                            khe=khe or {"claude-1": "tram-k-1"}, kiem=tu_cach_ly(chuoi), thu_muc_kiem=tmp_path / "kiem",
                            db_nghiep_vu=("127.0.0.1:3306",), quan_sat=he.quan_sat, chay=he.chay)


def test_sudoers_chi_runas_tram_kiem_va_tram_kiem_tu_tao_thu_muc(tram_home_tam, tmp_path):
    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
    sud = kh.tep[soan / "tram-tho.sudoers"].decode()
    assert "hung ALL=(tram-kiem)" not in sud and "root" not in sud
    buoc = [m for m, _ in kh.buoc]
    assert f"[tạo] thu_muc {tmp_path}/kiem: sudo -u tram-kiem /bin/mkdir -m 0755 {tmp_path}/kiem" in buoc
    assert "D22" in in_ke_hoach(kh) and "go-cai-dat-tho" in in_ke_hoach(kh) and buoc[0].startswith("Đối soát")


def test_co_che_user_cung_cai_ho_so_kiem_root_0644(tram_home_tam, tmp_path):
    """3C-D6: mọi lệnh của lượt chạy trong `HO_SO_KIEM` ở CẢ HAI cơ chế (`boc_luot`) — thiếu hồ sơ thì `ho_so_cai` đóng
    cổng, nên cơ chế `user` cũng phải cài. Sudoers của `user` không ghim hồ sơ (`ALL` dưới tram-kiem, D40)."""
    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
    hs = kh.tep[soan / HO_SO_KIEM.name].decode()
    assert "(deny default)" in hs and f'(subpath "{tram_home_tam}")' in hs and '(param "LUOT")' in hs
    buoc = " | ".join(m for m, _ in kh.buoc)
    assert f"install -d -o root -g wheel -m 0755 {THU_MUC_CAI}" in buoc
    assert f"install -m 0644 -o root -g wheel {soan / HO_SO_KIEM.name} {HO_SO_KIEM}" in buoc
    assert "chup-nen-lich" not in in_ke_hoach(kh)                     # lệnh r47 không còn trong 3c hiện hành


def test_sandbox_cai_ho_so_co_dinh_va_ghim_sudoers(tram_home_tam, tmp_path):
    kh, soan = ke_hoach(tmp_path, chuoi="sandbox:tram-kiem", co_che="sandbox"), tram_home_tam / "cai-dat-tho"
    hs = kh.tep[soan / HO_SO_KIEM.name].decode()
    assert f'(subpath "{tram_home_tam}")' in hs and '(subpath "/Users/tram-tho/.tram")' in hs
    assert "hung ALL=(tram-kiem)" not in kh.tep[soan / "tram-tho.sudoers"].decode()
    buoc = " | ".join(m for m, _ in kh.buoc)
    assert f"install -d -o root -g wheel -m 0755 {THU_MUC_CAI}" in buoc
    assert f"install -m 0644 -o root -g wheel {soan / HO_SO_KIEM.name} {HO_SO_KIEM}" in buoc


def test_lech_co_che_trung_user_khe_hoac_thieu_thu_muc_la_loi(tmp_path):
    with pytest.raises(ValueError, match="khác --co-che"):
        ke_hoach(tmp_path, chuoi="sandbox:tram-kiem")
    with pytest.raises(ValueError, match="user riêng"):
        ke_hoach(tmp_path, chuoi="sandbox:tram-k-1", co_che="sandbox")
    with pytest.raises(ValueError, match="thu_muc_kiem"):
        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="q", khe={}, co_che="user",
                         kiem=tu_cach_ly("user:tram-kiem"), quan_sat=HeGia().quan_sat)


def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp_path):
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    muc = SoCai().muc().values()
    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 14    # 3 user, 2 nhà, 2 thư mục, hồ sơ + manifest,
    #                                                                   sudoers, daemon
    assert sorted(m.ten for m in muc if m.kieu == "nha") == ["/Users/tram-k-1", "/Users/tram-tho"]
    assert "-home /var/empty" in next(x for x in he.lenh if "-addUser tram-kiem" in x)    # C01: không nhà ghi được
    assert not any("createhomedir -c -u tram-kiem" in x for x in he.lenh)
    u = next(m for m in muc if m.kieu == "user" and m.ten == "tram-kiem")
    assert u.dinh_danh == he.user["tram-kiem"] and he.user["tram-kiem"]["ten_day_du"] == f"tram tram-kiem {u.id}"
    assert he.lenh.index(f"sudo visudo -cf {tram_home_tam}/cai-dat-tho/tram-tho.sudoers") < next(
        i for i, x in enumerate(he.lenh) if x.endswith(str(SUDOERS)))


def test_user_co_san_khong_do_tram_tao_thi_tu_choi_cai(tram_home_tam, tmp_path):
    he = HeGia()
    he.them_user("tram-kiem")
    with pytest.raises(ValueError, match="không cài đè"):
        ke_hoach(tmp_path, he)
    assert not SoCai().p.exists() and he.lenh == []


def test_user_xuat_hien_giua_chung_thi_khong_nhan_la_cua_tram(tram_home_tam, tmp_path):
    he = HeGia()
    kh = ke_hoach(tmp_path, he)
    he.truoc["sysadminctl -addUser tram-kiem"] = lambda: he.them_user("tram-kiem")     # có sẵn ngay trước addUser
    with pytest.raises(LoiCaiDat):
        thuc_hien(kh, chay=he.chay)
    su = {m.ten: m.su for m in SoCai().muc().values() if m.kieu != "nhom"}
    assert su == {"tram-k-1": "da_tao", "tram-kiem": "khong_tao"} and he.user["tram-kiem"]["ten_day_du"] == "người khác"


def test_cai_lai_giu_user_cua_tram_thay_file_doi_noi_dung(tram_home_tam, tmp_path):
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he, khe={"claude-1": "tram-k-1", "claude-2": "tram-k-2"}), chay=he.chay)
    assert [x for x in he.lenh if "-addUser" in x] == [x for x in he.lenh if "-addUser tram-k-2" in x] != []
    sud = [m for m in SoCai().muc().values() if m.ten == str(SUDOERS)]
    assert [m.su for m in sud] == ["da_tao", "da_tao"] and sud[0].dinh_danh != sud[1].dinh_danh


def test_lenh_doc_cau_hinh_khong_con_co_tram_kiem(tram_home_tam, tmp_path, monkeypatch, capsys):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text(f"cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path}/kiem\n")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=False,
                           chi_tho=False, giu_tat=False)
    assert lenh_tho._cai_dat_tho(args) == 1 and f"{tmp_path}/kiem" in capsys.readouterr().out
    assert lenh_tho._cai_dat_tho(SimpleNamespace(**{**vars(args), "co_che": "sandbox"})) == 2
    assert "khác --co-che" in capsys.readouterr().err


def test_manifest_cai_sau_ho_so_cung_so_va_sinh_lai_dung_ho_so(tram_home_tam, tmp_path):
    """V2-5: manifest (input bộ sinh + phiên bản + digest) cài root:wheel 0644 SAU hồ sơ, cùng sổ cài."""
    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
    m, hs = ho_so_tu_manifest(kh.tep[soan / MANIFEST_KIEM.name])
    assert hs == kh.tep[soan / HO_SO_KIEM.name] and m["nha_quan_ly"] == "/Users/tram-tho"
    assert (m["tram_home"], m["goc"]) == (str(tram_home_tam), str(tmp_path / "kiem"))
    buoc = [x for x, _ in kh.buoc]
    i_hs = next(i for i, x in enumerate(buoc) if x.endswith(f"{soan / HO_SO_KIEM.name} {HO_SO_KIEM}"))
    assert buoc[i_hs + 1].endswith(f"install -m 0644 -o root -g wheel {soan / MANIFEST_KIEM.name} {MANIFEST_KIEM}")


def test_cai_hong_giua_ho_so_va_manifest_thi_so_ghi_dung_phan_da_cai(tram_home_tam, tmp_path):
    he = HeGia()
    he.hong.add(f"install -m 0644 -o root -g wheel {tram_home_tam / 'cai-dat-tho' / MANIFEST_KIEM.name}")
    with pytest.raises(LoiCaiDat):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    su = {m.ten: m.su for m in SoCai().muc().values() if m.kieu != "nhom"}
    assert su[str(HO_SO_KIEM)] == "da_tao" and su[str(MANIFEST_KIEM)] == "khong_tao"
    assert str(HO_SO_KIEM) in he.tep and str(MANIFEST_KIEM) not in he.tep    # runtime: thiếu manifest → cổng đóng
