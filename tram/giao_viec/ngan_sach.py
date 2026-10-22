"""Ngân sách (spec 4 §8). Phần 3 thực thi ngân sách MỘT phiếu và quyết toán (kể cả khi thiếu `chay.xong`);
phần 4 đặt giá trị phiếu và giữ ngân sách THỰC THI của bead theo chu kỳ.

Chu kỳ bắt đầu ở lần giao đầu, bắt đầu lại ở mỗi `ngan_sach.chu_ky_moi` (tick ghi sau `escalation.dong`,
`cot.tra_ve` — #16). Đã dùng trong chu kỳ: vòng = số `qc.ket_qua` `tra_ve`; lần chạy và phút = quyết toán của
phiếu đã kết thúc, phần GIỮ TRƯỚC (`giao.nhan.ngan_sach`) của phiếu chưa quyết toán."""
from dataclasses import dataclass
from datetime import datetime

from tram.cau_hinh.du_an_giao import NganSachBead, NganSachGiao
from tram.giao_viec.su_kien import SK, ghi_mot_lan, moi_nhat
from tram.phieu.cong_viec import doc_quyet_toan
from tram.phieu.kho import KhoPhieu
from tram.phieu.mo_hinh import NganSach


@dataclass(frozen=True)
class DaDung:
    vong_qc: int
    lan_chay: int
    phut: int


def ngan_sach_phieu(buoc: str, cau_hinh: NganSachGiao) -> NganSach:
    m = cau_hinh.code if buoc == "code" else cau_hinh.qc       # `spec` (4b) dùng mức của `qc`
    return NganSach(so_lan_chay=m.so_lan_chay, phut=m.phut, token_ra=m.token_ra)


def bat_dau_chu_ky(ds: list[SK]) -> int:
    s = moi_nhat(ds, "ngan_sach.chu_ky_moi")
    return s.id if s else 0


def da_dung(kho: KhoPhieu, ds: list[SK]) -> DaDung:
    tu = bat_dau_chu_ky(ds)
    vong = sum(1 for s in ds if s.id > tu and s.loai == "qc.ket_qua" and s.du_lieu["ket_luan"] == "tra_ve")
    lan = phut = 0
    for s in ds:
        if s.id > tu and s.loai == "giao.nhan":
            qt = doc_quyet_toan(kho, s.du_lieu["giao_id"]) or {"lan_chay": s.du_lieu["ngan_sach"]["so_lan_chay"],
                                                                "phut": s.du_lieu["ngan_sach"]["phut"]}
            lan, phut = lan + qt["lan_chay"], phut + qt["phut"]
    return DaDung(vong, lan, phut)


def du_mot_phieu(kho: KhoPhieu, ds: list[SK], ns_phieu: NganSach, ns_bead: NganSachBead) -> bool:
    """Hàm DUY NHẤT dùng cho chọn việc (§5.1 điều kiện 6) và vòng tick (§10 bước 1)."""
    d = da_dung(kho, ds)
    return (ns_bead.lan_chay - d.lan_chay >= ns_phieu.so_lan_chay and ns_bead.phut - d.phut >= ns_phieu.phut
            and d.vong_qc < ns_bead.vong_qc)


def mo_chu_ky(kho: KhoPhieu, du_an: str, bead_id: str, nguon_su_kien_id: int, luc: datetime) -> bool:
    """`ngan_sach.chu_ky_moi {bead_id, nguon_su_kien_id}` — phát lại cùng nguồn không mở hai lần."""
    return ghi_mot_lan(kho, du_an, "ngan_sach.chu_ky_moi", {"bead_id": bead_id, "nguon_su_kien_id": nguon_su_kien_id},
                       bead_id=bead_id, luc=luc, khoa=("bead_id", "nguon_su_kien_id")) is not None
