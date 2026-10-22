"""C1: bộ lọc có trần trước mọi ghi đĩa; test thuần, không thay thế kiểm vòng đời OS."""
from tram.deploy.ong import DONG_CHE, Loc, TRAN_DONG, TRAN_LOG


def test_token_tach_goi_khong_ghi_truoc_khi_che():
    ghi = []
    loc = Loc(ghi.append)
    token = b"ghp_" + b"A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    loc.nhan(token[:20])
    assert ghi == []
    loc.nhan(token[20:] + b"\n")
    assert b"".join(ghi).decode().strip() == DONG_CHE
    assert token not in b"".join(ghi)


def test_dong_va_log_co_tran():
    ghi = []
    loc = Loc(ghi.append)
    for _ in range(500):
        loc.nhan(b"x" * 8192)
        assert len(loc.do) <= TRAN_DONG
    loc.nhan(b"\n")
    assert "bỏ một dòng dài quá" in b"".join(ghi).decode()
    for _ in range(100000):
        loc.nhan(b"dong binh thuong\n")
    loc.xong()
    assert loc.cat > 0 and sum(map(len, ghi)) <= TRAN_LOG
