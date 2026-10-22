"""Trạng thái hiển thị của "agent tự cập nhật việc" (spec cong-tac-de-nghi-viec, de-nghi-viec-cua-agent; design D-9)
— tính lúc đọc từ sự kiện. Tiến độ đọc từ sự kiện của trạm, KHÔNG phân tích ghi chú Beads. Không bao giờ trả lý do bí
/ cần hỏi gốc (chỉ dòng đã lọc mới vào Beads) hay nội dung bị từ chối (không được lưu)."""
import json
import sqlite3
from dataclasses import asdict

from tram.de_nghi.cai_dat import doc_cai_dat, lich_su_doi

LOAI_BAO = {"bao.tien_do": "tien_do", "bao.viec_moi": "viec_moi", "bao.bi": "bi_chan", "bao.can_hoi": "bi_chan"}
KET_QUA = {"de_nghi.da_ghi": "da_ghi", "de_nghi.bo": "bo", "de_nghi.loi_ghi": "loi_ghi"}
GIU = ("ly_do", "bead_moi", "escalation_id", "ma_loi")


def chi_tiet(db: sqlite3.Connection, ten: str, *, bat_ghi: bool, kenh_ghi: str, la_dai_ca: bool) -> dict:
    cd, pb = doc_cai_dat(db, ten)
    return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": asdict(cd), "phien_ban": pb, "kenh_ghi": kenh_ghi,
            "chi_tat": kenh_ghi == "header", "la_dai_ca": la_dai_ca, "lich_su_doi": lich_su_doi(db, ten)}


def _muc(loai: str, luc: str, tac_nhan: str, d: dict) -> dict:
    m = {"ma_de_nghi": d["ma_de_nghi"], "loai": LOAI_BAO[loai], "giao_id": d["giao_id"], "luot": d["luot"],
         "khe": tac_nhan.removeprefix("tho/"), "luc": luc, "ket_qua": "cho", "luc_ket_qua": None}
    if loai == "bao.tien_do":
        m["noi_dung"] = d["noi_dung"]
    if loai == "bao.viec_moi":
        m["tieu_de"] = d["viec_moi"]["tieu_de"]
    return m


def de_nghi_cua_bead(db: sqlite3.Connection, du_an: str, bead_id: str, *, bat_ghi: bool = True) -> list[dict]:
    """Dấu vết từng đề nghị của một việc (Scenario "Xem dấu vết của một phiếu"; tiến độ cho dashboard), mới → cũ. Dự
    án đang khoá ghi → đề nghị còn chờ mang `ly_do: khoa-ghi` (D134: giữ, mở khoá thì ghi bù)."""
    theo_ma, ra = {}, []
    for loai, luc, tac_nhan, d in db.execute(
            "SELECT loai, luc, tac_nhan, du_lieu FROM su_kien WHERE du_an = ? AND bead_id = ? AND (loai IN"
            " ('bao.tien_do', 'bao.viec_moi', 'bao.bi', 'bao.can_hoi') OR loai LIKE 'de_nghi.%') ORDER BY id",
            (du_an, bead_id)):
        d = json.loads(d)
        if loai in LOAI_BAO and "ma_de_nghi" in d:
            theo_ma[d["ma_de_nghi"]] = _muc(loai, luc, tac_nhan, d)
            ra.append(theo_ma[d["ma_de_nghi"]])
        elif loai == "de_nghi.tu_choi":
            ra.append({"ma_de_nghi": None, "loai": d["loai"], "giao_id": d["giao_id"], "luot": d["luot"], "khe": None,
                       "luc": luc, "ket_qua": "tu_choi", "luc_ket_qua": luc, "ly_do": d["ly_do"]})
        elif loai in KET_QUA and (m := theo_ma.get(d.get("ma_de_nghi"))) is not None:
            m.update({"ket_qua": KET_QUA[loai], "luc_ket_qua": luc, **{k: d[k] for k in GIU if k in d}})
    for m in ra if not bat_ghi else ():
        if m["ket_qua"] == "cho":
            m["ly_do"] = "khoa-ghi"
    return ra[::-1]
