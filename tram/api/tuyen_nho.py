"""Màn Ký ức (spec 2 §7 `/api/nho/*`, spec 1b §3 lát 1b-3): xem, xoá, ghi tay ký ức; xem/xoá ký ức thăng cấp đang
chờ tự có hiệu lực (#19). tram-api gọi memory service qua HTTP nội bộ (Bearer `tram-nho-token`, spec 1b §9.1).

Ký ức của MỌI dự án (cả nghiệp vụ và `nguon`) chỉ cho Đại ca: GET cũng cần danh tính Đại ca (khác trang bead).
POST ghi theo đúng quy ước lát 2a: danh tính + `X-Tram` + `Origin`, `ma_thao_tac` qua bảng `thao_tac`."""
import json
from contextlib import closing

from fastapi import APIRouter, Depends, HTTPException, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau, yeu_cau_ghi
from tram.api.khach_nho import CHO_DOC, CHO_GHI
from tram.api.than import ThanNhoGhi, ThanNhoXoa
from tram.duong_dan import bay_gio
from tram.nho.khach import LoiNhoKhach
from tram.nho.pham_vi import du_an_cua
from tram.suy.lam_sach import lam_sach
from tram.suy.mo_ta_su_kien import mo_ta
from tram.thao_tac.chay import YeuCau, chay_thao_tac
from tram.thao_tac.loi import KhongHopLe, KhongThay, XungDot

router = APIRouter()
DU_AN_HE = "_tram"
KHOA_NHO = "nho"            # khoá riêng của thao tác ký ức trong bảng thao_tac —
                            # không chờ chung khoá estop (`_tram`, None)
LOAI_SU_KIEN = ("nho.ghi", "nho.gop", "nho.xoa", "nho.xoa_cung", "nho.thang_cap", "nho.tu_choi", "nho.loi_tach",
                "nho.loi_llm", "nho.loi_embedder", "nho.phuc_hoi", "nho.bo_bi_mat")   # 2f: + bỏ vì bí mật (1b-4)
SO_SU_KIEN = 50


def yeu_cau_dai_ca(request: Request) -> None:
    if not la_dai_ca_yeu_cau(request):
        raise HTTPException(status_code=403, detail="Ký ức chỉ Đại ca xem được (cần danh tính Tailscale của Đại ca)")


def _goi(pt, duong: str, than: dict, cho: float) -> dict:
    if pt.nho is None:
        raise LoiNhoKhach("tram-api chưa nối memory service")
    try:
        return pt.nho.goi(duong, than, thoi_gian_cho=cho)
    except LoiNhoKhach as e:
        loi = lam_sach(str(e.than.get("loi") or e), 300)
        if e.ma == 409:
            raise XungDot(loi) from None
        if e.ma == 404:
            raise KhongThay(loi) from None
        if e.ma == 422:
            raise KhongHopLe("; ".join([loi] + [lam_sach(str(x), 200) for x in (e.than.get("ly_do") or [])[:5]]))
        raise LoiNhoKhach(loi, ma=e.ma) from None


def _sach(k: dict, bay: str) -> dict:
    nguon = [{lam_sach(str(a), 30): lam_sach(str(b), 100) for a, b in list(n.items())[:10]}
             for n in (k.get("nguon") or [])[:20] if isinstance(n, dict)]
    return {"id": lam_sach(k.get("id"), 64), "noi_dung": lam_sach(k.get("noi_dung"), 1000),
            "pham_vi": lam_sach(k.get("pham_vi"), 200),
            "nhan": [lam_sach(str(x), 30) for x in (k.get("nhan") or [])][:5],
            "quan_trong": float(k.get("quan_trong") or 0), "nguon": nguon, "nguon_dai_ca": bool(k.get("nguon_dai_ca")),
            "tao_luc": lam_sach(k.get("tao_luc"), 30), "hieu_luc_tu": lam_sach(k.get("hieu_luc_tu"), 30),
            "dung_luc": lam_sach(k.get("dung_luc"), 30) or None, "so_lan_dung": int(k.get("so_lan_dung") or 0),
            "dang_cho": str(k.get("hieu_luc_tu") or "") > bay}


@router.get("/api/nho", dependencies=[Depends(yeu_cau_dai_ca)])
def danh_sach(request: Request, pham_vi: str = "", cho: bool = False) -> dict:
    r = _goi(request.app.state.pt, "/danh-sach", {"pham_vi": pham_vi or None, "cho_hieu_luc": cho, "gioi_han": 200},
             CHO_DOC)
    bay = bay_gio()
    return {"ky_uc": [_sach(k, bay) for k in r.get("ky_uc") or []], "tong": int(r.get("tong") or 0),
            "pham_vi": [{"pham_vi": lam_sach(p.get("pham_vi"), 200), "so": int(p.get("so") or 0),
                         "so_cho": int(p.get("so_cho") or 0)} for p in r.get("pham_vi") or []]}


@router.get("/api/nho/su-kien", dependencies=[Depends(yeu_cau_dai_ca)])
def su_kien(request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho:
        ds = [s for d in [*pt.cac_du_an(), DU_AN_HE] for l in LOAI_SU_KIEN for s in kho.gan_day(d, l, SO_SU_KIEN)]
    ds = sorted(ds, key=lambda s: -s.id)[:SO_SU_KIEN]
    return {"su_kien": [{"id": s.id, "luc": s.luc, "du_an": s.du_an, "bead_id": s.bead_id, "loai": s.loai,
                         "tom_tat": lam_sach(json.dumps(s.du_lieu, ensure_ascii=False), 300),
                         "mo_ta": mo_ta(s)} for s in ds]}                  # 2f (D39): câu từ mẫu cố định


def _chay(pt, than, loai: str, noi_dung: dict, buoc) -> dict:
    yc = YeuCau(than.ma_thao_tac, loai, DU_AN_HE, KHOA_NHO, noi_dung, than.expected_version)
    with closing(pt.mo_kho_tt()) as kho_tt:      # không kiểm expected_version: ký ức không có phiên bản (G-plan 1b-3)
        kq = chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None, cac_buoc=[(loai.removeprefix("nho."), buoc)])
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/nho/xoa", dependencies=[Depends(yeu_cau_ghi)])
def xoa(than: ThanNhoXoa, request: Request) -> dict:
    pt = request.app.state.pt
    return _chay(pt, than, "nho.xoa", {"id": than.id}, lambda _: _goi(pt, "/xoa", {"id": than.id}, CHO_DOC))


@router.post("/api/nho/ghi", dependencies=[Depends(yeu_cau_ghi)])
def ghi(than: ThanNhoGhi, request: Request) -> dict:
    pt = request.app.state.pt
    if (d := du_an_cua(than.pham_vi)) is not None and d not in pt.cac_du_an():
        raise KhongThay(f"Không có dự án {lam_sach(d, 64)}")
    noi_dung = {"noi_dung": than.noi_dung, "pham_vi": than.pham_vi, "nhan": than.nhan}
    return _chay(pt, than, "nho.ghi", noi_dung,
                 lambda _: _goi(pt, "/ghi", {**noi_dung, "ma_thao_tac": than.ma_thao_tac}, CHO_GHI))
