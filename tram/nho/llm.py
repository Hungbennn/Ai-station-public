"""Gọi Claude trả JSON theo schema, có guardrail + thử lại tối đa 3 lần như 1a (spec 1b §6.2 bước 1, §9.4).

Model `claude-haiku-5-5` (skill claude-api, 13/10/2026: $0.10/$0.50 mỗi triệu token khi prompt ≤ 100K; thinking
thích ứng bật sẵn, effort mặc định `medium`; không có fallback phía server khi bị từ chối)."""
import json
import time
from collections.abc import Callable
from dataclasses import dataclass

from tram.llm import han_goi

MO_HINH_NHO = "claude-haiku-5-5"
SO_LAN_THU = 3


class LoiLLMNho(RuntimeError):
    """Hết lượt thử vẫn sai schema/luật, bị cắt, hoặc model từ chối. Lỗi mạng/API KHÔNG bọc thành lỗi này."""


@dataclass(frozen=True)
class KetQuaLLM:
    du_lieu: dict
    token_vao: int
    token_ra: int
    so_lan: int
    thoi_gian_ms: int


def _goi(client, he_thong: str, messages: list, schema: dict, max_tokens: int):
    return han_goi.goi_trong_han(lambda: client.messages.create(            # bs-2bd.1.1: hạn tổng
        model=MO_HINH_NHO, max_tokens=max_tokens,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
        system=[{"type": "text", "text": he_thong, "cache_control": {"type": "ephemeral"}}],
        messages=messages))


def goi_json(client, *, he_thong: str, noi_dung: str, schema: dict, kiem: Callable[[dict], list[str]],
             max_tokens: int = 8000) -> KetQuaLLM:
    """`kiem(du_lieu)` trả danh sách lỗi ngữ nghĩa (rỗng = đạt). Lỗi → gửi lại kèm lỗi, tối đa SO_LAN_THU lần."""
    messages: list = [{"role": "user", "content": noi_dung}]
    vao = ra = 0
    bat_dau = time.monotonic()
    loi: list[str] = []
    for lan in range(1, SO_LAN_THU + 1):
        resp = _goi(client, he_thong, list(messages), schema, max_tokens)   # bản chụp mỗi lần
        vao += resp.usage.input_tokens
        ra += resp.usage.output_tokens
        if resp.stop_reason == "refusal":
            raise LoiLLMNho("Model từ chối (refusal)")
        van_ban = next((b.text for b in resp.content if b.type == "text"), "")
        try:
            du_lieu = json.loads(van_ban)
            loi = kiem(du_lieu) if isinstance(du_lieu, dict) else ["Đầu ra phải là một đối tượng JSON"]
        except ValueError as e:
            du_lieu, loi = None, [f"JSON hỏng: {e}"]
        if resp.stop_reason == "max_tokens":
            loi = ["Bị cắt vì max_tokens — trả lời ngắn hơn"]
        if not loi:
            return KetQuaLLM(du_lieu, vao, ra, lan, int((time.monotonic() - bat_dau) * 1000))
        messages += [
            {"role": "assistant", "content": resp.content},
            {"role": "user", "content": "Kết quả trước chưa đạt kiểm tra:\n- " + "\n- ".join(loi)
             + "\nHãy trả lại JSON đã sửa, giữ đúng schema."},
        ]
    raise LoiLLMNho(f"Hết {SO_LAN_THU} lượt vẫn lỗi: {loi[:3]}")
