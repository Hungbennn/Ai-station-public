from types import SimpleNamespace
from tram.chu.cap_ma import _cap_ma
from api_gia import tao_app_gia, DAI_CA
from asgi_gia import goi


def test_cli_cu_khong_cap_ma_khong_co_phien(capsys):
    assert _cap_ma(SimpleNamespace(may_id='C')) == 2
    assert 'passkey' in capsys.readouterr().err


def test_endpoint_cap_ma_ghep_chua_mo(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    r = goi(app, 'POST', '/api/passkey/ghep-ma', json_body={'may_id':'C'}, headers=DAI_CA)
    assert r.status == 404 and 'ma' not in r.json()
    assert r.headers['cache-control'] == 'no-store'
