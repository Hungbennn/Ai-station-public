"""Principal kiểm lại `tram-kiem` theo D22 (lát 3c; spec 3 §7.3 mục 5, spec 4 §6.2 bước 1) — KHÔNG root lúc chạy.

`tram-kiem` tự sở hữu bản chép kiểm dưới `thu_muc_kiem` (trạm `git archive` rồi đưa qua stdin cho `tram-kiem` tự
`tar -x`, tự dọn). Tài khoản trạm chỉ được chạy lệnh DƯỚI `tram-kiem` qua sudo — không có dòng sudoers nào chạy root,
không helper, không ACL/chmod. File này giữ chuỗi phía cài đặt: kiểm `thu_muc_kiem`, dòng sudoers, hồ sơ Seatbelt.

Sudoers KHÔNG chặn được lệnh tuỳ ý dưới `tram-kiem`, và chặn cũng không thêm an toàn: kiểm lại CHÍNH LÀ chạy mã agent
viết dưới `tram-kiem` (`vendor/bin/phpunit` của commit là chương trình tuỳ ý). Ranh giới thật là danh tính đích:
chỉ `tram-kiem` (không root, không user khác), user không credential, không đọc kho trạm. Cơ chế `sandbox` ghim thêm
tiền tố argv cố định `sandbox-exec -f HO_SO_KIEM` — mọi lệnh dưới `tram-kiem` nằm trong hồ sơ cố định do root giữ.
3C-D1 (C01, D45): CẢ HAI cơ chế chạy lệnh của lượt trong `HO_SO_KIEM` (`PrincipalKiem.boc_luot`) — hồ sơ cấm mặc
định, chỉ cho ghi `-D LUOT` (bản chép) và `-D NHA` (nhà của lượt): lượt N không để lại tệp ngoài hai chỗ đó, không tạo
job launchd, không chạy crontab/at/launchctl, không IPC POSIX/SysV, không mạng (DB/Redis dùng chung, cục bộ hay xa).
Cưỡng chế thật của Seatbelt dưới `sudo -u` (setuid, XPC tới launchd) chỉ chứng minh được ở G4.
V2-5 (dot7-Q04): installer ghi kèm hồ sơ một MANIFEST (input của bộ sinh + phiên bản + digest); runtime sinh lại hồ sơ
từ manifest rồi so TOÀN BỘ byte — không tìm chuỗi, không lấy hồ sơ đang kiểm làm mẫu của chính nó."""
import hashlib
import json
import re
from pathlib import Path

from tram.tho.principal import SANDBOX_EXEC, USER_RE
from tram.tho.sandbox import _p
from tram.kiem.toolchain import manifest

THU_MUC_CAI = Path("/usr/local/tram")                 # hồ sơ root:wheel 0644 (cả hai cơ chế — 3C-D5)
HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"
MANIFEST_KIEM = THU_MUC_CAI / "tram-kiem.sb.json"      # root:wheel 0644, cùng sổ cài với hồ sơ (V2-5)
PHIEN_BAN_HO_SO = 3                                   # TĂNG khi chữ của `ho_so_tram_kiem` đổi → bản cài cũ đóng cổng
KHOA_MANIFEST = ("cong", "goc", "nha_quan_ly", "phien_ban", "sha256", "toolchain", "tram_home")
LICH = ("/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/usr/bin/atq", "/usr/bin/atrm", "/bin/launchctl",
        "/usr/bin/osascript", "/usr/bin/open", "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/login", "/usr/bin/security",
        "/usr/bin/defaults")
MACH_CHO = ("com.apple.system.opendirectoryd.libinfo", "com.apple.system.logger", "com.apple.logd",
            "com.apple.system.notification_center", "com.apple.trustd")
KY_TU_DUONG = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/-")
CAM_DOC = ('/Users', '/private/var/root', '/Library/Keychains', '/private/var/db/tram-quan-kiem',
           '/private/var/db/tram-quan-kiem-socket', '/private/var/db/tram-g3-quan-kiem',
           '/private/etc/sudoers', '/private/etc/sudoers.d', '/Library/Application Support/com.apple.TCC',
           '/private/var/db/dslocal')  # CSDL danh tính cục bộ, không phải thư viện chạy toolchain.


def goc_hop_le(p: Path) -> str:
    """Gốc tuyệt đối, đã resolve, chỉ ký tự an toàn để nhúng vào hồ sơ sandbox và lệnh cài."""
    s = str(p)
    if not s.startswith("/") or s == "/" or set(s) - KY_TU_DUONG or str(Path(s).resolve()) != s:
        raise ValueError(f"thu_muc_kiem {s!r}: cần đường dẫn tuyệt đối THẬT (không symlink, không `..`), "
                         "chỉ gồm chữ, số, `._/-`")
    return s


def dong_sudoers_kiem(*, tram: str, tram_kiem: str, co_che: str) -> str:
    """MỘT dòng cho tài khoản trạm: runas CHỈ `tram_kiem`. `SETENV` cần cho `--preserve-env=` của `Principal.boc`
    (đích yếu quyền hơn trạm — biến môi trường không nâng quyền). Cơ chế `sandbox`: ghim tiền tố hồ sơ cố định."""
    if not USER_RE.fullmatch(tram) or not USER_RE.fullmatch(tram_kiem) or tram == tram_kiem:
        raise ValueError("tên user không hợp lệ (tram-kiem phải khác tài khoản trạm)")
    if co_che == "user":
        return f"{tram} ALL=({tram_kiem}) NOPASSWD:SETENV: ALL"
    if co_che == "sandbox":
        return f"{tram} ALL=({tram_kiem}) NOPASSWD:SETENV: {SANDBOX_EXEC} -f {HO_SO_KIEM} *"
    raise ValueError("co_che: user | sandbox")


def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> str:
    """V3: đọc chung trừ chỗ riêng tư; chỉ ghi LUOT/NHA; không mạng trừ unix socket trong LUOT, không IPC.
    `cong` giữ chữ ký T6 (đã bị cấm cùng mọi mạng). Cài root:wheel 0644."""
    g = goc_hop_le(goc)
    cam = " ".join(f'(subpath "{_p(p)}")' for p in (tram_home_tram, nha_quan_ly / ".tram"))
    luot = '(subpath (param "LUOT")) (subpath (param "NHA"))'
    cha = " ".join(f'(literal "{c}")' for c in [*reversed(Path(g).parents[:-1]), g])
    # Lớp 2 sau Unix (phần A), luật sau thắng: đọc chung → cấm riêng tư → LUOT/NHA; metadata cha goc cho realpath/git.
    dong = ["(version 1)", "(deny default)", "(allow process-fork)", "(allow process-exec)", "(allow signal)",
            "(allow process-info*)", "(allow sysctl-read)", "(allow system-socket)",
            '(allow file-read*)', *(f'(deny file-read* (subpath "{p}"))' for p in CAM_DOC),
            f"(deny file-read* {cam})", f'(deny file-read* (subpath "{g}"))', f"(allow file-read* {luot})",
            f"(allow file-read-metadata {cha})", f"(allow file-write* {luot})",
            '(allow file-write-data file-ioctl (literal "/dev/null") (literal "/dev/zero"))',
            "(deny job-creation)", "(deny process-exec " + " ".join(f'(literal "{x}")' for x in LICH) + ")",
            "(allow mach-lookup " + " ".join(f'(global-name "{m}")' for m in MACH_CHO) + ")",
            '(allow network-outbound (remote unix-socket (subpath (param "LUOT"))))']
    return "\n".join(dong) + "\n"


def manifest_ho_so(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> tuple[bytes, bytes]:
    """(hồ sơ, manifest) sinh từ CÙNG một bộ input — installer cài cả hai qua sổ; runtime chỉ tin manifest root."""
    hs = ho_so_tram_kiem(tram_home_tram=tram_home_tram, nha_quan_ly=nha_quan_ly, goc=goc, cong=cong).encode()
    m = {"cong": [int(c) for c in cong], "goc": goc_hop_le(goc), "nha_quan_ly": str(nha_quan_ly),
         "phien_ban": PHIEN_BAN_HO_SO, "sha256": hashlib.sha256(hs).hexdigest(),
         "tram_home": str(tram_home_tram), "toolchain": manifest()}
    return hs, (json.dumps(m, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode()


def _khong_trung(cap: list) -> dict:
    if len({k for k, _ in cap}) != len(cap):
        raise ValueError("khoá trùng")
    return dict(cap)


def ho_so_tu_manifest(du_lieu: bytes) -> tuple[dict, bytes]:
    """Đọc manifest CHẶT (khoá, kiểu, phiên bản mã hiện tại) rồi sinh lại hồ sơ mong đợi; digest ghi trong manifest
    phải bằng digest của bản vừa sinh (bộ sinh đổi mà quên tăng phiên bản cũng bị bắt). Sai → ValueError cố định."""
    try:
        m = json.loads(du_lieu.decode("utf-8"), object_pairs_hook=_khong_trung)
        if not isinstance(m, dict) or tuple(sorted(m)) != KHOA_MANIFEST or type(m["phien_ban"]) is not int:
            raise ValueError
        if not all(isinstance(m[k], str) for k in ("goc", "nha_quan_ly", "sha256", "tram_home")):
            raise ValueError
        if not isinstance(m["cong"], list) or not all(type(c) is int and 0 < c < 65536 for c in m["cong"]):
            raise ValueError
        if m["toolchain"] != manifest():
            raise ValueError
        if m["phien_ban"] != PHIEN_BAN_HO_SO or not re.fullmatch(rf"/Users/{USER_RE.pattern}", m["nha_quan_ly"]):
            raise ValueError
        hs = ho_so_tram_kiem(tram_home_tram=Path(m["tram_home"]), nha_quan_ly=Path(m["nha_quan_ly"]),
                             goc=Path(m["goc"]), cong=m["cong"]).encode()
    except (ValueError, TypeError, UnicodeDecodeError):
        raise ValueError("manifest hồ sơ sai dạng hoặc khác phiên bản mã — cài lại (`tram chu cai-dat-tho`)") from None
    if hashlib.sha256(hs).hexdigest() != m["sha256"]:
        raise ValueError("manifest hồ sơ ghi digest khác bản sinh từ mã hiện tại — cài lại (`tram chu cai-dat-tho`)")
    return m, hs
