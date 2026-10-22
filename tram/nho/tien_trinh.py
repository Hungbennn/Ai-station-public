"""Tiến trình `tram nho chay` (spec 1b §9): giữ flock, một luồng nạp sự kiện mỗi 2 phút + bảo trì hằng đêm,
HTTP nội bộ + MCP `/mcp` (1b-2) chỉ nghe 127.0.0.1:7710. Ollama chưa cài (#5) → lượt nạp ghi `nho.loi_embedder`,
recall trả 503.
Không khởi động được (thiếu khoá API, kho sai số chiều…) → in lý do, thoát mã 0: launchd không bật lại vô hạn."""
import signal
import sys
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from tram.nho.bao_tri import GIO_BAO_TRI, TEP_BAO_TRI, BaoTri, bao_tri_neu_den_han  # noqa: F401 — giữ tên cũ
from tram.nho.dich_vu import DichVuNho
from tram.nho.embed import LoiEmbedder
from tram.nho.khoa import khoa_dich_vu, thu_muc_nho
from tram.nho.vong import NguCanhNho, mot_luot

HOST = "127.0.0.1"
CONG_NHO = 7710
CHU_KY_NAP_GIAY = 120
CHO_LUONG_DUNG_GIAY = 10   # launchd chờ ~20 giây rồi SIGKILL; luồng nạp là daemon, nhật ký làm tiếp được nếu bị cắt


def _log(s: str) -> None:
    print(s[:500], file=sys.stderr, flush=True)


def vong_nap(nc: NguCanhNho, dv: DichVuNho, *, dung: threading.Event, thu_muc: Path, dich: Path,
             chu_ky: float = CHU_KY_NAP_GIAY, dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
    """Lỗi một lượt không giết tiến trình: ghi log, lượt sau thử lại (mốc chỉ tiến ở sự kiện đã xong)."""
    bt = BaoTri.doc(thu_muc / TEP_BAO_TRI)
    while not dung.is_set():
        try:
            bc = mot_luot(nc)
            if bc.loi or bc.su_kien or bc.bo:
                _log(f"nạp ký ức: {bc}")
        except Exception as e:                       # noqa: BLE001 — vòng thường trực, lỗi đã ghi log
            _log(f"lượt nạp lỗi: {type(e).__name__}: {e}")
        try:
            bao_tri_neu_den_han(nc, dv, bt, dong_ho(), thu_muc=thu_muc, dich=dich)
        except Exception as e:                       # noqa: BLE001
            _log(f"bảo trì lỗi: {type(e).__name__}: {e}")
        dung.wait(chu_ky)


def tao_ngu_canh_that() -> tuple[NguCanhNho, DichVuNho] | None:
    from tram.cham_cot.prompt import nap_vai
    from tram.llm.claude import tao_client
    from tram.nho.embed import OllamaEmbedder
    from tram.nho.khach import doc_token
    from tram.nho.kho import KhoKyUc
    from tram.nho.nhat_ky import NhatKy
    from tram.nho.nho_lai import BoDemDung
    from tram.su_kien.kho import mo_kho
    token = doc_token()
    if not token:
        return None
    thu, e, client = thu_muc_nho(), OllamaEmbedder(), tao_client()
    kho = KhoKyUc(thu / "lancedb", so_chieu=e.so_chieu)
    nc = NguCanhNho(kho, e, client, mo_kho(), NhatKy(thu / "nhat-ky.db"), nap_vai("nho-tach"), nap_vai("nho-gop"),
                    vai_thang_cap=nap_vai("nho-thang-cap"))
    return nc, DichVuNho(kho, e, mo_kho, BoDemDung(), token, client=client, vai_gop=nap_vai("nho-gop"),
                         mo_nhat_ky=lambda: NhatKy(thu / "nhat-ky.db"))


def chay_dich_vu(*, cong: int = CONG_NHO, tao=tao_ngu_canh_that, chay_http=None, dich: Path | None = None,
                 tao_mcp=None) -> int:
    from tram.nho.may_chu_mcp import tao_ung_dung
    from tram.nho.ung_dung import tao_cau_hinh_mcp_that
    thu = thu_muc_nho()
    with khoa_dich_vu(thu) as duoc:
        if not duoc:
            print("memory service đang chạy ở tiến trình khác — không mở bản thứ hai (M7a).")
            return 0
        try:
            tao_ra = tao()
        except Exception as e:                       # noqa: BLE001 — LoiChamLLM, ValueError (số chiều), LoiEmbedder…
            print(f"memory service không khởi động được: {type(e).__name__}: {str(e)[:300]}")
            return 0
        if tao_ra is None:
            print("Chưa có tram-nho-token (Keychain) — memory service không chạy. Cài: tram chu cai-dat --nho")
            return 0
        nc, dv = tao_ra
        try:
            nc.embedder.kiem()                       # recall trước lượt nạp đầu cần biết model (không thì 503)
        except LoiEmbedder as e:
            _log(f"embedder chưa sẵn sàng: {e}")
        dung = threading.Event()
        luong = threading.Thread(target=vong_nap, args=(nc, dv), daemon=True, name="nap-ky-uc",
                                 kwargs={"dung": dung, "thu_muc": thu, "dich": dich or thu.parent / "sao-luu"})
        luong.start()
        if chay_http is None:
            import uvicorn
            chay_http = uvicorn.run
        # launchd dừng bằng SIGTERM; uvicorn bắt rồi phát lại bằng bộ xử lý cũ — mặc định thì chết ngay, bỏ qua
        # finally. Đổi thành KeyboardInterrupt để dừng luồng nạp, xả bộ đếm, nhả khoá rồi thoát 0.
        cu = signal.signal(signal.SIGTERM, signal.default_int_handler) if _luong_chinh() else None
        try:
            chay_http(tao_ung_dung(dv, (tao_mcp or tao_cau_hinh_mcp_that)()), host=HOST, port=cong,
                      log_level="warning", server_header=False)
        except KeyboardInterrupt:
            _log("memory service nhận tín hiệu dừng")
        finally:
            dung.set()
            luong.join(timeout=CHO_LUONG_DUNG_GIAY)
            try:
                dv.dem_dung.xa_neu_den_han(nc.kho, datetime.now(timezone.utc), ep=True)
            except Exception as e:                   # noqa: BLE001 — đang dừng, chỉ ghi log
                _log(f"xả bộ đếm dùng lỗi: {type(e).__name__}: {e}")
            if cu is not None:
                signal.signal(signal.SIGTERM, cu)
    return 0


def _luong_chinh() -> bool:
    return threading.current_thread() is threading.main_thread()
