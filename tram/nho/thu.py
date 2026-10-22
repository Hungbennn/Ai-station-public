"""Chế độ thử (spec 1b §16.3): tách ký ức từ lịch sử sự kiện thật, KHÔNG embed, KHÔNG ghi kho, không tiến mốc.

Để Đại ca đọc 20 ký ức đầu: nội dung, phạm vi trạm sẽ đặt, lý do luật cứng (nếu có)."""
from collections.abc import Callable

from tram.nho.bi_mat import LoiBiMat
from tram.nho.cac_nguon import doc_nguon
from tram.nho.ke_hoach import cac_ky_uc_tach, nhanh_cuoi
from tram.nho.llm import LoiLLMNho
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.mo_hinh import ap_san
from tram.nho.pham_vi import pham_vi_du_an
from tram.su_kien.kho import KhoSuKien


def chay_thu(kho_sk: KhoSuKien, client, vai_tach: tuple[str, str], luat_cua: Callable[[str], LuatDuAn], *,
             du_an: str | None = None, tu_id: int = 0, gioi_han: int = 20) -> str:
    dong = ["# Thử nạp ký ức (không ghi)", ""]
    so, moc = 0, tu_id
    while so < gioi_han:
        ds = kho_sk.sau_id(moc, 200)
        if not ds:
            break
        for sk in ds:
            moc = sk.id
            try:
                dv = doc_nguon(sk, kho_sk)
            except Exception as e:                         # noqa: BLE001 — vòng nạp sẽ bỏ (nho.loi_tach, nho.bo_bi_mat)
                nhan = "BỎ VÌ CÓ DẤU HIỆU BÍ MẬT" if isinstance(e, LoiBiMat) else "SỰ KIỆN ĐỘC"     # D23
                dong.append(f"- sự kiện {sk.id} ({sk.loai}, {sk.bead_id}): {nhan} — {str(e)[:200]}")
                continue
            if dv is None or (du_an and dv.du_an != du_an):
                continue
            try:
                cac = cac_ky_uc_tach(dv, client, vai_tach)
            except LoiLLMNho as e:
                dong.append(f"- sự kiện {sk.id} ({sk.loai}, {sk.bead_id}): LỖI TÁCH — {str(e)[:200]}")
                continue
            luat = luat_cua(dv.du_an)
            for k in cac:
                ly_do = ly_do_nghiep_vu(k.noi_dung, luat, co_ten_rieng=k.co_ten_rieng)
                pv = pham_vi_du_an(dv.du_an, nhanh_cuoi(dv, k, luat))
                dong.append(f"- [{pv}] q={ap_san(k.quan_trong, [dv.nguon]):.2f} — {k.noi_dung}"
                            f"  _(sự kiện {sk.id} {sk.loai} {sk.bead_id}"
                            + (f"; luật cứng: {', '.join(ly_do)}" if ly_do else "") + ")_")
                so += 1
            if so >= gioi_han:
                break
    dong += ["", f"Tổng: {so} ký ức dự kiến; đọc tới sự kiện {moc}."]
    return "\n".join(dong)
