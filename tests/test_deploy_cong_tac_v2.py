"""D123/D124 giữ nguyên; điểm chèn race chuyển sang Uq thay tạo worktree."""
from test_deploy_vong import t
from tram.tu_dong.luu import ghi_tam_dung


def test_pause_resume_preserves_trigger(t):
    t.cd(tu_deploy=True)
    m = t.merge()
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan="dai-ca/dashboard")
    t.buoc()
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert t.buoc() == {"deploy_dat": 1} and t.ban == m


def test_off_on_between_ticks_consumes_ready_trigger(t):
    t.cd(tu_deploy=True)
    m = t.merge()
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan="dai-ca/dashboard")
    t.buoc()
    t.cd(tu_deploy=False)
    t.cd(tu_deploy=True)
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert t.buoc() == {} and not t.sk("deploy.bat_dau")
    t.bam(m)
    assert t.buoc() == {"deploy_dat": 1}


def test_failed_version_is_not_automatically_retried(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add("deploy")
    assert t.buoc() == {"deploy_da_lui": 1}
    n = len(t.calls)
    t.buoc()
    assert len(t.calls) == n
