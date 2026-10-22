"""Phiếu hết hiệu lực (spec 3 §6.3, §6.5, §6.6, §7.6) — MỘT giao dịch: đánh dấu kết thúc → snapshot (khi không `xong`)
→ quyết toán ngân sách của phiếu → công việc chờ phần 4 xử lý → yêu cầu chấm lại 1a. Sự kiện `giao.ket_thuc` của
phần 4 chỉ là xác nhận đã xử lý pipeline, không phải định nghĩa thứ hai của hiệu lực."""
import json
import math
from datetime import datetime

from tram.duong_dan import doc_luc
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.kho import BanGhiPhieu, KhoPhieu, chuoi_gio


def snapshot_cua(kho: KhoPhieu, du_an: str, bead_id: str, cha: str) -> str:
    """SHA mới nhất trong `giao.cong_bo` của bead (do trạm ghi — §6.4, chờ S7), không có thì `cha` của phiếu."""
    h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'giao.cong_bo'"
                       " ORDER BY id DESC LIMIT 1", (du_an, bead_id)).fetchone()
    return json.loads(h[0])["commit"] if h else cha


def quyet_toan(kho: KhoPhieu, b: BanGhiPhieu, moc_cuoi: datetime) -> dict:
    """Lần chạy đếm từ `chay.bat_dau` (bảng `lan_chay`, duy nhất theo request_id). Lần chạy thiếu `chay.xong` →
    cộng phần giữ trước của một lần (thời gian và token) — KHÔNG tính bằng 0 (§7.6)."""
    p, ns = b.phieu, b.phieu.ngan_sach
    lan = kho.db.execute("SELECT COUNT(*) FROM lan_chay WHERE giao_id = ?", (p.giao_id,)).fetchone()[0]
    xong = [json.loads(d) for (d,) in kho.db.execute(
        "SELECT du_lieu FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'chay.xong'"
        " AND json_extract(du_lieu, '$.giao_id') = ?", (p.du_an, p.bead_id, p.giao_id))]
    thieu = max(0, lan - len(xong))
    da_qua = max(0, math.ceil((moc_cuoi - doc_luc(b.cap_luc)).total_seconds() / 60))
    return {"lan_chay": lan, "thieu_chay_xong": thieu,
            "phut": da_qua + thieu * math.ceil(ns.phut / ns.so_lan_chay),
            "token_ra": sum(int(x.get("token_ra") or 0) for x in xong)
            + thieu * math.ceil(ns.token_ra / ns.so_lan_chay)}


def ket_thuc_phieu(kho: KhoPhieu, b: BanGhiPhieu, *, ket_thuc: str, su_kien_id: int, luc: datetime,
                   moc_cuoi: datetime) -> dict:
    """Trong giao dịch của người gọi. `su_kien_id` = sự kiện báo kết thúc / `giao.thu_hoi` đã ghi."""
    p = b.phieu
    danh_dau_ket_thuc(kho.db, p.giao_id, ket_thuc, luc)
    snap = None
    if ket_thuc != "xong":
        snap = snapshot_cua(kho, p.du_an, p.bead_id, p.repo.cha)
        kho.ghi_su_kien(p.du_an, "giao.snapshot", {"bead_id": p.bead_id, "luot": p.luot, "commit": snap},
                        luc=luc, bead_id=p.bead_id)
    qt = quyet_toan(kho, b, moc_cuoi)
    kho.db.execute("UPDATE giu_ngan_sach SET quyet_toan = ? WHERE giao_id = ?", (json.dumps(qt), p.giao_id))
    kho.db.execute("INSERT INTO cong_viec_cho (giao_id, du_an, bead_id, ket_thuc, su_kien_id, luc)"
                   " VALUES (?,?,?,?,?,?)", (p.giao_id, p.du_an, p.bead_id, ket_thuc, su_kien_id, chuoi_gio(luc)))
    kho.db.execute("INSERT OR IGNORE INTO yeu_cau_cham_lai (du_an, bead_id, nguon_id, nguon) VALUES (?,?,?,'phieu')",
                   (p.du_an, p.bead_id, su_kien_id))
    return {"snapshot": snap, "quyet_toan": qt}


def thu_hoi(kho: KhoPhieu, b: BanGhiPhieu, *, ly_do: str, luc: datetime) -> dict:
    """Trong giao dịch. `giao.thu_hoi {giao_id, luot, ly_do}`; thời gian quyết toán tới nhịp tim cuối."""
    p = b.phieu
    sk = kho.ghi_su_kien(p.du_an, "giao.thu_hoi", {"giao_id": p.giao_id, "luot": p.luot, "ly_do": ly_do},
                         luc=luc, bead_id=p.bead_id)
    return ket_thuc_phieu(kho, b, ket_thuc="thu_hoi", su_kien_id=sk, luc=luc,
                          moc_cuoi=doc_luc(b.nhip_cuoi or b.cap_luc))
