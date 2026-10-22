"""Lệnh `tram du-an them|go <repo>`: in kế hoạch (diff đầy đủ + bước beads), chờ đồng ý rồi mới ghi (Q15)."""
from pathlib import Path

from tram.du_an.ke_hoach import in_ke_hoach, lap_ke_hoach, thuc_hien
from tram.du_an.khoi import KhoiHong


def chay(repo: Path, them: bool, dong_y: bool, *, ten: str | None = None, gitnexus: str | None = None,
         ghi_de: bool = False) -> int:
    if not repo.is_dir():
        print(f"Không thấy thư mục repo: {repo}")
        return 2
    try:
        kh = lap_ke_hoach(repo, them=them, ten=ten, gitnexus=gitnexus, ghi_de=ghi_de)
    except KhoiHong as e:
        print(f"{e}. Sửa tay dấu khối rồi chạy lại. Không ghi file nào.")
        return 2
    except ValueError as e:
        print(f"{e}. Không ghi file nào.")
        return 2
    if (ban := in_ke_hoach(kh)):
        print(ban)
    if not kh.ghi:
        print("Không có gì thay đổi.")
        return 0
    if not dong_y and input("Gõ dong-y để ghi: ").strip() != "dong-y":
        print("Không ghi.")
        return 1
    thuc_hien(kh)
    print("Đã ghi. Trạm không commit — Đại ca tự commit trong repo dự án và repo trạm (du-an/).")
    return 0
