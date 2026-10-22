"""Danh sách cho phép; thiếu khoá giữ tương thích, danh sách rỗng tường minh bị từ chối."""
import re


def danh_sach(raw, ten):
    if ten not in raw:
        return ()
    ds = raw[ten]
    if not isinstance(ds, list) or not ds or any(
            not isinstance(x, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", x) for x in ds):
        raise ValueError(f"giao_viec.{ten} cần danh sách tên không rỗng")
    return tuple(dict.fromkeys(ds))
