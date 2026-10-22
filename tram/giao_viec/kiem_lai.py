"""Kiểm lại của trạm (spec 4 §6.2 — "báo xong" khác "đã kiểm chứng"): gắn MỘT commit = SHA công bố của lượt.

0. đường dẫn cấm từ gốc nhánh — TRƯỚC khi chạy bất cứ lệnh nào; 1. bản chép kiểm tại commit trong kho kiểm
(3c); 2. spike tài liệu: dừng ở đây (không chạy lệnh); 3. chép môi trường kiểm; 4. chạy MỌI lệnh bắt buộc của phiếu
(khớp `lenh_cho_phep`, không shell, 15 phút/lệnh, kill cả nhóm); 5. đạt ⇔ mọi lệnh chạy được và pass.
`boc` chọn principal `tram-kiem` (phần 3 §7.3 mục 5 — chờ S6); mã này không tự chạy dưới quyền trạm.
Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (`ban_chep.py` — `git archive` → `tar -x` dưới
`tram-kiem`, môi trường kiểm qua stdin, `tram-kiem` tự dọn; repo git MỘT commit do `tram-kiem` tự dựng — D40 (b);
không worktree, không trao quyền). Một lần kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không
sạch → ném, KHÔNG trả kết quả. 3C-D (C01, D45): `cong` mở mới được vào lượt (trước khi chép, nhận môi trường); mọi
lệnh của lượt qua `boc_luot(wt)` (hồ sơ Seatbelt của lượt); lượt ném lỗi → đóng cổng; xong → `cong.ra()` thu hồi và
quan sát. Hợp đồng P1 (H6): dấu hạn tổng `kiem-lai.dong` còn → từ chối trước cổng (trừ `chu_dau`: chính harness S6
đang giữ dấu đó); P1 báo chưa thu hồi cây của một lệnh (`da_thu_hoi=False`) → ném, không công nhận, cổng đóng."""
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.lenh import khop_bat_ky
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import (CayKhacNguon, LoiBanChep, chep_ban, don_ban, giu_khoa, nhan_moi_truong,
                                     ten_ban_chep)
from tram.giao_viec.cong_luot import CongLuot
from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
from tram.kiem.diff import diff_cham_cam
from tram.kiem.han_tong import cong_dong
from tram.kiem.moi_truong import LoiMoiTruongKiem

THOI_GIAN_CHO = 900
Boc = Callable[[list[str]], list[str]]


@dataclass(frozen=True)
class KetQuaKiemLai:
    dat: bool
    ket_qua: tuple[dict, ...] = ()      # dòng `lenh_kiem[]` (lenh, ket_qua, tom_tat, digest_log)
    cham_cam: tuple[str, ...] = ()
    loi: str | None = None              # "dong-file-cau-hinh" | "thieu-moi-truong-kiem" | "cay-khac-nguon" | None

    @property
    def digest_log(self) -> list[str]:
        return [k["digest_log"] for k in self.ket_qua]


def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem: list[str],
             lenh_cho_phep: list[str], chay_lenh: bool, thu_muc: Path, thu_muc_log: Path,
             boc: Boc, env_goc: Mapping[str, str],
             thoi_gian_cho: float = THOI_GIAN_CHO,
             don_sach: Callable[[], None] | None = None,
             kill: Callable[[int, int], None] = _kill_nhom,
             cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None,
             chu_dau: bool = False, them_cam: tuple[str, ...] = ()) -> KetQuaKiemLai:
    if not chu_dau and cong_dong(tram_home() / "kiem-lai.dong"):      # H6: trước mọi bước, kể cả spike tài liệu
        raise LoiBanChep("dấu hạn tổng kiem-lai.dong còn: harness chưa xác nhận dọn — Đại ca kiểm tay rồi xoá dấu")
    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit,
                         them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                         cho_phep=du_an.giao.duong_dan_cam_cho_phep)
    if cham:
        return KetQuaKiemLai(False, (), tuple(cham), "dong-file-cau-hinh")
    if not chay_lenh:
        return KetQuaKiemLai(True)                                       # spike tài liệu
    mt = du_an.moi_truong_kiem
    if mt is None:
        return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")
    with giu_khoa():
        if cong is not None:
            cong.vao(giao_id)                # lượt trước chưa xác nhận sạch → không chép, không nhận môi trường kiểm
        try:
            wt = thu_muc / ten_ban_chep(giao_id)
            kq = _tren_ban_chep(kho_git, commit, mt, wt, giao_id=giao_id, lenh_kiem=lenh_kiem,
                                lenh_cho_phep=lenh_cho_phep, thu_muc_log=thu_muc_log, env_goc=env_goc, kill=kill,
                                boc=boc_luot(wt) if boc_luot is not None else boc, don_sach=don_sach,
                                thoi_gian_cho=thoi_gian_cho)
        except BaseException as e:
            if cong is not None:
                cong.dong(f"lượt {giao_id}: {type(e).__name__}")         # dọn không rõ → chặn lượt sau (D45)
            raise
        if cong is not None:
            cong.ra(giao_id)
    return kq


def _tren_ban_chep(kho_git: Path, commit: str, mt, wt: Path, *, giao_id: str, lenh_kiem: list[str],
                   lenh_cho_phep: list[str], thu_muc_log: Path, boc: Boc, env_goc: Mapping[str, str],
                   thoi_gian_cho: float, don_sach: Callable[[], None] | None,
                   kill: Callable[[int, int], None]) -> KetQuaKiemLai:
    if don_sach is not None:
        don_sach()                           # tiến trình tram-kiem của lần trước không được sống sang lần này
    try:
        try:
            chep_ban(kho_git, commit, wt, boc=boc, kill=kill)
        except CayKhacNguon:
            return KetQuaKiemLai(False, loi="cay-khac-nguon")           # R7: tất định — escalation, không thử lại mãi
        try:
            nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc, kill=kill)
        except LoiMoiTruongKiem:
            return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
        env, ket_qua = moi_truong_kiem(env_goc, {"HOME": f"{wt}.nha", "TMPDIR": f"{wt}.nha/tmp"}), []
        for i, lenh in enumerate(lenh_kiem, 1):
            kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
                               log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
            if not kq.da_thu_hoi:
                raise LoiBanChep(f"lệnh kiểm {i}: chưa thu hồi được cây tiến trình — không công nhận kết quả")
            ket_qua.append(kq.sang_lenh_kiem())
    finally:
        don_ban(wt, boc=boc, don_sach=don_sach, kill=kill)   # lỗi → ném: không công nhận kết quả khi chưa dọn
    return KetQuaKiemLai(bool(ket_qua) and all(k["ket_qua"] == "pass" for k in ket_qua), tuple(ket_qua))
