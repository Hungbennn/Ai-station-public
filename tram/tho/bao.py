"""`tram bao` — agent gọi trong lệnh Bash của phiên, dưới principal thực thi, ĐỒNG BỘ, KHÔNG gọi mạng (spec 3 §7.4):
1. đọc khối bàn giao (nếu có), điền `nhanh`, `commit: null`, `luot: 0` (thợ ghi đè), kiểm cấu trúc;
2. `git add -A && git commit` nếu có thay đổi (hook Git tắt), rồi điền `commit`;
3. ghi một dòng JSON vào hàng đợi `$TRAM_HANG_DOI`."""
import json
import os
import subprocess
from pathlib import Path

from tram.ban_giao.cau_truc import kiem_cau_truc
from tram.ban_giao.schema import KHOI_RE
from tram.de_nghi.loc import LOAI_DE_NGHI, loc

GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false")
DANH_TINH = ("-c", "user.name=tram-tho", "-c", "user.email=tram-tho@localhost")
LOAI = ("moc", "can_hoi", "bi", "xong", *LOAI_DE_NGHI)
LOAI_HOI = ("can_quyet_dinh", "thao_tac_nguy_hiem")
GIOI_HAN_NOI_DUNG = 4000


class LoiBao(ValueError):
    pass


def _git(wt: Path, *args: str, chay=subprocess.run, kiem: bool = True) -> str:
    return chay([*GIT, "-C", str(wt), *args], capture_output=True, text=True, check=kiem).stdout.strip()


def doc_khoi(wt: Path, ten: str) -> dict:
    """Khối cuối cùng giữa hai dấu `<!-- ban-giao -->` trong file bàn giao (phải nằm trong worktree)."""
    p = (wt / ten).resolve()
    if not p.is_relative_to(wt.resolve()) or not p.is_file():
        raise LoiBao(f"Không thấy file bàn giao trong worktree: {ten}")
    khop = KHOI_RE.findall(p.read_text(encoding="utf-8"))
    if not khop:
        raise LoiBao(f"{ten}: không có khối <!-- ban-giao -->")
    try:
        return json.loads(khop[-1])
    except ValueError as e:
        raise LoiBao(f"{ten}: khối bàn giao không phải JSON ({e})") from None


def _kiem_tham_so(loai: str, noi_dung: str, ban_giao: str | None, loai_hoi: str | None) -> None:
    if loai not in LOAI:
        raise LoiBao(f"loại báo không hợp lệ: {loai}")
    if len(noi_dung) > GIOI_HAN_NOI_DUNG:
        raise LoiBao(f"Nội dung dài quá {GIOI_HAN_NOI_DUNG} ký tự")
    if loai == "xong" and not ban_giao:
        raise LoiBao("--xong cần --ban-giao <file>")
    if loai == "can_hoi" and (loai_hoi not in LOAI_HOI or not noi_dung.strip()):
        raise LoiBao("--can-hoi cần --loai can_quyet_dinh|thao_tac_nguy_hiem và câu hỏi")
    if loai == "bi" and not noi_dung.strip():
        raise LoiBao("--bi cần lý do")
    if loai == "can_hoi" and ban_giao:
        raise LoiBao("--can-hoi không kèm bàn giao")


def dong_de_nghi(loai: str, noi_dung: str, viec_moi: dict | None) -> dict:
    """TC (design D-1, D-3): tiến độ / việc mới — lọc sớm để agent thấy lỗi ngay; không commit, không bàn giao."""
    dong = {"loai": loai, "noi_dung": noi_dung, **({"viec_moi": viec_moi} if viec_moi is not None else {})}
    if (loi := loc(loai, dong)) is not None:
        raise LoiBao(f"Đề nghị bị từ chối: {loi.ly_do}" + (f" ({', '.join(loi.nhom)})" if loi.nhom else ""))
    return dong


def _ghi(hang_doi: Path, dong: dict) -> dict:
    with open(hang_doi, "a", encoding="utf-8") as f:
        f.write(json.dumps(dong, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return dong


def bao(loai: str, noi_dung: str, *, wt: Path, hang_doi: Path, ban_giao: str | None = None,
        loai_hoi: str | None = None, viec_moi: dict | None = None, chay=subprocess.run) -> dict:
    if loai in LOAI_DE_NGHI:
        if ban_giao or loai_hoi:
            raise LoiBao(f"--{loai.replace('_', '-')} không kèm bàn giao hay loại câu hỏi")
        return _ghi(hang_doi, dong_de_nghi(loai, noi_dung, viec_moi))
    _kiem_tham_so(loai, noi_dung, ban_giao, loai_hoi)
    qua_quan_ly = os.environ.get("TRAM_GIT_QUA_QUAN_LY") == "1"
    khoi = None
    if ban_giao:
        khoi = {**doc_khoi(wt, ban_giao), "nhanh": (os.environ["TRAM_NHANH"] if qua_quan_ly else
                _git(wt, "rev-parse", "--abbrev-ref", "HEAD", chay=chay)),
                "commit": None, "luot": 0}
        kiem_cau_truc(khoi, can_chinh_thuc=loai == "xong")
    if not qua_quan_ly and _git(wt, "status", "--porcelain", chay=chay):
        co_ten = _git(wt, "config", "user.email", chay=chay, kiem=False)
        _git(wt, "add", "-A", chay=chay)
        _git(wt, *(() if co_ten else DANH_TINH), "commit", "-q", "-m",
             f"{loai}: {(noi_dung.strip().splitlines() or [loai])[0][:72]}", chay=chay)
    commit = None if qua_quan_ly else _git(wt, "rev-parse", "HEAD", chay=chay)
    if khoi is not None:
        khoi["commit"] = commit
    dong = {"loai": loai, "noi_dung": noi_dung, "commit": commit,
            **({"ban_giao": khoi} if khoi is not None else {}), **({"loai_hoi": loai_hoi} if loai_hoi else {})}
    return _ghi(hang_doi, dong)
