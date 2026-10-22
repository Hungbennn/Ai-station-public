"""Duyệt spec (spec 4 §7.3, G7, G11): Đại ca bấm trên dashboard với `expected_commit` + `digest_bead` của bản đang xem.

Kiểm (trước khi ghi gì): feature còn `cho-duyet-spec`, version khớp, `spec.xong` hiện hành và ref công bố đúng
`expected_commit`, digest khớp, và `*.beads.json` đọc lại từ kho kiểm TẠI commit đó vẫn ra đúng digest → sai: 409.
Ghi (khoá theo feature, tiến độ từng bước theo `ma_thao_tac` — spec 2 §12.3) bằng `bd` của TRẠM
(`--actor tram/giao-viec`): tạo con còn thiếu (đối soát theo khoá) → nối phụ thuộc → gỡ `cho-duyet-spec`, gắn
`theo-plan` → sự kiện `spec.duyet {feature, commit, digest_bead, bead_moi[], ma_thao_tac}`."""
from dataclasses import dataclass
from pathlib import Path

from tram.giao_viec.xet_spec import doc_ke_hoach_tai
from tram.suy.phe_duyet_spec import spec_hien_hanh
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import NguCanhGhi, co_su_kien, kiem_version
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, XungDot
from tram.thao_tac.tao_con import noi_phu_thuoc, tao_con

TAC_NHAN_TRAM = "tram/giao-viec"
NHAN_CHO_DUYET, NHAN_THEO_PLAN = "cho-duyet-spec", "theo-plan"


@dataclass(frozen=True)
class NguonSpec:
    bd_tram: object                 # Bd(repo, actor="tram/giao-viec") — trạm là bên tạo bead (Q11)
    kho_git: Path | None            # kho kiểm của trạm (~/.tram/kho-kiem/<du_an>); None → 501
    nhanh_chinh: str = "main"


def nguon_spec_that(ten: str) -> NguonSpec:
    from tram.beads.bd import Bd
    from tram.cau_hinh.du_an import nap_du_an
    from tram.giao_viec.git_kiem import kho_kiem
    da, kg = nap_du_an(ten), kho_kiem(ten)
    return NguonSpec(Bd(da.duong_dan, actor=TAC_NHAN_TRAM), kg if (kg / ".git").exists() else None, da.nhanh_chinh)


def _ke_hoach(ns: NguonSpec, feature: str, commit: str, digest_bead: str):
    kh, dg, _ = doc_ke_hoach_tai(ns.kho_git, commit, feature)
    if kh is None or dg != digest_bead:
        raise XungDot("*.beads.json tại commit khác bản trạm đã kiểm — tải lại và xem bản mới")
    return kh


def duyet_spec(nc: NguCanhGhi, ns: NguonSpec, bead_id: str, *, ma: str, expected_version: str,
               expected_commit: str | None, digest_bead: str | None) -> KetQuaThaoTac:
    if not expected_commit or not digest_bead:
        raise KhongHopLe("Duyệt spec cần expected_commit và digest_bead của bản đang xem")

    def kiem_ban(*, moi=False) -> None:
        b = nc.bd.mot(bead_id)
        if moi:
            kiem_version(b, expected_version)
        if b.status == "closed" or (NHAN_CHO_DUYET not in b.labels and not (
                not moi and NHAN_THEO_PLAN in b.labels and f"(ma_thao_tac {ma})" in b.notes)):
            raise XungDot("Feature không còn là bản duyệt của thao tác này")
        hh = spec_hien_hanh(nc.kho, nc.du_an, bead_id)
        cb = nc.kho.moi_nhat(nc.du_an, bead_id, "giao.cong_bo")
        if hh is None or (hh.get("commit"), hh.get("digest_bead")) != (expected_commit, digest_bead) \
                or cb is None or cb.du_lieu.get("commit") != expected_commit:
            raise XungDot("Spec đã có bản khác bản Đại ca đang xem — tải lại và xem bản mới (G11)")
        if ns.kho_git is None:
            raise ChuaHoTro("Chưa có kho kiểm của trạm để đọc *.beads.json")
        _ke_hoach(ns, bead_id, expected_commit, digest_bead)

    def kiem_moi() -> None:
        kiem_ban(moi=True)

    def bao_ve(ham):
        def chay(da):
            kiem_ban()
            return ham(da)
        return chay

    def nhan(da: dict) -> bool:
        b = ns.bd_tram.mot(bead_id)
        if NHAN_CHO_DUYET in b.labels or NHAN_THEO_PLAN not in b.labels:
            ns.bd_tram.cap_nhat_nhan(bead_id, them=[NHAN_THEO_PLAN], bo=[NHAN_CHO_DUYET], ghi_chu=(
                f"[{TAC_NHAN_TRAM}] Đại ca duyệt spec tại {expected_commit}: {len(da['tao_bead'])} bead con "
                f"(ma_thao_tac {ma})"))
        return True

    def su_kien(da: dict) -> bool:
        if co_su_kien(nc.kho, nc.du_an, bead_id, "spec.duyet", ma):
            return False
        nc.kho.ghi(nc.du_an, "spec.duyet", {"feature": bead_id, "commit": expected_commit, "digest_bead": digest_bead,
                                            "bead_moi": list(da["tao_bead"].values()), "ma_thao_tac": ma},
                   bead_id=bead_id, tac_nhan=TAC_NHAN_TRAM)
        return True

    yc = YeuCau(ma, "duyet_spec", nc.du_an, bead_id, {"expected_commit": expected_commit, "digest_bead": digest_bead},
                expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[
        ("tao_bead", bao_ve(lambda _: tao_con(ns.bd_tram, bead_id,
                                              _ke_hoach(ns, bead_id, expected_commit, digest_bead)))),
        ("phu_thuoc", bao_ve(lambda da: noi_phu_thuoc(ns.bd_tram, _ke_hoach(ns, bead_id, expected_commit, digest_bead),
                                               da["tao_bead"]))),
        ("nhan", bao_ve(nhan)), ("su_kien", bao_ve(su_kien))])
