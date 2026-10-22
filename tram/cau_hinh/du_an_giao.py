"""Khoá phần 4 trong `du-an/<ten>.yaml` (spec 4 §13): `lenh_kiem_mac_dinh`, `duong_dan_cam`,
`duong_dan_cam_cho_phep`, `tai_lieu_du_an`, `ngan_sach`. Thiếu khoá → mặc định của spec (§6.2, §8, §11)."""
from dataclasses import dataclass, field

from tram.cau_hinh.lenh import khop_bat_ky

TAI_LIEU_MAC_DINH = ("AGENTS.md", "CLAUDE.md", "docs/ARCHITECTURE.md", "docs/CURRENT_STATE.md")
KY_TU_GLOB = frozenset("*?[")
GIOI_HAN = {"so_lan_chay": (1, 3), "phut": (1, 600), "token_ra": (1, 5_000_000),
            "vong_qc": (1, 20), "lan_chay": (1, 100), "phut_bead": (1, 10_080)}


@dataclass(frozen=True)
class NganSachMuc:
    """Ngân sách MỘT phiếu (phần 3 thực thi)."""
    so_lan_chay: int
    phut: int
    token_ra: int


@dataclass(frozen=True)
class NganSachBead:
    """Ngân sách thực thi của bead trong một chu kỳ (§8)."""
    vong_qc: int = 3
    lan_chay: int = 9
    phut: int = 360


@dataclass(frozen=True)
class NganSachGiao:
    code: NganSachMuc = NganSachMuc(3, 90, 200_000)
    qc: NganSachMuc = NganSachMuc(2, 45, 100_000)
    bead: NganSachBead = NganSachBead()


@dataclass(frozen=True)
class CauHinhGiao:
    lenh_kiem_mac_dinh: tuple[str, ...] = ()
    duong_dan_cam: tuple[str, ...] = ()
    duong_dan_cam_cho_phep: tuple[str, ...] = ()
    tai_lieu_du_an: tuple[str, ...] = TAI_LIEU_MAC_DINH
    ngan_sach: NganSachGiao = field(default_factory=NganSachGiao)


def _ds(raw: dict, khoa: str, mac_dinh: tuple[str, ...] = ()) -> tuple[str, ...]:
    if khoa not in raw:
        return mac_dinh
    ds = raw[khoa] or []
    if not isinstance(ds, list) or not all(isinstance(x, str) and x.strip() for x in ds):
        raise ValueError(f"{khoa} phải là danh sách chuỗi không rỗng")
    return tuple(x.strip() for x in ds)


def _duong_tuong_doi(khoa: str, ds: tuple[str, ...], *, cam_glob: bool) -> tuple[str, ...]:
    for p in ds:
        if p.startswith("/") or "\\" in p or ".." in p.split("/") or (cam_glob and set(p) & KY_TU_GLOB):
            raise ValueError(f"{khoa}: {p!r} phải là đường dẫn tương đối"
                             + (", cụ thể, không ký tự glob" if cam_glob else ""))
    return ds


def _so(bang: dict, khoa: str, ten_gioi_han: str) -> int:
    v = bang[khoa]
    lo, hi = GIOI_HAN[ten_gioi_han]
    if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
        raise ValueError(f"ngan_sach: {khoa} phải là số nguyên trong [{lo}, {hi}]")
    return v


def _bang(raw: dict, ten: str, khoa: tuple[str, ...]) -> dict:
    bang = raw.get(ten)
    if bang is None:
        return {}
    if not isinstance(bang, dict) or set(bang) - set(khoa):
        raise ValueError(f"ngan_sach.{ten} chỉ nhận khoá {list(khoa)}")
    return bang


def _ngan_sach(raw: dict) -> NganSachGiao:
    ns = raw.get("ngan_sach") or {}
    if not isinstance(ns, dict) or set(ns) - {"code", "qc", "bead"}:
        raise ValueError("ngan_sach chỉ nhận khoá code, qc, bead")
    mac_dinh, muc = NganSachGiao(), {}
    for ten in ("code", "qc"):
        b, goc = _bang(ns, ten, ("so_lan_chay", "phut", "token_ra")), getattr(mac_dinh, ten)
        muc[ten] = NganSachMuc(*(_so(b, k, k) if k in b else getattr(goc, k) for k in ("so_lan_chay", "phut",
                                                                                            "token_ra")))
    b = _bang(ns, "bead", ("vong_qc", "lan_chay", "phut"))
    bead = NganSachBead(*(_so(b, k, "phut_bead" if k == "phut" else k) if k in b else getattr(mac_dinh.bead, k)
                          for k in ("vong_qc", "lan_chay", "phut")))
    return NganSachGiao(muc["code"], muc["qc"], bead)


def doc_cau_hinh_giao(raw: dict, lenh_cho_phep: tuple[str, ...]) -> CauHinhGiao:
    mac_dinh = _ds(raw, "lenh_kiem_mac_dinh")
    for l in mac_dinh:
        if khop_bat_ky(l, lenh_cho_phep) is None:
            raise ValueError(f"lenh_kiem_mac_dinh {l!r} không khớp lenh_cho_phep")
    return CauHinhGiao(
        lenh_kiem_mac_dinh=mac_dinh,
        duong_dan_cam=_duong_tuong_doi("duong_dan_cam", _ds(raw, "duong_dan_cam"), cam_glob=False),
        duong_dan_cam_cho_phep=_duong_tuong_doi("duong_dan_cam_cho_phep", _ds(raw, "duong_dan_cam_cho_phep"),
                                                cam_glob=True),
        tai_lieu_du_an=_duong_tuong_doi("tai_lieu_du_an", _ds(raw, "tai_lieu_du_an", TAI_LIEU_MAC_DINH),
                                        cam_glob=True),
        ngan_sach=_ngan_sach(raw))
