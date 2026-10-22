import importlib.util
from pathlib import Path
import pytest


def module():
    spec = importlib.util.spec_from_file_location('migration', Path(__file__).parents[1] / 'scripts/siet_nhom_ownership.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_owner_acl_symlink_chan_truoc_lenh(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir()
    uid = p.stat().st_uid
    with pytest.raises(ValueError, match='owner'):
        m.audit(p, uid + 1, 701, acl=lambda p: False)
    with pytest.raises(ValueError, match='ACL'):
        m.audit(p, uid, 701, acl=lambda p: True)
    link = p / 'link'; link.symlink_to('/Users/dai-ca')
    with pytest.raises(ValueError, match='symlink'):
        m.audit(p, uid, 701, acl=lambda p: False)


def test_staff_only_exact_paths_and_snapshot(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir(); (p / 'file').write_text('fake')
    uid, gid = p.stat().st_uid, p.stat().st_gid
    rows = m.audit(p, uid, 701, staff_gid=gid, acl=lambda p: False)
    assert {r['path'] for r in rows} == {str(p), str(p / 'file')}
    assert all(r['old_gid'] == gid and r['uid'] == uid and r['new_gid'] == 701 for r in rows)
    assert not hasattr(m, 'command')  # Không sinh chown cho file vẫn thuộc cùng UID.


def test_walk_loi_khong_duoc_bo_qua(tmp_path, monkeypatch):
    m = module()
    p = tmp_path / 'owned'; p.mkdir()
    def walk(root, **kw):
        kw['onerror'](PermissionError('không đọc được thư mục con'))
        return []
    monkeypatch.setattr(m.os, 'walk', walk)
    with pytest.raises(PermissionError):
        m.audit(p, p.stat().st_uid, 701, acl=lambda p: False)


def test_audit_khong_doi_quyen(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir(); (p / 'config').write_text('fake')
    before = [(x.stat().st_uid, x.stat().st_gid, x.stat().st_mode) for x in (p, p / 'config')]
    m.audit(p, p.stat().st_uid, 701, acl=lambda p: False)
    assert before == [(x.stat().st_uid, x.stat().st_gid, x.stat().st_mode) for x in (p, p / 'config')]


def test_chan_worker_plist_chua_offline_no_sync(tmp_path):
    m = module()
    with pytest.raises(ValueError):
        m.kiem_duong_chay({'ProgramArguments': ['uv', '--project', str(tmp_path / 'repo')],
                          'WorkingDirectory': str(tmp_path)}, tmp_path)


@pytest.mark.parametrize('removed', [[], ['staff', 'com.apple.sharepoint.group.7'],
                                   ['everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator']])
def test_rollback_nhom_do_dang_khong_can_snapshot_ownership(tmp_path, monkeypatch, removed):
    import contextlib
    import json
    import sys
    from types import SimpleNamespace
    from tram.chu import so_cai_tho
    m = module()
    people = {u: {'user': {'uid': i + 502, 'guid': u}, 'group': {'gid': i + 701, 'guid': u}}
              for i, u in enumerate(m.USERS)}
    background = ['everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator']
    restored = sorted(set(removed) - set(background))
    old_groups = set(background + ['staff'] + restored)
    before = {u: {'identity': p['user'], 'new_group': p['group'], 'old_gid': '20',
                  'old_groups': sorted(old_groups), 'removed': removed} for u, p in people.items()}
    snapshot = tmp_path / 'identity.json'; snapshot.write_text(json.dumps(before))
    monkeypatch.setattr(sys, 'argv', ['migration', 'rollback', '--identity-snapshot', str(snapshot)])
    monkeypatch.setattr(so_cai_tho, 'SoCai', lambda: SimpleNamespace(giu=contextlib.nullcontext))
    monkeypatch.setattr(m, 'identities', lambda *a: people)
    seen = []
    monkeypatch.setattr(m, 'confirm', lambda cmds: seen.extend(cmds))
    monkeypatch.setattr(m.subprocess, 'run', lambda *a, **k: None)
    monkeypatch.setattr(m, 'run', lambda c: SimpleNamespace(stdout='20' if '-g' in c else ' '.join(old_groups)))
    m.main()
    assert len(seen) == 3 * (1 + len(restored))
    assert all(c[-2:] == ['PrimaryGroupID', '20'] for c in seen if '-a' not in c)
    assert [c[-1] for c in seen if '-a' in c] == restored * 3
    # Snapshot cũ kê nhầm nhóm lồng cũng không được thêm membership trực tiếp cho user.
    assert not any(c[-1] in background for c in seen if '-a' in c)


def test_acl_doc_ca_khi_co_xattr_va_chi_cho_qua_ace_vo_hai(monkeypatch):
    from types import SimpleNamespace
    m = module()
    out = ('drwxr-x---@ 11 tram-khe1  staff  352 Oct 18 08:32 /Users/tram-khe1\n'
           ' 0: group:everyone deny delete\n 1: user:tram-khe1 allow list,search,file_inherit\n')
    monkeypatch.setattr(m, 'run', lambda c: SimpleNamespace(stdout=out))
    assert m.acl_cua('/x') == ['group:everyone deny delete', 'user:tram-khe1 allow list,search,file_inherit']
    assert m.acl_la('tram-khe1')('/x') is False
    assert m.acl_la('tram-tho')('/x') is True  # ACE cấp cho người khác => dừng
    for ace in ('group:staff allow read', 'group:everyone allow list', 'user:hungle allow search'):
        assert not m.acl_vo_hai(ace, 'tram-khe1')
    monkeypatch.setattr(m, 'run', lambda c: SimpleNamespace(stdout='-rw-------  1 a  staff  3 Oct 18 x\n'))
    assert m.acl_cua('/x') == []


def test_bo_qua_ben_trong_library_nhung_van_kiem_noi_khac(tmp_path):
    m = module()
    p = tmp_path / 'nha'; (p / 'Library' / 'Containers').mkdir(parents=True)
    (p / 'Library' / 'Containers' / 'Music').symlink_to('../../Music')
    uid = p.stat().st_uid
    rows = m.audit(p, uid, 701, staff_gid=p.stat().st_gid, acl=lambda x: False)
    assert str(p / 'Library') in {r['path'] for r in rows}  # chính Library vẫn được kiểm
    assert not any('Containers' in r['path'] for r in rows)
    (p / 'Desktop').mkdir(); (p / 'Desktop' / 'link').symlink_to('/Users/dai-ca')
    with pytest.raises(ValueError, match='symlink'):
        m.audit(p, uid, 701, acl=lambda x: False)
    (p / 'Desktop' / 'link').unlink(); (p / 'Desktop' / 'Library').mkdir()
    (p / 'Desktop' / 'Library' / 'link').symlink_to('/Users/dai-ca')  # chỉ bỏ Library ở gốc nhà
    with pytest.raises(ValueError, match='symlink'):
        m.audit(p, uid, 701, acl=lambda x: False)


def test_audit_duoi_chay_duoi_uid_chu_va_ma_that_chay_duoc(tmp_path):
    import subprocess
    import sys
    m = module()
    p = tmp_path / 'nha'; p.mkdir(); (p / 'f').write_text('x')
    st = p.stat()
    seen = {}

    def chay(cmd, **kw):
        seen['cmd'], seen['kw'] = cmd, kw
        # Bỏ tiền tố sudo/env, chạy đúng mã con bằng Python hiện tại — kiểm cơ chế exec thật.
        return subprocess.run([sys.executable, *cmd[cmd.index('-I'):]], **kw)
    rows = m.audit_duoi('tram-khe1', p, st.st_uid, 701, chay=chay)
    assert seen['cmd'][:4] == ['sudo', '-u', 'tram-khe1', '--'] and seen['kw']['cwd'] == '/'
    assert 'def audit' in seen['kw']['input']
    assert isinstance(rows, list)
    with pytest.raises(ValueError, match='không đạt'):
        m.audit_duoi('tram-khe1', p, st.st_uid + 1, 701, chay=chay)
