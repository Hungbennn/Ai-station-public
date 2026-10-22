"""Khoá hiển thị TM-3 cho trang Tự động và Phê duyệt (D129: cùng tuyến ghi Deploy)."""
from tram.deploy.hien_thi import dang_deploy, lich_su, san_sang
from tram.deploy.doi_soat import ban_can_doi_soat
from tram.deploy.trang_thai import cuoi, dem_hong, doc_su_kien
from tram.tu_dong.luu import doc_trang_thai


def san_sang_du_an(db, ten):
    return san_sang(doc_su_kien(db, ten)) if doc_trang_thai(db, ten).cai_dat.du_lenh else None


def tom_tat_deploy(db, ten):
    return {"san_sang": san_sang_du_an(db, ten) is not None, "dem_hong": dem_hong(doc_su_kien(db, ten))}


def chi_tiet_deploy(db, ten):
    ds = doc_su_kien(db, ten)
    cho = cuoi(ds, "deploy.cho")
    nhan = {"deploy_cho_cam": "Bản chạm đường cấm hoặc schema — cần kịch bản riêng",
            "deploy_cho_duong": "Cần đường deploy riêng", "deploy_cho_ban_nen": "Cần bản quay lại đã kiểm",
            "deploy_cho_pham_vi": "Có mã ngoài luồng — Đại ca xem phạm vi rồi Deploy tay",
            "deploy_cho_kiem": "Bản gộp chưa kiểm đạt", "deploy_cho_doi_soat": "Cần đối soát hoặc mở cổng kiểm"}
    ly = nhan.get(cho.du_lieu.get("ly_do"), "") if cho else ""
    return {"san_sang": san_sang_du_an(db, ten), "dang_deploy": dang_deploy(ds), "ly_do_deploy": ly,
            "lich_su": lich_su(ds), "dem_hong": dem_hong(ds), "doi_soat": ban_can_doi_soat(ds)}


def muc_san_sang(du_an, kho):
    from tram.suy.phe_duyet import _muc
    ss = san_sang_du_an(kho.db, du_an)
    return [] if ss is None else [{**_muc("san-sang-deploy", du_an, None,
        {**ss, "phien_ban": doc_trang_thai(kho.db, du_an).phien_ban}), "updated_at": ss["luc"]}]
