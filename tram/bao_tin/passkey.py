"""D142/D149: hàng chờ bền riêng, giữ đủ ID và gom sau giờ yên lặng."""
from datetime import datetime, timezone
from tram.bao_tin.chong_on import trong_gio_yen_lang
from tram.bao_tin.telegram import LoiTelegram
from tram.passkey.kho import mo_kho, giao_dich

TEN = {'them':'Thêm thiết bị', 'thu-hoi':'Thu hồi thiết bị', 'khoi-phuc':'Khôi phục thiết bị'}


def gui_cho(path, gio_yen_lang, luc, gui):
    if path is None or not path.exists() or trong_gio_yen_lang(gio_yen_lang,luc):
        return 0
    with mo_kho(path) as db:
        ds = db.execute('SELECT id,loai,luc FROM tin WHERE gui=0 ORDER BY id LIMIT 20').fetchall()
    if not ds:
        return 0
    noi_dung = ['[tram] Thiết bị passkey:']
    for t in ds:
        gio = datetime.fromtimestamp(t['luc'],timezone.utc).isoformat(timespec='seconds')
        noi_dung.append(f"#{t['id']} · {TEN.get(t['loai'], 'Thay đổi thiết bị')} · {gio}")
    try:
        gui('\n'.join(noi_dung))  # dùng adapter Telegram hiện có, hạn 10 giây; không giữ khoá DB khi gửi
    except LoiTelegram:
        return 0
    with mo_kho(path) as db, giao_dich(db):
        db.executemany('UPDATE tin SET gui=1 WHERE id=?', [(t['id'],) for t in ds])
    return len(ds)  # crash sau gửi trước đánh dấu: có thể trùng cùng ID, không mất tin
