"""`tram tho kiem` (spec 3 §9.3, H7): in xanh/vàng/đỏ từng mục, mã thoát ≠ 0 nếu có đỏ.
Mục chờ cổng (đăng nhập CLI — S2; cách ly + quyền ghi của principal — S6) ĐỎ khi không có bộ kiểm thật
(`DauDo.dang_nhap`, `DauDo.cach_ly` — 3a-2 `tram/tho/kiem_cong.py`); không bao giờ xanh nhờ fixture."""
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tram.tho.cau_hinh import CauHinhTho

GB = 1024 ** 3


@dataclass(frozen=True)
class MucKiem:
    muc: str
    muc_do: str          # xanh | vang | do
    chi_tiet: str


@dataclass
class DauDo:
    ping: Callable[[], dict]
    du_an: Callable[[], list[str]]
    which: Callable[[str], str | None] = shutil.which
    chay: Callable = subprocess.run
    con_trong: Callable[[Path], int] = lambda p: shutil.disk_usage(p).free
    thu_muc_kho: Path = field(default_factory=lambda: Path.home() / "tram" / "kho")
    dang_nhap: Callable | None = None          # (KheCauHinh) -> (mức, chi tiết) — chạy thật dưới principal (3a-2)
    cach_ly: Callable | None = None            # () -> list[MucKiem] — kiểm chứng âm rút gọn mỗi khe (3a-2)


def _khe(ch: CauHinhTho, dd: DauDo, cau_dao: dict) -> list[MucKiem]:
    ra = []
    for k in ch.khe:
        kid, duong = ch.khe_id(k), dd.which(k.cli)
        if duong is None:
            ra.append(MucKiem(f"{kid} CLI", "do", f"không thấy `{k.cli}` trong PATH"))
        else:
            v = dd.chay([duong, "--version"], capture_output=True, text=True, timeout=20)
            ra.append(MucKiem(f"{kid} CLI", "xanh" if v.returncode == 0 else "do", (v.stdout or v.stderr).strip()[:80]))
        ra.append(MucKiem(f"{kid} cấu hình", "xanh" if k.thu_muc_cau_hinh.is_dir() else "do", str(k.thu_muc_cau_hinh)))
        ra.append(MucKiem(f"{kid} đăng nhập", *(dd.dang_nhap(k) if dd.dang_nhap else (
            "do", "chưa kiểm được — chờ spike S2 (lệnh trạng thái không đọc file)"))))
        if kid not in cau_dao:
            ra.append(MucKiem(f"{kid} cầu dao", "do", "khe chưa đăng ký với trạm"))
        elif cau_dao[kid].get("ngat"):
            ra.append(MucKiem(f"{kid} cầu dao", "vang", f"đang ngắt tới {cau_dao[kid].get('toi_luc')}"))
        else:
            ra.append(MucKiem(f"{kid} cầu dao", "xanh", "đóng"))
    return ra


def _kho(dd: DauDo) -> list[MucKiem]:
    try:
        ds = dd.du_an()
    except Exception as e:                                # noqa: BLE001
        return [MucKiem("kho", "do", f"không lấy được danh sách dự án: {e}")]
    ra = []
    for ten in ds:
        p = dd.thu_muc_kho / ten
        env = [x for x in (p / ".env", *p.glob("*/.env")) if x.exists()]
        ra.append(MucKiem(f"kho {ten}", "do" if not p.is_dir() or env else "xanh",
                          "chưa clone" if not p.is_dir() else (f"có .env thật: {env[0]}" if env else str(p))))
    return ra + ([] if dd.cach_ly
                 else [MucKiem("quyền ghi worktree", "do", "chờ spike S6 (principal thực thi của khe)")])


def kiem_may(ch: CauHinhTho, dd: DauDo) -> list[MucKiem]:
    try:
        ping = dd.ping()
        ra = [MucKiem("tram-api", "xanh", f"máy {ping['may_id']}")]
    except Exception as e:                                # noqa: BLE001
        ping, ra = {}, [MucKiem("tram-api", "do", str(e))]
    ra += _khe(ch, dd, {k["khe_id"]: k["cau_dao"] for k in ping.get("khe", [])})
    try:
        ra += (dd.cach_ly() if dd.cach_ly
               else [MucKiem("cách ly", "do", "chờ spike S6 — bộ kiểm chứng âm §7.3 mục 7 chưa có")])
    except Exception as e:                                # noqa: BLE001
        ra.append(MucKiem("cách ly", "do", f"không chạy được kiểm chứng âm: {e}"))
    ra += _kho(dd)
    ra += [MucKiem(f"công cụ {c}", "xanh" if dd.which(c) else "do", dd.which(c) or "không có trong PATH")
           for c in ("git", "uv")]
    ngu = dd.chay(["pmset", "-g"], capture_output=True, text=True).stdout
    bat_ngu = any(l.split()[:1] == ["sleep"] and l.split()[1:2] != ["0"] for l in ngu.splitlines() if l.strip())
    ra.append(MucKiem("máy ngủ", "vang" if bat_ngu else "xanh", "đang bật chế độ ngủ" if bat_ngu else "tắt"))
    trong = dd.con_trong(Path.home())
    ra.append(MucKiem("dung lượng", "vang" if trong < 10 * GB else "xanh", f"còn {trong / GB:.1f} GB"))
    from tram.tho.kiem_3b import bo_sung_3b          # lát 3b: khe Codex, tag Tailscale của máy từ xa
    return bo_sung_3b(ch, dd, ra)


def in_ket_qua(ds: list[MucKiem]) -> tuple[str, int]:
    nhan = {"xanh": "XANH", "vang": "VÀNG", "do": "ĐỎ"}
    return "\n".join(f"[{nhan[m.muc_do]}] {m.muc}: {m.chi_tiet}" for m in ds), int(any(m.muc_do == "do" for m in ds))
