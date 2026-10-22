"""Cổng cho đề nghị việc mới (design D-7, D84, D103) — hàm THUẦN đọc sự kiện của việc gốc (cũ → mới, như
`buoc_ke_tiep`). Kết quả:
- `("ghi", id bead.vao_cot_3)`: có lần vào cột 3 SAU đề nghị và lượt của đề nghị nằm trong bộ bằng chứng của nó —
  lượt code (`giao_id_code`) và lượt QC kết luận `dat` có `commit_qc` = `commit_ban_giao`; spike chỉ có lượt code
  (kiểm tài liệu thay QC). Lần vào cột 3 đó không gồm lượt này → bỏ (lượt bị thay bởi lượt sau).
- `("bo", "luot-khong-dat")`: phiếu kết thúc khác `xong` hoặc `xong` không hợp lệ (`ly_do`); kiểm lại của đúng phiếu
  không đạt; QC của chính phiếu, hoặc QC sau lần kiểm lại của phiếu code, kết luận khác `dat`.
- `("bo", "viec-da-dong")`: việc gốc đóng (hoặc mất) khi đề nghị còn chờ.
- `("cho", None)`: còn lại. Đề nghị bỏ không được "cứu" lại (D103)."""
from tram.giao_viec.su_kien import SK


def _cua(ds: list[SK], loai: str, giao_id: str) -> list[SK]:
    return [s for s in ds if s.loai == loai and s.du_lieu.get("giao_id") == giao_id]


def luot_trong_bang_chung(ds: list[SK], vc3: SK) -> set[str]:
    d = vc3.du_lieu
    qc = {s.du_lieu["giao_id"] for s in ds if s.loai == "qc.ket_qua" and s.id < vc3.id
          and s.du_lieu.get("ket_luan") == "dat" and s.du_lieu.get("commit_qc") == d["commit_ban_giao"]
          and s.du_lieu.get("commit_code") == d["commit_code"]}
    return {d["giao_id_code"], *qc}


def khong_dat(ds: list[SK], giao_id: str) -> bool:
    if any(s.du_lieu.get("ket_thuc") != "xong" or s.du_lieu.get("ly_do") is not None
           for s in _cua(ds, "giao.ket_thuc", giao_id)):
        return True
    kiem = _cua(ds, "kiem.lai", giao_id)
    if any(s.du_lieu.get("dat") is not True for s in kiem) or any(
            s.du_lieu.get("ket_luan") != "dat" for s in _cua(ds, "qc.ket_qua", giao_id)):
        return True
    code = {s.du_lieu.get("commit") for s in kiem}
    return any(s.loai == "qc.ket_qua" and s.du_lieu.get("commit_code") in code and s.du_lieu.get("ket_luan") != "dat"
               for s in ds)


def cong_viec_moi(ds: list[SK], giao_id: str, de_nghi_id: int, *, viec_dong: bool) -> tuple[str, int | str | None]:
    if viec_dong:
        return "bo", "viec-da-dong"
    vc3 = next((s for s in ds if s.loai == "bead.vao_cot_3" and s.id > de_nghi_id), None)
    if vc3 is not None:
        return ("ghi", vc3.id) if giao_id in luot_trong_bang_chung(ds, vc3) else ("bo", "luot-khong-dat")
    if khong_dat(ds, giao_id):
        return "bo", "luot-khong-dat"
    return "cho", None
