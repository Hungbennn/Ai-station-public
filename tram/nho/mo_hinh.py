"""Mô hình ký ức (spec 1b §5) và một bước ghi trong nhật ký thao tác (§6.4)."""
import hashlib
import math
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass

LOAI_NGUON = ("da_chot", "dai_ca_sua", "tra_ve", "dai_ca_ghi", "ban_giao", "agent", "thang_cap")
NGUON_DAI_CA = frozenset({"da_chot", "dai_ca_sua", "tra_ve", "dai_ca_ghi"})
SAN_QUAN_TRONG = {"da_chot": 0.8, "dai_ca_ghi": 0.8, "dai_ca_sua": 0.6, "tra_ve": 0.6}
NGUON_AGENT = frozenset({"ban_giao", "agent"})      # nội dung do agent viết (bàn giao, MCP ghi_nho)
TRAN_NGUON_AGENT = 0.6       # = sàn dai_ca_sua/tra_ve: chữ của agent không tự xếp mình ngang chữ của Đại ca
DO_DAI_TOI_DA = 600          # ký tự của noi_dung — đủ cho một ký ức ngắn, tự đứng được
SO_CHIEU = 1024              # bge-m3


class LoiVector(ValueError):
    """Vector rỗng, có NaN/vô cực, hoặc chuẩn bằng 0 — không bao giờ lưu (M3)."""


@dataclass(frozen=True)
class KyUc:
    id: str
    noi_dung: str
    pham_vi: str
    nhan: tuple[str, ...]
    quan_trong: float
    nguon: tuple[dict, ...]
    nguon_dai_ca: bool
    hieu_luc_tu: str
    tao_luc: str
    mo_hinh_embed: str
    vector: tuple[float, ...]
    dung_luc: str | None = None
    so_lan_dung: int = 0
    da_xoa: bool = False

    @property
    def so_chieu(self) -> int:
        return len(self.vector)

    def sang_dict(self) -> dict:
        d = asdict(self)
        d.update(nhan=list(self.nhan), nguon=[dict(n) for n in self.nguon], vector=list(self.vector))
        return d

    @classmethod
    def tu_dict(cls, d: dict) -> "KyUc":
        return cls(**{**d, "nhan": tuple(d["nhan"]), "nguon": tuple(dict(n) for n in d["nguon"]),
                      "vector": tuple(float(x) for x in d["vector"])})


@dataclass(frozen=True)
class BuocGhi:
    """Một ký ức dự kiến của một sự kiện nguồn: xoá mềm `xoa` (gộp/thay) rồi ghi `ky_uc`."""
    ky_uc: KyUc
    xoa: tuple[str, ...] = ()

    def sang_dict(self) -> dict:
        return {"ky_uc": self.ky_uc.sang_dict(), "xoa": list(self.xoa)}

    @classmethod
    def tu_dict(cls, d: dict) -> "BuocGhi":
        return cls(KyUc.tu_dict(d["ky_uc"]), tuple(d["xoa"]))


def la_nguon_dai_ca(nguon: Sequence[dict]) -> bool:
    """Ký ức "của Đại ca" khi MỌI nguồn thuộc da_chot | dai_ca_sua | tra_ve | dai_ca_ghi (§5)."""
    return bool(nguon) and all(n.get("loai") in NGUON_DAI_CA for n in nguon)


def ap_san(quan_trong: float, nguon: Iterable[dict]) -> float:
    """Kẹp về [0, 1]; mọi nguồn do agent viết → trần 0,6; rồi nâng lên sàn tất định của nguồn cao nhất (§5)."""
    nguon = list(nguon)
    q = min(1.0, max(0.0, float(quan_trong)))
    if nguon and all(n.get("loai") in NGUON_AGENT for n in nguon):
        q = min(q, TRAN_NGUON_AGENT)
    return max([q] + [SAN_QUAN_TRONG.get(n.get("loai"), 0.0) for n in nguon])


def hop_nguon(*cac: Iterable[dict]) -> tuple[dict, ...]:
    """Hợp các danh sách nguồn, bỏ trùng, giữ thứ tự gặp đầu tiên (gộp — §6.3)."""
    thay: dict[tuple, dict] = {}
    for ds in cac:
        for n in ds:
            thay.setdefault(tuple(sorted((k, str(v)) for k, v in n.items())), dict(n))
    return tuple(thay.values())


def chuan_hoa_l2(v: Sequence[float]) -> tuple[float, ...]:
    if not v or not all(math.isfinite(x) for x in v):
        raise LoiVector("Vector rỗng hoặc có giá trị không hữu hạn")
    lon = max(abs(x) for x in v)               # chia trước cho max|x|:
                                               # tránh tràn (1e308) và mất (1e-200) khi bình phương
    if lon == 0:
        raise LoiVector("Vector có chuẩn bằng 0")
    w = [x / lon for x in v]
    chuan = math.sqrt(sum(x * x for x in w))
    return tuple(x / chuan for x in w)


def ma_thao_tac(su_kien_id: int, phien_ban: int) -> str:
    return f"{su_kien_id}:{phien_ban}"


def id_ky_uc(su_kien_id: int, phien_ban: int, thu_tu: int) -> str:
    """ID ổn định suy từ ID thao tác + số thứ tự (§6.4) — phát lại không sinh ID mới."""
    return "m-" + hashlib.sha256(f"{ma_thao_tac(su_kien_id, phien_ban)}#{thu_tu}".encode()).hexdigest()[:24]


@dataclass(frozen=True)
class ThaoTacNho:
    ma: str
    su_kien_id: int
    trang_thai: str
    ke_hoach: dict
    buoc_xong: frozenset[str]
