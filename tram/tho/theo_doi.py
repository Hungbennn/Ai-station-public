"""Đọc hàng đợi `tram bao` của phiếu trong lúc CLI chạy (spec 3 §7.4) — luồng nền, mỗi `cho_doc` giây. Mỗi dòng đã
được kiểm lại + gắn phiếu bởi `xu_ly_hang_doi` (3a-1): `moc` → đưa lên ref tạm + `da-push` rồi `bao.moc` (giữ bàn
giao tạm cho lần sau); `can_hoi` → `bao.can_hoi` rồi DỪNG MỀM NGAY (4a: chưa có `pham_vi_doc_lap`); `bi` → dừng;
`xong` → cho CLI tối đa `cho_xong` giây để thoát rồi dừng. Lệnh dừng từ nhịp tim cũng được chuyển thành `dung`.
bs-863.16 + review vòng 1 A06: MỘT hạn (`han_dung`) bao trùm chờ luồng nền VÀ lần đọc cuối (chạy ở luồng riêng); hết hạn
→ báo thôi ở ranh giới dòng/đẩy mốc kế tiếp, `LoiThuHoi` (khe dừng, giữ phiếu; dòng chưa xử lý giữ vị trí — request_id
tất định). Một lượt đọc giữ khoá: không đọc song song. Đã bắt đầu dừng thì không hẹn `xong` nào được tạo nữa."""
import threading
import time

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.chuan_bi import PhieuDangChay
from tram.tho.day import day_va_cong_bo
from tram.tho.hang_doi import xu_ly_hang_doi
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.trong_han import chay_trong_han

DUNG_CUNG = ("luot-cu", "thu-hoi")
HAN_DUNG = 150.0        # > một dòng mốc: git update-ref ≤ 60 s + push ≤ 60 s + gửi HTTP (`KhachTram.thoi_gian_cho`)


class TheoDoi:
    def __init__(self, pc: PhieuDangChay, nc: NguCanhTho, dung: threading.Event, lenh_nhip=lambda: None,
                 han_dung: float = HAN_DUNG):
        self.pc, self.nc, self.dung, self.lenh_nhip, self.han_dung = pc, nc, dung, lenh_nhip, han_dung
        self.xong: dict | None = None
        self.bi: dict | None = None
        self.can_hoi, self.loi = False, []
        self._ngung, self._ngung_cuoi = threading.Event(), threading.Event()
        self._luong: threading.Thread | None = None
        self._luong_cuoi: list[threading.Thread] = []
        self._khoa, self._khoa_hen = threading.Lock(), threading.Lock()
        self._hen, self._het_hen = None, False          # hẹn `xong`; đã bắt đầu dừng → không tạo hẹn mới
        self.loi_nen: str | None = None                 # tên lỗi ở luồng nền — lần đọc cuối thử lại các dòng chưa ghi

    def _moc(self, than: dict, ngung: threading.Event | None) -> None:
        pc, nc = self.pc, self.nc
        if than.get("ban_giao"):
            pc.tt.ban_giao_tam = than["ban_giao"]
        if nc.ch.tren_may_b:
            return  # Mốc B lưu trong sổ phiếu; chỉ chốt/công bố sau khi thu hồi CLI.
        if than.get("commit") and len(than["commit"]) == 40:
            day_va_cong_bo(pc.wt, pc.p, than["commit"], khach=nc.khach, phuong_an=nc.ch.chay.day,
                           han=time.monotonic() + 60, cho=nc.cho_thu_lai, dung=ngung)
        pc.hop.gui_mot(nc.khach, "/api/tho/bao", than)

    def mot_luot(self, ngung: threading.Event | None = None) -> None:
        with self._khoa:
            self._doc(ngung)
        if self.lenh_nhip() and not self.dung.is_set():
            self.dung.set()

    def _doc(self, ngung: threading.Event | None) -> None:
        pc = self.pc
        ds, ke = xu_ly_hang_doi(pc.hang_doi, khe_id=pc.p.khe_id, giao_id=pc.p.giao_id, luot=pc.p.luot,
                                tu_dong=pc.tt.vi_tri_hang_doi)
        for d in ds:
            if ngung is not None and ngung.is_set():
                ke = d.so                                       # chưa xử lý: lần đọc cuối làm tiếp, đúng một lần
                break
            if d.than is None:
                self.loi.append(f"dòng {d.so}: {d.loi}")
            elif self.xong or self.bi or self.can_hoi:
                continue                                        # sau dòng kết thúc: bỏ
            elif d.than["loai"] in ("tien_do", "viec_moi"):       # TC (design D-1): gửi ngay, không dừng phiếu
                pc.hop.gui_mot(self.nc.khach, "/api/tho/bao", d.than)
            elif d.than["loai"] == "moc":
                self._moc(d.than, ngung)
            elif d.than["loai"] == "can_hoi":
                pc.hop.gui_mot(self.nc.khach, "/api/tho/bao", d.than)
                self.can_hoi = True
                self.dung.set()
            elif d.than["loai"] == "bi":
                self.bi = d.than
                self.dung.set()
            elif d.than["loai"] == "xong":
                self.xong = d.than
                self._dat_hen()
        pc.tt.vi_tri_hang_doi = ke
        pc.luu()

    def _vong(self) -> None:
        try:
            while not self._ngung.wait(self.nc.cho_doc):
                self.mot_luot(self._ngung)
        except Exception as e:                          # noqa: BLE001 — vị trí chưa ghi: lần đọc cuối thử lại
            self.loi_nen = type(e).__name__

    def bat_dau(self) -> "TheoDoi":
        self._luong = threading.Thread(target=self._vong, daemon=True, name=f"theo-doi-{self.pc.p.giao_id}")
        self._luong.start()
        return self

    def _dat_hen(self) -> None:
        with self._khoa_hen:
            if not self._het_hen:
                self._hen = threading.Timer(self.nc.cho_xong, self.dung.set)
                self._hen.daemon = True
                self._hen.start()

    def _dung_den(self, het: float) -> None:
        with self._khoa_hen:
            self._het_hen = True
            if self._hen is not None:
                self._hen.cancel()
        self._ngung.set()
        if self._luong is not None:
            self._luong.join(max(0.0, het - time.monotonic()))
            if self._luong.is_alive():
                raise LoiThuHoi("luồng đọc hàng đợi chưa dừng trong hạn — dừng khe, giữ phiếu")

    def dung_lai(self, han: float | None = None) -> None:     # KHÔNG đọc lần cuối; chưa dừng → `LoiThuHoi`
        self._dung_den(time.monotonic() + (self.han_dung if han is None else han))

    def ket_thuc(self, han: float | None = None) -> None:
        """Dừng luồng nền rồi đọc lần cuối (dòng ghi ngay trước khi CLI thoát) — cả hai trong MỘT hạn."""
        het = time.monotonic() + (self.han_dung if han is None else han)
        self._dung_den(het)
        chay_trong_han(lambda: self.mot_luot(self._ngung_cuoi), het, ngung=self._ngung_cuoi,
                       ten=f"đọc hàng đợi lần cuối {self.pc.p.giao_id}", luong=self._luong_cuoi)
