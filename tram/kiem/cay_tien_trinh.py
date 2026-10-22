"""Ảnh chụp tiến trình (lát P1, dot6-C02/Q02): `ps` của hệ thống — người dùng thường đọc được pid/ppid/pgid/uid/ruid
của MỌI tiến trình trên macOS, không cần sudo, không gửi tín hiệu. `uid` là UID HIỆU LỰC nhân ghi cho tiến trình,
không phải tên trong env. CHỈ lấy cột số (không `comm`): tên chương trình do agent đặt được, có thể chứa xuống dòng để
giả một dòng `ps` — dòng nào không đúng 5 số nguyên không âm làm cả ảnh chụp hỏng (người gọi coi như không xác nhận).
Cây của một lần chạy (V2-0, dot7-C01): gốc chưa gặt + con theo ppid + tiến trình ĐÃ THẤY là thành viên (cùng khoá
(pid, sinh)) + mọi tiến trình cùng NHÓM với một thành viên đã chứng minh trong CHÍNH ảnh đó. Số nhóm của ảnh cũ KHÔNG
còn là bằng chứng: nhóm có thể đã chết và số được cấp lại. Ai mang số nhóm cũ mà không chứng minh được → `mo_ho`.
Tiến trình rời cây (fork + setsid rồi cha thoát) GIỮA hai lần chụp không thấy được: ranh giới C01/3C-A, không phải lời
hứa của P1 — chỉ quét theo UID dành riêng (`tram-kiem`) bắt được."""
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from tram.kiem.lenh_ngan import chay_ngan

PS = ("/bin/ps", "-A", "-o", "pid=,ppid=,pgid=,uid=,ruid=")


@dataclass(frozen=True)
class TienTrinh:
    pid: int
    ppid: int
    pgid: int
    uid: int
    ruid: int
    sinh: int | None = None         # thời điểm sinh (µs) nhân ghi lúc fork — None: nguồn không có định danh sinh (`ps`)

    @property
    def khoa(self) -> tuple[int, int] | None:
        """Định danh MỘT lần sống: (pid, sinh). None → không chứng minh được là cùng tiến trình đã thấy."""
        return None if self.sinh is None else (self.pid, self.sinh)


def doc_ps(van_ban: bytes) -> list[TienTrinh]:
    ds = []
    for dong in van_ban.split(b"\n"):
        if not dong.strip():
            continue
        phan = dong.split()
        if len(phan) != 5 or not all(x.isdigit() for x in phan):
            raise ValueError("dòng ps sai dạng")
        ds.append(TienTrinh(*map(int, phan)))
    return ds


def chup_he(*, chay: Callable = chay_ngan) -> list[TienTrinh]:
    ma, ra = chay(list(PS), timeout=5, doc=True)
    if ma != 0:
        raise OSError(f"ps mã {ma}")
    return doc_ps(ra)


def cay(ds: Iterable[TienTrinh], goc: int | None, biet: set[tuple[int, int]]) -> list[TienTrinh]:
    """Cây trong MỘT ảnh chụp. Cùng nhóm với thành viên đã chứng minh ⇒ cùng phiên; phiên chỉ thừa kế qua fork, mà
    phiên của thành viên do chính cây tạo (gốc luôn `start_new_session`) — nên ai cùng nhóm cũng là hậu duệ."""
    ds, pids, nhom = list(ds), set(), set()
    doi = True
    while doi:
        doi = False
        for t in ds:
            if t.pid not in pids and (t.pid == goc or t.ppid in pids or t.khoa in biet or t.pgid in nhom):
                pids.add(t.pid)
                nhom |= {t.pgid} - {0, 1}
                doi = True
    return [t for t in ds if t.pid in pids]


def mo_ho(ds: Iterable[TienTrinh], con: list[TienTrinh], nhom_cu: set[int]) -> list[TienTrinh]:
    """Mang số nhóm cây từng có nhưng KHÔNG chứng minh được thuộc cây: mồ côi chưa từng thấy, hoặc nhóm khác được cấp
    lại cùng số. Không đoán — không gửi tín hiệu, thu hồi coi là chưa xác nhận."""
    trong = {t.pid for t in con}
    return [t for t in ds if t.pid not in trong and t.pgid in nhom_cu - {0, 1}]
