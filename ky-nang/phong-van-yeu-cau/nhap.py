"""Nháp yêu cầu tạo feature trên máy A (D47; spec 4 §7.1; plan 4d 4D-3a) — file JSON NGOÀI repo, tên file = mã.

Mã `yc-<32 hex>` sinh MỘT lần bằng `moi` (ngẫu nhiên, không suy từ nội dung). Sửa nháp tại chỗ giữ nguyên mã. Mã thiếu,
sai dạng hay khác tên file (chép nháp sang tên khác, sửa tay mã) → từ chối, KHÔNG tự sinh lại: yêu cầu mới phải chọn rõ
bằng `moi` (có thể `--tu <nháp cũ>` để chép nội dung sang mã mới). python3 ≥ 3.9, chỉ thư viện chuẩn."""
import json
import os
import re
import secrets
from pathlib import Path

MA_RE = re.compile(r"yc-[0-9a-f]{32}")
KHOA = {"ma_yeu_cau", "tieu_de", "uu_tien", "phieu"}
PHIEU_TRONG = {"phien_ban": 1, "muc_tieu": "", "nghiep_vu_da_chot": [], "pham_vi": "", "khong_lam": [],
               "nghiem_thu_so_bo": [], "cau_hoi_mo": [], "module": [], "bien_ban": None}


class Loi(Exception):
    pass


def thu_muc_mac_dinh():
    return Path(os.environ.get("PHONG_VAN_NHAP") or Path.home() / ".phong-van-yeu-cau")


def trong_repo(thu_muc):
    p = Path(thu_muc).expanduser().resolve()
    return any((x / ".git").exists() for x in (p, *p.parents))


def moi(thu_muc, du_an=None, tu=None):
    """Nháp mới với mã mới; `tu`: chép tiêu đề/ưu tiên/phiếu của nháp cũ (Đại ca đã chọn rõ "yêu cầu mới")."""
    thu_muc = Path(thu_muc).expanduser()
    if trong_repo(thu_muc):
        raise Loi("Thư mục nháp nằm trong một repo git — nháp và biên bản phải ở ngoài repo")
    if tu is not None:
        cu = doc(tu)
        noi_dung = {"tieu_de": cu["tieu_de"], "uu_tien": cu["uu_tien"], "phieu": cu["phieu"]}
    elif du_an:
        noi_dung = {"tieu_de": "", "uu_tien": 2, "phieu": dict(PHIEU_TRONG, du_an=du_an)}
    else:
        raise Loi("Cần --du-an <tên dự án> hoặc --tu <nháp cũ>")
    thu_muc.mkdir(mode=0o700, parents=True, exist_ok=True)
    ma = "yc-" + secrets.token_hex(16)
    p = thu_muc / (ma + ".json")
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)   # không ghi đè; chỉ chủ đọc được
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(dict(ma_yeu_cau=ma, **noi_dung), f, ensure_ascii=False, indent=2)
    return p


def doc(duong_dan):
    """Nháp → envelope gửi B `{ma_yeu_cau, du_an, tieu_de, uu_tien, phieu}`. Chỉ kiểm phần B không tự kiểm được."""
    p = Path(duong_dan).expanduser()
    if trong_repo(p.parent):
        raise Loi("Nháp nằm trong một repo git — chuyển ra ngoài repo")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise Loi("Không đọc được file nháp (JSON)") from None
    if not isinstance(d, dict) or set(d) != KHOA or not isinstance(d["phieu"], dict):
        raise Loi("Nháp phải có đúng bốn khoá ma_yeu_cau, tieu_de, uu_tien, phieu")
    ma = d["ma_yeu_cau"]
    if not isinstance(ma, str) or not MA_RE.fullmatch(ma) or p.name != ma + ".json":
        raise Loi("Mã yêu cầu thiếu, sai dạng hoặc khác tên file — không tự sinh lại; yêu cầu mới thì chạy `moi`")
    td, ut = d["tieu_de"], d["uu_tien"]
    if not isinstance(td, str) or not td or td != td.strip() or len(td) > 200 or not td.isprintable() \
            or td.startswith("-"):
        raise Loi("tieu_de: một dòng 1–200 ký tự, không khoảng trắng đầu/cuối, không bắt đầu bằng '-'")
    if type(ut) is not int or not 0 <= ut <= 4:
        raise Loi("uu_tien: số nguyên 0–4")
    if not isinstance(d["phieu"].get("du_an"), str) or not d["phieu"]["du_an"]:
        raise Loi("phieu.du_an thiếu")
    return {"ma_yeu_cau": ma, "du_an": d["phieu"]["du_an"], "tieu_de": td, "uu_tien": ut, "phieu": d["phieu"]}
