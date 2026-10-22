"""Chấm điểm recall và chọn theo nhóm (spec 1b §7 bước 3–4).

Phỏng theo cách chấm memory của crewAI (MIT License, Copyright (c) 2025 crewAI, Inc. — xem NOTICE):
diem = 0,5·nghĩa + 0,3·độ mới + 0,2·quan trọng. Khác crewAI: độ mới tính từ `tao_luc` (không từ lần dùng
cuối — tránh vòng tự củng cố), chọn riêng từng nhóm, không bù chéo."""
from collections.abc import Sequence
from datetime import datetime

from tram.duong_dan import doc_luc
from tram.nho.mo_hinh import KyUc

NUA_DOI_NGAY = 30.0
TRONG_SO = (0.5, 0.3, 0.2)        # nghĩa, mới, quan trọng


def diem(cosine: float, tao_luc: str, quan_trong: float, bay_gio: datetime) -> float:
    nghia = max(0.0, cosine)
    so_ngay = max(0.0, (bay_gio - doc_luc(tao_luc)).total_seconds() / 86400)
    moi = 0.5 ** (so_ngay / NUA_DOI_NGAY)
    return TRONG_SO[0] * nghia + TRONG_SO[1] * moi + TRONG_SO[2] * quan_trong


def chon(ung_vien: Sequence[tuple[KyUc, float]], han_muc: int, bay_gio: datetime) -> list[KyUc]:
    """Sắp `diem` giảm dần; hoà → `tao_luc` mới hơn → `id`. Lấy tối đa `han_muc`."""
    co_diem = [(diem(cos, k.tao_luc, k.quan_trong, bay_gio), doc_luc(k.tao_luc), k) for k, cos in ung_vien]
    co_diem.sort(key=lambda x: (-x[0], -x[1].timestamp(), x[2].id))
    return [k for _, _, k in co_diem[:max(0, han_muc)]]
