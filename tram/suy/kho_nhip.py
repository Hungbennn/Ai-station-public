"""Đọc nhịp đèn Điều phối từ kho sự kiện (plan 2e G9; review đợt 4 F11): MỌI nhịp trong `HAN_SONG`, không cắt theo
số dòng — nhiều phiên khác ghi dồn không đẩy được nhịp của phiên còn sống ra khỏi tập đọc. Không có nhịp nào trong
hạn thì trả nhịp mới nhất (nếu có) để phân biệt "đã hết hạn" (`sang: False`) với "chưa từng có" (`sang: None`).
Adapter duy nhất dùng `_CHON`/`_doc` nội bộ của `KhoSuKien`; tham số đều do mã đặt, không từ client."""
from tram.su_kien.kho import _CHON
from tram.suy.dieu_phoi import DU_AN_HE, HAN_SONG, LOAI


def doc_nhip(kho, luc):
    tu = (luc - HAN_SONG).strftime("%Y-%m-%dT%H:%M:%SZ")
    ds = kho._doc(
        f"{_CHON} WHERE du_an=? AND loai=? AND luc>=? ORDER BY id DESC",
        (DU_AN_HE, LOAI, tu),
    )
    return ds or kho.gan_day(DU_AN_HE, LOAI, 1)
