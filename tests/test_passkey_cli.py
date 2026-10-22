import io
from types import SimpleNamespace
from tram.chu.passkey import thuc_hien
from tram.cli import tao_parser


class TTY(io.StringIO):
    def isatty(self):
        return True


def test_dong_y_va_khong_redirect():
    goi = []
    dv = SimpleNamespace(cap_ma=lambda **kw: goi.append(kw) or 'MA-BI-MAT')
    doi = lambda *a: ([1], [], [])
    for vao, ra, expected in [(TTY('khong\n'), TTY(), 1), (TTY('dong-y\n'), io.StringIO(), 1),
                              (io.StringIO('dong-y\n'), TTY(), 1), (TTY('dong-y\n'), TTY(), 0)]:
        assert thuc_hien(dv, True, vao, ra, doi=doi) == expected
        assert ('MA-BI-MAT' in ra.getvalue()) == (expected == 0)
    assert goi == [{'khoi_phuc': True}]


def test_parser_khong_nhan_ma_argv():
    import pytest
    p = tao_parser()
    for cmd in ('cap-ma','khoi-phuc'):
        assert p.parse_args(['chu','passkey',cmd]).viec_passkey == cmd
        with pytest.raises(SystemExit):
            p.parse_args(['chu','passkey',cmd,'--yes'])
    assert thuc_hien(None,False,TTY('dong-y\n'),TTY(),doi=lambda *a:([],[],[])) == 1
