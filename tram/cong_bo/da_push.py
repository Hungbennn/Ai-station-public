"""Nhận `POST /api/tho/da-push` và công bố (spec 3 §6.4, §6.6, H2). Thứ tự: thuộc máy (403) → [giao dịch] request_id
cũ / thẻ chắn (409) / ref tạm đúng lượt (422) / `han_giu` còn đủ (bộ canh không thu hồi giữa lúc push) → đối soát
thao tác cũ → lấy commit từ nguồn (ref tạm hay kho thợ — §14 chưa chốt) → [giao dịch] thẻ chắn lại, hậu duệ của ref
công bố hiện tại (hoặc `cha`), ghi thao tác BỀN → CAS ref công bố → [giao dịch] phiếu còn hiệu lực → `giao.cong_bo`;
không còn → hoàn tác. Kết quả dứt khoát được nhớ theo request_id; kết quả tạm (`ly_do` trong `TAM`) thì thợ gửi lại
cùng request_id."""
import sqlite3
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.cong_bo.doi_soat import doi_soat_bead
from tram.cong_bo.git import day_cas, la_hau_due
from tram.cong_bo.ket_qua_day import chot, sau_cas, the_chan
from tram.cong_bo.nguon import ref_tam_cua
from tram.cong_bo.op import MO, cong_bo_cua_luot, cong_bo_hien_tai, dam_bao_luoc_do, ghi_cong_bo, mo_op
from tram.duong_dan import doc_luc
from tram.phieu.kho import KhoPhieu, LuotCu
from tram.phieu.yeu_cau_tho import digest_than, ket_qua_cu, kiem_thuoc_may

TAM = ("sap-het-han-giu", "dang-cong-bo", "khong-thay-commit", "khong-ro", "remote-tu-choi")


class ThanDaPush(BaseModel):
    model_config = ConfigDict(extra="forbid")
    khe_id: str = Field(max_length=70)
    giao_id: str = Field(max_length=40)
    luot: int = Field(ge=1)
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    ref_tam: str = Field(pattern=r"^tram/luot/[A-Za-z0-9][A-Za-z0-9._-]{0,63}/[1-9][0-9]{0,8}$")
    request_id: str = Field(pattern=r"^[A-Za-z0-9_-]{8,64}$")


class ChuaCongBoDuoc(Exception):
    """503: chưa chốt phương án (§14) hoặc trạm chưa có kho của dự án."""


class RefTamSai(ValueError):
    """422: ref tạm không phải ref của lượt này."""


def nhan_da_push(kho: KhoPhieu, may_id: str, than: ThanDaPush, *, bay_gio: datetime, cb: CauHinhCongBo,
                 nguon, kho_cua: Callable[[str], Path]) -> dict:
    """`kho_cua(du_an)`: kho của tài khoản trạm (mặc định `kho_kiem` của phần 4 — `~/.tram/kho-kiem/<dự án>`)."""
    kiem_thuoc_may(kho, may_id, than.khe_id, than.giao_id)
    if nguon is None:
        raise ChuaCongBoDuoc("chua-chot-phuong-an")
    dam_bao_luoc_do(kho)
    dg, t = digest_than(than.model_dump()), cb.thoi_gian_cho_giay
    with kho.giao_dich():
        if (cu := ket_qua_cu(kho, than.request_id, dg)) is not None:
            return cu
        b = the_chan(kho, than, bay_gio)
    if isinstance(b, LuotCu):
        raise b
    p, kho_git = b.phieu, kho_cua(b.phieu.du_an)
    if not (kho_git / ".git").exists():
        raise ChuaCongBoDuoc("chua-co-kho-tram")
    if than.ref_tam != ref_tam_cua(p.bead_id, p.luot):
        raise RefTamSai(f"ref tạm của lượt này là {ref_tam_cua(p.bead_id, p.luot)}")
    if doc_luc(p.han_giu) - bay_gio < timedelta(minutes=cb.giu_toi_thieu_phut):
        return {"cong_bo": False, "ly_do": "sap-het-han-giu"}
    if doi_soat_bead(kho, p.du_an, p.bead_id, kho_git=kho_git, timeout=t, bay_gio=bay_gio, cu_hon_giay=2 * t) in MO:
        return {"cong_bo": False, "ly_do": "dang-cong-bo"}
    if nguon.lay(kho_git, may_id=may_id, du_an=p.du_an, ref_tam=than.ref_tam, giao_id=p.giao_id,
                 timeout=t) != than.commit:
        return {"cong_bo": False, "ly_do": "khong-thay-commit"}
    with kho.giao_dich():
        b = the_chan(kho, than, bay_gio)
        if isinstance(b, LuotCu):
            loi = b
        else:
            loi, sha_cu = None, cong_bo_hien_tai(kho, p.du_an, p.bead_id)
            kq_ok = {"cong_bo": True, "commit": than.commit, "ref": p.repo.nhanh}
            if not la_hau_due(kho_git, sha_cu or p.repo.cha, than.commit):
                return chot(kho, than, dg, {"cong_bo": False, "ly_do": "khong-phai-hau-due"}, p.giao_id, bay_gio)
            if than.commit == sha_cu:                       # ref công bố đã là commit này: chỉ ghi cho lượt này
                if cong_bo_cua_luot(kho, p.du_an, p.bead_id, p.luot) != sha_cu:
                    ghi_cong_bo(kho, du_an=p.du_an, bead_id=p.bead_id, luot=p.luot, commit=sha_cu, ref=p.repo.nhanh,
                                luc=bay_gio)
                return chot(kho, than, dg, kq_ok, p.giao_id, bay_gio)
            try:
                op_id = mo_op(kho, p, request_id=than.request_id, commit=than.commit, sha_cu=sha_cu, luc=bay_gio)
            except sqlite3.IntegrityError:
                return {"cong_bo": False, "ly_do": "dang-cong-bo"}
    if loi is not None:
        raise loi
    kq_day = day_cas(kho_git, than.commit, p.repo.nhanh, sha_cu, timeout=t)
    return sau_cas(kho, than, dg, p, op_id, sha_cu, kq_ok, kq_day, kho_git=kho_git, t=t, bay_gio=bay_gio, nguon=nguon)

