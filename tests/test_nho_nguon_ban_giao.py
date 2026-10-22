"""Lát 1b-4 Task 2: nguồn `ban_giao` (spec 1b §6.1, D8) — bead thường: `qc.ket_qua` đạt → `kiem.lai` đạt cùng
`commit_code` → `bao.xong`; spike: `kiem.lai` đạt không chạy lệnh. Review đợt 4: phiếu mới cùng SHA, lỗi schema không lộ
nội dung; D23: bàn giao có dấu hiệu bí mật bị bỏ cả nguồn."""
import pytest

from bead_gia import KHOI_BAN_GIAO
from tram.nho.bi_mat import LoiBiMat
from tram.nho.nguon_ban_giao import DO_DAI_MUC, TOI_DA_MUC, doc_ban_giao, truoc
from tram.su_kien.kho import KhoSuKien

GID, C1 = "g-20261014-0007", "abc1234"
LENH = [{"lenh": "php artisan test", "ket_qua": "pass", "digest_log": "d1"}]
BG = {**KHOI_BAN_GIAO, "luot": 2,
      "quyet_dinh": ["Dùng `php artisan test --filter` thay phpunit"],
      "huong_da_bo": [{"huong": "Gọi phpunit trực tiếp", "vi_sao": "thiếu bootstrap Laravel"}],
      "vuong_mac": ["Seeder chậm 40 giây"], "buoc_tiep": ["BƯỚC TIẾP KHÔNG NẠP"], "cau_hoi_mo": ["HỎI MỞ KHÔNG NẠP"]}


def ghi(k, loai, du_lieu, *, tac_nhan="tram/giao-viec", du_an="hr", bead="hr-1"):
    k.ghi(du_an, loai, du_lieu, bead_id=bead, tac_nhan=tac_nhan)
    return k.sau_id(k.id_moi_nhat() - 1, 1)[0]


def nhan(k, *, gid=GID, vai="coder", luot=2, **kw):
    return ghi(k, "giao.nhan", {"giao_id": gid, "luot": luot, "bead_id": "hr-1", "buoc": "code", "vai": vai},
               tac_nhan="tram/api", **kw)


def bao(k, *, gid=GID, ban_giao=BG, luot=2, tac_nhan="tho/B/claude-1", **kw):
    return ghi(k, "bao.xong", {"giao_id": gid, "luot": luot, "ban_giao": ban_giao, "commit": C1,
                               "request_id": "r-12345678", "noi_dung": ""}, tac_nhan=tac_nhan, **kw)


def kiem(k, *, gid=GID, dat=True, luot=2, commit=C1, ket_qua=LENH, **kw):
    return ghi(k, "kiem.lai", {"giao_id": gid, "bead_id": "hr-1", "luot": luot, "commit": commit,
                               "digest_tieu_chi": "d", "dat": dat, "ket_qua": ket_qua, "digest_log": [],
                               "cham_cam": []}, **kw)


def qc(k, *, ket_luan="dat", commit_code=C1, **kw):
    return ghi(k, "qc.ket_qua", {"giao_id": "g-20261014-0009", "bead_id": "hr-1", "commit_code": commit_code,
                                 "commit_qc": "def5678", "ket_luan": ket_luan, "phat_hien": [], "ly_do": None}, **kw)


@pytest.fixture
def k(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def test_qc_dat_nap_ban_giao_cua_kiem_lai_cung_commit(k):
    nhan(k), bao(k)
    assert doc_ban_giao(kiem(k), k) is None                         # D8: kiểm lại đạt chưa đủ với bead thường
    sk = qc(k)
    dv = doc_ban_giao(sk, k)
    assert (dv.loai_nguon, dv.vai, dv.tat_dinh, dv.ep_nghiep_vu, dv.luc) == ("ban_giao", "coder", None, False, sk.luc)
    assert dv.nguon == {"loai": "ban_giao", "du_an": "hr", "bead_id": "hr-1", "su_kien_id": sk.id, "vai": "coder"}
    assert dv.van_ban.startswith("Bàn giao chính thức của bead hr-1 (vai coder, lượt 2), trạm kiểm lại và QC đạt ")
    assert ("Quyết định kỹ thuật:\n- Dùng `php artisan test --filter` thay phpunit\nHướng đã bỏ:\n"
            "- Gọi phpunit trực tiếp — vì thiếu bootstrap Laravel\nVướng mắc:\n- Seeder chậm 40 giây") in dv.van_ban
    assert "KHÔNG NẠP" not in dv.van_ban and "Đại ca chưa xác nhận" in dv.van_ban


def test_spike_kiem_lai_dat_khong_chay_lenh_la_nguon(k):
    nhan(k), bao(k)
    sk = kiem(k, ket_qua=[])
    dv = doc_ban_giao(sk, k)
    assert dv.nguon["su_kien_id"] == sk.id and "spike, trạm kiểm tài liệu đạt" in dv.van_ban
    assert doc_ban_giao(kiem(k, ket_qua=[]), k) is None             # kiểm lại lặp cùng phiếu: đã nạp


@pytest.mark.parametrize("ket_luan", ["tra_ve", "khong_cong_nhan", None])
def test_qc_khong_dat_khong_phai_nguon(k, ket_luan):
    nhan(k), bao(k), kiem(k)
    assert doc_ban_giao(qc(k, ket_luan=ket_luan), k) is None


def test_sai_tac_nhan_hoac_kiem_lai_khong_dat_khong_phai_nguon(k):
    nhan(k), bao(k), kiem(k)
    assert doc_ban_giao(qc(k, tac_nhan="tho/B/claude-2"), k) is None
    assert doc_ban_giao(kiem(k, ket_qua=[], tac_nhan="tho/B/claude-1"), k) is None
    assert doc_ban_giao(kiem(k, dat=False, ket_qua=[]), k) is None


def test_qc_lay_dung_kiem_lai_cua_commit_code(k):
    nhan(k), bao(k), kiem(k)
    g2 = "g-20261014-0008"
    nhan(k, gid=g2, luot=3, vai="qc"), bao(k, gid=g2, luot=3, ban_giao={**BG, "luot": 3})
    kiem(k, gid=g2, luot=3, commit="fff9999")
    assert "lượt 3" in doc_ban_giao(qc(k, commit_code="fff9999"), k).van_ban
    assert "lượt 2" in doc_ban_giao(qc(k), k).van_ban


def test_moi_ban_giao_mot_lan(k):
    nhan(k), bao(k), kiem(k)
    assert doc_ban_giao(qc(k), k) is not None
    assert doc_ban_giao(qc(k), k) is None                           # QC đạt lặp cùng commit code


def test_ban_giao_khong_co_bai_hoc_khong_phai_nguon(k):
    nhan(k), bao(k, ban_giao={**BG, "quyet_dinh": ["  "], "huong_da_bo": [], "vuong_mac": []}), kiem(k)
    assert doc_ban_giao(qc(k), k) is None


@pytest.mark.parametrize("sua", ["khong_bao", "khong_nhan", "vai_sai", "bao_gia_mao", "tam", "sai_schema",
                                 "lech_luot", "du_an_khac", "khong_kiem_lai", "kiem_lai_truot"])
def test_su_kien_doc(k, sua):
    if sua != "khong_nhan":
        nhan(k, vai="Coder" if sua == "vai_sai" else "coder", du_an="erp" if sua == "du_an_khac" else "hr")
    if sua != "khong_bao":
        bao(k, tac_nhan="tram/api" if sua == "bao_gia_mao" else "tho/B/claude-1",
            ban_giao={**BG, "loai": "tam"} if sua == "tam" else {**BG, "la": 1} if sua == "sai_schema" else BG,
            luot=1 if sua == "lech_luot" else 2, du_an="erp" if sua == "du_an_khac" else "hr")
    if sua != "khong_kiem_lai":
        kiem(k, dat=sua != "kiem_lai_truot")
    with pytest.raises(ValueError):
        doc_ban_giao(qc(k), k)


@pytest.mark.parametrize("loai, du_lieu, bead", [("qc.ket_qua", {"ket_luan": "dat"}, "hr-1"),
                                                 ("kiem.lai", {"dat": True, "ket_qua": [], "luot": 2}, "hr-1"),
                                                 ("qc.ket_qua", {"ket_luan": "dat", "commit_code": C1}, None)])
def test_thieu_truong_la_su_kien_doc(k, loai, du_lieu, bead):
    with pytest.raises(ValueError):
        doc_ban_giao(ghi(k, loai, du_lieu, bead=bead), k)


def test_cat_tung_muc_va_so_muc(k):
    dai = {**BG, "quyet_dinh": [f"Quyết định {i} " + "x" * 1000 for i in range(20)], "vuong_mac": []}
    nhan(k), bao(k, ban_giao=dai), kiem(k)
    dong = doc_ban_giao(qc(k), k).van_ban.splitlines()
    muc = [d for d in dong if d.startswith("- Quyết định")]
    assert len(muc) == TOI_DA_MUC and all(len(d) == DO_DAI_MUC + 2 and d.endswith("…") for d in muc)


def test_truoc_chi_nhin_cung_du_an_bead_va_truoc_su_kien(k):
    a = nhan(k)
    nhan(k, bead="hr-2"), nhan(k, du_an="erp")
    sk = kiem(k)
    nhan(k)                                                        # ghi SAU kiem.lai: không tính
    assert truoc(k, sk, "giao.nhan", lambda s: True).id == a.id


def test_phieu_moi_cung_sha_van_co_ban_giao_moi(k):
    nhan(k), bao(k), kiem(k)
    assert doc_ban_giao(qc(k), k) is not None
    ghi(k, "cot.tra_ve", {"gop_y": "Bổ sung bàn giao"})
    gid = "g-20261014-0010"
    nhan(k, gid=gid, luot=4)
    bao(k, gid=gid, luot=4, ban_giao={**BG, "luot": 4})
    kiem(k, gid=gid, luot=4)  # cùng C1, phiếu/lượt mới
    assert "lượt 4" in doc_ban_giao(qc(k), k).van_ban
    assert doc_ban_giao(qc(k), k) is None


def test_loi_schema_khong_lo_noi_dung_agent(k):
    nhan(k)
    bao(k, ban_giao={**BG, "truong_la": "SECRET-FAKE-ONLY-123"})
    kiem(k)
    with pytest.raises(ValueError) as e:
        doc_ban_giao(qc(k), k)
    assert str(e.value) == "bao.xong: bàn giao sai schema"
    assert "SECRET-FAKE" not in str(e.value)


@pytest.mark.parametrize("truong", ["quyet_dinh", "huong_da_bo", "vuong_mac", "muc_thu_9", "muc_dai"])
def test_ban_giao_co_bi_mat_bo_ca_nguon(k, truong):
    khoa = "".join(["gh", "p_", "Sentinel", "0" * 28])                 # GIẢ, ghép lúc chạy (D23)
    bg = {"quyet_dinh": {**BG, "quyet_dinh": [f"Dùng {khoa} để gọi API"]},
          "huong_da_bo": {**BG, "huong_da_bo": [{"huong": "Gọi thẳng", "vi_sao": f"lộ {khoa}"}]},
          "vuong_mac": {**BG, "vuong_mac": [f"Cấu hình cần {khoa}"]},
          "muc_thu_9": {**BG, "vuong_mac": ["Seeder chậm"] * TOI_DA_MUC + [khoa]},     # mục bị cắt bỏ vẫn quét
          "muc_dai": {**BG, "vuong_mac": ["chậm " * 100 + khoa]}}[truong]           # phần bị cắt vẫn quét
    nhan(k), bao(k, ban_giao=bg), kiem(k)
    with pytest.raises(LoiBiMat) as e:
        doc_ban_giao(qc(k), k)
    assert (e.value.loai_nguon, e.value.nhom) == ("ban_giao", {"khoa_da_biet": 1}) and "Sentinel" not in str(e.value)
