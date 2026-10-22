"""Kiểm chứng âm H9 — bộ thăm dò và cách chấm; `boc` giả (không sudo, không tạo user) — spec 3 §7.3 mục 7."""
import os
import sys

from tram.kiem.vong_doi import kill_cuc_bo
from tram.tho.kiem_am import ThamDo, chay_tham_do, tham_do_day_du, tham_do_khe


def boc_gia(dich: dict):
    """Thay mỗi argv bằng lệnh python trả mã/stdout/stderr đã định (CHỈ DÙNG TRONG TEST)."""
    def boc(argv):
        ma, out, *loi = dich.get(argv[0], (0, ""))
        return [sys.executable, "-c", f"import sys; print({out!r}); print({''.join(loi)!r}, file=sys.stderr); "
                f"sys.exit({ma})"]
    return boc


def test_bo_rut_gon_va_day_du(tmp_path):
    rg = tham_do_khe(keychain=["tram-tho-token"], doc_cam=[tmp_path / "phieu.json"], ghi_cam=[tmp_path / "hd-khe-2"],
                     ghi_duoc=tmp_path / "wt", ghi_tep_cam=[tmp_path / ".git" / "config"])
    assert [t.argv[0] for t in rg] == ["/usr/bin/security", "/bin/cat", "/usr/bin/touch", "/usr/bin/touch",
                                       "/usr/bin/true", "/usr/bin/touch"] and [t.kieu for t in rg][-2:] == ["ok", "ok"]
    assert rg[3].argv == ["/usr/bin/touch", "-c", str(tmp_path / ".git" / "config")]
    dd = tham_do_day_du(rut_gon=rg, api="http://127.0.0.1:7700", dai_ca_login="dai-ca@x", may_b="b.ts.net",
                        db=["127.0.0.1:3306"], tram_home_tram=tmp_path / ".tram")
    ten = [t.ten for t in dd]
    assert "API Duyệt với header danh tính giả" in ten and "kết nối DB nghiệp vụ 127.0.0.1:3306" in ten
    curl = next(t for t in dd if t.kieu == "http").argv
    assert "Tailscale-User-Login: dai-ca@x" in curl and curl[-1].endswith("/api/phe-duyet/kiem-am/kiem-am/duyet")
    assert next(t for t in dd if "DB" in t.ten).argv[-2:] == ["127.0.0.1", "3306"]


def test_cham_bi_chan_va_duong():
    ds = [ThamDo("keychain", ["/usr/bin/security"], "keychain"), ThamDo("đọc", ["/bin/cat"], "doc"),
          ThamDo("api 403", ["/usr/bin/curl"], "http"), ThamDo("api 422", ["/usr/bin/curl2"], "http"),
          ThamDo("hợp lệ", ["/usr/bin/true"], "ok")]
    kq = chay_tham_do(ds, boc=boc_gia({"/usr/bin/security": (44, "", "The specified item could not be found"),
                                       "/bin/cat": (0, "token!"), "/usr/bin/curl": (0, "403"),
                                       "/usr/bin/curl2": (0, "422"), "/usr/bin/true": (0, "")}), env=dict(os.environ),
                      kill=kill_cuc_bo)
    assert [k.dat for k in kq] == [True, False, True, False, True]
    assert kq[2].chi_tiet == "API từ chối (HTTP 403)" and "token!" not in kq[1].chi_tiet


def test_git_hook_that_khong_chay_voi_hook_tat(tmp_path):
    ds = [t for t in tham_do_day_du(rut_gon=[], api="http://x", dai_ca_login="a", may_b="b", db=[],
                                    tram_home_tram=None) if t.ten.startswith("git hook")]
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "TMPDIR": str(tmp_path)}
    assert chay_tham_do(ds, boc=lambda a: a, env=env, kill=kill_cuc_bo)[0].dat
