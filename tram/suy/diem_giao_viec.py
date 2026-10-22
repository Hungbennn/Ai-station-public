"""Hai chỉ số của bảng điểm thợ cần sự kiện phần 4 — theo chữ spec 4 §12 (D13) và các câu Đại ca chốt D25–D29
(15/10). Tính lúc đọc (Q12) theo khe, cho phiếu `code` (vai `coder`); lọc theo dự án và lúc cấp phiếu (D14, D28).

*Qua lần đầu* = số phiếu `code` mà `kiem.lai` đầu tiên cho SHA của phiếu đạt VÀ `qc.ket_qua` đầu tiên cho commit
đó, ghi SAU lần kiểm lại ấy (D26), là `dat` ÷ số phiếu `code` kết thúc `xong`.
*Bị trả về* (D27) = mỗi lần `bead.vao_cot_3` là một mẫu của khe giữ phiếu code trong bằng chứng (`giao_id_code`);
mẫu bị trả về khi có `cot.tra_ve` của bead trước lần vào cột 3 kế tiếp ÷ số mẫu."""
import json
import sqlite3
from collections import defaultdict

LOAI = ("giao.cong_bo", "kiem.lai", "qc.ket_qua", "bead.vao_cot_3", "cot.tra_ve")


def dieu_kien_phieu(du_an: str | None, tu: str | None) -> tuple[str, list]:
    """Mảnh WHERE cho bảng `phieu`. D29: dự án = `phieu.du_an`. D28: thuộc cửa sổ khi `cap_luc` ≥ `tu` (UTC)."""
    sql, tham = "", []
    if du_an:
        sql, tham = sql + " AND du_an = ?", tham + [du_an]
    if tu:
        sql, tham = sql + " AND cap_luc >= ?", tham + [tu]
    return sql, tham


def doc_phieu_code(db: sqlite3.Connection, du_an: str | None = None, tu: str | None = None) -> list[tuple]:
    """[(giao_id, khe_id, du_an, bead_id, luot, ket_thuc)] của phiếu `code`. D29: "kết thúc xong" = `phieu.ket_thuc`."""
    loc, tham = dieu_kien_phieu(du_an, tu)
    return db.execute("SELECT giao_id, khe_id, du_an, bead_id, luot, ket_thuc FROM phieu"
                      f" WHERE json_extract(noi_dung, '$.buoc') = 'code'{loc} ORDER BY giao_id", tham).fetchall()


def doc_su_kien(db: sqlite3.Connection, du_an: str | None = None) -> dict[str, list[tuple]]:
    """{loai: [(id, du_an, bead_id, du_lieu), …]} theo thứ tự ghi. Sự kiện đi theo phiếu, không lọc thời gian (D28)."""
    loc, tham = (" AND du_an = ?", [du_an]) if du_an else ("", [])
    ra: dict[str, list[tuple]] = defaultdict(list)
    for i, a, b, loai, d in db.execute(
            f"SELECT id, du_an, bead_id, loai, du_lieu FROM su_kien WHERE loai IN ({','.join('?' * len(LOAI))}){loc}"
            " ORDER BY id", (*LOAI, *tham)):
        ra[loai].append((i, a, b, json.loads(d)))
    return ra


def _dau_tien(ds: list[tuple], du_an: str, bead_id: str, khoa: str, sha: str, sau: int = 0) -> tuple | None:
    """(id, du_lieu) ghi sớm nhất cùng dự án + bead, có `khoa` = `sha`, id lớn hơn `sau`."""
    return next(((i, d) for i, a, b, d in ds if i > sau and (a, b) == (du_an, bead_id) and d.get(khoa) == sha), None)


def qua_lan_dau(phieu: list[tuple], sk: dict[str, list[tuple]]) -> dict[str, tuple[int, int]]:
    """{khe_id: (tử, mẫu)}. D25: SHA của phiếu = `commit` của `giao.cong_bo` cùng dự án, bead và `luot` (bản sau cùng);
    chưa công bố → không vào tử, vẫn ở mẫu. D26: `kiem.lai` sớm nhất có đúng SHA, rồi `qc.ket_qua` sớm nhất cho cùng
    commit ghi sau lần kiểm lại ấy. D29: tử không đòi phiếu `xong`."""
    cong_bo = {(a, b, d.get("luot")): d.get("commit") for _, a, b, d in sk["giao.cong_bo"]}
    dem: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for _, khe, a, b, luot, ket_thuc in phieu:
        x = dem[khe]
        x[1] += ket_thuc == "xong"
        if (sha := cong_bo.get((a, b, luot))) is None:
            continue
        kl = _dau_tien(sk["kiem.lai"], a, b, "commit", sha)
        qc = kl and _dau_tien(sk["qc.ket_qua"], a, b, "commit_code", sha, sau=kl[0])
        x[0] += bool(qc and kl[1].get("dat") is True and qc[1].get("ket_luan") == "dat")
    return {k: (tu, mau) for k, (tu, mau) in dem.items()}


def bi_tra_ve(phieu: list[tuple], sk: dict[str, list[tuple]]) -> dict[str, tuple[int, int]]:
    """{khe_id: (tử, mẫu)}. D27: mỗi `bead.vao_cot_3` là một mẫu, quy cho khe của phiếu `giao_id_code` trong bằng chứng
    (phiếu ngoài bộ lọc → bỏ mẫu). Bị trả về khi sự kiện kế tiếp của bead (trong hai loại) là `cot.tra_ve`, tức trả
    về xảy ra trước lần vào cột 3 kế tiếp."""
    khe_cua = {g: khe for g, khe, *_ in phieu}
    dong: dict[tuple, list[tuple]] = defaultdict(list)
    for loai in ("bead.vao_cot_3", "cot.tra_ve"):
        for i, a, b, d in sk[loai]:
            dong[(a, b)].append((i, loai, d.get("giao_id_code")))
    dem: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for ds in dong.values():
        ds.sort()
        for j, (_, loai, g) in enumerate(ds):
            if loai == "bead.vao_cot_3" and g in khe_cua:
                x = dem[khe_cua[g]]
                x[1] += 1
                x[0] += j + 1 < len(ds) and ds[j + 1][1] == "cot.tra_ve"
    return {k: (tu, mau) for k, (tu, mau) in dem.items()}
