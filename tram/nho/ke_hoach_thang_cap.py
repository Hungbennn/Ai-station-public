"""Kế hoạch ghi cho MỘT cặp thăng cấp (spec 1b §8, §6.3 "kiểm lại nội dung cuối"). Chưa đụng kho.

luật cứng trên hai bản gốc (danh sách mọi dự án) → LLM soạn bài học tổng quát → luật cứng + tên dự án trên nội dung
soạn → đích do trạm tính → embed → gộp trong phạm vi đích, CHỈ với ký ức đang chờ (bản đang hiệu lực: `giu_ca_hai`)
→ embed lại nội dung cuối. `nguon` = hai `{loai: thang_cap, id_goc, du_an}` → `nguon_dai_ca` luôn false."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tram.nho.embed import Embedder
from tram.nho.gop import TOI_DA_UNG_VIEN, KetQuaGop, gop, loc_ung_vien
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.luat_chung import ten_du_an_trong
from tram.nho.mo_hinh import BuocGhi, KyUc, ap_san, hop_nguon, la_nguon_dai_ca
from tram.nho.nho_lai import iso
from tram.nho.soan_thang_cap import soan
from tram.nho.thang_cap import CapThangCap, dich_thang_cap, du_an_cach_lam, id_thang_cap

CHO_HIEU_LUC = timedelta(days=7)          # #19: chờ 7 ngày rồi tự có hiệu lực


@dataclass(frozen=True)
class KetQuaCap:
    buoc: BuocGhi | None                  # None → không thăng cấp cặp này
    ly_do: list[str] = field(default_factory=list)
    tu_choi: bool = False                 # True: chạm luật (→ nho.tu_choi); False + buoc None: LLM không thấy bài học


def lap_ke_hoach_cap(cap: CapThangCap, *, kho: KhoKyUc, embedder: Embedder, client, vai_soan: tuple[str, str],
                     vai_gop: tuple[str, str], luat: LuatDuAn, cac_du_an: list[str], bay_gio: datetime) -> KetQuaCap:
    """`luat` = hợp luật của MỌI dự án đã `them`. LoiLLMNho / LoiEmbedder / anthropic.APIError nổi lên."""
    a, b = cap.a, cap.b
    ly = ly_do_nghiep_vu(a.noi_dung, luat) + ly_do_nghiep_vu(b.noi_dung, luat)
    if ly:
        return KetQuaCap(None, ly, True)
    s = soan(client, vai_soan, a.noi_dung, b.noi_dung)
    if not s.noi_dung:
        return KetQuaCap(None, ["LLM: hai ký ức không có bài học chung"])
    ly = ly_do_nghiep_vu(s.noi_dung, luat, co_ten_rieng=s.co_ten_rieng) + ten_du_an_trong(s.noi_dung, cac_du_an)
    if ly:
        return KetQuaCap(None, ly, True)
    pv, luc = dich_thang_cap(a, b), iso(bay_gio)
    v = embedder.embed([s.noi_dung])[0]
    tim_ra = kho.tim(v, [pv], mo_hinh=embedder.mo_hinh, gioi_han=TOI_DA_UNG_VIEN)
    ung = [k for k in loc_ung_vien(tim_ra, pv) if k.hieu_luc_tu > luc]
    g = gop(client, vai_gop, noi_dung_moi=s.noi_dung, moi_dai_ca=False, pham_vi=pv, ung_vien=ung, luat=luat)
    if g.noi_dung != s.noi_dung:
        if ten_du_an_trong(g.noi_dung, cac_du_an):     # câu gộp lộ tên dự án: bỏ gộp (giữ `thay`) như G8 của 1b-1
            gop_ids = {k.id for k in g.gop_tu}
            g = KetQuaGop(s.noi_dung, tuple(i for i in g.xoa if i not in gop_ids))
        else:
            v = embedder.embed([g.noi_dung])[0]
    goc = tuple({"loai": "thang_cap", "id_goc": k.id, "du_an": du_an_cach_lam(k.pham_vi)} for k in (a, b))
    nguon = hop_nguon(goc, *(k.nguon for k in g.gop_tu))
    ky = KyUc(id=id_thang_cap(cap.khoa), noi_dung=g.noi_dung, pham_vi=pv, nhan=s.nhan,
              quan_trong=ap_san(max([a.quan_trong, b.quan_trong] + [k.quan_trong for k in g.gop_tu]), nguon),
              nguon=nguon, nguon_dai_ca=la_nguon_dai_ca(nguon), hieu_luc_tu=iso(bay_gio + CHO_HIEU_LUC), tao_luc=luc,
              mo_hinh_embed=embedder.mo_hinh, vector=tuple(v))
    return KetQuaCap(BuocGhi(ky, g.xoa))
