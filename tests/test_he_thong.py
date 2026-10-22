"""2f P1: đọc dịch vụ launchd + Keychain cho trang Cài đặt — chỉ đọc, không lộ stdout, có bộ đệm (khảo sát §1.10)."""
import json
import subprocess

from tram.suy import he_thong
from tram.suy.he_thong import DocHeThong

BI_MAT = "BI-MAT-STDOUT keychain: \"acct\"<blob>=\"dai-ca@example.com\" PATH=/Users/x/.local/bin"
CHAY = f"gui/501/vn.tram.api = {{\n\tactive count = 1\n\tpath = /x\n\tstate = running\n\tpid = 4242\n\t{BI_MAT}\n}}"
DUNG = "gui/501/vn.tram.quet = {\n\tstate = not running\n\tlast exit code = 1\n}"


class ChayGia:
    def __init__(self, tra: dict[str, object] | None = None, mac_dinh=(113, "Could not find service")):
        self.tra, self.mac_dinh, self.argv = tra or {}, mac_dinh, []

    def __call__(self, argv: list[str]):
        self.argv.append(list(argv))
        kq = self.tra.get(argv[-1], self.mac_dinh)
        if isinstance(kq, BaseException):
            raise kq
        return kq


class DongHo:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def _doc(tmp_path, chay, dong_ho=None, cai=("vn.tram.api", "vn.tram.quet")):
    la = tmp_path / "Library" / "LaunchAgents"
    la.mkdir(parents=True, exist_ok=True)
    for n in cai:
        (la / f"{n}.plist").write_text("<plist/>")
    return DocHeThong(chay=chay, home=tmp_path, uid=501, dong_ho=dong_ho or DongHo())


def test_dich_vu_doc_state_va_chua_nap(tmp_path):
    chay = ChayGia({"gui/501/vn.tram.api": (0, CHAY), "gui/501/vn.tram.quet": (0, DUNG)})
    ds = _doc(tmp_path, chay).dich_vu()
    assert [d["nhan"] for d in ds] == ["vn.tram.api", "vn.tram.quet", "vn.tram.nho", "vn.tram.bao-tin",
                                       "vn.tram.sao-luu"]
    assert ds[0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": True, "dang_chay": True,
                     "kiem_duoc": True}
    assert ds[1]["da_cai"] is True and ds[1]["dang_chay"] is False and ds[1]["kiem_duoc"] is True
    assert ds[2] == {"nhan": "vn.tram.nho", "viec": "memory 127.0.0.1:7710", "da_cai": False,
                     "dang_chay": False, "kiem_duoc": True}          # mã ≠ 0: chưa nạp
    assert [d["viec"] for d in ds[3:]] == ["Telegram", "sao lưu su-kien.db"]


def test_chua_cai_va_timeout_khong_kiem_duoc(tmp_path):
    chay = ChayGia(mac_dinh=subprocess.TimeoutExpired(["launchctl"], 3))
    ds = _doc(tmp_path, chay, cai=()).dich_vu()
    assert all(d["da_cai"] is False and d["dang_chay"] is None and d["kiem_duoc"] is False for d in ds)
    ds = _doc(tmp_path, ChayGia(mac_dinh=OSError("không có launchctl"))).dich_vu()
    assert ds[0]["da_cai"] is True and ds[0]["dang_chay"] is None and ds[0]["kiem_duoc"] is False


def test_keychain_ma_0_44_khac_va_loi(tmp_path):
    chay = ChayGia({"tram-telegram-bot-token": (0, BI_MAT), "tram-anthropic-api-key": (44, ""),
                    "tram-nho-token": (36, "keychain locked"), "tram-noi-bo-token": OSError("x")})
    assert _doc(tmp_path, chay).keychain() == [
        {"ten": "tram-telegram-bot-token", "trang_thai": "co"}, {"ten": "tram-anthropic-api-key", "trang_thai": "chua"},
        {"ten": "tram-nho-token", "trang_thai": "khong_ro"}, {"ten": "tram-noi-bo-token", "trang_thai": "khong_ro"}]


def test_argv_tu_hang_so_khong_co_w(tmp_path):
    chay = ChayGia()
    d = _doc(tmp_path, chay)
    d.dich_vu(), d.keychain()
    assert chay.argv[0] == ["launchctl", "print", "gui/501/vn.tram.api"]
    sec = [a for a in chay.argv if a[0] == "security"]
    assert len(sec) == 4 and all(a[:3] == ["security", "find-generic-password", "-s"] and len(a) == 4 for a in sec)
    assert not any("-w" in a or "-g" in a for a in chay.argv)


def test_bo_dem_30_giay_dich_vu_60_giay_keychain(tmp_path):
    chay, dh = ChayGia(), DongHo()
    d = _doc(tmp_path, chay, dh)
    d.dich_vu(), d.keychain()
    n = len(chay.argv)
    dh.t += 29
    d.dich_vu(), d.keychain()
    assert len(chay.argv) == n                          # trong hạn: không gọi lại
    dh.t += 2
    d.dich_vu(), d.keychain()
    assert len(chay.argv) == n + 5                      # dịch vụ hết hạn 30 giây, Keychain chưa
    dh.t += 30
    d.keychain()
    assert len(chay.argv) == n + 9
    d.dich_vu()[0]["dang_chay"] = "sua"                 # sửa bản trả về không làm bẩn bộ đệm
    assert d.dich_vu()[0]["dang_chay"] is False


def test_khong_lo_stdout_pid_argv(tmp_path):
    chay = ChayGia({"gui/501/vn.tram.api": (0, CHAY), "tram-nho-token": (0, BI_MAT)}, mac_dinh=(0, BI_MAT))
    d = _doc(tmp_path, chay)
    s = json.dumps([d.dich_vu(), d.keychain()], ensure_ascii=False)
    for x in ("BI-MAT", "4242", "dai-ca@example.com", "PATH", "launchctl", "find-generic-password", "gui/501"):
        assert x not in s


def test_doc_he_thong_dung_chung_va_thay_duoc(monkeypatch):
    monkeypatch.setattr(he_thong, "_CHUNG", None)
    a = he_thong.doc_he_thong()
    assert isinstance(a, DocHeThong) and he_thong.doc_he_thong() is a
    gia = DocHeThong(chay=ChayGia(), uid=1)
    monkeypatch.setattr(he_thong, "_CHUNG", gia)
    assert he_thong.doc_he_thong() is gia
