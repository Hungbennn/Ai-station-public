"""Bd của đề nghị GIẢ, chung kho với một `BdGia` (cùng dict `beads`) — CHỈ DÙNG TRONG TEST. Hành vi như `bd 1.2.2` đã
đo (design D-5): việc tạo không `-p` mang ưu tiên 2, nhãn `tram:agent-tao`, liên kết `discovered-from` không chặn.
`loi_sau={"tao_viec_moi": n}`: lần thứ n LÀM XONG rồi mới ném `LoiBd` (giả lập trạm tắt sau `bd create`).
`nghe(ten)`: gọi sau MỖI lệnh xong (kể cả `tat_ca`) — test đổi nút / `bat_ghi` / estop / đồng hồ giữa hai lệnh `bd`."""
from dataclasses import replace

from bd_gia import BdGia
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead, PhuThuoc


class BdDeNghiGia:
    def __init__(self, g: BdGia, *, loi_sau: dict | None = None, loi_truoc: dict | None = None):
        self.g, self.actor, self.goi = g, "tram/de-nghi", []
        self._sau, self._truoc = dict(loi_sau or {}), dict(loi_truoc or {})
        self.nghe = lambda ten: None

    def _lan(self, ten: str) -> int:
        return sum(1 for x in self.goi if x[0] == ten) + 1

    def _truoc_khi(self, ten: str) -> None:
        if self._truoc.get(ten) == self._lan(ten):
            self._truoc.pop(ten)
            raise LoiBd(f"giả lập lỗi trước khi {ten}")

    def _xong(self, ten: str, *args) -> None:
        lan = self._lan(ten)
        self.goi.append((ten, *args))
        self.nghe(ten)
        if self._sau.get(ten) == lan:
            raise LoiBd(f"giả lập lỗi sau khi {ten}")

    def tat_ca(self) -> list[Bead]:
        ds = self.g.tat_ca()
        self.nghe("tat_ca")
        return ds

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None) -> None:
        self._truoc_khi("ghi_chu")
        self.g.cap_nhat_nhan(bead_id, them=them, bo=bo, ghi_chu=ghi_chu)
        self._xong("ghi_chu", bead_id, ghi_chu)

    def tao_viec_moi(self, tieu_de, *, loai, mo_ta, tieu_chi) -> str:
        self._truoc_khi("tao_viec_moi")
        moi = f"{self.g._tien_to}-d{len(self.g.beads) + 1}"
        self.g.beads[moi] = Bead.tu_json({"id": moi, "title": tieu_de, "description": mo_ta, "issue_type": loai,
                                          "status": "open", "labels": ["tram:agent-tao"], "priority": 2,
                                          "acceptance_criteria": tieu_chi, "updated_at": self.g._luc_moi()})
        self._xong("tao_viec_moi", moi, tieu_de, loai)
        return moi

    def lien_ket_phat_hien(self, moi, goc) -> None:
        self._truoc_khi("lien_ket")
        b = self.g.beads[moi]
        if PhuThuoc(goc, "discovered-from") not in b.phu_thuoc:
            self.g.beads[moi] = replace(b, phu_thuoc=b.phu_thuoc + (PhuThuoc(goc, "discovered-from"),))
        self._xong("lien_ket", moi, goc)
