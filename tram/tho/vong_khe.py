"""Vòng của MỘT khe trong `tram tho chay` (spec 3 §6.2, §7.2): nhịp tim 30 giây kiêm xin việc (luồng nền, kể cả khi
đang chạy phiếu — mang `giao_id`/`luot`/`buoc_tho`/`han_muc`; `tiep_tuc: false` → `lenh` + dừng lần chạy), và vòng
chính nhận phiếu → `chay_phieu`. Khởi động: dọn theo UID của khe (gồm CLI mồ côi), bảo đảm `chay.xong {mo-coi}`;
chưa chứng minh được khe sạch → khe dừng ngay; phiếu đang giữ (`phieu.json`) chạy tiếp từ lần kế (3a-1 G12). Hạn
mức lúc rảnh đọc SAU khi gửi nhịp, dưới principal của khe (`han_muc_ranh`, bs-78r.10)."""
import threading
import time

from tram.duong_dan import doc_luc
from tram.kiem.vong_doi import LoiThuHoi
from tram.phieu.mo_hinh import Phieu
from tram.tho.cau_hinh import KheCauHinh
from tram.tho.han_muc_ranh import DocHanMucRanh
from tram.tho.hop_thu import HopThu
from tram.tho.khach import LoiKhachTram
from tram.tho.mo_coi_khe import don_mo_coi_khe, don_phieu_cu
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.phieu_chay import chay_phieu
from tram.tho.so_khe import SoKhe, TrangThaiPhieu, gio_utc
from tram.tho.theo_doi import DUNG_CUNG


class VongKhe:
    def __init__(self, nc: NguCanhTho, k: KheCauHinh):
        self.nc, self.k = nc, k
        self.so = SoKhe(nc.ch.may_id, k.ten, nc.goc)
        self.hop = HopThu(self.so.goc)
        self.khe_id = nc.ch.khe_id(k)
        self.lenh: str | None = None
        self.dung = threading.Event()
        self.buoc, self.pc = "ranh", None
        self.phieu_moi: TrangThaiPhieu | None = None
        self.da_xac_nhan = False
        self.han_giu = None
        self.hong = False                       # P1: CLI chưa xác nhận thu hồi → dừng khe (cả nhịp tim)
        self.han_muc = DocHanMucRanh(nc, k, self.khe_id, self.so)

    def khoi_dong(self) -> None:
        tt, self.hong = don_mo_coi_khe(self.nc, self.k, self.so, self.hop)
        self.hop.gui(self.nc.khach)
        self.phieu_moi = tt

    def nhip(self) -> dict | None:
        try:
            return self._gui_nhip()
        finally:
            self.hong |= self.han_muc.doc(self.pc is None and self.phieu_moi is None)

    def _gui_nhip(self) -> dict | None:
        than = {"khe_id": self.khe_id, "buoc_tho": self.buoc}
        p = self.pc.p if self.pc else (Phieu.model_validate(self.phieu_moi.phieu) if self.phieu_moi else None)
        if p is not None:
            than |= {"giao_id": p.giao_id, "luot": p.luot}
        if (hm := self.so.doc_han_muc()) is not None:
            than["han_muc"] = hm.model_dump()
        try:
            ma, kq = self.nc.khach.goi("POST", "/api/tho/nhip", than)
        except LoiKhachTram:
            return None
        self.hop.gui(self.nc.khach)
        if ma in (401, 403, 409):
            self.lenh = "thu-hoi"
            self.da_xac_nhan = False
            self.dung.set()
        if ma != 200:
            return kq
        if p is not None and kq.get("tiep_tuc") is False:
            self.lenh = kq.get("ly_do") or "thu-hoi"
            self.da_xac_nhan = True
            self.dung.set()
        elif p is not None and kq.get("tiep_tuc") is True and kq.get("han_giu"):
            self.han_giu = doc_luc(kq["han_giu"])
            self.da_xac_nhan = self.han_giu > self.nc.dong_ho()
        elif self.pc is None and self.phieu_moi is None and kq.get("phieu"):
            self.phieu_moi = TrangThaiPhieu(phieu=kq["phieu"], nhan_luc=gio_utc(self.nc.dong_ho()))
            self.so.luu_phieu(self.phieu_moi)
            self.han_giu = doc_luc(kq["phieu"]["han_giu"])
            self.da_xac_nhan = self.han_giu > self.nc.dong_ho()
        return kq

    def _vong_nhip(self, tat: threading.Event) -> None:
        while not tat.is_set() and not self.hong:
            self.nhip()
            toi = time.monotonic() + self.nc.chu_ky_nhip
            while not tat.is_set() and time.monotonic() < toi:
                if self.han_giu is not None and self.nc.dong_ho() >= self.han_giu:
                    self.lenh, self.da_xac_nhan = "thu-hoi", False
                    self.dung.set()
                tat.wait(min(1.0, max(0.0, toi - time.monotonic())))
        if self.lenh not in DUNG_CUNG:          # tắt `tram tho chay`: dừng CLI,
                                                # GIỮ phiếu để chạy tiếp khi khởi động lại
            self.lenh = "tat-tho"
        self.dung.set()

    def chay(self, tat: threading.Event) -> None:
        self.khoi_dong()
        nhip = threading.Thread(target=self._vong_nhip, args=(tat,), daemon=True, name=f"nhip-{self.khe_id}")
        nhip.start()
        while not tat.is_set() and not self.hong:
            if self.lenh in DUNG_CUNG and self.phieu_moi is not None:
                self.hong = not don_phieu_cu(self)
                if self.hong:
                    break
            if self.phieu_moi is None or not self.da_xac_nhan:
                tat.wait(0.2)
                continue
            tt = self.phieu_moi
            try:
                chay_phieu(self.nc, self, tt)
            except LoiThuHoi:                   # P1: tiến trình dưới principal có thể còn sống → dừng khe
                print("Không xác nhận thu hồi tiến trình của khe; dừng khe — khởi động lại sẽ dọn mồ côi")
                self.hong = True
                break
            except Exception:                   # noqa: BLE001 — lỗi một phiếu không giết vòng của khe
                print("Lỗi xử lý phiếu; giữ sổ để đối soát, không in dữ liệu credential")
            self.phieu_moi = None
            self.han_giu, self.da_xac_nhan = None, False
            self.lenh = None
        self.dung.set()
        nhip.join(timeout=self.nc.chu_ky_nhip + 60)     # > cận trên một lần đọc hạn mức (48 s, han_muc_ranh)
