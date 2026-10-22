"""Embedder bge-m3 qua Ollama 127.0.0.1:11434 bằng urllib (spec 1b §6.2 bước 4, §9.4).

Lỗi → LoiEmbedder, KHÔNG BAO GIỜ lùi về vector giả/băm (M3). Embedder giả chỉ có trong tests/."""
import http.client
import json
import urllib.error
import urllib.request
from typing import Protocol

from tram.nho.mo_hinh import SO_CHIEU, LoiVector, chuan_hoa_l2

OLLAMA = "http://127.0.0.1:11434"     # chỉ localhost — không có tuỳ chọn đổi host
TEN_MO_HINH = "bge-m3"


class LoiEmbedder(RuntimeError):
    pass


class Embedder(Protocol):
    so_chieu: int

    @property
    def mo_hinh(self) -> str: ...            # "<tên>@<digest>" — ghi vào mỗi bản ghi

    def kiem(self) -> str: ...                # gọi thử; trả mo_hinh; lỗi → LoiEmbedder

    def embed(self, van_ban: list[str]) -> list[tuple[float, ...]]: ...   # đã chuẩn hoá L2


class OllamaEmbedder:
    def __init__(self, *, ten: str = TEN_MO_HINH, so_chieu: int = SO_CHIEU, mo=urllib.request.urlopen,
                 thoi_gian_cho: float = 30.0):
        self.ten, self.so_chieu, self._mo, self._cho = ten, so_chieu, mo, thoi_gian_cho
        self._mo_hinh: str | None = None

    def _goi(self, duong: str, than: dict | None = None) -> dict:
        yc = urllib.request.Request(
            OLLAMA + duong, method="GET" if than is None else "POST", headers={"Content-Type": "application/json"},
            data=None if than is None else json.dumps(than).encode())
        try:
            with self._mo(yc, timeout=self._cho) as r:
                kq = json.loads(r.read() or b"{}")
        except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
            raise LoiEmbedder(f"Ollama {duong} lỗi: {e}") from None
        if not isinstance(kq, dict):
            raise LoiEmbedder(f"Ollama {duong} trả JSON không phải object")
        return kq

    @property
    def mo_hinh(self) -> str:
        if self._mo_hinh is None:
            raise LoiEmbedder("Chưa kiểm embedder (gọi kiem() trước)")
        return self._mo_hinh

    def kiem(self) -> str:
        """Tên + digest model từ /api/tags — đổi bản bge-m3 thì `mo_hinh` đổi, recall lọc bản ghi cũ (M3)."""
        ds = self._goi("/api/tags").get("models")
        ds = [x for x in ds if isinstance(x, dict)] if isinstance(ds, list) else []
        m = next((x for x in ds if x.get("name") in (self.ten, f"{self.ten}:latest")), None)
        if m is None or not m.get("digest"):
            raise LoiEmbedder(f"Ollama chưa có model {self.ten} (chạy: ollama pull {self.ten})")
        self._mo_hinh = f"{self.ten}@{m['digest']}"
        return self._mo_hinh

    def embed(self, van_ban: list[str]) -> list[tuple[float, ...]]:
        if not van_ban:
            return []
        ds = self._goi("/api/embed", {"model": self.ten, "input": list(van_ban)}).get("embeddings")
        if not isinstance(ds, list) or len(ds) != len(van_ban):
            raise LoiEmbedder("Ollama trả số vector khác số văn bản")
        try:
            ket = [chuan_hoa_l2([float(x) for x in v]) for v in ds]
        except (LoiVector, TypeError, ValueError) as e:
            raise LoiEmbedder(f"Vector hỏng: {e}") from None
        if any(len(v) != self.so_chieu for v in ket):
            raise LoiEmbedder(f"Số chiều khác {self.so_chieu}")
        return ket
