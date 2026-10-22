"""Vân tay G4: tệp không cho mọi người đọc chỉ ghi chủ/quyền/cỡ (Uq không đọc được nội dung)."""
import os

from tram.quan_kiem.bang_chung import _tep


def test_tep_khong_doc_chung_khong_mo_noi_dung(tmp_path, monkeypatch):
    p = tmp_path / "test.netrc"
    p.write_text("bi-mat")
    os.chmod(p, 0o600)
    monkeypatch.setattr(type(p), "open", lambda *a, **kw: (_ for _ in ()).throw(PermissionError("cấm")))
    assert _tep(p)[-1] == 6


def test_tep_doc_chung_bam_noi_dung(tmp_path):
    p = tmp_path / "a"
    p.write_text("x")
    os.chmod(p, 0o644)
    assert len(_tep(p)[-1]) == 64
