"""Dùng lại quan sát/thu hồi hiện hành; không cho Uq vào repo hoặc env của trạm."""
import os
import json
import re
from functools import partial
from pathlib import Path

from tram.giao_viec.ban_chep import don_ban
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.cong_that import doc_tep_root, thu_hoi_theo_uid
from tram.giao_viec.launchd_kiem import doc_launchd
from tram.giao_viec.quan_sat_kiem import tien_trinh, tep_ngoai, goc_rong, cron_at
from tram.kiem.kiem_python import kiem_prefix
from tram.kiem.ngoai_le_uid import con_uid
from tram.kiem.bang_tien_trinh import mot_nhan
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, ho_so_tu_manifest


def ho_so(c):
    m, hs = ho_so_tu_manifest(doc_tep_root(MANIFEST_KIEM))
    if m['goc'] != c['goc'] or m['tram_home'] != c['home_tram'] or doc_tep_root(HO_SO_KIEM) != hs:
        raise ValueError('ho-so-khac-ban-cai')


def dung(c, pk, nc, *, quan_sat=True):
    g = Path(c['goc'])
    return CongLuot(Path(c['home']) / 'cong.json', partial(thu_hoi_theo_uid, pk), [
        quan_uq, kiem_prefix, partial(ho_so, c), partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, g),
        partial(goc_rong, g), partial(cron_at, pk),
        partial(doc_launchd, pk, ngu_canh=lambda ten: nc, bang_chung=frozenset({nc}))] if quan_sat else [])


def quan_uq():
    """Worker cũ sau crash không được sống cạnh daemon/lượt mới; không tự kill Uq theo UID."""
    toi, cha, uid = os.getpid(), os.getppid(), os.getuid()
    ds = con_uid(uid, ten='tram-quan-kiem')
    theo = {t.pid: t for t in ds}
    if set(theo) != {toi, cha} or theo[toi].ppid != cha or theo[cha].ppid != 1:
        raise OSError('Uq-con-tien-trinh-ngoai-luot')
    if any(t.uid != uid or t.ruid != uid or mot_nhan(t.pid) != t for t in ds):
        raise OSError('Uq-danh-tinh-da-doi')

def phuc_hoi(c, mode, id_):
    pk = tu_cach_ly('user:tram-kiem')
    ids = [id_]
    if mode == 'mo':
        ids = []
        for p in (Path(c['home']) / 'luot').glob('*.json'):
            d = json.loads(p.read_bytes())
            if d['trang_thai'] in ('dang-chay', 'dong'):
                ids.append(p.stem)
    thu_hoi_theo_uid(pk)
    for i in ids:
        if not re.fullmatch('[a-f0-9]{32}', i):
            raise ValueError('receipt-id-sai')
        wt = Path(c['goc']) / ('luot-' + i)
        don_ban(wt, boc=pk.boc_luot(wt), kill=pk.kill_nhom)
    if mode == 'mo':
        dung(c, pk, ngu_canh_hien_hanh(pk.ten)).mo_lai()
