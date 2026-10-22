"""Hàng đợi riêng từng dự án/pha. Mọi giá trị dữ liệu dùng SQL parameters."""
from tram.phieu.cong_viec import CongViecCho


def viec_cua_pha(kho, du_an: str, *, git: bool, gioi_han: int = 1000) -> list[CongViecCho]:
    so_sanh = "=" if git else "<>"
    sql = ("SELECT id,giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc FROM cong_viec_cho "
           f"WHERE xong_luc IS NULL AND du_an = ? AND ket_thuc {so_sanh} 'xong' ORDER BY id LIMIT ?")
    return [CongViecCho(*h) for h in kho.db.execute(sql, (du_an, gioi_han))]
