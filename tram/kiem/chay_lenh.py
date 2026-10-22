"""Chạy MỘT lệnh kiểm (spec 3 §7.5 bước 2, spec 4 §6.2 bước 4): danh sách đối số, KHÔNG qua shell, nhóm tiến trình
riêng, có timeout; quá hạn hay xong đều thu hồi cả cây qua `vong_doi` (lát P1 — mọi lần chờ có hạn; không xác nhận
được đã thu hồi → `da_thu_hoi=False`, kết quả "fail"). `boc` BẮT BUỘC: người gọi quyết principal chạy lệnh (thợ:
principal thực thi của khe; trạm: `tram-kiem`) — chốt sau spike S6; mã này không bao giờ tự chọn chạy dưới quyền của
chính nó."""
import hashlib
import math
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.so_huu import so_huu
from tram.kiem.toolchain import bien_kiem
from tram.kiem.vong_doi import khoi_chay
from tram.kiem.vong_doi import kill_cuc_bo as _kill_nhom          # tên cũ — 3c/4a import, một định nghĩa ở P1

BIEN_GIU = ("PATH", "HOME", "LANG", "TMPDIR", "USER")


@dataclass(frozen=True)
class KetQuaLenh:
    lenh: str
    ket_qua: str            # "pass" | "fail"
    tom_tat: str            # 3 dòng cuối của log
    digest_log: str         # "sha256:<hex>" của log
    ma_thoat: int | None
    het_gio: bool = False
    da_thu_hoi: bool = True

    def sang_lenh_kiem(self) -> dict:
        """Dòng `lenh_kiem[]` của khối bàn giao (spec 0+1a §4.3)."""
        return {"lenh": self.lenh, "ket_qua": self.ket_qua, "tom_tat": self.tom_tat, "digest_log": self.digest_log}


def moi_truong_kiem(goc: Mapping[str, str], them: Mapping[str, str] | None = None) -> dict[str, str]:
    """Môi trường tối thiểu: chỉ giữ biến cần thiết (không token, không khoá), `APP_ENV=testing`, hook Git tắt."""
    env = {k: goc[k] for k in BIEN_GIU if k in goc}
    env.update({"APP_ENV": "testing", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath",
                "GIT_CONFIG_VALUE_0": "/dev/null"})
    env.update(them or {})
    for k in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
        env.pop(k, None)
    env.update(bien_kiem(env.get("HOME", "/var/empty")))
    return env


def _ket_qua(lenh: str, log: Path, ma: int | None, het_gio: bool, sach: bool = True) -> KetQuaLenh:
    du_lieu = log.read_bytes()
    dong = [d for d in du_lieu.decode("utf-8", "replace").splitlines() if d.strip()]
    return KetQuaLenh(lenh, "pass" if ma == 0 and not het_gio and sach else "fail", "\n".join(dong[-3:]),
                      "sha256:" + hashlib.sha256(du_lieu).hexdigest(), ma, het_gio, sach)


def chay_mot_lenh(lenh: str, argv: list[str] | None, *, cwd: Path, env: Mapping[str, str], log: Path,
                  thoi_gian_cho: float, boc: Callable[[list[str]], list[str]], cho_kill: float = 10.0,
                  kill: Callable[[int, int], None] = _kill_nhom, khoi: Callable = khoi_chay) -> KetQuaLenh:
    """`argv` None = lệnh không khớp `lenh_cho_phep` → KHÔNG chạy, coi là fail. `kill(pgid, sig)`: cách kill cả nhóm —
    mặc định cùng user; chạy dưới principal khác user thì truyền `Principal.kill_nhom` (3a-2, chờ S6)."""
    if not math.isfinite(thoi_gian_cho):
        raise ValueError("thoi_gian_cho phải hữu hạn")
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "wb") as f, so_huu("lệnh kiểm: không xác nhận thu hồi cây tiến trình", cho_term=cho_kill) as chu:
        if argv is None:
            f.write(f"[tram] lệnh không khớp lenh_cho_phep — không chạy: {lenh}\n".encode())
            f.flush()
            return _ket_qua(lenh, log, None, False)
        try:                                        # sở hữu từ PID (`so_huu`): lỗi/ngắt trước bước thu hồi → thu hồi
            n = khoi(boc(argv), kill=kill, chu=chu, cwd=cwd, env=dict(env), stdin=subprocess.DEVNULL, stdout=f,
                     stderr=subprocess.STDOUT)
        except OSError as e:
            f.write(f"[tram] lỗi khởi chạy: {type(e).__name__}\n".encode())     # không chép argv/đường dẫn
            f.flush()
            return _ket_qua(lenh, log, None, False)
        bat_dau = time.monotonic()
        ma = n.cho(thoi_gian_cho)
        het_gio = ma is None
        sach = n.thu_hoi(cho_term=cho_kill)        # quá hạn, hoặc con cháu còn sống sau khi lệnh chính thoát
        ma = n.p.returncode if het_gio else ma
        if het_gio:
            f.write(f"\n[tram] quá hạn {thoi_gian_cho:g} s (đã chạy {time.monotonic() - bat_dau:.1f} s)"
                    " — đã kill cả nhóm tiến trình\n".encode())
        if not sach:
            f.write("\n[tram] KHÔNG xác nhận được đã thu hồi cả cây tiến trình — không công nhận kết quả\n".encode())
    return _ket_qua(lenh, log, ma, het_gio, sach)
