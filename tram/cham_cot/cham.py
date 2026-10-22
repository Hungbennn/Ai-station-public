from collections.abc import Callable
from dataclasses import dataclass, field

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.cau_hoi import cau_hoi_du_phong
from tram.cham_cot.luat_cung import kiem, quyet_dinh_da_chot
from tram.cham_cot.prompt import he_thong, noi_dung
from tram.cham_cot.soan_cau_hoi import soan_cau_hoi
from tram.llm.claude import MO_HINH, cham_bang_llm
from tram.nho.pham_vi import vung_cap_cham_cot
from tram.su_kien.kho import KhoSuKien

NhoLai = Callable[[str, list[str]], list[dict]]
DO_DAI_TRUY_VAN = 2000

NGUONG_TIN_CAY = 0.6


@dataclass(frozen=True)
class PhanCot:
    cot: str
    ly_do: str
    cau_hoi: list[str]
    du_lieu: dict = field(default_factory=dict)
    token_vao: int = 0
    token_ra: int = 0
    thoi_gian_ms: int = 0


def bai_hoc_gan_day(kho: KhoSuKien, du_an_ten: str, gioi_han: int = 5) -> list[str]:
    return [
        f"Bead '{s.du_lieu.get('tieu_de', s.bead_id)}': hệ chấm {s.du_lieu.get('cot_he')}, "
        f"Đại ca chuyển {s.du_lieu.get('cot_moi')}. Lý do hệ khi đó: {s.du_lieu.get('ly_do_he')}"
        for s in kho.gan_day(du_an_ten, "cot.dai_ca_sua", gioi_han)
    ]


def bai_hoc(kho: KhoSuKien, du_an_ten: str, bead: Bead, nho: NhoLai | None) -> tuple[list[str], str]:
    """Spec 1b §7: recall từ memory (vùng cấp 1a); memory tắt/lỗi/quá 2 giây → 5 sự kiện `cot.dai_ca_sua`
    gần nhất (bỏ hẳn recall vector, không vector giả). Trả (bài học, nguon_bai_hoc)."""
    if nho is not None:
        truy_van = f"{bead.title}\n{bead.description}"[:DO_DAI_TRUY_VAN]
        try:
            return [k["noi_dung"] for k in nho(truy_van, vung_cap_cham_cot(du_an_ten))], "nho"
        except Exception:                          # noqa: BLE001 — mọi lỗi recall (sai dạng, vùng cấp…) → cách cũ
            pass
    return bai_hoc_gan_day(kho, du_an_ten), "su_kien"


def cham_mot_bead(bead: Bead, *, du_an: DuAn, theo_id: dict[str, Bead], kho: KhoSuKien,
                  client, vai: tuple[str, str], nho: NhoLai | None = None,
                  vai_soan: tuple[str, str] | None = None) -> PhanCot:
    luat = kiem(bead, du_an, theo_id)
    quyet_dinh = quyet_dinh_da_chot(bead, theo_id)
    du_lieu = {"phien_ban_vai": vai[0], "mo_hinh": MO_HINH, "cham_rao": list(luat.cham),
               "bi_chan_boi": list(luat.bi_chan_boi), "quyet_dinh": [d.id for d in quyet_dinh],
               "llm_loi": None}
    if luat.la_decision_mo:  # spec 4 §14 mục 7: luật cứng đã xếp cột 2 — không gọi LLM, không recall
        return PhanCot("can-chot", luat.ly_do(), cau_hoi_du_phong(luat, bead.title),
                       {**du_lieu, "nguon_bai_hoc": None, "bo_llm": "decision-mo", "nguon_cau_hoi": "du_phong"})
    if luat.ep_cot_2:  # §5.2 bước 4: cột do luật cứng quyết; LLM chỉ soạn câu hỏi, không recall
        cau_hoi, them, goi = soan_cau_hoi(bead, luat, du_an=du_an, client=client, vai_soan=vai_soan)
        du_lieu.update(them, nguon_bai_hoc=None)
        so = (goi.token_vao, goi.token_ra, goi.thoi_gian_ms) if goi else (0, 0, 0)
        return PhanCot("can-chot", luat.ly_do(), cau_hoi, du_lieu, *so)
    hoc, du_lieu["nguon_bai_hoc"] = bai_hoc(kho, du_an.ten, bead, nho)
    goi = cham_bang_llm(client, he_thong(vai[1], du_an), noi_dung(bead, luat, hoc, quyet_dinh))
    kq = goi.ket_qua
    cot, ly_do = kq.cot, kq.ly_do
    if cot == "ai-lam" and kq.do_tin_cay < NGUONG_TIN_CAY:
        cot, ly_do = "can-chot", f"AI chưa chắc ({kq.do_tin_cay:.2f}): {kq.ly_do}"
    if cot == "ai-lam" and luat.bi_chan_boi:
        ly_do += f" (chờ {', '.join(luat.bi_chan_boi)})"
    du_lieu.update(do_tin_cay=kq.do_tin_cay, thieu=kq.thieu, so_lan=goi.so_lan,
                   token_cache_doc=goi.token_cache_doc)
    return PhanCot(cot, ly_do, kq.cau_hoi_can_chot, du_lieu, goi.token_vao, goi.token_ra, goi.thoi_gian_ms)
