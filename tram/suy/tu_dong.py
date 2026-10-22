"""Trạng thái hiển thị của tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5) — tính lúc đọc từ sự kiện.
TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
có sẵn."""
from tram.suy.deploy import chi_tiet_deploy, tom_tat_deploy
from tram.su_kien.kho import KhoSuKien
from tram.suy.tu_merge import TieuDe, cho_dai_ca  # TM-2
from tram.tu_dong.cai_dat import KHOA_CUNG, sang_api
from tram.tu_dong.luu import DU_AN_TRAM, TamDung, doc_trang_thai, lich_su_doi, tam_dung_cua


def tam_dung_api(td: TamDung | None) -> dict | None:
    return None if td is None else {"boi": td.boi, "luc": td.luc, "ly_do": td.ly_do}


def chung(kho: KhoSuKien, *, kenh_ghi: str, la_dai_ca: bool, estop_bat: bool) -> dict:
    """Phần chung của mọi GET: `chi_tam_dung` (D87) — dashboard khoá mọi nút trừ TẠM DỪNG, kèm giải thích."""
    return {"tam_dung_tram": tam_dung_api(tam_dung_cua(kho.db, DU_AN_TRAM)), "estop": estop_bat, "kenh_ghi": kenh_ghi,
            "chi_tam_dung": kenh_ghi == "header", "la_dai_ca": la_dai_ca}


def tom_tat_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"ten": ten, "bat_ghi": bat_ghi, "tu_merge": tt.cai_dat.tu_merge, "tu_deploy": tt.cai_dat.tu_deploy,
            "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an),
            **tom_tat_deploy(kho.db, ten)}


def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool, tieu_de: TieuDe = dict) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
            "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
            "lich_su_doi": lich_su_doi(kho.db, ten),
            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else [],  # TM-2: tắt → []
            **chi_tiet_deploy(kho.db, ten)}
