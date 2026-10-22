"""Kiểm chứng âm H9 (spec 3 §7.3 mục 7, §9.3): chạy từng thăm dò DƯỚI principal (`boc`) và đòi nó BỊ CHẶN; hai thăm
dò dương (lệnh hợp lệ chạy được, ghi được thư mục của chính nó) để "chặn hết" không do principal hỏng. Chạy thật cần
cổng S6 (user/sandbox đã tạo); test chỉ chạy với `boc` giả. Thăm dò ghi cố định trong mã — không nhận lệnh từ ngoài.
Review vòng 1 A04: mỗi `kieu` một bằng chứng riêng + đối chứng mục tiêu dưới quản lý (`cham_tham_do`); kết quả chỉ mang
lý do cố định, không chép đầu ra. Đọc thư mục bằng `ls` (cat thư mục luôn lỗi — không phải bằng chứng bị chặn).
bs-863.14: mọi thăm dò qua primitive P1 (`chay_gioi_han`: hạn tuyệt đối, thu hồi cả cây bằng `kill` CỦA PRINCIPAL —
không `wait()` trần). Dương chạy TRƯỚC; một dương hỏng → mọi âm "không kết luận" (không chạy). Lỗi hạ tầng (quá hạn,
không khởi chạy) không bao giờ thành "bị chặn"; chưa thu hồi được (`LoiThuHoi`) → dừng, phần còn lại không chạy."""
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import Kill, LoiThuHoi
from tram.tho.cham_tham_do import cham, co_muc_keychain, mo_cong

HUONG_DAN_SUDO = (" Nếu sudo cần mật khẩu, người vận hành chạy `sudo -v` trong Terminal rồi chạy lại. "
                  "Nếu vẫn lỗi, kiểm quyền sudo đã cấp; trạm không nhận hay lưu mật khẩu.")

HOOK = ("set -e; d=$(mktemp -d); cd \"$d\"; git init -q; mkdir -p .git/hooks; "
        "printf '#!/bin/sh\\ntouch \"$0.da-chay\"\\n' > .git/hooks/pre-commit; chmod +x .git/hooks/pre-commit; "
        "git -c core.hooksPath=/dev/null -c user.name=k -c user.email=k@k commit -q --allow-empty -m k; "
        "test ! -e .git/hooks/pre-commit.da-chay")


@dataclass(frozen=True)
class ThamDo:
    ten: str
    argv: list[str]
    kieu: str                                   # doc | ghi | sua | keychain | http | nc | tram | ok (cham_tham_do)
    doi_chung: Callable[[], bool] | None = field(default=None, compare=False)      # dưới quản lý: đích CÓ thật


@dataclass(frozen=True)
class KetQuaThamDo:
    ten: str
    dat: bool
    chi_tiet: str


def _doc(p: Path) -> ThamDo:
    argv = ["/bin/ls", str(p)] if p.is_dir() else ["/bin/cat", str(p)]
    return ThamDo(f"đọc {p}", argv, "doc", partial(p.exists))


def tham_do_khe(*, keychain: list[str], doc_cam: list[Path], ghi_cam: list[Path], ghi_duoc: Path,
                ghi_tep_cam: list[Path] = (), co_muc: Callable[[str], bool] = co_muc_keychain) -> list[ThamDo]:
    """Bản rút gọn cho `tram tho kiem`: Keychain, file/thư mục của tiến trình quản lý và khe khác, file cấu hình của
    kho (`ghi_tep_cam` — `touch -c` không tạo file mới), + hai dương."""
    ds = [ThamDo(f"đọc Keychain {k}", ["/usr/bin/security", "find-generic-password", "-s", k, "-w"], "keychain",
                 partial(co_muc, k)) for k in keychain]
    ds += [_doc(p) for p in doc_cam]
    ds += [ThamDo(f"ghi vào {p}", ["/usr/bin/touch", str(p / ".tram-kiem-am")], "ghi", partial(p.is_dir))
           for p in ghi_cam]
    ds += [ThamDo(f"sửa {p}", ["/usr/bin/touch", "-c", str(p)], "sua", partial(p.is_file)) for p in ghi_tep_cam]
    return ds + [ThamDo("lệnh hợp lệ chạy được", ["/usr/bin/true"], "ok"),
                 ThamDo(f"ghi được {ghi_duoc}", ["/usr/bin/touch", str(ghi_duoc / ".tram-kiem-duong")], "ok")]


def tham_do_api_db(*, api: str, dai_ca_login: str, may_b: str, db: list[str],
                   mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
    """Gọi API Duyệt với header danh tính giả (login THẬT của Đại ca + Origin máy B: chỉ bị chặn khi kênh ghi thật sự
    tách) và kết nối DB nghiệp vụ — chung cho `tram chu kiem-cach-ly` (`tram-kiem`) và `tram tho kiem` (khe, D54)."""
    ds = [ThamDo("API Duyệt với header danh tính giả", [
        "/usr/bin/curl", "-q", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
        "-H", "Content-Type: application/json", "-H", f"Tailscale-User-Login: {dai_ca_login}", "-H", "X-Tram: 1",
        "-H", f"Origin: https://{may_b}", "--data", "{}", f"{api}/api/phe-duyet/kiem-am/kiem-am/duyet"], "http")]
    return ds + [ThamDo(f"kết nối DB nghiệp vụ {d}", ["/usr/bin/nc", "-z", "-G", "3", *d.rsplit(":", 1)], "nc",
                        partial(mo, d)) for d in db]


def tham_do_day_du(*, rut_gon: list[ThamDo], api: str, dai_ca_login: str, may_b: str, db: list[str],
                   tram_home_tram: Path | None, mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
    """Bộ đủ §7.3 mục 7: + API Duyệt giả danh, DB nghiệp vụ (`tham_do_api_db`), `tram` khi xoá `TRAM_GIAO_ID` trỏ vào
    kho của trạm, git hook trong repo."""
    ds = list(rut_gon) + tham_do_api_db(api=api, dai_ca_login=dai_ca_login, may_b=may_b, db=db, mo=mo)
    if tram_home_tram is not None:
        ds.append(ThamDo("tram khi xoá TRAM_GIAO_ID, trỏ kho trạm", [
            "/usr/bin/env", "-u", "TRAM_GIAO_ID", f"TRAM_HOME={tram_home_tram}", "tram", "chu", "trang-thai"], "tram",
            partial(tram_home_tram.exists)))
    return ds + [ThamDo("git hook trong repo không chạy", ["/bin/sh", "-c", HOOK], "ok")]


def _doi_chung(t: ThamDo) -> bool:
    try:
        return t.doi_chung is None or t.doi_chung() is True
    except Exception:                                   # noqa: BLE001 — đối chứng hỏng = không chứng minh được đích
        return False


def chay_tham_do(ds: list[ThamDo], *, boc: Callable[[list[str]], list[str]], env: dict[str, str], kill: Kill,
                 timeout: float = 30, chay: Callable = chay_gioi_han) -> list[KetQuaThamDo]:
    ra: dict[int, KetQuaThamDo] = {}
    dung = None
    for i in sorted(range(len(ds)), key=lambda i: ds[i].kieu != "ok"):          # dương trước, giữ thứ tự trong nhóm
        t = ds[i]
        if dung is None and t.kieu != "ok" and not all(ra[j].dat for j in ra if ds[j].kieu == "ok"):
            dung = "không kết luận: thăm dò dương hỏng — principal/sandbox không chạy được lệnh hợp lệ"
        if dung is not None or not _doi_chung(t):
            ra[i] = KetQuaThamDo(t.ten, False, dung or "không kết luận: đối chứng hỏng — đích không có/không kiểm được")
            continue
        try:
            kq = chay(boc(t.argv), kill=kill, capture_output=True, text=True, timeout=timeout, env=env)
            kl, ly = cham(t.kieu, kq.returncode, (kq.stdout or "").strip(), kq.stderr or "")
        except LoiThuHoi:
            kl, ly = "khong-ket-luan", "không xác nhận thu hồi tiến trình thăm dò"
            dung = "không chạy: thăm dò trước chưa thu hồi được — kiểm principal"
        except (OSError, subprocess.SubprocessError, ValueError) as e:
            kl, ly = "khong-ket-luan", f"lỗi hạ tầng ({type(e).__name__})"
        ly += HUONG_DAN_SUDO if kl != "dat" else ""
        ra[i] = KetQuaThamDo(t.ten, kl == "dat", ly if kl != "khong-ket-luan" else f"không kết luận: {ly}")
    return [ra[i] for i in range(len(ds))]
