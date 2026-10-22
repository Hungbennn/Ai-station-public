"""Biên deploy giả; không sudo, launchd hay quyền máy thật."""
import json
from types import SimpleNamespace
import pytest
from tram.deploy import duong
from tram.tu_dong.cai_dat import CaiDatTuDong


def cd(ten="a"):
    def lenh(b):
        return f"/usr/bin/sudo -n -u tram-dp-{ten} -- /Library/TramDeploy/{ten}/{b}"
    return CaiDatTuDong(lenh_deploy=lenh("deploy"), lenh_kiem_song=lenh("kiem-song"), lenh_lui=lenh("lui"))


def test_shape_rejects_repo_shell_and_other_target():
    assert duong.tach_lenh("a", cd())
    assert duong.tach_lenh("b", cd()) is None
    assert duong.tach_lenh("a", CaiDatTuDong(lenh_deploy="sh deploy.sh")) is None


def test_response_bound_to_target_version_and_run(monkeypatch):
    monkeypatch.setattr(duong, "kiem_tep", lambda p: None)
    monkeypatch.setattr(duong.pwd, "getpwnam", lambda n: SimpleNamespace(pw_uid=900, pw_dir="/tmp/nha-dp"))
    monkeypatch.setattr(duong.os, "getuid", lambda: 501)
    calls = []
    def run(argv, **kw):
        calls.append((argv, kw))
        r = json.loads(kw["input"])
        d = {**r, "dat": True, "da_dung": True, "san_sang": True, "ban_truoc": "b" * 40, "ban_thuc": r["commit"], "artifact": r["commit"]}
        return SimpleNamespace(returncode=0, stdout=json.dumps(d).encode(), stderr=b"")
    monkeypatch.setattr(duong, "chay_gioi_han", run)
    d = duong.DuongDeploy("a", cd())
    r = d.goi("kiem_song", "dp-1", "a" * 40, "b" * 40)
    assert r["dat"] and calls[0][1]["timeout"] == 120
    assert calls[0][1]["cwd"] == "/"
    assert "GH_TOKEN" not in calls[0][1]["env"]
    assert calls[0][0][-1] == "/Library/TramDeploy/a/kiem-song"
    def sai(*a, **kw):
        return SimpleNamespace(returncode=0, stdout=b'{"dat":true}', stderr=b"secret")
    monkeypatch.setattr(duong, "chay_gioi_han", sai)
    assert d.goi("deploy", "dp-1", "a" * 40, "b" * 40) is None


def test_writable_or_symlink_entrypoint_is_rejected(tmp_path):
    p = tmp_path / "x"
    p.write_text("echo x")
    with pytest.raises(ValueError):
        duong.kiem_tep(p)
    q = tmp_path / "q"
    q.symlink_to(p)
    with pytest.raises(ValueError):
        duong.kiem_tep(q)
