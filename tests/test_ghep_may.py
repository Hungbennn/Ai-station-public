import re
from datetime import datetime, timezone

from tho_api_gia import tao_tram
from tram.cli import main
from tram.phieu.kho import mo_kho_phieu
from tram.phieu.ma_ghep import cap_ma_ghep
from tram.phieu.may import cap_token_may, xac_thuc_may


def test_doi_ma_qua_http_khong_can_bearer_token_dung_duoc_ngay(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    kho = t.kho()
    ma = cap_ma_ghep(kho, "C2", luc=t.gio[0]).ma
    r = t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma})
    assert r.status == 200 and r.headers["cache-control"] == "no-store" and r.json()["may_id"] == "C2"
    tok = r.json()["token"]
    assert xac_thuc_may(kho, tok) == "C2"
    t.token["C2"] = tok
    assert t.goi("GET", "/api/tho/ping", "C2").json() == {"may_id": "C2", "khe": []}
    lai = t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma})
    assert lai.status == 403 and tok not in lai.body.decode() and "token" not in lai.json()


def test_sai_nhieu_lan_bi_khoa_429_than_sai_422(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    ma = cap_ma_ghep(t.kho(), "C2", luc=t.gio[0]).ma
    for _ in range(5):
        assert t.goi("POST", "/api/ghep-may", None, json_body={"ma": "0000-0000-0000"}).status == 403
    assert t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma}).status == 429
    for than in ({}, {"ma": ma, "may_id": "X"}, {"ma": "x" * 65}):
        assert t.goi("POST", "/api/ghep-may", None, json_body=than).status == 422


def test_cli_chu_cap_ma_can_phien_passkey(tram_home_tam, capsys):
    assert main(["chu", "cap-ma", "C"]) == 2
    out = capsys.readouterr()
    assert out.out == "" and "passkey" in out.err
