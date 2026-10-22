"""Bộ quét bí mật cho nguồn ký ức phần 3/4 (Đại ca chốt D23, 15/10) — chạy TRƯỚC khi gửi LLM, embed hay lưu.

Bốn nhóm dấu hiệu: tiền tố khoá đã biết, khối khoá riêng, gán giá trị nhạy cảm (cả chuỗi kết nối có mật khẩu và
dòng `.env`), chuỗi entropy cao. Có dấu hiệu → `LoiBiMat`: vòng nạp bỏ CẢ nguồn, ghi `nho.bo_bi_mat` chỉ gồm nhóm +
số lượng — không chép đoạn khớp, không ghi vị trí. Regex hữu hạn không bắt được mọi bí mật viết tự do; báo nhầm thì
mất nguồn đó (Đại ca chấp nhận — D23)."""
import math
import re
from collections import Counter
from collections.abc import Iterable

LOAI_SU_KIEN = "nho.bo_bi_mat"
NHOM = ("khoa_da_biet", "khoa_rieng", "gan_gia_tri", "entropy_cao")
DO_DAI_TOKEN = 32             # token liền mạch ngắn hơn không xét entropy
NGUONG_ENTROPY = 4.2          # bit/ký tự, token có ký tự ngoài hex — lý lẽ: plan 1b-4 G24
NGUONG_ENTROPY_HEX = 3.0      # token thuần hex (tối đa 4 bit/ký tự); thuần chữ số (≤ 3,32) không xét

_N = r"(?![A-Za-z0-9_-])"
_KHOA = [re.compile(r"(?<![A-Za-z0-9_-])" + p + _N) for p in (
    r"sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}", r"gh[opsu]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{22,}",
    r"xox[abp]-[A-Za-z0-9-]{10,}", r"(?:AKIA|ASIA)[A-Z0-9]{16}", r"AIza[A-Za-z0-9_-]{35}",
    r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")] + [
    re.compile(r"(?<![0-9])[0-9]{8,10}:[A-Za-z0-9_-]{35}" + _N)]           # bot Telegram, kể cả trong URL /bot<id>:…
_KHOA_RIENG = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_GAN = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z0-9]+[_.-])*(?:password|passwd|pwd|secret|api[_-]?key|token|bearer"
                  r"|authorization)[\"']?[ \t]*[:=](?!=)[ \t]*[\"']?(?:(?:bearer|basic)[ \t]+)?([^\s\"'`,;)\]}]+)",
                  re.IGNORECASE)
_KET_NOI = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s:/@]+:[^\s/@]+@[^\s/@]+")          # scheme://user:pass@host
_ENV = re.compile(r"^[ \t]*(?:export[ \t]+)?[A-Z][A-Z0-9_]{2,}=[\"']?(\S{8,})", re.MULTILINE)
_KHONG_PHAI_GIA_TRI = re.compile(r"none|null|true|false|str|bytes|int|bool|\d+|[<{$(\[/~.@].*", re.IGNORECASE)
_TOKEN = re.compile(r"[A-Za-z0-9+/=_-]{%d,}" % DO_DAI_TOKEN)
_HEX = re.compile(r"[0-9a-fA-F]+")
_UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_MAU_TEN = re.compile(r"[A-Z0-9]+|(?:[A-Z]?[a-z0-9]+)+[A-Z]?")      # mẩu tên file/thư mục: thường, CamelCase, HOA


def entropy(s: str) -> float:
    """Entropy Shannon (bit/ký tự) theo tần suất ký tự trong chính chuỗi."""
    return -sum(c / len(s) * math.log2(c / len(s)) for c in Counter(s).values())


def _la_duong_dan(t: str) -> bool:
    doan = [d for d in t.split("/") if d]
    return len(doan) >= 2 and all(not m or _MAU_TEN.fullmatch(m) for d in doan for m in re.split(r"[-_]", d))


def _entropy_cao(t: str) -> bool:
    if _UUID.fullmatch(t) or t.isdigit() or _la_duong_dan(t):
        return False
    if _HEX.fullmatch(t):                                  # SHA git (40), SHA-256 (64): định danh, không phải bí mật
        return len(t) not in (40, 64) and entropy(t) > NGUONG_ENTROPY_HEX
    return entropy(t) > NGUONG_ENTROPY


def quet(cac_chuoi: Iterable[str]) -> dict[str, int]:
    """Số dấu hiệu theo nhóm (thứ tự NHOM, chỉ nhóm > 0); {} = không thấy gì."""
    dem = Counter()
    for s in cac_chuoi:
        dem["khoa_da_biet"] += sum(len(m.findall(s)) for m in _KHOA)
        dem["khoa_rieng"] += len(_KHOA_RIENG.findall(s))
        dem["gan_gia_tri"] += sum(not _KHONG_PHAI_GIA_TRI.fullmatch(g) for m in (_GAN, _ENV) for g in m.findall(s))
        dem["gan_gia_tri"] += len(_KET_NOI.findall(s))
        dem["entropy_cao"] += sum(_entropy_cao(m.group()) for m in _TOKEN.finditer(s))
    return {n: dem[n] for n in NHOM if dem[n]}


class LoiBiMat(Exception):
    """Nguồn có dấu hiệu bí mật — KHÔNG phải sự kiện độc: bỏ cả nguồn, `nho.bo_bi_mat`, mốc tiến, không thử lại.
    Thông điệp và sự kiện chỉ mang loại nguồn, nhóm dấu hiệu và số lượng."""

    def __init__(self, loai_nguon: str, nhom: dict[str, int]):
        self.loai_nguon, self.nhom = loai_nguon, dict(nhom)
        super().__init__(f"nguồn {loai_nguon} có dấu hiệu bí mật: "
                         + ", ".join(f"{k} ×{v}" for k, v in self.nhom.items()))

    def su_kien(self, su_kien_id: int) -> tuple[str, dict]:
        return LOAI_SU_KIEN, {"su_kien_id": su_kien_id, "loai_nguon": self.loai_nguon, "nhom": self.nhom}


def chan_bi_mat(loai_nguon: str, cac_chuoi: Iterable[str]) -> None:
    """Gọi trên MỌI trường chữ của nguồn, bản gốc chưa cắt, trước khi dựng văn bản gửi LLM."""
    if nhom := quet(cac_chuoi):
        raise LoiBiMat(loai_nguon, nhom)
