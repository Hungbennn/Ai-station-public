"""Kế hoạch cài memory service — `tram chu cai-dat --nho` (spec 1b §15). Liệt kê trước, chờ `dong-y` (Q15).

Quyết định #5 (cài Ollama + bge-m3, dịch vụ vn.tram.nho) CHƯA DUYỆT: mã có sẵn, chạy thật chờ Đại ca.
bs-2bd.1.23 (R2-09): mọi lệnh và bước đều có hạn — `security -i` tạo token `HAN_GIAY` của Keychain, tải/cài `HAN_NHO`
riêng theo loại, còn lại (`mkdir`, `launchctl`) `HAN_LENH_GIAY`. Quá hạn → dừng, lệnh sau không chạy, không tạo lại."""
import os
import secrets
import shutil
import subprocess
from functools import partial
from pathlib import Path

from tram.chu.cai_dat import KeHoach, _co_keychain
from tram.chu.dich_vu_tram import HAN_LENH_GIAY, LoiCaiDat, bien_nhan
from tram.chu.launchd import NHAN_API, NHAN_NHO, tao_plist_thuong_truc
from tram.duong_dan import tram_home
from tram.keychain import HAN_GIAY
from tram.nho.embed import TEN_MO_HINH
from tram.nho.khach import KEYCHAIN_NHO
from tram.api.noi_bo import KEYCHAIN_NOI_BO

HAN_NHO = {("brew", "install"): 1800.0, ("brew", "services"): 60.0, ("ollama", "pull"): 3600.0}   # đo lại ở cổng


def tao_token_nho(*, dich_vu: str = KEYCHAIN_NHO, co=_co_keychain, chay=None) -> bool:
    """Tạo token ngẫu nhiên (`tram-nho-token`; 1b-2: cả `tram-noi-bo-token`) nếu chưa có; trả True khi vừa tạo.
    Token đi qua stdin của `security -i` (G13: không bao giờ nằm trong đối số dòng lệnh — `ps` thấy được);
    không in, không ghi file. Có hạn `HAN_GIAY`: quá hạn → `subprocess.TimeoutExpired`, không thử tạo lại."""
    if co(dich_vu):
        return False
    token = secrets.token_hex(32)                    # chỉ [0-9a-f]: không cần thoát trong dòng lệnh của security -i
    (chay or subprocess.run)(["security", "-i"], input=f"add-generic-password -s {dich_vu} -a tram -w {token}\n",
                             text=True, check=True, capture_output=True, timeout=HAN_GIAY)
    if not co(dich_vu):                              # security -i có thể trả 0 dù lệnh con lỗi
        raise LoiCaiDat(f"Không tạo được Keychain {dich_vu}")
    return True


def _canh_bao_nho() -> list[str]:
    return [
        "Quyết định #5 (cài Ollama + bge-m3, dịch vụ vn.tram.nho) CHƯA DUYỆT — chỉ gõ dong-y khi Đại ca đã duyệt.",
        f"`ollama pull {TEN_MO_HINH}` tải model từ registry của Ollama một lần lúc cài; lúc chạy chỉ gọi 127.0.0.1.",
        "Ollama phải chỉ nghe 127.0.0.1 (mặc định của brew services). Kiểm sau khi cài: "
        "lsof -nP -iTCP:11434 -sTCP:LISTEN — thấy *:11434 thì dừng và báo.",
        "Memory service đọc thêm Keychain tram-anthropic-api-key (tách/gộp bằng claude-haiku-5-5).",
        "Kiểm sau khi cài: tram nho tim \"thử\" --du-an <tên> ; log ở ~/.tram/log/nho.log",
        "Keychain còn khoá trước khi đăng nhập màn hình (sau khởi động máy) → dịch vụ không đọc được token và tự "
        f"dừng; đăng nhập xong chạy: launchctl kickstart -k gui/{os.getuid()}/{NHAN_NHO}",
        f"1b-2: memory service tra phiếu của CLI máy thợ qua tram-api bằng Keychain {KEYCHAIN_NOI_BO}. tram-api đọc "
        f"token này một lần ở yêu cầu đầu tiên — nếu tram-api đang chạy: launchctl kickstart -k gui/{os.getuid()}/"
        f"{NHAN_API}",
        "Phiên tay của Đại ca (máy A) cần mã Đại ca: tạo trên máy A (#5 chưa duyệt) rồi chạy trên máy B "
        "`tram chu dat-ma-dai-ca`. Chưa đặt mã thì mọi phiên tay bị từ chối.",
        "MCP qua tailnet cần `tailscale serve` thêm đường /nho → http://127.0.0.1:7710 — chờ spike N2, Đại ca tự chạy.",
    ]


def lap_ke_hoach_nho(*, uv: str, repo: Path) -> KeHoach:
    la = Path(os.environ["HOME"]) / "Library/LaunchAgents"
    log, plist = tram_home() / "log", la / f"{NHAN_NHO}.plist"
    tep = {plist: tao_plist_thuong_truc(NHAN_NHO, ["nho", "chay"], uv=uv, repo=repo, log=log / "nho.log")}
    tep.update([bien_nhan(NHAN_NHO, plist, tep[plist])])         # bs-2bd.1.17: chứng cứ sở hữu cho go-dich-vu
    lenh = [["mkdir", "-p", str(log), str(tram_home() / "nho")]]
    if not shutil.which("ollama"):
        lenh += [["brew", "install", "ollama"], ["brew", "services", "start", "ollama"]]
    lenh += [["ollama", "pull", TEN_MO_HINH]]
    mien = f"gui/{os.getuid()}"
    lenh += [["launchctl", "bootout", f"{mien}/{NHAN_NHO}"], ["launchctl", "bootstrap", mien, str(plist)]]
    buoc = [(f"Tạo Keychain {KEYCHAIN_NHO} (ngẫu nhiên, không in ra) nếu chưa có", tao_token_nho),
            (f"Tạo Keychain {KEYCHAIN_NOI_BO} (ngẫu nhiên, không in ra) nếu chưa có — tra phiếu cho MCP (1b-2)",
             partial(tao_token_nho, dich_vu=KEYCHAIN_NOI_BO))]
    return KeHoach(tep=tep, lenh=lenh, canh_bao=_canh_bao_nho(), buoc=buoc, han_lenh=HAN_LENH_GIAY, han_rieng=HAN_NHO)
