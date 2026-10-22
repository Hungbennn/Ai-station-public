"""Nguồn ký ức lát 1b-1 (spec 1b §6.1): sự kiện của 1a và 2a → đầu vào cho bước tách.

Ba loại 1b-1: `cot.dai_ca_sua`, `cot.da_chot`, `cot.tra_ve`; 1b-2 thêm `nho.agent_ghi` (MCP `ghi_nho`). Nguồn của
phần 4 (`kiem.lai` + `bao.xong`, `escalation.dong`, `spec.tra_ve` — lát 1b-4) ở `nguon_ban_giao.py`,
`nguon_giao_viec.py`; mọi người đọc nguồn đi qua `cac_nguon.doc_nguon`. Gốc ghi luôn `/du-an/<du_an của sự kiện>` —
trạm quyết, LLM không chọn. Mọi trường chữ (bản gốc) qua `chan_bi_mat` trước khi dựng đầu vào (D23; bs-2bd.1.19)."""
import re
from dataclasses import dataclass

from tram.nho.bi_mat import chan_bi_mat
from tram.nho.mo_hinh import DO_DAI_TOI_DA
from tram.nho.pham_vi import TEN
from tram.su_kien.kho import SuKien

LOAI_NGUON_SU_KIEN = {"cot.dai_ca_sua": "dai_ca_sua", "cot.da_chot": "da_chot", "cot.tra_ve": "tra_ve"}
DO_DAI_VAN_BAN = 4000
LOAI_AGENT_GHI = "nho.agent_ghi"        # 1b-2: MCP ghi_nho ghi sự kiện này, vòng nạp biến thành ký ức (§6.1)
TAC_NHAN_NHO = "tram/nho"               # = ap_dung.TAC_NHAN — chỉ tin nho.agent_ghi do chính memory service ghi
NHAN_RE = re.compile(r"[a-z0-9-]{1,32}")
TOI_DA_NHAN = 8


@dataclass(frozen=True)
class DauVao:
    su_kien_id: int
    du_an: str
    bead_id: str | None
    loai_nguon: str                 # da_chot | dai_ca_sua | tra_ve
    van_ban: str | None = None      # đưa LLM tách (sẽ bọc <du_lieu_khong_tin_cay>)
    tat_dinh: str | None = None     # ký ức dựng sẵn — không gọi LLM
    ep_nghiep_vu: bool = False      # da_chot luôn nghiep-vu
    luc: str | None = None          # giờ của sự kiện nguồn → tao_luc, hieu_luc_tu của ký ức mới (§5)
    vai: str | None = None          # nguồn agent (1b-2): vai của phiếu — thăng cấp 1b-3 xét "cùng vai" (§5)
    nhan: tuple[str, ...] = ()      # nhãn agent gửi kèm ghi_nho

    @property
    def nguon(self) -> dict:
        n = {"loai": self.loai_nguon, "du_an": self.du_an, "bead_id": self.bead_id, "su_kien_id": self.su_kien_id}
        return n if self.vai is None else {**n, "vai": self.vai}


def _cat(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 1] + "…"


def _cat_dong(dong: list[str]) -> str:
    s = "\n".join(dong)
    return s if len(s) <= DO_DAI_VAN_BAN else s[:DO_DAI_VAN_BAN - 1] + "…"


def _cot(x) -> str:
    return str(x) if x else "(chưa chấm)"


def _dai_ca_sua(sk: SuKien, d: dict) -> DauVao:
    chan_bi_mat("dai_ca_sua", [str(d.get(k) or "") for k in ("tieu_de", "cot_he", "cot_moi", "ly_do_he", "vi_sao")])
    dong = (f"\"{d.get('tieu_de') or sk.bead_id}\": hệ xếp {_cot(d.get('cot_he'))}, "
            f"Đại ca chuyển {_cot(d.get('cot_moi'))}. Lý do hệ: {d.get('ly_do_he') or '(không có)'}")
    if d.get("vi_sao"):
        return DauVao(sk.id, sk.du_an, sk.bead_id, "dai_ca_sua", luc=sk.luc,
                      van_ban=_cat(f"Bead {sk.bead_id} — {dong}. Đại ca giải thích: {d['vi_sao']}", DO_DAI_VAN_BAN))
    return DauVao(sk.id, sk.du_an, sk.bead_id, "dai_ca_sua", tat_dinh=_cat(dong, DO_DAI_TOI_DA), luc=sk.luc)


def _da_chot(sk: SuKien, d: dict) -> DauVao:
    chan_bi_mat("da_chot", [str(d.get("decision_id") or ""), str(d.get("adr") or ""),
                            *map(str, d.get("cau_hoi") or []), *map(str, d.get("tra_loi") or [])])
    dong = [f"Đại ca chốt câu hỏi của bead {sk.bead_id} (decision {d.get('decision_id')}), ngày {sk.luc[:10]}:"]
    if d.get("adr"):
        dong.append(f"Theo {d['adr']}.")
    for q, a in zip(d.get("cau_hoi") or [], d.get("tra_loi") or []):
        dong += [f"Hỏi: {q}", f"Đáp: {a}"]
    return DauVao(sk.id, sk.du_an, sk.bead_id, "da_chot", van_ban=_cat_dong(dong), ep_nghiep_vu=True, luc=sk.luc)


def _agent_ghi(sk: SuKien, d: dict) -> DauVao | None:
    """`ghi_nho` không có bước tách (§6.2): nội dung đi thẳng, luật cứng quyết nhánh. Dữ liệu sai → ValueError
    (sự kiện "độc": `nho.loi_tach`, bỏ, mốc tiến)."""
    if sk.tac_nhan != TAC_NHAN_NHO:
        return None
    nd, nhan, vai = d.get("noi_dung"), d.get("nhan", []), d.get("vai")
    if not isinstance(nd, str) or not 0 < len(nd.strip()) <= DO_DAI_TOI_DA:
        raise ValueError(f"nho.agent_ghi: noi_dung phải 1–{DO_DAI_TOI_DA} ký tự")
    if not isinstance(nhan, list) or len(nhan) > TOI_DA_NHAN or not all(
            isinstance(x, str) and NHAN_RE.fullmatch(x) for x in nhan):
        raise ValueError("nho.agent_ghi: nhan sai dạng")
    if not isinstance(vai, str) or not re.fullmatch(TEN, vai):
        raise ValueError("nho.agent_ghi: vai sai dạng")
    chan_bi_mat("agent", [nd, *nhan])
    return DauVao(sk.id, sk.du_an, sk.bead_id, "agent", tat_dinh=nd.strip(), luc=sk.luc, vai=vai, nhan=tuple(nhan))


def doc_dau_vao(sk: SuKien) -> DauVao | None:
    """None: không phải nguồn ký ức (mốc vẫn tiến). `du_an` sai dạng tên (`[a-z0-9-]+`) cũng None — sự kiện
    "độc" không được làm kẹt vòng nạp (pham_vi_du_an sẽ từ chối)."""
    loai = "agent" if sk.loai == LOAI_AGENT_GHI else LOAI_NGUON_SU_KIEN.get(sk.loai)
    if loai is None or not re.fullmatch(TEN, sk.du_an or "") or not isinstance(sk.du_lieu, dict):
        return None
    if loai == "agent":
        return _agent_ghi(sk, sk.du_lieu)
    if loai == "dai_ca_sua":
        return _dai_ca_sua(sk, sk.du_lieu)
    if loai == "da_chot":
        return _da_chot(sk, sk.du_lieu)
    gop_y = str(sk.du_lieu.get("gop_y") or "").strip()
    if not gop_y:
        return None
    chan_bi_mat("tra_ve", [gop_y])
    return DauVao(sk.id, sk.du_an, sk.bead_id, "tra_ve", luc=sk.luc,
                  van_ban=_cat_dong([f"Đại ca trả về bead {sk.bead_id} ngày {sk.luc[:10]} với góp ý:", gop_y]))
