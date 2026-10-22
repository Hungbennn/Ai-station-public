"""Nhân vật của Văn phòng 3D (spec 2 §5.5): mỗi khe một nhân vật, trạng thái lấy từ `trang_thai_khe` của phần 3
(spec 3 §10.1) — KHÔNG có định nghĩa trạng thái thứ hai. Thêm hai việc chỉ để hiển thị:
- `hien_thi`: sáu giá trị gộp thành năm hàng của bảng §5.5 (`mat_ket_noi` → hàng "Tắt / mất kết nối");
- khe `ranh` mà phiếu cuối có escalation chưa đóng (`escalation.tao` cùng `giao_id`, chưa `escalation.dong` — sự
  kiện của 4a-1) → `can_nguoi` (spec 3 §10.1 "escalation liên kết chưa đóng"; plan 2c G3).
Không trả `ten_goi_nho` (có thể là email — §5.4) và không đọc cột nào chứa `ma_giao`."""
import re

from tram.phieu.kho import KhoPhieu
from tram.phieu.trang_thai import TrangThaiKhe
from tram.suy.lam_sach import lam_sach

HIEN_THI = {"lam": "lam", "ranh": "ranh", "can_nguoi": "can_nguoi", "loi": "loi", "tat": "tat", "mat_ket_noi": "tat"}
TEN_CLI = {"claude": "Claude", "codex": "Codex"}
CA_PHE = "ca-phe"


def ma_phong_du_an(du_an: str) -> str:
    return f"du-an:{du_an}"


def ten_nhan_vat(cac: list[tuple[str, str]]) -> dict[str, str]:
    """`[(khe_id, cli)]` → tên "<CLI> <số khe>"; trùng tên giữa các máy thì thêm "(<máy>)"."""
    ten = {}
    for khe_id, cli in cac:
        may, _, rieng = khe_id.partition("/")
        so = re.search(r"(\d+)$", rieng)
        ten[khe_id] = f"{TEN_CLI.get(cli, lam_sach(cli, 32).capitalize())} {so.group(1) if so else rieng}"
    dem: dict[str, int] = {}
    for t in ten.values():
        dem[t] = dem.get(t, 0) + 1
    return {k: (f"{t} ({k.split('/')[0]})" if dem[t] > 1 else t) for k, t in ten.items()}


def _phieu_cuoi(kho: KhoPhieu, khe_id: str) -> dict | None:
    h = kho.db.execute("SELECT giao_id, du_an, bead_id, json_extract(noi_dung, '$.buoc'),"
                       " json_extract(noi_dung, '$.tieu_de'), trang_thai FROM phieu WHERE khe_id = ?"
                       " ORDER BY rowid DESC LIMIT 1", (khe_id,)).fetchone()
    return None if h is None else dict(zip(("giao_id", "du_an", "bead_id", "buoc", "tieu_de", "trang_thai"), h))


def _escalation_mo(kho: KhoPhieu, du_an: str, giao_id: str) -> bool:
    return kho.db.execute(
        "SELECT 1 FROM su_kien t WHERE t.du_an = ? AND t.loai = 'escalation.tao'"
        " AND json_extract(t.du_lieu, '$.giao_id') = ? AND NOT EXISTS (SELECT 1 FROM su_kien d WHERE d.du_an = t.du_an"
        " AND d.loai = 'escalation.dong' AND json_extract(d.du_lieu, '$.escalation_id') ="
        " json_extract(t.du_lieu, '$.escalation_id')) LIMIT 1", (du_an, giao_id)).fetchone() is not None


def _bead(p: dict) -> dict:
    return {"du_an": p["du_an"], "bead_id": p["bead_id"], "tieu_de": lam_sach(p["tieu_de"] or "", 120),
            "buoc": p["buoc"]}


def _mot(kho: KhoPhieu, tt: TrangThaiKhe, ten: str, cac_du_an: list[str]) -> dict:
    trang_thai, bead, cuoi = tt.trang_thai, None, None
    if tt.phieu is not None:
        bead = _bead(tt.phieu)
    elif trang_thai != "lam":
        cuoi = _phieu_cuoi(kho, tt.khe_id)
        if (trang_thai in ("ranh", "loi") and not tt.cau_dao.get("ngat") and cuoi is not None
                and cuoi["trang_thai"] == "ket_thuc" and _escalation_mo(kho, cuoi["du_an"], cuoi["giao_id"])):
            trang_thai, bead = "can_nguoi", _bead(cuoi)
    noi = bead or (cuoi if trang_thai != "ranh" else None)
    phong = ma_phong_du_an(noi["du_an"]) if noi and noi["du_an"] in cac_du_an else CA_PHE
    return {"khe_id": tt.khe_id, "ten": ten, "cli": lam_sach(tt.cli, 32), "trang_thai": trang_thai,
            "hien_thi": HIEN_THI.get(trang_thai, "tat"), "phong": phong, "bead": bead,
            "cau_dao_ngat": bool(tt.cau_dao.get("ngat"))}        # 2f T2: nhãn "Lỗi · cầu dao ngắt"


def nhan_vat(kho: KhoPhieu, ds: list[TrangThaiKhe], cac_du_an: list[str]) -> list[dict]:
    ten = ten_nhan_vat([(t.khe_id, t.cli) for t in ds])
    return [_mot(kho, t, ten[t.khe_id], cac_du_an) for t in ds]
