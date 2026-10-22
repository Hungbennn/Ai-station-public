"""Mã thao tác phải được kiểm trước khi đối soát ghi mở chốt."""
import pytest
from test_tm20_chuoi import bo, M, L
from tram.api import doi_soat_deploy as api
from tram.deploy import chay
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import doc_su_kien
from tram.deploy.doi_soat import chua_doi_soat
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot


def test_reconcile_invalid_operation_id_cannot_unlock(bo, tmp_path, monkeypatch):
    bo.ans['deploy'] = None
    assert bo.run() == 'deploy_khong_ro'
    can = api.ban_can_doi_soat(doc_su_kien(bo.k.db, 'a'))
    monkeypatch.setattr(api, 'DuongDeploy', chay.DuongDeploy)
    than = api.ThanTiepTuc(ma_thao_tac='not valid id', expected_version='',
                          doi_soat={'ma': can['ma'], 'commit': L})
    kt = KhoThaoTac(tmp_path / 'tt.db')
    try:
        with pytest.raises(KhongHopLe):
            api.tiep_tuc(bo.k, kt, 'a', than)
        assert chua_doi_soat(doc_su_kien(bo.k.db, 'a'))
        assert not any(b == 'doi_soat' for b, *_ in bo.calls)
    finally:
        kt.close()



def test_same_operation_cannot_unlock_another_run(bo, tmp_path, monkeypatch):
    from tram.su_kien.kho import KhoSuKien
    bo.ans['deploy'] = None
    bo.run()
    can = api.ban_can_doi_soat(doc_su_kien(bo.k.db, 'a'))
    monkeypatch.setattr(api, 'DuongDeploy', chay.DuongDeploy)
    kt, kho = KhoThaoTac(tmp_path / 'tt.db'), KhoSuKien(tmp_path / 'sk.db')
    def than(ma):
        return api.ThanTiepTuc(ma_thao_tac='confirm-0001', expected_version='',
                              doi_soat={'ma': ma, 'commit': L})
    try:
        api.tiep_tuc(kho, kt, 'a', than(can['ma']))
        bd = next(s for s in doc_su_kien(kho.db, 'a') if s.loai == 'deploy.bat_dau')
        ghi(kho.db, 'a', 'deploy.bat_dau', {**bd.du_lieu, 'ma_thao_tac': 'dp-another'})
        ghi(kho.db, 'a', 'deploy.xong', {'ma_thao_tac': 'dp-another', 'ket_qua': 'khong_ro'})
        with pytest.raises(XungDot):
            api.tiep_tuc(kho, kt, 'a', than('dp-another'))
        assert chua_doi_soat(doc_su_kien(kho.db, 'a'))
    finally:
        kt.close()
        kho.close()

