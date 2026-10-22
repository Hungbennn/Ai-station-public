"""TM-3 (tu-deploy: Kiểm còn sống · Deploy hỏng thì tự lùi · Hỏng 3 lần thì tự tắt · Lùi cũng hỏng thì dừng hẳn ·
Kết quả không rõ; D75, D97 luật 1/2, Đại ca chốt D115): chuỗi lệnh (hàm thuần trên `chay` giả) và `deploy.xong` ghi
cùng giao dịch với hệ quả — đúng hợp đồng sự kiện/tin của TM-1."""
from dataclasses import replace

import pytest

from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.deploy.chuoi import chay_chuoi
from tram.deploy.ghi import ket_thuc, ma_chuoi
from tram.deploy.lenh import KetQuaBuoc
from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doc_trang_thai, doi_cai_dat

CD = CaiDatTuDong(tu_merge=True, tu_deploy=True, lenh_deploy="d.sh", lenh_kiem_song="k.sh", lenh_lui="l.sh")
DAT, HONG = KetQuaBuoc("x", 0, 1, False, "sha256:a"), KetQuaBuoc("x", 1, 1, False, "sha256:b")
QUA_HAN, KHONG_THU = KetQuaBuoc("x", -9, 900, True, "sha256:c"), KetQuaBuoc("x", None, 900, True, "sha256:d", False)


def gia(**theo_buoc):
    goi = []

    def chay(buoc, lenh):
        goi.append((buoc, lenh))
        return theo_buoc.get(buoc, DAT)
    return chay, goi


@pytest.mark.parametrize("theo, ket_qua, cac_buoc", [
    ({}, "dat", ["deploy", "kiem_song"]),
    ({"kiem_song": HONG}, "da_lui", ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"]),   # trang chết → lùi
    ({"deploy": QUA_HAN}, "da_lui", ["deploy", "lui", "kiem_song_sau_lui"]),                # lệnh deploy treo
    ({"deploy": HONG, "kiem_song_sau_lui": HONG}, "lui_hong", ["deploy", "lui", "kiem_song_sau_lui"]),
    ({"deploy": HONG, "lui": QUA_HAN}, "lui_hong", ["deploy", "lui"]),
    ({"deploy": KHONG_THU}, "khong_ro", ["deploy"]),                  # cây chưa thu hồi → không lùi chồng lên
    ({"kiem_song": HONG, "lui": KHONG_THU}, "khong_ro", ["deploy", "kiem_song", "lui"]),
])
def test_chuoi_deploy_kiem_song_lui(theo, ket_qua, cac_buoc):
    chay, goi = gia(**theo)
    assert chay_chuoi(CD, chay) == ket_qua
    assert [b for b, _ in goi] == cac_buoc
    assert dict(goi) == {b: {"deploy": "d.sh", "lui": "l.sh"}.get(b, "k.sh") for b in cac_buoc}


def test_ma_chuoi_tat_dinh():
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1") == ma_chuoi("rn", "m5", "dai_ca", "ma-1")
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1") != ma_chuoi("rn", "m5", "tu_dong", "ma-1")
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1").startswith("dp-") and len(ma_chuoi("a", "b", "c", "d")) == 43


@pytest.fixture
def kho(tmp_path):
    k = KhoPhieu(tmp_path / "su-kien.db")
    doi_cai_dat(k.db, "repo-nhap", lambda c: CD, tac_nhan="dai-ca/dashboard")
    yield k
    k.close()


def tin_sau(tmp_path, moc: int) -> list[Tin]:
    ks = KhoSuKien(tmp_path / "su-kien.db")
    try:
        return [t for s in ks.sau_id(moc, 100) for t in tin_tu_su_kien(s, ks)]
    finally:
        ks.close()


def test_hong_lan_thu_ba_tu_tat_va_bao(kho, tmp_path):
    """Scenario "Lùi thành công" (đếm tăng, công tắc giữ) rồi "Lần hỏng thứ ba" (tự tắt, tác nhân trạm)."""
    assert ket_thuc(kho.db, "repo-nhap", "dp-1", "da_lui") == 1
    assert ket_thuc(kho.db, "repo-nhap", "dp-2", "da_lui") == 2
    assert doc_trang_thai(kho.db, "repo-nhap").cai_dat.tu_deploy is True
    moc = kho.db.execute("SELECT max(id) FROM su_kien").fetchone()[0]
    assert ket_thuc(kho.db, "repo-nhap", "dp-3", "da_lui") == 3
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat == replace(CD, tu_deploy=False) and tt.tam_dung_du_an is None
    assert tin_sau(tmp_path, moc) == [Tin("deploy_da_lui", "repo-nhap", "hong-3-lan"),
                                      Tin("tu_deploy_tu_tat", "repo-nhap")]
    assert ket_thuc(kho.db, "repo-nhap", "dp-4", "dat") == 0          # thành công → về 0, không đổi gì thêm


def test_lui_hong_tat_va_tam_dung_cung_giao_dich(kho, tmp_path):
    """Scenario "Trang chết sau lùi": tắt tự deploy, TẠM DỪNG dự án, tin khẩn."""
    assert ket_thuc(kho.db, "repo-nhap", "dp-1", "lui_hong") == 1
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat.tu_deploy is False and tt.cai_dat.tu_merge is True
    assert (tt.tam_dung_du_an.boi, tt.tam_dung_du_an.ly_do) == ("tram/tu-deploy", "lui-hong")
    assert tin_sau(tmp_path, 1) == [Tin("lui_hong", "repo-nhap"), Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat"),
                                    Tin("cai_dat_doi", "repo-nhap", "tram-tam-dung")]


def test_khong_ro_tam_dung_ca_du_an_khong_tinh_hong(kho, tmp_path):
    """D115 (Đại ca chốt 18/10): không rõ kết quả → TẠM DỪNG cả dự án; tự deploy giữ nguyên, không tính lần hỏng."""
    ket_thuc(kho.db, "repo-nhap", "dp-1", "da_lui")
    assert ket_thuc(kho.db, "repo-nhap", "dp-2", "khong_ro") == 1
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat.tu_deploy is True and tt.tam_dung_du_an.ly_do == "khong-ro"
    assert Tin("deploy_khong_ro", "repo-nhap") in tin_sau(tmp_path, 2)


def test_loi_giua_giao_dich_khong_ghi_gi(kho, monkeypatch):
    import tram.deploy.ghi as g
    monkeypatch.setattr(g, "ghi_tam_dung", lambda *a, **k: (_ for _ in ()).throw(OSError("đĩa đầy")))
    trc = kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    with pytest.raises(OSError):
        ket_thuc(kho.db, "repo-nhap", "dp-1", "lui_hong")
    assert kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0] == trc
