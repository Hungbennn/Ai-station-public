"""tram-api gọi memory service (spec 1b §9.1: tram-api là một trong ba bên được đọc `tram-nho-token`).

Token đọc lười từ Keychain ở lời gọi đầu (Keychain có thể còn khoá lúc launchd bật tram-api sau khi khởi động máy)
và giữ trong bộ nhớ tiến trình; service trả 401 (token đổi do cài lại) → quên token, lần sau đọc lại."""
from collections.abc import Callable

from tram.nho.khach import LoiNhoKhach, doc_token, goi_nho

CHO_DOC = 10.0          # giây — danh sách ký ức
CHO_GHI = 60.0          # giây — /ghi có thể gọi Claude để gộp


class KhachNho:
    def __init__(self, *, doc: Callable[[], str | None] = doc_token, goi: Callable[..., dict] = goi_nho):
        self._doc, self._goi, self._token = doc, goi, None

    def goi(self, duong: str, than: dict, *, thoi_gian_cho: float = CHO_DOC) -> dict:
        if self._token is None:
            self._token = self._doc()
        if not self._token:
            self._token = None
            raise LoiNhoKhach("Chưa có tram-nho-token — memory service chưa cài (tram chu cai-dat --nho)")
        try:
            return self._goi(duong, than, token=self._token, thoi_gian_cho=thoi_gian_cho)
        except LoiNhoKhach as e:
            if e.ma == 401:
                self._token = None
            raise
