"""Dọn worktree của bead đã đóng (spec 3 §7.1): hỏi trạm `POST /api/tho/da-dong` cho các worktree đang có; bead đã có
`bead.dong` → `git worktree remove --force` + xoá nhánh cục bộ `tram/<…>` (nhánh `rac/…` giữ lại để Đại ca xem). Bỏ
qua worktree đang bị khoá bởi pid còn sống (một phiếu đang chạy)."""
import subprocess

from tram.tho.khach import LoiKhachTram
from tram.tho.mo_coi import con_song, doc_pid
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.worktree import GIT


def don_da_dong(nc: NguCanhTho) -> list[str]:
    if nc.ch.tren_may_b or not nc.goc_wt.is_dir():
        return []
    wt = {(d.name, w.name): w for d in nc.goc_wt.iterdir() if d.is_dir() for w in d.iterdir() if w.is_dir()}
    if not wt:
        return []
    bead = [{"du_an": da, "bead_id": ten.removeprefix("spec-")} for da, ten in sorted(wt)][:200]
    try:
        ma, kq = nc.khach.goi("POST", "/api/tho/da-dong", {"bead": bead})
    except LoiKhachTram:
        return []
    dong = {(x["du_an"], x["bead_id"]) for x in kq.get("dong", [])} if ma == 200 else set()
    da_xoa = []
    for (da, ten), w in sorted(wt.items()):
        if (da, ten.removeprefix("spec-")) not in dong:
            continue
        pid = (doc_pid(w / ".tram" / "khoa") or {}).get("pid")
        if isinstance(pid, int) and pid > 0 and con_song(pid):
            continue
        kho = nc.goc_kho / da
        subprocess.run([*GIT, "-C", str(kho), "worktree", "remove", "--force", str(w)], capture_output=True)
        subprocess.run([*GIT, "-C", str(kho), "branch", "-D", f"tram/{ten}"], capture_output=True)
        da_xoa.append(f"{da}/{ten}")
    return da_xoa
