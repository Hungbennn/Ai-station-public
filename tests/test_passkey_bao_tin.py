from datetime import datetime, timezone
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma
from tram.bao_tin.passkey import gui_cho
from tram.bao_tin.telegram import LoiTelegram


def test_dem_gom_sang_retry_restart(tmp_path):
    p = tmp_path/'pk.db'
    with mo_kho(p) as db, giao_dich(db):
        for loai in ('them','thu-hoi','khoi-phuc'):
            db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)',(loai,100))
    dem = datetime(2026,10,18,16,tzinfo=timezone.utc)  # 23h VN
    sang = datetime(2026,10,19,0,tzinfo=timezone.utc)  # 7h VN
    da_gui = []
    assert gui_cho(p,'23:00-07:00',dem,da_gui.append) == 0
    assert not da_gui
    def hong(t):
        raise LoiTelegram('marker-secret')
    assert gui_cho(p,'23:00-07:00',sang,hong) == 0
    assert gui_cho(p,'23:00-07:00',sang,da_gui.append) == 3
    assert len(da_gui) == 1
    for loai in ('Thêm thiết bị','Thu hồi thiết bị','Khôi phục thiết bị'):
        assert loai in da_gui[0]
    assert gui_cho(p,None,sang,da_gui.append) == 0
    assert 'marker-secret' not in da_gui[0]


def test_lan_dau_vong_bao_tin_van_doc_outbox(tmp_path):
    from types import SimpleNamespace
    from tram.bao_tin.vong import NguCanhBaoTin, mot_vong
    p = tmp_path/'pk.db'
    with mo_kho(p) as db, giao_dich(db):
        cap_ma(db,nguoi(db,'chu'),100,True)
    gui = []
    nc = NguCanhBaoTin(SimpleNamespace(id_moi_nhat=lambda:0),None,gui.append,tmp_path/'bao',passkey_path=p)
    mot_vong(nc)
    assert len(gui) == 1
