"""H1 (V2-6a, bs-863.18; dot7-C02): ống `git archive | tar` của bản chép có chủ HAI đầu và một hạn chung. Đích hết hạn,
lỗi, thoát sớm, không khởi chạy được hay không xác nhận thu hồi → nguồn vẫn bị thu hồi, kết quả không công nhận, byte
môi trường không vào ngoại lệ. Tiến trình thật chỉ là `git archive` + `python -c` của user test trong tmp_path. Ưu tiên
trạng thái chưa thu hồi và ngân sách hạn còn lại (B02): `test_ong_chep_uu_tien.py`."""
import signal
import subprocess
import sys
import time

import pytest

from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import chay, m  # noqa: F401 — fixture `m` dùng chung
from test_vong_doi import _song
from tram.giao_viec import ban_chep, cay_kiem, kiem_lai, ong_chep
from tram.giao_viec.ban_chep import CayKhacNguon, LoiBanChep, chep_ban, nhan_moi_truong
from tram.giao_viec.git_kiem import fetch
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable
TAR = "/usr/bin/tar"


@pytest.fixture
def ong(tmp_path, monkeypatch):
    """Kho có archive 2 MiB (lớn hơn bộ đệm ống: nguồn còn đang ghi khi đích dừng); ghi lại Nhom của nguồn."""
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"lon.txt": "x" * (2 << 20)}, tu=k.main)
    fetch(k.kho)
    monkeypatch.setattr(ban_chep, "THOI_GIAN", 1.0)
    nguon = []
    goc = ong_chep.nguon_archive
    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: nguon.append(goc(*a, **kw)) or nguon[-1])
    return k, sha, tmp_path / "kiem" / "g-1-ab", nguon


def boc_tar(thay: list[str]):
    return lambda a: thay if a[0] == TAR else a


def test_nguon_archive_la_nhom_rieng_kill_cuc_bo_va_co_chu(tmp_path):
    k, goi, chu = dung_kho(tmp_path), [], []
    cay_kiem.nguon_archive(k.kho, k.main, chu=chu, khoi=lambda a, **kw: goi.append((a, kw)))
    (a, kw), = goi
    assert a[-3:] == ["archive", "--format=tar", k.main] and kw["kill"] is kill_cuc_bo and kw["chu"] is chu
    assert (kw["stdin"], kw["stdout"], kw["stderr"]) == (subprocess.DEVNULL, subprocess.PIPE, subprocess.DEVNULL)


@pytest.mark.parametrize("dich, loi", [([PY, "-c", "import time; time.sleep(60)"], subprocess.TimeoutExpired),
                                       ([PY, "-c", "import sys; sys.exit(3)"], LoiBanChep),
                                       (["/khong-co/tar"], OSError)])
def test_dich_qua_han_loi_hoac_khong_chay_thi_nguon_van_bi_thu_hoi(ong, dich, loi):
    k, sha, wt, nguon = ong
    t0 = time.monotonic()
    with pytest.raises(loi):
        chep_ban(k.kho, sha, wt, boc=boc_tar(dich))
    assert time.monotonic() - t0 < 15
    n, = nguon
    assert n.p.returncode is not None and not _song(n.p.pid) and n.p.stdout.closed


def test_nguon_treo_khi_dich_xong_thi_het_phan_han_con_lai_roi_thu_hoi(ong, monkeypatch):
    k, sha, wt, nguon = ong
    treo = lambda *a, chu, **kw: nguon.append(khoi_chay([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo,
                                                        chu=chu, stdout=subprocess.PIPE)) or nguon[-1]
    monkeypatch.setattr(ong_chep, "nguon_archive", treo)
    t0 = time.monotonic()
    with pytest.raises(LoiBanChep, match=r"git archive \(mã None\)"):
        chep_ban(k.kho, sha, wt, boc=boc_tar([PY, "-c", "pass"]))
    assert time.monotonic() - t0 < 10 and not _song(nguon[0].p.pid)


def test_dich_khong_xac_nhan_thu_hoi_thanh_loi_ban_chep_nguon_van_thu_hoi(ong, monkeypatch):
    k, sha, wt, nguon = ong
    that = ban_chep.chay_gioi_han

    def chay(argv, **kw):
        if argv[0] == TAR:
            raise LoiThuHoi("tar: không xác nhận thu hồi")
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)
    with pytest.raises(LoiBanChep, match="không xác nhận thu hồi"):        # tick chỉ bắt OSError, không RuntimeError
        chep_ban(k.kho, sha, wt, boc=lambda a: a)
    assert not _song(nguon[0].p.pid)


def test_moi_truong_qua_han_khong_lo_byte_env(ong):
    k, sha, wt, _ = ong
    (env := wt.parent / "env.testing").parent.mkdir(parents=True)
    env.write_text("DB_PASSWORD=BI_MAT_ENV\n")
    with pytest.raises(subprocess.TimeoutExpired) as e:
        nhan_moi_truong(k.kho, sha, wt, env, ".env.testing", boc=boc_tar([PY, "-c", "import time; time.sleep(60)"]))
    assert "BI_MAT_ENV" not in f"{e.value}{e.value!r}" and e.value.output is None and e.value.stderr is None


def test_kiem_lai_truyen_kill_cua_principal_cho_ban_chep(m, monkeypatch):
    goi = []

    def kill(g, s):
        pass

    def chep(*a, **kw):
        goi.append(kw["kill"])
        raise CayKhacNguon("giả")
    monkeypatch.setattr(kiem_lai, "chep_ban", chep)
    monkeypatch.setattr(kiem_lai, "don_ban", lambda wt, **kw: goi.append(kw["kill"]))
    assert chay(m, {"kiem.sh": "exit 0\n"}, kill=kill).loi == "cay-khac-nguon" and goi == [kill, kill]


def test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi(tmp_path, monkeypatch):
    """Tiêm ngắt tại ranh giới Popen bằng handler đồng bộ; không phụ thuộc git hay lịch chạy OS."""
    import io
    from tram.kiem.ngat import term_thanh_ngat
    from tram.kiem import ngat

    goi, chu_nguon = [], []

    class P:
        pid, returncode = 4242, None
        stdin = stderr = None

        def __init__(self):
            self.stdout = io.BytesIO(b"archive-gia")

        def wait(self, timeout=None):
            if self.returncode is None:
                raise subprocess.TimeoutExpired("nguon-gia", timeout)
            return self.returncode

        def poll(self):
            return self.returncode

    p = P()

    def kill(pgid, sig):
        assert pgid == p.pid
        goi.append("thu-hoi")
        p.returncode = -sig

    def nguon(kho, commit, *, chu):
        chu_nguon.append(chu)
        def popen(a, **kw):
            assert kw["start_new_session"] is True and chu == []
            goi.append("spawn")
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
            return p
        return khoi_chay(["nguon-gia"], kill=kill, chu=chu, popen=popen, chup=lambda: [])

    def dich(*a, **kw):
        pytest.fail("đích không được chạy sau ngắt ở nguồn")

    monkeypatch.setattr(ong_chep, "nguon_archive", nguon)
    monkeypatch.setattr(ngat.signal, "raise_signal", lambda so: signal.getsignal(so)(so, None))
    try:
        with term_thanh_ngat(), pytest.raises(KeyboardInterrupt):
            ong_chep.chay_ong(tmp_path, "sha-gia", ["dich-gia"], chay=dich, han=1)
        assert goi == ["spawn", "thu-hoi"]
        assert len(chu_nguon[0]) == 1 and chu_nguon[0][0].p is p
        assert chu_nguon[0][0].ket_thu_hoi is True and p.returncode == -signal.SIGTERM
        assert p.stdout.closed
    finally:
        p.stdout.close()
