"""Dịch vụ launchd của trạm chủ (bs-2bd.1.23): tên ngắn ↔ nhãn, plist từng dịch vụ, hậu quả khi cài quét có ghi.

Đại ca chốt 17/10: cài TỪNG dịch vụ, không còn cài cả bốn một lần; `vn.tram.quet` chạy `tram quet --ghi` (ghi nhãn
cột vào Beads của dự án `bat_ghi: true`) nên chỉ cài khi chọn rõ, và kế hoạch in TỪNG dự án sẽ bị ghi / chỉ đọc.
Không đọc được danh sách dự án hay khoá `bat_ghi` của BẤT KỲ dự án nào → `LoiCaiDat`: không lập kế hoạch, không ghi
file, không chạy lệnh nào (INV-005 — chưa trình được hậu quả thì không cài). Mỗi plist cài kèm BIÊN NHẬN
`~/.tram/dich-vu/<nhãn>.json` (sha256 nội dung trạm ghi) — chứng cứ sở hữu duy nhất `go-dich-vu` chấp nhận."""
import hashlib
import json
from pathlib import Path

from tram.chu.launchd import (NHAN_API, NHAN_BAO_TIN, NHAN_QUET, NHAN_SAO_LUU, tao_plist, tao_plist_hang_ngay,
                              tao_plist_thuong_truc)

DICH_VU_TRAM = {"api": NHAN_API, "bao-tin": NHAN_BAO_TIN, "sao-luu": NHAN_SAO_LUU, "quet": NHAN_QUET}
HAN_LENH_GIAY = 30.0          # mỗi lệnh hệ thống của cài/gỡ (launchctl, mkdir, mv): quá hạn → dừng, không chạy tiếp


class LoiCaiDat(RuntimeError):
    pass


def chon(dich_vu: list[str] | None) -> list[str]:
    ds = list(dict.fromkeys(dich_vu or ()))
    if not ds or any(t not in DICH_VU_TRAM for t in ds):
        raise ValueError("Chọn ít nhất một dịch vụ trong: " + ", ".join(DICH_VU_TRAM) + " (không có mặc định)")
    return ds


def tep_dich_vu(ten: str, *, uv: str, repo: Path, log: Path) -> bytes:
    if ten == "quet":
        return tao_plist(uv=uv, repo=repo, log=log / "quet.log")
    if ten == "sao-luu":
        return tao_plist_hang_ngay(NHAN_SAO_LUU, ["chu", "sao-luu"], uv=uv, repo=repo, log=log / "sao-luu.log")
    return tao_plist_thuong_truc(DICH_VU_TRAM[ten], [ten], uv=uv, repo=repo, log=log / f"{ten}.log")


def bien_nhan(nhan: str, plist: Path, noi_dung: bytes) -> tuple[Path, bytes]:
    """(đường biên nhận, nội dung JSON) cho plist trạm vừa sinh — `thuc_hien` ghi cùng lúc với plist."""
    from tram.duong_dan import tram_home
    bn = {"nhan": nhan, "plist": str(plist), "sha256": hashlib.sha256(noi_dung).hexdigest()}
    return tram_home() / "dich-vu" / f"{nhan}.json", json.dumps(bn, ensure_ascii=False).encode()


def _du_an_bat_ghi() -> tuple[list[str], list[str]]:
    """(dự án sẽ bị ghi, dự án chỉ đọc) — MỌI dự án trong du-an/, không lọc bớt."""
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.cau_hinh.du_an import liet_ke_du_an
    ds = liet_ke_du_an()
    gia_tri = {t: bat_ghi(t) for t in ds}
    return [t for t in ds if gia_tri[t]], [t for t in ds if not gia_tri[t]]


def canh_bao_quet(*, du_an_ghi=None) -> list[str]:
    try:
        ghi, chi_doc = (du_an_ghi or _du_an_bat_ghi)()
    except Exception:                       # noqa: BLE001 — yaml hỏng, khoá sai kiểu, không đọc được thư mục…
        raise LoiCaiDat("Không đọc được du-an/*.yaml hay khoá bat_ghi của một dự án — chưa biết quét sẽ ghi vào "
                        "đâu nên KHÔNG cài vn.tram.quet. Sửa du-an/*.yaml rồi chạy lại.") from None
    return [f"vn.tram.quet chạy `tram quet --ghi` mỗi 120 giây: GHI nhãn cột vào Beads của: "
            f"{', '.join(ghi) or 'chưa dự án nào'}; chỉ đọc: {', '.join(chi_doc) or 'không có'}. "
            "Gỡ: tram chu go-dich-vu --dich-vu quet."]
