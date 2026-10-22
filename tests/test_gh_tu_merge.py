"""QĐ1: dạng lệnh merge chặt; required checks ở test_tm20_github."""
from tram.giao_viec.gh_tu_merge import dang_merge, la_dang_merge
R, H = "dai-ca/repo-nhap", "c" * 40

def test_dang_merge_duy_nhat():
    a = dang_merge(R, 12, H)
    assert a == ["12", "--repo", R, "--merge", "--match-head-commit", H] and la_dang_merge(tuple(a))
    assert dang_merge("x y", 12, H) is None and dang_merge(R, 0, H) is None and dang_merge(R, True, H) is None
    assert dang_merge(R, 12, "C" * 40) is None and dang_merge(R, 12, H[:39]) is None
    assert not la_dang_merge(("12", "--repo", R, "--squash", "--match-head-commit", H))
    assert not la_dang_merge(("+12", "--repo", R, "--merge", "--match-head-commit", H))
    assert not la_dang_merge(("12", "--repo", R, "--merge", "--match-head-commit", H, "--admin"))
