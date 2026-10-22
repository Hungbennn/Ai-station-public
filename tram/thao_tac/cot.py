"""Kéo cột (spec 2 §5.1) và nút 'thử lại' (§12.5) — thao tác ghi bền theo ma_thao_tac."""
from tram.cham_cot.ghi import NHAN_COT, NHAN_KHOA
from tram.suy.cot import hien_tren_bang, ly_do_khong_keo, suy_vi_tri
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.loi import KhongHopLe


def _cot_he(kho, du_an: str, bead_id: str) -> tuple[str | None, str | None]:
    """Cột hệ ghi lần cuối — cùng cách 1a tính trong kiem_sua_tay."""
    s = kho.moi_nhat(du_an, bead_id, "cham_cot.ket_qua", dieu_kien=lambda x: x.du_lieu.get("da_ghi"))
    return (NHAN_COT.get(s.du_lieu.get("cot")), s.du_lieu.get("ly_do")) if s else (None, None)


def keo_cot(nc: NguCanhGhi, bead_id: str, *, cot: str, vi_sao: str | None, ma: str,
            expected_version: str) -> KetQuaThaoTac:
    if cot not in NHAN_COT:
        raise KhongHopLe("Cột đích phải là ai-lam hoặc can-chot")
    dich = NHAN_COT[cot]

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        vt = suy_vi_tri(b, {})
        if (ly_do := ly_do_khong_keo(b, vt)) is not None:
            raise KhongHopLe(ly_do)
        if vt.hang == cot:
            raise KhongHopLe("Bead đã ở cột này")

    def doi(labels) -> tuple[list[str], list[str]]:
        return ([n for n in (dich, NHAN_KHOA) if n not in labels],
                [n for n in labels if n.startswith("cot:") and n != dich])

    def ngu_canh(_) -> dict:
        b = nc.bd.mot(bead_id)
        cot_he, ly_do_he = _cot_he(nc.kho, nc.du_an, bead_id)
        return {"tieu_de": b.title, "cot_he": cot_he, "ly_do_he": ly_do_he, "nhan_dau": list(b.labels)}

    def nhan(d: dict) -> dict:
        them, bo = doi(nc.bd.mot(bead_id).labels)  # đối soát: crash sau bd update thì không ghi lại
        if bo or them:
            nc.bd.cap_nhat_nhan(bead_id, them=them, bo=bo)
        dau = d["ngu_canh"].get("nhan_dau")        # lưu thay đổi so với lúc đọc đầu, kể cả khi chạy lại sau crash
        them, bo = doi(dau) if dau is not None else (them, bo)
        return {"them": them, "bo": bo}

    def su_kien(d: dict) -> bool:
        nt = d["ngu_canh"]
        du_lieu = {"tieu_de": nt["tieu_de"], "cot_he": nt["cot_he"], "cot_moi": dich, "ly_do_he": nt["ly_do_he"],
                   "nguon": "dashboard", "da_ghi": True}
        if vi_sao:
            du_lieu["vi_sao"] = vi_sao
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.dai_ca_sua", du_lieu, ma=ma)

    yc = YeuCau(ma, "keo_cot", nc.du_an, bead_id, {"cot": cot, "vi_sao": vi_sao}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi,
                         cac_buoc=[("ngu_canh", ngu_canh), ("nhan", nhan), ("su_kien", su_kien)])


def thu_lai(nc: NguCanhGhi, bead_id: str, *, ma: str, expected_version: str) -> KetQuaThaoTac:
    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if b.issue_type == "epic" or not hien_tren_bang(b):
            raise KhongHopLe("Không thử lại epic hoặc bead đã đóng / hoãn")

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cham_cot.thu_lai", {}, ma=ma)

    yc = YeuCau(ma, "thu_lai", nc.du_an, bead_id, {}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[("su_kien", su_kien)])
