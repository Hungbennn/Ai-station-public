"""Principal kiểm lại của trạm `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1, 4) — chờ spike S6.

Lát 3c: MỘT nguồn khai báo — `cach_ly.tram_kiem: user:<tên> | sandbox:<tên>` (cùng cú pháp principal khe, 3a-2 G3;
đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem`). `tu_cach_ly` dựng argv từ `Principal` của 3a-2 — không
còn argv tự do trong cấu hình: `boc` = `sudo -n -H -u <tên> --preserve-env=… --` (cơ chế sandbox thêm `sandbox-exec -f
HO_SO_KIEM`), khớp dòng sudoers `dong_sudoers_kiem`. D22: không trao/thu quyền — `tram-kiem` sở hữu bản chép
(`ban_chep.py`). Thu hồi giữa các lượt: `cong_that.thu_hoi_theo_uid` (3C-D5) — không còn `crontab -r`/`pkill` ngầm."""
import signal
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.lenh_ngan import chay_ngan
from tram.kiem.toolchain import bien_kiem
from tram.tho.principal import SANDBOX_EXEC, doc_principal
from tram.tho.quyen_kiem import HO_SO_KIEM

ENV = "/usr/bin/env"
KHONG_LUOT = ("-D", "LUOT=/var/empty", "-D", "NHA=/var/empty")


@dataclass(frozen=True)
class PrincipalKiem:
    ten: str
    boc: tuple[str, ...]
    co_che: str = "user"

    def boc_lenh(self, argv: list[str]) -> list[str]:
        """Tham số `boc` của `chay_mot_lenh`/`kiem_lai` (3a-1): argv chạy dưới `tram-kiem`, không qua shell. Cơ chế
        sandbox: hồ sơ ghim ở sudoers cần tham số — ngoài lượt cho `/var/empty` (root, không ghi được)."""
        return [*self.boc, *(KHONG_LUOT if self.co_che == "sandbox" else ()), *argv]

    def boc_luot(self, wt: Path) -> Callable[[list[str]], list[str]]:
        """3C-D1: `boc` của MỘT lượt — mọi lệnh trong `HO_SO_KIEM` với `-D LUOT=<bản chép> -D NHA=<bản chép>.nha`, chạy
        qua `env HOME=<NHA> TMPDIR=<NHA>/tmp/` (HOME/TMP riêng mỗi lượt, D45). Cơ chế sandbox đã có tiền tố hồ sơ (ghim
        ở sudoers) nên chỉ thêm tham số; không lồng sandbox-exec hai lần."""
        nha = f"{wt}.nha"
        ho_so = [] if self.co_che == "sandbox" else [SANDBOX_EXEC, "-f", str(HO_SO_KIEM)]
        dau = [*self.boc, *ho_so, "-D", f"LUOT={wt}", "-D", f"NHA={nha}", ENV, f"HOME={nha}", f"TMPDIR={nha}/tmp/"]
        dau += [f"{k}={v}" for k, v in bien_kiem(nha).items()]
        return lambda argv: [*dau, *argv]

    def kill_nhom(self, pgid: int, sig: int) -> None:
        """P1 (H2): gửi tín hiệu cho cả nhóm DƯỚI `tram-kiem`, hạn TUYỆT ĐỐI 5 s (`chay_ngan`) — không `run(timeout)`.
        Kết quả gửi không là bằng chứng: `vong_doi.thu_hoi` tự chụp cây để xác nhận."""
        chay_ngan(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"), "--", f"-{pgid}"]),
                  timeout=5)


def tu_cach_ly(chuoi: str) -> PrincipalKiem:
    """`cach_ly.tram_kiem` → PrincipalKiem. Sai dạng → `ChuaCoPrincipal` (ValueError)."""
    p = doc_principal(chuoi)
    if p.co_che == "sandbox":
        p = p.voi_ho_so(HO_SO_KIEM)
    return PrincipalKiem(p.user, tuple(p.boc([])), p.co_che)
