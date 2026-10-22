"""B dùng bundle root đã cài cho Uq; không đổi Uq, không chạy mã repo bằng UID quản lý."""
import subprocess
from tram.kiem.deps_manifest import KHOA_NGUON, bam, doc_manifest
from tram.kiem.deps_root import GOC_DEPS, doc_root
from tram.quan_kiem.cap_deps import cap_deps


def cap_deps_b(wt, *, chay=subprocess.run):
    if (wt / 'frontend').is_symlink() or any((wt / rel).is_symlink() for rel in KHOA_NGUON):
        raise ValueError('Nguồn dependency không được là symlink')
    nguon = {rel: bam((wt / rel).read_bytes()) for rel in KHOA_NGUON}
    ds = [doc_manifest(doc_root(p, 65536)) for p in sorted(GOC_DEPS.glob('*/manifest.json'))]
    ds = [m for m in ds if m['nguon'] == nguon]
    if len(ds) != 1:
        raise ValueError('Cần đúng một bundle root khớp lock ben-station')
    def chay_helper(argv, *, kill, **kw):
        # Helper -I/stdlb của runtime tin cậy, timeout do cap_deps áp; không chạy mã cây lượt.
        return chay(argv, **kw)
    cap_deps(wt, ds[0], boc=lambda a: a, kill=None, chay=chay_helper)


def boc_kiem_b(pc):
    from tram.tho.lenh_token_khe import boc_token
    def boc(argv):
        argv = boc_token(argv)
        if pc.p.du_an != 'ben-station':
            return pc.principal.boc(argv)
        return pc.principal.boc(['/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', *argv])
    return boc
