from dataclasses import dataclass, field

from tram.cham_cot.cham import cham_mot_bead


@dataclass
class KetQuaDanhGia:
    tong: int = 0
    khop: int = 0
    lech: list[tuple[str, str, str]] = field(default_factory=list)
    vi_pham_t1: list[str] = field(default_factory=list)

    @property
    def ti_le(self) -> float:
        return self.khop / self.tong if self.tong else 0.0


def danh_gia(du_an, mau: list[dict], *, beads, kho, client, vai) -> KetQuaDanhGia:
    """Chạy chế độ thử: không ghi beads, không dùng memory (`nho=None`). Đáp án từ bo-mau/<du_an>.yaml do Đại ca xếp."""
    theo_id = {x.id: x for x in beads}
    kq = KetQuaDanhGia()
    for m in mau:
        if m["id"] not in theo_id:
            raise KeyError(f"Bead mẫu {m['id']} không có trong beads")
        phan = cham_mot_bead(theo_id[m["id"]], du_an=du_an, theo_id=theo_id, kho=kho, client=client, vai=vai)
        kq.tong += 1
        if phan.cot == m["cot"]:
            kq.khop += 1
        else:
            kq.lech.append((m["id"], m["cot"], phan.cot))
        if m.get("cham_rao") and phan.cot == "ai-lam":
            kq.vi_pham_t1.append(m["id"])
    return kq
