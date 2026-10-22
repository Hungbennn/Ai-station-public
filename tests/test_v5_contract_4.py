from types import SimpleNamespace

from tram.tho.theo_doi import TheoDoi


def test_join_nhan_han_huu_han():
    goi = []
    luong = SimpleNamespace(join=lambda timeout=None: goi.append(timeout), is_alive=lambda: False)
    td = TheoDoi(None, None, None)
    td._luong = luong
    td.dung_lai(han=2)
    assert len(goi) == 1 and goi[0] is not None and 0 <= goi[0] <= 2
