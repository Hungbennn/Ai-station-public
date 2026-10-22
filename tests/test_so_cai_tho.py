"""Sổ cài đặt v2 (lát 3c R2, Codex F02; R4 review đợt 5): journal chỉ ghi thêm, đuôi dở được cắt (giữ bằng chứng) TRƯỚC
khi nối, ghi đủ bytes, khoá cài/gỡ; đối soát khi crash; định danh user UID + GeneratedUID, nhà thuộc UID của user.
Không dscl/sudo thật — `HeGia`, `tmp_path`."""
import json
import os

import pytest

from he_gia import HeGia
from tram.chu import nhat_ky
from tram.chu.dinh_danh import khop
from tram.chu.so_cai_tho import SoCai, SoCaiDangBan, doi_soat

DU_DINH = '{"v": 2, "id": "a1", "su": "du_dinh", "kieu": "user", "ten": "u", "mong": {"ten_day_du": "tram u a1"}}\n'


def test_ghi_them_trang_thai_la_ban_ghi_cuoi(tmp_path):
    so = SoCai(tmp_path / "so.jsonl")
    so.du_dinh("a1", "user", "tram-kiem", {"ten_day_du": "tram tram-kiem a1"})
    so.ket("a1", "da_tao", dinh_danh={"uid": 502, "guid": "G1"})
    so.du_dinh("b2", "tep", "/etc/x", {"sha256": "h"})
    m = so.muc()
    assert (m["a1"].su, m["a1"].dinh_danh["guid"], m["b2"].su) == ("da_tao", "G1", "du_dinh")
    assert so.co_ghi("tep", "/etc/x") and not so.co_ghi("user", "khac")
    assert [x.id for x in so.da_tao("user", "tram-kiem")] == ["a1"]


def test_dong_cuoi_ghi_do_bi_bo_dong_hong_thi_tu_choi(tmp_path):
    so = SoCai(tmp_path / "so.jsonl")
    so.du_dinh("a1", "user", "u", {})
    with open(so.p, "a") as f:
        f.write('{"v": 2, "id": "a1", "su": "da_t')                   # crash giữa lúc ghi: dòng cuối không có \n
    assert so.muc()["a1"].su == "du_dinh"
    for hong in ('khong-phai-json\n', '{"v": 2, "id": "zz", "su": "da_go"}\n', '{"v": 1, "id": "a1"}\n'):
        so.p.write_text('{"v": 2, "id": "a1", "su": "du_dinh", "kieu": "user", "ten": "u", "mong": {}}\n' + hong)
        with pytest.raises(ValueError, match="hỏng"):
            so.muc()


@pytest.mark.parametrize("duoi", [b'{"v": 2, "id": "a1", "su": "da_t', b'{"v": 2, "id": "a1", "ly_do": "t\xe1\xba',
                                  b'{"v": 2, "id": "a1", "su": "khong_tao"}'])
def test_duoi_do_bi_cat_giu_bang_chung_roi_moi_noi(tmp_path, duoi):
    """R4: du_dinh hoàn chỉnh + đuôi dở (ASCII, UTF-8 dở, JSON đủ mà thiếu \\n) → đối soát nối vào DÒNG MỚI."""
    he, so = HeGia(), SoCai(tmp_path / "so.jsonl")
    so.p.write_bytes(DU_DINH.encode() + duoi)
    he.them_user("u", "tram u a1")                                     # lệnh tạo đã chạy, crash lúc ghi da_tao
    assert so.muc()["a1"].su == "du_dinh" and doi_soat(so, he.quan_sat, khop) == 1
    du = so.p.read_bytes()
    assert du.startswith(DU_DINH.encode()) and du.endswith(b"\n")
    assert [json.loads(d)["su"] for d in du.decode().splitlines()] == ["du_dinh", "da_tao"]
    assert (tmp_path / "so.jsonl.duoi-hong").read_bytes() == duoi + b"\n"
    so.ket("a1", "da_go")
    assert so.muc()["a1"].su == "da_go" and doi_soat(so, he.quan_sat, khop) == 0


def test_short_write_va_loi_giua_chung_khong_lam_hong_so(tmp_path, monkeypatch):
    so, goc, lan = SoCai(tmp_path / "so.jsonl"), os.write, []

    def ghi_ngan(fd, b):                                               # mỗi lần chỉ ghi 7 bytes
        return goc(fd, b[:7])
    monkeypatch.setattr(nhat_ky.os, "write", ghi_ngan)
    so.du_dinh("a1", "user", "u", {"ten_day_du": "tram u a1"})
    assert so.muc()["a1"].su == "du_dinh"

    def het_cho(fd, b):                                                # ghi được 10 bytes rồi hết chỗ
        lan.append(1)
        if len(lan) > 1:
            raise OSError(28, "No space left on device")
        return goc(fd, b[:10])
    monkeypatch.setattr(nhat_ky.os, "write", het_cho)
    with pytest.raises(OSError):
        so.ket("a1", "da_tao", dinh_danh={"uid": 1, "guid": "G"})
    monkeypatch.setattr(nhat_ky.os, "write", goc)
    assert so.muc()["a1"].su == "du_dinh"                              # đuôi dở bị bỏ khi đọc
    so.ket("a1", "da_tao", dinh_danh={"uid": 1, "guid": "G"})
    assert so.muc()["a1"].dinh_danh == {"uid": 1, "guid": "G"} and so.p.read_bytes().count(b"\n") == 2


def test_khoa_so_chan_ghi_cua_lan_cai_go_khac(tmp_path):
    a, b = SoCai(tmp_path / "so.jsonl"), SoCai(tmp_path / "so.jsonl")
    with a.giu():
        a.du_dinh("a1", "user", "u", {})                               # cùng đối tượng: dùng lại khoá
        with pytest.raises(SoCaiDangBan, match="đang có cài/gỡ khác"):
            b.du_dinh("b2", "user", "v", {})
    b.du_dinh("b2", "user", "v", {})
    assert list(a.muc()) == ["a1", "b2"]


def test_doi_soat_crash_truoc_va_sau_lenh_tao(tmp_path):
    he, so = HeGia(), SoCai(tmp_path / "so.jsonl")
    he.them_user("sau-tao", "tram sau-tao c3")                        # lệnh đã chạy, crash trước da_tao
    he.them_user("co-san")                                             # có sẵn, RealName không mang mã
    for id_, u in (("a1", "truoc-tao"), ("c3", "sau-tao"), ("d4", "co-san")):
        so.du_dinh(id_, "user", u, {"ten_day_du": f"tram {u} {id_}"})
    assert doi_soat(so, he.quan_sat, khop) == 3 and doi_soat(so, he.quan_sat, khop) == 0
    m = so.muc()
    assert (m["a1"].su, m["c3"].su, m["d4"].su) == ("khong_tao", "da_tao", "khong_tao")
    assert m["c3"].dinh_danh["guid"] == he.user["sau-tao"]["guid"]


def test_khoa_giu_boi_tien_trinh_khac(tmp_path):
    import subprocess
    import sys
    p = tmp_path / "so.jsonl"
    giu = subprocess.Popen([sys.executable, "-c", "import sys, time; from tram.chu.so_cai_tho import SoCai\n"
                            f"with SoCai(__import__('pathlib').Path({str(p)!r})).giu():\n"
                            "    print('giu', flush=True); time.sleep(30)"], stdout=subprocess.PIPE, text=True)
    try:
        assert giu.stdout.readline().strip() == "giu"
        with pytest.raises(SoCaiDangBan):
            SoCai(p).du_dinh("a1", "user", "u", {})
    finally:
        giu.kill()
        giu.wait()
    assert not p.exists() or p.read_bytes() == b""
