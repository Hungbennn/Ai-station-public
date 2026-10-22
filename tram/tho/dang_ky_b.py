"""Đăng ký cấu hình B; không cài dịch vụ hoặc cấp lại token."""
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram


def kiem_b(ch):
    if ch.may_id != "B" or ch.tram_api != "http://127.0.0.1:7700" or ch.chay.day != "kho-tho":
        raise ValueError("Cần máy B, API loopback và đường kho-tho")
    expected = {"claude-1": "user:tram-khe1", "claude-2": "user:tram-khe2"}
    if {k.ten: k.principal for k in ch.khe} != expected or any(k.cli != "claude" for k in ch.khe):
        raise ValueError("Cần đúng hai khe Claude riêng trên B")
    for k in ch.khe:
        if k.thu_muc_cau_hinh != Path(f"/Users/{k.principal[5:]}/claude"):
            raise ValueError("Thư mục Claude phải thuộc đúng khe")


def dang_ky_b(nguon: Path, dich: Path, khach) -> list[str]:
    ch = nap_cau_hinh_tho(nguon)
    kiem_b(ch)
    noi_dung = nguon.read_bytes()
    if khach.ping().get("may_id") != "B":
        raise ValueError("Token không thuộc máy B")
    than = {"may_id": "B", "khe": [{n: asdict(k)[n] for n in
        ("ten", "cli", "ten_goi_nho", "vai_uu_tien", "models")} for k in ch.khe]}
    ma, _ = khach.goi("POST", "/api/tho/dang-ky", than)
    if ma != 200:
        raise LoiKhachTram(f"Đăng ký B chưa xác nhận (HTTP {ma})")
    dich.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if dich.is_symlink():
        raise ValueError("Không thay cấu hình là symlink")
    if dich.exists() and dich.read_bytes() == noi_dung:
        return [f"B/{k.ten}" for k in ch.khe]
    if dich.exists():
        fd, _ = tempfile.mkstemp(prefix="tho-truoc-", suffix=".yaml", dir=dich.parent)
        with os.fdopen(fd, "wb") as f:
            f.write(dich.read_bytes())
            f.flush()
            os.fsync(f.fileno())
    fd, ten = tempfile.mkstemp(prefix=".tho-", dir=dich.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(noi_dung)
            f.flush()
            os.fsync(f.fileno())
        os.replace(ten, dich)
    finally:
        Path(ten).unlink(missing_ok=True)
    return [f"B/{k.ten}" for k in ch.khe]


def lenh(args):
    import fcntl
    import pwd
    from tram.duong_dan import tram_home
    from tram.tho.khach import KhachTram, doc_token_may
    if pwd.getpwuid(os.getuid()).pw_name != "tram-tho":
        print("Chạy đăng ký dưới tài khoản tram-tho.")
        return 2
    if not args.dong_y:
        print("Sẽ đăng ký hai khe B và thay tho.yaml; không bật dịch vụ.")
        if input("Gõ dong-y: ").strip() != "dong-y":
            return 1
    try:
        token = doc_token_may(tren_may_b=True)
        if not token:
            raise ValueError("Thiếu token máy")
        goc = tram_home()
        goc.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(goc / ".dang-ky-b.lock", os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            dang_ky_b(Path(args.tep), goc / "tho.yaml", KhachTram("http://127.0.0.1:7700", token))
    except (OSError, ValueError, LoiKhachTram):
        print("Chưa hoàn tất đăng ký B; giữ dịch vụ tắt, đối soát rồi thử lại cùng cấu hình/token.")
        return 2
    print("Đã đăng ký hai khe B; chưa bật khe hoặc giao việc.")
    return 0


def them_lenh(tho):
    p = tho.add_parser("dang-ky-b", help="Đăng ký hai khe trên máy B, không bật thợ")
    p.add_argument("--tep", required=True)
    p.add_argument("--dong-y", action="store_true")
    p.set_defaults(ham=lenh)
