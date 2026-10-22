"""Lỗi constructor/start/join/get/assert tại callsite thật đều phải đi qua cleanup."""
from types import SimpleNamespace

import pytest
import test_api_yeu_cau_hai_tien_trinh as api
import test_yeu_cau_da_tien_trinh as dich_vu
from test_tien_trinh_thu import ConGia, HangGia


@pytest.mark.parametrize("mod", [api, dich_vu])
@pytest.mark.parametrize("diem", ["tao", "start", "join", "get", "assert"])
def test_callsite_don_khi_loi(tmp_path, monkeypatch, mod, diem):
    ds, hang = [], HangGia()

    class Con(ConGia):
        exitcode = (9 if mod is api else None) if diem == "assert" else 0

        def start(self):
            if diem == "start" and self is ds[-1] and len(ds) == 2:
                raise RuntimeError("loi-thu")
            self.pid, self.song = 1, True

        def join(self, han):
            if han == 60 and diem == "join":
                raise RuntimeError("loi-thu")
            super().join(han)

    def tao_con(**kw):
        if diem == "tao" and len(ds) == 1:
            raise RuntimeError("loi-thu")
        p = Con(pid=None, song=False)
        ds.append(p)
        return p

    def lay(*, timeout):
        assert timeout == 5
        raise RuntimeError("loi-thu")

    hang.get = lay
    ctx = SimpleNamespace(Barrier=lambda n: object(), Queue=lambda: hang, Process=tao_con)
    monkeypatch.setattr(mod, "CTX", ctx)
    with pytest.raises(AssertionError if diem == "assert" else RuntimeError):
        if mod is api:
            api.test_hai_tien_trinh_tram_api_cung_yeu_cau_chi_mot_feature(tmp_path)
        else:
            dich_vu.chay(2, tmp_path / "sk.db", tmp_path)
    assert hang.nhat_ky == ["cancel", "close"]
    assert all(not p.song for p in ds)
    assert all("kill" in p.nhat_ky for p in ds if p.pid is not None)
