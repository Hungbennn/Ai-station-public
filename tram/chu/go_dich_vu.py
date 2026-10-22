"""`tram chu go-dich-vu` (bs-2bd.1.17): gỡ dịch vụ launchd của TRẠM CHỦ đã chọn.

Chứng cứ sở hữu DUY NHẤT: biên nhận `~/.tram/dich-vu/<nhãn>.json` do `tram chu cai-dat` ghi (`chung_cu_go`). Plist
phải là file thường, đúng đường và sha256 trong biên nhận — thiếu/khác (dù có chữ `tram`) → từ chối CẢ kế hoạch.
Cài trước lát này (chưa có biên nhận): chạy lại `tram chu cai-dat` rồi mới gỡ. Từng dịch vụ, dừng ở lỗi đầu tiên:
KIỂM LẠI biên nhận + plist (đúng nội dung và định danh lúc hỏi) → `launchctl print`: vắng (`VANG`) thì không bootout;
đang nạp thì `path` phải đúng plist của biên nhận (job cùng nhãn từ nguồn khác → dừng, không bootout); mã khác → dừng
→ bootout → ĐỌC LẠI `print` (chỉ `VANG` là đã vắng) → cất độc quyền vào `~/.tram/go-dich-vu/` và xoá GIỮ ĐỊNH DANH
(không xoá file thay vào giữa chừng). Mỗi lệnh có hạn `HAN_LENH_GIAY`. Không đụng ~/.tram khác, Keychain, máy thợ."""
import os
import subprocess
from pathlib import Path

from tram.chu.chung_cu_go import LoiGo, MucGo, doc_chung_cu, kiem_lai, nguon_nap, rut
from tram.chu.dich_vu_tram import DICH_VU_TRAM, HAN_LENH_GIAY
from tram.chu.launchd import NHAN_NHO
from tram.duong_dan import bay_gio, tram_home
from tram.su_kien import ban_sao

DICH_VU_GO = {**DICH_VU_TRAM, "nho": NHAN_NHO}
HAU_QUA = {"api": "dashboard và mọi API ghi dừng", "quet": "ngừng chấm cột và ghi nhãn",
           "bao-tin": "ngừng tin Telegram", "sao-luu": "ngừng sao lưu su-kien.db hằng ngày",
           "nho": "memory 7710 dừng (LanceDB, nhật ký giữ nguyên)"}
VANG = 113                    # launchctl print: "Could not find service" — đo 18/10 máy dev; đo lại máy B ở cổng


def lap_ke_hoach_go(dich_vu: list[str] | None, *, home: Path) -> list[MucGo]:
    ds = list(dict.fromkeys(dich_vu or ()))
    if not ds or any(t not in DICH_VU_GO for t in ds):
        raise ValueError("Chọn ít nhất một dịch vụ trong: " + ", ".join(DICH_VU_GO))
    return [doc_chung_cu(t, DICH_VU_GO[t], home / "Library/LaunchAgents" / f"{DICH_VU_GO[t]}.plist",
                         tram_home() / "dich-vu" / f"{DICH_VU_GO[t]}.json") for t in ds]


def thuc_hien_go(ds: list[MucGo], *, uid: int, luc: str, chay=None) -> list[str]:
    """Trả tên dịch vụ đã gỡ xong. `LoiGo` / `subprocess.TimeoutExpired`: dừng, dịch vụ sau không đụng."""
    chay, xong, dau = chay or subprocess.run, [], luc.replace("-", "").replace(":", "")
    for m in ds:
        mien, da = f"gui/{uid}/{m.nhan}", f"Đã gỡ: {', '.join(xong) or 'chưa có'}."
        kiem_lai(m)                                            # trước MỌI thao tác: chứng cứ còn đúng như lúc hỏi
        kq = chay(["launchctl", "print", mien], check=False, capture_output=True, text=True, timeout=HAN_LENH_GIAY)
        ma = kq.returncode
        if ma == 0:
            if nguon_nap(kq.stdout) != str(m.plist.duong):
                raise LoiGo(f"{m.nhan}: job cùng nhãn đang nạp từ nguồn khác plist của biên nhận — không bootout. {da}")
            chay(["launchctl", "bootout", mien], check=False, capture_output=True, timeout=HAN_LENH_GIAY)
            ma = chay(["launchctl", "print", mien], check=False, capture_output=True, timeout=HAN_LENH_GIAY).returncode
        if ma != VANG:
            ly_do = "vẫn còn nạp sau bootout" if ma == 0 else f"không xác định được trạng thái (mã {ma})"
            raise LoiGo(f"{m.nhan}: {ly_do} — dừng, plist giữ nguyên. {da}")
        rut(m.plist, lambda noi: ban_sao.ghi_doc_quyen(tram_home() / "go-dich-vu", f"{m.nhan}-{dau}", noi,
                                                       duoi=".plist"))
        rut(m.bien_nhan)
        xong.append(m.ten)
    return xong


def _lenh(args) -> int:
    if not args.dich_vu:
        print("Chọn một/nhiều --dich-vu " + "|".join(DICH_VU_GO) + ".")
        return 2
    try:
        ds = lap_ke_hoach_go(args.dich_vu, home=Path(os.environ["HOME"]))
    except LoiGo as e:
        print(e)
        return 2
    print("Sẽ gỡ từng dịch vụ (dừng ở lỗi đầu tiên): launchctl bootout → kiểm launchctl print → cất plist vào "
          "~/.tram/go-dich-vu/ (không xoá). Dữ liệu ~/.tram khác và Keychain không đổi. Cài lại: tram chu cai-dat.")
    print("\n".join(f"  - {m.nhan}: {HAU_QUA[m.ten]}" for m in ds))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        print(f"Đã gỡ: {', '.join(thuc_hien_go(ds, uid=os.getuid(), luc=bay_gio()))}.")
    except LoiGo as e:
        print(e)
        return 3
    except subprocess.TimeoutExpired:
        print(f"Lệnh launchctl quá {HAN_LENH_GIAY:.0f} giây — dừng; dịch vụ sau không đụng. Chạy lại để tiếp.")
        return 3
    return 0


def them_lenh_go_dich_vu(chu) -> None:
    g = chu.add_parser("go-dich-vu", help="Gỡ dịch vụ launchd của trạm chủ đã chọn (liệt kê, chờ dong-y)")
    g.add_argument("--dich-vu", action="append", choices=list(DICH_VU_GO), help="Dịch vụ cần gỡ (lặp lại được)")
    g.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ dùng khi Đại ca đã đọc kế hoạch)")
    g.set_defaults(ham=_lenh)
