"""Nút Chốt (spec 2 §5.1, §12.3): decision → đóng → nối → gỡ nhãn → sự kiện; idempotent, đối soát khi crash."""
import re

from tram.cham_cot.ghi import NHAN_KHOA
from tram.suy.cot import cham_gan_nhat, ly_do_khong_chot, suy_vi_tri
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.loi import KhongHopLe

ADR_RE = re.compile(r"ADR-\d{4}")
CAU_CHUNG = "Chốt chung cho bead (lần chấm không có câu hỏi cụ thể)"
DAU_MA = "<!-- tram:ma_thao_tac={} -->"


def cau_hoi_hien_tai(kho, du_an: str, bead_id: str) -> list[str]:
    s = cham_gan_nhat(kho, du_an, bead_id)
    hoi = [q for q in (s.du_lieu.get("cau_hoi") or []) if q] if s else []
    return hoi or [CAU_CHUNG]


def kiem_noi_dung(hoi: list[str], tra_loi: list[str], adr: str | None) -> None:
    if adr is not None:
        if tra_loi:
            raise KhongHopLe("Chọn trả lời từng câu hoặc dẫn ADR, không cả hai")
        if not ADR_RE.fullmatch(adr):
            raise KhongHopLe("ADR phải có dạng ADR-0000")
        return
    if not tra_loi or len(tra_loi) != len(hoi) or any(not t.strip() for t in tra_loi):
        raise KhongHopLe(f"Cần đủ {len(hoi)} câu trả lời, không để trống")


def mo_ta_decision(bead_id: str, hoi: list[str], tra_loi: list[str], adr: str | None, ma: str) -> str:
    dong = [f"Chốt cho {bead_id} từ dashboard.", ""]
    if adr:
        dong.append(f"Dẫn ADR: {adr}")
    else:
        for q, a in zip(hoi, tra_loi):
            dong += [f"Hỏi: {q}", f"Đáp: {a.strip()}", ""]
    return "\n".join(dong + ["", DAU_MA.format(ma)])


def ly_do_dong(tra_loi: list[str], adr: str | None) -> str:
    s = f"Theo {adr}" if adr else "; ".join(f"({i}) {a.strip()}" for i, a in enumerate(tra_loi, 1))
    return s[:2000]


def chot(nc: NguCanhGhi, bead_id: str, *, tra_loi: list[str] | None, adr: str | None, ma: str,
         expected_version: str) -> KetQuaThaoTac:
    tra_loi = list(tra_loi or [])

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if (ly_do := ly_do_khong_chot(b, suy_vi_tri(b, {}))) is not None:
            raise KhongHopLe(ly_do)
        kiem_noi_dung(cau_hoi_hien_tai(nc.kho, nc.du_an, bead_id), tra_loi, adr)

    def ngu_canh(_) -> dict:
        return {"tieu_de": nc.bd.mot(bead_id).title, "cau_hoi": cau_hoi_hien_tai(nc.kho, nc.du_an, bead_id)}

    def tao_decision(d: dict) -> str:
        dau = DAU_MA.format(ma)                    # đối soát: crash sau bd create thì không tạo cái thứ hai
        co = sorted(b.id for b in nc.bd.tat_ca() if b.issue_type == "decision" and dau in b.description)
        if co:
            return co[0]
        nt = d["ngu_canh"]
        return nc.bd.tao(f"Chốt: {nt['tieu_de']}"[:200], loai="decision",
                         mo_ta=mo_ta_decision(bead_id, nt["cau_hoi"], tra_loi, adr, ma))

    def dong_decision(d: dict) -> bool:
        if nc.bd.mot(d["tao_decision"]).status != "closed":
            nc.bd.dong(d["tao_decision"], ly_do_dong(tra_loi, adr))
        return True

    def noi(d: dict) -> bool:
        b = nc.bd.mot(bead_id)                     # `bd dep add` lặp vẫn "Added" — tự kiểm trùng (spike)
        if not any(p.depends_on_id == d["tao_decision"] and p.loai == "blocks" for p in b.phu_thuoc):
            nc.bd.them_phu_thuoc(bead_id, d["tao_decision"])
        return True

    def go_nhan(_) -> list[str]:
        b = nc.bd.mot(bead_id)
        bo = [n for n in b.labels if n.startswith("cot:") or n == NHAN_KHOA]
        if bo:
            nc.bd.cap_nhat_nhan(bead_id, bo=bo)
        return bo

    def su_kien(d: dict) -> bool:
        du_lieu = {"decision_id": d["tao_decision"], "cau_hoi": d["ngu_canh"]["cau_hoi"],
                   "tra_loi": [t.strip() for t in tra_loi]}
        if adr:
            du_lieu["adr"] = adr
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.da_chot", du_lieu, ma=ma)

    yc = YeuCau(ma, "chot", nc.du_an, bead_id, {"tra_loi": tra_loi, "adr": adr}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[
        ("ngu_canh", ngu_canh), ("tao_decision", tao_decision), ("dong_decision", dong_decision),
        ("noi", noi), ("go_nhan", go_nhan), ("su_kien", su_kien)])
