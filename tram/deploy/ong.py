"""Đọc ống không chặn; chỉ giữ tối đa một dòng 16 KiB, ghi tối đa 1 MiB đã che mỗi bước."""
import os

from tram.nho.bi_mat import quet

DONG_CHE = "[trạm: đã che một dòng có dấu hiệu bí mật]"
TRAN_DONG = 16384
TRAN_LOG = 1024 * 1024


class Loc:
    def __init__(self, ghi):
        self.ghi, self.dem, self.cat = ghi, 0, 0
        self.do, self.bo = bytearray(), False

    def dong(self):
        text = self.do.decode("utf-8", "replace")
        sach = "[trạm: bỏ một dòng dài quá giới hạn]" if self.bo else DONG_CHE if quet([text]) else text
        phan = (sach + "\n").encode()
        if self.dem + len(phan) <= TRAN_LOG:
            self.ghi(phan)
            self.dem += len(phan)
        else:
            self.cat += len(phan)
        self.do.clear()
        self.bo = False

    def nhan(self, phan):
        for i, doan in enumerate(phan.split(b"\n")):
            if i:
                self.dong()
            if not self.bo:
                if len(self.do) + len(doan) > TRAN_DONG:
                    self.do.clear()
                    self.bo = True
                else:
                    self.do.extend(doan)

    def doc(self, fd):
        # Mỗi nhịp có trần: output vô hạn không làm đói kiểm timeout/ngắt.
        for _ in range(16):
            try:
                phan = os.read(fd, 8192)
            except BlockingIOError:
                return
            if not phan:
                return
            self.nhan(phan)

    def xong(self):
        if self.do or self.bo:
            self.dong()
