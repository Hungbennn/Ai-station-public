"""Mã điều phối (quyết định D24; plan 2e G2, G23): bí mật RIÊNG của hook phiên điều phối trên máy A, chỉ mở đúng
`POST /api/dieu-phoi/nhip`. Máy A giữ mã trong Keychain (mục `tram-dieu-phoi-ma`); trạm chỉ giữ sha256 ở khoá
`dieu_phoi_ma_sha256` của `~/.tram/cau-hinh.yaml`. Mã này không đọc được memory (memory service chỉ so với
`ma_dai_ca_sha256`), không mở route ghi nào khác, và phải KHÁC mã Đại ca. Mã không bao giờ đi qua argv, log hay màn
hình: `tram chu dat-ma-dieu-phoi` hỏi ẩn (getpass) hai lần, chờ `dong-y`. Chỉ import từ `tram/nho/ma_dai_ca.py`."""
import getpass
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

from tram.nho.ma_dai_ca import BAM_RE, MA_RE, bam, tep_cau_hinh
from tram.nho.ma_dai_ca import doc_bam as doc_bam_dai_ca

KHOA = "dieu_phoi_ma_sha256"
DONG_RE = re.compile(rf"^{KHOA}:.*$", re.M)


def _doc(van_ban: str) -> str | None:
    raw = yaml.safe_load(van_ban) or {}
    v = raw.get(KHOA) if isinstance(raw, dict) else None
    return v if isinstance(v, str) and BAM_RE.fullmatch(v) else None


def doc_bam(duong_dan: Path | None = None) -> str | None:
    """Bản băm đã đặt. Thiếu file, yaml hỏng, giá trị sai dạng → None: route nhịp từ chối mọi lời gọi (fail closed)."""
    try:
        return _doc(tep_cau_hinh(duong_dan).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def ghi_bam(gia_tri: str, duong_dan: Path | None = None) -> None:
    """Thay dòng `dieu_phoi_ma_sha256:` (hoặc thêm cuối file), giữ chú thích và khoá khác; kiểm trước, ghi nguyên tử."""
    if not BAM_RE.fullmatch(gia_tri):
        raise ValueError("bản băm phải là 64 ký tự hex thường")
    if gia_tri == doc_bam_dai_ca(duong_dan):
        raise ValueError("mã điều phối phải KHÁC mã Đại ca (D24) — không đổi gì")
    p = tep_cau_hinh(duong_dan)
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
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


def dat_ma_dieu_phoi(args, *, doc_an=None, hoi=None) -> int:
    doc_an, hoi, p = doc_an or getpass.getpass, hoi or input, tep_cau_hinh()
    print(f"Sẽ ghi sha256 của mã điều phối vào {p} (khoá {KHOA}; thay bản cũ nếu có). Mã không được lưu, không in.\n"
          "Mã: chuỗi ngẫu nhiên ≥ 32 ký tự, đúng mã trong Keychain máy A (mục tram-dieu-phoi-ma), KHÁC mã Đại ca. "
          "Mã này chỉ mở POST /api/dieu-phoi/nhip.\nDán trong Terminal.app — khung terminal của app Claude làm hỏng "
          "chuỗi dán vào ô ẩn.")
    if not args.dong_y and hoi("Gõ dong-y để tiếp tục: ").strip() != "dong-y":
        print("Không đổi gì.")
        return 1
    ma = doc_an("Mã điều phối (ẩn): ")
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
    print(f"Đã lưu bản băm vào {p}. tram-api dùng ngay từ nhịp kế tiếp, không cần khởi động lại.")
    return 0


def them_lenh_ma_dieu_phoi(chu) -> None:
    d = chu.add_parser("dat-ma-dieu-phoi", help="Đặt mã điều phối cho hook máy A (lưu sha256, hỏi ẩn; D24)")
    d.add_argument("--dong-y", action="store_true", help="Bỏ bước gõ dong-y (vẫn hỏi mã ẩn)")
    d.set_defaults(ham=dat_ma_dieu_phoi)
