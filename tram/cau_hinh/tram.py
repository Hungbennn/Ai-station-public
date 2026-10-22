"""~/.tram/cau-hinh.yaml (spec 2 §12.5): không chứa bí mật; thiếu file → dashboard chỉ đọc, không báo tin."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

GIO_RE = re.compile(r"([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d")
TEN_MAY_RE = re.compile(r"[A-Za-z0-9.-]+")


@dataclass(frozen=True)
class CauHinhTelegram:
    chat_id: str | None = None
    gio_yen_lang: str | None = None


@dataclass(frozen=True)
class CauHinhHanMuc:
    """Spec 3 §8.2: `han_muc: {ngung: 90, tuan_chi_uu_tien: 80, tuoi_toi_da_gio: 6}`."""
    ngung: float = 90.0
    tuan_chi_uu_tien: float = 80.0
    tuoi_toi_da_gio: float = 6.0


@dataclass(frozen=True)
class CauHinhThoTram:
    """Phía trạm của phần 3 (#21: mặc định giữ theo spec, chỉnh sau): trần §8.3, cầu dao, hợp đồng §6.2–§6.3."""
    lan_chay_moi_gio: int = 6
    lan_chay_moi_ngay: int = 60
    phut_cau_dao: int = 60
    loi_he_lien_tiep: int = 3
    han_giu_phut: int = 10
    mat_ket_noi_giay: int = 90


@dataclass(frozen=True)
class CauHinhTram:
    dai_ca_logins: tuple[str, ...] = ()
    ten_may_b: str | None = None
    telegram: CauHinhTelegram = field(default_factory=CauHinhTelegram)
    dashboard_url: str | None = None
    han_muc: CauHinhHanMuc = field(default_factory=CauHinhHanMuc)
    tho: CauHinhThoTram = field(default_factory=CauHinhThoTram)


GIOI_HAN = {"ngung": (1, 100), "tuan_chi_uu_tien": (1, 100), "tuoi_toi_da_gio": (0.1, 168),
            "lan_chay_moi_gio": (1, 60), "lan_chay_moi_ngay": (1, 1440), "phut_cau_dao": (1, 1440),
            "loi_he_lien_tiep": (1, 20), "han_giu_phut": (2, 120), "mat_ket_noi_giay": (30, 3600)}


def _bang_so(raw: dict, khoa: str, lop):
    """Bảng con số trong cau-hinh.yaml → dataclass; khoá lạ, sai kiểu hay ngoài giới hạn → ValueError."""
    tho = raw.get(khoa) or {}
    if not isinstance(tho, dict) or set(tho) - set(lop.__dataclass_fields__):
        raise ValueError(f"{khoa} phải là bảng với các khoá {sorted(lop.__dataclass_fields__)}")
    for k, v in tho.items():
        nguyen = isinstance(lop.__dataclass_fields__[k].default, int)
        if isinstance(v, bool) or not isinstance(v, int if nguyen else (int, float)) \
                or not GIOI_HAN[k][0] <= v <= GIOI_HAN[k][1]:
            raise ValueError(f"{khoa}.{k} phải là số trong {GIOI_HAN[k]}")
    return lop(**tho)


def _chuoi(x) -> str | None:
    return None if x is None else (str(x).strip() or None)


def nap_cau_hinh_tram(duong_dan: Path | None = None) -> CauHinhTram:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    if not p.exists():
        return CauHinhTram()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{p}: phải là một bảng khoá → giá trị")
    logins = raw.get("dai_ca_logins") or []
    if not isinstance(logins, list) or not all(isinstance(x, str) and x.strip() for x in logins):
        raise ValueError("dai_ca_logins phải là danh sách chuỗi không rỗng")
    ten_may = _chuoi(raw.get("ten_may_b"))
    if ten_may is not None and not TEN_MAY_RE.fullmatch(ten_may):
        raise ValueError("ten_may_b chỉ gồm chữ, số, '.', '-'")
    url = _chuoi(raw.get("dashboard_url"))
    if url is not None and not url.startswith("https://"):
        raise ValueError("dashboard_url phải bắt đầu bằng https://")
    tg = raw.get("telegram") or {}
    if not isinstance(tg, dict):
        raise ValueError("telegram phải là bảng {chat_id, gio_yen_lang}")
    gio = _chuoi(tg.get("gio_yen_lang"))
    if gio is not None and not GIO_RE.fullmatch(gio):
        raise ValueError("telegram.gio_yen_lang phải dạng HH:MM-HH:MM")
    return CauHinhTram(tuple(x.strip() for x in logins), ten_may,
                       CauHinhTelegram(_chuoi(tg.get("chat_id")), gio), url,
                       _bang_so(raw, "han_muc", CauHinhHanMuc), _bang_so(raw, "tho", CauHinhThoTram))
