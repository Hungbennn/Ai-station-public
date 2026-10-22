"""Kế hoạch `tram tho dang-ky` (spec 3 §9.2, Q15; kiến trúc §7 "Mac thợ"): DÒ máy (chỉ đọc) rồi LIỆT KÊ mọi thay đổi
— chưa ghi gì. Ghi thật ở `thuc_hien_dk` sau khi Đại ca gõ `dong-y`. Từ chối khi máy chưa gắn tag Tailscale (#3),
thiếu `tram` hoặc CLI của một khe. KHÔNG trỏ Beads về trạm chủ (máy thợ không có quyền ghi Beads — kiến trúc §7)."""
import difflib
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from tram.tho.do_may import KetQuaDo, TAG_THO, do_cli, kiem_tag
from tram.tho.khai_khe import KheKhai, noi_dung_tho_yaml
from tram.tho.launchd_tho import NHAN_THO, lenh_nap_launchd, tao_plist_tho
from tram.tho.mcp_tho import ghep_codex_toml, lenh_claude_mcp, url_nho


@dataclass
class DauDoDK:
    which: object = shutil.which
    chay: object = subprocess.run
    home: Path = field(default_factory=Path.home)
    uid: int = field(default_factory=os.getuid)
    tram_home: Path = field(default_factory=lambda: Path(os.environ.get("TRAM_HOME") or Path.home() / ".tram"))
    daemon: Path = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


@dataclass
class KeHoachDangKy:
    tram_chu: str
    khe: list[dict]
    do: list[KetQuaDo]
    tep: dict[Path, bytes]
    so_sanh: list[str]
    lenh_mcp: list[tuple[list[str], dict[str, str]]]
    lenh_launchd: list[list[str]]
    canh_bao: list[str]
    tho_yaml: Path
    nho_url: str | None = None
    daemon: Path = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


def lap_ke_hoach_dk(tram_chu: str, khe: list[KheKhai], *, thu_muc_khe: Path, nho: bool, dd: DauDoDK) -> KeHoachDangKy:
    url = url_nho(tram_chu)[: -len("/nho/mcp")]
    if dd.daemon.exists() or (dd.tram_home / "tho.yaml").exists():
        raise ValueError("Máy đã có cấu hình/service thợ; dừng để không ghi đè principal hay chạy hai manager")
    if not khe or len({k.ten for k in khe}) != len(khe):
        raise ValueError("cần ít nhất một --khe, tên không trùng")
    co_tag, ly_do = kiem_tag(which=dd.which, chay=dd.chay)
    if not co_tag:
        raise ValueError(ly_do)
    tram = dd.which("tram")
    if not tram or not Path(tram).is_absolute():
        raise ValueError("không thấy `tram` trong PATH — cài bằng `uv tool install` trước")
    ds, do, tep, so_sanh, lenh_mcp = [], [], {}, [], []
    canh_bao = ["Tài khoản/principal thực thi của khe chưa tạo — chờ spike S6; dang-ky không tạo user macOS.",
                "Push ref tạm từ Mac thợ chờ spike S7 (credential GitHub); kho ~/tram/kho/<du-an> Đại ca clone tay."]
    for k in khe:
        thu_muc = thu_muc_khe.expanduser() / k.ten
        d = do_cli(k.cli, thu_muc, which=dd.which, chay=dd.chay)
        if d.duong_dan is None:
            raise ValueError(f"khe {k.ten}: {d.chi_tiet}")
        if d.dang_nhap is not True:
            canh_bao.append(f"khe {k.ten}: {d.chi_tiet}")
        if not thu_muc.exists():
            canh_bao.append(f"khe {k.ten}: chưa có {thu_muc} — Đại ca đăng nhập CLI vào đúng thư mục này")
        do.append(d)
        ds.append({"ten": k.ten, "cli": k.cli, "thu_muc_cau_hinh": str(thu_muc), "ten_goi_nho": k.ten_goi_nho,
                   "vai_uu_tien": list(k.vai_uu_tien)})
        if nho and k.cli == "codex":
            p = thu_muc / "config.toml"
            cu = p.read_text(encoding="utf-8") if p.exists() else ""
            moi = ghep_codex_toml(cu, url + "/nho/mcp")
            tep[p] = moi.encode()
            so_sanh += difflib.unified_diff(cu.splitlines(keepends=True), moi.splitlines(keepends=True), str(p), str(p))
        elif nho:
            lenh_mcp += lenh_claude_mcp(d.duong_dan, thu_muc)
    if nho:
        canh_bao.append("Memory MCP: cấu hình CLI chưa kiểm bằng chạy thật (spike N2, S5); --khong-nho để bỏ qua.")
    plist = dd.home / "Library/LaunchAgents" / f"{NHAN_THO}.plist"
    log = dd.tram_home / "log"
    tep[plist] = tao_plist_tho(tram=tram, log=log / "tho.log", home=dd.home)
    return KeHoachDangKy(url, ds, do, tep, so_sanh, lenh_mcp, [["mkdir", "-p", str(log)], *lenh_nap_launchd(
        plist, uid=dd.uid)], canh_bao, dd.tram_home / "tho.yaml", url + "/nho/mcp" if nho else None, dd.daemon)


def in_ke_hoach_dk(kh: KeHoachDangKy) -> str:
    d = [f"Đăng ký máy thợ với trạm chủ {kh.tram_chu}", "Dò (chỉ đọc):", f"  - tailscale: máy gắn {TAG_THO}"]
    d += [f"  - khe {k['ten']} ({x.cli} {x.phien_ban}, {x.duong_dan}): {x.chi_tiet}" for k, x in zip(kh.khe, kh.do)]
    d += ["Sẽ làm, theo thứ tự:", f"  1. Đổi mã ghép (dùng một lần) lấy token máy: POST {kh.tram_chu}/api/ghep-may",
          "  2. Ghi token máy vào Keychain tram-tho-token của tài khoản đang chạy (không in, không ghi file)",
          f"  3. Ghi {kh.tho_yaml} (máy đã có tho.yaml thì dừng, không ghi đè):"]
    d += ["       " + x for x in noi_dung_tho_yaml("<theo mã ghép>", kh.tram_chu, kh.khe).splitlines()]
    d += ["  4. Ghi file:"] + [f"       - {p}" for p in kh.tep]
    d += ["  5. Cấu hình memory MCP cho Claude:"] + [
        f"       - {' '.join(f'{x}={y}' for x, y in e.items())} {' '.join(a)}" for a, e in kh.lenh_mcp]
    d += [f"  6. Gửi đăng ký khe: POST {kh.tram_chu}/api/tho/dang-ky ({', '.join(k['ten'] for k in kh.khe)})",
          "  7. Chỉ ghi plist; CHƯA nạp. Sau khai principal/chay.day và đạt S2/S6/S7, mới dùng lệnh kích hoạt:"] + [
        f"       - {' '.join(c)}" for c in kh.lenh_launchd]
    d += ["Thay đổi config.toml của khe Codex:"] + ["    " + x.rstrip("\n") for x in kh.so_sanh or ["(không có)"]]
    d += ["Không làm: không trỏ Beads về trạm chủ (máy thợ không có quyền ghi Beads); không tạo tài khoản macOS (S6); "
          "không đổi cài đặt Tailscale.", "Cảnh báo:"] + [f"  - {c}" for c in kh.canh_bao]
    d += ["Lúc chạy, máy này chỉ gọi trạm chủ qua tailnet; CLI của khe tự gọi API nhà cung cấp của nó."]
    return "\n".join(d)
