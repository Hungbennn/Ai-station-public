from pathlib import Path

import pytest

from tram.cau_hinh.du_an import MoiTruongKiem, nap_du_an

GOC = "ten: x\nduong_dan: /tmp/x\n"


def _nap(tmp_path, them: str = ""):
    (tmp_path / "x.yaml").write_text(GOC + them, encoding="utf-8")
    return nap_du_an("x", thu_muc=tmp_path)


def test_mac_dinh_khi_thieu_khoa(tmp_path):
    da = _nap(tmp_path)
    assert da.lenh_cho_phep == () and da.moi_truong_kiem is None and da.nhanh_chinh == "main"


def test_doc_du_ba_khoa(tmp_path):
    da = _nap(tmp_path, 'lenh_cho_phep: ["php artisan test --filter *", "npm run test:unit"]\n'
                        "moi_truong_kiem: {file: ~/tram/env/hr-codex.env, dich: erp/.env.testing}\n"
                        "nhanh_chinh: develop\n")
    assert da.lenh_cho_phep == ("php artisan test --filter *", "npm run test:unit")
    assert da.moi_truong_kiem == MoiTruongKiem(Path.home() / "tram/env/hr-codex.env", "erp/.env.testing")
    assert da.nhanh_chinh == "develop"


@pytest.mark.parametrize("them", [
    'lenh_cho_phep: ["* run"]\n', 'lenh_cho_phep: ["npm run test*"]\n', 'lenh_cho_phep: ["npm; rm"]\n',
    'lenh_cho_phep: "npm run test"\n', "moi_truong_kiem: {file: env, dich: erp/.env}\n",
    "moi_truong_kiem: {file: /a/env, dich: ../.env}\n", "moi_truong_kiem: {file: /a/env}\n",
    "moi_truong_kiem: /a/env\n", "nhanh_chinh: tram/x\n", "nhanh_chinh: a..b\n", "nhanh_chinh: -x\n",
    "nhanh_chinh: 3\n",
])
def test_sai_bao_loi(tmp_path, them):
    with pytest.raises(ValueError):
        _nap(tmp_path, them)


def test_du_an_that_van_nap_duoc():
    da = nap_du_an("vi-du")
    assert da.nhanh_chinh == "main" and da.lenh_cho_phep == () and da.moi_truong_kiem is None
