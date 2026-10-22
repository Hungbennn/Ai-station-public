"""Trạng thái deploy: chỉ tiêu thụ merge đã ghi trong tập bao phủ của commit thực chạy."""
import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

TAC_NHAN = "tram/tu-deploy"
LOAI = ("pr.da_merge", "tu_merge.bat_dau", "deploy.yeu_cau", "deploy.huy", "deploy.san_sang", "deploy.bat_dau",
        "deploy.lenh", "deploy.xong", "tu_dong.cai_dat", "tu_dong.tam_dung",
        "deploy.kiem", "deploy.doi_soat", "deploy.cho")
HONG = ("da_lui", "lui_hong")


@dataclass(frozen=True)
class SK:
    id: int
    loai: str
    du_lieu: dict
    luc: str
    tac_nhan: str
    bead_id: str | None


def doc_su_kien(db: sqlite3.Connection, du_an: str) -> list[SK]:
    return [SK(i, l, json.loads(d), luc, tn, b) for i, l, d, luc, tn, b in db.execute(
        f"SELECT id, loai, du_lieu, luc, tac_nhan, bead_id FROM su_kien WHERE du_an = ? AND loai IN"
        f" ({','.join('?' * len(LOAI))}) ORDER BY id", (du_an, *LOAI))]


def cuoi(ds: list[SK], loai: str, dk: Callable[[SK], bool] = lambda s: True) -> SK | None:
    return next((s for s in reversed(ds) if s.loai == loai and dk(s)), None)


def _id(s: SK | None) -> int:
    return s.id if s else 0


def ma(s: SK) -> str | None:
    return s.du_lieu.get("ma_thao_tac")


def chuoi_dang_do(ds: list[SK]) -> list[SK]:
    xong = {ma(s) for s in ds if s.loai == "deploy.xong"}
    return [s for s in ds if s.loai == "deploy.bat_dau" and ma(s) not in xong]


def bat_dau_cua(ds: list[SK], x: SK) -> SK | None:
    return cuoi(ds, "deploy.bat_dau", lambda s: ma(s) == ma(x))


def bat_dau_dat(ds: list[SK]) -> SK | None:
    """`deploy.bat_dau` của chuỗi `dat` gần nhất — bản khách đang dùng."""
    x = cuoi(ds, "deploy.xong", lambda s: s.du_lieu.get("ket_qua") == "dat")
    return None if x is None else bat_dau_cua(ds, x)


def dem_hong(ds: list[SK]) -> int:
    def bat_lai(s: SK) -> bool:
        return "tu_deploy" in s.du_lieu.get("doi", ()) and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is True
    moc = max(_id(cuoi(ds, "deploy.xong", lambda s: s.du_lieu.get("ket_qua") == "dat")),
              _id(cuoi(ds, "tu_dong.cai_dat", bat_lai)))
    return sum(s.id > moc and s.loai == "deploy.xong" and s.du_lieu.get("ket_qua") in HONG for s in ds)


def yeu_cau_cho(ds: list[SK]) -> SK | None:
    da = {s.du_lieu.get("yeu_cau") for s in ds if s.loai == "deploy.bat_dau"}
    da |= {ma(s) for s in ds if s.loai == "deploy.huy"}
    return cuoi(ds, "deploy.yeu_cau", lambda s: ma(s) not in da)


def la_tu_merge(ds: list[SK], m: SK) -> bool:
    return any(s.loai == "tu_merge.bat_dau" and s.bead_id == m.bead_id and s.du_lieu.get("loai", "code") == "code"
               and s.du_lieu.get("commit") == m.du_lieu.get("commit") for s in ds)


def bao_gom(ds: list[SK], loai: str, dk=lambda s: True) -> set[int]:
    return {i for s in ds if s.loai == loai and dk(s) for i in s.du_lieu.get("bao_gom", [])}


def tu_merge_cho_deploy(ds: list[SK], *, ma_nguon: str | None = None) -> SK | None:
    # D123: chỉ sự kiện merge sau lần bật gần nhất; không phụ thuộc có tick lúc đang tắt.
    bat = _id(cuoi(ds, "tu_dong.cai_dat", lambda s: "tu_deploy" in s.du_lieu.get("doi", [])
                  and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is True))
    da = bao_gom(ds, "deploy.bat_dau") | bao_gom(ds, "deploy.san_sang",
        lambda s: "tu_deploy_tat" in s.du_lieu.get("cho", []))
    return cuoi(ds, "pr.da_merge", lambda s: s.id > bat and s.id not in da and la_tu_merge(ds, s)
                and (ma_nguon is None or ma_nguon == f"sk-{s.id}"))


def merge_chua_deploy(ds: list[SK]) -> list[SK]:
    dat = {ma(s) for s in ds if s.loai == "deploy.xong" and s.du_lieu.get("ket_qua") == "dat"}
    da = bao_gom(ds, "deploy.bat_dau", lambda s: ma(s) in dat)
    return [s for s in ds if s.loai == "pr.da_merge" and s.id not in da]


def moc_ban(ds: list[SK]) -> list[SK]:
    return [s for s in ds if s.loai in ("deploy.san_sang", "deploy.bat_dau")]


def chua_ghi_nhan(ds: list[SK]) -> list[SK]:
    da = bao_gom(ds, "deploy.san_sang") | bao_gom(ds, "deploy.bat_dau")
    return [s for s in merge_chua_deploy(ds) if s.id not in da]


def da_ghi_nhan(ds: list[SK], commit: str, bao: list[int] | None = None, *, cho=()) -> bool:
    # Dấu tắt chỉ cần cho bản sẵn sàng chưa chạy; bắt đầu đã tiêu trigger (D124).
    return any(s.du_lieu.get("commit") == commit and
               (s.loai == "deploy.bat_dau" or "tu_deploy_tat" not in cho or
                "tu_deploy_tat" in s.du_lieu.get("cho", [])) and
               (bao is None or set(s.du_lieu.get("bao_gom", [])) == set(bao)) for s in moc_ban(ds))


def commit_truoc(ds: list[SK]) -> str:
    bd = bat_dau_dat(ds)
    return bd.du_lieu["commit"] if bd else ""
