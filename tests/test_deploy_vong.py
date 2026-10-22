"""TM20 thay giả lập shell dưới trạm bằng đường dự án; giữ Git/SQLite cục bộ."""
from dataclasses import replace
from types import SimpleNamespace as NS
import subprocess
import pytest
from kho_kiem_gia import dung_kho
from tram.deploy import chay, git as git_deploy
from tram.deploy.vong import buoc_deploy
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import doc_su_kien
from tram.giao_viec.git_kiem import fetch
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doi_cai_dat, doc_trang_thai, ghi_tam_dung
from tram.chu import estop

DAI_CA = "dai-ca/dashboard"


class Tram:
    def __init__(self, tmp_path, monkeypatch, *, tu_deploy=False):
        self.k, self.n = dung_kho(tmp_path), 0
        self.kho = KhoPhieu(tmp_path / "su-kien.db")
        self.da = NS(ten="repo-nhap", nhanh_chinh="main")
        self.bo = NS(kho_git=lambda da: self.k.kho)
        self.ban, self.calls, self.hong = self.k.main, [], set()
        self.khi_kiem, self.khi_goi = lambda: None, lambda b: None
        self.bg, self.uq = True, True
        self.cd(tu_deploy=tu_deploy, lenh_deploy="d", lenh_kiem_song="k", lenh_lui="l")
        monkeypatch.setattr(chay, "DuongDeploy", lambda *a: self)
        monkeypatch.setattr(chay, "cong_mo", lambda: True)
        monkeypatch.setattr(chay, "kiem_ban", lambda *a: (self.khi_kiem(), self.uq)[1])
        monkeypatch.setattr(chay, "pham_vi_du", lambda *a: True)
        monkeypatch.setattr(chay, "ban_an_toan", lambda *a: True)
        monkeypatch.setattr(git_deploy, "chay_gioi_han",
                            lambda a, *, kill, timeout, **kw: subprocess.run(a, timeout=timeout, **kw))

    def cd(self, **kw):
        doi_cai_dat(self.kho.db, self.da.ten, lambda c: replace(c, **kw), tac_nhan=DAI_CA)

    def ghi(self, loai, d):
        return ghi(self.kho.db, self.da.ten, loai, d)

    def merge(self, *, tu=True):
        self.n += 1
        c = self.k.day("main", {f"src/{self.n}.py": str(self.n)})
        fetch(self.k.kho)
        if tu:
            self.ghi("tu_merge.bat_dau", {"commit": c, "loai": "code"})
        self.ghi("pr.da_merge", {"commit": c, "merge_commit": c})
        return c

    def bam(self, c):
        self.ghi("deploy.yeu_cau", {"ma_thao_tac": f"tay-{self.n}", "commit": c,
                                    "phien_ban": doc_trang_thai(self.kho.db, self.da.ten).phien_ban})

    def goi(self, buoc, ma, c, truoc):
        self.calls.append((buoc, c, truoc))
        self.khi_goi(buoc)
        if "khong_ro" in self.hong and buoc == "deploy":
            return None
        dat = buoc not in self.hong
        if dat and buoc in ("deploy", "lui"):
            self.ban = c
        if buoc in ("kiem_song", "kiem_song_sau_lui"):
            dat = dat and self.ban == c
        return dict(dat=dat, da_dung=True, san_sang=True, ban_truoc=self.ban)

    def buoc(self):
        return buoc_deploy(self.bo, self.kho, self.da, bat_ghi=lambda ten: self.bg)

    def sk(self, loai):
        return [s.du_lieu for s in doc_su_kien(self.kho.db, self.da.ten) if s.loai == loai]


@pytest.fixture
def t(tmp_path, monkeypatch):
    tr = Tram(tmp_path, monkeypatch)
    yield tr
    tr.kho.close()


def test_disabled_then_enabled_does_not_retroactively_deploy(t):
    c = t.merge()
    assert t.buoc() == {"san_sang_deploy": 1}
    t.cd(tu_deploy=True)
    assert t.buoc() == {} and not t.calls
    t.bam(c)
    assert t.buoc() == {"deploy_dat": 1} and t.ban == c
    assert t.buoc() == {}


def test_manual_merge_never_triggers_auto(t):
    t.cd(tu_deploy=True)
    c = t.merge(tu=False)
    assert t.buoc() == {"san_sang_deploy": 1} and not t.calls
    t.bam(c)
    assert t.buoc() == {"deploy_dat": 1}


def test_three_pending_coalesce(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.merge()
    m = t.merge()
    assert t.buoc() == {"deploy_dat": 1} and t.ban == m
    assert len(t.sk("deploy.bat_dau")) == 1
    assert len(t.sk("deploy.bat_dau")[0]["bao_gom"]) == 3


def test_pause_only_manual_can_start(t):
    t.cd(tu_deploy=True)
    c = t.merge()
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan=DAI_CA)
    assert t.buoc() == {"san_sang_deploy": 1}
    t.bam(c)
    assert t.buoc() == {"deploy_dat": 1}


def test_three_known_failures_disable_only_deploy(t):
    t.cd(tu_deploy=True)
    old = t.ban
    t.hong.add("deploy")
    for n in range(1, 4):
        t.merge()
        assert t.buoc() == {"deploy_da_lui": 1}
        assert t.sk("deploy.xong")[-1]["dem_hong"] == n and t.ban == old
    assert not doc_trang_thai(t.kho.db, t.da.ten).cai_dat.tu_deploy


def test_unknown_blocks_next_tick_even_after_continue(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add("khong_ro")
    assert t.buoc() == {"deploy_khong_ro": 1}
    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan=DAI_CA)
    count = len(t.calls)
    t.buoc()
    assert len(t.calls) == count and t.sk("deploy.xong")[-1]["dem_hong"] == 0


def test_estop_mid_chain_keeps_safe_finish(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add("deploy")
    t.khi_goi = lambda b: estop.bat("test") if b == "deploy" else None
    try:
        assert t.buoc() == {"deploy_da_lui": 1}
        t.merge()
        before = len(t.calls)
        t.buoc()
        assert len(t.calls) == before
    finally:
        estop.tat()
