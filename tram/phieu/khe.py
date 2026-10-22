"""Sổ khe phía trạm (spec 3 §6.2 điều kiện 1 và 6, §6.3, §9, §10): trạng thái SUY từ sự kiện `_tram`
(`khe.dang_ky`, `khe.bat`, `khe.tat`, `khe.ket_noi`, `khe.mat_ket_noi`) và bảng `lan_chay`."""
import json
from datetime import datetime, timedelta

from tram.cau_hinh.tram import CauHinhThoTram
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, chuoi_gio

LOAI_BAT_TAT = ("khe.bat", "khe.tat")
LOAI_KET_NOI = ("khe.ket_noi", "khe.mat_ket_noi")


class KheLa(ValueError):
    """Khe chưa đăng ký."""


def su_kien_khe(kho: KhoPhieu, khe_id: str, loai: tuple[str, ...]) -> tuple[int, str, dict, str] | None:
    """(id, loại, dữ liệu, lúc) của sự kiện mới nhất trong `loai` mang `khe_id`."""
    h = kho.db.execute(
        f"SELECT id, loai, du_lieu, luc FROM su_kien WHERE du_an = ? AND loai IN ({','.join('?' * len(loai))})"
        " AND json_extract(du_lieu, '$.khe_id') = ? ORDER BY id DESC LIMIT 1", (DU_AN_TRAM, *loai, khe_id)).fetchone()
    return None if h is None else (h[0], h[1], json.loads(h[2]), h[3])


def cac_khe(kho: KhoPhieu) -> dict[str, dict]:
    """khe_id → dữ liệu `khe.dang_ky` mới nhất, mọi khe đã từng đăng ký."""
    ra: dict[str, dict] = {}
    for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE du_an = ? AND loai = 'khe.dang_ky' ORDER BY id",
                               (DU_AN_TRAM,)):
        du_lieu = json.loads(d)
        ra[du_lieu["khe_id"]] = du_lieu
    return ra


def khe_dang_bat(kho: KhoPhieu, khe_id: str) -> bool:
    """Điều kiện 1: chỉ sự kiện cấp quyền `khe.bat`; đăng ký thông tin không cấp quyền chạy."""
    x = su_kien_khe(kho, khe_id, LOAI_BAT_TAT)
    return x is not None and x[1] == "khe.bat"


def dang_ky_khe(kho: KhoPhieu, may_id: str, khe: list[dict], *, luc: datetime) -> list[str]:
    """Trong giao dịch. Ghi `khe.dang_ky` cho khe mới hoặc đổi thông tin (không cấp quyền bật). Trả các khe_id."""
    ra = []
    for k in khe:
        khe_id = f"{may_id}/{k['ten']}"
        du_lieu = {"khe_id": khe_id, "cli": k["cli"], "ten_goi_nho": k["ten_goi_nho"],
                   "vai_uu_tien": list(k["vai_uu_tien"])}
        if k.get("models"):
            du_lieu["models"] = list(k["models"])
        cu = su_kien_khe(kho, khe_id, ("khe.dang_ky",))
        if cu is None or cu[2] != du_lieu:
            kho.ghi_su_kien(DU_AN_TRAM, "khe.dang_ky", du_lieu, luc=luc)
        ra.append(khe_id)
    return ra


def bat_tat_khe(kho: KhoPhieu, khe_id: str, *, bat: bool, vi_sao: str, tac_nhan: str, luc: datetime,
                them: dict | None = None) -> None:
    """Trong giao dịch. `tram tho bat-khe|tat-khe` (3a) và dashboard 2b — `them` = `{ma_thao_tac}` của dashboard."""
    if su_kien_khe(kho, khe_id, ("khe.dang_ky",)) is None:
        raise KheLa(f"Khe {khe_id} chưa đăng ký")
    kho.ghi_su_kien(DU_AN_TRAM, "khe.bat" if bat else "khe.tat", {**(them or {}), "khe_id": khe_id, "vi_sao": vi_sao},
                    luc=luc, tac_nhan=tac_nhan)


def phien_ban_khe(kho: KhoPhieu, khe_id: str) -> str:
    """`expected_version` của thao tác khe trên dashboard (spec 2 §12.3): id sự kiện bật/tắt và cầu dao mới nhất."""
    a = su_kien_khe(kho, khe_id, LOAI_BAT_TAT)
    b = su_kien_khe(kho, khe_id, ("khe.cau_dao_ngat", "khe.cau_dao_dong"))
    return f"{a[0] if a else 0}:{b[0] if b else 0}"


def dang_mat_ket_noi(kho: KhoPhieu, khe_id: str) -> bool:
    x = su_kien_khe(kho, khe_id, LOAI_KET_NOI)
    return x is not None and x[1] == "khe.mat_ket_noi"


def dem_lan_chay(kho: KhoPhieu, khe_id: str, tu: datetime) -> int:
    return kho.db.execute("SELECT COUNT(*) FROM lan_chay WHERE khe_id = ? AND luc > ?",
                          (khe_id, chuoi_gio(tu))).fetchone()[0]


def con_cho_chay(kho: KhoPhieu, khe_id: str, bay_gio: datetime, ch: CauHinhThoTram) -> bool:
    """Điều kiện 6 / trần cứng §8.3: số lần chạy trong 60 phút và 24 giờ gần nhất (cửa sổ trượt)."""
    return (dem_lan_chay(kho, khe_id, bay_gio - timedelta(hours=1)) < ch.lan_chay_moi_gio
            and dem_lan_chay(kho, khe_id, bay_gio - timedelta(days=1)) < ch.lan_chay_moi_ngay)
