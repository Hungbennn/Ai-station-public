"""Dựng Bead/notes mẫu cho test lát 2a qua Bead.tu_json (không phụ thuộc thứ tự trường)."""
import json

from tram.beads.mo_hinh import Bead

KHOI_BAN_GIAO = {
    "phien_ban": 1, "loai": "chinh-thuc", "luot": 1, "file_ban_giao": "docs/handovers/x.md",
    "nhanh": "fix/x", "commit": "abc1234", "pr": "https://github.com/o/r/pull/7",
    "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [],
    "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": [],
}


def bead(id="hr-1", *, title="Việc", status="open", issue_type="task", labels=(), chan_boi=(),
         updated_at="2026-10-13T01:00:00Z", **them) -> Bead:
    d = {"id": id, "title": title, "status": status, "issue_type": issue_type, "labels": list(labels),
         "updated_at": updated_at,
         "dependencies": [{"issue_id": id, "depends_on_id": x, "type": "blocks"} for x in chan_boi]}
    return Bead.tu_json({**d, **them})


def notes_ban_giao(**ghi_de) -> str:
    return f"ghi chú\n<!-- ban-giao -->\n{json.dumps({**KHOI_BAN_GIAO, **ghi_de})}\n<!-- ban-giao -->"
