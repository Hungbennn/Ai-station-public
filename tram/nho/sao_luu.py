"""Sao lưu / khôi phục memory (spec 1b §6.4, §9.4): LanceDB + nhật ký thao tác + `moc_nho` tại CÙNG một điểm.

Chụp trong lúc giữ khoá kho (recall, ghi, dọn phiên bản đều dừng) và từ chính luồng nạp (nhật ký không đổi).
Khôi phục chỉ khi service đã dừng (khoá tiến trình rảnh); bản hiện tại được giữ lại, không xoá."""
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import lancedb

from tram.nho.bang import BANG
from tram.nho.khoa import khoa_dich_vu
from tram.nho.kho import KhoKyUc
from tram.nho.nhat_ky import NhatKy

TIEN_TO = "nho-"


def _nhan(luc: datetime | None) -> str:
    return (luc or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")


def sao_luu_nho(thu_muc_nho: Path, dich: Path, *, kho: KhoKyUc, nhat_ky: NhatKy, giu: int = 14,
                luc: datetime | None = None) -> Path:
    dich.mkdir(parents=True, exist_ok=True)
    ban, tam = dich / f"{TIEN_TO}{_nhan(luc)}", dich / f".dang-chup-{_nhan(luc)}"
    shutil.rmtree(tam, ignore_errors=True)
    with kho.khoa:
        shutil.copytree(thu_muc_nho / "lancedb", tam / "lancedb")
        nhat_ky.sao_luu(tam / "nhat-ky.db")
    tam.rename(ban)                                           # bản dở dang không bao giờ mang tên nho-*
    for mo_coi in dich.glob(".dang-chup-*"):                  # bản dở của lần chụp cũ bị cắt ngang
        if mo_coi.is_dir() and mo_coi.name < tam.name:
            shutil.rmtree(mo_coi, ignore_errors=True)
    for cu in sorted(p for p in dich.glob(f"{TIEN_TO}*") if p.is_dir())[:-giu]:
        shutil.rmtree(cu)
    return ban


def _kiem_ban(ban: Path) -> None:
    """Kiểm nhanh bản sao TRƯỚC khi đổi chỗ: nhật ký qua quick_check + đủ bảng, LanceDB mở được bảng ký ức."""
    try:
        db = sqlite3.connect(f"{(ban / 'nhat-ky.db').resolve().as_uri()}?mode=ro&immutable=1", uri=True)
        try:
            kq = db.execute("PRAGMA quick_check").fetchall()
            bang = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            db.close()
    except sqlite3.Error as e:
        raise ValueError(f"{ban}/nhat-ky.db hỏng: {e}") from None
    if kq != [("ok",)] or not {"thao_tac", "moc"} <= bang:
        raise ValueError(f"{ban}/nhat-ky.db hỏng hoặc thiếu bảng (quick_check: {kq[:3]})")
    try:
        lancedb.connect(ban / "lancedb").open_table(BANG).count_rows()
    except Exception as e:                       # noqa: BLE001 — lancedb ném nhiều loại lỗi khi bảng hỏng/thiếu
        raise ValueError(f"{ban}/lancedb hỏng: {type(e).__name__}: {str(e)[:200]}") from None


def khoi_phuc_nho(ban: Path, thu_muc_nho: Path, *, luc: datetime | None = None) -> Path:
    """Trả thư mục giữ bản hiện tại (trước khi khôi phục)."""
    if not (ban / "lancedb").is_dir() or not (ban / "nhat-ky.db").is_file():
        raise ValueError(f"{ban} không phải bản sao lưu memory (thiếu lancedb/ hoặc nhat-ky.db)")
    _kiem_ban(ban)
    with khoa_dich_vu(thu_muc_nho) as duoc:
        if not duoc:
            raise RuntimeError("memory service đang chạy — dừng dịch vụ trước khi khôi phục")
        giu = thu_muc_nho / f"truoc-khoi-phuc-{_nhan(luc)}"
        giu.mkdir()
        for ten in ("lancedb", "nhat-ky.db", "nhat-ky.db-wal", "nhat-ky.db-shm"):
            if (thu_muc_nho / ten).exists():
                shutil.move(thu_muc_nho / ten, giu / ten)
        shutil.copytree(ban / "lancedb", thu_muc_nho / "lancedb")
        shutil.copy2(ban / "nhat-ky.db", thu_muc_nho / "nhat-ky.db")
    return giu
