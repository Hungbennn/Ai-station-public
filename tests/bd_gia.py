"""Bd giả lập trong bộ nhớ cho test lát 2a — không chạy `bd` thật."""
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from tram.beads.bd import KhongThayBead, LoiBd
from tram.beads.mo_hinh import Bead, PhuThuoc

GOC = datetime(2026, 10, 13, 2, 0, tzinfo=timezone.utc)


class BdGia:
    def __init__(self, beads=(), *, ra_loi_truoc=None, ra_loi_sau=None, tien_to="hr", actor="tram/giao-viec"):
        self.beads: dict[str, Bead] = {b.id: b for b in beads}
        self.actor = actor
        self.goi: list[tuple] = []
        self._truoc, self._sau = dict(ra_loi_truoc or {}), dict(ra_loi_sau or {})
        self._dem: Counter = Counter()
        self._nhip = 0
        self._tien_to = tien_to

    def _bat_dau(self, ten: str) -> None:
        self._dem[ten] += 1
        if self._truoc.get(ten) == self._dem[ten]:
            raise LoiBd(f"giả lập lỗi trước khi {ten}")

    def _ket_thuc(self, ten: str, *args) -> None:
        self.goi.append((ten, *args))
        if self._sau.get(ten) == self._dem[ten]:
            raise LoiBd(f"giả lập lỗi sau khi {ten}")

    def _luc_moi(self) -> str:
        self._nhip += 1
        return (GOC + timedelta(seconds=self._nhip)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def so_lan(self, ten: str) -> int:
        return sum(1 for g in self.goi if g[0] == ten)

    def tat_ca(self) -> list[Bead]:
        self._bat_dau("tat_ca")
        self._ket_thuc("tat_ca")
        return list(self.beads.values())

    def mot(self, bead_id: str) -> Bead:
        if bead_id not in self.beads:
            raise KhongThayBead(f"Không thấy bead {bead_id}")   # như Bd.mot thật (Task 6) → 404
        return self.beads[bead_id]

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None) -> None:
        self._bat_dau("cap_nhat_nhan")
        b = self.beads[bead_id]
        nhan = [n for n in b.labels if n not in bo] + [n for n in them if n not in b.labels]
        notes = b.notes
        if ghi_chu:
            notes = f"{notes}\n{ghi_chu}" if notes else ghi_chu
        self.beads[bead_id] = replace(b, labels=tuple(nhan), notes=notes, updated_at=self._luc_moi())
        self._ket_thuc("cap_nhat_nhan", bead_id, tuple(them), tuple(bo), ghi_chu)

    def tao(self, tieu_de, *, loai, mo_ta, nhan=(), uu_tien=None, nghiem_thu=None, cha=None) -> str:
        self._bat_dau("tao")
        moi = f"{self._tien_to}-d{len(self.beads) + 1}"
        them = {}
        if cha:                                    # như bd: id con `<cha>.<n>` + phụ thuộc parent-child
            moi = f"{cha}.{sum(1 for b in self.beads.values() if b.parent == cha) + 1}"
            them = {"parent": cha, "dependencies": [{"issue_id": moi, "depends_on_id": cha, "type": "parent-child"}]}
        self.beads[moi] = Bead.tu_json({"id": moi, "title": tieu_de, "description": mo_ta, "issue_type": loai,
                                        "status": "open", "labels": list(nhan), "updated_at": self._luc_moi(),
                                        "priority": uu_tien, "acceptance_criteria": nghiem_thu, **them})
        self._ket_thuc("tao", tieu_de, loai, mo_ta, tuple(nhan))
        return moi

    def dong(self, bead_id, ly_do) -> None:
        self._bat_dau("dong")
        self.beads[bead_id] = replace(self.beads[bead_id], status="closed", close_reason=ly_do,
                                      updated_at=self._luc_moi())
        self._ket_thuc("dong", bead_id, ly_do)

    def them_phu_thuoc(self, bead_id, phu_thuoc_vao) -> None:
        self._bat_dau("them_phu_thuoc")
        b = self.beads[bead_id]
        self.beads[bead_id] = replace(b, phu_thuoc=b.phu_thuoc + (PhuThuoc(phu_thuoc_vao, "blocks"),),
                                      updated_at=self._luc_moi())
        self._ket_thuc("them_phu_thuoc", bead_id, phu_thuoc_vao)

    def san_sang(self) -> set[str]:
        """Như `bd ready`: `open`, mọi phụ thuộc `blocks` đã đóng (thiếu trong kho → coi như chặn)."""
        self._bat_dau("san_sang")
        self._ket_thuc("san_sang")
        return {b.id for b in self.beads.values() if b.status == "open" and all(
            (d := self.beads.get(p.depends_on_id)) is not None and d.status == "closed"
            for p in b.phu_thuoc if p.loai == "blocks")}

    def nhan_viec(self, bead_id) -> None:
        self._bat_dau("nhan_viec")
        b = self.beads[bead_id]
        if b.assignee or b.status != "open":
            raise LoiBd(f"issue already claimed by {b.assignee or '?'}")
        self.beads[bead_id] = replace(b, status="in_progress", assignee=self.actor, updated_at=self._luc_moi())
        self._ket_thuc("nhan_viec", bead_id)
