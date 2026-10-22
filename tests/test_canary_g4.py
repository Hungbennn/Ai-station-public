"""Canary dữ liệu giả ở tmp_path; tuyệt đối không đọc nhà thật."""
import subprocess

from tram.giao_viec import kich_ban_nghiem_thu as kb


def test_canary_chi_bao_khop_khong_in_noi_dung(tmp_path):
    mau = tmp_path / 'mau'
    mau.write_text('CANARY-NOT-A-SECRET-DO-NOT-PRINT')
    target = tmp_path / 'du lieu'
    target.mkdir()
    tep = target / 'canary'
    tep.write_bytes(mau.read_bytes())
    link = tmp_path / 'link'
    link.symlink_to(tep)
    script = kb.kich_ban_canary([tep, link, target / 'vang'], mau)
    result = subprocess.run(['/bin/sh', '-c', script], capture_output=True, text=True, check=True)
    assert result.stdout.splitlines() == ['0:match:yes:yes', '1:match:yes:yes', '2:no-match:no:yes']
    assert result.stderr == ''
    assert mau.read_text() not in result.stdout


def test_doi_chung_dung_cung_script_va_wrapper_that(tmp_path):
    from tram.giao_viec.mau_g4 import do_canary
    calls = []

    class PK:
        def boc_lenh(self, args):
            return ['ngoai', *args]

        def boc_luot(self, luot):
            assert luot == tmp_path
            return lambda args: ['trong', *args]

    def chay(argv, **kw):
        calls.append((argv, kw))
        return subprocess.CompletedProcess(argv, 0, '0:match:yes:yes\n' if argv[0] == 'ngoai' else '0:no-match:no:no\n')

    result = do_canary(PK(), tmp_path, [tmp_path / 'canary'], tmp_path / 'mau', chay=chay)
    assert result == {'ngoai': ['0:match:yes:yes'], 'trong': ['0:no-match:no:no']}
    assert calls[0][0][1:] == calls[1][0][1:]
    assert all(call[1]['timeout'] == 15 for call in calls)


def test_doi_chung_loi_khong_chep_dau_ra(tmp_path):
    from tram.giao_viec.mau_g4 import do_canary
    class PK:
        boc_lenh = staticmethod(lambda args: args)
        boc_luot = staticmethod(lambda luot: lambda args: args)
    result = do_canary(PK(), tmp_path, [tmp_path / 'canary'], tmp_path / 'mau',
                       chay=lambda *a, **k: subprocess.CompletedProcess(a, 0, 'SECRET-RAW'))
    assert result == {'ngoai': None, 'trong': None}


def test_doc_duoc_khac_mau_khong_tinh_la_bi_chan(tmp_path):
    mau, tep = tmp_path / 'mau', tmp_path / 'canary'
    mau.write_text('one'); tep.write_text('two')
    result = subprocess.run(['/bin/sh', '-c', kb.kich_ban_canary([tep], mau)],
                            capture_output=True, text=True, check=True)
    assert result.stdout == '0:different:yes:yes\n'
