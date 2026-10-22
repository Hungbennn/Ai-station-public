"""Chọn M từ pr.da_merge, kiểm M riêng với H; dữ liệu/Git/Uq giả."""
from types import SimpleNamespace as NS
from tram.deploy import ban
from tram.phieu.kho import KhoPhieu


def test_chon_merge_moi_nhat_khong_chon_head(monkeypatch):
    ds = [NS(id=1, loai="pr.da_merge", du_lieu={"merge_commit": "m1"}),
          NS(id=2, loai="pr.da_merge", du_lieu={"merge_commit": "m2"})]
    monkeypatch.setattr(ban, "merge_chua_deploy", lambda s: s)
    monkeypatch.setattr(ban, "la_to_tien", lambda kg, a, b: a == b or (a, b) in {
        ("m1", "origin/main"), ("m2", "origin/main"), ("m1", "m2")})
    assert ban.chon_ban(None, ds, "main") == "m2"
    assert ban.chon_ban(None, list(reversed(ds)), "main") == "m2"


def test_uq_receives_merge_sha_not_pr_head(tmp_path, monkeypatch):
    kho = KhoPhieu(tmp_path / "sk.db")
    da = NS(ten="a", nhanh_chinh="main", lenh_cho_phep=("test",),
            giao=NS(lenh_kiem_mac_dinh=("test",)))
    calls = []
    monkeypatch.setattr(ban, "cong_mo", lambda: True)
    def kiem(kg, da, **kw):
        calls.append(kw)
        return NS(dat=False)
    monkeypatch.setattr(ban, "kiem_tu_xa", kiem)
    try:
        assert not ban.kiem_ban(kho.db, None, da, "b" * 40, "7")
        assert calls[0]["commit"] == "b" * 40
        assert calls[0]["chay_lenh"] is True
        assert calls[0]["lenh_kiem"] == ["test"]
    finally:
        kho.close()


def test_direct_commit_requires_manual_scope(monkeypatch):
    monkeypatch.setattr(ban, "la_to_tien", lambda *a: True)
    monkeypatch.setattr(ban, "_git", lambda *a: NS(stdout=b"m1\ndirect\nm2\n"))
    ds = [NS(loai="pr.da_merge", du_lieu={"merge_commit": "m1"}),
          NS(loai="pr.da_merge", du_lieu={"merge_commit": "m2"})]
    assert not ban.pham_vi_du(None, ds, "old", "m2")


def test_manual_scope_never_waives_schema_or_protected_paths(monkeypatch):
    da = NS(giao=NS(duong_dan_cam=('deploy/**',)), hang_rao={'schema': NS(duong_dan=('db/**',))})
    for path in ('db/migrate.sql', 'deploy/entry.sh', 'src/safe.py'):
        monkeypatch.setattr(ban, 'tep_doi', lambda *a, p=path: [p], raising=False)
        assert ban.ban_an_toan(None, da, 'L', 'M') is (path == 'src/safe.py')
