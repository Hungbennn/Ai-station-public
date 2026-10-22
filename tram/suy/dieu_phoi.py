"""Đèn phòng Điều phối của Văn phòng 3D (spec 2 §5.5; plan 2e G7–G9) — suy lúc đọc từ sự kiện `dieu_phoi.nhip`.

Hook của phiên Claude Code trên máy A gửi nhịp (`POST /api/dieu-phoi/nhip`, `tram/api/dieu_phoi.py`); mỗi nhịp là
`{su_kien: <tên sự kiện hook>, phien: <16 hex = sha256(session_id)[:16], tính trên máy A>}`, dự án `_tram`.
- `sang = None`: chưa từng có nhịp ("chưa có tín hiệu" — không bịa trạng thái, như 2c G4).
- `sang = True`: có ít nhất một phiên mà nhịp cuối KHÔNG phải `SessionEnd` và cách đây ≤ `HAN_SONG`.
- `sang = False`: mọi phiên đã `SessionEnd` hoặc nhịp cuối quá hạn (đèn xám "tắt đèn").
Ghi gộp (`can_ghi`): mỗi phiên tối đa một nhịp mỗi `GOP`, trừ khi đổi giữa "đang chạy" và "kết thúc".
Danh sách nhịp vào hai hàm là MỌI nhịp trong `HAN_SONG` (`tram/suy/kho_nhip.py::doc_nhip`), không cắt theo số dòng."""
from datetime import datetime, timedelta

LOAI = "dieu_phoi.nhip"
DU_AN_HE = "_tram"
TAC_NHAN = "dai-ca/may-a"
SU_KIEN_HOOK = ("SessionStart", "UserPromptSubmit", "Stop", "SessionEnd")
KET_THUC = "SessionEnd"
HAN_SONG = timedelta(minutes=15)
GOP = timedelta(seconds=60)


def _luc(s) -> datetime:
    return datetime.fromisoformat(s.luc.replace("Z", "+00:00"))


def _cuoi_theo_phien(nhip: list) -> dict:
    """`nhip` xếp mới → cũ (như `KhoSuKien.gan_day`) → nhịp mới nhất của từng phiên."""
    ra: dict = {}
    for s in nhip:
        ra.setdefault(s.du_lieu.get("phien"), s)
    return ra


def den_dieu_phoi(nhip: list, bay_gio: datetime) -> dict:
    """`{sang: bool | None, nhip_cuoi: ISO | None}` — `nhip_cuoi` là lúc ghi nhịp mới nhất (mọi phiên)."""
    if not nhip:
        return {"sang": None, "nhip_cuoi": None}
    sang = any(s.du_lieu.get("su_kien") != KET_THUC and bay_gio - _luc(s) <= HAN_SONG
               for s in _cuoi_theo_phien(nhip).values())
    return {"sang": sang, "nhip_cuoi": nhip[0].luc}


def can_ghi(nhip: list, phien: str, su_kien: str, bay_gio: datetime) -> bool:
    """Ghi khi phiên chưa có nhịp, khi đổi giữa kết thúc / đang chạy, hoặc nhịp cuối của phiên đã cũ ≥ `GOP`."""
    cu = _cuoi_theo_phien(nhip).get(phien)
    if cu is None or (cu.du_lieu.get("su_kien") == KET_THUC) != (su_kien == KET_THUC):
        return True
    return bay_gio - _luc(cu) >= GOP
