"""Tin Telegram của luồng feature (spec 4 §10 bước 4): nhắc merge spec, feature xong chờ đóng — chỉ mã bead."""
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin, soan_tin
from tram.su_kien.kho import SuKien


def sk(loai, du_lieu=None):
    return SuKien("2026-10-13T03:00:00Z", "hr-codex", "hr-f", loai, "tram/giao-viec", du_lieu or {})


def test_su_kien_feature_thanh_tin():
    assert tin_tu_su_kien(sk("spec.cho_merge", {"commit": "abc"}), None) == [Tin("spec_cho_merge", "hr-codex", "hr-f")]
    assert tin_tu_su_kien(sk("feature.xong", {"feature": "hr-f"}), None) == [Tin("feature_xong", "hr-codex", "hr-f")]
    assert tin_tu_su_kien(sk("spec.duyet"), None) == []


def test_noi_dung_tin_chi_ma_bead():
    t = soan_tin("spec_cho_merge", [Tin("spec_cho_merge", "hr-codex", "hr-f")], "https://may-b/#/phe-duyet")
    assert t == "[tram] hr-codex · 1 spec đã duyệt chưa merge sau 24 giờ (hr-f) → https://may-b/#/phe-duyet"
    assert "chờ Đại ca đóng" in soan_tin("feature_xong", [Tin("feature_xong", "hr-codex", "hr-f")], None)
