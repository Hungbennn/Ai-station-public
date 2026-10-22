"""`tram chu cai-dat` (bs-2bd.1.23): cài TỪNG dịch vụ trạm chủ Đại ca chọn (`--dich-vu`, lặp lại được), hoặc
memory (`--nho`, spec 1b §15). Không còn mặc định cài cả bốn; `quet` (`tram quet --ghi`) chỉ khi chọn rõ. Chờ dong-y.
Không đọc được dự án (cài quét) → thoát 2, không làm gì. Một bước/lệnh quá hạn → dừng ngay, thoát 3."""
import shutil
import subprocess

from tram.chu.dich_vu_tram import DICH_VU_TRAM, LoiCaiDat
from tram.keychain import LoiKeychain


def chay_ke_hoach(kh, dong_y: bool, xong: str) -> int:
    """In kế hoạch, chờ dong-y, thực hiện; bước/lệnh quá hạn hay Keychain lỗi → báo (không chép argv), thoát 3."""
    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
    print(in_ke_hoach(kh))
    if not dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        thuc_hien(kh)
    except subprocess.TimeoutExpired as e:
        print(f"Một bước/lệnh hệ thống chạy quá {e.timeout:.0f} giây — đã dừng, các lệnh sau KHÔNG chạy. Đại ca kiểm "
              "`launchctl print gui/$(id -u)/<nhãn>` rồi chạy lại lệnh này.")
        return 3
    except (LoiCaiDat, LoiKeychain) as e:
        print(f"{e} — đã dừng, các lệnh sau KHÔNG chạy.")
        return 3
    print(xong)
    return 0


def _cai_dat(args) -> int:
    from tram.chu.cai_dat import lap_ke_hoach
    from tram.chu.cai_dat_nho import lap_ke_hoach_nho
    from tram.duong_dan import goc_repo
    if bool(args.nho) == bool(args.dich_vu):
        print("Chọn đúng một: --nho, hoặc một/nhiều --dich-vu " + "|".join(DICH_VU_TRAM) + " (không có mặc định).")
        return 2
    uv, repo = shutil.which("uv") or "uv", goc_repo()
    try:
        kh = lap_ke_hoach_nho(uv=uv, repo=repo) if args.nho else lap_ke_hoach(uv=uv, repo=repo, dich_vu=args.dich_vu)
    except LoiCaiDat as e:
        print(e)
        return 2
    return chay_ke_hoach(kh, args.dong_y, "Đã cài memory service." if args.nho
                         else f"Đã cài: {', '.join(dict.fromkeys(args.dich_vu))}.")


def them_lenh_cai_dat(chu) -> None:
    c = chu.add_parser("cai-dat", help="Cài dịch vụ launchd đã chọn (liệt kê thay đổi, chờ đồng ý)")
    c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ dùng khi Đại ca đã đọc kế hoạch)")
    c.add_argument("--nho", action="store_true", help="Cài memory service 1b (Ollama + bge-m3 + vn.tram.nho — #5)")
    c.add_argument("--dich-vu", action="append", choices=list(DICH_VU_TRAM),
                   help="Dịch vụ trạm chủ cần cài (lặp lại được); 'quet' = tram quet --ghi")
    c.set_defaults(ham=_cai_dat)
    from tram.chu.go_dich_vu import them_lenh_go_dich_vu          # bs-2bd.1.17: gỡ đối xứng với cài
    them_lenh_go_dich_vu(chu)
    from tram.chu.khoi_phuc_su_kien import them_lenh_khoi_phuc      # bs-2bd.1.17: khôi phục kho sự kiện
    them_lenh_khoi_phuc(chu)
