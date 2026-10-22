from types import SimpleNamespace
import pytest
from tram.chu import dinh_danh
from tram.chu.so_cai_tho import SoCai, Muc
from tram.chu.tai_nguyen import tao, kiem_truoc, LoiCaiDat
from tram.chu.go_cai_dat_tho import go, _thu_tu, lenh_go


def test_doc_nhom_va_danh_tinh():
    seen = []
    def run(cmd, **kw):
        seen.append(cmd)
        return SimpleNamespace(returncode=0, stdout='PrimaryGroupID: 701\nGeneratedUID: G\nRealName: tram g i\n')
    result = dinh_danh.nhom('tram-kiem', chay=run)
    assert result == {'gid': 701, 'guid': 'G', 'ten_day_du': 'tram g i'}
    assert seen[0][3] == '/Groups/tram-kiem'
    assert dinh_danh.khop('nhom', result, result)
    assert dinh_danh.cung('nhom', result, result)
    assert not dinh_danh.cung('nhom', result, {**result, 'guid': 'foreign'})


def test_nhom_co_so_cai_va_cai_lai(tmp_path):
    from tram.chu.nhom_rieng import nhom_tram
    so, state, calls = SoCai(tmp_path / 'so'), {}, []
    def observe(k, n, **kw):
        return state.get((k, n))
    def run(cmd, **kw):
        calls.append(cmd)
        marker = cmd[cmd.index('-r') + 1]
        state['nhom', 'tram-kiem'] = {'gid': 701, 'guid': 'G', 'ten_day_du': marker}
    tn = nhom_tram('tram-kiem')
    assert tao(so, tn, quan_sat=observe, chay=run) == 'tao'
    assert tao(so, tn, quan_sat=observe, chay=run) == 'giu'
    assert len(calls) == 1
    assert so.da_tao('nhom', 'tram-kiem')[0].dinh_danh['gid'] == 701
    state['nhom', 'tram-kiem']['guid'] = 'foreign'
    with pytest.raises(LoiCaiDat):
        tao(so, tn, quan_sat=observe, chay=run)
    assert len(calls) == 1


def test_go_nhom_sau_user_khong_go_nhom_la(tmp_path):
    so = SoCai(tmp_path / 'so')
    identity = {'gid': 701, 'guid': 'G'}
    so.du_dinh('i', 'nhom', 'tram-kiem', {'user': 'tram-kiem'})
    so.ket('i', 'da_tao', dinh_danh=identity)
    m = so.da_tao('nhom', 'tram-kiem')[0]
    assert _thu_tu(m) > _thu_tu(Muc('u', 'user', 'tram-kiem', {}))
    calls = []
    assert not go(so, m, quan_sat=lambda k,n: identity, chay=lambda *a,**k: calls.append(a), bao=lambda s: None)
    assert not calls
    assert not go(so, m, quan_sat=lambda k,n: {**identity, 'guid': 'foreign'},
                  chay=lambda *a,**k: calls.append(a), bao=lambda s: None)
    assert not calls
    assert lenh_go(m) == [['sudo', '/usr/sbin/dseditgroup', '-o', 'delete', 'tram-kiem']]


def test_user_gid_va_bo_nhom_thua(tmp_path):
    from tram.chu.nhom_rieng import user_nhom
    so = SoCai(tmp_path / 'so')
    identity = {'gid': 701, 'guid': 'G'}
    so.du_dinh('i', 'nhom', 'tram-kiem', {'user': 'tram-kiem'})
    so.ket('i', 'da_tao', dinh_danh=identity)
    tn = user_nhom('tram-kiem', '/Users/Shared/tram-kiem', so, lambda k,n,**kw: identity)
    cmds = tn.lenh('new')
    assert cmds[0][cmds[0].index('-GID') + 1] == '701'
    assert len(cmds) == 1  # Không sửa user nếu addUser gặp user lạ xuất hiện giữa chừng.


def test_bo_nhom_chi_danh_sach_cam():
    from tram.chu.nhom_rieng import lenh_bo_nhom
    cmds = lenh_bo_nhom('tram-kiem', {'staff', '_lpoperator', 'everyone', 'localaccounts'})
    assert [c[-1] for c in cmds] == ['staff']
    assert lenh_bo_nhom('tram-kiem', {'everyone', 'localaccounts', '_lpoperator',
                                     'com.apple.sharepoint.group.1'}) == []


def test_siet_user_la_khong_ghi(tmp_path):
    from tram.chu.nhom_rieng import siet_user
    calls = []
    with pytest.raises(ValueError, match='không khớp sổ'):
        siet_user('tram-kiem', SoCai(tmp_path / 'so'), lambda *a: {'uid': 503, 'guid': 'foreign'},
                  chay=lambda *a, **k: calls.append(a))
    assert not calls


def test_siet_user_giu_uid_guid_va_nhom_he_thong(tmp_path):
    from tram.chu.nhom_rieng import siet_user
    so, calls = SoCai(tmp_path / 'so'), []
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 701, 'guid': 'G'}}
    for k in identities:
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=identities[k])
    background = {'com.apple.sharepoint.group.1', '_lpoperator', 'everyone', 'localaccounts'}
    groups = background | {'staff', 'com.apple.sharepoint.group.7'}
    removed = []
    def run(cmd, **kw):
        calls.append(cmd)
        if cmd[:2] == ['/usr/bin/id', '-g']:
            return SimpleNamespace(stdout='701')
        if cmd[:2] == ['/usr/bin/id', '-Gn']:
            return SimpleNamespace(stdout=' '.join(groups))
        if '-d' in cmd:
            assert cmd[-1] not in background  # NestedGroups: không gỡ được bằng -d user.
            groups.remove(cmd[-1])
    siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run, truoc_bo=removed.extend)
    assert groups == background
    assert removed == ['com.apple.sharepoint.group.7', 'staff']
    assert next(c for c in calls if c[0] == 'sudo')[-2:] == ['PrimaryGroupID', '701']
    assert identities['user'] == {'uid': 503, 'guid': 'U'}


def test_sharepoint_khong_hardcode_mot_nhom():
    from tram.chu.nhom_rieng import lenh_bo_nhom
    assert [c[-1] for c in lenh_bo_nhom('tram-kiem', {'com.apple.sharepoint.group.7'})] == [
        'com.apple.sharepoint.group.7']


@pytest.mark.parametrize('extra', ['admin', 'nhom-la'])
def test_nhom_la_dung_truoc_doi_gid(tmp_path, extra):
    from tram.chu.nhom_rieng import siet_user
    so = SoCai(tmp_path / 'so')
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 701, 'guid': 'G'}}
    for k, value in identities.items():
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=value)
    calls = []
    def run(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(stdout=f'{extra} staff everyone localaccounts _lpoperator com.apple.sharepoint.group.1')
    with pytest.raises(ValueError, match='nhóm ngoài'):
        siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run)
    assert not any(c[0] == 'sudo' for c in calls)


def test_cai_lai_khong_tu_migrate_user_staff(tram_home_tam, tmp_path):
    from he_gia import HeGia
    from test_cai_dat_tho_kiem import ke_hoach
    from tram.chu.cai_dat import thuc_hien
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.phu['tram-tho'] = {'staff'}
    he.lenh.clear()
    with pytest.raises(ValueError, match='migration'):
        ke_hoach(tmp_path, he)
    assert not any(c.startswith('sudo') for c in he.lenh)


def test_cai_lai_chap_nhan_bon_nhom_nen_os(tram_home_tam, tmp_path):
    from he_gia import HeGia
    from test_cai_dat_tho_kiem import ke_hoach
    from tram.chu.cai_dat import thuc_hien
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    for user in he.user:
        he.phu[user] = {user, 'everyone', 'localaccounts', '_lpoperator', 'com.apple.sharepoint.group.1'}
    he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert not any(' -d ' in c for c in he.lenh)


@pytest.mark.parametrize('extra', ['staff', 'admin', 'nhom-la'])
def test_hau_kiem_khong_bo_qua_nhom_ngoai_nen(tmp_path, extra):
    from tram.chu.nhom_rieng import siet_user
    so = SoCai(tmp_path / 'so')
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 702, 'guid': 'G'}}
    for k, value in identities.items():
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=value)
    reads = 0
    def run(cmd, **kw):
        nonlocal reads
        if cmd[:2] == ['/usr/bin/id', '-g']:
            return SimpleNamespace(stdout='702')
        if cmd[:2] == ['/usr/bin/id', '-Gn']:
            reads += 1
            return SimpleNamespace(stdout='everyone localaccounts _lpoperator com.apple.sharepoint.group.1'
                                    + (f' {extra}' if reads == 3 else ''))
    with pytest.raises(ValueError, match='vẫn có nhóm thừa'):
        siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run)
