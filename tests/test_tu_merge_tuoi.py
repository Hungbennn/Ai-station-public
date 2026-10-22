"""V2-C1: thay dữ kiện khi đang đọc PR/cây Git, đi qua caller thật."""
from dataclasses import replace

import pytest

from su_kien_gia import ds, sk
from test_tu_merge import cot_3_co_pr, dung_tu_merge, merge_goi, tm
from test_tu_merge_spec import F, dung_spec
from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import HangRao
from tram.giao_viec.tick import mot_vong_tick


def doi_code(t, cach):
    b = t.g.beads['hr-1']
    if cach == 'tieu_chi':
        t.g.beads[b.id] = replace(b, acceptance_criteria='- Tiêu chí mới')
    elif cach == 'khoa_cot':
        t.g.beads[b.id] = replace(b, labels=(*b.labels, 'cot-khoa'))
    elif cach == 'seal':
        sk(t.kho, 'cot.tra_ve', {})
    elif cach == 'qc':
        q = next(s for s in reversed(ds(t.kho)) if s.loai == 'qc.ket_qua')
        sk(t.kho, q.loai, {**q.du_lieu, 'ket_luan': 'khong_dat'})
    elif cach == 'kiem_lai':
        k = next(s for s in reversed(ds(t.kho)) if s.loai == 'kiem.lai')
        sk(t.kho, k.loai, {**k.du_lieu, 'dat': False})
    elif cach == 'schema':
        t.g.beads[b.id] = replace(b, description='Xoá dữ liệu bằng drop table')
    elif cach == 'pr':
        p = next(s for s in reversed(ds(t.kho)) if s.loai == 'pr.mo')
        sk(t.kho, p.loai, {**p.du_lieu, 'pr': 2})
    elif cach == 'dong':
        t.g.beads[b.id] = replace(b, status='closed')
    elif cach == 'mat_bead':
        t.g.beads.pop(b.id)
    elif cach == 'loi_doc':
        def loi():
            raise LoiBd('nội dung không được ghi vào sự kiện')
        t.g.tat_ca = loi


@pytest.mark.parametrize('luc_doi', ['pr', 'cay'])
@pytest.mark.parametrize('cach', ['tieu_chi', 'khoa_cot', 'seal', 'qc', 'kiem_lai', 'schema', 'pr', 'dong', 'mat_bead', 'loi_doc'])
def test_code_doc_tuoi_sau_lenh_cham(tmp_path, monkeypatch, cach, luc_doi):
    from tram.giao_viec import tu_merge_rao
    from test_tu_merge import doi

    t, gh, _ = dung_tu_merge(tmp_path, monkeypatch,
                              hang_rao={'schema': HangRao(tu_khoa=('drop table',))})
    cot_3_co_pr(t, gh)
    doi(t, lenh_deploy='sh kiem.sh')
    da_doi = []

    def doi_mot_lan():
        if not da_doi:
            da_doi.append(True)
            doi_code(t, cach)
    if luc_doi == 'pr':
        gh.khi_xem = lambda so: doi_mot_lan()
    else:
        doc = tu_merge_rao._cay

        def doc_va_doi(*args):
            ra = doc(*args)
            doi_mot_lan()
            return ra
        monkeypatch.setattr(tu_merge_rao, '_cay', doc_va_doi)
    mot_vong_tick(t.bo)
    assert da_doi and merge_goi(gh) == []
    assert tm(t, 'tu_merge.bat_dau') == []
    assert tm(t, 'tu_merge.cho')
    assert 'nội dung không được' not in str(tm(t))


@pytest.mark.parametrize('luc_doi', ['pr', 'cay'])
@pytest.mark.parametrize('cach', ['tieu_chi', 'khoa_cot', 'duyet', 'pr', 'dong', 'loi_doc'])
def test_spec_doc_tuoi_sau_lenh_cham(tmp_path, monkeypatch, cach, luc_doi):
    from tram.giao_viec import tu_merge_rao
    from tram.tu_dong.luu import doi_cai_dat
    k, kho, gh, sha, chay = dung_spec(tmp_path, monkeypatch)
    chay()

    doi_cai_dat(kho.db, 'hr-codex', lambda c: replace(c, lenh_deploy='sh kiem.sh'), tac_nhan='dai-ca/dashboard')
    da_doi = []

    def doi(so):
        if da_doi:
            return
        da_doi.append(True)
        if cach == 'tieu_chi':
            chay.bd.beads[F.id] = replace(F, acceptance_criteria='- Mới')
        elif cach == 'khoa_cot':
            chay.bd.beads[F.id] = replace(F, labels=(*F.labels, 'cot-khoa'))
        elif cach == 'dong':
            chay.bd.beads[F.id] = replace(F, status='closed')
        elif cach == 'duyet':
            sk(kho, 'spec.duyet', {'commit': 'e' * 40}, bead_id=F.id)
        elif cach == 'pr':
            p = next(s for s in reversed(ds(kho, F.id)) if s.loai == 'pr.mo')
            sk(kho, p.loai, {**p.du_lieu, 'pr': 2}, bead_id=F.id)
        else:
            def loi():
                raise LoiBd('đọc thất bại')
            chay.bd.tat_ca = loi
    if luc_doi == 'pr':
        gh.khi_xem = doi
    else:
        doc = tu_merge_rao._cay

        def doc_va_doi(*args):
            ra = doc(*args)
            doi(1)
            return ra
        monkeypatch.setattr(tu_merge_rao, '_cay', doc_va_doi)
    chay()
    assert da_doi and merge_goi(gh) == []
    assert not [s for s in ds(kho, F.id) if s.loai == 'tu_merge.bat_dau']
    assert [s for s in ds(kho, F.id) if s.loai == 'tu_merge.cho']
