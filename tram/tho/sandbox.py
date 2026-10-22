"""Hồ sơ `sandbox-exec` cho cơ chế "user thực thi chung + sandbox mỗi khe" (spec 3 §7.3 mục 2 — đề xuất §14,
CHỜ SPIKE S6: cú pháp SBPL, thứ tự ưu tiên luật, khoá Keychain qua mach-lookup đều phải kiểm trên máy B). Cơ chế
"user riêng mỗi khe" không dùng file này. Quy ước: cấm trước, rồi mở lại đúng chỗ của lần chạy."""
from pathlib import Path

KEYCHAIN_MACH = ("com.apple.SecurityServer", "com.apple.securityd", "com.apple.security.agent")


def _p(p: Path) -> str:
    s = str(Path(p))
    if not s.startswith("/") or any(c in s for c in '"\\\n'):
        raise ValueError(f"Đường dẫn không dùng được trong hồ sơ sandbox: {s!r}")
    return s


def ho_so_sandbox(*, cam: list[Path], cam_ghi: list[Path], cho_ghi: list[Path], cong_cam: list[int]) -> str:
    """`cam`: không đọc/ghi (kho của trạm, thư mục tiến trình quản lý, hàng đợi/cấu hình khe khác); `cam_ghi`: chỉ đọc
    (gốc worktree, gốc kho); `cho_ghi`: mở lại đọc/ghi (worktree của phiếu, hàng đợi + cấu hình của chính khe, tmp);
    `cong_cam`: cổng TCP không được kết nối (tram-api, dashboard, DB nghiệp vụ)."""
    dong = ["(version 1)", "(allow default)"]
    dong += [f'(deny file-read* file-write* (subpath "{_p(p)}"))' for p in cam]
    dong += [f'(deny file-write* (subpath "{_p(p)}"))' for p in cam_ghi]
    dong += [f'(allow file-read* file-write* (subpath "{_p(p)}"))' for p in cho_ghi]
    dong += ["(deny mach-lookup " + " ".join(f'(global-name "{m}")' for m in KEYCHAIN_MACH) + ")"]
    for c in cong_cam:
        if not isinstance(c, int) or not 0 < c < 65536:
            raise ValueError(f"Cổng sai: {c!r}")
        dong.append(f'(deny network-outbound (remote tcp "*:{c}"))')
    return "\n".join(dong) + "\n"


def ghi_ho_so(p: Path, noi_dung: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8")
    p.chmod(0o644)                     # principal đọc được, không ghi được (thuộc tiến trình quản lý)
    return p
