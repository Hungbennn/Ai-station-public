"""Thao tác ghi dashboard của tự merge / tự deploy (`dieu-khien-tu-dong`, D79, D87, D88): lưu cài đặt, TẠM DỪNG /
Tiếp tục một dự án hoặc toàn trạm (`DU_AN_TRAM`). Idempotent theo `ma_thao_tac` (bảng `thao_tac`); sự kiện mang
`ma_thao_tac`, tác nhân `dai-ca/dashboard`. Lưu cài đặt kiểm `expected_version` = phiên bản cài đặt (409 khi cũ);
tạm dừng / tiếp tục KHÔNG kiểm (như estop — không hỏng vì màn hình cũ, D78). Kênh ghi (D87) kiểm ở tuyến API."""
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.deploy.san_sang import can_duong
from tram.thao_tac.chung import TAC_NHAN, co_su_kien
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.tu_dong.cai_dat import CaiDatTuDong, loi_cai_dat
from tram.tu_dong.luu import LOAI_CAI_DAT, LOAI_TAM_DUNG, LOAI_TIEP_TUC, doc_cai_dat, doi_cai_dat, ghi_tam_dung


def luu_cai_dat_thao_tac(kho, kho_tt, du_an: str, cd: CaiDatTuDong, *, bat_ghi: bool, ma: str,
                         expected_version: str, kiem_quyen=lambda cu, moi: None) -> KetQuaThaoTac:
    """Từ chối (422, 409) xảy ra TRƯỚC khi tạo bản ghi `thao_tac`: lệnh bị từ chối không lưu ở đâu cả. Bước ghi vẫn
    so phiên bản lần nữa trong giao dịch (`doi_cai_dat`)."""
    def kiem() -> None:
        if (loi := loi_cai_dat(cd, bat_ghi=bat_ghi)) is not None:
            raise KhongHopLe(loi)
        if cd.tu_deploy:
            can_duong(du_an, cd)
        if (hien := doc_cai_dat(kho.db, du_an)[1]) != expected_version:
            raise XungDot(f"Cài đặt tự động của {du_an} đã đổi (hiện {hien}, đang xem {expected_version}) — tải lại")

    def buoc(_) -> dict:
        if not co_su_kien(kho, du_an, None, LOAI_CAI_DAT, ma):        # crash sau khi ghi: không ghi lần hai
            doi_cai_dat(kho.db, du_an, lambda _cu: cd, tac_nhan=TAC_NHAN, expected=expected_version,
                        them={"ma_thao_tac": ma})
        return {"phien_ban": doc_cai_dat(kho.db, du_an)[1]}

    yc = YeuCau(ma, LOAI_CAI_DAT, du_an, None, {"cai_dat": cd.phang()}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI_CAI_DAT, buoc)],
                         kiem_quyen=lambda: kiem_quyen(doc_cai_dat(kho.db, du_an)[0], cd))


def tam_dung_thao_tac(kho, kho_tt, du_an: str, *, tam_dung: bool, ma: str, expected_version: str) -> KetQuaThaoTac:
    """`du_an` = tên dự án hoặc `DU_AN_TRAM`. Kết quả `{loai: True}` khi đã ghi, `False` khi vốn đã ở trạng thái đó."""
    loai = LOAI_TAM_DUNG if tam_dung else LOAI_TIEP_TUC

    def buoc(_) -> bool:
        if co_su_kien(kho, du_an, None, loai, ma):
            return True
        return ghi_tam_dung(kho.db, du_an, tam_dung=tam_dung, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma})

    yc = YeuCau(ma, loai, du_an, None, {}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None, cac_buoc=[(loai, buoc)])
