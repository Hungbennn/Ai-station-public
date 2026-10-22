"""Lệnh dịch vụ: `tram api`, `tram bao-tin`, `tram chu sao-luu` (lát 2a); `tram nho …` (lát 1b-1);
`tram bao` (3a-1, Task 6); `tram tho …`, `tram chu go-may` (3a-1, Task 24)."""
HOST = "127.0.0.1"          # spec 2 §4 mục 1: chỉ nghe localhost; ra tailnet chỉ qua `tailscale serve`
CONG_MAC_DINH = 7700


def _api(args) -> int:
    import threading

    from tram.api.app import tao_app
    from tram.api.kenh_ghi import chay_api
    from tram.api.phu_thuoc import phu_thuoc_that
    from tram.phieu.canh import bat_dau_canh
    dung = threading.Event()
    canh = bat_dau_canh(dung)                # bộ canh hợp đồng chạy trong tiến trình tram-api (spec 3 §6.3)
    from tram.giao_viec.noi_that import noi_giao_viec
    pt, luong_giao = noi_giao_viec(phu_thuoc_that(), dung)      # 4a-2: chỉ phát phiếu/chạy tick khi giao_viec.bat
    try:                                     # kênh ghi theo cach_ly.kenh_ghi (3a-2): TCP, hoặc TCP + Unix socket
        chay_api(tao_app(pt, cong=args.cong), host=HOST, cong=args.cong)
    finally:
        dung.set()
        canh.join(timeout=10)
        for t in luong_giao:
            t.join(timeout=10)
    return 0


def _bao_tin(args) -> int:
    from tram.bao_tin.vong import chay_mai, mot_vong, tao_ngu_canh_that
    nc = tao_ngu_canh_that()
    if nc is None:
        print("Chưa cấu hình telegram.chat_id trong ~/.tram/cau-hinh.yaml hoặc chưa có token Telegram "
              "trong Keychain — tram-bao-tin không chạy.")
        return 0
    if args.mot_lan:
        print(f"Đã gửi {mot_vong(nc)} tin.")
        return 0
    chay_mai(nc)
    return 0


def _sao_luu(args) -> int:
    from tram.duong_dan import tram_home
    from tram.su_kien.sao_luu import sao_luu
    print(f"Đã sao lưu: {sao_luu(tram_home() / 'su-kien.db', tram_home() / 'sao-luu', giu=args.giu)}")
    return 0


def them_lenh(sub, chu) -> None:
    a = sub.add_parser("api", help="Chạy tram-api (chỉ nghe 127.0.0.1)")
    a.add_argument("--cong", type=int, default=CONG_MAC_DINH)
    a.set_defaults(ham=_api)
    b = sub.add_parser("bao-tin", help="Chạy dịch vụ báo tin Telegram")
    b.add_argument("--mot-lan", action="store_true", help="Chạy một vòng rồi thoát")
    b.set_defaults(ham=_bao_tin)
    s = chu.add_parser("sao-luu", help="Sao lưu ~/.tram/su-kien.db vào ~/.tram/sao-luu/")
    s.add_argument("--giu", type=int, default=14, help="Số bản giữ lại")
    s.set_defaults(ham=_sao_luu)
    from tram.nho.lenh import them_lenh_nho
    them_lenh_nho(sub)
    from tram.nho.ma_dai_ca import them_lenh_ma_dai_ca
    them_lenh_ma_dai_ca(chu)
    from tram.chu.ma_dieu_phoi import them_lenh_ma_dieu_phoi     # plan 2e (D24): mã riêng của hook máy A
    them_lenh_ma_dieu_phoi(chu)
    from tram.chu.siet_quyen import them_lenh_siet               # bs-2bd.1.4
    them_lenh_siet(chu)
    from tram.tho.bao_lenh import them_lenh_bao
    them_lenh_bao(sub)
    from tram.tho.lenh import them_lenh_tho
    them_lenh_tho(sub, chu)
    from tram.giao_viec.lenh import them_lenh_giao
    them_lenh_giao(sub)
