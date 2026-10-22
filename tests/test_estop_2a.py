from tram.chu import estop
from tram.chu.dieu_khien import bat_estop, tat_estop
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.estop import bat_estop_thao_tac, tiep_tuc_thao_tac
from tram.thao_tac.kho import KhoThaoTac


def _kho(tmp_path):
    db = tmp_path / "sk.db"
    return KhoSuKien(db), KhoThaoTac(db)


def test_dieu_khien_dung_chung(tmp_path):
    k, _ = _kho(tmp_path)
    bat_estop(k, "thử", tac_nhan="dai-ca")
    s = k.gan_day("_tram", "estop.bat", 1)[0]
    assert estop.dang_bat() and s.du_lieu == {"ly_do": "thử"} and s.tac_nhan == "dai-ca"
    tat_estop(k, tac_nhan="dai-ca")
    assert not estop.dang_bat() and k.gan_day("_tram", "estop.tat", 1)[0].du_lieu == {}


def test_estop_thao_tac_mot_lan_theo_ma(tmp_path):
    k, kt = _kho(tmp_path)
    a = bat_estop_thao_tac(k, kt, ly_do=None, ma="ma-estop-001", expected_version="tat")
    b = bat_estop_thao_tac(k, kt, ly_do=None, ma="ma-estop-001", expected_version="bat")
    assert estop.dang_bat() and a.lap_lai is False and b.lap_lai is True
    ds = k.gan_day("_tram", "estop.bat", 10)
    assert len(ds) == 1 and ds[0].tac_nhan == "dai-ca/dashboard"
    assert ds[0].du_lieu == {"ly_do": "Đại ca bấm estop trên dashboard", "ma_thao_tac": "ma-estop-001"}


def test_tiep_tuc_thao_tac(tmp_path):
    k, kt = _kho(tmp_path)
    estop.bat("x")
    tiep_tuc_thao_tac(k, kt, ma="ma-tieptuc-01", expected_version="bat")
    assert not estop.dang_bat()
    assert k.gan_day("_tram", "estop.tat", 1)[0].du_lieu == {"ma_thao_tac": "ma-tieptuc-01"}


def test_cli_estop_van_ghi_nhu_cu(tram_home_tam):
    from tram.cli import main
    from tram.su_kien.kho import mo_kho
    assert main(["chu", "estop", "--ly-do", "thử"]) == 0
    s = mo_kho().gan_day("_tram", "estop.bat", 1)[0]
    assert s.tac_nhan == "dai-ca" and s.du_lieu == {"ly_do": "thử"}
    assert main(["chu", "tiep-tuc"]) == 0 and not estop.dang_bat()
