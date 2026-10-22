import hashlib
import io
import json
import struct
import pytest
from tram.quan_kiem.giao_thuc import doc, ghi, yeu_cau, fingerprint
from tram.quan_kiem.peer import xac_thuc


def mau():
    return dict(v=1, op='chay', id='a'*32, giao_id='giao-1', luot=1, du_an='repo',
                commit='b'*40, tree='c'*40, policy='d'*64, lenh=['python -m pytest'],
                nguon_n=3, nguon_sha=hashlib.sha256(b'abc').hexdigest(),
                env_n=0, env_sha=hashlib.sha256(b'').hexdigest(), dich='.env.testing')


class Ong:
    def __init__(self, data=b''):
        self.f = io.BytesIO(data)
    def recv(self, n):
        return self.f.read(min(n, 3))
    def sendall(self, data):
        self.f.write(data)
    def settimeout(self, t):
        assert 0 < t <= 30


def test_khung_doc_tung_manh():
    s = Ong()
    ghi(s, mau())
    s.f.seek(0)
    assert yeu_cau(doc(s)) == mau()


@pytest.mark.parametrize('doi', [dict(uid=501), dict(v=True), dict(luot=True), dict(luot=0),
    dict(nguon_n=67108865), dict(lenh=[]), dict(dich='../secret'), dict(id='../a'), dict(op='root')])
def test_tu_choi_du_lieu_sai(doi):
    with pytest.raises(ValueError):
        yeu_cau(mau() | doi)


def test_khoa_json_trung_va_upload_do():
    for raw in [b'{"v":1,"v":1}', b'{']:
        with pytest.raises(ValueError):
            doc(Ong(struct.pack('!I', len(raw)) + raw))
    with pytest.raises(OSError):
        doc(Ong(b'\0\0'))


def test_fingerprint_gan_moi_noi_dung():
    assert fingerprint(mau()) != fingerprint(mau() | {'tree': 'e'*40})


@pytest.mark.parametrize('uid', [0, 503, 504, 502])
def test_peer_gia_khong_tin_uid_client(uid):
    with pytest.raises(PermissionError):
        xac_thuc(object(), 501, lay=lambda s: (uid, 20))


def test_peer_dung():
    xac_thuc(object(), 501, lay=lambda s: (501, 20))


def test_getpeereid_stdlib_socketpair():
    import os
    import socket
    import sys
    from tram.quan_kiem.peer import danh_tinh
    if sys.platform != 'darwin':
        pytest.skip('ABI Darwin')
    a, b = socket.socketpair()
    try:
        assert danh_tinh(a) == (os.geteuid(), os.getegid())
        a.close()
        with pytest.raises(OSError):
            danh_tinh(a)
    finally:
        a.close()
        b.close()
