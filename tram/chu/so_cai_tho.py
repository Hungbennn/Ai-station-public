"""Sổ cài đặt máy thợ v2 — journal (lát 3c R2, Codex F02; R4 review đợt 5). `~/.tram/cai-dat-tho/so-cai.jsonl`, mỗi
dòng một bản ghi, CHỈ ghi thêm: `du_dinh` (kieu user|nha|tep|thu_muc, ten, mong — GHI TRƯỚC lệnh tạo), `da_tao`
(+dinh_danh, sau khi QUAN SÁT đúng định danh mong đợi), `khong_tao` (+ly_do), `da_go`. Trạng thái = bản ghi cuối của id.
Mọi lần ghi — và cả lần cài/gỡ, qua `giu()` — giữ khoá `so-cai.jsonl.khoa`; dưới khoá, đuôi dở được cắt (giữ bằng
chứng ở `.duoi-hong`) TRƯỚC khi nối, rồi ghi đủ bytes + fsync (`nhat_ky.py`). Lệnh tạo chỉ chạy SAU khi `du_dinh` đã
fsync, nên bỏ đuôi dở không làm mất dấu tài nguyên nào. Dòng hỏng ở giữa → ValueError (không cài/gỡ gì theo sổ hỏng).
`doi_soat` khép `du_dinh` dở bằng quan sát: đúng định danh mong đợi → `da_tao`, còn lại → `khong_tao`."""
import json
import secrets
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from tram.chu.nhat_ky import DangBan, cat_duoi, dong_hoan_chinh, ghi_het, khoa
from tram.duong_dan import tram_home

PHIEN_BAN = 2
KIEU = ("thanh_vien", "acl_search", "nhom", "user", "nha", "tep", "thu_muc")
SU = ("du_dinh", "da_tao", "khong_tao", "da_go")
CHUYEN = {"du_dinh": ("da_tao", "khong_tao"), "da_tao": ("da_go",)}     # chuyển trạng thái hợp lệ


class SoCaiDangBan(DangBan):
    """Đang có `cai-dat-tho`/`go-cai-dat-tho` khác giữ khoá sổ."""


@dataclass(frozen=True)
class Muc:
    id: str
    kieu: str
    ten: str
    mong: dict
    su: str = "du_dinh"
    dinh_danh: dict | None = None


class SoCai:
    def __init__(self, p: Path | None = None):
        self.p = p or tram_home() / "cai-dat-tho" / "so-cai.jsonl"
        self._giu = False

    def _hong(self, ly_do: str) -> ValueError:
        return ValueError(f"Sổ cài đặt {self.p} hỏng ({ly_do}) — không cài/gỡ gì theo sổ này, Đại ca kiểm tay")

    @contextmanager
    def giu(self):
        """Khoá giao dịch cài/gỡ (không chờ); lồng trong cùng đối tượng thì dùng lại khoá đang giữ."""
        if self._giu:
            yield self
            return
        with khoa(self.p.with_name(self.p.name + ".khoa"), f"đang có cài/gỡ khác giữ sổ {self.p} — chạy lại sau",
                  loi=SoCaiDangBan):
            self._giu = True
            try:
                yield self
            finally:
                self._giu = False

    def muc(self) -> dict[str, Muc]:
        ra: dict[str, Muc] = {}
        for d in dong_hoan_chinh(self.p.read_bytes() if self.p.exists() else b""):
            try:
                x = json.loads(d.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise self._hong("dòng không phải JSON UTF-8") from None
            if not isinstance(x, dict) or x.get("v") != PHIEN_BAN or not isinstance(x.get("id"), str) \
                    or x.get("su") not in SU:
                raise self._hong("bản ghi sai dạng")
            if x["su"] == "du_dinh":
                if x.get("kieu") not in KIEU or not isinstance(x.get("ten"), str) \
                        or not isinstance(x.get("mong"), dict):
                    raise self._hong("du_dinh sai dạng")
                ra[x["id"]] = Muc(x["id"], x["kieu"], x["ten"], x["mong"])
            elif x["id"] not in ra or x["su"] not in CHUYEN.get(ra[x["id"]].su, ()):
                raise self._hong(f"{x['su']} không theo sau trạng thái hợp lệ")
            elif not isinstance(x.get("dinh_danh", {}), dict):
                raise self._hong("dinh_danh sai dạng")
            else:
                ra[x["id"]] = replace(ra[x["id"]], su=x["su"], dinh_danh=x.get("dinh_danh", ra[x["id"]].dinh_danh))
        return ra

    def _ghi(self, x: dict) -> None:
        with self.giu():
            cat_duoi(self.p)                     # đuôi dở (crash/short write): giữ bằng chứng rồi cắt, không nối vào
            ghi_het(self.p, (json.dumps({"v": PHIEN_BAN, **x}, ensure_ascii=False) + "\n").encode())

    def du_dinh(self, id_: str, kieu: str, ten: str, mong: dict) -> None:
        self._ghi({"id": id_, "su": "du_dinh", "kieu": kieu, "ten": ten, "mong": mong,
                   "luc": datetime.now(timezone.utc).isoformat(timespec="seconds")})

    def ket(self, id_: str, su: str, **kw) -> None:
        self._ghi({"id": id_, "su": su, **kw})

    def da_tao(self, kieu: str, ten: str) -> list[Muc]:
        return [m for m in self.muc().values() if (m.kieu, m.ten, m.su) == (kieu, ten, "da_tao")]

    def co_ghi(self, kieu: str, ten: str) -> bool:
        """Sổ có ghi trạm tạo (hoặc đang tạo dở) tài nguyên này."""
        return any((m.kieu, m.ten) == (kieu, ten) and m.su in ("du_dinh", "da_tao") for m in self.muc().values())


def moi_id() -> str:
    return secrets.token_hex(8)


def doi_soat(so: SoCai, quan_sat: Callable, khop: Callable) -> int:
    """Khép mọi `du_dinh` dở dang bằng quan sát. Trả số mục đã khép."""
    dem = 0
    for m in [m for m in so.muc().values() if m.su == "du_dinh"]:
        hien = quan_sat(m.kieu, m.ten)
        if hien is not None and khop(m.kieu, m.mong, hien):
            so.ket(m.id, "da_tao", dinh_danh=hien, doi_soat=True)
        else:
            so.ket(m.id, "khong_tao", ly_do="đối soát: không thấy tài nguyên đúng định danh mong đợi")
        dem += 1
    return dem
