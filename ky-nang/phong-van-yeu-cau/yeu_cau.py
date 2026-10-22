#!/usr/bin/env python3
"""CLI skill `phong-van-yeu-cau` trên máy A (D46/D47; spec 4 §7.1; plan 4d 4D-3b). Không gọi `bd`, không ghi repo.

  moi --du-an <ten> | --tu <nháp cũ>  nháp mới NGOÀI repo, mã mới — chỉ khi Đại ca chọn rõ "yêu cầu mới"
  xem <nháp>                          B kiểm phiếu, cho biết kho đích, trạng thái mã; in nội dung và mã xem
  gui <nháp> --dau-xem <mã xem>       gửi tạo — chỉ sau khi Đại ca gõ đúng `tạo` cho bản xem vừa in
Mã thoát: 0 xong · 2 chắc chắn chưa tạo / cần Đại ca · 3 chưa rõ, đang xử lý (gửi lại ĐÚNG lệnh sau, không đổi mã)."""
import argparse
import json
import os
import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True                                   # không để __pycache__ trong ~/.claude/skills
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))     # python3 -I không tự thêm thư mục script
import khach  # noqa: E402
import nhap  # noqa: E402

XEM, TAO = "/api/feature/yeu-cau/xem", "/api/feature/yeu-cau"
LOI_HTTP = {403: "403 — B không nhận danh tính Đại ca hoặc kênh ghi (Tailscale, tailscale serve, Origin). Dừng, báo "
                 "Đại ca; không thử đường khác", 404: "404 — B không có dự án này",
            421: "421 — địa chỉ trạm không phải tên máy B",
            422: "422 — B từ chối: dự án chưa bật ghi hoặc nháp sai dạng"}
CHUA_RO = "CHƯA RÕ — B không tự tạo lại. Gửi lại ĐÚNG lệnh này sau; không đổi mã, không `moi`"
KQ = {"da_tao": (0, "ĐÃ TẠO"), "da_co": (0, "ĐÃ CÓ, không tạo lại"), "khong_ro": (3, CHUA_RO),
      "dang_xu_ly": (3, "ĐANG XỬ LÝ — lần gửi khác đang tạo. Gửi lại đúng lệnh này sau ít phút"),
      "chua_tao": (3, "CHƯA TẠO GÌ — B tạm không đọc được beads. Gửi lại đúng lệnh này sau"),
      "xung_dot": (2, "XUNG ĐỘT — mã này đã gửi với nội dung khác. B không ghi đè, không tạo thêm"),
      "lech_ban_xem": (2, "NỘI DUNG ĐÃ ĐỔI sau khi xem — chạy `xem` lại, hỏi Đại ca lại"),
      "chua_bat": (2, "B chưa bật chức năng tạo feature cho dự án này"),
      "nhieu_feature": (2, "NHIỀU FEATURE trên B mang mã này — B không chọn, không tạo. Báo Đại ca xử lý tay")}


def sach(x, toi_da=200):
    return "".join(c for c in str(x) if c.isprintable())[:toi_da]


def _in_loi(d):
    loi = d.get("loi")
    for x in (loi if isinstance(loi, list) else [])[:20]:
        print("- " + sach(x, 300))


def _xem(goc, yc, mo=None):
    try:
        ma, d = khach.goi(goc, XEM, yc, mo)
    except khach.MatKetNoi:
        print("LỖI: không với tới trạm")
        return 2
    if ma != 200:
        print("LỖI: " + LOI_HTTP.get(ma, "B trả HTTP " + str(ma)))
        return 2
    print(f"Dự án {sach(d.get('du_an'))} · kho trên B: {sach(d.get('kho'))} · bat_ghi: {d.get('bat_ghi') is True}")
    print(f"Mã yêu cầu {yc['ma_yeu_cau']} · tiêu đề: {sach(yc['tieu_de'])} · ưu tiên {yc['uu_tien']}")
    print(json.dumps(yc["phieu"], ensure_ascii=False, indent=2))
    bn = d.get("bien_nhan")
    if isinstance(bn, dict):
        print(f"Mã này đã gửi trước: {sach(bn.get('trang_thai'), 20)} {sach(bn.get('bead_id') or '', 64)}"
              + (" — NỘI DUNG KHÁC lần gửi trước: gửi sẽ XUNG ĐỘT" if bn.get("cung_noi_dung") is False else ""))
    if d.get("hop_le") is not True:
        print("KHÔNG HỢP LỆ")
        _in_loi(d)
        return 2
    if d.get("bat_ghi") is not True or not d.get("kho"):
        print("B CHƯA BẬT GHI hoặc chưa cấu hình kho cho dự án này — gửi sẽ bị từ chối. Báo Đại ca")
        return 2
    print("HỢP LỆ · mã xem " + sach(d.get("dau_xem"), 16) + ("" if isinstance(bn, dict) else " · không có biên nhận"))
    return 0


def _gui(goc, yc, dau_xem, mo=None):
    try:
        ma, d = khach.goi(goc, TAO, dict(yc, dau_xem=dau_xem), mo, timeout=khach.TIMEOUT_GUI)
    except Exception:                                   # mọi lỗi giữa đường: B có thể đã nhận — không phải "chưa tạo"
        print("CHƯA RÕ — mất kết nối khi gửi, B có thể đã nhận. Gửi lại ĐÚNG lệnh này sau; không đổi mã, không `moi`")
        return 3
    tt = "nhieu_feature" if d.get("ly_do") == "nhieu_feature" else d.get("trang_thai")
    tt = tt if isinstance(tt, str) else None
    if tt not in KQ and ma in LOI_HTTP:                 # bị chặn trước khi B giữ chỗ: chắc chắn chưa tạo
        print("LỖI: " + LOI_HTTP[ma])
        _in_loi(d)
        return 2
    if tt not in KQ:                                    # 5xx, phản hồi lạ: không được coi là chưa tạo
        print(f"CHƯA RÕ — B trả HTTP {ma}. Gửi lại ĐÚNG lệnh này sau; không đổi mã, không `moi`")
        return 3
    thoat, chu = KQ[tt]
    bead = sach(d.get("bead_id") or "", 64) if tt in ("da_tao", "da_co") else ""
    print(chu + (f" · feature {bead} · nhãn can-spec" if bead else "") + f" · mã {yc['ma_yeu_cau']}")
    return thoat


def main(argv=None, mo=None):
    ap = argparse.ArgumentParser(prog="yeu_cau.py")
    con = ap.add_subparsers(dest="lenh", required=True)
    m = con.add_parser("moi")
    for co in ("--du-an", "--tu", "--thu-muc"):
        m.add_argument(co)
    for ten in ("xem", "gui"):
        c = con.add_parser(ten)
        c.add_argument("nhap")
        c.add_argument("--tram")
        c.add_argument("--dau-xem", required=ten == "gui")
    a = ap.parse_args(argv)
    try:
        if a.lenh == "moi":
            print("NHÁP MỚI " + str(nhap.moi(a.thu_muc or nhap.thu_muc_mac_dinh(), a.du_an, a.tu)))
            return 0
        yc = nhap.doc(a.nhap)
        goc = khach.goc_tram(a.tram or os.environ.get("TRAM_DIEU_PHOI_URL", ""))
        if goc is None:
            raise nhap.Loi("Địa chỉ trạm phải dạng https://<máy B> (TRAM_DIEU_PHOI_URL hoặc --tram)")
    except nhap.Loi as e:
        print("LỖI: " + str(e))
        return 2
    return _xem(goc, yc, mo) if a.lenh == "xem" else _gui(goc, yc, a.dau_xem, mo)


if __name__ == "__main__":
    sys.exit(main())
