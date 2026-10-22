"""`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả).
Lát 3c: các mục principal `tram-kiem` ở `kiem_principal.py` (3C-D6, hợp đồng P1 H7 — dưới khoá, chỉ khi cổng chưa
đóng, UID thực, probe qua lượt tạm trong hồ sơ Seatbelt)."""
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.giao_viec.git_kiem import kho_kiem
from tram.giao_viec.kho_kiem_tao import url_origin
from tram.giao_viec.kiem_principal import kiem_principal
from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen
from tram.tho.kiem_may import MucKiem


def _muc(ten: str, dat: bool, chi_tiet: str, *, khong_dat: str = "do") -> MucKiem:
    return MucKiem(ten, "xanh" if dat else khong_dat, chi_tiet)


def kiem_du_an(da: DuAn) -> list[MucKiem]:
    kg, mt = kho_kiem(da.ten), da.moi_truong_kiem
    if (kg / ".git").exists():
        cu, goc = url_origin(kg), url_origin(da.duong_dan)
        ra = [_muc(f"{da.ten}: kho kiểm", bool(cu) and cu == goc, f"origin {cu} — dự án {goc}")]
    else:
        ra = [_muc(f"{da.ten}: kho kiểm", False, f"chưa có — chạy `tram giao kho-kiem {da.ten}`")]
    return ra + [_muc(f"{da.ten}: moi_truong_kiem", mt is not None and mt.file.is_file(), str(mt.file if mt else "")),
                 _muc(f"{da.ten}: lệnh kiểm mặc định", bool(da.giao.lenh_kiem_mac_dinh),
                      "không có thì mỗi bead phải nêu lệnh trong design", khong_dat="vang")]


def kiem_giao_viec(cg: CauHinhGiaoViec, cac_du_an: list[DuAn], *, goc_quyen: Path | None = None,
                   **kw) -> list[MucKiem]:
    ra = [_muc("giao_viec.bat", cg.bat, "bật" if cg.bat else "tắt — tram-api không phát phiếu", khong_dat="vang")]
    ra += [_muc(f"file quyền {v}", phien_ban_quyen(v, goc=goc_quyen) != KHONG_CO, "vai/quyen/<vai>.json — 3a-2")
           for v in ("coder", "qc")]
    from tram.quan_kiem.client import CongTuXa
    try:
        tt = CongTuXa().trang_thai()['trang_thai']
        ra.append(_muc('Bộ quản lý kiểm', tt == 'mo', tt))
    except (OSError, ValueError, KeyError):
        ra.append(_muc('Bộ quản lý kiểm', False, 'không liên lạc được — không chạy kiểm cục bộ'))
    for da in cac_du_an:
        ra += kiem_du_an(da)
    return ra
