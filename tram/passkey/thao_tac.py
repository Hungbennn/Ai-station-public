"""Buộc mã thao tác với người + tuyến + payload; kết quả vẫn do ledger nghiệp vụ giữ."""
import hashlib
import json
from tram.passkey.kho import TuChoi


class XungDotMa(ValueError):
    pass


def rang_ma(db, u, path, than):
    ma = than.get('ma_thao_tac') or than.get('ma_yeu_cau')
    if not ma:  # schema nghiệp vụ sẽ báo thiếu mã; riêng POST đọc không cần mã
        return
    if not isinstance(ma,str) or len(ma) > 128:
        raise ValueError('Mã thao tác không hợp lệ')
    digest = hashlib.sha256(json.dumps([path,than],sort_keys=True,ensure_ascii=False,
                                      separators=(',',':')).encode()).hexdigest()
    cu = db.execute('SELECT * FROM thao_tac WHERE ma=?',(ma,)).fetchone()
    if cu:
        if cu['nguoi'] != u['id']:
            raise TuChoi('Không có quyền')
        if cu['bam'] != digest:
            raise XungDotMa('Mã thao tác đã dùng cho nội dung khác')
    else:
        db.execute('INSERT INTO thao_tac VALUES(?,?,?)',(ma,u['id'],digest))
