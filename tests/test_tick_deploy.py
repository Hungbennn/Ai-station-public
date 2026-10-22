"""TM-3 (design D-6, D-9): pha thứ ba `vong_deploy` của vòng tick — luồng riêng `tram-giao-deploy`, khoá pha
`giao-deploy.lock`, lệnh `tram giao tick` chạy cả ba pha; estop vẫn đối soát chuỗi bỏ dở; một dự án lỗi không chặn."""
import subprocess
from types import SimpleNamespace

import tram.giao_viec.tick as tick
from giao_viec_gia import dung
from kho_phieu_gia import LUC
from tram.chu import estop
from tram.cli import main
from tram.giao_viec.luong import KHOA_DEPLOY, KHOA_GIT, chay_vong, giu_khoa
from tram.giao_viec.tick import mot_vong_tick, vong_deploy
from tram.tu_dong.luu import doc_trang_thai


def test_mot_vong_tick_chay_ca_pha_deploy_tru_khi_thu(tmp_path, monkeypatch):
    t, goi = dung(tmp_path), []
    (tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (tmp_path / "repo-tram" / "du-an" / "hr-codex.yaml").write_text("ten: hr-codex\nbat_ghi: true\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr(tick, "buoc_deploy",
                        lambda bo, kho, da, *, bat_ghi: goi.append((da.ten, bat_ghi(da.ten))) or {"x": 1})
    assert mot_vong_tick(t.bo)["x"] == 1
    assert goi == [("hr-codex", True)]                  # bat_ghi đọc lại du-an/<ten>.yaml mỗi lần hỏi (Q4)
    (tmp_path / "repo-tram" / "du-an" / "hr-codex.yaml").write_text("bat_ghi: [hong]\n")
    assert mot_vong_tick(t.bo)["x"] == 1 and goi[-1] == ("hr-codex", False)     # yaml sai → False (INV-005)
    assert "x" not in mot_vong_tick(t.bo, thu=True) and len(goi) == 2


def test_estop_van_doi_soat_chuoi_bo_do(tmp_path):
    """Trạm chết giữa chuỗi rồi estop bật: vẫn ghi "không rõ" và tạm dừng — không chạy lệnh nào."""
    t = dung(tmp_path)
    with t.kho.giao_dich():
        t.kho.ghi_su_kien("hr-codex", "deploy.bat_dau", {"ma_thao_tac": "dp-1", "commit": t.k.main, "commit_truoc": "",
                                                         "nguon": "tu_dong"}, luc=LUC, tac_nhan="tram/tu-deploy")
    estop.bat("thử")
    assert vong_deploy(t.bo, bat_ghi=lambda ten: True) == {"deploy_khong_ro": 1}
    assert doc_trang_thai(t.kho.db, "hr-codex").tam_dung_du_an.ly_do == "khong-ro"
    assert vong_deploy(t.bo, bat_ghi=lambda ten: True) == {}


def test_mot_du_an_loi_dem_loi(tmp_path, monkeypatch):
    t = dung(tmp_path)
    monkeypatch.setattr(tick, "buoc_deploy",
                        lambda *a, **k: (_ for _ in ()).throw(subprocess.CalledProcessError(128, ["git"])))
    assert vong_deploy(t.bo) == {"loi": 1}


def test_khoa_pha_deploy_rieng(tmp_path):
    with giu_khoa(KHOA_DEPLOY) as duoc:
        assert duoc and chay_vong(KHOA_DEPLOY, lambda: {"x": 1}) is None
        assert chay_vong(KHOA_GIT, lambda: {"x": 1}) == {"x": 1}  # kiểm lại không phải chờ deploy


def test_cli_tick_ba_pha(tmp_path, monkeypatch, capsys):
    t = dung(tmp_path)
    t.bo.cac_du_an = lambda: []
    monkeypatch.setattr("tram.giao_viec.lenh._bo", lambda: (SimpleNamespace(bat=True), t.bo))
    assert main(["giao", "tick"]) == 0
    ra = capsys.readouterr().out
    assert "pha git: không có việc" in ra and "pha deploy: không có việc" in ra


def test_ghep_tc_giu_callback_bat_ghi_tuoi(tmp_path, monkeypatch):
    t = dung(tmp_path)
    nut, doc, thay = [True], [], []

    def bat_ghi(ten):
        doc.append((ten, nut[0]))
        return nut[0]

    def buoc(bo, kho, da, *, bat_ghi):
        assert callable(bat_ghi)
        assert doc == []                         # vòng ngoài không được chụp bool trước khi vào deploy
        thay.append(bat_ghi(da.ten))
        nut[0] = False                          # giả lập đổi khoá trong lúc chuẩn bị worktree
        thay.append(bat_ghi(da.ten))
        return {"da_kiem_cua": 1}

    monkeypatch.setattr(tick, "buoc_deploy", buoc)
    assert vong_deploy(t.bo, bat_ghi=bat_ghi) == {"da_kiem_cua": 1}
    assert thay == [True, False]
    assert doc == [("hr-codex", True), ("hr-codex", False)]
