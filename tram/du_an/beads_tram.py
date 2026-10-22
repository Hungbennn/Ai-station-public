"""Bước (3) của `tram du-an them` (spec 0+1a §4.7): trỏ beads của dự án về trạm chủ.

Lát 1a-2 chỉ kiểm điều kiện và in lệnh dự kiến — KHÔNG chạy lệnh nào, không gọi `bd`, không đụng Dolt.
Thực thi chờ cổng spike beads từ xa (§4.6, T6, bead bs-g28.4) rồi một lát sau spike.
"""
import shlex
from dataclasses import dataclass
from pathlib import Path

CONG = "spike beads từ xa §4.6 (T6, bead bs-g28.4)"
DONG_DAT = "Kết luận: đạt"


@dataclass(frozen=True)
class BuocBeads:
    trang_thai: str                    # khong_dung_beads | cho_cong | cho_lat_sau
    ly_do: str
    lenh_du_kien: tuple[str, ...] = ()


def spike_dat(goc: Path) -> Path | None:
    """File kết luận spike (`docs/spikes/*-beads-tu-xa.md`, §4.6) có một dòng đúng 'Kết luận: đạt'."""
    for p in sorted((goc / "docs" / "spikes").glob("*-beads-tu-xa.md")):
        if any(dong.strip() == DONG_DAT for dong in p.read_text(encoding="utf-8").splitlines()):
            return p
    return None


def xet_beads(repo: Path, *, goc: Path, may_b: str | None) -> BuocBeads:
    if not (repo / ".beads").is_dir():
        return BuocBeads("khong_dung_beads", "repo chưa có .beads/ — không có gì để trỏ")
    lenh = (f"bd -C {shlex.quote(str(repo))} dolt set host {may_b or '<ten_may_b>'}",)
    ket_luan = spike_dat(goc)
    if ket_luan is None:
        return BuocBeads("cho_cong", f"chờ cổng {CONG}: chưa có docs/spikes/*-beads-tu-xa.md ghi '{DONG_DAT}'",
                         lenh)
    thieu = "" if may_b else "; ~/.tram/cau-hinh.yaml chưa có ten_may_b"
    return BuocBeads("cho_lat_sau", f"spike đạt ({ket_luan.name}) nhưng lát này chưa cài bước thực thi{thieu} "
                     "— Đại ca làm tay theo kết luận spike", lenh)
