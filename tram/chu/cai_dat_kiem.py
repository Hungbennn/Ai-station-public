"""Phần `tram-kiem` trong `tram chu cai-dat-tho` theo D22 (lát 3c, bead bs-urj.13) — KHÔNG helper root, không ACL.
Thêm: thư mục gốc bản chép `thu_muc_kiem` do CHÍNH `tram-kiem` tạo (nó sở hữu, trạm chỉ đi qua được), dòng sudoers
runas CHỈ `tram-kiem` (`dong_sudoers_kiem`), và hồ sơ Seatbelt cố định root:wheel 0644 `HO_SO_KIEM` cho CẢ HAI cơ
chế (3C-D6: mọi lệnh của lượt chạy trong hồ sơ — `boc_luot`; cơ chế `sandbox` ghim thêm hồ sơ ở sudoers).
Không tự chọn cơ chế: `cach_ly.tram_kiem` phải cùng cơ chế với `--co-che` (D3: thử `user` trước, giữ hai nhánh).
`tram-kiem` luôn là user RIÊNG: `don_sach` giết MỌI tiến trình của nó — dùng chung user với khe là giết agent khe."""
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from tram.chu.tai_nguyen import TaiNguyen
from tram.cli_dich_vu import CONG_MAC_DINH
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI, goc_hop_le, manifest_ho_so

NHA_KIEM = "/var/empty"        # C01: tram-kiem KHÔNG có nhà ghi được (root, 0755); lệnh kiểm nhận HOME mới mỗi lần


@dataclass
class PhanKiem:
    tep: dict[Path, bytes] = field(default_factory=dict)        # file soạn trong ~/.tram/cai-dat-tho
    tai_nguyen: list[TaiNguyen] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)


def cong_cam(db_nghiep_vu: tuple[str, ...]) -> list[int]:
    return [CONG_MAC_DINH, *sorted({int(x.rsplit(":", 1)[1]) for x in db_nghiep_vu})]


def tep_root(soan: Path, dich: Path, noi_dung: bytes, mode: str, *, truoc: tuple = ()) -> TaiNguyen:
    """File root:wheel cài từ bản soạn; định danh = sha256 nội dung."""
    h = hashlib.sha256(noi_dung).hexdigest()
    return TaiNguyen("tep", str(dich), lambda i: [*map(list, truoc), ["sudo", "install", "-m", mode, "-o", "root",
                                                                     "-g", "wheel", str(soan), str(dich)]],
                     lambda i: {"sha256": h})


def phan_kiem(*, kiem: PrincipalKiem | None, thu_muc_kiem: Path | None, co_che: str, tram: str, quan_ly: str,
              soan: Path, khe: tuple[str, ...] = (), db_nghiep_vu: tuple[str, ...] = (),
              quan_sat=lambda kieu, ten: None) -> PhanKiem:
    if kiem is None:
        return PhanKiem()
    if kiem.co_che != co_che:
        raise ValueError(f"cach_ly.tram_kiem dùng cơ chế {kiem.co_che}, khác --co-che {co_che} — khai cùng một cơ chế")
    if kiem.ten in khe or kiem.ten in (tram, quan_ly):
        raise ValueError(f"tram-kiem ({kiem.ten}) phải là user riêng — không trùng principal khe, trạm, quản lý thợ")
    if thu_muc_kiem is None:
        raise ValueError("Có cach_ly.tram_kiem thì cần giao_viec.thu_muc_kiem (gốc bản chép của tram-kiem)")
    goc = goc_hop_le(thu_muc_kiem)
    uid_kiem = lambda i: {"chu": kiem.ten, "uid": (quan_sat("user", kiem.ten) or {}).get("uid")}  # noqa: E731
    pk = PhanKiem(tai_nguyen=[TaiNguyen("thu_muc", goc, lambda i: [["sudo", "-u", kiem.ten, "/bin/mkdir", "-m", "0755",
                                                                     goc]], uid_kiem)])
    hs, mf = manifest_ho_so(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
                            cong=cong_cam(db_nghiep_vu))      # V2-5: manifest cài SAU hồ sơ — thiếu/cũ → cổng đóng
    pk.tep[soan / HO_SO_KIEM.name], pk.tep[soan / MANIFEST_KIEM.name] = hs, mf
    pk.tai_nguyen += [TaiNguyen("thu_muc", str(THU_MUC_CAI), lambda i: [
        ["sudo", "install", "-d", "-o", "root", "-g", "wheel", "-m", "0755", str(THU_MUC_CAI)]], lambda i: {"uid": 0}),
                      tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644"),
                      tep_root(soan / MANIFEST_KIEM.name, MANIFEST_KIEM, mf, "0644")]
    pk.canh_bao = [
        f"D22: KHÔNG có dòng sudoers nào chạy root — {tram} chỉ được chạy lệnh DƯỚI {kiem.ten}. {kiem.ten} tự tạo, tự "
        f"giải nén, tự dọn bản chép dưới {goc}; cây kiểm là repo git MỘT commit do {kiem.ten} tự dựng (D40).",
        f"C01: nhà của {kiem.ten} là {NHA_KIEM} (không ghi được, không createhomedir). Mọi lệnh của lượt chạy trong "
        f"hồ sơ {HO_SO_KIEM} (cả hai cơ chế). Quan sát launchd chưa có (chờ G3 đo định dạng) — cổng kiểm lại giữ đóng.",
        f"Principal kiểm lại đọc từ cach_ly.tram_kiem ({co_che}:{kiem.ten}), thư mục kiểm từ giao_viec.thu_muc_kiem "
        f"({goc}). Cài xong chạy `tram giao kiem`: mục thư mục kiểm, sudoers, ghi bản chép phải XANH trước khi bật "
        "giao_viec.bat."]
    return pk
