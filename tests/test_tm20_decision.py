"""Cửa đọc tươi phải dùng cùng luật blocks của luồng giao việc."""
from dataclasses import replace
from types import SimpleNamespace as NS
import pytest
from bd_gia import BdGia
from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.giao_viec.tu_merge_tuoi import doc_hien_hanh
from tram.phieu.kho import KhoPhieu


@pytest.mark.parametrize('state', ['open', 'missing', 'closed'])
def test_dependency_is_rechecked_at_merge(tmp_path, state):
    b = Bead.tu_json(dict(id='b', updated_at='2026-10-20', status='in_progress', issue_type='task'))
    b = replace(b, phu_thuoc=(PhuThuoc('decision-1', 'blocks'),))
    d = replace(b, id='decision-1', issue_type='decision', phu_thuoc=(), status=state)
    bd = BdGia([b] if state == 'missing' else [b, d])
    k = KhoPhieu(tmp_path / 'sk.db')
    try:
        assert (doc_hien_hanh(bd, k, NS(ten='a'), 'b') is not None) == (state == 'closed')
    finally:
        k.close()
