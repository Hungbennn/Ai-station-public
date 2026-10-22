"""Mô hình hạn mức theo cửa sổ (spec 3 §8.1). Không đọc được là `chua_biet` — KHÔNG BAO GIỜ ghi 0%."""
from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tram.duong_dan import doc_luc

GIO = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
CUA_SO_CHINH = ("5h", "tuan")          # Claude: luôn có hai cửa sổ này — thiếu trong số đo thì là chưa biết
PHUT_TEN = {300: "5h", 10080: "tuan"}
NGUONG_DOI = 5.0                        # §10: khe.han_muc khi một cửa sổ đổi ≥ 5 điểm %


class CuaSo(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    loai: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,48}$")
    trang_thai: Literal["biet", "chua_biet"]
    phan_tram: float | None = Field(default=None, ge=0, le=100)
    reset_luc: str | None = Field(default=None, pattern=GIO)
    doc_luc: str | None = Field(default=None, pattern=GIO)
    het_hieu_luc: str | None = Field(default=None, pattern=GIO)

    @model_validator(mode="after")
    def _biet_can_so_do(self):
        if self.trang_thai == "biet" and (self.phan_tram is None or self.doc_luc is None):
            raise ValueError("cửa sổ 'biet' phải có phan_tram và doc_luc")
        return self


class HanMuc(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    khe_id: str = Field(pattern=r"^[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}$")
    cua_so: list[CuaSo] = Field(default_factory=list, max_length=8)
    nguon: Literal["stream", "app-server", "log", "regex", "chua_co"] = "chua_co"

    @model_validator(mode="after")
    def _loai_duy_nhat(self):
        if len({c.loai for c in self.cua_so}) != len(self.cua_so):
            raise ValueError("mỗi loại cửa sổ chỉ một lần")
        return self


def ten_cua_so(thoi_luong_phut: int, ten_goc: str) -> str:
    """300 phút → `5h`, 10080 → `tuan`; cửa sổ khác giữ tên gốc + thời lượng, không tự bỏ (§8.1)."""
    return PHUT_TEN.get(thoi_luong_phut) or f"{ten_goc}:{thoi_luong_phut}m"


def _het_han(c: CuaSo, bay_gio: datetime, tuoi_toi_da_gio: float) -> bool:
    if c.trang_thai != "biet":
        return False
    moc = [doc_luc(x) for x in (c.reset_luc, c.het_hieu_luc) if x]
    return any(bay_gio >= m for m in moc) or bay_gio - doc_luc(c.doc_luc) > timedelta(hours=tuoi_toi_da_gio)


def lam_moi(hm: HanMuc | None, khe_id: str, bay_gio: datetime, *, tuoi_toi_da_gio: float = 6,
            cac_loai: tuple[str, ...] = CUA_SO_CHINH) -> HanMuc:
    """Số đo quá `reset_luc`/`het_hieu_luc` hoặc quá tuổi → `chua_biet` (giữ `doc_luc` để hiện "đọc lúc");
    thiếu cửa sổ chính → thêm `chua_biet`."""
    cs = [CuaSo(loai=c.loai, trang_thai="chua_biet", doc_luc=c.doc_luc) if _het_han(c, bay_gio, tuoi_toi_da_gio)
          else c for c in (hm.cua_so if hm else [])]
    cs += [CuaSo(loai=l, trang_thai="chua_biet") for l in cac_loai if l not in {c.loai for c in cs}]
    return HanMuc(khe_id=khe_id, cua_so=cs, nguon=hm.nguon if hm else "chua_co")


def co_chua_biet(hm: HanMuc) -> bool:
    return any(c.trang_thai == "chua_biet" for c in hm.cua_so)


def doi_dang_ke(cu: HanMuc | None, moi: HanMuc) -> bool:
    """Có cần ghi `khe.han_muc` không (§10): đổi ≥ 5 điểm %, đổi `reset_luc`, đổi biết/chưa biết, đổi tập cửa sổ."""
    if cu is None:
        return True
    a, b = {c.loai: c for c in cu.cua_so}, {c.loai: c for c in moi.cua_so}
    if a.keys() != b.keys():
        return True
    return any(a[k].trang_thai != b[k].trang_thai or a[k].reset_luc != b[k].reset_luc
               or abs((a[k].phan_tram or 0) - (b[k].phan_tram or 0)) >= NGUONG_DOI for k in a)
