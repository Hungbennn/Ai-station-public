import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cong-cu"))
from doi_ngu_io import Chay, Dung
import doi_ngu_io
from doi_ngu_chuan_bi import can_tat


def test_log_khong_ghi_dau_ra_con(tmp_path, monkeypatch):
    monkeypatch.setattr(doi_ngu_io.tempfile, "mkdtemp", lambda **kw: str(tmp_path))
    monkeypatch.setattr(doi_ngu_io.subprocess, "run", lambda *a, **kw:
                        SimpleNamespace(returncode=1, stdout="bi-mat", stderr="bi-mat"))
    c = Chay()
    with pytest.raises(Dung):
        c.goi("thu", ["gia"])
    assert c.log.read_text() == "thu: 1\n"
    assert c.log.stat().st_mode & 0o777 == 0o600


def test_khong_co_service_chua_du_phai_disable():
    class Gia:
        def goi(self, ten, argv, **kw):
            return (SimpleNamespace(returncode=113, stderr="Could not find service", stdout="")
                    if ten == "dich-vu-tho" else SimpleNamespace(stdout='"vn.tram.tho" => false'))
    with pytest.raises(Dung, match="disable"):
        can_tat(Gia())


@pytest.mark.parametrize("tat", ["true", "disabled"])  # macOS 15 in "disabled"/"enabled" (đo máy B 21/10)
def test_disable_nhan_ca_hai_kieu_in(tat):
    class Gia:
        def goi(self, ten, argv, **kw):
            return (SimpleNamespace(returncode=113, stderr="Could not find service", stdout="")
                    if ten == "dich-vu-tho" else SimpleNamespace(stdout=f'\t\t"vn.tram.tho" => {tat}\n'))
    can_tat(Gia())


def test_bat_kieu_moi_van_chua_disable():
    class Gia:
        def goi(self, ten, argv, **kw):
            return (SimpleNamespace(returncode=113, stderr="Could not find service", stdout="")
                    if ten == "dich-vu-tho" else SimpleNamespace(stdout='\t\t"vn.tram.tho" => enabled\n'))
    with pytest.raises(Dung, match="disable"):
        can_tat(Gia())


def test_kho_tho_nhan_commit_moi_tu_remote_tracking_cua_nguon(tmp_path):
    from git_gia import git
    from kho_kiem_gia import dung_kho
    from doi_ngu_chuan_bi import dong_bo_nguon
    k = dung_kho(tmp_path)
    tho = tmp_path / "tho"
    git(tmp_path, "clone", "-q", str(k.kho), str(tho))
    moi = k.day("main", {"moi.txt": "moi"})
    git(k.kho, "fetch", "-q", "origin")
    assert git(k.kho, "rev-parse", "main") != moi
    class Gia:
        def goi(self, ten, argv, **kw):
            assert argv[:5] == ["sudo", "-H", "-u", "tram-tho", "git"]
            assert argv[5:7] == ["-C", str(tho)]
            return git(tho, *argv[7:])
    dong_bo_nguon(Gia(), tho)
    assert git(tho, "rev-parse", "origin/main") == moi
    assert git(tho, "cat-file", "-t", moi) == "commit"


def test_bat_giao_khong_gioi_han_bead_giu_ngan_sach(tmp_path, monkeypatch):
    import yaml
    import doi_ngu_b as m
    from tram.phieu.kho import KhoPhieu
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    for ten in ("ben-station", "hr-codex"):
        (repo / f"du-an/{ten}.yaml").write_text("bat_ghi: false\n")
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: false, bead: [bs-cu]}\nhan_muc: {ngung: 90}\n")
    kho = KhoPhieu(tmp_path / "su-kien.db")
    kho.close()
    monkeypatch.setattr(m, "REPO", repo)
    monkeypatch.setattr(m, "CAU_HINH", ch)
    monkeypatch.setattr("builtins.input", lambda *a: (_ for _ in ()).throw(AssertionError("hoi bead")))
    c = SimpleNamespace(goi=lambda *a, **kw: None)
    m.giao(c, True)
    raw = yaml.safe_load(ch.read_text())
    assert raw["giao_viec"] == {"bat": True, "du_an": ["ben-station"]}
    assert raw["han_muc"] == {"ngung": 90}
    assert yaml.safe_load((repo / "du-an/ben-station.yaml").read_text())["bat_ghi"] is True
    assert yaml.safe_load((repo / "du-an/hr-codex.yaml").read_text())["bat_ghi"] is False


@pytest.mark.parametrize("truong", ["tu_merge", "tu_deploy"])
def test_bat_giao_tu_choi_khi_tu_dong_dang_bat(tmp_path, monkeypatch, truong):
    from dataclasses import replace
    from contextlib import closing
    from tram.phieu.kho import KhoPhieu
    from tram.tu_dong.luu import doi_cai_dat
    import doi_ngu_b as m
    with closing(KhoPhieu(tmp_path / "su-kien.db")) as kho:
        doi_cai_dat(kho.db, "ben-station", lambda cd: replace(cd, **{truong: True}), tac_nhan="fixture")
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: false}\n")
    monkeypatch.setattr(m, "CAU_HINH", ch)
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    (repo / "du-an/ben-station.yaml").write_text("bat_ghi: false\n")
    monkeypatch.setattr(m, "REPO", repo)
    with pytest.raises(Dung, match="tu-dong"):
        m.giao(SimpleNamespace(goi=lambda *a, **kw: None), True)
    assert ch.read_text() == "giao_viec: {bat: false}\n"


@pytest.mark.parametrize("bat_ghi", ["true", "false"])
def test_tat_giao_giu_nguyen_kenh_nhan_yeu_cau(tmp_path, monkeypatch, bat_ghi):
    import yaml
    import doi_ngu_b as m
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    p = repo / "du-an/ben-station.yaml"
    truoc = f"# Kênh nhận yêu cầu độc lập với giao việc\nbat_ghi: {bat_ghi}\n"
    p.write_text(truoc)
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: true}\nhan_muc: {ngung: 90}\n")
    monkeypatch.setattr(m, "REPO", repo)
    monkeypatch.setattr(m, "CAU_HINH", ch)
    m.giao(SimpleNamespace(goi=lambda *a, **kw: None), False)
    assert p.read_text() == truoc
    raw = yaml.safe_load(ch.read_text())
    assert raw["giao_viec"]["bat"] is False
    assert raw["han_muc"] == {"ngung": 90}


def test_con_phieu_b_doc_tram_home_chi_doc(tmp_path, monkeypatch):
    import sqlite3
    import doi_ngu_b as m
    home = tmp_path / "tram home # rieng"
    home.mkdir()
    p = home / "su-kien.db"
    connect = sqlite3.connect
    db = connect(p)
    db.execute("CREATE TABLE phieu (may_id TEXT, trang_thai TEXT)")
    db.executemany("INSERT INTO phieu VALUES (?, ?)",
                   [("B", "hieu_luc"), ("B", "xong"), ("A", "hieu_luc")])
    db.commit()
    db.close()
    monkeypatch.setenv("TRAM_HOME", str(home))
    def doc(dia_chi, **kw):
        assert dia_chi == p.as_uri() + "?mode=ro"
        assert kw == {"uri": True, "timeout": 5}
        return connect(dia_chi, **kw)
    monkeypatch.setattr(m.sqlite3, "connect", doc)
    assert m.con_phieu_b() == 1
    p.unlink()
    with pytest.raises(sqlite3.OperationalError):
        m.con_phieu_b()
    assert not p.exists()


def test_runtime_dung_bundle_root_va_chi_mo_doc_sau_chuan_bi(tmp_path, monkeypatch):
    import shutil
    import subprocess
    import doi_ngu_chuan_bi as c
    repo, runtime, log = tmp_path / 'repo', tmp_path / 'runtime', tmp_path / 'log'
    (repo / 'du-an').mkdir(parents=True)
    log.mkdir()
    (repo / 'du-an/ben-station.yaml').write_text('ten: ben-station\nmoi_truong_kiem: {file: /x, dich: .env.testing}\n')
    cfg = tmp_path / 'cau-hinh.yaml'
    cfg.write_text('{}')
    for name, value in {'REPO': repo, 'RUNTIME': runtime, 'TRAM': runtime / '.venv/bin/tram',
                        'CAU_HINH': cfg}.items():
        monkeypatch.setattr(c, name, value)
    monkeypatch.setattr(c, 'can_tat', lambda c: None)
    da = []
    def goi(ten, argv, **kw):
        da.append((ten, argv))
        if ten == 'clone-runtime':
            assert runtime.stat().st_mode & 0o777 == 0o700
            shutil.copytree(repo / 'du-an', runtime / 'du-an')
        if ten == 'deps-root':
            assert 'cap_deps_b' in argv[3] and '-I' in argv
            (runtime / '.venv/bin').mkdir(parents=True)
        if ten == 'runtime-chi-doc':
            subprocess.run(argv, check=True)
    obj = type('C', (), {'goc': log, 'goi': staticmethod(goi), 'ghi': staticmethod(lambda *a: None)})()
    c.chuan_bi(obj)
    assert runtime.stat().st_mode & 0o777 == 0o755
    assert not any('uv' in a or 'sync' in a for _, a in da)
    assert c.TRAM.stat().st_mode & 0o777 == 0o755
    assert str(runtime) in c.TRAM.read_text()


def test_main_doi_thu_muc_ve_goc_truoc_lenh_duoi_user_khe(tmp_path, monkeypatch):
    # R2 máy B 21/10: chạy từ ~ (nhà hungle đã chặn khe) làm `claude auth login` dưới tram-khe1 lỗi EACCES.
    import os
    import doi_ngu_b
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(doi_ngu_b.sys, "argv", ["doi_ngu_b.py", "login-1"])
    monkeypatch.setattr(doi_ngu_b.Path, "home", staticmethod(lambda: Path("/Users/dai-ca")))
    monkeypatch.setattr(doi_ngu_b.os, "getuid", lambda: 501)
    thay = []
    class Gia:
        def tuong_tac(self, ten, argv):
            thay.append(os.getcwd())
        def ghi(self, *a):
            pass
    monkeypatch.setattr(doi_ngu_b, "Chay", Gia)
    monkeypatch.setattr(doi_ngu_b, "dang_nhap", lambda c, n: thay.append(os.getcwd()))
    assert doi_ngu_b.main() == 0
    assert thay and all(d == "/" for d in thay)


def test_khong_con_ham_keychain_trong_so_tay():
    import doi_ngu_b
    assert not hasattr(doi_ngu_b, 'keychain')


def _kho_gia(tmp_path, monkeypatch, ma_test):
    import doi_ngu_chuan_bi as c
    monkeypatch.setattr(c, "can_tat", lambda c: None)
    monkeypatch.setattr(c, "THO", tmp_path / "khong-doc-duoc")
    monkeypatch.setattr(c.Path, "exists", lambda self: (_ for _ in ()).throw(PermissionError(13, "x"))
                        if "khong-doc-duoc" in str(self) else False)
    monkeypatch.setattr(c.Path, "is_symlink", lambda self: False)  # không đọc symlink kho kiểm thật của máy B
    da = []
    class Gia:
        def goi(self, ten, argv, **kw):
            da.append((ten, argv))
            if ten == "doc-remote":
                return SimpleNamespace(returncode=0, stdout="https://github.com/Hungbennn/ben-station.git\n")
            if ten == "co-kho-tho":
                return SimpleNamespace(returncode=ma_test)
            raise Dung("dung-sau-kiem")
    return c, Gia(), da


def test_kho_kiem_kho_tho_bang_quyen_tram_tho(tmp_path, monkeypatch):
    # R3 máy B 21/10: hungle không stat được nhà tram-tho (700) → PermissionError, dừng trước clone.
    c, g, da = _kho_gia(tmp_path, monkeypatch, 1)
    with pytest.raises(Dung, match="dung-sau-kiem"):
        c.kho(g)
    ten, argv = next(x for x in da if x[0] == "co-kho-tho")
    assert argv[:4] == ["sudo", "-u", "tram-tho", "test"] and argv[-1].endswith("tram/kho/ben-station")


def test_kho_tho_da_co_thi_dung_doi_soat(tmp_path, monkeypatch):
    c, g, da = _kho_gia(tmp_path, monkeypatch, 0)
    with pytest.raises(Dung, match="kho-da-co"):
        c.kho(g)
