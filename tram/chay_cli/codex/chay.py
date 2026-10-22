"""Codex dưới principal, callback pid, budget và dọn cả cây con có hạn qua `vong_doi` (lát P1; S5/S6 chưa kiểm thật)."""
import hashlib
import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from tram.chay_cli.codex.luong import DocLuongCodex
from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.nguon import NguonHanMuc
from tram.phieu.mo_hinh import che_ma_giao
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
from tram.tho.mo_coi import kill_cuc_bo

LOI_DON = "Không dọn được nhóm CLI; dừng khe để kiểm principal"


class ChayCodex:
    def __init__(self, boc=lambda a: a, *, khe_id="", kill=kill_cuc_bo, khi_bat_dau=None,
                 khi_han_muc=None, tran_token_ra=None, popen=subprocess.Popen, cho_dung_giay=10.0):
        self.boc, self.khe_id, self.kill = boc, khe_id, kill
        self.khi_bat_dau, self.khi_han_muc = khi_bat_dau, khi_han_muc
        self.tran_token_ra, self.popen, self.cho_dung_giay = tran_token_ra, popen, cho_dung_giay

    def _doc(self, p, ghi, doc, dung, nguon, ma_giao):
        for tho in p.stdout:
            dong = che_ma_giao(tho.decode("utf-8", errors="replace"), ma_giao)
            ghi.write(dong.encode())
            ghi.flush()
            try:
                obj = json.loads(dong)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            doc.nap(obj)
            hm = nguon.doc_dong(obj, khe_id=self.khe_id, bay_gio=datetime.now(timezone.utc))
            if hm is not None and self.khi_han_muc:
                self.khi_han_muc(hm)
            if self.tran_token_ra is not None and doc.token_ra >= self.tran_token_ra:
                dung.set()

    def chay(self, argv: list[str], *, cwd: Path, env: dict[str, str], stdin: Path, log: Path,
             dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
        doc, t0, ma = DocLuongCodex(nguon), time.monotonic(), None
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(stdin, "rb") as vao, open(log, "wb") as ghi, so_huu(LOI_DON, cho_term=self.cho_dung_giay) as chu:
            try:                                            # sở hữu từ PID (`so_huu`): lỗi/ngắt trước khi thu hồi
                n = khoi_chay(self.boc(argv), kill=self.kill, chu=chu, popen=self.popen, cwd=cwd, env=env, stdin=vao,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except OSError as e:
                ghi.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
            else:
                if self.khi_bat_dau:
                    self.khi_bat_dau(n.p.pid)
                doc_t = threading.Thread(target=self._doc,
                                         args=(n.p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
                doc_t.start()
                ma, sach = cho_den_dung(n, dung, cho_term=self.cho_dung_giay)
                doc_t.join(timeout=self.cho_dung_giay)
                if not sach or doc_t.is_alive():
                    raise LoiThuHoi(LOI_DON)
        digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
        return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - t0) * 1000),
                           digest_log=digest)
