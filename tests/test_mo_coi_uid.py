"""V2-0 / bs-863.15, review vòng 1 A01: CLI mồ côi được dọn theo UID của khe, KHÔNG theo số pid/pgid đọc từ file (số có
thể đã cấp lại). Bản ghi chỉ còn để gửi `chay.xong mo-coi`; dọn không chứng minh được → giữ bản ghi + phiếu, khe dừng.
Dọn UID là bản GIẢ."""
import json
from types import SimpleNamespace

import pytest

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import mo_coi_khe
from tram.tho.mo_coi import don_mo_coi

BAN_GHI = {"pid": 4242, "pgid": 4242, "giao_id": "g-1", "luot": 2, "lan": 1}


@pytest.mark.parametrize("noi_dung, ra", [(json.dumps(BAN_GHI), BAN_GHI), ("không phải json", None),
                                          (json.dumps({"pid": 4242}), None), (None, None)])
def test_don_theo_uid_roi_moi_xoa_ban_ghi(tmp_path, noi_dung, ra):
    p, goi = tmp_path / "pid", []
    if noi_dung is not None:
        p.write_text(noi_dung)
    assert don_mo_coi(p, don=lambda: goi.append(1)) == ra and goi == [1] and not p.exists()


def _hong(*a):
    raise LoiThuHoi("còn tàn dư của UID khe")


def test_don_khong_chung_minh_duoc_thi_giu_ban_ghi(tmp_path):
    (p := tmp_path / "pid").write_text(json.dumps(BAN_GHI))
    with pytest.raises(LoiThuHoi):
        don_mo_coi(p, don=_hong)
    assert json.loads(p.read_text()) == BAN_GHI


def test_khoi_dong_khe_khong_chung_minh_duoc_khe_sach_thi_dung_va_giu_phieu(tmp_path):
    (p := tmp_path / "pid").write_text(json.dumps(BAN_GHI))
    so = SimpleNamespace(pid=p, doc_phieu=lambda: 1 / 0)
    assert mo_coi_khe.don_mo_coi_khe(SimpleNamespace(don_khe=_hong), None, so, SimpleNamespace()) == (None, True)
    assert p.exists()
