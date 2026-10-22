"""§6.4: crash ở từng bước, phát lại hai lần không đổi số bản, lỗi một ký ức trong sự kiện ba ký ức."""
import threading

import pytest

from nho_gia import EmbedderGia, ky_uc
from tram.nho.ap_dung import ap_dung, luu_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import BuocGhi
from tram.nho.nhat_ky import NhatKy
from tram.su_kien.kho import KhoSuKien

E = EmbedderGia()


class Sap(RuntimeError):
    pass


class Hong:
    """Bọc một đối tượng: lần gọi thứ `lan` của `ten` ném Sap — trước (sau=False) hoặc sau khi chạy thật."""

    def __init__(self, that, ten, lan=1, sau=False):
        self._that, self._ten, self._lan, self._sau, self._dem = that, ten, lan, sau, 0

    def __getattr__(self, ten):
        ham = getattr(self._that, ten)
        if ten != self._ten:
            return ham

        def boc(*a, **kw):
            self._dem += 1
            if self._dem == self._lan and not self._sau:
                raise Sap(ten)
            kq = ham(*a, **kw)
            if self._dem == self._lan:
                raise Sap(ten)
            return kq
        return boc


@pytest.fixture
def mt(tmp_path):
    kho = KhoKyUc(tmp_path / "lancedb", so_chieu=E.so_chieu)
    for i in ("cu-1", "cu-2"):
        kho.them(ky_uc(i, vector=E.embed([i])[0]))
    return kho, KhoSuKien(tmp_path / "sk.db"), NhatKy(tmp_path / "nk.db")


def ke_hoach(nk, n=1, xoa=("cu-1",)):
    buoc = [BuocGhi(ky_uc(f"m-{i}", vector=E.embed([f"m-{i}"])[0]), xoa if i == 0 else ()) for i in range(n)]
    return luu_ke_hoach(nk, su_kien_id=42, phien_ban=1, du_an="x", bead_id="x-1", buoc=buoc)


def trang_thai(kho, sk, nk):
    return (kho.dem(), kho.dem("da_xoa = true"), len(sk.gan_day("x", "nho.ghi", 99)),
            len(sk.gan_day("x", "nho.gop", 99)), nk.moc(), nk.lay("42:1").trang_thai)


def test_ap_dung_binh_thuong(mt):
    kho, sk, nk = mt
    assert ap_dung(ke_hoach(nk), kho=kho, kho_sk=sk, nhat_ky=nk) == 1
    assert trang_thai(kho, sk, nk) == (3, 1, 1, 1, 42, "xong")
    ev = sk.gan_day("x", "nho.ghi", 1)[0]
    assert ev.bead_id == "x-1" and ev.tac_nhan == "tram/nho" and ev.du_lieu["pham_vi"] == "/du-an/x/cach-lam"
    assert sk.gan_day("x", "nho.gop", 1)[0].du_lieu == {"cu": ["cu-1"], "moi": "m-0"}


@pytest.mark.parametrize("dt, ten, sau", [
    ("kho", "xoa_mem", False), ("kho", "xoa_mem", True), ("kho", "them", True),
    ("sk", "ghi", True), ("nk", "danh_dau_buoc", True), ("nk", "hoan_tat", False)])
def test_crash_tung_buoc_roi_lam_tiep_tu_nhat_ky(mt, dt, ten, sau):
    kho, sk, nk = mt
    tt = ke_hoach(nk)
    hong = {"kho": kho, "sk": sk, "nk": nk}
    hong[dt] = Hong(hong[dt], ten, sau=sau)
    with pytest.raises(Sap):
        ap_dung(tt, kho=hong["kho"], kho_sk=hong["sk"], nhat_ky=hong["nk"])
    assert nk.moc() == 0 and [t.ma for t in nk.dang_do()] == ["42:1"]
    for _ in range(2):                                        # đối soát rồi phát lại thêm lần nữa
        for t in nk.dang_do():
            ap_dung(t, kho=kho, kho_sk=sk, nhat_ky=nk)
    ap_dung(nk.lay("42:1"), kho=kho, kho_sk=sk, nhat_ky=nk)
    assert trang_thai(kho, sk, nk) == (3, 1, 1, 1, 42, "xong")


def test_loi_ky_uc_thu_hai_trong_su_kien_ba_ky_uc(mt):
    kho, sk, nk = mt
    tt = ke_hoach(nk, n=3)
    with pytest.raises(Sap):
        ap_dung(tt, kho=Hong(kho, "them", lan=2), kho_sk=sk, nhat_ky=nk)
    assert kho.dem() == 3 and nk.moc() == 0 and nk.lay("42:1").buoc_xong == {"0"}
    assert ap_dung(nk.lay("42:1"), kho=kho, kho_sk=sk, nhat_ky=nk) == 2
    assert trang_thai(kho, sk, nk) == (5, 1, 3, 1, 42, "xong")


def test_phat_lai_ke_hoach_giu_ban_cu(mt):
    kho, sk, nk = mt
    ke_hoach(nk)
    tt = luu_ke_hoach(nk, su_kien_id=42, phien_ban=1, du_an="x", bead_id="x-1", buoc=[])
    assert len(tt.ke_hoach["buoc"]) == 1


def luong_khac_lay_duoc(khoa) -> bool:
    kq = []
    t = threading.Thread(target=lambda: kq.append(khoa.acquire(blocking=False) and (khoa.release() or True)))
    t.start()
    t.join()
    return kq[0]


def test_xoa_mem_va_them_trong_cung_mot_lan_giu_khoa(mt):
    kho, sk, nk = mt
    giu = []

    class GhiKhoa:                       # Q5: recall xen giữa không thấy lúc bản cũ đã xoá mà bản mới chưa ghi
        def __getattr__(self, ten):
            ham = getattr(kho, ten)
            if ten not in ("xoa_mem", "them"):
                return ham
            return lambda *a, **kw: giu.append((ten, not luong_khac_lay_duoc(kho.khoa))) or ham(*a, **kw)
    ap_dung(ke_hoach(nk), kho=GhiKhoa(), kho_sk=sk, nhat_ky=nk)
    assert giu == [("xoa_mem", True), ("them", True)]
