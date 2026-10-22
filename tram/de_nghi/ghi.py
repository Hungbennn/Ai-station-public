"""Ghi MỘT đề nghị vào Beads (design D-2, D-5, D-6, D-7) qua `BdDeNghi` (actor `tram/de-nghi`). Trước mỗi lần ghi:
ĐỐI SOÁT dấu `<!-- ma_thao_tac: dn-… -->` (ghi chú của việc gốc; mô tả của việc mang nhãn `tram:agent-tao`) — đã có
thì ghi `de_nghi.da_ghi`, không ghi Beads lần hai (trạm tắt giữa `bd` và sự kiện). `kiem(loai)` (`cua.Cua.truoc_ghi`)
chạy NGAY TRƯỚC mỗi lệnh `bd` ghi, kể cả giữa `create` và `dep add` (Q11): ném `DungGhi`; việc đã tạo mà chưa liên kết
thì nhịp sau tìm lại theo dấu mã, chỉ nối liên kết. Chữ của agent chỉ vào GHI CHÚ (bộ chấm cột không đọc ghi chú) hoặc
mô tả việc mới; tiền tố, dòng `viec_goc:` và dấu mã do trạm viết."""
from collections.abc import Callable
from datetime import datetime

from tram.beads.bd_de_nghi import LOAI_PHAT_HIEN, NHAN_AGENT_TAO
from tram.de_nghi.cho import Cho, escalation_cua, ghi_ket_qua
from tram.de_nghi.cong import cong_viec_moi
from tram.de_nghi.cua import DungGhi
from tram.de_nghi.loc import ly_do_bi_chan
from tram.giao_viec.su_kien import su_kien_bead


def dau(ma: str) -> str:
    return f"<!-- ma_thao_tac: {ma} -->"


def dong_ghi_chu(c: Cho, chu: str, esc: str | None = None) -> str:
    nhan = "tiến độ" if c.loai == "tien_do" else "bị chặn"
    return f"[tram/de-nghi · {nhan} · {c.khe} · lượt {c.luot}] {chu}" + (f" (escalation {esc})" if esc else "") + \
        f"\n{dau(c.ma)}"


def mo_ta_viec_moi(c: Cho) -> str:
    return (f"Do agent tạo khi làm {c.bead_id} (khe {c.khe}, lượt {c.luot})\nviec_goc: {c.bead_id}\n\n"
            f"{c.du_lieu['viec_moi']['mo_ta']}\n\n{dau(c.ma)}")


def _viec_moi(kho, bd, beads: dict, c: Cho, goc, luc: datetime, kiem: Callable[[str], None]) -> str:
    kq, v = cong_viec_moi(su_kien_bead(kho, c.du_an, c.bead_id), c.giao_id, c.id, viec_dong=goc.status == "closed")
    if kq != "ghi":
        if kq == "bo":
            ghi_ket_qua(kho, c, "de_nghi.bo", {"ly_do": v}, luc=luc)
        return kq
    vm = c.du_lieu["viec_moi"]
    moi = next((b for b in beads.values() if NHAN_AGENT_TAO in b.labels and dau(c.ma) in b.description.splitlines()),
               None)
    if moi is None:
        kiem(c.loai)
        moi_id = bd.tao_viec_moi(vm["tieu_de"], loai=vm["loai_viec"], mo_ta=mo_ta_viec_moi(c),
                                 tieu_chi=vm.get("tieu_chi", ""))
    else:
        moi_id = moi.id
    if moi is None or (c.bead_id, LOAI_PHAT_HIEN) not in [(p.depends_on_id, p.loai) for p in moi.phu_thuoc]:
        try:
            kiem(c.loai)                                # Q11: đọc lại giữa `bd create` và `bd dep add`
        except DungGhi as e:
            if e.ly_do != "tat":
                raise                                   # giữ: nhịp sau tìm thấy việc theo dấu mã, chỉ nối liên kết
            ghi_ket_qua(kho, c, "de_nghi.bo", {"ly_do": "tat", "bead_moi": moi_id}, luc=luc)
            return "bo"
        bd.lien_ket_phat_hien(moi_id, c.bead_id)
    ghi_ket_qua(kho, c, "de_nghi.da_ghi", {"bead_id": c.bead_id, "bead_moi": moi_id, "vao_cot_3": v}, luc=luc)
    return "da_ghi"


def ghi_mot(kho, bd, beads: dict, c: Cho, luc: datetime, kiem: Callable[[str], None]) -> str:
    """→ "da_ghi" | "bo" | "cho". Lỗi `bd` (`LoiBd`) và `DungGhi` lan ra cho người gọi."""
    goc = beads.get(c.bead_id)
    if goc is None:
        ghi_ket_qua(kho, c, "de_nghi.bo", {"ly_do": "viec-da-dong"}, luc=luc)
        return "bo"
    if c.loai == "viec_moi":
        return _viec_moi(kho, bd, beads, c, goc, luc, kiem)
    esc, chu = None, c.du_lieu.get("noi_dung", "")
    if c.loai == "bi_chan":
        if (esc := escalation_cua(kho, c)) is None:
            if goc.status != "closed":
                return "cho"                            # escalation chưa tạo (cùng pha, nhịp sau)
            ghi_ket_qua(kho, c, "de_nghi.bo", {"ly_do": "viec-da-dong"}, luc=luc)
            return "bo"
        chu = ly_do_bi_chan(chu)
    if dau(c.ma) not in goc.notes.splitlines():
        kiem(c.loai)
        bd.cap_nhat_nhan(goc.id, ghi_chu=dong_ghi_chu(c, chu, esc))
    ghi_ket_qua(kho, c, "de_nghi.da_ghi", {"bead_id": goc.id, **({"escalation_id": esc} if esc else {})}, luc=luc)
    return "da_ghi"
