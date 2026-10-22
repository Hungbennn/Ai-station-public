import json
from contextlib import closing

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from tram.api.than import ThanChot
from tram.phieu.kho import KhoPhieu


def test_chot_than_hop_le_lon_van_den_kiem_bat_ghi(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    pt.cac_du_an = lambda: ['hr']
    pt.bat_ghi = lambda _: False
    body = {'ma_thao_tac': 'v2-chot-001', 'expected_version': '',
            'tra_loi': ['a' * 4000 for _ in range(20)]}
    ThanChot.model_validate(body)
    assert len(json.dumps(body).encode()) > 65536
    r = goi(app, 'POST', '/api/bead/hr/hr-1/chot', headers=DAI_CA, json_body=body)
    assert r.status == 422
    assert 'bat_ghi: false' in r.json()['loi']


def test_cap_ma_ghep_dong_ke_ca_co_phien_va_retry(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    pt.mo_kho_phieu = lambda: KhoPhieu(tmp_path / 'ghep-v2.db')
    with closing(pt.mo_kho_phieu()) as kho:
        from tram.phieu.ma_ghep import LUOC_DO_GHEP
        kho.db.executescript(LUOC_DO_GHEP)
        before = kho.db.execute('SELECT * FROM ma_ghep').fetchall()
        events = kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    for may in ('C2', 'C2', 'D2'):
        r = goi(app, 'POST', '/api/passkey/ghep-ma', headers=DAI_CA,
                json_body={'may_id': may, 'ma_thao_tac': 'v2-ghep-001'})
        assert r.status == 404
        assert 'ma' not in r.json()
    with closing(pt.mo_kho_phieu()) as kho:
        assert kho.db.execute('SELECT * FROM ma_ghep').fetchall() == before
        assert kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0] == events
