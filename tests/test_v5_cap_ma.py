from contextlib import closing
from types import SimpleNamespace

from tram.chu.cap_ma import _cap_ma
from tram.phieu.kho import mo_kho_phieu
from tram.phieu.ma_ghep import cap_ma_ghep
from kho_phieu_gia import LUC


def test_cli_cap_ma_da_dong_khong_ghi_su_kien(tram_home_tam, capsys):
    assert _cap_ma(SimpleNamespace(may_id="may-v5")) == 2
    out = capsys.readouterr()
    assert out.out == "" and "passkey" in out.err
    with closing(mo_kho_phieu()) as kho:
        assert kho.db.execute("SELECT * FROM su_kien WHERE loai='may.cap_ma'").fetchall() == []


def test_cap_ma_mac_dinh_van_la_api(tram_home_tam):
    with closing(mo_kho_phieu()) as kho:
        cap_ma_ghep(kho, "may-api", luc=LUC)
        assert kho.db.execute("SELECT tac_nhan FROM su_kien WHERE loai='may.cap_ma'").fetchall() == [("tram/api",)]
