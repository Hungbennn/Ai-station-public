"""`tram chu kiem-cach-ly` (spec 3 §7.3 mục 7, H9; spec 2 §4 mục 2b) — chạy ở TÀI KHOẢN TRẠM: bộ kiểm chứng âm ĐỦ dưới
`tram-kiem` (principal kiểm lại, một nguồn `doc_principal_kiem` — `cach_ly.tram_kiem`; thăm dò qua ĐÚNG argv lúc kiểm
lại `PrincipalKiem.boc_lenh`, P1 với `kill` của principal, UID thực chứng minh TRƯỚC). Biết `dai_ca_logins` thật nên
thăm dò "API Duyệt với header danh tính giả" mang đúng login của Đại ca: chỉ bị chặn khi kênh ghi thật sự tách
(`cach_ly.kenh_ghi`). Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh.
D54 (18/10): trạm KHÔNG được chạy thay khe (không sudoers trạm → khe). `--principal` của khe chỉ in [CHUYỂN] chỉ sang
`tram tho kiem` — tài khoản quản lý thợ chạy kiểm chứng âm của khe, gồm API Duyệt giả danh và DB nghiệp vụ, dưới
CHÍNH principal khe; mục [CHUYỂN] không phải kết quả kiểm nên không tính vào mã thoát."""
import os
import tempfile
from pathlib import Path

from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.vong_doi import LoiThuHoi

from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.cau_hinh.principal_kiem import doc_principal_kiem
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.duong_dan import tram_home
from tram.tho.kiem_am import HUONG_DAN_SUDO
from tram.tho.kiem_am import chay_tham_do, tham_do_day_du, tham_do_khe
from tram.tho.kiem_cong import KEYCHAIN_CAM

CHUYEN = "kiểm cách ly khe bằng `tram tho kiem` dưới tài khoản quản lý thợ (D54) — lệnh này không chạy thay khe"


def _ds_kiem(doc_pk) -> list[tuple[str, object]]:
    """(nhãn, (tên, boc, kill) | lỗi) của `tram-kiem` — qua đúng argv và kill của kiểm lại."""
    try:
        pk = doc_pk()
        return [(f"{pk.co_che}:{pk.ten}", (pk.ten, pk.boc_lenh, pk.kill_nhom))] if pk else []
    except ValueError as e:
        return [("cach_ly.tram_kiem", e)]


def kiem_cach_ly(principal: list[str], *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem,
                 xac_minh=xac_minh_uid) -> tuple[str, int]:
    ch, cl = nap_cau_hinh_tram(), nap_cau_hinh_cach_ly()
    chuyen, ds = [f"[CHUYỂN] {chuoi}: {CHUYEN}" for chuoi in principal], _ds_kiem(doc_pk)
    if not ds:
        return "\n".join([*chuyen, "Chưa có principal kiểm lại ở tài khoản trạm (cach_ly.tram_kiem) — chờ S6."]), 1
    dong, ma = [f"Kênh ghi dashboard: {cl.kenh_ghi}" + ("  (header GIẢ ĐƯỢC — chưa đạt §4 mục 2b)"
                                                       if cl.kenh_ghi == "header" else ""), *chuyen], 0
    for chuoi, pr in ds:
        if not isinstance(pr, Exception):
            try:
                xac_minh(*pr)
            except (LoiDanhTinh, LoiThuHoi) as e:
                pr = ValueError(f"UID thực chưa chứng minh ({type(e).__name__}) — không chạy thăm dò"
                                + HUONG_DAN_SUDO)
        if isinstance(pr, Exception):
            dong.append(f"[ĐỎ] {chuoi}: {pr}")
            ma = 1
            continue
        _, boc, kill = pr
        rg = tham_do_khe(keychain=list(KEYCHAIN_CAM), doc_cam=[tram_home() / "su-kien.db"], ghi_cam=[tram_home()],
                         ghi_duoc=Path(tempfile.gettempdir()))
        td = tham_do_day_du(rut_gon=rg, api="http://127.0.0.1:7700", dai_ca_login=(ch.dai_ca_logins or ("?",))[0],
                            may_b=ch.ten_may_b or "may-b", db=list(cl.db_nghiep_vu), tram_home_tram=tram_home())
        for kq in chay_td(td, boc=boc, env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}, kill=kill):
            dong.append(f"[{'XANH' if kq.dat else 'ĐỎ'}] {chuoi} — {kq.ten}: {kq.chi_tiet}")
            ma |= 0 if kq.dat else 1
    return "\n".join(dong), ma
