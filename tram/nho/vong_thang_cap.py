"""Một lượt thăng cấp mỗi ngày trong `tram nho chay` (spec 1b §8) — chạy trong luồng nạp, cùng giờ bảo trì đêm.

Mỗi cặp là một thao tác bền trong nhật ký (`tc:<cặp>`, su_kien_id 0 — không đụng `moc_nho`), áp dụng idempotent như
sự kiện nguồn (§6.4). `nho.thang_cap` ghi TRƯỚC khi áp dụng (một lần theo `id`): crash giữa chừng thì lượt nạp sau
làm tiếp thao tác dở, sự kiện không mất; ap_dung phát từ kế hoạch ở cả lần đầu và replay. Chạm luật → `nho.tu_choi` + sổ
cặp; LLM bỏ → sổ cặp (không thử lại mỗi ngày). Embedder / Claude API lỗi → dừng lượt, không ghi sổ: mai thử lại."""
from dataclasses import dataclass
from datetime import datetime

from tram.cau_hinh.du_an import liet_ke_du_an
from tram.nho.ap_dung import TAC_NHAN, ap_dung
from tram.nho.ke_hoach_thang_cap import KetQuaCap, lap_ke_hoach_cap
from tram.nho.llm import LoiLLMNho
from tram.nho.luat_chung import luat_moi_du_an
from tram.nho.thang_cap import cac_cap_da_co, tim_cap
from tram.nho.vong import NguCanhNho

TOI_DA_CAP_MOI_NGAY = 10          # trần chi phí Claude mỗi ngày
DU_AN_HE = "_tram"


@dataclass
class BaoCaoThangCap:
    cap: int = 0
    thang_cap: int = 0
    tu_choi: int = 0
    bo: int = 0
    loi: str | None = None


def _mot_cap(nc: NguCanhNho, cap, kq: KetQuaCap, bc: BaoCaoThangCap) -> None:
    if kq.buoc is None:
        if kq.tu_choi:
            nc.kho_sk.ghi(DU_AN_HE, "nho.tu_choi", {"ly_do": "; ".join(kq.ly_do)[:300], "nguon": "thang_cap",
                                                   "id_goc": [cap.a.id, cap.b.id]}, tac_nhan=TAC_NHAN)
        nc.nhat_ky.ghi_cap(cap.khoa, "tu_choi" if kq.tu_choi else "bo")
        bc.tu_choi, bc.bo = bc.tu_choi + kq.tu_choi, bc.bo + (not kq.tu_choi)
        return
    k = kq.buoc.ky_uc
    tt = nc.nhat_ky.bat_dau(f"tc:{cap.khoa}", 0, {"du_an": DU_AN_HE, "bead_id": None, "buoc": [kq.buoc.sang_dict()]})
    ap_dung(tt, kho=nc.kho, kho_sk=nc.kho_sk, nhat_ky=nc.nhat_ky)
    bc.thang_cap += 1


def mot_lan_thang_cap(nc: NguCanhNho, bay_gio: datetime, *, vai_soan: tuple[str, str], cac_du_an=liet_ke_du_an,
                      toi_da: int = TOI_DA_CAP_MOI_NGAY) -> BaoCaoThangCap:
    """Không ném: lỗi ghi vào `BaoCaoThangCap.loi` để bảo trì đêm (dọn phiên bản, sao lưu) vẫn chạy tiếp."""
    bc = BaoCaoThangCap()
    try:
        ten = [t for t in cac_du_an() if not t.startswith("_")]
        luat = luat_moi_du_an(ten, nc.luat_cua)            # yaml hỏng → không thăng cấp với danh sách thiếu
        nc.embedder.kiem()
        ds = tim_cap(nc.kho, nc.embedder.mo_hinh, bo_qua=cac_cap_da_co(nc.kho, nc.nhat_ky), toi_da=toi_da)
        bc.cap = len(ds)
        for cap in ds:
            with nc.kho.khoa_gop:
                hien = nc.kho.lay([cap.a.id, cap.b.id])
                if any(i not in hien or hien[i].da_xoa for i in (cap.a.id, cap.b.id)):
                    continue
                if cap.khoa in cac_cap_da_co(nc.kho, nc.nhat_ky):
                    continue
                try:
                    kq = lap_ke_hoach_cap(cap, kho=nc.kho, embedder=nc.embedder, client=nc.client,
                                          vai_soan=vai_soan, vai_gop=nc.vai_gop, luat=luat, cac_du_an=ten,
                                          bay_gio=bay_gio)
                except LoiLLMNho as e:
                    kq = KetQuaCap(None, [f"LLM: {e}"])
                _mot_cap(nc, cap, kq, bc)
    except Exception as e:                  # noqa: BLE001 — LoiEmbedder, anthropic.APIError, yaml hỏng: mai thử lại
        bc.loi = f"{type(e).__name__}: {str(e)[:200]}"
    return bc
