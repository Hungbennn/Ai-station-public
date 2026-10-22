"""Xét `bao.xong` của phiếu `spec` tại SHA trạm đã công bố (spec 4 §7.2). Thứ tự: SHA công bố của lượt → đường dẫn
cấm (§6.2 bước 0) → diff từ gốc nhánh CHỈ trong `docs/**` → `docs/plans/<feature>.beads.json` + `spec_file` +
`plan_file` là file thường tại commit, JSON đạt kiểm → bàn giao theo luật `chinh-thuc` chặt (tiêu chí = nghiệm thu
sơ bộ của phiếu yêu cầu, không lệnh kiểm). `ly_do` None = hợp lệ (G5 của 4a-1; thêm `spec-ngoai-docs`,
`ke-hoach-loi`)."""
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from tram.ban_giao.schema import BanGiao, kiem_ban_giao
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import doc_file
from tram.giao_viec.ke_hoach import GIOI_HAN_BYTE, KeHoachBead, digest_ke_hoach, doc_ke_hoach, duong_ke_hoach
from tram.kiem.diff import diff_cham_cam, goc_nhanh, tep_doi
from tram.kiem.duong_dan_cam import khop_mau
from tram.phieu.mo_hinh import Phieu

SPEC_DUOC_DOI = "docs/**"


@dataclass(frozen=True)
class KetLuanSpec:
    ly_do: str | None
    loi: tuple[str, ...]
    commit: str | None
    cham_cam: tuple[str, ...] = ()
    ke_hoach: KeHoachBead | None = None
    digest: str | None = None


def doc_ke_hoach_tai(kho_git: Path, commit: str, feature: str) -> tuple[KeHoachBead | None, str | None, list[str]]:
    """(kế hoạch, digest, lỗi) tại `commit` — dùng cho xét `bao.xong`, ghi `spec.xong` và Duyệt (đọc lại từ Git)."""
    van_ban = doc_file(kho_git, commit, duong_ke_hoach(feature), gioi_han=GIOI_HAN_BYTE + 1)
    kh, loi = doc_ke_hoach(van_ban, feature)
    if kh is None:
        return None, None, loi
    loi = [f"Không thấy file thường {p} tại commit" for p in (kh.spec_file, kh.plan_file)
           if doc_file(kho_git, commit, p, gioi_han=1) is None]
    return (None, None, loi) if loi else (kh, digest_ke_hoach(van_ban), [])


def _ban_giao(bao: dict, phieu: Phieu, kho_git: Path, sha: str) -> list[str]:
    try:
        bg = BanGiao.model_validate(bao.get("ban_giao"))
    except ValidationError:
        return ["Khối bàn giao sai schema"]
    loi = list(bao.get("loi_ban_giao") or [])
    loi += kiem_ban_giao(bg, list(phieu.tieu_chi), kho_git, lenh_bat_buoc=[], can_lenh_kiem=False, commit=sha)
    return loi + (["commit trong khối bàn giao khác SHA công bố"] if bg.commit != sha else [])


def xet_xong_spec(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn, *,
                  them_cam: tuple[str, ...] = ()) -> KetLuanSpec:
    """`them_cam` (TM-3, D89): mẫu cấm từ ba lệnh deploy của dự án, cộng vào đường dẫn cấm."""
    if sha is None:
        return KetLuanSpec("chua-cong-bo", ("Lượt này chưa có commit trạm công bố",), None)
    if bao.get("commit") != sha:
        return KetLuanSpec("commit-khong-cong-bo", (f"bao.xong mang {bao.get('commit')}, ref công bố là {sha}",), None)
    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                         cho_phep=du_an.giao.duong_dan_cam_cho_phep)
    if cham:
        return KetLuanSpec("dong-file-cau-hinh", (f"Diff chạm đường dẫn cấm: {', '.join(cham)}",), sha, tuple(cham))
    goc = goc_nhanh(kho_git, f"origin/{du_an.nhanh_chinh}", sha)
    ngoai = [p for p in tep_doi(kho_git, goc, sha) if not khop_mau(p, SPEC_DUOC_DOI)]
    if ngoai:
        return KetLuanSpec("spec-ngoai-docs", (f"Khe spec chỉ được đổi docs/**: {', '.join(ngoai[:20])}",), sha)
    kh, dg, loi = doc_ke_hoach_tai(kho_git, sha, phieu.bead_id)
    if kh is None:
        return KetLuanSpec("ke-hoach-loi", tuple(loi[:20]), sha)
    loi = _ban_giao(bao, phieu, kho_git, sha)
    if loi:
        return KetLuanSpec("ban-giao-loi", tuple(dict.fromkeys(loi))[:20], sha)
    return KetLuanSpec(None, (), sha, (), kh, dg)
