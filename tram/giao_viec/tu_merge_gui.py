"""Gửi lệnh tự merge và đối soát (spec `tu-merge` "Không merge lặp", "Kiểm lại công tắc ngay trước lúc merge";
design D-7). Mỗi lần tự merge mang mã `tm-` cố định theo (dự án, bead, commit). Thứ tự: đọc PR → đối soát lần trước
→ xét điều kiện (đọc lại khoá chung NGAY lúc này, sau mọi lệnh chậm) → ghi `tu_merge.bat_dau` → `gh pr merge` chặt →
đọc lại PR. Kết quả không rõ thì vòng sau đọc PR trước: đã merge → `tu_merge.xong`; còn mở và vẫn đủ điều kiện → gửi
lại đúng lệnh cùng commit; đóng, hay merge ở đầu khác → `tu_merge.loi`. Gửi tối đa 3 lần rồi `tu_merge.loi`."""
import hashlib
from collections.abc import Callable
from datetime import datetime

from tram.giao_viec.gh import GhCli, PrInfo, LoiGh
from tram.giao_viec.doc_merge import doc, ghi_doc
from tram.giao_viec.su_kien import SK, cua_so, da_co, moi_nhat
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.cong_kiem import cong_mo
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.trang_thai import chuoi_dang_do, doc_su_kien

TAC_NHAN = "tram/tu-merge"
SO_LAN = 3
LyDo = Callable[[PrInfo], list[str]]


def ma_tu_merge(du_an: str, bead_id: str, commit: str) -> str:
    return "tm-" + hashlib.sha256(f"{du_an}:{bead_id}:{commit}".encode()).hexdigest()[:20]


def ghi(kho: KhoPhieu, du_an: str, loai: str, du_lieu: dict, *, bead_id: str, luc: datetime,
        khoa: tuple[str, ...]) -> None:
    """Một giao dịch; đã có sự kiện cùng các trường `khoa` thì thôi (phát lại vòng tick không ghi hai lần)."""
    with kho.giao_dich():
        if not da_co(kho, du_an, loai, {k: du_lieu[k] for k in khoa}):
            kho.ghi_su_kien(du_an, loai, du_lieu, luc=luc, bead_id=bead_id, tac_nhan=TAC_NHAN)


def ghi_cho(kho: KhoPhieu, du_an: str, bead_id: str, ds: list[SK], ly_do: list[str], commit: str,
            luc: datetime) -> None:
    """Spec mốc 2.5: chỉ ghi khi khác lần trước (lần trước = `tu_merge.cho` hay lần gửi lệnh gần nhất trong cửa sổ)."""
    w = cua_so(ds)
    tr, gui = moi_nhat(w, "tu_merge.cho"), moi_nhat(w, "tu_merge.bat_dau")
    if tr is not None and (gui is None or tr.id > gui.id) and tr.du_lieu == {"ly_do": ly_do, "commit": commit}:
        return
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, "tu_merge.cho", {"ly_do": ly_do, "commit": commit}, luc=luc, bead_id=bead_id,
                        tac_nhan=TAC_NHAN)


def _loi(kho, du_an, bead_id, ma, ma_loi, luc) -> str:
    ghi(kho, du_an, "tu_merge.loi", {"ma_thao_tac": ma, "ma_loi": ma_loi}, bead_id=bead_id, luc=luc,
        khoa=("ma_thao_tac",))
    return "tu_merge_loi"


def _xong(kho, du_an, bead_id, ma, loai, luc) -> str:
    ghi(kho, du_an, "tu_merge.xong", {"ma_thao_tac": ma, "loai": loai}, bead_id=bead_id, luc=luc,
        khoa=("ma_thao_tac",))
    return "tu_merge"


def gui_merge(gh: GhCli, repo: str, kho: KhoPhieu, du_an: str, bead_id: str, ds: list[SK], *, so_pr: int,
              commit: str, loai: str, ly_do: LyDo, luc: datetime) -> str | None:
    """`ly_do(pr)` đọc lại cài đặt, TẠM DỪNG, estop, `bat_ghi` mỗi lần gọi và trả mã lý do (rỗng = được merge).
    None = không làm gì để `kiem_merge` chạy tiếp (Đại ca merge tay, hoặc đang chờ điều kiện)."""
    ma = ma_tu_merge(du_an, bead_id, commit)
    if any(s.loai in ("tu_merge.xong", "tu_merge.loi") and s.du_lieu.get("ma_thao_tac") == ma for s in ds):
        return None
    da_gui = sum(1 for s in ds if s.loai == "tu_merge.bat_dau" and s.du_lieu.get("ma_thao_tac") == ma)
    try:
        pr = doc(gh, repo, so_pr)
    except LoiGh:
        n = ghi_doc(kho, du_an, bead_id, ds, ma, True, luc)
        return _loi(kho, du_an, bead_id, ma, "gh-doc-loi-3-lan", luc) if n >= SO_LAN else None
    ghi_doc(kho, du_an, bead_id, ds, ma, False, luc)
    if pr.trang_thai == "MERGED":
        if not da_gui:
            return None                                     # Đại ca merge tay — xác minh như luồng cũ
        return _xong(kho, du_an, bead_id, ma, loai, luc) if pr.head == commit else _loi(
            kho, du_an, bead_id, ma, "merge-khac-commit", luc)
    if pr.trang_thai != "OPEN":
        return _loi(kho, du_an, bead_id, ma, "pr-da-dong", luc) if da_gui else None
    cong = cong_mo()
    ly = ly_do(pr)
    if not cong:
        ly.append("cong_kiem")
    deploy = doc_su_kien(kho.db, du_an)
    if chua_doi_soat(deploy) or chuoi_dang_do(deploy):
        ly.append("deploy_chua_ro")
    if ly:
        ghi_cho(kho, du_an, bead_id, ds, ly, commit, luc)
        return None
    if da_gui >= SO_LAN:
        return _loi(kho, du_an, bead_id, ma, "gh-loi-3-lan", luc)
    ghi(kho, du_an, "tu_merge.bat_dau", {"ma_thao_tac": ma, "commit": commit, "pr": pr.so, "loai": loai,
                                          "lan": da_gui + 1}, bead_id=bead_id, luc=luc, khoa=("ma_thao_tac", "lan"))
    gh.merge_pr(repo, pr.so, commit)                         # LoiGh: luôn đối soát vòng sau, kể cả lần thứ ba
    if gh.xem_pr(repo, pr.so).trang_thai == "MERGED":
        return _xong(kho, du_an, bead_id, ma, loai, luc)
    return "tu_merge_gui"                                   # chưa thấy MERGED: vòng sau đối soát
