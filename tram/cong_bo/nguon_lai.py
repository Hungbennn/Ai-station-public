"""D4: nguồn theo máy đã xác thực; không fallback nguồn hoặc đổi trạng thái giữa request."""
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam


class NguonLai:
    ten = "lai"

    def __init__(self, kho_tho):
        self.kho_tho = dict(kho_tho)
        self.local = NguonKhoTho(self.kho_tho)
        self.remote = NguonRefTam()

    def lay(self, kho, *, may_id, du_an, ref_tam, giao_id, timeout):
        nguon = self.local if may_id in self.kho_tho else self.remote
        return nguon.lay(kho, may_id=may_id, du_an=du_an, ref_tam=ref_tam, giao_id=giao_id, timeout=timeout)

    def don_cu(self, kho, *, bead_id, luot, timeout):
        # Dọn ref remote cũ cả khi lượt mới chạy B; don_cu chỉ xoá ref cũ bằng CAS.
        return self.remote.don_cu(kho, bead_id=bead_id, luot=luot, timeout=timeout)
