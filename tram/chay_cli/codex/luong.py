"""Đọc stream `codex exec --json` của một lần chạy (spec 3 §7.2, §7.8) — bộ chuẩn hoá riêng của Codex, không dùng
parser của Claude. HÌNH DẠNG CHƯA XÁC MINH (chờ spike S5); theo hiểu biết hiện tại các sự kiện là: `thread.started`,
`turn.started`, `item.started|updated|completed {item: {type: agent_message | reasoning | command_execution | …}}`,
`turn.completed {usage: {input_tokens, cached_input_tokens, output_tokens}}`, `turn.failed {error: {message}}`,
`error {message}`. Trường thiếu/sai → bỏ qua (đếm 0), không đoán."""
from tram.chay_cli.codex.han_muc import MAU_CHUA_DANG_NHAP, thong_diep_loi
from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.nguon import NguonHanMuc


def _so(usage: dict, khoa: str) -> int:
    x = usage.get(khoa)
    return x if isinstance(x, int) and not isinstance(x, bool) and x > 0 else 0


class DocLuongCodex:
    def __init__(self, nguon: NguonHanMuc):
        self.nguon = nguon
        self.co_assistant = self.het_han_muc = self.chua_dang_nhap = False
        self.token_vao = self.token_cache_doc = self.token_ra = 0

    def nap(self, dong: dict) -> None:
        loai, item = dong.get("type"), dong.get("item")
        if loai == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            self.co_assistant = True
        elif loai == "turn.completed" and isinstance(dong.get("usage"), dict):
            u = dong["usage"]
            cache = _so(u, "cached_input_tokens")
            self.token_vao += max(_so(u, "input_tokens") - cache, 0)   # input_tokens của Codex GỒM phần cache
            self.token_cache_doc += cache
            self.token_ra += _so(u, "output_tokens")
        loi = thong_diep_loi(dong)
        if loi and MAU_CHUA_DANG_NHAP.search(loi):
            self.chua_dang_nhap = True
        if self.nguon.het_han_muc(dong):
            self.het_han_muc = True

    def ket_qua(self, *, ma_thoat: int | None, bi_dung: bool, thoi_gian_ms: int, digest_log: str) -> KetQuaChay:
        return KetQuaChay(ma_thoat=ma_thoat, co_assistant=self.co_assistant, het_han_muc=self.het_han_muc,
                          chua_dang_nhap=self.chua_dang_nhap, bi_dung=bi_dung, token_vao=self.token_vao,
                          token_ra=self.token_ra, token_cache_doc=self.token_cache_doc, thoi_gian_ms=thoi_gian_ms,
                          digest_log=digest_log)
