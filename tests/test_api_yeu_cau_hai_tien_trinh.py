"""Hai tiến trình tram-api THẬT (mỗi tiến trình một app) dùng chung sổ SQLite tạm và `bd` giả (plan 4d 4D-2): cùng
yêu cầu gửi đồng thời vào hai tiến trình chỉ sinh MỘT lần `bd create`."""
import multiprocessing as mp

from api_yeu_cau_gia import chay_api, mo_app, tao
from tien_trinh_thu import quan_ly_con
from yeu_cau_gia import BdTep

CTX = mp.get_context("spawn")


def test_hai_tien_trinh_tram_api_cung_yeu_cau_chi_mot_feature(tmp_path):
    cho, hang = CTX.Barrier(2), CTX.Queue()
    ds = []
    with quan_ly_con(ds, hang):
        for _ in range(2):
            p = CTX.Process(target=chay_api, args=(str(tmp_path), cho, hang))
            ds.append(p)
            p.start()
        for p in ds:
            p.join(60)
        assert [p.exitcode for p in ds] == [0, 0]
        ma = sorted(hang.get(timeout=5) for _ in ds)
        assert ma.count(201) == 1 and set(ma) <= {200, 201, 202}
        assert BdTep(tmp_path).so_lan_tao() == 1
        app, _, _, _ = mo_app(tmp_path)
        r = tao(app)
        assert (r.status, r.json()["trang_thai"], r.json()["bead_id"]) == (200, "da_co", "hr-f1")
