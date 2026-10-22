"""Tạo tài nguyên hệ thống CÓ SỔ (lát 3c R2; R5 review đợt 5) cho `tram chu cai-dat-tho`. Mỗi tài nguyên (user, nhà
của user, file root, thư mục) là MỘT bước riêng có bản ghi riêng — biên nhận sở hữu user không chứng minh nhà đã tạo:
1. lúc lập kế hoạch — đã có mà sổ không ghi trạm tạo → TỪ CHỐI cài (không cài đè, không nhận làm của mình). Nhà
   (`nhan`): chỉ nhận/giữ khi user cùng tên ĐANG là của trạm (`user_cua_tram`), nhà là thư mục thật của đúng UID ấy, và
   mọi biên nhận cũ của nhà này ghi cùng GeneratedUID — nhà giữ lại từ user đã gỡ (kể cả UID được dùng lại) là nhà lạ;
2. lúc chạy — quan sát lại; đã có: phải khớp định danh một bản ghi `da_tao` (user giữ nguyên; file đổi nội dung thì
   thay), không khớp → dừng; chưa có: ghi `du_dinh` (fsync) → chạy lệnh → quan sát → `da_tao` kèm định danh, hoặc
   `khong_tao` rồi dừng. Chạy lại chỉ làm bước còn thiếu; UID/GUID user giữ nguyên.
User mang mã `id` của bản ghi trong RealName: `addUser` "thành công" trên user có sẵn không biến nó thành của trạm."""
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field

from tram.chu.dinh_danh import cung, khop, quan_sat_that
from tram.chu.so_cai_tho import SoCai, moi_id


class LoiCaiDat(RuntimeError):
    """Dừng cài giữa chừng — sổ đã ghi đúng phần đã tạo; `tram chu go-cai-dat-tho` gỡ được phần đó."""


@dataclass(frozen=True)
class TaiNguyen:
    kieu: str                                            # user | nha | tep | thu_muc
    ten: str                                             # tên user | đường dẫn tuyệt đối
    lenh: Callable[[str], list[list[str]]]               # id bản ghi → lệnh tạo
    mong: Callable[[str], dict] = field(default=lambda i: {})
    nhan: Callable[[dict], bool] | None = None           # nhà: có sẵn mà nhận được là của trạm không

    def mo_ta(self) -> str:
        return " && ".join(" ".join(c) for c in self.lenh("<id>"))


def cua_tram(so: SoCai, kieu: str, ten: str, hien: dict) -> bool:
    return any(cung(kieu, m.dinh_danh, hien) for m in so.da_tao(kieu, ten))


def user_cua_tram(so: SoCai, u: str, quan_sat: Callable) -> dict | None:
    """User `u` đang có VÀ là của trạm: cùng UID + GUID một `da_tao`, hoặc RealName mang mã id của một `du_dinh` còn dở
    (crash sau `addUser`, trước `da_tao` — đối soát chưa chạy)."""
    hien = quan_sat("user", u)
    ok = hien is not None and any(m.su == "da_tao" and cung("user", m.dinh_danh, hien)
                                  or m.su == "du_dinh" and khop("user", m.mong, hien)
                                  for m in so.muc().values() if (m.kieu, m.ten) == ("user", u))
    return hien if ok else None


def nha_tram(u: str, so: SoCai, quan_sat: Callable) -> TaiNguyen:
    """`/Users/<u>` của user trạm `u` — `createhomedir`; mong: UID + GUID của user lúc tạo."""
    p = f"/Users/{u}"

    def nhan(hien: dict) -> bool:
        ch = user_cua_tram(so, u, quan_sat)
        return ch is not None and khop("nha", {"uid": ch["uid"]}, hien) and all(
            m.mong.get("guid") == ch["guid"] for m in so.da_tao("nha", p) if cung("nha", m.dinh_danh, hien))

    def mong(i: str) -> dict:
        ch = user_cua_tram(so, u, quan_sat) or {}
        return {"user": u, "uid": ch.get("uid"), "guid": ch.get("guid")}
    return TaiNguyen("nha", p, lambda i: [["sudo", "createhomedir", "-c", "-u", u]], mong, nhan)


def kiem_truoc(so: SoCai, ds: list[TaiNguyen], *, quan_sat: Callable = quan_sat_that) -> list[str]:
    """Hành động dự kiến cho từng tài nguyên (`tạo` | `giữ/thay` | `nhận`). Thứ đã có mà sổ không ghi → ValueError."""
    ra, la = [], []
    for tn in ds:
        hien, ghi = quan_sat(tn.kieu, tn.ten, nhe=True), so.co_ghi(tn.kieu, tn.ten)
        if hien is None:
            ra.append("tạo")
        elif tn.nhan is not None:
            (ra.append("giữ" if ghi else "nhận") if tn.nhan(hien) else la.append(f"{tn.kieu} {tn.ten}"))
        elif ghi:
            ra.append("giữ/thay")
        else:
            la.append(f"{tn.kieu} {tn.ten}")
    if la:
        raise ValueError("Đã có nhưng không phải của trạm (sổ không ghi, hoặc nhà cũ của user đã gỡ — `go-cai-dat-tho "
                         "--xoa-nha` nếu sổ ghi nhà đó, không thì xoá tay) — không cài đè, Đại ca kiểm tay: "
                         + ", ".join(la))
    return ra


def tao(so: SoCai, tn: TaiNguyen, *, quan_sat: Callable = quan_sat_that, chay: Callable = subprocess.run) -> str:
    hien = quan_sat(tn.kieu, tn.ten)
    if hien is not None:
        if tn.nhan is not None:
            if not tn.nhan(hien):
                raise LoiCaiDat(f"{tn.kieu} {tn.ten} có sẵn nhưng không thuộc user trạm hiện tại — dừng, không ghi đè")
            if cua_tram(so, tn.kieu, tn.ten, hien):
                return "giu"
            i = moi_id()
            so.du_dinh(i, tn.kieu, tn.ten, tn.mong(i))
            so.ket(i, "da_tao", dinh_danh=hien, nhan=True)
            return "nhan"
        if not cua_tram(so, tn.kieu, tn.ten, hien):
            raise LoiCaiDat(f"{tn.kieu} {tn.ten} đã có nhưng không khớp định danh trạm đã ghi — dừng, không đè")
        if tn.kieu == "thu_muc" and not khop("thu_muc", tn.mong(""), hien):
            raise LoiCaiDat(f"thu_muc {tn.ten} của trạm nhưng chủ không còn là UID mong đợi — dừng, không chown")
        if tn.kieu != "tep" or khop("tep", tn.mong(""), hien):
            return "giu"
    i = moi_id()
    mong = tn.mong(i)
    so.du_dinh(i, tn.kieu, tn.ten, mong)
    loi = None
    try:
        for c in tn.lenh(i):
            chay(c, check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        loi = e
    sau = quan_sat(tn.kieu, tn.ten)
    if sau is not None and khop(tn.kieu, mong, sau):
        so.ket(i, "da_tao", dinh_danh=sau)
        if loi is None:
            return "tao"
    else:
        so.ket(i, "khong_tao", ly_do=f"{type(loi).__name__ if loi else 'định danh không khớp'}")
    raise LoiCaiDat(f"Không tạo được {tn.kieu} {tn.ten} đúng định danh — dừng (sổ đã ghi)") from loi
