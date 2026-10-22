import hashlib
import json

import pytest

from tram.chu.cai_ho_so_kiem import lap
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, PHIEN_BAN_HO_SO, ho_so_tu_manifest

CU = {"cong": [7700], "goc": "/Users/Shared/tram-kiem", "nha_quan_ly": "/Users/tram-tho", "phien_ban": 1,
      "sha256": "x", "tram_home": "/Users/dai-ca/.tram"}


@pytest.mark.parametrize('cu', [1, 2])
def test_sinh_v3_tu_manifest_cu_va_thu_tu_ho_so_truoc(tmp_path, cu):
    ds = lap(CU | {'phien_ban': cu}, tmp_path)
    assert [t.ten for t in ds] == [str(HO_SO_KIEM), str(MANIFEST_KIEM)]
    hs, mf = (tmp_path / HO_SO_KIEM.name).read_bytes(), (tmp_path / MANIFEST_KIEM.name).read_bytes()
    m, hs2 = ho_so_tu_manifest(mf)
    assert hs2 == hs and m["phien_ban"] == PHIEN_BAN_HO_SO == 3
    assert ds[0].mong("")["sha256"] == hashlib.sha256(hs).hexdigest()
    assert json.loads(mf)["goc"] == CU["goc"] and b"(allow file-read*)" in hs


def test_manifest_thieu_khoa_tu_choi(tmp_path):
    with pytest.raises(ValueError):
        lap({"cong": [7700]}, tmp_path)
