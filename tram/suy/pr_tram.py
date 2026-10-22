"""PR do trạm mở (lát 4c) trên thẻ cột 3 — spec 2 §5.2, spec 4 §6.5; plan 2d G10–G13.

Chỉ đọc sự kiện `pr.mo` (loại `bead`), `pr.da_merge`, `pr.khong_xac_minh` ghi SAU `bead.vao_cot_3` đang hiện và
cùng `commit_ban_giao` — trả về vòng trước không còn dính. Mọi chuỗi trả về dựng từ hằng số, số PR nguyên và URL
GitHub đã kiểm dạng; không lấy chữ từ GitHub hay từ notes của agent."""
import re

URL_PR = re.compile(r"https://github\.com/[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}/pull/[0-9]{1,9}")
LY_DO = {   # mã của tram/giao_viec/pr_merge.py::ly_do_khong_xac_minh
    "pr-khac": "PR trên GitHub không còn là PR trạm đã mở",
    "sai-nhanh": "PR không đi từ nhánh tram/<bead> của cùng repo",
    "sai-nhanh-chinh": "PR không merge vào nhánh chính của dự án",
    "thieu-merge-commit": "GitHub không trả merge commit",
    "merge-khong-tren-nhanh-chinh": "merge commit không nằm trên nhánh chính",
    "khong-phai-merge-commit": "không phải merge commit (squash / rebase)",           # chữ mockup (D20)
    "head-khac-commit-ban-giao": "head của PR khác commit trạm đã kiểm",
}
LY_DO_KHAC = "lý do khác — xem nhật ký sự kiện của bead"


def pr_tram(kho, du_an: str, bead_id: str, vao_cot_3) -> dict | None:
    """`{so, url, trang_thai: mo | khong_xac_minh | da_merge, ly_do}` hoặc None khi trạm chưa mở PR."""
    c = vao_cot_3.du_lieu.get("commit_ban_giao")

    def sau(s) -> bool:
        return s.id > vao_cot_3.id and s.du_lieu.get("commit") == c

    mo = kho.moi_nhat(du_an, bead_id, "pr.mo", dieu_kien=lambda s: sau(s) and s.du_lieu.get("loai") == "bead")
    if mo is None:
        return None
    so, url = mo.du_lieu.get("pr"), mo.du_lieu.get("url")
    ra = {"so": so if type(so) is int else None,
          "url": url if isinstance(url, str) and URL_PR.fullmatch(url) else None,
          "trang_thai": "mo", "ly_do": None}
    if kho.moi_nhat(du_an, bead_id, "pr.da_merge", dieu_kien=sau) is not None:
        return {**ra, "trang_thai": "da_merge"}
    kx = kho.moi_nhat(du_an, bead_id, "pr.khong_xac_minh", dieu_kien=sau)
    if kx is not None:
        return {**ra, "trang_thai": "khong_xac_minh", "ly_do": LY_DO.get(kx.du_lieu.get("ly_do"), LY_DO_KHAC)}
    return ra
