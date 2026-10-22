"""Migration nhóm riêng máy B (plan siết đọc, mục Migration máy B bước 4). In kế hoạch, chờ dong-y hai lần."""
import json
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from tram.chu import dinh_danh
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao, user_cua_tram, cua_tram
from tram.chu.nhom_rieng import nhom_tram, gid_tram, nhom_phu, lenh_bo_nhom, siet_user, NHOM_NEN
from scripts.siet_nhom_ownership import preflight

users = ('tram-kiem', 'tram-khe1', 'tram-tho')
so, obs = SoCai(), dinh_danh.quan_sat_that
receipt = so.p.with_name('migration-nhom-rieng-20261018.json')


def checkpoint():
    with NamedTemporaryFile(mode='w', dir=receipt.parent, delete=False) as f:
        json.dump(before, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    Path(f.name).replace(receipt)


def before_remove(user, groups):
    before[user]['removed'] = groups
    checkpoint()  # Ghi trước xóa; phục hồi lại membership vốn đã có là an toàn nếu lệnh chưa chạy.


with so.giu():
    doi_soat(so, obs, dinh_danh.khop)
    before = {}
    for u in users:
        ident = user_cua_tram(so, u, obs)
        if ident is None:
            raise SystemExit(f'DỪNG: user {u} không có biên nhận đúng UID/GUID')
        group = obs('nhom', u)
        if group is not None and not cua_tram(so, 'nhom', u, group):
            raise SystemExit(f'DỪNG: nhóm {u} không đúng biên nhận')
        groups = nhom_phu(u)
        removable = {c[-1] for c in lenh_bo_nhom(u, groups)}
        if groups - removable - {u} - NHOM_NEN:
            raise SystemExit(f'DỪNG: {u} có nhóm ngoài danh sách đã duyệt')
        old = subprocess.run(['/usr/bin/id', '-g', u], check=True, capture_output=True,
                             text=True, timeout=30).stdout.strip()
        before[u] = {'identity': ident, 'old_gid': old, 'old_groups': sorted(groups), 'removed': []}
    resources = [nhom_tram(u) for u in users]
    actions = kiem_truoc(so, resources, quan_sat=obs)
    for tn, action in zip(resources, actions):
        print(action, tn.mo_ta())
    if input('Tạo nhóm có sổ — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Chưa thay hệ thống')
    if receipt.exists():
        # Chạy lại sau khi audit dừng: chỉ nhận biên nhận cũ nếu chưa user nào đổi và chưa gỡ nhóm nào.
        cu = json.loads(receipt.read_text())
        for u in users:
            c = cu.get(u) or {}
            if (c.get('identity') != before[u]['identity'] or str(c.get('old_gid')) != before[u]['old_gid']
                    or set(c.get('old_groups', [])) - {u} != set(before[u]['old_groups']) - {u} or c.get('removed')):
                raise SystemExit(f'DỪNG: biên nhận {receipt} khác hiện trạng {u} — báo Em, không ghi đè')
        checkpoint()
    else:
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(before, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
    for tn in resources:
        tao(so, tn, quan_sat=obs)
    # Không đổi quyền file: cùng UID vẫn dùng owner bits. Audit lỗi => user chưa đổi nhóm.
    people = preflight(so, obs)
    for u in users:
        before[u]['new_group'] = people[u]['group']
    checkpoint()
    for u in users:
        print('sudo /usr/bin/dscl . -create', f'/Users/{u}', 'PrimaryGroupID', gid_tram(u, so, obs))
        for cmd in lenh_bo_nhom(u, nhom_phu(u)):
            print(' '.join(cmd), '(chỉ nếu membership còn sau đổi nhóm chính)')
    if input('Đổi nhóm chính và bỏ nhóm thừa — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Giữ nhóm đã tạo có sổ; user chưa đổi')
    for u in users:
        siet_user(u, so, obs, truoc_bo=lambda groups, u=u: before_remove(u, groups))
