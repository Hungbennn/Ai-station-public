"""Khai khe cho `tram tho dang-ky --khe <ten>:<cli>:<vai,…>:<tên gợi nhớ>` (spec 3 §9.1, §9.2) và nội dung
`~/.tram/tho.yaml` sinh ra — cùng luật với `nap_cau_hinh_tho` (3a-1). `principal` để trống: chốt sau spike S6."""
from dataclasses import dataclass

import yaml

from tram.tho.cau_hinh import CLI, TEN_KHE_RE, VAI


@dataclass(frozen=True)
class KheKhai:
    ten: str
    cli: str
    vai_uu_tien: tuple[str, ...]
    ten_goi_nho: str


def doc_khe(chuoi: str) -> KheKhai:
    phan = chuoi.split(":", 3)
    if len(phan) != 4:
        raise ValueError(f"--khe {chuoi!r}: dạng <ten>:<cli>:<vai,…>:<tên gợi nhớ>")
    ten, cli, vai, goi_nho = phan[0], phan[1], tuple(v for v in phan[2].split(",") if v), phan[3].strip()
    if not TEN_KHE_RE.fullmatch(ten):
        raise ValueError(f"--khe: tên khe {ten!r} chỉ gồm chữ thường, số, '-'")
    if cli not in CLI:
        raise ValueError(f"--khe {ten}: cli {cli!r} không hỗ trợ — chỉ {CLI}")
    if not vai or not set(vai) <= set(VAI):
        raise ValueError(f"--khe {ten}: vai ưu tiên là danh sách con của {VAI}")
    if not goi_nho or len(goi_nho) > 64 or "@" in goi_nho:
        raise ValueError(f"--khe {ten}: tên gợi nhớ bắt buộc, ≤ 64 ký tự, không phải email")
    return KheKhai(ten, cli, vai, goi_nho)


def noi_dung_tho_yaml(may_id: str, tram_api: str, khe: list[dict], *, nho_url: str | None = None) -> str:
    """`khe`: các dict `{ten, cli, thu_muc_cau_hinh, ten_goi_nho, vai_uu_tien}` của kế hoạch. Không chứa bí mật."""
    du_lieu = {"may_id": may_id, "tram_api": tram_api, "khe": [
        {"ten": k["ten"], "cli": k["cli"], "thu_muc_cau_hinh": k["thu_muc_cau_hinh"], "ten_goi_nho": k["ten_goi_nho"],
         "vai_uu_tien": list(k["vai_uu_tien"])} for k in khe]}
    du_lieu["chay"] = {"nho_url": nho_url}
    return ("# Sinh bởi `tram tho dang-ky` (spec 3 §9.1). principal: chốt sau spike S6.\n"
            + yaml.safe_dump(du_lieu, allow_unicode=True, sort_keys=False))
