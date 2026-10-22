"""Nhận đề nghị trong `nhan_bao` (spec de-nghi-viec-cua-agent, design D-2, D-4) — gọi TRONG giao dịch của `nhan_bao`,
SAU thẻ chắn lượt, TRƯỚC khi ghi `bao.<loại>`.

- Tiến độ / việc mới: lọc (D-3) → phiếu `spec` không được việc mới (D103) → đếm theo phiếu: ≥ 20 tiến độ hay ≥ 5 việc
  mới → `qua-gioi-han` (D83, D106) → mã đề nghị → nút lúc nhận: tắt → vẫn nhận, rồi bỏ ngay (`tat`); dự án đang
  khoá ghi (`bat_ghi: false`) → nhận và GIỮ chờ (`cho: khoa-ghi`), mở khoá thì vòng tick ghi bù nếu còn đủ điều kiện
  (D134). Từ chối → `TuChoiDeNghi` (422 dứt khoát; hộp thư phía thợ không gửi lại).
- Báo bí của agent (`ly_do: agent`) / cần hỏi: KHÔNG bao giờ bị từ chối (phiếu phải dừng được). Khi nút dự án bật thì
  mang mã đề nghị loại `bi_chan` để vòng tick thêm dòng "bị chặn" (D-6, D102); nút dự án tắt → không thêm dấu vết.

Mã đề nghị `dn-<20 hex>` = băm (dự án, giao_id, request_id) do trạm tính — agent không chọn được (D-2)."""
import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from tram.de_nghi.cai_dat import bat_ghi_an_toan, doc_cai_dat
from tram.de_nghi.loc import LOAI_DE_NGHI, loc

TOI_DA = {"tien_do": 20, "viec_moi": 5}
TAC_NHAN = "tram/api"


class TuChoiDeNghi(Exception):
    """422 `{ly_do}` — chỉ mã lý do; `nhom` (khi có bí mật) chỉ là nhóm + số lượng."""

    def __init__(self, loai: str, ly_do: str, nhom: dict | None = None):
        super().__init__(ly_do)
        self.loai, self.ly_do, self.nhom = loai, ly_do, dict(nhom or {})


@dataclass(frozen=True)
class DeNghi:
    ma: str
    loai: str               # tien_do | viec_moi | bi_chan
    bo: str | None          # tat — bỏ ngay lúc nhận; None = chờ vòng tick ghi
    giu: str | None = None  # khoa-ghi — dự án đang khoá ghi: chờ, mở khoá thì ghi bù (D134)

    def ket_qua(self) -> dict:
        return {"ma_de_nghi": self.ma, "se_ghi": self.bo is None, **({"ly_do": self.bo} if self.bo else {}),
                **({"cho": self.giu} if self.giu else {})}


def ma_de_nghi(du_an: str, giao_id: str, request_id: str) -> str:
    return "dn-" + hashlib.sha256(f"{du_an}:{giao_id}:{request_id}".encode()).hexdigest()[:20]


def _da_nhan(kho, p, loai: str) -> int:
    return kho.db.execute("SELECT COUNT(*) FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = ? AND"
                          " json_extract(du_lieu, '$.giao_id') = ?", (p.du_an, p.bead_id, f"bao.{loai}",
                                                                     p.giao_id)).fetchone()[0]


def xet_de_nghi(kho, p, than: dict, *, bat_ghi: Callable[[str], bool]) -> DeNghi | None:
    """`than` = `ThanBao.model_dump()`; `p` = phiếu hiệu lực (đã qua thẻ chắn). None = không phải đề nghị."""
    loai = than["loai"]
    if loai in LOAI_DE_NGHI:
        if (loi := loc(loai, than)) is not None:
            raise TuChoiDeNghi(loai, loi.ly_do, loi.nhom)
        if loai == "viec_moi" and p.buoc == "spec":
            raise TuChoiDeNghi(loai, "phieu-khong-ho-tro")
        if _da_nhan(kho, p, loai) >= TOI_DA[loai]:
            raise TuChoiDeNghi(loai, "qua-gioi-han")
    elif not (loai == "bi" and than.get("ly_do") == "agent" or loai == "can_hoi"):
        return None
    cd = doc_cai_dat(kho.db, p.du_an)[0]
    if loai not in LOAI_DE_NGHI:
        if not cd.bat:
            return None                       # tính năng tắt: escalation như cũ, không thêm dấu vết
        loai = "bi_chan"
    ma = ma_de_nghi(p.du_an, p.giao_id, than["request_id"])
    if not cd.cho_ghi(loai):
        return DeNghi(ma, loai, "tat")
    return DeNghi(ma, loai, None, None if bat_ghi_an_toan(bat_ghi, p.du_an) else "khoa-ghi")


def ghi_tu_choi(kho, p, e: TuChoiDeNghi, *, luot: int, luc: datetime) -> None:
    """`de_nghi.tu_choi` — KHÔNG nội dung (INV-001)."""
    kho.ghi_su_kien(p.du_an, "de_nghi.tu_choi", {"giao_id": p.giao_id, "luot": luot, "loai": e.loai,
                                                 "ly_do": e.ly_do, **({"nhom": e.nhom} if e.nhom else {})},
                    luc=luc, bead_id=p.bead_id, tac_nhan=TAC_NHAN)


def ghi_bo(kho, p, dn: DeNghi, *, luc: datetime) -> None:
    kho.ghi_su_kien(p.du_an, "de_nghi.bo", {"ma_de_nghi": dn.ma, "loai": dn.loai, "ly_do": dn.bo}, luc=luc,
                    bead_id=p.bead_id, tac_nhan=TAC_NHAN)
