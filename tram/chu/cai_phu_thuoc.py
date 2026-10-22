"""Cài bytes bundle bằng sổ R2 có sẵn; đích theo hash bất biến, không sửa tại chỗ."""
import json
import os
import stat
import subprocess
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_kiem import tep_root
from tram.chu.so_cai_tho import doi_soat
from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, tao
from tram.duong_dan import tram_home
from tram.kiem.deps_manifest import ARCHIVES, bam, doc_manifest
from tram.kiem.deps_root import doc_bundle, duong_manifest


def doc_goi(p, tran):
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        st = os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_size > tran:
            raise ValueError('deps-tep-goi-qua-lon-hoac-sai-loai')
        b = f.read(tran + 1)
    if len(b) > tran:
        raise ValueError('deps-tep-goi-qua-lon')
    return b


def lap_cai(goi, so, *, quan_sat=dinh_danh.quan_sat_that, chay=subprocess.run):
    mf = doc_goi(goi / 'manifest.json', 65536)
    m = doc_manifest(mf)
    from tram.chu.soan_phu_thuoc import do_cong_cu
    # Chỉ kiểm nền tảng ở bước thực thi; lập kế hoạch không chạy gói hay sudo.
    dich, soan = duong_manifest(m), tram_home() / 'cai-deps' / duong_manifest(m).parent.name
    tep = {soan / n: doc_goi(goi / n, m['artifacts'][n]['size']) for n in ARCHIVES}
    tep[soan / 'manifest.json'] = mf
    for name in ARCHIVES:
        a, b = m['artifacts'][name], tep[soan / name]
        if len(b) != a['size'] or bam(b) != a['sha256']:
            raise ValueError('deps-goi-hash-sai')
    ds = [TaiNguyen('thu_muc', str(p), lambda i, p=p: [
        ['sudo', 'install', '-d', '-o', 'root', '-g', 'wheel', '-m', '0755', str(p)]], lambda i: {'uid': 0})
        for p in reversed((dich.parent, *[q for q in dich.parent.parents if q.is_relative_to('/usr/local/tram')]))]
    ds += [tep_root(p, dich.parent / p.name, b, '0644') for p, b in tep.items()]
    def bat_bien():
        for tn in ds:
            hien = quan_sat(tn.kieu, tn.ten)
            if hien is not None and (hien.get('uid') != 0 or tn.kieu == 'tep' and
                                     hien.get('sha256') != tn.mong('')['sha256']):
                raise ValueError('deps-dich-da-co-khac-dinh-danh')
            if hien is not None and quan_sat is dinh_danh.quan_sat_that:
                from tram.kiem.deps_root import khong_acl
                p = Path(tn.ten)
                st = p.lstat()
                mode = 0o644 if tn.kieu == 'tep' else 0o755
                if p.is_symlink() or st.st_gid != 0 or st.st_mode & 0o7777 != mode:
                    raise ValueError('deps-dich-khong-kin')
                khong_acl(p)
    bat_bien()
    viec = kiem_truoc(so, ds, quan_sat=quan_sat)
    def nen():
        r, c = do_cong_cu()
        if r != m['runtime'] or c != m['cong_cu']:
            raise ValueError('deps-nen-tang-cong-cu-khac')
    def xong():
        if quan_sat is dinh_danh.quan_sat_that:
            doc_bundle(dich)
    buoc = [('Kiểm nền tảng/công cụ', nen),
            ('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop)),
            ('Từ chối đích khác bytes/chủ/quyền', bat_bien)]
    buoc += [(f'[{v}] {tn.kieu} {tn.ten}: {tn.mo_ta()}',
              lambda tn=tn: tao(so, tn, quan_sat=quan_sat,
                               chay=lambda a, **kw: chay(a, timeout=120, **kw))) for tn, v in zip(ds, viec)]
    buoc.append(('Kiểm bytes/quyền root sau cài', xong))
    return KeHoach(tep, [], [f'DEPS_MANIFEST={dich}', json.dumps(m, ensure_ascii=False),
                            'Chỉ cài bytes sau dong-y; lỗi giữ phần đã tạo trong sổ R2.'], buoc)
