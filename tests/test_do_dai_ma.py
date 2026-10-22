"""bs-2bd.1.20 (ENGINEERING_STANDARDS "Kiểu code"): file trong tram/ ≤ 120 dòng, dòng ≤ 120 ký tự Unicode. Không có
ngoại lệ FILE. Ngoại lệ DÒNG gắn với NGUYÊN VĂN dòng (không theo số dòng): dòng đó đổi chữ hay biến mất thì ngoại lệ
hết hiệu lực — thêm ngoại lệ mới phải ghi lý do và được duyệt như đổi luật."""
from pathlib import Path

GOC = Path(__file__).resolve().parents[1] / "tram"
TRAN = 120
NGOAI_LE_DONG = {      # (file, nguyên văn dòng) → lý do
    ("du_an/khoi.py", "- Xong việc: viết bàn giao theo `docs/handovers/_TEMPLATE.md`, thêm khối máy đọc giữa hai dấu "
                      "`<!-- ban-giao -->` vào notes của bead."):
        "dòng trong văn bản mẫu ghi vào repo dự án — cắt sẽ đổi chữ sinh ra",
    ("giao_viec/goi.py", "- Bàn giao đúng schema khối `<!-- ban-giao -->` (phien_ban 1, loai `chinh-thuc`, "
                         "`file_ban_giao` dưới `docs/handovers/`)."):
        "dòng trong prompt gửi agent — cắt sẽ đổi prompt",
}


def vuot(goc: Path) -> tuple[list[str], list[str]]:
    file, dong = [], []
    for p in sorted(goc.rglob("*.py")):
        ten, ds = p.relative_to(goc).as_posix(), p.read_text(encoding="utf-8").splitlines()
        if len(ds) > TRAN:
            file.append(f"{ten}: {len(ds)} dòng")
        dong += [f"{ten}:{i}" for i, d in enumerate(ds, 1) if len(d) > TRAN and (ten, d) not in NGOAI_LE_DONG]
    return file, dong


def test_tram_khong_vuot_tran():
    assert vuot(GOC) == ([], [])


def test_ngoai_le_con_hieu_luc():
    """Ngoại lệ phải còn đúng nguyên văn trong mã — dòng đã sửa/xoá thì gỡ ngoại lệ, không để treo."""
    for ten, d in NGOAI_LE_DONG:
        assert d in (GOC / ten).read_text(encoding="utf-8").splitlines(), ten


def test_bo_dem_bat_duoc_file_va_dong_vuot(tmp_path):
    """Bộ đếm tự nó: file 121 dòng, dòng 121 ký tự (chữ có dấu đếm một ký tự) bị bắt; đúng trần thì không."""
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "dai.py").write_text("x = 1\n" * 121, encoding="utf-8")
    (tmp_path / "a" / "vua.py").write_text("x = 1\n" * 119 + "# " + "ạ" * 118 + "\n", encoding="utf-8")
    (tmp_path / "rong.py").write_text("# " + "ạ" * 119 + "\n", encoding="utf-8")
    assert vuot(tmp_path) == (["a/dai.py: 121 dòng"], ["rong.py:1"])
