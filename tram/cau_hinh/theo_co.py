"""Chính sách cỡ tuỳ chọn; thiếu khối giữ nguyên đường cũ, khối sai từ chối nạp."""
import hashlib
import json

MAC_DINH = {"nho_file": 2, "vua_file": 8, "nho_nhom": 1, "vua_nhom": 2,
            "nho_tieu_chi": 3, "vua_tieu_chi": 8, "nhom": {}, "nguy_hiem": [],
            "model_nho": "sonnet", "model_lon": "opus", "lenh_ca_bo": [],
            "effort_nho": "medium", "effort_vua": "high", "effort_lon": "high"}


def doc_theo_co(raw):
    if not isinstance(raw, dict) or set(raw) - set(MAC_DINH):
        raise ValueError("theo_co: sai khối hoặc khoá lạ")
    d = {**MAC_DINH, **raw}
    for ten in ("file", "nhom", "tieu_chi"):
        a, b = d["nho_" + ten], d["vua_" + ten]
        if type(a) is not int or type(b) is not int or not 0 < a <= b:
            raise ValueError("theo_co: ngưỡng phải nguyên dương, nhỏ không vượt vừa")
    if not isinstance(d["nhom"], dict) or any(
            not isinstance(k, str) or not k or k.startswith("/") or ".." in k.split("/")
            or any(c in k for c in "*?[\\") or not isinstance(v, str) or not v
            for k, v in d["nhom"].items()):
        raise ValueError("theo_co: ánh xạ nhóm không hợp lệ")
    for k in ("nguy_hiem", "lenh_ca_bo"):
        if not isinstance(d[k], list) or any(not isinstance(x, str) or not x.strip() for x in d[k]):
            raise ValueError("theo_co: cần danh sách chuỗi không rỗng")
    if d["model_nho"] != "sonnet" or d["model_lon"] != "opus":
        raise ValueError("theo_co: bản đầu chỉ Sonnet/Opus")
    for k in ("effort_nho", "effort_vua", "effort_lon"):
        if d[k] not in ("low", "medium", "high", "xhigh", "max"):
            raise ValueError("theo_co: effort chỉ nhận low/medium/high/xhigh/max")
    d["ban_luat"] = hashlib.sha256(json.dumps(["co-v1", d], sort_keys=True).encode()).hexdigest()
    return d
