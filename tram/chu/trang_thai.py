"""`tram chu trang-thai`: estop, lần quét cuối và lỗi gần nhất từng dự án (dời từ `cai_dat.py`, bs-2bd.1.23)."""
from tram.chu import estop


def trang_thai(kho) -> str:
    dong = [f"estop: {'BẬT' if estop.dang_bat() else 'tắt'}"]
    for du_an in (d for d in kho.cac_du_an() if not d.startswith("_")):  # "_tram": sự kiện nội bộ
        cuoi = kho.gan_day(du_an, "quet.xong", 1)
        loi = kho.gan_day(du_an, "cham_cot.loi", 1)
        dong.append(f"{du_an}: quét cuối {cuoi[0].luc if cuoi else 'chưa'} {cuoi[0].du_lieu if cuoi else ''}"
                    f" · lỗi gần nhất: {loi[0].luc + ' ' + loi[0].du_lieu.get('loi', '')[:80] if loi else 'không'}")
    return "\n".join(dong)
