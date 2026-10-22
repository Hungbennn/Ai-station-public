"""Nút Phê duyệt của luồng feature (spec 2 §5.2; spec 4 §7.3, §10 bước 4) — `phe_duyet.duyet`/`tra_ve` chuyển sang
đây khi tram-api có `nguon_spec` (không có → giữ 501 của 2a).

Loại thao tác theo bản ghi `thao_tac` nếu mã đã dùng (làm tiếp đúng thao tác sau sự cố), không thì theo nhãn hiện tại:
`cho-duyet-spec` → `duyet_spec` / `tra_ve_spec`; feature `theo-plan` có mọi con đã đóng → `dong_feature` (Đại ca tự
đóng, #16). Trả về spec: góp ý vào notes, gỡ `cho-duyet-spec`, gắn lại `can-spec`, sự kiện `spec.tra_ve {gop_y}`."""
from tram.cham_cot.ghi import GIO_VN
from tram.duong_dan import bay_gio, doc_luc
from tram.suy.phe_duyet_spec import feature_xong
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.duyet_spec import NHAN_CHO_DUYET, NHAN_THEO_PLAN
from tram.thao_tac.loi import KhongHopLe

NHAN_CAN_SPEC = "can-spec"


def loai_thao_tac(nc: NguCanhGhi, bead_id: str, ma: str, *, la_duyet: bool) -> str:
    """`duyet_spec` | `dong_feature` | `tra_ve_spec` | `cot_3` (đường cũ của 2a)."""
    bg = nc.kho_tt.lay(ma)
    if bg is not None:
        return bg.loai if bg.loai in ("duyet_spec", "dong_feature", "tra_ve_spec") else "cot_3"
    b = nc.bd.mot(bead_id)
    if NHAN_CHO_DUYET in b.labels:
        return "duyet_spec" if la_duyet else "tra_ve_spec"
    if la_duyet and b.issue_type == "feature" and NHAN_THEO_PLAN in b.labels:
        return "dong_feature"
    return "cot_3"


def tra_ve_spec(nc: NguCanhGhi, bead_id: str, *, gop_y: str, ma: str, expected_version: str) -> KetQuaThaoTac:
    gop_y = gop_y.strip()
    if not gop_y:
        raise KhongHopLe("Cần góp ý khi trả về spec")
    dau = f"(ma_thao_tac {ma})"

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if NHAN_CHO_DUYET not in b.labels or b.status == "closed":
            raise KhongHopLe("Feature không còn ở 'Spec chờ duyệt'")

    def nhan_va_ghi_chu(_) -> dict:
        b = nc.bd.mot(bead_id)
        gio = doc_luc(bay_gio()).astimezone(GIO_VN).strftime("%Y-%m-%d %H:%M")
        ghi_chu = None if dau in b.notes else f"[{TAC_NHAN} {gio}] Trả về spec: {gop_y} {dau}"
        bo = [NHAN_CHO_DUYET] if NHAN_CHO_DUYET in b.labels else []
        them = [] if NHAN_CAN_SPEC in b.labels else [NHAN_CAN_SPEC]
        if bo or them or ghi_chu:
            nc.bd.cap_nhat_nhan(bead_id, them=them, bo=bo, ghi_chu=ghi_chu)
        return {"bo": bo, "them": them}

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "spec.tra_ve", {"gop_y": gop_y}, ma=ma)

    yc = YeuCau(ma, "tra_ve_spec", nc.du_an, bead_id, {"gop_y": gop_y}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi,
                         cac_buoc=[("nhan_va_ghi_chu", nhan_va_ghi_chu), ("su_kien", su_kien)])


def dong_feature(nc: NguCanhGhi, bead_id: str, *, ma: str, expected_version: str) -> KetQuaThaoTac:
    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if not feature_xong(b, nc.bd.tat_ca()):
            raise KhongHopLe("Chỉ đóng feature theo-plan khi mọi bead con đã đóng")

    def dong(_) -> bool:
        if nc.bd.mot(bead_id).status != "closed":
            nc.bd.dong(bead_id, "Đại ca đóng feature trên dashboard sau khi mọi bead con đã đóng")
        return True

    yc = YeuCau(ma, "dong_feature", nc.du_an, bead_id, {}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[("dong", dong)])
