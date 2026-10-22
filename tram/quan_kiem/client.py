"""Trạm gọi Uq; mất kênh không rơi về sudo từ 501. ID ổn định qua retry."""
import select
import socket
import sys
import time
from pathlib import Path

from tram.giao_viec.kiem_lai import KetQuaKiemLai
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cay_kiem import cay_goc
from tram.kiem.diff import diff_cham_cam
from tram.quan_kiem.cau_hinh import nap
from tram.quan_kiem.giao_thuc import digest_policy, ghi, doc, bam, fingerprint, HAN_LUOT, yeu_cau
from tram.quan_kiem.nguon import archive, moi_truong
from tram.quan_kiem.peer import duong_socket, xac_thuc


def gui(d, nguon=b'', env=b'', *, cau_hinh=nap):
    c = cau_hinh()
    p = Path(c['socket'])
    duong_socket(p, c['uid_quan'], c['gid_socket'])
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect(str(p))
            xac_thuc(s, c['uid_quan'])
            ghi(s, d)
            s.sendall(nguon)
            s.sendall(env)
            het = time.monotonic() + HAN_LUOT + 300
            while not select.select([s], [], [], 0.2)[0]:
                from tram.duong_dan import tram_home
                if time.monotonic() >= het or (d['op'] == 'chay' and (tram_home() / 'estop').exists()):
                    raise TimeoutError('estop-hoac-het-han')
            return doc(s, het=het)
    except (OSError, ValueError):
        raise LoiBanChep('bo-quan-ly-khong-tra-ket-qua-hop-le') from None


class CongTuXa:
    def trang_thai(self):
        r = gui({'v': 1, 'op': 'trang-thai', 'id': '0'*32})
        return {'trang_thai': r.get('cong', 'dong')}

    def mo_lai(self):
        if gui({'v': 1, 'op': 'mo', 'id': '0'*32}) != {'cong': 'mo'}:
            raise LoiBanChep('cong-van-dong')


def kiem_tu_xa(kho_git, du_an, *, giao_id, luot, commit, lenh_kiem, lenh_cho_phep, chay_lenh,
                them_cam=(), goi=gui, cau_hinh=nap, **kw):
    cham = diff_cham_cam(kho_git, f'origin/{du_an.nhanh_chinh}', commit,
                        them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                        cho_phep=du_an.giao.duong_dan_cam_cho_phep)
    if cham:
        return KetQuaKiemLai(False, cham_cam=tuple(cham), loi='dong-file-cau-hinh')
    if not chay_lenh:
        return KetQuaKiemLai(True)
    if du_an.moi_truong_kiem is None:
        return KetQuaKiemLai(False, loi='thieu-moi-truong-kiem')
    nguon, env = archive(kho_git, commit), moi_truong(kho_git, commit, du_an.moi_truong_kiem)
    deps = cau_hinh()['policy'].get(du_an.ten, {}).get('deps')
    d = yeu_cau(dict(v=1, op='chay', id=bam(f'{giao_id}/{luot}/{commit}'.encode())[:32],
        giao_id=giao_id, luot=luot, du_an=du_an.ten, commit=commit, tree=cay_goc(kho_git, commit),
        policy=digest_policy(lenh_cho_phep, du_an.giao.lenh_kiem_mac_dinh, deps), lenh=lenh_kiem,
        nguon_n=len(nguon), nguon_sha=bam(nguon),
        env_n=len(env), env_sha=bam(env), dich=du_an.moi_truong_kiem.dich))
    r = goi(d, nguon, env)
    if r.get('ly_do'):      # chỉ in cho người vận hành; không đưa vào kết quả hay prompt
        print(f"bộ quản lý kiểm báo: {str(r['ly_do'])[:600]}", file=sys.stderr)
    if r.get('trang_thai') != 'xong' or r.get('da_thu_hoi') is not True or any(
            r.get(k) != d[k] for k in ('id', 'giao_id', 'luot', 'commit')) or r.get('fingerprint') != fingerprint(d):
        raise LoiBanChep('ket-qua-khong-khop-luot')
    k = r['ket_qua']
    if type(k.get('dat')) is not bool or not isinstance(k.get('ket_qua'), list):
        raise LoiBanChep('ket-qua-sai-dang')
    return KetQuaKiemLai(k['dat'], tuple(k['ket_qua']))
