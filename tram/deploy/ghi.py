"""Ghi sự kiện `deploy.*` đúng hợp đồng TM-1 (plan TM-1 mục "Interfaces cho lát sau"), tác nhân `tram/tu-deploy`.
`deploy.xong` ghi CÙNG MỘT giao dịch với hệ quả của nó (tự tắt, tạm dừng — qua `tram.tu_dong.luu`, chỉ gọi), nên
trạm chết giữa chừng không để lại "đã hỏng lần 3 mà chưa tắt". `deploy.yeu_cau` (nút Deploy) và `deploy.huy` là hai
loại TM-3 thêm, không có tin Telegram (`nguon_tu_dong` bỏ qua loại lạ)."""
import hashlib
import sqlite3
from dataclasses import replace

from tram.deploy.trang_thai import HONG, TAC_NHAN, dem_hong, doc_su_kien
from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung, giao_dich

TU_TAT_SAU = 3          # D75: hỏng 3 lần liên tiếp thì tự tắt tự deploy


def ma_chuoi(du_an: str, commit: str, nguon: str, ma_yeu_cau: str) -> str:
    """D-7: `dp-` + sha256(dự án, commit, nguồn, mã yêu cầu) — cùng yêu cầu không bao giờ thành hai chuỗi."""
    return "dp-" + hashlib.sha256("\0".join((du_an, commit, nguon, ma_yeu_cau)).encode()).hexdigest()[:40]


def ghi(db: sqlite3.Connection, du_an: str, loai: str, du_lieu: dict) -> int:
    with giao_dich(db):
        return ghi_trong_giao_dich(db, du_an, loai, du_lieu, tac_nhan=TAC_NHAN, luc=bay_gio())


def ket_thuc(db: sqlite3.Connection, du_an: str, ma: str, ket_qua: str) -> int:
    """`deploy.xong {ma_thao_tac, ket_qua, dem_hong}` + hệ quả; trả bộ đếm hỏng sau lần này.
    Hỏng (`da_lui`) lần thứ 3 liên tiếp → tắt tự deploy, `ly_do: hong-3-lan` (D75). Lùi hỏng → tắt tự deploy và
    TẠM DỪNG dự án, `lui-hong` (D97 luật 1). Không rõ kết quả → TẠM DỪNG dự án, `khong-ro` (Đại ca chốt 18/10, câu 3
    plan TM-1); không tính là một lần hỏng."""
    with giao_dich(db):
        cu = next((s for s in doc_su_kien(db, du_an) if s.loai == "deploy.xong"
                   and s.du_lieu.get("ma_thao_tac") == ma), None)
        if cu is not None:
            return cu.du_lieu["dem_hong"]
        dem = 0 if ket_qua == "dat" else dem_hong(doc_su_kien(db, du_an)) + (ket_qua in HONG)
        ghi_trong_giao_dich(db, du_an, "deploy.xong", {"ma_thao_tac": ma, "ket_qua": ket_qua, "dem_hong": dem},
                            tac_nhan=TAC_NHAN, luc=bay_gio())
        tat = "lui-hong" if ket_qua == "lui_hong" else ("hong-3-lan" if ket_qua in HONG and dem >= TU_TAT_SAU else "")
        if ket_qua == "khong_ro" and any(s.loai == "deploy.lenh" and s.du_lieu.get("ma_thao_tac") == ma
                and s.du_lieu.get("buoc") in ("lui", "kiem_song_sau_lui")
                for s in doc_su_kien(db, du_an)):
            tat = "lui-hong"
        if tat:
            doi_cai_dat(db, du_an, lambda c: replace(c, tu_deploy=False), tac_nhan=TAC_NHAN, them={"ly_do": tat})
        if ket_qua in ("lui_hong", "khong_ro"):
            ghi_tam_dung(db, du_an, tam_dung=True, tac_nhan=TAC_NHAN, them={"ly_do": ket_qua.replace("_", "-")})
        return dem
