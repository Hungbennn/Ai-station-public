"""Vòng lặp tram-bao-tin (spec 2 §6): đọc sự kiện mới theo mốc riêng → nguồn tin → chống ồn → Telegram."""
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.luu import doc_json, ghi_json
from tram.bao_tin.nguon import anh_tu_beads, tin_tu_anh, tin_tu_su_kien
from tram.bao_tin.telegram import LoiTelegram
from tram.bao_tin.tin import soan_tin
from tram.beads.bd import LoiBd

CHU_KY_GIAY = 15


def _bay_gio_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class NguCanhBaoTin:
    kho: object
    tao_bd: Callable[[str], object]
    gui: Callable[[str], None]
    thu_muc: Path
    passkey_path: Path | None = None
    gio_yen_lang: str | None = None
    dashboard_url: str | None = None
    bay_gio: Callable[[], datetime] = _bay_gio_utc


def _anh(nc: NguCanhBaoTin, du_an: str) -> tuple[list, dict | None]:
    try:
        beads = nc.tao_bd(du_an).tat_ca()
    except (LoiBd, OSError, ValueError) as e:
        print(f"bao-tin {du_an}: {e}", file=sys.stderr)
        return [], None
    truoc = doc_json(nc.thu_muc / f"anh-{du_an}.json", None)
    return ([] if truoc is None else tin_tu_anh(du_an, truoc, beads)), anh_tu_beads(beads)


def mot_vong(nc: NguCanhBaoTin) -> int:
    from tram.bao_tin.passkey import gui_cho
    gui_cho(nc.passkey_path, nc.gio_yen_lang, nc.bay_gio(), nc.gui)
    p_moc = nc.thu_muc / "moc.json"
    moc = doc_json(p_moc, None)
    if moc is None:
        ghi_json(p_moc, {"sau_id": nc.kho.id_moi_nhat()})
        return 0
    ds = nc.kho.sau_id(moc["sau_id"], 500)
    tins = [t for sk in ds for t in tin_tu_su_kien(sk, nc.kho)]
    anh_moi = {}
    for du_an in sorted({sk.du_an for sk in ds if sk.loai == "quet.xong" and not sk.du_an.startswith("_")}):
        them, anh = _anh(nc, du_an)
        tins += them
        if anh is not None:
            anh_moi[du_an] = anh
    p_co = nc.thu_muc / "chong-on.json"
    bo, luc, da_gui = BoChongOn(nc.gio_yen_lang, doc_json(p_co, None)), nc.bay_gio(), 0
    for tg in bo.den_han(luc) + bo.nhan(tins, luc):  # hàng chờ (kể cả tin gửi lỗi vòng trước) trước, tin mới sau
        try:
            nc.gui(soan_tin(tg.loai, tg.tins, nc.dashboard_url))
            da_gui += 1
        except LoiTelegram as e:
            print(f"bao-tin: {e} — xếp lại, gửi lại vòng sau", file=sys.stderr)
            bo.tra_lai(tg)
    ghi_json(p_co, bo.trang_thai())
    for du_an, anh in anh_moi.items():
        ghi_json(nc.thu_muc / f"anh-{du_an}.json", anh)
    if ds:
        ghi_json(p_moc, {"sau_id": ds[-1].id})
    return da_gui


def chay_mai(nc, *, nghi=time.sleep, chu_ky_giay: int = CHU_KY_GIAY, so_vong: int | None = None) -> None:
    i = 0
    while so_vong is None or i < so_vong:
        try:
            mot_vong(nc)
        except Exception as e:                       # một vòng lỗi không được giết dịch vụ
            print(f"bao-tin: vòng lỗi {type(e).__name__}: {e}", file=sys.stderr)
        i += 1
        nghi(chu_ky_giay)


def tao_ngu_canh_that() -> NguCanhBaoTin | None:
    from tram.bao_tin.telegram import doc_token, gui_telegram
    from tram.beads.bd import Bd
    from tram.cau_hinh.du_an import nap_du_an
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.duong_dan import tram_home
    from tram.su_kien.kho import mo_kho

    ch = nap_cau_hinh_tram()
    if not ch.telegram.chat_id:
        return None
    token = doc_token()
    if not token:
        return None
    return NguCanhBaoTin(kho=mo_kho(), tao_bd=lambda ten: Bd(nap_du_an(ten).duong_dan),
                         gui=lambda vb: gui_telegram(token, ch.telegram.chat_id, vb), thu_muc=tram_home() / "bao-tin",
                         gio_yen_lang=ch.telegram.gio_yen_lang, dashboard_url=ch.dashboard_url,
                         passkey_path=tram_home() / 'passkey.db')
