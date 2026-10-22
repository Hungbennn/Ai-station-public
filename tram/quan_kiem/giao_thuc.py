"""Khung JSON 64 KiB, byte nguồn riêng; thời hạn tuyệt đối, không pickle/shell/đường dẫn client."""
import hashlib
import json
import re
import struct
import time

from tram.kiem.moi_truong import loi_dich

KHUNG = 65536
NGUON = 64 * 1024 * 1024
ENV = 1024 * 1024
HAN_DOC = 30
HAN_LUOT = 3600
KHOA = {'v', 'op', 'id', 'giao_id', 'luot', 'du_an', 'commit', 'tree', 'policy', 'lenh',
        'nguon_n', 'nguon_sha', 'env_n', 'env_sha', 'dich'}


def bam(b):
    return hashlib.sha256(b).hexdigest()


def json_bytes(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def fingerprint(d):
    return bam(json_bytes(d))


def nhan(s, n, het):
    ra = bytearray()
    while len(ra) < n:
        con = het - time.monotonic()
        if con <= 0:
            raise TimeoutError('het-han-doc')
        s.settimeout(min(HAN_DOC, con))
        k = s.recv(min(n - len(ra), 65536))
        if not k:
            raise OSError('upload-do')
        ra.extend(k)
    return bytes(ra)


def _cap(cap):
    if len(dict(cap)) != len(cap):
        raise ValueError('khoa-trung')
    return dict(cap)


def doc(s, *, het=None):
    het = time.monotonic() + HAN_DOC if het is None else het
    n, = struct.unpack('!I', nhan(s, 4, het))
    if not 0 < n <= KHUNG:
        raise ValueError('khung-qua-lon')
    try:
        return json.loads(nhan(s, n, het), object_pairs_hook=_cap)
    except (UnicodeError, ValueError):
        raise ValueError('json-sai') from None


def ghi(s, d):
    b = json_bytes(d)
    if len(b) > KHUNG:
        raise ValueError('khung-qua-lon')
    s.settimeout(HAN_DOC)
    s.sendall(struct.pack('!I', len(b)) + b)


def yeu_cau(d):
    if not isinstance(d, dict) or type(d.get('v')) is not int or d['v'] != 1:
        raise ValueError('phien-ban-sai')
    if d.get('op') in ('trang-thai', 'huy', 'mo'):
        if set(d) != {'v', 'op', 'id'}:
            raise ValueError('khoa-sai')
    elif d.get('op') != 'chay' or set(d) != KHOA:
        raise ValueError('khoa-sai')
    if not isinstance(d.get('id'), str) or not re.fullmatch('[a-f0-9]{32}', d['id']):
        raise ValueError('id-sai')
    if d['op'] != 'chay':
        return d
    for k in ('giao_id', 'du_an'):
        if not isinstance(d[k], str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}', d[k]):
            raise ValueError('danh-tinh-sai')
    for k in ('commit', 'tree', 'policy', 'nguon_sha', 'env_sha'):
        n = 40 if k in ('commit', 'tree') else 64
        if not isinstance(d[k], str) or not re.fullmatch('[a-f0-9]{%d}' % n, d[k]):
            raise ValueError('digest-sai')
    if type(d['luot']) is not int or not 1 <= d['luot'] <= 2**53:
        raise ValueError('luot-sai')
    for k, tran in (('nguon_n', NGUON), ('env_n', ENV)):
        if type(d[k]) is not int or not 0 <= d[k] <= tran:
            raise ValueError('do-dai-sai')
    if not isinstance(d['lenh'], list) or not 1 <= len(d['lenh']) <= 20 or any(
            not isinstance(x, str) or not 0 < len(x) <= 1024 for x in d['lenh']):
        raise ValueError('lenh-sai')
    if loi_dich(d['dich']):
        raise ValueError('dich-sai')
    return d


def digest_policy(lenh, mac_dinh=(), deps=None):
    from tram.kiem.toolchain import manifest
    from tram.tho.quyen_kiem import PHIEN_BAN_HO_SO
    return fingerprint({'lenh': lenh, 'mac_dinh': list(mac_dinh), 'toolchain': manifest(),
                        'ho_so': PHIEN_BAN_HO_SO, 'deps': deps})
