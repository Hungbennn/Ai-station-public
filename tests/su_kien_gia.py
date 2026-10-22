"""Ghi sự kiện mẫu của phần 3/phần 4 vào kho phiếu tạm (CHỈ DÙNG TRONG TEST)."""
from kho_phieu_gia import LUC
from tram.giao_viec.su_kien import su_kien_bead

DA = "hr-codex"


def sk(kho, loai, du_lieu, bead_id="hr-1", du_an=DA) -> int:
    with kho.giao_dich():
        return kho.ghi_su_kien(du_an, loai, du_lieu, luc=LUC, bead_id=bead_id)


def nhan(kho, giao_id, luot, buoc="code", bead_id="hr-1", khe_id="B/claude-1", ngan_sach=None):
    return sk(kho, "giao.nhan", {"giao_id": giao_id, "luot": luot, "khe_id": khe_id, "bead_id": bead_id,
                                 "buoc": buoc, "ngan_sach": ngan_sach or {"so_lan_chay": 3, "phut": 90,
                                                                          "token_ra": 200000}}, bead_id)


def cong_bo(kho, luot, commit, bead_id="hr-1"):
    return sk(kho, "giao.cong_bo", {"bead_id": bead_id, "luot": luot, "commit": commit,
                                    "ref": f"tram/{bead_id}"}, bead_id)


def ket_thuc(kho, giao_id, luot, ket_thuc="xong", ly_do=None, commit=None, buoc="code", bead_id="hr-1"):
    return sk(kho, "giao.ket_thuc", {"giao_id": giao_id, "luot": luot, "buoc": buoc, "ket_thuc": ket_thuc,
                                     "ly_do": ly_do, "commit": commit, "loi": []}, bead_id)


def kiem(kho, giao_id, commit, dat=True, digest="sha256:d", luot=1, bead_id="hr-1"):
    return sk(kho, "kiem.lai", {"giao_id": giao_id, "bead_id": bead_id, "luot": luot, "commit": commit,
                                "digest_tieu_chi": digest, "dat": dat, "ket_qua": [], "digest_log": [],
                                "cham_cam": [], "nguon_kiem": "uq"}, bead_id)


def qc(kho, giao_id, commit_code, commit_qc, ket_luan="dat", bead_id="hr-1", phat_hien=()):
    return sk(kho, "qc.ket_qua", {"giao_id": giao_id, "bead_id": bead_id, "commit_code": commit_code,
                                  "commit_qc": commit_qc, "ket_luan": ket_luan, "phat_hien": list(phat_hien)},
              bead_id)


def ds(kho, bead_id="hr-1"):
    return su_kien_bead(kho, DA, bead_id)
