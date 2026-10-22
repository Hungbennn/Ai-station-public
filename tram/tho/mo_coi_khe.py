"""Khởi động một khe trong `tram tho chay` (spec 3 §7.2; 3a-1 G12; V2-0, review vòng 1 A02): dọn TOÀN UID của khe
(`nc.don_khe` — gồm cả CLI mồ côi của lần chạy trước), bảo đảm đã gửi `chay.xong {mo-coi}` cho phiếu đang giữ, trả lại
phiếu đó (đọc `phieu.json`) để chạy tiếp. Không chứng minh được khe sạch → (None, True): khe DỪNG, giữ bản ghi và
phiếu."""
from tram.kiem.vong_doi import LoiThuHoi
from tram.phieu.mo_hinh import Phieu
from tram.tho.cau_hinh import KheCauHinh
from tram.tho.chuan_bi import gui_su_kien
from tram.tho.hop_thu import HopThu
from tram.tho.mo_coi import don_mo_coi
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.so_khe import SoKhe, TrangThaiPhieu


def don_mo_coi_khe(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu) -> tuple[TrangThaiPhieu | None, bool]:
    """(phiếu đang giữ, khe phải dừng)."""
    try:
        x = don_mo_coi(so.pid, don=lambda: nc.don_khe(k))
    except LoiThuHoi:
        print("Chưa chứng minh được khe sạch (dọn theo UID của principal) — giữ bản ghi và phiếu, dừng khe; "
              "Đại ca kiểm theo sổ tay G7")
        return None, True
    tt = so.doc_phieu()
    if x and tt and Phieu.model_validate(tt.phieu).giao_id == x["giao_id"]:
        p = Phieu.model_validate(tt.phieu)
        if not hop.co(lambda d, t: t.get("loai") == "chay.xong" and t.get("du_lieu", {}).get("lan") == x["lan"]
                      and t.get("giao_id") == p.giao_id):
            gui_su_kien(nc, hop, p, "chay.xong", {"lan": x["lan"], "ket_thuc": "mo-coi"}, x["lan"])
    return tt, False


def don_phieu_cu(vk):
    """Nhịp từ chối phiếu giữ qua restart: dọn lượt B trước khi bỏ sổ."""
    try:
        if vk.nc.ch.tren_may_b:
            from tram.tho.luot_b import don_phieu_cu_b
            don_phieu_cu_b(vk.nc, vk.k, vk.phieu_moi)
        vk.so.xoa_phieu()
        vk.phieu_moi, vk.han_giu = None, None
        return True
    except LoiThuHoi:
        return False
