"""Vòng tick — luồng feature (spec 4 §7, §8, §9, §10). Với mỗi feature `can-spec` đang mở:
- phiếu yêu cầu không hợp lệ → `phieu.loi` + MỘT escalation `phieu-thieu` mở (đóng mà vẫn sai thì tạo lại);
- `chuyen_duyet` (spec vừa xong hợp lệ) → `spec.xong {feature, nhanh, commit, digest_bead, file[], de_xuat[], giao_id}`
  rồi gỡ `can-spec`, gắn `cho-duyet-spec` (điểm dừng #1; Phê duyệt + Telegram);
- `spec` mà đợt sửa spec đã đủ trả về → escalation `spec-tra-ve-nhieu`; hết ngân sách chu kỳ → `het-ngan-sach`.
`mo_dot_spec_con_thieu` (chỉ ghi sự kiện, chạy cả khi estop): escalation `spec-tra-ve-nhieu` đã đóng → đợt mới."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.feature import (NHAN_CAN_SPEC, NHAN_CHO_DUYET, bat_dau_dot, buoc_feature, con_dot_spec,
                                    cua_so_spec, ly_do_khong_giao_spec, spec_xong_hop_le)
from tram.giao_viec.ke_hoach import duong_ke_hoach
from tram.giao_viec.ngan_sach import bat_dau_chu_ky, du_mot_phieu, ngan_sach_phieu
from tram.giao_viec.phieu_yeu_cau import doc_phieu
from tram.giao_viec.su_kien import SK, da_co, ghi_mot_lan, su_kien_bead
from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
from tram.giao_viec.xet_spec import doc_ke_hoach_tai
from tram.phieu.kho import KhoPhieu


def _phieu_thieu(bd, kho: KhoPhieu, da: DuAn, b, ds: list[SK], loi: list[str], luc: datetime) -> bool:
    dg = "sha256:" + hashlib.sha256(b.description.encode()).hexdigest()
    ghi_mot_lan(kho, da.ten, "phieu.loi", {"bead_id": b.id, "loi": loi[:20], "digest_mo_ta": dg}, bead_id=b.id,
                luc=luc, khoa=("bead_id", "digest_mo_ta"))
    tao = {s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.tao" and s.du_lieu["ly_do"] == "phieu-thieu"}
    dong = [s for s in ds if s.loai == "escalation.dong" and s.du_lieu.get("escalation_id") in tao]
    if tao - {s.du_lieu["escalation_id"] for s in dong}:
        return False                                     # đã có escalation phieu-thieu đang mở
    cau_hoi = f"Phiếu yêu cầu không hợp lệ: {'; '.join(loi[:5])}. Sửa mô tả feature rồi trả lời."
    return tao_escalation(bd, kho, da.ten, b, ly_do="phieu-thieu", cau_hoi=cau_hoi, giao_id=None,
                          nguon=f"pyc-{dong[-1].id if dong else 0}", luc=luc) is not None


def chuyen_cho_duyet(bd, kho: KhoPhieu, kg: Path, da: DuAn, b, ds: list[SK], luc: datetime) -> bool:
    kt = spec_xong_hop_le(cua_so_spec(ds))
    kh, dg, _ = doc_ke_hoach_tai(kg, kt.du_lieu["commit"], b.id)
    if kh is None:
        return False
    de_xuat = [{"khoa": x.khoa, "tieu_de": x.tieu_de, "loai": x.loai, "uu_tien": x.uu_tien, "phu_thuoc": x.phu_thuoc,
                "nhan": x.nhan} for x in kh.bead]
    ghi_mot_lan(kho, da.ten, "spec.xong", {
        "feature": b.id, "nhanh": f"tram/spec-{b.id}", "commit": kt.du_lieu["commit"], "digest_bead": dg,
        "file": [kh.spec_file, kh.plan_file, duong_ke_hoach(b.id)], "de_xuat": de_xuat,
        "giao_id": kt.du_lieu["giao_id"]}, bead_id=b.id, luc=luc, khoa=("giao_id",))
    bd.cap_nhat_nhan(b.id, them=[NHAN_CHO_DUYET], bo=[NHAN_CAN_SPEC])
    return True


CAU_HOI_DOT = "Spec đã bị trả về đủ số lần của đợt sửa spec. Làm tiếp (mở đợt mới), đổi hướng hay dừng?"


def day_feature(kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str], kg: Path | None,
                luc: datetime, *, pha: str = "tat_ca") -> dict[str, int]:
    theo_id, ton, dem, ns = {b.id: b for b in beads}, viec_ton_cua(kho, da.ten), {}, da.giao.ngan_sach

    def esc(b, ly_do: str, cau_hoi: str, nguon: str) -> bool:
        return tao_escalation(bd, kho, da.ten, b, ly_do=ly_do, cau_hoi=cau_hoi, giao_id=None, nguon=nguon,
                              luc=luc) is not None

    for b in beads:
        ly = ly_do_khong_giao_spec(b, san_sang, da.ten)
        if ly not in (None, "phieu-thieu"):
            continue
        ds, kq = su_kien_bead(kho, da.ten, b.id), None
        if ly == "phieu-thieu" and pha != "git":
            kq = "phieu_thieu" if _phieu_thieu(bd, kho, da, b, ds, doc_phieu(b.description, da.ten)[1], luc) else None
        elif ((buoc := buoc_feature(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton))) == "chuyen_duyet"
              and pha != "nhanh"):
            kq = "spec_xong" if kg is not None and chuyen_cho_duyet(bd, kho, kg, da, b, ds, luc) else None
        elif buoc == "spec" and pha != "git" and not con_dot_spec(ds):
            kq = "spec_tra_ve_nhieu" if esc(b, "spec-tra-ve-nhieu", CAU_HOI_DOT, f"dot-{bat_dau_dot(ds)}") else None
        elif buoc == "spec" and pha != "git" and not du_mot_phieu(kho, ds, ngan_sach_phieu("spec", ns), ns.bead):
            kq = "het_ngan_sach" if esc(b, "het-ngan-sach", "", f"ns-{bat_dau_chu_ky(ds)}") else None
        if kq:
            dem[kq] = dem.get(kq, 0) + 1
    return dem


def mo_dot_spec_con_thieu(kho: KhoPhieu, du_an: str, luc: datetime) -> int:
    so = 0
    for i, raw in kho.db.execute("SELECT id, du_lieu FROM su_kien WHERE du_an = ? AND loai = 'escalation.dong' AND"
                                 " json_extract(du_lieu, '$.ly_do') = 'spec-tra-ve-nhieu' ORDER BY id", (du_an,)):
        d = json.loads(raw)
        if not da_co(kho, du_an, "ngan_sach.dot_spec_moi", {"bead_id": d["bead_goc"], "nguon_su_kien_id": i}):
            so += ghi_mot_lan(kho, du_an, "ngan_sach.dot_spec_moi", {"bead_id": d["bead_goc"], "nguon_su_kien_id": i},
                              bead_id=d["bead_goc"], luc=luc, khoa=("bead_id", "nguon_su_kien_id")) is not None
    return so
