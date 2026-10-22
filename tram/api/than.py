"""Thân yêu cầu POST lát 2a, 1b-3 (spec 2 §7, §12.3) — trường lạ bị từ chối (422)."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ThanGhi(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma_thao_tac: str = Field(min_length=8, max_length=64)
    expected_version: str = Field(max_length=100)


class ThanCot(ThanGhi):
    cot: Literal["ai-lam", "can-chot"]
    vi_sao: str | None = Field(default=None, max_length=2000)


class ThanChot(ThanGhi):
    tra_loi: list[Annotated[str, Field(max_length=4000)]] | None = Field(default=None, max_length=20)
    adr: str | None = Field(default=None, max_length=20)


class ThanTraVe(ThanGhi):
    gop_y: str = Field(min_length=1, max_length=4000)


class ThanTraLoi(ThanGhi):
    tra_loi: str = Field(min_length=1, max_length=4000)


class ThanDuyet(ThanGhi):
    expected_commit: str | None = Field(default=None, max_length=64)
    digest_bead: str | None = Field(default=None, max_length=128)


class ThanEstop(ThanGhi):
    ly_do: str | None = Field(default=None, max_length=500)


class ThanNhoXoa(ThanGhi):                                  # lát 1b-3 — màn Ký ức
    id: str = Field(pattern=r"^[A-Za-z0-9-]{1,64}$")


class ThanNhoGhi(ThanGhi):
    noi_dung: str = Field(min_length=1, max_length=600)
    pham_vi: str = Field(min_length=1, max_length=200)
    nhan: list[Annotated[str, Field(min_length=1, max_length=30)]] = Field(default_factory=list, max_length=5)


class _Kin(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ThanDieuKien(_Kin):                                   # TM-1 (D70, D71): chỉ ba nút có nút; QC/kiểm lại → 422
    ci: Literal[True]
    cot: bool
    hang_rao: bool


class ThanLenh(_Kin):                                       # D73: trần thật 500 ký tự kiểm ở tram/tu_dong/cai_dat.py
    deploy: str = Field(max_length=2000)
    kiem_song: str = Field(max_length=2000)
    lui: str = Field(max_length=2000)


class ThanCaiDat(_Kin):
    tu_merge: bool
    tu_deploy: bool
    dieu_kien: ThanDieuKien
    lenh: ThanLenh


class ThanCaiDatTuDong(ThanGhi):
    cai_dat: ThanCaiDat


class ThanNutTuCapNhat(_Kin):                               # TC (D85, D105): nút dự án + ba nút con
    bat: bool
    tien_do: bool
    viec_moi: bool
    bi_chan: bool


class ThanTuCapNhat(ThanGhi):
    cai_dat: ThanNutTuCapNhat
