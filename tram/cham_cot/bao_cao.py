from collections import Counter
from dataclasses import dataclass, field


@dataclass
class DongBaoCao:
    bead_id: str
    tieu_de: str
    cot: str
    ly_do: str
    cau_hoi: list[str]
    cham_rao: list[str]
    da_ghi: bool


@dataclass
class BaoCaoQuet:
    du_an: str
    thu: bool
    dong: list[DongBaoCao] = field(default_factory=list)
    bo_qua: Counter = field(default_factory=Counter)
    loi: list[str] = field(default_factory=list)
    token_vao: int = 0
    token_ra: int = 0


def xuat_bao_cao(bc: BaoCaoQuet) -> str:
    dong = [f"# Báo cáo chấm cột — {bc.du_an} ({'thử' if bc.thu else 'ghi thật'})", "",
            f"Đã chấm: {len(bc.dong)} · Bỏ qua: {dict(bc.bo_qua)} · Lỗi: {len(bc.loi)}",
            f"Token vào/ra: {bc.token_vao}/{bc.token_ra}", ""]
    for cot, ten in (("can-chot", "Cột 2 — cần Đại ca chốt"), ("ai-lam", "Cột 1 — AI tự làm")):
        dong += [f"## {ten}", ""]
        for d in (x for x in bc.dong if x.cot == cot):
            dong.append(f"- **{d.bead_id}** {d.tieu_de} — {d.ly_do}")
            dong += [f"  - Cần chốt: {q}" for q in d.cau_hoi]
        dong.append("")
    if bc.loi:
        dong += ["## Lỗi", ""] + [f"- {l}" for l in bc.loi]
    return "\n".join(dong)
