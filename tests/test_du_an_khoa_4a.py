import pytest

from tram.cau_hinh.du_an import nap_du_an
from tram.cau_hinh.du_an_giao import TAI_LIEU_MAC_DINH, CauHinhGiao, NganSachBead, NganSachMuc

GOC = 'ten: x\nduong_dan: /tmp/x\nlenh_cho_phep: ["php artisan test --filter *", "npm run test:unit"]\n'


def _nap(tmp_path, them: str = ""):
    (tmp_path / "x.yaml").write_text(GOC + them, encoding="utf-8")
    return nap_du_an("x", thu_muc=tmp_path)


def test_mac_dinh_theo_spec(tmp_path):
    g = _nap(tmp_path).giao
    assert g == CauHinhGiao() and g.tai_lieu_du_an == TAI_LIEU_MAC_DINH
    assert g.ngan_sach.code == NganSachMuc(3, 90, 200_000) and g.ngan_sach.qc == NganSachMuc(2, 45, 100_000)
    assert g.ngan_sach.bead == NganSachBead(3, 9, 360)


def test_doc_du_khoa(tmp_path):
    g = _nap(tmp_path, 'lenh_kiem_mac_dinh: ["npm run test:unit"]\nduong_dan_cam: ["erp/config/**"]\n'
                       'duong_dan_cam_cho_phep: ["erp/package.json"]\ntai_lieu_du_an: [AGENTS.md]\n'
                       "ngan_sach: {code: {phut: 120}, bead: {vong_qc: 2}}\n").giao
    assert g.lenh_kiem_mac_dinh == ("npm run test:unit",) and g.duong_dan_cam == ("erp/config/**",)
    assert g.duong_dan_cam_cho_phep == ("erp/package.json",) and g.tai_lieu_du_an == ("AGENTS.md",)
    assert g.ngan_sach.code == NganSachMuc(3, 120, 200_000) and g.ngan_sach.bead == NganSachBead(2, 9, 360)


def test_du_an_that_van_nap_duoc():
    assert nap_du_an("vi-du").giao == CauHinhGiao()


@pytest.mark.parametrize("them", [
    'lenh_kiem_mac_dinh: ["npm run build"]\n',              # không khớp lenh_cho_phep
    'lenh_kiem_mac_dinh: "npm run test:unit"\n',
    'duong_dan_cam: ["/etc/**"]\n', 'duong_dan_cam: ["../x"]\n',
    'duong_dan_cam_cho_phep: ["erp/*.json"]\n',             # ngoại lệ chỉ từng đường dẫn cụ thể
    'tai_lieu_du_an: ["../bi-mat.md"]\n',
    "ngan_sach: {code: {so_lan_chay: 4}}\n",                 # #13: tối đa 3
    "ngan_sach: {qc: {phut: 0}}\n", "ngan_sach: {bead: {phut: true}}\n",
    "ngan_sach: {spec: {phut: 10}}\n", "ngan_sach: {code: {la: 1}}\n", "ngan_sach: [1]\n",
])
def test_sai_bao_loi(tmp_path, them):
    with pytest.raises(ValueError):
        _nap(tmp_path, them)
