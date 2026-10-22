"""Bằng chứng gắn commit và vào cột 3 (spec 4 §6.4, §6.7 — điểm dừng #2 của Q6).

Bộ bằng chứng `(du_an, bead_id, giao_id_code, luot_code, commit_code, commit_ban_giao, digest_tieu_chi)`;
`commit_ban_giao` = `commit_qc` (bug/task/chore) hoặc commit của spike. Trạm xác minh `commit_code` là tổ tiên
`commit_ban_giao` và ref công bố HIỆN TẠI (sự kiện `giao.cong_bo` trạm ghi — không đọc HEAD remote) đúng bằng
`commit_ban_giao`. Ghi beads: gỡ MỌI `cot:*`, gắn duy nhất `cot:cho-review` (#8) + notes, ID thao tác bền.
Lát 4c: cờ đỏ thêm theo gitnexus `detect_changes` (`co_do_ly_do`); khối bàn giao chép vào notes mang `pr = null`
— PR chỉ do trạm điền."""
import fnmatch
import hashlib
import json
from datetime import datetime
from pathlib import Path

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.co_do_gn import co_do_gitnexus
from tram.giao_viec.git_kiem import la_to_tien
from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, ref_cong_bo
from tram.giao_viec.tieu_chi import digest_tieu_chi, tach_tieu_chi
from tram.kiem.diff import goc_nhanh, tep_doi
from tram.phieu.kho import KhoPhieu

NHAN_REVIEW, NHAN_CO_DO = "cot:cho-review", "co-do"


def bo_bang_chung(du_an: str, ds: list[SK], *, la_spike: bool) -> dict | None:
    w = cua_so(ds)
    n = moi_nhat(w, "giao.nhan", lambda e: e.du_lieu.get("buoc") == "code")
    kl = moi_nhat(w, "kiem.lai")
    if (n is None or kl is None or not kl.du_lieu["dat"]
            or kl.du_lieu.get("giao_id") != n.du_lieu["giao_id"]
            or kl.du_lieu.get("luot") != n.du_lieu["luot"]):
        return None
    kt = moi_nhat(w, "giao.ket_thuc", lambda e: e.du_lieu.get("giao_id") == n.du_lieu["giao_id"])
    if (kt is None or kt.du_lieu.get("ket_thuc") != "xong" or kt.du_lieu.get("ly_do") is not None
            or kt.du_lieu.get("commit") != kl.du_lieu["commit"]):
        return None
    code = kl.du_lieu["commit"]
    ban_giao = code
    if not la_spike:
        qk = moi_nhat(w, "qc.ket_qua")
        if (qk is None or qk.id <= kl.id or qk.du_lieu["ket_luan"] != "dat"
                or qk.du_lieu["commit_code"] != code):
            return None
        ban_giao = qk.du_lieu["commit_qc"]
    return {"du_an": du_an, "bead_id": kl.du_lieu["bead_id"], "giao_id_code": kl.du_lieu["giao_id"],
            "luot_code": kl.du_lieu["luot"], "commit_code": code, "commit_ban_giao": ban_giao,
            "digest_tieu_chi": kl.du_lieu["digest_tieu_chi"]}


def co_do(kho_git: Path, du_an: DuAn, commit: str) -> bool:
    """Cờ đỏ 4a theo đường dẫn file: diff từ gốc nhánh khớp `duong_dan` của bất kỳ hàng rào nào (§6.4 mục 3)."""
    tep = tep_doi(kho_git, goc_nhanh(kho_git, f"origin/{du_an.nhanh_chinh}", commit), commit)
    return any(fnmatch.fnmatch(p, g) for rao in du_an.hang_rao.values() for g in rao.duong_dan for p in tep)


def vao_cot_3(bd, kho: KhoPhieu, kho_git: Path, du_an: DuAn, bead: Bead, ds: list[SK], *, la_spike: bool,
              luc: datetime, gitnexus=None) -> bool:
    bc = bo_bang_chung(du_an.ten, ds, la_spike=la_spike)
    if bc is None or bc["digest_tieu_chi"] != digest_tieu_chi(tach_tieu_chi(bead.acceptance_criteria)) \
            or ref_cong_bo(ds) != bc["commit_ban_giao"] \
            or not la_to_tien(kho_git, bc["commit_code"], bc["commit_ban_giao"]):
        return False                                        # bằng chứng không còn hiệu lực → không vào cột 3
    xong = moi_nhat(ds, "bao.xong", lambda s: s.du_lieu.get("giao_id") == bc["giao_id_code"])
    ma = "cot3-" + hashlib.sha256(json.dumps(bc, sort_keys=True).encode()).hexdigest()[:20]
    ly_do_do = (("duong-dan",) if co_do(kho_git, du_an, bc["commit_ban_giao"]) else ()) + co_do_gitnexus(
        gitnexus, kho_git, du_an, bc["commit_ban_giao"])
    do = bool(ly_do_do)
    if ma not in bead.notes:                                # đối soát: notes đã mang dấu → đã ghi
        khoi = json.dumps({**xong.du_lieu["ban_giao"], "pr": None} if xong else {}, ensure_ascii=False)
        ghi_chu = (f"<!-- ban-giao -->\n{khoi}\n<!-- ban-giao -->\n<!-- bang-chung -->\n"
                   f"{json.dumps({**bc, 'ma_thao_tac': ma}, ensure_ascii=False)}\n<!-- bang-chung -->")
        bd.cap_nhat_nhan(bead.id, them=[NHAN_REVIEW, *([NHAN_CO_DO] if do else [])],
                         bo=[n for n in bead.labels if n.startswith("cot:") and n != NHAN_REVIEW], ghi_chu=ghi_chu)
    ghi_mot_lan(kho, du_an.ten, "bead.vao_cot_3", {**{k: bc[k] for k in ("bead_id", "commit_code", "commit_ban_giao",
                                                                         "digest_tieu_chi", "giao_id_code",
                                                                         "luot_code")},
                                                   "co_do": do, "co_do_ly_do": list(ly_do_do), "pr": None,
                                                   "ma_thao_tac": ma},
                bead_id=bead.id, luc=luc, khoa=("ma_thao_tac",))
    return True
