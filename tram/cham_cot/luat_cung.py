import fnmatch
import re
import unicodedata
from dataclasses import dataclass

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao

LOAI_CHAN = "blocks"
DUONG_DAN_RE = re.compile(r"[\w.\-]+(?:/[\w.\-]+)+")
ADR_RE = re.compile(r"\bADR-\d{4}\b")


@dataclass(frozen=True)
class KetQuaLuat:
    cham: tuple[str, ...]
    da_chot: bool
    la_decision_mo: bool
    bi_chan_boi: tuple[str, ...]

    @property
    def ep_cot_2(self) -> bool:
        return self.la_decision_mo or (bool(self.cham) and not self.da_chot)

    def ly_do(self) -> str:
        if self.la_decision_mo:
            return "Bead quyết định đang mở — chờ Đại ca chốt."
        return f"Chạm hàng rào: {'; '.join(self.cham)}; chưa có quyết định liên kết."


def _chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s).casefold()


def _cham_loai(loai: str, rao: HangRao, van_ban: str, duong: list[str], nhan: set[str]) -> str | None:
    for tu in rao.tu_khoa:
        if re.search(rf"(?<!\w){re.escape(_chuan(tu))}(?!\w)", van_ban):
            return f"{loai} (từ khoá '{tu}')"
    for d in duong:
        if any(fnmatch.fnmatch(d, g) for g in rao.duong_dan):
            return f"{loai} (đường dẫn {d})"
    trung = sorted(nhan & set(rao.nhan))
    return f"{loai} (nhãn {trung[0]})" if trung else None


def _chan(bead: Bead) -> list[str]:
    return [p.depends_on_id for p in bead.phu_thuoc if p.loai == LOAI_CHAN]


def quyet_dinh_da_chot(bead: Bead, theo_id: dict[str, Bead]) -> list[Bead]:
    """Decision đã đóng mà bead phụ thuộc loại `blocks` (§5.2 mục 3; đưa vào prompt v2 — §5.3)."""
    return [b for i in _chan(bead)
            if (b := theo_id.get(i)) is not None and b.issue_type == "decision" and b.status == "closed"]


def bi_chan_boi(bead: Bead, theo_id: dict[str, Bead]) -> tuple[str, ...]:
    """Phụ thuộc `blocks` tới bead chưa đóng **hoặc không có trong snapshot** (fail-closed)."""
    return tuple(i for i in _chan(bead) if (b := theo_id.get(i)) is None or b.status != "closed")


def kiem(bead: Bead, du_an: DuAn, theo_id: dict[str, Bead]) -> KetQuaLuat:
    goc = bead.van_ban()
    van_ban, duong, nhan = _chuan(goc), DUONG_DAN_RE.findall(goc), set(bead.labels)
    cham = tuple(c for loai, rao in du_an.hang_rao.items()
                 if (c := _cham_loai(loai, rao, van_ban, duong, nhan)))
    da_chot = bool(ADR_RE.search(goc)) or bool(quyet_dinh_da_chot(bead, theo_id))
    la_decision_mo = bead.issue_type == "decision" and bead.status != "closed"
    return KetQuaLuat(cham, da_chot, la_decision_mo, bi_chan_boi(bead, theo_id))
