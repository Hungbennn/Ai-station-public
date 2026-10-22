"""I/O cho sổ tay B: log chỉ tên bước và mã, không ghi đầu ra con."""
import os
import subprocess
import tempfile
from pathlib import Path


class Dung(RuntimeError):
    pass


class Chay:
    def __init__(self):
        self.goc = Path(tempfile.mkdtemp(prefix="doi-ngu-b-", dir="/private/tmp"))
        self.log = self.goc / "ket-qua.txt"
        self.log.touch(mode=0o600)
        print(f"Log: {self.log}", flush=True)

    def ghi(self, ten, ma):
        with self.log.open("a") as f:
            f.write(f"{ten}: {ma}\n")

    def goi(self, ten, argv, *, han=600, input=None, check=True, env=None):
        try:
            r = subprocess.run(argv, input=input, capture_output=True, text=True, timeout=han, env=env)
        except (OSError, subprocess.TimeoutExpired):
            self.ghi(ten, "KHONG-KET-LUAN")
            raise Dung(ten) from None
        self.ghi(ten, r.returncode)
        if check and r.returncode:
            raise Dung(ten)
        return r

    def tuong_tac(self, ten, argv):
        # Terminal hiện màn đăng nhập; không thu/copy/log stdout hoặc stdin.
        ma = subprocess.call(argv)
        self.ghi(ten, ma)
        if ma:
            raise Dung(ten)


def ghi_yaml(p, raw):
    import yaml
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, ten = tempfile.mkstemp(prefix=".doi-ngu-", dir=p.parent)
    try:
        with os.fdopen(fd, "w") as f:
            yaml.safe_dump(raw, f, allow_unicode=True, sort_keys=False)
            f.flush()
            os.fsync(f.fileno())
        if p.exists():
            fd, _ = tempfile.mkstemp(prefix="truoc-doi-ngu-", dir=p.parent)
            with os.fdopen(fd, "wb") as f:
                f.write(p.read_bytes())
        os.replace(ten, p)
    finally:
        Path(ten).unlink(missing_ok=True)
