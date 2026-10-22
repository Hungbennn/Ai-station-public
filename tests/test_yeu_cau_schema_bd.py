import json
import pytest
from yeu_cau_gia import BI_MAT, LOGIN, MA, yc
from tram.beads.bd import Bd, LoiBd
from tram.yeu_cau.mau import dong_dau
from tram.yeu_cau.dich_vu import tiep_nhan
from tram.yeu_cau.so_nhan import SoNhan


@pytest.mark.parametrize("sua, bo", [({"id": None}, None), ({"id": ""}, None),
    ({"id": 7}, None), ({}, "issue_type"),
    ({"description": None}, None), ({"issue_type": []}, None)])
def test_schema_la_khong_duoc_coi_la_khong_thay(tmp_path, sua, bo):
    row = {"id": "hr-f1", "updated_at": "x", "issue_type": "feature",
           "description": dong_dau(MA)}
    row.update(sua)
    if bo:
        row.pop(bo)
    goi = []
    def runner(a):
        goi.append(a[2])
        return json.dumps([row]) if a[2] == "list" else "hr-f2"
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=runner), yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.ly_do) == ("chua_tao", "doc_bd_loi")
        assert goi == ["list"]
        assert so.lay(MA).trang_thai == "nhan"
    finally:
        so.close()


def test_schema_tot_marker_cu_khong_create(tmp_path):
    row = {"id": "hr-f1", "updated_at": "x", "issue_type": "feature",
           "description": dong_dau(MA)}
    goi = []
    def runner(a):
        goi.append(a[2])
        return json.dumps([row])
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=runner), yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.bead_id) == ("da_co", "hr-f1")
        assert goi == ["list"]
    finally:
        so.close()


# Ca bổ sung theo bullet 3 của V2-2: cùng Bd thật + runner JSON giả, zero create khi không kết luận được.
class RunnerJson:
    """`bd` giả mức argv/stdout: `ra_list` là stdout thô của `bd list --json`; `create` là id trả về hoặc lỗi ném ra."""

    def __init__(self, ra_list="[]", create="hr-f9"):
        self.ra_list, self.create, self.goi = ra_list, create, []

    def __call__(self, a):
        self.goi.append(a[2])
        if a[2] == "list":
            return self.ra_list
        if isinstance(self.create, Exception):
            raise self.create
        return self.create


def _dong(bid="hr-f1", **sua):
    return {"id": bid, "updated_at": "x", "issue_type": "feature", "description": dong_dau(MA), **sua}


# Dạng `bd list --all --json` thật (bd 1.2.2, điều phối đo 17/10): bỏ khoá description khi rỗng, có khoá lạ.
_THAT = {"id": "hr-a1", "title": "t", "status": "closed", "priority": 2, "issue_type": "task", "created_at": "x",
         "updated_at": "x", "dependency_count": 0, "dependent_count": 1}


@pytest.mark.parametrize("them, ket_qua, goi", [([], ("da_tao", "hr-f9"), ["list", "create"]),
    ([_dong("hr-f2", dependency_count=0)], ("da_co", "hr-f2"), ["list"]),
    ([_dong("hr-f2", description=None)], ("chua_tao", "doc_bd_loi"), ["list"])])
def test_dang_bd_that_thieu_khoa_description(tmp_path, them, ket_qua, goi):
    r = RunnerJson(json.dumps([_THAT, {**_THAT, "id": "hr-a2", "issue_type": "feature"}, *them]))
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=r), yc(), nguoi_gui=LOGIN)
        assert ((kq.trang_thai, kq.bead_id or kq.ly_do), r.goi) == (ket_qua, goi)
    finally:
        so.close()

@pytest.mark.parametrize("ra", ["{}", "[{}]", "null", json.dumps({"issues": [_dong()]})])
def test_container_la_khong_ket_luan_zero_create(tmp_path, ra):
    r = RunnerJson(ra)
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=r), yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.ly_do, r.goi) == ("chua_tao", "doc_bd_loi", ["list"])
    finally:
        so.close()


def test_trung_dau_hai_feature_khong_chon_bua_zero_create(tmp_path):
    r = RunnerJson(json.dumps([_dong("hr-f1"), _dong("hr-f2")]))
    so, bd = SoNhan(tmp_path / "so.db"), Bd(tmp_path, runner=r)
    try:
        for _ in range(2):
            kq = tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
            assert (kq.trang_thai, kq.ly_do, kq.bead_id) == ("khong_ro", "nhieu_feature", None)
        assert "create" not in r.goi
    finally:
        so.close()


def test_khong_ro_gap_schema_hong_roi_commit_tre_khong_tao_lai(tmp_path):
    r = RunnerJson(create=LoiBd("bd create hết giờ"))
    so, bd = SoNhan(tmp_path / "so.db"), Bd(tmp_path, runner=r)
    try:
        kq = tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.ly_do, so.lay(MA).trang_thai) == ("khong_ro", "chua_thay", "khong_ro")
        r.ra_list = json.dumps([_dong(id=None)])                  # schema hỏng lúc đối soát lại
        kq = tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.ly_do, so.lay(MA).trang_thai) == ("khong_ro", "doc_bd_loi", "khong_ro")
        r.ra_list = json.dumps([_dong("hr-f9")])                  # create treo của lần đầu commit trễ
        kq = tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.bead_id, so.lay(MA).bead_id) == ("da_co", "hr-f9", "hr-f9")
        assert r.goi.count("create") == 1
    finally:
        so.close()


def test_loi_adapter_khong_lo_json_tho(tmp_path):
    ra = json.dumps([_dong(id=None, description=dong_dau(MA) + "\n" + BI_MAT)])
    with pytest.raises(LoiBd) as e:
        Bd(tmp_path, runner=RunnerJson(ra)).tat_ca_yeu_cau()
    assert BI_MAT not in str(e.value) and e.value.__cause__ is None
