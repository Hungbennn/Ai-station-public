# Lát V3b — dọn cuối: file/dòng ≤ 120 và tài liệu sở hữu theo mã đã ghép (V3-18, V3-19) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Trạng thái: PLAN (18/10/2026), viết lại V3-18/V3-19 theo Codex R2-11 và vòng 3 mục 4.5** — trên cây THẬT `main` `92430e0` (đã ghép plan A V2b T1–T8, plan B V2c T1–T9, V3-1/2/3/4/5/8/9/10/11/12/13/14/15/16/17 và sửa docs lệnh test của điều phối). Mọi số đo, danh sách vượt trần và hunk dưới đây đo/dựng lại trên cây đó, KHÔNG chép từ bản vòng 2 (`2026-10-17-lat-v3-va-don.md`, bản đó là lịch sử, không áp). Đã chạy RED→GREEN thật trong worktree `plan/v3b-don-cuoi`, đo cả bộ qua `tests/chan_host/chay.sh -q`, áp lại toàn bộ khối mã/docs của plan lên bản sạch và so `diff -r` (khớp), rồi hoàn nguyên. V3-6/V3-7 KHÔNG thuộc plan này. CHƯA áp vào `main`; V3-18 chạm vùng kill list (chỉ dời/xuống dòng) → chờ Đại ca duyệt + Codex review.

**Goal:** (V3-18, `bs-2bd.1.20`) mọi file `tram/**/*.py` ≤ 120 dòng và mọi dòng ≤ 120 ký tự Unicode, có test canh giữ — chỉ dời khối tự đứng sang module khác và xuống dòng, KHÔNG đổi hành vi. (V3-19) tài liệu sở hữu mô tả đúng mã đã ghép: bộ chạy chặn host (`AGENT_RULES.md` §13), cài từng dịch vụ / gỡ / khôi phục / siết quyền (`DEPLOY.md`), số phiên bản kho (`ARCHITECTURE.md`), module và tích hợp mới (`MODULES.md`), luật độ dài + quyền `~/.tram` (`ENGINEERING_STANDARDS.md`).

**Architecture:** V3-18 không thêm khái niệm nào: mỗi file vượt trần dời MỘT khối tự đứng (lớp mô hình, lỗi, hàm đọc, phần dòng lệnh) sang module cùng package — có sẵn nếu đúng chủ đề (`nho/mo_hinh.py`, `phieu/mo_hinh.py`, `giao_viec/quan_sat_kiem.py`, `giao_viec/repo_ban_chep.py`, `giao_viec/lenh.py`), mới khi chưa có (6 file). File cũ import lại tên đã dời nên đường import cũ (`from tram.beads.bd import LoiBd`…) vẫn chạy; không tạo vòng import (V3-11 `tests/test_vong_import.py` canh). Dòng dài xuống dòng trong ngoặc, giữ thứ tự đánh giá. V3-19 chỉ sửa docs, thêm phần còn thiếu trên nội dung `main` mới (không ghi đè sửa của điều phối ở `CLAUDE.md`, `AGENTS.md`, §13).

**Tech Stack:** Python 3.12 stdlib (`pathlib`), pytest 8. Không dependency mới.

**Spec / nguồn:** bead `bs-2bd.1.20` (dọn file/dòng dài), `bs-2bd.1.18` (bộ chặn host — phần docs), `bs-2bd.1.23`, `.17`, `.4`, `.3`, `.1`, `.2` (phần docs của các task đã ghép); `docs/ENGINEERING_STANDARDS.md` mục Kiểu code; `docs/AGENTS.md` bảng sở hữu + quy tắc thăng cấp; `docs/AGENT_RULES.md` §2, §8, §9, §12, §13; review Codex `REVIEW-CODEX-dot8-vong2.md` R2-11, `REVIEW-CODEX-dot8-vong3.md` mục 4.5.

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2) — STOP, chờ Đại ca duyệt trước khi code V3-18.** Chỉ DỜI NGUYÊN VĂN hoặc XUỐNG DÒNG, không đổi lệnh, điều kiện, thông báo hay thứ tự đánh giá: mục 3 *Cách ly* — `tram/giao_viec/kiem_principal.py` (tách MỘT phép gán hai biến thành hai dòng), và cổng/harness kiểm lại `tram/giao_viec/ban_chep.py`, `repo_ban_chep.py` (dời `ten_ban_chep`), `cong_that.py`, `quan_sat_kiem.py` (dời `env_kin`), `lenh_nghiem_thu.py` (dời phần khai tham số dòng lệnh sang `giao_viec/lenh.py`); mục 5 *PR* — `tram/giao_viec/pr.py` (xuống dòng hai chữ ký hàm); mục 6 *Cài/gỡ* — `tram/chu/cai_dat.py` (xuống dòng một dòng in kế hoạch), `tram/chu/go_cai_dat_tho.py` (dời `lenh_cli` sang `tram/chu/lenh_go_tho.py`, `lenh_tho.py` trỏ theo). Mục 4 *Cấu trúc DB*: KHÔNG chạm `LUOC_DO` nào; `nho/nhat_ky.py` chỉ dời dataclass `ThaoTacNho` và xuống dòng một câu SELECT (chuỗi SQL giữ nguyên ký tự).
- **Đường import cũ giữ nguyên:** tên đã dời được file cũ import lại — `tram.beads.bd.{LoiBd, KhongThayBead}`, `tram.ban_giao.schema.{DoiChieu, LenhKiem, HuongDaBo}`, `tram.cau_hinh.du_an.MoiTruongKiem`, `tram.phieu.kho.LuotCu`, `tram.su_kien.kho.SuKien`, `tram.nho.nhat_ky.ThaoTacNho`, `tram.giao_viec.ban_chep.ten_ban_chep`, `tram.giao_viec.cong_that.env_kin`. Chỉ hai tên công khai đổi chỗ có người gọi duy nhất được sửa cùng: `go_cai_dat_tho.lenh_cli` (gọi trễ từ `chu/lenh_tho.py`) và `lenh_nghiem_thu.them` (gọi từ `giao_viec/lenh.py`). Tên riêng đổi tên vì nay dùng giữa module: `_Nghiem` → `Nghiem`, `_doc_ds`/`_doc_ds_yeu_cau` → `doc_ds`/`doc_ds_yeu_cau`, `_moi_truong_kiem` → `doc_moi_truong_kiem` (đã `grep` cả `tram/` và `tests/`: không ai ngoài file gốc dùng tên riêng cũ, không test nào `monkeypatch` tên đã dời theo đường module cũ).
- **Không thêm ngoại lệ để làm xanh.** Không ngoại lệ FILE. Ngoại lệ DÒNG chỉ hai dòng chữ sinh ra (văn bản mẫu `du_an/khoi.py`, prompt `giao_viec/goi.py` — cắt sẽ đổi chữ gửi đi), gắn với NGUYÊN VĂN dòng; test thứ hai bắt ngoại lệ treo.
- **Docs (V3-19) chỉ mô tả cái đã có trong mã ở `92430e0`** (đã đọc mã từng câu): không viết mạnh hơn mã — ví dụ `cai-dat-tho` CHƯA có hạn từng lệnh (ghi rõ), quyền đúng từ lúc tạo CHỈ cho kho SQLite và bản sao lưu (phần còn lại do `siet-quyen`), `nhat-ky.db`/LanceDB CHƯA có số phiên bản. Không hạ luật cấm `git push` (§11 giữ nguyên; bộ chặn chỉ là lưới an toàn). Không chép code vào docs (§8); mỗi loại thông tin ở đúng tài liệu sở hữu (`docs/AGENTS.md`); giữ trần: `AGENT_RULES.md` ≤ 300 dòng (sau: 198), `ARCHITECTURE.md` ≤ 200 (sau: 79), mọi dòng docs ≤ 300 ký tự (dòng dài nhất sau sửa: 283). Không sửa `CURRENT_STATE.md` trong plan (điều phối viết đè dòng Test sau khi ghép, theo số đo thật lúc đó).
- **N₀ = 3230** (`tests/chan_host/chay.sh -q` trên `5a495ca` — cây mã của `92430e0`, docs-only khác — 18/10: `3230 passed in 346.39s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629). Plan **+3 → 3233**. Đo lại trước Task V3-18; lệch thì tìm nguyên nhân trước.
- Chạy test BẮT BUỘC qua `tests/chan_host/chay.sh -q [đường test]` (KHÔNG `uv run pytest` trần — test cũ sẽ push thật vào kho tạm). "0 dòng mới" trong nhật ký chặn là điều kiện xanh.
- Hunk viết trên `92430e0`; áp theo NỘI DUNG (`git apply --check` trước; không sạch thì DỪNG, báo điều phối — không chép dòng cộng theo trí nhớ, không tự "dọn thêm").
- Commit trên nhánh task, một task một commit; không push/merge. Giữ `bat_ghi: false`, `giao_viec.bat: false`.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline |
|---|---|---|---|
| G1 | Mọi `tram/**/*.py` ≤ 120 dòng, mọi dòng ≤ 120 ký tự Unicode (trừ đúng 2 dòng chữ sinh ra, gắn nguyên văn) | `tests/test_do_dai_ma.py` | `test_tram_khong_vuot_tran` (RED thật: 10 file, 18 dòng → GREEN) |
| G2 | Ngoại lệ không treo: dòng ngoại lệ đổi/biến mất thì test đỏ | cùng file | `test_ngoai_le_con_hieu_luc` |
| G3 | Bộ đếm đếm đúng (121 dòng, 121 ký tự có dấu bị bắt; đúng 120 thì không) | `vuot()` | `test_bo_dem_bat_duoc_file_va_dong_vuot` |
| G4 | Không đổi hành vi: mọi test cũ xanh không sửa test nào | toàn bộ `tram/` | cả bộ `3233 passed` = N₀ + 3 test mới, 0 dòng chặn mới |
| G5 | Không vòng import mới | 6 module mới + import lại | `tests/test_vong_import.py` xanh |
| G6 | Đường import cũ còn chạy | file gốc import lại tên đã dời | các test import theo đường cũ (`tests/bd_gia.py`, `test_kho_phieu.py`, `test_cong_that.py`, `test_du_an_quan_sat.py` — `q.func is cong_that.env_kin`…) xanh |
| G7 | Thứ tự đánh giá giữ nguyên ở chỗ có tác dụng phụ | `kiem_principal.py` (gán tuple → hai gán: vế phải thứ hai không đọc biến vừa gán), `lenh_khe.py` (`doc_token_may()` vẫn gọi TRƯỚC khi dựng danh sách khe — xuống dòng, không kéo biểu thức ra biến) | đọc diff; test hiện có của hai file |
| G8 | Docs khớp mã ở `92430e0`, đường dẫn tồn tại | V3-19 | Step 2 của V3-19: `ls` mọi đường dẫn mã nhắc tới, đo dòng |

## Task ↔ file

| Task | Bead | ⛔ | File |
|---|---|---|---|
| V3-18 | `bs-2bd.1.20` | một phần (kill list mục 3, 5, 6 — chỉ dời/xuống dòng) | Create `tests/test_do_dai_ma.py`, `tram/ban_giao/mo_hinh.py`, `tram/beads/doc_ds.py`, `tram/beads/loi.py`, `tram/cau_hinh/moi_truong_kiem.py`, `tram/chu/lenh_go_tho.py`, `tram/su_kien/mo_hinh.py`; Modify 29 file `tram/` (liệt kê trong Step 3) |
| V3-19 | docs của `.18/.20/.23/.17/.4/.3/.1/.2` | không (chỉ docs) | Modify `docs/AGENT_RULES.md`, `docs/DEPLOY.md`, `docs/ARCHITECTURE.md`, `docs/MODULES.md`, `docs/ENGINEERING_STANDARDS.md` |

Thứ tự: V3-18 rồi V3-19 (docs nhắc `tests/test_do_dai_ma.py`). Không giao nhau với V3-6/V3-7 (chúng sửa `tram/api/tong_quan.py`, `app.py`, `tuyen_feature.py`; plan này chỉ sửa `tram/api/tuyen_nho.py`). Sau V3-18, mọi plan mới phải tự giữ trần (test đỏ ngay).

## Tasks

### Task V3-18: File và dòng trong `tram/` ≤ 120 — dời khối tự đứng, xuống dòng (bs-2bd.1.20)

**Files:** như bảng trên. Số dòng sau task (đo thật): `beads/bd.py` 142 → 107, `ban_giao/schema.py` 122 → 101, `cau_hinh/du_an.py` 121 → 100, `chu/go_cai_dat_tho.py` 122 → 93, `giao_viec/ban_chep.py` 122 → 114, `giao_viec/cong_that.py` 122 → 110, `giao_viec/lenh_nghiem_thu.py` 122 → 111, `nho/nhat_ky.py` 122 → 115, `phieu/kho.py` 121 → 113, `su_kien/kho.py` 122 → 107; nơi nhận: `nho/mo_hinh.py` 107 → 116, `phieu/mo_hinh.py` 89 → 97, `giao_viec/quan_sat_kiem.py` 102 → 115, `giao_viec/repo_ban_chep.py` 35 → 43, `giao_viec/lenh.py` 97 → 104; mới: `ban_giao/mo_hinh.py` 26, `beads/doc_ds.py` 34, `beads/loi.py` 9, `cau_hinh/moi_truong_kiem.py` 26, `chu/lenh_go_tho.py` 35, `su_kien/mo_hinh.py` 17.

**Interfaces:** không đổi chữ ký nào. Tên mới: `tram.ban_giao.mo_hinh.{Nghiem, DoiChieu, LenhKiem, HuongDaBo}`, `tram.beads.loi.{LoiBd, KhongThayBead}`, `tram.beads.doc_ds.{doc_ds, doc_ds_yeu_cau}`, `tram.cau_hinh.moi_truong_kiem.{MoiTruongKiem, doc_moi_truong_kiem}`, `tram.chu.lenh_go_tho.lenh_cli`, `tram.su_kien.mo_hinh.SuKien`; chỗ mới của tên cũ: `tram.nho.mo_hinh.ThaoTacNho`, `tram.phieu.mo_hinh.LuotCu`, `tram.giao_viec.quan_sat_kiem.env_kin`, `tram.giao_viec.repo_ban_chep.ten_ban_chep`.

- [ ] **Step 0: Kiểm điều kiện vào** — HEAD có `92430e0` (hoặc sau đó mà `git diff 92430e0 HEAD -- tram` rỗng); Đại ca đã duyệt phần kill list; đo N₀ bằng `tests/chan_host/chay.sh -q` (mong đợi `3230 passed`, 0 dòng chặn mới). `git diff 92430e0 HEAD -- tram` không rỗng → `git apply --check` từng bản vá Step 3; hỏng thì DỪNG, báo.

- [ ] **Step 1: Viết test canh giữ**

`tests/test_do_dai_ma.py` (mới):

```python
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
```

- [ ] **Step 2: Chạy thấy đỏ**

Run: `tests/chan_host/chay.sh -q tests/test_do_dai_ma.py`
Expected (thật, 18/10, cây `5a495ca`/`92430e0`): `1 failed, 2 passed` — `test_tram_khong_vuot_tran` đỏ, `vuot(tram/)` trả 10 file: `ban_giao/schema.py: 122 dòng`, `beads/bd.py: 142 dòng`, `cau_hinh/du_an.py: 121 dòng`, `chu/go_cai_dat_tho.py: 122 dòng`, `giao_viec/ban_chep.py: 122 dòng`, `giao_viec/cong_that.py: 122 dòng`, `giao_viec/lenh_nghiem_thu.py: 122 dòng`, `nho/nhat_ky.py: 122 dòng`, `phieu/kho.py: 121 dòng`, `su_kien/kho.py: 122 dòng`; 18 dòng: `api/tuyen_nho.py:56`, `chu/cai_dat.py:92`, `giao_viec/kiem_principal.py:97`, `giao_viec/phu_thuoc_4c.py:41`, `giao_viec/pr.py:33`, `giao_viec/pr.py:72`, `giao_viec/tick_feature.py:71`, `giao_viec/tick_github.py:28`, `giao_viec/tick_pipeline.py:41`, `nho/nhat_ky.py:99`, `nho/nhat_ky.py:102`, `nho/tra_phieu.py:35`, `suy/nhan_vat.py:61`, `thao_tac/duyet_spec.py:93`, `tho/kiem_may.py:66`, `tho/kiem_may.py:77`, `tho/lenh_khe.py:37`, `tho/lenh_khe.py:38`. Nhật ký chặn 0 dòng mới. (So với bản vòng 2: `tho/kiem_cong.py:49` hết vượt sau plan A; thêm `giao_viec/cong_that.py`, `giao_viec/lenh_nghiem_thu.py` do plan B; `chu/cai_dat.py` nay ở dòng 92.)

- [ ] **Step 3: Dời/xuống dòng cơ học** — áp nguyên văn các bản vá và file mới dưới đây (bản vá là `git diff` thật trên `92430e0`).

`tram/api/tuyen_nho.py` (sửa):

````diff
--- a/tram/api/tuyen_nho.py
+++ b/tram/api/tuyen_nho.py
@@ -53,7 +53,8 @@ def _sach(k: dict, bay: str) -> dict:
     nguon = [{lam_sach(str(a), 30): lam_sach(str(b), 100) for a, b in list(n.items())[:10]}
              for n in (k.get("nguon") or [])[:20] if isinstance(n, dict)]
     return {"id": lam_sach(k.get("id"), 64), "noi_dung": lam_sach(k.get("noi_dung"), 1000),
-            "pham_vi": lam_sach(k.get("pham_vi"), 200), "nhan": [lam_sach(str(x), 30) for x in (k.get("nhan") or [])][:5],
+            "pham_vi": lam_sach(k.get("pham_vi"), 200),
+            "nhan": [lam_sach(str(x), 30) for x in (k.get("nhan") or [])][:5],
             "quan_trong": float(k.get("quan_trong") or 0), "nguon": nguon, "nguon_dai_ca": bool(k.get("nguon_dai_ca")),
             "tao_luc": lam_sach(k.get("tao_luc"), 30), "hieu_luc_tu": lam_sach(k.get("hieu_luc_tu"), 30),
             "dung_luc": lam_sach(k.get("dung_luc"), 30) or None, "so_lan_dung": int(k.get("so_lan_dung") or 0),
````

`tram/ban_giao/mo_hinh.py` (mới):

```python
"""Mô hình con của khối bàn giao (tách khỏi `schema.py` — bs-2bd.1.20, chỉ dời chỗ): trường lạ bị từ chối."""
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Nghiem(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DoiChieu(Nghiem):
    tieu_chi: str
    dat: bool
    bang_chung: str


class LenhKiem(Nghiem):
    lenh: str
    ket_qua: Literal["pass", "fail"]
    tom_tat: str
    digest_log: str


class HuongDaBo(Nghiem):
    huong: str
    vi_sao: str
```

`tram/ban_giao/schema.py` (sửa):

````diff
--- a/tram/ban_giao/schema.py
+++ b/tram/ban_giao/schema.py
@@ -2,38 +2,17 @@ import re
 from pathlib import Path
 from typing import Literal
 
-from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
+from pydantic import ValidationError, field_validator
 
 from tram.ban_giao.file_ban_giao import loi_duong_dan, loi_tai_commit, loi_tren_dia
+from tram.ban_giao.mo_hinh import DoiChieu, HuongDaBo, LenhKiem, Nghiem
 
 GIOI_HAN_BYTE = 64 * 1024
 KHOI_RE = re.compile(r"<!-- ban-giao -->\s*(\{.*?\})\s*<!-- ban-giao -->", re.S)
 PR_RE = re.compile(r"https?://[^\s/]+/\S+")
 
 
-class _Nghiem(BaseModel):
-    model_config = ConfigDict(extra="forbid")
-
-
-class DoiChieu(_Nghiem):
-    tieu_chi: str
-    dat: bool
-    bang_chung: str
-
-
-class LenhKiem(_Nghiem):
-    lenh: str
-    ket_qua: Literal["pass", "fail"]
-    tom_tat: str
-    digest_log: str
-
-
-class HuongDaBo(_Nghiem):
-    huong: str
-    vi_sao: str
-
-
-class BanGiao(_Nghiem):
+class BanGiao(Nghiem):
     phien_ban: Literal[1]
     loai: Literal["chinh-thuc", "tam"]
     luot: int
````

`tram/beads/bd.py` (sửa):

````diff
--- a/tram/beads/bd.py
+++ b/tram/beads/bd.py
@@ -3,19 +3,13 @@ import subprocess
 from collections.abc import Callable, Sequence
 from pathlib import Path
 
+from tram.beads.doc_ds import doc_ds, doc_ds_yeu_cau
+from tram.beads.loi import KhongThayBead, LoiBd
 from tram.beads.mo_hinh import Bead
 
 Runner = Callable[[Sequence[str]], str]
 
 
-class LoiBd(RuntimeError):
-    pass
-
-
-class KhongThayBead(LoiBd):
-    """Bead không có trong `bd list` của dự án."""
-
-
 def chay_bd(args: Sequence[str]) -> str:
     try:
         kq = subprocess.run(["bd", *args], capture_output=True, text=True, timeout=120)
@@ -36,11 +30,11 @@ class Bd:
         return self._runner(["-C", str(self.repo), *args])
 
     def tat_ca(self) -> list[Bead]:
-        return _doc_ds(self._chay("list", "--json", "--all", "--limit", "0"))
+        return doc_ds(self._chay("list", "--json", "--all", "--limit", "0"))
 
     def tat_ca_yeu_cau(self) -> list[Bead]:
         """Đối soát trước create: schema lạ không đồng nghĩa danh sách rỗng."""
-        return _doc_ds_yeu_cau(self._chay("list", "--json", "--all", "--limit", "0"))
+        return doc_ds_yeu_cau(self._chay("list", "--json", "--all", "--limit", "0"))
 
     def phien_ban(self, bead_id: str) -> str:
         """`updated_at` hiện tại của một bead — version để kiểm lại trước khi ghi (spec §5.6).
@@ -111,32 +105,3 @@ class Bd:
     def them_phu_thuoc(self, bead_id: str, phu_thuoc_vao: str) -> None:
         """`bd dep add A B`: A phụ thuộc B (B chặn A). Lặp cặp cũ vẫn 'Added' — người gọi tự kiểm trùng."""
         self._chay("dep", "add", bead_id, phu_thuoc_vao, "--actor", self.actor)
-
-
-def _doc_ds(ra: str) -> list[Bead]:
-    try:
-        ds = json.loads(ra)
-        if not isinstance(ds, list):
-            raise TypeError(f"cần mảng, nhận {type(ds).__name__}")
-        return [Bead.tu_json(d) for d in ds]
-    except (ValueError, KeyError, TypeError, AttributeError) as e:
-        raise LoiBd(f"bd list: JSON không đọc được ({type(e).__name__}: {e})") from e
-
-
-def _doc_ds_yeu_cau(ra: str) -> list[Bead]:
-    try:
-        ds = json.loads(ra)
-        if not isinstance(ds, list):
-            raise ValueError
-        for d in ds:
-            if not isinstance(d, dict):
-                raise ValueError
-            if any(not isinstance(d.get(k), str) for k in ("id", "issue_type")):
-                raise ValueError
-            if not isinstance(d.get("description", ""), str):   # bd 1.2.2 bỏ khoá khi rỗng; có mà null/sai kiểu: lỗi
-                raise ValueError
-            if not d["id"] or d["id"] != d["id"].strip() or not d["issue_type"]:
-                raise ValueError
-        return [Bead.tu_json(d) for d in ds]
-    except (ValueError, KeyError, TypeError, AttributeError):
-        raise LoiBd("bd list: schema đối soát không hợp lệ") from None
````

`tram/beads/doc_ds.py` (mới):

```python
"""Đọc JSON `bd list` (bs-2bd.1.20: dời nguyên văn khỏi `bd.py`)."""
import json

from tram.beads.loi import LoiBd
from tram.beads.mo_hinh import Bead


def doc_ds(ra: str) -> list[Bead]:
    try:
        ds = json.loads(ra)
        if not isinstance(ds, list):
            raise TypeError(f"cần mảng, nhận {type(ds).__name__}")
        return [Bead.tu_json(d) for d in ds]
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise LoiBd(f"bd list: JSON không đọc được ({type(e).__name__}: {e})") from e


def doc_ds_yeu_cau(ra: str) -> list[Bead]:
    try:
        ds = json.loads(ra)
        if not isinstance(ds, list):
            raise ValueError
        for d in ds:
            if not isinstance(d, dict):
                raise ValueError
            if any(not isinstance(d.get(k), str) for k in ("id", "issue_type")):
                raise ValueError
            if not isinstance(d.get("description", ""), str):   # bd 1.2.2 bỏ khoá khi rỗng; có mà null/sai kiểu: lỗi
                raise ValueError
            if not d["id"] or d["id"] != d["id"].strip() or not d["issue_type"]:
                raise ValueError
        return [Bead.tu_json(d) for d in ds]
    except (ValueError, KeyError, TypeError, AttributeError):
        raise LoiBd("bd list: schema đối soát không hợp lệ") from None
```

`tram/beads/loi.py` (mới):

```python
"""Lỗi của lớp `bd` (bs-2bd.1.20: dời khỏi `bd.py` để `doc_ds.py` dùng mà không vòng import)."""


class LoiBd(RuntimeError):
    pass


class KhongThayBead(LoiBd):
    """Bead không có trong `bd list` của dự án."""
```

`tram/cau_hinh/du_an.py` (sửa):

````diff
--- a/tram/cau_hinh/du_an.py
+++ b/tram/cau_hinh/du_an.py
@@ -6,8 +6,8 @@ import yaml
 
 from tram.cau_hinh.du_an_giao import CauHinhGiao, doc_cau_hinh_giao
 from tram.cau_hinh.lenh import kiem_mau
+from tram.cau_hinh.moi_truong_kiem import MoiTruongKiem, doc_moi_truong_kiem
 from tram.duong_dan import goc_repo
-from tram.kiem.moi_truong import loi_dich
 
 LOAI_HANG_RAO = ("tien", "schema", "quyen", "khach_thay")
 
@@ -22,13 +22,6 @@ class HangRao:
 NHANH_CHINH_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}")
 
 
-@dataclass(frozen=True)
-class MoiTruongKiem:
-    """Spec 3 §7.1: Đại ca đặt tay, trỏ DB test. `file` trên máy chạy kiểm; `dich` tương đối trong worktree."""
-    file: Path
-    dich: str
-
-
 @dataclass(frozen=True)
 class DuAn:
     ten: str
@@ -63,20 +56,6 @@ def _lenh_cho_phep(raw: dict) -> tuple[str, ...]:
     return ds
 
 
-def _moi_truong_kiem(raw: dict) -> MoiTruongKiem | None:
-    mt = raw.get("moi_truong_kiem")
-    if mt is None:
-        return None
-    if not isinstance(mt, dict) or set(mt) != {"file", "dich"}:
-        raise ValueError("moi_truong_kiem phải là bảng {file, dich}")
-    f = Path(str(mt["file"])).expanduser()
-    if not f.is_absolute():
-        raise ValueError("moi_truong_kiem.file phải là đường dẫn tuyệt đối")
-    if (loi := loi_dich(mt["dich"])) is not None:
-        raise ValueError(f"moi_truong_kiem.dich: {loi}")
-    return MoiTruongKiem(f, mt["dich"])
-
-
 def _nhanh_chinh(raw: dict) -> str:
     n = raw.get("nhanh_chinh", "main")
     if not isinstance(n, str) or not NHANH_CHINH_RE.fullmatch(n) or ".." in n or n.endswith(("/", ".lock")) \
@@ -111,7 +90,7 @@ def nap_du_an(ten: str, *, thu_muc: Path | None = None, repo: Path | None = None
         module=_ds_chuoi(raw, "module"),
         tu_khoa_khach=_ds_chuoi(raw, "tu_khoa_khach"),
         lenh_cho_phep=lenh,
-        moi_truong_kiem=_moi_truong_kiem(raw),
+        moi_truong_kiem=doc_moi_truong_kiem(raw),
         nhanh_chinh=_nhanh_chinh(raw),
         giao=doc_cau_hinh_giao(raw, lenh),
     )
````

`tram/cau_hinh/moi_truong_kiem.py` (mới):

```python
"""Khoá `moi_truong_kiem` của du-an/<ten>.yaml (tách khỏi `du_an.py` — bs-2bd.1.20, chỉ dời chỗ)."""
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.moi_truong import loi_dich


@dataclass(frozen=True)
class MoiTruongKiem:
    """Spec 3 §7.1: Đại ca đặt tay, trỏ DB test. `file` trên máy chạy kiểm; `dich` tương đối trong worktree."""
    file: Path
    dich: str


def doc_moi_truong_kiem(raw: dict) -> MoiTruongKiem | None:
    mt = raw.get("moi_truong_kiem")
    if mt is None:
        return None
    if not isinstance(mt, dict) or set(mt) != {"file", "dich"}:
        raise ValueError("moi_truong_kiem phải là bảng {file, dich}")
    f = Path(str(mt["file"])).expanduser()
    if not f.is_absolute():
        raise ValueError("moi_truong_kiem.file phải là đường dẫn tuyệt đối")
    if (loi := loi_dich(mt["dich"])) is not None:
        raise ValueError(f"moi_truong_kiem.dich: {loi}")
    return MoiTruongKiem(f, mt["dich"])
```

`tram/chu/cai_dat.py` (sửa):

````diff
--- a/tram/chu/cai_dat.py
+++ b/tram/chu/cai_dat.py
@@ -89,7 +89,8 @@ def in_ke_hoach(kh: KeHoach) -> str:
     if kh.buoc:
         dong += ["Sẽ làm trước các lệnh:"] + [f"  - {mo_ta}" for mo_ta, _ in kh.buoc]
     dong += ["Sẽ chạy các lệnh:"] + [f"  - {' '.join(c)}" for c in kh.lenh]
-    dong += ["Cảnh báo (Đại ca tự xử lý, trạm không đổi cài đặt hệ thống):"] + [f"  - {c}" for c in kh.canh_bao or ["không có"]]
+    dong += ["Cảnh báo (Đại ca tự xử lý, trạm không đổi cài đặt hệ thống):"]
+    dong += [f"  - {c}" for c in kh.canh_bao or ["không có"]]
     dong += ["Trạm không tự cập nhật. Lúc chạy chỉ gọi ra ngoài tới: Claude API, api.telegram.org, GitHub (Q15)."]
     return "\n".join(dong)
 
````

`tram/chu/go_cai_dat_tho.py` (sửa):

````diff
--- a/tram/chu/go_cai_dat_tho.py
+++ b/tram/chu/go_cai_dat_tho.py
@@ -91,32 +91,9 @@ def lap_ke_hoach_go(so: SoCai, *, toi: str, quan_sat: Callable | None = None, ch
                  "Token máy B ở trạm vẫn hiệu lực — thu hồi bằng `tram chu go-may B` nếu không cài lại.",
                  f"Sổ {so.p} được giữ (ghi thêm da_go). Chạy lại lệnh này để xem còn gì (đối soát có thể mở thêm)."]
     return KeHoach(tep={}, lenh=[], canh_bao=canh_bao, buoc=buoc)
-
-
-def lenh_cli(args, *, hoi: Callable) -> int:
-    """`tram chu go-cai-dat-tho`: 0 không còn gì / đã chạy; 1 không dong-y / dừng giữa chừng; 2 sổ hỏng / đang bận."""
-    import getpass
-    import sys
-
-    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
-    so = SoCai()
-    try:
-        with so.giu():                         # R4: gỡ và cài không chạy đồng thời (khoá TRƯỚC khi xem sổ)
-            kh = lap_ke_hoach_go(so, toi=getpass.getuser(), xoa_nha=args.xoa_nha) if so.p.exists() else None
-            if kh is None or not kh.buoc:
-                print("Không còn gì để gỡ." if kh else f"Không còn gì để gỡ (chưa có sổ {so.p}).")
-                return 0
-            print(in_ke_hoach(kh))
-            if not hoi(args):
-                print("Không làm gì.")
-                return 1
-            try:
-                thuc_hien(kh)
-            except (OSError, ValueError, subprocess.CalledProcessError) as e:
-                print(f"Dừng giữa chừng: {e}\nChạy lại `tram chu go-cai-dat-tho` sau khi xem lỗi.", file=sys.stderr)
-                return 1
-    except (ValueError, OSError) as e:         # sổ hỏng, SoCaiDangBan, dscl lỗi lúc lập kế hoạch
-        print(f"Không gỡ gì: {e}", file=sys.stderr)
-        return 2
-    print("Đã chạy kế hoạch gỡ. Chạy lại `tram chu go-cai-dat-tho`: phải báo không còn gì để gỡ.")
-    return 0
+
+
+def lenh_cli(args, *, hoi: Callable) -> int:
+    """Giữ đường gọi cũ; import trễ để không tạo vòng với lenh_go_tho."""
+    from tram.chu.lenh_go_tho import lenh_cli as chay
+    return chay(args, hoi=hoi)
````

`tram/chu/lenh_go_tho.py` (mới):

```python
"""`tram chu go-cai-dat-tho` — phần dòng lệnh (tách khỏi `go_cai_dat_tho.py` — bs-2bd.1.20, chỉ dời chỗ)."""
import subprocess
from collections.abc import Callable

from tram.chu.go_cai_dat_tho import lap_ke_hoach_go
from tram.chu.so_cai_tho import SoCai


def lenh_cli(args, *, hoi: Callable) -> int:
    """`tram chu go-cai-dat-tho`: 0 không còn gì / đã chạy; 1 không dong-y / dừng giữa chừng; 2 sổ hỏng / đang bận."""
    import getpass
    import sys

    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
    so = SoCai()
    try:
        with so.giu():                         # R4: gỡ và cài không chạy đồng thời (khoá TRƯỚC khi xem sổ)
            kh = lap_ke_hoach_go(so, toi=getpass.getuser(), xoa_nha=args.xoa_nha) if so.p.exists() else None
            if kh is None or not kh.buoc:
                print("Không còn gì để gỡ." if kh else f"Không còn gì để gỡ (chưa có sổ {so.p}).")
                return 0
            print(in_ke_hoach(kh))
            if not hoi(args):
                print("Không làm gì.")
                return 1
            try:
                thuc_hien(kh)
            except (OSError, ValueError, subprocess.CalledProcessError) as e:
                print(f"Dừng giữa chừng: {e}\nChạy lại `tram chu go-cai-dat-tho` sau khi xem lỗi.", file=sys.stderr)
                return 1
    except (ValueError, OSError) as e:         # sổ hỏng, SoCaiDangBan, dscl lỗi lúc lập kế hoạch
        print(f"Không gỡ gì: {e}", file=sys.stderr)
        return 2
    print("Đã chạy kế hoạch gỡ. Chạy lại `tram chu go-cai-dat-tho`: phải báo không còn gì để gỡ.")
    return 0
```

`tram/chu/lenh_tho.py` (sửa):

````diff
--- a/tram/chu/lenh_tho.py
+++ b/tram/chu/lenh_tho.py
@@ -75,7 +75,7 @@ def _kiem_cach_ly(args) -> int:
 
 
 def _go_cai_dat_tho(args) -> int:
-    from tram.chu.go_cai_dat_tho import lenh_cli
+    from tram.chu.lenh_go_tho import lenh_cli
     return lenh_cli(args, hoi=_hoi)
 
 
````

`tram/giao_viec/ban_chep.py` (sửa):

````diff
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -8,7 +8,6 @@ MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo_ban_chep.py`). Fail-clos
 → ném; `tar`/`git` lỗi hoặc cây khác cây commit gốc (R7) → ném, không chạy lệnh kiểm; dọn xong mà thư mục còn → ném."""
 import fcntl
 import os
-import secrets
 import subprocess
 from collections.abc import Callable
 from contextlib import contextmanager
@@ -17,7 +16,7 @@ from pathlib import Path
 from tram.duong_dan import tram_home
 from tram.giao_viec.cay_kiem import cay_goc, loi_cau_hinh_kho, loi_dich_trong_cay, tar_mot_tep
 from tram.giao_viec.ong_chep import chay_ong
-from tram.giao_viec.repo_ban_chep import lenh_cay, lenh_repo
+from tram.giao_viec.repo_ban_chep import lenh_cay, lenh_repo, ten_ban_chep  # noqa: F401 — đường import cũ
 from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich
 from tram.kiem.vong_doi import Kill, LoiThuHoi, kill_cuc_bo
@@ -55,13 +54,6 @@ def giu_khoa(p: Path | None = None):
         os.close(fd)
 
 
-def ten_ban_chep(giao_id: str) -> str:
-    """Tên MỚI mỗi lần (không dùng lại thư mục của lần trước)."""
-    if not giao_id or "/" in giao_id or giao_id.startswith((".", "-")):
-        raise ValueError(f"giao_id không dùng làm tên thư mục được: {giao_id!r}")
-    return f"{giao_id}-{secrets.token_hex(4)}"
-
-
 def _chay(argv: list[str], *, kill: Kill, timeout: float | None = None, **kw) -> subprocess.CompletedProcess:
     try:
         return chay_gioi_han(argv, kill=kill, capture_output=True, timeout=timeout or THOI_GIAN, **kw)
````

`tram/giao_viec/cong_that.py` (sửa):

````diff
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -19,7 +19,8 @@ from pathlib import Path
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongLuot
-from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, launchd, mo_cong_kiem, tep_ngoai, tien_trinh
+from tram.giao_viec.quan_sat_kiem import (HAN, cron_at, env_kin, goc_rong, launchd, mo_cong_kiem, tep_ngoai,
+                                         tien_trinh)
 from tram.giao_viec.thu_muc_he import don_thu_muc_he
 from tram.kiem.cay_tien_trinh import chup_he
 from tram.kiem.danh_tinh import LoiDanhTinh
@@ -100,19 +101,6 @@ def ho_so_cai(goc: Path, p: Path = HO_SO_KIEM, mf: Path = MANIFEST_KIEM, *, chu:
         raise LoiBanChep(f"hồ sơ {p} khác bản đã duyệt (sinh lại từ manifest) — cài lại bằng `tram chu cai-dat-tho`")
 
 
-def env_kin(cac_du_an: Callable[[], list]) -> None:
-    for da in cac_du_an():
-        mt = da.moi_truong_kiem
-        if mt is None:
-            continue
-        try:
-            st = mt.file.stat()
-        except OSError as e:
-            raise LoiBanChep(f"{da.ten}: không đọc được tệp môi trường kiểm: {e.strerror}") from e
-        if st.st_uid != os.getuid() or st.st_mode & 0o077:
-            raise LoiBanChep(f"{da.ten}: tệp môi trường kiểm phải 0600 của trạm (tram-kiem đọc được env lượt khác)")
-
-
 def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
               thu_hoi: Callable[[], None] | None = None) -> CongLuot:
     goc = goc or tram_home() / "kiem"
````

`tram/giao_viec/kiem_principal.py` (sửa):

````diff
--- a/tram/giao_viec/kiem_principal.py
+++ b/tram/giao_viec/kiem_principal.py
@@ -94,7 +94,8 @@ def kiem_principal(pk, thu_muc: Path | None, *, chay: Callable | None = None, ch
                    uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
     if pk is None:
         return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
-    sud_chay, cong = chay or partial(chay_gioi_han, kill=kill_cuc_bo), cong or dung_cong(pk, thu_muc, cac_du_an=cac_du_an_quan_sat)
+    sud_chay = chay or partial(chay_gioi_han, kill=kill_cuc_bo)
+    cong = cong or dung_cong(pk, thu_muc, cac_du_an=cac_du_an_quan_sat)
     chay = chay or partial(chay_gioi_han, kill=gop_kill(pk.kill_nhom, kill_cuc_bo))
     try:
         sud = kiem_sudoers_khong_root(chay=sud_chay)
````

`tram/giao_viec/lenh.py` (sửa):

````diff
--- a/tram/giao_viec/lenh.py
+++ b/tram/giao_viec/lenh.py
@@ -3,6 +3,7 @@
 (harness S6, `lenh_nghiem_thu.py`) —
 chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
 Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
+import argparse
 import sys
 
 
@@ -93,5 +94,15 @@ def them_lenh_giao(sub) -> None:
     c = g.add_parser("mo-cong-kiem", help="Thu hồi + quan sát tram-kiem rồi mở lại cổng kiểm lại (chờ dong-y)")
     c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã xem lý do đóng)")
     c.set_defaults(ham=_mo_cong)
-    from tram.giao_viec.lenh_nghiem_thu import them
-    them(g)
+    _them_nghiem_thu(g)
+
+
+def _them_nghiem_thu(g) -> None:
+    from tram.giao_viec.lenh_nghiem_thu import lenh_nghiem_thu
+    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
+    h.add_argument("--tai-sinh", action="store_true", help="Thử cài lịch cron/at/launchd như mã agent rồi chờ (G4)")
+    h.add_argument("--cho", type=float, default=300.0, help="Giây chờ quá giờ hẹn của lịch (mặc định 300, ≥ 240)")
+    h.add_argument("--trong", action="store_true", help=argparse.SUPPRESS)
+    h.add_argument("--dau-ino", type=int, default=None, help=argparse.SUPPRESS)
+    h.add_argument("--cha", type=int, default=None, help=argparse.SUPPRESS)
+    h.set_defaults(ham=lenh_nghiem_thu)
````

`tram/giao_viec/lenh_nghiem_thu.py` (sửa):

````diff
--- a/tram/giao_viec/lenh_nghiem_thu.py
+++ b/tram/giao_viec/lenh_nghiem_thu.py
@@ -11,7 +11,6 @@ mới xoá dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem`
 tạo dấu + spawn harness (`chay_han_tong` tự hoãn tới khi con có chủ) — rồi thu hồi + dọn trong `finally` mới trả. Con
 `--trong` giữ tín hiệu mặc định (cha thu hồi cả cây). Mã: 0 không đỏ, 1 đỏ/quá hạn/chưa dọn, 2 không chạy, 130
 Ctrl-C, 143 SIGTERM (dấu còn hay đã xoá in ra stderr)."""
-import argparse
 import math
 import os
 import sys
@@ -110,13 +109,9 @@ def _chay(args, han_tong, xac_minh) -> int:
     except LoiThuHoi as e:                  # HetHanTong là LoiThuHoi
         print(f"[ĐỎ] {e} — {_trang_thai(dau)}", file=sys.stderr)
         return 1
-
-
-def them(g) -> None:
-    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
-    h.add_argument("--tai-sinh", action="store_true", help="Thử cài lịch cron/at/launchd như mã agent rồi chờ (G4)")
-    h.add_argument("--cho", type=float, default=300.0, help="Giây chờ quá giờ hẹn của lịch (mặc định 300, ≥ 240)")
-    h.add_argument("--trong", action="store_true", help=argparse.SUPPRESS)
-    h.add_argument("--dau-ino", type=int, default=None, help=argparse.SUPPRESS)
-    h.add_argument("--cha", type=int, default=None, help=argparse.SUPPRESS)
-    h.set_defaults(ham=lenh_nghiem_thu)
+
+
+def them(g) -> None:
+    """Giữ đường gọi cũ; phần khai tham số thuộc module lenh."""
+    from tram.giao_viec.lenh import _them_nghiem_thu
+    _them_nghiem_thu(g)
````

`tram/giao_viec/phu_thuoc_4c.py` (sửa):

````diff
--- a/tram/giao_viec/phu_thuoc_4c.py
+++ b/tram/giao_viec/phu_thuoc_4c.py
@@ -38,7 +38,8 @@ def luong_lien_quan(gn: GitnexusCli | None, du_an: DuAn, bead: Bead) -> str:
     return boc_khong_tin_cay(van) if van else ""
 
 
-def tao_phu_thuoc_4c(*, github: bool, gitnexus: bool, memory: bool = False, which=shutil.which, chay=subprocess.run) -> PhuThuoc4c:
+def tao_phu_thuoc_4c(*, github: bool, gitnexus: bool, memory: bool = False, which=shutil.which,
+                     chay=subprocess.run) -> PhuThuoc4c:
     """Dựng cho tram-api. `github`/`gitnexus` do người nối bật SAU cổng; recall bật khi có `tram-nho-token`."""
     return PhuThuoc4c(gh=GhCli() if github and which("gh") else None,
                       gitnexus=GitnexusCli() if gitnexus and which("gitnexus") else None,
````

`tram/giao_viec/pr.py` (sửa):

````diff
--- a/tram/giao_viec/pr.py
+++ b/tram/giao_viec/pr.py
@@ -30,7 +30,8 @@ def _pr_mo(gh: GhCli, repo: str, nhanh: str, base: str) -> list[PrInfo]:
             if p.trang_thai in ("OPEN", "MERGED") and p.nhanh == nhanh and p.base == base and not p.ngoai_repo]
 
 
-def dam_bao_pr(gh: GhCli, repo: str, nhanh: str, base: str, commit: str, tieu_de: str, than: str, *, cho_tao: bool = True) -> PrInfo | None:
+def dam_bao_pr(gh: GhCli, repo: str, nhanh: str, base: str, commit: str, tieu_de: str, than: str, *,
+               cho_tao: bool = True) -> PrInfo | None:
     """PR mở duy nhất của `nhanh` → `base`; chưa có thì tạo rồi ĐỌC LẠI (kết quả tạo không rõ vẫn đối soát được).
     Trả None khi head chưa đúng `commit` — không ghi gì, vòng sau thử lại."""
     mo = _pr_mo(gh, repo, nhanh, base)
@@ -69,7 +70,8 @@ def dien_pr(bd, b: Bead, d: dict) -> None:
     bd.cap_nhat_nhan(b.id, ghi_chu=f"{khoi}{dau}\nPR #{d['pr']}: {d['url']}")
 
 
-def mo_pr_bead(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK], luc: datetime) -> str | None:
+def mo_pr_bead(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
+               luc: datetime) -> str | None:
     w = cua_so(ds)
     v = bang_chung_hien_hanh(b, ds)
     if v is None:
````

`tram/giao_viec/quan_sat_kiem.py` (sửa):

````diff
--- a/tram/giao_viec/quan_sat_kiem.py
+++ b/tram/giao_viec/quan_sat_kiem.py
@@ -100,3 +100,16 @@ def launchd(pk, *, doc: Callable | None = None) -> None:
     if doc is None:
         raise LoiBanChep("quan sát launchd user/gui/login của tram-kiem chưa có — G3 chưa đo định dạng launchctl print")
     doc(pk)
+
+
+def env_kin(cac_du_an: Callable[[], list]) -> None:
+    for da in cac_du_an():
+        mt = da.moi_truong_kiem
+        if mt is None:
+            continue
+        try:
+            st = mt.file.stat()
+        except OSError as e:
+            raise LoiBanChep(f"{da.ten}: không đọc được tệp môi trường kiểm: {e.strerror}") from e
+        if st.st_uid != os.getuid() or st.st_mode & 0o077:
+            raise LoiBanChep(f"{da.ten}: tệp môi trường kiểm phải 0600 của trạm (tram-kiem đọc được env lượt khác)")
````

`tram/giao_viec/repo_ban_chep.py` (sửa):

````diff
--- a/tram/giao_viec/repo_ban_chep.py
+++ b/tram/giao_viec/repo_ban_chep.py
@@ -7,6 +7,7 @@ Không cấu hình nào ngoài trạm kiểm soát được chạm vào: `env -i
 `--template=` (không template, không `.git/hooks`), `core.hooksPath=/dev/null` + `--no-verify`. `.gitattributes` của
 cây chỉ GỌI TÊN driver (`filter=lfs`); lệnh `clean`/`process` chỉ đến từ cấu hình — không còn nguồn nào, nên `git add`
 không chạy filter. `.git` trong commit: `git archive` của trạm từ chối (đường dẫn không hợp lệ) → `LoiBanChep`."""
+import secrets
 import shutil
 
 MOI_TRUONG = ("/usr/bin/env", "-i", "PATH=/usr/bin:/bin:/usr/sbin:/sbin", "HOME=/var/empty", "LC_ALL=C",
@@ -33,3 +34,10 @@ def lenh_repo(wt) -> dict[str, list[str]]:
 def lenh_cay(wt) -> list[str]:
     """In cây của HEAD bản chép (dưới `tram-kiem`) để trạm so với cây commit gốc (R7)."""
     return [*_git(wt), "rev-parse", "--verify", "HEAD^{tree}"]
+
+
+def ten_ban_chep(giao_id: str) -> str:
+    """Tên MỚI mỗi lần (không dùng lại thư mục của lần trước)."""
+    if not giao_id or "/" in giao_id or giao_id.startswith((".", "-")):
+        raise ValueError(f"giao_id không dùng làm tên thư mục được: {giao_id!r}")
+    return f"{giao_id}-{secrets.token_hex(4)}"
````

`tram/giao_viec/tick_feature.py` (sửa):

````diff
--- a/tram/giao_viec/tick_feature.py
+++ b/tram/giao_viec/tick_feature.py
@@ -68,7 +68,8 @@ def day_feature(kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str], kg
         ds, kq = su_kien_bead(kho, da.ten, b.id), None
         if ly == "phieu-thieu" and pha != "git":
             kq = "phieu_thieu" if _phieu_thieu(bd, kho, da, b, ds, doc_phieu(b.description, da.ten)[1], luc) else None
-        elif (buoc := buoc_feature(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton))) == "chuyen_duyet" and pha != "nhanh":
+        elif ((buoc := buoc_feature(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton))) == "chuyen_duyet"
+              and pha != "nhanh"):
             kq = "spec_xong" if kg is not None and chuyen_cho_duyet(bd, kho, kg, da, b, ds, luc) else None
         elif buoc == "spec" and pha != "git" and not con_dot_spec(ds):
             kq = "spec_tra_ve_nhieu" if esc(b, "spec-tra-ve-nhieu", CAU_HOI_DOT, f"dot-{bat_dau_dot(ds)}") else None
````

`tram/giao_viec/tick_github.py` (sửa):

````diff
--- a/tram/giao_viec/tick_github.py
+++ b/tram/giao_viec/tick_github.py
@@ -25,7 +25,8 @@ def buoc_github(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, kg: Path | None, l
         ds = su_kien_bead(kho, da.ten, b.id)
         try:
             if NHAN_REVIEW in b.labels:
-                k = mo_pr_bead(gh, repo, kho, kg, da, bd, b, ds, luc) or kiem_merge(gh, repo, kho, kg, da, bd, b, ds, luc)
+                k = (mo_pr_bead(gh, repo, kho, kg, da, bd, b, ds, luc)
+                     or kiem_merge(gh, repo, kho, kg, da, bd, b, ds, luc))
             else:
                 k = mo_pr_spec(gh, repo, kho, kg, da, b, ds, luc)
         except LoiGh:
````

`tram/giao_viec/tick_pipeline.py` (sửa):

````diff
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -38,7 +38,8 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
     p, sha = kho.lay(code.du_lieu["giao_id"]).phieu, sha_code_hop_le(w)
     if p.can_lenh_kiem and bo.boc is None:
         return "cho_boc"                                 # chưa có principal tram-kiem (S6) — không chạy dưới quyền trạm
-    kq = kiem_lai(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem), lenh_cho_phep=list(p.lenh_cho_phep),
+    kq = kiem_lai(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem),
+                  lenh_cho_phep=list(p.lenh_cho_phep),
                   chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                   thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
                   don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot)
````

`tram/nho/mo_hinh.py` (sửa):

````diff
--- a/tram/nho/mo_hinh.py
+++ b/tram/nho/mo_hinh.py
@@ -105,3 +105,12 @@ def ma_thao_tac(su_kien_id: int, phien_ban: int) -> str:
 def id_ky_uc(su_kien_id: int, phien_ban: int, thu_tu: int) -> str:
     """ID ổn định suy từ ID thao tác + số thứ tự (§6.4) — phát lại không sinh ID mới."""
     return "m-" + hashlib.sha256(f"{ma_thao_tac(su_kien_id, phien_ban)}#{thu_tu}".encode()).hexdigest()[:24]
+
+
+@dataclass(frozen=True)
+class ThaoTacNho:
+    ma: str
+    su_kien_id: int
+    trang_thai: str
+    ke_hoach: dict
+    buoc_xong: frozenset[str]
````

`tram/nho/nhat_ky.py` (sửa):

````diff
--- a/tram/nho/nhat_ky.py
+++ b/tram/nho/nhat_ky.py
@@ -4,10 +4,10 @@ Giữ kết quả tách (kế hoạch ghi có ID ký ức ổn định) TRƯỚC
 Đánh dấu hoàn tất + tiến mốc nằm trong MỘT giao dịch SQLite."""
 import json
 import sqlite3
-from dataclasses import dataclass
 from pathlib import Path
 
 from tram.duong_dan import bay_gio
+from tram.nho.mo_hinh import ThaoTacNho
 from tram.su_kien.ket_noi import mo_ket_noi
 
 LUOC_DO = """
@@ -28,15 +28,6 @@ CREATE TABLE IF NOT EXISTS cap_thang_cap (   -- 1b-3: cặp KHÔNG thăng cấp
 """
 
 
-@dataclass(frozen=True)
-class ThaoTacNho:
-    ma: str
-    su_kien_id: int
-    trang_thai: str
-    ke_hoach: dict
-    buoc_xong: frozenset[str]
-
-
 class NhatKy:
     def __init__(self, duong_dan: Path):
         duong_dan.parent.mkdir(parents=True, exist_ok=True)
@@ -96,10 +87,12 @@ class NhatKy:
         return dict(self._db.execute("SELECT cap, trang_thai FROM cap_thang_cap"))
 
     def xoa_noi_dung_ke_hoach(self, id_ky_uc: str) -> int:
-        """Xoá cứng: kế hoạch đã xong/bỏ còn chép nội dung ký ức — xoá luôn (thao tác dở thì người gọi từ chối trước)."""
+        """Xoá cứng: kế hoạch đã xong/bỏ còn chép nội dung ký ức — xoá luôn (thao tác dở thì người gọi từ chối
+        trước)."""
         so = 0
         with self._db:
-            for ma, van_ban in self._db.execute("SELECT ma, ke_hoach FROM thao_tac WHERE trang_thai != 'dang'").fetchall():
+            for ma, van_ban in self._db.execute(
+                    "SELECT ma, ke_hoach FROM thao_tac WHERE trang_thai != 'dang'").fetchall():
                 kh = json.loads(van_ban)
                 doi = False
                 for b in kh.get("buoc", []):
````

`tram/nho/tra_phieu.py` (sửa):

````diff
--- a/tram/nho/tra_phieu.py
+++ b/tram/nho/tra_phieu.py
@@ -32,8 +32,9 @@ def doc_token_noi_bo(*, chay=None) -> str | None:
 
 
 def _dung_dang(d) -> bool:
-    return (isinstance(d, dict) and all(k in d for k in TRUONG) and isinstance(d.get("du_an"), str) and isinstance(d.get("vai"), str)
-            and isinstance(d.get("con_hieu_luc"), bool) and (d.get("ma_giao") is None or isinstance(d["ma_giao"], str)))
+    return (isinstance(d, dict) and all(k in d for k in TRUONG) and isinstance(d.get("du_an"), str)
+            and isinstance(d.get("vai"), str) and isinstance(d.get("con_hieu_luc"), bool)
+            and (d.get("ma_giao") is None or isinstance(d["ma_giao"], str)))
 
 
 class TraPhieu:
````

`tram/phieu/kho.py` (sửa):

````diff
--- a/tram/phieu/kho.py
+++ b/tram/phieu/kho.py
@@ -11,7 +11,7 @@ from pathlib import Path
 
 from tram.duong_dan import tram_home
 from tram.phieu.luoc_do import LUOC_DO
-from tram.phieu.mo_hinh import Phieu
+from tram.phieu.mo_hinh import LuotCu, Phieu
 from tram.su_kien.ghi_trong import ghi_trong_giao_dich
 from tram.su_kien.ket_noi import LUOC_DO as LUOC_DO_SU_KIEN, mo_kho_su_kien
 from tram.su_kien.yeu_cau import LUOC_DO as LUOC_DO_YEU_CAU
@@ -37,14 +37,6 @@ class BanGhiPhieu:
     may_id: str
 
 
-class LuotCu(Exception):
-    """Thẻ chắn từ chối (§6.3): `giao_id` không phải phiếu hiệu lực của bead, hoặc `luot` ≠ `luot` hiện hành."""
-
-    def __init__(self, bead_id: str | None, du_an: str | None, luot_dung: int | None, thu_hoi: bool):
-        super().__init__("luot-cu")
-        self.bead_id, self.du_an, self.luot_dung, self.thu_hoi = bead_id, du_an, luot_dung, thu_hoi
-
-
 class KhoPhieu:
     def __init__(self, duong_dan: Path):
         self.db = mo_kho_su_kien(duong_dan)
````

`tram/phieu/mo_hinh.py` (sửa):

````diff
--- a/tram/phieu/mo_hinh.py
+++ b/tram/phieu/mo_hinh.py
@@ -87,3 +87,11 @@ def sinh_ma_giao() -> str:
 
 def che_ma_giao(van_ban: str, ma_giao: str | None) -> str:
     return van_ban.replace(ma_giao, "***") if ma_giao else van_ban
+
+
+class LuotCu(Exception):
+    """Thẻ chắn từ chối (§6.3): `giao_id` không phải phiếu hiệu lực của bead, hoặc `luot` ≠ `luot` hiện hành."""
+
+    def __init__(self, bead_id: str | None, du_an: str | None, luot_dung: int | None, thu_hoi: bool):
+        super().__init__("luot-cu")
+        self.bead_id, self.du_an, self.luot_dung, self.thu_hoi = bead_id, du_an, luot_dung, thu_hoi
````

`tram/su_kien/kho.py` (sửa):

````diff
--- a/tram/su_kien/kho.py
+++ b/tram/su_kien/kho.py
@@ -1,10 +1,10 @@
 import json
 from collections.abc import Callable
-from dataclasses import dataclass
 from pathlib import Path
 
 from tram.duong_dan import bay_gio, tram_home
 from tram.su_kien.ket_noi import LUOC_DO, mo_kho_su_kien
+from tram.su_kien.mo_hinh import SuKien
 from tram.su_kien.yeu_cau import YeuCauChamLai
 
 _CHON = ("SELECT luc, du_an, bead_id, loai, tac_nhan, du_lieu, id,"
@@ -13,21 +13,6 @@ _CHON = ("SELECT luc, du_an, bead_id, loai, tac_nhan, du_lieu, id,"
 _CAT_CHUOI_LOI = ("cham_cot.ket_qua", "cham_cot.thu_lai")
 
 
-@dataclass(frozen=True)
-class SuKien:
-    luc: str
-    du_an: str
-    bead_id: str | None
-    loai: str
-    tac_nhan: str
-    du_lieu: dict
-    id: int = 0
-    token_vao: int | None = None
-    token_ra: int | None = None
-    mo_hinh: str | None = None
-    thoi_gian_ms: int | None = None
-
-
 class KhoSuKien:
     """Bảng chỉ thêm. Trạng thái hiển thị tính lúc đọc."""
 
````

`tram/su_kien/mo_hinh.py` (mới):

```python
"""Một dòng của kho sự kiện (tách khỏi `kho.py` — bs-2bd.1.20, chỉ dời chỗ)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SuKien:
    luc: str
    du_an: str
    bead_id: str | None
    loai: str
    tac_nhan: str
    du_lieu: dict
    id: int = 0
    token_vao: int | None = None
    token_ra: int | None = None
    mo_hinh: str | None = None
    thoi_gian_ms: int | None = None
```

`tram/suy/nhan_vat.py` (sửa):

````diff
--- a/tram/suy/nhan_vat.py
+++ b/tram/suy/nhan_vat.py
@@ -58,8 +58,8 @@ def _mot(kho: KhoPhieu, tt: TrangThaiKhe, ten: str, cac_du_an: list[str]) -> dic
         bead = _bead(tt.phieu)
     elif trang_thai != "lam":
         cuoi = _phieu_cuoi(kho, tt.khe_id)
-        if (trang_thai in ("ranh", "loi") and not tt.cau_dao.get("ngat") and cuoi is not None and cuoi["trang_thai"] == "ket_thuc"
-                and _escalation_mo(kho, cuoi["du_an"], cuoi["giao_id"])):
+        if (trang_thai in ("ranh", "loi") and not tt.cau_dao.get("ngat") and cuoi is not None
+                and cuoi["trang_thai"] == "ket_thuc" and _escalation_mo(kho, cuoi["du_an"], cuoi["giao_id"])):
             trang_thai, bead = "can_nguoi", _bead(cuoi)
     noi = bead or (cuoi if trang_thai != "ranh" else None)
     phong = ma_phong_du_an(noi["du_an"]) if noi and noi["du_an"] in cac_du_an else CA_PHE
````

`tram/thao_tac/duyet_spec.py` (sửa):

````diff
--- a/tram/thao_tac/duyet_spec.py
+++ b/tram/thao_tac/duyet_spec.py
@@ -90,7 +90,8 @@ def duyet_spec(nc: NguCanhGhi, ns: NguonSpec, bead_id: str, *, ma: str, expected
     yc = YeuCau(ma, "duyet_spec", nc.du_an, bead_id, {"expected_commit": expected_commit, "digest_bead": digest_bead},
                 expected_version)
     return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[
-        ("tao_bead", bao_ve(lambda _: tao_con(ns.bd_tram, bead_id, _ke_hoach(ns, bead_id, expected_commit, digest_bead)))),
+        ("tao_bead", bao_ve(lambda _: tao_con(ns.bd_tram, bead_id,
+                                              _ke_hoach(ns, bead_id, expected_commit, digest_bead)))),
         ("phu_thuoc", bao_ve(lambda da: noi_phu_thuoc(ns.bd_tram, _ke_hoach(ns, bead_id, expected_commit, digest_bead),
                                                da["tao_bead"]))),
         ("nhan", bao_ve(nhan)), ("su_kien", bao_ve(su_kien))])
````

`tram/tho/kiem_may.py` (sửa):

````diff
--- a/tram/tho/kiem_may.py
+++ b/tram/tho/kiem_may.py
@@ -63,7 +63,8 @@ def _kho(dd: DauDo) -> list[MucKiem]:
         env = [x for x in (p / ".env", *p.glob("*/.env")) if x.exists()]
         ra.append(MucKiem(f"kho {ten}", "do" if not p.is_dir() or env else "xanh",
                           "chưa clone" if not p.is_dir() else (f"có .env thật: {env[0]}" if env else str(p))))
-    return ra + ([] if dd.cach_ly else [MucKiem("quyền ghi worktree", "do", "chờ spike S6 (principal thực thi của khe)")])
+    return ra + ([] if dd.cach_ly
+                 else [MucKiem("quyền ghi worktree", "do", "chờ spike S6 (principal thực thi của khe)")])
 
 
 def kiem_may(ch: CauHinhTho, dd: DauDo) -> list[MucKiem]:
@@ -74,7 +75,8 @@ def kiem_may(ch: CauHinhTho, dd: DauDo) -> list[MucKiem]:
         ping, ra = {}, [MucKiem("tram-api", "do", str(e))]
     ra += _khe(ch, dd, {k["khe_id"]: k["cau_dao"] for k in ping.get("khe", [])})
     try:
-        ra += dd.cach_ly() if dd.cach_ly else [MucKiem("cách ly", "do", "chờ spike S6 — bộ kiểm chứng âm §7.3 mục 7 chưa có")]
+        ra += (dd.cach_ly() if dd.cach_ly
+               else [MucKiem("cách ly", "do", "chờ spike S6 — bộ kiểm chứng âm §7.3 mục 7 chưa có")])
     except Exception as e:                                # noqa: BLE001
         ra.append(MucKiem("cách ly", "do", f"không chạy được kiểm chứng âm: {e}"))
     ra += _kho(dd)
````

`tram/tho/lenh_khe.py` (sửa):

````diff
--- a/tram/tho/lenh_khe.py
+++ b/tram/tho/lenh_khe.py
@@ -34,8 +34,10 @@ def _ap_dung(args, moi: str, ke_hoach: list[str]) -> int:
     p = tram_home() / "tho.yaml"
     p.write_text(moi, encoding="utf-8")
     ch = nap_cau_hinh_tho(p)
-    ma, kq = KhachTram(ch.tram_api, doc_token_may() or "").goi("POST", "/api/tho/dang-ky", {"may_id": ch.may_id, "khe": [
-        {"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho, "vai_uu_tien": list(k.vai_uu_tien)} for k in ch.khe]})
+    ma, kq = KhachTram(ch.tram_api, doc_token_may() or "").goi(
+        "POST", "/api/tho/dang-ky",
+        {"may_id": ch.may_id, "khe": [{"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho,
+                                       "vai_uu_tien": list(k.vai_uu_tien)} for k in ch.khe]})
     print(f"Đã ghi {p}; đăng ký với trạm: {ma}")
     return 0 if ma == 200 else 2
 
````

- [ ] **Step 4: Chạy thấy xanh**

Run: `tests/chan_host/chay.sh -q tests/test_do_dai_ma.py tests/test_vong_import.py tests/test_beads.py tests/test_ban_giao.py tests/test_go_cai_dat_tho.py tests/test_lenh_nghiem_thu.py tests/test_du_an_quan_sat.py tests/test_cong_that.py tests/test_kiem_principal.py tests/test_kho_phieu.py tests/test_nho_ap_dung.py tests/test_ban_chep_pipeline_han.py`
Expected (thật, 18/10): `116 passed in 10.11s`, nhật ký chặn 0 dòng mới.

Run cả bộ: `tests/chan_host/chay.sh -q`
Expected (thật, 18/10): `3233 passed in 325.86s (0:05:25)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629 (= N₀ + 3 test mới).

- [ ] **Step 5: Commit** — `fix(tram): file và dòng ≤ 120 — dời khối tự đứng, xuống dòng, không đổi hành vi (bs-2bd.1.20)` + dòng `Co-Authored-By` của model viết.

### Task V3-19: Tài liệu sở hữu theo mã đã ghép

**Files:** Modify `docs/AGENT_RULES.md` (§13 đoạn "PATH chặn host" — bổ sung, giữ hàng bảng và câu của điều phối), `docs/DEPLOY.md` (§2 câu khoá thiếu, §3 bảng + cài từng dịch vụ + hạn + siết quyền + gỡ dịch vụ, §5 sao lưu + khôi phục, §6 bước 3), `docs/ARCHITECTURE.md` (tầng Nền, Lược đồ DB), `docs/MODULES.md` (vòng import, bảng package, `tram/keychain.py`, tích hợp Anthropic/Keychain/`launchctl`, Kiểm thử), `docs/ENGINEERING_STANDARDS.md` (Kiểu code, Quy tắc kiến trúc, quyền `~/.tram`, sao lưu). KHÔNG sửa `CLAUDE.md`, `AGENTS.md` (điều phối đã sửa lệnh test ở `92430e0`), `CURRENT_STATE.md`.

Nguồn mã đã đọc cho từng câu: `tests/chan_host/chay.sh`, `chan_host.py` (bộ chặn); `tram/chu/lenh_cai_dat.py`, `dich_vu_tram.py`, `cai_dat.py`, `cai_dat_nho.py` (`HAN_NHO`), `go_dich_vu.py`, `chung_cu_go.py`, `khoi_phuc_su_kien.py`, `siet_quyen.py`; `tram/cau_hinh/bat_ghi.py`; `tram/su_kien/phien_ban.py`, `ket_noi.py`, `mo_an_toan.py`, `ban_sao.py`, `sao_luu.py`; `tram/duong_dan.py` (`tram_home()` chỉ `mkdir`, không ép quyền); `tram/llm/han_goi.py` (`HAN_GOI_GIAY = 120`, `TOI_DA_LUONG = 2`), `tram/llm/claude.py` (`max_retries=0`); `tram/keychain.py` (`HAN_GIAY = 10`, `doc_muc`/`co_muc`); `tram/kiem/so_huu.py`, `ngat.py`, `bang_tien_trinh.py`, `giu_xac.py`, `gui_tin.py`; `tram/tho/don_uid.py`, `cham_tham_do.py`; `tram/giao_viec/chung_cu_probe.py`, `ong_chep.py`; `tests/test_vong_import.py`. Cài máy thợ (`cai_dat_tho.py`) không có `han_lenh` → docs ghi "chưa đặt hạn từng lệnh".

- [ ] **Step 1: Áp bản vá docs** (dựng trên `92430e0`, sau V3-18)

`docs/AGENT_RULES.md` (sửa):

````diff
--- a/docs/AGENT_RULES.md
+++ b/docs/AGENT_RULES.md
@@ -157,10 +157,12 @@
 | Tích hợp ngoài | test với bản giả `tests/*_gia.py`; không gọi thật |
 | Chạy thật, dịch vụ, OS | **chỉ theo cổng sổ tay**, đúng kịch bản Đại ca cho phép; ghi bằng chứng (lệnh, giờ, kết quả) vào sổ tay |
 
-**PATH chặn host:** đặt trước `PATH` một thư mục lệnh giả cho `sudo`, `crontab`, `at`, `batch`, `launchctl`,
-`security`, `dscl`, `sysadminctl`, `sandbox-exec`, `pkill`, `killall`, `bd`, `gh`, và `git` (chặn `push`); mỗi lệnh
-giả chỉ ghi nhật ký rồi thoát lỗi. Bộ chạy có trong repo: `tests/chan_host/` (lệnh giả, audithook, git giả — push chỉ giả lập).
-Không phải sandbox: runner in số "điểm mù" (Python con không mang bộ chặn).
+**PATH chặn host:** `tests/chan_host/chay.sh [tham số pytest]` đặt `tests/chan_host/bin/` đầu `PATH`: lệnh giả cho
+`sudo`, `crontab`, `at`, `batch`, `launchctl`, `security`, `dscl`, `sysadminctl`, `sandbox-exec`, `pkill`, `killall`,
+`bd`, `gh`… chỉ ghi nhật ký rồi thoát lỗi; `git` giả không bao giờ push thật (push vào kho trong thư mục tạm được giả
+lập, còn lại chặn). Audithook (pytest và Python con mang `PYTHONPATH` của bộ chặn) bắt cả đường tuyệt đối, lệnh bọc,
+chuỗi shell. Nhật ký chặn có dòng mới → thoát 3 dù test xanh. Không phải sandbox: runner in số "điểm mù" (Python con
+không mang bộ chặn). Luật §11 vẫn nguyên. Thêm lệnh cấm: sửa cả `bin/` và `CHAN` trong `tests/chan_host/chan_host.py`.
 
 ## 14. Dữ liệu, secrets và hardcode
 - Bí mật **không bao giờ** nằm trong argv, file, log, báo cáo, bead hay docs. Tên mục Keychain thì được ghi.
````

`docs/DEPLOY.md` (sửa):

````diff
--- a/docs/DEPLOY.md
+++ b/docs/DEPLOY.md
@@ -2,7 +2,7 @@
 
 Project: `ben-station`
 Status: `ACTIVE`
-Cập nhật: `2026-10-17`
+Cập nhật: `2026-10-18`
 
 ## Mục đích và sở hữu
 Sở hữu **quy trình chung**: cài và gỡ dịch vụ launchd, cấu hình `~/.tram`, tên mục Keychain, `tailscale serve`,
@@ -54,10 +54,10 @@
 | `usage` (`ccusage`, `ccusage_phien_ban`, `gia_usd_moi_trieu_token`) | màn Usage | `tram/cau_hinh/usage.py` |
 | `ma_dai_ca_sha256`, `dieu_phoi_ma_sha256` | bản băm mã, đặt bằng `tram chu dat-ma-dai-ca`, `dat-ma-dieu-phoi` | `tram/nho/ma_dai_ca.py` |
 
-Khoá thiếu → giá trị an toàn (tắt, `kenh_ghi: header`, chưa chọn công bố). `giao_viec.bat`, `bat_ghi` và
-ngưỡng hạn mức thuộc kill list. Máy thợ có `~/.tram/tho.yaml` riêng (`tram/tho/cau_hinh.py`). Dự án con:
-`du-an/<ten>.yaml` trong repo, tạo bằng `tram du-an them <repo>` (mặc định `bat_ghi: false`), gỡ khối trạm bằng
-`tram du-an go <repo>`.
+Khoá thiếu → giá trị an toàn (tắt, `kenh_ghi: header`, chưa chọn công bố; `du-an/*.yaml` thiếu `bat_ghi` = tắt
+ghi, `tram/cau_hinh/bat_ghi.py`). `giao_viec.bat`, `bat_ghi` và ngưỡng hạn mức thuộc kill list. Máy thợ có
+`~/.tram/tho.yaml` riêng (`tram/tho/cau_hinh.py`). Dự án con: `du-an/<ten>.yaml` trong repo, tạo bằng
+`tram du-an them <repo>` (mặc định `bat_ghi: false`), gỡ khối trạm bằng `tram du-an go <repo>`.
 
 **Keychain — chỉ tên mục**, của tài khoản trạm trừ khi ghi khác. Đại ca tự tạo qua Terminal.app; agent không đọc:
 
@@ -73,34 +73,44 @@
 Agent và mã dự án chạy dưới principal khác, không có các mục này.
 
 ## 3. Dịch vụ launchd
-Nhãn và lệnh lấy từ `tram/chu/launchd.py`, `tram/chu/cai_dat.py`, `tram/chu/cai_dat_nho.py`, `tram/chu/cai_dat_tho.py`,
-`tram/tho/launchd_tho.py`. Log ở `~/.tram/log/<tên>.log`.
+Nhãn và lệnh lấy từ `tram/chu/launchd.py`, `tram/chu/dich_vu_tram.py`, `tram/chu/cai_dat.py`, `tram/chu/cai_dat_nho.py`,
+`tram/chu/cai_dat_tho.py`, `tram/tho/launchd_tho.py`. Log ở `~/.tram/log/<tên>.log`.
 
 | Nhãn | Chạy | Kiểu | Cài bằng |
 | --- | --- | --- | --- |
-| `vn.tram.quet` | `tram quet --ghi` | mỗi 120 giây | `tram chu cai-dat` |
-| `vn.tram.api` | `tram api` (127.0.0.1:7700) | thường trực | `tram chu cai-dat` |
-| `vn.tram.bao-tin` | `tram bao-tin` | thường trực | `tram chu cai-dat` |
-| `vn.tram.sao-luu` | `tram chu sao-luu` | hằng ngày 03:15 | `tram chu cai-dat` |
+| `vn.tram.quet` | `tram quet --ghi` | mỗi 120 giây | `tram chu cai-dat --dich-vu quet` |
+| `vn.tram.api` | `tram api` (127.0.0.1:7700) | thường trực | `tram chu cai-dat --dich-vu api` |
+| `vn.tram.bao-tin` | `tram bao-tin` | thường trực | `tram chu cai-dat --dich-vu bao-tin` |
+| `vn.tram.sao-luu` | `tram chu sao-luu` | hằng ngày 03:15 | `tram chu cai-dat --dich-vu sao-luu` |
 | `vn.tram.nho` | `tram nho chay` (127.0.0.1:7710) | thường trực | `tram chu cai-dat --nho` |
 | `vn.tram.tho` | `tram tho chay` | thường trực | B: `tram chu cai-dat-tho` (LaunchDaemon có `UserName`); Mac thợ: plist `tram/tho/launchd_tho.py` |
 
-- Bốn dịch vụ đầu là LaunchAgent trong `~/Library/LaunchAgents`, miền `gui/<uid>`. **`tram chu cai-dat` cài cả
-  bốn một lần**, kể cả `vn.tram.quet` chạy `--ghi` (ghi nhãn cột vào dự án `bat_ghi: true`). Đại ca chốt 17/10: tách
-  cài từng dịch vụ — bead `bs-2bd.1.23`; tới lúc đó chỉ cài khi đúng cổng sổ tay.
-- Mọi lệnh cài in kế hoạch (file sẽ ghi, lệnh sẽ chạy, cảnh báo) rồi chờ gõ `dong-y`. Mỗi dịch vụ: `launchctl bootout`
-  (bỏ qua lỗi nếu chưa nạp) rồi `launchctl bootstrap`.
+- Bốn dịch vụ đầu là LaunchAgent trong `~/Library/LaunchAgents`, miền `gui/<uid>`. `tram chu cai-dat` cài **đúng
+  dịch vụ chọn** bằng `--dich-vu` (lặp lại được, không có mặc định; `--nho` là lệnh riêng, không đi cùng `--dich-vu`).
+  Chọn `quet` (chạy `--ghi`): kế hoạch in từng dự án sẽ bị ghi / chỉ đọc; không đọc được `du-an/*.yaml` hay khoá
+  `bat_ghi` của một dự án thì thoát 2, không cài gì.
+- Mọi lệnh cài in kế hoạch (file sẽ ghi, bước, lệnh sẽ chạy, cảnh báo) rồi chờ gõ `dong-y`. `cai-dat --dich-vu`:
+  ghi plist kèm **biên nhận** `~/.tram/dich-vu/<nhãn>.json` (sha256 plist — chứng cứ sở hữu cho lệnh gỡ), siết quyền
+  `~/.tram` theo phạm vi `siet-quyen` bên dưới, rồi `launchctl bootout` (bỏ qua mã lỗi) và `launchctl bootstrap`.
+- Hạn từng tích hợp: `MODULES.md` mục Tích hợp ngoài (Keychain, launchctl, tải/cài memory). Quá hạn trong
+  thực hiện kế hoạch → dừng, lệnh sau không chạy, thoát 3; cần đối soát phần đã làm trước khi thử lại.
+  Timeout của subprocess không chứng minh toàn bộ cây con đã dừng; xác nhận ở cổng sổ tay.
 - Thường trực dùng `KeepAlive` chỉ khi thoát lỗi: `tram bao-tin` thoát mã 0 khi thiếu token hay `chat_id` nên launchd
   **không tự bật lại** — cấu hình xong, Đại ca chạy `launchctl kickstart -k gui/<uid>/vn.tram.bao-tin`.
 - Sau khởi động máy, Keychain còn khoá tới khi đăng nhập: `vn.tram.nho` không đọc được token, tự dừng; đăng nhập
   xong kickstart lại. tram-api đọc `tram-noi-bo-token` một lần ở yêu cầu đầu; đổi token thì kickstart `vn.tram.api`.
 - Xem (chỉ đọc): `tram chu trang-thai`, `launchctl list | grep vn.tram`, log trong `~/.tram/log/`.
+- Quyền `~/.tram` cũ: `tram chu siet-quyen` (liệt kê, chờ `dong-y`); phạm vi bảo đảm và mục bỏ qua ở
+  `ENGINEERING_STANDARDS.md` mục Quy tắc bảo mật. Cài `--dich-vu` gọi bước này trước khi nạp dịch vụ.
 
 **Gỡ:**
 - Máy thợ: `tram chu go-cai-dat-tho [--xoa-nha]` — chỉ gỡ thứ sổ cài ghi đã tạo, còn đúng định danh; user luôn
   giữ nhà trừ khi `--xoa-nha`. Thu hồi token và phiếu của một máy: `tram chu go-may <may_id>`.
-- Dịch vụ trên B: **chưa có lệnh `tram` gỡ** (suy từ code, chưa xác nhận). Gỡ tay: `launchctl bootout
-  gui/<uid>/<nhãn>`, rồi chuyển plist khỏi `~/Library/LaunchAgents` (cách gỡ tay chưa kiểm trên máy).
+- Dịch vụ trên B: `tram chu go-dich-vu --dich-vu <api|quet|bao-tin|sao-luu|nho>` (lặp lại được; liệt kê, chờ
+  `dong-y`). Chỉ gỡ dịch vụ có biên nhận khớp plist (cài trước khi có biên nhận: chạy lại `cai-dat` trước); thiếu hay
+  lệch chứng cứ → từ chối cả kế hoạch. Đang nạp từ plist khác → dừng, không bootout. Sau `bootout` đọc lại
+  `launchctl print`: chỉ khi đã vắng mới cất plist vào `~/.tram/go-dich-vu/` (không xoá, không ghi đè); còn nạp hay
+  không rõ → dừng, plist giữ nguyên. Nguồn: `tram/chu/go_dich_vu.py`, `tram/chu/chung_cu_go.py`.
 
 ## 4. Tailscale serve
 tram-api và memory chỉ nghe localhost; ra tailnet **chỉ** qua `tailscale serve`. Trạm chỉ **in** lệnh, Đại ca tự chạy
@@ -109,9 +119,14 @@
 chờ spike N2. `dashboard_url` trong cấu hình phải là địa chỉ `https://` của tailnet.
 
 ## 5. Sao lưu và khôi phục — chốt TRƯỚC khi chạy
-- **Kho sự kiện:** `tram chu sao-luu [--giu 14]` → `~/.tram/sao-luu/su-kien-<thời điểm>.db` (online backup của
-  SQLite), giữ 14 bản; `vn.tram.sao-luu` chạy 03:15 mỗi ngày khi đã cài. Khôi phục: chưa có lệnh (suy từ code,
-  chưa xác nhận) — dừng mọi dịch vụ ghi trước khi thay file.
+- **Kho sự kiện:** `tram chu sao-luu [--giu 14]` → `~/.tram/sao-luu/su-kien-<thời điểm>.db` (online backup có hạn,
+  file mới độc quyền 600 trong thư mục 700), giữ 14 bản; `vn.tram.sao-luu` chạy 03:15 mỗi ngày khi đã cài. Mã mới
+  nâng số phiên bản cấu trúc kho thì để bản `truoc-nang-v<cũ>-v<mới>-*.db` cạnh đó.
+- **Khôi phục kho sự kiện:** ghi lại dịch vụ đang nạp; dừng mọi bên mở kho, kể cả CLI. Chỉ gỡ dịch vụ có biên nhận
+  hợp lệ theo mục 3; thiếu chứng cứ thì Đại ca dừng theo kịch bản sổ tay, không cài/bật thêm để lấy biên nhận.
+  Chạy `tram chu khoi-phuc-su-kien <tên bản trong ~/.tram/sao-luu>`: kiểm toàn vẹn/phiên bản/cấu trúc, khoá bảo trì,
+  chép kho cũ ra `truoc-khoi-phuc-*.db`, thay và so vân tay. Chỉ khởi động lại dịch vụ đã chạy trước bảo trì và được
+  duyệt ở cổng; giữ dịch vụ vốn tắt. Nguồn: `tram/chu/khoi_phuc_su_kien.py` (khoá từ chối khi còn bên mở kho WAL).
 - **Memory:** `vn.tram.nho` tự bảo trì mỗi ngày sau 3 giờ sáng giờ VN: thăng cấp, dọn, chụp LanceDB + nhật ký thao
   tác cùng một điểm → `~/.tram/sao-luu/nho-<thời điểm>`, giữ 14 bản. Khôi phục: dừng dịch vụ
   (`launchctl bootout gui/<uid>/vn.tram.nho`), `tram nho khoi-phuc <bản>`; bản đang có được giữ lại, không xoá.
@@ -122,7 +137,7 @@
 Đường lui riêng của từng cổng (thu hồi tiến trình, dọn lịch, gỡ principal) ở phụ lục cổng mục "Thu hồi và đường lui".
 1. **Dừng khẩn cấp:** `tram chu estop` (vòng quét, tick giao việc, cấp phiếu, thợ đều dừng); bỏ: `tram chu tiep-tuc`.
 2. **Tắt công tắc:** `giao_viec.bat: false`; dự án về `bat_ghi: false`; khe: `tram tho tat-khe <khe>`.
-3. **Dừng dịch vụ:** `launchctl bootout gui/<uid>/<nhãn>` (Đại ca gõ).
+3. **Dừng dịch vụ:** `launchctl bootout gui/<uid>/<nhãn>` (Đại ca gõ); gỡ hẳn: `tram chu go-dich-vu` (mục 3).
 4. **Thu hồi máy thợ:** `tram chu go-may <may_id>`; gỡ cài đặt thợ: `tram chu go-cai-dat-tho`.
 5. **Dữ liệu:** khôi phục từ mục 5. Cổng kiểm lại đã đóng thì **chỉ Đại ca mở lại** sau đối soát (D49).
 
````

`docs/ARCHITECTURE.md` (sửa):

````diff
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -2,7 +2,7 @@
 
 Project: `ben-station`
 Status: `ACTIVE`
-Cập nhật: `2026-10-17`
+Cập nhật: `2026-10-18`
 
 ## Mục đích và sở hữu
 Sở hữu: tầng, luật module, hợp đồng chung, luồng dữ liệu, ràng buộc.
@@ -22,7 +22,7 @@
 | Điểm vào | lệnh `tram …`, dịch vụ launchd | `tram/cli.py`, `tram/cli_*.py`, `tram/*/lenh*.py` |
 | HTTP | tram-api: đọc cho dashboard, ghi có xác thực, API thợ, API nội bộ | `tram/api/` |
 | Thao tác, suy, nghiệp vụ | xem [MODULES.md](MODULES.md) | `tram/thao_tac/`, `tram/suy/`, các package còn lại |
-| Nền | đường dẫn, kho sự kiện, cấu hình, client `bd`, LLM, chạy CLI, schema bàn giao | `tram/duong_dan.py`, `tram/su_kien/`, `tram/cau_hinh/`, `tram/beads/`, `tram/llm/`, `tram/chay_cli/`, `tram/ban_giao/` |
+| Nền | đường dẫn, Keychain, kho sự kiện, cấu hình, client `bd`, LLM, chạy CLI, schema bàn giao | `tram/duong_dan.py`, `tram/keychain.py`, `tram/su_kien/`, `tram/cau_hinh/`, `tram/beads/`, `tram/llm/`, `tram/chay_cli/`, `tram/ban_giao/` |
 | Giao diện | SPA hash-router; trang, thành phần, văn phòng 3D | `frontend/src/` |
 | Ngoài gói | prompt và quyền theo vai; skill và hook máy A; cấu hình dự án | `vai/`, `ky-nang/`, `may-a/`, `du-an/` |
 
@@ -45,7 +45,9 @@
 - **Sự kiện:** chỉ ghi thêm; trạng thái hiển thị tính lúc đọc (`tram/suy/`). Thao tác ghi mang ID để thử lại
   không tạo trùng (`tram/thao_tac/`).
 - **Lượt (fencing):** mọi báo cáo của thợ mang số lượt; lượt cũ bị từ chối (`tram/phieu/`).
-- **Lược đồ DB:** chỉ `CREATE … IF NOT EXISTS`, **chưa có migration** — tạm, phải thêm trước chạy thật.
+- **Lược đồ DB:** bảng tạo bằng `CREATE … IF NOT EXISTS`. `su-kien.db` có số phiên bản cấu trúc
+  (`PRAGMA user_version`, `tram/su_kien/phien_ban.py`): cần nâng thì giữ khoá ghi, sao lưu nếu đã có bảng rồi
+  áp trong một giao dịch; kho mới hơn mã thì từ chối mở. `nhat-ky.db` của memory và LanceDB chưa có số phiên bản.
   Nguồn: `tram/su_kien/ket_noi.py`, `tram/phieu/luoc_do.py`, `tram/nho/bang.py`.
 - **Nội dung bead và bàn giao là dữ liệu không tin cậy** khi đưa vào prompt.
 
````

`docs/MODULES.md` (sửa):

````diff
--- a/docs/MODULES.md
+++ b/docs/MODULES.md
@@ -2,14 +2,15 @@
 
 Project: `ben-station`
 Status: `ACTIVE`
-Cập nhật: `2026-10-17`
+Cập nhật: `2026-10-18`
 
 ## Mục đích và sở hữu
 Tầng 2 — đọc khi task chạm package, tích hợp ngoài hay bộ test. Tách từ `ARCHITECTURE.md` để giữ Tầng 1 trong ngân sách.
 Sở hữu: package nào giữ gì, vòng import, tích hợp ngoài, bộ test. Không sở hữu: tầng, hợp đồng chung, luồng, ràng buộc (`ARCHITECTURE.md`).
 
 ## Vòng import
-- Nguồn sự thật danh sách package: `ls tram/`. Không có registry, không có test kiến trúc cưỡng chế ranh giới.
+- Nguồn sự thật danh sách package: `ls tram/`. Không có registry, không có test cưỡng chế ranh giới package.
+  `tests/test_vong_import.py` chặn vòng import ở cấp **module** (import chạy lúc nạp) và `__init__.py` có import.
 - **Có vòng import ở cấp package**, ví dụ `cau_hinh ↔ giao_viec`, `giao_viec ↔ tho`, `api ↔ chu`,
   `cham_cot ↔ nho`, `chay_cli ↔ phieu`. Chạy được vì mỗi file import đúng module con nó cần (không qua
   `__init__`), và một số chỗ **import trễ trong hàm**: `tram/cli*.py`, `chu → phieu`, `nho → api, llm`,
@@ -20,19 +21,19 @@
 ## Bản đồ module
 | Package | Sở hữu |
 | --- | --- |
-| `tram/su_kien/` | kho sự kiện `~/.tram/su-kien.db` (WAL, nhiều tiến trình), ghi thêm, sao lưu |
+| `tram/su_kien/` | kho sự kiện, ghi thêm, sao lưu (`ban_sao.py`); phiên bản cấu trúc (`phien_ban.py`); mở kho theo chuỗi cha được tin (`mo_an_toan.py`, `thu_muc_an_toan.py`); hợp đồng ở `ARCHITECTURE.md`, quyền ở `ENGINEERING_STANDARDS.md` |
 | `tram/cau_hinh/` | đọc `~/.tram/cau-hinh.yaml`, `du-an/*.yaml`; khoá `cach_ly`, `giao_viec`, `cong_bo`, `usage`, `bat_ghi` |
 | `tram/beads/` | gọi `bd` của dự án con (đọc, ghi nhãn), mô hình bead |
 | `tram/cham_cot/` | chấm cột: luật cứng trước, Claude API sau, ghi `cot:*` |
-| `tram/llm/` | client Anthropic (khoá lấy từ Keychain) |
+| `tram/llm/` | client Anthropic (khoá lấy từ Keychain); hạn chờ mỗi lời gọi, trần lời gọi còn sống (`han_goi.py`) |
 | `tram/du_an/` | `tram du-an them`: thêm dự án ở chế độ chỉ đọc |
 | `tram/phieu/` | kho phiếu: khe, máy thợ, lượt, giữ ngân sách, cầu dao hạn mức, mã ghép |
 | `tram/han_muc/` | đọc hạn mức CLI, ngưỡng ngừng |
 | `tram/usage/` | đếm usage (ccusage tuỳ chọn) |
-| `tram/giao_viec/` | vòng tick, pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, xác minh merge |
-| `tram/tho/` | tiến trình quản lý thợ: đăng ký, nhịp tim, chạy CLI dưới principal, sandbox, worktree, bàn giao |
+| `tram/giao_viec/` | vòng tick, pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu (`ong_chep.py`) |
+| `tram/tho/` | tiến trình quản lý thợ: đăng ký, nhịp tim, chạy CLI dưới principal, sandbox, worktree, bàn giao; dọn theo UID của khe (`don_uid.py`), chấm thăm dò cách ly (`cham_tham_do.py`) |
 | `tram/chay_cli/` | dựng lệnh `claude -p` / `codex`, đọc stream, quyền theo vai |
-| `tram/kiem/` | chạy lệnh có giới hạn, cây tiến trình, danh tính UID, vòng đời tiến trình, đường cấm |
+| `tram/kiem/` | chạy lệnh có giới hạn, cây tiến trình, danh tính UID, vòng đời tiến trình, đường cấm; hợp đồng sở hữu tiến trình con (`so_huu.py`), hoãn ngắt (`ngat.py`), bảng tiến trình của nhân (`bang_tien_trinh.py`), giữ xác gốc (`giu_xac.py`), gửi tín hiệu nhóm (`gui_tin.py`) |
 | `tram/cong_bo/` | công bố nhánh `tram/<bead>`, đối soát push |
 | `tram/ban_giao/` | schema và đọc file bàn giao của agent |
 | `tram/nho/` | memory service + MCP (cổng 7710): tách/gộp ký ức, embed, quét bí mật, thăng cấp, phạm vi |
@@ -40,8 +41,9 @@
 | `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe |
 | `tram/suy/` | tính trạng thái hiển thị từ sự kiện + beads |
 | `tram/api/` | tram-api: router, bảo mật, kênh ghi, API thợ, ghép máy, nội bộ, điều phối |
-| `tram/chu/` | lệnh trạm chủ: cài/gỡ launchd, estop, cấp mã, kiểm cách ly, trạng thái |
+| `tram/chu/` | lệnh trạm chủ: cài từng dịch vụ launchd kèm biên nhận, gỡ theo biên nhận (`go_dich_vu.py`, `chung_cu_go.py`), khôi phục kho sự kiện (`khoi_phuc_su_kien.py`), siết quyền `~/.tram` (`siet_quyen.py`), estop, cấp mã, kiểm cách ly, trạng thái |
 | `tram/bao_tin/` | vòng báo tin Telegram, chống ồn |
+| `tram/keychain.py` | đọc mục Keychain có hạn (module ở gốc gói) |
 
 ## Tích hợp ngoài
 Cột "Hỏng thì" suy từ code, chưa xác nhận.
@@ -51,13 +53,15 @@
 | `bd` (Beads) | đọc/ghi việc của dự án con | 120 giây | API trả 502; vòng quét ghi lỗi |
 | `git`, `gh` | worktree, công bố, mở/xem PR (không merge) | theo lệnh | bead ở lại cột 3, sự kiện lỗi |
 | `claude -p`, `codex` | agent thợ chạy việc | trần của phiếu | thu hồi phiếu, giao lại |
-| Anthropic API | chấm cột, tách/gộp ký ức | **chưa đặt trong repo** (mặc định SDK) | vòng chấm hay memory chờ lâu |
+| Anthropic API | chấm cột, tách/gộp ký ức | chờ tối đa 120 giây/lời gọi, kể cả đợi chỗ; SDK không retry (`tram/llm/han_goi.py`) | quá hạn: bỏ chờ, không huỷ luồng; tối đa 2 luồng sống/tiến trình; hết chỗ: chờ tới hạn rồi lỗi, không mở lời gọi mới |
 | Ollama bge-m3 | embed ký ức (chỉ localhost) | 30 giây | memory báo lỗi, không lùi về vector giả |
 | Telegram | báo tin ngắn | 10 giây | mất tin, vòng sau gửi lại |
 | Tailscale | danh tính Đại ca, nối A–B | — | ghi bị 403 |
 | `ccusage` | đếm usage (tuỳ chọn) | 60 giây | trang Usage báo chưa biết |
-| `security` (Keychain) | lấy khoá | **chưa đặt** | thiếu khoá: báo lỗi rõ; treo: chờ không giới hạn |
-| `sudo -u`, `sandbox-exec`, `launchctl` | chạy dưới principal, cách ly, dịch vụ | theo `tram/kiem/` | cổng đóng |
+| `security` (Keychain) | lấy khoá | 10 giây (`tram/keychain.py`) | đọc lỗi hay quá hạn: coi như chưa có khoá, dịch vụ báo thiếu token; kiểm tồn tại lỗi: dừng, không tạo khoá thay |
+| `sudo -u`, `sandbox-exec` | chạy dưới principal, cách ly | theo `tram/kiem/` | cổng đóng |
+| `launchctl` | cài/gỡ dịch vụ trạm chủ | 30 giây mỗi lệnh (`tram/chu/dich_vu_tram.py`); `cai-dat-tho` chưa đặt | dừng, lệnh sau không chạy, thoát 3 |
+| `brew`, `ollama pull` | cài memory | install 30 phút, services 60 giây, pull 60 phút (`tram/chu/cai_dat_nho.py`) | quá hạn: dừng kế hoạch, thoát 3; đối soát cây con ở cổng |
 
 ## Kiểm thử
 - **pytest** (`tests/`): mỗi test có `TRAM_HOME` tạm (`tests/conftest.py`); hệ ngoài thay bằng bản giả
@@ -65,4 +69,6 @@
 - **Frontend:** `frontend/tests/*.test.mjs` (logic), `frontend/kiem-an-toan.mjs` (quét nguồn),
   `frontend/kiem-dist.mjs` (quét bundle cho CSP).
 - **Kiểm tay giao diện:** `tests/chay_thu_giao_dien.py` chạy tram-api thật với dữ liệu giả, CSP thật.
-- Lệnh và cách chạy an toàn: `AGENT_RULES.md` §13.
+- Chạy cả bộ qua `tests/chan_host/chay.sh -q` (bộ chặn host); lệnh và cách chạy an toàn: `AGENT_RULES.md` §13.
+- Test canh giữ cấu trúc: `tests/test_vong_import.py` (vòng import cấp module), `tests/test_do_dai_ma.py` (file và
+  dòng của `tram/`: giới hạn và ngoại lệ ở `ENGINEERING_STANDARDS.md` mục Kiểu code).
````

`docs/ENGINEERING_STANDARDS.md` (sửa):

````diff
--- a/docs/ENGINEERING_STANDARDS.md
+++ b/docs/ENGINEERING_STANDARDS.md
@@ -2,7 +2,7 @@
 
 Project: `ben-station`
 Status: `ACTIVE`
-Cập nhật: `2026-10-17`
+Cập nhật: `2026-10-18`
 
 ## Mục đích và sở hữu
 Sở hữu: chuẩn viết code, nơi đặt giá trị (hardcode hay cấu hình), cách code giữ bí mật, quy tắc dữ liệu,
@@ -26,10 +26,9 @@
 - Phiên bản ghi **chính xác** (không `^`) cho phần lớn gói. Thêm gói phải hỏi trước (`AGENT_RULES.md` §11).
 
 ## Kiểu code
-- **File nhỏ, ~≤ 120 dòng.** Thực tế 17/10: 365 file Python trong `tram/`, 7 file ở mức 121–122 dòng, không file
-  nào quá 150; file Vue/JS lớn nhất 129 dòng (`frontend/src/trang/CongViec.vue`). Sắp vượt thì tách theo việc,
-  không nén chữ vào một dòng.
-- **Dòng ≤ 120 ký tự** (đếm ký tự Unicode). Hiện 20 trên 22.572 dòng của `tram/` vượt; không thêm dòng vượt mới.
+- **File ≤ 120 dòng, dòng ≤ 120 ký tự Unicode** trong `tram/` — `tests/test_do_dai_ma.py` cưỡng chế; không có
+  ngoại lệ file, ngoại lệ dòng gắn với nguyên văn dòng và ghi lý do trong test. File Vue/JS lớn nhất 129 dòng
+  (`frontend/src/trang/CongViec.vue`, chưa có test). Sắp vượt thì tách theo việc, không nén chữ vào một dòng.
 - **Tên tiếng Việt không dấu**, `snake_case` cho hàm/biến/module, `PascalCase` cho lớp, `HOA_CO_GACH` cho hằng
   (ví dụ `NHAN_QUET`, `KEYCHAIN_NHO`). Chú thích và thông báo cho người đọc viết tiếng Việt có dấu.
 - **TDD.** Viết test trước, chạy thấy đỏ đúng lý do, viết mã, chạy thấy xanh, rồi chạy cả bộ. Plan trong
@@ -47,11 +46,13 @@
 Chỉ phần cài đặt; ranh giới và hướng import ở `ARCHITECTURE.md` mục Luật module.
 - **Gọi lệnh ngoài luôn có hạn.** Lệnh chạy rồi chờ đi qua các khối trong `tram/kiem/` (`vong_doi.py`,
   `chay_gioi_han.py`, `lenh_ngan.py`): có hạn tuyệt đối, thu hồi cả cây con. Không `subprocess.run` không
-  `timeout` (suy từ plan P1, chưa xác nhận là luật chung).
+  `timeout` (suy từ plan P1, chưa xác nhận là luật chung). Spawn theo hợp đồng sở hữu (`tram/kiem/so_huu.py`): con
+  vào danh sách chủ trước mọi lối ra, người gọi thu hồi trong `finally`.
 - **Lệnh đổi máy thì liệt kê trước, chờ `dong-y`.** Mẫu `KeHoach` trong `tram/chu/cai_dat.py`: in file sẽ ghi,
   lệnh sẽ chạy, cảnh báo; chỉ thực hiện khi Đại ca gõ `dong-y`. Lệnh cài, gỡ, cấp mã mới đều theo mẫu này.
 - **Gỡ chỉ gỡ thứ mình đã tạo.** Cài máy thợ ghi sổ (`tram/chu/so_cai_tho.py`) trước và sau mỗi bước; gỡ
-  (`tram/chu/go_cai_dat_tho.py`) chỉ đụng mục sổ ghi đã tạo và còn đúng định danh (UID, sha256, inode).
+  (`tram/chu/go_cai_dat_tho.py`) chỉ đụng mục sổ ghi đã tạo và còn đúng định danh (UID, sha256, inode). Dịch vụ
+  trạm chủ: cài ghi biên nhận sha256 plist, gỡ chỉ theo biên nhận đó (`tram/chu/chung_cu_go.py`).
 - **Công tắc lớn mặc định tắt**; đọc cấu hình thiếu khoá thì rơi về giá trị an toàn (tắt, chỉ đọc).
 - **Đọc cấu hình chặt:** khoá lạ, sai kiểu, ngoài giới hạn thì báo lỗi, không đoán (`tram/cau_hinh/tram.py`).
 
@@ -82,8 +83,10 @@
 - Mọi phản hồi HTTP có CSP chặt và kiểm `Host`; API ghi luôn kiểm danh tính (`tram/api/bao_mat.py`). Test API ghi
   phải có ca **thiếu** và **giả** danh tính.
 - Memory lọc phạm vi bằng khớp chính xác, cấm lọc tiền tố; quét bí mật trước khi ghi (`tram/nho/bi_mat.py`).
-- Thư mục và file dữ liệu dưới `~/.tram` chỉ chủ sở hữu đọc được (Đại ca 17/10 coi quyền hiện tại là lỗi cần
-  sửa; mức quyền cụ thể suy từ code, chưa xác nhận).
+- Kho SQLite qua `mo_an_toan.py`: tạo với mode 600; siết file có quyền nhóm/người khác về 600 trước khi mở.
+  Bản sao qua `ban_sao.py`: file độc quyền 600, thư mục đích 700. `siet_quyen.py` chỉ sửa mục còn bit 0077;
+  giữ mục đã kín, bỏ qua `hang-doi/`, `sandbox/`, symlink, file hardlink và mục khác chủ. Không bảo đảm toàn cây
+  đúng 700/600 hay ACL đã sạch; `tram_home()` không ép quyền. Cách chạy: `DEPLOY.md` mục 3.
 
 ## Quy tắc dữ liệu
 Sở hữu dữ liệu và kho nào ai ghi: `PRODUCT_ARCHITECTURE.md`, `ARCHITECTURE.md` mục Hợp đồng chung.
@@ -92,7 +95,8 @@
 - Lược đồ DB: hiện trạng ở `ARCHITECTURE.md` mục Hợp đồng chung. Đổi lược đồ thuộc kill list.
 - Ghi file trạng thái nguyên tử: ghi file tạm cạnh đích rồi `os.replace` (ví dụ `tram/nho/bao_tri.py`).
 - Thời gian lưu dạng ISO; giờ bảo trì tính theo giờ Việt Nam (`GIO_VN` trong `tram/nho/bao_tri.py`).
-- Sao lưu dùng API online backup của SQLite (`tram/su_kien/sao_luu.py`), không chép file DB đang mở.
+- Sao lưu kho sự kiện dùng API online backup (`tram/su_kien/sao_luu.py`), không chép file DB đang mở; hạn chụp
+  kiểm giữa các bước backup (`ban_sao.py`), không bao trùm ghi/fsync. Không suy rộng sang sao lưu memory.
 
 ## Mã định danh
 | Thứ | Dạng | Ví dụ |
````

- [ ] **Step 2: Kiểm docs** — mọi đường dẫn mã nhắc tới tồn tại: `ls tests/chan_host/chay.sh tests/chan_host/chan_host.py tests/test_vong_import.py tests/test_do_dai_ma.py tram/keychain.py tram/llm/han_goi.py tram/su_kien/phien_ban.py tram/su_kien/ket_noi.py tram/su_kien/mo_an_toan.py tram/su_kien/thu_muc_an_toan.py tram/su_kien/ban_sao.py tram/su_kien/sao_luu.py tram/chu/dich_vu_tram.py tram/chu/go_dich_vu.py tram/chu/chung_cu_go.py tram/chu/khoi_phuc_su_kien.py tram/chu/siet_quyen.py tram/cau_hinh/bat_ghi.py tram/kiem/so_huu.py tram/kiem/ngat.py tram/kiem/bang_tien_trinh.py tram/kiem/giu_xac.py tram/kiem/gui_tin.py tram/tho/don_uid.py tram/tho/cham_tham_do.py tram/giao_viec/chung_cu_probe.py tram/giao_viec/ong_chep.py` (đo 18/10: đủ); `wc -l docs/AGENT_RULES.md docs/ARCHITECTURE.md` → 198, 79; không dòng docs nào > 300 ký tự (đo: dài nhất 283, `docs/MODULES.md` hàng `tram/chu/`).

- [ ] **Step 3: Commit** — `docs: bộ chặn host, cài/gỡ từng dịch vụ, khôi phục kho, siết quyền, số phiên bản kho, module mới, luật độ dài (lát V3b)`.

## Kết quả chạy thử (18/10/2026, worktree `plan/v3b-don-cuoi`, `main` `92430e0`)

- N₀: `tests/chan_host/chay.sh -q` → `3230 passed in 346.39s`; nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629.
- V3-18 RED thật (Step 2) → GREEN thật (Step 4); cả bộ sau V3-18: `3233 passed in 325.86s (0:05:25)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629 (= N₀ + 3 test mới).
- Áp lại toàn bộ khối mã (test + 29 bản vá + 6 file mới) và 5 bản vá docs của plan lên bản `git archive 92430e0` sạch bằng `patch -p1` + ghi file: `diff -r` với cây đã chạy test → khớp hoàn toàn (`tram/`, `tests/`, 5 file docs; bỏ qua `__pycache__`). Lệnh áp: trích khối `(mới)`/`(sửa)` từ chính file plan, `patch -p1 --forward`, 0 hunk lỗi.
- Đã hoàn nguyên mọi thay đổi ngoài file plan (`git checkout -- tram` + xoá file mới). Không bước OS nào được chạy.

## Đo trên OS thật

Không có. V3-18 không đổi hành vi; V3-19 chỉ mô tả mã — hành vi `launchctl`/quyền thật vẫn chứng minh ở cổng sổ tay (G1/G2/G3), docs không tuyên bố đã chạy thật.

## Câu hỏi cho Đại ca

1. **Duyệt sửa cơ học ở vùng kill list (cách ly, PR, cài/gỡ).** Chỉ dời nguyên văn hàm/lớp sang file bên cạnh và xuống dòng — không đổi lệnh, điều kiện hay thông báo; toàn bộ bộ test cũ xanh không sửa test nào. Em đề xuất: duyệt cho làm cùng V3-18. Nếu không duyệt: bỏ các file đó khỏi task thì test canh giữ sẽ đỏ, phải thêm ngoại lệ — trái luật "không ngoại lệ file", nên Em không khuyên.
2. **Hai dòng chữ dài hơn 120 ký tự trong văn bản mẫu và prompt gửi agent** (`du_an/khoi.py`, `giao_viec/goi.py`): giữ nguyên làm ngoại lệ (đề xuất — cắt thì chữ gửi cho agent đổi theo), hay cho phép sửa câu chữ ngắn lại ở một việc riêng?
3. **Cài máy thợ (`tram chu cai-dat-tho`) chưa đặt hạn cho từng lệnh** như cài/gỡ dịch vụ trạm chủ (30 giây). Docs mới ghi đúng là "chưa đặt". Em đề xuất tạo một bead nhỏ để thêm hạn trước cổng G3; không làm trong plan dọn này.

## Ghi chú triển khai — review Codex V3b vòng 1 (18/10/2026)

Mục này thắng các số đo và mô tả cũ ở phần thân. Reviewer chỉ đọc mã, không chạy code/test, không gọi mạng.
Các số `3233`, `116 passed`, thời gian chạy và tuyên bố áp bản vá sạch ở trên là báo cáo của tác giả cho bản
TRƯỚC review; không phải bằng chứng cho bản đã sửa. Sau review phải kiểm lại patch và chạy qua bộ chặn khi code.

### R1-01 — giữ đủ đường gọi công khai và kiểm tương thích

Đã sửa ngay các hunk V3-18: `go_cai_dat_tho.lenh_cli(args, *, hoi)` và `lenh_nghiem_thu.them(g)` đều còn,
qua hàm chuyển tiếp import trễ. Không áp ngoại lệ bỏ hai tên này ở Global Constraints nữa. Phần khai tham số
chỉ có một bản trong `lenh._them_nghiem_thu`; cả đường cũ và CLI dùng nó. Không gọi harness khi khai parser.
Không thêm vòng import lúc nạp: chiều ngược ở hai hàm chuyển tiếp chỉ chạy sau khi module đã nạp.

Số dòng suy từ hunk (chưa đo): `chu/go_cai_dat_tho.py` 99, `giao_viec/lenh_nghiem_thu.py` 117,
`giao_viec/lenh.py` 108; các file khác theo thân plan. Không thêm ngoại lệ file.

Thêm `tests/test_doi_cho_v3b.py` vào Files của V3-18. Viết file dưới đây CÙNG Step 1, trước sửa mã:

```python
"""Giữ đường import và cách khai CLI khi dời mã V3b; không chạy lệnh hệ thống."""
import argparse
from importlib import import_module


def test_ten_cu_la_cung_doi_tuong_o_noi_moi():
    cac_cap = [
        ("beads.bd", "beads.loi", ("LoiBd", "KhongThayBead")),
        ("ban_giao.schema", "ban_giao.mo_hinh", ("DoiChieu", "LenhKiem", "HuongDaBo")),
        ("cau_hinh.du_an", "cau_hinh.moi_truong_kiem", ("MoiTruongKiem",)),
        ("phieu.kho", "phieu.mo_hinh", ("LuotCu",)),
        ("su_kien.kho", "su_kien.mo_hinh", ("SuKien",)),
        ("nho.nhat_ky", "nho.mo_hinh", ("ThaoTacNho",)),
        ("giao_viec.ban_chep", "giao_viec.repo_ban_chep", ("ten_ban_chep",)),
        ("giao_viec.cong_that", "giao_viec.quan_sat_kiem", ("env_kin",)),
    ]
    for cu, moi, ten in cac_cap:
        a, b = import_module(f"tram.{cu}"), import_module(f"tram.{moi}")
        for t in ten:
            assert getattr(a, t) is getattr(b, t), (cu, moi, t)


def test_lenh_go_duong_cu_chuyen_dung_doi_so_va_ket_qua(monkeypatch):
    from tram.chu import go_cai_dat_tho, lenh_go_tho
    args, hoi, ket_qua = object(), object(), object()
    goi = []

    def gia(a, *, hoi):
        goi.append((a, hoi))
        return ket_qua

    monkeypatch.setattr(lenh_go_tho, "lenh_cli", gia)
    assert go_cai_dat_tho.lenh_cli(args, hoi=hoi) is ket_qua
    assert goi == [(args, hoi)]


def test_khai_nghiem_thu_cu_va_cli_giu_tham_so():
    from tram.giao_viec import lenh, lenh_nghiem_thu
    cu, cli = argparse.ArgumentParser(), argparse.ArgumentParser()
    lenh_nghiem_thu.them(cu.add_subparsers(required=True))
    lenh.them_lenh_giao(cli.add_subparsers(required=True))
    for p, dau in ((cu, []), (cli, ["giao"])):
        a = p.parse_args([*dau, "nghiem-thu-kiem"])
        assert (a.tai_sinh, a.cho, a.trong, a.dau_ino, a.cha) == (False, 300.0, False, None, None)
        assert a.ham is lenh_nghiem_thu.lenh_nghiem_thu
        a = p.parse_args([*dau, "nghiem-thu-kiem", "--tai-sinh", "--cho", "240",
                          "--trong", "--dau-ino", "12", "--cha", "34"])
        assert (a.tai_sinh, a.cho, a.trong, a.dau_ino, a.cha) == (True, 240.0, True, 12, 34)
        assert a.ham is lenh_nghiem_thu.lenh_nghiem_thu
```

Step 2 bổ sung chạy `tests/chan_host/chay.sh -q tests/test_doi_cho_v3b.py`.
Suy luận trên HEAD trước vá: hai test đầu đỏ vì module mới chưa tồn tại; test parser xanh (canh hành vi cũ).
Sau toàn bộ Step 3: ba test này phải xanh. Nếu chỉ áp bản trước review, test thứ hai đỏ vì mất `lenh_cli`
ở module cũ và test thứ ba đỏ vì mất `them`; không coi bộ cũ xanh là chứng minh giữ đủ đường import.
Test chuyển tiếp chỉ thay đúng đích gọi để kiểm đối số/kết quả; test parser dùng argparse thật, không mock.
Test hành vi hiện có của Beads, env, kho và CLI vẫn giữ nguyên, không thay bằng các test nối dây này.

Step 4 thêm file test mới vào lệnh tập trung: dự kiến **119** test (116 cũ + 3).
Cả bộ dự kiến **N₀ + 6 = 3236**, không phải 3233; chỉ chốt số thực tế sau khi chạy. Nhật ký chặn vẫn phải
0 dòng mới. G4 là bằng chứng không thấy hồi quy trong bộ test, không phải chứng minh mọi hành vi Python bất biến:
dời lớp đổi `__module__`, dời hàm đổi namespace tra global; re-export không bảo toàn mọi monkeypatch tùy ý.
Đã tìm ở `tram/`, `tests/`: không thấy caller phụ thuộc các global bị dời; không đổi đường monkeypatch đang dùng.

### R1-02 — docs phải phân biệt giới hạn thật với mục tiêu

Các bản vá V3-19 ở trên đã sửa: thời hạn Anthropic là hạn chờ, luồng còn sống vẫn chiếm chỗ; quyền toàn cây
không được bảo đảm bởi `siet-quyen`; hạn sao lưu chỉ kiểm giữa các bước backup, không bao trùm ghi/fsync;
kho rỗng không có bản trước nâng. Không thêm retry, cleanup hay cơ chế bảo mật mới vào mã trong lát dọn.
Quyền do ENGINEERING_STANDARDS sở hữu, MODULES và DEPLOY dẫn tới đó. MODULES ghi test canh giữ nhưng dẫn
luật độ dài/ngoại lệ về ENGINEERING_STANDARDS, không tự đặt luật thứ hai.

Khôi phục chỉ khởi động lại dịch vụ đã chạy trước bảo trì và được duyệt; không dùng lệnh gỡ cả năm dịch vụ như
một bước luôn chạy được (một biên nhận thiếu đã làm toàn kế hoạch bị từ chối). Giữ nguyên §11 cấm push thật.

Step 2 V3-19: ngoài kiểm đường dẫn, đọc đối chiếu các nhánh lỗi/quá hạn ở đúng file nguồn nêu trong Step 1;
kiểm link tương đối, đo lại trần dòng sau sửa. Các số 198/79/283 phía trên chỉ là số cũ, không nghiệm thu thay
cho cây sau review. Các hunk đổi số dòng đã cập nhật header; bảng timeout tập trung ở MODULES, DEPLOY dẫn tới đó.

### Cổng OS và điều kiện trước code

Không đo OS trong vòng review. Cổng sổ tay vẫn phải chứng minh mã vắng 113 và `path` của `launchctl print`,
quyền/ACL thực tế sau cài, giữ dữ liệu và chỉ khởi động lại đúng dịch vụ khi khôi phục; thu hồi UID, lịch và
Seatbelt vẫn ở G3/G4 cùng các cổng liên quan. Bộ test offline và việc dời mã không mở các cổng này.
Việc duyệt phần kill list và hai ngoại lệ dòng ở câu hỏi 1–2 vẫn là điều kiện trước khi coding agent bắt đầu.
