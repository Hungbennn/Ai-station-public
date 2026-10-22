from types import SimpleNamespace
from tram.tho.chot_bao_b import chot_bao_b


def test_bo_sha_agent_gan_sha_quan_ly():
    pc = SimpleNamespace(wt="/work", p=SimpleNamespace(luot=4, repo=SimpleNamespace(nhanh="tram/bs-thu")))
    dong = {"commit": "a" * 40, "ban_giao": {"commit": "a" * 40, "luot": 999, "nhanh": "main"}}
    ra = chot_bao_b(pc, dong, chot=lambda wt, msg: "b" * 40)
    assert ra["commit"] == ra["ban_giao"]["commit"] == "b" * 40
    assert ra["ban_giao"]["luot"] == 4 and ra["ban_giao"]["nhanh"] == "tram/bs-thu"
    assert dong["ban_giao"]["commit"] == "a" * 40


def test_moc_b_khong_cong_bo(monkeypatch):
    from tram.tho import theo_doi
    pc = SimpleNamespace(tt=SimpleNamespace(ban_giao_tam=None), wt="/work", p=object(),
                         hop=SimpleNamespace(gui_mot=lambda *a: None))
    nc = SimpleNamespace(ch=SimpleNamespace(tren_may_b=True, chay=SimpleNamespace(day="kho-tho")),
                         khach=object(), cho_thu_lai=0)
    monkeypatch.setattr(theo_doi, "day_va_cong_bo", lambda *a, **kw: (_ for _ in ()).throw(AssertionError()))
    obj = SimpleNamespace(pc=pc, nc=nc)
    theo_doi.TheoDoi._moc(obj, {"commit": "a" * 40, "ban_giao": {"buoc_tiep": ["x"]}}, None)
    assert pc.tt.ban_giao_tam == {"buoc_tiep": ["x"]}


def test_chot_git_that_bo_sha_gia_trong_hang_doi(tmp_path, monkeypatch):
    from git_gia import git
    from tho_chay_gia import FILE_BG, dung_may, khoi_bg, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.bao import bao
    from tram.tho.hang_doi import xu_ly_hang_doi
    m = dung_may(tmp_path, monkeypatch, [])
    pc = chuan_bi(m.nc, *lay_phieu(m))
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg("Tên kết thúc 'ỷ' không mất byte"))
    monkeypatch.setenv("TRAM_GIT_QUA_QUAN_LY", "1")
    monkeypatch.setenv("TRAM_NHANH", pc.p.repo.nhanh)
    dong = bao("xong", "xong", wt=pc.wt, hang_doi=pc.hang_doi, ban_giao=FILE_BG)
    assert dong["commit"] is None and git(pc.wt, "status", "--porcelain")
    ds, _ = xu_ly_hang_doi(pc.hang_doi, khe_id=pc.p.khe_id, giao_id=pc.p.giao_id, luot=pc.p.luot)
    than = ds[0].than
    than["commit"] = "a" * 40
    ra = chot_bao_b(pc, than)
    assert ra["commit"] == ra["ban_giao"]["commit"] == git(pc.wt, "rev-parse", "HEAD")
    assert ra["commit"] != "a" * 40 and not git(pc.wt, "status", "--porcelain")
    assert ra["ban_giao"]["luot"] == pc.p.luot
