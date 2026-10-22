"""Đề nghị đang chờ ghi (design D-4) — tính lúc đọc từ sự kiện, không bảng mới: `bao.tien_do`, `bao.viec_moi`,
`bao.bi`, `bao.can_hoi` mang `ma_de_nghi` (do `nhan.py` gắn lúc nhận) mà chưa có `de_nghi.da_ghi` hay `de_nghi.bo`
cùng mã. Sự kiện kết quả (`de_nghi.*`) ghi đúng một lần theo mã đề nghị, tác nhân `tram/de-nghi`."""
import json
from dataclasses import dataclass
from datetime import datetime

from tram.de_nghi.bi_chan import ma_escalation_cua
from tram.giao_viec.su_kien import da_co

TAC_NHAN = "tram/de-nghi"
LOAI_BAO = {"bao.tien_do": "tien_do", "bao.viec_moi": "viec_moi", "bao.bi": "bi_chan", "bao.can_hoi": "bi_chan"}


@dataclass(frozen=True)
class Cho:
    id: int                 # id sự kiện `bao.*` — thứ tự nhận
    nguon: str              # loại sự kiện `bao.*`
    du_an: str
    bead_id: str
    loai: str               # tien_do | viec_moi | bi_chan
    ma: str
    giao_id: str
    luot: int
    khe: str
    du_lieu: dict


def de_nghi_cho(kho) -> list[Cho]:
    xong = {m for (m,) in kho.db.execute("SELECT json_extract(du_lieu, '$.ma_de_nghi') FROM su_kien WHERE loai IN"
                                         " ('de_nghi.da_ghi', 'de_nghi.bo')")}
    ra = []
    for i, loai, du_an, bead_id, tac_nhan, d in kho.db.execute(
            "SELECT id, loai, du_an, bead_id, tac_nhan, du_lieu FROM su_kien WHERE loai IN (?, ?, ?, ?) AND"
            " json_extract(du_lieu, '$.ma_de_nghi') IS NOT NULL ORDER BY id", tuple(LOAI_BAO)):
        d = json.loads(d)
        if d["ma_de_nghi"] not in xong:
            ra.append(Cho(i, loai, du_an, bead_id, LOAI_BAO[loai], d["ma_de_nghi"], d["giao_id"], d["luot"],
                          tac_nhan.removeprefix("tho/"), d))
    return ra


def escalation_cua(kho, c: Cho) -> str | None:
    """`escalation_id` luồng sẵn có đã tạo cho báo bí / cần hỏi này; None = chưa tạo (chờ nhịp sau)."""
    ma = ma_escalation_cua(c.du_an, c.bead_id, c.nguon, c.id, c.du_lieu)
    h = kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE du_an = ? AND loai ="
                       " 'escalation.tao' AND json_extract(du_lieu, '$.ma_thao_tac') = ? LIMIT 1", (c.du_an, ma))
    return (h.fetchone() or (None,))[0]


def ghi_ket_qua(kho, c: Cho, loai_sk: str, du_lieu: dict, *, luc: datetime) -> bool:
    """`de_nghi.da_ghi` / `de_nghi.bo` / `de_nghi.loi_ghi` một lần theo mã đề nghị (+ mã lỗi) — không nội dung."""
    khoa = {"ma_de_nghi": c.ma, **({"ma_loi": du_lieu["ma_loi"]} if "ma_loi" in du_lieu else {})}
    with kho.giao_dich():
        if da_co(kho, c.du_an, loai_sk, khoa):
            return False
        kho.ghi_su_kien(c.du_an, loai_sk, {"ma_de_nghi": c.ma, "loai": c.loai, **du_lieu}, luc=luc,
                        bead_id=c.bead_id, tac_nhan=TAC_NHAN)
        return True
