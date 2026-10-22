"""Đọc diff của một lần tự merge (spec `tu-merge`; D76, D89, D91, D92, D112) — phần cần Git của `tu_merge.py`.

- `cham_rao`: hàng rào chỉ theo đường dẫn diff từ gốc nhánh (D91); `schema` thêm từ khoá nội dung bead (D92, D112).
- `cham_file_lenh` (D89 tại cửa merge — Codex Q2): tập file cấm tính từ ba lệnh của CÀI ĐẶT HIỆN HÀNH (người gọi đọc
  lại ngay trước `gh pr merge`) so với diff. Tập này BẮT BUỘC: không theo nút, không bị `duong_dan_cam_cho_phep` miễn
  (Codex C2); dấu QC/kiểm lại cũ không thay được lần so này.
- `loai_trong_repo`: callback cho `tram.tu_dong.file_cam.duong_dan_tu_lenh` (hợp đồng D89 TM-1 vòng 2). "Có trong
  repo" = có trong cây Git ở MỘT trong `refs` (commit của PR, nhánh chính) — tạo mới hay xoá script lệnh sẽ chạy
  đều bị bắt. Token tuyệt đối → tương đối theo gốc đáng tin (`da.duong_dan`, kho kiểm); `..` thoát gốc → ngoài repo.
  Một đoạn là symlink → đóng bảo thủ (`file_lenh_loi`), không theo ra ngoài cây và không chỉ cấm tên link:
  cấm riêng tên link sẽ bỏ lọt PR sửa đích mà giữ nguyên link. Kiểm từng đoạn TRƯỚC khi rút gọn `..`."""
import fnmatch
import os
import subprocess
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path, PurePosixPath

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.luat_cung import kiem
from tram.duong_dan import tram_home
from tram.giao_viec.su_kien import SK
from tram.kiem.diff import goc_nhanh, tep_doi
from tram.kiem.duong_dan_cam import khop_mau
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.file_cam import duong_dan_tu_lenh

NHAN_CO_DO = "co-do"
GIT = ("git", "--literal-pathspecs", "-c", "core.hooksPath=/dev/null")
HAN_GIT = 60                                                # giây — lời gọi Git không bao giờ chờ vô hạn
LoaiTrongRepo = Callable[[str], tuple[str, str] | None]


def doc_tep(kg: Path, da: DuAn, c: str) -> list[str] | None:
    """File đổi từ gốc nhánh tới `c`; None = không đọc được (người gọi luôn chờ: `diff_loi`)."""
    try:
        return tep_doi(kg, goc_nhanh(kg, f"origin/{da.nhanh_chinh}", c), c)
    except (subprocess.CalledProcessError, OSError):
        return None


def cham_rao(da: DuAn, b: Bead, v: SK, tep: list[str] | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(cấu trúc DB, hàng rào có nút). Bead mang cờ đỏ mà không khớp loại nào (D120) vẫn là chạm."""
    if tep is None:
        return ("diff_loi",), ()                            # không biết diff chạm gì → luôn chờ, như cấu trúc DB
    loai = [l for l, r in da.hang_rao.items() if any(fnmatch.fnmatch(p, g) for g in r.duong_dan for p in tep)]
    sc = da.hang_rao.get("schema")
    tu_khoa = sc is not None and bool(kiem(b, replace(da, hang_rao={"schema": HangRao(tu_khoa=sc.tu_khoa)}), {}).cham)
    schema = (("schema_duong_dan",) if "schema" in loai else ()) + (("schema_tu_khoa",) if tu_khoa else ())
    rao = tuple(f"hang_rao_{l}" for l in loai if l != "schema")
    if not rao and "schema" not in loai and (NHAN_CO_DO in b.labels or v.du_lieu.get("co_do") is True):
        rao = ("hang_rao_co_do",)
    return schema, rao


def _tuong_doi(tok: str, goc: tuple[str, ...]) -> str | None:
    if os.path.isabs(tok):
        g = next((g for g in goc if tok.lower().startswith(g.lower() + "/")), None)
        return None if g is None else tok[len(g) + 1:]
    return tok if tok not in ("", ".") else None


def _cay(kg: Path, ref: str) -> dict[str, tuple[str, str, str]]:
    """Cả cây ở `ref`, không đi vào symlink; khoá chữ thường (ổ macOS không phân biệt hoa) → (tên, mode, kiểu)."""
    tho = subprocess.run([*GIT, "-C", str(kg), "ls-tree", "-r", "-t", "-z", "--full-tree", ref], capture_output=True,
                         timeout=HAN_GIT, check=True).stdout
    ra = {}
    for x in (x for x in tho.split(b"\0") if x):
        dau, ten = x.split(b"\t", 1)
        ra[os.fsdecode(ten).lower()] = (os.fsdecode(ten), *dau.decode().split(" ")[:2])
    return ra


def loai_trong_repo(kg: Path, goc: tuple[Path, ...], refs: tuple[str, ...]) -> LoaiTrongRepo:
    goc_s = tuple(dict.fromkeys(os.path.normpath(s) for g in goc for s in (g, g.resolve())))
    cay: dict[str, dict] = {}

    def loai(tok: str) -> tuple[str, str] | None:
        if (p := _tuong_doi(tok, goc_s)) is None:
            return None
        for ref in refs:
            muc = cay[ref] if ref in cay else cay.setdefault(ref, _cay(kg, ref))
            doan = []
            for d in PurePosixPath(p).parts:
                if d == "..":
                    if not doan:
                        return None
                    doan.pop()
                    continue
                doan.append(d.lower())
                m = muc.get("/".join(doan))
                if m is None:
                    break
                if m[1] == "120000":
                    raise OSError("đường lệnh qua symlink: chưa chứng minh được đích an toàn")
            else:
                if m := muc.get("/".join(doan)):
                    return m[0], "dir" if m[2] == "tree" else "file"
        return None
    return loai


def cham_file_lenh(cd: CaiDatTuDong, kg: Path, da: DuAn, c: str, tep: list[str] | None) -> tuple[str, ...]:
    """`("file_lenh",)` khi diff chạm file ba lệnh dùng; `("file_lenh_loi",)` khi không đọc được cây Git."""
    if tep is None:
        return ()                                           # đã có `diff_loi` (luôn chờ)
    try:
        gocs = (da.duong_dan, kg, tram_home() / "kho-deploy" / da.ten)
        cam = duong_dan_tu_lenh(cd, loai_trong_repo(kg, gocs, (c, f"origin/{da.nhanh_chinh}")))
    except (subprocess.SubprocessError, OSError):
        return ("file_lenh_loi",)
    return ("file_lenh",) if any(khop_mau(p, m) for p in tep for m in cam) else ()
