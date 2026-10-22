import pytest
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import env_kin
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat


def test_du_an_khoa_ghi_van_phai_kin_env(tmp_path):
    env = tmp_path / "env.testing"
    env.write_text("GIA=1")
    env.chmod(0o644)
    cfg = tmp_path / "du-an"
    cfg.mkdir()
    (cfg / "b.yaml").write_text(
        f"ten: b\nduong_dan: /r/b\nhang_rao: {{}}\nbat_ghi: false\n"
        f"moi_truong_kiem:\n  file: {env}\n  dich: .env.testing\n")
    ds = lambda: cac_du_an_quan_sat(cfg)
    assert [x.ten for x in ds()] == ["b"]
    with pytest.raises(LoiBanChep):
        env_kin(ds)
    env.chmod(0o600)
    env_kin(ds)


def test_mot_yaml_hong_khong_duoc_bien_mat_khoi_inventory(tmp_path):
    (tmp_path / "x.yaml").write_text("ten: [")
    with pytest.raises(LoiBanChep):
        cac_du_an_quan_sat(tmp_path)


# --- Wiring (V2-3): ba đường dựng cổng THẬT phải lấy inventory quan sát, không phải danh sách giao việc. Chỉ gọi
# observer env lấy từ CongLuot; observer OS khác (ps/cron/launchd/hồ sơ) không chạy. Không sudo, không bd thật.
import os
from functools import partial
from types import SimpleNamespace

from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec import cong_that
from tram.giao_viec import kiem_principal as kp
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.noi_that import dung_bo_that
from tram.giao_viec.principal_kiem import PrincipalKiem

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))


class Dung(Exception):
    pass


@pytest.fixture
def repo_khoa(tmp_path, monkeypatch):
    """TRAM_REPO tạm: một dự án `bat_ghi: false` có env 0644 (tram-kiem đọc được env lượt khác)."""
    env = tmp_path / "env.khoa"
    env.write_text("GIA=1")
    env.chmod(0o644)
    (cfg := tmp_path / "repo" / "du-an").mkdir(parents=True)
    (cfg / "b.yaml").write_text(f"ten: b\nduong_dan: {tmp_path}\nbat_ghi: false\n"
                                f"moi_truong_kiem:\n  file: {env}\n  dich: .env.testing\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo"))
    return cfg


def env_obs(cong):
    q, = [q for q in cong.quan_sat if getattr(q, "func", None) is cong_that.env_kin]
    return q


def test_bo_that_khong_giao_du_an_khoa_nhung_cong_thay_env(repo_khoa, tmp_path, monkeypatch):
    bo = dung_bo_that(CauHinhGiaoViec(thu_muc_kiem=tmp_path / "k", principal_kiem=PK), CauHinhTram(),
                      thu_muc_du_an=repo_khoa)
    assert bo.cac_du_an() == []                               # khoá ghi: vẫn không giao
    from tram.cau_hinh.du_an import nap_du_an
    from tram.quan_kiem.client import CongTuXa
    from tram.quan_kiem.nguon import moi_truong
    assert isinstance(bo.cong, CongTuXa)                      # cổng production là Uq qua socket (bộ quản lý kiểm)
    mt = nap_du_an("b", thu_muc=repo_khoa).moi_truong_kiem    # env 0644 bị client từ chối trước khi gửi
    monkeypatch.setattr("tram.quan_kiem.nguon.loi_dich_trong_cay", lambda *a: None)   # bỏ kiểm cây git, giữ kiểm env
    with pytest.raises(ValueError, match="env-khong-kin"):
        moi_truong(tmp_path, "HEAD", mt)


def test_cli_con_dung_cong_voi_inventory_quan_sat(repo_khoa, tram_home_tam, tmp_path, monkeypatch):
    goi = []
    monkeypatch.setattr("tram.giao_viec.nghiem_thu_kiem.nghiem_thu", lambda *a, **kw: goi.append(kw) or [])
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (dau := tram_home_tam / "kiem-lai.dong").touch()
    a = SimpleNamespace(tai_sinh=False, cho=300.0, trong=True, dau_ino=dau.stat().st_ino, cha=os.getppid())
    assert lnt._trong(a, PK, tmp_path) == 0
    with pytest.raises(LoiBanChep):
        env_obs(goi[0]["cong"])()


def test_don_cua_cli_dong_cong_khi_env_du_an_khoa_ho(repo_khoa, tmp_path, monkeypatch):
    c = []

    def dung(pk, goc, cac_du_an):
        c.append(CongLuot(tmp_path / "c.json", thu_hoi=lambda: None, quan_sat=[partial(cong_that.env_kin, cac_du_an)]))
        return c[0]
    monkeypatch.setattr("tram.giao_viec.cong_that.dung_cong", dung)
    with pytest.raises(LoiBanChep):
        lnt._don(PK, tmp_path)
    assert c[0].trang_thai()["trang_thai"] == "dong"


def test_probe_mac_dinh_dung_cong_voi_inventory_quan_sat(repo_khoa, tmp_path, monkeypatch):
    c = []

    def dung(*a, **kw):
        c.append(cong_that.dung_cong(*a, **kw))
        raise Dung                                            # dừng trước mọi probe/sudo
    monkeypatch.setattr(kp, "dung_cong", dung)
    with pytest.raises(Dung):
        kp.kiem_principal(PK, tmp_path)
    with pytest.raises(LoiBanChep):
        env_obs(c[0])()
