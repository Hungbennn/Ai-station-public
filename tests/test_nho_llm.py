import anthropic
import httpx2
import pytest

from nho_gia import ClientGia, EmbedderGia, tra_loi
from tram.nho.embed import LoiEmbedder
from tram.nho.llm import MO_HINH_NHO, LoiLLMNho, goi_json

SCHEMA = {"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"],
          "additionalProperties": False}


def kiem(d):
    return [] if d.get("x", 0) > 0 else ["x phải dương"]


def test_dung_ngay_lan_dau_va_tham_so_goi():
    c = ClientGia(tra_loi({"x": 2}))
    kq = goi_json(c, he_thong="HỆ", noi_dung="ND", schema=SCHEMA, kiem=kiem)
    assert kq.du_lieu == {"x": 2} and kq.so_lan == 1 and kq.token_vao == 100
    kw = c.goi[0]
    assert kw["model"] == MO_HINH_NHO == "claude-haiku-5-5"
    assert kw["output_config"] == {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"} and kw["messages"][0]["content"] == "ND"
    assert "thinking" not in kw and "temperature" not in kw


def test_sai_thi_gui_loi_va_thu_lai():
    c = ClientGia(tra_loi({"x": 0}), tra_loi("không json"), tra_loi({"x": 1}))
    kq = goi_json(c, he_thong="H", noi_dung="N", schema=SCHEMA, kiem=kiem)
    assert kq.so_lan == 3 and kq.token_vao == 300
    cuoi = c.goi[2]["messages"]
    assert [m["role"] for m in cuoi] == ["user", "assistant", "user", "assistant", "user"]
    assert "x phải dương" in cuoi[2]["content"] and "JSON hỏng" in cuoi[4]["content"]


@pytest.mark.parametrize("cac", [
    [tra_loi({"x": 0})] * 3, [tra_loi({"x": 1}, stop="max_tokens")] * 3, [tra_loi([1, 2])] * 3,
    [tra_loi({"x": 1}, stop="refusal")]])
def test_het_luot_hoac_tu_choi_thi_loi_llm(cac):
    with pytest.raises(LoiLLMNho):
        goi_json(ClientGia(*cac), he_thong="H", noi_dung="N", schema=SCHEMA, kiem=kiem)


def test_loi_api_khong_bi_nuot():
    loi = anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com"))
    with pytest.raises(anthropic.APIConnectionError):
        goi_json(ClientGia(loi), he_thong="H", noi_dung="N", schema=SCHEMA, kiem=kiem)


def test_embedder_gia_tat_dinh_va_loi():
    e = EmbedderGia(vector={"a": [3, 4] + [0] * 14})
    v1, v2 = e.embed(["b", "b"])
    assert v1 == v2 and abs(sum(x * x for x in v1) - 1) < 1e-9
    assert e.embed(["a"])[0][:2] == (0.6, 0.8) and e.kiem() == "gia@1"
    with pytest.raises(LoiEmbedder):
        EmbedderGia(loi_kiem=True).kiem()
    e = EmbedderGia(loi_tu_lan=2)
    e.embed(["x"])
    with pytest.raises(LoiEmbedder):
        e.embed(["y"])


def test_moi_lan_goi_nhan_ban_chup_messages_rieng():
    c = ClientGia(tra_loi({"x": 0}), tra_loi({"x": 1}))
    goi_json(c, he_thong="H", noi_dung="N", schema=SCHEMA, kiem=kiem)
    assert len(c.goi[0]["messages"]) == 1 and len(c.goi[1]["messages"]) == 3
