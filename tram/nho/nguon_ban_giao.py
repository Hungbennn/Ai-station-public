"""Nguồn ký ức `ban_giao` (spec 1b §6.1, hàng "Bàn giao chính thức đã qua kiểm"; Đại ca chốt D8 15/10).

Hai cửa kích hoạt, cả hai do bộ giao việc ghi:
- bead thường: `qc.ket_qua {ket_luan: "dat", commit_code}` → `kiem.lai` đạt cùng bead, `commit = commit_code`, ghi
  trước nó (đúng cặp mà `pipeline.buoc_ke_tiep` dùng để vào cột 3). `kiem.lai` đạt một mình CHƯA đủ;
- spike tài liệu (không QC): `kiem.lai {dat: true, ket_qua: []}` — kiểm lại không chạy lệnh (`chay_lenh = False`).
Từ `kiem.lai` đó: `bao.xong` cùng `giao_id` (thợ gửi) cho `quyet_dinh`, `huong_da_bo`, `vuong_mac`; `giao.nhan` cùng
`giao_id` (tram-api ghi lúc cấp phiếu) cho `vai`. Nội dung bàn giao do AGENT viết — không tin cậy: chỉ vào bước tách
(bọc `<du_lieu_khong_tin_cay>`), nguồn `ban_giao` không bao giờ là nguồn Đại ca, gốc ghi do trạm quyết. Ba danh sách
được quét bí mật (D23) trên bản gốc chưa cắt, TRƯỚC khi dựng văn bản: có dấu hiệu → `LoiBiMat`, bỏ cả bàn giao."""
import re
from collections.abc import Callable

from tram.ban_giao.schema import BanGiao
from tram.giao_viec.su_kien import TAC_NHAN as TAC_NHAN_GIAO_VIEC
from tram.nho.bi_mat import chan_bi_mat
from tram.nho.nguon import DauVao, _cat, _cat_dong
from tram.nho.pham_vi import TEN
from tram.phieu.kho import TAC_NHAN as TAC_NHAN_API
from tram.su_kien.kho import KhoSuKien, SuKien

TIEN_TO_THO = "tho/"          # bao.* do thợ gửi qua POST /api/tho/bao (tram/phieu/bao.py)
TOI_DA_MUC = 8                # mỗi danh sách của bàn giao
DO_DAI_MUC = 400              # ký tự mỗi mục; cả văn bản ≤ DO_DAI_VAN_BAN (4000) qua _cat_dong


def truoc(kho_sk: KhoSuKien, sk: SuKien, loai: str, khop: Callable[[SuKien], bool]) -> SuKien | None:
    """Sự kiện `loai` mới nhất CÙNG dự án + bead, ghi TRƯỚC `sk`, thoả `khop` — không nhìn sang dự án khác."""
    return kho_sk.moi_nhat(sk.du_an, sk.bead_id, loai, dieu_kien=lambda s: s.id < sk.id and khop(s))


def _gv(s: SuKien) -> bool:
    return s.tac_nhan == TAC_NHAN_GIAO_VIEC and isinstance(s.du_lieu, dict)


def _cung_giao(gid: str) -> Callable[[SuKien], bool]:
    return lambda s: isinstance(s.du_lieu, dict) and s.du_lieu.get("giao_id") == gid


def _kiem_lai_nguon(sk: SuKien, kho_sk: KhoSuKien) -> SuKien | None:
    """`kiem.lai` có bàn giao cần nạp, hoặc None (chưa/không phải nguồn, đã nạp). Lỗi dữ liệu → ValueError."""
    d = sk.du_lieu
    if sk.loai == "kiem.lai":                              # chỉ spike: bead thường chờ QC đạt (D8)
        if d.get("dat") is not True or d.get("ket_qua") != []:
            return None
        gid = d.get("giao_id")
        if not isinstance(gid, str) or not gid:
            raise ValueError("kiem.lai: thiếu giao_id")
        da_co = truoc(kho_sk, sk, "kiem.lai", lambda s: _gv(s) and _cung_giao(gid)(s) and s.du_lieu.get("dat") is True)
        return None if da_co else sk
    if d.get("ket_luan") != "dat":                         # qc.ket_qua: tra_ve, khong_cong_nhan → không nạp
        return None
    code = d.get("commit_code")
    if not isinstance(code, str) or not code:
        raise ValueError("qc.ket_qua: thiếu commit_code")
    kl = truoc(kho_sk, sk, "kiem.lai", lambda s: _gv(s) and s.du_lieu.get("dat") is True
               and s.du_lieu.get("commit") == code)
    if kl is None:
        raise ValueError(f"qc.ket_qua: không thấy kiem.lai đạt của commit {code[:12]}")
    if truoc(kho_sk, sk, "qc.ket_qua", lambda s: _gv(s) and s.id > kl.id
             and s.du_lieu.get("ket_luan") == "dat" and s.du_lieu.get("commit_code") == code):
        return None                                        # chỉ trùng QC sau chính lần kiểm này
    return kl


def _vai(kho_sk: KhoSuKien, kl: SuKien, gid: str) -> str:
    nhan = truoc(kho_sk, kl, "giao.nhan", lambda s: s.tac_nhan == TAC_NHAN_API and _cung_giao(gid)(s))
    vai = nhan.du_lieu.get("vai") if nhan else None
    if not isinstance(vai, str) or not re.fullmatch(TEN, vai):
        raise ValueError(f"kiem.lai: không rõ vai của phiếu {gid}")
    return vai


def _ban_giao(kho_sk: KhoSuKien, kl: SuKien, gid: str) -> BanGiao:
    bao = truoc(kho_sk, kl, "bao.xong", lambda s: s.tac_nhan.startswith(TIEN_TO_THO) and _cung_giao(gid)(s))
    if bao is None:
        raise ValueError(f"kiem.lai: không thấy bao.xong của phiếu {gid}")
    if bao.du_lieu.get("luot") != kl.du_lieu.get("luot"):
        raise ValueError(f"kiem.lai: lượt của bao.xong khác lượt kiểm lại ({gid})")
    try:
        bg = BanGiao.model_validate(bao.du_lieu.get("ban_giao"))
    except ValueError:
        raise ValueError("bao.xong: bàn giao sai schema") from None  # không log input_value của agent
    if bg.loai != "chinh-thuc":
        raise ValueError("bao.xong: bàn giao không chính thức")
    return bg


def _muc(ds: list[str]) -> list[str]:
    return [f"- {_cat(x, DO_DAI_MUC)}" for x in ds if x.strip()][:TOI_DA_MUC]


def doc_ban_giao(sk: SuKien, kho_sk: KhoSuKien) -> DauVao | None:
    """`sk` là `kiem.lai` hoặc `qc.ket_qua`. None: không phải nguồn (sai tác nhân, chưa/không đạt, đã nạp, bàn giao
    không có bài học). ValueError: sự kiện độc — `nho.loi_tach`, bỏ, mốc tiến. LoiBiMat: có dấu hiệu bí mật (D23) —
    `nho.bo_bi_mat`, bỏ, mốc tiến. Nguồn mang id của `sk`."""
    if sk.tac_nhan != TAC_NHAN_GIAO_VIEC:
        return None
    if not sk.bead_id:
        raise ValueError(f"{sk.loai}: thiếu bead_id")
    kl = _kiem_lai_nguon(sk, kho_sk)
    if kl is None:
        return None
    gid = kl.du_lieu.get("giao_id")
    if not isinstance(gid, str) or not gid:
        raise ValueError("kiem.lai: thiếu giao_id")
    vai, bg = _vai(kho_sk, kl, gid), _ban_giao(kho_sk, kl, gid)
    huong = [f"{h.huong} — vì {h.vi_sao}" for h in bg.huong_da_bo]
    chan_bi_mat("ban_giao", [*bg.quyet_dinh, *huong, *bg.vuong_mac])     # D23: trước LLM, embed, lưu
    dong = []
    for tieu_de, ds in (("Quyết định kỹ thuật:", bg.quyet_dinh), ("Hướng đã bỏ:", huong), ("Vướng mắc:", bg.vuong_mac)):
        if muc := _muc(ds):
            dong += [tieu_de, *muc]
    if not dong:
        return None
    kiem = "trạm kiểm lại và QC đạt" if sk.loai == "qc.ket_qua" else "spike, trạm kiểm tài liệu đạt"
    dau = (f"Bàn giao chính thức của bead {sk.bead_id} (vai {vai}, lượt {kl.du_lieu.get('luot')}), {kiem} ngày "
           f"{sk.luc[:10]}. Phần dưới do agent viết, Đại ca chưa xác nhận:")
    return DauVao(sk.id, sk.du_an, sk.bead_id, "ban_giao", van_ban=_cat_dong([dau, *dong]), luc=sk.luc, vai=vai)
