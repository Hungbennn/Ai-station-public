"""Bản giả cho test memory 1b — CHỈ DÙNG TRONG TEST (spec 1b §16.1). Mã thật không bao giờ lùi về vector giả (M3)."""
import hashlib
import json
import math
import random
from types import SimpleNamespace as NS

from tram.nho.embed import LoiEmbedder


def _chuan(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


class EmbedderGia:
    """Vector tất định từ băm văn bản (gần như trực giao nhau); `vector` cho phép đặt tay để điều khiển cosine.
    `loi_kiem=True` → kiem() lỗi; `loi_tu_lan=k` → lần embed thứ k (đếm từ 1) trở đi lỗi."""

    def __init__(self, so_chieu=16, *, mo_hinh="gia@1", vector=None, loi_kiem=False, loi_tu_lan=None):
        self.so_chieu, self._mo_hinh, self.vector = so_chieu, mo_hinh, dict(vector or {})
        self.loi_kiem, self.loi_tu_lan, self.goi = loi_kiem, loi_tu_lan, []

    @property
    def mo_hinh(self) -> str:
        return self._mo_hinh

    def kiem(self) -> str:
        if self.loi_kiem:
            raise LoiEmbedder("Ollama tắt (giả)")
        return self._mo_hinh

    def embed(self, van_ban):
        self.goi.append(list(van_ban))
        if self.loi_tu_lan is not None and len(self.goi) >= self.loi_tu_lan:
            raise LoiEmbedder("embed lỗi (giả)")
        return [_chuan(self.vector[t]) if t in self.vector else self.ngau_nhien(t) for t in van_ban]

    def ngau_nhien(self, t: str):
        r = random.Random(hashlib.sha256(t.encode()).digest())
        return _chuan([r.gauss(0, 1) for _ in range(self.so_chieu)])


def tra_loi(du_lieu, stop="end_turn", thinking=True):
    """Một phản hồi Messages API giả: có thể mở đầu bằng khối thinking (Haiku 5.5 bật thinking sẵn)."""
    van_ban = du_lieu if isinstance(du_lieu, str) else json.dumps(du_lieu, ensure_ascii=False)
    khoi = ([NS(type="thinking", thinking="", signature="s")] if thinking else []) + [NS(type="text", text=van_ban)]
    return NS(stop_reason=stop, content=khoi, usage=NS(input_tokens=100, output_tokens=20))


class ClientGia:
    """`client.messages.create(**kw)` trả lần lượt các phản hồi đã nạp; phần tử là Exception thì ném."""

    def __init__(self, *cac_tra_loi):
        self._ds, self.goi = list(cac_tra_loi), []
        self.messages = NS(create=self._create)

    def _create(self, **kw):
        self.goi.append(kw)
        x = self._ds.pop(0)
        if isinstance(x, Exception):
            raise x
        return x


def ky_uc(id, pham_vi="/du-an/x/cach-lam", *, vector, noi_dung=None, tao_luc="2026-10-01T00:00:00Z",
          quan_trong=0.5, nguon=None, mo_hinh="gia@1", **them):
    """KyUc mẫu; `vector` lấy từ EmbedderGia để cosine có nghĩa."""
    from tram.nho.mo_hinh import KyUc, la_nguon_dai_ca
    nguon = tuple(nguon or ({"loai": "dai_ca_sua", "du_an": "x", "bead_id": "x-1", "su_kien_id": 1},))
    d = dict(id=id, noi_dung=noi_dung or f"ký ức {id}", pham_vi=pham_vi, nhan=(), quan_trong=quan_trong,
             nguon=nguon, nguon_dai_ca=la_nguon_dai_ca(nguon), hieu_luc_tu=tao_luc, tao_luc=tao_luc,
             mo_hinh_embed=mo_hinh, vector=tuple(vector))
    return KyUc(**{**d, **them})
