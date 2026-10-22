"""3C-D4/D5: cổng thật ghép thu hồi + quan sát; thu hồi theo UID (`test_thu_hoi_uid.py`) không gỡ lịch; hồ sơ Seatbelt
đã cài: `test_ho_so_cai_attest.py` (V2-5); tệp môi trường kiểm của mọi dự án phải kín. Không chạy lệnh hệ thống thật."""
import os
from functools import partial
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import dung_cong, env_kin, ho_so_cai, thu_hoi_theo_uid
from tram.giao_viec.launchd_kiem import doc_launchd
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, launchd, tep_ngoai, tien_trinh
from tram.kiem.kiem_python import kiem_prefix


def test_env_kin_doi_0600_cua_tram(tmp_path):
    f = tmp_path / "env.testing"
    f.write_text("DB=x\n")
    da = [SimpleNamespace(ten="hr", moi_truong_kiem=SimpleNamespace(file=f)),
          SimpleNamespace(ten="x", moi_truong_kiem=None)]
    f.chmod(0o640)
    with pytest.raises(LoiBanChep, match="0600"):
        env_kin(lambda: da)
    f.chmod(0o600)
    env_kin(lambda: da)
    assert os.stat(f).st_uid == os.getuid()


def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam, tmp_path):
    pk = tu_cach_ly("user:tram-kiem")
    c = dung_cong(pk, tmp_path, cac_du_an=list)
    assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is thu_hoi_theo_uid
    ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
    assert ham == [kiem_prefix, tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin, launchd]
    assert c.quan_sat[5].args == (tmp_path,)                       # V2-5: hồ sơ so với gốc bản chép HIỆN HÀNH
    assert c.quan_sat[7].args == (pk,) and c.quan_sat[7].keywords == {"doc": doc_launchd}     # 3C-D7: bộ đọc đã đo
    assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
