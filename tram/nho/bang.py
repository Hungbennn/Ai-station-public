"""Lược đồ bảng ký ức LanceDB và chuyển đổi hàng ↔ KyUc (spec 1b §5). Chuỗi trong điều kiện lọc luôn qua `sql()`."""
import json
from collections.abc import Iterable

import pyarrow as pa

from tram.nho.mo_hinh import KyUc

BANG = "ky_uc"
COT = ["id", "noi_dung", "pham_vi", "nhan", "quan_trong", "nguon", "nguon_dai_ca", "hieu_luc_tu", "tao_luc",
       "dung_luc", "so_lan_dung", "mo_hinh_embed", "so_chieu", "vector", "da_xoa"]


def luoc_do(so_chieu: int) -> pa.Schema:
    return pa.schema([
        ("id", pa.string()), ("noi_dung", pa.string()), ("pham_vi", pa.string()), ("nhan", pa.string()),
        ("quan_trong", pa.float32()), ("nguon", pa.string()), ("nguon_dai_ca", pa.bool_()),
        ("hieu_luc_tu", pa.string()), ("tao_luc", pa.string()), ("dung_luc", pa.string()),
        ("so_lan_dung", pa.int32()), ("mo_hinh_embed", pa.string()), ("so_chieu", pa.int32()),
        ("vector", pa.list_(pa.float32(), so_chieu)), ("da_xoa", pa.bool_())])


def sql(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def trong(ds: Iterable[str]) -> str:
    return "(" + ",".join(sql(x) for x in ds) + ")"


def hang(k: KyUc) -> dict:
    return {**k.sang_dict(), "nhan": json.dumps(list(k.nhan), ensure_ascii=False),
            "nguon": json.dumps(list(k.nguon), ensure_ascii=False, sort_keys=True), "so_chieu": k.so_chieu}


def ky_uc_tu_hang(h: dict) -> KyUc:
    return KyUc(h["id"], h["noi_dung"], h["pham_vi"], tuple(json.loads(h["nhan"])), float(h["quan_trong"]),
                tuple(json.loads(h["nguon"])), bool(h["nguon_dai_ca"]), h["hieu_luc_tu"], h["tao_luc"],
                h["mo_hinh_embed"], tuple(float(x) for x in h["vector"]), h["dung_luc"], int(h["so_lan_dung"]),
                bool(h["da_xoa"]))
