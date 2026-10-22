import json
import re
import unicodedata
from collections.abc import Sequence

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.luat_cung import KetQuaLuat
from tram.duong_dan import goc_repo

THE = "du_lieu_khong_tin_cay"
# Mọi biến thể thẻ mà mô hình có thể đọc thành thẻ: hoa/thường, khoảng trắng, dấu nối, ngoặc toàn khổ.
THE_RE = re.compile(r"[<＜﹤]\s*/?\s*du[\s_\-]*lieu[\s_\-]*khong[\s_\-]*tin[\s_\-]*cay", re.I)


def nap_vai(ten: str) -> tuple[str, str]:
    raw = (goc_repo() / "vai" / f"{ten}.md").read_text(encoding="utf-8")
    _, dau, than = raw.split("---", 2)
    phien_ban = next(l.split(":", 1)[1].strip() for l in dau.splitlines() if l.startswith("phien_ban"))
    return phien_ban, than.strip()


def he_thong(than_vai: str, du_an: DuAn) -> str:
    """Phần cố định — không chứa gì đổi theo từng lần gọi, để prompt cache trúng."""
    return f"{than_vai}\n\n## Dự án {du_an.ten}\n{du_an.boi_canh.strip()}"


def _boc(s: str) -> str:
    """Vô hiệu hoá mọi thẻ giả trong dữ liệu không tin cậy. Bỏ ký tự định dạng vô hình (Cf) trước."""
    s = "".join(c for c in s if unicodedata.category(c) != "Cf")
    return THE_RE.sub(lambda m: "‹" + m.group(0)[1:], s)


def boc_khong_tin_cay(s: str) -> str:
    """Bọc dữ liệu không tin cậy trong thẻ sau khi vô hiệu hoá thẻ giả bên trong (dùng chung với memory 1b)."""
    return f"<{THE}>\n{_boc(s)}\n</{THE}>"


def _muc_bai_hoc(bai_hoc: list[str]) -> str:
    """Vai v3 (spec 1b §7, §10): ký ức từ memory hoặc sự kiện cũ đều là dữ liệu, bọc thẻ."""
    if not bai_hoc:
        return "## Bài học và quyết định đã ghi nhớ\n- (chưa có)"
    return "## Bài học và quyết định đã ghi nhớ\n" + boc_khong_tin_cay(
        "\n".join(f"- {' '.join(b.split())}" for b in bai_hoc))


def _muc_quyet_dinh(quyet_dinh: Sequence[Bead]) -> str:
    """Decision đã đóng dạng {id, title, description, close_reason}; thiếu close_reason → rỗng (§5.3)."""
    if not quyet_dinh:
        return "## Quyết định đã chốt\n- (không có)"
    dong = "\n".join(json.dumps({"id": d.id, "title": d.title, "description": d.description,
                                 "close_reason": d.close_reason}, ensure_ascii=False) for d in quyet_dinh)
    return f"## Quyết định đã chốt\n{boc_khong_tin_cay(dong)}"


def noi_dung(bead: Bead, luat: KetQuaLuat, bai_hoc: list[str], quyet_dinh: Sequence[Bead] = ()) -> str:
    phan = [_muc_bai_hoc(bai_hoc), _muc_quyet_dinh(quyet_dinh)]
    if luat.ep_cot_2:
        phan.append(f"## Bead này đã bị luật cứng xếp cột can-chot\n{luat.ly_do()}\n"
                    "Trả cot = \"can-chot\" và soạn cau_hoi_can_chot cụ thể cho phần chạm hàng rào.")
    if luat.bi_chan_boi:
        phan.append(f"## Phụ thuộc\nĐang bị chặn bởi: {', '.join(luat.bi_chan_boi)}. "
                    "Điều này không làm giảm readiness về nội dung.")
    du_lieu = (f"ID: {bead.id}\nLoại: {bead.issue_type}\nTrạng thái: {bead.status}\n"
               f"Tiêu đề: {bead.title}\nMô tả:\n{bead.description}\n"
               f"Tiêu chí nghiệm thu:\n{bead.acceptance_criteria or '(trống)'}\n"
               f"Thiết kế:\n{bead.design or '(trống)'}")
    phan.append(boc_khong_tin_cay(du_lieu))
    return "\n\n".join(phan)
