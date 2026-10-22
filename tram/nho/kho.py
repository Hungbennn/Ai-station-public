"""Kho ký ức LanceDB — chỉ memory service mở (spec 1b §9; M7b: chỉ tram/nho/ import lancedb). Spike N1 (0.40.0):
`pham_vi IN` phải prefilter; compact_files/cleanup_old_versions cần `pylance` → dùng optimize(cleanup_older_than).
Mọi thao tác qua một RLock: recall, ghi, thống kê, dọn phiên bản được tuần tự hoá (§6.4). `khoa_gop` (1b-3): người lập
kế hoạch gộp — vòng nạp, thăng cấp, `/ghi` của Đại ca — giữ suốt từ lúc tìm ứng viên tới lúc áp dụng xong."""
import threading
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import timedelta
from pathlib import Path

import lancedb

from tram.nho.bang import BANG, COT, hang, ky_uc_tu_hang, luoc_do, sql, trong
from tram.nho.mo_hinh import SO_CHIEU, KyUc


class KhoKyUc:
    def __init__(self, thu_muc: Path, *, so_chieu: int = SO_CHIEU):
        self.khoa = threading.RLock()
        self.khoa_gop = threading.RLock()
        self._bang = lancedb.connect(thu_muc).create_table(BANG, schema=luoc_do(so_chieu), exist_ok=True)
        co = self._bang.schema.field("vector").type.list_size
        if co != so_chieu:
            raise ValueError(f"Kho lưu vector {co} chiều, embedder {so_chieu} chiều — không trộn (M3)")
        self.so_chieu = so_chieu

    def them(self, k: KyUc) -> bool:
        """Idempotent theo id: đã có (kể cả đã xoá mềm) thì bỏ qua. Trả True khi thật sự thêm."""
        if k.so_chieu != self.so_chieu:
            raise ValueError("Sai số chiều vector (M3)")
        with self.khoa:
            if self._bang.count_rows(f"id = {sql(k.id)}"):
                return False
            self._bang.add([hang(k)])
            return True

    def them_lo(self, ds: list[KyUc]) -> None:
        """Thêm hàng loạt KHÔNG kiểm trùng — chỉ cho kho đo M6 (`do_tre.sinh_kho`)."""
        with self.khoa:
            self._bang.add([hang(k) for k in ds])

    def lay(self, ids: Iterable[str]) -> dict[str, KyUc]:
        ids = list(ids)
        if not ids:
            return {}
        with self.khoa:
            ds = self._bang.search().where(f"id IN {trong(ids)}").limit(len(ids)).select(COT).to_list()
        return {h["id"]: ky_uc_tu_hang(h) for h in ds}

    def xoa_mem(self, ids: Iterable[str]) -> int:
        """Xoá mềm; bản đã xoá thì không xoá lần hai (không tạo phiên bản thừa)."""
        ids = list(ids)
        if not ids:
            return 0
        dk = f"id IN {trong(ids)} AND da_xoa = false"
        with self.khoa:
            if not self._bang.count_rows(dk):
                return 0
            return self._bang.update(where=dk, values={"da_xoa": True}).rows_updated

    def tim(self, vector: Sequence[float], tap_pham_vi: Iterable[str], *, mo_hinh: str, gioi_han: int,
            bay_gio: str | None = None) -> list[tuple[KyUc, float]]:
        """Ứng viên theo cosine, LỌC TRƯỚC: chưa xoá, đúng model (M3), `pham_vi IN` (so khớp chính xác),
        và `hieu_luc_tu <= bay_gio` khi có. Trả [(ký ức, cosine)] giảm dần."""
        tap = sorted(set(tap_pham_vi))
        if not tap:
            return []
        dk = f"da_xoa = false AND mo_hinh_embed = {sql(mo_hinh)} AND pham_vi IN {trong(tap)}"
        if bay_gio is not None:
            dk += f" AND hieu_luc_tu <= {sql(bay_gio)}"
        with self.khoa:
            ds = (self._bang.search(list(vector), vector_column_name="vector").distance_type("cosine")
                  .where(dk, prefilter=True).limit(gioi_han).select(COT + ["_distance"]).to_list())
        return [(ky_uc_tu_hang(h), 1.0 - float(h["_distance"])) for h in ds]

    def quet(self, dieu_kien: str | None = None, *, cot: Sequence[str] = COT) -> list[dict]:
        """Mọi hàng khớp, không tìm vector (thăng cấp, danh sách cho dashboard, xoá cứng). Chuỗi qua `bang.sql()`."""
        with self.khoa:
            n = self._bang.count_rows(dieu_kien)
            if not n:
                return []
            q = self._bang.search()
            return (q.where(dieu_kien) if dieu_kien else q).limit(n).select(list(cot)).to_list()

    def xoa_cung(self, ids: Iterable[str]) -> int:
        """Xoá HẲN hàng đã xoá mềm (lệnh riêng của Đại ca, chỉ khi dịch vụ dừng — spec 1b §5).
        Hàng chưa xoá mềm giữ nguyên."""
        ids = list(ids)
        if not ids:
            return 0
        dk = f"id IN {trong(ids)} AND da_xoa = true"
        with self.khoa:
            n = self._bang.count_rows(dk)
            if n:
                self._bang.delete(dk)
            return n

    def cap_nhat_dung(self, so_lan: Counter, luc: str) -> None:
        """Gom: một lệnh update cho mỗi giá trị đếm khác nhau (§7 bước 5 — ít phiên bản LanceDB)."""
        theo_dem: dict[int, list[str]] = {}
        for i, n in so_lan.items():
            theo_dem.setdefault(n, []).append(i)
        with self.khoa:
            for n, ids in sorted(theo_dem.items()):
                self._bang.update(where=f"id IN {trong(sorted(ids))}",
                                  values_sql={"so_lan_dung": f"so_lan_dung + {int(n)}", "dung_luc": sql(luc)})

    def don_dep(self, giu: timedelta = timedelta(days=1)) -> None:
        """Gộp file nhỏ + xoá phiên bản cũ hơn `giu` (thay compact_files + cleanup_old_versions — spike N1)."""
        with self.khoa:
            self._bang.optimize(cleanup_older_than=giu)

    def dem(self, dieu_kien: str | None = None) -> int:
        with self.khoa:
            return self._bang.count_rows(dieu_kien)

    def so_phien_ban(self) -> int:
        with self.khoa:
            return len(self._bang.list_versions())
