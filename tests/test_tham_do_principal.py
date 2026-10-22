"""bs-863.14: thăm dò cách ly của `tram tho kiem` và `tram chu kiem-cach-ly` CHỈ chạy sau khi UID thực của principal
được chứng minh, qua `sudo -n` (không hỏi mật khẩu, không cần tty), `kill` của đúng principal, env dựng mới không HOME
của quản lý. D54: khe chỉ kiểm ở `tram tho kiem`; `tram chu kiem-cach-ly` in [CHUYỂN] cho khe, kiểm `tram-kiem`.
Không sudo/user thật: xác minh UID và chạy thăm dò đều GIẢ."""
from test_kiem_cong import cau_hinh
from tram.chu.kiem_cach_ly import kiem_cach_ly
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.khach import DichKiemAm
from tram.tho.kiem_am import KetQuaThamDo
from tram.tho.kiem_cong import cach_ly

DICH = DichKiemAm("dai-ca@x", "b.ts.net", ())


def ghi(da):
    def chay_td(ds, *, boc, env, kill):
        da.append({"argv": boc(["/bin/cat", "x"]), "env": env, "kill": kill})
        return [KetQuaThamDo(t.ten, True, "mã 1") for t in ds]
    return chay_td


def test_tho_kiem_uid_truoc_roi_tham_do_voi_kill_va_env_cua_principal(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", "/Users/quan-ly")
    ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
    ra = cach_ly(ch, ["hr"], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda ten, boc, kill: xm.append(ten) or 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["xanh"] and xm == ["tram-k-1"]
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and da[0]["env"] == {
        "PATH": "/x/bin", "LANG": "C.UTF-8"} and da[0]["kill"].__self__.user == "tram-k-1"


def test_tho_kiem_uid_chua_chung_minh_thi_do_va_khong_tham_do(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1", "user:tram-k-2")), []

    def xm(ten, boc, kill):
        raise (LoiDanhTinh("x") if ten == "tram-k-1" else LoiThuHoi("y"))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: DICH, chay_td=ghi(da), xac_minh=xm)
    assert [m.muc_do for m in ra] == ["do", "do"] and da == [] and "UID" in ra[0].chi_tiet


def test_chu_kiem_cach_ly_khe_chuyen_tram_kiem_van_uid_truoc(tram_home_tam):
    """D54: tài khoản trạm KHÔNG `sudo -n` sang khe (không chạy gì dưới khe, không dò UID khe) — in [CHUYỂN], không tính
    vào mã thoát; `tram-kiem` vẫn UID trước, `kill` của principal, env dựng mới."""
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {tram_kiem: user:tram-kiem}\n")
    da, xm = [], []
    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "sandbox:tram-exec"], chay_td=ghi(da),
                               xac_minh=lambda ten, boc, kill: xm.append(ten))
    assert xm == ["tram-kiem"] and len(da) == 1 and da[0]["kill"].__self__.ten == "tram-kiem" and ma == 0
    assert "tram-k-b-claude-1" not in da[0]["argv"] and set(da[0]["env"]) == {"PATH", "LANG"}
    assert "[CHUYỂN] user:tram-k-b-claude-1: kiểm cách ly khe bằng `tram tho kiem`" in van_ban
    assert "[CHUYỂN] sandbox:tram-exec:" in van_ban

    def xac_minh(ten, boc, kill):
        raise LoiDanhTinh("x")
    van_ban, ma = kiem_cach_ly([], chay_td=ghi(da), xac_minh=xac_minh)
    assert "[ĐỎ] user:tram-kiem: UID" in van_ban and ma == 1 and len(da) == 1



def test_tho_kiem_con_tien_trinh_cua_principal_sau_tham_do_thi_do_khong_giet(tmp_path):
    """A02: chỉ quan sát — bảng tiến trình còn tiến trình của UID principal → ĐỎ; không gửi tín hiệu nào."""
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []
    con = [TienTrinh(7000, 1, 7000, 600, 600, 1)]
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda *a: 600, chup=lambda: con)
    assert [m.muc_do for m in ra] == ["do"] and "còn 1 tiến trình của principal" in ra[0].chi_tiet
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda *a: 600, chup=lambda: (_ for _ in ()).throw(OSError("sysctl")))
    assert [m.muc_do for m in ra] == ["do"] and "không đọc được bảng tiến trình" in ra[0].chi_tiet
