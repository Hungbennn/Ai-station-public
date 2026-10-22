"""Bản THẬT của Protocol `ChayCLI` (3a-1, spec 3 §7.2, §7.8) cho Claude Code — CHỜ SPIKE S2–S4 trước khi chạy thật.
Một lần chạy = một tiến trình con dưới principal của khe (`boc`), nhóm tiến trình riêng, stdin = gói của lần chạy,
stdout+stderr che `ma_giao` trước khi ghi vào log `~/.tram/log/chay/<giao_id>-<luot>-<lan>.jsonl` (digest gửi trong
`chay.xong`) và đọc từng dòng (`DocStream`). `dung` được đặt (dừng cứng/mềm, hết trần thời gian, vượt `token_ra`) hay
CLI thoát → thu hồi cả cây có hạn (`vong_doi`, lát P1) qua `kill` của principal (tiến trình quản lý khác user không kill
được con cháu của principal); không xác nhận thu hồi → `LoiThuHoi`, vòng khe dừng để kiểm principal."""
import hashlib
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

from tram.chay_cli.giao_dien import KetQuaChay
from tram.chay_cli.stream import DocStream
from tram.phieu.mo_hinh import che_ma_giao
from tram.han_muc.mo_hinh import HanMuc
from tram.han_muc.nguon import NguonHanMuc
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
from tram.tho.mo_coi import Kill, kill_cuc_bo

LOI_DON = "Không dọn được nhóm CLI; dừng khe để kiểm principal"


class ChayClaude:
    def __init__(self, boc: Callable[[list[str]], list[str]], *, khe_id: str, kill: Kill = kill_cuc_bo,
                 khi_bat_dau: Callable[[int], None] | None = None,
                 khi_han_muc: Callable[[HanMuc], None] | None = None,
                 tran_token_ra: int | None = None, cho_kill: float = 10.0, khoi: Callable = khoi_chay):
        self.boc, self.khe_id, self.kill, self.khi_bat_dau = boc, khe_id, kill, khi_bat_dau
        self.khi_han_muc, self.tran_token_ra, self.cho_kill, self.khoi = khi_han_muc, tran_token_ra, cho_kill, khoi

    @staticmethod
    def _doc(p: subprocess.Popen, f, doc: DocStream, ma_giao: str | None) -> None:
        for dong in p.stdout:
            sach = che_ma_giao(dong.decode("utf-8", "replace"), ma_giao)
            f.write(sach.encode("utf-8"))
            f.flush()
            doc.an(sach)

    def chay(self, argv: list[str], *, cwd: Path, env: dict[str, str], stdin: Path, log: Path,
             dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
        doc = DocStream(nguon, khe_id=self.khe_id, khi_han_muc=self.khi_han_muc, tran_token_ra=self.tran_token_ra,
                        khi_vuot=dung.set)
        log.parent.mkdir(parents=True, exist_ok=True)
        bat_dau, ma = time.monotonic(), None
        with open(stdin, "rb") as vao, open(log, "wb") as f, so_huu(LOI_DON, cho_term=self.cho_kill) as chu:
            try:                                            # sở hữu từ PID (`so_huu`): lỗi/ngắt trước khi thu hồi
                n = self.khoi(self.boc(argv), kill=self.kill, chu=chu, cwd=cwd, env=env, stdin=vao,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except OSError as e:
                f.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
            else:
                if self.khi_bat_dau:
                    self.khi_bat_dau(n.p.pid)
                doc_t = threading.Thread(target=self._doc, args=(n.p, f, doc, env.get("TRAM_MA_GIAO")), daemon=True)
                doc_t.start()
                ma, sach = cho_den_dung(n, dung, cho_term=self.cho_kill)   # kể cả con cháu giữ stdout sau khi CLI thoát
                doc_t.join(timeout=self.cho_kill)
                if not sach or doc_t.is_alive():
                    raise LoiThuHoi(LOI_DON)
        digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
        return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - bat_dau) * 1000),
                           digest_log=digest)
