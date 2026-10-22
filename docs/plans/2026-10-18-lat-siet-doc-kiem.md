# Siết đọc kiểm — Implementation Plan

> **For agentic workers:** dùng `ai-skills:executing-plans` thực hiện từng task. PLAN để review;
> phiên này chỉ áp tạm test/mã rồi hoàn nguyên, không commit, không sửa CURRENT_STATE/handover.

**Trạng thái review vòng 2 (19/10): ĐẠT về plan; chưa nghiệm thu máy B.**
Giữ repo hiện tại; chỉ quản lý tin cậy `tram-tho` có ACL search, hai principal chạy mã không tin cậy không có ACL.
Không dùng các con số lịch sử của bản soạn làm bằng chứng cho bản sửa; xem mục kiểm chứng cuối.

**Goal:** các principal bỏ staff; quản lý tin cậy dùng ACL search riêng, khe/kiểm không vào nhà Đại ca; lượt kiểm chỉ đọc đúng vùng được cấp,
Python kiểm nằm ngoài nhà người vận hành; G4.3 phát hiện đường đọc và launchd còn lọt.

**Architecture:** nhóm chính riêng mỗi principal; sổ R2 theo dõi group bằng GID/GUID, không nhận nhóm lạ.
Hồ sơ mặc định từ chối đọc, toolchain phiên bản cố định; toàn prefix Python được cài root:wheel có manifest SHA.
Bộ kiểm prefix tham gia quan sát trước/sau lượt. Các phép thử G4 không phải bộ chạy tách phiên.

**Tech Stack:** Python 3.12/std library, pytest qua bộ chặn host, Seatbelt/macOS 24G90, Homebrew hiện có; không tải gói.

**Spec:** D159 `docs/quyet-dinh/2026-10-18-tach-phien-kiem.md`; yêu cầu Đại ca phiên này;
`/Users/dai-ca/Developer/Ben Station/.handover/thao-luan-phien-rieng/v2-codex.md` §2 và §3 bước 2–4.
D159 thắng đề xuất cũ của v2: **S6 vẫn đóng tới khi cắt kế thừa phiên**, kể cả rào giai đoạn 1 đạt.

**Giữ gọn:** Task 4 còn 3 module mới (gộp canary và receipt vào `mau_g4`); bỏ `user_tram` đã hết caller.
Migration không chown toàn cây: UID không đổi thì owner bits vẫn áp dụng; chỉ audit và đổi nhóm.
Giữ R2/rollback, checksum Python và receipt G4 vì chúng phục vụ an toàn, không thêm broker/daemon/IPC mới.

## Global Constraints

- Mốc review vòng 2 `754da6a` (vòng 1 `ba13fa8`, bản soạn dựa `ad02c0d`), nhánh `plan/siet-doc-d157`, cây ban đầu sạch. Không commit, push, bd ghi, mạng,
  sudo/launchctl ghi thật, Keychain, cấu hình thật hoặc tiến trình không do test tạo.
- File `tram/` ≤120 dòng, dòng ≤120 ký tự. Test chỉ adapter giả; cổng OS là việc Đại ca chạy riêng sau duyệt.
- Không đổi UID của user; chỉ thêm ACL search cho quản lý tin cậy, không thêm quyền cho khe/kiểm; không mở toàn `/opt/homebrew`, `/System`, `/private`, `/dev`.
- Không cho khe/kiểm đọc nhà Đại ca để chữa Python; ACL quản lý là ngoại lệ tách biệt. Giữ Mach allowlist hiện có, bỏ `user-preference-read`.
- Nhóm riêng từng user tránh một khe hưởng group-read của khe khác. Nền OS đo máy B 24G90 ngày 19/10:
  `12 everyone`, `61 localaccounts`, `701 com.apple.sharepoint.group.1` (NestedGroups = everyone),
  `100 _lpoperator` (NestedGroups = localaccounts). Không gỡ theo user; bốn nhóm này được phép cùng nhóm riêng.
  `staff`, `admin` và mọi nhóm khác đều không được còn sau migration; nhóm lạ khiến preflight dừng trước đổi GID.
- Pin Python **3.12.15, build 20261009**: prefix nguồn cục bộ đã thấy có BUILD=20261009. SHA từng file được
  tính trên snapshot byte chuẩn bị cài, ghi manifest root và R2; đây là kiểm toàn vẹn bản cài, không phải chữ ký
  nhà phát hành. Không tải hoặc tự nhận nguồn không được người vận hành tin cậy.
- uv 0.13.0, git 2.56.0_1, node 26.5.0; phụ thuộc ở `toolchain.py` lấy từ INSTALL_RECEIPT.json trên máy này,
  đối chiếu `otool -L` ba executable. Chưa chứng minh mọi plugin/dlopen của công cụ chạy đủ dưới Seatbelt.
- Runtime kiểm không đọc nguồn Python ở nhà Đại ca; runtime quản lý vẫn dùng `.venv` của repo tin cậy. Không chuyển `.venv` cũ; dựng venv mới trong LUOT bằng Python mới.
- Không ghi/nhận việc Beads; không sửa sổ tay thật trong phiên review.

## Bảng G

| G | Bảo đảm bằng mã/test | Bằng chứng máy B vẫn cần |
|---|---|---|
| G1 | Nhóm có identity/R2, tạo trước user, giữ nhóm lạ | `id`, PrimaryGroupID, tiến trình mới không staff |
| G2 | Không còn allow đọc toàn cục, manifest phiên bản 2 | canary đường thật/symlink/firmlink, metadata/listing |
| G3 | PATH/Git/Python ghim ngoài nhà Đại ca | Python relocated + uv/git/node/npm và dự án thực dưới hồ sơ |
| G4 | Prefix root, manifest SHA từng file, lỗi đóng cổng | kiểm root chain/digest trên máy thật sau cài |
| G5 | copied launchctl + receipt/dọn exact labels | control ngoài hồ sơ, exec tới IPC, submit/bootstrap bị chặn |
| G6 | Canary chỉ báo boolean, có đối chứng DAC-readable | nhà Đại ca 750 + canary ngoài nhà, không đọc dữ liệu thật |
| G7 | D159 không bị nới | G3.12 và plan bộ chạy system riêng; nằm ngoài hai plan này |

## File Structure / thứ tự

Task 1 ghim policy/toolchain/env; Task 2 trình cài Python và kiểm toàn vẹn; Task 3 nhóm + migration;
những task G4 cuối bổ sung harness. Khi áp code có thể làm theo thứ tự task; **khi vận hành máy B:**
cài Python kiểm riêng → smoke relocation → Task 3A cấp ACL quản lý + ghim plist offline/no-sync có R2
→ tạo nhóm có sổ → audit quyền trước đổi GID → migration nhóm → hậu kiểm ACL/đường chạy + smoke quản lý
→ cài lại hồ sơ v2 → G4, không bật giao việc giữa chừng.
Cài Python riêng đi qua `python -m tram.chu.cai_python_kiem`, cùng sổ R2 của trình cài thợ, luôn in rồi chờ `dong-y`.
Không cần đưa source Python vào tài nguyên sau nhóm trong `cai_dat_tho`.

Plan D157 áp trước hoặc sau đều được: cùng chạm `cong_that.py` nhưng chỉ khác đoạn;
Task 2 của plan này thêm quan sát Python vào `dung_cong`, plan D157 đổi phép xác nhận UID.
Khi ghép phải giữ cả hai và chạy lại test; không lấy nguyên file cũ ghi đè.

## Môi trường kiểm chứng

```bash
export PYTHONPATH="$PWD"
export UV_CACHE_DIR=/tmp/siet-uv-cache
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1
```

Không đồng bộ/tải gói. Venv dùng chỉ đọc; PYTHONPATH buộc import worktree này thay checkout chính.
Mọi lệnh test bên dưới chạy sau khối trên. Không có bước commit trong phiên soạn hoặc thử plan.

## Task 1 — hồ sơ v2, toolchain ghim, môi trường lượt

**Files:** Create `tram/kiem/toolchain.py`, `tests/test_siet_doc_plan.py`;
Modify `tram/tho/quyen_kiem.py`, `tram/kiem/chay_lenh.py`, `tram/giao_viec/repo_ban_chep.py`,
`tram/giao_viec/kiem_lai.py`, `tram/giao_viec/principal_kiem.py`, `tests/test_chay_lenh.py`, `tests/test_ho_so_kiem_lai.py`.

**Interfaces:** `manifest() -> dict`, `quyen_doc() -> list[str]`, `bien_kiem(nha) -> dict`;
chữ ký các hàm cũ giữ nguyên. PATH/Python cố định được ghi sau `them`; bỏ PYTHONHOME/PYTHONPATH/VIRTUAL_ENV.
HOME/TMP của lượt lấy từ wt do trạm dựng, cache uv/npm ở NHA. Git archive phía trạm không đổi;
Git init/add/commit trong bản chép dùng executable đã ghim.

- [ ] **Step 1 — test nguyên văn:**
`tests/test_siet_doc_plan.py`

```python
from pathlib import Path
import json

from tram.tho.quyen_kiem import manifest_ho_so, ho_so_tu_manifest
from tram.kiem.chay_lenh import moi_truong_kiem
from tram.giao_viec.repo_ban_chep import lenh_repo


def test_ho_so_chi_doc_danh_sach(tmp_path):
    hs, raw = manifest_ho_so(tram_home_tram=tmp_path / 'tram', nha_quan_ly=Path('/Users/tram-tho'),
                            goc=tmp_path.resolve(), cong=[7710])
    text = hs.decode()
    assert '(allow file-read*)' not in text
    assert 'user-preference-read' not in text
    for p in ('/usr/local/tram/toolchains/python/3.12.15-20261009', '/opt/homebrew/Cellar/uv/0.13.0',
              '/opt/homebrew/Cellar/git/2.56.0_1', '/opt/homebrew/Cellar/node/26.5.0', '/System/Library'):
        assert f'(subpath "{p}")' in text
    for p in ('/Users', '/opt/homebrew', '/System', '/private', '/dev'):
        assert f'(allow file-read* (subpath "{p}"))' not in text
    m, same = ho_so_tu_manifest(raw)
    assert m['phien_ban'] == 2 and same == hs
    assert m['toolchain']['python'].startswith('/usr/local/tram/')
    bad = json.loads(raw)
    bad['toolchain']['python'] = '/Users/dai-ca/.local/python'
    import pytest
    with pytest.raises(ValueError):
        ho_so_tu_manifest(json.dumps(bad).encode())


def test_path_kiem_khong_ke_thua_nha():
    env = moi_truong_kiem({'PATH': '/Users/dai-ca/.local/bin', 'HOME': '/luot.nha'},
                         {'PATH': '/tmp/agent', 'UV_PYTHON': '/Users/dai-ca/python'})
    assert env['PATH'].startswith('/usr/local/tram/toolchains/python/')
    assert '/Users/' not in env['PATH']
    assert env['UV_PYTHON'].endswith('/bin/python3.12')
    assert env['UV_PYTHON_DOWNLOADS'] == 'never'
    assert env['UV_CACHE_DIR'] == '/luot.nha/.cache/uv'
    assert env['NPM_CONFIG_CACHE'] == '/luot.nha/.cache/npm'


def test_git_ban_chep_khong_tim_tren_path(monkeypatch, tmp_path):
    monkeypatch.setenv('PATH', '/tmp/agent')
    for argv in lenh_repo(tmp_path).values():
        assert '/opt/homebrew/Cellar/git/2.56.0_1/bin/git' in argv
        assert '/usr/bin/git' not in argv


def test_bien_toolchain_duoc_dat_sau_sudo(tmp_path):
    from tram.giao_viec.principal_kiem import tu_cach_ly
    argv = tu_cach_ly('user:tram-kiem').boc_luot(tmp_path)(['uv', 'run', 'python'])
    vi_tri = argv.index('/usr/bin/env')
    assert f'UV_CACHE_DIR={tmp_path}.nha/.cache/uv' in argv[vi_tri:]
    assert 'UV_PYTHON=/usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12' in argv[vi_tri:]
    assert any(x.startswith('PATH=/usr/local/tram/toolchains/python/') for x in argv[vi_tri:])


def test_runtime_system_paths_and_offline():
    from tram.kiem.toolchain import quyen_doc, bien_kiem
    text = '\n'.join(quyen_doc())
    assert '(subpath "/System/Volumes/Preboot/Cryptexes/OS/usr/lib")' in text
    assert '(subpath "/private/var/db/timezone")' in text
    assert '(regex #"^/dev/fd/[0-9]+$")' in text
    assert '(subpath "/dev")' not in text
    assert bien_kiem('/luot.nha')['UV_OFFLINE'] == '1'
```

- [ ] **Step 2 — chạy RED:** `tests/chan_host/chay.sh -q tests/test_siet_doc_plan.py`.
Bản soạn thiếu policy/PATH/Git/env; vòng review thêm ca timezone/dyld/dev-fd/offline.
Bằng chứng RED/GREEN đã đo trong mục kiểm chứng cuối; không suy test chuỗi thành Seatbelt đã chạy.

- [ ] **Step 3 — mã nguyên văn:**
`tram/kiem/toolchain.py`

```python
"""Toolchain kiểm ghim theo bản máy B; đổi pin phải cài lại hồ sơ/manifest và đo G4."""
from pathlib import Path

PYTHON = '/usr/local/tram/toolchains/python/3.12.15-20261009'
UV = '/opt/homebrew/Cellar/uv/0.13.0'
GIT = '/opt/homebrew/Cellar/git/2.56.0_1'
NODE = '/opt/homebrew/Cellar/node/26.5.0'
PHU_THUOC = (
    '/opt/homebrew/Cellar/pcre2/10.49',
    '/opt/homebrew/Cellar/json-c/0.19',
    '/opt/homebrew/Cellar/libunistring/1.4.2',
    '/opt/homebrew/Cellar/gettext/1.0',
    '/opt/homebrew/Cellar/fmt/12.2.0',
    '/opt/homebrew/Cellar/ada-url/3.4.4',
    '/opt/homebrew/Cellar/brotli/1.2.0',
    '/opt/homebrew/Cellar/c-ares/1.34.8',
    '/opt/homebrew/Cellar/hdrhistogram_c/0.11.10',
    '/opt/homebrew/Cellar/icu4c@78/78.3',
    '/opt/homebrew/Cellar/libffi/3.7.1',
    '/opt/homebrew/Cellar/libnghttp2/1.69.0',
    '/opt/homebrew/Cellar/libnghttp3/1.17.0',
    '/opt/homebrew/Cellar/ca-certificates/2026-07-16',
    '/opt/homebrew/Cellar/openssl@3/3.6.3',
    '/opt/homebrew/Cellar/libngtcp2/1.24.0',
    '/opt/homebrew/Cellar/libuv/1.52.1',
    '/opt/homebrew/Cellar/llhttp/9.4.2',
    '/opt/homebrew/Cellar/simdutf/9.0.0',
    '/opt/homebrew/Cellar/merve/1.2.2_1',
    '/opt/homebrew/Cellar/nbytes/0.1.4',
    '/opt/homebrew/Cellar/simdjson/4.6.4',
    '/opt/homebrew/Cellar/readline/8.3.3',
    '/opt/homebrew/Cellar/sqlite/3.53.3',
    '/opt/homebrew/Cellar/uvwasi/0.0.23',
    '/opt/homebrew/Cellar/lz4/1.10.0',
    '/opt/homebrew/Cellar/xz/5.8.3',
    '/opt/homebrew/Cellar/zstd/1.5.7_1',
)
PREFIX = (PYTHON, UV, GIT, NODE)
PATH_KIEM = ':'.join(f'{p}/bin' for p in PREFIX) + ':/usr/bin:/bin:/usr/sbin:/sbin'
HE_THONG = ('/bin', '/usr/bin', '/usr/lib', '/usr/libexec', '/usr/share', '/System/Library',
             '/System/Cryptexes/OS/usr/lib', '/System/Volumes/Preboot/Cryptexes/OS/usr/lib',
             '/System/Cryptexes/OS/System/Library/dyld',
             '/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld', '/private/var/db/timezone')
LITERAL = ('/dev/null', '/dev/zero', '/dev/random', '/dev/urandom', '/private/etc/localtime',
           '/dev/fd')


def manifest() -> dict:
    return {'python': PYTHON, 'prefix': list((*PREFIX, *PHU_THUOC)),
            'he_thong': list(HE_THONG), 'literal': list(LITERAL)}


def quyen_doc() -> list[str]:
    link = [f'/opt/homebrew/opt/{Path(p).parent.name}' for p in (*PREFIX[1:], *PHU_THUOC)]
    cha = sorted({str(q) for p in (*PREFIX, *PHU_THUOC, *HE_THONG, *LITERAL, *link) for q in Path(p).parents}
                 | set(link))
    return [*(f'(allow file-read* (subpath "{p}"))' for p in (*PREFIX, *PHU_THUOC, *HE_THONG)),
            *(f'(allow file-read* (literal "{p}"))' for p in LITERAL),
            '(allow file-read* (regex #"^/dev/fd/[0-9]+$"))',
            *(f'(allow file-read-metadata (literal "{p}"))' for p in cha)]


def bien_kiem(nha: str) -> dict[str, str]:
    return {'PATH': PATH_KIEM, 'UV_PYTHON': f'{PYTHON}/bin/python3.12', 'UV_PYTHON_DOWNLOADS': 'never',
            'UV_OFFLINE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
            'UV_CACHE_DIR': f'{nha}/.cache/uv', 'UV_TOOL_DIR': f'{nha}/.local/uv',
            'XDG_CONFIG_HOME': f'{nha}/.config', 'XDG_CACHE_HOME': f'{nha}/.cache',
            'NPM_CONFIG_CACHE': f'{nha}/.cache/npm', 'NPM_CONFIG_USERCONFIG': f'{nha}/.npmrc'}
```

```diff
diff --git a/tram/tho/quyen_kiem.py b/tram/tho/quyen_kiem.py
index f0fd9e0..17775cf 100644
--- a/tram/tho/quyen_kiem.py
+++ b/tram/tho/quyen_kiem.py
@@ -23,2 +23,3 @@ from tram.tho.principal import SANDBOX_EXEC, USER_RE
 from tram.tho.sandbox import _p
+from tram.kiem.toolchain import manifest, quyen_doc

@@ -27,4 +28,4 @@ HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"
 MANIFEST_KIEM = THU_MUC_CAI / "tram-kiem.sb.json"      # root:wheel 0644, cùng sổ cài với hồ sơ (V2-5)
-PHIEN_BAN_HO_SO = 1                                   # TĂNG khi chữ của `ho_so_tram_kiem` đổi → bản cài cũ đóng cổng
-KHOA_MANIFEST = ("cong", "goc", "nha_quan_ly", "phien_ban", "sha256", "tram_home")
+PHIEN_BAN_HO_SO = 2                                   # TĂNG khi chữ của `ho_so_tram_kiem` đổi → bản cài cũ đóng cổng
+KHOA_MANIFEST = ("cong", "goc", "nha_quan_ly", "phien_ban", "sha256", "toolchain", "tram_home")
 LICH = ("/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/usr/bin/atq", "/usr/bin/atrm", "/bin/launchctl",
@@ -60,3 +61,3 @@ def dong_sudoers_kiem(*, tram: str, tram_kiem: str, co_che: str) -> str:
 def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> str:
-    """Hồ sơ Seatbelt của lượt kiểm (3C-D1): cấm mặc định. Đọc mọi nơi TRỪ kho trạm/quản lý và `goc` chung (chỉ đọc lại
+    """Hồ sơ Seatbelt của lượt kiểm (3C-D1): cấm mặc định. Chỉ đọc toolchain ghim, hệ thống cần thiết và
     `LUOT`, `NHA` của lượt); ghi CHỈ `LUOT`, `NHA`; không mạng (chỉ unix socket trong `LUOT`) — DB/Redis/dịch vụ dùng
@@ -68,4 +69,4 @@ def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong:
     dong = ["(version 1)", "(deny default)", "(allow process-fork)", "(allow process-exec)", "(allow signal)",
-            "(allow process-info*)", "(allow sysctl-read)", "(allow user-preference-read)", "(allow system-socket)",
-            "(allow file-read*)", f"(deny file-read* {cam})", f'(deny file-read* (subpath "{g}"))',
+            "(allow process-info*)", "(allow sysctl-read)", "(allow system-socket)",
+            *quyen_doc(), f"(deny file-read* {cam})", f'(deny file-read* (subpath "{g}"))',
             f'(allow file-read-metadata (literal "{g}"))', f"(allow file-read* {luot})", f"(allow file-write* {luot})",
@@ -82,3 +83,4 @@ def manifest_ho_so(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong:
     m = {"cong": [int(c) for c in cong], "goc": goc_hop_le(goc), "nha_quan_ly": str(nha_quan_ly),
-         "phien_ban": PHIEN_BAN_HO_SO, "sha256": hashlib.sha256(hs).hexdigest(), "tram_home": str(tram_home_tram)}
+         "phien_ban": PHIEN_BAN_HO_SO, "sha256": hashlib.sha256(hs).hexdigest(),
+         "tram_home": str(tram_home_tram), "toolchain": manifest()}
     return hs, (json.dumps(m, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode()
@@ -103,2 +105,4 @@ def ho_so_tu_manifest(du_lieu: bytes) -> tuple[dict, bytes]:
             raise ValueError
+        if m["toolchain"] != manifest():
+            raise ValueError
         if m["phien_ban"] != PHIEN_BAN_HO_SO or not re.fullmatch(rf"/Users/{USER_RE.pattern}", m["nha_quan_ly"]):
```

```diff
diff --git a/tram/kiem/chay_lenh.py b/tram/kiem/chay_lenh.py
index 46d093b..0534f45 100644
--- a/tram/kiem/chay_lenh.py
+++ b/tram/kiem/chay_lenh.py
@@ -14,2 +14,3 @@ from pathlib import Path
 from tram.kiem.so_huu import so_huu
+from tram.kiem.toolchain import bien_kiem
 from tram.kiem.vong_doi import khoi_chay
@@ -41,2 +42,5 @@ def moi_truong_kiem(goc: Mapping[str, str], them: Mapping[str, str] | None = Non
     env.update(them or {})
+    for k in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
+        env.pop(k, None)
+    env.update(bien_kiem(env.get("HOME", "/var/empty")))
     return env
```

```diff
diff --git a/tram/giao_viec/repo_ban_chep.py b/tram/giao_viec/repo_ban_chep.py
index b9271f6..b0aaac4 100644
--- a/tram/giao_viec/repo_ban_chep.py
+++ b/tram/giao_viec/repo_ban_chep.py
@@ -10,5 +10,5 @@ không chạy filter. `.git` trong commit: `git archive` của trạm từ chố
 import secrets
-import shutil
+from tram.kiem.toolchain import GIT, PATH_KIEM

-MOI_TRUONG = ("/usr/bin/env", "-i", "PATH=/usr/bin:/bin:/usr/sbin:/sbin", "HOME=/var/empty", "LC_ALL=C",
+MOI_TRUONG = ("/usr/bin/env", "-i", f"PATH={PATH_KIEM}", "HOME=/var/empty", "LC_ALL=C",
               "GIT_CONFIG_NOSYSTEM=1", "GIT_CONFIG_GLOBAL=/dev/null", "GIT_ATTR_NOSYSTEM=1")
@@ -20,3 +20,3 @@ CAU_HINH = ("core.hooksPath=/dev/null", "core.attributesFile=/dev/null", "core.f
 def _git(wt) -> list[str]:
-    git = [*MOI_TRUONG, shutil.which("git") or "/usr/bin/git"]
+    git = [*MOI_TRUONG, f"{GIT}/bin/git"]
     for c in CAU_HINH:
```

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index dc3ddbe..f19eb3a 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -97,3 +97,3 @@ def _tren_ban_chep(kho_git: Path, commit: str, mt, wt: Path, *, giao_id: str, le
             return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
-        env, ket_qua = moi_truong_kiem(env_goc), []
+        env, ket_qua = moi_truong_kiem(env_goc, {"HOME": f"{wt}.nha", "TMPDIR": f"{wt}.nha/tmp"}), []
         for i, lenh in enumerate(lenh_kiem, 1):
```

```diff
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index b984988..691eaa3 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -13,2 +13,3 @@ from pathlib import Path
 from tram.kiem.lenh_ngan import chay_ngan
+from tram.kiem.toolchain import bien_kiem
 from tram.tho.principal import SANDBOX_EXEC, doc_principal
@@ -38,2 +39,3 @@ class PrincipalKiem:
         dau = [*self.boc, *ho_so, "-D", f"LUOT={wt}", "-D", f"NHA={nha}", ENV, f"HOME={nha}", f"TMPDIR={nha}/tmp/"]
+        dau += [f"{k}={v}" for k, v in bien_kiem(nha).items()]
         return lambda argv: [*dau, *argv]
```

```diff
diff --git a/tests/test_chay_lenh.py b/tests/test_chay_lenh.py
index c98dac0..4f5f4cc 100644
--- a/tests/test_chay_lenh.py
+++ b/tests/test_chay_lenh.py
@@ -76,3 +76,4 @@ def test_moi_truong_toi_thieu_va_boc_principal(tmp_path):
                           {"X": "1"})
-    assert env == {"PATH": "/usr/bin", "HOME": "/h", "APP_ENV": "testing", "GIT_CONFIG_COUNT": "1",
+    from tram.kiem.toolchain import bien_kiem
+    assert env == {**bien_kiem("/h"), "HOME": "/h", "APP_ENV": "testing", "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": "/dev/null", "X": "1"}
```

```diff
diff --git a/tests/test_ho_so_kiem_lai.py b/tests/test_ho_so_kiem_lai.py
index 8d6c850..69ef466 100644
--- a/tests/test_ho_so_kiem_lai.py
+++ b/tests/test_ho_so_kiem_lai.py
@@ -8,2 +8,3 @@ from pathlib import Path
 from tram.giao_viec.principal_kiem import tu_cach_ly
+from tram.kiem.toolchain import bien_kiem
 from tram.tho.principal import SANDBOX_EXEC
@@ -52,3 +53,4 @@ def test_boc_luot_user_boc_moi_lenh_trong_ho_so_co_tham_so_va_nha_cua_luot():
     assert a[n + 3:] == ["-D", f"LUOT={WT}", "-D", f"NHA={WT}.nha", "/usr/bin/env", f"HOME={WT}.nha",
-                         f"TMPDIR={WT}.nha/tmp/", "/bin/rm", "-rf", str(WT)]
+                         f"TMPDIR={WT}.nha/tmp/", *[f"{k}={v}" for k, v in bien_kiem(f"{WT}.nha").items()],
+                         "/bin/rm", "-rf", str(WT)]
     assert pk.boc_lenh(["/bin/kill"]) == [*pk.boc, "/bin/kill"]
@@ -61,3 +63,5 @@ def test_boc_luot_sandbox_khong_long_hai_lan_va_khop_sudoers():
         assert a.count(SANDBOX_EXEC) == 1 and fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau)
-    assert pk.boc_luot(WT)(["x"])[-6:-3] == ["-D", f"NHA={WT}.nha", "/usr/bin/env"]
+    argv = pk.boc_luot(WT)(["x"])
+    i = argv.index("/usr/bin/env")
+    assert argv[i - 2:i + 1] == ["-D", f"NHA={WT}.nha", "/usr/bin/env"]
     assert pk.boc_lenh(["x"])[-5:] == ["-D", "LUOT=/var/empty", "-D", "NHA=/var/empty", "x"]  # hồ sơ ghim cần tham số
```

- [ ] **Step 4 — GREEN:**

```bash
tests/chan_host/chay.sh -q tests/test_siet_doc_plan.py tests/test_quyen_kiem.py
```

Số đo hiện hành ở mục kiểm chứng cuối; chưa chứng nhận OS.
Test môi trường cũ đổi expected theo hợp đồng PATH mới; các test thực thi tiến trình còn lỗi sandbox,
không bỏ kiểm thu hồi để ép xanh.

## Task 2 — cài toàn prefix Python có sổ + xác minh trước/sau lượt

**Files:** Create `tram/chu/python_kiem.py`, `tram/chu/cai_python_kiem.py`, `tram/kiem/kiem_python.py`,
`tests/test_siet_python_plan.py`; Modify `tram/giao_viec/cong_that.py`.

**Interfaces:** `phan_python(nguon, soan) -> (tep, tai_nguyen)` chụp byte trước duyệt;
`lap(nguon, so) -> KeHoach`, `kiem_prefix() -> None`, lỗi → cổng đóng.
Mỗi thư mục/file là tài nguyên R2; symlink file chỉ được dereference khi đích bên trong prefix;
symlink thư mục hoặc đích ngoài đều từ chối. `install` root:wheel 0755/0644; không chạy interpreter nguồn lúc lập plan.
Manifest và file cài đều có SHA trong sổ; cài lỗi giữa chừng giữ receipt để thử lại/gỡ.
`go-cai-dat-tho` gỡ file theo SHA và thư mục bằng rmdir; nếu cha được thử trước con, chạy lại để gỡ cha rỗng.
Không xoá prefix bằng rm -rf và không nhận cây có sẵn không có biên nhận.

- [ ] **Step 1 — test nguyên văn:**
`tests/test_siet_python_plan.py`

```python
import hashlib
import json
from pathlib import Path
import pytest


def nguon(tmp_path):
    src = tmp_path / 'python'
    (src / 'bin').mkdir(parents=True)
    (src / 'lib/python3.12').mkdir(parents=True)
    (src / 'BUILD').write_text('20261009')
    (src / 'bin/python3.12').write_bytes(b'python-gia')
    (src / 'bin/python').symlink_to('python3.12')
    (src / 'lib/python3.12/os.py').write_bytes(b'pass\n')
    return src


def test_prefix_day_du_manifest_sha_va_root(tmp_path):
    from tram.chu.python_kiem import phan_python
    tep, ds = phan_python(nguon(tmp_path), tmp_path / 'soan')
    dich = '/usr/local/tram/toolchains/python/3.12.15-20261009'
    assert any(t.ten == dich + '/lib/python3.12/os.py' for t in ds)
    assert any(t.ten == dich + '/bin/python' for t in ds)
    mf = json.loads(next(b for p, b in tep.items() if p.name == 'python-manifest.json'))
    assert mf['phien_ban'] == '3.12.15-20261009'
    assert mf['tep']['lib/python3.12/os.py']['sha256'] == hashlib.sha256(b'pass\n').hexdigest()
    for t in ds:
        for c in t.lenh('id'):
            assert c[:2] == ['sudo', 'install']
            assert c[c.index('-o') + 1] == 'root' and c[c.index('-g') + 1] == 'wheel'
    assert mf['tep']['bin/python']['sha256'] == mf['tep']['bin/python3.12']['sha256']


def test_khong_chep_symlink_ra_nha_nguoi_khac(tmp_path):
    from tram.chu.python_kiem import phan_python
    src = nguon(tmp_path)
    (src / 'lib/ngoai').symlink_to('/etc/passwd')
    with pytest.raises(ValueError, match='ngoài prefix'):
        phan_python(src, tmp_path / 'soan')


def test_build_khac_khong_cai(tmp_path):
    from tram.chu.python_kiem import phan_python
    src = nguon(tmp_path)
    (src / 'BUILD').write_text('khac')
    with pytest.raises(ValueError, match='build'):
        phan_python(src, tmp_path / 'soan')


def test_kiem_prefix_hash_va_quyen(tmp_path):
    from tram.chu.python_kiem import phan_python
    from tram.kiem.kiem_python import kiem_prefix
    tep, ds = phan_python(nguon(tmp_path), tmp_path / 'soan')
    root = tmp_path / 'root'
    root.mkdir()
    source = tmp_path / 'soan/python'
    for p, data in tep.items():
        rel = p.relative_to(source) if p.is_relative_to(source) else Path('manifest.json')
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(0o644)
    import os
    kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
    (root / 'lib/python3.12/os.py').write_bytes(b'bi sua')
    with pytest.raises(ValueError, match='digest'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
    (root / 'lib/python3.12/os.py').unlink()
    (root / 'lib/python3.12/os.py').symlink_to('/etc/passwd')
    with pytest.raises(ValueError, match='chủ/quyền/loại'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)


def test_cong_luot_kiem_python_truoc_tien_trinh(monkeypatch, tmp_path):
    from tram.giao_viec import cong_that
    from tram.kiem.kiem_python import kiem_prefix
    seen = {}
    monkeypatch.setattr(cong_that, 'CongLuot', lambda *a, **kw: seen.update(kw))
    cong_that.dung_cong(type('PK', (), {'ten': 'tram-kiem'})(), tmp_path, cac_du_an=lambda: [])
    assert seen['quan_sat'][0] is kiem_prefix


def test_prefix_khong_co_thu_muc_rong_ghi_duoc(tmp_path):
    import os
    from tram.chu.python_kiem import phan_python
    from tram.kiem.kiem_python import kiem_prefix
    tep, _ = phan_python(nguon(tmp_path), tmp_path / 'soan')
    root, source = tmp_path / 'root', tmp_path / 'soan/python'
    for p, data in tep.items():
        rel = p.relative_to(source) if p.is_relative_to(source) else Path('manifest.json')
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(0o644)
    (root / 'chen').mkdir()
    (root / 'chen').chmod(0o777)
    with pytest.raises(ValueError, match='chủ/quyền/loại'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
```

- [ ] **Step 2 — chạy RED:** `tests/chan_host/chay.sh -q tests/test_siet_python_plan.py`.
Trước áp mã: `ModuleNotFoundError` cho installer/validator. Xem số đo vòng review ở cuối.

- [ ] **Step 3 — mã nguyên văn:**
`tram/chu/python_kiem.py`

```python
"""Soạn toàn prefix Python offline; mỗi file có SHA và tài nguyên R2 riêng, không chạy nguồn."""
import hashlib
import json
from pathlib import Path

from tram.chu.cai_dat_kiem import tep_root
from tram.chu.tai_nguyen import TaiNguyen
from tram.kiem.toolchain import PYTHON

BAN = '3.12.15-20261009'


def phan_python(nguon: Path, soan: Path) -> tuple[dict, list]:
    nguon = nguon.resolve(strict=True)
    if (nguon / 'BUILD').read_text().strip() != '20261009' or not (nguon / 'bin/python3.12').is_file():
        raise ValueError('Python khác build đã ghim — không cài')
    tep, ds, muc = {}, [], {}
    dich = Path(PYTHON)
    thu_muc = {dich, *[p for p in dich.parents if str(p).startswith('/usr/local/tram')]}
    for p in sorted(nguon.rglob('*')):
        that = p.resolve(strict=True)
        if not that.is_relative_to(nguon):
            raise ValueError('symlink ra ngoài prefix — không cài')
        if p.is_dir():
            if p.is_symlink():
                raise ValueError('symlink thư mục chưa hỗ trợ — không cài')
            thu_muc.add(dich / p.relative_to(nguon))
            continue
        if not p.is_file():
            raise ValueError('prefix chứa tài nguyên không phải file — không cài')
        ten = p.relative_to(nguon).as_posix()
        data = p.read_bytes()
        if data.startswith(b'#!'):
            data = data.replace(str(nguon).encode(), PYTHON.encode())
        mode = '0755' if p.stat().st_mode & 0o111 else '0644'
        muc[ten] = {'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode}
        tam = soan / 'python' / ten
        tep[tam] = data
        ds.append(tep_root(tam, dich / ten, data, mode))
    mf = (json.dumps({'phien_ban': BAN, 'tep': muc}, sort_keys=True, indent=1) + '\n').encode()
    tam = soan / 'python-manifest.json'
    tep[tam] = mf
    ds.append(tep_root(tam, dich / 'manifest.json', mf, '0644'))
    dirs = [TaiNguyen('thu_muc', str(p), lambda i, p=p: [
        ['sudo', 'install', '-d', '-o', 'root', '-g', 'wheel', '-m', '0755', str(p)]], lambda i: {'uid': 0})
        for p in sorted(thu_muc, key=lambda p: (len(p.parts), str(p)))]
    return tep, dirs + ds
```

`tram/chu/cai_python_kiem.py`

```python
"""Trình cài Python kiểm riêng, offline, dùng cùng sổ R2; luôn in rồi chờ dong-y."""
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.cai_dat import KeHoach, in_ke_hoach, thuc_hien
from tram.chu.python_kiem import phan_python
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao
from tram.duong_dan import tram_home


def lap(nguon: Path, so: SoCai, *, quan_sat=dinh_danh.quan_sat_that) -> KeHoach:
    tep, ds = phan_python(nguon, tram_home() / 'cai-dat-tho/python-soan')
    viec = kiem_truoc(so, ds, quan_sat=quan_sat)
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    buoc += [(f'[{v}] {t.kieu} {t.ten}: {t.mo_ta()}', lambda t=t: tao(so, t, quan_sat=quan_sat))
             for t, v in zip(ds, viec)]
    return KeHoach(tep, [], ['Chưa đổi nhóm: chạy smoke Python và đối chiếu manifest trước khi đổi nhóm.'], buoc)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nguon', type=Path)
    args = parser.parse_args()
    so = SoCai()
    try:
        with so.giu():
            kh = lap(args.nguon, so)
            print(in_ke_hoach(kh))
            if input('Gõ dong-y để cài Python kiểm: ').strip() != 'dong-y':
                return 1
            thuc_hien(kh)
    except (OSError, ValueError, RuntimeError) as e:
        print(f'Không cài Python kiểm: {type(e).__name__}; sổ R2 giữ phần đã tạo.')
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

`tram/kiem/kiem_python.py`

```python
"""Kiểm toàn prefix Python root giữ, so digest trước cổng; không thực thi file đang kiểm."""
import hashlib
import json
import os
import stat
from pathlib import Path

from tram.kiem.toolchain import PYTHON


def _an_toan(p: Path, chu: int, thu_muc: bool = False) -> None:
    st = p.lstat()
    dung = stat.S_ISDIR(st.st_mode) if thu_muc else stat.S_ISREG(st.st_mode)
    if not dung or st.st_uid != chu or st.st_mode & 0o022:
        raise ValueError('Python kiểm sai chủ/quyền/loại — cài lại')


def kiem_prefix(goc: Path = Path(PYTHON), *, chu: int = 0, kiem_cha: bool = True) -> None:
    for p in (goc, *(goc.parents if kiem_cha else ())):
        _an_toan(p, chu, True)
    mf = goc / 'manifest.json'
    _an_toan(mf, chu)
    if mf.stat().st_size > 4_000_000:
        raise ValueError('manifest Python quá lớn')
    m = json.loads(mf.read_bytes())
    if set(m) != {'phien_ban', 'tep'} or m['phien_ban'] != '3.12.15-20261009' or not isinstance(m['tep'], dict):
        raise ValueError('manifest Python khác bản ghim')
    if not {'bin/python3.12', 'bin/python', 'lib/python3.12/os.py'}.issubset(m['tep']):
        raise ValueError('manifest Python thiếu prefix đầy đủ')
    for ten, expected in m['tep'].items():
        rel = Path(ten)
        if rel.is_absolute() or '..' in rel.parts or str(rel) != ten:
            raise ValueError('manifest Python sai đường')
        p = goc / rel
        for cha in p.parents:
            if cha == goc:
                break
            _an_toan(cha, chu, True)
        _an_toan(p, chu)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as f:
            st = os.fstat(f.fileno())
            if st.st_uid != chu or st.st_mode & 0o022 or not stat.S_ISREG(st.st_mode):
                raise ValueError('Python kiểm đổi định danh')
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        if digest != expected['sha256']:
            raise ValueError('Python kiểm sai digest — cài lại')
    thuc = set()
    for p in goc.rglob('*'):
        _an_toan(p, chu, p.is_dir())
        if not p.is_dir():
            thuc.add(p.relative_to(goc).as_posix())
    if thuc != set(m['tep']) | {'manifest.json'}:
        raise ValueError('Python kiểm có file ngoài manifest — cài lại')
```

```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index 1b50cf7..c87d241 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -27,2 +27,3 @@ from tram.kiem.cay_tien_trinh import chup_he
 from tram.kiem.danh_tinh import LoiDanhTinh
+from tram.kiem.kiem_python import kiem_prefix
 from tram.kiem.vong_doi import LoiThuHoi
@@ -108,3 +109,4 @@ def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
     return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
-                    quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
+                    quan_sat=[kiem_prefix, partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc),
+                              partial(goc_rong, goc),
                               partial(cron_at, pk), partial(ho_so_cai, goc), partial(env_kin, cac_du_an),
```

- [ ] **Step 4 — GREEN và kiểm cấu trúc:**

```bash
tests/chan_host/chay.sh -q tests/test_siet_doc_plan.py tests/test_siet_python_plan.py tests/test_manifest_ho_so.py tests/test_ho_so_kiem_lai.py tests/test_quyen_kiem.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

Số đo hiện hành ở mục kiểm chứng cuối; unit/contract không thay chạy toolchain trong Seatbelt.

- [ ] **Step 5 — nghiệm thu cài thực (Đại ca chạy sau duyệt, chưa chạy trong phiên này):**

```bash
UV_NO_SYNC=1 uv run --offline python -m tram.chu.cai_python_kiem /Users/dai-ca/.local/share/uv/python/cpython-3.12.15-macos-aarch64-none
/usr/bin/env -i HOME=/var/empty PATH=/usr/bin:/bin /usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12 -I -B -c 'import sys,sysconfig,ssl,sqlite3,ctypes,venv; assert sysconfig.get_path("stdlib").startswith(sys.prefix); assert sys.version_info[:3] == (3,12,15); assert sys.prefix == "/usr/local/tram/toolchains/python/3.12.15-20261009"; print("python-prefix: dat")'
UV_NO_SYNC=1 uv run --offline python -c 'from tram.kiem.kiem_python import kiem_prefix; kiem_prefix(); print("manifest: dat")'
```

Trước smoke giữ nguồn giao việc tắt. Không dùng `/usr/bin/env -i` để suy đã có Seatbelt: đây chỉ kiểm relocation.
Sau có principal, G4 tạo LUOT/NHA mới rồi dùng chính `boc_luot`: Python `-m venv --without-pip` vào LUOT,
kiểm `sys.base_prefix` bằng prefix ghim; uv/git/node/npm chạy trong cùng wrapper. Dự án cần dependency
phải mang artifact offline vào LUOT theo quy trình dự án; không mở cache nhà Đại ca khi uv thiếu gói.
Prefix root không được ghi pyc; chạy smoke `-B`, ghi cache/venv ở LUOT/NHA.
Nếu relocate/dlopen/SDK/config thiếu: giữ cổng đóng, ghi đúng literal/prefix thực từ số đo rồi review lại policy;
không mở cả thư mục lớn hoặc đổi Mach allowlist theo đoán.

### Quyết định vòng 2 về cài prefix theo lô

**Không nhận nguyên đề xuất 2; giữ Task 2 hiện tại.** Số 2.067 mục R2 là chi phí có thật,
nhưng một bản ghi thư mục + SHA của tệp manifest chưa thay được các điều kiện sở hữu/phục hồi:

- SHA manifest còn nguyên trong khi `lib/python3.12/os.py` bị sửa hoặc có file lạ: không được rm-rf.
  Phải so lại toàn cây, loại/mode/owner, không theo symlink và kiểm inode/device đích trước gỡ.
- `ditto`/`cp -Rp` lỗi hoặc mất điện trước rename để lại `.tmp` chưa đủ manifest. Không được nhận cây
  tạm có sẵn hay xóa nó bằng digest của cây hoàn chỉnh. Cần biên nhận sở hữu cây tạm từ trước copy.
- `mv source existing-directory` có thể lồng source vào đích thay vì publish đúng prefix; `mv -f`
  có thể đè tài nguyên lạ. Cần đích mới độc quyền, cha root không ghi được bởi principal, cùng filesystem,
  khóa cài/gỡ; chown/chmod và kiểm toàn cây **trước** publish, không làm sau mv như đề xuất.
- Chép giữ ACL bằng `ditto`/`cp -Rp` rồi `chmod go-w` chưa loại quyền write trong ACL; nguồn phải bỏ
  ACL/xattr không cần thiết, kiểm link/hardlink và quyền cây thực trước khi nhận là root-only.

Các điểm này sửa được, nhưng cần một giao dịch cây mới và test crash/retry/gỡ; không thể chỉ đổi
vài argv của R2 đang có mà giữ bảo đảm. Trong vòng này giữ installer từng file đã có mã/test đầy đủ,
không thêm một thiết kế theo lô chưa triển khai. Đây là **NÊN tối ưu**, không phải CHẶN của phương án
được giữ. Nếu Đại ca ưu tiên bắt buộc ít sudo ngay, cần mở lại Task 2 với giao dịch cây đầy đủ trước
triển khai; không chạy chuỗi ditto/mv/rm-rf thô. Không khẳng định đã đo thời gian hay số lần hỏi mật khẩu.

## Task 3 — nhóm riêng — phụ thuộc cài và smoke-test Python mới ĐẠT trước khi đổi nhóm

Nguồn: D159; vòng 2 §2. Không đổi UID/GUID của user đang có. Nhóm riêng cùng tên mỗi principal
(`tram-kiem`, `tram-khe1`, `tram-tho`; installer áp cùng quy tắc cho user đã cấu hình).
Nhóm được tạo trước `sysadminctl -addUser -GID`; sau đó siết PrimaryGroupID và bỏ đúng membership thừa nếu có.
Không bỏ bốn nhóm nền `everyone`, `localaccounts`, `com.apple.sharepoint.group.1`, `_lpoperator`.
Chỉ sharepoint `.1` đo qua nhóm lồng được giữ; sharepoint khác vẫn phải gỡ. `admin`/nhóm lạ không tự gỡ,
phải dừng xử lý riêng trước migration; hậu kiểm không chấp nhận bất kỳ nhóm nào ngoài nền và nhóm riêng.
Nhóm là tài nguyên R2 riêng: `du_dinh` fsync trước tạo;
RealName chứa id biên nhận, sau quan sát ghi GID + GeneratedUID; cài lại chỉ giữ cùng định danh;
gỡ user trước nhóm, user chưa gỡ được thì giữ nhóm. Không nhận nhóm có sẵn không được sổ chứng minh.

**Ghép với task Python:** chạy trình cài Python độc lập và smoke gate và chuẩn bị ACL/đường chạy quản lý ở Task 3A ĐẠT trước khi chạy task nhóm; KHÔNG đổi nhóm nếu gate chưa đạt.
`<gid:USER>` trong bản in trước tạo là kết quả quan sát sau khi dseditgroup tạo nhóm; không phải số GID đoán cứng.
Migration bên dưới in lại số thật và chờ `dong-y` trước đổi PrimaryGroupID. S6 vẫn đóng.

### Files

- Tạo `tram/chu/nhom_rieng.py`, `tests/test_nhom_rieng.py`.
- Sửa `tram/chu/cai_dat_tho.py`, `tram/chu/dinh_danh.py`, `tram/chu/so_cai_tho.py`, `tram/chu/go_cai_dat_tho.py`.
- Cập nhật fixture `tests/he_gia.py`, `tests/test_cai_dat_tho_kiem.py`, `tests/test_go_cai_dat_tho.py`.
- Tạo `scripts/siet_nhom_ownership.py`, `tests/test_siet_nhom_migration.py` cho migration có audit/snapshot.

### Steps

- [ ] Xác nhận trình cài Python độc lập và smoke gate đã đạt; S6 đóng, nguồn giao việc dừng.
- [ ] Thêm test nhóm, chạy RED bằng bộ chặn; ghi lỗi thật.
- [ ] Thêm mã nhóm/R2 và cập nhật fixture; chạy GREEN nhóm + regression cài/gỡ.
- [ ] Thêm test migration trước script, chạy RED; thêm script rồi chạy GREEN.
- [ ] Đọc kế hoạch lệnh máy B và các điều kiện dừng; Đại ca duyệt kịch bản riêng trước chạy thật.
- [ ] Tạo nhóm có sổ, audit ownership trước đổi GID, rồi migration danh tính có snapshot/chờ dong-y.
- [ ] Kiểm nhóm tiến trình mới, test -x nhà Đại ca, smoke toolchain/config và canary Seatbelt; ghi kết quả.
- [ ] Nếu cần rollback: dùng snapshot, kiểm định danh, in lệnh/chờ dong-y; giữ S6 đóng.

### RED → GREEN
Chạy `tests/chan_host/chay.sh -q tests/test_nhom_rieng.py tests/test_siet_nhom_migration.py`.
Bản cũ chưa có nhóm/R2; vòng review bắt thêm sharepoint ngoài nền OS, nhóm lạ, cài lại tự migration,
audit bỏ qua lỗi đọc cây, và daemon còn dùng repo trong nhà operator. Số đo thật ở cuối.

### Test nguyên văn (thêm mới)

`tests/test_nhom_rieng.py`

```python
from types import SimpleNamespace
import pytest
from tram.chu import dinh_danh
from tram.chu.so_cai_tho import SoCai, Muc
from tram.chu.tai_nguyen import tao, kiem_truoc, LoiCaiDat
from tram.chu.go_cai_dat_tho import go, _thu_tu, lenh_go


def test_doc_nhom_va_danh_tinh():
    seen = []
    def run(cmd, **kw):
        seen.append(cmd)
        return SimpleNamespace(returncode=0, stdout='PrimaryGroupID: 701\nGeneratedUID: G\nRealName: tram g i\n')
    result = dinh_danh.nhom('tram-kiem', chay=run)
    assert result == {'gid': 701, 'guid': 'G', 'ten_day_du': 'tram g i'}
    assert seen[0][3] == '/Groups/tram-kiem'
    assert dinh_danh.khop('nhom', result, result)
    assert dinh_danh.cung('nhom', result, result)
    assert not dinh_danh.cung('nhom', result, {**result, 'guid': 'foreign'})


def test_nhom_co_so_cai_va_cai_lai(tmp_path):
    from tram.chu.nhom_rieng import nhom_tram
    so, state, calls = SoCai(tmp_path / 'so'), {}, []
    def observe(k, n, **kw):
        return state.get((k, n))
    def run(cmd, **kw):
        calls.append(cmd)
        marker = cmd[cmd.index('-r') + 1]
        state['nhom', 'tram-kiem'] = {'gid': 701, 'guid': 'G', 'ten_day_du': marker}
    tn = nhom_tram('tram-kiem')
    assert tao(so, tn, quan_sat=observe, chay=run) == 'tao'
    assert tao(so, tn, quan_sat=observe, chay=run) == 'giu'
    assert len(calls) == 1
    assert so.da_tao('nhom', 'tram-kiem')[0].dinh_danh['gid'] == 701
    state['nhom', 'tram-kiem']['guid'] = 'foreign'
    with pytest.raises(LoiCaiDat):
        tao(so, tn, quan_sat=observe, chay=run)
    assert len(calls) == 1


def test_go_nhom_sau_user_khong_go_nhom_la(tmp_path):
    so = SoCai(tmp_path / 'so')
    identity = {'gid': 701, 'guid': 'G'}
    so.du_dinh('i', 'nhom', 'tram-kiem', {'user': 'tram-kiem'})
    so.ket('i', 'da_tao', dinh_danh=identity)
    m = so.da_tao('nhom', 'tram-kiem')[0]
    assert _thu_tu(m) > _thu_tu(Muc('u', 'user', 'tram-kiem', {}))
    calls = []
    assert not go(so, m, quan_sat=lambda k,n: identity, chay=lambda *a,**k: calls.append(a), bao=lambda s: None)
    assert not calls
    assert not go(so, m, quan_sat=lambda k,n: {**identity, 'guid': 'foreign'},
                  chay=lambda *a,**k: calls.append(a), bao=lambda s: None)
    assert not calls
    assert lenh_go(m) == [['sudo', '/usr/sbin/dseditgroup', '-o', 'delete', 'tram-kiem']]


def test_user_gid_va_bo_nhom_thua(tmp_path):
    from tram.chu.nhom_rieng import user_nhom
    so = SoCai(tmp_path / 'so')
    identity = {'gid': 701, 'guid': 'G'}
    so.du_dinh('i', 'nhom', 'tram-kiem', {'user': 'tram-kiem'})
    so.ket('i', 'da_tao', dinh_danh=identity)
    tn = user_nhom('tram-kiem', '/Users/Shared/tram-kiem', so, lambda k,n,**kw: identity)
    cmds = tn.lenh('new')
    assert cmds[0][cmds[0].index('-GID') + 1] == '701'
    assert len(cmds) == 1  # Không sửa user nếu addUser gặp user lạ xuất hiện giữa chừng.


def test_bo_nhom_chi_danh_sach_cam():
    from tram.chu.nhom_rieng import lenh_bo_nhom
    cmds = lenh_bo_nhom('tram-kiem', {'staff', '_lpoperator', 'everyone', 'localaccounts'})
    assert [c[-1] for c in cmds] == ['staff']
    assert lenh_bo_nhom('tram-kiem', {'everyone', 'localaccounts', '_lpoperator',
                                     'com.apple.sharepoint.group.1'}) == []


def test_siet_user_la_khong_ghi(tmp_path):
    from tram.chu.nhom_rieng import siet_user
    calls = []
    with pytest.raises(ValueError, match='không khớp sổ'):
        siet_user('tram-kiem', SoCai(tmp_path / 'so'), lambda *a: {'uid': 503, 'guid': 'foreign'},
                  chay=lambda *a, **k: calls.append(a))
    assert not calls


def test_siet_user_giu_uid_guid_va_nhom_he_thong(tmp_path):
    from tram.chu.nhom_rieng import siet_user
    so, calls = SoCai(tmp_path / 'so'), []
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 701, 'guid': 'G'}}
    for k in identities:
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=identities[k])
    background = {'com.apple.sharepoint.group.1', '_lpoperator', 'everyone', 'localaccounts'}
    groups = background | {'staff', 'com.apple.sharepoint.group.7'}
    removed = []
    def run(cmd, **kw):
        calls.append(cmd)
        if cmd[:2] == ['/usr/bin/id', '-g']:
            return SimpleNamespace(stdout='701')
        if cmd[:2] == ['/usr/bin/id', '-Gn']:
            return SimpleNamespace(stdout=' '.join(groups))
        if '-d' in cmd:
            assert cmd[-1] not in background  # NestedGroups: không gỡ được bằng -d user.
            groups.remove(cmd[-1])
    siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run, truoc_bo=removed.extend)
    assert groups == background
    assert removed == ['com.apple.sharepoint.group.7', 'staff']
    assert next(c for c in calls if c[0] == 'sudo')[-2:] == ['PrimaryGroupID', '701']
    assert identities['user'] == {'uid': 503, 'guid': 'U'}


def test_sharepoint_khong_hardcode_mot_nhom():
    from tram.chu.nhom_rieng import lenh_bo_nhom
    assert [c[-1] for c in lenh_bo_nhom('tram-kiem', {'com.apple.sharepoint.group.7'})] == [
        'com.apple.sharepoint.group.7']


@pytest.mark.parametrize('extra', ['admin', 'nhom-la'])
def test_nhom_la_dung_truoc_doi_gid(tmp_path, extra):
    from tram.chu.nhom_rieng import siet_user
    so = SoCai(tmp_path / 'so')
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 701, 'guid': 'G'}}
    for k, value in identities.items():
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=value)
    calls = []
    def run(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(stdout=f'{extra} staff everyone localaccounts _lpoperator com.apple.sharepoint.group.1')
    with pytest.raises(ValueError, match='nhóm ngoài'):
        siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run)
    assert not any(c[0] == 'sudo' for c in calls)


def test_cai_lai_khong_tu_migrate_user_staff(tram_home_tam, tmp_path):
    from he_gia import HeGia
    from test_cai_dat_tho_kiem import ke_hoach
    from tram.chu.cai_dat import thuc_hien
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.phu['tram-tho'] = {'staff'}
    he.lenh.clear()
    with pytest.raises(ValueError, match='migration'):
        ke_hoach(tmp_path, he)
    assert not any(c.startswith('sudo') for c in he.lenh)


def test_cai_lai_chap_nhan_bon_nhom_nen_os(tram_home_tam, tmp_path):
    from he_gia import HeGia
    from test_cai_dat_tho_kiem import ke_hoach
    from tram.chu.cai_dat import thuc_hien
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    for user in he.user:
        he.phu[user] = {user, 'everyone', 'localaccounts', '_lpoperator', 'com.apple.sharepoint.group.1'}
    he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert not any(' -d ' in c for c in he.lenh)


@pytest.mark.parametrize('extra', ['staff', 'admin', 'nhom-la'])
def test_hau_kiem_khong_bo_qua_nhom_ngoai_nen(tmp_path, extra):
    from tram.chu.nhom_rieng import siet_user
    so = SoCai(tmp_path / 'so')
    identities = {'user': {'uid': 503, 'guid': 'U'}, 'nhom': {'gid': 702, 'guid': 'G'}}
    for k, value in identities.items():
        so.du_dinh(k, k, 'tram-kiem', {})
        so.ket(k, 'da_tao', dinh_danh=value)
    reads = 0
    def run(cmd, **kw):
        nonlocal reads
        if cmd[:2] == ['/usr/bin/id', '-g']:
            return SimpleNamespace(stdout='702')
        if cmd[:2] == ['/usr/bin/id', '-Gn']:
            reads += 1
            return SimpleNamespace(stdout='everyone localaccounts _lpoperator com.apple.sharepoint.group.1'
                                    + (f' {extra}' if reads == 3 else ''))
    with pytest.raises(ValueError, match='vẫn có nhóm thừa'):
        siet_user('tram-kiem', so, lambda k,n: identities[k], chay=run)
```

### Mã mới nguyên văn

`tram/chu/nhom_rieng.py`

```python
"""Nhóm chính riêng; sổ R2 chứng minh GID/GUID trước mọi thao tác dùng nhóm."""
import subprocess

from tram.chu.dinh_danh import cung
from tram.chu.tai_nguyen import TaiNguyen

# Máy B 24G90, 19/10: 701 lồng everyone; 100 lồng localaccounts, không gỡ theo user được.
NHOM_NEN = frozenset({'everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator'})
NHOM_THUA = ('staff',)


def nhom_tram(u: str) -> TaiNguyen:
    return TaiNguyen('nhom', u, lambda i: [
        ['sudo', '/usr/sbin/dseditgroup', '-o', 'create', '-r', f'tram {u} {i}', u]],
        lambda i: {'user': u, 'ten_day_du': f'tram {u} {i}'})


def gid_tram(u, so, quan_sat):
    hien = quan_sat('nhom', u)
    if hien is None or not any(cung('nhom', m.dinh_danh, hien) for m in so.da_tao('nhom', u)):
        raise ValueError(f'Nhóm {u} chưa có biên nhận đúng GID/GUID — dừng')
    return str(hien['gid'])


def user_nhom(u, nha, so, quan_sat) -> TaiNguyen:
    def lenh(i):
        gid = f'<gid:{u}>' if i == '<id>' else gid_tram(u, so, quan_sat)
        return [['sudo', 'sysadminctl', '-addUser', u, '-fullName', f'tram {u} {i}',
                 '-home', nha, '-shell', '/usr/bin/false', '-GID', gid]]
    return TaiNguyen('user', u, lenh, lambda i: {'ten_day_du': f'tram {u} {i}'})


def nhom_phu(u, *, chay=subprocess.run):
    r = chay(['/usr/bin/id', '-Gn', u], capture_output=True, text=True, timeout=30, check=True)
    return set(r.stdout.split())


def lenh_bo_nhom(u, nhom):
    return [['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-d', u, '-t', 'user', g]
            for g in sorted(nhom) if g not in NHOM_NEN
            and (g in NHOM_THUA or g.startswith("com.apple.sharepoint.group."))]


def siet_user(u, so, quan_sat, *, chay=subprocess.run, truoc_bo=lambda groups: None):
    from tram.chu.tai_nguyen import user_cua_tram
    if user_cua_tram(so, u, quan_sat) is None:
        raise ValueError(f'User {u} không khớp sổ; dừng')
    gid = gid_tram(u, so, quan_sat)
    groups = nhom_phu(u, chay=chay)
    removable = {c[-1] for c in lenh_bo_nhom(u, groups)}
    if groups - removable - {u} - NHOM_NEN:
        raise ValueError(f'User {u} có nhóm ngoài danh sách đã duyệt; dừng trước đổi GID')
    chay(['sudo', '/usr/bin/dscl', '.', '-create', f'/Users/{u}', 'PrimaryGroupID', gid], check=True, timeout=30)
    commands = lenh_bo_nhom(u, nhom_phu(u, chay=chay))
    truoc_bo([cmd[-1] for cmd in commands])  # fsync receipt trước xóa membership thực, sau đổi nhóm chính.
    for cmd in commands:
        if user_cua_tram(so, u, quan_sat) is None or gid_tram(u, so, quan_sat) != gid:
            raise ValueError('Danh tính đổi giữa chừng; dừng')
        chay(cmd, check=True, timeout=30)
    actual = chay(['/usr/bin/id', '-g', u], capture_output=True, text=True, timeout=30, check=True)
    if actual.stdout.strip() != gid or nhom_phu(u, chay=chay) - {u} - NHOM_NEN:
        raise ValueError(f'User {u} vẫn có nhóm thừa; dừng')
```

### Diff các file hiện hữu

```diff
diff --git a/tests/he_gia.py b/tests/he_gia.py
index ebd8f82..45e70ef 100644
--- a/tests/he_gia.py
+++ b/tests/he_gia.py
@@ -13,2 +13,3 @@ class HeGia:
     def __init__(self, add_tao_nha: bool = False, dung_lai_uid: bool = False):
+        self.nhom, self.gid, self.phu = {}, {}, {}
         self.user: dict[str, dict] = {}
@@ -32,2 +33,4 @@ class HeGia:
     def quan_sat(self, kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
+        if kieu == "nhom":
+            return self.nhom.get(ten)
         if kieu == "user":
@@ -40,2 +43,6 @@ class HeGia:
         self.lenh.append(" ".join(c))
+        if c[:2] == ["/usr/bin/id", "-g"]:
+            return subprocess.CompletedProcess(c, 0, str(self.gid[c[-1]]), "")
+        if c[:2] == ["/usr/bin/id", "-Gn"]:
+            return subprocess.CompletedProcess(c, 0, " ".join(self.phu.get(c[-1], set())), "")
         x = c[1:] if c[0] == "sudo" else c
@@ -51,3 +58,12 @@ class HeGia:
     def _lam(self, x: list[str], ai: str | None = None) -> bool:
-        if x[:2] == ["sysadminctl", "-addUser"] and x[2] not in self.user:
+        if x[:3] == ["/usr/sbin/dseditgroup", "-o", "create"]:
+            self.nhom.setdefault(x[-1], {"gid": 700 + len(self.nhom), "guid": f"G-{x[-1]}",
+                                        "ten_day_du": x[x.index("-r") + 1]})
+        elif x[:3] == ["/usr/sbin/dseditgroup", "-o", "delete"]:
+            self.nhom.pop(x[-1], None)
+        elif x[:3] == ["/usr/sbin/dseditgroup", "-o", "edit"]:
+            self.phu.get(x[x.index("-d") + 1], set()).discard(x[-1])
+        elif x[:3] == ["/usr/bin/dscl", ".", "-create"]:
+            self.gid[x[3].split("/")[-1]] = int(x[-1])
+        elif x[:2] == ["sysadminctl", "-addUser"] and x[2] not in self.user:
             self.them_user(x[2], x[x.index("-fullName") + 1])
diff --git a/tests/test_cai_dat_tho_kiem.py b/tests/test_cai_dat_tho_kiem.py
index 4855699..31facf0 100644
--- a/tests/test_cai_dat_tho_kiem.py
+++ b/tests/test_cai_dat_tho_kiem.py
@@ -70,3 +70,3 @@ def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp
     muc = SoCai().muc().values()
-    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 11    # 3 user, 2 nhà, 2 thư mục, hồ sơ + manifest,
+    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 14    # 3 user, 2 nhà, 2 thư mục, hồ sơ + manifest,
     #                                                                   sudoers, daemon
@@ -75,3 +75,3 @@ def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp
     assert not any("createhomedir -c -u tram-kiem" in x for x in he.lenh)
-    u = next(m for m in muc if m.ten == "tram-kiem")
+    u = next(m for m in muc if m.kieu == "user" and m.ten == "tram-kiem")
     assert u.dinh_danh == he.user["tram-kiem"] and he.user["tram-kiem"]["ten_day_du"] == f"tram tram-kiem {u.id}"
@@ -95,3 +95,3 @@ def test_user_xuat_hien_giua_chung_thi_khong_nhan_la_cua_tram(tram_home_tam, tmp
         thuc_hien(kh, chay=he.chay)
-    su = {m.ten: m.su for m in SoCai().muc().values()}
+    su = {m.ten: m.su for m in SoCai().muc().values() if m.kieu != "nhom"}
     assert su == {"tram-k-1": "da_tao", "tram-kiem": "khong_tao"} and he.user["tram-kiem"]["ten_day_du"] == "người khác"
@@ -137,3 +137,3 @@ def test_cai_hong_giua_ho_so_va_manifest_thi_so_ghi_dung_phan_da_cai(tram_home_t
         thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
-    su = {m.ten: m.su for m in SoCai().muc().values()}
+    su = {m.ten: m.su for m in SoCai().muc().values() if m.kieu != "nhom"}
     assert su[str(HO_SO_KIEM)] == "da_tao" and su[str(MANIFEST_KIEM)] == "khong_tao"
diff --git a/tests/test_go_cai_dat_tho.py b/tests/test_go_cai_dat_tho.py
index 87a9725..0b96ca7 100644
--- a/tests/test_go_cai_dat_tho.py
+++ b/tests/test_go_cai_dat_tho.py
@@ -43,3 +43,4 @@ def test_go_dung_thu_tu_het_sach_va_chay_lai_rong(tram_home_tam, tmp_path):
         *(f"Gỡ user {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho")),
-        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ"]
+        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ",
+        *(f"Gỡ nhom {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho"))]
     he.lenh.clear()
@@ -74,5 +75,5 @@ def test_crash_quanh_lenh_tao_doi_soat_roi_moi_go(tram_home_tam, tmp_path, sau):
         cai(tmp_path, he, co_che="user", chay=chay)
-    assert [m.su for m in SoCai().muc().values()] == ["du_dinh"]
+    assert [m.su for m in SoCai().muc().values() if m.kieu == "user"] == ["du_dinh"]
     thuc_hien(ke_hoach_go(he), chay=he.chay)
-    assert he.user == {} and [m.su for m in SoCai().muc().values()] == ["da_go" if sau else "khong_tao"]
+    assert he.user == {} and [m.su for m in SoCai().muc().values() if m.kieu == "user"] == ["da_go" if sau else "khong_tao"]
     assert ke_hoach_go(he).buoc == []          # trước lệnh: chỉ đối soát khép bản ghi dở, không có gì để gỡ
@@ -86,4 +87,5 @@ def test_user_xoa_tao_lai_hoac_file_bi_sua_thi_khong_go(tram_home_tam, tmp_path)
     thuc_hien(ke_hoach_go(he, bao), chay=he.chay)
-    assert list(he.user) == ["tram-kiem"] and list(he.tep) == [str(SUDOERS)] and len(bao) == 2
-    assert all("không khớp sổ" in b for b in bao)
+    assert list(he.user) == ["tram-kiem"] and list(he.tep) == [str(SUDOERS)] and len(bao) == 3
+    assert all("không khớp sổ" in b for b in bao[:2])
+    assert "user vẫn còn" in bao[-1]

diff --git a/tram/chu/cai_dat_tho.py b/tram/chu/cai_dat_tho.py
index c9cf207..4275cae 100644
--- a/tram/chu/cai_dat_tho.py
+++ b/tram/chu/cai_dat_tho.py
@@ -16,2 +16,3 @@ from tram.chu import dinh_danh
 from tram.chu.launchd import PATH_HE_THONG
+from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user, lenh_bo_nhom, NHOM_THUA, NHOM_NEN, nhom_phu
 from tram.chu.so_cai_tho import SoCai, doi_soat
@@ -39,4 +40,4 @@ def plist_tho(*, uv: str, repo: Path, quan_ly: str) -> bytes:
     return plistlib.dumps({
-        "Label": NHAN_THO, "UserName": quan_ly, "ProgramArguments": [uv, "run", "--project", str(repo), "tram", "tho",
-                                                                      "chay"],
+        "Label": NHAN_THO, "UserName": quan_ly,
+        "ProgramArguments": [uv, "run", "--offline", "--no-sync", "--project", str(repo), "tram", "tho", "chay"],
         "WorkingDirectory": str(repo), "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False},
@@ -46,10 +47,2 @@ def plist_tho(*, uv: str, repo: Path, quan_ly: str) -> bytes:

-def user_tram(u: str, nha: str) -> TaiNguyen:
-    """CHỈ `addUser` — RealName mang mã id của bản ghi sổ (bằng chứng user do CHÍNH lần cài này tạo). Nhà là bước
-    riêng (`nha_tram`, R5): biên nhận user không có nghĩa nhà đã tạo xong."""
-    return TaiNguyen("user", u, lambda i: [["sudo", "sysadminctl", "-addUser", u, "-fullName", f"tram {u} {i}", "-home",
-                                            nha, "-shell", "/usr/bin/false"]],
-                     lambda i: {"ten_day_du": f"tram {u} {i}"})
-
-
 def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[str, str], co_che: str,
@@ -71,3 +64,4 @@ def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[
     nguoi = sorted(set(khe.values()) | ({kiem.ten} if kiem else set()) | {quan_ly})
-    ds = [user_tram(u, NHA_KIEM if kiem and u == kiem.ten else f"/Users/{u}") for u in nguoi]
+    ds = [nhom_tram(u) for u in nguoi]
+    ds += [user_nhom(u, NHA_KIEM if kiem and u == kiem.ten else f"/Users/{u}", so, quan_sat) for u in nguoi]
     ds += [nha_tram(u, so, quan_sat) for u in nguoi if not (kiem and u == kiem.ten)]
@@ -78,2 +72,5 @@ def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[
     viec = kiem_truoc(so, ds, quan_sat=quan_sat)
+    for u in nguoi:
+        if quan_sat('user', u) is not None and nhom_phu(u, chay=chay) - {u} - NHOM_NEN:
+            raise ValueError('User cũ còn nhóm ngoài: chạy migration có audit/rollback trước cài lại')
     buoc = [("Đối soát sổ cài đặt (bản ghi dở dang của lần trước)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
@@ -81,2 +78,6 @@ def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[
              for tn, v in zip(ds, viec)]
+    siet = [(f"Siết {u}: sudo dscl . -create /Users/{u} PrimaryGroupID <gid:{u}>; "
+             + "; ".join(" ".join(c) + " (nếu là thành viên)" for c in lenh_bo_nhom(u, NHOM_THUA)),
+             lambda u=u: siet_user(u, so, quan_sat, chay=chay)) for u in nguoi]
+    buoc[1 + 2 * len(nguoi):1 + 2 * len(nguoi)] = siet
     lenh = [["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"], ["sudo", "launchctl", "bootstrap", "system",
diff --git a/tram/chu/dinh_danh.py b/tram/chu/dinh_danh.py
index f6bac64..4137437 100644
--- a/tram/chu/dinh_danh.py
+++ b/tram/chu/dinh_danh.py
@@ -26,2 +26,14 @@ def _doc_dscl(s: str) -> dict:

+def nhom(ten: str, *, chay=subprocess.run) -> dict | None:
+    r = chay(["/usr/bin/dscl", ".", "-read", f"/Groups/{ten}", "PrimaryGroupID", "GeneratedUID", "RealName"],
+             capture_output=True, text=True, timeout=30)
+    if r.returncode == 0:
+        gia = _doc_dscl(r.stdout.replace("PrimaryGroupID:", "UniqueID:"))
+        gia["gid"] = gia.pop("uid")
+        return gia
+    if "eDSRecordNotFound" in (r.stdout or "") + (r.stderr or ""):
+        return None
+    raise OSError(f"Không đọc được nhóm {ten}; dừng")
+
+
 def user(ten: str, *, chay=subprocess.run) -> dict | None:
@@ -61,2 +73,7 @@ def quan_sat_that(kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
     """`nhe`: lúc lập kế hoạch — không gọi `sudo` (chỉ biết file có hay không)."""
+    if kieu == "acl_search":
+        from tram.chu.acl_tho import quan_sat
+        return quan_sat(Path(ten))
+    if kieu == "nhom":
+        return nhom(ten)
     if kieu == "user":
@@ -69,3 +86,5 @@ def khop(kieu: str, mong: dict, hien: dict) -> bool:
         return False
-    if kieu == "user":
+    if kieu == "acl_search":
+        return hien == mong
+    if kieu in ("user", "nhom"):
         return hien.get("ten_day_du") == mong.get("ten_day_du")
@@ -79,4 +98,7 @@ def cung(kieu: str, da: dict | None, hien: dict) -> bool:
         return False
-    if kieu == "user":
-        return (hien.get("uid"), hien.get("guid")) == (da.get("uid"), da.get("guid"))
+    if kieu == "acl_search":
+        return hien == da
+    if kieu in ("user", "nhom"):
+        key = "gid" if kieu == "nhom" else "uid"
+        return (hien.get(key), hien.get("guid")) == (da.get(key), da.get("guid"))
     return hien.get("sha256") == da.get("sha256") if kieu == "tep" else hien.get("ino") == da.get("ino")
diff --git a/tram/chu/go_cai_dat_tho.py b/tram/chu/go_cai_dat_tho.py
index 33b8d93..21bed08 100644
--- a/tram/chu/go_cai_dat_tho.py
+++ b/tram/chu/go_cai_dat_tho.py
@@ -18,5 +18,7 @@ TEN = USER_RE                                        # cùng luật với lúc c
 def _thu_tu(m: Muc) -> int:
+    if m.kieu == "acl_search":
+        return 1
     if m.kieu == "tep":
         return 0 if m.ten == str(DAEMON) else 1
-    return {"user": 3, "nha": 4}.get(m.kieu, 2 if m.mong.get("chu") else 5)
+    return {"user": 3, "nha": 4, "nhom": 6}.get(m.kieu, 2 if m.mong.get("chu") else 5)

@@ -25,3 +27,3 @@ def _hop_le(m: Muc) -> bool:
     """Trường của sổ đi vào lệnh sudo: tên user/chủ đúng dạng, đường dẫn tuyệt đối không `..`, nhà là /Users/<user>."""
-    if m.kieu == "user":
+    if m.kieu in ("user", "nhom"):
         return bool(TEN.fullmatch(m.ten))
@@ -34,2 +36,6 @@ def _hop_le(m: Muc) -> bool:
 def lenh_go(m: Muc) -> list[list[str]]:
+    if m.kieu == "acl_search":
+        return [["sudo", "/bin/chmod", "-a", "user:tram-tho allow search", m.ten]]
+    if m.kieu == "nhom":
+        return [["sudo", "/usr/sbin/dseditgroup", "-o", "delete", m.ten]]
     if m.kieu == "user":
@@ -62,2 +68,5 @@ def go(so: SoCai, m: Muc, *, quan_sat: Callable, chay: Callable, bao: Callable[[
         return False
+    if m.kieu == "nhom" and quan_sat("user", m.ten) is not None:
+        bao(f"Giữ nhóm {m.ten}: user vẫn còn")
+        return False
     for c in lenh_go(m):
diff --git a/tram/chu/so_cai_tho.py b/tram/chu/so_cai_tho.py
index 37db761..a291dc6 100644
--- a/tram/chu/so_cai_tho.py
+++ b/tram/chu/so_cai_tho.py
@@ -19,3 +19,3 @@ from tram.duong_dan import tram_home
 PHIEN_BAN = 2
-KIEU = ("user", "nha", "tep", "thu_muc")
+KIEU = ("acl_search", "nhom", "user", "nha", "tep", "thu_muc")
 SU = ("du_dinh", "da_tao", "khong_tao", "da_go")
```

### Task 3A — ACL search riêng cho quản lý tin cậy, không chép repo

**Quyết định vòng 2:** chấp nhận đề xuất 1 trong mô hình `tram-tho` chỉ chạy mã trạm tin cậy.
Không nới DAC của `tram-khe1`/`tram-kiem`. Search khác list nhưng vẫn cho truy cập tên đã biết:
quản lý bị chiếm có thể đọc file 644 trong nhà Đại ca nếu chuỗi cha đi được. Không mô tả đây là
cách ly nhà trước quản lý; nếu quản lý chạy mã dự án không tin cậy thì thiết kế này không hợp lệ.

**Trình tự:** áp mã Task 1–3, dừng daemon theo sổ tay đã duyệt, rồi chạy `cai` dưới đây trước migration.
CLI đọc plist đã cài, chỉ nhận đúng layout uv của trạm; đổi plist sang offline/no-sync qua tài nguyên
file R2 (không bootstrap). Repo/venv giữ nguyên vị trí và owner. Nếu thiếu `.venv`, dừng để operator
chuẩn bị dependency offline bằng quy trình hiện có; không cấp write cho quản lý để uv tự sửa repo.
Nguồn ACL là cha của repo, uv, Python `.venv` và đích symlink đã resolve; không nhập danh sách tùy ý.
Chỉ tài khoản `tram-tho`; không cấp group ACL hay cờ kế thừa. Các ACL khác giữ nguyên.

R2 mới `acl_search`: inode/device/owner thư mục + UID/GUID quản lý + nội dung ACL sau thêm.
Có ACE sẵn không có sổ thì từ chối nhận. Quan sát trước/sau; đổi ACL hoặc danh tính thì không gỡ.
Crash sau chmod trước da_tao được đối soát từ du_dinh. Gỡ đúng ACE bằng `chmod -a`, trước gỡ user;
không xóa thư mục, không `chmod -N`. Nếu ACL đã bị sửa, giữ lại để operator kiểm tay.
Mọi lần `cai`/`go` in lệnh, chờ `dong-y`; không chạy lệnh trong phiên review.

```bash
UV_NO_SYNC=1 uv run --offline python -m scripts.acl_tho cai
```

Sau migration nhóm, **trước cài lại/khởi động daemon**, chạy:

```bash
UV_NO_SYNC=1 uv run --offline python -m scripts.acl_tho kiem
sudo -u tram-tho /usr/bin/env -i HOME=/Users/tram-tho PATH=/usr/bin:/bin:/usr/sbin:/sbin /opt/homebrew/Cellar/uv/0.13.0/bin/uv run --offline --no-sync --project '/Users/dai-ca/Developer/Ben Station' tram tho kiem
```

`kiem` dùng uv đúng plist, kiểm -x/-r cả lexical path và đích thật, kiểm hai principal không vào nhà,
smoke import mã quản lý bằng môi trường sạch. Lệnh `tram tho kiem` kiểm config/runtime của thợ;
không được mở S6 khi đỏ. Lệnh thứ hai pin đúng uv trong Task 1; nếu plist dùng bản khác thì dừng
đối chiếu pin trước chạy, không tự đổi. Khi thay repo/venv/uv/Python phải chạy lại `cai` và `kiem`.
Đường lùi riêng, sau dừng daemon và rollback nhóm khi cần:

```bash
UV_NO_SYNC=1 uv run --offline python -m scripts.acl_tho go
```

**TDD:** tạo test sau, chạy qua bộ chặn để RED; thêm module/script và diff Task 3 để GREEN.
Bằng chứng vòng 2 ở cuối. Đây là cài/migration máy B đã có user/daemon R2; máy mới phải tạo user
và chuẩn bị venv trước rồi thực hiện cùng cổng ACL trước cho daemon hoạt động.

`tests/test_acl_tho_plan.py` (file mới):

```python
from pathlib import Path
from types import SimpleNamespace
import pytest
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import tao, kiem_truoc
from tram.chu.go_cai_dat_tho import go


def test_acl_r2_dung_principal_va_go_khong_xoa_acl_khac(tmp_path):
    from tram.chu import acl_tho
    path = tmp_path / 'home'; path.mkdir()
    state = ['group:everyone deny delete']
    calls = []
    who = lambda: {'uid': 701, 'guid': 'THO'}
    def read(p):
        return list(state)
    def observe(k, n, **kw):
        return acl_tho.quan_sat(Path(n), doc=read, nguoi=who)
    def run(cmd, **kw):
        calls.append(cmd)
        if '+a' in cmd:
            state.append(acl_tho.ACE)
        elif '-a' in cmd:
            state.remove(acl_tho.ACE)
    resource = acl_tho.tai_nguyen(path, doc=read, nguoi=who)
    so = SoCai(tmp_path / 'so')
    assert kiem_truoc(so, [resource], quan_sat=observe) == ['tạo']
    assert tao(so, resource, quan_sat=observe, chay=run) == 'tao'
    assert tao(so, resource, quan_sat=observe, chay=run) == 'giu'
    item = so.da_tao('acl_search', str(path))[0]
    assert go(so, item, quan_sat=observe, chay=run, bao=lambda s: None)
    assert state == ['group:everyone deny delete']
    assert calls == [['sudo', '/bin/chmod', '+a', acl_tho.ACE, str(path)],
                     ['sudo', '/bin/chmod', '-a', acl_tho.ACE, str(path)]]


def test_acl_co_san_khong_nhan_va_thay_doi_khong_go(tmp_path):
    from tram.chu import acl_tho
    path = tmp_path / 'home'; path.mkdir()
    state = [acl_tho.ACE]
    who = lambda: {'uid': 701, 'guid': 'THO'}
    observe = lambda k, n, **kw: acl_tho.quan_sat(Path(n), doc=lambda p: state, nguoi=who)
    resource = acl_tho.tai_nguyen(path, doc=lambda p: state, nguoi=who)
    so = SoCai(tmp_path / 'so')
    with pytest.raises(ValueError, match='không phải của trạm'):
        kiem_truoc(so, [resource], quan_sat=observe)
    so.du_dinh('receipt', 'acl_search', str(path), resource.mong('receipt'))
    so.ket('receipt', 'da_tao', dinh_danh=observe('acl_search', str(path)))
    state.append('group:staff allow search')
    assert not go(so, so.da_tao('acl_search', str(path))[0], quan_sat=observe,
                  chay=lambda *a, **k: pytest.fail('không được chmod'), bao=lambda s: None)


def test_acl_symlink_va_quyen_rong_bi_chan(tmp_path):
    from tram.chu import acl_tho
    link = tmp_path / 'link'; link.symlink_to(tmp_path)
    with pytest.raises(ValueError):
        acl_tho.tai_nguyen(link, doc=lambda p: [], nguoi=lambda: {})
    with pytest.raises(ValueError):
        acl_tho.tai_nguyen(tmp_path, doc=lambda p: ['user:tram-tho allow list,search'], nguoi=lambda: {})


def test_preflight_duong_that_va_kiem_am(tmp_path):
    from tram.chu import acl_tho
    seen = []
    def run(cmd, **kw):
        seen.append(cmd)
        return SimpleNamespace(returncode=1 if cmd[3] == '/bin/test' and cmd[2] in ('tram-kiem', 'tram-khe1') else 0)
    acl_tho.kiem_quyen([(tmp_path, '-x'), (tmp_path / 'code', '-r')], chay=run)
    assert seen[-2:] == [['sudo', '-u', u, '/bin/test', '-x', '/Users/dai-ca']
                        for u in ('tram-khe1', 'tram-kiem')]
    with pytest.raises(ValueError):
        acl_tho.kiem_quyen([], chay=lambda *a, **k: SimpleNamespace(returncode=0))


def test_duong_can_bao_gom_python_that_va_khong_sync(tmp_path):
    from scripts.acl_tho import duong_can
    from tram.chu.cai_dat_tho import plist_tho
    import plistlib
    repo = tmp_path / 'repo'; (repo / '.venv/bin').mkdir(parents=True)
    (repo / 'tram').mkdir()
    for rel in ('pyproject.toml', 'tram/__init__.py', '.venv/pyvenv.cfg'):
        (repo / rel).touch()
    python = tmp_path / 'python'; python.touch()
    uv = tmp_path / 'uv'; uv.touch()
    (repo / '.venv/bin/python').symlink_to(python)
    pl = plistlib.loads(plist_tho(uv=str(uv), repo=repo, quan_ly='tram-tho'))
    assert (python, '-x') in duong_can(pl)
    assert (repo / '.venv/bin/python', '-x') in duong_can(pl)
    pl['ProgramArguments'].remove('--no-sync')
    with pytest.raises(ValueError, match='offline/no-sync'):
        duong_can(pl)


def test_acl_drift_truoc_chmod_khong_ghi(tmp_path):
    from tram.chu.acl_tho import tai_nguyen
    state = []
    resource = tai_nguyen(tmp_path, doc=lambda p: list(state), nguoi=lambda: {'uid': 701, 'guid': 'THO'})
    state.append('group:everyone deny delete')
    with pytest.raises(ValueError, match='đổi sau preview'):
        resource.lenh('receipt')


def test_acl_parser_giu_noi_dung_khong_lay_so_thu_tu(tmp_path, monkeypatch):
    from tram.chu import acl_tho
    monkeypatch.setattr(acl_tho.subprocess, 'run', lambda *a, **k: SimpleNamespace(
        stdout='drwxr-x---+ 3 hungle staff 96 Oct 19 00:00 home\n 0: user:tram-tho allow search\n'))
    assert acl_tho.doc_acl(tmp_path) == [acl_tho.ACE]


def test_acl_crash_du_dinh_doi_soat_va_guid_la(tmp_path):
    from tram.chu import acl_tho, dinh_danh
    from tram.chu.so_cai_tho import doi_soat
    state = []
    who = {'uid': 701, 'guid': 'THO'}
    resource = acl_tho.tai_nguyen(tmp_path, doc=lambda p: state, nguoi=lambda: dict(who))
    so = SoCai(tmp_path / 'so')
    so.du_dinh('pending', 'acl_search', str(tmp_path), resource.mong('pending'))
    state.append(acl_tho.ACE)  # giả lập crash sau chmod, trước da_tao
    obs = lambda k, n, **kw: acl_tho.quan_sat(Path(n), doc=lambda p: state, nguoi=lambda: dict(who))
    doi_soat(so, obs, dinh_danh.khop)
    assert so.da_tao('acl_search', str(tmp_path))
    who['guid'] = 'OTHER'
    assert not go(so, so.da_tao('acl_search', str(tmp_path))[0], quan_sat=obs,
                  chay=lambda *a, **k: pytest.fail('không gỡ ACL của danh tính khác'), bao=lambda s: None)


def test_sudo_loi_khong_duoc_tinh_thanh_dac_chan():
    from tram.chu.acl_tho import kiem_quyen
    with pytest.raises(ValueError, match='đối chứng sudo'):
        kiem_quyen([], chay=lambda *a, **k: SimpleNamespace(returncode=1))
```

`tram/chu/acl_tho.py` (file mới):

```python
"""ACL search riêng cho quản lý tin cậy; R2 giữ định danh thư mục, user và toàn ACL để gỡ đúng mục."""
import os
from pathlib import Path
import stat
import subprocess

from tram.chu.tai_nguyen import TaiNguyen

ACE = 'user:tram-tho allow search'


def nguoi_that():
    from tram.chu.dinh_danh import user
    who = user('tram-tho')
    if who is None:
        raise ValueError('Chưa có quản lý tram-tho')
    return {k: who[k] for k in ('uid', 'guid')}


def doc_acl(path):
    r = subprocess.run(['/bin/ls', '-lde', str(path)], check=True, capture_output=True, text=True, timeout=30)
    rows = r.stdout.splitlines()[1:]
    if any(not row.strip().partition(':')[0].isdigit() for row in rows):
        raise ValueError('Không đọc được ACL')
    return [row.strip().partition(':')[2].strip() for row in rows]


def danh_tinh(path, doc, nguoi):
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or path.resolve() != path or st.st_mode & 0o002:
        raise ValueError('Đường ACL không phải thư mục thật hoặc cho mọi người ghi')
    acl = doc(path)
    mine = [a for a in acl if 'tram-tho' in a]
    if mine and mine != [ACE]:
        raise ValueError('ACL tram-tho khác search; kiểm tay')
    return {'ino': st.st_ino, 'dev': st.st_dev, 'uid': st.st_uid, 'user': nguoi(), 'acl': sorted(acl)}


def quan_sat(path, *, doc=doc_acl, nguoi=nguoi_that):
    if not os.path.lexists(path):
        return None
    identity = danh_tinh(path, doc, nguoi)
    return identity if ACE in identity['acl'] else None


def tai_nguyen(path, *, doc=doc_acl, nguoi=nguoi_that):
    identity = danh_tinh(path, doc, nguoi)
    expected = {**identity, 'acl': sorted(set(identity['acl']) | {ACE})}
    def lenh(i):
        if danh_tinh(path, doc, nguoi) != identity:
            raise ValueError('ACL hoặc thư mục đổi sau preview; dừng')
        return [['sudo', '/bin/chmod', '+a', ACE, str(path)]]
    return TaiNguyen('acl_search', str(path), lenh, lambda i: expected)


def kiem_quyen(paths, *, chay=subprocess.run):
    # Xác minh sudo/id riêng: exit 1 của sudo lỗi không được tính thành test âm đạt.
    for user in ('tram-tho', 'tram-khe1', 'tram-kiem'):
        r = chay(['sudo', '-u', user, '/usr/bin/true'], timeout=30)
        if r.returncode:
            raise ValueError('Không chạy được đối chứng sudo; giữ cổng đóng')
    for path, mode in paths:
        r = chay(['sudo', '-u', 'tram-tho', '/bin/test', mode, str(path)], timeout=30)
        if r.returncode:
            raise ValueError('Quản lý không đọc/chạy được đường cần thiết')
    for user in ('tram-khe1', 'tram-kiem'):
        r = chay(['sudo', '-u', user, '/bin/test', '-x', '/Users/dai-ca'], timeout=30)
        if r.returncode != 1:
            raise ValueError('Khe/kiểm còn vào được nhà Đại ca hoặc phép thử lỗi')
```

`scripts/acl_tho.py` (file mới):

```python
"""Cài/gỡ ACL quản lý có R2; in kế hoạch và chờ dong-y. Chỉ chạy trên máy B sau duyệt."""
import argparse
from pathlib import Path
import plistlib

from tram.chu import dinh_danh
from tram.chu.acl_tho import tai_nguyen, kiem_quyen
from tram.chu.cai_dat_tho import DAEMON
from tram.chu.go_cai_dat_tho import go, lenh_go
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao, user_cua_tram

NHA = Path('/Users/dai-ca')


def duong_can(plist):
    args = plist['ProgramArguments']
    repo = Path(plist['WorkingDirectory'])
    if plist.get('UserName') != 'tram-tho' or not args or not Path(args[0]).is_absolute():
        raise ValueError('Plist không phải quản lý tram-tho/uv tuyệt đối')
    if args[1:] != ['run', '--offline', '--no-sync', '--project', str(repo), 'tram', 'tho', 'chay']:
        raise ValueError('Plist phải ghim uv offline/no-sync; cài lại plist trước migration')
    paths = [(repo, '-x'), (repo / 'pyproject.toml', '-r'), (repo / 'tram/__init__.py', '-r'),
             (Path(args[0]), '-x'), (repo / '.venv/bin/python', '-x'), (repo / '.venv/pyvenv.cfg', '-r')]
    result = []
    for path, mode in paths:
        if not path.is_absolute() or '..' in path.parts or not path.exists():
            raise ValueError('Đường chạy thiếu hoặc không tuyệt đối')
        result.extend(((path, mode), (path.resolve(strict=True), mode)))
    return sorted(set(result))


def thu_muc(paths):
    result = {NHA}
    for path, mode in paths:
        for p in path.parents:
            if p.is_relative_to(NHA):
                result.add(p.resolve(strict=True))
    return sorted(result, key=lambda p: (len(p.parts), str(p)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('cai', 'kiem', 'go'))
    parser.add_argument('--plist', type=Path, default=DAEMON)
    args = parser.parse_args()
    so, obs = SoCai(), dinh_danh.quan_sat_that
    with so.giu():
        if user_cua_tram(so, 'tram-tho', obs) is None:
            raise ValueError('tram-tho không khớp UID/GUID trong sổ')
        if args.mode == 'go':
            items = [m for m in so.muc().values() if m.kieu == 'acl_search' and m.su in ('du_dinh', 'da_tao')]
            for m in items:
                print(lenh_go(m))
            if input('Gỡ đúng ACL đã tạo — gõ dong-y: ') != 'dong-y':
                return
            doi_soat(so, obs, dinh_danh.khop)
            import subprocess
            for m in items:
                go(so, m, quan_sat=obs, chay=subprocess.run, bao=print)
            return
        pl = plistlib.loads(args.plist.read_bytes())
        patch = None
        old = pl['ProgramArguments']
        if args.mode == 'cai' and old[1:] == ['run', '--project', pl['WorkingDirectory'], 'tram', 'tho', 'chay']:
            from tram.chu.cai_dat_kiem import tep_root
            pl['ProgramArguments'] = [old[0], 'run', '--offline', '--no-sync', *old[2:]]
            patch = plistlib.dumps(pl)
            staged = so.p.parent / 'tho-offline.plist'
        paths = duong_can(pl)
        resources = [tai_nguyen(p) for p in thu_muc(paths)]
        if args.mode == 'kiem':
            from tram.chu.tai_nguyen import cua_tram
            if not all(cua_tram(so, r.kieu, r.ten, obs(r.kieu, r.ten) or {}) for r in resources):
                raise ValueError('ACL chưa khớp biên nhận; giữ cổng đóng')
            kiem_quyen(paths)
            import subprocess
            subprocess.run(['sudo', '-u', 'tram-tho', '/usr/bin/env', '-i', 'HOME=/Users/tram-tho',
                            'PATH=/usr/bin:/bin:/usr/sbin:/sbin', 'PYTHONDONTWRITEBYTECODE=1',
                            *pl['ProgramArguments'][:-3], 'python', '-I', '-B', '-c',
                            'import tram, ssl, sqlite3, ctypes; from tram.tho import cau_hinh'],
                           cwd=pl['WorkingDirectory'], check=True, timeout=60)
            return
        if patch is not None:
            resources.append(tep_root(staged, args.plist, patch, '0644'))
        actions = kiem_truoc(so, resources, quan_sat=obs)
        for r, action in zip(resources, actions):
            print(action, r.mo_ta())
        if input('Chỉ cấp search cho quản lý tram-tho — gõ dong-y: ') != 'dong-y':
            return
        if patch is not None:
            from tram.chu.cai_dat import KeHoach, thuc_hien
            thuc_hien(KeHoach({staged: patch}, [], []))
        doi_soat(so, obs, dinh_danh.khop)
        for r in resources:
            tao(so, r, quan_sat=obs)
        print('ACL đã ghi sổ; sau migration phải chạy kiem và smoke import trước khởi động daemon.')


if __name__ == '__main__':
    main()
```

### Migration máy B — chỉ Đại ca chạy sau khi chốt các điều kiện chặn

**Không chạy thẳng `cai-dat-tho` để chuyển tài khoản cũ.** Trình cài nay từ chối user còn nhóm ngoài;
phải đi qua migration có snapshot. Không cần đổi quyền owner/group từng file để giữ quyền của cùng UID.

1. Giữ Estop/S6 đóng, dừng nguồn cấp lượt và hết tiến trình agent cũ theo sổ tay. Không dùng lệnh giết
   theo tên. Nhóm tiến trình cũ không đổi theo Directory Service; kiểm dưới tiến trình mới sau migration.
2. Cài Python và đạt smoke Task 2. Chạy Task 3A `cai` trước đổi nhóm: cấp ACL có R2 cho quản lý và
   ghim plist offline/no-sync; daemon vẫn dừng. `preflight` xác minh đường chạy + biên nhận ACL.
   Không tạo bản sao repo. Config khe/kiểm vẫn ngoài nhà Đại ca; dependency gián tiếp của quản lý
   phải qua hậu kiểm import và `tram tho kiem` sau đổi nhóm trước khi khởi động lại daemon.
3. Đối chiếu UID/GUID trong R2; quan sát GID/nhóm và ACL chuỗi cha bằng lệnh chỉ đọc dưới đây.
   Không nhận user/nhóm lạ bằng cách sửa RealName. Sao lưu sổ; receipt migration là file mới, không ghi đè.

```sh
/usr/bin/id tram-kiem
/usr/bin/id tram-khe1
/usr/bin/id tram-tho
/bin/ls -lde /Users/dai-ca /Users/tram-khe1 /Users/tram-tho /Users/Shared/tram-kiem
```

4. Chạy nguyên khối lệnh dưới từ repo đã áp mã (Python chạy bằng uv offline).
   Nó kiểm UID/GUID qua `dscl -read`, tạo nhóm có R2 sau lần `dong-y` đầu; **audit nhà, gốc kiểm và config
   thuộc cây trước đổi GID**, rồi in GID thật và lệnh gỡ nhóm trước lần `dong-y` thứ hai.
   Chỉ cây cùng UID, không ACL/symlink/chủ lạ mới được qua. Lỗi đọc cây cũng dừng; không coi cây không đọc được
   là rỗng. Config ngoài các cây này phải được kê và xử lý riêng trước bước này, không tự mở staff để cứu.
   Nhóm mới không phá quyền cũ; audit lỗi thì giữ nhóm có sổ, user chưa đổi. Snapshot cập nhật trước mỗi
   lần gỡ membership, nên rollback được cả lúc chỉ đổi xong PrimaryGroupID.

```bash
UV_NO_SYNC=1 uv run --offline python - <<'PYMIGRATE'
import json
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from tram.chu import dinh_danh
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao, user_cua_tram, cua_tram
from tram.chu.nhom_rieng import nhom_tram, gid_tram, nhom_phu, lenh_bo_nhom, siet_user, NHOM_NEN
from scripts.siet_nhom_ownership import preflight

users = ('tram-kiem', 'tram-khe1', 'tram-tho')
so, obs = SoCai(), dinh_danh.quan_sat_that
receipt = so.p.with_name('migration-nhom-rieng-20261018.json')


def checkpoint():
    with NamedTemporaryFile(mode='w', dir=receipt.parent, delete=False) as f:
        json.dump(before, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    Path(f.name).replace(receipt)


def before_remove(user, groups):
    before[user]['removed'] = groups
    checkpoint()  # Ghi trước xóa; phục hồi lại membership vốn đã có là an toàn nếu lệnh chưa chạy.


with so.giu():
    doi_soat(so, obs, dinh_danh.khop)
    before = {}
    for u in users:
        ident = user_cua_tram(so, u, obs)
        if ident is None:
            raise SystemExit(f'DỪNG: user {u} không có biên nhận đúng UID/GUID')
        group = obs('nhom', u)
        if group is not None and not cua_tram(so, 'nhom', u, group):
            raise SystemExit(f'DỪNG: nhóm {u} không đúng biên nhận')
        groups = nhom_phu(u)
        removable = {c[-1] for c in lenh_bo_nhom(u, groups)}
        if groups - removable - {u} - NHOM_NEN:
            raise SystemExit(f'DỪNG: {u} có nhóm ngoài danh sách đã duyệt')
        old = subprocess.run(['/usr/bin/id', '-g', u], check=True, capture_output=True,
                             text=True, timeout=30).stdout.strip()
        before[u] = {'identity': ident, 'old_gid': old, 'old_groups': sorted(groups), 'removed': []}
    resources = [nhom_tram(u) for u in users]
    actions = kiem_truoc(so, resources, quan_sat=obs)
    for tn, action in zip(resources, actions):
        print(action, tn.mo_ta())
    if input('Tạo nhóm có sổ — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Chưa thay hệ thống')
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(before, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    for tn in resources:
        tao(so, tn, quan_sat=obs)
    # Không đổi quyền file: cùng UID vẫn dùng owner bits. Audit lỗi => user chưa đổi nhóm.
    people = preflight(so, obs)
    for u in users:
        before[u]['new_group'] = people[u]['group']
    checkpoint()
    for u in users:
        print('sudo /usr/bin/dscl . -create', f'/Users/{u}', 'PrimaryGroupID', gid_tram(u, so, obs))
        for cmd in lenh_bo_nhom(u, nhom_phu(u)):
            print(' '.join(cmd), '(chỉ nếu membership còn sau đổi nhóm chính)')
    if input('Đổi nhóm chính và bỏ nhóm thừa — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Giữ nhóm đã tạo có sổ; user chưa đổi')
    for u in users:
        siet_user(u, so, obs, truoc_bo=lambda groups, u=u: before_remove(u, groups))
PYMIGRATE
```

5. Hậu kiểm dưới tiến trình mới: `sudo -u tram-kiem /usr/bin/id`, `sudo -u tram-khe1 /usr/bin/id`,
   `sudo -u tram-tho /usr/bin/id`. Nhóm chính phải đúng nhóm riêng; chỉ kèm bốn nhóm nền OS
   `12 everyone`, `61 localaccounts`, `701 com.apple.sharepoint.group.1`, `100 _lpoperator`.
   Không còn `20 staff`, `80 admin`, sharepoint khác hay nhóm chưa được duyệt. Chạy từng lệnh dưới và xem mã thoát ngay sau mỗi lệnh:

```sh
sudo -u tram-kiem /bin/test -x /Users/dai-ca
printf 'tram-kiem: %s\n' "$?"
sudo -u tram-khe1 /bin/test -x /Users/dai-ca
printf 'tram-khe1: %s\n' "$?"
sudo -u tram-tho /bin/test -x /Users/dai-ca
printf 'tram-tho: %s\n' "$?"
```

   Hai principal `tram-kiem`/`tram-khe1` phải mã1, quản lý `tram-tho` phải mã0. Lỗi sudo/mật khẩu
   không tính là DAC chặn: Task 3A `kiem` có đối chứng sudo riêng rồi kiểm -x/-r các đường thực và import.
   Không thay mode nhà Đại ca; chỉ ACL search quản lý, không list/inherit/write. Giữ S6 đóng khi có lỗi.
6. Cài lại hồ sơ/manifest bằng trình cài có sổ, kiểm v2 khớp trước G4. Lệnh cài vẫn liệt kê/chờ `dong-y`.
   Làm trong cùng một Terminal để dùng timestamp sudo hiện có; không `sudo -v` nền, không thêm NOPASSWD root.
   Cài Python vẫn có tài nguyên R2 từng file (bản nguồn đo được 2.067 mục): **không hứa chỉ một lệnh sudo**;
   số lần hỏi mật khẩu tùy timeout sudo. Không chạy cả Python trạm bằng sudo để tiết kiệm lời nhắc.
7. Đường lùi: giữ Estop/S6, chạy lệnh dưới. Không cần snapshot quyền file vì không chown file nào.
   Script kiểm cả user UID/GUID lẫn nhóm GID/GUID, in lệnh/chờ `dong-y`, phục hồi GID cũ và chỉ membership
   đã ghi trước khi xóa; kiểm nhóm cuối khớp snapshot. Rollback khôi phục lỗ staff, không cho mở S6.
   Nếu dừng trước bước lưu `new_group` thì chưa đổi user: giữ nhóm đã tạo, không gọi rollback này.
   Sau phục hồi nhóm, gỡ ACL bằng Task 3A `go`; không dùng `chmod -N` hoặc xóa ACL của người khác.
   Plist offline/no-sync được giữ: lần chạy sau vẫn dùng venv đã chuẩn bị, không tự sync; không cần phục hồi byte cũ.

```sh
UV_NO_SYNC=1 uv run --offline python scripts/siet_nhom_ownership.py rollback \
 --identity-snapshot "$HOME/.tram/cai-dat-tho/migration-nhom-rieng-20261018.json"
```

Audit độc lập (chỉ đọc; dùng sau tạo nhóm, trước đổi GID):

```sh
UV_NO_SYNC=1 uv run --offline python scripts/siet_nhom_ownership.py audit
```

Rollback Python/hồ sơ: không gọi `go-cai-dat-tho` toàn bộ vì nó còn gỡ user/daemon. Nếu Python smoke lỗi,
giữ prefix có receipt và dừng; chưa đổi nhóm nên không mất đường cũ. Nếu hồ sơ v2 lỗi sau migration,
rollback nhóm theo snapshot và giữ cổng đóng; sửa policy rồi cài lại theo R2. Không dùng hồ sơ đọc toàn cục
để tiếp tục kiểm. Gỡ prefix riêng có chọn mục R2 chưa có CLI trong lát này: để nguyên prefix vô hại khi dừng.

### Mã audit ownership/rollback nhóm nguyên văn

```python
"""Audit ownership, không đổi UID/GID/mode file; rollback nhóm đúng cây có receipt R2; không theo symlink, không sửa ACL."""
import argparse
import json
import os
import plistlib
from pathlib import Path
import shlex
import stat
import subprocess

USERS = ('tram-kiem', 'tram-khe1', 'tram-tho')


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)


def has_acl(path):
    return '+' in run(['/bin/ls', '-lde', str(path)]).stdout.split()[0]


def record(path, uid, gid, acl):
    st = path.lstat()
    if stat.S_ISLNK(st.st_mode):
        raise ValueError(f'symlink: {path}; dừng audit')
    if st.st_uid != uid:
        raise ValueError(f'owner lạ: {path}; dừng audit')
    if not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
        raise ValueError(f'Loại file không hỗ trợ: {path}')
    if acl(path):
        raise ValueError(f'ACL tại {path}; cần audit riêng, chưa sửa quyền')
    return {'path': str(path), 'uid': uid, 'old_gid': st.st_gid, 'new_gid': gid,
            'mode': stat.S_IMODE(st.st_mode), 'ino': st.st_ino, 'dev': st.st_dev}


def audit(root, uid, gid, *, staff_gid=20, acl=has_acl):
    rows = [record(root, uid, gid, acl)]
    if root.is_dir():
        def fail(error):
            raise error
        for current, dirs, files in os.walk(root, followlinks=False, onerror=fail):
            for name in sorted(dirs + files):
                rows.append(record(Path(current) / name, uid, gid, acl))
    return [r for r in rows if r['old_gid'] == staff_gid]


def confirm(commands):
    for cmd in commands:
        print(shlex.join(cmd))
    if input('Chỉ chạy các lệnh trên — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Chưa thay hệ thống')


def home(user):
    raw = run(['/usr/bin/dscl', '.', '-read', f'/Users/{user}', 'NFSHomeDirectory']).stdout
    value = raw.partition(':')[2].strip()
    if not value.startswith('/') or '\n' in value:
        raise ValueError(f'Home không hợp lệ: {user}')
    return Path(value)


def identities(so, obs):
    from tram.chu.tai_nguyen import user_cua_tram, cua_tram
    result = {}
    for user in USERS:
        who, group = user_cua_tram(so, user, obs), obs('nhom', user)
        if who is None or group is None or not cua_tram(so, 'nhom', user, group):
            raise ValueError(f'User/nhóm không đúng receipt R2: {user}')
        result[user] = {'user': who, 'group': group}
    return result


def roots_from_receipts(so, obs, people):
    from tram.chu.dinh_danh import cung
    roots = {}
    for user in USERS:
        for root in (home(user), Path('/Users/Shared/tram-kiem') if user == 'tram-kiem' else home(user)):
            if root == Path('/var/empty'):
                continue  # home không ghi được của tram-kiem, không đổi ownership hệ thống
            if root.resolve() != root or root.is_symlink() or '..' in root.parts:
                raise ValueError(f'Gốc không an toàn: {root}')
            matches = [m for m in so.muc().values() if m.su == 'da_tao' and m.kieu in ('nha', 'thu_muc')
                       and m.ten == str(root) and cung(m.kieu, m.dinh_danh, obs(m.kieu, m.ten) or {})]
            if not matches or root.lstat().st_uid != people[user]['user']['uid']:
                raise ValueError(f'Gốc không đúng receipt R2/owner: {root}')
            roots[root] = user
    return roots


def kiem_duong_chay(plist, nha_operator):
    from scripts.acl_tho import duong_can, thu_muc
    from tram.chu import dinh_danh
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.tai_nguyen import cua_tram
    so = SoCai()
    for path in thu_muc(duong_can(plist)):
        hien = dinh_danh.quan_sat_that('acl_search', str(path))
        if not hien or not cua_tram(so, 'acl_search', str(path), hien):
            raise ValueError('Đường chạy trong nhà người vận hành chưa có ACL R2 đúng định danh')


def preflight(so, obs, config_roots=()):
    from tram.chu.cai_dat_tho import DAEMON
    if not DAEMON.exists():
        raise ValueError('Thiếu plist thợ; chưa có bản kê đường chạy để migration')
    with DAEMON.open('rb') as f:
        kiem_duong_chay(plistlib.load(f), Path.home())
    people = identities(so, obs)
    roots = roots_from_receipts(so, obs, people)
    for p in config_roots:
        if not p.exists() or not p.is_absolute() or p.resolve() != p or not any(p.is_relative_to(r) for r in roots):
            raise ValueError(f'Config thiếu/ngoài gốc có receipt hoặc qua symlink: {p}')
    for root, user in roots.items():
        audit(root, people[user]['user']['uid'], people[user]['group']['gid'])
    return people


def main():
    from tram.chu import dinh_danh
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.nhom_rieng import lenh_bo_nhom
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('audit', 'rollback'))
    parser.add_argument('--identity-snapshot', type=Path)
    parser.add_argument('--config-root', type=Path, action='append', default=[])
    args = parser.parse_args()
    so, obs = SoCai(), dinh_danh.quan_sat_that
    with so.giu():
        if args.mode == 'audit':
            preflight(so, obs, args.config_root)
            print('Audit ownership đạt: chỉ quyền owner được dùng; không chown file.')
            return
        if args.identity_snapshot is None:
            raise ValueError('Rollback cần snapshot trước đổi nhóm; không cần snapshot ownership')
        people = identities(so, obs)
        before = json.loads(args.identity_snapshot.read_text())
        commands = []
        for user in USERS:
            if before[user]['identity'] != people[user]['user']:
                raise ValueError(f'User thay định danh: {user}')
            if before[user].get('new_group') != people[user]['group']:
                raise ValueError('Nhóm thay GID/GUID; không rollback')
            gid = before[user]['old_gid']
            if not str(gid).isdigit():
                raise ValueError('Snapshot old_gid không hợp lệ')
            commands.append(['sudo', '/usr/bin/dscl', '.', '-create', f'/Users/{user}', 'PrimaryGroupID', str(gid)])
            # Chỉ khôi phục membership đã gỡ, không thêm staff vốn chỉ là nhóm chính.
            # lenh_bo_nhom bỏ cả bốn nhóm nền OS, kể cả snapshot cũ từng kê nhầm 701/100.
            for command in lenh_bo_nhom(user, before[user].get('removed', [])):
                command[command.index('-d')] = '-a'
                commands.append(command)
        confirm(commands)
        for cmd in commands:
            if identities(so, obs) != people:
                raise ValueError('Danh tính đổi giữa chừng; dừng')
            subprocess.run(cmd, check=True, timeout=30)
        for user in USERS:
            gid = run(['/usr/bin/id', '-g', user]).stdout.strip()
            groups = set(run(['/usr/bin/id', '-Gn', user]).stdout.split())
            if gid != str(before[user]['old_gid']) or groups != set(before[user]['old_groups']):
                raise ValueError('Rollback chưa khớp nhóm cũ; giữ S6 đóng')


if __name__ == '__main__':
    main()
```

### Test migration giả nguyên văn

Tạo `tests/test_siet_nhom_migration.py` (test chỉ tạo thư mục tạm và mock ACL, không chạm `/Users`):

```python
import importlib.util
from pathlib import Path
import pytest


def module():
    spec = importlib.util.spec_from_file_location('migration', Path(__file__).parents[1] / 'scripts/siet_nhom_ownership.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_owner_acl_symlink_chan_truoc_lenh(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir()
    uid = p.stat().st_uid
    with pytest.raises(ValueError, match='owner'):
        m.audit(p, uid + 1, 701, acl=lambda p: False)
    with pytest.raises(ValueError, match='ACL'):
        m.audit(p, uid, 701, acl=lambda p: True)
    link = p / 'link'; link.symlink_to('/Users/dai-ca')
    with pytest.raises(ValueError, match='symlink'):
        m.audit(p, uid, 701, acl=lambda p: False)


def test_staff_only_exact_paths_and_snapshot(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir(); (p / 'file').write_text('fake')
    uid, gid = p.stat().st_uid, p.stat().st_gid
    rows = m.audit(p, uid, 701, staff_gid=gid, acl=lambda p: False)
    assert {r['path'] for r in rows} == {str(p), str(p / 'file')}
    assert all(r['old_gid'] == gid and r['uid'] == uid and r['new_gid'] == 701 for r in rows)
    assert not hasattr(m, 'command')  # Không sinh chown cho file vẫn thuộc cùng UID.


def test_walk_loi_khong_duoc_bo_qua(tmp_path, monkeypatch):
    m = module()
    p = tmp_path / 'owned'; p.mkdir()
    def walk(root, **kw):
        kw['onerror'](PermissionError('không đọc được thư mục con'))
        return []
    monkeypatch.setattr(m.os, 'walk', walk)
    with pytest.raises(PermissionError):
        m.audit(p, p.stat().st_uid, 701, acl=lambda p: False)


def test_audit_khong_doi_quyen(tmp_path):
    m = module()
    p = tmp_path / 'owned'; p.mkdir(); (p / 'config').write_text('fake')
    before = [(x.stat().st_uid, x.stat().st_gid, x.stat().st_mode) for x in (p, p / 'config')]
    m.audit(p, p.stat().st_uid, 701, acl=lambda p: False)
    assert before == [(x.stat().st_uid, x.stat().st_gid, x.stat().st_mode) for x in (p, p / 'config')]


def test_chan_worker_plist_chua_offline_no_sync(tmp_path):
    m = module()
    with pytest.raises(ValueError):
        m.kiem_duong_chay({'ProgramArguments': ['uv', '--project', str(tmp_path / 'repo')],
                          'WorkingDirectory': str(tmp_path)}, tmp_path)


@pytest.mark.parametrize('removed', [[], ['staff', 'com.apple.sharepoint.group.7'],
                                   ['everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator']])
def test_rollback_nhom_do_dang_khong_can_snapshot_ownership(tmp_path, monkeypatch, removed):
    import contextlib
    import json
    import sys
    from types import SimpleNamespace
    from tram.chu import so_cai_tho
    m = module()
    people = {u: {'user': {'uid': i + 502, 'guid': u}, 'group': {'gid': i + 701, 'guid': u}}
              for i, u in enumerate(m.USERS)}
    background = ['everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator']
    restored = sorted(set(removed) - set(background))
    old_groups = set(background + ['staff'] + restored)
    before = {u: {'identity': p['user'], 'new_group': p['group'], 'old_gid': '20',
                  'old_groups': sorted(old_groups), 'removed': removed} for u, p in people.items()}
    snapshot = tmp_path / 'identity.json'; snapshot.write_text(json.dumps(before))
    monkeypatch.setattr(sys, 'argv', ['migration', 'rollback', '--identity-snapshot', str(snapshot)])
    monkeypatch.setattr(so_cai_tho, 'SoCai', lambda: SimpleNamespace(giu=contextlib.nullcontext))
    monkeypatch.setattr(m, 'identities', lambda *a: people)
    seen = []
    monkeypatch.setattr(m, 'confirm', lambda cmds: seen.extend(cmds))
    monkeypatch.setattr(m.subprocess, 'run', lambda *a, **k: None)
    monkeypatch.setattr(m, 'run', lambda c: SimpleNamespace(stdout='20' if '-g' in c else ' '.join(old_groups)))
    m.main()
    assert len(seen) == 3 * (1 + len(restored))
    assert all(c[-2:] == ['PrimaryGroupID', '20'] for c in seen if '-a' not in c)
    assert [c[-1] for c in seen if '-a' in c] == restored * 3
    # Snapshot cũ kê nhầm nhóm lồng cũng không được thêm membership trực tiếp cho user.
    assert not any(c[-1] in background for c in seen if '-a' in c)
```

Test chỉ dùng cây tạm/adapter giả; audit ACL và quyền thực vẫn là cổng máy B.
Không đổi quyền file nên không có migration ownership hai pha hay snapshot từng inode cần hoàn tác.

## Task 4 — G4.3: bản chép launchctl, canary, đối chứng thật theo wrapper và receipt dọn

**Files:**
- Modify: `tram/giao_viec/kich_ban_nghiem_thu.py`
- Modify: `tram/giao_viec/nghiem_thu_kiem.py`
- Modify: `tram/giao_viec/chung_cu_probe.py`
- Create: `tram/giao_viec/mau_g4.py`
- Create: `tram/giao_viec/do_launchd_g4.py`
- Create: `tram/giao_viec/nghiem_thu_doc.py`
- Test: `tests/test_siet_g4.py`
- Test: `tests/test_canary_g4.py`
- Test: `tests/test_nghiem_thu_doc_g4.py`

**Hợp đồng:** thực hiện sau Task 1–3, dùng các pin `tram.kiem.toolchain` đã khai. Harness S6 hiện tại
thêm `submitcopy`, `launchdcopy` vào bảng nguồn “CÀI ĐƯỢC”. CLI bổ sung
`python -m tram.giao_viec.nghiem_thu_doc --dong-y-g4` dành riêng phép đo G4 đã được Đại ca duyệt;
không tự mở S6, không tạo runner tách phiên D159. G3.12 chưa đạt thì S6 vẫn đóng.

CLI cần dấu `kiem-lai.dong`, xác minh UID khác root/operator và giữ khóa. Chuẩn bị canary giả trong nhà
operator và `/private/tmp` (DAC mở), đường symlink/firmlink, mẫu trong LUOT; không đọc `.env` hay dữ liệu thật.
Canary chỉ xuất match/no-match + stat/list yes/no. Smoke dựng venv `--without-pip`, xác minh base_prefix,
uv/Git/Node/npm đúng pin, env riêng/offline; mỗi lệnh qua `pk.boc_luot(luot)`.
Ma trận launchctl gốc/copy × ngoài/trong × submit/bootstrap dùng `/bin/sleep 10` cố định, plist RunAtLoad,
không KeepAlive. Byte-copy được `cmp`, `help submit` chứng minh exec; lỗi126/127 hoặc thiếu exec control
không thành bằng chứng IPC. Mã khác0 vẫn chưa chứng minh Seatbelt: phải đối chiếu bằng chứng OS.

Receipt ghi trước thao tác launchd, cập nhật trạng thái trước từng ca, chỉ các nhãn của run trong
user/UID kiểm, gui/UID kiểm, gui/operator. Quan sát service + PID sống + UID/ruid/lstart, bootout nhãn chính xác,
kiểm service vắng và PID hết. Lỗi quan sát/dọn hoặc lọt trong hồ sơ dừng; giữ fixture/receipt để phục hồi.
Không nhận mã lỗi không kèm chứng cứ vắng là đã sạch. GUI vắng chỉ nhận đúng mã112 + thông báo đầy đủ gắn UID; lỗi quyền không được nhận là vắng;
người chạy phải phân biệt bằng quan sát OS, không suy “0 PID” thành “không job”.

- [ ] **Step 1 — tạo các test nguyên văn dưới đây.**

`tests/test_siet_g4.py` (file mới):

```python
"""Chỉ sinh/đọc kịch bản; không chạy launchctl hay đụng nhà người vận hành."""
import json
from pathlib import Path

import pytest

from tram.giao_viec import kich_ban_nghiem_thu as kb
from tram.giao_viec.chung_cu_probe import muc_lich


def test_copy_launchctl_co_doi_chung_exec_va_nhan_rieng(tmp_path):
    a = kb.kich_ban_tai_sinh(tmp_path / 'a')
    b = kb.kich_ban_tai_sinh(tmp_path / 'b')
    assert 'submitcopy' in kb.NGUON and 'launchdcopy' in kb.NGUON
    assert 'cp /bin/launchctl "$PWD/launchctl-copy"' in a
    assert 'cmp -s /bin/launchctl "$PWD/launchctl-copy"' in a
    assert '"$PWD/launchctl-copy" help submit' in a
    assert 'probe:execcopy:' in a
    assert '"$PWD/launchctl-copy" submit' in a
    assert '"$PWD/launchctl-copy" bootstrap' in a
    assert '<key>RunAtLoad</key><true/>' in a
    assert 'KeepAlive' not in a
    assert kb.nhan_luot(tmp_path / 'a') in a
    assert kb.nhan_luot(tmp_path / 'a') not in b


@pytest.mark.parametrize('ma', [126, 127])
def test_loi_exec_khong_duoc_tinh_la_toi_ipc(ma):
    dat, ly_do = muc_lich(f'probe:submitcopy:bat-dau\nprobe:submitcopy:ket:{ma}\n', 'submitcopy')
    assert dat is False
    assert 'exec' in ly_do


def test_receipt_giu_dung_mien_nhan_run_khong_bootout_ca_mien(tmp_path):
    from tram.giao_viec.mau_g4 import ghi_receipt, lenh_don
    tep = tmp_path / 'receipt.json'
    ghi_receipt(tep, tmp_path / 'dau', 503, 501)
    receipt = json.loads(tep.read_text())
    assert receipt['trang_thai'] == 'chua-do'
    assert {x['mien'] for x in receipt['dich']} == {'user/503', 'gui/503', 'gui/501'}
    assert len(receipt['dich']) == 12
    cmds = lenh_don(receipt)
    assert len(cmds) == 12
    assert all(cmd[:2] == ['/bin/launchctl', 'bootout'] and cmd[2].count('/') == 2 for cmd in cmds)
    with pytest.raises(FileExistsError):
        ghi_receipt(tep, tmp_path / 'dau', 503, 501)
    receipt['dich'][0]['nhan'] = 'vn.tram.nho'
    with pytest.raises(ValueError):
        lenh_don(receipt)


def test_harness_ghi_receipt_truoc_khi_cai_lich(tmp_path, monkeypatch, tram_home_tam):
    from types import SimpleNamespace
    from tram.giao_viec import nghiem_thu_kiem as nt
    monkeypatch.setattr(nt, 'git_nhap', lambda *a: 'sha')
    monkeypatch.setattr(nt, 'commit_nhap', lambda *a: 'sha')
    monkeypatch.setattr(nt, 'kiem_lai', lambda *a, **k: SimpleNamespace(loi=None, ket_qua=[]))
    observed = []
    def tai_sinh(*a):
        observed.extend((tram_home_tam / 'log' / 'nghiem-thu').glob('receipt-*.json'))
        return []
    monkeypatch.setattr(nt, '_tai_sinh', tai_sinh)
    pk = SimpleNamespace(ten='gia', boc_lenh=lambda a: a, kill_nhom=lambda *a: None)
    goc = tmp_path / 'kiem'
    goc.mkdir()
    nt.nghiem_thu(pk, goc, cong=None, boc_luot=None, thu_hoi=lambda: None, khang_dinh={},
                 tai_sinh=True, xac_minh=lambda *a: 503, dau_goc=tmp_path)
    assert len(observed) == 1
    assert json.loads(observed[0].read_text())['trang_thai'] == 'chua-do'


@pytest.mark.parametrize('prep', ['', 'probe:execcopy:bat-dau\nprobe:execcopy:ket:126\n'])
def test_copy_that_bai_thieu_doi_chung_exec_khong_la_bang_chung(prep):
    log = prep + 'probe:submitcopy:bat-dau\nprobe:submitcopy:ket:1\n'
    assert muc_lich(log, 'submitcopy')[0] is False


def test_copy_exec_tot_lenh_that_bai_van_chi_vang():
    log = 'probe:execcopy:bat-dau\nprobe:execcopy:ket:0\nprobe:submitcopy:bat-dau\nprobe:submitcopy:ket:1\n'
    assert muc_lich(log, 'submitcopy')[0] is None
```

`tests/test_canary_g4.py` (file mới):

```python
"""Canary dữ liệu giả ở tmp_path; tuyệt đối không đọc nhà thật."""
import subprocess

from tram.giao_viec import kich_ban_nghiem_thu as kb


def test_canary_chi_bao_khop_khong_in_noi_dung(tmp_path):
    mau = tmp_path / 'mau'
    mau.write_text('CANARY-NOT-A-SECRET-DO-NOT-PRINT')
    target = tmp_path / 'du lieu'
    target.mkdir()
    tep = target / 'canary'
    tep.write_bytes(mau.read_bytes())
    link = tmp_path / 'link'
    link.symlink_to(tep)
    script = kb.kich_ban_canary([tep, link, target / 'vang'], mau)
    result = subprocess.run(['/bin/sh', '-c', script], capture_output=True, text=True, check=True)
    assert result.stdout.splitlines() == ['0:match:yes:yes', '1:match:yes:yes', '2:no-match:no:yes']
    assert result.stderr == ''
    assert mau.read_text() not in result.stdout


def test_doi_chung_dung_cung_script_va_wrapper_that(tmp_path):
    from tram.giao_viec.mau_g4 import do_canary
    calls = []

    class PK:
        def boc_lenh(self, args):
            return ['ngoai', *args]

        def boc_luot(self, luot):
            assert luot == tmp_path
            return lambda args: ['trong', *args]

    def chay(argv, **kw):
        calls.append((argv, kw))
        return subprocess.CompletedProcess(argv, 0, '0:match:yes:yes\n' if argv[0] == 'ngoai' else '0:no-match:no:no\n')

    result = do_canary(PK(), tmp_path, [tmp_path / 'canary'], tmp_path / 'mau', chay=chay)
    assert result == {'ngoai': ['0:match:yes:yes'], 'trong': ['0:no-match:no:no']}
    assert calls[0][0][1:] == calls[1][0][1:]
    assert all(call[1]['timeout'] == 15 for call in calls)


def test_doi_chung_loi_khong_chep_dau_ra(tmp_path):
    from tram.giao_viec.mau_g4 import do_canary
    class PK:
        boc_lenh = staticmethod(lambda args: args)
        boc_luot = staticmethod(lambda luot: lambda args: args)
    result = do_canary(PK(), tmp_path, [tmp_path / 'canary'], tmp_path / 'mau',
                       chay=lambda *a, **k: subprocess.CompletedProcess(a, 0, 'SECRET-RAW'))
    assert result == {'ngoai': None, 'trong': None}


def test_doc_duoc_khac_mau_khong_tinh_la_bi_chan(tmp_path):
    mau, tep = tmp_path / 'mau', tmp_path / 'canary'
    mau.write_text('one'); tep.write_text('two')
    result = subprocess.run(['/bin/sh', '-c', kb.kich_ban_canary([tep], mau)],
                            capture_output=True, text=True, check=True)
    assert result.stdout == '0:different:yes:yes\n'
```

`tests/test_nghiem_thu_doc_g4.py` (file mới):

```python
"""G4 CLI: chỉ adapter giả, không sudo/launchctl ghi, không nhà thật."""
import json
from types import SimpleNamespace

import pytest


def test_cli_khong_dong_y_khong_doc_cau_hinh(monkeypatch):
    from tram.giao_viec import nghiem_thu_doc as g4
    monkeypatch.setattr(g4, '_cau_hinh', lambda: pytest.fail('không được nạp cấu hình'))
    assert g4.main([]) == 2


def test_fixture_co_home_operator_dac_mo_symlink_va_positive(tmp_path):
    from tram.giao_viec.mau_g4 import tao_mau
    home = tmp_path / 'home'
    home.mkdir()
    calls = []
    chay = lambda argv: calls.append(argv) or (0, b'')
    pk = SimpleNamespace(boc_lenh=lambda a: ['uid-503', *a])
    fixture = tao_mau(pk, tmp_path / 'luot', home, tmp_path, chay)
    assert fixture['home'].is_relative_to(home)
    assert fixture['dac'].stat().st_mode & 0o777 == 0o644
    assert fixture['dac'].parent.stat().st_mode & 0o777 == 0o755
    assert len(fixture['tep']) == 5
    assert fixture['tep'][-1] == tmp_path / 'luot' / 'mau'
    assert 'ln -s' in calls[0][-1]
    assert 'CANARY' not in repr(fixture)


def test_controls_bat_buoc_ngoai_trong_va_receipt_truoc_lenh(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    receipt = tmp_path / 'receipt.json'
    calls = []
    pk = SimpleNamespace(boc_lenh=lambda a: ['ngoai', *a], boc_luot=lambda p: lambda a: ['trong', *a])
    def chay(argv):
        assert receipt.exists()
        calls.append(argv)
        if argv[-1] == 'submit' and 'help' in argv:
            return 0, b''
        if '/bin/sh' in argv:
            return 0, b''
        if 'print' in argv or 'bootout' in argv:
            return 113, ('Could not find service ' + argv[-1].rsplit('/', 1)[-1]).encode()
        return 1, b'PRIVATE-RAW'
    rows = do_launchd(pk, tmp_path, receipt, 503, 501, chay)
    assert {r['ho_so'] for r in rows} == {'ngoai', 'trong'}
    assert {r['binary'] for r in rows} == {'goc', 'copy'}
    assert {r['lenh'] for r in rows} == {'submit', 'bootstrap'}
    assert 'PRIVATE-RAW' not in repr(rows)
    assert len(rows) == 8
    assert any('submit' in a for a in calls) and any('bootstrap' in a for a in calls)
    assert json.loads(receipt.read_text())['trang_thai'] == 'da-don'


def test_fixture_receipt_co_truoc_khi_gui_lenh_cho_principal(tmp_path):
    from tram.giao_viec.mau_g4 import tao_mau
    receipt = tmp_path / 'fixture.json'
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    def chay(argv):
        data = json.loads(receipt.read_text())
        assert data['luot'] == str(tmp_path / 'luot')
        assert data['home'].startswith(str(tmp_path))
        return 0, b''
    tao_mau(pk, tmp_path / 'luot', tmp_path, tmp_path, chay, receipt=receipt)


def test_quan_sat_khong_doc_duoc_mien_dung_ngay(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    rows = do_launchd(pk, tmp_path, tmp_path / 'r.json', 503, 501, lambda argv: (5, b'PRIVATE'))
    assert len(rows) == 1 and rows[0]['don'] is False
    assert 'PRIVATE' not in repr(rows)


def test_service_duoc_nhan_nhung_chua_chay_van_la_lot(tmp_path):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    seen = set()
    def chay(argv):
        target = argv[-1]
        if target not in seen:
            seen.add(target)
            return 0, b'state = waiting'
        return 113, b'Could not find service nhan'
    observed, clean = _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay)
    assert len(observed) == 3 and all(r['pid'] is None for r in observed)
    assert clean is False


def test_receipt_luu_chung_cu_huu_han_sau_moi_ca(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    receipt = tmp_path / 'r.json'
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    do_launchd(pk, tmp_path, receipt, 503, 501, lambda argv: (5, b'PRIVATE'))
    data = json.loads(receipt.read_text())
    assert data['trang_thai'] == 'can-don'
    assert len(data['ket_qua']) == 1
    assert 'PRIVATE' not in receipt.read_text()


def test_smoke_dung_toolchain_ghim_va_boc_luot(tmp_path):
    from tram.giao_viec.mau_g4 import smoke_toolchain
    calls = []
    pk = SimpleNamespace(boc_luot=lambda p: lambda a: ['ho-so', *a])
    result = smoke_toolchain(pk, tmp_path, lambda argv: calls.append(argv) or (0, b'PRIVATE'))
    assert all(result.values()) and len(result) == 6
    assert all(a[0] == 'ho-so' for a in calls)
    assert any('--without-pip' in a for a in calls)
    assert 'PRIVATE' not in repr(result)


@pytest.mark.parametrize('ps_rc, ps_out', [(1, b''), (0, b'PRIVATE'),
                                          (0, b'503 501 Sun Oct 18 12:00:00 2026')])
def test_khong_xac_nhan_danh_tinh_thi_chua_sach(ps_rc, ps_out):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    seen = set()
    ps_calls = 0
    def chay(argv):
        nonlocal ps_calls
        if '/bin/ps' in argv:
            ps_calls += 1
            return (ps_rc, ps_out) if ps_calls % 2 else (1, b'')
        target = argv[-1]
        if target not in seen:
            seen.add(target)
            return 0, b'pid = 4242'
        return 113, b'Could not find service nhan'
    observed, clean = _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay)
    assert clean is False
    assert 'PRIVATE' not in repr(observed)


def test_vang_phai_dung_ma_va_dung_nhan():
    from tram.giao_viec.do_launchd_g4 import _vang
    assert not _vang(5, b'Could not find service nhan', 'nhan')
    assert not _vang(113, b'Could not find service nhan-khac', 'nhan')
    assert _vang(113, b'Could not find service "nhan" in domain for user gui: 501', 'nhan')


def test_sudo_loi_canary_khong_chay_launchd(tmp_path, monkeypatch, tram_home_tam):
    from tram.giao_viec import nghiem_thu_doc as g4
    monkeypatch.setattr(g4, 'tao_mau', lambda *a, **k: {'tep': [], 'mau': tmp_path})
    monkeypatch.setattr(g4, 'smoke_toolchain', lambda *a: {'python': True})
    monkeypatch.setattr(g4, 'do_canary', lambda *a, **k: {'ngoai': None, 'trong': None})
    monkeypatch.setattr(g4, 'do_launchd', lambda *a: pytest.fail('canary lỗi phải dừng'))
    result = g4.nghiem_thu(None, tmp_path, 503, home=tmp_path, tam=tmp_path)
    assert result['don'] is False


def test_submit_nhan_nhung_khong_tim_duoc_mien_khong_tinh_sach(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    def chay(argv):
        if 'print' in argv:
            return 113, ('Could not find service ' + argv[-1].rsplit('/', 1)[-1]).encode()
        return 0, b''
    rows = do_launchd(pk, tmp_path, tmp_path / 'r.json', 503, 501, chay)
    assert len(rows) == 1 and rows[0]['don'] is False


@pytest.mark.parametrize('rc, clean', [(112, True), (1, False)])
def test_mien_gui_vang_khac_khong_co_quyen(tmp_path, rc, clean):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    def chay(argv):
        if argv[-1].startswith('gui/503/'):
            return rc, b'Bad request.\nCould not find domain for user gui: 503\n'
        return 113, b'Could not find service nhan'
    observed, result = _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay)
    assert observed == [] and result is clean
```

- [ ] **Step 2 — RED:** chạy ba file test G4 ở bước GREEN bên dưới trước áp mã.
Vòng review bắt thêm: nhầm lỗi 5 thành service vắng, nhầm tên nhãn gần giống, canary đọc được nhưng khác mẫu,
canary lỗi vẫn thử launchd, submit nhận nhưng không tìm được miền, và nhầm GUI vắng với không có quyền.
Xem bằng chứng thật ở cuối; mọi adapter ghi launchd đều giả.

- [ ] **Step 3 — áp mã nguyên văn.**

`tram/giao_viec/kich_ban_nghiem_thu.py`:

```diff
diff --git a/tram/giao_viec/kich_ban_nghiem_thu.py b/tram/giao_viec/kich_ban_nghiem_thu.py
index 051bda4..0467187 100644
--- a/tram/giao_viec/kich_ban_nghiem_thu.py
+++ b/tram/giao_viec/kich_ban_nghiem_thu.py
@@ -5,2 +5,3 @@ từ chối khi UID là người vận hành); dưới hồ sơ đúng thì mọ
 của harness dựng bằng `git_nhap`/`commit_nhap` (không hook, không cấu hình global/system)."""
+import shlex
 import subprocess
@@ -9,2 +10,3 @@ from pathlib import Path
 from tram.giao_viec.chung_cu_probe import boc_probe
+from tram.giao_viec.mau_g4 import nhan_luot

@@ -24,3 +26,3 @@ KHANG_DINH = {
 }
-NGUON = ("cron", "at", "submit", "launchd", "setsid")
+NGUON = ("cron", "at", "submit", "launchd", "setsid", "submitcopy", "launchdcopy")

@@ -33,12 +35,21 @@ def kich_ban_tai_sinh(dau: Path) -> str:
     hồi cùng lệnh kiểm."""
-    plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>vn.tram.nghiem-'
-             f'thu.launchd</string><key>ProgramArguments</key><array><string>/usr/bin/touch</string><string>{dau}/'
-             'launchd</string></array><key>StartInterval</key><integer>150</integer></dict></plist>')
-    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau}/cron" | crontab -',
-           f'echo "/usr/bin/touch {dau}/at" | at now + 3 minutes',
-           f'launchctl submit -l vn.tram.nghiem-thu.submit -- /bin/sh -c "sleep 150; touch {dau}/submit"',
-           f"printf '%s' '{plist}' > \"$TMPDIR/nt.plist\" && "
+    nhan = nhan_luot(dau)
+    dau_q = shlex.quote(str(dau))
+    plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>'
+             f'{nhan}.launchd</string><key>ProgramArguments</key><array><string>/bin/sh</string><string>-c</string>'
+             f'<string>sleep 150; touch {dau}/launchd</string></array><key>RunAtLoad</key><true/></dict></plist>')
+    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau_q}/cron" | crontab -',
+           f'echo "/usr/bin/touch {dau_q}/at" | at now + 3 minutes',
+           f'launchctl submit -l {nhan}.submit -- /bin/sh -c "sleep 150; touch {dau_q}/submit"',
+           f"printf '%s' {shlex.quote(plist)} > \"$TMPDIR/nt.plist\" && "
            'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist"',
            f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")'"]
-    return "\n".join(["echo kich-ban-bat-dau", *map(boc_probe, NGUON, cai), "sleep 20", "exit 0", ""])
+    cai += [cai[2].replace('launchctl ', '\"$PWD/launchctl-copy\" ').replace('.submit ', '.submitcopy '),
+            cai[3].replace('launchctl ', '\"$PWD/launchctl-copy\" ').replace('.launchd<', '.launchdcopy<')
+            .replace('nt.plist', 'nt-copy.plist')]
+    prep = ('cp /bin/launchctl "$PWD/launchctl-copy" && '
+            'cmp -s /bin/launchctl "$PWD/launchctl-copy" && "$PWD/launchctl-copy" help submit')
+    return "\n".join(["echo kich-ban-bat-dau", boc_probe('execcopy', prep), "wait",
+                      *map(boc_probe, NGUON, cai), "sleep 20", "exit 0", ""])
+

@@ -60 +71,13 @@ def commit_nhap(kho: Path, tep: dict[str, str], tu: str | None) -> str:
     return git_nhap(kho, "rev-parse", "HEAD")
+
+
+def kich_ban_canary(tep: list[Path], mau: Path) -> str:
+    """Chỉ đọc dữ liệu GIẢ được chuẩn bị cho G4; không in nội dung, tên con hay metadata."""
+    dong = []
+    for i, p in enumerate(tep):
+        q, cha = shlex.quote(str(p)), shlex.quote(str(p.parent))
+        dong.append(f'r=no-match; s=no; l=no; if /bin/cat {q} >/dev/null 2>&1; then r=different; '
+                    f'cmp -s {q} {shlex.quote(str(mau))} && r=match; fi; '
+                    f'/usr/bin/stat -L {q} >/dev/null 2>&1 && s=yes; '
+                    f'/bin/ls -A {cha} >/dev/null 2>&1 && l=yes; echo {i}:$r:$s:$l')
+    return '\n'.join(dong)
```

`tram/giao_viec/nghiem_thu_kiem.py`:

```diff
diff --git a/tram/giao_viec/nghiem_thu_kiem.py b/tram/giao_viec/nghiem_thu_kiem.py
index d776332..7f793cf 100644
--- a/tram/giao_viec/nghiem_thu_kiem.py
+++ b/tram/giao_viec/nghiem_thu_kiem.py
@@ -22,2 +22,3 @@ from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
 from tram.giao_viec.chung_cu_probe import doc_probe, muc_lich
+from tram.giao_viec.mau_g4 import receipt_truoc_luot
 from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, NGUON, commit_nhap, git_nhap, kich_ban_tai_sinh
@@ -30,3 +31,2 @@ LOI = (OSError, subprocess.SubprocessError, ValueError, LoiDanhTinh, LoiThuHoi)

-
 def _muc(ten: str, dat: bool | None, chi_tiet: str) -> MucKiem:
@@ -34,3 +34,2 @@ def _muc(ten: str, dat: bool | None, chi_tiet: str) -> MucKiem:

-
 def _kiem_an_toan(kiem, *a) -> tuple[object | None, str | None]:
@@ -48,3 +47,3 @@ def nghiem_thu(pk, goc: Path, *, cong, boc_luot, thu_hoi, khang_dinh: dict = KHA
         try:
-            xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
+            uid = xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
         except (LoiDanhTinh, LoiThuHoi) as e:
@@ -79,2 +78,4 @@ def nghiem_thu(pk, goc: Path, *, cong, boc_luot, thu_hoi, khang_dinh: dict = KHA
         if tai_sinh:
+            if kich_ban is kich_ban_tai_sinh:
+                receipt_truoc_luot(dau, uid)
             ra += _tai_sinh(kiem, kho, goc_sha, sha, kd, dau, kich_ban, cho, ngu)
@@ -95,3 +96,2 @@ def nghiem_thu(pk, goc: Path, *, cong, boc_luot, thu_hoi, khang_dinh: dict = KHA

-
 def _tai_sinh(kiem, kho: Path, goc_sha: str, sha: str, kd: dict, dau: Path, kich_ban, cho: float, ngu) -> list:
```

`tram/giao_viec/chung_cu_probe.py`:

```diff
diff --git a/tram/giao_viec/chung_cu_probe.py b/tram/giao_viec/chung_cu_probe.py
index 4c9a431..649ba8f 100644
--- a/tram/giao_viec/chung_cu_probe.py
+++ b/tram/giao_viec/chung_cu_probe.py
@@ -53,2 +53,6 @@ def muc_lich(log: str, nguon: str) -> tuple[bool | None, str]:
         return False, "CÀI ĐƯỢC — hồ sơ không chặn"
+    if nguon in {"submitcopy", "launchdcopy"} and ma in {126, 127}:
+        return False, "bản chép lỗi exec/tìm lệnh — chưa tới IPC; sửa phép đo"
+    if nguon in {"submitcopy", "launchdcopy"} and doc_probe(log, "execcopy") != 0:
+        return False, "chưa chứng minh bản chép exec được — chưa kết luận IPC"
     ld = ly_do(log, nguon)
```

`tram/giao_viec/mau_g4.py` (file mới):

```python
"""Dựng dữ liệu giả của G4; không đọc dữ liệu cá nhân có sẵn."""
import json
import hashlib
import os
import re
import subprocess
import secrets
import shlex
from pathlib import Path


def tao_mau(pk, luot: Path, home: Path, tam: Path, chay, *, receipt: Path | None = None) -> dict:
    run = secrets.token_hex(12)
    cay_home, cay_dac = home / f'tram-g4-canary-{run}', tam / f'tram-g4-dac-{run}'
    if receipt is not None:
        with receipt.open('x') as f:
            json.dump({'luot': str(luot), 'home': str(cay_home), 'dac': str(cay_dac)}, f)
            f.flush()
            os.fchmod(f.fileno(), 0o600)
            os.fsync(f.fileno())
    dau = secrets.token_hex(32)
    for cay in (cay_home, cay_dac):
        cay.mkdir()
        cay.chmod(0o755)
        (cay / 'canary').write_text(dau)
        (cay / 'canary').chmod(0o644)
    q = shlex.quote
    mau, link = luot / 'mau', luot / 'canary-link'
    script = (f'mkdir -p {q(str(luot))} {q(str(luot) + ".nha/tmp")}; '
              f'printf %s {q(dau)} > {q(str(mau))}; '
              f'ln -s {q(str(cay_home / "canary"))} {q(str(link))}; '
              f'cp /bin/launchctl {q(str(luot / "launchctl-copy"))} && '
              f'cmp -s /bin/launchctl {q(str(luot / "launchctl-copy"))}')
    ma, _ = chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
    if ma != 0:
        raise ValueError('không dựng được fixture G4; giữ cây để kiểm/dọn')
    tep_home, tep_dac = cay_home / 'canary', cay_dac / 'canary'
    firmlink = Path('/System/Volumes/Data') / tep_home.relative_to('/')
    return {'home': tep_home, 'dac': tep_dac, 'mau': mau, 'tep': [tep_home, link, firmlink, tep_dac, mau]}


def smoke_toolchain(pk, luot: Path, chay) -> dict[str, bool]:
    from tram.kiem.toolchain import PYTHON, UV, GIT, NODE, bien_kiem
    env = ['/usr/bin/env', '-i', f'HOME={luot}.nha', f'TMPDIR={luot}.nha/tmp',
           *(f'{k}={v}' for k, v in bien_kiem(f'{luot}.nha').items()), 'UV_OFFLINE=1']
    lenh = {
        'venv': [f'{PYTHON}/bin/python3.12', '-B', '-I', '-m', 'venv', '--without-pip', str(luot / 'venv')],
        'python': [str(luot / 'venv/bin/python'), '-I', '-B', '-c',
                   f'import sys; assert sys.base_prefix == {PYTHON!r}'],
        'uv': [f'{UV}/bin/uv', '--version'], 'git': [f'{GIT}/bin/git', '--version'],
        'node': [f'{NODE}/bin/node', '--version'], 'npm': [f'{NODE}/bin/npm', '--version'],
    }
    return {ten: chay(pk.boc_luot(luot)([*env, *argv]))[0] == 0 for ten, argv in lenh.items()}


def do_canary(pk, luot: Path, tep: list[Path], mau: Path, *, chay=subprocess.run) -> dict:
    """Bên gọi chuẩn bị LUOT/NHA, mẫu và canary; chỉ trả mã hữu hạn, lỗi/timeout thành None."""
    from tram.giao_viec.kich_ban_nghiem_thu import kich_ban_canary
    script = kich_ban_canary(tep, mau)
    ra = {}
    for ten, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        try:
            kq = chay(boc(['/bin/sh', '-c', script]), capture_output=True, text=True, timeout=15)
            dong = kq.stdout.splitlines()
            hop_le = len(dong) == len(tep) and all(
                re.fullmatch(rf'{i}:(match|different|no-match):(yes|no):(yes|no)', d) for i, d in enumerate(dong))
            ra[ten] = dong if kq.returncode == 0 and hop_le else None
        except (OSError, subprocess.SubprocessError):
            ra[ten] = None
    return ra


NGUON_LAUNCHD = ('submit', 'launchd', 'submitcopy', 'launchdcopy')


def nhan_luot(dau: Path) -> str:
    return 'vn.tram.nghiem-thu.' + hashlib.sha256(str(dau).encode()).hexdigest()[:24]


def ghi_receipt(tep: Path, dau: Path, uid_kiem: int, uid_tram: int) -> None:
    if uid_kiem <= 0 or uid_tram <= 0 or uid_kiem == uid_tram:
        raise ValueError('UID nghiệm thu phải khác nhau và khác root')
    nhan = nhan_luot(dau)
    dich = [{'mien': m, 'nhan': f'{nhan}.{n}'} for m in
            (f'user/{uid_kiem}', f'gui/{uid_kiem}', f'gui/{uid_tram}') for n in NGUON_LAUNCHD]
    with tep.open('x', encoding='utf-8') as f:
        json.dump({'run': nhan, 'trang_thai': 'chua-do', 'dich': dich}, f, ensure_ascii=False)
        f.flush()
        os.fchmod(f.fileno(), 0o600)
        os.fsync(f.fileno())


def lenh_don(receipt: dict) -> list[list[str]]:
    """Chỉ sinh argv để chủ miền duyệt/chạy; không biến exit 0 thành chứng cứ sạch."""
    run = receipt.get('run', '')
    if not re.fullmatch(r'vn\.tram\.nghiem-thu\.[a-f0-9]{24}', run):
        raise ValueError('run receipt sai dạng')
    ra = []
    for dich in receipt['dich']:
        mien, nhan = dich['mien'], dich['nhan']
        if not re.fullmatch(r'(user|gui)/[1-9][0-9]*', mien) or nhan not in {
            f'{run}.{n}' for n in NGUON_LAUNCHD
        }:
            raise ValueError('đích dọn không thuộc receipt của run')
        ra.append(['/bin/launchctl', 'bootout', f'{mien}/{nhan}'])
    return ra


def receipt_truoc_luot(dau: Path, uid_kiem: int) -> None:
    import os
    from tram.duong_dan import tram_home
    goc = tram_home() / 'log' / 'nghiem-thu'
    goc.mkdir(parents=True, exist_ok=True)
    ghi_receipt(goc / f'receipt-{nhan_luot(dau)}.json', dau, uid_kiem, os.getuid())
```

`tram/giao_viec/do_launchd_g4.py` (file mới):

```python
"""Ma trận launchctl G4 dùng sleep cố định; receipt trước ghi; không coi lỗi OS là Seatbelt chặn."""
import json
import os
import plistlib
import re
import shlex
import time
from tempfile import NamedTemporaryFile
from pathlib import Path

from tram.giao_viec.mau_g4 import ghi_receipt, nhan_luot


def _ghi(tep: Path, **gia_tri) -> None:
    data = json.loads(tep.read_text())
    data.update(gia_tri)
    with NamedTemporaryFile(mode='w', dir=tep.parent, delete=False) as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    Path(f.name).replace(tep)


def _vang(ma, out: bytes, nhan: str) -> bool:
    pattern = rb'Could not find service \"?' + re.escape(nhan.encode()) + rb'\"?(?: in domain[^\n]*)?\s*'
    return ma == 113 and re.fullmatch(pattern, out.strip()) is not None


def _quan_sat_don(pk, mien: list[str], nhan: str, chay) -> tuple[list[dict], bool]:
    thay, sach = [], True
    for m in mien:
        boc = (lambda a: a) if m == mien[-1] else pk.boc_lenh
        target = f'{m}/{nhan}'
        ma, out = chay(boc(['/bin/launchctl', 'print', target]))
        vang_mien = (m.startswith('gui/') and ma == 112 and out.strip() ==
                     f"Bad request.\nCould not find domain for user gui: {m.split('/')[1]}".encode())
        if _vang(ma, out, nhan) or vang_mien:
            continue
        pid = re.search(rb'^\s*pid = ([1-9][0-9]*)\s*$', out, re.M) if ma == 0 else None
        if ma != 0:
            sach = False
            continue
        row = {'mien': m, 'co_service': True, 'pid': int(pid[1]) if pid else None, 'danh_tinh': None}
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            text = ps.decode(errors='replace').strip()
            if rc == 0 and re.fullmatch(r'\d+\s+\d+\s+\w{3}\s+\w{3}\s+\d+\s+[\d:]+\s+\d{4}', text):
                row['danh_tinh'] = text
                allowed = {int(mien[0].split('/')[1]), int(mien[-1].split('/')[1])}
                uid, ruid = map(int, text.split()[:2])
                sach = sach and uid == ruid and uid in allowed
        sach = sach and row['danh_tinh'] is not None
        thay.append(row)
        chay(boc(['/bin/launchctl', 'bootout', target]))
        rc, con = chay(boc(['/bin/launchctl', 'print', target]))
        sach = sach and _vang(rc, con, nhan)
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            sach = sach and rc == 1 and not ps.strip()
    return thay, sach


def do_launchd(pk, luot: Path, receipt: Path, uid: int, operator: int, chay) -> list[dict]:
    ghi_receipt(receipt, luot, uid, operator)
    nhan = nhan_luot(luot)
    mien = [f'user/{uid}', f'gui/{uid}', f'gui/{operator}']
    rows = []
    for ho_so, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        for binary, exe in (('goc', '/bin/launchctl'), ('copy', str(luot / 'launchctl-copy'))):
            exec_ma, _ = chay(boc([exe, 'help', 'submit']))
            for op in ('submit', 'bootstrap'):
                bat_dau = time.monotonic()
                def case_chay(argv):
                    if time.monotonic() - bat_dau > 45:
                        raise TimeoutError('ca G4 hết ngân sách 60 giây')
                    return chay(argv)
                nguon = ('submit' if op == 'submit' else 'launchd') + ('copy' if binary == 'copy' else '')
                label = f'{nhan}.{nguon}'
                if op == 'submit':
                    argv = [exe, op, '-l', label, '--', '/bin/sleep', '10']
                else:
                    p = luot / f'{nguon}.plist'
                    data = plistlib.dumps({'Label': label, 'ProgramArguments': ['/bin/sleep', '10'],
                                           'RunAtLoad': True}).decode()
                    script = f'printf %s {shlex.quote(data)} > {shlex.quote(str(p))}'
                    rc, _ = case_chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
                    if rc != 0:
                        raise ValueError('không dựng được plist G4')
                    argv = [exe, op, mien[0], str(p)]
                _ghi(receipt, trang_thai='can-don', ca_hien_tai=f'{ho_so}:{binary}:{op}')
                ma, _ = case_chay(boc(argv))
                thay, sach = _quan_sat_don(pk, mien, label, case_chay)
                sach = sach and not (ma == 0 and not thay)  # Nhận job nhưng mất dấu miền: giữ fixture.
                ket_luan = 'chua-ket-luan'
                if ho_so == 'trong' and (ma == 0 or thay):
                    ket_luan = 'lot'
                elif sach and exec_ma == 0:
                    if ho_so == 'ngoai' and ma == 0 and thay:
                        ket_luan = 'doi-chung-duong'
                    elif ho_so == 'trong' and ma not in (None, 0):
                        ket_luan = 'cho-bang-chung-os'
                rows.append({'ket_luan': ket_luan, 'ho_so': ho_so, 'binary': binary, 'lenh': op, 'exec_ma': exec_ma,
                             'ma': ma, 'service': thay, 'don': sach})
                _ghi(receipt, trang_thai='da-don' if sach else 'can-don', ket_qua=rows)
                if not sach or (ho_so == 'trong' and (ma == 0 or thay)):
                    return rows
    return rows
```

`tram/giao_viec/nghiem_thu_doc.py` (file mới):

```python
"""CLI G4 dữ liệu giả, chỉ chạy sau duyệt riêng; không mở S6 hay bỏ dấu đóng cổng."""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.mau_g4 import do_canary
from tram.giao_viec.do_launchd_g4 import do_launchd
from tram.giao_viec.mau_g4 import tao_mau, smoke_toolchain
from tram.kiem.danh_tinh import xac_minh_uid
from tram.kiem.lenh_ngan import chay_ngan


def _cau_hinh():
    from tram.giao_viec.lenh_nghiem_thu import _pk_goc
    return _pk_goc()


def _chay(argv):
    return chay_ngan(['/bin/sh', '-c', 'exec "$@" 2>&1', '--', *argv], timeout=15, doc=True)


def _adapter(chay):
    def run(argv, **kw):
        ma, out = chay(argv)
        return subprocess.CompletedProcess(argv, 255 if ma is None else ma, out.decode(errors='replace'))
    return run


def nghiem_thu(pk, goc: Path, uid: int, *, home: Path, tam: Path, chay=_chay) -> dict:
    luot = goc / f'g4-{secrets.token_hex(12)}'
    log = tram_home() / 'log' / 'nghiem-thu'
    log.mkdir(parents=True, exist_ok=True)
    receipt = log / f'{luot.name}.json'
    meta = log / f'{luot.name}-fixture.json'
    fixture = tao_mau(pk, luot, home, tam, chay, receipt=meta)
    smoke = smoke_toolchain(pk, luot, chay)
    if not all(smoke.values()):
        return {'toolchain': smoke, 'don': False, 's6': 'dong'}
    canary = do_canary(pk, luot, fixture['tep'], fixture['mau'], chay=_adapter(chay))
    expected = ['0:no-match:no:no', '1:no-match:no:yes', '2:no-match:no:no',
                '3:no-match:no:no', '4:match:yes:yes']
    outside = canary.get('ngoai')
    if canary.get('trong') != expected or not outside or outside[3:] != ['3:match:yes:yes', '4:match:yes:yes']:
        return {'toolchain': smoke, 'canary': canary, 'don': False, 's6': 'dong'}
    launchd = do_launchd(pk, luot, receipt, uid, os.getuid(), chay)
    sach = len(launchd) == 8 and all(r['don'] for r in launchd)
    if sach:
        ma, _ = chay(pk.boc_lenh(['/bin/rm', '-rf', '--', str(luot), f'{luot}.nha']))
        sach = ma == 0
    if sach:
        for p in (fixture['home'].parent, fixture['dac'].parent):
            shutil.rmtree(p)
    return {'toolchain': smoke, 'canary': canary, 'launchd': launchd, 'don': sach, 's6': 'dong'}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='G4: canary giả + launchctl cố định ngoài/trong hồ sơ')
    p.add_argument('--dong-y-g4', action='store_true', help='Chỉ dùng sau khi Đại ca duyệt đúng kịch bản G4')
    args = p.parse_args(argv)
    if not args.dong_y_g4:
        print('Chưa chạy: cần duyệt canary trong nhà và đối chứng launchd của G4.', file=sys.stderr)
        return 2
    try:
        if not (tram_home() / 'kiem-lai.dong').is_file():
            raise ValueError('phải giữ dấu kiem-lai.dong trước nghiệm thu')
        pk, goc = _cau_hinh()
        uid = xac_minh_uid(pk.ten, pk.boc_lenh, pk.kill_nhom)
        with giu_khoa():
            kq = nghiem_thu(pk, goc.resolve(strict=True), uid, home=Path.home(),
                            tam=Path('/private/tmp'))
        print(json.dumps(kq, ensure_ascii=False))
        return 1                         # không chứng nhận OS/S6 tự động, kể cả mọi lệnh đã dọn
    except (OSError, ValueError, RuntimeError) as e:
        print(f'G4 dừng: {type(e).__name__}; giữ cổng đóng và receipt để kiểm/dọn.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
```

- [ ] **Step 4–5 — GREEN + regression:**

```bash
tests/chan_host/chay.sh -q tests/test_nghiem_thu_doc_g4.py tests/test_siet_g4.py tests/test_canary_g4.py tests/test_chung_cu_probe.py tests/test_do_dai_ma.py
```

Bằng chứng vòng review gộp các task ở cuối. Harness chạy thật, nguồn context và thu hồi tiến trình vẫn
phải đo riêng, không miễn chỉ vì unit test xanh.

- [ ] **Step 6 — chỉ sau phê duyệt OS riêng: chạy phép đo từ Terminal của operator.**

Không chạy các lệnh dưới trong phiên viết plan. Các Task1–3 phải được triển khai/cài lại, hồ sơ/manifest khớp,
không có lượt repo thật đồng thời, dấu đóng cổng vẫn còn. Đối chiếu build/context/G3.12 theo sổ tay;
chạy G4 không thay chứng cứ tách phiên D159. Lệnh đo hoàn chỉnh, không điền mẫu:

```bash
cd '/Users/dai-ca/Developer/Ben Station'
UV_NO_SYNC=1 uv run --offline python -m tram.giao_viec.nghiem_thu_doc --dong-y-g4
```

CLI cố ý mã1 và `s6: dong` kể cả đã dọn: cần biên bản OS. Nhìn sáu boolean toolchain; bất kỳ false thì
không có ma trận launchd, sửa đúng pin/phụ thuộc trước. Canary thứ tự: home, symlink, firmlink, DAC-mở, LUOT.
Ngoài hồ sơ DAC-mở và LUOT phải match; trong hồ sơ LUOT phải match, các đường ngoài phải no-match (không đọc được); different nghĩa đọc được nhưng khác mẫu, phải dừng.
Ngoài hồ sơ home không đọc được sau siết nhóm chỉ chứng minh DAC; dùng canary DAC-mở phân biệt rào Seatbelt.
Stat/list riêng, nhớ parent symlink trong LUOT có thể list được; không đòi giấu metadata chính symlink trong LUOT.

Launchd: đối chứng ngoài hồ sơ submit gốc và copy phải có service/PID sống/UID hợp lệ. Chỉ `ma=0`
chưa đủ là job đã chạy. Trong hồ sơ copy phải `exec_ma=0`, submit/bootstrap không được nhận hay có service.
Đối chứng bootstrap ngoài hồ sơ cũng thất bại thì ghi rào OS nền, không nhận làm chứng cứ riêng Seatbelt.
`exec_ma` khác0, mã5, thiếu PID, miền không quan sát được, hết hạn hay dọn không rõ đều chưa kết luận.
Một lệnh ≤15s, mỗi ca ngân sách60s; sleep job tối đa10s. Job nhận trong hồ sơ dù chưa PID vẫn là lọt.

- [ ] **Step 7 — nếu ngắt/lỗi: phục hồi đúng receipt, không bootout cả miền.**

Đoạn hoàn chỉnh dưới chỉ chạy sau Đại ca duyệt dọn đúng run. Chọn số receipt được liệt kê; mã không chép
raw service output. Nó xác minh UID hiện hành, khóa, chỉ nhận đúng ba miền và nhãn của run; dọn từng nhãn,
quan sát PID/định nghĩa service. Miền không đọc được hoặc lỗi không khớp mẫu đã đo giữ kết quả chưa rõ và không xóa fixture.
Fixture-only receipt (lỗi trước khi thử launchd) vẫn dọn được vì launchd receipt bắt buộc có trước thao tác.

```bash
UV_NO_SYNC=1 uv run --offline python - <<'PYRECOVER'
import json
import os
import re
import shutil
from pathlib import Path
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.mau_g4 import lenh_don
from tram.giao_viec.do_launchd_g4 import _quan_sat_don, _ghi
from tram.giao_viec.nghiem_thu_doc import _cau_hinh, _chay
from tram.kiem.danh_tinh import xac_minh_uid
log = tram_home() / 'log' / 'nghiem-thu'
files = sorted([*log.glob('g4-*-fixture.json'), *log.glob('receipt-*.json')])
for i, f in enumerate(files):
    print(i, f.name)
if not files:
    raise SystemExit('Không có receipt của G4.')
index = int(input('Số receipt của đúng run đã duyệt dọn: '))
if not 0 <= index < len(files):
    raise SystemExit('Số không hợp lệ.')
f = files[index]
meta = f if f.name.endswith('-fixture.json') else None
receipt = f.with_name(f.name.replace('-fixture', '')) if meta else f
pk, goc = _cau_hinh()
uid = xac_minh_uid(pk.ten, pk.boc_lenh, pk.kill_nhom)
mien = [f'user/{uid}', f'gui/{uid}', f'gui/{os.getuid()}']
with giu_khoa():
    sach = True
    if receipt.exists():
        data = json.loads(receipt.read_text())
        lenh_don(data)
        assert {d['mien'] for d in data['dich']} == set(mien)
        for nhan in sorted({d['nhan'] for d in data['dich']}):
            observed, clean = _quan_sat_don(pk, mien, nhan, _chay)
            print(json.dumps({'nhan': nhan, 'quan_sat': observed, 'sach': clean}))
            sach = sach and clean
        _ghi(receipt, trang_thai='da-don' if sach else 'can-don')
    if sach and meta:
        fixture = json.loads(meta.read_text())
        luot = Path(fixture['luot'])
        assert luot.parent == goc and re.fullmatch(r'g4-[a-f0-9]{24}', luot.name)
        rc, _ = _chay(pk.boc_lenh(['/bin/rm', '-rf', '--', str(luot), f'{luot}.nha']))
        assert rc == 0
        for key, parent, prefix in [('home', Path.home(), 'tram-g4-canary-'),
                                    ('dac', Path('/private/tmp'), 'tram-g4-dac-')]:
            tree = Path(fixture[key])
            assert tree.parent == parent and re.fullmatch(prefix + r'[a-f0-9]{24}', tree.name)
            assert not tree.is_symlink()
            if tree.exists():
                shutil.rmtree(tree)
    print('Đã dọn đúng run; S6 vẫn đóng.' if sach else 'Chưa xác nhận sạch; giữ fixture/receipt và S6 đóng.')
PYRECOVER
```

Không chạy tiếp ca sau nếu chưa biết miền thực/UID bất thường/dọn chưa rõ. Chứng cứ này chỉ cho đúng
build/context/profile và submit/bootstrap đã đo; không tuyên bố mọi XPC/API đều qua một hook.
Đối chứng chủ miền gui/operator và runner tách phiên vẫn theo G3.12, không tự mở rộng sang system bootstrap.
Commit/ghép do điều phối sau QC; task này không có bước commit trong phiên chuẩn bị plan.

## Kiểm chứng review vòng 1 — 19/10/2026

HEAD `ba13fa8`; cây đầu sạch. Áp thử đúng các khối mã/test của plan này trong worktree, không áp plan D157.
`git apply --check` các diff bản đầu đạt. Chỉ test giả qua bộ chặn; không sudo, dscl/sysadminctl,
launchctl ghi, Keychain hay sửa cấu hình thật. Các con số bản soạn đã thay bằng bằng chứng dưới đây.

- RED bản đầu: **40 failed, 1 passed**; thiếu module/contract đúng các task. Áp bản đầu: **48 passed**
  (gồm trần dòng và vòng import).
- RED sửa policy/nhóm/G4: **5 failed, 22 passed**; thiếu quyền hệ thống/offline, sharepoint .7 không gỡ,
  nhóm admin không dừng trước ghi, `_vang` nhận lỗi 5, canary lỗi vẫn gọi launchd.
- RED audit lỗi đọc cây: **1 failed, 3 passed** (`KeyError: onerror`).
- RED đối chứng: **2 failed, 16 passed** (khác mẫu bị báo no-match; submit nhận mất dấu vẫn sạch).
- RED preflight: **2 failed, 13 passed** (cài lại bỏ qua migration; thiếu kiểm repo trong nhà operator).
- RED miền GUI: **1 failed, 1 passed, 14 deselected**; mã112 GUI không tồn tại bị gộp với lỗi quan sát.
- GREEN cuối: **164 passed**, 0 failed, **0 dòng chặn mới, 0 điểm mù, 0 push giả lập**; lệnh dưới.
  Test rollback nhóm dở dang là bổ sung kiểm sau khi sửa, không nhận là một ca RED đã đo trước sửa.

```bash
tests/chan_host/chay.sh -q tests/test_siet_doc_plan.py tests/test_siet_python_plan.py tests/test_nhom_rieng.py tests/test_siet_nhom_migration.py tests/test_siet_g4.py tests/test_canary_g4.py tests/test_nghiem_thu_doc_g4.py tests/test_manifest_ho_so.py tests/test_ho_so_kiem_lai.py tests/test_quyen_kiem.py tests/test_dinh_danh_cai.py tests/test_so_cai_tho.py tests/test_go_cai_lai.py tests/test_go_cai_dat_tho.py tests/test_cai_dat_tho_kiem.py tests/test_chung_cu_probe.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

Cả bộ với `--maxfail=1`: **1 failed, 106 passed / 20.71s**, 0 dòng chặn; lỗi
`test_hai_tien_trinh_tram_api_cung_yeu_cau_chi_mot_feature` tại passkey `Mã không hợp lệ hoặc hết hạn`,
peer `BrokenBarrierError`. Chạy riêng khi còn áp mã: **1 passed / 2.42s**; sau hoàn nguyên đúng HEAD,
chạy lại cùng file: **1 failed / 12.01s**, cùng lỗi passkey/barrier, 0 dòng chặn.
Lỗi tái hiện cả trên HEAD; chưa có toàn bộ xanh, chưa xác định nguyên nhân sâu và không tự sửa ngoài phạm vi.

Relocation thật chỉ trong thư mục tạm, cùng UID operator, không Seatbelt/root install: dùng đúng
`phan_python` chụp nguồn 3.12.15/build20261009, ghi **1.887 file / 2.067 tài nguyên R2**; interpreter mới
import `ssl/sqlite3/ctypes/venv/sysconfig` đạt, `sys.prefix` + `sysconfig.get_path('stdlib')` ở prefix mới,
dựng venv `--without-pip` và `sys.base_prefix` đạt. Chưa chứng minh mọi shebang, SDK, dylib hoặc dự án thật.
`otool -L` executable nguồn không có dylib trong nhà Đại ca; các extension động vẫn cần smoke dưới hồ sơ.

Nguồn OS cục bộ build **24G90**: `/usr/share/man/man8/dseditgroup.8`, `/usr/share/man/man1/dscl.1`,
usage string của `/usr/sbin/sysadminctl` có `-addUser ... -GID`; không gọi các lệnh quản lý user thật.
Đối chiếu `/System/Library/Sandbox/Profiles/dyld-support.sb` và `system.sb`: thêm đúng cây dyld/Cryptex,
timezone, regex neo đầu/cuối cho `/dev/fd/[0-9]+`; không import nguyên policy Apple.
Quan sát chỉ đọc `launchctl print gui/2147483646` và đích service dưới miền đó: mã112, đúng
`Bad request.\nCould not find domain for user gui: 2147483646`; `user/2147483646` báo thiếu quyền,
không được nhận là vắng. Unit test không chứng minh profile được Seatbelt biên dịch/chạy thành công.

## Kết luận và kiểm chứng review vòng 2 — 19/10/2026

**ĐẠT về review plan với phương án cuối ghi trong file này.** Không còn CHẶN phải chép bản chạy
thợ ra ngoài nhà. Nhận đề xuất ACL quản lý, không nhận chuỗi cài prefix theo lô nguyên trạng
(vì các rủi ro cụ thể tại quyết định Task 2); giữ trình cài từng file hiện có. Không có placeholder
triển khai mới; module, script, test và diff ACL được ghi nguyên văn. Các cổng OS không đổi.

- HEAD `754da6a`, cây đầu sạch. Đọc CHUNG, báo cáo vòng 1, luật/tài liệu sở hữu và D159; review theo
  skill `code-review-and-quality`, kiểm chứng theo `verification-before-completion`.
- Đối chiếu `/usr/share/man/man1/chmod.1` cục bộ: `user:` phân biệt user với group cùng tên;
  `search` là tra tên, `list` là liệt kê; `+a`/`-a` thêm/gỡ ACE. Không cấp inherit/list/write.
  Không chạy chmod ACL thật hoặc sudo; chưa chứng minh quyền hiệu lực trên máy B.
- RED test ACL đầu: **4 failed**, `ImportError: cannot import name 'acl_tho' from 'scripts'`;
  sau tách phần tài nguyên sang `tram.chu.acl_tho`, test import theo vị trí cuối. Test bổ sung
  GUID/crash/parse/plist được chạy GREEN, không nhận là RED đã đo trước sửa.
- GREEN cuối: **181 passed / 5.64s**, gồm 9 test ACL, migration, policy, Python, G4,
  cài/gỡ/R2, trần dòng và vòng import. **0 dòng chặn mới, 0 điểm mù, 0 push giả lập.**
- Cả bộ `tests/chan_host/chay.sh -q --maxfail=1`: **1 failed, 172 passed / 21.11s**,
  lỗi `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`:
  `LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`.
  **0 dòng chặn, 0 điểm mù**, 14 push được giả lập. Sau hoàn nguyên chính xác HEAD,
  chạy riêng đúng test đó: **1 failed / 8.60s**, cùng lỗi, 0 dòng chặn, 2 push giả lập.
  Đây là lỗi tái hiện cả trên HEAD trong môi trường này; chưa có cả bộ xanh, không sửa ngoài phạm vi.
- 19 file mới trong plan khớp từng byte với cây đã thử; các khối Python biên dịch cú pháp được.
  Diff áp ngược lên cây thử và áp xuôi lên HEAD đều qua. Mã/test đã hoàn nguyên bằng byte HEAD,
  xóa đúng file mới đã tạo; chỉ giữ plan và REVIEW-CODEX.md. Không sửa CURRENT_STATE, Beads hay handover.

Lệnh GREEN cuối (sau khối môi trường kiểm chứng):

```bash
tests/chan_host/chay.sh -q tests/test_acl_tho_plan.py tests/test_siet_doc_plan.py tests/test_siet_python_plan.py tests/test_nhom_rieng.py tests/test_siet_nhom_migration.py tests/test_siet_g4.py tests/test_canary_g4.py tests/test_nghiem_thu_doc_g4.py tests/test_manifest_ho_so.py tests/test_ho_so_kiem_lai.py tests/test_quyen_kiem.py tests/test_dinh_danh_cai.py tests/test_so_cai_tho.py tests/test_go_cai_lai.py tests/test_go_cai_dat_tho.py tests/test_cai_dat_tho_kiem.py tests/test_cai_nha_tho.py tests/test_chung_cu_probe.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

## Rủi ro còn lại / phụ thuộc / câu hỏi cho Đại ca

- **G3.12/D159 giai đoạn 2:** còn cần số đo và bộ chạy system không kế thừa phiên Đại ca. Không có mã
  bộ chạy đó trong plan này. Siết đọc đạt cũng không mở S6.
- **Quản lý tin cậy:** dùng repo hiện tại qua ACL search riêng có R2. Search không giới hạn đường con:
  `tram-tho` biết tên vẫn đọc được file world-readable qua các thư mục đi được. Đây là chấp nhận tin cậy
  đối với quản lý, không phải cam kết giữ kín nhà Đại ca trước quản lý bị chiếm. Khe/kiểm không có ACL.
- **Máy B:** cần chứng minh Python sau chuyển vị trí, dylib/config/SDK cần thiết, venv và các lệnh kiểm thực;
  nếu chưa đủ quyền đọc chỉ bổ sung literal/prefix có bằng chứng rồi đổi manifest, không mở rộng toàn cây.
- **Nhóm và ownership:** user cũ chỉ được chuyển khi UID/GUID khớp R2. ACL hoặc đường cấu hình không có
  biên nhận sẽ bị script giữ lại; Đại ca cần audit riêng, không cho nhận làm của trạm bằng cách sửa sổ.
- **G4:** copied launchctl phải exec được và control ngoài hồ sơ tạo job đúng UID, rồi đường trong hồ sơ
  phải bị chặn ở thao tác tạo job; mã lỗi chung không đủ. Canary dùng dữ liệu giả, chỉ boolean; không log mẫu.
- **G5:** ngoại lệ Apple của khe thợ phải đo riêng, xem plan D157; không mượn danh sách của tram-kiem.
- **Đề xuất cho Đại ca khi duyệt:** dùng ba nhóm riêng và Python cục bộ 3.12.15/build20261009 làm nguồn
  đã kiểm SHA; duyệt riêng kịch bản máy B sau khi bộ hồi quy chạy ngoài sandbox xanh. Chưa thao tác máy thật.

## Ghi chú triển khai

Chưa triển khai sản phẩm. Vòng review chỉ giữ file plan này và `REVIEW-CODEX.md`; mọi file mã/test áp tạm
được hoàn nguyên đúng HEAD hoặc xóa nếu mới tạo. Không commit, không sửa CURRENT_STATE/handover/Beads.
**Review plan không phải giấy phép chạy máy B.** Còn nghiệm thu ACL/config/quyền thực,
Seatbelt + toolchain + G4 thật và hồi quy cả bộ ngoài sandbox. D159 vẫn chặn S6 độc lập với lát siết đọc này.
