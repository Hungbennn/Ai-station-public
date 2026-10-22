"""Câu mô tả dễ đọc của một sự kiện (D39; khảo sát giao diện A3) — dùng cho "Sự kiện gần đây" (Tổng quan) và khối
sự kiện ký ức. Dựng từ MẪU CỐ ĐỊNH theo loại (`tram/suy/mau_su_kien.py`); chỉ ghép trường đã kiểm dạng: mã khe, mã
bead, số lượt, bước, cột, kết luận, mã lý do → câu hằng. KHÔNG BAO GIỜ đưa chữ tự do ra ngoài (`vi_sao`, `gop_y`,
`loi`, `tra_loi`, `noi_dung`, `ly_do` tự do, `tieu_de`, nội dung ký ức). Loại lạ hoặc mẫu lỗi → ""."""
import re

from tram.su_kien.kho import SuKien

MA = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}(/[A-Za-z0-9][A-Za-z0-9._-]{0,63})?")
PHAM_VI = re.compile(r"/[a-z0-9/-]{1,120}")
SHA = re.compile(r"[0-9a-f]{7,40}")
ADR = re.compile(r"ADR-\d{4}")
COT = {"ai-lam": "cột 1", "can-chot": "cột 2", "cho-review": "cột 3",
       "cot:ai-lam": "cột 1", "cot:can-chot": "cột 2", "cot:cho-review": "cột 3"}
BUOC = {"code": "code", "qc": "QC", "spec": "spec"}


def ma(x) -> str:
    return x if isinstance(x, str) and MA.fullmatch(x) else "?"


def so(x) -> str:
    return str(x) if isinstance(x, int) and not isinstance(x, bool) else "?"


def sha(x) -> str:
    return x[:7] if isinstance(x, str) and SHA.fullmatch(x) else "?"


def pham_vi(x) -> str:
    return x if isinstance(x, str) and PHAM_VI.fullmatch(x) and ".." not in x else "?"


def chon(bang: dict, x, mac_dinh: str = "?") -> str:
    return bang.get(x, mac_dinh) if isinstance(x, str) else mac_dinh


def adr(x) -> str:
    return x if isinstance(x, str) and ADR.fullmatch(x) else ""


def khe_tho(tac_nhan: str) -> str:
    """Báo cáo của thợ mang tác nhân `tho/<khe_id>` — chỉ lấy khi đúng dạng mã khe."""
    return ma(tac_nhan[4:]) if isinstance(tac_nhan, str) and tac_nhan.startswith("tho/") else "?"


def mo_ta(s: SuKien) -> str:
    from tram.suy.mau_su_kien import MAU
    mau = MAU.get(s.loai)
    if mau is None or not isinstance(s.du_lieu, dict):
        return ""
    try:
        return mau(s.du_lieu, s)
    except (KeyError, TypeError, ValueError, AttributeError):
        return ""
