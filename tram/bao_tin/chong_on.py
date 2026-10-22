"""Chống ồn Telegram (spec 2 §6): tin đầu gửi ngay, gom phần sau trong 5 phút, không lặp trong 1 giờ, giờ yên lặng;
gửi lỗi thì xếp lại cho vòng sau. TM-1 (D98, D99): tin xấu của tự deploy và tin đổi cài đặt gửi cả trong giờ yên
lặng; tin tốt của tự merge / tự deploy gom tới khi hết giờ yên lặng (loại cũ vẫn bỏ như trước); loại "mỗi lần một
tin" không theo luật 1 giờ."""
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from tram.bao_tin.tin import Tin
from tram.cham_cot.ghi import GIO_VN

CUA_SO = timedelta(minutes=5)
KHONG_LAP = timedelta(hours=1)
LOAI_LUON_GUI = frozenset({"tram_loi", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro", "lui_hong",
                           "cai_dat_doi"})
GOM_SAU_YEN_LANG = frozenset({"tu_merge", "san_sang_deploy", "deploy_xong", "viec_moi_agent"})   # TC: D132
MOI_LAN_MOT_TIN = frozenset({"cai_dat_doi", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
                             "lui_hong"})


@dataclass(frozen=True)
class TinGui:
    loai: str
    tins: tuple[Tin, ...]


def _khoa(t: Tin) -> str:
    return f"{t.loai}|{t.du_an}|{t.bead_id or ''}"


def _gio(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def trong_gio_yen_lang(gio_yen_lang: str | None, luc: datetime) -> bool:
    if not gio_yen_lang:
        return False
    bat, ket = (_gio(x) for x in gio_yen_lang.split("-"))
    if bat == ket:          # khoảng rỗng — không có giờ yên lặng
        return False
    t = luc.astimezone(GIO_VN).time()
    return bat <= t < ket if bat < ket else (t >= bat or t < ket)


class BoChongOn:
    def __init__(self, gio_yen_lang: str | None = None, trang_thai: dict | None = None):
        tt = trang_thai or {}
        self._yen = gio_yen_lang
        self._da_gui: dict[str, str] = dict(tt.get("da_gui", {}))
        self._cua_so: dict[str, str] = dict(tt.get("cua_so", {}))
        self._cho: dict[str, list[list]] = {k: [list(x) for x in v] for k, v in tt.get("cho", {}).items()}
        self._sang: list[list] = [list(x) for x in tt.get("cho_sang", [])]        # [loai, du_an, bead_id]

    def trang_thai(self) -> dict:
        return {"da_gui": self._da_gui, "cua_so": self._cua_so, "cho": self._cho, "cho_sang": self._sang}

    def _hoan(self, t: Tin, luc: datetime) -> bool:
        """D98: tin tốt trong giờ yên lặng vào hàng `cho_sang` (không mất); True = đã hoãn."""
        if t.loai not in GOM_SAU_YEN_LANG or not trong_gio_yen_lang(self._yen, luc):
            return False
        if [t.loai, t.du_an, t.bead_id] not in self._sang:
            self._sang.append([t.loai, t.du_an, t.bead_id])
        return True

    def _duoc_gui(self, t: Tin, luc: datetime) -> bool:
        if t.loai not in LOAI_LUON_GUI and trong_gio_yen_lang(self._yen, luc):
            return False
        cu = None if t.loai in MOI_LAN_MOT_TIN else self._da_gui.get(_khoa(t))
        return cu is None or luc - datetime.fromisoformat(cu) >= KHONG_LAP

    def _gui(self, loai: str, tins: list[Tin], luc: datetime) -> TinGui:
        self._cua_so[loai] = luc.isoformat()
        for t in tins:
            self._da_gui[_khoa(t)] = luc.isoformat()
        return TinGui(loai, tuple(tins))

    def nhan(self, tins: list[Tin], luc: datetime) -> list[TinGui]:
        ngay: dict[str, list[Tin]] = {}
        for t in tins:
            if self._hoan(t, luc) or not self._duoc_gui(t, luc):
                continue
            cs = None if t.loai in LOAI_LUON_GUI - {"tram_loi"} else self._cua_so.get(t.loai)
            if cs is not None and luc - datetime.fromisoformat(cs) < CUA_SO:
                hang = self._cho.setdefault(t.loai, [])
                if [t.du_an, t.bead_id] not in hang:
                    hang.append([t.du_an, t.bead_id])
            elif t not in (ds := ngay.setdefault(t.loai, [])):
                ds.append(t)
        return [self._gui(loai, ds, luc) for loai, ds in ngay.items()]

    def tra_lai(self, tg: TinGui) -> None:
        """Gửi lỗi (spec 2 §6): xoá dấu 'đã gửi' (không tính luật 1 giờ), đưa tin lên đầu hàng chờ và coi cửa sổ
        đã hết hạn — `den_han` của vòng sau (15 s) gửi lại ngay."""
        for t in tg.tins:
            self._da_gui.pop(_khoa(t), None)
        self._cua_so[tg.loai] = (datetime.fromisoformat(self._cua_so[tg.loai]) - CUA_SO).isoformat()
        hang = self._cho.get(tg.loai, [])
        self._cho[tg.loai] = [[t.du_an, t.bead_id] for t in tg.tins if [t.du_an, t.bead_id] not in hang] + hang

    def den_han(self, luc: datetime) -> list[TinGui]:
        ra = []
        if self._sang and not trong_gio_yen_lang(self._yen, luc):           # D98: hết giờ yên lặng → gửi phần gom
            nhom: dict[str, list[Tin]] = {}
            for loai, d, b in self._sang:
                nhom.setdefault(loai, []).append(Tin(loai, d, b))
            self._sang, ra = [], [self._gui(loai, ds, luc) for loai, ds in nhom.items()]
        for loai in list(self._cua_so):
            if luc - datetime.fromisoformat(self._cua_so[loai]) < CUA_SO:
                continue
            cho = [t for d, b in self._cho.pop(loai, [])
                   if not self._hoan(t := Tin(loai, d, b), luc) and self._duoc_gui(t, luc)]
            if cho:
                ra.append(self._gui(loai, cho, luc))
            else:
                del self._cua_so[loai]
        han = luc - KHONG_LAP
        self._da_gui = {k: v for k, v in self._da_gui.items() if datetime.fromisoformat(v) > han}
        return ra
