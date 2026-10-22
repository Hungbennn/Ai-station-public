"""Nhận kết quả dưới BEGIN IMMEDIATE; phiếu đã bị thay không được công bố pass muộn."""
from tram.giao_viec.pipeline import sha_code_hop_le
from tram.giao_viec.su_kien import cua_so, su_kien_bead, da_co


def ghi_ket_qua(kho, da, p, sha, d, luc):
    with kho.giao_dich():
        moi = kho.lay(p.giao_id)
        if moi is None or moi.ket_thuc in ('thu_hoi', 'het_han') or \
                kho.luot_hien_hanh(da.ten, p.bead_id) != p.luot or \
                sha_code_hop_le(cua_so(su_kien_bead(kho, da.ten, p.bead_id))) != sha:
            return 'luot-cu'
        if not da_co(kho, da.ten, 'kiem.lai', {'giao_id': p.giao_id, 'commit': sha}):
            kho.ghi_su_kien(da.ten, 'kiem.lai', d, bead_id=p.bead_id, luc=luc, tac_nhan='tram/giao-viec')
    return 'kiem_lai'
