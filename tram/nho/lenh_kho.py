"""Lệnh `tram nho` đụng thẳng thư mục kho (chỉ khi dịch vụ dừng): khôi phục, đặt mốc; và đo M6 trên kho tạm."""
from pathlib import Path

from tram.nho.khoa import khoa_dich_vu
from tram.nho.nhat_ky import NhatKy
from tram.su_kien.kho import KhoSuKien


def dat_moc_hien_tai(thu_muc: Path, kho_sk: KhoSuKien) -> int | None:
    """`moc_nho` = id sự kiện mới nhất: bỏ qua lịch sử, chỉ nạp sự kiện từ bây giờ (mốc không lùi).
    None khi dịch vụ đang chạy (giữ flock) — không đụng nhật ký của tiến trình khác."""
    with khoa_dich_vu(thu_muc) as duoc:
        if not duoc:
            return None
        nk = NhatKy(thu_muc / "nhat-ky.db")
        try:
            nk.dat_moc(kho_sk.id_moi_nhat())
            return nk.moc()
        finally:
            nk.close()


def _dat_moc(args) -> int:
    from tram.nho.khoa import thu_muc_nho
    from tram.su_kien.kho import mo_kho
    moc = dat_moc_hien_tai(thu_muc_nho(), mo_kho())
    if moc is None:
        print("memory service đang chạy — dừng trước: launchctl bootout gui/$(id -u)/vn.tram.nho")
        return 1
    print(f"Đã đặt moc_nho = {moc}: sự kiện cũ hơn sẽ không được nạp thành ký ức.")
    return 0


def _khoi_phuc(args) -> int:
    from tram.nho.khoa import thu_muc_nho
    from tram.nho.sao_luu import khoi_phuc_nho
    print(f"Sẽ thay ~/.tram/nho/lancedb và nhat-ky.db bằng bản {args.ban} (bản hiện tại được giữ lại).")
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    print(f"Đã khôi phục. Bản trước khi khôi phục: {khoi_phuc_nho(Path(args.ban), thu_muc_nho())}")
    return 0


def _do_tre(args) -> int:
    import tempfile
    from tram.nho.do_tre import do_tre, sinh_kho
    from tram.nho.embed import OllamaEmbedder
    e = OllamaEmbedder()
    e.kiem()
    with tempfile.TemporaryDirectory(prefix="tram-do-m6-") as tam:
        kho = sinh_kho(Path(tam), e, args.so_ban)
        kq = do_tre(kho, e, [f"truy vấn đo độ trễ số {i}" for i in range(20)], so_lan=args.so_lan)
    print(f"M6 ({args.so_ban} ký ức, {args.so_lan} lần): p50={kq['p50']:.0f} ms, p95={kq['p95']:.0f} ms "
          f"(ngưỡng 800 ms), max={kq['max']:.0f} ms")
    return 0


def them_lenh_kho(nho) -> None:
    k = nho.add_parser("khoi-phuc", help="Khôi phục từ một bản sao lưu (dịch vụ phải dừng)")
    k.add_argument("ban")
    k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    k.set_defaults(ham=_khoi_phuc)
    m = nho.add_parser("dat-moc", help="Bỏ qua lịch sử: chỉ nạp sự kiện từ bây giờ (dịch vụ phải dừng)")
    m.add_argument("--hien-tai", action="store_true", required=True, help="moc_nho = sự kiện mới nhất")
    m.set_defaults(ham=_dat_moc)
    d = nho.add_parser("do-tre", help="Đo M6 với kho sinh giả + embed truy vấn qua Ollama")
    d.add_argument("--so-ban", type=int, default=10_000)
    d.add_argument("--so-lan", type=int, default=200)
    d.set_defaults(ham=_do_tre)
