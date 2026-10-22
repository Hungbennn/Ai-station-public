"""Dashboard 4a (spec 4 §5.1, §6.4 mục 4): vì sao bead cột 1 CHƯA được giao, và lệnh/link để Đại ca tự tạo PR từ
`tram/<bead>` tại `commit_ban_giao` (trước 4c trạm không mở PR, không coi `pr` null là đã merge). Chỉ đọc: bộ đệm
beads, sự kiện `bead.vao_cot_3`, ref CỤC BỘ của kho kiểm (không fetch, không `bd ready` — "bị chặn" đã hiện bằng
"chờ …" trên thẻ). Mọi chuỗi trả về dựng từ hằng số, id đã kiểm dạng, SHA hex, tên nhánh đã kiểm."""
import re
from pathlib import Path
from urllib.parse import quote

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.dieu_kien import NHAN_COT_1, ly_do_khong_giao
from tram.giao_viec.git_kiem import sha_cua
from tram.giao_viec.kho_kiem_tao import github_repo, url_origin
from tram.giao_viec.tieu_chi import lenh_bat_buoc
from tram.suy.pr_tram import pr_tram

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
VAN_BAN = {
    "nhan-lech": "nhãn lệch — bead mang nhiều nhãn cột",
    "nhan-luong": "bead đang trong luồng feature (can-spec / cho-duyet-spec / theo-plan)",
    "loai-khong-giao": "loại bead này không giao ở 4a (chỉ bug, task, chore, spike)",
    "thieu-tieu-chi": "thiếu tiêu chí máy đọc được — chép tiêu chí vào acceptance_criteria",
    "cho-merge-spec": "chờ merge spec",
    "nguoi-khac-nhan": "bead đang do người khác nhận",
    "thieu-moi-truong-kiem": "dự án chưa có moi_truong_kiem",
    "thieu-lenh-kiem": "không có lệnh kiểm bắt buộc khớp lenh_cho_phep",
    "chua-co-kho-kiem": "trạm chưa có kho kiểm của dự án (tram giao kho-kiem)",
}
BO_QUA = {"bi-chan", "trang-thai", "khong-o-cot-1"}


def ly_do_hien(b: Bead, theo_id: dict[str, Bead], da: DuAn, co_kho_kiem: bool) -> str | None:
    if NHAN_COT_1 not in b.labels or b.status not in ("open", "in_progress"):
        return None
    ly = ly_do_khong_giao(b, theo_id, {b.id}, da)
    if ly in BO_QUA:
        return None
    if ly is None and b.issue_type != "spike" and not lenh_bat_buoc(da.giao.lenh_kiem_mac_dinh, b.design,
                                                                    da.lenh_cho_phep):
        ly = "thieu-lenh-kiem"
    return "chua-co-kho-kiem" if ly is None and not co_kho_kiem else ly


def thong_tin_pr(da: DuAn, b: Bead, vao_cot_3: dict | None, kg: Path | None) -> dict | None:
    commit = (vao_cot_3 or {}).get("commit_ban_giao")
    if "cot:cho-review" not in b.labels or not ID_RE.fullmatch(b.id) or not isinstance(commit, str) \
            or not SHA_RE.fullmatch(commit):
        return None
    nhanh = f"tram/{b.id}"
    tu_xa = sha_cua(kg, f"origin/{nhanh}") if kg else None
    repo = github_repo(url_origin(kg)) if kg else None
    link = (f"https://github.com/{repo}/compare/{quote(da.nhanh_chinh, safe='/')}...{quote(nhanh, safe='/')}"
            "?expand=1") if repo else None
    lenh = f"gh pr create {f'--repo {repo} ' if repo else ''}--base {da.nhanh_chinh} --head {nhanh} --fill"
    return {"nhanh": nhanh, "commit": commit, "tu_xa": tu_xa, "lech": tu_xa is not None and tu_xa != commit,
            "link": link, "lenh": lenh}


def suy_giao(da: DuAn, beads: list[Bead], kho, kg: Path | None) -> dict[str, dict]:
    """{"<du_an>/<bead_id>": {"khong_giao": văn bản | None, "pr": {..., "tram": {...} | None} | None}} — chỉ bead
    có điều để hiện. `pr.tram`: PR trạm đã mở ở lát 4c (`tram/suy/pr_tram.py`, plan 2d G10)."""
    theo_id, ra = {b.id: b for b in beads}, {}
    for b in beads:
        ly = ly_do_hien(b, theo_id, da, kg is not None)
        vc3 = kho.moi_nhat(da.ten, b.id, "bead.vao_cot_3") if "cot:cho-review" in b.labels else None
        pr = thong_tin_pr(da, b, vc3.du_lieu if vc3 else None, kg)
        if pr is not None:
            pr["tram"] = pr_tram(kho, da.ten, b.id, vc3)
        if ly or pr:
            ra[f"{da.ten}/{b.id}"] = {"khong_giao": VAN_BAN[ly] if ly else None, "pr": pr}
    return ra
