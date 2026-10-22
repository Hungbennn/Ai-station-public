"""Chụp cấu hình dự án đã được trạm đọc; không có mặc định cho phép mọi lệnh."""
import re
from tram.cau_hinh.lenh import khop_bat_ky, kiem_mau


def kiem_policy(policy):
    if not isinstance(policy, dict) or not policy:
        raise ValueError('thieu-policy-du-an')
    for ten, p in policy.items():
        if not isinstance(ten, str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}', ten):
            raise ValueError('ten-policy-sai')
        if not isinstance(p, dict) or set(p) not in ({'mac_dinh', 'cho_phep'}, {'mac_dinh', 'cho_phep', 'deps'}):
            raise ValueError('policy-sai')
        if 'deps' in p:
            from tram.kiem.deps_manifest import kiem_manifest
            if kiem_manifest(p['deps'])['du_an'] != ten:
                raise ValueError('deps-khac-du-an')
        for k in ('mac_dinh', 'cho_phep'):
            if not isinstance(p[k], list) or not p[k] or any(
                    not isinstance(x, str) or not 0 < len(x) <= 1024 for x in p[k]):
                raise ValueError('lenh-policy-sai')
        if len(p['mac_dinh']) > 20 or any(kiem_mau(x) for x in p['cho_phep']) or any(
                not khop_bat_ky(x, p['cho_phep']) for x in p['mac_dinh']):
            raise ValueError('policy-khong-khop')
    return policy


def chup_policy(thu_muc=None):
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    policy = {}
    for ten in liet_ke_du_an(thu_muc):
        da = nap_du_an(ten, thu_muc=thu_muc)
        if da.giao.lenh_kiem_mac_dinh:
            policy[ten] = {'mac_dinh': list(da.giao.lenh_kiem_mac_dinh),
                           'cho_phep': list(da.lenh_cho_phep)}
    return kiem_policy(policy)
