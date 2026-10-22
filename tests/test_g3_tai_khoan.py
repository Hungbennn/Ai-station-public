"""Lệnh dscl/visudo/id và API D162 đều giả; chỉ file trong thư mục tạm được ghi thật."""
import importlib.util
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.g3

PATH = Path(__file__).resolve().parents[1] / 'cong-cu/g3-tai-khoan.py'
spec = importlib.util.spec_from_file_location('g3_tk', PATH)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


@pytest.fixture(autouse=True)
def gia_d162(monkeypatch):
    monkeypatch.setattr('tram.kiem.ngoai_le_uid.con_uid', lambda *a, **kw: [])


class Gia:
    def __init__(self):
        self.rows = {'/Users/root': {'UniqueID':'0', 'PrimaryGroupID':'0'},
                     '/Users/dai-ca': {'UniqueID':'501', 'PrimaryGroupID':'20'},
                     '/Users/tram-kiem': {'UniqueID':'503', 'PrimaryGroupID':'20'},
                     '/Users/khac': {'UniqueID':'505', 'PrimaryGroupID':'505'},
                     '/Groups/staff': {'PrimaryGroupID':'20'},
                     '/Groups/khac': {'PrimaryGroupID':'505'}}
        self.calls = []; self.ps = '501 501'; self.fail = None

    def __call__(self, *args):
        self.calls.append(args)
        name = Path(args[0]).name; a = args[1:]
        if self.fail and self.fail in a: raise RuntimeError('loi gia')
        if name == 'id':
            if a == ('-u', 'tram-kiem'): return '503'
            return self.rows['/Users/'+m.TEN]['PrimaryGroupID']
        if name == 'ps': return self.ps
        if name == 'visudo':
            if a[0] == '-cf':
                text = Path(a[1]).read_text()
                assert m.RULE in text and '(root)' not in text and '(ALL)' not in text
            return ''
        assert name == 'dscl' and a[0] == '.'
        cmd, path = a[1:3]
        if cmd == '-list':
            attr = a[3]
            return '\n'.join(p.split('/')[-1]+' '+v.get(attr,'') for p,v in self.rows.items() if p.startswith(path+'/'))
        if cmd == '-create': self.rows.setdefault(path, {})[a[3]] = a[4]; return ''
        if cmd == '-read':
            if len(a) == 3: return '\n'.join(k+': '+v for k,v in self.rows[path].items())
            tien_to = 'dsAttrTypeNative:' if a[3] == 'IsHidden' else ''  # đúng như dscl thật 24G90
            return tien_to+a[3]+': '+self.rows[path][a[3]]
        if cmd == '-delete': del self.rows[path]; return ''
        raise AssertionError(args)


def setup(tmp_path):
    g = Gia(); root = tmp_path/'ledger'; root.mkdir(mode=0o700)
    return m.CaiGo(root, tmp_path/'sudoers', g), g


def test_cai_go_chi_runas_kiem_uid_gid_tu_chon_va_giu_receipt(tmp_path):
    c,g = setup(tmp_path); s = c.ke_hoach()
    assert s['uid'] == 506 and s['gid'] == 506
    old = os.umask(0o077)
    try: c.cai(s)
    finally: os.umask(old)
    assert c.doc()['complete'] and c.rule.stat().st_mode & 0o777 == 0o440
    assert g.rows['/Users/'+m.TEN]['UserShell'] == '/usr/bin/false'
    c.go(c.doc())
    assert not c.rule.exists() and c.doc()['uninstalled']
    assert not any(p.endswith('/'+m.TEN) for p in g.rows)
    assert [a[-1] for a in g.calls if '-delete' in a] == ['/Users/'+m.TEN, '/Groups/'+m.TEN]


@pytest.mark.parametrize('what', ['user', 'group', 'rule', 'symlink'])
def test_khong_nhan_so_huu_thu_co_san(tmp_path, what):
    c,g = setup(tmp_path)
    if what == 'user': g.rows['/Users/'+m.TEN] = {'UniqueID':'519'}
    elif what == 'group': g.rows['/Groups/'+m.TEN] = {'PrimaryGroupID':'519'}
    elif what == 'rule': c.rule.write_text('co san')
    else: c.rule.symlink_to(tmp_path/'vang')
    with pytest.raises(RuntimeError): c.ke_hoach()
    assert not any('-create' in a or '-delete' in a for a in g.calls)


@pytest.mark.parametrize('what', ['uid', 'uuid', 'sudoers', 'process', 'group-member'])
def test_tu_choi_go_khi_lech_chung_cu(tmp_path, what, monkeypatch):
    c,g = setup(tmp_path); c.cai(c.ke_hoach()); before = len(g.calls)
    if what == 'uid': g.rows['/Users/'+m.TEN]['UniqueID'] = '999'
    elif what == 'uuid': g.rows['/Users/'+m.TEN]['GeneratedUID'] = 'uuid-khac'
    elif what == 'sudoers': c.rule.chmod(0o600); c.rule.write_text('khac')
    elif what == 'group-member': g.rows['/Groups/'+m.TEN]['GroupMembership'] = 'hungle'
    else: monkeypatch.setattr('tram.kiem.ngoai_le_uid.con_uid', lambda *a, **kw: [object()])
    with pytest.raises(RuntimeError): c.go(c.doc())
    assert c.rule.exists() and not any('-delete' in a for a in g.calls[before:])


def test_loi_giua_cai_giu_receipt_khong_xoa_record_mo_ho(tmp_path):
    c,g = setup(tmp_path); g.fail = 'GeneratedUID'
    with pytest.raises(RuntimeError): c.cai(c.ke_hoach())
    s = c.doc(); assert s['todo'] == ['Groups'] and s['made'] == []
    with pytest.raises(RuntimeError, match='mutation dở'): c.go(s)
    assert not any('-delete' in a for a in g.calls)
    s['made'] = ['Groups']; s['todo'] = []
    with pytest.raises(RuntimeError, match='receipt'): c.go(s)
    assert '/Groups/'+m.TEN in g.rows


def test_receipt_symlink_khong_theo(tmp_path):
    c,g = setup(tmp_path); target = tmp_path/'target'; target.write_text('{}')
    c.rc.symlink_to(target)
    with pytest.raises(RuntimeError): c.doc()
    assert target.read_text() == '{}'


def test_id_bi_chiem_sau_luc_in_ke_hoach_khong_tao(tmp_path):
    c,g = setup(tmp_path); s = c.ke_hoach()
    g.rows['/Users/nguoi-khac'] = {'UniqueID':str(s['uid']), 'PrimaryGroupID':'20'}
    with pytest.raises(RuntimeError, match='ID đã bị chiếm'): c.cai(s)
    assert not any('-create' in a for a in g.calls)


def test_nhom_member_nhieu_dong_khong_go(tmp_path):
    c,g = setup(tmp_path); c.cai(c.ke_hoach())
    g.rows['/Groups/'+m.TEN]['GroupMembers'] = '\n UUID-cua-nguoi-khac'
    with pytest.raises(RuntimeError, match='nhóm có thành viên'): c.go(c.doc())
    assert c.rule.exists()


@pytest.mark.parametrize('attr,value', [('Password','********'), ('IsHidden','0')])
def test_tai_khoan_bat_dau_dung_cho_viec_khac_khong_go(tmp_path, attr, value):
    c,g = setup(tmp_path); c.cai(c.ke_hoach())
    g.rows['/Users/'+m.TEN][attr] = value
    with pytest.raises(RuntimeError, match='danh tính/nhóm'): c.go(c.doc())
    assert c.rule.exists()


def test_builtin_nobody_id_am_khong_chan_chon_id(tmp_path):
    c,g = setup(tmp_path)
    g.rows['/Users/nobody'] = {'UniqueID':'-2', 'PrimaryGroupID':'-2'}
    g.rows['/Groups/nobody'] = {'PrimaryGroupID':'-2'}
    c.cai(c.ke_hoach()); c.go(c.doc())
    assert c.doc()['uninstalled'] and '/Users/nobody' in g.rows
