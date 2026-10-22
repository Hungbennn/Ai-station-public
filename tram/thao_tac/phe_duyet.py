"""Phê duyệt (spec 2 §5.2): Duyệt cột 3, Trả về + góp ý, Trả lời escalation / decision mở. Spec, đóng feature →
`tram/thao_tac/spec.py` (4b) khi tram-api truyền `nguon_spec`."""
from tram.cham_cot.ghi import GIO_VN, NHAN_KHOA
from tram.duong_dan import bay_gio, doc_luc
from tram.suy.cot import hien_tren_bang, ly_do_khong_tra_loi
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.duyet_spec import NguonSpec, duyet_spec
from tram.thao_tac.duyet_merge import kiem_da_merge, pr_cua
from tram.thao_tac.loi import KhongHopLe
from tram.thao_tac.spec import dong_feature, loai_thao_tac, tra_ve_spec

NHAN_REVIEW = "cot:cho-review"


def ly_do_duyet(pr: str | None, commit: str | None = None, nhanh: str = "main") -> str:
    if commit:
        return f"Đại ca duyệt — commit {commit[:7]} đã vào {nhanh}"
    if pr:
        return (f"Đại ca xác nhận đã merge PR {pr} trên GitHub — thao tác tay trên dashboard, "
                "không phải bằng chứng máy")
    return "Đại ca duyệt trên dashboard"


def _kiem_cot_3(nc: NguCanhGhi, bead_id: str, expected_version: str) -> None:
    b = nc.bd.mot(bead_id)
    if "cho-duyet-spec" in b.labels:          # spec chỉ đi `duyet_spec`/`tra_ve_spec` (cần `nguon_spec`) — bs-2bd.1.7
        raise KhongHopLe("Bead đang chờ duyệt spec — chỉ duyệt/trả về qua luồng spec")
    kiem_version(b, expected_version)
    if NHAN_REVIEW not in b.labels or not hien_tren_bang(b):     # đã đóng hoặc hoãn (Q2)
        raise KhongHopLe("Chỉ thao tác với bead đang chờ review (cột 3)")


def duyet(nc: NguCanhGhi, bead_id: str, *, ma: str, expected_version: str, expected_commit: str | None = None,
          digest_bead: str | None = None, nguon_spec: NguonSpec | None = None) -> KetQuaThaoTac:
    if nguon_spec is not None and (loai := loai_thao_tac(nc, bead_id, ma, la_duyet=True)) != "cot_3":
        if loai == "dong_feature":
            return dong_feature(nc, bead_id, ma=ma, expected_version=expected_version)
        return duyet_spec(nc, nguon_spec, bead_id, ma=ma, expected_version=expected_version,
                          expected_commit=expected_commit, digest_bead=digest_bead)
    bang_chung = None

    def dong(_) -> dict:
        b = nc.bd.mot(bead_id)
        pr = pr_cua(nc, bead_id)
        if b.status != "closed":
            # Retry sau lỗi trước bd close cũng phải có bằng chứng; retry sau close chỉ đối soát.
            pr, commit, nhanh = bang_chung or kiem_da_merge(nc, bead_id)
            _kiem_cot_3(nc, bead_id, expected_version)
            nc.bd.dong(bead_id, ly_do_duyet(pr, commit, nhanh))
        return {"pr": pr}

    def kiem_moi() -> None:
        nonlocal bang_chung
        _kiem_cot_3(nc, bead_id, expected_version)
        bang_chung = kiem_da_merge(nc, bead_id)
        _kiem_cot_3(nc, bead_id, expected_version)  # fetch/gh có thể chờ lâu: kiểm lại trước tạo thao tác

    yc = YeuCau(ma, "duyet", nc.du_an, bead_id, {"expected_commit": expected_commit, "digest_bead": digest_bead},
                expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi,
                         cac_buoc=[("dong", dong)])


def tra_ve(nc: NguCanhGhi, bead_id: str, *, gop_y: str, ma: str, expected_version: str,
           nguon_spec: NguonSpec | None = None) -> KetQuaThaoTac:
    if nguon_spec is not None and loai_thao_tac(nc, bead_id, ma, la_duyet=False) == "tra_ve_spec":
        return tra_ve_spec(nc, bead_id, gop_y=gop_y, ma=ma, expected_version=expected_version)
    gop_y = gop_y.strip()
    if not gop_y:
        raise KhongHopLe("Cần góp ý khi trả về")
    dau = f"(ma_thao_tac {ma})"

    def nhan_va_ghi_chu(_) -> dict:
        b = nc.bd.mot(bead_id)                     # đối soát: notes đã có dấu mã thì không ghi lại
        bo = [n for n in b.labels if n.startswith("cot:") or n == NHAN_KHOA]
        gio = doc_luc(bay_gio()).astimezone(GIO_VN).strftime("%Y-%m-%d %H:%M")
        ghi_chu = None if dau in b.notes else f"[{TAC_NHAN} {gio}] Trả về: {gop_y} {dau}"
        if bo or ghi_chu:
            nc.bd.cap_nhat_nhan(bead_id, bo=bo, ghi_chu=ghi_chu)
        return {"bo": bo}

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.tra_ve", {"gop_y": gop_y}, ma=ma)

    yc = YeuCau(ma, "tra_ve", nc.du_an, bead_id, {"gop_y": gop_y}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=lambda: _kiem_cot_3(nc, bead_id, expected_version),
                         cac_buoc=[("nhan_va_ghi_chu", nhan_va_ghi_chu), ("su_kien", su_kien)])


def tra_loi_decision(nc: NguCanhGhi, bead_id: str, *, tra_loi: str, ma: str,
                     expected_version: str) -> KetQuaThaoTac:
    """Escalation hoặc decision mở: `bd close <decision> --reason <trả lời>` — đóng **chính** decision;
    sự kiện dùng chung `escalation.tra_loi {escalation_id = id decision}` (spec 2 §12.2)."""
    tra_loi = tra_loi.strip()
    if not tra_loi:
        raise KhongHopLe("Cần câu trả lời")

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if (ly_do := ly_do_khong_tra_loi(b)) is not None:
            raise KhongHopLe(ly_do)

    def dong(_) -> bool:
        if nc.bd.mot(bead_id).status != "closed":
            nc.bd.dong(bead_id, tra_loi)           # câu trả lời = close_reason; không mở quyền nguy hiểm (Q6)
        return True

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "escalation.tra_loi", {"escalation_id": bead_id}, ma=ma)

    yc = YeuCau(ma, "tra_loi", nc.du_an, bead_id, {"tra_loi": tra_loi}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[("dong", dong), ("su_kien", su_kien)])
