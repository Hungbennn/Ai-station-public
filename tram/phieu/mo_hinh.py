"""Phiếu giao (spec 3 §6.1). Phần 4 dựng `DeXuatPhieu` (nội dung); phần 3 cấp `giao_id`, `luot`, `khe_id`, `han_giu`,
`ma_giao` khi phát phiếu. `ma_giao` là CREDENTIAL: không vào sự kiện, log hay dashboard (`an_toan()`, `che_ma_giao`)."""
import secrets
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, model_serializer

from tram.cau_hinh.lenh import khop_bat_ky, kiem_mau

GIO = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
SHA = r"^[0-9a-f]{7,40}$"
NHANH = r"^tram/[A-Za-z0-9][A-Za-z0-9._-]{0,63}(/[A-Za-z0-9][A-Za-z0-9._-]{0,63})*$"
VAI_CUA_BUOC = {"code": "coder", "qc": "qc", "spec": "spec"}


class _Mau(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Repo(_Mau):
    kho: str = Field(min_length=1, max_length=500)
    nhanh: str = Field(pattern=NHANH)             # ref công bố — luôn bắt đầu bằng tram/ (Q7)
    ref_tam: str | None = Field(default=None, pattern=NHANH)   # đề xuất §6.4 (chờ S7) — 3a-1 để None
    cha: str = Field(pattern=SHA)                 # SHA trạm đã chấp nhận (§6.5)
    nhanh_chinh: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$")


class NganSach(_Mau):
    so_lan_chay: int = Field(ge=1, le=3)          # #13
    phut: int = Field(ge=1, le=600)
    token_ra: int = Field(ge=1, le=5_000_000)


class DeXuatPhieu(_Mau):
    du_an: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    bead_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
    tieu_de: str = Field(max_length=300)
    buoc: Literal["code", "qc", "spec"]
    vai: Literal["coder", "qc", "spec"]
    repo: Repo
    goi_ngu_canh: str = Field(max_length=400_000)
    ngan_sach: NganSach
    lenh_kiem: list[str] = Field(max_length=20)
    lenh_cho_phep: list[str] = Field(max_length=50)
    can_lenh_kiem: bool
    can_moi_truong_kiem: bool
    tieu_chi: list[str] = Field(min_length=1, max_length=100)
    co: dict | None = None
    khoa_chong_trung: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_serializer(mode="wrap")
    def _xuat(self, handler):
        d = handler(self)
        if self.co is None:
            d.pop("co", None)
        return d

    @model_validator(mode="after")
    def _nhat_quan(self):
        loi = []
        if self.vai != VAI_CUA_BUOC[self.buoc]:
            loi.append(f"bước {self.buoc} phải do vai {VAI_CUA_BUOC[self.buoc]}")
        if self.repo.nhanh != f"tram/{'spec-' if self.buoc == 'spec' else ''}{self.bead_id}":
            loi.append("repo.nhanh phải là tram/<bead> (code, qc) hoặc tram/spec-<bead> (spec)")
        loi += [f"lenh_cho_phep {m!r}: {e}" for m in self.lenh_cho_phep if (e := kiem_mau(m))]
        if self.can_lenh_kiem and not self.lenh_kiem:
            loi.append("can_lenh_kiem mà không có lệnh bắt buộc")
        loi += [f"lệnh bắt buộc không khớp lenh_cho_phep: {l}" for l in self.lenh_kiem
                if khop_bat_ky(l, self.lenh_cho_phep) is None]
        if self.buoc == "spec" and (self.lenh_cho_phep or self.can_lenh_kiem or self.can_moi_truong_kiem):
            loi.append("phiếu spec không chạy mã dự án: lenh_cho_phep rỗng, không lệnh kiểm, không môi trường kiểm")
        if any(not t.strip() or len(t) > 1000 for t in self.tieu_chi):
            loi.append("tiêu chí rỗng hoặc dài quá 1000 ký tự")
        if loi:
            raise ValueError("; ".join(loi))
        return self


class Phieu(DeXuatPhieu):
    giao_id: str = Field(pattern=r"^g-\d{8}-\d{4,}$")
    luot: int = Field(ge=1)
    khe_id: str = Field(pattern=r"^[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}$")
    han_giu: str = Field(pattern=GIO)
    ma_giao: str = Field(pattern=r"^[A-Za-z0-9_-]{22}$")

    def an_toan(self) -> dict:
        """Phiếu bỏ `ma_giao` — dạng duy nhất được log/hiện."""
        return self.model_dump(exclude={"ma_giao"})


def sinh_ma_giao() -> str:
    """128 bit ngẫu nhiên, base64url 22 ký tự (§4)."""
    return secrets.token_urlsafe(16)


def che_ma_giao(van_ban: str, ma_giao: str | None) -> str:
    return van_ban.replace(ma_giao, "***") if ma_giao else van_ban


class LuotCu(Exception):
    """Thẻ chắn từ chối (§6.3): `giao_id` không phải phiếu hiệu lực của bead, hoặc `luot` ≠ `luot` hiện hành."""

    def __init__(self, bead_id: str | None, du_an: str | None, luot_dung: int | None, thu_hoi: bool):
        super().__init__("luot-cu")
        self.bead_id, self.du_an, self.luot_dung, self.thu_hoi = bead_id, du_an, luot_dung, thu_hoi
