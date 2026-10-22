"""V2-C1: đọc nguồn Beads/sự kiện sau Git/GitHub; lỗi đọc luôn chờ, không chép nội dung lỗi."""
import sqlite3

from tram.beads.bd import LoiBd
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.giao_viec.doc_lai import dau_bead
from tram.giao_viec.su_kien import cua_so, moi_nhat, su_kien_bead


def doc_hien_hanh(bd, kho, da, bead_id):
    """Không dùng bộ đệm. Đọc Beads trước SQLite vì bd list có thể chậm; không giữ giao dịch khi đọc bd."""
    try:
        theo_id = {b.id: b for b in bd.tat_ca()}
        b = theo_id.get(bead_id)
        if b is None or bi_chan_boi(b, theo_id):
            return None
        return b, su_kien_bead(kho, da.ten, bead_id)
    except (LoiBd, OSError, ValueError, sqlite3.Error):
        return None


def spec_con_nguyen(cu, moi, ds, dy, mo):
    """D95: đúng feature theo-plan, bản duyệt/PR hiện hành; không dùng digest kế hoạch làm digest bead."""
    return (moi.status != 'closed' and moi.issue_type == 'feature' and 'theo-plan' in moi.labels
            and (moi.status, moi.assignee, dau_bead(moi)) == (cu.status, cu.assignee, dau_bead(cu))
            and moi_nhat(cua_so(ds), 'spec.duyet') == dy and moi_nhat(cua_so(ds), 'pr.mo') == mo)
