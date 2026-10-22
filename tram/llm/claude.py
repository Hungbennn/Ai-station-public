import os
import time
from collections.abc import Callable
from dataclasses import dataclass

import anthropic
from pydantic import BaseModel, ValidationError

from tram.cham_cot.ket_qua import SCHEMA, KetQuaCham, loi_ngu_nghia
from tram.keychain import doc_muc
from tram.llm import han_goi

MO_HINH = "claude-sonnet-5-5"
SO_LAN_THU = 3
KEYCHAIN_DICH_VU = "tram-anthropic-api-key"


class LoiChamLLM(RuntimeError):
    pass


@dataclass(frozen=True)
class DauRa:
    """Kiểu đầu ra của một lần gọi: mô hình pydantic, JSON schema gửi API, kiểm ngữ nghĩa, trần token, effort."""
    mau: type[BaseModel]
    schema: dict
    kiem: Callable[[BaseModel], list[str]]
    max_tokens: int = 4000
    effort: str = "medium"


DAU_RA_CHAM = DauRa(KetQuaCham, SCHEMA, loi_ngu_nghia)  # chấm đầy đủ (spec 0+1a §5.3)


@dataclass(frozen=True)
class KetQuaGoi:
    ket_qua: BaseModel
    token_vao: int
    token_ra: int
    token_cache_doc: int
    so_lan: int
    thoi_gian_ms: int


def tao_client() -> anthropic.Anthropic:
    """bs-2bd.1.1: SDK không tự thử lại (không ngủ theo retry-after); hạn tổng mỗi lời gọi ở `han_goi`."""
    han = {"timeout": han_goi.HAN_GOI_GIAY, "max_retries": 0}
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic(**han)
    khoa = doc_muc(KEYCHAIN_DICH_VU)
    if khoa is None:
        raise LoiChamLLM(f"Chưa có API key: đặt ANTHROPIC_API_KEY hoặc thêm vào Keychain dịch vụ {KEYCHAIN_DICH_VU}")
    return anthropic.Anthropic(api_key=khoa, **han)


def _goi(client, he_thong: str, messages: list, dau_ra: DauRa):
    return han_goi.goi_trong_han(lambda: client.beta.messages.create(
        model=MO_HINH,
        max_tokens=dau_ra.max_tokens,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": dau_ra.effort, "format": {"type": "json_schema", "schema": dau_ra.schema}},
        system=[{"type": "text", "text": he_thong, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    ))


def cham_bang_llm(client, he_thong: str, noi_dung: str, dau_ra: DauRa = DAU_RA_CHAM) -> KetQuaGoi:
    """Gọi + guardrail (§5.3): parse, kiểm schema và ngữ nghĩa; trượt → gửi lỗi kèm đầu ra cũ, tối đa SO_LAN_THU."""
    messages: list = [{"role": "user", "content": noi_dung}]
    vao = ra = cache = 0
    bat_dau = time.monotonic()
    loi: list[str] = []
    for lan in range(1, SO_LAN_THU + 1):
        resp = _goi(client, he_thong, messages, dau_ra)
        vao += resp.usage.input_tokens
        ra += resp.usage.output_tokens
        cache += resp.usage.cache_read_input_tokens or 0
        if resp.stop_reason == "refusal":
            raise LoiChamLLM("Model từ chối (refusal)")
        van_ban = next((b.text for b in resp.content if b.type == "text"), "")
        try:
            kq = dau_ra.mau.model_validate_json(van_ban)
            loi = dau_ra.kiem(kq)
        except ValidationError as e:
            loi = [f"JSON không đúng schema: {e.errors()[:3]}"]
        if resp.stop_reason == "max_tokens":
            loi = ["Bị cắt vì max_tokens — trả lời ngắn hơn"]
        if not loi:
            return KetQuaGoi(kq, vao, ra, cache, lan, int((time.monotonic() - bat_dau) * 1000))
        messages += [
            {"role": "assistant", "content": resp.content},
            {"role": "user", "content": "Kết quả trước chưa đạt kiểm tra:\n- " + "\n- ".join(loi)
             + "\nHãy trả lại JSON đã sửa, giữ đúng schema."},
        ]
    raise LoiChamLLM(f"Hết {SO_LAN_THU} lượt vẫn lỗi: {loi}")
