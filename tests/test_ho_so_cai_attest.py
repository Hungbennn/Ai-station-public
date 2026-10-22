"""V2-5 (dot7-Q04): hồ sơ Seatbelt đã cài phải ĐÚNG TỪNG BYTE bản sinh lại từ manifest root của installer — không tìm
hai chuỗi. Tệp thật trong tmp_path; chủ/quyền/loại do `lstat`/`fstat` GIẢ trả (root:wheel) — không chmod/chown/sudo."""
import os
import json
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import ho_so_cai
from tram.tho.quyen_kiem import manifest_ho_so

THU_MUC_ROOT = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_uid=0)


class StatGia:
    """`lstat` thư mục cha mặc định root 0755; `fstat` theo inode: mặc định root 0644, `sai` đổi riêng từng tệp."""
    def __init__(self, cha: dict | None = None, tep: dict | None = None):
        self.cha, self.tep = cha or {}, tep or {}

    def lstat(self, p):
        return self.cha.get(Path(p), THU_MUC_ROOT)

    def fstat(self, fd):
        that = os.fstat(fd)
        for p, (quyen, chu) in self.tep.items():
            if os.stat(p).st_ino == that.st_ino:
                return SimpleNamespace(st_mode=stat.S_IFMT(that.st_mode) | quyen, st_uid=chu)
        return SimpleNamespace(st_mode=stat.S_IFMT(that.st_mode) | 0o644, st_uid=0)


@pytest.fixture
def cai(tmp_path, tram_home_tam):
    """Bản cài giả: (hồ sơ, manifest, gốc) sinh bởi CÙNG hàm installer dùng."""
    goc = (tmp_path / "kiem").resolve()
    hs, mf = manifest_ho_so(tram_home_tram=tram_home_tam, nha_quan_ly=Path("/Users/tram-tho"), goc=goc, cong=[7700])
    (d := tmp_path / "usr-local-tram").mkdir()
    (d / "tram-kiem.sb").write_bytes(hs)
    (d / "tram-kiem.sb.json").write_bytes(mf)
    return d / "tram-kiem.sb", d / "tram-kiem.sb.json", goc


def kiem(cai, st=None, goc=None):
    st = st or StatGia()
    ho_so_cai(goc or cai[2], cai[0], cai[1], lstat=st.lstat, fstat=st.fstat)


def test_ban_cai_dung_tung_byte_thi_dat(cai):
    kiem(cai)


@pytest.mark.parametrize('phien_ban', [1, 2])
def test_ban_cai_phien_ban_cu_dong_cong(cai, phien_ban):
    mf = json.loads(cai[1].read_bytes())
    cai[1].write_text(json.dumps(mf | {'phien_ban': phien_ban}))
    with pytest.raises(LoiBanChep, match='khác phiên bản'):
        kiem(cai)


@pytest.mark.parametrize("sua", [
    lambda b: b.replace(b"(allow signal)", b"(allow network*)"),                 # sửa một allow
    lambda b: b + b"(allow file-write*)\n",                                       # mở rộng, vẫn đủ hai chuỗi cũ
    lambda b: b + b"; (deny default) BIMAT\n",                                    # comment giả deny
    lambda b: b.replace(b"(deny job-creation)\n", b""),
    lambda b: b.replace(b'(deny file-read* (subpath "/Users"))\n', b''),
    lambda b: b.replace(b"\n", b"\r\n"),
    lambda b: b"x" * 70000])
def test_ho_so_lech_mot_byte_bi_tu_choi_khong_lo_noi_dung(cai, sua):
    cai[0].write_bytes(sua(cai[0].read_bytes()))
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt|quá lớn") as e:
        kiem(cai)
    assert "BIMAT" not in str(e.value) and "allow" not in str(e.value)


def test_ba_dong_hai_chuoi_cu_khong_con_du(cai, tram_home_tam):
    cai[0].write_text(f'(version 1)\n(deny default)\n(deny file-read* (subpath "{tram_home_tam}"))\n(allow network*)\n')
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt"):
        kiem(cai)


def test_goc_hoac_tram_home_doi_thi_phai_cai_lai(cai, tmp_path, monkeypatch):
    with pytest.raises(LoiBanChep, match="khác cấu hình hiện hành"):
        kiem(cai, goc=(tmp_path / "goc-moi").resolve())                           # đường gốc cũ trong manifest
    monkeypatch.setenv("TRAM_HOME", str(tmp_path / "tram-home-khac"))
    with pytest.raises(LoiBanChep, match="khác cấu hình hiện hành"):
        kiem(cai)


def test_manifest_thieu_hong_hoac_cu_hon_ho_so(cai, tram_home_tam):
    hs, mf, goc = cai
    _, mf_khac = manifest_ho_so(tram_home_tram=tram_home_tam, nha_quan_ly=Path("/Users/quan-ly-cu"), goc=goc,
                                cong=[7700])
    mf.write_bytes(mf_khac)                         # cài hỏng giữa hai tệp: manifest của lần cài khác, hồ sơ mới
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt"):
        kiem(cai)
    mf.write_bytes(b'{"BIMAT": 1}')
    with pytest.raises(LoiBanChep, match="sai dạng") as e:
        kiem(cai)
    assert "BIMAT" not in str(e.value)
    mf.unlink()                                     # cài dừng sau hồ sơ, trước manifest
    with pytest.raises(LoiBanChep, match="không đọc được"):
        kiem(cai)


def test_symlink_hoac_khong_phai_tep_thuong(cai, tmp_path):
    that = tmp_path / "ho-so-that.sb"
    that.write_bytes(cai[0].read_bytes())
    cai[0].unlink()
    cai[0].symlink_to(that)
    with pytest.raises(LoiBanChep, match="không đọc được"):
        kiem(cai)                                   # O_NOFOLLOW: symlink bị từ chối dù đích đúng từng byte
    cai[0].unlink()
    cai[0].mkdir()
    with pytest.raises(LoiBanChep, match="sai chủ/quyền/loại"):
        kiem(cai)


@pytest.mark.parametrize("tep, quyen, chu", [(0, 0o644, 501), (0, 0o664, 0), (0, 0o646, 0), (1, 0o644, 501),
                                             (1, 0o666, 0)])
def test_chu_hoac_quyen_root_sai(cai, tep, quyen, chu):
    with pytest.raises(LoiBanChep, match="sai chủ/quyền/loại"):
        kiem(cai, StatGia(tep={cai[tep]: (quyen, chu)}))


@pytest.mark.parametrize("st", [SimpleNamespace(st_mode=stat.S_IFDIR | 0o775, st_uid=0),
                                SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_uid=501),
                                SimpleNamespace(st_mode=stat.S_IFLNK | 0o755, st_uid=0)])
def test_thu_muc_cha_ghi_duoc_hoac_khong_cua_root(cai, st):
    with pytest.raises(LoiBanChep, match="thư mục cha"):
        kiem(cai, StatGia(cha={cai[0].parent: st}))
