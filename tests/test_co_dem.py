from dataclasses import replace
import pytest
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.theo_co import doc_theo_co
from tram.giao_viec.co_dem import cham_co, pham_vi


def bead(files=(), tc=3, **kw):
    d = "<!-- pham-vi-co:v1 -->\n" + "\n".join("- " + p for p in files) + "\n<!-- /pham-vi-co -->"
    return Bead.tu_json(dict(id="b-1", updated_at="", design=d,
                            acceptance_criteria="\n".join(f"- {i}" for i in range(tc)), **kw))


def cfg(**kw):
    return doc_theo_co({"nhom": {"src/a/": "a", "src/b/": "b", "src/c/": "c"}, **kw})


@pytest.mark.parametrize("f,g,t,co", [(2,1,3,"nho"),(3,1,3,"vua"),(8,2,8,"vua"),
                                     (9,2,8,"lon"),(3,3,3,"lon"),(2,1,9,"lon")])
def test_s1(f, g, t, co):
    files = [f"src/{'abc'[i % g]}/{i}.py" for i in range(f)]
    b = bead(files + files, t)
    q = cham_co(b, cfg(), {}, diff=())
    assert q["co"] == co and q["dem"]["file"] == f
    assert cham_co(replace(b, priority=0), cfg(), {}, diff=()) == q


@pytest.mark.parametrize("raw", ["", "- x", "<!-- pham-vi-co:v1 -->- ../x<!-- /pham-vi-co -->",
                                 "<!-- pham-vi-co:v1 -->- /x<!-- /pham-vi-co -->"])
def test_pham_vi_sai(raw):
    assert pham_vi(raw) is None


def test_s2_s3_s9():
    assert pham_vi(bead(["./src/a/x", "src/a/x"]).design) == ("src/a/x",)
    b = bead(["src/a/x"])
    assert cham_co(replace(b, design=""), cfg(), {})["co"] == "vua"
    assert cham_co(replace(bead(tc=9), design=""), cfg(), {})["co"] == "lon"
    q = cham_co(b, cfg(), {}, diff=("tram/api/bao_mat.py",), ben=True)
    assert q["co"] == "lon" and "nguy-hiem" in q["ly_do"]
    assert cham_co(replace(b, labels=("co:vua",)), cfg(), {})["co"] == "vua"
    assert cham_co(replace(b, labels=("co:nho", "co:lon")), cfg(), {})["co"] == "lon"
    assert cham_co(bead(["la/x"]), cfg(), {})["thieu"] == ["nhom"]
    assert cham_co(b, cfg(), {}, nguy_hiem=True)["co"] == "lon"
    assert cham_co(b, cfg(), {}, phu_thuoc_ro=False)["co"] == "vua"


@pytest.mark.parametrize("raw", [None, False, [], {"x": 1}, {"nho_file": True}, {"nho_file": 9},
                                 {"vua_file": 0}, {"nhom": []}, {"model_nho": "opus"}])
def test_cau_hinh_sai(raw):
    with pytest.raises(ValueError):
        doc_theo_co(raw)


def test_s11():
    b = bead(["src/a/x", "src/a/y", "src/a/z"])
    cu, moi = cfg(), cfg(nho_file=3)
    assert cu["ban_luat"] != moi["ban_luat"]
    assert cham_co(b, cu, {})["co"] == "vua"
    assert cham_co(b, moi, {})["co"] == "nho"
    assert cham_co(replace(b, labels=("co:lon",)), moi, {})["co"] == "lon"


@pytest.mark.parametrize("co,effort", [("nho", "medium"), ("vua", "high"), ("lon", "high")])
def test_effort_mac_dinh_theo_co_sau_nang_nhan(co, effort):
    q = cham_co(bead(["src/a/x"], labels=("co:" + co,)), cfg(), {})
    assert q["co"] == co and q["effort"] == effort


@pytest.mark.parametrize("co", ["nho", "vua", "lon"])
@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_effort_tuy_chinh_va_ban_luat(co, effort):
    cu, moi = cfg(), cfg(**{"effort_" + co: effort})
    q = cham_co(bead(["src/a/x"], labels=("co:" + co,)), moi, {})
    assert q["effort"] == effort
    assert (cu["ban_luat"] == moi["ban_luat"]) is (cu["effort_" + co] == effort)


@pytest.mark.parametrize("co", ["nho", "vua", "lon"])
@pytest.mark.parametrize("effort", [None, True, 1, [], {}, "", "HIGH", " high", "high ", "auto"])
def test_effort_sai_bi_tu_choi(co, effort):
    with pytest.raises(ValueError, match="effort"):
        cfg(**{"effort_" + co: effort})


from tram.giao_viec.co_dem import cham_co


def test_docs_tests_openspec_chi_tang_so_file_ke_ca_khai_nhom():
    ch = cfg(nhom={"docs/":"docs", "tests/":"tests", "openspec/":"spec"})
    q = cham_co(bead(["docs/a.md","tests/a.py","openspec/a.md"]), ch, {})
    assert q["dem"]["file"] == 3 and q["dem"]["nhom"] == 0 and q["co"] == "vua"
