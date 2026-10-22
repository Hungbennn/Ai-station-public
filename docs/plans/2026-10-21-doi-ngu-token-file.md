# Token file cho hai khe B — plan TDD bổ sung

Status: `REVIEW` · 21/10/2026 · nền HEAD `b26cb9e`, nhánh soạn `plan/token-file`.
**Goal:** B dùng token file dưới đúng UID, Claude nhận FD sau sudo, không cần mở Keychain.
**Architecture:** tái dùng principal/daemon/runner; một helper stdlib mở file sau đổi UID rồi exec Claude.
**Tech Stack:** Python 3.12, stdlib, pytest và bộ chặn host sẵn có; macOS 15.6.1/Claude 2.1.227 ở cổng thật.
**Spec:** [QĐ2 sửa 21/10](../../openspec/changes/doi-ngu-tho/QUYET-DINH.md),
[design §2](../../openspec/changes/doi-ngu-tho/design.md),
[spec token](../../openspec/changes/doi-ngu-tho/specs/doi-ngu-tho/spec.md),
[ADR-0009](../decisions/ADR-0009-quyen-khe-b.md).

> Triển khai từng task theo TDD; phiên này chỉ soạn/kiểm trên bản sao, không commit.
> Plan này thay phần token/Keychain của Task 4/9 và R2/R4/R5 trong
> [plan 20/10](2026-10-20-doi-ngu-tho.md); giữ mọi phần khác. Đọc spec trước mã.

## Global Constraints

- Không sửa `tram/`, `tests/`, `cong-cu/` trong worktree soạn; chỉ áp patch vào bản sao HEAD.
- Không commit, bd, push, mạng, tải gói, sudo/Keychain/launchctl thật; không sửa CURRENT_STATE/handover.
- Không thêm dependency hoặc daemon. `tram/` ≤120 dòng/file, ≤120 ký tự/dòng.
- QĐ2 sửa 21/10 cho phép file bí mật **chỉ** token Claude khe B và token máy B; các cấm bí mật khác giữ nguyên.
- File thường 0600, đúng UID, một hardlink; thư mục cuối 0700; từ chối symlink mọi thành phần.
  Không tin HOME/TRAM_HOME để tìm token; dùng passwd của effective UID. ACL macOS phải đo S6.
- Token không trong argv/log/env quản lý/sudo preserve-env. FD chỉ được mở và đặt env sau đổi UID.
- Giữ QĐ3/QĐ4/QĐ5, Uq, Git, quota, kiểm lại/QC, HR/tự merge/deploy tắt. Không tự xoay token.
- Sudoers hiện `NOPASSWD:SETENV: ALL`: 0600 không chống quản lý đổi UID qua sudo. Chưa được
  coi “tram-tho không đọc được” là bao gồm chống sudo; câu hỏi phạm vi ở QĐ2 chưa có trả lời trong phiên.
  Nếu đòi chống cả sudo: **blocker thiết kế**, không triển khai với lời hứa cách ly đó.
- Chỉ test qua `tests/chan_host/chay.sh`; lần kiểm cuối phải 0 dòng chặn mới. Không gọi pytest trần.
- Baseline đo trước sửa: 30 passed, 1 failed ở nhóm nen/kiem_cong/token_may/cong_cu.
  Test `test_kho_kiem_kho_tho_bang_quyen_tram_tho` phụ thuộc đường kho thật đang tồn tại,
  đỏ `kho-da-co-can-doi-soat-khong-ghi-de` thay `dung-sau-kiem`; **không phải lỗi sandbox**.
  Baseline riêng vòng thợ cũng đỏ `Không xác nhận thu hồi tiến trình của khe`, 1 failed/41.32s;
  chưa đủ dữ kiện quy toàn bộ nguyên nhân cho sandbox. Không sửa hai test ngoài phạm vi này.
- Lỗi ps/sysctl/bind do sandbox không tính hồi quy, nhưng không ghi suite xanh khi còn lỗi chưa phân loại.
- Chỉ QC/ghép và cổng thật sau này mới được nghiệm thu; không đánh dấu S2/S6 hoặc bs-2bd.11 bằng test giả.

## Bảng G và Files

| G | Bảo đảm | Task / bằng chứng |
|---|---|---|
| G1 | Nguyên tử, không symlink/hardlink/FIFO; lỗi giữ file cũ | 1, filesystem tạm thật |
| G2 | B file, từ xa Keychain, bootstrap trước YAML, HOME không đổi chủ | 2, runner Keychain giả |
| G3 | Helper sau sudo, FD và exec giữ prompt stdin; auth/do_nen/phiếu cùng đường | 3, exec/runner giả |
| G4 | setup-token/ô ẩn/stdin; bỏ keychain; sáu phép S6 có đối chứng | 4, công cụ giả |
| G5 | ACL, UID, CLI thật, không credential ngoài ý muốn, reboot không unlock | R2/R4/R5; chưa chứng minh offline |

Bản đồ tác động: `tram/tho` giữ file/helper/caller; `tram/chu/cai_dat_tho.py` chỉ sửa hướng dẫn,
không đổi sudoers; `cong-cu` giữ nhập token và phép S6. `tram/chay_cli/lenh_claude.py`,
`principal.boc`/`BIEN_GIU`, `san_sang_b.py` giữ mã vì allowlist/điểm gọi sẵn đủ; test đi qua chúng.
Không đổi schema/API/UI. Kill list §2 mục 2/3/6: được Đại ca giao soạn và thử giả, chưa cho chạy máy thật.

## Cách áp nguyên văn trên bản sao HEAD

Lưu từng khối `diff` theo nhãn `patch` vào `/private/tmp/codex-token/patches/` bằng mã sau.
`git archive` không chép sửa đổi chưa commit. Dùng thư mục mới để không ghi đè bản thử đã có.

```bash
mkdir -p /private/tmp/codex-token/patches
python3 - <<'PYCODE'
from pathlib import Path
import re
p = Path('docs/plans/2026-10-21-doi-ngu-token-file.md')
for ten, patch in re.findall(r'<!-- patch: ([^ ]+) -->\n```diff\n(.*?)```', p.read_text(), re.S):
    (Path('/private/tmp/codex-token/patches') / ten).write_text(patch)
PYCODE
TOKEN_PLAN_COPY=$(mktemp -d /private/tmp/codex-token/verify.XXXXXX)
git archive HEAD -o /private/tmp/codex-token/verify-head.tar
tar -xf /private/tmp/codex-token/verify-head.tar -C "$TOKEN_PLAN_COPY"
cd "$TOKEN_PLAN_COPY"
export PYTHONPATH="$TOKEN_PLAN_COPY"
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1 UV_CACHE_DIR=/private/tmp/codex-token/uv
```

Mỗi task: áp test → chạy RED → áp code → chạy GREEN. Patch task sau dựa trên task trước.
Bản mới phải `git apply --check` lại; không dùng số test trong plan thay kết quả mới.

## Task 1: Kho file kín, thay nguyên tử

**Files:**

- Tạo: `tests/test_token_file.py`.
- Tạo: `tram/tho/tep_token.py`.

**Interfaces:** `ghi(p: Path, token: str) -> None`, `doc(p: Path) -> str`, `mo(p: Path) -> int`; FD trả về do caller đóng. Chỉ stdlib.

- [ ] **Step 1: áp test nguyên văn.**

<!-- patch: t1-tests.patch -->
```diff
diff --git a/tests/test_token_file.py b/tests/test_token_file.py
new file mode 100644
--- /dev/null
+++ b/tests/test_token_file.py
@@ -0,0 +1,76 @@
+import os
+import stat
+from pathlib import Path
+
+import pytest
+
+
+def api():
+    import importlib.util
+    assert importlib.util.find_spec('tram.tho.tep_token'), 'Thiếu kho token file an toàn'
+    from tram.tho import tep_token
+    return tep_token
+
+
+def test_ghi_nguyen_tu_quyen_va_doc(tmp_path, monkeypatch):
+    m = api()
+    p = tmp_path / 'kin' / 'token'
+    m.ghi(p, 'gia-lap-cu')
+    inode = p.stat().st_ino
+    cu = os.replace
+    def replace(src, dst, **kw):
+        s = os.stat(src, dir_fd=kw['src_dir_fd'], follow_symlinks=False)
+        assert stat.S_IMODE(s.st_mode) == 0o600
+        assert p.read_text() == 'gia-lap-cu'
+        return cu(src, dst, **kw)
+    monkeypatch.setattr(os, 'replace', replace)
+    m.ghi(p, 'gia-lap-moi')
+    assert m.doc(p) == 'gia-lap-moi' and p.stat().st_ino != inode
+    assert p.stat().st_uid == os.geteuid()
+    assert stat.S_IMODE(p.stat().st_mode) == 0o600
+    assert stat.S_IMODE(p.parent.stat().st_mode) == 0o700
+    assert list(p.parent.iterdir()) == [p]
+
+
+@pytest.mark.parametrize('loi', ['symlink-file', 'symlink-cha', 'mode-file', 'mode-cha', 'hardlink', 'fifo', 'uid'])
+def test_tu_choi_kho_khong_kin(tmp_path, monkeypatch, loi):
+    m = api()
+    p = tmp_path / 'kin' / 'token'
+    m.ghi(p, 'gia-lap')
+    if loi == 'symlink-file':
+        p.rename(p.with_name('that')); p.symlink_to('that')
+    elif loi == 'symlink-cha':
+        p.parent.rename(tmp_path / 'that'); p.parent.symlink_to('that')
+    elif loi == 'mode-file':
+        p.chmod(0o644)
+    elif loi == 'mode-cha':
+        p.parent.chmod(0o755)
+    elif loi == 'hardlink':
+        os.link(p, p.with_name('khac'))
+    elif loi == 'fifo':
+        p.unlink(); os.mkfifo(p, 0o600)
+    else:
+        monkeypatch.setattr(os, 'geteuid', lambda: -1)
+    with pytest.raises((OSError, ValueError)):
+        m.doc(p)
+    with pytest.raises((OSError, ValueError)):
+        m.ghi(p, 'gia-lap-moi')
+
+
+def test_loi_rename_giu_token_cu_va_don_tmp(tmp_path, monkeypatch):
+    m = api(); p = tmp_path / 'kin/token'
+    m.ghi(p, 'gia-lap-cu')
+    def hong(*a, **kw):
+        raise OSError('gia-lap')
+    monkeypatch.setattr(os, 'replace', hong)
+    with pytest.raises(OSError):
+        m.ghi(p, 'gia-lap-moi')
+    assert m.doc(p) == 'gia-lap-cu' and list(p.parent.iterdir()) == [p]
+
+
+@pytest.mark.parametrize('token', ['', 'x\ny', 'x y', 'x' * 4097])
+def test_khong_ghi_gia_tri_sai(tmp_path, token):
+    m = api()
+    with pytest.raises(ValueError):
+        m.ghi(tmp_path / 'kin/token', token)
+    assert not (tmp_path / 'kin').exists()
```

```bash
git apply --check /private/tmp/codex-token/patches/t1-tests.patch
git apply /private/tmp/codex-token/patches/t1-tests.patch
```

- [ ] **Step 2: chạy RED.**

```bash
tests/chan_host/chay.sh -q tests/test_token_file.py
```

Đã đo trên bản sao HEAD: **13 failed; `AssertionError: Thiếu kho token file an toàn`**; 0 dòng chặn mới.

- [ ] **Step 3: áp mã nguyên văn.**

<!-- patch: t1-code.patch -->
```diff
diff --git a/tram/tho/tep_token.py b/tram/tho/tep_token.py
new file mode 100644
--- /dev/null
+++ b/tram/tho/tep_token.py
@@ -0,0 +1,80 @@
+"""File bí mật của chính UID: dirfd/no-follow, 0700/0600, thay nguyên tử; không log giá trị."""
+import os
+import re
+import secrets
+import stat
+from contextlib import contextmanager
+from pathlib import Path
+
+TOKEN = re.compile(r'[!-~]{1,4096}')
+
+
+def kiem(s, mode, *, thu_muc=False):
+    dung_loai = stat.S_ISDIR(s.st_mode) if thu_muc else stat.S_ISREG(s.st_mode) and s.st_nlink == 1
+    if not dung_loai or s.st_uid != os.geteuid() or stat.S_IMODE(s.st_mode) != mode:
+        raise ValueError('Kho token sai chủ/quyền/loại')
+
+
+@contextmanager
+def thu_muc(p: Path, *, tao=False):
+    if not p.is_absolute() or '..' in p.parts:
+        raise ValueError('Đường token phải tuyệt đối')
+    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
+    try:
+        for i, ten in enumerate(p.parts[1:]):
+            if tao and i == len(p.parts) - 2:
+                try:
+                    os.mkdir(ten, 0o700, dir_fd=fd)
+                except FileExistsError:
+                    pass
+            moi = os.open(ten, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
+            os.close(fd)
+            fd = moi
+        kiem(os.fstat(fd), 0o700, thu_muc=True)
+        yield fd
+    finally:
+        os.close(fd)
+
+
+def mo(p: Path) -> int:
+    with thu_muc(p.parent) as d:
+        fd = os.open(p.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
+    try:
+        kiem(os.fstat(fd), 0o600)
+        return fd
+    except BaseException:
+        os.close(fd)
+        raise
+
+
+def doc(p: Path) -> str:
+    with os.fdopen(mo(p), 'r', encoding='ascii') as f:
+        token = f.read(4097)
+    if not TOKEN.fullmatch(token):
+        raise ValueError('Token sai dạng')
+    return token
+
+
+def ghi(p: Path, token: str) -> None:
+    if not TOKEN.fullmatch(token):
+        raise ValueError('Token sai dạng')
+    with thu_muc(p.parent, tao=True) as d:
+        try:
+            kiem(os.stat(p.name, dir_fd=d, follow_symlinks=False), 0o600)
+        except FileNotFoundError:
+            pass
+        ten = '.token-' + secrets.token_hex(12)
+        fd = os.open(ten, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=d)
+        try:
+            with os.fdopen(fd, 'w', encoding='ascii') as f:
+                os.fchmod(f.fileno(), 0o600)
+                f.write(token)
+                f.flush()
+                os.fsync(f.fileno())
+            os.replace(ten, p.name, src_dir_fd=d, dst_dir_fd=d)
+            os.fsync(d)
+        finally:
+            try:
+                os.unlink(ten, dir_fd=d)
+            except FileNotFoundError:
+                pass
```

```bash
git apply --check /private/tmp/codex-token/patches/t1-code.patch
git apply /private/tmp/codex-token/patches/t1-code.patch
```

- [ ] **Step 4: chạy GREEN.**

```bash
tests/chan_host/chay.sh -q tests/test_token_file.py
```

Đã đo trên bản sao HEAD: **13 passed**; 0 dòng chặn mới.

- [ ] **Step 5:** đối chiếu diff/bằng chứng; không commit trong phiên soạn. Sau Task 4 chạy nhóm hồi quy dưới đây.

## Task 2: Token máy B chọn file, máy từ xa giữ Keychain

**Files:**

- Tạo: `tests/test_token_may_file.py`.
- Sửa: `tests/test_tho_lenh_chay.py`.
- Tạo: `tram/tho/token_may_file.py`.
- Sửa: `tram/tho/khach.py`.
- Sửa: `tram/tho/token_may.py`.
- Sửa: `tram/tho/lenh_chay.py`.
- Sửa: `tram/tho/lenh.py`.
- Sửa: `tram/tho/lenh_khe.py`.
- Sửa: `tram/tho/dang_ky_b.py`.
- Sửa: `tram/tho/do_nen.py`.
- Sửa: `tram/tho/cau_hinh.py`.

**Interfaces:** Dùng `tep_token.ghi/doc`; `doc_token_may(*, tren_may_b=False, chay=None)` và `ghi_token_may(..., tren_may_b=False)` giữ mặc định xa. CLI `nhan-token --may-b` cho bootstrap; có YAML thì tự chọn theo `tren_may_b`, YAML hỏng giữ đóng.

- [ ] **Step 1: áp test nguyên văn.**

<!-- patch: t2-tests.patch -->
```diff
diff --git a/tests/test_token_may_file.py b/tests/test_token_may_file.py
new file mode 100644
--- /dev/null
+++ b/tests/test_token_may_file.py
@@ -0,0 +1,69 @@
+import io
+import os
+from types import SimpleNamespace
+
+import pytest
+
+from tram.tho import khach, lenh_chay, token_may
+
+
+def nha(tmp_path, monkeypatch):
+    import pwd
+    monkeypatch.setattr(pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='tram-tho', pw_dir=str(tmp_path)))
+    return tmp_path / '.tram/token-may'
+
+
+def test_b_ghi_doc_file_khong_keychain(tmp_path, monkeypatch):
+    p = nha(tmp_path, monkeypatch)
+    token_may.ghi_token_may('B', 't' * 43, tren_may_b=True,
+                            chay=lambda *a, **kw: pytest.fail('đụng Keychain'))
+    assert khach.doc_token_may(tren_may_b=True) == 't' * 43
+    assert p.stat().st_mode & 0o777 == 0o600
+    p.chmod(0o644)
+    assert khach.doc_token_may(tren_may_b=True) is None
+
+
+def test_b_thieu_file_khong_lui_keychain(tmp_path, monkeypatch):
+    nha(tmp_path, monkeypatch)
+    monkeypatch.setattr(khach, 'doc_muc', lambda *a, **kw: pytest.fail('fallback'))
+    assert khach.doc_token_may(tren_may_b=True) is None
+
+
+def test_nhan_token_b_truoc_co_yaml(tmp_path, monkeypatch, capsys):
+    p = nha(tmp_path, monkeypatch)
+    monkeypatch.setattr(lenh_chay.sys, 'stdin', io.StringIO('t' * 43 + '\n'))
+    luu = lenh_chay.luu_token_may
+    monkeypatch.setattr(lenh_chay, 'luu_token_may', lambda token, **kw: luu(
+        token, chay=lambda *a, **k: pytest.fail('nhan-token B vẫn gọi Keychain'), doc=lambda: None, **kw))
+    assert lenh_chay._nhan_token(SimpleNamespace(may_b=True)) == 0
+    assert p.read_text() == 't' * 43
+    assert 't' * 43 not in str(capsys.readouterr())
+
+
+def test_khong_duoc_gia_home_de_ghi_duoi_user_khac(tmp_path, monkeypatch):
+    import pwd
+    monkeypatch.setenv('HOME', str(tmp_path))
+    monkeypatch.setattr(pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='khac', pw_dir=str(tmp_path)))
+    with pytest.raises(ValueError):
+        token_may.ghi_token_may('B', 't' * 43, tren_may_b=True)
+    assert not (tmp_path / '.tram').exists()
+
+
+def test_tu_xa_giu_keychain(monkeypatch):
+    monkeypatch.setattr(khach, 'doc_muc', lambda *a, **kw: 'gia-keychain')
+    assert khach.doc_token_may(tren_may_b=False) == 'gia-keychain'
+
+
+def test_nhan_token_tu_chon_b_theo_cau_hinh(tmp_path, monkeypatch):
+    from tram.tho import cau_hinh
+    from tram.duong_dan import tram_home
+    tram_home().mkdir(parents=True, exist_ok=True)
+    (tram_home() / "tho.yaml").touch()
+    p = nha(tmp_path, monkeypatch)
+    monkeypatch.setattr(cau_hinh, 'nap_cau_hinh_tho', lambda: SimpleNamespace(tren_may_b=True))
+    monkeypatch.setattr(lenh_chay.sys, 'stdin', io.StringIO('t' * 43))
+    monkeypatch.setattr(lenh_chay, 'luu_token_may', lambda token, **kw: (
+        token_may.ghi_token_may('B', token, tren_may_b=kw.get('tren_may_b', False),
+                               chay=lambda *a, **kw: pytest.fail('không dùng Keychain cho B'))))
+    assert lenh_chay._nhan_token(SimpleNamespace(may_b=False)) == 0
+    assert p.exists()
diff --git a/tests/test_tho_lenh_chay.py b/tests/test_tho_lenh_chay.py
--- a/tests/test_tho_lenh_chay.py
+++ b/tests/test_tho_lenh_chay.py
@@ -77,7 +77,7 @@
         sua_khe(tram_home_tam / "tho.yaml", bot="khong-co")
     goi = []
     monkeypatch.setattr("tram.tho.khach.KhachTram.goi", lambda self, m, d, than=None, **kw: goi.append(than) or (200, {}))
-    monkeypatch.setattr("tram.tho.khach.doc_token_may", lambda: "x")
+    monkeypatch.setattr("tram.tho.khach.doc_token_may", lambda **kw: "x")
     args = SimpleNamespace(ten="claude-1", dong_y=True)
     assert lenh_khe._bot_khe(args) == 2                                       # bỏ khe cuối → tho.yaml không hợp lệ
     args = SimpleNamespace(ten="claude-2", principal="user:tram-k-2", thu_muc_cau_hinh="/Users/k2/.claude",
```

```bash
git apply --check /private/tmp/codex-token/patches/t2-tests.patch
git apply /private/tmp/codex-token/patches/t2-tests.patch
```

- [ ] **Step 2: chạy RED.**

```bash
tests/chan_host/chay.sh -q tests/test_token_may_file.py tests/test_launchd_token_tho.py
```

Đã đo trên bản sao HEAD: **6 failed, 6 passed; `TypeError: ghi_token_may() got an unexpected keyword argument 'tren_may_b'`; test bootstrap báo `nhan-token B vẫn gọi Keychain`**; 0 dòng chặn mới.

- [ ] **Step 3: áp mã nguyên văn.**

<!-- patch: t2-code.patch -->
```diff
diff --git a/tram/tho/token_may_file.py b/tram/tho/token_may_file.py
new file mode 100644
--- /dev/null
+++ b/tram/tho/token_may_file.py
@@ -0,0 +1,28 @@
+"""Kho token máy B theo passwd của UID, không tin HOME/TRAM_HOME từ môi trường."""
+import os
+import pwd
+import re
+from pathlib import Path
+
+from tram.tho.tep_token import doc, ghi
+
+
+def duong() -> Path:
+    user = pwd.getpwuid(os.geteuid())
+    if user.pw_name != 'tram-tho':
+        raise ValueError('Token B chỉ do tram-tho giữ')
+    return Path(user.pw_dir) / '.tram/token-may'
+
+
+def doc_token_b() -> str | None:
+    try:
+        token = doc(duong())
+        return token if re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token) else None
+    except (OSError, ValueError, KeyError):
+        return None
+
+
+def ghi_token_b(token: str) -> None:
+    if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
+        raise ValueError('Token máy sai dạng')
+    ghi(duong(), token)
diff --git a/tram/tho/khach.py b/tram/tho/khach.py
--- a/tram/tho/khach.py
+++ b/tram/tho/khach.py
@@ -1,6 +1,4 @@
-"""Thợ gọi tram-api qua HTTP (spec 3 §5.1, §13 mục 2), kể cả trên máy B. Token máy đọc từ Keychain của TÀI KHOẢN
-QUẢN LÝ THỢ (`tram-tho-token` — tạo ở bước cài của 3a-2, sau spike S6); không in, không ghi file, không đưa vào môi
-trường CLI của khe."""
+"""Khách API thợ: B đọc file riêng của tram-tho; máy từ xa giữ Keychain. Không đưa token xuống khe."""
 import json
 import re
 import urllib.error
@@ -19,7 +17,10 @@
     pass
 
 
-def doc_token_may(*, chay=None) -> str | None:
+def doc_token_may(*, tren_may_b=False, chay=None) -> str | None:
+    if tren_may_b:
+        from tram.tho.token_may_file import doc_token_b
+        return doc_token_b()
     return doc_muc(KEYCHAIN_THO, chay=chay)
 
 
diff --git a/tram/tho/token_may.py b/tram/tho/token_may.py
--- a/tram/tho/token_may.py
+++ b/tram/tho/token_may.py
@@ -1,9 +1,4 @@
-"""Ghi token máy vào Keychain `tram-tho-token` của TÀI KHOẢN QUẢN LÝ THỢ (spec 3 §5.1, §9.2) — bước của
-`tram tho dang-ky` sau khi ghép. Token đi qua STDIN của `security -i` (không nằm trong argv — `ps` thấy được), không
-in, không ghi file; ghi xong đọc lại và so hằng thời gian (`security -i` có thể trả 0 dù lệnh con lỗi).
-
-Giá trị đến từ phản hồi của trạm → kiểm dạng trước khi ghép vào dòng lệnh của `security -i`. Chạy thật chờ S6 (Keychain
-của tài khoản quản lý thợ khi không có phiên GUI)."""
+"""Ghi token: B dùng file kín; máy từ xa giữ Keychain/stdin, không log giá trị."""
 import hmac
 import re
 import subprocess
@@ -14,9 +9,13 @@
 TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{32,128}")
 
 
-def ghi_token_may(may_id: str, token: str, *, chay=subprocess.run) -> None:
+def ghi_token_may(may_id: str, token: str, *, tren_may_b=False, chay=subprocess.run) -> None:
     if not MAY_RE.fullmatch(may_id or "") or not TOKEN_RE.fullmatch(token or ""):
-        raise ValueError("may_id hoặc token trạm trả về sai dạng — không ghi Keychain")
+        raise ValueError("may_id hoặc token trạm trả về sai dạng — không ghi kho token")
+    if tren_may_b:
+        from tram.tho.token_may_file import ghi_token_b
+        ghi_token_b(token)
+        return
     chay(["security", "-i"], input=f'add-generic-password -U -s {KEYCHAIN_THO} -a {may_id} -w "{token}"\n',
          text=True, check=True, capture_output=True)
     doc = doc_token_may(chay=chay)
diff --git a/tram/tho/lenh_chay.py b/tram/tho/lenh_chay.py
--- a/tram/tho/lenh_chay.py
+++ b/tram/tho/lenh_chay.py
@@ -1,5 +1,5 @@
 """Lệnh phía TÀI KHOẢN QUẢN LÝ THỢ (lát 3a-2): `tram tho chay` (một tiến trình/máy, mỗi khe một vòng — spec 3 §5),
-`tram tho nhan-token` (token máy vào Keychain `tram-tho-token`, đọc từ ống/ô ẩn, không in). Chạy thật cần cổng
+`tram tho nhan-token` (token B vào file kín, máy từ xa vào Keychain, đọc từ ống/ô ẩn, không in). Chạy thật cần cổng
 S2–S4, S6, S7 (`tram tho kiem` xanh hết) — không có cờ nào bỏ qua."""
 import re
 import signal
@@ -57,9 +57,9 @@
     except (ValueError, OSError, yaml.YAMLError):
         print("Cấu hình thợ chưa sẵn sàng; giữ tắt, đối soát rồi khởi động lại.")
         return 0
-    token = doc_token_may()
+    token = doc_token_may(tren_may_b=ch.tren_may_b)
     if not token:
-        print("Chưa có token máy trong Keychain; mở đúng Keychain rồi khởi động lại thợ.", file=sys.stderr)
+        print("Chưa có token máy hợp lệ; đối soát kho token rồi khởi động lại thợ.", file=sys.stderr)
         return 0
     tat = threading.Event()
     for s in (signal.SIGTERM, signal.SIGINT):
@@ -67,10 +67,14 @@
     return chay_may(NguCanhTho(ch, KhachTram(ch.tram_api, token)), tat)
 
 
-def luu_token_may(token: str, *, chay=subprocess.run, doc=doc_token_may) -> None:
-    """Token đi qua stdin của `security -i` (không nằm trong argv — `ps` thấy được); không in, không ghi file."""
+def luu_token_may(token: str, *, tren_may_b=False, chay=subprocess.run, doc=doc_token_may) -> None:
+    """B dùng file kín; máy từ xa giữ stdin Keychain. Không in token."""
     if not TOKEN_RE.fullmatch(token):
         raise ValueError("Token máy sai dạng")
+    if tren_may_b:
+        from tram.tho.token_may_file import ghi_token_b
+        ghi_token_b(token)
+        return
     chay(["security", "-i"], input=f"add-generic-password -U -s {KEYCHAIN_THO} -a tram -w {token}\n", text=True,
          check=True, capture_output=True, timeout=10)
     if doc() != token:
@@ -81,15 +85,24 @@
     import getpass
     token = (sys.stdin.readline() if not sys.stdin.isatty() else getpass.getpass("Dán token máy (ẩn): ")).strip()
     try:
-        luu_token_may(token)
-    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError):
-        print("Chưa xác nhận lưu token máy; giữ thợ tắt và đối soát Keychain.", file=sys.stderr)
+        from tram.duong_dan import tram_home
+        from tram.tho.cau_hinh import nap_cau_hinh_tho
+        may_b = getattr(args, "may_b", False)
+        if not may_b and (tram_home() / "tho.yaml").exists():
+            may_b = nap_cau_hinh_tho().tren_may_b
+        if may_b:
+            luu_token_may(token, tren_may_b=True)
+        else:
+            luu_token_may(token)
+    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, yaml.YAMLError):
+        print("Chưa xác nhận lưu token máy; giữ thợ tắt và đối soát kho token.", file=sys.stderr)
         return 2
-    print(f"Đã lưu token máy vào Keychain ({KEYCHAIN_THO}).")
+    print("Đã lưu token máy; chưa bật thợ.")
     return 0
 
 
 def them_lenh_chay(tho) -> None:
     tho.add_parser("chay", help="Chạy máy thợ: nhịp tim, nhận phiếu, chạy CLI (chờ cổng S2–S7)").set_defaults(ham=_chay)
-    tho.add_parser("nhan-token", help="Lưu token máy (đọc từ ống hoặc ô ẩn) vào Keychain").set_defaults(
-        ham=_nhan_token)
+    nhan = tho.add_parser("nhan-token", help="Lưu token qua stdin/ô ẩn; B dùng --may-b trước khi có YAML")
+    nhan.add_argument("--may-b", action="store_true")
+    nhan.set_defaults(ham=_nhan_token)
diff --git a/tram/tho/lenh.py b/tram/tho/lenh.py
--- a/tram/tho/lenh.py
+++ b/tram/tho/lenh.py
@@ -15,7 +15,7 @@
     except ValueError as e:
         print(f"[ĐỎ] tho.yaml: {e}")
         return 1
-    khach = KhachTram(ch.tram_api, doc_token_may() or "")
+    khach = KhachTram(ch.tram_api, doc_token_may(tren_may_b=ch.tren_may_b) or "")
     try:
         dd = dau_do_that(ch, khach, du_an=tuple(args.du_an))
         van_ban, ma = in_ket_qua(kiem_may(ch, dd))
diff --git a/tram/tho/lenh_khe.py b/tram/tho/lenh_khe.py
--- a/tram/tho/lenh_khe.py
+++ b/tram/tho/lenh_khe.py
@@ -34,7 +34,7 @@
     p = tram_home() / "tho.yaml"
     p.write_text(moi, encoding="utf-8")
     ch = nap_cau_hinh_tho(p)
-    ma, kq = KhachTram(ch.tram_api, doc_token_may() or "").goi(
+    ma, kq = KhachTram(ch.tram_api, doc_token_may(tren_may_b=ch.tren_may_b) or "").goi(
         "POST", "/api/tho/dang-ky",
         {"may_id": ch.may_id, "khe": [{"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho,
                                        "vai_uu_tien": list(k.vai_uu_tien)} for k in ch.khe]})
diff --git a/tram/tho/dang_ky_b.py b/tram/tho/dang_ky_b.py
--- a/tram/tho/dang_ky_b.py
+++ b/tram/tho/dang_ky_b.py
@@ -66,7 +66,7 @@
         if input("Gõ dong-y: ").strip() != "dong-y":
             return 1
     try:
-        token = doc_token_may()
+        token = doc_token_may(tren_may_b=True)
         if not token:
             raise ValueError("Thiếu token máy")
         goc = tram_home()
diff --git a/tram/tho/do_nen.py b/tram/tho/do_nen.py
--- a/tram/tho/do_nen.py
+++ b/tram/tho/do_nen.py
@@ -32,7 +32,7 @@
 def main():
     try:
         ch = nap_cau_hinh_tho()
-        token = doc_token_may()
+        token = doc_token_may(tren_may_b=ch.tren_may_b)
         if not token or not san_sang_b(ch):
             print("DO-NEN: CHUA-DANG-NHAP", flush=True)
             return 2
diff --git a/tram/tho/cau_hinh.py b/tram/tho/cau_hinh.py
--- a/tram/tho/cau_hinh.py
+++ b/tram/tho/cau_hinh.py
@@ -1,4 +1,5 @@
-"""`~/.tram/tho.yaml` của tài khoản quản lý thợ (spec 3 §9.1). Không chứa bí mật — token máy ở Keychain.
+"""`~/.tram/tho.yaml` của tài khoản quản lý thợ (spec 3 §9.1). Không chứa bí mật.
+Token B ở file riêng, máy từ xa ở Keychain.
 
 `principal` (tài khoản/sandbox thực thi của khe) chốt sau spike S6: lát 3a-1 chỉ đọc như chuỗi, chưa dùng."""
 import re
```

```bash
git apply --check /private/tmp/codex-token/patches/t2-code.patch
git apply /private/tmp/codex-token/patches/t2-code.patch
```

- [ ] **Step 4: chạy GREEN.**

```bash
tests/chan_host/chay.sh -q tests/test_token_may_file.py tests/test_launchd_token_tho.py
```

Đã đo trên bản sao HEAD: **12 passed**; 0 dòng chặn mới.

- [ ] **Step 5:** đối chiếu diff/bằng chứng; không commit trong phiên soạn. Sau Task 4 chạy nhóm hồi quy dưới đây.

## Task 3: Claude mở FD sau chuyển UID

**Files:**

- Tạo: `tests/test_claude_token_file.py`.
- Sửa: `tests/test_kiem_cong.py`.
- Tạo: `tram/tho/claude_token.py`.
- Tạo: `tram/tho/lenh_token_khe.py`.
- Sửa: `tram/tho/kiem_cong.py`.
- Sửa: `tram/tho/deps_b.py`.
- Sửa: `tram/tho/do_nen.py`.

**Interfaces:** Dùng `tep_token.mo/doc/ghi`; `lenh_token_khe(*args)` chỉ dựng argv, `boc_token(argv)` chỉ bọc Claude. Helper lệnh `ghi|kiem|chay`, không nhận đường file/CLI tuỳ ý. Principal và BIEN_GIU không mang thêm OAuth.

- [ ] **Step 1: áp test nguyên văn.**

<!-- patch: t3-tests.patch -->
```diff
diff --git a/tests/test_claude_token_file.py b/tests/test_claude_token_file.py
new file mode 100644
--- /dev/null
+++ b/tests/test_claude_token_file.py
@@ -0,0 +1,82 @@
+import importlib.util
+import os
+from pathlib import Path
+from types import SimpleNamespace
+
+import pytest
+
+
+def api():
+    assert importlib.util.find_spec('tram.tho.claude_token'), 'Thiếu wrapper FD dưới UID khe'
+    from tram.tho import claude_token
+    return claude_token
+
+
+def test_wrapper_fd_khong_token_trong_argv_env(tmp_path, monkeypatch):
+    m = api()
+    monkeypatch.setattr(m.pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='tram-khe1', pw_dir=str(tmp_path)))
+    from tram.tho.tep_token import ghi
+    p = tmp_path / 'claude/oauth-token'; ghi(p, 'oauth-gia-lap')
+    monkeypatch.setenv('CLAUDE_CODE_OAUTH_TOKEN', 'token-cu')
+    monkeypatch.setenv('CLAUDE_CODE_REMOTE', '1')
+    monkeypatch.setenv('ANTHROPIC_API_KEY', 'key-cu')
+    monkeypatch.setenv('CLAUDE_CONFIG_DIR', '/sai')
+    monkeypatch.setenv('TRAM_THO_TOKEN', 'may-cu')
+    da = []
+    def execve(cli, argv, env):
+        fd = int(env['CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR'])
+        da.append(fd)
+        assert os.get_inheritable(fd) and os.read(fd, 4096) == b'oauth-gia-lap'
+        assert env['CLAUDE_CONFIG_DIR'] == str(p.parent)
+        assert env['HOME'] == str(tmp_path)
+        assert not {'CLAUDE_CODE_OAUTH_TOKEN', 'CLAUDE_CODE_REMOTE', 'ANTHROPIC_API_KEY', 'TRAM_THO_TOKEN'} & env.keys()
+        assert cli == '/opt/homebrew/bin/claude' and argv == [cli, 'auth', 'status']
+        assert all('oauth-gia-lap' not in str(x) for x in (argv, env))
+    monkeypatch.setattr(os, 'execve', execve)
+    m.chay(['auth', 'status'])
+    with pytest.raises(OSError):
+        os.fstat(da[0])
+
+
+@pytest.mark.parametrize('loi', ['thieu', 'credential', 'uid', 'sai-mode'])
+def test_wrapper_dong_khi_kho_hong(tmp_path, monkeypatch, loi):
+    m = api()
+    monkeypatch.setattr(m.pwd, 'getpwuid', lambda uid: SimpleNamespace(
+        pw_name='tram-tho' if loi == 'uid' else 'tram-khe2', pw_dir=str(tmp_path)))
+    from tram.tho.tep_token import ghi
+    p = tmp_path / 'claude/oauth-token'; ghi(p, 'gia-lap')
+    if loi == 'thieu': p.unlink()
+    if loi == 'credential': (p.parent / '.credentials.json').touch()
+    if loi == 'sai-mode': p.chmod(0o644)
+    monkeypatch.setattr(os, 'execve', lambda *a: pytest.fail('exec khi kho hong'))
+    with pytest.raises((ValueError, OSError)):
+        m.chay(['auth', 'status'])
+
+
+def test_boc_nam_sau_sudo_va_env_khong_bi_mat(tmp_path):
+    from test_doi_ngu_nen import ch
+    from tram.tho.kiem_cong import dang_nhap
+    from tram.tho.deps_b import boc_kiem_b
+    from tram.tho.principal import Principal, BIEN_GIU
+    c = ch(); da = []
+    def run(argv, **kw):
+        da.append((argv, kw)); return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}')
+    assert dang_nhap(c, c.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=run, xac_minh=lambda *a: 600)[0] == 'xanh'
+    a, kw = da[0]
+    assert any(x.endswith('/claude_token.py') for x in a), 'auth status chưa qua wrapper'
+    assert a.index('-u') < a.index('-I') and a[-3:] == ['chay', 'auth', 'status']
+    assert not any('OAUTH' in x for x in BIEN_GIU) and not any('TOKEN' in x for x in kw['env'])
+    pc = SimpleNamespace(p=SimpleNamespace(du_an='ben-station'), principal=Principal('user', 'tram-khe1'))
+    a = boc_kiem_b(pc)(['claude', '-p'])
+    assert a.index('--') < a.index('TRAM_KIEM_DA_CHUAN_BI=1') < a.index('-I')
+    assert a[-2:] == ['chay', '-p']
+
+
+def test_do_nen_cung_wrapper(tmp_path, monkeypatch):
+    from test_doi_ngu_nen import ch
+    from tram.tho.do_nen import thu_claude
+    monkeypatch.setattr(Path, 'home', lambda: tmp_path); (tmp_path / 'tram').mkdir()
+    def run(argv, **kw):
+        assert any(x.endswith('/claude_token.py') for x in argv), 'do-nen chưa qua wrapper'
+        return SimpleNamespace(returncode=0, stdout='{"type":"result","is_error":false,"result":"SAN-SANG"}')
+    assert thu_claude(ch(), chay=run)
diff --git a/tests/test_kiem_cong.py b/tests/test_kiem_cong.py
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -47,7 +47,7 @@
     ch = cau_hinh(tmp_path)
     assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)[0] == "xanh"
     argv, env = goi[0]
-    assert argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and argv[-3:] == ["claude", "auth", "status"]
+    assert argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and argv[-3:] == ["chay", "auth", "status"]
     assert env["CLAUDE_CONFIG_DIR"] == str(tmp_path / "cfg1") and "TRAM_THO_TOKEN" not in env
     ch2 = cau_hinh(tmp_path, (None, None))
     assert dang_nhap(ch2, ch2.khe[0], goc=tmp_path, goc_wt=tmp_path)[0] == "do"
```

```bash
git apply --check /private/tmp/codex-token/patches/t3-tests.patch
git apply /private/tmp/codex-token/patches/t3-tests.patch
```

- [ ] **Step 2: chạy RED.**

```bash
tests/chan_host/chay.sh -q tests/test_claude_token_file.py tests/test_kiem_cong.py tests/test_doi_ngu_nen.py
```

Đã đo trên bản sao HEAD: **8 failed, 10 passed; `Thiếu wrapper FD dưới UID khe`, `auth status chưa qua wrapper`, `do-nen chưa qua wrapper`**; 0 dòng chặn mới.

- [ ] **Step 3: áp mã nguyên văn.**

<!-- patch: t3-code.patch -->
```diff
diff --git a/tram/tho/claude_token.py b/tram/tho/claude_token.py
new file mode 100644
--- /dev/null
+++ b/tram/tho/claude_token.py
@@ -0,0 +1,69 @@
+"""Điểm vào stdlib sau sudo: mở token bằng UID khe rồi exec Claude; không in bí mật."""
+import os
+import pwd
+import sys
+from pathlib import Path
+
+if not __package__:
+    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
+from tram.tho.principal import BIEN_GIU
+from tram.tho.tep_token import TOKEN, doc, ghi, mo
+
+CLI = '/opt/homebrew/bin/claude'
+FD_ENV = 'CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR'
+
+
+def duong():
+    user = pwd.getpwuid(os.geteuid())
+    if user.pw_name not in ('tram-khe1', 'tram-khe2'):
+        raise ValueError('Chỉ chạy dưới UID khe B')
+    return Path(user.pw_dir) / 'claude/oauth-token'
+
+
+def kiem():
+    p = duong()
+    for credential in (p.parent / '.credentials.json', p.parent.parent / '.claude/.credentials.json'):
+        if credential.exists() or credential.is_symlink():
+            raise ValueError('Còn credential ngoài file đã duyệt')
+    doc(p)
+    return p
+
+
+def chay(argv):
+    p = kiem()
+    fd = mo(p)
+    try:
+        if not TOKEN.fullmatch(os.read(fd, 4097).decode('ascii')):
+            raise ValueError('Token sai dạng')
+        os.lseek(fd, 0, os.SEEK_SET)
+        os.set_inheritable(fd, True)
+        env = {k: v for k, v in os.environ.items() if k in BIEN_GIU}
+        env.update(HOME=str(p.parent.parent), CLAUDE_CONFIG_DIR=str(p.parent))
+        # Cờ thư viện được đặt bởi boc_kiem_b sau sudo, không mang bí mật.
+        if os.environ.get('TRAM_KIEM_DA_CHUAN_BI') == '1':
+            env['TRAM_KIEM_DA_CHUAN_BI'] = '1'
+        env[FD_ENV] = str(fd)
+        os.execve(CLI, [CLI, *argv], env)
+    finally:
+        os.close(fd)
+
+
+def main():
+    try:
+        if sys.argv[1:] == ['ghi']:
+            ghi(duong(), sys.stdin.read(4098).strip())
+            kiem()
+        elif sys.argv[1:] == ['kiem']:
+            kiem()
+        elif sys.argv[1:2] == ['chay']:
+            chay(sys.argv[2:])
+        else:
+            raise ValueError('Sai lệnh')
+    except (OSError, ValueError, KeyError):
+        print('TOKEN-KHE: CHUA-XAC-NHAN', file=sys.stderr)
+        return 2
+    return 0
+
+
+if __name__ == '__main__':
+    raise SystemExit(main())
diff --git a/tram/tho/lenh_token_khe.py b/tram/tho/lenh_token_khe.py
new file mode 100644
--- /dev/null
+++ b/tram/tho/lenh_token_khe.py
@@ -0,0 +1,12 @@
+"""Chỉ dựng argv không bí mật; helper thuộc runtime tin cậy, được chạy SAU principal.boc."""
+from pathlib import Path
+
+from tram.kiem.toolchain import PYTHON
+
+
+def lenh_token_khe(*args):
+    return [f'{PYTHON}/bin/python3.12', '-I', str(Path(__file__).with_name('claude_token.py')), *args]
+
+
+def boc_token(argv):
+    return lenh_token_khe('chay', *argv[1:]) if argv and argv[0] == 'claude' else argv
diff --git a/tram/tho/kiem_cong.py b/tram/tho/kiem_cong.py
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -8,7 +8,6 @@
 from tram.kiem.bang_tien_trinh import chup_nhan
 from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.vong_doi import LoiThuHoi
-
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.don_uid import con_lai
 from tram.tho.khach import DichKiemAm, LoiKhachTram
@@ -17,10 +16,10 @@
 from tram.tho.kiem_may import DauDo, MucKiem
 from tram.tho.principal import ChuaCoPrincipal
 from tram.tho.principal_khe import principal_cua
+from tram.tho.lenh_token_khe import boc_token
 
-LENH_DANG_NHAP = ("auth", "status")                    # CHỜ S2: lệnh trạng thái không đọc file đăng nhập
+LENH_DANG_NHAP = ("auth", "status")  # B qua helper FD; S2 vẫn cần đo daemon thật
 KEYCHAIN_CAM = ("tram-tho-token", "tram-noi-bo-token", "tram-anthropic-api-key")
-
 def _uid(p, xac_minh) -> tuple[int | None, str | None]:
     """Lỗi UID/thu hồi: không chạy thêm; chỉ hướng dẫn có điều kiện, không chép ngoại lệ."""
     try:
@@ -40,8 +39,9 @@
     if (ly_do := _uid(p, xac_minh)[1]) is not None:
         return "do", ly_do
     env = {"CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh), "PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}
+    argv = boc_token([k.cli, *LENH_DANG_NHAP]) if ch.tren_may_b else [k.cli, *LENH_DANG_NHAP]
     try:
-        kq = chay(p.boc([k.cli, *LENH_DANG_NHAP]), kill=p.kill_nhom, capture_output=True, text=True, timeout=30,
+        kq = chay(p.boc(argv), kill=p.kill_nhom, capture_output=True, text=True, timeout=30,
                   env=env)
     except LoiThuHoi:
         return "do", "không xác nhận thu hồi tiến trình lệnh trạng thái — kiểm principal" + HUONG_DAN_SUDO
diff --git a/tram/tho/deps_b.py b/tram/tho/deps_b.py
--- a/tram/tho/deps_b.py
+++ b/tram/tho/deps_b.py
@@ -20,6 +20,10 @@
 
 
 def boc_kiem_b(pc):
+    from tram.tho.lenh_token_khe import boc_token
     def boc(argv):
+        argv = boc_token(argv)
+        if pc.p.du_an != 'ben-station':
+            return pc.principal.boc(argv)
         return pc.principal.boc(['/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', *argv])
-    return boc if pc.p.du_an == 'ben-station' else pc.principal.boc
+    return boc
diff --git a/tram/tho/do_nen.py b/tram/tho/do_nen.py
--- a/tram/tho/do_nen.py
+++ b/tram/tho/do_nen.py
@@ -7,6 +7,7 @@
 from tram.tho.cau_hinh import nap_cau_hinh_tho
 from tram.tho.khach import KhachTram, doc_token_may
 from tram.tho.principal import doc_principal
+from tram.tho.lenh_token_khe import boc_token
 from tram.tho.san_sang_b import san_sang_b
 
 
@@ -19,7 +20,7 @@
             env = {"PATH": ch.chay.path_cli, "LANG": "C.UTF-8", "CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh)}
             argv = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--tools", "",
                     "--setting-sources", "user", "--strict-mcp-config", "--max-turns", "1"]
-            kq = chay(pr.boc(argv), env=env, cwd=goc, kill=pr.kill_nhom, timeout=120,
+            kq = chay(pr.boc(boc_token(argv)), env=env, cwd=goc, kill=pr.kill_nhom, timeout=120,
                       input="Chỉ trả lời SAN-SANG. Không dùng công cụ.", text=True, capture_output=True)
             dong = [json.loads(x) for x in kq.stdout.splitlines() if x.strip()]
             dat = any(x.get("type") == "result" and x.get("is_error") is False
```

```bash
git apply --check /private/tmp/codex-token/patches/t3-code.patch
git apply /private/tmp/codex-token/patches/t3-code.patch
```

- [ ] **Step 4: chạy GREEN.**

```bash
tests/chan_host/chay.sh -q tests/test_claude_token_file.py tests/test_kiem_cong.py tests/test_doi_ngu_nen.py
```

Đã đo trên bản sao HEAD: **18 passed**; 0 dòng chặn mới.

- [ ] **Step 5:** đối chiếu diff/bằng chứng; không commit trong phiên soạn. Sau Task 4 chạy nhóm hồi quy dưới đây.

## Task 4: Sổ tay setup-token và S6 file có đối chứng

**Files:**

- Tạo: `tests/test_doi_ngu_token_file.py`.
- Sửa: `tests/test_doi_ngu_cong_cu.py`.
- Tạo: `cong-cu/doi_ngu_token.py`.
- Sửa: `cong-cu/doi_ngu_b.py`.
- Sửa: `cong-cu/doi_ngu_chuan_bi.py`.
- Sửa: `cong-cu/doi_ngu_s6.py`.
- Sửa: `tram/chu/cai_dat_tho.py`.

**Interfaces:** Dùng helper Task 3 qua Python ghim `-I`. `dang_nhap(c, n)` thay login cũ; `kiem_token_s6(c)` đo sáu phép âm sau đối chứng owner. `c.goi` chỉ log tên/mã, `c.tuong_tac` chỉ hiện Terminal.

- [ ] **Step 1: áp test nguyên văn.**

<!-- patch: t4-tests.patch -->
```diff
diff --git a/tests/test_doi_ngu_token_file.py b/tests/test_doi_ngu_token_file.py
new file mode 100644
--- /dev/null
+++ b/tests/test_doi_ngu_token_file.py
@@ -0,0 +1,68 @@
+import importlib
+import sys
+from pathlib import Path
+from types import SimpleNamespace
+
+import pytest
+
+sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cong-cu'))
+
+
+def api():
+    assert importlib.util.find_spec('doi_ngu_token'), 'Thiếu sổ tay token file'
+    return importlib.import_module('doi_ngu_token')
+
+
+def test_login_setup_token_an_stdin_khong_log(monkeypatch):
+    m = api(); goi = []; log = []
+    monkeypatch.setattr(m, 'can_tat', lambda c: None)
+    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
+    monkeypatch.setattr(m.getpass, 'getpass', lambda prompt: 'oauth-gia-lap')
+    class Gia:
+        def tuong_tac(self, ten, argv):
+            goi.append((ten, argv, {}))
+        def goi(self, ten, argv, **kw):
+            goi.append((ten, argv, kw))
+            return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}', stderr='')
+        def ghi(self, *a): log.append(a)
+    m.dang_nhap(Gia(), 1)
+    assert goi[0][1][-1] == 'setup-token'
+    ghi = next(x for x in goi if x[0] == 'ghi-token-khe')
+    assert ghi[1][:5] == ['sudo', '-H', '-u', 'tram-khe1', m.PYTHON]
+    assert ghi[2]['input'] == 'oauth-gia-lap' and ghi[1][-1] == 'ghi'
+    assert all('oauth-gia-lap' not in str(x[1]) for x in goi)
+    assert 'oauth-gia-lap' not in str(log)
+    assert goi[-1][1][-3:] == ['chay', 'auth', 'status']
+
+
+def test_login_khong_tty_khong_setup(monkeypatch):
+    m = api(); monkeypatch.setattr(m, 'can_tat', lambda c: None)
+    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: False))
+    with pytest.raises(m.Dung, match='Terminal'):
+        m.dang_nhap(SimpleNamespace(), 1)
+
+
+@pytest.mark.parametrize('ma, err, dat', [(1, 'Permission denied', True),
+                                        (1, 'No such file or directory', False), (0, '', False), (127, '', False)])
+def test_s6_chi_tu_choi_quyen_moi_dat(ma, err, dat):
+    m = api(); da = []
+    class Gia:
+        def goi(self, ten, argv, **kw):
+            da.append((ten, argv))
+            return SimpleNamespace(returncode=ma if 'bi-chan' in ten else 0,
+                                   stdout='', stderr=err)
+    if dat:
+        m.kiem_token_s6(Gia())
+        am = [a for t, a in da if 'bi-chan' in t]
+        assert len(am) == 6  # hai chiều chéo + hai quản lý→khe + hai khe→máy
+        assert all('security' not in a and '-c' in a for a in am)
+        assert all('.read(' not in a[a.index('-c') + 1] for a in am)
+    else:
+        with pytest.raises(m.Dung): m.kiem_token_s6(Gia())
+
+
+def test_keychain_khong_con_la_buoc(monkeypatch):
+    import doi_ngu_b as b
+    monkeypatch.setattr(b.sys, 'argv', ['doi_ngu_b.py', 'keychain'])
+    monkeypatch.setattr(b, 'Chay', lambda: pytest.fail('không được bắt đầu bước keychain'))
+    assert b.main() == 2
diff --git a/tests/test_doi_ngu_cong_cu.py b/tests/test_doi_ngu_cong_cu.py
--- a/tests/test_doi_ngu_cong_cu.py
+++ b/tests/test_doi_ngu_cong_cu.py
@@ -211,22 +211,9 @@
     assert thay and all(d == "/" for d in thay)
 
 
-def test_keychain_tat_tu_khoa_sau_mo(monkeypatch):
-    # R2 máy B 21/10 (Đại ca chọn A): keychain tạo bằng lệnh tự khoá sau 300s + khi ngủ → Claude mất đăng nhập.
+def test_khong_con_ham_keychain_trong_so_tay():
     import doi_ngu_b
-    monkeypatch.setattr(doi_ngu_b, "can_tat", lambda c: None)
-    lenh = []
-    class Gia:
-        def goi(self, ten, argv, **kw):
-            return SimpleNamespace(returncode=0)
-        def tuong_tac(self, ten, argv):
-            lenh.append((ten, argv))
-    doi_ngu_b.keychain(Gia())
-    for u in ("tram-tho", "tram-khe1", "tram-khe2"):
-        kc = f"/Users/{u}/Library/Keychains/login.keychain-db"
-        ten = [t for t, a in lenh if u in a]
-        assert ten.index("bo-tu-khoa") > ten.index("mo-keychain")
-        assert ("bo-tu-khoa", ["sudo", "-H", "-u", u, "security", "set-keychain-settings", kc]) in lenh
+    assert not hasattr(doi_ngu_b, 'keychain')
 
 
 def _kho_gia(tmp_path, monkeypatch, ma_test):
```

```bash
git apply --check /private/tmp/codex-token/patches/t4-tests.patch
git apply /private/tmp/codex-token/patches/t4-tests.patch
```

- [ ] **Step 2: chạy RED.**

```bash
tests/chan_host/chay.sh -q tests/test_doi_ngu_token_file.py tests/test_doi_ngu_cong_cu.py -k 'not test_kho_kiem_kho_tho_bang_quyen_tram_tho'
```

Đã đo trên bản sao HEAD: **8 failed, 15 passed, 1 deselected; `Thiếu sổ tay token file` và test bỏ keychain đỏ**; 0 dòng chặn mới.

- [ ] **Step 3: áp mã nguyên văn.**

<!-- patch: t4-code.patch -->
```diff
diff --git a/cong-cu/doi_ngu_token.py b/cong-cu/doi_ngu_token.py
new file mode 100644
--- /dev/null
+++ b/cong-cu/doi_ngu_token.py
@@ -0,0 +1,68 @@
+"""Nhập token tại Terminal; thăm dò quyền chỉ mở/đóng, không trả nội dung bí mật."""
+import getpass
+import json
+import sys
+import warnings
+
+from doi_ngu_chuan_bi import PYTHON, RUNTIME, THO, can_tat
+from doi_ngu_io import Dung
+
+HELPER = str(RUNTIME / 'tram/tho/claude_token.py')
+MO_THU = '''import os, sys
+try:
+    fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOFOLLOW)
+    os.close(fd)
+except PermissionError:
+    print('Permission denied', file=sys.stderr)
+    sys.exit(1)
+'''
+
+
+def dang_nhap(c, n):
+    can_tat(c)
+    if n not in (1, 2) or not sys.stdin.isatty():
+        raise Dung('can-Terminal.app-khe-hop-le')
+    u = f'tram-khe{n}'
+    dau = ['sudo', '-H', '-u', u]
+    c.tuong_tac('setup-token', [*dau, '/usr/bin/env', f'CLAUDE_CONFIG_DIR=/Users/{u}/claude',
+                              '/opt/homebrew/bin/claude', 'setup-token'])
+    with warnings.catch_warnings():
+        warnings.simplefilter('error', getpass.GetPassWarning)
+        try:
+            token = getpass.getpass('Dán token Claude vừa tạo (ẩn): ').strip()
+        except (getpass.GetPassWarning, EOFError):
+            raise Dung('khong-co-o-nhap-an') from None
+    # Bỏ ACL cũ trước ghi: mode 0700 không tự xoá ACL của bước chuẩn bị cũ.
+    c.goi('bo-acl-claude', [*dau, 'chmod', '-N', f'/Users/{u}/claude'], han=30)
+    c.goi('kin-claude', [*dau, 'chmod', '700', f'/Users/{u}/claude'], han=30)
+    try:
+        c.goi('ghi-token-khe', [*dau, PYTHON, '-I', HELPER, 'ghi'], input=token, han=30)
+    finally:
+        token = None
+    c.goi('kiem-token-khe', [*dau, PYTHON, '-I', HELPER, 'kiem'], han=30)
+    r = c.goi('auth-status-fd', [*dau, PYTHON, '-I', HELPER, 'chay', 'auth', 'status'], han=30)
+    try:
+        dat = json.loads(r.stdout).get('loggedIn') is True
+    except (ValueError, AttributeError):
+        dat = False
+    if not dat:
+        raise Dung('S2-chua-dang-nhap-qua-FD')
+    c.ghi('S2-file', 'DAT-CHO-DO-NEN')
+
+
+def kiem_token_s6(c):
+    from tram.tho.cham_tham_do import cham
+    # Đối chứng dưới chủ file; helper kiểm chủ, mode, loại, không trả token.
+    for n in (1, 2):
+        c.goi('token-khe-doi-chung', ['sudo', '-H', '-u', f'tram-khe{n}', PYTHON, '-I', HELPER, 'kiem'], han=30)
+    script = ('import sys; sys.path.insert(0, sys.argv[1]); '
+              'from tram.tho.token_may_file import doc_token_b; sys.exit(0 if doc_token_b() else 2)')
+    c.goi('token-may-doi-chung', ['sudo', '-H', '-u', 'tram-tho', PYTHON, '-I', '-c', script, str(RUNTIME)], han=30)
+    for n in (1, 2):
+        dich = f'/Users/tram-khe{n}/claude/oauth-token'
+        for user, p in ((f'tram-khe{3-n}', dich), ('tram-tho', dich),
+                        (f'tram-khe{n}', str(THO / '.tram/token-may'))):
+            r = c.goi('token-bi-chan', ['sudo', '-H', '-u', user, PYTHON, '-I', '-c', MO_THU, p],
+                      check=False, han=30)
+            if cham('doc', r.returncode, '', r.stderr)[0] != 'dat':
+                raise Dung('token-file-chua-chung-minh-bi-chan')
diff --git a/cong-cu/doi_ngu_b.py b/cong-cu/doi_ngu_b.py
--- a/cong-cu/doi_ngu_b.py
+++ b/cong-cu/doi_ngu_b.py
@@ -11,34 +11,7 @@
 from doi_ngu_chuan_bi import CAU_HINH, PLIST, REPO, RUNTIME, THO, TRAM, can_tat, chuan_bi, kho, lenh_tho
 
 
-def keychain(c):
-    can_tat(c)
-    for u in ("tram-tho", "tram-khe1", "tram-khe2"):
-        p = Path(f"/Users/{u}/Library/Keychains/login.keychain-db")
-        r = c.goi("co-keychain", ["sudo", "test", "-f", str(p)], check=False, han=30)
-        if r.returncode == 1:
-            c.goi("thu-muc-keychain", ["sudo", "-u", u, "mkdir", "-p", str(p.parent)], han=30)
-            c.tuong_tac("tao-keychain", ["sudo", "-H", "-u", u, "security", "create-keychain", str(p)])
-        elif r.returncode != 0:
-            raise Dung("khong-doc-duoc-keychain")
-        c.tuong_tac("chon-keychain", ["sudo", "-H", "-u", u, "security", "default-keychain", "-s", str(p)])
-        c.tuong_tac("mo-keychain", ["sudo", "-H", "-u", u, "security", "unlock-keychain", str(p)])
-        # Đại ca chọn A (21/10): không tự khoá theo giờ/khi ngủ; mở tới khi reboot (sau reboot chạy lại bước này).
-        c.tuong_tac("bo-tu-khoa", ["sudo", "-H", "-u", u, "security", "set-keychain-settings", str(p)])
-
-
-def dang_nhap(c, n):
-    can_tat(c)
-    u = f"tram-khe{n}"
-    # Không chụp đầu ra: trình duyệt/mã đăng nhập chỉ Đại ca nhìn ở Terminal.app.
-    c.tuong_tac("dang-nhap-claude", ["sudo", "-H", "-u", u, "env",
-        f"CLAUDE_CONFIG_DIR=/Users/{u}/claude", "/opt/homebrew/bin/claude", "auth", "login"])
-    c.tuong_tac("xem-danh-tinh", ["sudo", "-H", "-u", u, "env",
-        f"CLAUDE_CONFIG_DIR=/Users/{u}/claude", "/opt/homebrew/bin/claude", "auth", "status"])
-    for p in (f"/Users/{u}/claude/.credentials.json", f"/Users/{u}/.claude/.credentials.json"):
-        r = c.goi("khong-credential-file", ["sudo", "test", "-e", p], check=False, han=30)
-        if r.returncode != 1:
-            raise Dung("S2-can-doi-soat-cach-luu-khong-mo-file")
+from doi_ngu_token import dang_nhap
 
 
 def token(c):
@@ -51,11 +24,11 @@
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
     b = None
     try:
-        b = subprocess.Popen(lenh_tho("nhan-token"), stdin=a.stdout,
+        b = subprocess.Popen(lenh_tho("nhan-token", "--may-b"), stdin=a.stdout,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
         a.stdout.close()
         mb, ma = b.wait(timeout=30), a.wait(timeout=30)
-        c.ghi("token-keychain", f"nguon={ma},dich={mb}")
+        c.ghi("token-file", f"nguon={ma},dich={mb}")
         if ma or mb:
             raise Dung("token-chua-xac-nhan-khong-tu-cap-lai")
     finally:
@@ -154,7 +127,7 @@
 
 
 def main():
-    if len(sys.argv) != 2 or sys.argv[1] not in ("chuan-bi", "keychain", "login-1", "login-2", "token",
+    if len(sys.argv) != 2 or sys.argv[1] not in ("chuan-bi", "login-1", "login-2", "token",
             "dang-ky", "kho", "do-nen", "kiem", "s6", "bat-khe", "bat-tho", "bat-giao", "tat-giao", "dung"):
         print("Chọn đúng bước của sổ tay; không có bước chạy tất cả.")
         return 2
@@ -167,8 +140,6 @@
         c.tuong_tac("xac-thuc-sudo", ["sudo", "-v"])
         if buoc == "chuan-bi":
             chuan_bi(c)
-        elif buoc == "keychain":
-            keychain(c)
         elif buoc.startswith("login-"):
             dang_nhap(c, int(buoc[-1]))
         elif buoc == "token":
diff --git a/cong-cu/doi_ngu_chuan_bi.py b/cong-cu/doi_ngu_chuan_bi.py
--- a/cong-cu/doi_ngu_chuan_bi.py
+++ b/cong-cu/doi_ngu_chuan_bi.py
@@ -55,8 +55,7 @@
         c.goi("quyen-nha-khe", ["sudo", "chmod", "700", f"/Users/{user}"], han=30)
         c.goi("quyen-claude", ["sudo", "chmod", "700", f"/Users/{user}/claude"], han=30)
         c.goi("quan-ly-di-qua", ["sudo", "chmod", "+a", "user:tram-tho allow search", f"/Users/{user}"], han=30)
-        c.goi("quan-ly-xem-thu-muc", ["sudo", "chmod", "+a", "user:tram-tho allow search,list",
-                                   f"/Users/{user}/claude"], han=30)
+        c.goi("claude-khong-acl", ["sudo", "-u", user, "chmod", "-N", f"/Users/{user}/claude"], han=30)
     for rel in (".tram", ".tram/log", "tram", "tram/kho", "tram/worktrees", ".tram/hang-doi/B"):
         c.goi("thu-muc-tho", ["sudo", "-u", "tram-tho", "mkdir", "-p", str(THO / rel)], han=30)
     for rel in ("", ".tram"):
diff --git a/cong-cu/doi_ngu_s6.py b/cong-cu/doi_ngu_s6.py
--- a/cong-cu/doi_ngu_s6.py
+++ b/cong-cu/doi_ngu_s6.py
@@ -75,21 +75,22 @@
         script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
         script += "from tram.tho.luot_b import xoa_cay; xoa_cay(Path(sys.argv[2]), Path(sys.argv[3]))"
         q("xoa-luot", RUNTIME / ".venv/bin/python", "-I", "-c", script, RUNTIME, gate, repo)
-    # Đối chứng token từ đúng chủ; giá trị chỉ dùng trong bộ nhớ gọi API, không ghi log.
-    r = q("token-doi-chung", "security", "find-generic-password", "-s", "tram-tho-token", "-w")
-    from tram.tho.khach import KhachTram
+    from doi_ngu_token import kiem_token_s6
+    kiem_token_s6(c)
+    from tram.tho.khach import DichKiemAm
     from tram.tho.kiem_am import chay_tham_do, tham_do_api_db
     from tram.tho.principal import doc_principal
-    khach = KhachTram("http://127.0.0.1:7700", r.stdout.strip())
-    d = khach.kiem_am()
+    # Token chỉ được đọc trong tiến trình tram-tho; stdout chỉ chứa đích thăm dò không bí mật.
+    script = ("import sys, json; from dataclasses import asdict; sys.path.insert(0, sys.argv[1]); "
+              "from tram.tho.khach import KhachTram, doc_token_may; "
+              "k = KhachTram('http://127.0.0.1:7700', doc_token_may(tren_may_b=True) or ''); "
+              "print(json.dumps(asdict(k.kiem_am())))")
+    r = q('dich-kiem-am', RUNTIME / '.venv/bin/python', '-I', '-c', script, RUNTIME)
+    d = DichKiemAm(**json.loads(r.stdout))
     for n in (1, 2):
         user = f"tram-khe{n}"
         pr = doc_principal(f"user:{user}")
-        r = c.goi("token-khe-bi-chan", ["sudo", "-H", "-u", user, "security", "find-generic-password",
-            "-s", "tram-tho-token", "-w", str(THO / "Library/Keychains/login.keychain-db")], check=False, han=30)
-        if cham("keychain", r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
-            raise Dung("keychain-chua-chung-minh-bi-chan")
-        ds = tham_do_api_db(api=khach.url, dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu))
+        ds = tham_do_api_db(api="http://127.0.0.1:7700", dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu))
         kq = chay_tham_do(ds, boc=pr.boc, kill=pr.kill_nhom,
                          env={"PATH": "/opt/homebrew/bin:/usr/bin:/bin", "LANG": "C.UTF-8"})
         if not all(x.dat for x in kq):
diff --git a/tram/chu/cai_dat_tho.py b/tram/chu/cai_dat_tho.py
--- a/tram/chu/cai_dat_tho.py
+++ b/tram/chu/cai_dat_tho.py
@@ -91,15 +91,15 @@
     canh_bao = [
         "Cơ chế cách ly CHƯA CHỐT (§14): chỉ gõ dong-y khi Đại ca đã chốt sau spike S6 — "
         "tạo user là thay đổi hệ thống.",
-        "Token máy B: sau khi user quản lý có Keychain, chạy (token không hiện ra màn hình): "
-        f"tram chu cap-token-may B --dong-y | sudo -u {quan_ly} -H {uv} run --project {repo} tram tho nhan-token",
+        "Token máy B: ghi file riêng của quản lý qua stdin (token không hiện ra màn hình): "
+        f"tram chu cap-token-may B --dong-y | sudo -u {quan_ly} -H {uv} run --project {repo} "
+        "tram tho nhan-token --may-b",
         "Mỗi khe: Đại ca tự đăng nhập Claude dưới đúng principal (S2): sudo -u <principal> -H env "
         "CLAUDE_CONFIG_DIR=<thu_muc_cau_hinh> claude — hoặc claude setup-token nếu S2 buộc dùng token.",
         f"Viết ~/.tram/tho.yaml của {quan_ly} (spec 3 §9.1) với principal: {co_che}:<user> và khoá chay.day "
         "(khớp cong_bo.phuong_an của trạm — chốt sau S7). Kiểm: tram tho kiem (mọi mục xanh) và "
         "tram chu kiem-cach-ly (H9) TRƯỚC khi bật 3a.",
-        "launchd: LaunchDaemon có UserName chạy không cần đăng nhập màn hình; Keychain của user dịch vụ có mở được "
-        "dưới launchd không là việc của spike S2 — không được thì dừng, không đổi sang lưu token ra file.",
+        "launchd: B dùng token file riêng theo QĐ2 sửa 21/10; S2/R5 phải đo FD và reboot không mở Keychain.",
         f"Sổ {so.p}: chỉ ghi thêm. S6 hỏng → `tram chu go-cai-dat-tho` chỉ gỡ thứ sổ ghi da_tao VÀ còn đúng định "
         "danh (user: UID + GeneratedUID; file: sha256) — in kế hoạch, chờ dong-y."]
     return KeHoach(tep=tep, lenh=[] if giu_tat else lenh, canh_bao=canh_bao + pk.canh_bao,
```

```bash
git apply --check /private/tmp/codex-token/patches/t4-code.patch
git apply /private/tmp/codex-token/patches/t4-code.patch
```

- [ ] **Step 4: chạy GREEN.**

```bash
tests/chan_host/chay.sh -q tests/test_doi_ngu_token_file.py tests/test_doi_ngu_cong_cu.py -k 'not test_kho_kiem_kho_tho_bang_quyen_tram_tho'
```

Đã đo trên bản sao HEAD: **23 passed, 1 deselected**; 0 dòng chặn mới.

- [ ] **Step 5:** đối chiếu diff/bằng chứng; không commit trong phiên soạn. Sau Task 4 chạy nhóm hồi quy dưới đây.

## Kiểm tích hợp, giới hạn và QC

```bash
tests/chan_host/chay.sh -q tests/test_token_file.py tests/test_token_may_file.py \
  tests/test_claude_token_file.py tests/test_doi_ngu_token_file.py tests/test_doi_ngu*.py \
  tests/test_kiem_cong.py tests/test_dang_nhap_principal.py tests/test_launchd_token_tho.py \
  tests/test_token_may.py tests/test_principal.py tests/test_tho_lenh_chay.py \
  tests/test_do_dai_ma.py tests/test_vong_import.py \
  -k 'not test_kho_kiem_kho_tho_bang_quyen_tram_tho and not test_chay_may_tron_vong_roi_don_worktree_bead_da_dong'
```

Hai test bị loại đã đỏ trên HEAD chưa sửa như Global Constraints; không xoá/sửa để lấy xanh.
Chạy lại đầy đủ hai ca trên môi trường QC trước ghép; toàn suite sau triển khai do người điều phối chạy.
Không coi đây là chứng nhận toàn bộ hệ thống. Skill TDD cung cấp RED/GREEN; verification kiểm patch thực;
security/code-review rà chủ/mode, đường bí mật, sudo và caller. Tự review không thay QC độc lập.

Một lần RED đầu thiếu stub đã chạm bộ chặn `security -i` (1 dòng chặn, không chạy host).
Đã sửa test dùng fake bắt lỗi, chạy lại cả chuỗi trên bản sao mới: mọi RED/GREEN cuối đều 0 dòng chặn.
Các test cũ đổi đúng hợp đồng: auth argv thêm wrapper, mock nhận keyword backend, xoá kỳ vọng set-keychain-settings.

## R2 bổ sung — login và token máy (chỉ sau code/QC/ghép, duyệt kịch bản)

Bỏ hoàn toàn bước `keychain`. Không gọi `set-keychain-settings`, không đưa mật khẩu/token vào lệnh.
Giữ giao việc tắt và daemon disable/vắng. Runtime đã cập nhật đúng SHA, khe không có quyền sửa helper/CLI.
Không chạy lại `chuan-bi` trên runtime đã có; đối soát/cập nhật runtime bằng kịch bản riêng có sao lưu.

Tại Terminal.app dưới hungle, chạy từng lệnh riêng:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" login-1
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" login-2
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" token
```

Login: setup-token hiện trực tiếp Terminal/trình duyệt; Đại ca chọn đúng account rồi dán token vào ô ẩn.
Không tee/script/xtrace/chụp màn token. Writer chạy dưới khe qua stdin; helper kiểm đúng UID/chủ/0600,
cha 0700/no-follow, không `.credentials.json` ở hai vị trí phổ biến; auth status qua FD loggedIn=true.
Không tự xoá credential cũ: nếu phát hiện thì dừng, đối soát rồi duyệt bước thu hồi/xoá riêng.
S3: Đại ca xác nhận hai account trong luồng setup-token; auth status qua token có thể không trả email,
không lấy hai tên thư mục hay hai token khác nhau thay bằng chứng account. Log chỉ kết luận khác/chưa rõ.

Bước token vẫn đòi sao lưu, không phiếu B và `cap-moi`; pipe trực tiếp vào `nhan-token --may-b`,
không cần tho.yaml trước. Nếu nguồn đã cấp nhưng đích lỗi: giữ tắt, đối soát trước cấp lại.
Không mở lại CLI ghép đã đóng. Không đổi token chỉ vì API/auth đang lỗi.

## R4 bổ sung — FD thực, quyền và headless

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" do-nen
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" s6
```

Do-nen dùng chính system/vn.tram.tho/UserName tram-tho, wrapper dưới từng khe, hai câu cố định,
tối đa 120 giây/khe, không tools/nhận phiếu. Chỉ nhận `DO-NEN: DAT-HAI-KHE` khi ping B,
auth và hai headless đều đạt; kiểm không xuất hiện credential ngoài file đã duyệt sau chạy.
Test fake exec chỉ chứng minh code dựng FD; macOS `/dev/fd/N`, CLI đọc token/không tự lưu thêm,
hạn/thu hồi, stdin prompt và account thực phải đo ở đây. Không suy hành vi từ tên env đơn thuần.

Khảo sát binary cục bộ 2.1.227: SHA256 và hàm HEu/tA/Lgs ở design §2; CLI đọc FD bằng
`/dev/fd/N`, token env thường thắng FD, CLAUDE_CODE_REMOTE có nhánh persist. Wrapper dựng env mới
không có các biến ấy. Chưa chạy CLI/API thật trong phiên plan; thay CLI version phải đo lại.

S6 có owner đối chứng trước, sáu phép mở/đóng không đọc token: khe2→khe1, tram-tho→khe1,
khe1→máy, khe1→khe2, tram-tho→khe2, khe2→máy. Chỉ đúng lỗi quyền mới đạt; thiếu file không đạt.
Các ca Git/settings/API/DB/thu hồi của R4 cũ giữ nguyên. `token-khe-bi-chan` cũ được thay bằng
file probe; không còn phụ thuộc lỗi Keychain mã 44. Bộ chấm Keychain chung không đổi.
S6 trực tiếp **không** chứng minh quản lý có sudo ALL không thể đọc; phải xử lý phạm vi QĐ2 trước triển khai.

## R5 bổ sung — tự lên sau reboot, không unlock

Không dùng “chạy do-nen thủ công sau login” làm bằng chứng tự lên. Giữ `giao_viec.bat=false`,
phiếu B rỗng. Sau R4, người vận hành duyệt riêng việc chuẩn bị phép đo hữu hạn cho lần reboot:

1. Giữ bản plist gốc kín để phục hồi. Tạo bản của **cùng** `vn.tram.tho`, giữ UserName/HOME/PATH/cwd;
   ProgramArguments là `/Users/Shared/tram-tho-code/.venv/bin/python -m tram.tho.do_nen`,
   `RunAtLoad=true`, `KeepAlive=false`, log 0600 ở nhà tram-tho với tên mới cho lần đo.
   Đối soát plist trước cài, enable service; không bootstrap để tránh chạy phép đo trước reboot.
2. Đại ca reboot. Không chạy keychain/unlock/login-N/token; không cấp lại bí mật. Daemon tự thực hiện
   phép đo theo RunAtLoad. Sau đó đọc riêng kết luận cố định và mốc thời gian khởi động để xác nhận
   kết quả thuộc lần boot mới; kiểm không cần phiên GUI của khe. API phải sẵn sàng; nếu chưa, ghi
   chưa đạt và điều tra thứ tự khởi động, không quy cho token hoặc tự thêm retry/daemon.
3. Đòi ping may_id=B, hai auth/Claude qua wrapper và `DO-NEN: DAT-HAI-KHE`, không credential mới,
   chủ/mode/ACL còn đúng. Dừng/disable phép đo, phục hồi nguyên plist gốc. Sau khi toàn bộ cổng đạt
   và Đại ca duyệt bật thợ, đo thêm nhịp của daemon gốc sau reboot (giao vẫn tắt), không chỉ phép do_nen.

R5 chỉ ghi hết nợ bs-2bd.11 sau bằng chứng trên; không đóng bead trong phiên này. Quy trình chuẩn bị
plist dùng cơ chế sao lưu/cài/khôi phục của `doi_ngu_b.do_nen`; không thêm service hay file mật khẩu.
R6/R7 và đường lui cũ giữ nguyên. Token hỏng/hết hạn: giữ giao tắt, đăng nhập lại có chủ ý;
không rollback về Keychain đã chứng minh không hoạt động. Giữ token hợp lệ khi rollback mã,
không sao chép giá trị vào backup thường; khoá/thu hồi qua nhà cung cấp khi cần đổi.

## Kết quả phiên soạn

Xem [KET-QUA-TOKEN-FILE.md](../../openspec/changes/doi-ngu-tho/KET-QUA-TOKEN-FILE.md)
cho số đo cuối, OpenSpec và phần chưa thể kết luận. Không có mã triển khai trong worktree.

## Ghi chú triển khai

Chưa triển khai/commit/ghép. Bản sao tạm là bằng chứng áp plan, không là runtime được phép chạy thật.
