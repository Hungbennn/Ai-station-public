"""D129: một tuyến Deploy dùng chung trang Tự động và Phê duyệt; kiểm bản mới nhất lúc nhận."""
from fastapi import APIRouter, Depends, Request
from pydantic import Field

from tram.api.passkey_phu_thuoc import dich_vu
from tram.api.passkey_tu_dong import can_p
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanGhi
from tram.api.tuyen_tu_dong import _bat_ghi, _chay
from tram.cau_hinh.du_an import nap_du_an
from tram.chu import estop
from tram.deploy.ban import chon_ban
from tram.deploy.trang_thai import doc_su_kien
from tram.giao_viec.git_kiem import kho_kiem
from tram.thao_tac.deploy import deploy_thao_tac

router = APIRouter(dependencies=[Depends(dich_vu), Depends(can_p)], route_class=TuyenEnvelopeKin)


class ThanDeploy(ThanGhi):
    expected_commit: str = Field(pattern=r"^[0-9a-f]{40}$")


def doc_dinh(ten, db):
    return chon_ban(kho_kiem(ten), doc_su_kien(db, ten), nap_du_an(ten).nhanh_chinh)


@router.post("/api/du-an/{ten}/tu-dong/deploy")
def r_deploy(ten: str, than: ThanDeploy, request: Request):
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    return _chay(request, lambda k, kt: deploy_thao_tac(
        k, kt, ten, commit=than.expected_commit, ma=than.ma_thao_tac, bat_ghi=_bat_ghi(pt, ten),
        estop_bat=estop.dang_bat(), doc_dinh=lambda: doc_dinh(ten, k.db),
        expected_version=than.expected_version))
