"""Khoá phu_thuoc_4c riêng; thiếu/tắt không gọi CLI, mạng hay Keychain."""
from dataclasses import replace
from pathlib import Path

import yaml

from tram.duong_dan import tram_home
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c, tao_phu_thuoc_4c
from tram.nho.khach import tao_nho_lai


def nap_phu_thuoc_4c(path: Path | None = None, *, tao=tao_phu_thuoc_4c, nho=tao_nho_lai) -> PhuThuoc4c:
    p = path or tram_home() / "cau-hinh.yaml"
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("cau-hinh phải là bảng")
    cfg = raw.get("phu_thuoc_4c", {})
    if not isinstance(cfg, dict) or set(cfg) - {"github", "gitnexus", "memory"} or any(
            not isinstance(v, bool) for v in cfg.values()):
        raise ValueError("phu_thuoc_4c cần bảng boolean github/gitnexus/memory")
    github, gn, memory = (cfg.get(k, False) for k in ("github", "gitnexus", "memory"))
    dep = tao(github=github, gitnexus=gn, memory=False) if github or gn else PhuThuoc4c()
    return replace(dep, nho_lai=nho()) if memory else dep
