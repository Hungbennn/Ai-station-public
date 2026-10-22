"""Kế hoạch cài máy thợ B — `tram chu cai-dat-tho` (spec 3 §5.1, §7.3, §9; Q15: liệt kê trước, chờ `dong-y`). Chạy ở
TÀI KHOẢN TRẠM (Đại ca, quyền admin — các lệnh `sudo` hỏi mật khẩu trong Terminal). CƠ CHẾ CÁCH LY CHƯA CHỐT (§14 —
chốt sau S6): `--co-che user` (user macOS mỗi khe) hay `sandbox` (một user thực thi chung + sandbox). Cú pháp
`sysadminctl`, sudoers, LaunchDaemon có `UserName` và việc Keychain của user dịch vụ đọc được dưới launchd — CHỜ S2, S6.
File cần quyền root được soạn trong `~/.tram/cai-dat-tho/` rồi `sudo install`; sudoers kiểm bằng `visudo -cf` trước.
Lát 3c: principal kiểm lại đọc từ MỘT nguồn (`doc_principal_kiem`, không còn cờ `--tram-kiem`); D22: không dòng
sudoers root, không helper. R2: mọi user/file/thư mục đi qua `tai_nguyen.py` — có sổ `so-cai.jsonl` (du_dinh trước
lệnh, da_tao kèm định danh sau quan sát), thứ đã có mà sổ không ghi thì từ chối cài."""
import plistlib
import subprocess
from functools import partial
from pathlib import Path

from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_kiem import NHA_KIEM, phan_kiem, tep_root
from tram.chu import dinh_danh
from tram.chu.launchd import PATH_HE_THONG
from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user, lenh_bo_nhom, NHOM_THUA, NHOM_NEN, nhom_phu
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, nha_tram, tao
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.principal import USER_RE
from tram.tho.quyen_kiem import dong_sudoers_kiem

NHAN_THO = "vn.tram.tho"
SUDOERS = Path("/etc/sudoers.d/tram-tho")
DAEMON = Path(f"/Library/LaunchDaemons/{NHAN_THO}.plist")


def noi_dung_sudoers(*, quan_ly: str, principal: list[str], tram: str, kiem: PrincipalKiem | None) -> bytes:
    dong = ["# Sinh bởi `tram chu cai-dat-tho` (spec 3 §7.3) — chỉ cho chạy lệnh DƯỚI principal không credential.",
            f"{quan_ly} ALL=({','.join(sorted(set(principal)))}) NOPASSWD:SETENV: ALL"]
    # D159/D160: quyền kiểm chỉ do trình cài Uq quản lý; không cấp lại 501→503.
    return ("\n".join(dong) + "\n").encode()


def plist_tho(*, uv: str, repo: Path, quan_ly: str) -> bytes:
    nha = f"/Users/{quan_ly}"
    return plistlib.dumps({
        "Label": NHAN_THO, "UserName": quan_ly,
        "ProgramArguments": [uv, "run", "--offline", "--no-sync", "--project", str(repo), "tram", "tho", "chay"],
        "WorkingDirectory": str(repo), "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False},
        "StandardOutPath": f"{nha}/.tram/log/tho.log", "StandardErrorPath": f"{nha}/.tram/log/tho.log",
        "EnvironmentVariables": {"PATH": f"{nha}/.local/bin:{PATH_HE_THONG}", "HOME": nha}})


def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[str, str], co_che: str,
                     kiem: PrincipalKiem | None = None, thu_muc_kiem: Path | None = None,
                     db_nghiep_vu: tuple[str, ...] = (), so: SoCai | None = None, quan_sat=None,
                     chay=subprocess.run, chi_tho: bool = False, giu_tat: bool = False) -> KeHoach:
    """`khe`: tên khe → user principal (cơ chế `sandbox`: mọi khe cùng một user). `tram`: user macOS của tài khoản
    trạm (chủ tram-api). `kiem`, `thu_muc_kiem`: từ `doc_principal_kiem()` và `giao_viec.thu_muc_kiem`."""
    if co_che not in ("user", "sandbox"):
        raise ValueError("--co-che user | sandbox (Đại ca chốt sau S6)")
    if la := [u for u in (*khe.values(), quan_ly) if not USER_RE.fullmatch(u)]:
        raise ValueError(f"tên user không hợp lệ (cần [a-z_][a-z0-9_-]*, gỡ được về sau): {', '.join(la)}")
    if co_che == "user" and (len(set(khe.values())) != len(khe) or
                             set(khe.values()) & {tram, quan_ly, "tram-kiem", "tram-quan-kiem"}):
        raise ValueError("Mỗi khe cần user riêng, khác trạm và phần kiểm")
    if chi_tho:
        kiem, thu_muc_kiem, db_nghiep_vu = None, None, ()
    chay = partial(chay, timeout=30)
    soan, so, quan_sat = tram_home() / "cai-dat-tho", so or SoCai(), quan_sat or dinh_danh.quan_sat_that
    pk = phan_kiem(kiem=kiem, thu_muc_kiem=thu_muc_kiem, co_che=co_che, tram=tram, quan_ly=quan_ly, soan=soan,
                   khe=tuple(khe.values()), db_nghiep_vu=db_nghiep_vu, quan_sat=quan_sat)
    sud = noi_dung_sudoers(quan_ly=quan_ly, principal=list(khe.values()), tram=tram, kiem=kiem)
    pl = plist_tho(uv=uv, repo=repo, quan_ly=quan_ly)
    tep = {soan / "tram-tho.sudoers": sud, soan / f"{NHAN_THO}.plist": pl, **pk.tep}
    nguoi = sorted(set(khe.values()) | ({kiem.ten} if kiem else set()) | {quan_ly})
    ds = [nhom_tram(u) for u in nguoi]
    ds += [user_nhom(u, NHA_KIEM if kiem and u == kiem.ten else f"/Users/{u}", so, quan_sat) for u in nguoi]
    ds += [nha_tram(u, so, quan_sat) for u in nguoi if not (kiem and u == kiem.ten)]
    ds += [*pk.tai_nguyen,
          tep_root(soan / "tram-tho.sudoers", SUDOERS, sud, "0440",
                   truoc=(("sudo", "visudo", "-cf", str(soan / "tram-tho.sudoers")),)),
          tep_root(soan / f"{NHAN_THO}.plist", DAEMON, pl, "0644")]
    viec = kiem_truoc(so, ds, quan_sat=quan_sat)
    for u in nguoi:
        if quan_sat('user', u) is not None and nhom_phu(u, chay=chay) - {u} - NHOM_NEN:
            raise ValueError('User cũ còn nhóm ngoài: chạy migration có audit/rollback trước cài lại')
    buoc = [("Đối soát sổ cài đặt (bản ghi dở dang của lần trước)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    buoc += [(f"[{v}] {tn.kieu} {tn.ten}: {tn.mo_ta()}", lambda tn=tn: tao(so, tn, quan_sat=quan_sat, chay=chay))
             for tn, v in zip(ds, viec)]
    siet = [(f"Siết {u}: sudo dscl . -create /Users/{u} PrimaryGroupID <gid:{u}>; "
             + "; ".join(" ".join(c) + " (nếu là thành viên)" for c in lenh_bo_nhom(u, NHOM_THUA)),
             lambda u=u: siet_user(u, so, quan_sat, chay=chay)) for u in nguoi]
    buoc[1 + 2 * len(nguoi):1 + 2 * len(nguoi)] = siet
    lenh = [["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"], ["sudo", "launchctl", "bootstrap", "system",
                                                                    str(DAEMON)]]
    canh_bao = [
        "Cơ chế cách ly CHƯA CHỐT (§14): chỉ gõ dong-y khi Đại ca đã chốt sau spike S6 — "
        "tạo user là thay đổi hệ thống.",
        "Token máy B: ghi file riêng của quản lý qua stdin (token không hiện ra màn hình): "
        f"tram chu cap-token-may B --dong-y | sudo -u {quan_ly} -H {uv} run --project {repo} "
        "tram tho nhan-token --may-b",
        "Mỗi khe: Đại ca tự đăng nhập Claude dưới đúng principal (S2): sudo -u <principal> -H env "
        "CLAUDE_CONFIG_DIR=<thu_muc_cau_hinh> claude — hoặc claude setup-token nếu S2 buộc dùng token.",
        f"Viết ~/.tram/tho.yaml của {quan_ly} (spec 3 §9.1) với principal: {co_che}:<user> và khoá chay.day "
        "(khớp cong_bo.phuong_an của trạm — chốt sau S7). Kiểm: tram tho kiem (mọi mục xanh) và "
        "tram chu kiem-cach-ly (H9) TRƯỚC khi bật 3a.",
        "launchd: B dùng token file riêng theo QĐ2 sửa 21/10; S2/R5 phải đo FD và reboot không mở Keychain.",
        f"Sổ {so.p}: chỉ ghi thêm. S6 hỏng → `tram chu go-cai-dat-tho` chỉ gỡ thứ sổ ghi da_tao VÀ còn đúng định "
        "danh (user: UID + GeneratedUID; file: sha256) — in kế hoạch, chờ dong-y."]
    return KeHoach(tep=tep, lenh=[] if giu_tat else lenh, canh_bao=canh_bao + pk.canh_bao,
                  buoc=buoc, han_lenh=30)
