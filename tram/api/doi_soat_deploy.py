"""Tiếp tục chỉ mở chốt deploy khi Đại ca xác nhận đúng bản và đường đích chứng minh đã dừng."""
from pydantic import BaseModel, ConfigDict, Field

from tram.api.than import ThanGhi
from tram.deploy.doi_soat import ban_can_doi_soat
from tram.deploy.duong import DuongDeploy
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import doc_su_kien
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa, KiemLaiDangBan
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.thao_tac.chay import YeuCau, chay_thao_tac
from tram.tu_dong.luu import ghi_tam_dung
from tram.thao_tac.tu_dong import tam_dung_thao_tac
from tram.tu_dong.cai_dat import tu_phang


class XacNhan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma: str = Field(min_length=1, max_length=64)
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")


class ThanTiepTuc(ThanGhi):
    doi_soat: XacNhan | None = None


def _doi_soat(kho, ten, xn):
    ds = doc_su_kien(kho.db, ten)
    can = ban_can_doi_soat(ds)
    if can is None:
        if xn and not any(s.loai == "deploy.doi_soat" and s.du_lieu.get("ma_thao_tac") == xn.ma
                          and s.du_lieu.get("commit") == xn.commit for s in ds):
            raise XungDot("Lượt đối soát đã đổi — tải lại")
        return
    if xn is None:
        raise KhongHopLe("Cần xác nhận bản thực tế và lượt cũ đã dừng trước khi Tiếp tục")
    if xn.ma != can["ma"] or xn.commit not in (can["commit"], can["truoc"]):
        raise XungDot("Lượt hoặc bản đối soát đã đổi — tải lại")
    bd = next(s for s in ds if s.loai == "deploy.bat_dau" and s.du_lieu.get("ma_thao_tac") == xn.ma)
    try:
        duong = DuongDeploy(ten, tu_phang(bd.du_lieu["cai_dat"]))
        r = duong.goi("doi_soat", xn.ma, xn.commit, can["truoc"])
    except (OSError, ValueError, KeyError):
        r = None
    if not r or not all(r[k] for k in ("dat", "da_dung", "san_sang")):
        raise KhongHopLe("Chưa xác minh được bản thực tế hoặc lượt cũ còn chạy")
    ghi(kho.db, ten, "deploy.doi_soat", {"ma_thao_tac": xn.ma, "commit": xn.commit,
                                       "xac_nhan": "dai-ca/passkey"})


def tiep_tuc(kho, kho_tt, ten, than):
    try:
        with giu_khoa(tram_home() / "deploy-khoa" / f"{ten}.lock"):
            if than.doi_soat is None:
                _doi_soat(kho, ten, None)
                return tam_dung_thao_tac(kho, kho_tt, ten, tam_dung=False,
                                         ma=than.ma_thao_tac, expected_version=than.expected_version)
            def buoc(_):
                _doi_soat(kho, ten, than.doi_soat)
                ghi_tam_dung(kho.db, ten, tam_dung=False, tac_nhan="dai-ca/dashboard",
                             them={"ma_thao_tac": than.ma_thao_tac})
                return True
            yc = YeuCau(than.ma_thao_tac, "tu_dong.tiep_tuc", ten, None,
                         {"doi_soat": than.doi_soat.model_dump()}, than.expected_version)
            return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None,
                                 cac_buoc=[("tu_dong.tiep_tuc", buoc)])
    except KiemLaiDangBan:
        raise KhongHopLe("Chuỗi deploy đang chạy — chờ kết thúc") from None
