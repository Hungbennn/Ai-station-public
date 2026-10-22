"""Kế hoạch của `tram du-an them|go` (spec 0+1a §4.7, Q15): tính đủ thay đổi, in ra, chỉ ghi khi Đại ca đồng ý.

`them`: (1) `du-an/<ten>.yaml` trong repo trạm, (2) khối trạm trong AGENTS.md/CLAUDE.md, (3) beads — chỉ in.
`go`: chỉ gỡ khối; `du-an/<ten>.yaml` giữ nguyên.
"""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.cau_hinh.du_an import nap_du_an
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.du_an.beads_tram import BuocBeads, xet_beads
from tram.du_an.cau_hinh_moi import kiem_ten, kiem_yaml, tao_yaml, ten_tu_repo
from tram.du_an.khoi import KhoiHong, chen_khoi, diff, go_khoi
from tram.duong_dan import goc_repo

TEN_FILE = ("AGENTS.md", "CLAUDE.md")
CHUA_BAT_GHI = ("du-an/{ten}.yaml mới có bat_ghi: false — trạm chỉ đọc và quét thử dự án này (`tram quet {ten}`): "
                "`tram quet --ghi` bỏ qua, bộ giao việc không giao, nút ghi trên dashboard bị từ chối. Bật ghi: "
                "Đại ca sửa tay thành bat_ghi: true sau khi điền hàng rào riêng (D31).")


@dataclass
class KeHoachDuAn:
    ghi: dict[Path, bytes] = field(default_factory=dict)   # file sẽ ghi → nội dung cuối (giữ kiểu xuống dòng)
    hien: list[str] = field(default_factory=list)          # diff đầy đủ từng file, theo thứ tự bước
    canh_bao: list[str] = field(default_factory=list)
    beads: BuocBeads | None = None


def _doc(p: Path) -> tuple[str, str]:
    """Trả (nội dung với xuống dòng LF, kiểu xuống dòng gốc) — giữ CRLF khi ghi lại."""
    if not p.exists():
        return "", "\n"
    tho = p.read_bytes().decode("utf-8")
    return tho.replace("\r\n", "\n"), "\r\n" if "\r\n" in tho else "\n"


def _khoi(repo: Path, them: bool, kh: KeHoachDuAn) -> None:
    for ten in TEN_FILE:
        p = repo / ten
        cu, xd = _doc(p)
        try:
            moi = (chen_khoi if them else go_khoi)(cu)
        except KhoiHong as e:
            raise KhoiHong(f"{p}: {e}") from e
        if moi != cu:
            kh.ghi[p] = moi.replace("\n", xd).encode("utf-8")
            kh.hien.append(diff(cu, moi, str(p)))


def _xet_co_san(ten: str, repo: Path) -> list[str]:
    try:
        da = nap_du_an(ten)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        return [f"du-an/{ten}.yaml đã có nhưng nạp lỗi: {e}"]
    return [] if da.duong_dan.resolve() == repo else [f"du-an/{ten}.yaml trỏ {da.duong_dan}, khác repo {repo}"]


def _cau_hinh(repo: Path, ten: str, gitnexus: str | None, ghi_de: bool, kh: KeHoachDuAn) -> None:
    p = goc_repo() / "du-an" / f"{ten}.yaml"
    moi = tao_yaml(ten, repo, gitnexus)
    kiem_yaml(ten, moi)
    if p.exists() and not ghi_de:
        kh.canh_bao.append(f"{p} đã có — giữ nguyên (thêm --ghi-de-cau-hinh để thay bằng bản nháp mới).")
        loi = _xet_co_san(ten, repo)
        if loi:
            raise ValueError("; ".join(loi))
        return
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
    if cu != moi:
        kh.ghi[p] = moi.encode("utf-8")
        kh.hien.append(diff(cu, moi, str(p)))
    kh.canh_bao.append(CHUA_BAT_GHI.format(ten=ten))


def _may_b(kh: KeHoachDuAn) -> str | None:
    try:
        return nap_cau_hinh_tram().ten_may_b
    except (OSError, ValueError, yaml.YAMLError) as e:
        kh.canh_bao.append(f"~/.tram/cau-hinh.yaml lỗi: {e}")
        return None


def lap_ke_hoach(repo: Path, *, them: bool, ten: str | None = None, gitnexus: str | None = None,
                 ghi_de: bool = False) -> KeHoachDuAn:
    """Không ghi gì. Lỗi dấu khối → `KhoiHong`; tên/cấu hình sai → `ValueError` (KhoiHong cũng là ValueError)."""
    repo = repo.resolve()
    kh = KeHoachDuAn()
    if them:
        ten = ten or ten_tu_repo(repo)
        if (loi := kiem_ten(ten)) is not None:
            raise ValueError(loi)
        _cau_hinh(repo, ten, gitnexus, ghi_de, kh)
    _khoi(repo, them, kh)
    if them:
        kh.beads = xet_beads(repo, goc=goc_repo(), may_b=_may_b(kh))
    else:
        kh.canh_bao.append("`go` không xoá du-an/<ten>.yaml — xoá tay trong repo trạm nếu muốn trạm thôi quét.")
    return kh


def in_ke_hoach(kh: KeHoachDuAn) -> str:
    dong = list(kh.hien)
    if kh.beads is not None:
        dong.append(f"Bước 3 — trỏ beads về trạm chủ: {kh.beads.trang_thai} — {kh.beads.ly_do}")
        dong += [f"  lệnh dự kiến (KHÔNG chạy ở lát này; cú pháp chờ spike xác nhận): {l}"
                 for l in kh.beads.lenh_du_kien]
    if kh.canh_bao:
        dong += ["Lưu ý:"] + [f"  - {c}" for c in kh.canh_bao]
    return "\n".join(dong)


def thuc_hien(kh: KeHoachDuAn) -> None:
    for p, noi_dung in kh.ghi.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(noi_dung)
