"""Trạng thái riêng của tram-bao-tin (~/.tram/bao-tin/): ghi nguyên tử, file hỏng thì dùng mặc định."""
import json
import os
import sys
from pathlib import Path


def doc_json(p: Path, mac_dinh):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return mac_dinh
    except ValueError:
        print(f"bao-tin: {p} hỏng — dùng mặc định", file=sys.stderr)
        return mac_dinh


def ghi_json(p: Path, du_lieu) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tam = p.with_name(p.name + ".tam")
    tam.write_text(json.dumps(du_lieu, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    os.replace(tam, p)
