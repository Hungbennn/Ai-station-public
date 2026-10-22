"""Harness nghiệm thu S6 cho kiểm lại dưới principal THẬT (lát 3c — thay r47 T12; Q03, C01). Phần TRONG tiến trình con
của `tram giao nghiem-thu-kiem` (CLI cha giữ hạn tổng — `lenh_nghiem_thu.py`). Gọi ĐÚNG đường production `kiem_lai`
qua `cong` (cổng lượt) và `boc_luot` (hồ sơ Seatbelt của lượt), `don_sach` = thu hồi theo UID, trên kho git NHÁP + môi
trường kiểm GIẢ trong thư mục tạm của trạm (không dự án thật, không cần `giao_viec.bat`). Harness là chủ dấu hạn tổng
`kiem-lai.dong` (`chu_dau=True`). Mỗi khẳng định là MỘT lệnh kiểm (`KHANG_DINH`). `--tai-sinh`: commit thứ hai thử cài
lịch như mã agent; chỉ khi log có dấu `kich-ban-bat-dau` mới xét TỪNG nguồn qua `chung_cu_probe` (V2-4: thiếu dấu =
đỏ, cài được = đỏ, thất bại = vàng chờ biên bản OS G4 — mục tổng "đủ bằng chứng S6" luôn đỏ, harness không tự đóng
C01), lọt thì quan sát đóng cổng, sau `cho` (≥ 240 s) không dấu nào chạy, lần kiểm sau vẫn đạt. Kịch bản lịch
thật hay khẳng định exec `crontab` chỉ chạy khi `xac_minh_uid` chứng minh UID thực không phải người vận hành/root —
kiểm TRƯỚC mọi spawn. Cuối cùng, dưới khoá, thu hồi theo UID rồi xem gốc rỗng; lỗi giữa chừng vẫn dọn."""
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
from tram.giao_viec.chung_cu_probe import doc_probe, muc_lich
from tram.giao_viec.mau_g4 import receipt_truoc_luot
from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, NGUON, commit_nhap, git_nhap, kich_ban_tai_sinh
from tram.giao_viec.kiem_lai import kiem_lai
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.kiem_may import MucKiem

LOI = (OSError, subprocess.SubprocessError, ValueError, LoiDanhTinh, LoiThuHoi)

def _muc(ten: str, dat: bool | None, chi_tiet: str) -> MucKiem:
    return MucKiem(ten, {True: "xanh", False: "do", None: "vang"}[dat], chi_tiet[:200])

def _kiem_an_toan(kiem, *a) -> tuple[object | None, str | None]:
    try:
        kq = kiem(*a)
        return kq, kq.loi
    except LoiBanChep as e:                                # cổng đóng, dọn lỗi, chưa thu hồi: không công nhận
        return None, f"{type(e).__name__}: {e}"


def nghiem_thu(pk, goc: Path, *, cong, boc_luot, thu_hoi, khang_dinh: dict = KHANG_DINH, xac_minh=xac_minh_uid,
               cho: float = 300, thoi_gian_cho: float = 120, tai_sinh: bool = False,
               dau_goc: Path = Path("/Users/Shared"), ngu=time.sleep, kich_ban=kich_ban_tai_sinh) -> list[MucKiem]:
    if (tai_sinh and kich_ban is kich_ban_tai_sinh) or "khong-chay-cong-cu-lich" in khang_dinh:
        try:
            uid = xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
        except (LoiDanhTinh, LoiThuHoi) as e:
            raise ValueError(f"lệnh lịch THẬT: chỉ dưới tram-kiem đã chứng minh UID thực ({e})") from None
    if tai_sinh and not cho >= 240:
        raise ValueError("--cho phải ≥ 240 giây (lịch của kịch bản hẹn 121–180 s sau khi cài)")
    tam = dau = None
    ra = []
    try:
        tam = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-"))
        dau = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-dau-", dir=dau_goc))
        os.chmod(dau, 0o777)                       # job lọt (chạy ngoài hồ sơ) ghi được dấu; `tep_ngoai` thấy tệp
        kho = tam / "kho"
        kho.mkdir()
        git_nhap(kho, "init", "-q", "-b", "main")
        goc_sha = commit_nhap(kho, {"README": "nháp\n"}, None)
        git_nhap(kho, "update-ref", "refs/remotes/origin/main", goc_sha)
        kd = {f"kiem/{k}.sh": v.format(ten=pk.ten, kho_tram=shlex.quote(str(tram_home()))) + "\n"
              for k, v in khang_dinh.items()}
        sha = commit_nhap(kho, kd, goc_sha)
        (tam / "env.testing").write_text("NGHIEM_THU=1\n")
        da = DuAn("nghiem-thu", kho, None, {}, moi_truong_kiem=MoiTruongKiem(tam / "env.testing", ".env.testing"))

        def kiem(commit: str, lenh: list[str], nhan: str):
            return kiem_lai(kho, da, giao_id=f"nghiem-thu-{nhan}", commit=commit, lenh_kiem=lenh, chay_lenh=True,
                            lenh_cho_phep=["sh *"], thu_muc=goc, boc=pk.boc_lenh, env_goc=os.environ, cong=cong,
                            thu_muc_log=tram_home() / "log" / "nghiem-thu", thoi_gian_cho=thoi_gian_cho,
                            don_sach=thu_hoi, kill=pk.kill_nhom, boc_luot=boc_luot, chu_dau=True)
        kq, loi = _kiem_an_toan(kiem, sha, [f"sh {k}" for k in kd], "1")
        ra += [_muc(f"chuỗi kiểm lại: {k['lenh'][3:]}", k["ket_qua"] == "pass", k["tom_tat"][-120:])
               for k in (kq.ket_qua if kq else ())] or [_muc("chuỗi kiểm lại", False, str(loi))]
        if tai_sinh:
            if kich_ban is kich_ban_tai_sinh:
                receipt_truoc_luot(dau, uid)
            ra += _tai_sinh(kiem, kho, goc_sha, sha, kd, dau, kich_ban, cho, ngu)
    except LOI as e:
        ra.append(_muc("nghiệm thu dừng vì lỗi", False, f"{type(e).__name__}: {e}"))
    finally:
        try:
            with giu_khoa():                     # không đụng lần kiểm lại thật đang chạy
                thu_hoi()
                con = os.listdir(goc)
            ra.append(_muc("dọn: gốc bản chép rỗng sau thu hồi theo UID", not con, str(con)))
        except LOI as e:
            ra.append(_muc("dọn: thu hồi theo UID lần cuối", False, f"{type(e).__name__}: {e}"))
        for x in (tam, dau):
            if x is not None:
                shutil.rmtree(x, ignore_errors=True)
    return ra

def _tai_sinh(kiem, kho: Path, goc_sha: str, sha: str, kd: dict, dau: Path, kich_ban, cho: float, ngu) -> list:
    nk = tram_home() / "log" / "nghiem-thu" / "nghiem-thu-2-kiem-lai-1.log"
    nk.unlink(missing_ok=True)                      # không đọc nhầm log của lần nghiệm thu trước
    cai_lich = commit_nhap(kho, {"kiem/cai-lich.sh": kich_ban(dau)}, goc_sha)
    _, loi = _kiem_an_toan(kiem, cai_lich, ["sh kiem/cai-lich.sh"], "2")
    log = nk.read_text(errors="replace") if nk.exists() else ""
    if "kich-ban-bat-dau" not in log:                # cổng đóng/lỗi trước khi chạy: không có gì được chứng minh
        return [_muc("tái sinh: lượt cài lịch đã chạy", False, str(loi or "log không có dấu bắt đầu"))]
    lich = {n: muc_lich(log, n) for n in NGUON if n != "setsid"}          # V2-4: chứng cứ TỪNG nguồn, không suy từ vắng
    lot = [n for n in lich if doc_probe(log, n) == 0]  # fork + setsid được phép; bằng chứng là `ra()` thu hồi sạch
    ra = [_muc(f"tái sinh: hồ sơ chặn cài {n}", *lich[n]) for n in lich]
    ss = doc_probe(log, "setsid")
    ra.append(_muc("tái sinh: tiến trình setsid bị thu hồi ở ra()", {None: False, 0: loi is None}.get(ss),
                   str(loi or {None: "probe chưa hoàn tất", 0: "ra() sạch"}.get(ss, f"không fork được (mã {ss})"))))
    ra.append(_muc("tái sinh: quan sát đóng cổng khi lịch lọt", "CongDong" in str(loi) if lot else None,
                   str(loi or "không có lịch lọt để quan sát")))
    vang = sum(v[0] is None for v in lich.values())
    ra.append(_muc("tái sinh: đủ bằng chứng S6", False, f"{vang}/{len(lich)} nguồn chỉ 'thất bại' — chưa nguồn nào có "
                   "biên bản OS G4 (lý do + đối chứng dương); harness không tự đóng C01"))
    ngu(cho)
    chay = sorted(p.name for p in dau.iterdir())
    ra.append(_muc("tái sinh: không gì chạy sau thu hồi", not chay, f"đã chạy: {chay} / chờ {cho:g} s"))
    kq, loi = _kiem_an_toan(kiem, sha, [f"sh {k}" for k in kd], "3")
    return ra + [_muc("tái sinh: lần kiểm sau đạt", bool(kq and kq.dat), str(loi or ""))]
