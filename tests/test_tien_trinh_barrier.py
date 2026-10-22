"""Con bỏ barrier không làm teardown treo; chỉ spawn con Python của chính test."""
import multiprocessing as mp

import pytest
from api_yeu_cau_gia import chay_api
from tien_trinh_thu import quan_ly_con
from yeu_cau_gia import BdTep, chay_mot

CTX = mp.get_context("spawn")


def bo_barrier(san_sang, dung):
    san_sang.set()
    dung.wait(timeout=30)


@pytest.mark.parametrize("target", [chay_mot, chay_api])
def test_con_khong_toi_barrier_duoc_thu_hoi(tmp_path, target):
    san_sang, dung, cho = CTX.Event(), CTX.Event(), CTX.Barrier(2)
    hang, ds = CTX.Queue(), []
    with quan_ly_con(ds, hang):
        bo = CTX.Process(target=bo_barrier, args=(san_sang, dung))
        ds.append(bo)
        bo.start()
        assert san_sang.wait(timeout=10)
        args = (str(tmp_path), cho, hang) if target is chay_api else (
            str(tmp_path / "sk.db"), str(tmp_path), cho, hang)
        p = CTX.Process(target=target, args=args)
        ds.append(p)
        p.start()
        p.join(15)
        assert p.exitcode is not None and p.exitcode != 0
        assert bo.is_alive()
        assert BdTep(tmp_path).so_lan_tao() == 0
        assert not (tmp_path / "beads.jsonl").exists()
    assert all(not p.is_alive() and p.exitcode is not None for p in ds)
