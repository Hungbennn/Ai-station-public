from pathlib import Path
from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
from tram.giao_viec.ban_chep import LoiBanChep


def cac_du_an_quan_sat(thu_muc: Path | None = None) -> list:
    try:
        return [nap_du_an(ten, thu_muc=thu_muc)
                for ten in liet_ke_du_an(thu_muc) if not ten.startswith("_")]
    except Exception as e:
        raise LoiBanChep(f"không đọc đủ inventory môi trường kiểm ({type(e).__name__})") from None
