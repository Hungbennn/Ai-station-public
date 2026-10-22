"""MỘT nguồn khai báo principal kiểm lại `tram-kiem` (lát 3c, bead bs-urj.12; spec 3 §7.3 mục 5, spec 4 §6.2).

Khoá chuẩn: `cach_ly.tram_kiem: user:<tên> | sandbox:<tên>` trong `~/.tram/cau-hinh.yaml`. Khoá cũ của 4a-2
`giao_viec.principal_kiem {ten, boc, trao_quyen}` chỉ còn được đọc để đối chiếu:
- có cả hai, cùng tên user → cảnh báo, bỏ `boc`/`trao_quyen` cũ (argv dựng từ khoá chuẩn);
- có cả hai, khác tên user → lỗi cấu hình;
- chỉ có khoá cũ → lỗi cấu hình (khoá cũ không nói cơ chế §14 — không chọn thay Đại ca).
Mọi nơi đọc (`nap_cau_hinh_giao_viec`, `tram chu cai-dat-tho`, `tram chu kiem-cach-ly`) đi qua `doc_principal_kiem`."""
import sys
from collections.abc import Callable
from pathlib import Path

import yaml

from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly

KHOA_CU = {"ten", "boc", "trao_quyen"}


def _bao(tin: str) -> None:
    print(f"[cau-hinh] {tin}", file=sys.stderr, flush=True)


def _ten_khoa_cu(p: Path) -> str | None:
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    gv = raw.get("giao_viec") if isinstance(raw, dict) else None
    cu = gv.get("principal_kiem") if isinstance(gv, dict) else None
    if cu is None:
        return None
    if not isinstance(cu, dict) or not set(cu) <= KHOA_CU or not isinstance(cu.get("ten"), str):
        raise ValueError("giao_viec.principal_kiem (khoá cũ) phải là bảng {ten, boc?, trao_quyen?}")
    return cu["ten"]


def doc_principal_kiem(duong_dan: Path | None = None, *, bao: Callable[[str], None] = _bao) -> PrincipalKiem | None:
    """None khi chưa khai (chờ S6). Sai dạng hoặc hai khoá lệch nhau → ValueError."""
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    moi, cu = nap_cau_hinh_cach_ly(p).tram_kiem, _ten_khoa_cu(p)
    pk = None if moi is None else tu_cach_ly(moi)
    if cu is None:
        return pk
    if pk is None:
        raise ValueError("giao_viec.principal_kiem là khoá cũ — khai cach_ly.tram_kiem: user:<tên> | sandbox:<tên> "
                         "(lát 3c) rồi xoá khoá cũ")
    if cu != pk.ten:
        raise ValueError(f"giao_viec.principal_kiem.ten = {cu!r} khác cach_ly.tram_kiem = {moi!r} — "
                         "chỉ giữ cach_ly.tram_kiem")
    bao("giao_viec.principal_kiem là khoá cũ, trùng cach_ly.tram_kiem — bỏ qua boc/trao_quyen cũ; hãy xoá khoá này")
    return pk
