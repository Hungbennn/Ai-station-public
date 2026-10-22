"""Thao tác ghi dashboard của nút "agent tự cập nhật việc" (spec cong-tac-de-nghi-viec, design D-8): idempotent theo
`ma_thao_tac` (bảng `thao_tac`), kiểm `expected_version` = phiên bản cài đặt (409 khi màn hình cũ), dự án
`bat_ghi: false` không bật được nút dự án (422; tắt và chỉnh nút con vẫn được). Sự kiện mang `ma_thao_tac`, tác nhân
`dai-ca/dashboard`. Kênh ghi (D110, D113) kiểm ở tuyến API."""
from dataclasses import asdict

from tram.de_nghi.cai_dat import LOAI_CAI_DAT, CaiDatTuCapNhat, doc_cai_dat, doi_cai_dat
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, co_su_kien
from tram.thao_tac.loi import KhongHopLe, XungDot

CHI_QUET_THU = "Dự án chỉ quét thử (bat_ghi: false) — không bật được agent tự cập nhật việc"


def luu_tu_cap_nhat_thao_tac(kho, kho_tt, du_an: str, cd: CaiDatTuCapNhat, *, bat_ghi: bool, ma: str,
                             expected_version: str) -> KetQuaThaoTac:
    """Từ chối (422, 409) xảy ra TRƯỚC khi tạo bản ghi `thao_tac`. Bước ghi so phiên bản lần nữa trong giao dịch."""
    def kiem() -> None:
        if cd.bat and not bat_ghi:
            raise KhongHopLe(CHI_QUET_THU)
        if (hien := doc_cai_dat(kho.db, du_an)[1]) != expected_version:
            raise XungDot(f"Cài đặt agent tự cập nhật việc của {du_an} đã đổi (hiện {hien}, đang xem"
                          f" {expected_version}) — tải lại")

    def buoc(_) -> dict:
        if not co_su_kien(kho, du_an, None, LOAI_CAI_DAT, ma):       # crash sau khi ghi: không ghi lần hai
            doi_cai_dat(kho.db, du_an, cd, tac_nhan=TAC_NHAN, expected=expected_version, ma_thao_tac=ma)
        return {"phien_ban": doc_cai_dat(kho.db, du_an)[1]}

    yc = YeuCau(ma, LOAI_CAI_DAT, du_an, None, {"cai_dat": asdict(cd)}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI_CAI_DAT, buoc)])
