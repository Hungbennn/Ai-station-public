"""Gỡ và cài lại sau crash (lát 3c, R4/R5 review đợt 5): đuôi sổ dở → đối soát → đọc → gỡ → đọc → cài lại; nhà giữ
lại (-keepHome) không bị nhận cho user mới khác UID; `--xoa-nha`; gỡ khi đang cài thì không làm gì. `HeGia` — KHÔNG
sudo/sysadminctl/launchctl thật."""
import json
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from test_go_cai_dat_tho import cai, ke_hoach_go
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat


def test_duoi_do_doi_soat_doc_go_doc_cai_lai(tram_home_tam, tmp_path):
    he = HeGia()

    def chay(c, check=False, **kw):
        r = he.chay(c, check=check)
        if "-addUser tram-k-1" in " ".join(c):
            raise SystemExit("mất điện khi đang ghi da_tao")
        return r
    with pytest.raises(SystemExit):
        cai(tmp_path, he, co_che="user", chay=chay)
    so = SoCai()
    i = next(m.id for m in so.muc().values() if m.ten == "tram-k-1")
    with open(so.p, "ab") as f:                                       # da_tao ghi dở, cắt giữa ký tự UTF-8
        f.write(f'{{"v": 2, "id": "{i}", "su": "da_tao", "dinh_danh": {{"ten_day_du": "tr'.encode() + "ạ".encode()[:2])
    du = so.p.read_bytes()
    hoan_chinh = du[:du.rfind(b"\n") + 1]
    thuc_hien(ke_hoach_go(he), chay=he.chay)                          # đọc (bỏ đuôi) → đối soát → gỡ
    du = so.p.read_bytes()
    assert du.startswith(hoan_chinh) and all(json.loads(d) for d in du.decode().splitlines())
    assert he.user == {} and {m.su for m in so.muc().values()} == {"da_go"} and ke_hoach_go(he).buoc == []
    assert so.p.with_name("so-cai.jsonl.duoi-hong").read_bytes().endswith("ạ".encode()[:2] + b"\n")
    cai(tmp_path, he, co_che="user")                                  # cài lại từ đầu, sổ cũ vẫn đọc được
    assert set(he.user) == {"tram-k-1", "tram-kiem", "tram-tho"} and len(ke_hoach_go(he).buoc) > 1


@pytest.mark.parametrize("dung_lai_uid", [False, True])
def test_cai_lai_sau_khi_giu_nha_khong_nhan_nha_cu(tram_home_tam, tmp_path, dung_lai_uid):
    he = HeGia(dung_lai_uid=dung_lai_uid)              # macOS dùng lại UID trống nhỏ nhất: nhà cũ "khớp UID"
    cai(tmp_path, he, co_che="user")
    thuc_hien(ke_hoach_go(he), chay=he.chay)                          # mặc định giữ nhà
    cu, he.lenh = dict(he.chu), []
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        cai(tmp_path, he, co_che="user")                              # từ chối ngay lúc lập kế hoạch
    assert he.lenh == [] and he.chu == cu and he.user == {}           # không tạo user, không chown nhà cũ
    thuc_hien(ke_hoach_go(he, xoa_nha=True), chay=he.chay)
    assert not any(p.startswith("/Users/") for p in he.thu_muc) and ke_hoach_go(he, xoa_nha=True).buoc == []
    cai(tmp_path, he, co_che="user")
    assert all(he.chu[f"/Users/{u}"] == he.user[u]["uid"] for u in ("tram-k-1", "tram-tho"))


def test_xoa_nha_khong_xoa_nha_la_va_khong_dung_var_empty(tram_home_tam, tmp_path):
    he = HeGia()
    he.hong.add("createhomedir -c -u tram-k-1")
    with pytest.raises(LoiCaiDat):
        cai(tmp_path, he, co_che="user")
    he.hong.clear()
    he.them_nha("tram-k-1", 777)                                      # nhà lạ xuất hiện, sổ ghi khong_tao
    thuc_hien(ke_hoach_go(he, xoa_nha=True), chay=he.chay)
    assert he.chu["/Users/tram-k-1"] == 777 and not any("rm -rf /Users/tram-k-1" in x for x in he.lenh)
    assert not any("/var/empty" in x for x in he.lenh if "-addUser" not in x)
    assert all("-keepHome" in x for x in he.lenh if "-deleteUser" in x)


def test_go_xoa_nha_ghi_da_go_va_chay_lai_rong(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    kh = ke_hoach_go(he, xoa_nha=True)
    assert [m.split(":")[0] for m, _ in kh.buoc if m.startswith("Gỡ nha")] == [   # 3C-D6: hồ sơ cài cả cơ chế user
        "Gỡ nha /Users/tram-k-1 nếu còn đúng định danh trong sổ",
        "Gỡ nha /Users/tram-tho nếu còn đúng định danh trong sổ"]
    thuc_hien(kh, chay=he.chay)
    assert {m.su for m in SoCai().muc().values()} == {"da_go"} and ke_hoach_go(he, xoa_nha=True).buoc == []


def test_go_khi_dang_cai_thi_khong_lam_gi(tram_home_tam, tmp_path, capsys):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    with SoCai().giu():
        assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err and set(he.user) == {"tram-k-1", "tram-kiem", "tram-tho"}


def test_khoa_truoc_khi_xem_so(tram_home_tam, capsys):
    with SoCai().giu():                                               # lần cài đang chờ dong-y, sổ chưa có dòng nào
        assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err


def test_ten_user_khong_go_duoc_thi_tu_choi_cai(tram_home_tam, tmp_path):
    from pathlib import Path

    from tram.chu.cai_dat_tho import lap_ke_hoach_tho
    he = HeGia()
    with pytest.raises(ValueError, match="tram.tho"):
        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram.tho", co_che="user", khe={},
                         quan_sat=he.quan_sat, chay=he.chay)
    assert he.lenh == []


def test_thu_muc_kiem_khong_go_duoc_thi_giu_user_va_chu_doi_thi_khong_giu(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he, co_che="user")
    he.hong.add(f"/bin/rm -rf {tmp_path}/kiem")
    thuc_hien(ke_hoach_go(he, bao, xoa_nha=True), chay=he.chay)
    assert "tram-kiem" in he.user and any("thư mục của nó chưa gỡ được" in b for b in bao)   # không mồ côi UID
    he.hong.clear()
    he.chu[f"{tmp_path}/kiem"] = 999                                   # chủ đổi (UID cũ bị dùng lại…)
    with pytest.raises(LoiCaiDat, match="không chown"):
        cai(tmp_path, he, co_che="user")
