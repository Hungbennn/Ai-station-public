from types import SimpleNamespace

import tram.kiem.chay_gioi_han as gh


def test_stdin_truyen_nguyen_va_khong_dong_cua_nguoi_goi(tmp_path, monkeypatch):
    goi = []
    p = SimpleNamespace(stdin=None, stdout=None, stderr=None, returncode=0)
    n = SimpleNamespace(p=p, ket_thu_hoi=True)
    def khoi(a, **kw):
        goi.append(kw["stdin"])
        kw["chu"].append(n)
        return n
    monkeypatch.setattr(gh, "_ong", lambda *a: (b"", b"", True))
    f = tmp_path / "vao"
    f.write_bytes(b"du-lieu-gia")
    with f.open("rb") as vao:
        assert gh.chay_gioi_han(["gia"], kill=lambda *a: None, timeout=1, stdin=vao, khoi=khoi).returncode == 0
        assert goi == [vao] and not vao.closed
