"""Gửi Telegram bằng urllib (spec 2 §6, §8 — không SDK). Token chỉ đọc từ biến môi trường / Keychain do Đại ca đặt."""
import http.client
import json
import os
import urllib.error
import urllib.request

from tram.keychain import doc_muc

KEYCHAIN_TELEGRAM = "tram-telegram-bot-token"
BIEN_MOI_TRUONG = "TRAM_TELEGRAM_BOT_TOKEN"
API = "https://api.telegram.org/bot{token}/sendMessage"


class LoiTelegram(RuntimeError):
    pass


def doc_token(*, chay=None) -> str | None:
    if os.environ.get(BIEN_MOI_TRUONG, "").strip():
        return os.environ[BIEN_MOI_TRUONG].strip()
    return doc_muc(KEYCHAIN_TELEGRAM, chay=chay)


def _che(s: str, token: str) -> str:
    return s.replace(token, "***") if token else s


def gui_telegram(token: str, chat_id: str, van_ban: str, *, mo=urllib.request.urlopen,
                 thoi_gian_cho: float = 10.0) -> None:
    yc = urllib.request.Request(
        API.format(token=token), method="POST", headers={"Content-Type": "application/json"},
        data=json.dumps({"chat_id": chat_id, "text": van_ban, "disable_web_page_preview": True}).encode())
    try:
        with mo(yc, timeout=thoi_gian_cho) as r:
            kq = json.loads(r.read() or b"{}")
    except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
        raise LoiTelegram(_che(f"Gửi Telegram lỗi: {e}", token)) from None    # không xâu chuỗi: URL chứa token
    if not kq.get("ok"):
        raise LoiTelegram(_che(f"Telegram từ chối: {str(kq.get('description', ''))[:200]}", token))
