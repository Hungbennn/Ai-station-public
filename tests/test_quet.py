import json
from pathlib import Path
from types import SimpleNamespace as NS

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.chu import estop
from tram.cham_cot.quet import quet, xuat_bao_cao
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "ERP")
VAI = ("1", "VAI")
DUNG = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}


def b(id, title="Việc", status="open", labels=(), updated_at="2026-10-12T10:00:00Z"):
    return Bead(id, title, "", "", "", "", status, "task", tuple(labels), (), updated_at)


class BdGia:
    def __init__(self, beads):
        self.beads, self.goi = beads, []

    def tat_ca(self):
        return list(self.beads)

    def phien_ban(self, bead_id):  # 2a: bộ quét đọc lại version trước khi ghi (spec §5.6)
        return next(x.updated_at for x in self.beads if x.id == bead_id)

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None):
        self.goi.append((bead_id, list(them), list(bo)))


class ClientGia:
    def __init__(self):
        self.so_goi = 0
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.so_goi += 1
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(DUNG))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


def chay(tmp_path, beads, **kw):
    k = KhoSuKien(tmp_path / "sk.db")
    bd, c = BdGia(beads), ClientGia()
    return quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, **kw), bd, c, k


def test_chi_cham_trang_thai_mo_va_bo_nhan_bo_qua(tmp_path):
    beads = [b("hr-1"), b("hr-2", status="closed"), b("hr-3", labels=["cot:cho-review"]),
             b("hr-4", labels=["cot-khoa", "cot:ai-lam"]), b("hr-5", status="deferred")]
    bc, _, c, _ = chay(tmp_path, beads, tat_ca=True)
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and c.so_goi == 1


def test_che_do_thu_khong_ghi_va_khong_doi_moc(tmp_path):
    bc, bd, _, k = chay(tmp_path, [b("hr-1")], tat_ca=True, thu=True)
    assert bd.goi == [] and k.doc_moc("hr") is None and bc.thu


def test_ghi_that_va_moc(tmp_path):
    _, bd, _, k = chay(tmp_path, [b("hr-1", updated_at="2026-10-12T10:00:00Z")], tat_ca=True, thu=False)
    assert bd.goi[0][1] == ["cot:ai-lam"] and k.doc_moc("hr") == "2026-10-12T10:00:00Z"


def test_chi_cham_bead_doi_sau_moc(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi_moc("hr", "2026-10-12T10:00:00Z")
    bd, c = BdGia([b("hr-1"), b("hr-2", updated_at="2026-10-12T11:00:00Z")]), ClientGia()
    bc = quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, thu=False)
    assert [d.bead_id for d in bc.dong] == ["hr-2"]


def test_estop_thi_khong_chay(tmp_path):
    estop.bat("thử")
    try:
        bc, _, c, k = chay(tmp_path, [b("hr-1")], tat_ca=True)
        assert bc is None and c.so_goi == 0
    finally:
        estop.tat()


def test_gioi_han(tmp_path):
    bc, _, c, _ = chay(tmp_path, [b("hr-1"), b("hr-2"), b("hr-3")], tat_ca=True, gioi_han=2)
    assert len(bc.dong) == 2 and c.so_goi == 2


def test_bao_cao_markdown(tmp_path):
    bc, *_ = chay(tmp_path, [b("hr-1"), b("hr-2", title="hoa hồng")], tat_ca=True)
    md = xuat_bao_cao(bc)
    assert "hr-1" in md and "hr-2" in md and "Chạm hàng rào" in md and "Token" in md


def test_cli_estop(tram_home_tam):
    from tram.cli import main
    assert main(["chu", "estop", "--ly-do", "thử"]) == 0
    assert estop.dang_bat()
    assert main(["chu", "tiep-tuc"]) == 0
    assert not estop.dang_bat()


MOC = "2026-10-12T10:00:00Z"


def _kho_co_loi(tmp_path, so_loi):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi_moc("hr", MOC)
    for _ in range(so_loi):
        k.ghi("hr", "cham_cot.loi", {"loi": "API lỗi"}, bead_id="hr-1")
    return k


def test_bead_loi_luot_truoc_duoc_thu_lai_du_chua_doi(tmp_path):
    k = _kho_co_loi(tmp_path, 1)
    bd, c = BdGia([b("hr-1", updated_at=MOC)]), ClientGia()
    bc = quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, thu=False)
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and c.so_goi == 1
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 0


def test_bead_loi_lien_tiep_qua_nguong_van_bo_qua(tmp_path):
    k = _kho_co_loi(tmp_path, 3)
    bd, c = BdGia([b("hr-1", updated_at=MOC)]), ClientGia()
    bc = quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, thu=False)
    assert bc.dong == [] and c.so_goi == 0 and bc.bo_qua["loi_lien_tiep"] == 1
    assert "chua_doi" not in bc.bo_qua


class BdLoiKhoa(BdGia):
    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None):
        from tram.beads.bd import LoiBd
        if "cot-khoa" in them:
            raise LoiBd("bd update lỗi 1: khoá")
        super().cap_nhat_nhan(bead_id, them=them, bo=bo, ghi_chu=ghi_chu)


def test_loi_bd_khi_gan_khoa_khong_dung_ca_luot(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    bd, c = BdLoiKhoa([b("hr-1", labels=["cot:can-chot"]), b("hr-2")]), ClientGia()
    bc = quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, tat_ca=True, thu=False)
    assert [d.bead_id for d in bc.dong] == ["hr-2"]
    assert len(bc.loi) == 1 and bc.loi[0].startswith("hr-1:")
    assert k.moi_nhat("hr", "hr-1", "cham_cot.loi") is not None


def test_cli_estop_ghi_su_kien(tram_home_tam):
    from tram.cli import main
    from tram.su_kien.kho import mo_kho
    main(["chu", "estop", "--ly-do", "thử"])
    bat = mo_kho().gan_day("_tram", "estop.bat", 1)
    assert bat and bat[0].du_lieu == {"ly_do": "thử"} and bat[0].tac_nhan == "dai-ca"
    main(["chu", "tiep-tuc"])
    tat = mo_kho().gan_day("_tram", "estop.tat", 1)
    assert tat and tat[0].du_lieu == {} and tat[0].tac_nhan == "dai-ca"


def test_bo_qua_loi_lien_tiep_chi_ghi_su_kien_mot_lan(tmp_path):
    k = _kho_co_loi(tmp_path, 3)
    for _ in range(3):
        quet(DU_AN, bd=BdGia([b("hr-1", updated_at=MOC)]), kho=k, client=ClientGia(), vai=VAI, thu=False)
    assert len(k.gan_day("hr", "cham_cot.bo_qua", 10)) == 1


def test_loi_bd_lap_lai_dung_o_nguong(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    bd = BdLoiKhoa([b("hr-1", labels=["cot:can-chot"])])
    for _ in range(5):
        quet(DU_AN, bd=bd, kho=k, client=ClientGia(), vai=VAI, thu=False)
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 3


def test_bead_qua_nguong_loi_cu_hon_lan_loi_cuoi_van_bo_qua(tmp_path):
    k = _kho_co_loi(tmp_path, 3)
    bc = quet(DU_AN, bd=BdGia([b("hr-1", updated_at="2026-10-12T11:00:00Z")]), kho=k,
              client=ClientGia(), vai=VAI, thu=False)
    assert bc.dong == [] and bc.bo_qua["loi_lien_tiep"] == 1


def test_bead_qua_nguong_loi_doi_sau_lan_loi_cuoi_duoc_cham_lai(tmp_path):
    k = _kho_co_loi(tmp_path, 3)
    c = ClientGia()
    bc = quet(DU_AN, bd=BdGia([b("hr-1", updated_at="2099-01-01T00:00:00Z")]), kho=k,
              client=c, vai=VAI, thu=False)
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and c.so_goi == 1
    assert "loi_lien_tiep" not in bc.bo_qua


def test_cli_quet_khi_estop_khong_tao_client(monkeypatch, capsys):
    import tram.llm.claude
    from tram.cli import main

    def cam_goi():
        raise AssertionError("tao_client bị gọi khi estop")
    monkeypatch.setattr(tram.llm.claude, "tao_client", cam_goi)
    estop.bat("thử")
    assert main(["quet"]) == 0
    assert "estop đang bật" in capsys.readouterr().out


# --- Lát 2a: bỏ qua epic (#9), bd list lỗi → quet.loi ---

def test_bo_qua_epic(tmp_path):
    epic = Bead("hr-e", "Epic", "", "", "", "", "open", "epic", (), (), "2026-10-12T10:00:00Z")
    bc, _, c, _ = chay(tmp_path, [epic, b("hr-1")], tat_ca=True)
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and bc.bo_qua["epic"] == 1 and c.so_goi == 1


def test_in_progress_khong_phieu_van_cham(tmp_path):
    bc, *_ = chay(tmp_path, [b("hr-1", status="in_progress")], tat_ca=True)
    assert [d.bead_id for d in bc.dong] == ["hr-1"]


class BdListLoi(BdGia):
    def tat_ca(self):
        from tram.beads.bd import LoiBd
        raise LoiBd("bd list: JSON không đọc được (JSONDecodeError: ...)")


def test_bd_list_loi_ghi_quet_loi_va_khong_doi_moc(tmp_path):
    k, c = KhoSuKien(tmp_path / "sk.db"), ClientGia()
    bc = quet(DU_AN, bd=BdListLoi([]), kho=k, client=c, vai=VAI, thu=False)
    sk = k.gan_day("hr", "quet.loi", 1)
    assert sk and "JSON" in sk[0].du_lieu["loi"] and sk[0].bead_id is None
    assert bc is not None and bc.loi and bc.dong == [] and c.so_goi == 0
    assert k.doc_moc("hr") is None and k.gan_day("hr", "quet.xong", 1) == []
