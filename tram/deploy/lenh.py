"""Chạy lệnh deploy qua ống, hạn giờ và sở hữu nhóm theo primitive P1."""
import hashlib
import os
import shlex
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import tram_home
import subprocess

from tram.deploy.ong import DONG_CHE, Loc
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo
from tram.nho.bi_mat import quet

HAN = {"deploy": 900, "kiem_song": 120, "lui": 900, "kiem_song_sau_lui": 120, "git": 60}       # D100: giây
GIU_NGAY = 30
BIEN_GIU = ("PATH", "HOME", "LANG")


@dataclass(frozen=True)
class KetQuaBuoc:
    buoc: str
    ma_thoat: int | None
    giay: int
    het_gio: bool
    digest_log: str
    da_thu_hoi: bool = True

    @property
    def dat(self) -> bool:
        return self.ma_thoat == 0 and not self.het_gio and self.da_thu_hoi

    def su_kien(self) -> dict:
        return {"buoc": self.buoc, "ma_thoat": self.ma_thoat, "giay": self.giay, "het_gio": self.het_gio,
                "digest_log": self.digest_log}


def thu_muc_log(du_an: str) -> Path:
    p = tram_home() / "deploy-log" / du_an
    for d in (p.parent, p):
        d.mkdir(mode=0o700, exist_ok=True)
        os.chmod(d, 0o700)
    return p


def don_log_cu(thu_muc: Path, *, bay_gio: float | None = None) -> int:
    han, so = (bay_gio or time.time()) - GIU_NGAY * 86400, 0
    for f in thu_muc.glob("*.log"):
        if f.stat().st_mtime < han:
            f.unlink(missing_ok=True)
            so += 1
    return so


def moi_truong(goc: Mapping[str, str], du_an: str, commit: str, commit_truoc: str) -> dict[str, str]:
    return {**{k: goc[k] for k in BIEN_GIU if k in goc}, "TRAM_DU_AN": du_an, "TRAM_DEPLOY_COMMIT": commit,
            "TRAM_DEPLOY_COMMIT_TRUOC": commit_truoc}


def che(van_ban: str) -> str:
    return "\n".join(DONG_CHE if quet([d]) else d for d in van_ban.splitlines())


def _noi_log(log: Path, phan: bytes) -> None:
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, phan)
    finally:
        os.close(fd)
    os.chmod(log, 0o600)


def chay_buoc(buoc: str, lenh: str, *, cwd: Path, env: Mapping[str, str], log: Path) -> KetQuaBuoc:
    """Ống → RAM có trần → che → log 0600 từ lúc tạo. Không file tạm chứa output."""
    try:
        argv = shlex.split(lenh)
    except ValueError:
        argv = []
    bat_dau, ma, het_gio, sach = time.monotonic(), None, False, True
    digest = hashlib.sha256()
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb", buffering=0) as f:
        os.fchmod(f.fileno(), 0o600)
        def ghi(phan):
            f.write(phan)
            digest.update(phan)
        f.write(f"=== {buoc}\n".encode())
        loc = Loc(ghi)
        with so_huu("deploy: không xác nhận thu hồi cây tiến trình") as chu:
            try:
                if argv:
                    n = khoi_chay(argv, kill=kill_cuc_bo, chu=chu, cwd=cwd, env=dict(env),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    with n.p.stdout as ong:
                        os.set_blocking(ong.fileno(), False)
                        while True:
                            loc.doc(ong.fileno())
                            ma = n.cho(0.02)
                            if ma is not None or time.monotonic() - bat_dau >= HAN[buoc]:
                                break
                        het_gio = ma is None
                        sach = n.thu_hoi()
                        ma = n.p.returncode if het_gio else ma
                        loc.doc(ong.fileno())
            except OSError:
                ma = None
                ghi("[trạm: lỗi khởi chạy/đọc đầu ra]\n".encode())
            finally:
                loc.xong()
        giay = round(time.monotonic() - bat_dau)
        f.write((f"\n=== {buoc} · mã thoát {ma} · {giay} giây" + (" · quá hạn" if het_gio else "")
                 + (f" · đã cắt {loc.cat} byte" if loc.cat else "") + "\n").encode())
    return KetQuaBuoc(buoc, ma, giay, het_gio, "sha256:" + digest.hexdigest(), sach)
