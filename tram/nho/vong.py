"""Một lượt nạp ký ức (spec 1b §6.1–6.4), mỗi 2 phút: thử embedder → đối soát thao tác dở → sự kiện sau `moc_nho`.

Embedder chết / Claude API lỗi → dừng lượt, mốc không tiến, `nho.loi_embedder` / `nho.loi_llm` MỘT lần mỗi đợt lỗi,
gắn vào dự án + bead của sự kiện nguồn đang kẹt; dự án đó xử lý xong một sự kiện nguồn → `nho.phuc_hoi {loai}`."""
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

import anthropic

from tram.duong_dan import bay_gio
from tram.nho.ap_dung import TAC_NHAN, ap_dung, luu_ke_hoach
from tram.nho.bi_mat import LoiBiMat
from tram.nho.cac_nguon import doc_nguon
from tram.nho.embed import Embedder, LoiEmbedder
from tram.nho.ke_hoach import PHIEN_BAN, lap_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.llm import LoiLLMNho
from tram.nho.loi_nap import LOI_NHO, dang_loi, la_nguon, phuc_hoi
from tram.nho.luat import LuatDuAn, luat_cua_du_an
from tram.nho.mo_hinh import ma_thao_tac
from tram.nho.nhat_ky import NhatKy
from tram.nho.pham_vi import LoiVungCap
from tram.su_kien.kho import KhoSuKien, SuKien

SO_SU_KIEN_MOI_LUOT = 100


@dataclass
class NguCanhNho:
    kho: KhoKyUc
    embedder: Embedder
    client: object                       # anthropic.Anthropic (test: ClientGia)
    kho_sk: KhoSuKien
    nhat_ky: NhatKy
    vai_tach: tuple[str, str]
    vai_gop: tuple[str, str]
    luat_cua: Callable[[str], LuatDuAn] = luat_cua_du_an
    luc: Callable[[], str] = bay_gio
    vai_thang_cap: tuple[str, str] | None = None     # 1b-3: None → bảo trì đêm không thăng cấp


@dataclass
class BaoCaoLuot:
    su_kien: int = 0          # sự kiện nguồn đã áp dụng xong
    ky_uc_moi: int = 0
    bo: int = 0               # nho.loi_tach, nho.bo_bi_mat
    loi: str | None = None


def _bao_loi(nc: NguCanhNho, loai: str, e: Exception, bc: BaoCaoLuot, ket) -> BaoCaoLuot:
    bc.loi = f"{loai}: {type(e).__name__}: {str(e)[:200]}"
    if ket is None:                    # lỗi lúc thử embedder: gắn vào sự kiện nguồn chờ đầu tiên (thao tác dở trước)
        ket = next(iter([(t.ke_hoach["du_an"], t.ke_hoach["bead_id"], t.su_kien_id) for t in nc.nhat_ky.dang_do()
                         if t.su_kien_id]                  # thao tác ghi tay / thăng cấp (id 0) không phải chỗ kẹt
                        + [(s.du_an, s.bead_id, s.id) for s in nc.kho_sk.sau_id(nc.nhat_ky.moc(), SO_SU_KIEN_MOI_LUOT)
                           if la_nguon(s, nc.kho_sk)]), None)
    if ket is not None and dang_loi(nc.kho_sk, ket[0], loai) is None:
        nc.kho_sk.ghi(ket[0], LOI_NHO[loai], {"su_kien_id": ket[2], "loi": str(e)[:300]}, bead_id=ket[1],
                      tac_nhan=TAC_NHAN)
    return bc


def _bo(nc: NguCanhNho, sk: SuKien, e: Exception, bc: BaoCaoLuot) -> None:
    """Hết lượt guardrail / dữ liệu sai kiểu / cấu hình dự án hỏng / có bí mật (D23): bỏ, mốc tiến (không kẹt)."""
    loai, du_lieu = (e.su_kien(sk.id) if isinstance(e, LoiBiMat)      # nho.bo_bi_mat: chỉ nhóm + số lượng
                     else ("nho.loi_tach", {"su_kien_id": sk.id, "loi": f"{type(e).__name__}: {e}"[:300]}))
    nc.kho_sk.ghi(sk.du_an, loai, du_lieu, bead_id=sk.bead_id, tac_nhan=TAC_NHAN)
    nc.nhat_ky.hoan_tat(ma_thao_tac(sk.id, PHIEN_BAN), sk.id, "bo")
    bc.bo += 1


def _mot_su_kien(nc: NguCanhNho, sk: SuKien, bc: BaoCaoLuot) -> bool:
    """True khi là sự kiện nguồn và đã xong (áp dụng hoặc bỏ)."""
    try:
        dv = doc_nguon(sk, nc.kho_sk)                      # phần 4: tra bao.xong, giao.nhan trong kho sự kiện
        luat = None if dv is None else nc.luat_cua(dv.du_an)
    except sqlite3.OperationalError:
        raise                                              # kho sự kiện bận/khoá: lượt sau thử lại, KHÔNG bỏ sự kiện
    except Exception as e:                                 # noqa: BLE001 — dữ liệu sai kiểu, yaml hỏng: sự kiện "độc"
        _bo(nc, sk, e, bc)
        return True
    if dv is None:
        nc.nhat_ky.dat_moc(sk.id)
        return False
    with nc.kho.khoa_gop:                                  # 1b-3: `/ghi` của Đại ca gộp ở luồng HTTP
        try:
            buoc = lap_ke_hoach(dv, kho=nc.kho, embedder=nc.embedder, client=nc.client, vai_tach=nc.vai_tach,
                                vai_gop=nc.vai_gop, luat=luat, luc=nc.luc())
        except (LoiLLMNho, LoiVungCap) as e:
            _bo(nc, sk, e, bc)
            return True
        tt = luu_ke_hoach(nc.nhat_ky, su_kien_id=sk.id, phien_ban=PHIEN_BAN, du_an=dv.du_an, bead_id=dv.bead_id,
                          buoc=buoc)
        bc.ky_uc_moi += ap_dung(tt, kho=nc.kho, kho_sk=nc.kho_sk, nhat_ky=nc.nhat_ky)
    bc.su_kien += 1
    return True


def mot_luot(nc: NguCanhNho, *, gioi_han: int = SO_SU_KIEN_MOI_LUOT) -> BaoCaoLuot:
    """Lỗi khác (đĩa…) nổi lên cho vòng ngoài ghi log; mốc chỉ tiến ở sự kiện đã xong."""
    bc, ket = BaoCaoLuot(), None
    try:
        nc.embedder.kiem()
        for tt in nc.nhat_ky.dang_do():                    # khởi động lại / lượt trước hỏng: làm tiếp
            with nc.kho.khoa_gop:                          # `/ghi` có thể vừa làm xong chính thao tác này
                if (tt := nc.nhat_ky.lay(tt.ma)).trang_thai != "dang":
                    continue
                ket = tt.ke_hoach["du_an"], tt.ke_hoach["bead_id"], tt.su_kien_id
                bc.ky_uc_moi += ap_dung(tt, kho=nc.kho, kho_sk=nc.kho_sk, nhat_ky=nc.nhat_ky)
            phuc_hoi(nc.kho_sk, ket[0])
        for sk in nc.kho_sk.sau_id(nc.nhat_ky.moc(), gioi_han):
            ket = sk.du_an, sk.bead_id, sk.id
            if _mot_su_kien(nc, sk, bc):
                phuc_hoi(nc.kho_sk, sk.du_an)
    except LoiEmbedder as e:
        return _bao_loi(nc, "embedder", e, bc, ket)
    except anthropic.APIError as e:                        # mạng, 5xx, khoá sai — khác hết lượt guardrail (G9)
        return _bao_loi(nc, "llm", e, bc, ket)
    return bc
