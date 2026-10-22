"""Mã Đại ca cho phiên tay MCP trên máy A (spec 1b §9.3, §15): trạm chỉ giữ sha256 của mã — khoá `ma_dai_ca_sha256`
trong `~/.tram/cau-hinh.yaml`; tiến trình nào đọc được bản băm cũng không dùng được. Mã không bao giờ đi qua argv,
biến môi trường, log hay màn hình: `tram chu dat-ma-dai-ca` hỏi ẩn (getpass) hai lần, chờ `dong-y`."""
import getpass
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

KHOA = "ma_dai_ca_sha256"
KHOA_DIEU_PHOI = "dieu_phoi_ma_sha256"          # = tram.chu.ma_dieu_phoi.KHOA (D24); nho không import ngược tầng chu
MA_RE = re.compile(r"[A-Za-z0-9._~+/=-]{32,256}")       # an toàn trong header HTTP, đủ dài để không đoán được
BAM_RE = re.compile(r"[0-9a-f]{64}")
DONG_RE = re.compile(rf"^{KHOA}:.*$", re.M)


def tep_cau_hinh(duong_dan: Path | None = None) -> Path:
    return duong_dan or tram_home() / "cau-hinh.yaml"


def bam(ma: str) -> str:
    return hashlib.sha256(ma.encode()).hexdigest()


def _doc(van_ban: str, khoa: str = KHOA) -> str | None:
    raw = yaml.safe_load(van_ban) or {}
    v = raw.get(khoa) if isinstance(raw, dict) else None
    return v if isinstance(v, str) and BAM_RE.fullmatch(v) else None


def doc_bam(duong_dan: Path | None = None) -> str | None:
    """Bản băm đã đặt. Thiếu file, yaml hỏng, giá trị sai dạng → None: phiên tay bị từ chối (fail closed)."""
    try:
        return _doc(tep_cau_hinh(duong_dan).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def ghi_bam(gia_tri: str, duong_dan: Path | None = None) -> None:
    """Thay dòng `ma_dai_ca_sha256:` (hoặc thêm cuối file), giữ chú thích và khoá khác; kiểm trước, ghi nguyên tử."""
    if not BAM_RE.fullmatch(gia_tri):
        raise ValueError("bản băm phải là 64 ký tự hex thường")
    p = tep_cau_hinh(duong_dan)
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
    try:
        trung = _doc(cu, KHOA_DIEU_PHOI) == gia_tri
    except yaml.YAMLError:
        trung = False                                   # file hỏng: bước kiểm dưới từ chối, không đổi gì
    if trung:
        raise ValueError("mã Đại ca phải KHÁC mã điều phối (D24) — không đổi gì")
    dong = f'{KHOA}: "{gia_tri}"'
    if DONG_RE.search(cu):
        moi = DONG_RE.sub(dong, cu)
    else:
        moi = (cu if not cu or cu.endswith("\n") else cu + "\n") + dong + "\n"
    try:
        dung = _doc(moi) == gia_tri
    except yaml.YAMLError:
        dung = False
    if not dung:
        raise ValueError(f"{p} không phải bảng khoá → giá trị hợp lệ — sửa tay rồi chạy lại; không đổi gì")
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tam = tempfile.mkstemp(dir=p.parent, prefix=".cau-hinh-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(moi)
    os.replace(tam, p)


def dat_ma_dai_ca(args, *, doc_an=None, hoi=None) -> int:
    doc_an, hoi, p = doc_an or getpass.getpass, hoi or input, tep_cau_hinh()
    print(f"Sẽ ghi sha256 của mã Đại ca vào {p} (khoá {KHOA}; thay bản cũ nếu có). Mã không được lưu, không in.\n"
          "Mã: chuỗi ngẫu nhiên ≥ 32 ký tự Đại ca tạo trên máy A (ví dụ `openssl rand -hex 32`), đúng mã đặt vào "
          "TRAM_DAI_CA_MA của cấu hình MCP trên máy A.\nDán trong Terminal.app — khung terminal của app Claude làm "
          "hỏng chuỗi dán vào ô ẩn.")
    if not args.dong_y and hoi("Gõ dong-y để tiếp tục: ").strip() != "dong-y":
        print("Không đổi gì.")
        return 1
    ma = doc_an("Mã Đại ca (ẩn): ")
    if not MA_RE.fullmatch(ma):
        print("Lỗi: mã phải 32–256 ký tự trong [A-Za-z0-9._~+/=-] — không đổi gì.", file=sys.stderr)
        return 1
    if doc_an("Nhập lại (ẩn): ") != ma:
        print("Lỗi: hai lần nhập không khớp — không đổi gì.", file=sys.stderr)
        return 1
    try:
        ghi_bam(bam(ma), p)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    print(f"Đã lưu bản băm vào {p}. Memory service dùng ngay từ lời gọi kế tiếp, không cần khởi động lại.")
    return 0


def them_lenh_ma_dai_ca(chu) -> None:
    d = chu.add_parser("dat-ma-dai-ca", help="Đặt mã Đại ca cho phiên tay MCP (lưu sha256, hỏi ẩn)")
    d.add_argument("--dong-y", action="store_true", help="Bỏ bước gõ dong-y (vẫn hỏi mã ẩn)")
    d.set_defaults(ham=dat_ma_dai_ca)
