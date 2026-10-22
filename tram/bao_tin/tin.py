"""Tin Telegram (spec 2 §6): chỉ mã bead, loại việc, tên dự án, link — không nội dung nghiệp vụ (§4 mục 5)."""
import re
from collections.abc import Sequence
from dataclasses import dataclass

LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat",
            "khe_cau_dao", "khe_het_han_muc", "spec_cho_merge", "feature_xong", "pr_da_merge",
            "pr_khong_xac_minh")
LOAI_TIN += ("tu_merge", "san_sang_deploy", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
             "lui_hong", "cai_dat_doi")                                   # TM-1: tự merge / tự deploy (D-8, D99)
LOAI_TIN += ("viec_moi_agent",)                                          # TC: việc mới do agent tạo (D86)
NHAN_LOAI = {"cho_review": "việc chờ review", "spec_cho_duyet": "spec chờ duyệt", "escalation": "escalation bí",
             "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt",
             "khe_cau_dao": "cầu dao khe ngắt", "khe_het_han_muc": "khe hết hạn mức",
             "spec_cho_merge": "spec đã duyệt chưa merge sau 24 giờ", "feature_xong": "feature xong, chờ Đại ca đóng",
             "pr_da_merge": "PR đã merge, trạm xác minh đúng commit đã kiểm",           # 2d: pr.da_merge (4c)
             "pr_khong_xac_minh": "PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay"}   # 2d D15
NHAN_LOAI |= {"tu_merge": "tự merge", "san_sang_deploy": "sẵn sàng deploy", "deploy_xong": "deploy xong",
              "deploy_da_lui": "deploy hỏng, đã tự lùi", "tu_deploy_tu_tat": "trạm đã tự tắt tự deploy sau 3 lần hỏng",
              "deploy_khong_ro": "deploy không rõ kết quả — cần Đại ca kiểm", "lui_hong": "LÙI HỎNG — cần Đại ca",
              "cai_dat_doi": "cài đặt tự động vừa đổi"}
NHAN_LOAI["viec_moi_agent"] = "việc mới do agent tạo"
# Loại mà ô `bead_id` mang MÃ CHI TIẾT (do `nguon_tu_dong.py` đặt) thay cho mã bead → dịch sang lời thường.
LOAI_CHI_TIET = frozenset({"cai_dat_doi", "deploy_da_lui"})
NHAN_CHI_TIET = {"tu-merge-bat": "tự merge bật", "tu-merge-tat": "tự merge tắt", "tu-deploy-bat": "tự deploy bật",
                 "tu-deploy-tat": "tự deploy tắt", "dk-ci-bat": "nút CI xanh bật", "dk-ci-tat": "nút CI xanh tắt",
                 "dk-cot-bat": "nút cột AI tự làm bật", "dk-cot-tat": "nút cột AI tự làm tắt",
                 "dk-hang-rao-bat": "nút hàng rào bật", "dk-hang-rao-tat": "nút hàng rào tắt",
                 "lenh-deploy-doi": "lệnh deploy đổi", "lenh-kiem-song-doi": "lệnh kiểm còn sống đổi",
                 "lenh-lui-doi": "lệnh lùi đổi", "tam-dung": "TẠM DỪNG", "tiep-tuc": "tiếp tục",
                 "tam-dung-toan-tram": "TẠM DỪNG toàn trạm", "tiep-tuc-toan-tram": "tiếp tục toàn trạm"}
HONG_RE = re.compile(r"hong-([1-9][0-9]?)-lan")
ID_AN_TOAN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
KHE_AN_TOAN = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")      # khe_id (spec 3 §4) — tin hệ của lát 2b


@dataclass(frozen=True)
class Tin:
    loai: str
    du_an: str
    bead_id: str | None = None


def chi_tiet(ma: str) -> str:
    goc = ma.removeprefix("tram-")
    hong = HONG_RE.fullmatch(goc)
    nhan = f"hỏng liên tiếp {hong[1]} lần" if hong else NHAN_CHI_TIET.get(goc, goc)
    return ("trạm: " if goc != ma else "") + nhan


def soan_tin(loai: str, tins: Sequence[Tin], dashboard_url: str | None) -> str:
    theo: dict[str, list[str]] = {}
    for t in tins:
        ok = t.bead_id and (ID_AN_TOAN.fullmatch(t.bead_id) or KHE_AN_TOAN.fullmatch(t.bead_id))
        theo.setdefault(t.du_an, []).append((chi_tiet(t.bead_id) if loai in LOAI_CHI_TIET else t.bead_id) if ok else "")
    phan = []
    for du_an in sorted(theo):
        ma = [i for i in theo[du_an] if i]
        if du_an.startswith("_"):                      # tin hệ: chỉ nhãn loại (+ mã khe nếu có)
            phan.append(NHAN_LOAI[loai] + (f" ({', '.join(ma[:5])})" if ma else ""))
            continue
        s = f"{du_an} · {len(theo[du_an])} {NHAN_LOAI[loai]}"
        if ma:
            s += f" ({', '.join(ma[:5])}{', …' if len(ma) > 5 else ''})"
        phan.append(s)
    return "[tram] " + " · ".join(phan) + (f" → {dashboard_url}" if dashboard_url else "")
