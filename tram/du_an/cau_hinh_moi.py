"""Bước (1) của `tram du-an them` (spec 0+1a §4.7): sinh `du-an/<ten>.yaml` bản nháp đúng schema `nap_du_an` (§4.2).

Hàng rào mặc định chung chỉ đẩy về cột 2 (§5.2) — Đại ca thêm từ khoá, đường dẫn riêng trước khi bật ghi.
"""
import json
import re
import tempfile
import unicodedata
from pathlib import Path

from tram.cau_hinh.du_an import nap_du_an

TEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")  # tập con của nho.pham_vi.TEN: tên dự án cũng là tên vùng nhớ
RAO_MAC_DINH: dict[str, list[str]] = {  # đủ bốn loại LOAI_HANG_RAO
    "tien": ["báo giá", "bảng giá", "thuế", "VAT", "hoa hồng", "hóa đơn", "hoá đơn", "hoàn tiền", "công nợ",
             "thanh toán", "đặt cọc", "giảm giá"],
    "schema": ["migration", "migrate", "schema", "thêm cột", "đổi cột", "xoá cột", "xóa cột", "khoá ngoại",
               "khóa ngoại", "FK", "index", "bảng mới"],
    "quyen": ["phân quyền", "quyền", "permission", "policy", "vai trò", "2FA", "đăng nhập", "mật khẩu", "bảo mật"],
    "khach_thay": ["email khách", "gửi khách", "website", "bản dịch", "khách nhìn thấy"],
}


def ten_tu_repo(repo: Path) -> str:
    """'HR Codex' → 'hr-codex'; bỏ dấu tiếng Việt, ký tự khác chữ/số thành '-'."""
    s = repo.name.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40].strip("-")


def kiem_ten(ten: str) -> str | None:
    if not isinstance(ten, str) or not TEN_RE.fullmatch(ten):
        return (f"tên dự án {ten!r} không hợp lệ: chỉ chữ thường không dấu, số và '-', tối đa 40 ký tự, "
                "không bắt đầu bằng '-' (dùng --ten)")
    return None


def _ds(xs: list[str]) -> str:
    return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in xs) + "]"


def tao_yaml(ten: str, repo: Path, gitnexus: str | None = None) -> str:
    """Chuỗi JSON là scalar YAML hợp lệ — dùng `json.dumps` để trích dẫn an toàn đường dẫn có dấu cách."""
    dong = [
        "# Bản nháp do `tram du-an them` sinh (spec 0+1a §4.2, §4.7). Đại ca xem lại trước khi bật ghi.",
        f"ten: {json.dumps(ten)}",
        f"duong_dan: {json.dumps(str(repo), ensure_ascii=False)}",
        f"gitnexus_repo: {json.dumps(gitnexus, ensure_ascii=False) if gitnexus else 'null'}",
        'boi_canh: ""  # 3–5 dòng: dự án là gì, module chính, quy ước repo',
        "# D31: chỉ đọc + quét thử — `tram quet --ghi` bỏ qua, không giao việc, dashboard không ghi được bead.",
        "bat_ghi: false  # Đại ca sửa tay thành true khi đã điền hàng rào riêng và cho trạm ghi beads",
        "# Khoá tuỳ chọn: module, tu_khoa_khach, lenh_cho_phep, moi_truong_kiem, nhanh_chinh (mặc định main),",
        "# lenh_kiem_mac_dinh, duong_dan_cam, tai_lieu_du_an, ngan_sach — xem du-an/vi-du.yaml.",
        "hang_rao:  # mặc định chung — chỉ đẩy về cột 2; thêm từ khoá, đường dẫn (glob), nhãn riêng của dự án",
    ]
    for loai, tu in RAO_MAC_DINH.items():
        dong += [f"  {loai}:", f"    tu_khoa: {_ds(tu)}", "    duong_dan: []", "    nhan: []"]
    return "\n".join(dong) + "\n"


def kiem_yaml(ten: str, noi_dung: str) -> None:
    """Nạp thử bằng chính `nap_du_an` trong thư mục tạm — file sắp ghi chắc chắn qua được bộ nạp thật."""
    with tempfile.TemporaryDirectory() as tam:
        (Path(tam) / f"{ten}.yaml").write_text(noi_dung, encoding="utf-8")
        nap_du_an(ten, thu_muc=Path(tam))
