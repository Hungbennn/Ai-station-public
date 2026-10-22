"""Tắt / bật khe và đóng cầu dao từ dashboard 2b (spec 2 §5.4, §7, §12.3; spec 3 §8.3, §10).

Idempotent theo `ma_thao_tac` (bảng `thao_tac`), và ghi QUA ĐÚNG đường ghi của phần 3 — `bat_tat_khe`,
`dong_cau_dao` trong `KhoPhieu.giao_dich()` — nên nhịp tim (dừng mềm `khe-tat`), cấp phiếu và `trang_thai_khe`
thấy y như lệnh `tram tho tat-khe`. Sự kiện mang `ma_thao_tac`, `tac_nhan = dai-ca/dashboard`."""
from collections.abc import Callable
from datetime import datetime

from tram.phieu.cau_dao import dong_cau_dao, trang_thai_cau_dao
from tram.phieu.khe import bat_tat_khe, phien_ban_khe, su_kien_khe
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongThay, XungDot


def _da_ghi(kho: KhoPhieu, loai: str, ma: str) -> bool:
    return kho.db.execute("SELECT 1 FROM su_kien WHERE du_an = ? AND loai = ? AND json_extract(du_lieu,"
                          " '$.ma_thao_tac') = ? LIMIT 1", (DU_AN_TRAM, loai, ma)).fetchone() is not None


def _kiem_khe(kho: KhoPhieu, khe_id: str) -> None:
    if su_kien_khe(kho, khe_id, ("khe.dang_ky",)) is None:
        raise KhongThay(f"Không có khe {khe_id}")


def _kiem_version(kho: KhoPhieu, khe_id: str, expected: str) -> None:
    _kiem_khe(kho, khe_id)
    if (hien := phien_ban_khe(kho, khe_id)) != expected:
        raise XungDot(f"Khe {khe_id} đã đổi (hiện {hien}, đang xem {expected}) — tải lại")


def _chay(kho: KhoPhieu, kho_tt: KhoThaoTac, yc: YeuCau, kiem: Callable[[], None],
          ghi: Callable[[], None]) -> KetQuaThaoTac:
    def buoc(_) -> bool:
        with kho.giao_dich():
            if not _da_ghi(kho, yc.loai, yc.ma):     # crash giữa ghi sự kiện và đánh dấu bước: không ghi lần hai
                # Kiểm và ghi cùng BEGIN IMMEDIATE: cả lần đầu lẫn resume sau crash.
                bg = kho_tt.lay(yc.ma)
                if yc.loai != "khe.tat" and bg.expected_version != yc.expected_version:
                    raise XungDot("Thao tác chưa xong phải giữ phiên bản gốc; tải lại và dùng mã mới")
                kiem()
                ghi()
        return True
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(yc.loai, buoc)])


def tat_khe_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, vi_sao: str | None, ma: str,
                     expected_version: str, luc: datetime) -> KetQuaThaoTac:
    """KHÔNG kiểm `expected_version` (như estop — plan 2b G9): tắt khe không được hỏng vì màn hình cũ."""
    vs = (vi_sao or "").strip()
    yc = YeuCau(ma, "khe.tat", DU_AN_TRAM, khe_id, {"vi_sao": vs}, expected_version)
    return _chay(kho, kho_tt, yc, lambda: _kiem_khe(kho, khe_id), lambda: bat_tat_khe(
        kho, khe_id, bat=False, vi_sao=vs, tac_nhan=TAC_NHAN, luc=luc, them={"ma_thao_tac": ma}))


def bat_khe_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, vi_sao: str | None, ma: str,
                     expected_version: str, luc: datetime) -> KetQuaThaoTac:
    vs = (vi_sao or "").strip()
    yc = YeuCau(ma, "khe.bat", DU_AN_TRAM, khe_id, {"vi_sao": vs}, expected_version)
    return _chay(kho, kho_tt, yc, lambda: _kiem_version(kho, khe_id, expected_version), lambda: bat_tat_khe(
        kho, khe_id, bat=True, vi_sao=vs, tac_nhan=TAC_NHAN, luc=luc, them={"ma_thao_tac": ma}))


def dong_cau_dao_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, ma: str, expected_version: str,
                          luc: datetime) -> KetQuaThaoTac:
    def kiem() -> None:
        _kiem_version(kho, khe_id, expected_version)
        if not trang_thai_cau_dao(kho, khe_id, luc).ngat:
            raise XungDot(f"Cầu dao khe {khe_id} đang đóng — tải lại")

    yc = YeuCau(ma, "khe.cau_dao_dong", DU_AN_TRAM, khe_id, {}, expected_version)
    return _chay(kho, kho_tt, yc, kiem, lambda: dong_cau_dao(
        kho, khe_id, ly_do="dai-ca", luc=luc, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}))
