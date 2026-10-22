"""Nguồn tin của tự merge / tự deploy (design D-8, D98, D99) — HỢP ĐỒNG sự kiện → tin cho TM-2, TM-3: hai lát đó
chỉ ghi đúng sự kiện dưới đây, không sửa `tram/bao_tin/`. Tin chỉ mang dự án, mã bead, nhãn loại và MÃ CHI TIẾT từ
bảng cố định (`tin.NHAN_CHI_TIET`) — không lệnh, SHA, URL PR, đầu ra lệnh, lý do tự do (INV-001, spec 2 §4 mục 5)."""
from tram.bao_tin.tin import Tin

TIEN_TO = ("tu_dong.", "tu_merge.", "deploy.")
KET_QUA_DEPLOY = {"dat": "deploy_xong", "da_lui": "deploy_da_lui", "lui_hong": "lui_hong",
                  "khong_ro": "deploy_khong_ro"}
MA_TRUONG = {"tu_merge": "tu-merge", "tu_deploy": "tu-deploy", "dk_ci": "dk-ci", "dk_cot": "dk-cot",
             "dk_hang_rao": "dk-hang-rao", "lenh_deploy": "lenh-deploy", "lenh_kiem_song": "lenh-kiem-song",
             "lenh_lui": "lenh-lui"}


def _tram(sk) -> str:
    return "tram-" if sk.tac_nhan.startswith("tram/") else ""


def _cai_dat(sk) -> list[Tin]:
    """Một tin mỗi trường đổi. Trạm tự tắt tự deploy sau 3 lần hỏng (TM-3, `ly_do: hong-3-lan`) → một tin riêng."""
    cd = sk.du_lieu.get("cai_dat") or {}
    if _tram(sk) and sk.du_lieu.get("ly_do") == "hong-3-lan" and cd.get("tu_deploy") is False:
        return [Tin("tu_deploy_tu_tat", sk.du_an)]
    ra = []
    for t in (t for t in sk.du_lieu.get("doi") or [] if t in MA_TRUONG):
        duoi = "doi" if t.startswith("lenh_") else ("bat" if cd.get(t) else "tat")
        ra.append(Tin("cai_dat_doi", sk.du_an, f"{_tram(sk)}{MA_TRUONG[t]}-{duoi}"))
    return ra


def tin_tu_dong(sk) -> list[Tin]:
    if sk.loai == "tu_dong.cai_dat":
        return _cai_dat(sk)
    if sk.loai in ("tu_dong.tam_dung", "tu_dong.tiep_tuc"):
        ma = sk.loai.removeprefix("tu_dong.").replace("_", "-")
        return [Tin("cai_dat_doi", sk.du_an, f"{ma}-toan-tram" if sk.du_an == "_tram" else _tram(sk) + ma)]
    if sk.loai == "tu_merge.xong":
        return [Tin("tu_merge", sk.du_an, sk.bead_id)]
    if sk.loai == "tu_merge.loi":
        return [Tin("tram_loi", sk.du_an, sk.bead_id)]
    if sk.loai == "deploy.san_sang":
        return [Tin("san_sang_deploy", sk.du_an)]
    loai = KET_QUA_DEPLOY.get(sk.du_lieu.get("ket_qua")) if sk.loai == "deploy.xong" else None
    if loai is None:
        return []
    dem = sk.du_lieu.get("dem_hong")
    hong = loai == "deploy_da_lui" and type(dem) is int and 0 < dem < 100
    return [Tin(loai, sk.du_an, f"hong-{dem}-lan" if hong else None)]
