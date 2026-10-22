"""`tram chu go-cai-dat-tho` — hoàn tác `cai-dat-tho` (lát 3c R2, bs-urj.14; Codex F02; R4/R5 review đợt 5). Ở TÀI
KHOẢN TRẠM, giữ khoá sổ suốt lần gỡ, in kế hoạch rồi chờ `dong-y`. CHỈ gỡ thứ sổ ghi `da_tao` VÀ còn đúng định danh
(user: UID + GeneratedUID; file: sha256; thư mục, nhà: inode); quan sát lại trước/sau mỗi bước, hết hẳn mới `da_go`;
bước lỗi chỉ cảnh báo. User luôn `-deleteUser -keepHome`; nhà là bước riêng chỉ khi `--xoa-nha` (D40), sau khi user đã
gỡ. Thứ tự: đối soát → daemon → file root → thư mục kiểm (tram-kiem tự xoá) → user → nhà → thư mục root."""
import subprocess
from collections.abc import Callable

from tram.chu import dinh_danh
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_tho import DAEMON, NHAN_THO
from tram.chu.so_cai_tho import Muc, SoCai, doi_soat
from tram.tho.principal import USER_RE

TEN = USER_RE                                        # cùng luật với lúc cài (`lap_ke_hoach_tho`)


def _thu_tu(m: Muc) -> int:
    if m.kieu == "acl_search":
        return 1
    if m.kieu == "tep":
        return 0 if m.ten == str(DAEMON) else 1
    return {"user": 3, "nha": 4, "nhom": 6}.get(m.kieu, 2 if m.mong.get("chu") else 5)


def _hop_le(m: Muc) -> bool:
    """Trường của sổ đi vào lệnh sudo: tên user/chủ đúng dạng, đường dẫn tuyệt đối không `..`, nhà là /Users/<user>."""
    if m.kieu in ("user", "nhom"):
        return bool(TEN.fullmatch(m.ten))
    chu, u = m.mong.get("chu"), m.mong.get("user", "")
    ok = m.ten.startswith("/") and m.ten.count("/") >= 2 and ".." not in m.ten.split("/") and chu != "root" \
        and (not chu or TEN.fullmatch(chu))
    return bool(ok) and (m.kieu != "nha" or bool(TEN.fullmatch(u)) and m.ten == f"/Users/{u}")


def lenh_go(m: Muc) -> list[list[str]]:
    if m.kieu == "acl_search":
        return [["sudo", "/bin/chmod", "-a", "user:tram-tho allow search", m.ten]]
    if m.kieu == "nhom":
        return [["sudo", "/usr/sbin/dseditgroup", "-o", "delete", m.ten]]
    if m.kieu == "user":
        return [["sudo", "pkill", "-KILL", "-u", m.ten], ["sudo", "sysadminctl", "-deleteUser", m.ten, "-keepHome"]]
    if m.kieu == "nha":
        return [["sudo", "rm", "-rf", m.ten]]
    if m.kieu == "tep":
        dung = [["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"]] if m.ten == str(DAEMON) else []
        return dung + [["sudo", "rm", "-f", m.ten]]
    chu = m.mong.get("chu")
    return [["sudo", "-u", chu, "/bin/rm", "-rf", m.ten]] if chu else [["sudo", "rmdir", m.ten]]


def go(so: SoCai, m: Muc, *, quan_sat: Callable, chay: Callable, bao: Callable[[str], None]) -> bool:
    hien = quan_sat(m.kieu, m.ten)
    if hien is None:                                 # đã không còn: khép bản ghi da_tao
        for x in so.da_tao(m.kieu, m.ten):
            so.ket(x.id, "da_go", ly_do="quan sát: không còn")
        return True
    cua_tram = [x for x in so.da_tao(m.kieu, m.ten) if dinh_danh.cung(m.kieu, x.dinh_danh, hien)]
    if not cua_tram:
        bao(f"Bỏ qua {m.kieu} {m.ten}: định danh hiện tại không khớp sổ (có sẵn, bị xoá-tạo lại hoặc bị sửa)")
        return False
    if m.kieu == "user" and (con := [x.ten for x in so.muc().values() if x.su == "da_tao" and x.kieu == "thu_muc"
                                    and x.mong.get("chu") == m.ten and quan_sat("thu_muc", x.ten) is not None]):
        bao(f"Bỏ qua user {m.ten}: thư mục của nó chưa gỡ được ({', '.join(con)}) — không để thư mục mồ côi UID")
        return False
    if m.kieu == "nha" and quan_sat("user", m.mong["user"]) is not None:
        bao(f"Bỏ qua nha {m.ten}: user {m.mong['user']} vẫn còn — chỉ xoá nhà sau khi đã gỡ user")
        return False
    if m.kieu == "nhom" and quan_sat("user", m.ten) is not None:
        bao(f"Giữ nhóm {m.ten}: user vẫn còn")
        return False
    for c in lenh_go(m):
        chay(c, check=False)
    if quan_sat(m.kieu, m.ten) is not None:
        bao(f"Chưa gỡ được {m.kieu} {m.ten} (vd thư mục không rỗng) — Đại ca xem tay; sổ giữ nguyên")
        return False
    for x in cua_tram:
        so.ket(x.id, "da_go")
    return True


def lap_ke_hoach_go(so: SoCai, *, toi: str, quan_sat: Callable | None = None, chay: Callable = subprocess.run,
                    xoa_nha: bool = False, bao: Callable[[str], None] = print) -> KeHoach:
    """`buoc` rỗng = không còn gì để gỡ. Sổ hỏng hoặc trường sổ sai dạng → ValueError."""
    quan_sat = quan_sat or dinh_danh.quan_sat_that
    muc = so.muc().values()
    if not all(_hop_le(m) for m in muc):
        raise ValueError(f"Sổ cài đặt {so.p} hỏng (tên/đường dẫn sai dạng) — không gỡ gì, Đại ca kiểm tay")
    nhom = {(m.kieu, m.ten): m for m in muc if m.su in ("du_dinh", "da_tao")}
    canh_bao = [f"Không gỡ user {toi}: là tài khoản đang chạy lệnh này" for k, t in nhom if (k, t) == ("user", toi)]
    ds = sorted((m for m in nhom.values() if (m.kieu, m.ten) != ("user", toi) and m.mong.get("user") != toi
                 and (xoa_nha or m.kieu != "nha") and (m.su == "da_tao" or quan_sat(m.kieu, m.ten, nhe=True))),
                key=_thu_tu)                         # da_tao đã mất: bước gỡ chỉ khép bản ghi (da_go)
    buoc = [("Đối soát sổ cài đặt (khép bản ghi dở do crash)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    if not ds and all(m.su != "du_dinh" for m in muc):
        return KeHoach(tep={}, lenh=[], canh_bao=canh_bao)
    buoc += [(f"Gỡ {m.kieu} {m.ten} nếu còn đúng định danh trong sổ: " + " && ".join(" ".join(c) for c in lenh_go(m)),
              lambda m=m: go(so, m, quan_sat=quan_sat, chay=chay, bao=bao)) for m in ds]
    canh_bao += [f"Thư mục nhà của user được {'XOÁ (sau khi gỡ user)' if xoa_nha else 'giữ (--xoa-nha để xoá)'} (D40).",
                 "Token máy B ở trạm vẫn hiệu lực — thu hồi bằng `tram chu go-may B` nếu không cài lại.",
                 f"Sổ {so.p} được giữ (ghi thêm da_go). Chạy lại lệnh này để xem còn gì (đối soát có thể mở thêm)."]
    return KeHoach(tep={}, lenh=[], canh_bao=canh_bao, buoc=buoc)


def lenh_cli(args, *, hoi: Callable) -> int:
    """Giữ đường gọi cũ; import trễ để không tạo vòng với lenh_go_tho."""
    from tram.chu.lenh_go_tho import lenh_cli as chay
    return chay(args, hoi=hoi)
