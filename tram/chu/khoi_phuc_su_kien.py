"""`tram chu khoi-phuc-su-kien <bản>` (bs-2bd.1.17): thay nội dung `~/.tram/su-kien.db` bằng một bản sao lưu.

1–2. Đọc bản qua fd vào bộ nhớ, dựng ĐÚNG bản sẽ chép và kiểm chính bản đó (`kiem_ban_su_kien.ban_ap`).
3. Khoá bảo trì: mở kho qua `mo_da_kiem` (chuỗi cha tin được, không liên kết, định danh đối chiếu lại), rồi
   `locking_mode=EXCLUSIVE` + `BEGIN EXCLUSIVE` trên kho WAL (chờ tối đa `HAN_KHOA_GIAY`) — ở WAL, khoá này CHỈ lấy được
   khi không tiến trình nào khác đang mở kho (api, quet, bao-tin, sao-luu, memory `nho`…); còn ai mở → từ chối.
4. Trong khoá: chụp kho hiện tại (có hạn) → `sao-luu/truoc-khoi-phuc-<lúc>.db` độc quyền 600 (không ghi đè bản nào).
5. Trong khoá: online backup bản → kho, từng `SO_TRANG_AP` trang, CÓ HẠN `HAN_AP_GIAY` (quá hạn giữa các bước →
   SQLite hoàn tác giao dịch ghi của đích). Ba loại kết quả tách bạch, mỗi loại đều KIỂM LẠI bằng vân tay chứ không
   đoán: lỗi trước khi thay → "chưa đổi gì"; lỗi trong lúc thay → so kho với ảnh chụp ở bước 4: trùng → "kho giữ
   nguyên", khác/không đọc được → "KHÔNG còn như trước", chỉ đường lui; thay xong mà kho khác bản → chỉ đường lui.
Lệnh không tự dừng dịch vụ (kế hoạch nhắc `DUNG_TRUOC`); bước 3 kiểm thật. Thông báo lỗi không chép đường dẫn."""
import sqlite3
import time
from pathlib import Path

from tram.chu.cau_truc_su_kien import van_tay, van_tay_anh
from tram.chu.kiem_ban_su_kien import LoiKhoiPhuc, ban_ap, doc_ban, kiem_ban
from tram.duong_dan import bay_gio, tram_home
from tram.su_kien import ban_sao
from tram.su_kien.mo_an_toan import LoiQuyenKho, mo_da_kiem

DUNG_TRUOC = "tram chu go-dich-vu --dich-vu api --dich-vu quet --dich-vu bao-tin --dich-vu sao-luu --dich-vu nho"
HAN_KHOA_GIAY = 2.0
HAN_AP_GIAY = ban_sao.HAN_SAO_LUU_GIAY
SO_TRANG_AP = ban_sao.SO_TRANG
_dong_ho = time.monotonic


def _ap_ban(nguon: sqlite3.Connection, db: sqlite3.Connection) -> None:
    het = _dong_ho() + HAN_AP_GIAY

    def tien_do(trang_thai: int, con_lai: int, tong: int) -> None:
        if trang_thai != sqlite3.SQLITE_DONE and _dong_ho() > het:
            raise ban_sao.LoiBanSao("chép bản vào kho quá hạn")
    nguon.backup(db, pages=SO_TRANG_AP, progress=tien_do)


def _khoa_bao_tri(kho: Path) -> sqlite3.Connection:
    co_san = kho.exists()
    try:
        db = mo_da_kiem(kho, timeout=HAN_KHOA_GIAY, isolation_level=None)
    except LoiQuyenKho as e:
        raise LoiKhoiPhuc(str(e)) from None
    try:
        db.execute("PRAGMA locking_mode=EXCLUSIVE")
        db.execute("BEGIN EXCLUSIVE")
        che_do = db.execute("PRAGMA journal_mode").fetchone()[0]
        db.execute("COMMIT")                         # chế độ EXCLUSIVE: khoá vẫn giữ sau COMMIT
    except sqlite3.OperationalError:
        db.close()
        raise LoiKhoiPhuc(f"Còn tiến trình đang mở su-kien.db — dừng trước: {DUNG_TRUOC}") from None
    if co_san and che_do != "wal":
        db.close()
        raise LoiKhoiPhuc("su-kien.db không ở chế độ WAL — không chứng minh được không còn ai mở, không khôi phục")
    return db


def khoi_phuc(ten: str, kho: Path, thu_muc: Path, *, luc: str) -> Path:
    """Trả đường bản sao lưu của kho TRƯỚC khi thay. Mọi lỗi → `LoiKhoiPhuc` nói rõ kho đã đổi hay chưa."""
    nguon = ban_ap(doc_ban(ten, thu_muc, kho))
    try:
        db = _khoa_bao_tri(kho)
        try:
            try:
                anh = ban_sao.chup(db)
                truoc = ban_sao.ghi_doc_quyen(thu_muc, f"truoc-khoi-phuc-{luc.replace('-', '').replace(':', '')}", anh)
            except ban_sao.LoiBanSao as e:
                raise LoiKhoiPhuc(f"Không sao lưu được kho hiện tại ({e}) — chưa đổi gì") from None
            lui = f"đường lui: tram chu khoi-phuc-su-kien {truoc.name}"
            try:
                _ap_ban(nguon, db)
            except (sqlite3.Error, ban_sao.LoiBanSao):
                try:
                    giu = van_tay(db) == van_tay_anh(anh)
                except sqlite3.Error:
                    giu = False
                raise LoiKhoiPhuc(f"Chép bản vào kho lỗi — kho giữ nguyên (đã kiểm lại); bản trước khôi phục: "
                                  f"{truoc.name}" if giu else f"Chép bản vào kho lỗi giữa chừng — kho KHÔNG còn như "
                                  f"trước; {lui}") from None
            try:
                khop = van_tay(db) == van_tay(nguon)
            except sqlite3.Error:
                khop = False
            if not khop:
                raise LoiKhoiPhuc(f"Kho sau khôi phục không khớp bản — {lui}")
            return truoc
        finally:
            db.close()
    finally:
        nguon.close()


def _lenh(args) -> int:
    thu_muc, kho, ten = tram_home() / "sao-luu", tram_home() / "su-kien.db", Path(args.ban).name
    try:
        kiem_ban(doc_ban(ten, thu_muc, kho))
    except LoiKhoiPhuc as e:
        print(e)
        return 2
    print(f"Sẽ: khoá bảo trì su-kien.db (từ chối nếu còn tiến trình mở) → sao lưu kho hiện tại vào "
          f"sao-luu/truoc-khoi-phuc-…db → thay bằng {ten} → đọc lại kiểm khớp.\nDừng các dịch vụ TRƯỚC: {DUNG_TRUOC}; "
          "xong thì cài lại (tram chu cai-dat).\nSự kiện ghi sau thời điểm của bản sẽ mất khỏi kho (vẫn còn trong "
          "bản truoc-khoi-phuc).")
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        print(f"Đã khôi phục su-kien.db. Bản trước khôi phục: {khoi_phuc(ten, kho, thu_muc, luc=bay_gio()).name}")
    except LoiKhoiPhuc as e:
        print(e)
        return 3
    return 0


def them_lenh_khoi_phuc(chu) -> None:
    k = chu.add_parser("khoi-phuc-su-kien", help="Khôi phục ~/.tram/su-kien.db từ bản trong ~/.tram/sao-luu")
    k.add_argument("ban", help="Tên file bản sao lưu trong ~/.tram/sao-luu")
    k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ dùng khi Đại ca đã đọc kế hoạch)")
    k.set_defaults(ham=_lenh)
