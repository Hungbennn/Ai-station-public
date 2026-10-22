"""Dựng `DeXuatPhieu` (spec 4 §6.1, §6.3; phần 3 cấp `giao_id`, `luot`, `khe_id`, `han_giu`, `ma_giao` — 3a-1 G8).

`cha`: `code` lần đầu = `origin/<nhanh_chinh>`; giao lại = snapshot; code lại = SHA công bố mới nhất (cái nào ghi
sau cùng trong `giao.snapshot`/`giao.cong_bo`). `qc`: `cha` = commit code đã kiểm lại đạt. Spike tài liệu: không
lệnh kiểm, `lenh_cho_phep` rỗng, không môi trường kiểm."""
from pathlib import Path

from pydantic import ValidationError

from tram.cham_cot.prompt import nap_vai
from tram.de_nghi.cai_dat import doc_cai_dat
from tram.de_nghi.huong_dan import huong_dan
from tram.giao_viec.chon import VAI, UngVien
from tram.giao_viec.git_kiem import sha_cua
from tram.giao_viec.goi import DauVaoGoi, GoiQuaLon, dung_goi
from tram.giao_viec.lop_5 import thu_lop_5
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c, luong_lien_quan
from tram.giao_viec.lop_4 import doc_tai_lieu, thu_lop_4
from tram.giao_viec.ngan_sach import ngan_sach_phieu
from tram.giao_viec.quyen import phien_ban_quyen
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.giao_viec.tieu_chi import khoa_chong_trung, lenh_bat_buoc, tach_tieu_chi
from tram.phieu.mo_hinh import DeXuatPhieu, Repo


def cha_cua(ds: list[SK], buoc: str, kho_git: Path, nhanh_chinh: str) -> str | None:
    if buoc == "qc":
        kl = moi_nhat(cua_so(ds), "kiem.lai", lambda s: s.du_lieu["dat"])
        return kl.du_lieu["commit"] if kl else None
    plan = {s.du_lieu["luot"] for s in ds if s.loai == "giao.nhan" and s.du_lieu.get("co", {}).get("pha")}
    moc = max((s for s in ds if s.loai in ("giao.snapshot", "giao.cong_bo")
               and s.du_lieu.get("luot") not in plan), key=lambda s: s.id, default=None)
    return moc.du_lieu["commit"] if moc else sha_cua(kho_git, f"origin/{nhanh_chinh}")


def dung_de_xuat(uv: UngVien, ds: list[SK], theo_id: dict, kho_git: Path,
                 p4c: PhuThuoc4c = PhuThuoc4c(), db=None) -> DeXuatPhieu | None:
    """None khi chưa dựng được: chưa có `cha`, phiếu code thiếu lệnh bắt buộc, hoặc nội dung vượt khuôn phiếu.
    `db` (kết nối `su-kien.db`): đọc nút tự cập nhật việc cho hướng dẫn lớp 2 (TC); None → không hướng dẫn."""
    b, da, buoc = uv.bead, uv.du_an, uv.buoc
    if (cha := cha_cua(ds, buoc, kho_git, da.nhanh_chinh)) is None:
        return None
    chay_ma = b.issue_type != "spike"
    lenh = lenh_bat_buoc(da.giao.lenh_kiem_mac_dinh, b.design, da.lenh_cho_phep) if buoc == "code" and chay_ma else []
    if buoc == "code" and chay_ma and not lenh:
        return None                          # không có lệnh bắt buộc thì kiểm lại không bao giờ đạt — không giao
    tieu_chi = tach_tieu_chi(b.acceptance_criteria)
    phien_ban, than = nap_vai(VAI[buoc])
    l4 = thu_lop_4(ds, b, theo_id, buoc=buoc, kho_git=kho_git, nhanh_chinh=da.nhanh_chinh,
                   commit_code=cha if buoc == "qc" else None)
    try:
        goi = dung_goi(DauVaoGoi(doc_tai_lieu(kho_git, da.nhanh_chinh, da.giao.tai_lieu_du_an),
                                (VAI[buoc], phien_ban, than), b, buoc, tuple(tieu_chi), tuple(lenh), l4,
                                thu_lop_5(b, theo_id, du_an=da.ten, vai=VAI[buoc], nho_lai=p4c.nho_lai),
                                luong_lien_quan(p4c.gitnexus, da, b),
                                de_nghi=huong_dan(doc_cai_dat(db, da.ten)[0], buoc=buoc) if db is not None else ""))
        return DeXuatPhieu(
            du_an=da.ten, bead_id=b.id, tieu_de=b.title[:300], buoc=buoc, vai=VAI[buoc],
            repo=Repo(kho=f"~/tram/kho/{da.ten}", nhanh=f"tram/{b.id}", cha=cha, nhanh_chinh=da.nhanh_chinh),
            goi_ngu_canh=goi, ngan_sach=ngan_sach_phieu(buoc, da.giao.ngan_sach), lenh_kiem=lenh,
            lenh_cho_phep=list(da.lenh_cho_phep) if chay_ma else [], can_lenh_kiem=buoc == "code" and chay_ma,
            can_moi_truong_kiem=chay_ma, tieu_chi=tieu_chi,
            khoa_chong_trung=khoa_chong_trung(da.ten, cha, b.id, buoc, phien_ban, phien_ban_quyen(VAI[buoc])))
    except (ValidationError, GoiQuaLon):
        return None
