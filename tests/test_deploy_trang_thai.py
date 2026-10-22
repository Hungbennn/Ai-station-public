"""TM-3 (tu-deploy, design D-6, D-7; D75, D96, D97 luật 2/5, D123, D124, D126, D127; Codex Q6, Q8): trạng thái tự
deploy tính lúc đọc từ sự kiện — hàm thuần, không kho, không git, không lệnh. Bao phủ ghi rõ bằng `bao_gom`."""
import pytest

from tram.deploy.hien_thi import AI, LOAI_LICH_SU, dang_deploy, lich_su, san_sang
from tram.deploy.trang_thai import (SK, chua_ghi_nhan, chuoi_dang_do, commit_truoc, da_ghi_nhan, dem_hong,
                                    merge_chua_deploy, tu_merge_cho_deploy, yeu_cau_cho)

TRAM = "tram/tu-deploy"


class Dong:
    """Dựng dãy sự kiện cũ → mới, id tăng dần."""

    def __init__(self):
        self.ds: list[SK] = []

    def __call__(self, kieu: str, bead: str | None = None, tac_nhan: str = TRAM, /, **du_lieu) -> SK:
        s = SK(len(self.ds) + 1, kieu, du_lieu, f"2026-10-18T10:{len(self.ds):02d}:00Z", tac_nhan, bead)
        self.ds.append(s)
        return s


def merge(d: Dong, bead: str, mc: str, *, tu: bool) -> SK:
    if tu:
        d("tu_merge.bat_dau", bead, "tram/tu-merge", ma_thao_tac=f"tm-{bead}", commit=f"c-{bead}", pr=7, loai="code")
    return d("pr.da_merge", bead, "tram/giao-viec", commit=f"c-{bead}", merge_commit=mc, pr=7, ma_thao_tac=f"pr-{bead}")


def chuoi(d: Dong, ma: str, commit: str, ket_qua: str | None, bao=(), nguon: str = "tu_dong", dem: int = 0,
          truoc: str = "", yeu_cau: str | None = None):
    d("deploy.bat_dau", ma_thao_tac=ma, commit=commit, commit_truoc=truoc, nguon=nguon, bao_gom=[s.id for s in bao],
      **({"yeu_cau": yeu_cau} if yeu_cau else {}))
    d("deploy.lenh", ma_thao_tac=ma, buoc="deploy", ma_thoat=1, giay=12, het_gio=False, digest_log="sha256:x")
    if ket_qua:
        d("deploy.xong", ma_thao_tac=ma, ket_qua=ket_qua, dem_hong=dem)


def ss(d: Dong, commit: str, *bao: SK, cho=()):
    return d("deploy.san_sang", commit=commit, so_merge=len(bao), bao_gom=[s.id for s in bao], cho=list(cho))


def test_tu_merge_moi_la_co_tu_deploy_gop_tay_thi_khong():
    """D-6: chỉ TỰ merge mới kích tự deploy; Đại ca gộp tay (D96) chỉ thành "sẵn sàng"; PR spec (D95) không kích."""
    d = Dong()
    m6 = merge(d, "rn-6", "m6", tu=False)
    assert tu_merge_cho_deploy(d.ds) is None and merge_chua_deploy(d.ds) == [m6]
    m7 = merge(d, "rn-7", "m7", tu=True)
    assert tu_merge_cho_deploy(d.ds) == m7
    d("tu_merge.bat_dau", "f-1", "tram/tu-merge", ma_thao_tac="tm-f", commit="c-f-1", pr=8, loai="spec")
    d("pr.da_merge", "f-1", "tram/giao-viec", commit="c-f-1", merge_commit="m8", ma_thao_tac="pr-f")
    assert tu_merge_cho_deploy(d.ds) == m7


def test_san_sang_khi_tu_deploy_tat_tieu_kich_khi_tam_dung_thi_khong():
    """D123: bản đã báo "sẵn sàng" lúc tự deploy TẮT → chờ Đại ca bấm. Codex Q8: báo "sẵn sàng" vì TẠM DỪNG không
    tiêu kích — Tiếp tục thì tự deploy."""
    d = Dong()
    m7 = merge(d, "rn-7", "m7", tu=True)
    s = ss(d, "m7", m7, cho=["tam_dung_du_an"])
    assert tu_merge_cho_deploy(d.ds) == m7 and da_ghi_nhan(d.ds, "m7", [m7.id]) and not da_ghi_nhan(d.ds, "m8", [])
    ss(d, "m7", m7, cho=["tu_deploy_tat"])
    assert tu_merge_cho_deploy(d.ds) is None and san_sang(d.ds)["commit"] == "m7" and s.id < d.ds[-1].id


def test_bao_phu_ghi_ro_khong_dung_thu_tu_id():
    """Codex Q6: m6 ghi `pr.da_merge` TRƯỚC `bat_dau` của chuỗi m5 nhưng worktree chỉ chứa m5 → m5 `dat` không làm
    m6 thành "đã deploy"; kích tự deploy của m6 vẫn còn."""
    d = Dong()
    m5 = merge(d, "rn-5", "m5", tu=True)
    m6 = merge(d, "rn-6", "m6", tu=True)
    chuoi(d, "dp-5", "m5", "dat", bao=[m5])
    assert merge_chua_deploy(d.ds) == [m6] and tu_merge_cho_deploy(d.ds) == m6 and commit_truoc(d.ds) == "m5"
    assert san_sang(d.ds) is None and chua_ghi_nhan(d.ds) == [m6]       # chưa vòng nào ghi nhận m6
    ss(d, "m6", m6)
    assert san_sang(d.ds)["bead_ids"] == ["rn-6"] and chua_ghi_nhan(d.ds) == []


def test_ba_merge_cho_deploy_mot_hang():
    """Scenario "Ba lần merge chờ deploy": một hàng cho commit mới nhất, "gồm 3 việc đã merge"."""
    d = Dong()
    ms = [merge(d, f"rn-{i}", f"m{i}", tu=True) for i in (7, 8, 9)]
    assert san_sang(d.ds) is None                                   # vòng deploy chưa ghi nhận commit nào
    ss(d, "m9", *ms)
    s = san_sang(d.ds)
    assert s == {"commit": "m9", "so_merge": 3, "bead_ids": ["rn-7", "rn-8", "rn-9"], "luc": s["luc"],
                 "commit_dang_chay": None}


def test_dang_deploy_an_hang_va_yeu_cau_cho():
    """Scenario "Đại ca bấm Deploy": hàng "sẵn sàng" chuyển "đang deploy"; yêu cầu chờ tới khi một chuỗi nhận nó."""
    d = Dong()
    m5 = merge(d, "rn-7", "m5", tu=False)
    ss(d, "m5", m5)
    yc = d("deploy.yeu_cau", None, "dai-ca/dashboard", ma_thao_tac="ma-dp-1", commit="m5", nguon="dai_ca")
    assert yeu_cau_cho(d.ds) == yc and san_sang(d.ds) is None
    assert dang_deploy(d.ds) == {"trang_thai": "cho", "commit": "m5", "nguon": "dai_ca", "luc": yc.luc}
    chuoi(d, "dp-0", "m5", "khong_ro", bao=[m5])                    # chuỗi KHÁC không tiêu yêu cầu (không theo id)
    assert yeu_cau_cho(d.ds) == yc
    chuoi(d, "dp-1", "m5", None, bao=[m5], nguon="dai_ca", yeu_cau="ma-dp-1")
    assert yeu_cau_cho(d.ds) is None and [s.du_lieu["ma_thao_tac"] for s in chuoi_dang_do(d.ds)] == ["dp-1"]
    assert dang_deploy(d.ds)["trang_thai"] == "chay"
    d("deploy.xong", ma_thao_tac="dp-1", ket_qua="dat", dem_hong=0)
    assert dang_deploy(d.ds) is None and san_sang(d.ds) is None and commit_truoc(d.ds) == "m5"
    assert merge_chua_deploy(d.ds) == []


def test_huy_tieu_thu_yeu_cau():
    d = Dong()
    d("deploy.yeu_cau", None, "dai-ca/dashboard", ma_thao_tac="ma-dp-2", commit="m5", nguon="dai_ca")
    d("deploy.huy", ma_thao_tac="ma-dp-2", commit="m5", ly_do="estop")
    assert yeu_cau_cho(d.ds) is None and dang_deploy(d.ds) is None


def test_hong_xong_van_san_sang_cho_dai_ca_bam_lai():
    """D124: sau lần hỏng đã lùi, bản đó vẫn ở hàng "sẵn sàng" để Đại ca bấm lại — trạm không tự thử lại."""
    d = Dong()
    chuoi(d, "dp-0", "m4", "dat")
    m = merge(d, "rn-13", "c0d9", tu=True)
    chuoi(d, "dp-1", "c0d9", "da_lui", bao=[m], dem=1)
    assert tu_merge_cho_deploy(d.ds) is None                        # đã vào một chuỗi
    s = san_sang(d.ds)
    assert (s["commit"], s["so_merge"], s["commit_dang_chay"], commit_truoc(d.ds)) == ("c0d9", 1, "m4", "m4")


@pytest.mark.parametrize("ket_qua", ["da_lui", "lui_hong", "khong_ro"])
def test_ban_da_bat_dau_khong_bao_san_sang_lai_khi_tu_deploy_tat(ket_qua):
    """D124: bắt đầu đã tiêu trigger; dấu tắt mới không tạo thêm tin sẵn sàng cho cùng commit/tập merge."""
    d = Dong()
    m = merge(d, "rn-1", "m1", tu=True)
    chuoi(d, "dp-1", "m1", ket_qua, bao=[m])
    assert da_ghi_nhan(d.ds, "m1", [m.id], cho=["tu_deploy_tat"])
    assert not da_ghi_nhan(d.ds, "m1", [m.id, 999], cho=["tu_deploy_tat"])
    assert tu_merge_cho_deploy(d.ds) is None and san_sang(d.ds)["commit"] == "m1"


def test_dem_hong_lien_tiep():
    """D75: đếm `da_lui`/`lui_hong` từ lần `dat` hoặc lần bật lại tự deploy; D126: `khong_ro` không tính."""
    d = Dong()
    chuoi(d, "a", "m1", "da_lui")
    chuoi(d, "b", "m1", "khong_ro")
    chuoi(d, "c", "m1", "da_lui")
    assert dem_hong(d.ds) == 2
    chuoi(d, "e", "m2", "dat")                                      # Scenario "Thành công xen giữa"
    assert dem_hong(d.ds) == 0
    chuoi(d, "f", "m3", "da_lui")
    chuoi(d, "g", "m3", "lui_hong")
    assert dem_hong(d.ds) == 2
    d("tu_dong.cai_dat", None, "dai-ca/dashboard", cai_dat={"tu_deploy": False}, doi=["lenh_lui"])
    assert dem_hong(d.ds) == 2
    d("tu_dong.cai_dat", None, "dai-ca/dashboard", cai_dat={"tu_deploy": True}, doi=["tu_deploy"])
    assert dem_hong(d.ds) == 0                                      # Đại ca bật lại → về 0


def test_lich_su_dang_hop_dong_tm4_khong_chep_lenh():
    """Dạng khoá TM-4: `{luc, loai, bead_id, commit, chi_tiet, ai}`; `chi_tiet` chỉ mã thoát/giây/PR/commit ngắn;
    D127: nút Deploy bị huỷ thành dòng `huy` kèm lý do bằng lời."""
    d = Dong()
    m11 = merge(d, "rn-11", "9be2", tu=False)                       # gộp tay: không thành dòng riêng
    m12 = merge(d, "rn-12", "a41c", tu=True)
    ss(d, "a41c", m11, m12)
    chuoi(d, "dp-9", "a41c", "da_lui", bao=[m11, m12], dem=1, nguon="dai_ca", truoc="5d3e8b2aa", yeu_cau="ma-0")
    d("deploy.lenh", ma_thao_tac="dp-9", buoc="lui", ma_thoat=None, giay=900, het_gio=True, digest_log="sha256:y")
    d("tu_dong.cai_dat", cai_dat={"tu_deploy": False}, doi=["tu_deploy"], ly_do="hong-3-lan")
    d("tu_dong.tam_dung", ly_do="khong-ro")
    d("tu_dong.tam_dung", None, "dai-ca/dashboard", ma_thao_tac="x")          # Đại ca bấm: đã có ở lịch sử đổi
    d("deploy.huy", ma_thao_tac="ma-1", commit="a41c", ly_do="estop")
    d("deploy.huy", ma_thao_tac="ma-2", commit="a41c", ly_do="ban_moi_hon")
    ls = lich_su(d.ds)
    assert [(x["loai"], x["ai"]) for x in ls] == [("huy", "dai_ca_bam"), ("huy", "dai_ca_bam"), ("tam_dung", "tram"),
                                                  ("tu_tat", "tram"), ("deploy_lui", "dai_ca_bam"),
                                                  ("san_sang", "tram"), ("tu_merge", "tram")]
    assert {x["loai"] for x in ls} <= set(LOAI_LICH_SU) and {x["ai"] for x in ls} <= set(AI)
    assert all(set(x) == {"luc", "loai", "bead_id", "commit", "chi_tiet", "ai"} for x in ls)
    assert (ls[0]["chi_tiet"], ls[1]["chi_tiet"], ls[1]["commit"]) == (
        "Có bản mới hơn — bấm Deploy lại trên bản mới", "Estop đang bật", "a41c")
    assert ls[2]["chi_tiet"].endswith("deploy không rõ kết quả — cần Đại ca kiểm")
    assert ls[3]["chi_tiet"] == "hỏng 3 lần liên tiếp — chờ Đại ca bật lại"
    assert ls[4]["chi_tiet"] == "deploy: mã thoát 1 · 12 giây → lùi: quá hạn · 900 giây (bản trước 5d3e8b2)"
    assert (ls[4]["commit"], ls[5]["chi_tiet"]) == ("a41c", "gồm 2 việc đã merge")
    assert (ls[6]["bead_id"], ls[6]["commit"], ls[6]["chi_tiet"]) == ("rn-12", "a41c", "PR #7")
    assert len(lich_su(d.ds, gioi_han=2)) == 2
