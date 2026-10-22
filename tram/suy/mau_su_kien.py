"""Mẫu câu cố định theo loại sự kiện (D39). Mỗi mẫu nhận `(du_lieu, su_kien)` và chỉ dùng hàm kiểm dạng của
`tram/suy/mo_ta_su_kien.py`. Mã lý do → câu hằng; mã lạ → "?". Không mẫu nào đọc trường chữ tự do."""
from tram.suy.mau_nho import MAU_NHO
from tram.suy.mo_ta_su_kien import BUOC, COT, adr, chon, khe_tho, ma, sha, so

KET_CHAY = {"xong": "xong", "loi": "lỗi", "loi_he": "lỗi hệ", "het_han_muc": "hết hạn mức", "dung": "dừng",
            "mo-coi": "mồ côi"}
KET_GIAO = {"xong": "xong", "bi": "bí", "het_han_muc": "hết hạn mức", "thu_hoi": "thu hồi"}
CAU_DAO = {"het-han-muc": "hết hạn mức", "loi-lien-tiep": "lỗi liên tiếp", "het-gio": "hết giờ",
           "dai-ca": "Đại ca đóng"}
THU_HOI = {"mat-nhip": "mất nhịp tim", "go-may": "gỡ máy"}
HOI = {"can_quyet_dinh": "cần quyết định", "thao_tac_nguy_hiem": "thao tác nguy hiểm"}
BI = {"agent": "agent bí", "het-ngan-sach": "hết ngân sách", "khe-tat": "khe tắt", "estop": "estop",
      "cau-dao": "cầu dao", "can-hoi": "cần hỏi", "thieu-moi-truong-kiem": "thiếu môi trường kiểm",
      "nhanh-bi-day-ngoai-luong": "nhánh bị đẩy ngoài luồng", "loi-may-tho": "lỗi máy thợ"}
ESC = {"agent-bi": "agent bí", "can-thao-tac-nguy-hiem": "cần thao tác nguy hiểm", "agent-can-hoi": "agent cần hỏi",
       "het-ngan-sach": "hết ngân sách", "nhanh-bi-day": "nhánh bị đẩy",
       "thieu-moi-truong-kiem": "thiếu môi trường kiểm", "dong-file-cau-hinh": "đụng file cấu hình",
       "qc-doi-ma": "QC đổi mã", "spec-tra-ve-nhieu": "spec bị trả về nhiều", "phieu-thieu": "phiếu thiếu",
       "cay-khac-nguon": "cây bản chép khác nguồn"}
QC = {"dat": "QC đạt", "tra_ve": "QC trả về", "khong_cong_nhan": "QC không công nhận"}
PR_LY_DO = {"pr-khac": "PR khác PR trạm mở", "sai-nhanh": "sai nhánh", "sai-nhanh-chinh": "sai nhánh chính",
            "thieu-merge-commit": "thiếu merge commit",
            "merge-khong-tren-nhanh-chinh": "merge không nằm trên nhánh chính",
            "khong-phai-merge-commit": "không phải merge commit (squash / rebase)",
            "head-khac-commit-ban-giao": "head khác commit bàn giao"}


def _khe(d):
    return ma(d.get("khe_id"))


def _luot(d):
    return f"lượt {so(d.get('luot'))}"


MAU = {
    "quet.bat_dau": lambda d, s: f"bắt đầu quét {so(d.get('so_bead'))} bead"
    + (" (quét thử)" if d.get("thu") else ""),
    "quet.xong": lambda d, s: f"đã chấm {so(d.get('da_cham'))} bead"
    + (f", {so(d['loi'])} lỗi" if d.get("loi") else ""),
    "quet.loi": lambda d, s: "lỗi đọc beads",
    "quet.bo_qua": lambda d, s: "bỏ lượt quét vì estop",
    "cham_cot.ket_qua": lambda d, s: f"→ {chon(COT, d.get('cot'))}" + (" (huỷ)" if d.get("huy") else ""),
    "cham_cot.loi": lambda d, s: "lỗi khi chấm",
    "cham_cot.bo_qua": lambda d, s: "bỏ chấm vì lỗi liên tiếp",
    "cham_cot.thu_lai": lambda d, s: "Đại ca bấm thử lại",
    "cham_cot.can_cham_lai": lambda d, s: "cần chấm lại sau khi decision đóng",
    "cot.dai_ca_sua": lambda d, s: f"Đại ca chuyển sang {chon(COT, d.get('cot_moi'))}",
    "cot.da_chot": lambda d, s: "Đại ca chốt câu hỏi"
    + (f" (dẫn {adr(d.get('adr'))})" if adr(d.get("adr")) else ""),
    "cot.tra_ve": lambda d, s: "Đại ca trả về kèm góp ý",
    "escalation.tao": lambda d, s: f"mở escalation {ma(d.get('escalation_id'))} ({chon(ESC, d.get('ly_do'))})",
    "escalation.dong": lambda d, s: f"đóng escalation {ma(d.get('escalation_id'))}",
    "escalation.tra_loi": lambda d, s: "Đại ca trả lời escalation",
    "estop.bat": lambda d, s: "Estop bật",
    "estop.tat": lambda d, s: "Estop tắt",
    "khe.dang_ky": lambda d, s: f"{_khe(d)} đăng ký ({chon({'claude': 'claude', 'codex': 'codex'}, d.get('cli'))})",
    "khe.bat": lambda d, s: f"{_khe(d)} · Đại ca bật",
    "khe.tat": lambda d, s: f"{_khe(d)} · Đại ca tắt",
    "khe.ket_noi": lambda d, s: f"{_khe(d)} kết nối lại",
    "khe.mat_ket_noi": lambda d, s: f"{_khe(d)} mất nhịp tim",
    "khe.han_muc": lambda d, s: f"{_khe(d)} cập nhật hạn mức",
    "khe.han_muc_khong_ro": lambda d, s: f"{_khe(d)} chưa đọc được hạn mức",
    "khe.cau_dao_ngat": lambda d, s: f"{_khe(d)} · cầu dao ngắt ({chon(CAU_DAO, d.get('ly_do'))})",
    "khe.cau_dao_dong": lambda d, s: f"{_khe(d)} · cầu dao đóng ({chon(CAU_DAO, d.get('ly_do'))})",
    "chay.bat_dau": lambda d, s: f"{_khe(d)} · {_luot(d)}"
    + (f" · lần {so(d['lan'])}" if isinstance(d.get("lan"), int) and d["lan"] > 1 else ""),
    "chay.xong": lambda d, s: f"{_khe(d)} · {_luot(d)} · {chon(KET_CHAY, d.get('ket_thuc'))}",
    "chay.don_rac": lambda d, s: f"{_khe(d)} · dọn nhánh rác",
    "giao.nhan": lambda d, s: f"→ {_khe(d)} · {chon(BUOC, d.get('buoc'))}",
    "giao.snapshot": lambda d, s: f"lưu snapshot {_luot(d)}",
    "giao.thu_hoi": lambda d, s: f"thu hồi {_luot(d)} ({chon(THU_HOI, d.get('ly_do'))})",
    "giao.cong_bo": lambda d, s: f"công bố {_luot(d)} · {sha(d.get('commit'))}",
    "giao.ket_thuc": lambda d, s: f"{chon(BUOC, d.get('buoc'))} {_luot(d)} · {chon(KET_GIAO, d.get('ket_thuc'))}",
    "bao.moc": lambda d, s: f"{khe_tho(s.tac_nhan)} báo mốc {_luot(d)}",
    "bao.can_hoi": lambda d, s: f"{khe_tho(s.tac_nhan)} hỏi Đại ca ({chon(HOI, d.get('loai_hoi'))})",
    "bao.bi": lambda d, s: f"{khe_tho(s.tac_nhan)} báo bí ({chon(BI, d.get('ly_do'))})",
    "bao.xong": lambda d, s: f"{khe_tho(s.tac_nhan)} báo xong {_luot(d)}",
    "bao.het_han_muc": lambda d, s: f"{khe_tho(s.tac_nhan)} báo hết hạn mức",
    "tho.tu_choi": lambda d, s: f"trạm từ chối báo cáo của {_khe(d)}",
    "kiem.lai": lambda d, s: f"kiểm lại {_luot(d)}: {'đạt' if d.get('dat') is True else 'không đạt'}",
    "qc.ket_qua": lambda d, s: chon(QC, d.get("ket_luan"), "QC ?"),
    "pr.mo": lambda d, s: f"mở PR #{so(d.get('pr'))}",
    "pr.khong_xac_minh": lambda d, s: f"PR #{so(d.get('pr'))} — {chon(PR_LY_DO, d.get('ly_do'))}",
    "pr.da_merge": lambda d, s: f"PR #{so(d.get('pr'))} đã merge đúng commit đã kiểm",
    "bead.vao_cot_3": lambda d, s: "chờ review" + (" · cờ đỏ" if d.get("co_do") is True else ""),
    "bead.dong": lambda d, s: "đã đóng",
    "spec.duyet": lambda d, s: f"Đại ca duyệt spec · {len(d.get('bead_moi') or [])} bead mới",
    "spec.tra_ve": lambda d, s: "Đại ca trả về spec",
    "spec.xong": lambda d, s: f"spec xong · {sha(d.get('commit'))}",
    "spec.cho_merge": lambda d, s: "spec đã duyệt, chờ merge",
    "feature.xong": lambda d, s: "feature xong, chờ Đại ca đóng",
    **MAU_NHO,
}
