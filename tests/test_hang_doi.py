import json

from tram.tho.hang_doi import request_id_cho, xu_ly_hang_doi

KHOI = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 0, "file_ban_giao": "docs/handovers/x.md",
        "nhanh": "tram/hr-1", "commit": "abcdef1", "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [],
        "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": []}
PHIEU = {"khe_id": "B/claude-1", "giao_id": "g-20261013-0042", "luot": 3}


def _ghi(p, *dong, cuoi="\n"):
    p.write_text("\n".join(d if isinstance(d, str) else json.dumps(d, ensure_ascii=False) for d in dong) + cuoi)


def test_gan_phieu_bo_id_cua_agent_va_request_id_tat_dinh(tmp_path):
    p = tmp_path / "hd.jsonl"
    _ghi(p, {"loai": "moc", "noi_dung": "m1", "commit": "abcdef1", "giao_id": "g-gia", "luot": 99,
             "khe_id": "B/claude-2", "request_id": "r-gia"})
    ds, ke = xu_ly_hang_doi(p, **PHIEU)
    assert ke == 1 and ds[0].loi is None
    assert ds[0].than == {"loai": "moc", "noi_dung": "m1", "commit": "abcdef1", **PHIEU,
                          "request_id": request_id_cho("g-20261013-0042", 3, 0)}
    assert xu_ly_hang_doi(p, **PHIEU)[0][0].than["request_id"] == ds[0].than["request_id"]   # đọc lại: cùng id


def test_dong_sau_xong_bi_bo_va_luot_ban_giao_bi_ghi_de(tmp_path):
    p = tmp_path / "hd.jsonl"
    _ghi(p, {"loai": "moc", "commit": None}, {"loai": "xong", "commit": "abcdef1", "ban_giao": KHOI},
         {"loai": "bi", "noi_dung": "sau xong"})
    ds, ke = xu_ly_hang_doi(p, **PHIEU)
    assert [d.than["loai"] for d in ds] == ["moc", "xong"] and ke == 3
    assert ds[1].than["ban_giao"]["luot"] == 3 and ds[0].than["noi_dung"] == ""


def test_dong_sai_cau_truc_bi_tu_choi_dong_tiep_van_doc(tmp_path):
    p = tmp_path / "hd.jsonl"
    _ghi(p, "không phải json", ["mảng"], {"loai": "xoa_db"}, {"loai": "moc", "la": 1},
         {"loai": "xong", "commit": "abcdef1"}, {"loai": "xong", "ban_giao": {**KHOI, "loai": "tam"}},
         {"loai": "can_hoi", "noi_dung": "?"}, {"loai": "moc", "commit": "HEAD"},
         {"loai": "moc", "noi_dung": "x" * 4001}, {"loai": "bi", "noi_dung": "kẹt"})
    ds, ke = xu_ly_hang_doi(p, **PHIEU)
    assert [d.loi is None for d in ds] == [False] * 9 + [True] and ke == 10


def test_dong_dang_ghi_do_chua_doc_va_doc_tiep_tu_vi_tri(tmp_path):
    p = tmp_path / "hd.jsonl"
    _ghi(p, {"loai": "moc"}, '{"loai": "bi", "noi', cuoi="")
    ds, ke = xu_ly_hang_doi(p, **PHIEU)
    assert len(ds) == 1 and ke == 1
    _ghi(p, {"loai": "moc"}, {"loai": "bi", "noi_dung": "kẹt"})
    ds, ke = xu_ly_hang_doi(p, **PHIEU, tu_dong=ke)
    assert [d.than["loai"] for d in ds] == ["bi"] and ds[0].so == 1 and ke == 2
    assert xu_ly_hang_doi(tmp_path / "khong", **PHIEU) == ([], 0)
