from datetime import datetime, timezone
from tram.phieu.kho import KhoPhieu
from tram.phieu.khe import dang_ky_khe, khe_dang_bat, bat_tat_khe


def test_dang_ky_khong_cap_quyen_bat(tmp_path):
    kho = KhoPhieu(tmp_path/'sk.db')
    luc = datetime.now(timezone.utc)
    k = {'ten':'k1','cli':'claude','ten_goi_nho':'Khe','vai_uu_tien':['code']}
    try:
        with kho.giao_dich():
            dang_ky_khe(kho,'B',[k],luc=luc)
        assert not khe_dang_bat(kho,'B/k1')
        with kho.giao_dich():
            bat_tat_khe(kho,'B/k1',bat=True,vi_sao='',tac_nhan='dai-ca',luc=luc)
        assert khe_dang_bat(kho,'B/k1')
        with kho.giao_dich():
            bat_tat_khe(kho,'B/k1',bat=False,vi_sao='',tac_nhan='dai-ca',luc=luc)
            dang_ky_khe(kho,'B',[{**k,'ten_goi_nho':'Mới'}],luc=luc)
        assert not khe_dang_bat(kho,'B/k1')
    finally:
        kho.close()
