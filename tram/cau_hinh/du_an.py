import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from tram.cau_hinh.du_an_giao import CauHinhGiao, doc_cau_hinh_giao
from tram.cau_hinh.lenh import kiem_mau
from tram.cau_hinh.moi_truong_kiem import MoiTruongKiem, doc_moi_truong_kiem
from tram.duong_dan import goc_repo
from tram.cau_hinh.theo_co import doc_theo_co

LOAI_HANG_RAO = ("tien", "schema", "quyen", "khach_thay")


@dataclass(frozen=True)
class HangRao:
    tu_khoa: tuple[str, ...] = ()
    duong_dan: tuple[str, ...] = ()
    nhan: tuple[str, ...] = ()


NHANH_CHINH_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}")


@dataclass(frozen=True)
class DuAn:
    ten: str
    duong_dan: Path
    gitnexus_repo: str | None
    hang_rao: dict[str, HangRao]
    boi_canh: str = ""
    module: tuple[str, ...] = ()          # spec 1b §6.2 bước 3: tên module — luật cứng nghiệp vụ của memory
    tu_khoa_khach: tuple[str, ...] = ()   # tuỳ chọn (#20)
    lenh_cho_phep: tuple[str, ...] = ()   # spec 3 §13 mục 9: mẫu lệnh phiếu code/qc được chạy (khop_lenh)
    moi_truong_kiem: MoiTruongKiem | None = None
    nhanh_chinh: str = "main"
    theo_co: dict | None = None
    giao: CauHinhGiao = CauHinhGiao()     # spec 4 §13: khoá của bộ giao việc


def _thu_muc(thu_muc: Path | None) -> Path:
    return thu_muc or goc_repo() / "du-an"


def _ds_chuoi(raw: dict, khoa: str) -> tuple[str, ...]:
    ds = raw.get(khoa) or []
    if not isinstance(ds, list) or not all(isinstance(x, str) and x.strip() for x in ds):
        raise ValueError(f"{khoa} phải là danh sách chuỗi không rỗng")
    return tuple(x.strip() for x in ds)


def _lenh_cho_phep(raw: dict) -> tuple[str, ...]:
    ds = _ds_chuoi(raw, "lenh_cho_phep")
    for mau in ds:
        if (loi := kiem_mau(mau)) is not None:
            raise ValueError(f"lenh_cho_phep {mau!r}: {loi}")
    return ds


def _nhanh_chinh(raw: dict) -> str:
    n = raw.get("nhanh_chinh", "main")
    if not isinstance(n, str) or not NHANH_CHINH_RE.fullmatch(n) or ".." in n or n.endswith(("/", ".lock")) \
            or n.startswith("tram/"):
        raise ValueError(f"nhanh_chinh không hợp lệ: {n!r}")
    return n


def nap_du_an(ten: str, *, thu_muc: Path | None = None, repo: Path | None = None) -> DuAn:
    raw = yaml.safe_load((_thu_muc(thu_muc) / f"{ten}.yaml").read_text(encoding="utf-8"))
    if raw.get("ten") != ten:
        raise ValueError(f"Trường ten trong file là {raw.get('ten')!r}, khác tên file {ten!r}")
    rao = raw.get("hang_rao") or {}
    la = sorted(set(rao) - set(LOAI_HANG_RAO))
    if la:
        raise ValueError(f"Loại hàng rào không hợp lệ: {la}")
    hang_rao = {
        loai: HangRao(
            tu_khoa=tuple((cau or {}).get("tu_khoa") or ()),
            duong_dan=tuple((cau or {}).get("duong_dan") or ()),
            nhan=tuple((cau or {}).get("nhan") or ()),
        )
        for loai, cau in rao.items()
    }
    lenh = _lenh_cho_phep(raw)
    return DuAn(
        ten=ten,
        duong_dan=repo or Path(raw["duong_dan"]),
        gitnexus_repo=raw.get("gitnexus_repo"),
        hang_rao=hang_rao,
        boi_canh=raw.get("boi_canh", ""),
        module=_ds_chuoi(raw, "module"),
        tu_khoa_khach=_ds_chuoi(raw, "tu_khoa_khach"),
        lenh_cho_phep=lenh,
        moi_truong_kiem=doc_moi_truong_kiem(raw),
        nhanh_chinh=_nhanh_chinh(raw),
        giao=doc_cau_hinh_giao(raw, lenh),
        theo_co=doc_theo_co(raw["theo_co"]) if "theo_co" in raw else None,
    )


def liet_ke_du_an(thu_muc: Path | None = None) -> list[str]:
    return sorted(p.stem for p in _thu_muc(thu_muc).glob("*.yaml"))
