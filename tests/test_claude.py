import json
from types import SimpleNamespace as NS

import pytest

from tram.llm.claude import LoiChamLLM, cham_bang_llm

DUNG = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}
SAI_NGU_NGHIA = {**DUNG, "cot": "can-chot"}


def tra_loi(van_ban, stop="end_turn"):
    return NS(stop_reason=stop, content=[NS(type="text", text=van_ban)],
              usage=NS(input_tokens=100, output_tokens=20, cache_read_input_tokens=80))


class ClientGia:
    def __init__(self, *cac_tra_loi):
        self._ds = list(cac_tra_loi)
        self.goi = []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.goi.append(kw)
        return self._ds.pop(0)


def test_dung_ngay_lan_dau():
    c = ClientGia(tra_loi(json.dumps(DUNG)))
    kq = cham_bang_llm(c, "HỆ", "NỘI DUNG")
    assert kq.ket_qua.cot == "ai-lam" and kq.so_lan == 1 and kq.token_cache_doc == 80
    kw = c.goi[0]
    assert kw["model"] == "claude-sonnet-5-5"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert kw["fallbacks"] == "default"


def test_sai_ngu_nghia_thi_gui_loi_va_thu_lai():
    c = ClientGia(tra_loi(json.dumps(SAI_NGU_NGHIA)), tra_loi(json.dumps(DUNG)))
    kq = cham_bang_llm(c, "HỆ", "ND")
    assert kq.so_lan == 2 and kq.token_vao == 200
    lan2 = c.goi[1]["messages"]
    assert lan2[1]["role"] == "assistant" and "cau_hoi_can_chot" in lan2[2]["content"]


def test_json_hong_cung_thu_lai():
    c = ClientGia(tra_loi("{không phải json"), tra_loi(json.dumps(DUNG)))
    assert cham_bang_llm(c, "HỆ", "ND").so_lan == 2


def test_het_luot_thi_nem_loi():
    c = ClientGia(*[tra_loi(json.dumps(SAI_NGU_NGHIA)) for _ in range(3)])
    with pytest.raises(LoiChamLLM):
        cham_bang_llm(c, "HỆ", "ND")


def test_tu_choi_thi_nem_loi_ngay():
    c = ClientGia(tra_loi("", stop="refusal"))
    with pytest.raises(LoiChamLLM, match="refusal"):
        cham_bang_llm(c, "HỆ", "ND")
    assert len(c.goi) == 1
