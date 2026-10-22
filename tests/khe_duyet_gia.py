"""Tiền điều kiện test nghiệp vụ: chủ đã cấp quyền chạy; không dùng trong test cửa máy."""
from tram.phieu.khe import dang_ky_khe, bat_tat_khe


def dang_ky_va_duyet(kho, may, khe, *, luc):
    ids = dang_ky_khe(kho, may, khe, luc=luc)
    for kid in ids:
        bat_tat_khe(kho, kid, bat=True, vi_sao='fixture đã được chủ duyệt', tac_nhan='dai-ca', luc=luc)
    return ids
