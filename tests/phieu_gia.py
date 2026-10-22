"""Đề xuất phiếu mẫu cho test (CHỈ DÙNG TRONG TEST) — phần 4 chưa có, test tự dựng `DeXuatPhieu`."""
import hashlib

from tram.phieu.mo_hinh import DeXuatPhieu

CHA = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"


def khoa(*phan: object) -> str:
    return "sha256:" + hashlib.sha256(":".join(map(str, phan)).encode()).hexdigest()


def de_xuat(bead_id: str = "hr-6xe1", *, buoc: str = "code", du_an: str = "hr-codex", cha: str = CHA,
            **ghi_de) -> DeXuatPhieu:
    vai = {"code": "coder", "qc": "qc", "spec": "spec"}[buoc]
    chay_ma = buoc != "spec"
    d = {"du_an": du_an, "bead_id": bead_id, "tieu_de": "Sửa cắt UTF-8 tóm tắt hoàn tiền", "buoc": buoc, "vai": vai,
         "repo": {"kho": f"~/tram/kho/{du_an}", "nhanh": f"tram/{'spec-' if buoc == 'spec' else ''}{bead_id}",
                  "cha": cha, "nhanh_chinh": "main"},
         "goi_ngu_canh": "# Gói\n", "ngan_sach": {"so_lan_chay": 3, "phut": 90, "token_ra": 200000},
         "lenh_kiem": ["php artisan test --filter TomTatHoanTien"] if buoc == "code" else [],
         "lenh_cho_phep": ["php artisan test --filter *", "npm run test:unit"] if chay_ma else [],
         "can_lenh_kiem": buoc == "code", "can_moi_truong_kiem": chay_ma,
         "tieu_chi": ["Tên kết thúc 'ỷ' không mất byte"], "khoa_chong_trung": khoa(du_an, cha, bead_id, buoc)}
    d.update(ghi_de)
    return DeXuatPhieu.model_validate(d)
