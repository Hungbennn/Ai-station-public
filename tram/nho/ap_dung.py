"""Áp dụng kế hoạch ghi từ nhật ký — idempotent, làm tiếp được sau crash (spec 1b §6.4).

Mỗi ký ức: xoá mềm bản cũ (gộp/thay) → ghi bản mới theo id ổn định → sự kiện `nho.ghi` (+ `nho.gop`) một lần
→ đánh dấu bước. Hết các ký ức → hoàn tất + tiến mốc cùng giao dịch. Bước nào lỗi: thao tác vẫn `dang`."""
from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import BuocGhi, ma_thao_tac
from tram.nho.nhat_ky import NhatKy, ThaoTacNho
from tram.su_kien.kho import KhoSuKien

TAC_NHAN = "tram/nho"


def luu_ke_hoach(nhat_ky: NhatKy, *, su_kien_id: int, phien_ban: int, du_an: str, bead_id: str | None,
                 buoc: list[BuocGhi]) -> ThaoTacNho:
    """Lưu kết quả tách (ID ký ức ổn định) TRƯỚC khi đụng kho. Phát lại: giữ kế hoạch cũ."""
    return nhat_ky.bat_dau(ma_thao_tac(su_kien_id, phien_ban), su_kien_id,
                           {"du_an": du_an, "bead_id": bead_id, "buoc": [b.sang_dict() for b in buoc]})


def ghi_su_kien_mot_lan(kho_sk: KhoSuKien, du_an: str, bead_id: str | None, loai: str, du_lieu: dict,
                        khoa: str) -> bool:
    """Không ghi lần hai khi đã có sự kiện cùng loại mang cùng `du_lieu[khoa]` (crash giữa sự kiện và nhật ký)."""
    def khop(s) -> bool:
        return s.du_lieu.get(khoa) == du_lieu[khoa]

    da_co = (kho_sk.moi_nhat(du_an, bead_id, loai, dieu_kien=khop) is not None if bead_id is not None
             else bool(kho_sk.gan_day(du_an, loai, 1, du_lieu_co={khoa: du_lieu[khoa]})))
    if da_co:
        return False
    kho_sk.ghi(du_an, loai, du_lieu, bead_id=bead_id, tac_nhan=TAC_NHAN)
    return True


def ap_dung(tt: ThaoTacNho, *, kho: KhoKyUc, kho_sk: KhoSuKien, nhat_ky: NhatKy) -> int:
    """Trả số ký ức thật sự thêm mới ở lần chạy này."""
    du_an, bead_id = tt.ke_hoach["du_an"], tt.ke_hoach["bead_id"]
    if tt.ma.startswith("tc:"):
        k = tt.ke_hoach["buoc"][0]["ky_uc"]
        goc = k["nguon"][:2]
        ghi_su_kien_mot_lan(kho_sk, du_an, bead_id, "nho.thang_cap", {
            "id": k["id"], "pham_vi": k["pham_vi"], "id_goc": [n["id_goc"] for n in goc],
            "du_an": [n["du_an"] for n in goc], "hieu_luc_tu": k["hieu_luc_tu"]}, "id")
    them = 0
    for i, d in enumerate(tt.ke_hoach["buoc"]):
        if str(i) in tt.buoc_xong:
            continue
        b = BuocGhi.tu_dict(d)
        with kho.khoa:                                       # recall xen giữa không thấy lúc bản cũ đã xoá,
                                                             # bản mới chưa có
            kho.xoa_mem(b.xoa)                               # bản đã xoá thì không xoá lần hai
            them += kho.them(b.ky_uc)                        # đã có theo id thì bỏ qua
        k = b.ky_uc
        ghi_su_kien_mot_lan(kho_sk, du_an, bead_id, "nho.ghi",
                            {"id": k.id, "pham_vi": k.pham_vi, "nguon": list(k.nguon)}, "id")
        if b.xoa:
            ghi_su_kien_mot_lan(kho_sk, du_an, bead_id, "nho.gop", {"cu": list(b.xoa), "moi": k.id}, "moi")
        nhat_ky.danh_dau_buoc(tt.ma, str(i))
    nhat_ky.hoan_tat(tt.ma, tt.su_kien_id)
    return them
