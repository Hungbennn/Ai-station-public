"""Cài đặt tự merge / tự deploy của một dự án (change `tu-merge-tu-deploy`, D69–D75, D88, D97): mô hình, mặc định,
dạng API và dạng sự kiện, kiểm khi lưu. Hàm thuần — lưu/đọc ở `luu.py`.

QC đạt, kiểm lại đạt, hàng rào cấu trúc DB (D71, D76) KHÔNG có trường: không có chỗ nào để tắt chúng."""
import shlex
from dataclasses import asdict, dataclass, fields

from tram.nho.bi_mat import quet

DO_DAI_LENH = 500
KHOA_CUNG = ("qc", "kiem_lai", "schema")
TEN_LENH = {"lenh_deploy": "Lệnh deploy", "lenh_kiem_song": "Lệnh kiểm còn sống", "lenh_lui": "Lệnh lùi"}
TRUONG_LENH = tuple(TEN_LENH)


@dataclass(frozen=True)
class CaiDatTuDong:
    tu_merge: bool = False          # D69: mặc định tắt
    tu_deploy: bool = False         # D74: mặc định tắt
    dk_ci: bool = True              # ba nút điều kiện có nút (D70), mặc định bật
    dk_cot: bool = True
    dk_hang_rao: bool = True
    lenh_deploy: str = ""           # D73: trống = chưa khai
    lenh_kiem_song: str = ""
    lenh_lui: str = ""

    @property
    def du_lenh(self) -> bool:
        return all(getattr(self, t) for t in TRUONG_LENH)

    def phang(self) -> dict:
        return asdict(self)


MAC_DINH = CaiDatTuDong()
_TEN = tuple(f.name for f in fields(CaiDatTuDong))


def tu_phang(d: dict) -> CaiDatTuDong:
    """Đọc từ sự kiện: khoá lạ bỏ qua, khoá thiếu lấy mặc định — mã cũ đọc được sự kiện mới và ngược lại."""
    return CaiDatTuDong(**{**{k: v for k, v in d.items() if k in _TEN}, "dk_ci": True})


def sang_api(cd: CaiDatTuDong) -> dict:
    return {"tu_merge": cd.tu_merge, "tu_deploy": cd.tu_deploy,
            "dieu_kien": {"ci": True, "cot": cd.dk_cot, "hang_rao": cd.dk_hang_rao},
            "lenh": {"deploy": cd.lenh_deploy, "kiem_song": cd.lenh_kiem_song, "lui": cd.lenh_lui}}


def tu_api(d: dict) -> CaiDatTuDong:
    """`d` đã qua kiểm thân yêu cầu (đủ khoá, đúng kiểu, không khoá lạ). Lệnh bỏ khoảng trắng hai đầu."""
    dk, ln = d["dieu_kien"], d["lenh"]
    return CaiDatTuDong(d["tu_merge"], d["tu_deploy"], True, dk["cot"], dk["hang_rao"],
                        ln["deploy"].strip(), ln["kiem_song"].strip(), ln["lui"].strip())


def truong_doi(cu: CaiDatTuDong, moi: CaiDatTuDong) -> list[str]:
    return [t for t in _TEN if getattr(cu, t) != getattr(moi, t)]


def loi_lenh(lenh: str) -> str | None:
    """Lý do từ chối một lệnh — câu hằng, KHÔNG chép lệnh (INV-001); None = được. Trống = chưa khai (được)."""
    if not lenh:
        return None
    if len(lenh) > DO_DAI_LENH:
        return f"Lệnh dài quá {DO_DAI_LENH} ký tự"
    if any(ord(c) < 32 or ord(c) == 127 for c in lenh):
        return "Lệnh có ký tự điều khiển (xuống dòng, tab…)"
    try:
        argv = shlex.split(lenh)
    except ValueError:
        return "Lệnh không tách được thành các đối số (thiếu dấu nháy?)"
    if not argv or not argv[0]:
        return "Lệnh rỗng"
    if quet([lenh]):
        return "Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
    return None


def loi_cai_dat(cd: CaiDatTuDong, *, bat_ghi: bool) -> str | None:
    """Kiểm khi Đại ca lưu (422 khi khác None). `bat_ghi: false` không bật được công tắc nào (INV-005);
    tự deploy cần đủ 3 lệnh (D73)."""
    for t in TRUONG_LENH:
        if (loi := loi_lenh(getattr(cd, t))) is not None:
            return f"{TEN_LENH[t]}: {loi}"
    if not bat_ghi and (cd.tu_merge or cd.tu_deploy):
        return "Dự án chỉ quét thử (bat_ghi: false) — không bật được tự merge, tự deploy"
    if cd.tu_deploy and not cd.du_lenh:
        return "Chưa khai đủ 3 lệnh — không bật được tự deploy"
    return None
