"""Đọc JSON `bd list` (bs-2bd.1.20: dời nguyên văn khỏi `bd.py`)."""
import json

from tram.beads.loi import LoiBd
from tram.beads.mo_hinh import Bead


def doc_ds(ra: str) -> list[Bead]:
    try:
        ds = json.loads(ra)
        if not isinstance(ds, list):
            raise TypeError(f"cần mảng, nhận {type(ds).__name__}")
        return [Bead.tu_json(d) for d in ds]
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise LoiBd(f"bd list: JSON không đọc được ({type(e).__name__}: {e})") from e


def doc_ds_yeu_cau(ra: str) -> list[Bead]:
    try:
        ds = json.loads(ra)
        if not isinstance(ds, list):
            raise ValueError
        for d in ds:
            if not isinstance(d, dict):
                raise ValueError
            if any(not isinstance(d.get(k), str) for k in ("id", "issue_type")):
                raise ValueError
            if not isinstance(d.get("description", ""), str):   # bd 1.2.2 bỏ khoá khi rỗng; có mà null/sai kiểu: lỗi
                raise ValueError
            if not d["id"] or d["id"] != d["id"].strip() or not d["issue_type"]:
                raise ValueError
        return [Bead.tu_json(d) for d in ds]
    except (ValueError, KeyError, TypeError, AttributeError):
        raise LoiBd("bd list: schema đối soát không hợp lệ") from None
