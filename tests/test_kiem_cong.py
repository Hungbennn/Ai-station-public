"""Mục chờ cổng của `tram tho kiem` chạy dưới principal (spec 3 §9.3, H7) — chạy/boc GIẢ, không sudo, không tạo user."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.khach import DichKiemAm
from tram.tho.kiem_am import KetQuaThamDo
from tram.tho.kiem_cong import cach_ly, dang_nhap
from tram.tho.kiem_may import DauDo, MucKiem, kiem_may
from tram.tho.principal_khe import lenh_trao_quyen, principal_cua


def cau_hinh(tmp_path, principal=("user:tram-k-1", "user:tram-k-2")):
    khe = tuple(KheCauHinh(f"claude-{i}", "claude", p, tmp_path / f"cfg{i}", f"Claude {i}", ("coder",))
                for i, p in enumerate(principal, 1))
    return CauHinhTho("B", "http://127.0.0.1:7700", khe, CauHinhChay(path="/x/bin", thu_muc_tram=Path("/Users/tram/.tram")))


def test_principal_sandbox_co_ho_so_rieng_cua_khe(tmp_path):
    ch = cau_hinh(tmp_path, ("sandbox:tram-thuc-thi", "sandbox:tram-thuc-thi"))
    p = principal_cua(ch, ch.khe[0], goc=tmp_path / "home", goc_wt=tmp_path / "wt", wt=tmp_path / "wt" / "hr" / "hr-1",
                      ten="g-1-1")
    hs = (tmp_path / "home" / "sandbox" / "B" / "claude-1" / "g-1-1.sb").read_text()
    assert p.ho_so.name == "g-1-1.sb" and "/usr/bin/sandbox-exec" in p.boc(["claude"])
    assert f'(deny file-read* file-write* (subpath "{tmp_path}/home/hang-doi/B/claude-2"))' in hs
    assert f'(allow file-read* file-write* (subpath "{tmp_path}/wt/hr/hr-1"))' in hs and "/Users/tram/.tram" in hs
    assert principal_cua(cau_hinh(tmp_path), cau_hinh(tmp_path).khe[0], goc=tmp_path, goc_wt=tmp_path, wt=None,
                         ten="x").ho_so is None


def test_lenh_trao_quyen_acl_cho_principal(tmp_path):
    ds = lenh_trao_quyen(tmp_path / "wt", tmp_path / "kho" / ".git" / "worktrees" / "hr-1", user="tram-k-1")
    assert ds[0][:2] == ["/usr/bin/find", str(tmp_path / "wt")] and ds[0][10:12] == ["/bin/chmod", "+a"]
    assert ds[0][12].startswith("user:tram-k-1 allow list,add_file") and "-R" not in ds[0]
    assert len(ds) == 2 and all(".git/config" not in " ".join(x) for x in ds)
    assert lenh_trao_quyen(tmp_path, user="tram-k-1", thu=True)[0][11] == "-a"


def test_dang_nhap_chay_lenh_trang_thai_duoi_principal(tmp_path):
    goi = []

    def chay(argv, **kw):
        goi.append((argv, kw["env"]))
        return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}')
    ch = cau_hinh(tmp_path)
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)[0] == "xanh"
    argv, env = goi[0]
    assert argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and argv[-3:] == ["chay", "auth", "status"]
    assert env["CLAUDE_CONFIG_DIR"] == str(tmp_path / "cfg1") and "TRAM_THO_TOKEN" not in env
    ch2 = cau_hinh(tmp_path, (None, None))
    assert dang_nhap(ch2, ch2.khe[0], goc=tmp_path, goc_wt=tmp_path)[0] == "do"


def test_cach_ly_xanh_khi_moi_tham_do_dat_do_khi_mot_cai_hong(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1", None)), []

    def chay_td(ds, *, boc, env, kill):
        da.append([t.ten for t in ds])
        return [KetQuaThamDo(t.ten, "Keychain" not in t.ten, "mã 0") for t in ds]
    ra = cach_ly(ch, ["hr-codex"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=chay_td,
                 dich=lambda: DichKiemAm("dai-ca@x", "b.ts.net", ("127.0.0.1:3306",)),
                 xac_minh=lambda ten, boc, kill: 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["do", "do"] and "đọc Keychain tram-tho-token" in ra[0].chi_tiet
    assert f"sửa {tmp_path}/kho/hr-codex/.git/config" in da[0] and "chờ spike S6" in ra[1].chi_tiet
    assert "API Duyệt với header danh tính giả" in da[0] and "kết nối DB nghiệp vụ 127.0.0.1:3306" in da[0]   # D54


def test_kiem_may_dung_bo_kiem_that_khi_co(tmp_path):
    ch = replace(cau_hinh(tmp_path), khe=cau_hinh(tmp_path).khe[:1])
    dd = DauDo(ping=lambda: {"may_id": "B", "khe": [{"khe_id": "B/claude-1", "cau_dao": {"ngat": False}}]},
               du_an=lambda: [], which=lambda c: None, chay=lambda *a, **kw: SimpleNamespace(stdout="", returncode=0),
               con_trong=lambda p: 50 * 1024 ** 3, dang_nhap=lambda k: ("xanh", "ok"),
               cach_ly=lambda: [MucKiem("B/claude-1 cách ly", "xanh", "9 thăm dò đạt")])
    muc = {m.muc: m.muc_do for m in kiem_may(ch, dd)}
    assert muc["B/claude-1 đăng nhập"] == "xanh" and muc["B/claude-1 cách ly"] == "xanh"
    assert "cách ly" not in muc and "quyền ghi worktree" not in muc
