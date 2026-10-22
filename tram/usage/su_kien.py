"""Usage từ sự kiện của trạm (spec 2 §5.4; §12.2: dùng cột `token_vao`, `token_ra`, `mo_hinh` đã lưu riêng).

Hai nguồn: `chay.xong` (mỗi lần chạy CLI của một khe — spec 3 §10; token cache nằm trong `du_lieu`) và
`cham_cot.ket_qua` (bộ chấm cột 1a gọi Claude API). Ngày/tuần tính theo giờ Việt Nam, tuần theo ISO."""
import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from tram.cham_cot.ghi import GIO_VN
from tram.duong_dan import doc_luc

LOAI = ("chay.xong", "cham_cot.ket_qua")
NGUON_CHAM = "cham-cot"
TRUONG = ("token_vao", "token_ra", "token_cache_doc", "token_cache_ghi")


@dataclass(frozen=True)
class DongUsage:
    ngay: date
    nguon: str                 # khe_id ("B/claude-1") hoặc "cham-cot"
    du_an: str
    mo_hinh: str | None
    token_vao: int
    token_ra: int
    token_cache_doc: int
    token_cache_ghi: int


def moc_utc(ngay: date) -> str:
    """00:00 giờ Việt Nam của `ngay`, viết theo UTC `YYYY-MM-DDTHH:MM:SSZ` (so sánh chuỗi với cột `luc`)."""
    return datetime.combine(ngay, time(0), GIO_VN).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _so(x) -> int:
    return x if isinstance(x, int) and not isinstance(x, bool) and x > 0 else 0


def doc_dong_usage(db: sqlite3.Connection, tu: date, den: date) -> list[DongUsage]:
    """Sự kiện có `luc` trong [00:00 VN ngày `tu`, 00:00 VN ngày sau `den`)."""
    ra = []
    for luc, du_an, loai, dl, tv, tr, mh in db.execute(
            "SELECT luc, du_an, loai, du_lieu, token_vao, token_ra, mo_hinh FROM su_kien"
            " WHERE loai IN (?, ?) AND luc >= ? AND luc < ? ORDER BY id",
            (*LOAI, moc_utc(tu), moc_utc(den + timedelta(days=1)))):
        d = json.loads(dl)
        nguon = str(d.get("khe_id") or "?") if loai == "chay.xong" else NGUON_CHAM
        ra.append(DongUsage(doc_luc(luc).astimezone(GIO_VN).date(), nguon, du_an, mh, _so(tv), _so(tr),
                            _so(d.get("token_cache_doc")), _so(d.get("token_cache_ghi"))))
    return ra


def _chi_phi(d: DongUsage, gia: dict[str, dict[str, float]]) -> float | None:
    g = gia.get(d.mo_hinh or "")
    if g is None:
        return None
    return (d.token_vao * g["vao"] + d.token_ra * g["ra"] + d.token_cache_doc * g["cache_doc"]
            + d.token_cache_ghi * g["cache_ghi"]) / 1_000_000


def _cong(bang: dict, khoa: str, d: DongUsage, chi_phi: float | None) -> None:
    x = bang.setdefault(khoa, {**dict.fromkeys(TRUONG, 0), "so_lan": 0, "chi_phi_usd": 0.0, "thieu_gia": 0})
    for t in TRUONG:
        x[t] += getattr(d, t)
    x["so_lan"] += 1
    if chi_phi is None:
        x["thieu_gia"] += 1
    else:
        x["chi_phi_usd"] += chi_phi


def tong_hop(dong: list[DongUsage], gia: dict[str, dict[str, float]]) -> dict[str, list[dict]]:
    """`theo_ngay`, `theo_tuan`, `theo_nguon`, `theo_du_an`: mỗi dòng `{khoa, token_*, so_lan, chi_phi_usd,
    thieu_gia}`; `chi_phi_usd` = None khi không dòng nào có giá (spec 2 §5.4 — chi phí ước tính từ bảng giá)."""
    nhom: dict[str, dict] = {"theo_ngay": {}, "theo_tuan": {}, "theo_nguon": {}, "theo_du_an": {}}
    for d in dong:
        cp, (nam, tuan, _) = _chi_phi(d, gia), d.ngay.isocalendar()
        for ten, khoa in (("theo_ngay", d.ngay.isoformat()), ("theo_tuan", f"{nam}-W{tuan:02d}"),
                          ("theo_nguon", d.nguon), ("theo_du_an", d.du_an)):
            _cong(nhom[ten], khoa, d, cp)
    return {ten: [{"khoa": k, **v, "chi_phi_usd": None if v["thieu_gia"] == v["so_lan"] else round(v["chi_phi_usd"], 4)}
                  for k, v in sorted(bang.items())] for ten, bang in nhom.items()}
