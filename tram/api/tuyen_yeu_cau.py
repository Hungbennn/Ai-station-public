"""Máy A gửi yêu cầu, máy B tạo feature (D46/D47; spec 4 §7.1; kiến trúc §5.7 bước 1–2; plan 4d 4D-2).

Hai tuyến đều qua `yeu_cau_ghi` như API ghi của dashboard: kênh ghi, đúng một `Tailscale-User-Login` ∈ `dai_ca_logins`
do `tailscale serve` gắn, `X-Tram: 1`, `Origin` = máy B. `/xem` không ghi dữ liệu. Kho beads do B chọn theo
`du-an/<du_an>.yaml` (`tao_bd_yeu_cau`), không nhận đường dẫn từ máy A. Dự án `bat_ghi: false` → 422 trước khi mở sổ
hay gọi bd. Chỉ tạo `feature` nhãn `can-spec`, actor `dai-ca/may-a` (nhãn nguồn, không phải chứng thực)."""
import json
from contextlib import closing

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

from tram.api.bao_mat import HEADER_DANH_TINH, yeu_cau_ghi
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.giao_viec.phieu_yeu_cau import DAU, doc_phieu
from tram.thao_tac.loi import KhongHopLe
from tram.yeu_cau.dich_vu import tiep_nhan
from tram.yeu_cau.mau import YeuCau, dau_xem, digest, mo_ta

router = APIRouter(dependencies=[Depends(yeu_cau_ghi)], route_class=TuyenEnvelopeKin)
MA_HTTP = {"da_tao": 201, "da_co": 200, "dang_xu_ly": 202, "khong_ro": 202, "xung_dot": 409, "chua_tao": 503}


class ThanXem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma_yeu_cau: str = Field(pattern=r"^yc-[0-9a-f]{32}$")
    du_an: str = Field(min_length=1, max_length=64)
    tieu_de: str = Field(min_length=1, max_length=200)
    uu_tien: StrictInt = Field(ge=0, le=4)
    phieu: dict

    @field_validator("tieu_de")
    @classmethod
    def _mot_dong(cls, v: str) -> str:
        if not v.isprintable() or v != v.strip() or v.startswith("-"):
            raise ValueError("một dòng in được, không khoảng trắng đầu/cuối, không bắt đầu bằng '-'")
        return v


class ThanTao(ThanXem):
    dau_xem: str = Field(pattern=r"^[0-9a-f]{16}$")


def _bat_ghi(pt, du_an: str) -> bool:
    """1a-2 Task 5 (D31): `pt.bat_ghi`. Chưa nối, yaml lỗi, lỗi bất kỳ → coi như CHƯA bật (đóng khi lỗi)."""
    try:
        return pt.bat_ghi(du_an) is True
    except Exception:
        return False


def _yeu_cau(than: ThanXem) -> tuple[YeuCau | None, list[str]]:
    p, loi = doc_phieu(f"{DAU}\n{json.dumps(than.phieu, ensure_ascii=False)}\n{DAU}", than.du_an)
    if p is None:
        return None, loi
    yc = YeuCau(than.ma_yeu_cau, than.du_an, than.tieu_de, than.uu_tien, p)
    _, loi = doc_phieu(mo_ta(yc), than.du_an)          # mô tả thật sẽ ghi cũng phải đạt kiểm của vòng tick
    return (yc if not loi else None), loi


def _tra(trang_thai: str, ma: int, **them) -> JSONResponse:
    return JSONResponse({"trang_thai": trang_thai, **them}, status_code=ma)


def _bd(pt, du_an: str):
    """Bd của dự án theo du-an/<du_an>.yaml; chưa nối hoặc yaml lỗi → None (chắc chắn chưa ghi gì)."""
    try:
        return pt.tao_bd_yeu_cau(du_an) if pt.tao_bd_yeu_cau is not None else None
    except Exception:
        return None


@router.post("/api/feature/yeu-cau/xem")
def xem(than: ThanXem, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, than.du_an)
    yc, loi = _yeu_cau(than)
    bat, bd, bn = _bat_ghi(pt, than.du_an), _bd(pt, than.du_an), None
    if bat and pt.mo_so_nhan is not None:              # chưa bật ghi: không mở sổ
        with closing(pt.mo_so_nhan()) as so:
            bn = so.lay(than.ma_yeu_cau)
    cung = None if bn is None or yc is None else bn.digest == digest(yc)
    return {"hop_le": yc is not None, "loi": loi, "du_an": than.du_an, "kho": str(bd.repo) if bd else None,
            "bat_ghi": bat, "ma_yeu_cau": than.ma_yeu_cau, "dau_xem": dau_xem(yc) if yc else None,
            "bien_nhan": None if bn is None else {"trang_thai": bn.trang_thai, "cung_noi_dung": cung,
                                                   "bead_id": bn.bead_id if cung else None}}


@router.post("/api/feature/yeu-cau")
def tao(than: ThanTao, request: Request) -> JSONResponse:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, than.du_an)
    if not _bat_ghi(pt, than.du_an):
        raise KhongHopLe(f"Dự án {than.du_an} chưa bật ghi (bat_ghi trong du-an/{than.du_an}.yaml) — không tạo")
    bd = _bd(pt, than.du_an)
    if pt.mo_so_nhan is None or bd is None:
        return _tra("chua_bat", 503)
    yc, loi = _yeu_cau(than)
    if yc is None:
        return _tra("khong_hop_le", 422, loi=loi)
    if dau_xem(yc) != than.dau_xem:
        return _tra("lech_ban_xem", 409, ma_yeu_cau=yc.ma)
    nguoi_gui = request.headers[HEADER_DANH_TINH].strip()       # đã qua yeu_cau_ghi: đúng một header hợp lệ
    try:
        with closing(pt.mo_so_nhan()) as so:
            kq = tiep_nhan(so, bd, yc, nguoi_gui=nguoi_gui)
    finally:
        pt.bo_dem.danh_dau_cu(yc.du_an)
    return _tra(kq.trang_thai, MA_HTTP[kq.trang_thai], ma_yeu_cau=yc.ma, du_an=yc.du_an, bead_id=kq.bead_id,
                ly_do=kq.ly_do)
