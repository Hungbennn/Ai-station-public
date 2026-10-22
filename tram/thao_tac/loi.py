"""Lỗi nghiệp vụ của thao tác ghi; tram-api ánh xạ sang mã HTTP (tram/api/app.py)."""


class XungDot(Exception):
    """409: bead đã đổi so với expected_version, hoặc cùng ma_thao_tac mà nội dung khác."""


class KhongHopLe(ValueError):
    """422: yêu cầu sai luật (sai cột, thiếu câu trả lời, mã không hợp lệ, ...)."""


class ChuaHoTro(Exception):
    """501: nút có từ 2a nhưng phần xử lý thuộc lát sau (Duyệt / Trả về spec — phần 4b)."""


class KhongThay(LookupError):
    """404: dự án hoặc bead không có."""
