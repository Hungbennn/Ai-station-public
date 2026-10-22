"""Chứng cứ TỪNG nguồn lịch của kịch bản tái sinh S6 (V2-4, dot7-Q03; B01 vòng 1). Mỗi nguồn chạy trong một khối
riêng in đúng `probe:<nguồn>:bat-dau` rồi — SAU khi lệnh cài trả — `probe:<nguồn>:ket:<mã>`. Đầu ra của lệnh vào tệp
riêng trong `$TMPDIR` (không lẫn vào dòng dấu); bộ phân loại trong CHÍNH khối đó chỉ in MỘT mã lý do HỮU HẠN
`ly-do:<nguồn>:<mã>` (`LY_DO`) rồi xoá tệp — byte đầu ra không bao giờ ra stdout, vào kết quả hay bản ghi (INV-001).
Bên đọc chỉ nhận mã thuộc `LY_DO`; dòng lạ/thiếu/trùng → `khong-ro`, không chép. Mã lý do chỉ là GỢI Ý: Seatbelt chặn
hay thiếu công cụ/sai cú pháp chỉ phân biệt được bằng biên bản G4 (Đại ca xem log Sandbox + đối chứng dương; biên bản
ghi mã + kết luận, không dán đầu ra thô). Thiếu/trùng/sai thứ tự/không phải số/ngoài 0–255 = probe CHƯA HOÀN TẤT (đỏ)
— vắng dấu không bao giờ là "bị chặn"; mã khác 0 chỉ là "lệnh thất bại" (vàng)."""
import re

NGUON_RE = re.compile(r"[a-z]{1,16}")
LY_DO = {"eperm": "Operation not permitted", "eacces": "Permission denied", "khong-thay": "không thấy lệnh/tệp",
         "khac": "có đầu ra khác (không chép)", "trong": "không có đầu ra",
         "khong-ro": "dòng lý do thiếu/trùng/lạ (không chép)"}


def boc_probe(nguon: str, lenh: str) -> str:
    """Một khối nền cho MỘT nguồn. Không tạo được tệp đầu ra → khối dừng trước `ket` (đỏ), không giả mã thất bại.
    Phân loại theo thứ tự ưu tiên tăng dần (mẫu sau thắng): trong < khac < khong-thay < eacces < eperm."""
    if not NGUON_RE.fullmatch(nguon):
        raise ValueError(f"tên nguồn probe sai dạng: {nguon!r}")
    return (f'( echo probe:{nguon}:bat-dau; ra="${{TMPDIR:?}}/probe-{nguon}"; : >"$ra" || exit 0; '
            f'( {lenh} ) >"$ra" 2>&1; ma=$?; ld=trong; [ -s "$ra" ] && ld=khac; '
            "grep -qiE 'not found|no such file' \"$ra\" && ld=khong-thay; "
            "grep -qi 'permission denied' \"$ra\" && ld=eacces; "
            "grep -qi 'operation not permitted' \"$ra\" && ld=eperm; "
            f'rm -f "$ra"; echo ly-do:{nguon}:$ld; echo probe:{nguon}:ket:$ma ) &')


def doc_probe(log: str, nguon: str) -> int | None:
    dong = [s for s in log.splitlines() if s.startswith(f"probe:{nguon}:")]
    if len(dong) != 2 or dong[0] != f"probe:{nguon}:bat-dau":
        return None
    m = re.fullmatch(rf"probe:{re.escape(nguon)}:ket:([0-9]+)", dong[1])
    if m is None:
        return None
    ma = int(m.group(1))
    return ma if 0 <= ma <= 255 else None


def ly_do(log: str, nguon: str) -> str:
    """Mã lý do thuộc `LY_DO` — không bao giờ là chuỗi lấy từ log ngoài tập đó."""
    dong = [s[len(f"ly-do:{nguon}:"):] for s in log.splitlines() if s.startswith(f"ly-do:{nguon}:")]
    return dong[0] if len(dong) == 1 and dong[0] in LY_DO else "khong-ro"


def muc_lich(log: str, nguon: str) -> tuple[bool | None, str]:
    """(False, …) đỏ: chưa hoàn tất hoặc CÀI ĐƯỢC · (None, …) vàng: thất bại, chờ proof OS. Không bao giờ True."""
    ma = doc_probe(log, nguon)
    if ma is None:
        return False, "probe chưa hoàn tất (thiếu/trùng/hỏng dấu hoặc quá 20 s) — không chứng minh gì"
    if ma == 0:
        return False, "CÀI ĐƯỢC — hồ sơ không chặn"
    if nguon in {"submitcopy", "launchdcopy"} and ma in {126, 127}:
        return False, "bản chép lỗi exec/tìm lệnh — chưa tới IPC; sửa phép đo"
    if nguon in {"submitcopy", "launchdcopy"} and doc_probe(log, "execcopy") != 0:
        return False, "chưa chứng minh bản chép exec được — chưa kết luận IPC"
    ld = ly_do(log, nguon)
    return None, f"lệnh thất bại (mã {ma}, lý do {ld} — {LY_DO[ld]}) — chờ biên bản OS + đối chứng dương ở G4"
