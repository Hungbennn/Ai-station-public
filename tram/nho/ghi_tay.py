"""Đại ca ghi tay một ký ức vào phạm vi Đại ca chọn (spec 1b §6.1 hàng cuối, §6.2 bước 3–6, §9.1 `/ghi`).

Không có bước tách. `/du-an/X/cach-lam` chạm luật của X → ép `/du-an/X/nghiep-vu`. `/vai/*`, `/chung` chạm luật của
MỌI dự án → từ chối + `nho.tu_choi`. Rồi embed → gộp trong cùng phạm vi (ký ức Đại ca được `thay`/`gop` ký ức cũ)
→ kế hoạch vào nhật ký (ID thao tác `ghi:<ma_thao_tac>`) → áp dụng idempotent như sự kiện nguồn (§6.4)."""
import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from tram.nho.ap_dung import TAC_NHAN, ap_dung
from tram.nho.embed import Embedder
from tram.nho.gop import TOI_DA_UNG_VIEN, gop, loc_ung_vien
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.luat_chung import luat_moi_du_an
from tram.nho.mo_hinh import BuocGhi, KyUc, ap_san, hop_nguon, la_nguon_dai_ca
from tram.nho.nhat_ky import NhatKy, ThaoTacNho
from tram.nho.pham_vi import LoiVungCap, du_an_cua, la_pham_vi
from tram.su_kien.kho import KhoSuKien

DU_AN_HE = "_tram"          # sự kiện của ký ức /vai, /chung (spec 2 §12.2: sự kiện hệ không gắn dự án)


class XungDotGhi(ValueError):
    """Cùng mã thao tác nhưng khác nội dung yêu cầu — HTTP 409."""


class TuChoiGhi(ValueError):
    """Ghi vào `/vai/*`, `/chung` mà chạm luật cứng nghiệp vụ (xét với danh sách của mọi dự án)."""

    def __init__(self, ly_do: list[str]):
        super().__init__("Chạm luật nghiệp vụ: " + "; ".join(ly_do))
        self.ly_do = ly_do


@dataclass
class NguCanhGhiTay:
    kho: KhoKyUc
    embedder: Embedder
    client: object
    vai_gop: tuple[str, str]
    nhat_ky: NhatKy
    kho_sk: KhoSuKien
    luat_cua: Callable[[str], LuatDuAn]
    cac_du_an: Callable[[], list[str]]
    luc: Callable[[], str]


@dataclass(frozen=True)
class KetQuaGhiTay:
    id: str
    pham_vi: str
    xoa: tuple[str, ...]
    lap_lai: bool

    def sang_dict(self) -> dict:
        return {"id": self.id, "pham_vi": self.pham_vi, "xoa": list(self.xoa), "lap_lai": self.lap_lai}


def ma_ghi_tay(ma_thao_tac: str) -> str:
    return f"ghi:{ma_thao_tac}"


def id_ghi_tay(ma_thao_tac: str) -> str:
    return "m-" + hashlib.sha256(f"dai_ca_ghi:{ma_thao_tac}".encode()).hexdigest()[:24]


def _ket_qua(tt: ThaoTacNho, lap_lai: bool) -> KetQuaGhiTay:
    b = tt.ke_hoach["buoc"][0]
    return KetQuaGhiTay(b["ky_uc"]["id"], b["ky_uc"]["pham_vi"], tuple(b["xoa"]), lap_lai)


def _luat(nc: NguCanhGhiTay, noi_dung: str, pham_vi: str) -> tuple[str, LuatDuAn]:
    """Trả (phạm vi cuối, luật dùng cho câu gộp). Từ chối thì ghi `nho.tu_choi` rồi ném TuChoiGhi."""
    du_an = du_an_cua(pham_vi)
    try:
        luat = nc.luat_cua(du_an) if du_an else luat_moi_du_an(nc.cac_du_an(), nc.luat_cua)
    except Exception as e:                                  # noqa: BLE001 — yaml hỏng: không xét với danh sách thiếu
        ly_do = [f"không đọc được cấu hình dự án: {type(e).__name__}: {str(e)[:200]}"]
    else:
        ly_do = ly_do_nghiep_vu(noi_dung, luat)
        if not ly_do or du_an:
            return (f"/du-an/{du_an}/nghiep-vu" if ly_do else pham_vi), luat
    nc.kho_sk.ghi(du_an or DU_AN_HE, "nho.tu_choi", {"ly_do": "; ".join(ly_do)[:300], "nguon": "dai_ca_ghi",
                                                    "pham_vi": pham_vi}, tac_nhan=TAC_NHAN)
    raise TuChoiGhi(ly_do)


def ghi_tay(nc: NguCanhGhiTay, *, noi_dung: str, pham_vi: str, nhan: list[str], ma_thao_tac: str) -> KetQuaGhiTay:
    """LoiVungCap (phạm vi sai dạng), TuChoiGhi, LoiEmbedder, anthropic.APIError: kho và nhật ký không đổi."""
    if not la_pham_vi(pham_vi):
        raise LoiVungCap(f"Phạm vi phải đúng một trong bốn dạng của spec 1b §4: {pham_vi[:80]!r}")
    noi_dung, ma = noi_dung.strip(), ma_ghi_tay(ma_thao_tac)
    dau_vao = hashlib.sha256(repr((noi_dung, pham_vi, tuple(nhan))).encode()).hexdigest()
    with nc.kho.khoa_gop:
        if (tt := nc.nhat_ky.lay(ma)) is not None:          # gửi lại cùng mã: áp dụng nốt kế hoạch cũ, không gọi LLM
            if tt.ke_hoach.get("dau_vao") != dau_vao:
                raise XungDotGhi("Mã thao tác đã dùng cho nội dung khác")
            if tt.trang_thai == "dang":
                ap_dung(tt, kho=nc.kho, kho_sk=nc.kho_sk, nhat_ky=nc.nhat_ky)
            return _ket_qua(tt, True)
        pv, luat = _luat(nc, noi_dung, pham_vi)
        v = nc.embedder.embed([noi_dung])[0]
        tim_ra = nc.kho.tim(v, [pv], mo_hinh=nc.embedder.mo_hinh, gioi_han=TOI_DA_UNG_VIEN)
        g = gop(nc.client, nc.vai_gop, noi_dung_moi=noi_dung, moi_dai_ca=True, pham_vi=pv,
                ung_vien=loc_ung_vien(tim_ra, pv), luat=luat)
        if g.noi_dung != noi_dung:
            v = nc.embedder.embed([g.noi_dung])[0]
        nguon = hop_nguon(({"loai": "dai_ca_ghi", "ma_thao_tac": ma_thao_tac},), *(k.nguon for k in g.gop_tu))
        luc = nc.luc()
        ky = KyUc(id=id_ghi_tay(ma_thao_tac), noi_dung=g.noi_dung, pham_vi=pv, nhan=tuple(nhan),
                  quan_trong=ap_san(max([0.0] + [k.quan_trong for k in g.gop_tu]), nguon), nguon=nguon,
                  nguon_dai_ca=la_nguon_dai_ca(nguon), hieu_luc_tu=luc, tao_luc=luc,
                  mo_hinh_embed=nc.embedder.mo_hinh, vector=tuple(v))
        tt = nc.nhat_ky.bat_dau(ma, 0, {"dau_vao": dau_vao, "du_an": du_an_cua(pv) or DU_AN_HE, "bead_id": None,
                                        "buoc": [BuocGhi(ky, g.xoa).sang_dict()]})
        ap_dung(tt, kho=nc.kho, kho_sk=nc.kho_sk, nhat_ky=nc.nhat_ky)
        return _ket_qua(tt, False)
