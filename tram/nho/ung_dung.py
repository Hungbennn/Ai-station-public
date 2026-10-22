"""Ứng dụng ASGI của memory service (spec 1b §9): `/mcp` → cổng xác thực → máy chủ MCP (SDK, `may_chu_mcp.py`);
đường khác → HTTP nội bộ `/nho-lai`, `/xoa` (Bearer `tram-nho-token`, 1b-1) giữ nguyên.

Trước hết kiểm `Host` cho MỌI đường (bs-2bd.1.5, chống DNS rebinding — như `tram/api/bao_mat.py`): lạ → 421.
Cổng chạy TRƯỚC SDK: không có bằng chứng hợp lệ → 401/403/503 `{loi}`, không chạm công cụ nào (M2). Hợp lệ →
`DanhTinh` đặt vào `scope["state"]["tram_danh_tinh"]`; công cụ chỉ đọc vùng cấp từ đó. Log từ chối không có bí mật."""
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass

from fastapi.concurrency import run_in_threadpool

from tram.nho.danh_tinh import TuChoi, xac_thuc

DUONG_MCP = "/mcp"
HOST_NOI_BO = frozenset({"127.0.0.1:7710", "localhost:7710"})     # = tien_trinh.HOST:CONG_NHO
KHOA_DANH_TINH = "tram_danh_tinh"


@dataclass
class CauHinhMcp:
    tra: Callable[[str], dict | None] | None      # TraPhieu (cache 30 giây); None → mọi lời gọi theo phiếu 503
    bam_ma_dai_ca: Callable[[], str | None]        # đọc mỗi lời gọi: `tram chu dat-ma-dai-ca` có hiệu lực ngay
    co_du_an: Callable[[str], bool]
    host: frozenset[str] = HOST_NOI_BO              # Host được nhận; thêm tên máy B cho đường tailnet (spike N2)


def tao_cau_hinh_mcp_that() -> CauHinhMcp:
    """Không đụng Keychain lúc khởi động: `tram-noi-bo-token` đọc ở lời gọi theo phiếu đầu tiên rồi giữ trong bộ nhớ.
    Host: localhost:7710 + `ten_may_b` (như tram-api); cấu hình hỏng → chỉ localhost (hẹp hơn, không mở thêm)."""
    from tram.api.bao_mat import host_hop_le
    from tram.api.noi_bo import doc_mot_lan
    from tram.cau_hinh.du_an import liet_ke_du_an
    from tram.nho.ma_dai_ca import doc_bam
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.nho.tien_trinh import CONG_NHO
    from tram.nho.tra_phieu import TraPhieu, doc_token_noi_bo
    try:
        host = HOST_NOI_BO | host_hop_le(nap_cau_hinh_tram(), CONG_NHO)
    except ValueError:
        print("cau-hinh.yaml hỏng — memory chỉ nhận Host localhost:7710", file=sys.stderr, flush=True)
        host = HOST_NOI_BO
    return CauHinhMcp(tra=TraPhieu(doc_mot_lan(doc_token_noi_bo)), bam_ma_dai_ca=doc_bam,
                      co_du_an=lambda ten: not ten.startswith("_") and ten in liet_ke_du_an(), host=host)


async def _tu_choi(send, ma: int, loi: str) -> None:
    than = json.dumps({"loi": loi}, ensure_ascii=False).encode()
    await send({"type": "http.response.start", "status": ma, "headers": [
        (b"content-type", b"application/json"), (b"content-length", str(len(than)).encode()),
        (b"cache-control", b"no-store")]})
    await send({"type": "http.response.body", "body": than})


class UngDungNho:
    def __init__(self, http_app, mcp_app, cfg: CauHinhMcp):
        self.http_app, self.mcp_app, self.cfg = http_app, mcp_app, cfg

    def _xac_thuc(self, headers):
        return xac_thuc(headers, tra=self.cfg.tra, bam_ma_dai_ca=self.cfg.bam_ma_dai_ca, co_du_an=self.cfg.co_du_an)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.mcp_app(scope, receive, send)       # bộ quản lý phiên của SDK chạy theo lifespan
        if scope["type"] == "http" and dict(scope["headers"]).get(b"host", b"").decode("latin-1").lower() \
                not in self.cfg.host:
            return await _tu_choi(send, 421, "Host không hợp lệ")
        if scope["type"] != "http" or scope["path"] != DUONG_MCP:
            return await self.http_app(scope, receive, send)
        try:
            dt = await run_in_threadpool(self._xac_thuc, scope["headers"])   # tra phiếu gọi tram-api (≤ 2 giây)
        except TuChoi as e:
            print(f"mcp từ chối ({e.ma}): {e}"[:300], file=sys.stderr, flush=True)
            return await _tu_choi(send, e.ma, str(e))
        await self.mcp_app({**scope, "state": {**scope.get("state", {}), KHOA_DANH_TINH: dt}}, receive, send)
