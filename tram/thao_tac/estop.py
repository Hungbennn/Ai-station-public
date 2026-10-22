"""Nút estop / tiếp tục của dashboard — cùng logic `tram chu estop` (spec 2 §5.3), idempotent theo ma_thao_tac."""
from collections.abc import Callable

from tram.chu.dieu_khien import DU_AN_TRAM, bat_estop, tat_estop
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, co_su_kien

LY_DO_MAC_DINH = "Đại ca bấm estop trên dashboard"


def _chay(kho, kho_tt, loai_sk: str, noi_dung: dict, lam: Callable[[], None], ma: str,
          expected_version: str) -> KetQuaThaoTac:
    def buoc(_) -> bool:
        if not co_su_kien(kho, DU_AN_TRAM, None, loai_sk, ma):   # crash sau khi đặt cờ: đặt lại + ghi sự kiện
            lam()
        return True

    yc = YeuCau(ma, loai_sk, DU_AN_TRAM, None, noi_dung, expected_version)
    # G6: không kiểm expected_version — dừng khẩn cấp không được hỏng vì màn hình cũ.
    return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None, cac_buoc=[(loai_sk, buoc)])


def bat_estop_thao_tac(kho, kho_tt, *, ly_do: str | None, ma: str, expected_version: str) -> KetQuaThaoTac:
    ly_do = (ly_do or "").strip() or LY_DO_MAC_DINH
    return _chay(kho, kho_tt, "estop.bat", {"ly_do": ly_do},
                 lambda: bat_estop(kho, ly_do, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}), ma, expected_version)


def tiep_tuc_thao_tac(kho, kho_tt, *, ma: str, expected_version: str) -> KetQuaThaoTac:
    return _chay(kho, kho_tt, "estop.tat", {},
                 lambda: tat_estop(kho, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}), ma, expected_version)
