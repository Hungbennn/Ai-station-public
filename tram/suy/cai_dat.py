"""Gom cấu hình cho trang Cài đặt (D19; khảo sát §1.6, §1.10 A1). CHỈ ĐỌC, danh sách cho phép từng trường.

Không bao giờ trả: `tu_khoa_khach`, nội dung/đường dẫn file `moi_truong_kiem`, `chat_id`, email `dai_ca_logins`,
`ten_may_b`, `dashboard_url`, mọi bản băm, đường dẫn ccusage. Mỗi lỗi nạp cấu hình chỉ làm hỏng mục của nó:
câu lỗi cố định qua `lam_sach(…, 200)` vào `loi_cau_hinh`; YAML chỉ thêm số dòng, các lỗi khác không dùng str(e)."""
from collections.abc import Callable
from pathlib import Path

import yaml

from tram.bao_tin.tin import NHAN_LOAI
from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
from tram.cau_hinh.du_an import DuAn, nap_du_an
from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
from tram.cau_hinh.tram import CauHinhTram
from tram.cau_hinh.usage import CauHinhUsage
from tram.chu import estop, ma_dieu_phoi
from tram.nho import ma_dai_ca
from tram.suy.he_thong import DocHeThong
from tram.suy.lam_sach import lam_sach

TOI_DA_DS = 50


def mo_ta_loi(e: Exception) -> str:
    """Không đưa giá trị cấu hình/đường dẫn từ exception vào API; YAML chỉ nêu vị trí."""
    if isinstance(e, yaml.MarkedYAMLError) and e.problem_mark is not None:
        return f"YAML hỏng ở dòng {e.problem_mark.line + 1}"
    if isinstance(e, yaml.YAMLError):
        return "YAML hỏng"
    if isinstance(e, ValueError):
        return "Giá trị cấu hình không hợp lệ"
    if isinstance(e, OSError):
        return "Không đọc được cấu hình"
    return "Không nạp được cấu hình"


def _rut_gon(p: Path) -> str:
    try:
        return "~/" + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)


def _ds(xs) -> list[str]:
    return [lam_sach(str(x), 200) for x in list(xs)[:TOI_DA_DS]]


def mot_du_an(ten: str, nap: Callable[[str], DuAn] = nap_du_an) -> dict:
    try:
        d = nap(ten)
    except Exception as e:
        return {"ten": lam_sach(ten, 64), "duong_dan": "", "nhanh_chinh": "", "gitnexus": None, "lenh_cho_phep": [],
                "hang_rao": [], "moi_truong_kiem": False, "loi": lam_sach(mo_ta_loi(e), 200)}
    return {"ten": lam_sach(d.ten, 64), "duong_dan": lam_sach(_rut_gon(d.duong_dan), 300),
            "nhanh_chinh": lam_sach(d.nhanh_chinh, 100),
            "gitnexus": lam_sach(d.gitnexus_repo, 100) if d.gitnexus_repo else None,
            "lenh_cho_phep": _ds(d.lenh_cho_phep),
            "hang_rao": [{"loai": loai, "tu_khoa": _ds(r.tu_khoa), "duong_dan": _ds(r.duong_dan)}
                         for loai, r in d.hang_rao.items()],
            "moi_truong_kiem": d.moi_truong_kiem is not None, "loi": None}


def _co(ch: CauHinhTram, usage: CauHinhUsage) -> list[tuple[str, str, Callable[[], tuple]]]:
    """(khoá, ghi chú cố định, hàm đọc → (bat, gia_tri)). Cờ bool: gia_tri None; cờ giá trị: bat = có giá trị."""
    def pa():
        p = nap_cau_hinh_cong_bo().phuong_an
        return p is not None, lam_sach(p, 40) or None

    def kenh():
        k = nap_cau_hinh_cach_ly().kenh_ghi
        return k == "unix-socket", lam_sach(k, 40)
    return [
        ("estop", "BẬT = dừng khẩn cấp, trạm không tự làm việc", lambda: (estop.dang_bat(), None)),
        ("giao_viec.bat", "chỉ bật sau 3a-2, S6, S7", lambda: (nap_cau_hinh_giao_viec().bat, None)),
        ("cong_bo.phuong_an", "cách công bố PR; trống = chưa chốt (sau S7)", pa),
        ("cach_ly.kenh_ghi", "unix-socket = API ghi chỉ qua socket cục bộ; header = qua header Tailscale", kenh),
        ("usage.ccusage", "màn Usage đọc log Claude Code qua ccusage",
         lambda: (usage.ccusage is not None, lam_sach(usage.ccusage_phien_ban, 40) or None)),
        ("usage.gia", "bảng giá USD theo mô hình", lambda: (bool(usage.gia), f"{len(usage.gia)} mô hình")),
        ("ten_may_b", "tên máy B trên tailnet — cần cho mọi thao tác ghi", lambda: (ch.ten_may_b is not None, None)),
        ("dashboard_url", "link dashboard gắn vào tin Telegram", lambda: (ch.dashboard_url is not None, None)),
        ("dai_ca_logins", "số danh tính Tailscale của Đại ca (không hiện email)",
         lambda: (bool(ch.dai_ca_logins), str(len(ch.dai_ca_logins)))),
        ("ma_dai_ca", "băm mã Đại ca cho phiên tay ký ức (1b-2)", lambda: (ma_dai_ca.doc_bam() is not None, None)),
        ("ma_dieu_phoi", "băm mã điều phối cho hook máy A (D24)", lambda: (ma_dieu_phoi.doc_bam() is not None, None)),
    ]


def doc_co(ch: CauHinhTram, usage: CauHinhUsage, loi: list[str]) -> list[dict]:
    ra = []
    for khoa, ghi_chu, doc in _co(ch, usage):
        try:
            bat, gia_tri = doc()
        except Exception as e:                             # lỗi một khoá không làm hỏng cả trang
            loi.append(lam_sach(f"{khoa}: {mo_ta_loi(e)}", 200))
            bat, gia_tri = None, None
        ra.append({"khoa": khoa, "bat": bat, "gia_tri": gia_tri, "ghi_chu": ghi_chu})
    return ra


def gom_cai_dat(ch: CauHinhTram, usage: CauHinhUsage, cac_du_an: Callable[[], list[str]], he: DocHeThong,
                nap: Callable[[str], DuAn] = nap_du_an) -> dict:
    loi: list[str] = []
    try:
        ds = [mot_du_an(t, nap) for t in cac_du_an()]
    except Exception as e:
        ds = []
        loi.append(lam_sach(f"du-an: {mo_ta_loi(e)}", 200))
    tg = {"co_chat_id": ch.telegram.chat_id is not None, "gio_yen_lang": ch.telegram.gio_yen_lang,
          "loai_tin": list(NHAN_LOAI.values())}
    co = doc_co(ch, usage, loi)
    return {"du_an": ds, "dich_vu": he.dich_vu(), "telegram": tg, "co": co, "keychain": he.keychain(),
            "loi_cau_hinh": loi}
