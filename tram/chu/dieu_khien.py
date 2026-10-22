"""Bật/tắt estop dùng chung cho `tram chu estop|tiep-tuc` và nút trên dashboard (spec 2 §5.3)."""
from tram.chu import estop
from tram.su_kien.kho import KhoSuKien

DU_AN_TRAM = "_tram"


def bat_estop(kho: KhoSuKien, ly_do: str, *, tac_nhan: str, them: dict | None = None) -> None:
    estop.bat(ly_do)
    kho.ghi(DU_AN_TRAM, "estop.bat", {"ly_do": ly_do, **(them or {})}, tac_nhan=tac_nhan)


def tat_estop(kho: KhoSuKien, *, tac_nhan: str, them: dict | None = None) -> None:
    estop.tat()
    kho.ghi(DU_AN_TRAM, "estop.tat", dict(them or {}), tac_nhan=tac_nhan)
