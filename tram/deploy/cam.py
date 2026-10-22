"""D89 nối vào kiểm đường cấm (spec `tu-deploy` "File mà ba lệnh dùng là file cấm sửa"; design D-4): file/thư mục
trong repo dự án mà ba lệnh nhắc tới (`tram.tu_dong.file_cam.duong_dan_tu_lenh`, hợp đồng TM-1) được chuyển riêng qua
`bat_buoc=` của kiểm đường cấm — agent sửa → `dong-file-cau-hinh`, không bao giờ tự merge.

"Có trong repo" = có ở commit đang xét HOẶC ở nhánh chính: agent tạo script mà lệnh deploy sẽ chạy, hay xoá script
đang có, đều bị bắt. Phía trạm đọc cài đặt từ kho sự kiện; phía thợ (`tram/tho/ket_thuc.py`, máy thợ không mở kho
sự kiện) đọc qua GET công khai của tram-api. Không đọc/xác minh được → dừng trước runner, ghi lỗi bàn giao."""
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.tu_merge_rao import loai_trong_repo
from tram.tu_dong.cai_dat import MAC_DINH, TRUONG_LENH, CaiDatTuDong, loi_cai_dat, sang_api, tu_api
from tram.tu_dong.file_cam import duong_dan_tu_lenh
from tram.tu_dong.luu import doc_cai_dat

def loai_trong_cay(goc_tin: tuple[Path, ...], repo: Path, *refs: str) -> Callable[[str], tuple[str, str] | None]:
    """Dùng đúng bộ nhận diện TM-2: cây commit, không theo symlink, so không phân biệt hoa/thường."""
    return loai_trong_repo(repo, goc_tin, refs)


def cam_cua(cd: CaiDatTuDong, gocs: tuple[Path, ...], repo: Path, *refs: str) -> tuple[str, ...]:
    """Chưa khai lệnh nào → () và không gọi git."""
    return duong_dan_tu_lenh(cd, loai_trong_cay(gocs, repo, *refs)) if any(getattr(cd, t) for t in TRUONG_LENH) else ()


def cam_tu_lenh(db, repo: Path, da, commit: str) -> tuple[str, ...]:
    gocs = (repo, da.duong_dan, tram_home() / "kho-deploy" / da.ten)
    return cam_cua(doc_cai_dat(db, da.ten)[0], gocs, repo, commit, f"origin/{da.nhanh_chinh}")


LOI_CAM = "Không xác minh được file lệnh tự động — không chạy kiểm; chờ trạm kiểm lại"


def _dung_dang(d, mau) -> bool:
    if isinstance(mau, dict):
        return isinstance(d, dict) and d.keys() == mau.keys() and all(_dung_dang(d[k], v) for k, v in mau.items())
    return type(d) is type(mau)


def cam_tu_lenh_tho(khach, du_an: str, wt: Path, nhanh_chinh: str) -> tuple[str, ...]:
    """GET đọc, hạn 10s của KhachTram; lỗi cố định để thợ vẫn bàn giao, không chạy kiểm."""
    try:
        ma, kq = khach.goi("GET", f"/api/du-an/{du_an}/tu-dong", xac_thuc=False)
        if ma != 200 or not _dung_dang(kq["cai_dat"], sang_api(MAC_DINH)):
            raise ValueError
        cd = tu_api(kq["cai_dat"])
        if loi_cai_dat(cd, bat_ghi=True):
            raise ValueError
        return cam_cua(cd, (wt,), wt, "HEAD", f"origin/{nhanh_chinh}")
    except (RuntimeError, KeyError, TypeError, AttributeError, ValueError, OSError, subprocess.SubprocessError):
        raise OSError(LOI_CAM) from None
