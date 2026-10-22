"""Bảng điểm thợ theo (khe, vai) — spec 2 §5.4; công thức ở spec 4 §12.

Từ kho phiếu của phần 3: số phiếu, số phiếu kết thúc `xong`, và *số lần chạy trung bình* = trung bình số
`chay.bat_dau` (bảng `lan_chay`, duy nhất theo `request_id`) trên các phiếu ĐÃ kết thúc. *Qua lần đầu* và *bị trả
về* (lát 2d) tính từ sự kiện phần 4 trong `tram/suy/diem_giao_viec.py`, chỉ cho vai `coder`; kèm cỡ mẫu `*_mau`.
Mẫu 0 → tỉ lệ `null` (không hiện 0 giả); vai khác → tỉ lệ và mẫu đều `null` (D29).
Lọc (D14): `du_an` (None = mọi dự án) và `tu` (UTC; None = từ đầu) áp cho MỌI cột, theo phiếu (D28, D29)."""
import sqlite3

from tram.suy.diem_giao_viec import bi_tra_ve, dieu_kien_phieu, doc_phieu_code, doc_su_kien, qua_lan_dau


def _ti_le(x: tuple[int, int]) -> tuple[float | None, int]:
    tu, mau = x
    return (round(tu / mau, 4) if mau else None), mau


def bang_diem(db: sqlite3.Connection, *, du_an: str | None = None, tu: str | None = None) -> list[dict]:
    lan = dict(db.execute("SELECT giao_id, COUNT(*) FROM lan_chay GROUP BY giao_id").fetchall())
    loc, tham = dieu_kien_phieu(du_an, tu)
    nhom: dict[tuple[str, str], dict] = {}
    for giao_id, khe_id, vai, trang_thai, ket_thuc in db.execute(
            "SELECT giao_id, khe_id, json_extract(noi_dung, '$.vai'), trang_thai, ket_thuc"
            f" FROM phieu WHERE 1 = 1{loc} ORDER BY giao_id", tham):
        x = nhom.setdefault((khe_id, vai), {"so_phieu": 0, "so_xong": 0, "lan": []})
        x["so_phieu"] += 1
        x["so_xong"] += ket_thuc == "xong"
        if trang_thai == "ket_thuc":
            x["lan"].append(lan.get(giao_id, 0))
    phieu, sk = doc_phieu_code(db, du_an, tu), doc_su_kien(db, du_an)
    qld, btv = qua_lan_dau(phieu, sk), bi_tra_ve(phieu, sk)
    ra = []
    for (k, v), x in sorted(nhom.items()):
        h = {"khe_id": k, "vai": v, "so_phieu": x["so_phieu"], "so_xong": x["so_xong"],
             "lan_chay_tb": round(sum(x["lan"]) / len(x["lan"]), 2) if x["lan"] else None,
             "qua_lan_dau": None, "qua_lan_dau_mau": None, "bi_tra_ve": None, "bi_tra_ve_mau": None}
        if v == "coder":
            h["qua_lan_dau"], h["qua_lan_dau_mau"] = _ti_le(qld.get(k, (0, 0)))
            h["bi_tra_ve"], h["bi_tra_ve_mau"] = _ti_le(btv.get(k, (0, 0)))
        ra.append(h)
    return ra
