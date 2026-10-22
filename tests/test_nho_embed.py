import json
import urllib.error

import pytest

from tram.nho.embed import LoiEmbedder, OllamaEmbedder

TAGS = {"models": [{"name": "nomic:latest", "digest": "zz"}, {"name": "bge-m3:latest", "digest": "sha256abc"}]}


class TraLoi:
    def __init__(self, du_lieu):
        self._b = json.dumps(du_lieu).encode() if not isinstance(du_lieu, bytes) else du_lieu

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class MoGia:
    def __init__(self, *cac):
        self.cac, self.goi = list(cac), []

    def __call__(self, yc, timeout):
        self.goi.append((yc.get_method(), yc.full_url, json.loads(yc.data) if yc.data else None, timeout))
        x = self.cac.pop(0)
        if isinstance(x, Exception):
            raise x
        return TraLoi(x)


def test_kiem_lay_digest_va_embed_chuan_hoa():
    mo = MoGia(TAGS, {"embeddings": [[3.0, 4.0], [0.0, 2.0]]})
    e = OllamaEmbedder(so_chieu=2, mo=mo)
    assert e.kiem() == "bge-m3@sha256abc" and e.mo_hinh == "bge-m3@sha256abc"
    assert e.embed(["a", "b"]) == [(0.6, 0.8), (0.0, 1.0)]
    assert mo.goi[0][:2] == ("GET", "http://127.0.0.1:11434/api/tags")
    assert mo.goi[1][:3] == ("POST", "http://127.0.0.1:11434/api/embed", {"model": "bge-m3", "input": ["a", "b"]})


def test_chua_kiem_thi_khong_co_mo_hinh():
    with pytest.raises(LoiEmbedder):
        OllamaEmbedder(mo=MoGia()).mo_hinh


@pytest.mark.parametrize("tra", [
    urllib.error.URLError("Connection refused"), TimeoutError("timed out"), b"khong-phai-json",
    {"models": [{"name": "nomic:latest", "digest": "zz"}]}, {"models": [{"name": "bge-m3"}]}, {}])
def test_kiem_loi_thi_bao_loi_to(tra):
    with pytest.raises(LoiEmbedder):
        OllamaEmbedder(mo=MoGia(tra)).kiem()


@pytest.mark.parametrize("tra", [
    {"embeddings": [[1.0, 0.0]]}, {"embeddings": [[0.0, 0.0], [1.0, 0.0]]},
    {"embeddings": [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]}, {"embeddings": [[1.0, "x"], [1.0, 0.0]]},
    {"loi": "x"}, urllib.error.URLError("refused")])
def test_embed_loi_khong_lui_ve_vector_gia(tra):
    e = OllamaEmbedder(so_chieu=2, mo=MoGia(TAGS, tra))
    e.kiem()
    with pytest.raises(LoiEmbedder):
        e.embed(["a", "b"])


def test_embed_rong_khong_goi_mang():
    mo = MoGia()
    assert OllamaEmbedder(mo=mo).embed([]) == [] and mo.goi == []


@pytest.mark.parametrize("tra", [[], "x", None, 3, {"models": "abc"}, {"models": ["x", None, 3]}])
def test_kiem_json_sai_dang_chi_ra_loi_embedder(tra):
    with pytest.raises(LoiEmbedder):
        OllamaEmbedder(mo=MoGia(tra)).kiem()


def test_kiem_bo_qua_phan_tu_khong_phai_dict():
    tra = {"models": ["x", None, {"name": "bge-m3:latest", "digest": "d1"}]}
    assert OllamaEmbedder(mo=MoGia(tra)).kiem() == "bge-m3@d1"


@pytest.mark.parametrize("tra", [[], "x", None, {"embeddings": [None, [1.0, 0.0]]}])
def test_embed_json_sai_dang_chi_ra_loi_embedder(tra):
    e = OllamaEmbedder(so_chieu=2, mo=MoGia(TAGS, tra))
    e.kiem()
    with pytest.raises(LoiEmbedder):
        e.embed(["a", "b"])


def test_embed_thanh_phan_cuc_lon_van_chuan_hoa():
    e = OllamaEmbedder(so_chieu=2, mo=MoGia(TAGS, {"embeddings": [[1e308, 1e308], [1.0, 0.0]]}))
    e.kiem()
    assert abs(e.embed(["a", "b"])[0][0] - 2 ** -0.5) < 1e-12
