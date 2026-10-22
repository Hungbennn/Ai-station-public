"""Một hạn worker 3300 s, thu hồi 240 s; giữ dấu bền nếu bất kỳ bước nào chưa rõ."""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from tram.kiem.gui_tin import gop_kill, kill_cuc_bo
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import khoi_chay


def chay_con(mode, p, han, huy, *, cfg, pk, khoi=khoi_chay, dong_ho=time.monotonic):
    chu, het = [], dong_ho() + han
    try:
        n = khoi([cfg['python'], '-I', cfg['entry'], mode, str(p)], chu=chu,
                 kill=gop_kill(pk.kill_nhom, kill_cuc_bo), stdin=subprocess.DEVNULL,
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 env={'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': cfg['home'],
                      'TRAM_HOME': cfg['home']}, cwd='/var/empty')
        while (ma := n.cho(0.1)) is None:
            if huy() or dong_ho() >= het:
                raise TimeoutError('huy-hoac-het-han')
        if ma != 0 or huy():
            raise OSError('luot-loi')
    finally:
        if not thu_hoi_con_lai(chu):
            raise OSError('thu-hoi-chua-ro')


def thuc_thi(d, nguon, env, huy, *, cfg, pk, thu_hoi=None, khoi=khoi_chay, dong_ho=time.monotonic):
    home, dau = Path(cfg['home']), Path(cfg['home']) / 'kiem-lai.dong'
    os.close(os.open(dau, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    with tempfile.TemporaryDirectory(dir=home, prefix='nhan-') as tam:
        p = Path(tam)
        (p / 'yeu-cau.json').write_text(json.dumps(d))
        (p / 'nguon').write_bytes(nguon)
        (p / 'env').write_bytes(env)
        try:
            chay_con('luot', p, 3300, huy, cfg=cfg, pk=pk, khoi=khoi, dong_ho=dong_ho)
            r = json.loads((p / 'ket-qua.json').read_bytes())
        except BaseException:
            chay_con('don', d['id'], 240, lambda: False, cfg=cfg, pk=pk, khoi=khoi, dong_ho=dong_ho)
            raise
        dau.unlink()
        return r


def mo_that(*, cfg, pk):
    chay_con('mo', '0'*32, 240, lambda: False, cfg=cfg, pk=pk)
    (Path(cfg['home']) / 'kiem-lai.dong').unlink(missing_ok=True)
