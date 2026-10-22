"""Thu dữ liệu cho gói (spec 4 §11): lớp 1 đọc tại `origin/<nhanh_chinh>` của kho kiểm — KHÔNG tại `cha` (agent
có thể đã sửa các file đó trên nhánh của nó); lớp 4 từ sự kiện (cửa sổ kể từ `cot.tra_ve` gần nhất) và notes."""
from pathlib import Path

from tram.ban_giao.schema import doc_khoi_ban_giao
from tram.beads.mo_hinh import Bead
from tram.cham_cot.luat_cung import LOAI_CHAN
from tram.giao_viec.git_kiem import diff_theo_file, doc_file
from tram.giao_viec.goi import Lop4
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.kiem.diff import goc_nhanh

KY_TU_MOI_TAI_LIEU = 40_000
GIU_TOI_DA = 5


def doc_tai_lieu(kho_git: Path, nhanh_chinh: str, cac_file: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    ra = []
    for p in cac_file:
        if (nd := doc_file(kho_git, f"origin/{nhanh_chinh}", p, KY_TU_MOI_TAI_LIEU)) is not None:
            ra.append((p, nd))
    return tuple(ra)


def _ban_giao_phu_thuoc(bead: Bead, theo_id: dict[str, Bead]) -> tuple[tuple[str, dict], ...]:
    ra = []
    for p in bead.phu_thuoc:
        d = theo_id.get(p.depends_on_id)
        if p.loai == LOAI_CHAN and d is not None and d.status == "closed" and d.issue_type != "decision":
            if (bg := doc_khoi_ban_giao(d.notes)) is not None and bg.loai == "chinh-thuc":
                ra.append((d.id, bg.model_dump()))
    return tuple(ra)


def thu_lop_4(ds: list[SK], bead: Bead, theo_id: dict[str, Bead], *, buoc: str, kho_git: Path | None,
              nhanh_chinh: str, commit_code: str | None) -> Lop4:
    w = cua_so(ds)
    tam = moi_nhat(w, "bao.bi", lambda s: bool(s.du_lieu.get("ban_giao")))
    moc = moi_nhat(w, "bao.moc", lambda s: bool(s.du_lieu.get("ban_giao")))
    tam = max((x for x in (tam, moc) if x), key=lambda s: s.id, default=None)
    kt = moi_nhat(w, "giao.ket_thuc", lambda s: s.du_lieu.get("buoc") == "code")
    kl = moi_nhat(w, "kiem.lai")
    qk = moi_nhat(w, "qc.ket_qua")
    l4 = Lop4(
        ban_giao_phu_thuoc=_ban_giao_phu_thuoc(bead, theo_id),
        ban_giao_tam=tam.du_lieu["ban_giao"] if tam else None,
        loi_ban_giao=tuple(kt.du_lieu.get("loi") or ()) if kt and kt.du_lieu.get("ly_do") else (),
        kiem_lai=({k: kl.du_lieu[k] for k in ("commit", "ket_qua", "cham_cam")}
                  if kl and not kl.du_lieu["dat"] else None),
        phat_hien_qc=tuple(qk.du_lieu["phat_hien"]) if qk and qk.du_lieu["ket_luan"] != "dat" else (),
        gop_y=tuple(s.du_lieu.get("gop_y", "") for s in ds if s.loai == "cot.tra_ve")[-GIU_TOI_DA:],
        tra_loi=tuple(s.du_lieu.get("tra_loi", "") for s in ds if s.loai == "escalation.dong")[-GIU_TOI_DA:])
    if buoc != "qc" or commit_code is None:
        return l4
    xong = moi_nhat(w, "bao.xong", lambda s: s.du_lieu.get("commit") == commit_code)
    diff = ()
    if kho_git is not None:
        diff = tuple(diff_theo_file(kho_git, goc_nhanh(kho_git, f"origin/{nhanh_chinh}", commit_code), commit_code))
    return Lop4(**{**l4.__dict__, "ban_giao_code": xong.du_lieu.get("ban_giao") if xong else None,
                   "commit_code": commit_code, "diff_qc": diff})
