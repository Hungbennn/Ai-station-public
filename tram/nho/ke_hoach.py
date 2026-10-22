"""Lập kế hoạch ghi cho một sự kiện nguồn (spec 1b §6.2): tất định trước, LLM sau (Q5).

tách (LLM, hoặc dựng sẵn) → luật cứng nghiệp vụ (ghi đè LLM) → đặt phạm vi (gốc do trạm) → embed → gộp trong
cùng phạm vi → embed lại nội dung cuối. Chưa đụng kho: kết quả là danh sách BuocGhi để lưu vào nhật ký."""
from tram.nho.embed import Embedder
from tram.nho.gop import TOI_DA_UNG_VIEN, gop, loc_ung_vien
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.mo_hinh import BuocGhi, KyUc, ap_san, hop_nguon, id_ky_uc, la_nguon_dai_ca
from tram.nho.nguon import DauVao
from tram.nho.pham_vi import pham_vi_du_an
from tram.nho.tach import KyUcTach, tach

PHIEN_BAN = 1          # phiên bản pipeline — thành phần của ID thao tác bền (§6.4)


def cac_ky_uc_tach(dv: DauVao, client, vai_tach: tuple[str, str]) -> list[KyUcTach]:
    if dv.tat_dinh is not None:                       # cot.dai_ca_sua không vi_sao, nho.agent_ghi: không gọi LLM
        return [KyUcTach(dv.tat_dinh, "cach-lam", dv.nhan)]
    return tach(client, dv.van_ban, vai=vai_tach)[0]


def nhanh_cuoi(dv: DauVao, k: KyUcTach, luat: LuatDuAn) -> str:
    """da_chot luôn nghiep-vu; chạm luật cứng → nghiep-vu; còn lại theo LLM."""
    if dv.ep_nghiep_vu or ly_do_nghiep_vu(k.noi_dung, luat, co_ten_rieng=k.co_ten_rieng):
        return "nghiep-vu"
    return k.nhanh


def lap_ke_hoach(dv: DauVao, *, kho: KhoKyUc, embedder: Embedder, client, vai_tach: tuple[str, str],
                 vai_gop: tuple[str, str], luat: LuatDuAn, luc: str) -> list[BuocGhi]:
    """Lỗi tách hết lượt → LoiLLMNho; embedder lỗi → LoiEmbedder. Cả hai: chưa ghi gì.

    `tao_luc` = `hieu_luc_tu` = giờ sự kiện nguồn (`dv.luc`) — nạp lịch sử không làm ký ức cũ thành "mới";
    chỉ bản gộp lấy `luc` (bây giờ, §6.3)."""
    nguon = (dv.nguon,)
    buoc, da_xoa = [], set()                      # id cũ đã gop/thay ở bước trước: không là ứng viên nữa
    for i, t in enumerate(cac_ky_uc_tach(dv, client, vai_tach)):
        pv = pham_vi_du_an(dv.du_an, nhanh_cuoi(dv, t, luat))
        v = embedder.embed([t.noi_dung])[0]
        tim_ra = kho.tim(v, [pv], mo_hinh=embedder.mo_hinh, gioi_han=TOI_DA_UNG_VIEN + len(da_xoa))
        ung = loc_ung_vien([(k, cos) for k, cos in tim_ra if k.id not in da_xoa], pv)
        g = gop(client, vai_gop, noi_dung_moi=t.noi_dung, moi_dai_ca=la_nguon_dai_ca(nguon), pham_vi=pv,
                ung_vien=ung, luat=luat)
        if g.noi_dung != t.noi_dung:
            v = embedder.embed([g.noi_dung])[0]           # vector luôn biểu diễn đúng văn bản đã lưu
        nguon_cuoi = hop_nguon(nguon, *(k.nguon for k in g.gop_tu))
        q = ap_san(max([t.quan_trong] + [k.quan_trong for k in g.gop_tu]), nguon_cuoi)
        moc = luc if g.gop_tu else (dv.luc or luc)
        ky = KyUc(id=id_ky_uc(dv.su_kien_id, PHIEN_BAN, i), noi_dung=g.noi_dung, pham_vi=pv, nhan=t.nhan,
                  quan_trong=q, nguon=nguon_cuoi, nguon_dai_ca=la_nguon_dai_ca(nguon_cuoi), hieu_luc_tu=moc,
                  tao_luc=moc, mo_hinh_embed=embedder.mo_hinh, vector=tuple(v))
        buoc.append(BuocGhi(ky, g.xoa))
        da_xoa.update(g.xoa)
    return buoc
