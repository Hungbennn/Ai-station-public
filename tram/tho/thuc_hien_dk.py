"""Thực hiện kế hoạch `tram tho dang-ky` (spec 3 §9.2) — CHỈ gọi sau khi Đại ca gõ `dong-y`.

Thứ tự: đổi mã ghép (dùng một lần) → Keychain → `tho.yaml` → file (config.toml của khe Codex, plist) → lệnh MCP của
Claude → đăng ký khe với trạm → nạp launchd (cuối cùng). Lỗi giữa chừng thì dừng; chạy lại cần mã ghép MỚI, và nếu
máy đã nhận token thì `tram chu go-may <máy>` ở trạm trước. Token chỉ nằm trong bộ nhớ và Keychain."""
import os
import subprocess
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.ke_hoach_dk import KeHoachDangKy
from tram.tho.khach import KhachTram, LoiKhachTram
from tram.tho.khai_khe import noi_dung_tho_yaml
from tram.tho.token_may import ghi_token_may


@dataclass
class HieuUng:
    ghep: Callable[[str, str], tuple[str, str]]               # (tram_chu, ma) -> (may_id, token)
    ghi_token: Callable[[str, str], None]                     # (may_id, token)
    dang_ky: Callable[[str, str, str, list[dict]], None]      # (tram_chu, may_id, token, khe)
    chay: Callable = subprocess.run


def ghep_that(tram_chu: str, ma: str, *, mo=urllib.request.urlopen) -> tuple[str, str]:
    ma_http, kq = KhachTram(tram_chu, "", mo=mo).goi("POST", "/api/ghep-may", {"ma": ma}, xac_thuc=False)
    if ma_http != 200:
        raise LoiKhachTram(f"trạm từ chối mã ghép ({ma_http}): {str(kq.get('loi', ''))[:120]}")
    return str(kq.get("may_id", "")), str(kq.get("token", ""))


def dang_ky_that(tram_chu: str, may_id: str, token: str, khe: list[dict], *, mo=urllib.request.urlopen) -> None:
    than = {"may_id": may_id, "khe": [{k: x[k] for k in ("ten", "cli", "ten_goi_nho", "vai_uu_tien")} for x in khe]}
    ma_http, kq = KhachTram(tram_chu, token, mo=mo).goi("POST", "/api/tho/dang-ky", than)
    if ma_http != 200:
        raise LoiKhachTram(f"trạm từ chối đăng ký khe ({ma_http}): {str(kq.get('loi', ''))[:120]}")


def hieu_ung_that() -> HieuUng:
    return HieuUng(ghep=ghep_that, ghi_token=ghi_token_may, dang_ky=dang_ky_that)


def _ghi(p: Path, noi_dung: bytes) -> None:
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tam = p.with_name(p.name + ".moi")
    tam.write_bytes(noi_dung)
    tam.chmod(0o644 if p.suffix == ".plist" else 0o600)
    os.replace(tam, p)


def thuc_hien_dk(kh: KeHoachDangKy, ma: str, hu: HieuUng) -> str:
    if kh.daemon.exists() or kh.tho_yaml.exists():
        raise ValueError("Máy đã có cấu hình/service thợ; chưa đổi mã ghép")
    may_id, token = hu.ghep(kh.tram_chu, ma)
    hu.ghi_token(may_id, token)
    tam = kh.tho_yaml.with_name("tho.yaml.moi")
    tam.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tam.write_text(noi_dung_tho_yaml(may_id, kh.tram_chu, kh.khe, nho_url=kh.nho_url), encoding="utf-8")
    nap_cau_hinh_tho(tam)                                   # đúng luật đọc của `tram tho chay` trước khi thay
    os.replace(tam, kh.tho_yaml)                            # đã có tho.yaml thì dừng từ đầu hàm (không có .bak)
    for p, noi_dung in kh.tep.items():
        _ghi(p, noi_dung)
    for argv, env in kh.lenh_mcp:
        hu.chay(argv, env={**os.environ, **env}, check=argv[2] != "remove", capture_output=True, text=True)
    hu.dang_ky(kh.tram_chu, may_id, token, kh.khe)
    # Chỉ staging: tho.yaml mới chưa có principal/chay.day và các cổng S2/S6/S7 chưa được duyệt.
    # Không bootstrap service lặp exit 2; lệnh kh.lenh_launchd được giữ để kích hoạt sau kiểm.
    return may_id
