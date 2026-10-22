"""2f P3: bảng sẵn sàng — suy trạng thái bead nhãn `san-sang`, tự kiểm, lỗi bd không làm mất phần tự kiểm, bộ đệm."""
import json

from test_he_thong import ChayGia, DongHo
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.suy.he_thong import DocHeThong
from tram.suy.san_sang import LOI_BEAD, BangSanSang, tu_bead


def _bead(id_, status="open", nhan=("san-sang",), chan=(), con=()):
    phu = [{"depends_on_id": c, "type": "blocks"} for c in chan] + [{"depends_on_id": c, "type": "parent-child"}
                                                                     for c in con]
    return Bead.tu_json({"id": id_, "title": f"Cổng {id_}‮", "description": "MO-TA-BI-MAT", "notes": "NOTES-BI-MAT",
                         "status": status, "labels": list(nhan), "updated_at": "2026-10-16T00:00:00Z",
                         "dependencies": phu})


BEADS = [_bead("bs-1", "closed"), _bead("bs-2", chan=["bs-3"]), _bead("bs-3", chan=["bs-1"]),
         _bead("bs-4", nhan=()), _bead("bs-5", con=["bs-3"]), _bead("bs-6", chan=["bs-3", "bs-x"])]


def test_suy_trang_thai_bead():
    ds = tu_bead(BEADS)
    assert [(m["ma"], m["trang_thai"], m["ghi_chu"]) for m in ds] == [
        ("bs-1", "dat", ""), ("bs-2", "cho", "cần bs-3"), ("bs-3", "thieu", ""),        # blocks vào bead đã đóng
        ("bs-5", "thieu", ""), ("bs-6", "cho", "cần bs-3, bs-x")]                       # parent-child không chặn
    assert ds[0] == {"ma": "bs-1", "ten": "Cổng bs-1", "trang_thai": "dat", "ghi_chu": "", "nguon": "bead"}
    s = json.dumps(ds, ensure_ascii=False)
    assert "MO-TA-BI-MAT" not in s and "NOTES-BI-MAT" not in s and "bs-4" not in s


def _bang(tmp_path, doc_bead, dong_ho=None):
    he = DocHeThong(chay=ChayGia({"tram-nho-token": (0, "x")}), home=tmp_path, uid=501, dong_ho=DongHo())
    return BangSanSang(doc_bead=doc_bead, which=lambda l: l == "bd" or None, dong_ho=dong_ho or DongHo()), he


def test_tu_kiem_va_dem(tmp_path):
    bang, he = _bang(tmp_path, lambda: BEADS)
    j = bang.lay(he)
    tu = {m["ma"]: m for m in j["muc"] if m["nguon"] == "tu_kiem"}
    assert [m for m in tu if m.startswith("lenh:")] == ["lenh:bd", "lenh:tailscale", "lenh:gh", "lenh:codex",
                                                        "lenh:claude", "lenh:gitnexus", "lenh:uv", "lenh:ollama"]
    assert tu["lenh:bd"]["trang_thai"] == "dat" and tu["lenh:ollama"]["trang_thai"] == "thieu"
    assert [m for m in tu if m.startswith("dich-vu:")] == ["dich-vu:vn.tram.api", "dich-vu:vn.tram.quet",
                                                           "dich-vu:vn.tram.nho", "dich-vu:vn.tram.bao-tin"]
    assert tu["dich-vu:vn.tram.api"] == {"ma": "dich-vu:vn.tram.api", "ten": "Đã cài vn.tram.api",
                                         "trang_thai": "thieu", "ghi_chu": "chưa có plist trong ~/Library/LaunchAgents",
                                         "nguon": "tu_kiem"}
    assert tu["keychain:tram-nho-token"]["trang_thai"] == "dat"
    assert tu["keychain:tram-noi-bo-token"]["ghi_chu"] == "không kiểm được (Keychain khoá?)"
    assert j["dem"] == {"dat": 3, "thieu": 16, "cho": 2} and j["loi"] is None and j["doc_luc"].endswith("Z")


def test_loi_bd_van_tra_tu_kiem_va_bo_dem_60_giay(tmp_path):
    goi, dh = [], DongHo()

    def doc():
        goi.append(1)
        raise LoiBd("bd lỗi: STDERR-BI-MAT /Users/x/.beads")
    bang, he = _bang(tmp_path, doc, dh)
    j = bang.lay(he)
    assert j["loi"] == LOI_BEAD and j["muc"] and all(m["nguon"] == "tu_kiem" for m in j["muc"])
    assert "STDERR-BI-MAT" not in json.dumps(j, ensure_ascii=False)
    dh.t += 59
    bang.lay(he)
    assert len(goi) == 1
    dh.t += 1
    bang.lay(he)
    assert len(goi) == 2
