"""Phụ thuộc của tram-api gom một chỗ — test thay bằng bản giả (tests/api_gia.py)."""
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tram.api.bo_dem import BoDemBeads
from tram.api.khach_nho import KhachNho
from tram.beads.bd import Bd
from tram.cau_hinh.tram import CauHinhTram
from tram.cau_hinh.usage import CauHinhUsage
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, KhongThay

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


@dataclass
class PhuThuocApi:
    cau_hinh: CauHinhTram
    cac_du_an: Callable[[], list[str]]
    tao_bd: Callable[[str], Bd]
    bo_dem: BoDemBeads
    mo_kho: Callable[[], KhoSuKien]
    mo_kho_tt: Callable[[], KhoThaoTac]
    nguon_spec: Callable | None = None
    thu_muc_tinh: Path | None = None
    mo_kho_phieu: Callable | None = None                 # spec 3 §6.6: kho phiếu (cùng su-kien.db) — None: tắt /api/tho
    chon_phieu: Callable | None = None                   # phần 4 `chon_phieu(khe_id, han_muc)`; None: không phát phiếu
    con_hop_le_phieu: Callable = lambda d: True          # 4a-2: phần 4 kiểm lại trong giao dịch cấp phiếu
    bo_giao: object | None = None                        # 4a-2: BoGiaoViec — dashboard đọc lý do không giao, PR
    mo_so_nhan: Callable | None = None                   # 4d: sổ tiếp nhận yêu cầu tạo feature; None → tạo trả 503
    tao_bd_yeu_cau: Callable[[str], Bd] | None = None    # 4d: Bd actor dai-ca/may-a, kho theo du-an/<ten>.yaml
    doc_token_noi_bo: Callable[[], str | None] = lambda: None
    dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    nho: KhachNho | None = None          # lát 1b-3: memory service (None → /api/nho/* trả 503)
    usage: CauHinhUsage = field(default_factory=CauHinhUsage)   # 2b: khoá `usage:` (bảng giá, ccusage)
    doc_ccusage: Callable | None = None                         # 2b: `(tu, den) -> KetQuaCcusage`; None: chưa cấu hình
    bat_ghi: Callable[[str], bool] = lambda ten: True           # lát 1a-2 (D31): False → từ chối thao tác ghi bead
    nguon_duyet: Callable | None = None                       # kho kiểm + nhánh chính + gh cho Duyệt cột 3


def kiem_du_an_bead(pt: PhuThuocApi, du_an: str, bead_id: str | None = None) -> None:
    """Chặn tên dự án lạ (không bao giờ dựng đường dẫn repo từ URL) và mã bead có thể thành cờ `bd`."""
    if du_an not in pt.cac_du_an():
        raise KhongThay(f"Không có dự án {du_an}")
    if bead_id is not None and not ID_RE.fullmatch(bead_id):
        raise KhongHopLe("Mã bead không hợp lệ")


def phu_thuoc_that() -> PhuThuocApi:
    from tram.thao_tac.duyet_spec import nguon_spec_that
    from tram.thao_tac.duyet_merge import nguon_duyet_that
    from tram.api.noi_bo import doc_mot_lan
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.cau_hinh.usage import nap_cau_hinh_usage
    from tram.duong_dan import goc_repo
    from tram.phieu.kho import mo_kho_phieu
    from tram.su_kien.kho import mo_kho
    from tram.thao_tac.kho import mo_kho_thao_tac
    from tram.usage.bo_dem import BoDemCcusage
    from tram.usage.ccusage import DocCcusage
    from tram.yeu_cau.mau import TAC_NHAN_A
    from tram.yeu_cau.so_nhan import mo_so_nhan

    def tao_bd(ten: str) -> Bd:
        return Bd(nap_du_an(ten).duong_dan, actor=TAC_NHAN)

    dist = goc_repo() / "frontend" / "dist"
    cu = nap_cau_hinh_usage()
    doc_cc = BoDemCcusage(DocCcusage(cu.ccusage, cu.ccusage_phien_ban).theo_ngay).lay if cu.ccusage else None
    return PhuThuocApi(
        mo_so_nhan=mo_so_nhan, tao_bd_yeu_cau=lambda ten: Bd(nap_du_an(ten).duong_dan, actor=TAC_NHAN_A),
        nguon_spec=nguon_spec_that, nguon_duyet=nguon_duyet_that,
        cau_hinh=nap_cau_hinh_tram(),
        cac_du_an=lambda: [t for t in liet_ke_du_an() if not t.startswith("_")],
        tao_bd=tao_bd, bo_dem=BoDemBeads(tao_bd), mo_kho=mo_kho, mo_kho_tt=mo_kho_thao_tac,
        thu_muc_tinh=dist if dist.is_dir() else None, mo_kho_phieu=mo_kho_phieu, doc_token_noi_bo=doc_mot_lan(),
        nho=KhachNho(), usage=cu, doc_ccusage=doc_cc, bat_ghi=bat_ghi)
