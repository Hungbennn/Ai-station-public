"""Đọc stream JSON của `claude -p --output-format stream-json --verbose` từng dòng (spec 3 §7.8): hạn mức (qua
`NguonHanMuc`), hết hạn mức, chưa đăng nhập, có thông điệp `assistant` không, token, mô hình. CHỜ S1/S4 — dạng
dòng theo tài liệu Agent SDK, chưa xác minh khi chạy thật; dòng lạ/không phải JSON bị bỏ qua, không làm hỏng lần chạy.

Một lượt `assistant` có thể ra nhiều dòng cùng `message.id`, mỗi dòng mang đủ `usage` → đếm theo `id` (lấy số lớn
nhất), không cộng dồn từng dòng. Có dòng `result` thì lấy `usage` tổng của nó."""
import json
from collections.abc import Callable
from datetime import datetime, timezone

from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.log_claude import gop_han_muc
from tram.han_muc.mo_hinh import HanMuc
from tram.han_muc.nguon import NguonHanMuc

TOKEN = (("token_vao", "input_tokens"), ("token_ra", "output_tokens"),
         ("token_cache_doc", "cache_read_input_tokens"), ("token_cache_ghi", "cache_creation_input_tokens"))


def _so(x: object) -> int:
    return int(x) if isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0 else 0


class DocStream:
    def __init__(self, nguon: NguonHanMuc, *, khe_id: str,
                 dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
                 khi_han_muc: Callable[[HanMuc], None] | None = None, tran_token_ra: int | None = None,
                 khi_vuot: Callable[[], None] | None = None):
        self.nguon, self.khe_id, self.dong_ho = nguon, khe_id, dong_ho
        self.khi_han_muc, self.tran_token_ra, self.khi_vuot = khi_han_muc, tran_token_ra, khi_vuot
        self.co_assistant = self.het_han_muc = self.chua_dang_nhap = self.vuot_token = False
        self.han_muc: HanMuc | None = None
        self.reset_luc: str | None = None
        self.mo_hinh: str | None = None
        self._theo_id: dict[str, dict] = {}
        self._tong: dict | None = None
        self._models: set[str] = set()

    def tokens(self) -> dict[str, int]:
        if self._tong is not None:
            return {k: _so(self._tong.get(g)) for k, g in TOKEN}
        return {k: sum(_so(u.get(g)) for u in self._theo_id.values()) for k, g in TOKEN}

    def _assistant(self, d: dict) -> None:
        m = d.get("message") if isinstance(d.get("message"), dict) else {}
        if not d.get("error"):
            self.co_assistant = True
        self.mo_hinh = self.mo_hinh or (m.get("model") if isinstance(m.get("model"), str) else None)
        self._ghi_model(m.get("model"))
        u = m.get("usage") if isinstance(m.get("usage"), dict) else {}
        k = str(m.get("id") or len(self._theo_id))
        cu = self._theo_id.get(k, {})
        self._theo_id[k] = {g: max(_so(cu.get(g)), _so(u.get(g))) for _, g in TOKEN}

    def _ghi_model(self, model):
        if isinstance(model, str):
            self._models.add(model)
        else:
            self._models.add("")

    def an(self, raw: str) -> None:
        try:
            d = json.loads(raw)
        except ValueError:
            return
        if not isinstance(d, dict):
            return
        if self.nguon.het_han_muc(d):
            self.het_han_muc = True
            self.reset_luc = self.reset_luc or getattr(self.nguon, "reset_luc", lambda _: None)(d)
        if getattr(self.nguon, "chua_dang_nhap", lambda _: False)(d):
            self.chua_dang_nhap = True
        if (hm := self.nguon.doc_dong(d, khe_id=self.khe_id, bay_gio=self.dong_ho())) is not None:
            self.han_muc = gop_han_muc(self.han_muc, hm)
            if self.khi_han_muc:
                self.khi_han_muc(self.han_muc)
        loai = d.get("type")
        if loai == "system" and d.get("subtype") == "init" and isinstance(d.get("model"), str):
            self.mo_hinh = d["model"]
            self._ghi_model(d["model"])
        elif loai == "assistant":
            self._assistant(d)
        elif loai == "result" and isinstance(d.get("usage"), dict):
            self._tong = d["usage"]
        if self.tran_token_ra is not None and not self.vuot_token and self.tokens()["token_ra"] > self.tran_token_ra:
            self.vuot_token = True
            if self.khi_vuot:
                self.khi_vuot()

    def ket_qua(self, *, ma_thoat: int | None, bi_dung: bool, thoi_gian_ms: int, digest_log: str) -> KetQuaChay:
        return KetQuaChay(ma_thoat=ma_thoat, co_assistant=self.co_assistant, het_han_muc=self.het_han_muc,
                          chua_dang_nhap=self.chua_dang_nhap, bi_dung=bi_dung, mo_hinh=self.mo_hinh,
                          thoi_gian_ms=thoi_gian_ms, digest_log=digest_log, reset_luc=self.reset_luc,
                          model_lech=len(self._models) != 1 or "" in self._models, **self.tokens())
