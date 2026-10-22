"""Nút Deploy của Đại ca (spec `tu-deploy` "Nút Deploy của Đại ca"; `dieu-khien-tu-dong` "Estop dừng cả tự merge và
tự deploy", "Deploy tay khi dự án tạm dừng"; D97 luật 3; Đại ca chốt 18/10: `bat_ghi: false` không Deploy tay).
Chỉ GHI YÊU CẦU (`deploy.yeu_cau`, nguồn `dai_ca`); chuỗi lệnh chạy ở pha `vong_deploy` (`tram.deploy.vong`), nơi
khoá chung được xét lại ngay trước chuỗi. Idempotent theo `ma_thao_tac` (bảng `thao_tac`). Từ chối TRƯỚC khi tạo
bản ghi `thao_tac`: khoá chung `deploy_tay` (estop, `bat_ghi`, thiếu lệnh → 422 kèm nhãn), đang deploy hay đã có
yêu cầu chờ → 422, không có gì chờ → 422, commit Đại ca đang xem khác commit mới nhất → 409 (màn hình cũ)."""
from tram.deploy.hien_thi import dang_deploy, san_sang
from tram.deploy.doi_soat import chua_doi_soat
from tram.tu_dong.cong_kiem import cong_mo
from tram.deploy.san_sang import can_duong
from tram.deploy.trang_thai import chua_ghi_nhan, doc_su_kien
from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.tu_dong.khoa import NHAN_LY_DO, ly_do_chan
from tram.tu_dong.luu import doc_trang_thai, giao_dich

LOAI = "deploy.yeu_cau"


def deploy_thao_tac(kho, kho_tt, du_an: str, *, commit: str, ma: str, bat_ghi: bool,
                    estop_bat: bool, doc_dinh, expected_version: str) -> KetQuaThaoTac:
    def kiem() -> None:
        ly = ly_do_chan(doc_trang_thai(kho.db, du_an), viec="deploy_tay", bat_ghi=bat_ghi, estop_bat=estop_bat)
        if ly:
            raise KhongHopLe(NHAN_LY_DO[ly[0]])
        if doc_trang_thai(kho.db, du_an).phien_ban != expected_version:
            raise XungDot("Cài đặt đã đổi — tải lại")
        ds = doc_su_kien(kho.db, du_an)
        if chua_doi_soat(ds) or not cong_mo():
            raise KhongHopLe("Cổng kiểm đóng hoặc deploy chưa đối soát")
        can_duong(du_an, doc_trang_thai(kho.db, du_an).cai_dat)
        if dang_deploy(ds) is not None:
            raise KhongHopLe("Đang có một lần deploy của dự án này — chờ xong rồi bấm lại")
        if (ss := san_sang(ds)) is None:
            raise KhongHopLe("Không có bản mới nào chờ deploy")
        if ss["commit"] != commit or chua_ghi_nhan(ds) or doc_dinh() != commit:
            raise XungDot(f"Có bản mới hơn — tải lại (bản chờ deploy của {du_an} đã đổi: hiện {ss['commit'][:12]},"
                          f" đang xem {commit[:12]})")

    def buoc(_) -> dict:
        with giao_dich(kho.db):
            if not any(s.loai == LOAI and s.du_lieu.get("ma_thao_tac") == ma for s in doc_su_kien(kho.db, du_an)):
                ghi_trong_giao_dich(kho.db, du_an, LOAI, {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca",
                                    "phien_ban": expected_version},
                                    tac_nhan=TAC_NHAN, luc=bay_gio())
        return {"commit": commit}

    yc = YeuCau(ma, LOAI, du_an, None, {"commit": commit, "phien_ban": expected_version}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI, buoc)])
