"""Chuẩn bị cây mới sau cổng đóng; retry cùng phiếu không reset bản sửa hay cấp lại ACL."""
import os
from tram.cau_hinh.du_an import nap_du_an
from tram.chay_cli.lenh_claude import ghi_file_phieu
from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem
from tram.tho.quyen_cay_b import trao_quyen_b
from tram.tho.worktree import _them_exclude


def tao_noi_dung(nc, p, wt, hd, pr):
    import subprocess
    from tram.tho.chuan_bi import loai_khoi_git
    _them_exclude(wt, lambda a, **kw: subprocess.run(a, timeout=60, **kw))
    if os.path.lexists(wt / '.tram'):
        raise ValueError('Cây nguồn chứa .tram')
    (wt / '.tram').mkdir(mode=0o700)
    (wt / '.tram/goi.md').write_text(p.goi_ngu_canh, encoding='utf-8')
    if p.can_moi_truong_kiem:
        mt = nap_du_an(p.du_an).moi_truong_kiem
        if mt is None:
            raise LoiMoiTruongKiem('Thiếu môi trường kiểm')
        if p.du_an == "ben-station":
            from tram.quan_kiem.cap_deps import kiem_dich_env
            kiem_dich_env(mt.dich)
        loai_khoi_git(wt, mt.dich)
        chep_moi_truong_kiem(mt.file, wt, mt.dich)
    if p.du_an == 'ben-station':
        from tram.tho.deps_b import cap_deps_b
        cap_deps_b(wt, chay=nc.chay_lenh)
    hd.mkdir(mode=0o700)
    (hd / 'hang-doi.jsonl').touch(mode=0o600)
    ghi_file_phieu(hd, p, nho=bool(nc.ch.chay.nho_url))
    if getattr(pr, 'user', None):
        trao_quyen_b(wt, hd / 'hang-doi.jsonl', user=pr.user, chay=nc.chay_lenh)
