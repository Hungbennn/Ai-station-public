"""Mẫu câu của sự kiện ký ức (`nho.*`, D39) và vài loại hệ thống. Không bao giờ đưa nội dung ký ức, `ly_do` tự do,
`loi` ra ngoài — chỉ mã ký ức, phạm vi đã kiểm dạng, số sự kiện. `nho.bo_bi_mat` theo mẫu plan 1b-4 G22."""
from tram.suy.mo_ta_su_kien import chon, ma, pham_vi, so

NGUON_BI_MAT = {"ban_giao": "bàn giao", "da_chot": "trả lời escalation", "tra_ve": "trả về spec"}
NHOM_BI_MAT = {"khoa_da_biet": "khoá đã biết", "khoa_rieng": "khối khoá riêng", "gan_gia_tri": "gán giá trị nhạy cảm",
               "entropy_cao": "chuỗi entropy cao"}
NGUON_TU_CHOI = {"dai_ca_ghi": "Đại ca ghi tay", "thang_cap": "thăng cấp"}
LOI_NAP = {"llm": "Claude API", "embedder": "embedder"}


def _bo_bi_mat(d, s) -> str:
    nhom = d.get("nhom") if isinstance(d.get("nhom"), dict) else {}
    ds = ", ".join(f"{NHOM_BI_MAT[k]} ×{so(v)}" for k, v in nhom.items() if k in NHOM_BI_MAT)
    return (f"Bỏ nguồn {chon(NGUON_BI_MAT, d.get('loai_nguon'))} (sự kiện #{so(d.get('su_kien_id'))}) vì có dấu hiệu "
            f"bí mật: {ds or '?'}")


MAU_NHO = {
    "nho.ghi": lambda d, s: f"ghi ký ức {ma(d.get('id'))} vào {pham_vi(d.get('pham_vi'))}",
    "nho.gop": lambda d, s: f"gộp {len(d.get('cu') or [])} ký ức thành {ma(d.get('moi'))}",
    "nho.thang_cap": lambda d, s: f"thăng cấp ký ức {ma(d.get('id'))} lên {pham_vi(d.get('pham_vi'))}",
    "nho.tu_choi": lambda d, s: f"từ chối ghi ký ức ({chon(NGUON_TU_CHOI, d.get('nguon'))})",
    "nho.xoa": lambda d, s: f"xoá mềm ký ức {ma(d.get('id'))}",
    "nho.xoa_cung": lambda d, s: f"xoá cứng ký ức {ma(d.get('id'))}",
    "nho.loi_llm": lambda d, s: f"lỗi Claude API khi nạp sự kiện #{so(d.get('su_kien_id'))}",
    "nho.loi_embedder": lambda d, s: f"lỗi embedder khi nạp sự kiện #{so(d.get('su_kien_id'))}",
    "nho.loi_tach": lambda d, s: f"bỏ sự kiện #{so(d.get('su_kien_id'))} không tách được",
    "nho.phuc_hoi": lambda d, s: f"nạp ký ức chạy lại ({chon(LOI_NAP, d.get('loai'))})",
    "nho.agent_ghi": lambda d, s: "agent ghi ký ức",
    "nho.bo_bi_mat": _bo_bi_mat,
    "may.cap_ma": lambda d, s: f"cấp mã ghép máy {ma(d.get('may_id'))}",
    "may.ghep_sai": lambda d, s: f"ghép máy sai {so(d.get('so_lan'))} lần",
    "may.ghep": lambda d, s: f"máy {ma(d.get('may_id'))} đã ghép",
    "ngan_sach.chu_ky_moi": lambda d, s: "ngân sách chu kỳ mới",
    "ngan_sach.dot_spec_moi": lambda d, s: "đợt spec mới",
    "phieu.loi": lambda d, s: f"phiếu lỗi ({len(d.get('loi') or [])} lỗi)",
    "dieu_phoi.nhip": lambda d, s: "nhịp phiên điều phối",
}
