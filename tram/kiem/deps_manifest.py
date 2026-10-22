"""Manifest bundle chốt: chỉ stdlib; không import hoặc chạy mã trong site-packages."""
import hashlib
import json
import platform
import re
import sys
import sysconfig
from pathlib import Path

KHOA_NGUON = ('uv.lock', 'pyproject.toml', 'frontend/package-lock.json', 'frontend/package.json')
ARCHIVES = ('python-site.tar', 'node-modules.tar')
TRAN_BYTE = 1024**3
TRAN_ENTRY = 100000
TRAN_TAR = TRAN_BYTE + 4096 * TRAN_ENTRY


def bam(b):
    return hashlib.sha256(b).hexdigest()


def chuan(m):
    return json.dumps(m, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def ma_bundle(m):
    return bam(chuan(m))


def doc_manifest(b):
    def cap(ds):
        if len(dict(ds)) != len(ds):
            raise ValueError('deps-khoa-trung')
        return dict(ds)
    return kiem_manifest(json.loads(b, object_pairs_hook=cap))


def nen_tang():
    p = Path(sys.base_prefix).resolve()
    return {'python': str(p), 'build': (p / 'BUILD').read_text().strip() if (p / 'BUILD').is_file() else '',
            'version': platform.python_version(), 'abi': sysconfig.get_config_var('SOABI'),
            'macos': platform.mac_ver()[0], 'arch': platform.machine()}


def kiem_manifest(m):
    from tram.kiem.toolchain import PYTHON
    keys = {'v', 'du_an', 'commit', 'nguon', 'runtime', 'cong_cu', 'python_groups', 'npm_flags', 'artifacts'}
    if not isinstance(m, dict) or set(m) != keys or type(m['v']) is not int or m['v'] != 1:
        raise ValueError('deps-manifest-sai')
    if m['du_an'] != 'ben-station' or not isinstance(m['commit'], str) or not re.fullmatch('[a-f0-9]{40}', m['commit']):
        raise ValueError('deps-du-an-commit-sai')
    if not isinstance(m['nguon'], dict) or set(m['nguon']) != set(KHOA_NGUON) or any(
            not isinstance(v, str) or not re.fullmatch('[a-f0-9]{64}', v) for v in m['nguon'].values()):
        raise ValueError('deps-nguon-sai')
    r = m['runtime']
    if not isinstance(r, dict) or set(r) != {'python', 'build', 'version', 'abi', 'macos', 'arch'} or any(
            not isinstance(v, str) or not 0 < len(v) < 200 for v in r.values()):
        raise ValueError('deps-runtime-sai')
    if (r['python'], r['build'], r['version'], r['arch']) != (PYTHON, '20261009', '3.12.15', 'arm64'):
        raise ValueError('deps-khac-pin')
    c = m['cong_cu']
    if not isinstance(c, dict) or set(c) != {'uv', 'node', 'npm'} or any(
            not isinstance(v, str) or not re.fullmatch(r'\d+\.\d+\.\d+', v) for v in c.values()) or \
            c['uv'] != '0.13.0' or c['node'] != '26.5.0':
        raise ValueError('deps-cong-cu-sai')
    if m['python_groups'] != ['dev'] or m['npm_flags'] != [
            '--ignore-scripts', '--include=dev', '--no-audit', '--no-fund']:
        raise ValueError('deps-tuy-chon-sai')
    if not isinstance(m['artifacts'], dict) or set(m['artifacts']) != set(ARCHIVES):
        raise ValueError('deps-artifacts-sai')
    for a in m['artifacts'].values():
        if not isinstance(a, dict) or set(a) != {'sha256', 'size', 'bytes', 'entries'} or \
                not isinstance(a['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', a['sha256']):
            raise ValueError('deps-artifact-sai')
        for k, tran in (('size', TRAN_TAR), ('bytes', TRAN_BYTE), ('entries', TRAN_ENTRY)):
            if type(a[k]) is not int or not 0 < a[k] <= tran:
                raise ValueError('deps-vuot-tran')
    if sum(a['bytes'] for a in m['artifacts'].values()) > TRAN_BYTE or sum(
            a['entries'] for a in m['artifacts'].values()) > TRAN_ENTRY:
        raise ValueError('deps-tong-vuot-tran')
    return m
