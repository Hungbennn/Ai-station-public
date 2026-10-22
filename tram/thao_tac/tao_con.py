"""Tạo bead con từ `*.beads.json` đã duyệt (spec 4 §7.3 bước 1–3) — idempotent theo `khoa`, đối soát sau sự cố (G7).

Mỗi con mang dòng đầu mô tả `<!-- khoa: <khoa> -->` và `--parent <feature>`. Con nào của feature đã có dòng đó thì
không tạo lại. `bd create` lỗi/không rõ kết quả → đọc lại và tìm theo dòng khoá trước khi coi là chưa tạo.
Phụ thuộc: `bd dep add <bead-sau> <bead-trước>` (KHÔNG `bd create --deps blocks:…` — chiều ngược, spike bd); bỏ cặp
đã có vì `bd dep add` lặp vẫn báo thành công."""
import re

from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.giao_viec.ke_hoach import KeHoachBead

DAU_KHOA = re.compile(r"<!-- khoa: ([a-z0-9-]{1,20}) -->")


def dong_khoa(khoa: str) -> str:
    return f"<!-- khoa: {khoa} -->"


def khoa_cua(b: Bead) -> str | None:
    dau = (b.description or "").split("\n", 1)[0].strip()
    m = DAU_KHOA.fullmatch(dau)
    return m.group(1) if m else None


def con_theo_khoa(beads: list[Bead], feature: str) -> dict[str, Bead]:
    ra: dict[str, Bead] = {}
    for b in sorted(beads, key=lambda x: x.id):
        if b.parent == feature and (k := khoa_cua(b)) is not None:
            ra.setdefault(k, b)
    return ra


def tao_con(bd, feature: str, kh: KeHoachBead) -> dict[str, str]:
    """{khoa: id} của MỌI bead trong kế hoạch, theo thứ tự file — tạo cái còn thiếu."""
    co = {k: b.id for k, b in con_theo_khoa(bd.tat_ca(), feature).items()}
    for x in kh.bead:
        if x.khoa in co:
            continue
        try:
            co[x.khoa] = bd.tao(x.tieu_de, loai=x.loai, mo_ta=f"{dong_khoa(x.khoa)}\n{x.mo_ta}", nhan=x.nhan,
                                uu_tien=x.uu_tien, nghiem_thu=x.nghiem_thu, cha=feature)
        except LoiBd:
            lai = con_theo_khoa(bd.tat_ca(), feature)
            if x.khoa not in lai:
                raise
            co[x.khoa] = lai[x.khoa].id
    return {x.khoa: co[x.khoa] for x in kh.bead}


def noi_phu_thuoc(bd, kh: KeHoachBead, theo_khoa: dict[str, str]) -> list[list[str]]:
    """Thêm phụ thuộc còn thiếu; trả các cặp [bead-sau, bead-trước] vừa thêm."""
    hien = {b.id: b for b in bd.tat_ca()}
    them = []
    for x in kh.bead:
        sau = theo_khoa[x.khoa]
        da = {p.depends_on_id for p in hien[sau].phu_thuoc if p.loai == "blocks"} if sau in hien else set()
        for k in x.phu_thuoc:
            if theo_khoa[k] not in da:
                bd.them_phu_thuoc(sau, theo_khoa[k])
                them.append([sau, theo_khoa[k]])
    return them
