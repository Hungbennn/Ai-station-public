# bs-78r.10 — quota Codex rảnh phải chạy đúng principal — Implementation Plan (Q1, Q2)

> **Review đợt 7 (17/10/2026):** trạng thái vận hành hiện hành theo [phụ lục cổng](../handovers/2026-10-17-cong-sau-review-dot7.md) và [plan V2](../plans/2026-10-17-lat-v2-va-sau-review-dot7.md). Các chữ ĐẠT/count bên dưới giữ làm lịch sử tác giả; không vượt blockers review mới. Khi khác nhau về lệnh thử/cleanup hoặc readiness, phụ lục đợt 7 ưu tiên; quyết định D1–D53 giữ nguyên.


> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Trạng thái: **plan TDD đầy đủ, đã chạy thử trọn trên bản sao `main` `5da881e` sau P1/3C-B; CHƯA áp vào `main`; CHƯA nghiệm thu G5.** Liên quan dot6-Q02, không phải Q02 đợt 5 (home receipt).

**Goal:** Đường đọc hạn mức khe rảnh `VongKhe.nhip → doc_han_muc_ranh → hoi_app_server` chạy dưới principal CỦA KHE (wrapper, env, timeout, kill), thiếu principal thì không chạy; lỗi/treo của quota không làm hỏng nhịp tim, không lộ token.

**Architecture:** Không thêm `sudo` đơn lẻ: argv do `Principal.boc` dựng, kill qua `Principal.kill_nhom`, vòng đời qua primitive P1 (`tram/kiem/vong_doi.py`). Một module mới `tram/tho/han_muc_ranh.py` gom việc đọc hạn mức của vòng khe (principal của khe, xác minh UID thực lần đầu, chặn lỗi).

**Tech Stack:** Python 3.12 stdlib, pytest 8; app-server GIẢ `tests/du_lieu/codex/app_server_gia.py`.

**Spec / nguồn:** review Codex đợt 6 Q02; [D45–D47](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md); [kế hoạch tích hợp](../../tasks/plan.md) (Q1, Q2); **phụ thuộc** [plan lát P1 + 3C-B](2026-10-16-lat-p1-vong-doi-tien-trinh.md) Task 2–5, 7.

## P1 — primitive vòng đời process chung (đã tách thành plan riêng)

Phần P1 trước đây ở mục này nay là [plan lát P1](2026-10-16-lat-p1-vong-doi-tien-trinh.md) (Task 1–5), cùng 3C-B (Task 6–9). Nghiệm thu P1 giữ nguyên: timeout hữu hạn cho khởi tạo/đọc/kết thúc/kill/wait; parent wrapper và descendants đúng quyền đều được thu hồi hoặc báo không xác nhận cleanup; không `p.wait()` vô hạn, không kill rộng theo username; cancellation không để timer/thread mồ côi; không log secrets. Q1/Q2 dưới đây CHỈ dùng primitive đó, không sửa kill/wait.

## Global Constraints

- **N₀ (cho plan này) = 2311** — sau khi ghép P1 + 3C-B (Task 1–9). Q1-a có thể chạy cùng đợt 4 với P1 Task 5/7/8 (khác file); số tổng dưới đây theo thứ tự chạy thử T1…T9 → Q1-a → Q1-b → Q2: **+15 → 2326**. Gốc `main` `5da881e` = 2242.
- TDD, mã nguyên văn như plan P1; file ≤ ~120 dòng, dòng ≤ 120 ký tự Unicode (`tram/tho/vong_khe.py` 120, `tram/chay_cli/codex/app_server.py` 119, `tests/test_han_muc_principal.py` 118).
- Test không chạy `sudo`, app-server thật, Keychain, mạng; `hoi` là spy hoặc app-server GIẢ (python của user đang test) sau principal giả cùng user; `xac_minh_uid` bị thay bằng giả trong test vòng khe (UID thật đã có test riêng ở P1 Task 7 và chờ G3).
- Không credential mới, không đổi nguồn auth, không fallback chạy quota bằng tài khoản quản lý, không nới sandbox.

## Yêu cầu gốc (giữ nguyên văn từ bản 16/10, trước plan TDD)

### Q1 — đưa principal xuyên suốt đường quota

Files: `tram/tho/vong_khe.py`, `tram/tho/ngu_canh.py`, `tram/tho/principal_khe.py`, `tram/chay_cli/codex/bo.py`, `tram/chay_cli/codex/app_server.py`. Tách theo chữ ký và caller thành task nhỏ khi triển khai.

Phụ thuộc: hợp đồng P1. Nghiệm thu: `nhip → doc_han_muc_ranh → hoi_app_server` nhận đúng principal của khe, wrapper và env allowlist tương ứng. HOME/USER/CODEX_HOME không thừa hưởng danh tính quản lý; sandbox cũng theo khe. Principal thiếu/sai thì không spawn quota bằng manager. Không “sửa” bằng thêm sudo ở một chỗ rồi giữ `_giet` cũ.

Xác minh: user principal, sandbox principal, thiếu principal, hai khe khác nhau; assert argv/env/wrapper/ownership và không gọi process khi bị từ chối. Xem lại principal API khi `wt=None`, không nới profile để quota đọc thư mục khe khác.

### Q2 — timeout, heartbeat và lỗi

Phụ thuộc: P1 + Q1. Files: vòng khe và app-server tests, đường đóng process nếu thiếu.

Nghiệm thu: lỗi/quota không đọc được trả trạng thái không có dữ liệu theo contract, heartbeat vẫn tiếp diễn; không dùng quota manager thay thế, không coi thiếu quota là vô hạn. Mọi tiến trình đúng principal được kết thúc trong budget hoặc báo cleanup không xác nhận; không rò token vào logs/exception.

Xác minh: lỗi parse/process/timeout, token sentinel, heartbeat sau lỗi, identity/env không trộn giữa hai khe. Chạy integration đúng principal chỉ sau quyền vận hành và môi trường thử chuẩn bị riêng.

## Thiết kế đã chọn cho Q1/Q2 (sau P1)

- **Một đường duy nhất:** `VongKhe.nhip` → `DocHanMucRanh.doc` → `BoCLI.doc_han_muc_ranh(…, principal=)` →
  `app_server.doc_han_muc_ranh(…, principal=)` → `hoi_app_server(principal.boc([codex, "app-server"]), env=…,
  kill=principal.kill_nhom)` → `vong_doi.khoi_chay`/`thu_hoi` (P1). `principal` là tham số keyword BẮT BUỘC ở mọi
  tầng — quên truyền là `TypeError`, không có mặc định "chạy như quản lý".
- **Principal của khe:** `nc.principal(k, None, "han-muc")` → `principal_khe.principal_cua` (cơ chế `user`: `Principal`
  nguyên; `sandbox`: hồ sơ `~/.tram/sandbox/<máy>/<khe>/han-muc.sb`, `wt=None` nên chỉ mở hàng đợi + `CODEX_HOME` của
  chính khe, cấm thư mục khe khác). Không thêm `sudo` đơn lẻ: argv do `Principal.boc` dựng (`sudo -n -H -u … -- [sandbox-exec
  -f hồ sơ] codex app-server`), kill qua `Principal.kill_nhom` (P1 Task 3: `chay_ngan`, có hạn tuyệt đối).
- **Env:** dựng mới, không đọc env quản lý: `PATH` của CLI theo cấu hình thợ (`ch.chay.path_cli`, như lần chạy CLI),
  `LANG=C.UTF-8`, `CODEX_HOME` của khe. Không `HOME`/`USER`/`TMPDIR` (`sudo -H` đặt HOME của principal), không token.
- **Thiếu/sai principal:** `ChuaCoPrincipal` (ValueError) ở `nc.principal` → không spawn; `principal=None` ở
  `doc_han_muc_ranh` → None, không spawn. `tram tho kiem` (kiem_3b) đi cùng đường: khe thiếu principal → VÀNG
  "chưa đọc được … dưới principal của khe", không chạy dưới tài khoản quản lý.
- **UID thực:** nhịp đầu của khe CHỈ chạy `xac_minh_uid` (3C-B Task 7) cho principal của quota; nhịp sau mới hỏi
  app-server. Cấu hình nhầm `user:<tài khoản quản lý>` bị chặn bằng UID nhân ghi; `tram tho kiem` cũng xác minh trước.
- **Q2 nhịp tim:** đọc hạn mức chạy SAU khi gửi nhịp (`try/finally` quanh `_gui_nhip`), mọi lỗi (kể cả ghi sổ) bị chặn
  ở `DocHanMucRanh` với thông báo cố định (không in exception/argv/env). Mỗi nhịp tối đa một việc (dò UID hoặc hỏi
  app-server), cận trên xấu nhất 48 s → nhịp kế trễ tối đa ~78 s < `mat_ket_noi_giay` 90 s; `join` khi tắt chờ 90 s.
  `LoiThuHoi` (app-server hay cây dò UID không thu hồi được) → `doc` trả True → `VongKhe.hong` → vòng khe và nhịp DỪNG,
  như CLI không thu hồi được (P1 Task 5) — không nhận phiếu mới dưới principal có thể còn tiến trình rò.
- **Sentinel:** thông báo lỗi app-server cố định (P1 Task 4: chỉ mã số JSON-RPC); test đi trọn đường VongKhe với
  app-server giả ghi lại env thật nó nhận, chứng minh token của tài khoản quản lý không có trong env con, stdout/stderr
  của test, hay thân nhịp.
- Giữ dot6-Q01 (kiểm returncode — thuộc 3c T11, không đụng) và dot6-Q06 (không lộ argv/stderr của exception: P1 Task 4
  thông báo cố định; `chay_gioi_han` chỉ mang tên chương trình).

Còn ngoài phạm vi, ghi rủi ro: `do_cli("codex", …)` (`codex login status`) của `tram tho kiem` vẫn chạy dưới tài khoản
quản lý với `CODEX_HOME` của khe — cùng loại lỗi bs-78r.10 nhưng không nằm trên đường `nhip → doc_han_muc_ranh →
hoi_app_server`; đề nghị bead riêng, không mở rộng Q1 âm thầm.

## Bảng G — Q1/Q2

| # | Bảo đảm | Bằng chứng offline | Còn chờ OS (G5) |
|---|---|---|---|
| GQ1 | Argv quota = `Principal.boc([codex, "app-server"])` của đúng khe, cả `user:` và `sandbox:`; kill = `kill_nhom` của principal đó | `test_hai_khe_hai_co_che_dung_principal_env_kill_thieu_principal_khong_spawn` (qua `VongKhe.nhip`) | `sudo -n -H -u <khe>` thật chạy được `codex app-server` |
| GQ2 | Env dựng mới: PATH cấu hình thợ, `LANG=C.UTF-8`, `CODEX_HOME` của khe; không HOME/USER/TMPDIR/TRAM_*/token của quản lý | test trên + `test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu` + `test_sentinel_token_khong_lo_qua_env_log_hay_nhip` (env THẬT app-server giả nhận) | app-server đọc đúng `CODEX_HOME`, không dùng auth của quản lý |
| GQ3 | Thiếu principal → không spawn (vòng khe và `tram tho kiem`); `principal` là keyword bắt buộc mọi tầng | `…thieu_principal_khong_spawn`, `test_thieu_principal_khong_spawn_nhip_van_gui`, `test_kiem_3b_mac_dinh_khe_thieu_principal_khong_spawn` | — |
| GQ4 | UID thực của principal kiểm lần đọc đầu; sai → không hỏi quota | `test_uid_principal_chua_chung_minh_khong_hoi_quota` | UID thật dưới sudo (P1 G6) |
| GQ5 | Hồ sơ sandbox `wt=None` cấm thư mục cấu hình/hàng đợi khe khác, không nới | assert trong test hai khe | sandbox-exec thật cho phép app-server chạy |
| GQ6 | Quota lỗi/treo/ghi sổ lỗi không làm chết hay trễ quá hạn nhịp; nhịp gửi TRƯỚC quota | `test_quota_loi_nhip_van_gui_va_sau_khi_gui[*]`, `test_app_server_treo_co_han_nhip_ke_tiep_van_gui`, `test_ghi_so_han_muc_loi_khong_lam_chet_nhip` | thời gian thật một lần đọc |
| GQ7 | Không xác nhận thu hồi app-server → dừng khe (như CLI) | `test_khong_thu_hoi_duoc_thi_dung_khe_khong_doc_lai` | — |
| GQ8 | Không lộ token: env con, stdout/stderr, thân nhịp, thông báo lỗi (Q06) | `test_sentinel_token_khong_lo_qua_env_log_hay_nhip`, `test_loi_khong_chep_chu_cua_app_server` (P1 T4) | log launchd thật |

## File Structure (Q)

```
tram/chay_cli/codex/app_server.py  (sửa, Q1-a)  doc_han_muc_ranh(…, principal, path) — argv/env/kill theo principal
tram/chay_cli/codex/bo.py          (sửa, Q1-a)  BoCodex(hoi=…), doc_han_muc_ranh(…, principal, path)
tram/chay_cli/bo_cli.py            (sửa, Q1-a)  Protocol + BoClaude cùng chữ ký
tram/tho/kiem_3b.py                (sửa, Q1-a)  `tram tho kiem` đọc hạn mức dưới principal của khe
tram/tho/han_muc_ranh.py           (mới, Q1-b; Q2 sửa)  DocHanMucRanh — principal của khe, xác minh UID, chặn lỗi
tram/tho/vong_khe.py               (sửa, Q1-b; Q2)  dùng DocHanMucRanh; Q2: đọc sau khi gửi nhịp, hong khi LoiThuHoi
tests/test_han_muc_principal.py    (mới, Q1-a; Q1-b thêm) · tests/test_nhip_han_muc.py (mới, Q2)
tests/test_codex_app_server.py, test_bo_codex.py, test_kiem_3b.py (sửa, Q1-a) · du_lieu/codex/app_server_gia.py (Q2)
```

## Tasks

### Task Q1-a: `principal` bắt buộc qua `doc_han_muc_ranh`, `BoCLI`, `tram tho kiem`

**Đợt:** 4 (song song P1 Task 5, 3C-B Task 7, 8) · **Phải sau:** P1 Task 2–4. `principal` là keyword bắt buộc; argv do `principal.boc` dựng; env dựng mới: `PATH` của CLI theo cấu hình thợ (`ch.chay.path_cli`, không lấy env quản lý), `LANG=C.UTF-8`, `CODEX_HOME` của khe; kill qua `principal.kill_nhom`; `principal=None` → None, không spawn. `kiem_3b` dựng principal của khe (`wt=None`) và `xac_minh_uid` trước khi hỏi; thiếu principal/UID chưa chứng minh/dữ liệu hỏng → VÀNG, `LoiThuHoi` → ĐỎ. Đổi 3 test cũ cho đúng chữ ký mới.

**Files:**
- Modify: `tests/test_bo_codex.py`
- Modify: `tests/test_codex_app_server.py`
- Create: `tests/test_han_muc_principal.py`
- Modify: `tests/test_kiem_3b.py`
- Modify: `tram/chay_cli/bo_cli.py`
- Modify: `tram/chay_cli/codex/app_server.py`
- Modify: `tram/chay_cli/codex/bo.py`
- Modify: `tram/tho/kiem_3b.py`

**Interfaces:**
- Consumes: P1 `hoi_app_server(..., kill=)`, `LoiThuHoi`; `principal_khe.principal_cua`.
- Produces: `doc_han_muc_ranh(khe_id, thu_muc, *, bay_gio, principal, path, codex='codex', hoi=hoi_app_server)`; `BoCodex(*, codex, chay, hoi=hoi_app_server)`, `BoCodex.doc_han_muc_ranh(..., *, bay_gio, principal, path)`; `BoClaude.doc_han_muc_ranh(..., *, bay_gio, principal, path)`; `bo_sung_3b(..., principal_cua_=_principal)`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bo_codex.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_bo_codex.py b/tests/test_bo_codex.py
index 9961788..3f51cfb 100644
--- a/tests/test_bo_codex.py
+++ b/tests/test_bo_codex.py
@@ -39,7 +39,8 @@ def test_dang_ky_vao_bo_cli_cua_vong_tho(tmp_path, monkeypatch):
     assert bo.chu_ky_han_muc_ranh_giay == 300
     assert isinstance(bo.tao_chay(), ChayCLI) and isinstance(bo.tao_nguon(), NguonHanMuc)
     khong = BoCodex(codex=str(tmp_path / "khong-co-codex"))
-    assert khong.doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=datetime.now(timezone.utc)) is None
+    assert khong.doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=datetime.now(timezone.utc), principal=None,
+                                  path="/usr/bin") is None
     from dataclasses import replace
     from types import SimpleNamespace
     import threading
```

`tests/test_codex_app_server.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_codex_app_server.py b/tests/test_codex_app_server.py
index 86e2e8d..0ba2ec2 100644
--- a/tests/test_codex_app_server.py
+++ b/tests/test_codex_app_server.py
@@ -40,21 +40,36 @@ def test_treo_thi_het_gio_va_giet(tmp_path):
     assert time.monotonic() - t0 < 10
 
 
+class _PGia:
+    """Principal giả: chỉ dựng tiền tố như sudo — `hoi` là spy nên không có gì được chạy."""
+    user = "tram-k-c-codex-1"
+
+    def boc(self, argv):
+        return ["/usr/bin/sudo", "-n", "-H", "-u", self.user, "--", *argv]
+
+    def kill_nhom(self, pgid, sig):
+        pass
+
+
 def test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu(tmp_path, monkeypatch):
     monkeypatch.setenv("TRAM_TOKEN_BAT_KY", "bi-mat")
-    goi = []
+    monkeypatch.setenv("HOME", "/Users/quan-ly")
+    goi, pr = [], _PGia()
     mau = json.loads((GIA.parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))["plus"]
-    hm = doc_han_muc_ranh("C/codex-1", tmp_path / "khe", bay_gio=LUC,
-                          hoi=lambda argv, env: goi.append((argv, env)) or mau)
+    hm = doc_han_muc_ranh("C/codex-1", tmp_path / "khe", bay_gio=LUC, principal=pr, path="/opt/cli/bin",
+                          hoi=lambda argv, env, kill: goi.append((argv, env, kill)) or mau)
     assert hm.nguon == "app-server" and {c.loai for c in hm.cua_so} == {"5h", "tuan"}
-    argv, env = goi[0]
-    assert argv == ["codex", "app-server"] and env["CODEX_HOME"] == str(tmp_path / "khe")
-    assert not any(k.startswith("TRAM_") for k in env)
+    argv, env, kill = goi[0]
+    assert argv == pr.boc(["codex", "app-server"]) and kill == pr.kill_nhom
+    assert env == {"PATH": "/opt/cli/bin", "LANG": "C.UTF-8", "CODEX_HOME": str(tmp_path / "khe")}
 
-    def hong(argv, env):
+    def hong(argv, env, kill):
         raise LoiAppServer("x")
-    assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=hong) is None
-    assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=lambda a, env: {}) is None
+    kw = {"bay_gio": LUC, "path": "/opt/cli/bin"}
+    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=pr, hoi=hong, **kw) is None
+    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=pr, hoi=lambda a, env, kill: {}, **kw) is None
+    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=None, hoi=lambda *a, **k: goi.append("KHONG"),
+                            **kw) is None and len(goi) == 1
 
 
 def test_treo_thu_hoi_qua_kill_nguoi_goi_khong_de_luong_nen(tmp_path):
```

`tests/test_han_muc_principal.py` (mới):

```python
"""bs-78r.10 (dot6-Q02) — Q1: quota khe rảnh đi `DocHanMucRanh → BoCodex.doc_han_muc_ranh → hoi_app_server` dưới
principal CỦA KHE. `hoi` là spy: không sudo/app-server thật nào được chạy; argv dựng bằng `Principal.boc` thật."""
from datetime import datetime, timezone
from types import SimpleNamespace

from tram.chay_cli.codex.app_server import doc_han_muc_ranh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_may import DauDo
from tram.tho.ngu_canh import NguCanhTho

def _nc(tmp_path):
    k = [KheCauHinh("codex-1", "codex", "user:tram-k-c-codex-1", tmp_path / "cfg1", "Codex 1", ("coder",)),
         KheCauHinh("codex-2", "codex", "sandbox:tram-exec", tmp_path / "cfg2", "Codex 2", ("coder",)),
         KheCauHinh("codex-3", "codex", None, tmp_path / "cfg3", "Codex 3", ("coder",))]
    ch = CauHinhTho("C", "http://127.0.0.1:7700", tuple(k))
    khach = SimpleNamespace(goi=lambda m, u, than: (200, {"tiep_tuc": True, "phieu": None}))
    return NguCanhTho(ch, khach, goc=tmp_path / "tho-home", goc_wt=tmp_path / "wt"), k


def test_kiem_3b_dung_principal_khe_va_bao_do_khi_khong_thu_hoi(tmp_path):
    nc, k = _nc(tmp_path)
    dd = DauDo(ping=lambda: {}, du_an=lambda: [], which=lambda c: None, con_trong=lambda p: 1,
               chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout="", stderr=""), thu_muc_kho=tmp_path)
    goi = []

    def doc(kid, thu_muc, *, bay_gio, principal, path, codex):
        goi.append((kid, principal))
        if kid.endswith("codex-2"):
            raise LoiThuHoi("x")
        return None
    ds = {m.muc: m.muc_do for m in bo_sung_3b(nc.ch, dd, [], doc_han_muc=doc, bay_gio=datetime.now(timezone.utc),
                                              principal_cua_=lambda ch, x: None if x.principal is None else x.ten)}
    assert goi == [("C/codex-1", "codex-1"), ("C/codex-2", "codex-2"), ("C/codex-3", None)]
    assert [ds[f"C/codex-{i} hạn mức"] for i in (1, 2, 3)] == ["vang", "do", "vang"]


def test_kiem_3b_mac_dinh_khe_thieu_principal_khong_spawn(tmp_path):
    nc, k = _nc(tmp_path)
    goi = []

    def doc(kid, thu_muc, **kw):
        return doc_han_muc_ranh(kid, thu_muc, hoi=lambda *a, **x: goi.append(a), **kw)
    dd = DauDo(ping=lambda: {}, du_an=lambda: [], which=lambda c: None, con_trong=lambda p: 1,
               chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout="", stderr=""), thu_muc_kho=tmp_path)
    ds = {m.muc: m for m in bo_sung_3b(CauHinhTho("C", "http://127.0.0.1:7700", (k[2],)), dd, [], doc_han_muc=doc)}
    assert goi == [] and ds["C/codex-3 hạn mức"].muc_do == "vang" and "principal" in ds["C/codex-3 hạn mức"].chi_tiet
```

`tests/test_kiem_3b.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_kiem_3b.py b/tests/test_kiem_3b.py
index bffd684..69155fe 100644
--- a/tests/test_kiem_3b.py
+++ b/tests/test_kiem_3b.py
@@ -29,7 +29,7 @@ def _dd(tmp_path, *, dang_nhap=0, tags=(TAG_THO,), goc="/opt/bin"):
                  chay=chay, con_trong=lambda p: 50 * 1024 ** 3, thu_muc_kho=tmp_path / "kho")
 
 
-def _hm(kid, thu_muc, *, bay_gio, codex):
+def _hm(kid, thu_muc, *, bay_gio, principal, path, codex):
     return HanMuc(khe_id=kid, nguon="app-server", cua_so=[
         CuaSo(loai="5h", trang_thai="biet", phan_tram=62.0, doc_luc="2026-10-13T03:00:00Z")])
 
@@ -62,3 +62,14 @@ def test_kiem_may_goi_bo_sung_3b(tmp_path):
     m = _muc(kiem_may(_ch(tmp_path), _dd(tmp_path, goc=str(tmp_path / "khong-co"))))
     assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["tailscale tag"][0] == "xanh"
     assert m["C/codex-1 hạn mức"][0] == "vang"                      # không có `codex` thật → không đọc được
+
+
+def test_uid_principal_chua_chung_minh_thi_vang_khong_hoi(tmp_path, monkeypatch):
+    from dataclasses import replace
+    from tram.kiem.danh_tinh import LoiDanhTinh
+    ch = _ch(tmp_path)
+    ch = replace(ch, khe=(replace(ch.khe[0], principal="user:quan-ly"),))       # cấu hình nhầm: principal = quản lý
+    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))
+    goi = []
+    ds = bo_sung_3b(ch, _dd(tmp_path), [], doc_han_muc=lambda *a, **k: goi.append(k["principal"]), bay_gio=LUC)
+    assert goi == [None] and _muc(ds)["C/codex-1 hạn mức"][0] == "vang"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_codex_app_server.py tests/test_bo_codex.py tests/test_kiem_3b.py tests/test_han_muc_principal.py`

Kết quả THẬT trên bản sao (trích):

```text
E       TypeError: doc_han_muc_ranh() got an unexpected keyword argument 'principal'
E       TypeError: BoCodex.doc_han_muc_ranh() got an unexpected keyword argument 'principal'
E           TypeError: _hm() missing 2 required keyword-only arguments: 'principal' and 'path'
E           TypeError: _hm() missing 2 required keyword-only arguments: 'principal' and 'path'
E   KeyError: 'principal'
E       TypeError: bo_sung_3b() got an unexpected keyword argument 'principal_cua_'
E       AttributeError: 'NoneType' object has no attribute 'get'
FAILED tests/test_codex_app_server.py::test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu
FAILED tests/test_bo_codex.py::test_dang_ky_vao_bo_cli_cua_vong_tho - TypeErr...
FAILED tests/test_kiem_3b.py::test_khe_codex_thay_muc_dang_nhap_them_han_muc_va_tag
FAILED tests/test_kiem_3b.py::test_chua_dang_nhap_chua_doc_han_muc_chua_gan_tag
FAILED tests/test_kiem_3b.py::test_uid_principal_chua_chung_minh_thi_vang_khong_hoi
FAILED tests/test_han_muc_principal.py::test_kiem_3b_dung_principal_khe_va_bao_do_khi_khong_thu_hoi
FAILED tests/test_han_muc_principal.py::test_kiem_3b_mac_dinh_khe_thieu_principal_khong_spawn
7 failed, 11 passed in 6.61s
```

- [ ] **Step 3: Viết mã**

`tram/chay_cli/bo_cli.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/bo_cli.py b/tram/chay_cli/bo_cli.py
index ade48c7..0cc0d32 100644
--- a/tram/chay_cli/bo_cli.py
+++ b/tram/chay_cli/bo_cli.py
@@ -17,7 +17,7 @@ class BoCLI(Protocol):
              settings: Path | None = None, mcp: Path | None = None) -> list[str]: ...
     def tao_chay(self, boc, **kw): ...
     def tao_nguon(self, **kw): ...
-    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio): ...
+    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio, principal, path): ...
 
 
 class BoClaude:
@@ -34,7 +34,7 @@ class BoClaude:
     def tao_nguon(self, **kw):
         return NguonHanMucClaude(**kw)
 
-    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio):
+    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio, principal, path):
         return None
 
 
```

`tram/chay_cli/codex/app_server.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/codex/app_server.py b/tram/chay_cli/codex/app_server.py
index 9970057..128a27b 100644
--- a/tram/chay_cli/codex/app_server.py
+++ b/tram/chay_cli/codex/app_server.py
@@ -6,7 +6,10 @@ Giao thức theo tài liệu app-server (JSON-RPC qua stdio, mỗi dòng một J
 Timer/luồng nền), chụp cây mỗi giây trong lúc chờ, xong hay lỗi đều `thu_hoi` cả cây qua `kill` của người gọi; không xác
 nhận thu hồi → `LoiThuHoi`. Cận trên một lần hỏi: 10 s (+ ≤ 5 s một lần `ps` lố hạn) + `thu_hoi(1, 3, 2)` ≤ 1 + 3 +
 2 × (2 + 5) + 3 × 5 = 33 s → 48 s.
-Thông báo lỗi cố định: không chép argv, stderr hay chữ do app-server gửi về (dot6-Q06)."""
+Thông báo lỗi cố định: không chép argv, stderr hay chữ do app-server gửi về (dot6-Q06).
+bs-78r.10 (dot6-Q02): app-server chạy dưới PRINCIPAL CỦA KHE (`principal.boc`, `principal.kill_nhom`) với env dựng mới
+(PATH của CLI theo cấu hình thợ, LANG, CODEX_HOME) — không đọc env của tài khoản quản lý; không có principal → không
+spawn."""
 import json
 import os
 import select
@@ -23,7 +26,6 @@ PHUONG_THUC = "account/rateLimits/read"
 CHU_KY_RANH_GIAY = 300
 THOI_GIAN_CHO = 10.0
 DONG_TOI_DA = 1 << 20
-BIEN_GIU = ("PATH", "HOME", "LANG", "USER", "TMPDIR")
 
 
 class LoiAppServer(RuntimeError):
@@ -103,13 +105,15 @@ def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float
             raise LoiThuHoi("không xác nhận thu hồi tiến trình app-server")
 
 
-def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, codex: str = "codex",
-                     hoi=hoi_app_server) -> HanMuc | None:
-    """Số đo của khe, hoặc None khi không đọc được (vòng 3a-2 gửi nhịp không có số đo → cửa sổ chưa biết, #15)."""
-    env = {k: os.environ[k] for k in BIEN_GIU if k in os.environ}
-    env["CODEX_HOME"] = str(thu_muc_cau_hinh)
+def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, principal, path: str,
+                     codex: str = "codex", hoi=hoi_app_server) -> HanMuc | None:
+    """Số đo của khe, hoặc None khi không đọc được (vòng 3a-2 gửi nhịp không có số đo → cửa sổ chưa biết, #15).
+    `principal` None → None, KHÔNG chạy dưới tài khoản quản lý. `LoiThuHoi` để nổi lên: người gọi phải biết."""
+    if principal is None:
+        return None
+    env = {"PATH": path, "LANG": "C.UTF-8", "CODEX_HOME": str(thu_muc_cau_hinh)}
     try:
-        kq = hoi([codex, "app-server"], env=env)
-    except (LoiAppServer, OSError):
+        kq = hoi(principal.boc([codex, "app-server"]), env=env, kill=principal.kill_nhom)
+    except (LoiAppServer, OSError, ValueError):
         return None
     return han_muc_app_server(kq, khe_id=khe_id, bay_gio=bay_gio)
```

`tram/chay_cli/codex/bo.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/codex/bo.py b/tram/chay_cli/codex/bo.py
index ae116b7..ded1d36 100644
--- a/tram/chay_cli/codex/bo.py
+++ b/tram/chay_cli/codex/bo.py
@@ -10,7 +10,7 @@ import subprocess
 from datetime import datetime
 from pathlib import Path
 
-from tram.chay_cli.codex.app_server import CHU_KY_RANH_GIAY, doc_han_muc_ranh
+from tram.chay_cli.codex.app_server import CHU_KY_RANH_GIAY, doc_han_muc_ranh, hoi_app_server
 from tram.chay_cli.codex.chay import ChayCodex
 from tram.chay_cli.codex.han_muc import NguonHanMucCodex
 from tram.han_muc.mo_hinh import HanMuc
@@ -36,8 +36,8 @@ class BoCodex:
     bien_thu_muc = "CODEX_HOME"
     chu_ky_han_muc_ranh_giay = CHU_KY_RANH_GIAY
 
-    def __init__(self, *, codex: str = "codex", chay=subprocess.run):
-        self.codex, self.chay = codex, chay
+    def __init__(self, *, codex: str = "codex", chay=subprocess.run, hoi=hoi_app_server):
+        self.codex, self.chay, self.hoi = codex, chay, hoi
 
     def lenh(self, *, worktree: Path, thu_muc_phieu: Path, vai: str, lenh_cho_phep: list[str],
              settings: Path | None = None, mcp: Path | None = None) -> list[str]:
@@ -50,5 +50,7 @@ class BoCodex:
     def tao_nguon(self, **kw) -> NguonHanMucCodex:
         return NguonHanMucCodex()
 
-    def doc_han_muc_ranh(self, khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime) -> HanMuc | None:
-        return doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, bay_gio=bay_gio, codex=self.codex)
+    def doc_han_muc_ranh(self, khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, principal,
+                         path: str) -> HanMuc | None:
+        return doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, bay_gio=bay_gio, principal=principal, path=path,
+                                codex=self.codex, hoi=self.hoi)
```

`tram/tho/kiem_3b.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/kiem_3b.py b/tram/tho/kiem_3b.py
index 7e4eb39..e08c2f4 100644
--- a/tram/tho/kiem_3b.py
+++ b/tram/tho/kiem_3b.py
@@ -1,30 +1,60 @@
 """Mục `tram tho kiem` của lát 3b (spec 3 §9.2, §9.3, H7) — nối vào cuối `kiem_may` (3a-1):
 
 - Khe Codex: đăng nhập qua `codex login status` với `CODEX_HOME` của khe (thay mục "chờ S2" chung); hạn mức đọc một lần
-  qua `codex app-server` — không đọc được thì VÀNG (#15: vẫn nhận việc, cảnh báo), không đỏ.
+  qua `codex app-server` DƯỚI PRINCIPAL CỦA KHE (bs-78r.10), sau khi xác minh UID thực của principal — chưa có
+  principal, UID chưa chứng minh hay không đọc được thì VÀNG (#15: vẫn nhận việc, cảnh báo), không đỏ; không xác nhận
+  thu hồi tiến trình (dò UID hay app-server) → ĐỎ.
 - Máy từ xa (`tram_api` là https): Mac thợ phải gắn tag Tailscale (#3) — chỉ kiểm, không đổi.
 Mục cách ly, quyền ghi worktree của principal giữ nguyên như 3a-1/3a-2 (S6)."""
 from datetime import datetime, timezone
+from pathlib import Path
 
 from tram.chay_cli.codex.app_server import doc_han_muc_ranh
-from tram.tho.cau_hinh import CauHinhTho
+from tram.duong_dan import tram_home
+from tram.kiem import danh_tinh
+from tram.kiem.vong_doi import LoiThuHoi
+from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.do_may import do_cli, kiem_tag
 from tram.tho.kiem_may import DauDo, MucKiem
+from tram.tho.principal_khe import principal_cua
+
+
+def _principal(ch: CauHinhTho, k: KheCauHinh):
+    try:
+        pr = principal_cua(ch, k, goc=tram_home(), goc_wt=Path.home() / "tram" / "worktrees", wt=None,
+                           ten="han-muc-kiem")
+        danh_tinh.xac_minh_uid(pr.user, pr.boc, pr.kill_nhom)
+        return pr
+    except (ValueError, OSError, danh_tinh.LoiDanhTinh):  # ChuaCoPrincipal là ValueError; LoiThuHoi để nổi lên
+        return None
+
+
+def _han_muc(kid: str, hm, loi: bool) -> MucKiem:
+    if loi:
+        return MucKiem(f"{kid} hạn mức", "do", "không xác nhận thu hồi tiến trình đọc hạn mức — kiểm principal")
+    if hm:
+        return MucKiem(f"{kid} hạn mức", "xanh", ", ".join(f"{c.loai} {c.phan_tram:g}%" for c in hm.cua_so))
+    return MucKiem(f"{kid} hạn mức", "vang", "chưa đọc được qua `codex app-server` dưới principal của khe (chờ S5/S6) "
+                   "— vẫn nhận việc, cảnh báo vàng (#15)")
 
 
 def bo_sung_3b(ch: CauHinhTho, dd: DauDo, ra: list[MucKiem], *, doc_han_muc=doc_han_muc_ranh,
-               bay_gio: datetime | None = None) -> list[MucKiem]:
+               bay_gio: datetime | None = None, principal_cua_=_principal) -> list[MucKiem]:
     ra = list(ra)
     for k in (k for k in ch.khe if k.cli == "codex"):
         kid = ch.khe_id(k)
         d = do_cli("codex", k.thu_muc_cau_hinh, which=dd.which, chay=dd.chay)
         muc = MucKiem(f"{kid} đăng nhập", "xanh" if d.dang_nhap else "do", d.chi_tiet)
         ra = [muc if m.muc == muc.muc else m for m in ra] if any(m.muc == muc.muc for m in ra) else [*ra, muc]
-        hm = doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
-                         codex=d.duong_dan or "codex")
-        ra.append(MucKiem(f"{kid} hạn mức", "xanh", ", ".join(f"{c.loai} {c.phan_tram:g}%" for c in hm.cua_so))
-                  if hm else MucKiem(f"{kid} hạn mức", "vang", "chưa đọc được qua `codex app-server` (chờ spike S5) "
-                                     "— vẫn nhận việc, cảnh báo vàng (#15)"))
+        hm, loi = None, False
+        try:
+            hm = doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
+                             principal=principal_cua_(ch, k), path=ch.chay.path_cli, codex=d.duong_dan or "codex")
+        except LoiThuHoi:
+            loi = True
+        except Exception:                                # noqa: BLE001 — dữ liệu app-server hỏng: vàng, không sập lệnh
+            pass
+        ra.append(_han_muc(kid, hm, loi))
     if ch.tram_api.startswith("https://"):
         co, chi_tiet = kiem_tag(which=dd.which, chay=dd.chay)
         ra.append(MucKiem("tailscale tag", "xanh" if co else "do", chi_tiet))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_codex_app_server.py tests/test_bo_codex.py tests/test_kiem_3b.py tests/test_han_muc_principal.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2314 tests collected in 3.23s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_bo_codex.py tests/test_codex_app_server.py tests/test_han_muc_principal.py tests/test_kiem_3b.py tram/chay_cli/bo_cli.py tram/chay_cli/codex/app_server.py tram/chay_cli/codex/bo.py tram/tho/kiem_3b.py
git commit -m "fix(codex): quota khe rảnh bắt buộc chạy dưới principal của khe (bs-78r.10)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task Q1-b: Vòng khe đọc hạn mức qua principal của CHÍNH khe

**Đợt:** 5 (song song 3C-B Task 9) · **Phải sau:** Q1-a, P1 Task 5, 3C-B Task 7. `DocHanMucRanh` lấy `nc.principal(k, None, "han-muc")`; thiếu principal không spawn; nhịp đầu CHỈ `danh_tinh.xac_minh_uid(pr.user, pr.boc, pr.kill_nhom)` (chặn `user:<quản lý>` cấu hình nhầm; sai → khoá đọc hạn mức của khe), nhịp kế mới hỏi app-server — mỗi nhịp tối đa một việc có cận 48 s. Test đi đúng đường `VongKhe.nhip` cho ba khe: `user:`, `sandbox:` và thiếu principal; hồ sơ sandbox cấm thư mục cấu hình khe khác.

**Files:**
- Modify: `tests/test_han_muc_principal.py`
- Create: `tram/tho/han_muc_ranh.py`
- Modify: `tram/tho/vong_khe.py`

**Interfaces:**
- Consumes: Q1-a; 3C-B `danh_tinh.xac_minh_uid`, `LoiDanhTinh`.
- Produces: `tram/tho/han_muc_ranh.DocHanMucRanh(nc, k, khe_id, so)` + `.doc(ranh)`, `.khoa`, `.da_xac_minh`; `VongKhe.han_muc`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_han_muc_principal.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_han_muc_principal.py b/tests/test_han_muc_principal.py
index 0f0b2a3..e77a778 100644
--- a/tests/test_han_muc_principal.py
+++ b/tests/test_han_muc_principal.py
@@ -1,14 +1,24 @@
 """bs-78r.10 (dot6-Q02) — Q1: quota khe rảnh đi `DocHanMucRanh → BoCodex.doc_han_muc_ranh → hoi_app_server` dưới
 principal CỦA KHE. `hoi` là spy: không sudo/app-server thật nào được chạy; argv dựng bằng `Principal.boc` thật."""
+import json
 from datetime import datetime, timezone
+from pathlib import Path
 from types import SimpleNamespace
 
+from tram.chay_cli.bo_cli import BO_CLI
 from tram.chay_cli.codex.app_server import doc_han_muc_ranh
+from tram.chay_cli.codex.bo import BoCodex
 from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.kiem_3b import bo_sung_3b
 from tram.tho.kiem_may import DauDo
 from tram.tho.ngu_canh import NguCanhTho
+from tram.tho.principal import BIEN_GIU, SANDBOX_EXEC, SUDO
+from tram.tho.so_khe import SoKhe
+from tram.tho.vong_khe import VongKhe
+
+MAU = json.loads((Path(__file__).parent / "du_lieu" / "codex" / "app_server_rate_limits.json").read_text())["plus"]
+
 
 def _nc(tmp_path):
     k = [KheCauHinh("codex-1", "codex", "user:tram-k-c-codex-1", tmp_path / "cfg1", "Codex 1", ("coder",)),
@@ -19,6 +29,37 @@ def _nc(tmp_path):
     return NguCanhTho(ch, khach, goc=tmp_path / "tho-home", goc_wt=tmp_path / "wt"), k
 
 
+def test_hai_khe_hai_co_che_dung_principal_env_kill_thieu_principal_khong_spawn(tmp_path, monkeypatch):
+    goi, xm = [], []
+    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda argv, *, env, kill: goi.append((argv, env, kill)) or MAU))
+    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda ten, boc, kill: xm.append((ten, boc([]))) or 600)
+    for bien, gia_tri in (("HOME", "/Users/quan-ly"), ("USER", "quan-ly"), ("TMPDIR", "/var/folders/ql"),
+                          ("TRAM_THO_TOKEN", "BI-MAT-MAY")):
+        monkeypatch.setenv(bien, gia_tri)
+    nc, k = _nc(tmp_path)
+    for x in k:                                                            # đúng đường VongKhe.nhip của từng khe
+        vk = VongKhe(nc, x)
+        vk.hop = SimpleNamespace(gui=lambda _: None)
+        vk.nhip()                                                          # nhịp 1: chỉ xác minh UID
+        vk.nhip()                                                          # nhịp 2: hỏi app-server
+    assert len(goi) == 2                                                   # codex-3 thiếu principal: không spawn
+    (a1, e1, kill1), (a2, e2, kill2) = goi
+    assert a1 == [SUDO, "-n", "-H", "-u", "tram-k-c-codex-1", f"--preserve-env={','.join(BIEN_GIU)}", "--", "codex",
+                  "app-server"]
+    ho_so = nc.goc / "sandbox" / "C" / "codex-2" / "han-muc.sb"
+    assert a2[:5] == [SUDO, "-n", "-H", "-u", "tram-exec"] and a2[-5:] == [SANDBOX_EXEC, "-f", str(ho_so), "codex",
+                                                                            "app-server"]
+    assert (e1["CODEX_HOME"], e2["CODEX_HOME"]) == (str(k[0].thu_muc_cau_hinh), str(k[1].thu_muc_cau_hinh))
+    assert all(set(e) == {"PATH", "LANG", "CODEX_HOME"} and e["PATH"] == nc.ch.chay.path_cli for e in (e1, e2))
+    assert [x[0] for x in xm] == ["tram-k-c-codex-1", "tram-exec"] and xm[1][1][-3:] == [SANDBOX_EXEC, "-f", str(ho_so)]
+    assert (kill1.__self__.user, kill2.__self__.user) == ("tram-k-c-codex-1", "tram-exec")
+    hs = ho_so.read_text()
+    for khac in (k[0], k[2]):                                              # wt=None không nới sang khe khác
+        assert f'(deny file-read* file-write* (subpath "{khac.thu_muc_cau_hinh}"))' in hs
+    assert f'(allow file-read* file-write* (subpath "{k[1].thu_muc_cau_hinh}"))' in hs
+    assert [SoKhe("C", x.ten, nc.goc).doc_han_muc() is not None for x in k] == [True, True, False]
+
+
 def test_kiem_3b_dung_principal_khe_va_bao_do_khi_khong_thu_hoi(tmp_path):
     nc, k = _nc(tmp_path)
     dd = DauDo(ping=lambda: {}, du_an=lambda: [], which=lambda c: None, con_trong=lambda p: 1,
@@ -46,3 +87,17 @@ def test_kiem_3b_mac_dinh_khe_thieu_principal_khong_spawn(tmp_path):
                chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout="", stderr=""), thu_muc_kho=tmp_path)
     ds = {m.muc: m for m in bo_sung_3b(CauHinhTho("C", "http://127.0.0.1:7700", (k[2],)), dd, [], doc_han_muc=doc)}
     assert goi == [] and ds["C/codex-3 hạn mức"].muc_do == "vang" and "principal" in ds["C/codex-3 hạn mức"].chi_tiet
+
+
+def test_uid_principal_chua_chung_minh_khong_hoi_quota(tmp_path, monkeypatch, capsys):
+    from tram.kiem.danh_tinh import LoiDanhTinh
+    goi = []
+    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: goi.append(a) or MAU))
+    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))
+    nc, k = _nc(tmp_path)
+    vk = VongKhe(nc, k[0])
+    vk.hop = SimpleNamespace(gui=lambda _: None)
+    vk.nhip()
+    vk.han_muc.lan_sau = 0.0
+    vk.nhip()
+    assert goi == [] and vk.han_muc.khoa and not vk.hong and "chưa chứng minh được UID" in capsys.readouterr().out
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_han_muc_principal.py`

Kết quả THẬT trên bản sao (trích):

```text
E           TypeError: BoCodex.doc_han_muc_ranh() missing 2 required keyword-only arguments: 'principal' and 'path'
E           TypeError: BoCodex.doc_han_muc_ranh() missing 2 required keyword-only arguments: 'principal' and 'path'
FAILED tests/test_han_muc_principal.py::test_hai_khe_hai_co_che_dung_principal_env_kill_thieu_principal_khong_spawn
FAILED tests/test_han_muc_principal.py::test_uid_principal_chua_chung_minh_khong_hoi_quota
2 failed, 2 passed in 0.19s
```

- [ ] **Step 3: Viết mã**

`tram/tho/han_muc_ranh.py` (mới):

```python
"""Đọc hạn mức lúc khe RẢNH cho vòng nhịp tim (spec 3 §8.1; bs-78r.10 = dot6-Q02). Principal lấy từ ngữ cảnh của
CHÍNH khe (`nc.principal(k, None, …)` — hồ sơ sandbox với `wt=None` không mở thêm thư mục khe khác); thiếu principal
(`ChuaCoPrincipal`, một `ValueError`) → không spawn gì. Lần đọc đầu xác minh UID THỰC của principal (3C-B
`xac_minh_uid` — `user:<quản lý>` cấu hình nhầm bị chặn); sai → thôi đọc hạn mức của khe."""
import time

from tram.chay_cli.bo_cli import BO_CLI
from tram.kiem import danh_tinh


class DocHanMucRanh:
    def __init__(self, nc, k, khe_id: str, so):
        self.nc, self.k, self.khe_id, self.so = nc, k, khe_id, so
        self.lan_sau = 0.0
        self.khoa = self.da_xac_minh = False

    def _doc(self):
        pr = self.nc.principal(self.k, None, "han-muc")
        if not self.da_xac_minh:
            danh_tinh.xac_minh_uid(pr.user, pr.boc, pr.kill_nhom)
            self.da_xac_minh, self.lan_sau = True, 0.0           # hỏi app-server ở nhịp kế tiếp
            return
        hm = BO_CLI[self.k.cli].doc_han_muc_ranh(self.khe_id, self.k.thu_muc_cau_hinh, bay_gio=self.nc.dong_ho(),
                                                 principal=pr, path=self.nc.ch.chay.path_cli)
        if hm is not None:
            self.so.luu_han_muc(hm)

    def doc(self, ranh: bool) -> None:
        chu_ky = BO_CLI[self.k.cli].chu_ky_han_muc_ranh_giay
        if self.khoa or not ranh or chu_ky is None or time.monotonic() < self.lan_sau:
            return
        self.lan_sau = time.monotonic() + chu_ky
        try:
            self._doc()
        except danh_tinh.LoiDanhTinh:
            self.khoa = True
            print(f"{self.khe_id}: chưa chứng minh được UID của principal — không đọc hạn mức dưới principal này")
        except ValueError:                  # ChuaCoPrincipal: khe chưa có principal → không đọc, không spawn
            pass
```

`tram/tho/vong_khe.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/vong_khe.py b/tram/tho/vong_khe.py
index 6d17dd0..207a36a 100644
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -5,11 +5,11 @@ lại `phieu.json`) được chạy tiếp từ lần kế — trạm không tra
 import threading
 import time
 
-from tram.chay_cli.bo_cli import BO_CLI
 from tram.duong_dan import doc_luc
 from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.cau_hinh import KheCauHinh
+from tram.tho.han_muc_ranh import DocHanMucRanh
 from tram.tho.hop_thu import HopThu
 from tram.tho.khach import LoiKhachTram
 from tram.tho.mo_coi_khe import don_mo_coi_khe
@@ -31,8 +31,8 @@ class VongKhe:
         self.phieu_moi: TrangThaiPhieu | None = None
         self.da_xac_nhan = False
         self.han_giu = None
-        self.han_muc_doc_lai = 0.0
         self.hong = False                       # P1: CLI chưa xác nhận thu hồi → dừng khe (cả nhịp tim)
+        self.han_muc = DocHanMucRanh(nc, k, self.khe_id, self.so)
 
     def khoi_dong(self) -> None:
         tt = don_mo_coi_khe(self.nc, self.k, self.so, self.hop)
@@ -40,13 +40,7 @@ class VongKhe:
         self.phieu_moi = tt
 
     def nhip(self) -> dict | None:
-        bo = BO_CLI[self.k.cli]
-        if self.pc is None and self.phieu_moi is None and bo.chu_ky_han_muc_ranh_giay is not None \
-                and time.monotonic() >= self.han_muc_doc_lai:
-            self.han_muc_doc_lai = time.monotonic() + bo.chu_ky_han_muc_ranh_giay
-            hm = bo.doc_han_muc_ranh(self.khe_id, self.k.thu_muc_cau_hinh, bay_gio=self.nc.dong_ho())
-            if hm is not None:
-                self.so.luu_han_muc(hm)
+        self.han_muc.doc(self.pc is None and self.phieu_moi is None)
         than = {"khe_id": self.khe_id, "buoc_tho": self.buoc}
         p = self.pc.p if self.pc else (Phieu.model_validate(self.phieu_moi.phieu) if self.phieu_moi else None)
         if p is not None:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_han_muc_principal.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2316 tests collected in 3.26s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_han_muc_principal.py tram/tho/han_muc_ranh.py tram/tho/vong_khe.py
git commit -m "fix(tho): vòng khe đọc hạn mức dưới principal của chính khe (bs-78r.10)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task Q2: Quota lỗi/treo không làm hỏng nhịp tim, sentinel token

**Đợt:** 6 · **Phải sau:** Q1-b. Đọc hạn mức SAU khi gửi nhịp (`try/finally`); mọi lỗi (kể cả ghi sổ) bị chặn với thông báo cố định; `LoiThuHoi` (app-server hay cây dò UID) → `doc` trả True → `VongKhe.hong` dừng khe. `join` khi tắt chờ `chu_ky_nhip + 60` (> cận trên 48 s một lần đọc). App-server giả ghi env thật nó nhận (`GHI_ENV`) để test sentinel đi trọn đường.

**Files:**
- Modify: `tests/du_lieu/codex/app_server_gia.py`
- Modify: `tests/test_han_muc_principal.py`
- Create: `tests/test_nhip_han_muc.py`
- Modify: `tram/tho/han_muc_ranh.py`
- Modify: `tram/tho/vong_khe.py`

**Interfaces:**
- Consumes: Q1-b, P1 Task 5 (`VongKhe.hong`).
- Produces: `DocHanMucRanh.doc(ranh) -> bool`, `.khoa`; `VongKhe.nhip` = `_gui_nhip` + đọc hạn mức sau.

- [ ] **Step 1: Viết test thất bại**

`tests/du_lieu/codex/app_server_gia.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/du_lieu/codex/app_server_gia.py b/tests/du_lieu/codex/app_server_gia.py
index 9fa404b..87daa97 100644
--- a/tests/du_lieu/codex/app_server_gia.py
+++ b/tests/du_lieu/codex/app_server_gia.py
@@ -11,6 +11,8 @@ from pathlib import Path
 MAU = json.loads((Path(__file__).parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))
 che_do, ghi = os.environ.get("CHE_DO", "ok"), Path(os.environ.get("GHI", os.devnull))
 nhan = [{"CODEX_HOME": os.environ.get("CODEX_HOME")}]
+if os.environ.get("GHI_ENV"):                       # test bs-78r.10: env + argv thật mà app-server nhận
+    Path(os.environ["GHI_ENV"]).write_text(json.dumps({"env": dict(os.environ), "argv": sys.argv}))
 
 
 def tra(tin):
```

`tests/test_han_muc_principal.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_han_muc_principal.py b/tests/test_han_muc_principal.py
index e77a778..f7e5942 100644
--- a/tests/test_han_muc_principal.py
+++ b/tests/test_han_muc_principal.py
@@ -101,3 +101,18 @@ def test_uid_principal_chua_chung_minh_khong_hoi_quota(tmp_path, monkeypatch, ca
     vk.han_muc.lan_sau = 0.0
     vk.nhip()
     assert goi == [] and vk.han_muc.khoa and not vk.hong and "chưa chứng minh được UID" in capsys.readouterr().out
+
+
+def test_cay_do_uid_khong_thu_hoi_duoc_thi_dung_khe(tmp_path, monkeypatch):
+    from tram.kiem.vong_doi import LoiThuHoi
+    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: _khong_duoc_hoi()))
+    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiThuHoi("x")))
+    nc, k = _nc(tmp_path)
+    vk = VongKhe(nc, k[0])
+    vk.hop = SimpleNamespace(gui=lambda _: None)
+    vk.nhip()
+    assert vk.hong and vk.han_muc.khoa
+
+
+def _khong_duoc_hoi():
+    raise AssertionError("không được hỏi quota")
```

`tests/test_nhip_han_muc.py` (mới):

```python
"""bs-78r.10 (dot6-Q02) — Q2: quota lỗi/quá hạn/không thu hồi không làm hỏng nhịp tim; token không lộ. Nhịp gửi qua
`khach` giả; app-server là bản GIẢ (python của user đang test) sau principal giả cùng user — không sudo thật."""
import functools
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.chay_cli.bo_cli import BO_CLI
from tram.chay_cli.codex.app_server import LoiAppServer, hoi_app_server
from tram.chay_cli.codex.bo import BoCodex
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.principal import ChuaCoPrincipal
from tram.tho.vong_khe import VongKhe

GIA = Path(__file__).parent / "du_lieu" / "codex" / "app_server_gia.py"
BI_MAT = ("SENTINEL-MAY-9c1e", "SENTINEL-OPENAI-44d2", "SENTINEL-SERVER-0b7f")


class PrincipalGia:
    """Cùng user đang test: thay `codex app-server` bằng app-server giả, tiêm biến điều khiển qua /usr/bin/env."""
    user = "tram-k-c-codex-1"

    def __init__(self, *bien: str):
        self.bien = list(bien)

    def boc(self, argv):
        return ["/usr/bin/env", *self.bien, sys.executable, str(GIA)] if argv[-1] == "app-server" else argv

    def kill_nhom(self, pgid, sig):
        kill_cuc_bo(pgid, sig)


def _vk(tmp_path, monkeypatch, hoi, principal):
    thu_tu = []
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: 600)   # UID thật: test_danh_tinh, G3
    monkeypatch.setitem(BO_CLI, "codex", BoCodex(hoi=lambda *a, **k: thu_tu.append("hoi") or hoi(*a, **k)))
    k = KheCauHinh("codex-1", "codex", "user:x", tmp_path / "cfg", "Codex 1", ("coder",))
    gui = []
    khach = SimpleNamespace(goi=lambda m, u, than: thu_tu.append("nhip") or gui.append(than) or (200, {"phieu": None}))
    nc = NguCanhTho(CauHinhTho("C", "http://127.0.0.1:7700", (k,)), khach, goc=tmp_path / "tho-home",
                    principal_cua=principal)
    vk = VongKhe(nc, k)
    vk.hop = SimpleNamespace(gui=lambda _: None)
    vk.han_muc.da_xac_minh = True                       # nhịp xác minh UID riêng: test_han_muc_principal
    return vk, gui, thu_tu


def _nhip_hai_lan(vk):
    vk.nhip()
    vk.han_muc.lan_sau = 0.0
    return vk.nhip()


@pytest.mark.parametrize("loi", [LoiAppServer("x"), OSError("y"), RuntimeError("BI-MAT-LOI"), ChuaCoPrincipal("z")])
def test_quota_loi_nhip_van_gui_va_sau_khi_gui(tmp_path, monkeypatch, capsys, loi):
    def hoi(*a, **k):
        raise loi
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, hoi, lambda k, wt, ten: PrincipalGia())
    assert _nhip_hai_lan(vk) == {"phieu": None} and len(gui) == 2 and thu_tu[:2] == ["nhip", "hoi"]
    assert vk.so.doc_han_muc() is None and "BI-MAT-LOI" not in capsys.readouterr().out


def test_thieu_principal_khong_spawn_nhip_van_gui(tmp_path, monkeypatch):
    def khong_co(k, wt, ten):
        raise ChuaCoPrincipal("chưa khai")
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, lambda *a, **k: pytest.fail("không được hỏi quota"), khong_co)
    _nhip_hai_lan(vk)
    assert len(gui) == 2 and "hoi" not in thu_tu


def test_khong_thu_hoi_duoc_thi_dung_khe_khong_doc_lai(tmp_path, monkeypatch, capsys):
    def hoi(*a, **k):
        raise LoiThuHoi("x")
    vk, gui, thu_tu = _vk(tmp_path, monkeypatch, hoi, lambda k, wt, ten: PrincipalGia())
    _nhip_hai_lan(vk)
    assert gui and thu_tu.count("hoi") == 1 and vk.han_muc.khoa and vk.hong
    assert "dừng khe để kiểm principal" in capsys.readouterr().out


def test_app_server_treo_co_han_nhip_ke_tiep_van_gui(tmp_path, monkeypatch):
    vk, gui, _ = _vk(tmp_path, monkeypatch, functools.partial(hoi_app_server, thoi_gian_cho=0.5),
                     lambda k, wt, ten: PrincipalGia("CHE_DO=treo"))
    t0 = time.monotonic()
    _nhip_hai_lan(vk)
    assert len(gui) == 2 and time.monotonic() - t0 < 15 and vk.so.doc_han_muc() is None


def test_sentinel_token_khong_lo_qua_env_log_hay_nhip(tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("TRAM_THO_TOKEN", BI_MAT[0])
    monkeypatch.setenv("OPENAI_API_KEY", BI_MAT[1])
    env_con = tmp_path / "env-con.json"
    vk, gui, _ = _vk(tmp_path, monkeypatch, hoi_app_server,
                     lambda k, wt, ten: PrincipalGia("CHE_DO=lo", f"LO={BI_MAT[2]}", f"GHI_ENV={env_con}"))
    _nhip_hai_lan(vk)
    con = json.loads(env_con.read_text())
    assert not any(b in json.dumps(con["env"]) for b in BI_MAT[:2])
    assert not {"HOME", "USER", "TMPDIR", "TRAM_THO_TOKEN", "OPENAI_API_KEY"} & set(con["env"])
    ra = "".join(capfd.readouterr()) + json.dumps(gui)
    assert len(gui) == 2 and not any(b in ra for b in BI_MAT[:2]) and BI_MAT[2] not in json.dumps(gui)


def test_ghi_so_han_muc_loi_khong_lam_chet_nhip(tmp_path, monkeypatch):
    mau = json.loads((GIA.parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))["plus"]
    vk, gui, _ = _vk(tmp_path, monkeypatch, lambda *a, **k: mau, lambda k, wt, ten: PrincipalGia())
    monkeypatch.setattr(vk.so, "luu_han_muc", lambda hm: (_ for _ in ()).throw(OSError("đĩa đầy")))
    assert _nhip_hai_lan(vk) == {"phieu": None} and len(gui) == 2 and not vk.hong
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_nhip_han_muc.py tests/test_han_muc_principal.py`

Kết quả THẬT trên bản sao (trích):

```text
E       AssertionError: assert ({'phieu': None} == {'phieu': None}
E         
E         Omitting 1 identical items, use -vv to show
E         Use -v to get more diff and 2 == 2 and ['hoi', 'nhip'] == ['nhip', 'hoi']
E        +  where 2 = len([{'buoc_tho': 'ranh', 'khe_id': 'C/codex-1'}, {'buoc_tho': 'ranh', 'khe_id': 'C/codex-1'}])
E         
E         At index 0 diff: 'hoi' != 'nhip'
E         Use -v to get more diff)
E       AssertionError: assert ({'phieu': None} == {'phieu': None}
E         
E         Omitting 1 identical items, use -vv to show
E         Use -v to get more diff and 2 == 2 and ['hoi', 'nhip'] == ['nhip', 'hoi']
E        +  where 2 = len([{'buoc_tho': 'ranh', 'khe_id': 'C/codex-1'}, {'buoc_tho': 'ranh', 'khe_id': 'C/codex-1'}])
E         
7 failed, 7 passed in 1.47s
```

- [ ] **Step 3: Viết mã**

`tram/tho/han_muc_ranh.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/han_muc_ranh.py b/tram/tho/han_muc_ranh.py
index 31fd8f4..807803b 100644
--- a/tram/tho/han_muc_ranh.py
+++ b/tram/tho/han_muc_ranh.py
@@ -1,11 +1,15 @@
-"""Đọc hạn mức lúc khe RẢNH cho vòng nhịp tim (spec 3 §8.1; bs-78r.10 = dot6-Q02). Principal lấy từ ngữ cảnh của
-CHÍNH khe (`nc.principal(k, None, …)` — hồ sơ sandbox với `wt=None` không mở thêm thư mục khe khác); thiếu principal
-(`ChuaCoPrincipal`, một `ValueError`) → không spawn gì. Lần đọc đầu xác minh UID THỰC của principal (3C-B
-`xac_minh_uid` — `user:<quản lý>` cấu hình nhầm bị chặn); sai → thôi đọc hạn mức của khe."""
+"""Đọc hạn mức lúc khe RẢNH cho vòng nhịp tim (spec 3 §8.1; bs-78r.10 = dot6-Q02). Chạy SAU khi nhịp đã gửi: lỗi hay
+quá hạn của quota không làm trễ/chết nhịp tim. Principal lấy từ ngữ cảnh của CHÍNH khe (`nc.principal(k, None, …)` —
+hồ sơ sandbox với `wt=None` không mở thêm thư mục khe khác); thiếu/sai principal → không spawn gì. Nhịp đầu chỉ xác
+minh UID THỰC của principal (3C-B `xac_minh_uid` — `user:<quản lý>` cấu hình nhầm bị chặn; sai → thôi đọc hạn mức của
+khe), nhịp sau mới hỏi app-server: mỗi nhịp tốn tối đa một việc, cận trên XẤU NHẤT 48 s (`app_server`) → nhịp kế tiếp
+trễ tối đa ~78 s, vẫn < `mat_ket_noi_giay` 90 s. Không xác nhận thu hồi (`LoiThuHoi`, kể cả cây dò UID) → `doc` trả
+True: vòng khe DỪNG (như CLI không thu hồi được — P1). Thông báo cố định: không in exception, argv hay env (token)."""
 import time
 
 from tram.chay_cli.bo_cli import BO_CLI
 from tram.kiem import danh_tinh
+from tram.kiem.vong_doi import LoiThuHoi
 
 
 class DocHanMucRanh:
@@ -25,15 +29,21 @@ class DocHanMucRanh:
         if hm is not None:
             self.so.luu_han_muc(hm)
 
-    def doc(self, ranh: bool) -> None:
+    def doc(self, ranh: bool) -> bool:
+        """True = không xác nhận thu hồi tiến trình đọc hạn mức: người gọi dừng khe."""
         chu_ky = BO_CLI[self.k.cli].chu_ky_han_muc_ranh_giay
         if self.khoa or not ranh or chu_ky is None or time.monotonic() < self.lan_sau:
-            return
+            return False
         self.lan_sau = time.monotonic() + chu_ky
         try:
             self._doc()
+        except LoiThuHoi:
+            self.khoa = True
+            print(f"{self.khe_id}: không xác nhận thu hồi tiến trình đọc hạn mức — dừng khe để kiểm principal")
+            return True
         except danh_tinh.LoiDanhTinh:
             self.khoa = True
             print(f"{self.khe_id}: chưa chứng minh được UID của principal — không đọc hạn mức dưới principal này")
-        except ValueError:                  # ChuaCoPrincipal: khe chưa có principal → không đọc, không spawn
-            pass
+        except Exception:                   # noqa: BLE001 — quota hỏng không được làm chết luồng nhịp tim
+            print(f"{self.khe_id}: không đọc được hạn mức khe rảnh; nhịp tim tiếp tục")
+        return False
```

`tram/tho/vong_khe.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/vong_khe.py b/tram/tho/vong_khe.py
index 207a36a..08d95c0 100644
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -1,7 +1,8 @@
 """Vòng của MỘT khe trong `tram tho chay` (spec 3 §6.2, §7.2): nhịp tim 30 giây kiêm xin việc (luồng nền, kể cả khi
 đang chạy phiếu — mang `giao_id`/`luot`/`buoc_tho`/`han_muc`; `tiep_tuc: false` → `lenh` + dừng lần chạy), và vòng
 chính nhận phiếu → `chay_phieu`. Khởi động: CLI mồ côi bị kill + bảo đảm `chay.xong {mo-coi}`; phiếu đang giữ (đọc
-lại `phieu.json`) được chạy tiếp từ lần kế — trạm không trao lại phiếu (3a-1 G12)."""
+lại `phieu.json`) được chạy tiếp từ lần kế — trạm không trao lại phiếu (3a-1 G12). Hạn mức lúc rảnh đọc SAU khi gửi
+nhịp, dưới principal của khe (`han_muc_ranh`, bs-78r.10)."""
 import threading
 import time
 
@@ -40,7 +41,12 @@ class VongKhe:
         self.phieu_moi = tt
 
     def nhip(self) -> dict | None:
-        self.han_muc.doc(self.pc is None and self.phieu_moi is None)
+        try:
+            return self._gui_nhip()
+        finally:
+            self.hong |= self.han_muc.doc(self.pc is None and self.phieu_moi is None)
+
+    def _gui_nhip(self) -> dict | None:
         than = {"khe_id": self.khe_id, "buoc_tho": self.buoc}
         p = self.pc.p if self.pc else (Phieu.model_validate(self.phieu_moi.phieu) if self.phieu_moi else None)
         if p is not None:
@@ -90,7 +96,7 @@ class VongKhe:
         self.khoi_dong()
         nhip = threading.Thread(target=self._vong_nhip, args=(tat,), daemon=True, name=f"nhip-{self.khe_id}")
         nhip.start()
-        while not tat.is_set():
+        while not tat.is_set() and not self.hong:
             if self.lenh in DUNG_CUNG and self.phieu_moi is not None:
                 self.so.xoa_phieu()
                 self.phieu_moi = None
@@ -111,4 +117,4 @@ class VongKhe:
             self.han_giu, self.da_xac_nhan = None, False
             self.lenh = None
         self.dung.set()
-        nhip.join(timeout=self.nc.chu_ky_nhip + 5)
+        nhip.join(timeout=self.nc.chu_ky_nhip + 60)     # > cận trên một lần đọc hạn mức (48 s, han_muc_ranh)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_nhip_han_muc.py tests/test_han_muc_principal.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2326 tests collected in 3.26s`.

- [ ] **Step 5: Commit**

```bash
git add tests/du_lieu/codex/app_server_gia.py tests/test_han_muc_principal.py tests/test_nhip_han_muc.py tram/tho/han_muc_ranh.py tram/tho/vong_khe.py
git commit -m "fix(tho): quota lỗi hoặc treo không làm hỏng nhịp tim, không lộ token (bs-78r.10)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Gate

P1 → Q1 → Q2; P1 cũng chặn 3C-B. Phải đạt trước S5 và S6 có Codex cùng S1–S4 dưới principal có sử dụng Codex. S1 sơ bộ dưới user hiện tại theo D2 không thay nghiệm thu này. Không kéo blocker quota Codex sang bằng chứng Claude-only độc lập nếu điều kiện riêng đã đủ.

Không hỏi Đại ca có chấp nhận quota bỏ principal; câu trả lời đã nằm trong yêu cầu an toàn. Credential mới, đổi nguồn auth, fallback manager hoặc nới sandbox là ngoài phạm vi, phải trình riêng nếu thực sự cần.

**G2 (offline) cho Q1/Q2:** các task trên xanh + suite đầy đủ 2326 trên bản sao (xem dưới). **G5 — CHỈ chứng minh được trên macOS thật, sau quyền vận hành và tài khoản thử riêng (CHƯA CHẠY):**
1. `sudo -n -H -u <khe user>` (và `sandbox:` với hồ sơ `han-muc.sb`) chạy được `codex app-server` theo PATH cấu hình thợ; `ps` thấy tiến trình dưới UID của khe (P1 G6); `xac_minh_uid` lần đầu đạt.
2. App-server dùng `CODEX_HOME` của khe, KHÔNG đọc auth/`~/.codex` của tài khoản quản lý (đối chiếu bằng tài khoản thử chưa đăng nhập: phải ra "chưa đọc được", không ra số đo của quản lý).
3. Hồ sơ sandbox thật không chặn app-server cần gì ngoài thư mục khe (nếu chặn → báo, không nới tự ý).
4. Treo/giết thật: app-server bị giết qua `sudo -n -u <khe> /bin/kill`, không còn tiến trình dưới UID khe sau `thu_hoi` (`ps -U`), nhịp kế tiếp vẫn tới trạm trong 90 s.
5. Log launchd của `tram tho chay` không chứa token (grep sentinel đã cài trong env quản lý của phiên thử).

## Kết quả chạy thử trên bản sao (16/10/2026)

Bản sao `main` `5da881e` → áp P1 Task 1–9 rồi Q1-a, Q1-b, Q2 đúng nguyên văn plan, mỗi task RED rồi GREEN (log thật trích ở Step 2/4 từng task):

| Task | RED (thật) | GREEN (thật) | Tổng thu thập |
|---|---|---|---|
| Q1-a | 7 failed, 11 passed | 18 passed | 2314 |
| Q1-b | 2 failed, 2 passed | 4 passed | 2316 |
| Q2 | 7 failed, 7 passed | 14 passed | 2326 |

Ở RED của Q2, 7 ca xanh gồm 4 ca có sẵn của `test_han_muc_principal.py` (Q1-a/Q1-b) và 3 ca mới giữ hành vi Q1-b đã có (`test_thieu_principal_khong_spawn_nhip_van_gui`, `test_app_server_treo_co_han_nhip_ke_tiep_van_gui`, `test_sentinel_token_khong_lo_qua_env_log_hay_nhip`) — không phải test rỗng: chúng đỏ trên `main` gốc (chữ ký `principal` chưa có).

Suite đầy đủ cuối: xem "Kết quả chạy thử" ở plan P1 (cùng một lần chạy).

## Ghi chú triển khai (17/10/2026, I1)

Đối chiếu với `main` `59f8281`. Em không chạy lại test (I1 chỉ sửa tài liệu).

- **Ghép:** cùng merge `0e33fbf` với P1 + 3C-B. Commit: Q1-a `1ebb493` (`fix(codex): quota khe rảnh bắt buộc chạy dưới principal của khe`), Q1-b `e51ea65` (`fix(tho): vòng khe đọc hạn mức dưới principal của chính khe`), Q2 `fead2e1` (`fix(tho): quota lỗi hoặc treo không làm hỏng nhịp tim, không lộ token`).
- **Số test:** cả merge `0e33fbf` đưa `main` 2566 → 2650 (+84 = P1/3C-B +69, Q1/Q2 +15). Thân commit không ghi số riêng của Q1/Q2; +15 là số của bảng chạy thử, khớp tổng.
- **Chỗ lệch khi code:** không ghi nhận. Em không so lại từng dòng với plan.
- **Mã đã có:** `tram/chay_cli/codex/app_server.py` (`doc_han_muc_ranh` bắt buộc `principal`, thiếu thì không spawn); `tram/tho/han_muc_ranh.py` (`DocHanMucRanh`: principal của chính khe, xác minh UID thực lần đầu, lỗi/treo không làm chết nhịp, `LoiThuHoi` → dừng khe); `tram/tho/vong_khe.py`; `tram/tho/kiem_3b.py` (mục hạn mức của `tram tho kiem`).
- **Bead:** `bs-78r.10`, `bs-863.6` (Q1), `bs-863.7` (Q2) đã đóng ở mức mã. Đóng bead **không** có nghĩa G5 đạt.
- **Còn lại:** `codex login status` trong `tram tho kiem` vẫn chạy dưới tài khoản quản lý (`bs-863.17`, cùng loại, ngoài đường quota).
- **Cổng đang chờ:** G5 (mục "Gate" ở trên) — **CHƯA CHẠY**. Kịch bản cụ thể ở sổ tay, mục G5. Cần trước: S2 (user khe có thật), S5 (Codex của khe đã đăng nhập), Đại ca cho phép tài khoản thử riêng.
