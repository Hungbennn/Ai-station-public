"""Xét tự merge (spec `tu-merge`, design D-2; D70–D72, D76, D90–D93, D112) — hàm thuần trả danh sách MÃ lý do,
rỗng = được merge. Thứ tự cố định: khoá chung (`tram.tu_dong.khoa`: estop → tạm dừng toàn trạm → tạm dừng dự án →
`bat_ghi` → công tắc) → QC → kiểm lại → đúng PR → đầu PR → cấu trúc DB / xoá dữ liệu (luôn) → file ba lệnh dùng
(luôn, D89) → CI → cột → hàng rào. Ba điều kiện cuối theo nút của dự án; QC, kiểm lại, cấu trúc DB, file lệnh không
có nút (D71, D76, D89). Mã lý do là hợp đồng với
dashboard (`NHAN`, `MUC`) và nằm trong sự kiện `tu_merge.cho` — không chứa tên file, từ khoá hay nội dung bead."""
from dataclasses import dataclass

from tram.giao_viec.bang_chung import bo_bang_chung
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.tu_dong.khoa import NHAN_LY_DO, ly_do_chan
from tram.tu_dong.luu import TrangThaiTuDong

NHAN = {**NHAN_LY_DO,
        "cong_kiem": "Cổng kiểm đóng hoặc chưa đọc được",
        "deploy_chua_ro": "Deploy chưa đối soát — cần Đại ca xác nhận bản thực tế",
         "du_lieu_loi": "Dữ kiện chưa đủ hoặc việc còn bị chặn — chờ xét lại",
        "du_lieu_doi": "Dữ kiện duyệt spec đã đổi — chờ xét lại", "qc": "QC chưa đạt cho đúng commit này",
        "kiem_lai": "Kiểm lại chưa đạt hoặc bằng chứng hết hiệu lực", "pr_khac": "PR không phải PR trạm đã mở",
        "dau_pr_khac": "Đầu PR khác commit đã kiểm", "schema_duong_dan": "Cấu trúc DB — luôn chờ Đại ca",
        "schema_tu_khoa": "Nội dung việc nhắc cấu trúc DB / xoá dữ liệu — luôn chờ Đại ca",
        "ci_do": "CI chưa xanh", "ci_rong": "CI chưa xanh — repo chưa có CI",
        "ci_dang_chay": "CI đang chạy — xét lại vòng sau", "cot": "Đại ca đã tự gán cột",
        "hang_rao_tien": "Chạm hàng rào: tiền/giá", "hang_rao_quyen": "Chạm hàng rào: quyền/bảo mật",
        "hang_rao_khach_thay": "Chạm hàng rào: thứ khách thấy", "hang_rao_co_do": "Cờ đỏ",
        "tu_merge_loi": "Tự merge lỗi — cần Đại ca", "pr_khong_xac_minh": "Trạm không xác minh được merge — cần Đại ca",
        "diff_loi": "Không đọc được thay đổi của việc — chờ Đại ca",
        "file_lenh": "Sửa file mà lệnh deploy / kiểm còn sống / lùi dùng — luôn chờ Đại ca",
        "file_lenh_loi": "Không đọc được file mà ba lệnh dùng — chờ Đại ca"}
MUC = {"schema_duong_dan": "loi", "schema_tu_khoa": "loi", "diff_loi": "loi", "tu_merge_loi": "loi",
       "file_lenh": "loi", "file_lenh_loi": "loi", "ci_dang_chay": "tat"}


@dataclass(frozen=True)
class DuKien:
    """Điều trạm đọc được về một bead ở cột 3, tại `commit_ban_giao` của bằng chứng hiện hành."""
    qc_dat: bool
    kiem_lai_dat: bool
    dung_pr: bool                       # PR là PR trạm đã ghi ở `pr.mo`: số, nhánh `tram/<bead>`, base, cùng repo
    dau_pr_dung: bool                   # đầu PR đúng commit đã kiểm
    schema: tuple[str, ...] = ()        # schema_duong_dan, schema_tu_khoa (D76, D92, D112); diff_loi
    ci: str = "rong"                    # xanh | do | dang_chay | rong (D93)
    cot_ai: bool = True                 # không có `cot-khoa` (D90)
    hang_rao: tuple[str, ...] = ()      # hang_rao_<loai> theo đường dẫn diff; hang_rao_co_do (D91)
    file_lenh: tuple[str, ...] = ()     # file_lenh / file_lenh_loi — từ ba lệnh của cài đặt ĐỌC LẠI (D89)


def ly_do_chua_merge(tt: TrangThaiTuDong, dk: DuKien, *, bat_ghi: bool, estop_bat: bool) -> list[str]:
    cd = tt.cai_dat
    ra = ly_do_chan(tt, viec="merge", bat_ghi=bat_ghi, estop_bat=estop_bat)
    ra += [m for m, chan in (("qc", not dk.qc_dat), ("kiem_lai", not dk.kiem_lai_dat), ("pr_khac", not dk.dung_pr),
                             ("dau_pr_khac", not dk.dau_pr_dung)) if chan]
    ra += [*dk.schema, *dk.file_lenh]
    ra += [f"ci_{dk.ci}"] if dk.ci != "xanh" else []
    ra += ["cot"] if cd.dk_cot and not dk.cot_ai else []
    return ra + (list(dk.hang_rao) if cd.dk_hang_rao else [])


def ly_do_chua_merge_spec(tt: TrangThaiTuDong, *, dung_pr: bool, dau_pr_dung: bool, bat_ghi: bool,
                          estop_bat: bool, file_lenh: tuple[str, ...] = ()) -> list[str]:
    """PR spec đã duyệt (D95, design D-11): khoá chung + đúng PR + đầu PR đúng commit của lần duyệt mới nhất + file ba
    lệnh dùng (D89, bắt buộc như việc code). Năm điều kiện còn lại của việc code không áp — lần duyệt của Đại ca thay
    QC, spec chỉ đổi tài liệu đã kiểm lúc `spec.xong`."""
    ra = ly_do_chan(tt, viec="merge", bat_ghi=bat_ghi, estop_bat=estop_bat)
    return ra + [m for m, chan in (("pr_khac", not dung_pr), ("dau_pr_khac", not dau_pr_dung)) if chan] + [*file_lenh]


def kiem_lai_qc(ds: list[SK], v: SK) -> tuple[bool, bool]:
    """(QC đạt, kiểm lại đạt) cho ĐÚNG bằng chứng `v` (`bead.vao_cot_3` hiện hành) — tính lại từ sự kiện, không tin
    nhãn. Kiểm lại: lượt code mới nhất đạt tại `commit_code` của `v`. QC: kết luận đạt sau lần kiểm lại đó, cho đúng
    commit, do khe KHÁC khe đã code (INV-006); thiếu sự kiện nhận việc của khe QC → không đạt (đóng khi không biết)."""
    d, w = v.du_lieu, cua_so(ds)
    ket = moi_nhat(w, "kiem.lai")
    if ket is None or ket.du_lieu.get("nguon_kiem") != "uq" or any(
            ket.du_lieu.get(a) != d.get(b) for a, b in (
                ("luot", "luot_code"), ("giao_id", "giao_id_code"),
                ("commit", "commit_code"), ("digest_tieu_chi", "digest_tieu_chi"))):
        return False, False
    kl = bo_bang_chung("", ds, la_spike=True)
    kl_dat = kl is not None and (kl["commit_code"], kl["giao_id_code"]) == (d["commit_code"], d["giao_id_code"])
    bc = bo_bang_chung("", ds, la_spike=False)
    if not kl_dat or bc is None or bc["commit_ban_giao"] != d["commit_ban_giao"]:
        return False, kl_dat
    khe = {s.du_lieu["giao_id"]: s.du_lieu.get("khe_id") for s in w if s.loai == "giao.nhan"}
    qk = moi_nhat(w, "qc.ket_qua")
    return khe.get(qk.du_lieu.get("giao_id")) not in (None, khe.get(bc["giao_id_code"])), True
