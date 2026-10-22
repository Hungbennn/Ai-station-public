# Plan 3c — bản làm việc sau chốt đợt 6, 16/10/2026

> **Review đợt 7 (17/10/2026):** trạng thái vận hành hiện hành theo [phụ lục cổng](../handovers/2026-10-17-cong-sau-review-dot7.md) và [plan V2](../plans/2026-10-17-lat-v2-va-sau-review-dot7.md). Các chữ ĐẠT/count bên dưới giữ làm lịch sử tác giả; không vượt blockers review mới. Khi khác nhau về lệnh thử/cleanup hoặc readiness, phụ lục đợt 7 ưu tiên; quyết định D1–D53 giữ nguyên.


**Hướng đã duyệt theo D45; C01/C02/R7 chưa nghiệm thu. Chưa được chạy S6.**

> **Đợt 7 (16/10/2026):**
> - 3C-A đã có thiết kế: khả thi trong D45, **có điều kiện G4**.
> - 3C-C đã có mã TDD đầy đủ.
> - 3C-D1–D4 đã có mã TDD đầy đủ. 3C-D5 chờ P1/3C-B; 3C-D6 chờ r47 T6/T7.
> - Toàn bộ đã chạy thử trên bản sao: `main 5da881e` + r47 đợt 1–2 + 1a-2 T5 (chỉ mã). Kết quả: 2242 → 2280 → 2303 → **2351 passed**.
> - Đã qua một vòng review đối kháng cho mỗi phần, và đã sửa theo review.
> - Thứ tự ghép: **1a-2 T5 → 3c**.
> - Chưa review Codex, chưa có bằng chứng OS.
>
> **Đợt 8 (16/10/2026) — trên `main` `0e33fbf` (P1 + 3C-B + Q1/Q2 + đợt 7 đã ghép, N₀ = 2650):**
> - 3C-D5 (thu hồi theo UID qua P1, xác minh bằng ảnh chụp `ps`; phần Q01 còn giữ của r47 T11), 3C-D6 (hồ sơ cho cả hai cơ chế; `tram giao kiem` dưới khoá; khung quan sát launchd — cổng đóng tới khi G3 đo định dạng), áp hợp đồng P1 H1–H8, harness S6 thay r47 T12: **mã TDD đầy đủ**, 8 task, chạy thử thật **2650 → 2696 passed**, nhật ký chặn host rỗng.
> - Hai chu kỳ review đối kháng (ngữ cảnh mới); không có cross-model (ngữ cảnh không tương tác).
> - Task 9 (S6) viết lại thành kịch bản G3/G4 — **CHƯA CHẠY, chờ Đại ca duyệt**. G4 cần thêm 3C-D7 (bộ đọc launchd, sau G3).
Đọc [quyết định mới](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md), [kế hoạch tích hợp](../../tasks/plan.md) và [cổng chạy thật](../handovers/2026-10-15-so-tay-chay-that.md).

Bản r47 sau review được lưu nguyên văn ở [lịch sử 3c](../lich-su-dot6/2026-10-15-lat-3c-principal-kiem-trao-quyen.md). Các phần không bị thay dưới đây vẫn là đầu vào tái sử dụng sau khi đối chiếu source hiện tại. Không trích/chạy toàn bộ bản lịch sử như plan hiện hành. T2/T4/R3 có phần đã ghép: kiểm diff, không code lại.

## Hợp đồng hiện hành và phần bị thay

| Phần r47 | Quy tắc hiện hành |
|---|---|
| G6/G22/G25, T11 `_sot`, cleanup hai lượt | Chỉ là quan sát bổ trợ. Phải có boundary cưỡng chế nơi ghi/nguồn thực thi và thu hồi trước lượt kế tiếp. Không coi scan sạch là cách ly. |
| T12 daemon thread + `join(timeout)` | Hết hiệu lực. Tiến trình con phải quản lý được, có deadline cho cancel/kill/wait/cleanup. Lỗi cleanup giữ gate đóng. |
| Guard `getpass.getuser()` và argv khác nhau | Không đủ. So UID hiệu lực của tiến trình dưới đúng wrapper với UID tài khoản mục tiêu và UID người vận hành trước mọi thao tác lịch. |
| HOME/TMP và home tài khoản | `/var/empty` làm home tài khoản, HOME/TMP riêng từng lượt; không tự chạy createhomedir. Không suy ra đủ cách ly từ HOME mới. |
| Câu hỏi r47 về lịch/baseline | Lịch ngoài allowlist hoặc quan sát lỗi → không hợp lệ và chặn lượt sau. Mốc launchd do Đại ca ghi nhận khi được phép, phải review lại sau cập nhật OS; không thay boundary. |
| cron.deny/at.deny | Chưa sửa. Không tự thêm tài nguyên mới vào installer/journal. |
| R7 synthetic repo | Giữ repo một commit D40; phải chứng minh đúng cây nguồn, không normalize âm thầm khi archive/init/add. |
| T11 returncode (dot6-Q01) | Giữ sửa getconf/xóa/xác nhận và 3 ca fake regression. Không đóng C01 bằng sửa này. |

## Task 3C-A — thiết kế boundary (ĐÃ THIẾT KẾ đợt 7; chờ review và G4)

Thiết kế đầy đủ, bảng threat → control 31 hàng, đánh giá hướng, phương án thay kiến trúc: [phụ lục thiết kế 3C](../handovers/2026-10-16-thiet-ke-3c-boundary.md).

**Kết luận:** C01 **khả thi trong D45, có điều kiện G4**. Cưỡng chế bằng hồ sơ Seatbelt cấm mặc định cho mọi lệnh của lượt (3C-D1), thu hồi theo UID (3C-D5, cần P1 và 3C-B), cổng lượt bền fail-closed (3C-D2, 3C-D4), quan sát chỉ là dây báo (3C-D3, T11). Không root lúc chạy, không VM, không sửa `cron.deny`/`at.deny`, không coi mốc launchd là bằng chứng.

Chạy thử (không phải bằng chứng G4): dưới user hiện tại, macOS 15.6.1, hồ sơ do 3C-D1 sinh ra, chỉ trong thư mục tạm:
- bị chặn:
  - ghi vào thư mục 0777 ngoài lượt; ghi qua symlink; hardlink từ ngoài; `rename` ra ngoài; `chmod` tệp ngoài;
  - `mkdir` lượt khác cùng gốc; đọc `.env.testing` của lượt cũ cùng gốc; liệt kê gốc; đọc kho trạm;
  - exec `crontab -l` và `launchctl`;
  - `shm_open`, `sem_open`;
  - `bind`/`connect` mạng;
- vẫn chạy: ghi `LUOT`/`NHA`/HOME/TMPDIR của lượt, git `init`/`status`, sh, python, node, php, npm (bản hồ sơ đầu).

**Điều kiện chỉ chứng minh trên OS (G4).** Thiếu (1) hoặc (2) thì C01 không đóng được trong D45 → trình phương án A1/A2/A3 của phụ lục §5 (khuyến nghị A1: pool user dùng một lần, bảo trì root do Đại ca).
1. Seatbelt giữ dưới `sudo -u tram-kiem` và qua exec setuid (`crontab`/`at`).
2. `job-creation` chặn `launchctl submit/bootstrap` và XPC thẳng tới launchd ở `user/<uid>`, `gui/<uid>`, `login/<asid>`.
3. `mach-lookup` tối thiểu đủ cho bộ test thật của HR.
4. `kill -1` thu hồi đủ.

**Còn hở, ghi rõ:**
- Kênh dư chỉ dùng được khi thông đồng: POSIX semaphore có tên, notifyd state.
- SysV IPC chưa có quan sát.
- Chưa có quan sát cho miền `login/<asid>`: chờ G3 đo định dạng, không viết parser đoán.
- Thư mục ghi qua nhóm `staff` không được quan sát; chỉ có cưỡng chế chặn.
- Tiến trình setuid không giết được: cổng đóng, tức là hỏng khả năng chạy tiếp chứ không lọt.

**Câu Đại ca cần biết** (phụ lục §6):
- Q-A: kiểm lại không còn dùng được DB/Redis dùng chung.
- Q-B: cổng đóng thì dừng mọi kiểm lại tới khi Đại ca mở lại.
- Q-C: R7 từ chối thêm một số loại repo.

## Task 3C-B — vòng đời process và UID (sau hợp đồng process P1)

Files trọng tâm: `tram/kiem/chay_lenh.py`, module CLI/harness hiện tại, test runner/UID; cùng primitive process với plan quota.

Nghiệm thu: toàn bộ đợi/kết thúc có hạn; timeout không chỉ trả khỏi thread; giữ quyền sở hữu process tree để thu hồi. Kiểm UID thực bằng probe không có tác dụng phụ dưới đúng wrapper trước thao tác lịch. Sai UID, wrapper lỗi, không đọc được identity → không gọi cron/at/launchctl. Cleanup không xác nhận được → trả lỗi riêng, không giải phóng gate cho lượt sau. Không giết rộng theo username hay nhầm process của Đại ca.

Xác minh: fake runner spy cho sai UID, env giả mạo, wrapper bất thường, exception, timeout; test child/grandchild treo chỉ trong môi trường kiểm thử bỏ được và không cài lịch. Đo deadline, xác nhận không còn child khi báo cleanup đạt. Mọi kiểm macOS thật nằm sau gate vận hành.

## Task 3C-C — cây Git đúng nguồn (R7) — mã TDD đầy đủ

**Quy mô:** M · **Đợt:** sau r47 T3+T10 (bản chép + repo một commit), độc lập P1/3C-B · **Không sửa** `noi_that.py`.

**Nền chạy thử:** `main 5da881e` + mã/test đợt 1–2 của r47 (T1, T3, T5, T10 — áp nguyên từ bản sao `c7716aa` đã kiểm ở r47, khớp byte với plan lịch sử). N = **2280** trên nền đó (2242 + 38 của r47, đúng số r47 ghi "N₀ + 38"). Khi Claude triển khai: đo lại sau khi T3/T10 thật đã ghép; lệch thì dừng.

**Files:**
- Modify: `tram/giao_viec/cay_kiem.py` (môi trường git của trạm cô lập, ghim cấu hình archive, `loi_cau_hinh_kho`, `cay_goc`)
- Modify: `tram/giao_viec/repo_ban_chep.py` (`_git`, `lenh_cay`, `core.ignorecase=false`)
- Modify: `tram/giao_viec/ban_chep.py` (`CayKhacNguon`, so cây, `--no-mac-metadata`)
- Modify: `tram/giao_viec/kiem_lai.py` (bắt `CayKhacNguon` → `loi="cay-khac-nguon"`)
- Modify: `tram/giao_viec/tick_pipeline.py` (`cay-khac-nguon` như `thieu-moi-truong-kiem`: escalation, không ghi `kiem.lai`)
- Modify: `tram/giao_viec/escalation.py`, `tram/suy/mau_su_kien.py` (lý do escalation mới + câu hỏi + nhãn)
- Test: `tests/test_ban_chep_cay.py`, `tests/test_ban_chep_cay_kho.py` (mới)

**Interfaces:**
- Consumes: `chep_ban`, `LoiBanChep`, `_chay`, `TAR_NHAN` (T3); `lenh_repo`, `MOI_TRUONG`, `CAU_HINH` (T10); `nguon_archive`, `_git` (T3); fixture `m`, `ban_chep` (`tests/test_kiem_lai_principal.py`, T3); `dung`, `bug`, `xin`, `bao`, `PASS`, `F`, `bg` (tests có sẵn 4a-1).
- Produces: `CayKhacNguon(LoiBanChep)`; `cay_goc(kho, commit) -> str`; `loi_cau_hinh_kho(kho) -> str | None`; `lenh_cay(wt) -> list[str]`; `KetQuaKiemLai.loi == "cay-khac-nguon"`; escalation `ly_do="cay-khac-nguon"`.

**Hợp đồng (G-C1…G-C5):**
- Bằng chứng duy nhất của "đúng nguồn" là **mã cây**: `git rev-parse HEAD^{tree}` trong bản chép (dưới `tram-kiem`) phải bằng `<commit>^{tree}` của kho kiểm. Bằng nhau ⇔ cùng tập đường dẫn/mode/blob (gồm CRLF, encoding, symlink, bit thực thi). Đồng thời đây là bằng chứng cây làm việc khứ hồi được qua `.gitattributes` của commit. Không "sửa cho khớp" (không renormalize, không chạy filter).
- `git archive` của trạm bỏ mọi `GIT_*`, cấu hình global/system/`XDG` attributes, `refs/replace`; ghim `core.autocrlf=false`, `core.eol=lf`, `core.attributesFile=/dev/null`, `core.ignorecase=false`, `core.protectHFS/NTFS=true`. Kho kiểm có `filter.*` (kể cả LFS cục bộ) → từ chối. Phía bản chép thêm `core.ignorecase=false` để khớp thuộc tính giống archive.
- Không khớp → `CayKhacNguon` TRƯỚC khi nhận môi trường kiểm và trước mọi lệnh kiểm; `kiem_lai` vẫn dọn bản chép (finally) rồi trả `KetQuaKiemLai(False, loi="cay-khac-nguon")`; vòng tick tạo escalation, **không** ghi `kiem.lai`, không thử lại mãi (lỗi tất định — review đối kháng đợt 7 mục 1).
- Lớp repo nay bị từ chối (đã đo): blob CRLF dưới `text`/`text=auto`/`eol=crlf`, dòng lẫn CRLF/LF dưới `text=auto`, `$Id: …$` đã mở dưới `ident`, submodule, trùng tên hoa-thường trên APFS, tệp `._*` (bsdtar coi là metadata), kho sha256, kho kiểm có `filter.*`. Giữ được: `eol=crlf` với blob LF, CRLF không thuộc tính, `working-tree-encoding`, `ident` chuẩn, LFS con trỏ (bản chép mang con trỏ — test cần nội dung LFS sẽ fail, ghi rõ), nhị phân, symlink, bit thực thi, tên NFD. Câu hỏi Q-C của phụ lục thiết kế: Đại ca cần biết, không tự nới.

- [ ] **Step 1: Viết test thất bại**

`tests/test_ban_chep_cay.py` (mới):

```python
"""R7 (lát 3c, 3C-C): cây git của bản chép phải ĐÚNG cây commit gốc — CRLF/`.gitattributes`, encoding, ident, mode,
symlink. `git archive` của trạm không mang cấu hình git riêng của trạm; `git add` trong bản chép chuẩn hoá khác commit
gốc, trùng tên hoa-thường hay submodule → `CayKhacNguon`, không chạy lệnh kiểm. `git` THẬT trong `tmp_path`."""
import os
import subprocess

import pytest

from git_gia import MOI_TRUONG, git
from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec.ban_chep import CayKhacNguon, LoiBanChep, chep_ban
from tram.giao_viec.kiem_lai import kiem_lai

PHP = "* text=auto\n"
LFS = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"0" * 64 + b"\nsize 3\n"


def dung_commit(kho, tep: dict) -> str:
    """Commit con của origin/main qua lệnh nền (giữ nguyên bytes, kể cả CRLF mà `git add` thường sẽ chuẩn hoá)."""
    env = {**MOI_TRUONG, "GIT_INDEX_FILE": str(kho / ".git" / "chi-muc-tam")}
    g = lambda *a, vao=None: subprocess.run(["git", "-C", str(kho), *a], input=vao, env=env, check=True,
                                            capture_output=True).stdout.decode().strip()
    g("read-tree", "origin/main")
    for duong, (mode, nd) in tep.items():
        sha = nd if isinstance(nd, str) else g("hash-object", "-w", "--stdin", vao=nd)
        g("update-index", "--add", "--cacheinfo", f"{mode},{sha},{duong}")
    return g("commit-tree", g("write-tree"), "-p", "origin/main", "-m", "x")


def chep(tmp_path, tep: dict, boc=lambda a: a, cau_hinh_kho: tuple = ()):
    k = dung_kho(tmp_path)
    for c in cau_hinh_kho:
        git(k.kho, "config", *c.split("="))
    sha = dung_commit(k.kho, tep)
    wt = tmp_path / "kiem" / "g-1-ab"
    chep_ban(k.kho, sha, wt, boc=boc)
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")
    return wt


def test_cay_dung_nguon_va_tep_dung_nhu_checkout(tmp_path):
    thuoc_tinh = b"*.crlf eol=crlf\n*.u16 working-tree-encoding=UTF-16\n*.c ident\n*.bin filter=lfs -text\n"
    wt = chep(tmp_path, {".gitattributes": ("100644", thuoc_tinh + PHP.encode()), "a.crlf": ("100644", b"x\ny\n"),
                         "b.u16": ("100644", "xin chào\n".encode()), "c.c": ("100644", b"/* $Id$ */\n"),
                         "d.bin": ("100644", LFS), "e.dat": ("100644", b"\0\r\n"),
                         "chay.sh": ("100755", b"#!/bin/sh\n"), "lk": ("120000", b"chay.sh"),
                         "ra": ("120000", b"../x")})
    assert (wt / "a.crlf").read_bytes() == b"x\r\ny\r\n" and (wt / "e.dat").read_bytes() == b"\0\r\n"
    assert (wt / "b.u16").read_bytes().decode("utf-16") == "xin chào\n" and (wt / "d.bin").read_bytes() == LFS
    assert b"$Id: " in (wt / "c.c").read_bytes() and os.access(wt / "chay.sh", os.X_OK)
    assert os.readlink(wt / "lk") == "chay.sh" and os.readlink(wt / "ra") == "../x"


def test_crlf_khong_thuoc_tinh_giu_nguyen(tmp_path):
    assert (chep(tmp_path, {"a.txt": ("100644", b"x\r\ny\r\n")}) / "a.txt").read_bytes() == b"x\r\ny\r\n"


@pytest.mark.parametrize("bien", [{"HOME": "NHA"}, {"GIT_CONFIG_GLOBAL": "CFG"}, {"GIT_CONFIG_SYSTEM": "CFG"},
                                  {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "filter.lfs.smudge",
                                   "GIT_CONFIG_VALUE_0": "tr a-z A-Z"}, {"XDG_CONFIG_HOME": "XDG"}])
def test_cau_hinh_git_cua_tram_khong_doi_noi_dung_ban_chep(tmp_path, monkeypatch, bien):
    nha, xdg = tmp_path / "nha", tmp_path / "xdg"
    (xdg / "git").mkdir(parents=True)
    (xdg / "git" / "attributes").write_text("* text eol=crlf\n")
    nha.mkdir()
    (nha / ".gitconfig").write_text('[core]\n\tautocrlf = true\n[filter "lfs"]\n\tsmudge = tr a-z A-Z\n\tclean = cat\n')
    for k, v in bien.items():
        monkeypatch.setenv(k, {"NHA": str(nha), "CFG": str(nha / ".gitconfig"), "XDG": str(xdg)}.get(v, v))
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.bin filter=lfs -text\n"), "a.txt": ("100644", b"x\ny\n"),
                         "d.bin": ("100644", b"abc\n")})
    assert (wt / "a.txt").read_bytes() == b"x\ny\n" and (wt / "d.bin").read_bytes() == b"abc\n"


def test_cau_hinh_rieng_cua_kho_kiem_khong_doi_noi_dung_ban_chep(tmp_path):
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.txt text\n"), "a.txt": ("100644", b"x\n"),
                         "b.md": ("100644", b"y\n")}, cau_hinh_kho=("core.autocrlf=true", "core.eol=crlf"))
    assert (wt / "a.txt").read_bytes() == b"x\n" and (wt / "b.md").read_bytes() == b"y\n"


@pytest.mark.parametrize("tep", [
    {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\ny\r\n")},
    {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\ny\n")},
    {".gitattributes": ("100644", b"*.txt eol=crlf\n"), "a.txt": ("100644", b"x\r\ny\r\n")},
    {".gitattributes": ("100644", b"*.c ident\n"), "c.c": ("100644", b"/* $Id: abc $ */\n")},
    {"sub": ("160000", "1" * 40)}], ids=["crlf-text-auto", "lan-dong", "crlf-eol-crlf", "ident-da-mo", "submodule"])
def test_cay_lech_nguon_thi_fail_closed(tmp_path, tep):
    with pytest.raises(CayKhacNguon, match="khác cây commit gốc"):
        chep(tmp_path, tep)


def test_trung_ten_hoa_thuong_tren_o_khong_phan_biet(tmp_path):
    (tmp_path / "Hoa").touch()
    if not (tmp_path / "hoa").exists():
        pytest.skip("ổ phân biệt hoa-thường: không có ca trùng tên")
    with pytest.raises(CayKhacNguon):
        chep(tmp_path, {"A.txt": ("100644", b"1"), "a.txt": ("100644", b"2")})


@pytest.mark.parametrize("thay", [["/usr/bin/false"], ["/bin/echo", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]])
def test_khong_doc_duoc_hoac_doc_sai_cay_ban_chep_thi_fail_closed(tmp_path, thay):
    with pytest.raises(LoiBanChep, match="rev-parse|khác cây commit gốc"):
        chep(tmp_path, {"a.txt": ("100644", b"x\n")}, boc=lambda a: thay if "rev-parse" in a else a)


def test_kiem_lai_cay_lech_khong_chay_lenh_va_van_don(m):
    k, da, tmp = m
    sha = dung_commit(k.kho, {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\n"),
                              "kiem.sh": ("100644", f"touch {tmp}/DA_CHAY\n".encode())})
    kq = kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"],
                  chay_lenh=True, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
                  env_goc=os.environ)
    assert (kq.dat, kq.loi) == (False, "cay-khac-nguon") and not (tmp / "DA_CHAY").exists() and ban_chep(m) == []
```

`tests/test_ban_chep_cay_kho.py` (mới):

```python
"""R7 (3C-C, sau review đối kháng): cấu hình RIÊNG của kho kiểm không đổi được bản chép (filter, ignorecase); tên NFD
giữ nguyên cây, tệp `._*` bị từ chối; cây lệch là lỗi tất định → `kiem_lai` trả `cay-khac-nguon`, vòng tick tạo
escalation, không ghi `kiem.lai`, không thử lại mãi. `git` THẬT trong `tmp_path`."""
import unicodedata

import pytest

from giao_viec_gia import bug, dung
from su_kien_gia import ds, sk
from test_ban_chep_cay import chep
from test_kich_ban_4a1 import PASS, bao, xin
from test_xet_xong import F, bg
from tram.giao_viec.ban_chep import CayKhacNguon
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick


def test_filter_rieng_cua_kho_kiem_thi_tu_choi(tmp_path):
    with pytest.raises(CayKhacNguon, match="filter"):
        chep(tmp_path, {".gitattributes": ("100644", b"*.txt filter=x\n"), "a.txt": ("100644", b"abc\n")},
             cau_hinh_kho=("filter.x.smudge=tr a-z A-Z",))


@pytest.mark.parametrize("blob, cau_hinh", [(b"x\n", ("core.ignorecase=true",)), (b"x\r\n", ())])
def test_thuoc_tinh_khop_phan_biet_hoa_thuong_ca_hai_phia(tmp_path, blob, cau_hinh):
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.TXT text eol=crlf\n"), "a.txt": ("100644", blob)},
              cau_hinh_kho=cau_hinh)                               # `*.TXT` không khớp `a.txt` ở cả archive lẫn add
    assert (wt / "a.txt").read_bytes() == blob


def test_ten_nfd_giu_nguyen_cay(tmp_path):
    chep(tmp_path, {unicodedata.normalize("NFD", "chào.txt"): ("100644", b"x")})    # `chep` so mã cây hai phía


def test_tep_appledouble_bi_tar_nuot_thi_tu_choi(tmp_path):
    with pytest.raises(CayKhacNguon):                               # bsdtar coi `._*` là metadata: cây lệch, không lọt
        chep(tmp_path, {"._ghi-chu": ("100644", b"khong phai metadata")})


def test_tick_cay_lech_tao_escalation_khong_ghi_kiem_lai(tmp_path):
    t = dung(tmp_path, bug())
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    t.k.day(p.repo.nhanh, {"a.txt": "x\r\n"}, tu=p.repo.cha)                  # blob CRLF đã theo dõi từ trước
    sha = t.k.day(p.repo.nhanh, {".gitattributes": "* text=auto\n", F: "x"})  # rồi mới thêm text=auto
    sk(t.kho, "giao.cong_bo", {"bead_id": p.bead_id, "luot": p.luot, "commit": sha, "ref": p.repo.nhanh})
    bao(t, p, "xong", commit=sha, ban_giao=bg(sha, luot=p.luot, lenh_kiem=PASS))
    mot_vong_tick(t.bo)
    assert moi_nhat(ds(t.kho), "kiem.lai") is None
    esc = [b for b in t.g.beads.values() if b.issue_type == "decision"]
    assert len(esc) == 1 and "cay-khac-nguon" in esc[0].description
    mot_vong_tick(t.bo)
    assert len([b for b in t.g.beads.values() if b.issue_type == "decision"]) == 1   # không tạo trùng
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_ban_chep_cay.py tests/test_ban_chep_cay_kho.py -q`
Expected (kết quả chạy thật): `2 errors` — `ImportError: cannot import name 'CayKhacNguon' from 'tram.giao_viec.ban_chep'`. Thêm tạm riêng lớp `CayKhacNguon` để xem lỗi hành vi: `20 failed, 3 passed` — 15 ca lệch đi tới phép so cây của test (`assert '<cây bản chép>' == '<cây gốc>'`, tức R7 có thật trên nền T10), `DID NOT RAISE` ở 2 ca rev-parse, `ValueError: ly_do escalation lạ` chưa có (ca tick); 3 ca giữ nguyên (cây đúng + checkout, CRLF không thuộc tính, NFD) xanh sẵn — cố ý, là regression giữ hành vi.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cay_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/cay_kiem.py b/tram/giao_viec/cay_kiem.py
index e28b7eb..d9bfce3 100644
--- a/tram/giao_viec/cay_kiem.py
+++ b/tram/giao_viec/cay_kiem.py
@@ -1,7 +1,11 @@
 """Cây của commit cho bản chép kiểm (D22, lát 3c) — mọi phép xét làm trên ĐỐI TƯỢNG GIT của kho kiểm (bất biến theo
 SHA), không trên đĩa mà `tram-kiem` sửa được. `info/attributes` của kho kiểm vô hiệu `export-ignore`/`export-subst`
-trong `.gitattributes` của commit (ưu tiên cao nhất theo gitattributes) — commit không giấu được file khỏi bản chép."""
+trong `.gitattributes` của commit (ưu tiên cao nhất theo gitattributes) — commit không giấu được file khỏi bản chép.
+R7: lệnh git của trạm bỏ biến `GIT_*`, cấu hình global/system, attributes ngoài và `refs/replace`; `git archive` ghim
+autocrlf/eol/ignorecase/protectHFS; kho kiểm có `filter.*` riêng thì từ chối — bản chép theo `.gitattributes` của
+commit, cùng phép mà `git add` của bản chép (`repo_ban_chep.py`) đảo lại; cây lệch thì `ban_chep` từ chối."""
 import io
+import os
 import subprocess
 import tarfile
 import time
@@ -9,10 +13,18 @@ from pathlib import Path
 
 GIT = ("git", "-c", "core.hooksPath=/dev/null")
 THUOC_TINH = "* -export-ignore -export-subst\n"
+ARCHIVE = ("-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "core.attributesFile=/dev/null", "-c",
+           "core.ignorecase=false", "-c", "core.protectHFS=true", "-c", "core.protectNTFS=true")
+
+
+def _env() -> dict[str, str]:
+    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
+    return env | {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_ATTR_NOSYSTEM": "1",
+                  "GIT_NO_REPLACE_OBJECTS": "1"}
 
 
 def _git(kho: Path, *args: str, **kw) -> subprocess.CompletedProcess:
-    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, timeout=120, **kw)
+    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, timeout=120, env=_env(), **kw)
 
 
 def loi_dich_trong_cay(kho: Path, commit: str, dich: str) -> str | None:
@@ -46,8 +58,19 @@ def chuan_bi_thuoc_tinh(kho: Path) -> None:
 def nguon_archive(kho: Path, commit: str) -> subprocess.Popen:
     """`git archive` của commit, stdout là ống — người gọi đóng ống và `wait()`."""
     chuan_bi_thuoc_tinh(kho)
-    return subprocess.Popen([*GIT, "-C", str(kho), "archive", "--format=tar", commit], stdout=subprocess.PIPE,
-                            stderr=subprocess.DEVNULL)
+    return subprocess.Popen([*GIT, *ARCHIVE, "-C", str(kho), "archive", "--format=tar", commit], env=_env(),
+                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
+
+
+def loi_cau_hinh_kho(kho: Path) -> str | None:
+    """Kho kiểm khai `filter.*` (vd LFS cục bộ) thì archive chạy smudge của trạm — bản chép không còn theo commit."""
+    r = _git(kho, "config", "--name-only", "--get-regexp", r"^filter\.", text=True)
+    return None if r.returncode == 1 else f"kho kiểm có cấu hình filter riêng (mã {r.returncode}) — không chép"
+
+
+def cay_goc(kho: Path, commit: str) -> str:
+    """Mã cây (tree) của commit trong kho kiểm — bản chép phải dựng lại ĐÚNG cây này (R7)."""
+    return _git(kho, "rev-parse", "--verify", f"{commit}^{{tree}}", check=True, text=True).stdout.strip()
 
 
 def tar_mot_tep(dich: str, du_lieu: bytes) -> bytes:
```

`tram/giao_viec/repo_ban_chep.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/repo_ban_chep.py b/tram/giao_viec/repo_ban_chep.py
index a2f7f0c..8e081b0 100644
--- a/tram/giao_viec/repo_ban_chep.py
+++ b/tram/giao_viec/repo_ban_chep.py
@@ -13,14 +13,23 @@ MOI_TRUONG = ("/usr/bin/env", "-i", "PATH=/usr/bin:/bin:/usr/sbin:/sbin", "HOME=
               "GIT_CONFIG_NOSYSTEM=1", "GIT_CONFIG_GLOBAL=/dev/null", "GIT_ATTR_NOSYSTEM=1")
 CAU_HINH = ("core.hooksPath=/dev/null", "core.attributesFile=/dev/null", "core.fsmonitor=false", "gc.auto=0",
             "maintenance.auto=false", "commit.gpgSign=false", "init.defaultBranch=kiem", "user.name=tram-kiem",
-            "user.email=tram-kiem@localhost")
+            "user.email=tram-kiem@localhost", "core.ignorecase=false")
 
 
-def lenh_repo(wt) -> dict[str, list[str]]:
-    """Ba lệnh (chạy theo thứ tự, DƯỚI `tram-kiem` qua `boc`) dựng repo một commit trong `wt`."""
+def _git(wt) -> list[str]:
     git = [*MOI_TRUONG, shutil.which("git") or "/usr/bin/git"]
     for c in CAU_HINH:
         git += ["-c", c]
-    git += ["-C", str(wt)]
+    return [*git, "-C", str(wt)]
+
+
+def lenh_repo(wt) -> dict[str, list[str]]:
+    """Ba lệnh (chạy theo thứ tự, DƯỚI `tram-kiem` qua `boc`) dựng repo một commit trong `wt`."""
+    git = _git(wt)
     return {"init": [*git, "init", "-q", "--template="], "add": [*git, "add", "-A", "-f"],
             "commit": [*git, "commit", "-q", "--allow-empty", "--no-verify", "-m", "kiem"]}
+
+
+def lenh_cay(wt) -> list[str]:
+    """In cây của HEAD bản chép (dưới `tram-kiem`) để trạm so với cây commit gốc (R7)."""
+    return [*_git(wt), "rev-parse", "--verify", "HEAD^{tree}"]
```

`tram/giao_viec/ban_chep.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/ban_chep.py b/tram/giao_viec/ban_chep.py
index eccbb40..3c5ea5b 100644
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -7,7 +7,7 @@ Cây kiểm là repo git MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo
 Fail-closed:
 - một lần kiểm lại một lúc trên máy (khoá `~/.tram/kiem-lai.khoa`, không chờ) — lần thứ hai ném `KiemLaiDangBan`;
 - `don_sach` (giết mọi tiến trình `tram-kiem`, xác nhận không còn) chạy trước khi chép và trước khi dọn — lỗi → ném;
-- `tar` hoặc `git init/add/commit` lỗi → ném `LoiBanChep`, không chạy lệnh kiểm;
+- `tar`, `git init/add/commit` lỗi hoặc cây git của bản chép khác cây commit gốc (R7) → ném, không chạy lệnh kiểm;
 - dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về."""
 import fcntl
 import os
@@ -18,11 +18,11 @@ from contextlib import contextmanager
 from pathlib import Path
 
 from tram.duong_dan import tram_home
-from tram.giao_viec.cay_kiem import loi_dich_trong_cay, nguon_archive, tar_mot_tep
-from tram.giao_viec.repo_ban_chep import lenh_repo
+from tram.giao_viec.cay_kiem import cay_goc, loi_cau_hinh_kho, loi_dich_trong_cay, nguon_archive, tar_mot_tep
+from tram.giao_viec.repo_ban_chep import lenh_cay, lenh_repo
 from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich
 
-TAR_NHAN = ("/usr/bin/tar", "-x", "-f", "-", "-C")
+TAR_NHAN = ("/usr/bin/tar", "-x", "--no-mac-metadata", "-f", "-", "-C")
 THOI_GIAN = 600
 Boc = Callable[[list[str]], list[str]]
 
@@ -35,6 +35,11 @@ class KiemLaiDangBan(LoiBanChep):
     """Đang có lần kiểm lại khác (hoặc `tram giao kiem`) giữ khoá."""
 
 
+class CayKhacNguon(LoiBanChep):
+    """Không dựng được cây đúng commit (R7: CRLF/text, ident, encoding, hoa-thường, submodule, filter riêng của kho
+    kiểm) — tất định, nên `kiem_lai` trả lỗi `cay-khac-nguon` (escalation) thay vì để vòng tick thử lại mãi."""
+
+
 @contextmanager
 def giu_khoa(p: Path | None = None):
     p = p or tram_home() / "kiem-lai.khoa"
@@ -63,7 +68,11 @@ def _chay(argv: list[str], **kw) -> subprocess.CompletedProcess:
 
 def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
     """`tram-kiem` tạo `wt` MỚI (đã có → lỗi), tự `tar -x` nội dung đúng commit từ stdin, rồi tự dựng repo git một
-    commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git."""
+    commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git. Cây của
+    repo đó phải ĐÚNG cây commit gốc (R7): `git add` chuẩn hoá khác commit thì ném, không sửa cho khớp."""
+    goc, loi = cay_goc(kho, commit), loi_cau_hinh_kho(kho)
+    if loi is not None:
+        raise CayKhacNguon(loi)
     _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
     _chay(boc(["/bin/mkdir", str(wt)]), check=True)
     nguon = nguon_archive(kho, commit)
@@ -78,6 +87,11 @@ def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
         r = _chay(boc(argv))
         if r.returncode:
             raise LoiBanChep(f"git {buoc} dưới tram-kiem lỗi (mã {r.returncode}) — bản chép không thành repo kiểm")
+    r = _chay(boc(lenh_cay(wt)))
+    if r.returncode:
+        raise LoiBanChep(f"git rev-parse dưới tram-kiem lỗi (mã {r.returncode}) — không đọc được cây bản chép")
+    if r.stdout.decode(errors="replace").strip() != goc:
+        raise CayKhacNguon(f"cây git của bản chép khác cây commit gốc {goc[:12]} (CRLF/encoding/hoa-thường/submodule)")
 
 
 def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc) -> None:
```

`tram/giao_viec/kiem_lai.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index ca7a35f..92ac80d 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -14,7 +14,7 @@ from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.lenh import khop_bat_ky
-from tram.giao_viec.ban_chep import chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
+from tram.giao_viec.ban_chep import CayKhacNguon, chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
 from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
 from tram.kiem.diff import diff_cham_cam
 from tram.kiem.moi_truong import LoiMoiTruongKiem
@@ -27,7 +27,7 @@ class KetQuaKiemLai:
     dat: bool
     ket_qua: tuple[dict, ...] = ()      # dòng `lenh_kiem[]` (lenh, ket_qua, tom_tat, digest_log)
     cham_cam: tuple[str, ...] = ()
-    loi: str | None = None              # "dong-file-cau-hinh" | "thieu-moi-truong-kiem" | None
+    loi: str | None = None              # "dong-file-cau-hinh" | "thieu-moi-truong-kiem" | "cay-khac-nguon" | None
 
     @property
     def digest_log(self) -> list[str]:
@@ -54,7 +54,10 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
             don_sach()                       # tiến trình tram-kiem của lần trước không được sống sang lần này
         wt = thu_muc / ten_ban_chep(giao_id)
         try:
-            chep_ban(kho_git, commit, wt, boc=boc)
+            try:
+                chep_ban(kho_git, commit, wt, boc=boc)
+            except CayKhacNguon:
+                return KetQuaKiemLai(False, loi="cay-khac-nguon")       # R7: tất định — escalation, không thử lại mãi
             try:
                 nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc)
             except LoiMoiTruongKiem:
```

`tram/giao_viec/tick_pipeline.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/tick_pipeline.py b/tram/giao_viec/tick_pipeline.py
index 7ca25e4..336ab4e 100644
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -44,7 +44,7 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
                   don_sach=bo.don_sach, kill=bo.kill)
     if kq.loi is not None:
         tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
-        if kq.loi == "thieu-moi-truong-kiem":
+        if kq.loi in ("thieu-moi-truong-kiem", "cay-khac-nguon"):
             return "escalation"                          # không ghi kiem.lai: trả lời xong thì kiểm lại (dòng 5)
     ghi_mot_lan(kho, da.ten, "kiem.lai", {
         "giao_id": p.giao_id, "bead_id": b.id, "luot": p.luot, "commit": sha, "digest_tieu_chi": digest_tieu_chi(
```

`tram/giao_viec/escalation.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/escalation.py b/tram/giao_viec/escalation.py
index 6e5a5ca..c83e649 100644
--- a/tram/giao_viec/escalation.py
+++ b/tram/giao_viec/escalation.py
@@ -13,14 +13,17 @@ from tram.phieu.kho import KhoPhieu
 
 NHAN = "tram:escalation"
 LY_DO = ("agent-bi", "can-thao-tac-nguy-hiem", "agent-can-hoi", "het-ngan-sach", "nhanh-bi-day",
-         "thieu-moi-truong-kiem", "dong-file-cau-hinh", "qc-doi-ma", "spec-tra-ve-nhieu", "phieu-thieu")
+         "thieu-moi-truong-kiem", "dong-file-cau-hinh", "qc-doi-ma", "spec-tra-ve-nhieu", "phieu-thieu",
+         "cay-khac-nguon")
 LY_DO_BI = {"agent": "agent-bi", "thieu-moi-truong-kiem": "thieu-moi-truong-kiem",
             "nhanh-bi-day-ngoai-luong": "nhanh-bi-day"}          # bao.bi khác (khe-tat, estop…) → giao lại
 LY_DO_HOI = {"thao_tac_nguy_hiem": "can-thao-tac-nguy-hiem", "can_quyet_dinh": "agent-can-hoi"}
 CAU_HOI = {"het-ngan-sach": "Bead đã dùng hết ngân sách chu kỳ. Làm tiếp, đổi hướng hay dừng?",
            "thieu-moi-truong-kiem": "Dự án chưa có `moi_truong_kiem` (hoặc file không đọc được). Đặt rồi trả lời.",
            "dong-file-cau-hinh": "Diff chạm đường dẫn cấm. Trả lời 'hoàn tác', hoặc thêm ngoại lệ cụ thể rồi trả lời.",
-           "qc-doi-ma": "Khe QC đã đổi file ngoài docs/handovers/. QC không được công nhận."}
+           "qc-doi-ma": "Khe QC đã đổi file ngoài docs/handovers/. QC không được công nhận.",
+           "cay-khac-nguon": "Bản chép kiểm không dựng lại được đúng cây git của commit (CRLF/text, ident, encoding, "
+                             "trùng tên hoa-thường, submodule hoặc filter của kho kiểm). Sửa repo rồi trả lời."}
 
 
 def ma_escalation(du_an: str, bead_id: str, ly_do: str, nguon: str) -> str:
```

`tram/suy/mau_su_kien.py` (sửa — bản vá):

```diff
diff --git a/tram/suy/mau_su_kien.py b/tram/suy/mau_su_kien.py
index b5c9c56..c46bf6a 100644
--- a/tram/suy/mau_su_kien.py
+++ b/tram/suy/mau_su_kien.py
@@ -16,7 +16,8 @@ BI = {"agent": "agent bí", "het-ngan-sach": "hết ngân sách", "khe-tat": "kh
 ESC = {"agent-bi": "agent bí", "can-thao-tac-nguy-hiem": "cần thao tác nguy hiểm", "agent-can-hoi": "agent cần hỏi",
        "het-ngan-sach": "hết ngân sách", "nhanh-bi-day": "nhánh bị đẩy",
        "thieu-moi-truong-kiem": "thiếu môi trường kiểm", "dong-file-cau-hinh": "đụng file cấu hình",
-       "qc-doi-ma": "QC đổi mã", "spec-tra-ve-nhieu": "spec bị trả về nhiều", "phieu-thieu": "phiếu thiếu"}
+       "qc-doi-ma": "QC đổi mã", "spec-tra-ve-nhieu": "spec bị trả về nhiều", "phieu-thieu": "phiếu thiếu",
+       "cay-khac-nguon": "cây bản chép khác nguồn"}
 QC = {"dat": "QC đạt", "tra_ve": "QC trả về", "khong_cong_nhan": "QC không công nhận"}
 PR_LY_DO = {"pr-khac": "PR khác PR trạm mở", "sai-nhanh": "sai nhánh", "sai-nhanh-chinh": "sai nhánh chính",
             "thieu-merge-commit": "thiếu merge commit",
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest tests/test_ban_chep_cay.py tests/test_ban_chep_cay_kho.py tests/test_ban_chep_git.py tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_tick_hai_pha.py -q`
Expected: `64 passed` (23 mới + 41 của T3/T10).

Run: `UV_OFFLINE=1 uv run pytest -q` → **2303 passed** (2280 + 23) trên nền chạy thử. Cũng đã chạy riêng bốn file `test_ban_chep*` với `PATH=/usr/bin:/bin` (Apple git 2.39), trên bản cuối (sau 3C-D): 37 passed.

Kiểm đột biến (đã làm): bỏ `-c` ARCHIVE → 2 đỏ (XDG attributes, cấu hình kho kiểm); không lọc `GIT_*` → đỏ ca `GIT_CONFIG_COUNT`; bỏ `GIT_CONFIG_GLOBAL=/dev/null` → đỏ ca `HOME/.gitconfig`; bỏ so cây → 8 đỏ; bỏ `core.ignorecase=false` phía bản chép hoặc phía archive → 1 đỏ mỗi phía; bỏ kiểm `filter.*` → 1 đỏ. Lớp chỉ đỡ cấu hình system thật (`GIT_CONFIG_NOSYSTEM`, `GIT_ATTR_NOSYSTEM`) không giả lập được mà không sửa máy — giữ có chủ ý.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/cay_kiem.py tram/giao_viec/repo_ban_chep.py tram/giao_viec/ban_chep.py tram/giao_viec/kiem_lai.py \
  tram/giao_viec/tick_pipeline.py tram/giao_viec/escalation.py tram/suy/mau_su_kien.py \
  tests/test_ban_chep_cay.py tests/test_ban_chep_cay_kho.py
git commit -m "fix(giao-viec): bản chép kiểm phải đúng cây commit (R7) — so mã cây, archive cô lập cấu hình trạm, lệch thì escalation cay-khac-nguon" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

## Task 3C-D — thực hiện boundary (chia S/M; mã TDD đầy đủ, chạy thử đợt 7)

Phụ thuộc: 3C-A (thiết kế ở trên), r47 T1/T3/T5/T10 (mã nguồn principal và bản chép), 1a-2 T5 (`noi_that.py`), 3C-C (`kiem_lai.py`, `tick_pipeline.py`). 3C-D5 dùng hợp đồng P1/3C-B qua tham số, không tự viết primitive tiến trình. Nền chạy thử: nền 3C-C (2303) + 1a-2 T5 (chỉ mã) — mỗi task tính trên commit trước.

Regression Codex yêu cầu → test (mọi ca đều đỏ hoặc ném TRƯỚC khi nhận môi trường N+1):

| Ca Codex | Cưỡng chế (D1) | Test chặn N+1 |
|---|---|---|
| Thư mục cha khác owner (0777), tệp con của `tram-kiem` | Hồ sơ cấm ghi ngoài `LUOT/NHA` (`test_cam_mac_dinh_chi_ghi_va_doc_lai_ban_chep_va_nha_cua_luot`) | `test_tep_ngoai_thay_tep_sau_trong_thu_muc_cha_khac_owner_hoac_find_loi`, `test_luot_n_de_tan_du_thi_luot_n1_khong_chep_khong_nhan_moi_truong` |
| Vùng ghi được ngoài allowlist (kể cả `NHA`/bản chép dời trong gốc) | như trên + `test_moi_lenh_cua_luot_di_qua_boc_luot_khong_qua_boc_chung` | như trên + `test_goc_rong_thay_ban_chep_hoac_nha_con_sot` |
| Tái sinh trễ | `(deny job-creation)`, cấm exec công cụ lập lịch | `test_tai_sinh_tre_giua_hai_lan_quan_sat`, `test_tai_sinh_sau_khi_mo_bi_bat_luc_vao_luot_sau`, `test_cron_at_co_lich_hoac_khong_xac_nhan_duoc_thi_nem` |
| Miền lịch không nằm trong `user/uid` | `test_khong_tao_job_khong_chay_cong_cu_lap_lich_khong_ipc` | quan sát miền `login/<asid>` CHỜ G3 (không viết parser đoán); cổng: mọi quan sát ném → đóng (`test_quan_sat_thay_hoac_loi_khi_ra_thi_dong_va_chan_luot_sau`) |
| Lỗi quan sát | — | `test_quan_sat_thay_hoac_loi_khi_ra_thi_dong_va_chan_luot_sau` (4 kiểu lỗi), `test_tep_trang_thai_hong_thi_dong`, `test_tien_trinh_con_hoac_pgrep_loi_thi_nem` |
| Crash/lỗi giữa lượt | — | `test_crash_giua_luot_thi_lan_khoi_dong_sau_van_dong`, `test_luot_loi_giua_chung_thi_dong_cong_va_chan_luot_sau` |

Sau review đối kháng (một vòng, reviewer mới, chỉ ARTIFACT + CONTRACT; không có cross-model — ngữ cảnh không tương tác) đã sửa: `NHA` không được dọn và đọc chéo qua gốc (nay `don_ban` xoá cả hai, hồ sơ cấm đọc gốc, `goc_rong`); semaphore có tên sống qua lượt (nay cấm); cơ chế sandbox thiếu tham số hồ sơ (nay `KHONG_LUOT`); mạng không phải loopback vẫn tới DB dùng chung (nay không mạng); `crontab -r` ngầm xoá dấu vết trước khi quan sát (nay chỉ giết, `cron_at` quan sát); HOME/TMP mỗi lượt chưa có (nay `env` trong `boc_luot`); `ra` không kiểm đúng lượt, `ten_ban_chep` ngoài `try` (đã sửa); kiểm hồ sơ đã cài và tệp môi trường kiểm 0600 (thêm). Còn mở, ghi ở 3C-D5/D6 và phụ lục: C02 trong `chay_mot_lenh`, `tram giao kiem` ngoài khoá, cài hồ sơ cho cơ chế `user`, quan sát launchd, `find` trên `/private/tmp` có thể đóng cổng giả, `tom_tat` của N vào ngữ cảnh tác tử.

### Task 3C-D1 — hồ sơ Seatbelt của lượt, `boc_luot`, HOME/TMP mới mỗi lượt (S)

**Files:**
- Modify: `tram/tho/quyen_kiem.py` (`LICH`, `MACH_CHO`, viết lại `ho_so_tram_kiem` — cùng chữ ký r47 T1)
- Modify: `tram/giao_viec/principal_kiem.py` (`KHONG_LUOT`, `boc_lenh` cho cơ chế sandbox, `boc_luot`)
- Modify: `tram/giao_viec/ban_chep.py` (tạo `<wt>.nha`, `<wt>.nha/tmp` 0700; `don_ban` xoá cả hai)
- Test: `tests/test_ho_so_kiem_lai.py` (mới); sửa `tests/test_quyen_kiem.py` (bỏ test hồ sơ allow-default cũ), `tests/test_kiem_lai_principal.py`, `tests/test_tick_hai_pha.py` (gốc có thêm nhà của lượt khi `don_sach` chạy)

**Interfaces:** Produces `LICH`, `MACH_CHO`, `ho_so_tram_kiem(...) -> str` (hồ sơ dùng `(param "LUOT")`, `(param "NHA")`), `PrincipalKiem.boc_luot(wt) -> Callable[[list[str]], list[str]]`, `KHONG_LUOT`. Consumes `goc_hop_le`, `HO_SO_KIEM`, `SANDBOX_EXEC`, `_p` (`tram/tho/sandbox.py`).

**Acceptance:** hồ sơ cấm mặc định; ghi/đọc lại chỉ `LUOT`/`NHA` (+`/dev/null`, `/dev/zero`); không đọc gốc chung, kho trạm; `(deny job-creation)`; cấm exec `LICH` sau `(allow process-exec)`; không `ipc-`; `mach-lookup` đúng `MACH_CHO`; mạng chỉ unix socket trong `LUOT`. `boc_luot` cơ chế `user` thêm `sandbox-exec -f HO_SO_KIEM`, cơ chế `sandbox` chỉ thêm `-D` (khớp sudoers ghim); mọi lệnh của lượt chạy qua `env HOME=<NHA> TMPDIR=<NHA>/tmp/`. `boc_lenh` cơ chế sandbox mang `-D LUOT=/var/empty -D NHA=/var/empty` (review: thiếu tham số thì mọi lệnh rc 65).

**Verification:** test dưới đây; chạy thử thủ công bằng `sandbox-exec` CHỈ trong thư mục tạm (kết quả ở phụ lục thiết kế §2). Bằng chứng dưới `sudo -u tram-kiem`: G4.

- [ ] **Step 1: Viết test thất bại**

`tests/test_ho_so_kiem_lai.py` (mới):

```python
"""3C-D1 (C01, D45): mọi lệnh dưới `tram-kiem` trong MỘT lượt chạy trong hồ sơ Seatbelt cấm mặc định — chỉ ghi được
bản chép và nhà của chính lượt đó (`-D LUOT/NHA`), không tạo job launchd, không chạy công cụ lập lịch, không tạo bộ nhớ
chia sẻ, không nối dịch vụ loopback. Chỉ kiểm văn bản hồ sơ và argv — không chạy sandbox-exec/sudo (G4 chứng minh)."""
import fnmatch
import re
from pathlib import Path

from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.tho.principal import SANDBOX_EXEC
from tram.tho.quyen_kiem import HO_SO_KIEM, LICH, MACH_CHO, dong_sudoers_kiem, ho_so_tram_kiem

WT = Path("/Users/Shared/tram-kiem/g-1-ab12cd34")


def ho_so(tmp_path):
    return ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                           goc=tmp_path.resolve(), cong=[7700])


def test_cam_mac_dinh_chi_ghi_va_doc_lai_ban_chep_va_nha_cua_luot(tmp_path):
    hs, g = ho_so(tmp_path), tmp_path.resolve()
    assert hs.startswith("(version 1)\n(deny default)\n") and "(allow default)" not in hs
    luot = '(subpath (param "LUOT")) (subpath (param "NHA"))'
    ghi = [d for d in hs.splitlines() if re.search(r"\(allow [^)]*file-write", d)]
    assert ghi == [f"(allow file-write* {luot})", '(allow file-write-data file-ioctl (literal "/dev/null") '
                   '(literal "/dev/zero"))']                     # gốc chung KHÔNG ghi được — lượt khác không với tới
    d = hs.splitlines()
    assert d.index(f'(deny file-read* (subpath "{g}"))') < d.index(f"(allow file-read* {luot})")
    assert '(deny file-read* (subpath "/Users/dai-ca/.tram") (subpath "/Users/tram-tho/.tram"))' in d


def test_khong_tao_job_khong_chay_cong_cu_lap_lich_khong_ipc(tmp_path):
    hs = ho_so(tmp_path).splitlines()
    assert "(deny job-creation)" in hs and not any("job-creation" in d and "allow" in d or "ipc-" in d for d in hs)
    cam = hs.index("(deny process-exec " + " ".join(f'(literal "{x}")' for x in LICH) + ")")
    assert cam > hs.index("(allow process-exec)")                  # luật sau thắng luật trước (SBPL)
    assert {"/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/bin/launchctl", "/usr/bin/osascript"} <= set(LICH)
    tim = [d for d in hs if d.startswith("(allow mach-lookup")]
    assert tim == ["(allow mach-lookup " + " ".join(f'(global-name "{m}")' for m in MACH_CHO) + ")"]
    assert not any("SecurityServer" in m or "pasteboard" in m or "cfprefsd" in m for m in MACH_CHO)


def test_khong_mang_chi_unix_socket_trong_luot(tmp_path):
    mang = [d for d in ho_so(tmp_path).splitlines() if "network" in d]
    assert mang == ['(allow network-outbound (remote unix-socket (subpath (param "LUOT"))))']


def test_boc_luot_user_boc_moi_lenh_trong_ho_so_co_tham_so_va_nha_cua_luot():
    pk = tu_cach_ly("user:tram-kiem")
    a, n = pk.boc_luot(WT)(["/bin/rm", "-rf", str(WT)]), len(pk.boc)
    assert a[:n] == list(pk.boc) and a[n:n + 3] == [SANDBOX_EXEC, "-f", str(HO_SO_KIEM)]
    assert a[n + 3:] == ["-D", f"LUOT={WT}", "-D", f"NHA={WT}.nha", "/usr/bin/env", f"HOME={WT}.nha",
                         f"TMPDIR={WT}.nha/tmp/", "/bin/rm", "-rf", str(WT)]
    assert pk.boc_lenh(["/bin/kill"]) == [*pk.boc, "/bin/kill"]


def test_boc_luot_sandbox_khong_long_hai_lan_va_khop_sudoers():
    pk = tu_cach_ly("sandbox:tram-kiem")
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="sandbox").split("SETENV: ", 1)[1]
    for a in (pk.boc_luot(WT)(["/usr/bin/tar", "-x"]), pk.boc_lenh(["/bin/kill", "-KILL", "-1"])):
        assert a.count(SANDBOX_EXEC) == 1 and fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau)
    assert pk.boc_luot(WT)(["x"])[-6:-3] == ["-D", f"NHA={WT}.nha", "/usr/bin/env"]
    assert pk.boc_lenh(["x"])[-5:] == ["-D", "LUOT=/var/empty", "-D", "NHA=/var/empty", "x"]  # hồ sơ ghim cần tham số
```

`tests/test_quyen_kiem.py` (sửa — bản vá):

```diff
diff --git a/tests/test_quyen_kiem.py b/tests/test_quyen_kiem.py
index 485a148..5af9112 100644
--- a/tests/test_quyen_kiem.py
+++ b/tests/test_quyen_kiem.py
@@ -6,7 +6,7 @@ from pathlib import Path
 import pytest
 
 from tram.tho.principal import Principal
-from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem, goc_hop_le, ho_so_tram_kiem
+from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem, goc_hop_le
 
 
 def test_goc_phai_la_duong_dan_that(tmp_path):
@@ -49,13 +49,3 @@ def test_co_che_sandbox_ghim_tien_to_ho_so_co_dinh():
 def test_sai_dang_la_loi(kw):
     with pytest.raises(ValueError):
         dong_sudoers_kiem(**kw)
-
-
-def test_ho_so_sandbox_tram_kiem_cam_kho_tram_va_quan_ly(tmp_path):
-    goc = tmp_path.resolve()
-    hs = ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
-                         goc=goc, cong=[7700, 3306])
-    assert '(deny file-read* file-write* (subpath "/Users/dai-ca/.tram"))' in hs
-    assert '(deny file-read* file-write* (subpath "/Users/tram-tho/.tram"))' in hs
-    assert f'(allow file-read* file-write* (subpath "{goc}"))' in hs
-    assert '(remote tcp "*:7700")' in hs and '(remote tcp "*:3306")' in hs and "com.apple.securityd" in hs
```

`tests/test_kiem_lai_principal.py` (sửa — bản vá):

```diff
diff --git a/tests/test_kiem_lai_principal.py b/tests/test_kiem_lai_principal.py
index 0896674..ef02738 100644
--- a/tests/test_kiem_lai_principal.py
+++ b/tests/test_kiem_lai_principal.py
@@ -42,7 +42,7 @@ def test_don_sach_truoc_khi_chep_va_truoc_khi_don(m):
         thay.append([(p.name.startswith("g-1-"), (p / "DA_CHAY").exists()) for p in ban_chep(m)])
 
     kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, don_sach=don_sach)
-    assert kq.dat and thay == [[], [(True, True)]] and ban_chep(m) == []
+    assert kq.dat and thay == [[], [(True, True), (True, False)]] and ban_chep(m) == []    # bản chép + nhà của lượt
 
 
 def test_con_tien_trinh_tram_kiem_thi_khong_chep_khong_chay(m):
```

`tests/test_tick_hai_pha.py` (sửa — bản vá):

```diff
diff --git a/tests/test_tick_hai_pha.py b/tests/test_tick_hai_pha.py
index 1eebb44..65d1d74 100644
--- a/tests/test_tick_hai_pha.py
+++ b/tests/test_tick_hai_pha.py
@@ -64,8 +64,9 @@ def test_kiem_lai_dung_thu_muc_va_don_sach_cua_bo(tmp_path):
     don = []
     t.bo.thu_muc_kiem, t.bo.don_sach = goc, lambda: don.append([p.name for p in goc.glob("*")])
     chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
-    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 1
-    assert don[1][0].startswith(loai(t, "giao.nhan")[0].du_lieu["giao_id"] + "-") and list(goc.iterdir()) == []
+    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 2          # bản chép + nhà của lượt
+    gid = loai(t, "giao.nhan")[0].du_lieu["giao_id"]
+    assert all(n.startswith(gid + "-") for n in don[1]) and list(goc.iterdir()) == []
 
 
 def test_cot_3_nhanh_bi_day_ngoai_luong(tmp_path):
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_ho_so_kiem_lai.py tests/test_quyen_kiem.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py tests/test_principal_kiem_hop_nhat.py -q`
Expected (chạy thật): `1 error` — `ImportError: cannot import name 'LICH' from 'tram.tho.quyen_kiem'`. Riêng hai test sửa (`test_kiem_lai_principal.py`, `test_tick_hai_pha.py`) trên mã cũ: `2 failed, 9 passed` — `test_don_sach_truoc_khi_chep_va_truoc_khi_don` (`[(True, True)]` ≠ `[(True, True), (True, False)]`: chưa có nhà của lượt), `test_kiem_lai_dung_thu_muc_va_don_sach_cua_bo` (`len(don[1]) == 1`, mong 2).

- [ ] **Step 3: Viết mã**

`tram/tho/quyen_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/tho/quyen_kiem.py b/tram/tho/quyen_kiem.py
index cd28d1e..ea0adc7 100644
--- a/tram/tho/quyen_kiem.py
+++ b/tram/tho/quyen_kiem.py
@@ -2,19 +2,28 @@
 
 `tram-kiem` tự sở hữu bản chép kiểm dưới `thu_muc_kiem` (trạm `git archive` rồi đưa qua stdin cho `tram-kiem` tự
 `tar -x`, tự dọn). Tài khoản trạm chỉ được chạy lệnh DƯỚI `tram-kiem` qua sudo — không có dòng sudoers nào chạy root,
-không helper, không ACL/chmod. File này giữ chuỗi phía cài đặt: kiểm `thu_muc_kiem`, dòng sudoers, hồ sơ sandbox.
+không helper, không ACL/chmod. File này giữ chuỗi phía cài đặt: kiểm `thu_muc_kiem`, dòng sudoers, hồ sơ Seatbelt.
 
 Sudoers KHÔNG chặn được lệnh tuỳ ý dưới `tram-kiem`, và chặn cũng không thêm an toàn: kiểm lại CHÍNH LÀ chạy mã agent
 viết dưới `tram-kiem` (`vendor/bin/phpunit` của commit là chương trình tuỳ ý). Ranh giới thật là danh tính đích:
 chỉ `tram-kiem` (không root, không user khác), user không credential, không đọc kho trạm. Cơ chế `sandbox` ghim thêm
-tiền tố argv cố định `sandbox-exec -f HO_SO_KIEM` — mọi lệnh dưới `tram-kiem` nằm trong hồ sơ cố định do root giữ."""
+tiền tố argv cố định `sandbox-exec -f HO_SO_KIEM` — mọi lệnh dưới `tram-kiem` nằm trong hồ sơ cố định do root giữ.
+3C-D1 (C01, D45): CẢ HAI cơ chế chạy lệnh của lượt trong `HO_SO_KIEM` (`PrincipalKiem.boc_luot`) — hồ sơ cấm mặc
+định, chỉ cho ghi `-D LUOT` (bản chép) và `-D NHA` (nhà của lượt): lượt N không để lại tệp ngoài hai chỗ đó, không tạo
+job launchd, không chạy crontab/at/launchctl, không IPC POSIX/SysV, không mạng (DB/Redis dùng chung, cục bộ hay xa).
+Cưỡng chế thật của Seatbelt dưới `sudo -u` (setuid, XPC tới launchd) chỉ chứng minh được ở G4."""
 from pathlib import Path
 
 from tram.tho.principal import SANDBOX_EXEC, USER_RE
-from tram.tho.sandbox import ho_so_sandbox
+from tram.tho.sandbox import _p
 
-THU_MUC_CAI = Path("/usr/local/tram")                 # chỉ dùng cho cơ chế sandbox: hồ sơ root:wheel 0644
+THU_MUC_CAI = Path("/usr/local/tram")                 # hồ sơ root:wheel 0644 (cả hai cơ chế — 3C-D5)
 HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"
+LICH = ("/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/usr/bin/atq", "/usr/bin/atrm", "/bin/launchctl",
+        "/usr/bin/osascript", "/usr/bin/open", "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/login", "/usr/bin/security",
+        "/usr/bin/defaults")
+MACH_CHO = ("com.apple.system.opendirectoryd.libinfo", "com.apple.system.logger", "com.apple.logd",
+            "com.apple.system.notification_center", "com.apple.trustd")
 KY_TU_DUONG = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/-")
 
 
@@ -41,7 +50,19 @@ def dong_sudoers_kiem(*, tram: str, tram_kiem: str, co_che: str) -> str:
 
 
 def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> str:
-    """Hồ sơ sandbox của `tram-kiem` (cơ chế `sandbox`): cấm kho trạm, thư mục tiến trình quản lý thợ, Keychain,
-    cổng tram-api/DB nghiệp vụ; mở lại `thu_muc_kiem`. Cài root:wheel 0644 tại `HO_SO_KIEM` — tram-kiem chỉ đọc."""
-    return ho_so_sandbox(cam=[tram_home_tram, nha_quan_ly / ".tram"], cam_ghi=[], cho_ghi=[Path(goc_hop_le(goc))],
-                         cong_cam=cong)
+    """Hồ sơ Seatbelt của lượt kiểm (3C-D1): cấm mặc định. Đọc mọi nơi TRỪ kho trạm/quản lý và `goc` chung (chỉ đọc lại
+    `LUOT`, `NHA` của lượt); ghi CHỈ `LUOT`, `NHA`; không mạng (chỉ unix socket trong `LUOT`) — DB/Redis/dịch vụ dùng
+    chung là trạng thái sống qua lượt; không IPC POSIX/SysV (semaphore có tên sống tới khi khởi động lại). `cong` giữ
+    chữ ký T6 (đã bị cấm cùng mọi mạng). Cài root:wheel 0644."""
+    g = goc_hop_le(goc)
+    cam = " ".join(f'(subpath "{_p(p)}")' for p in (tram_home_tram, nha_quan_ly / ".tram"))
+    luot = '(subpath (param "LUOT")) (subpath (param "NHA"))'
+    dong = ["(version 1)", "(deny default)", "(allow process-fork)", "(allow process-exec)", "(allow signal)",
+            "(allow process-info*)", "(allow sysctl-read)", "(allow user-preference-read)", "(allow system-socket)",
+            "(allow file-read*)", f"(deny file-read* {cam})", f'(deny file-read* (subpath "{g}"))',
+            f'(allow file-read-metadata (literal "{g}"))', f"(allow file-read* {luot})", f"(allow file-write* {luot})",
+            '(allow file-write-data file-ioctl (literal "/dev/null") (literal "/dev/zero"))',
+            "(deny job-creation)", "(deny process-exec " + " ".join(f'(literal "{x}")' for x in LICH) + ")",
+            "(allow mach-lookup " + " ".join(f'(global-name "{m}")' for m in MACH_CHO) + ")",
+            '(allow network-outbound (remote unix-socket (subpath (param "LUOT"))))']
+    return "\n".join(dong) + "\n"
```

`tram/giao_viec/principal_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index 79106dd..1a3cfee 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -10,12 +10,14 @@ import subprocess
 import time
 from collections.abc import Callable
 from dataclasses import dataclass
+from pathlib import Path
 
 from tram.giao_viec.ban_chep import LoiBanChep
-from tram.tho.principal import doc_principal
+from tram.tho.principal import SANDBOX_EXEC, doc_principal
 from tram.tho.quyen_kiem import HO_SO_KIEM
 
-PGREP = "/usr/bin/pgrep"
+PGREP, ENV = "/usr/bin/pgrep", "/usr/bin/env"
+KHONG_LUOT = ("-D", "LUOT=/var/empty", "-D", "NHA=/var/empty")
 
 
 @dataclass(frozen=True)
@@ -25,8 +27,18 @@ class PrincipalKiem:
     co_che: str = "user"
 
     def boc_lenh(self, argv: list[str]) -> list[str]:
-        """Tham số `boc` của `chay_mot_lenh`/`kiem_lai` (3a-1): argv chạy dưới `tram-kiem`, không qua shell."""
-        return [*self.boc, *argv]
+        """Tham số `boc` của `chay_mot_lenh`/`kiem_lai` (3a-1): argv chạy dưới `tram-kiem`, không qua shell. Cơ chế
+        sandbox: hồ sơ ghim ở sudoers cần tham số — ngoài lượt cho `/var/empty` (root, không ghi được)."""
+        return [*self.boc, *(KHONG_LUOT if self.co_che == "sandbox" else ()), *argv]
+
+    def boc_luot(self, wt: Path) -> Callable[[list[str]], list[str]]:
+        """3C-D1: `boc` của MỘT lượt — mọi lệnh trong `HO_SO_KIEM` với `-D LUOT=<bản chép> -D NHA=<bản chép>.nha`, chạy
+        qua `env HOME=<NHA> TMPDIR=<NHA>/tmp/` (HOME/TMP riêng mỗi lượt, D45). Cơ chế sandbox đã có tiền tố hồ sơ (ghim
+        ở sudoers) nên chỉ thêm tham số; không lồng sandbox-exec hai lần."""
+        nha = f"{wt}.nha"
+        ho_so = [] if self.co_che == "sandbox" else [SANDBOX_EXEC, "-f", str(HO_SO_KIEM)]
+        dau = [*self.boc, *ho_so, "-D", f"LUOT={wt}", "-D", f"NHA={nha}", ENV, f"HOME={nha}", f"TMPDIR={nha}/tmp/"]
+        return lambda argv: [*dau, *argv]
 
     def kill_nhom(self, pgid: int, sig: int, *, chay=subprocess.run) -> None:
         """S6: kill trong cùng principal; không nuốt lỗi quyền/timeout."""
```

`tram/giao_viec/ban_chep.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/ban_chep.py b/tram/giao_viec/ban_chep.py
index 3c5ea5b..db48baf 100644
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -75,6 +75,7 @@ def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
         raise CayKhacNguon(loi)
     _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
     _chay(boc(["/bin/mkdir", str(wt)]), check=True)
+    _chay(boc(["/bin/mkdir", "-m", "700", f"{wt}.nha", f"{wt}.nha/tmp"]), check=True)   # HOME/TMP MỚI của lượt (D45)
     nguon = nguon_archive(kho, commit)
     try:
         nhan = _chay(boc([*TAR_NHAN, str(wt)]), stdin=nguon.stdout)
@@ -107,15 +108,15 @@ def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *,
 
 
 def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None) -> None:
-    """Giết mọi tiến trình `tram-kiem` rồi `tram-kiem` tự `rm -rf`. Còn sót (thư mục hoặc tiến trình) → ném."""
+    """Giết mọi tiến trình `tram-kiem` rồi `tram-kiem` tự `rm -rf` bản chép và nhà của lượt. Còn sót → ném."""
     loi = None
     if don_sach is not None:
         try:
             don_sach()
         except (OSError, subprocess.SubprocessError) as e:
             loi = e
-    r = _chay(boc(["/bin/rm", "-rf", str(wt)]))
-    if r.returncode or os.path.lexists(wt):
+    r = _chay(boc(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]))
+    if r.returncode or os.path.lexists(wt) or os.path.lexists(f"{wt}.nha"):
         raise LoiBanChep(f"không dọn được bản chép {wt} — không công nhận kết quả") from loi
     if loi is not None:
         raise loi
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `37 passed`. `UV_OFFLINE=1 uv run pytest -q` → **2307 passed** (2303 + 5 − 1).

- [ ] **Step 5: Commit**

```bash
git add tram/tho/quyen_kiem.py tram/giao_viec/principal_kiem.py tram/giao_viec/ban_chep.py tests/test_ho_so_kiem_lai.py \
  tests/test_quyen_kiem.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py
git commit -m "feat(giao-viec): mọi lệnh của lượt kiểm trong hồ sơ Seatbelt cấm mặc định, HOME/TMP riêng mỗi lượt (C01, 3C-D1)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

### Task 3C-D2 — cổng lượt bền, fail-closed (S)

**Files:** Create `tram/giao_viec/cong_luot.py`; Test `tests/test_cong_luot.py`.

**Interfaces:** Produces `CongDong(LoiBanChep)`, `CongLuot(tep, thu_hoi, quan_sat, ngu=time.sleep, cho=5.0)` với `trang_thai() -> dict`, `vao(luot)`, `ra(luot)`, `mo_lai()`, `dong(ly_do)`. Consumes `LoiBanChep` (T3).

**Acceptance:** chỉ `ra(luot)` (đúng lượt đang `dang-chay`) hoặc `mo_lai()` thành công mới ghi `mo`; mỗi lần cần thu hồi + quan sát HAI lần cách `cho`; `vao` đòi `mo` + một lần quan sát sạch rồi ghi `dang-chay` TRƯỚC khi chép; lỗi bất kỳ (kể cả `TimeoutExpired`, định dạng lạ) → `dong` + `CongDong`; tệp thiếu/hỏng/khác trạng thái → đóng; ghi trạng thái fsync + `os.replace` + fsync thư mục.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cong_luot.py` (mới):

```python
"""3C-D2 (C01, D45): cổng lượt kiểm lại bền trên đĩa — chỉ `ra()` thành công (thu hồi + hai lượt quan sát sạch) mới mở
cho lượt sau. Quan sát thấy gì, quan sát lỗi, tái sinh trễ, crash giữa lượt, tệp trạng thái hỏng → cổng đóng; lượt
N+1 bị từ chối TRƯỚC khi chép/nhận môi trường kiểm. Quan sát/thu hồi giả, không chạy lệnh hệ thống."""
import subprocess

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot


def cong(tmp_path, *quan_sat, thu_hoi=lambda: None, ngu=lambda s: None):
    return CongLuot(tmp_path / "cong.json", thu_hoi=thu_hoi, quan_sat=list(quan_sat), ngu=ngu)


def thay(*lan_co):
    """Quan sát giả: lần gọi thứ i (đếm từ 1) nằm trong `lan_co` thì thấy tàn dư."""
    dem = [0]

    def q():
        dem[0] += 1
        if dem[0] in lan_co:
            raise LoiBanChep(f"tram-kiem còn tàn dư (lần quan sát {dem[0]})")
    return q


def test_chua_mo_lan_nao_thi_dong(tmp_path):
    with pytest.raises(CongDong, match="chua-mo"):
        cong(tmp_path).vao("g-1")


def test_mo_vao_ra_roi_lai_vao_duoc(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    c.vao("g-1")
    assert c.trang_thai() == {"trang_thai": "dang-chay", "luot": "g-1"}
    c.ra("g-1")
    c.vao("g-2")


@pytest.mark.parametrize("loi", [LoiBanChep("thư mục cha khác owner còn tệp"), OSError("pgrep mã 3"),
                                 subprocess.TimeoutExpired(["find"], 30), RuntimeError("định dạng lạ")])
def test_quan_sat_thay_hoac_loi_khi_ra_thi_dong_va_chan_luot_sau(tmp_path, loi):
    lan = [0]

    def q():
        lan[0] += 1
        if lan[0] > 3:                                             # 1–2: mo_lai, 3: vào lượt N — sạch
            raise loi
    c = cong(tmp_path, q)
    c.mo_lai()
    c.vao("g-1")
    with pytest.raises(CongDong):
        c.ra("g-1")
    assert c.trang_thai()["trang_thai"] == "dong"
    with pytest.raises(CongDong):
        cong(tmp_path).vao("g-2")                                  # tiến trình trạm mới cũng thấy đóng


def test_tai_sinh_tre_giua_hai_lan_quan_sat(tmp_path):
    ngu = []
    c = cong(tmp_path, thay(2), ngu=ngu.append)                    # lần 1 sạch; tàn dư hiện ra sau khi chờ
    with pytest.raises(CongDong):
        c.mo_lai()
    assert ngu == [c.cho] and c.trang_thai()["trang_thai"] == "dong"


def test_tai_sinh_sau_khi_mo_bi_bat_luc_vao_luot_sau(tmp_path):
    c = cong(tmp_path, thay(3))                                    # mo_lai sạch 2 lần; lần 3 (vào g-2) thấy
    c.mo_lai()
    with pytest.raises(CongDong, match="trước lượt g-2"):
        c.vao("g-2")
    assert c.trang_thai()["trang_thai"] == "dong"


def test_crash_giua_luot_thi_lan_khoi_dong_sau_van_dong(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    c.vao("g-1")                                                   # trạm chết trước `ra()`
    with pytest.raises(CongDong, match="dang-chay"):
        cong(tmp_path).vao("g-2")


@pytest.mark.parametrize("noi_dung", ["{hỏng", '{"trang_thai": "MO"}', "[]"])
def test_tep_trang_thai_hong_thi_dong(tmp_path, noi_dung):
    (tmp_path / "cong.json").write_text(noi_dung, encoding="utf-8")
    with pytest.raises(CongDong):
        cong(tmp_path).vao("g-1")


def test_thu_hoi_loi_hoac_dong_chu_dong_thi_dong(tmp_path):
    def hong():
        raise OSError("kill -1 dưới tram-kiem lỗi")
    c = cong(tmp_path, thu_hoi=hong)
    with pytest.raises(CongDong, match="kill -1"):
        c.mo_lai()
    c2 = cong(tmp_path)
    c2.mo_lai()
    c2.vao("g-1")
    c2.dong("lượt g-1 lỗi: LoiBanChep")
    assert c2.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1 lỗi: LoiBanChep"}


def test_ra_cua_luot_khac_hoac_khi_khong_dang_chay_thi_dong(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    with pytest.raises(CongDong, match="đổi giữa lượt"):
        c.ra("g-1")                                                # chưa `vao` mà đã `ra`
    c.mo_lai()
    c.vao("g-1")
    with pytest.raises(CongDong):
        c.ra("g-2")
    assert c.trang_thai()["trang_thai"] == "dong"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_cong_luot.py -q`
Expected: `1 error` — `ModuleNotFoundError: No module named 'tram.giao_viec.cong_luot'`.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_luot.py` (mới):

```python
"""Cổng lượt kiểm lại (3C-D2; C01, D45) — "lịch ngoài phạm vi hoặc cleanup không rõ thì chặn lượt sau", bền trên đĩa.

`vao(luot)`: chỉ đi tiếp khi tệp trạng thái ghi `mo` VÀ một lượt quan sát sạch (bắt tàn dư tái sinh sau khi mở); ghi
`dang-chay` TRƯỚC khi chép hay nhận môi trường kiểm. `ra()`: thu hồi (giết mọi tiến trình của `tram-kiem`) rồi quan
sát HAI lần cách `cho` giây; sạch mới ghi `mo`. Bất kỳ lỗi nào — quan sát thấy tàn dư, quan sát không chạy được, hết
hạn, định dạng lạ — ghi `dong` kèm lý do và ném `CongDong`. Trạm chết giữa lượt để lại `dang-chay` = đóng. Chỉ Đại ca mở
lại (`tram giao mo-cong-kiem` → `mo_lai`) sau khi xem; `mo_lai` cũng phải thu hồi + quan sát sạch. Quan sát chỉ là
bằng chứng bổ trợ; ranh giới cưỡng chế là hồ sơ Seatbelt của lượt (`boc_luot`, 3C-D1)."""
import json
import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tram.giao_viec.ban_chep import LoiBanChep

TRANG_THAI = ("mo", "dang-chay", "dong")


class CongDong(LoiBanChep):
    """Cổng kiểm lại đóng: lượt trước chưa được thu hồi/xác nhận sạch — không chép, không nhận môi trường kiểm."""


@dataclass
class CongLuot:
    tep: Path
    thu_hoi: Callable[[], None]
    quan_sat: Sequence[Callable[[], None]]
    ngu: Callable[[float], None] = time.sleep
    cho: float = 5.0

    def trang_thai(self) -> dict:
        try:
            tt = json.loads(self.tep.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"trang_thai": "chua-mo"}
        except (OSError, ValueError):
            return {"trang_thai": "hong"}
        return tt if isinstance(tt, dict) and tt.get("trang_thai") in TRANG_THAI else {"trang_thai": "hong"}

    def _ghi(self, tt: dict) -> None:
        self.tep.parent.mkdir(parents=True, exist_ok=True)
        tam = self.tep.with_name(self.tep.name + ".tam")
        with open(tam, "w", encoding="utf-8") as f:
            f.write(json.dumps(tt, ensure_ascii=False))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tam, self.tep)
        fd = os.open(self.tep.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def dong(self, ly_do: str) -> None:
        self._ghi({"trang_thai": "dong", "ly_do": ly_do})

    def _sach(self, ly_do: str, *, lan: int) -> None:
        try:
            for i in range(lan):
                if i:
                    self.ngu(self.cho)                    # nguồn tái sinh trễ phải lộ ra giữa hai lần quan sát
                for q in self.quan_sat:
                    q()
        except Exception as e:                            # noqa: BLE001 — mọi lỗi quan sát đều đóng cổng
            self.dong(f"{ly_do}: {type(e).__name__}: {e}")
            raise CongDong(f"{ly_do}: {e}") from e

    def vao(self, luot: str) -> None:
        tt = self.trang_thai()
        if tt["trang_thai"] != "mo":
            raise CongDong(f"cổng kiểm lại {tt['trang_thai']} ({tt.get('ly_do') or tt.get('luot') or 'chưa xác nhận'})"
                           " — Đại ca xem rồi chạy `tram giao mo-cong-kiem`")
        self._sach(f"trước lượt {luot}", lan=1)
        self._ghi({"trang_thai": "dang-chay", "luot": luot})

    def ra(self, luot: str) -> None:
        if self.trang_thai() != {"trang_thai": "dang-chay", "luot": luot}:
            self.dong(f"sau lượt {luot}: trạng thái cổng không phải dang-chay của lượt này")
            raise CongDong(f"sau lượt {luot}: trạng thái cổng bị đổi giữa lượt")
        self._thu_hoi_va_xet(f"sau lượt {luot}")

    def mo_lai(self) -> None:
        self._thu_hoi_va_xet("mở lại")

    def _thu_hoi_va_xet(self, ly_do: str) -> None:
        try:
            self.thu_hoi()
        except Exception as e:                            # noqa: BLE001
            self.dong(f"{ly_do}: thu hồi lỗi: {type(e).__name__}: {e}")
            raise CongDong(f"{ly_do}: thu hồi lỗi: {e}") from e
        self._sach(ly_do, lan=2)
        self._ghi({"trang_thai": "mo"})
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `14 passed`. `UV_OFFLINE=1 uv run pytest -q` → **2321 passed**.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/cong_luot.py tests/test_cong_luot.py
git commit -m "feat(giao-viec): cổng lượt kiểm lại bền trên đĩa — dọn không rõ thì chặn lượt sau (C01, D45, 3C-D2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

### Task 3C-D3 — quan sát bổ trợ do trạm tự chạy (S)

**Files:** Create `tram/giao_viec/quan_sat_kiem.py`; Test `tests/test_quan_sat_kiem.py`.

**Interfaces:** Produces `GOC_CHUNG`, `HAN`, `tien_trinh(ten, *, chay)`, `tep_ngoai(ten, goc, *, chay)`, `goc_rong(goc)`, `cron_at(pk, *, chay)` — mỗi hàm ném `LoiBanChep` khi thấy tàn dư hoặc không quan sát được. Consumes `LoiBanChep`, `USER_RE`, `PrincipalKiem.boc_lenh`.

**Acceptance:** `pgrep -U` và `-u` do trạm chạy (không sudo); `find -x` mọi độ sâu trong `GOC_CHUNG`, không `-maxdepth`, cắt nhánh `goc` và thư mục user khác không đọc được; gốc bản chép phải rỗng; `crontab -l` mã 1 + "no crontab for", `atq` rỗng, `/usr/lib/cron/jobs` không có tệp của `tram-kiem`; KHÔNG gỡ gì (quan sát không xoá dấu vết).

- [ ] **Step 1: Viết test thất bại**

`tests/test_quan_sat_kiem.py` (mới):

```python
"""3C-D3 (C01): quan sát bổ trợ do TRẠM tự chạy (không qua sudo, không tin lời `tram-kiem`): tiến trình theo UID thực
và hiệu lực; tệp của `tram-kiem` ở MỌI độ sâu trong vùng ghi-chung (ca Codex: tệp con trong thư mục cha 0777 của user
khác — `_sot -maxdepth 1` cũ bỏ sót). Thấy hoặc không quan sát được → ném (cổng đóng). `chay` giả, không chạy lệnh."""
import subprocess
from pathlib import Path

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import GOC_CHUNG, cron_at, goc_rong, tep_ngoai, tien_trinh

GOC = Path("/Users/Shared/tram-kiem")


def gia(*kq):
    goi, con = [], list(kq)

    def chay(argv, **kw):
        goi.append(argv)
        ma, ra = con.pop(0)
        return subprocess.CompletedProcess(argv, ma, ra, "")
    return chay, goi


def test_tien_trinh_tram_tu_dem_ca_uid_thuc_va_hieu_luc():
    chay, goi = gia((1, ""), (1, ""))
    tien_trinh("tram-kiem", chay=chay)
    assert goi == [["/usr/bin/pgrep", "-U", "tram-kiem"], ["/usr/bin/pgrep", "-u", "tram-kiem"]]


@pytest.mark.parametrize("kq, khop", [([(0, "812\n"), (1, "")], "còn tiến trình"), ([(1, ""), (0, "9\n")], "còn"),
                                      ([(3, "")], "không quan sát")])
def test_tien_trinh_con_hoac_pgrep_loi_thi_nem(kq, khop):
    with pytest.raises(LoiBanChep, match=khop):
        tien_trinh("tram-kiem", chay=gia(*kq)[0])


def test_tep_ngoai_quet_moi_do_sau_bo_qua_goc_va_thu_muc_khong_doc_duoc():
    chay, goi = gia((0, ""))
    tep_ngoai("tram-kiem", GOC, chay=chay)
    a = goi[0]
    assert a[:2] == ["/usr/bin/find", "-x"] and a[2:2 + len(GOC_CHUNG)] == list(GOC_CHUNG)
    assert "-maxdepth" not in a and a[-4:] == ["-o", "-user", "tram-kiem", "-print"]
    assert ["-path", str(GOC), "-o", "-type", "d", "!", "-user", "tram-kiem", "!", "-perm", "-0005"] == \
        a[a.index("(") + 1:a.index(")")] and a[a.index(")") + 1] == "-prune"


@pytest.mark.parametrize("kq, khop", [((0, "/Users/Shared/chung-0777/sau/hon/tep\n"), "1 mục"),
                                      ((1, ""), "không quan sát"), ((0, "\n"), "không quan sát")])
def test_tep_ngoai_thay_tep_sau_trong_thu_muc_cha_khac_owner_hoac_find_loi(kq, khop):
    with pytest.raises(LoiBanChep, match=khop):
        tep_ngoai("tram-kiem", GOC, chay=gia(kq)[0])


def test_ten_user_la_bi_tu_choi_truoc_khi_chay():
    with pytest.raises(ValueError):
        tien_trinh("-x", chay=gia()[0])



def test_goc_rong_thay_ban_chep_hoac_nha_con_sot(tmp_path):
    goc_rong(tmp_path)
    (tmp_path / "g-1-ab.nha").mkdir()                              # nhà lượt (hoặc bản chép bị dời vào đó) còn sót
    with pytest.raises(LoiBanChep, match="1 mục"):
        goc_rong(tmp_path)
    with pytest.raises(LoiBanChep, match="không đọc"):
        goc_rong(tmp_path / "khong-co")


def test_cron_at_sach_khong_go_gi():
    pk = tu_cach_ly("user:tram-kiem")
    goi, kq = [], [(1, "", "crontab: no crontab for tram-kiem\n"), (0, "", ""), (0, "", "")]

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *kq.pop(0))
    cron_at(pk, chay=chay)
    assert goi == [pk.boc_lenh(["/usr/bin/crontab", "-l"]), pk.boc_lenh(["/usr/bin/atq"]),
                   ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]
    assert not any("-r" in a or "atrm" in " ".join(a) for a in goi)        # quan sát không xoá dấu vết


@pytest.mark.parametrize("kq", [[(0, "* * * * * sh x\n", "")], [(1, "", "crontab: tmp/tmp.1: Permission denied\n")],
                                [(1, "", "no crontab for tram-kiem"), (0, "3 Fri Oct 16 a tram-kiem\n", "")],
                                [(1, "", "no crontab for tram-kiem"), (0, "", ""), (0, "/usr/lib/cron/jobs/a01\n", "")],
                                [(1, "", "no crontab for tram-kiem"), (2, "", "")]])
def test_cron_at_co_lich_hoac_khong_xac_nhan_duoc_thi_nem(kq):
    con = list(kq)
    with pytest.raises(LoiBanChep):
        cron_at(tu_cach_ly("user:tram-kiem"), chay=lambda a, **kw: subprocess.CompletedProcess(a, *con.pop(0)))
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_quan_sat_kiem.py -q`
Expected: `1 error` — `ModuleNotFoundError: No module named 'tram.giao_viec.quan_sat_kiem'`.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/quan_sat_kiem.py` (mới):

```python
"""Quan sát bổ trợ sau mỗi lượt kiểm (3C-D3; C01) — TRẠM tự chạy, không qua sudo, không tin lời `tram-kiem`.

Không phải ranh giới cách ly (ranh giới là hồ sơ Seatbelt của lượt, 3C-D1); là dây báo: thấy tàn dư hoặc không quan
sát được thì ném, `CongLuot` đóng cổng. `tep_ngoai` tìm tệp của `tram-kiem` ở MỌI độ sâu trong vùng ghi-chung (sửa lỗ
`_sot -maxdepth 1` mà Codex nêu: tệp con trong thư mục cha 0777 của user khác), cắt nhánh thư mục user khác mà trạm
không đọc được; `goc_rong` đòi gốc bản chép trống (bản chép, nhà lượt, thứ dời đi đều phải đã dọn); `cron_at` đòi
không có crontab/việc `at` (KHÔNG gỡ — gỡ là việc của Đại ca sau khi xem). `DARWIN_USER_*` (0700 của `tram-kiem`), thư
mục ghi qua nhóm `staff` ngoài `GOC_CHUNG`, launchd (T11) KHÔNG nằm ở đây — chỉ hồ sơ Seatbelt chặn."""
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.ban_chep import LoiBanChep
from tram.tho.principal import USER_RE

PGREP, FIND = "/usr/bin/pgrep", "/usr/bin/find"
GOC_CHUNG = ("/private/tmp", "/private/var/tmp", "/Users/Shared", "/Library/Caches")
HAN = 120


def _ten(ten: str) -> str:
    if not USER_RE.fullmatch(ten):
        raise ValueError(f"tên user không hợp lệ: {ten!r}")
    return ten


def tien_trinh(ten: str, *, chay: Callable = subprocess.run) -> None:
    """Không còn tiến trình nào có UID thực (`-U`) hoặc hiệu lực (`-u`) là `ten` — pgrep mã 1 cả hai."""
    for co in ("-U", "-u"):
        r = chay([PGREP, co, _ten(ten)], capture_output=True, text=True, timeout=HAN)
        if r.returncode == 0:
            raise LoiBanChep(f"{ten} còn tiến trình ({co}): {len(r.stdout.split())} pid")
        if r.returncode != 1:
            raise LoiBanChep(f"pgrep {co} {ten} mã {r.returncode} — không quan sát được tiến trình")


def tep_ngoai(ten: str, goc: Path, *, chay: Callable = subprocess.run) -> None:
    """Không còn mục nào của `ten` trong `GOC_CHUNG` (mọi độ sâu, không qua ổ khác); find lỗi → không quan sát được."""
    cat = ["(", "-path", str(goc), "-o", "-type", "d", "!", "-user", _ten(ten), "!", "-perm", "-0005", ")", "-prune"]
    r = chay([FIND, "-x", *GOC_CHUNG, *cat, "-o", "-user", ten, "-print"], capture_output=True, text=True, timeout=HAN)
    muc = [x for x in r.stdout.splitlines() if x.strip()]
    if r.returncode != 0 or (r.stdout and not muc):
        raise LoiBanChep(f"find vùng ghi-chung mã {r.returncode} — không quan sát được tệp của {ten}")
    if muc:
        raise LoiBanChep(f"{ten} còn {len(muc)} mục ngoài bản chép (vùng ghi-chung, kể cả thư mục cha khác owner)")


def goc_rong(goc: Path) -> None:
    """Gốc bản chép không còn mục nào: lượt trước đã dọn cả bản chép lẫn nhà của lượt, không dời gì sang chỗ khác."""
    try:
        con = os.listdir(goc)
    except OSError as e:
        raise LoiBanChep(f"không đọc được gốc bản chép {goc}: {e.strerror}") from e
    if con:
        raise LoiBanChep(f"gốc bản chép còn {len(con)} mục của lượt trước — chưa dọn")


def cron_at(pk, *, chay: Callable = subprocess.run) -> None:
    """`tram-kiem` không có crontab (`crontab -l` mã 1, "no crontab for") và không có việc `at` (`atq` rỗng; trạm tự
    tìm tệp của nó trong `/usr/lib/cron/jobs`). Thấy hay không chắc → ném; không tự gỡ để quan sát không bị xoá dấu."""
    r = chay(pk.boc_lenh(["/usr/bin/crontab", "-l"]), capture_output=True, text=True, timeout=HAN)
    if r.returncode != 1 or "no crontab for" not in r.stderr:
        raise LoiBanChep(f"{pk.ten}: crontab -l mã {r.returncode} — có crontab hoặc không xác nhận được")
    for argv in (pk.boc_lenh(["/usr/bin/atq"]), [FIND, "/usr/lib/cron/jobs", "-user", _ten(pk.ten)]):
        r = chay(argv, capture_output=True, text=True, timeout=HAN)
        if r.returncode or r.stdout.strip():
            raise LoiBanChep(f"{pk.ten}: {argv[-1] if argv[0] == FIND else 'atq'} mã {r.returncode} — có việc at "
                             "hoặc không xác nhận được")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `16 passed`. `UV_OFFLINE=1 uv run pytest -q` → **2337 passed**. Biểu thức `find` đã chạy thử trên thư mục tạm: thấy tệp ở độ sâu 3 dưới thư mục 0777, bỏ qua gốc, mã 0.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/quan_sat_kiem.py tests/test_quan_sat_kiem.py
git commit -m "feat(giao-viec): quan sát tàn dư tram-kiem mọi độ sâu, gốc rỗng, cron/at — không gỡ (C01, 3C-D3)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

### Task 3C-D4 — ghép cổng + hồ sơ vào kiểm lại, cổng thật, `tram giao mo-cong-kiem` (M)

**Nền:** sau 1a-2 T5 (bản vá `noi_that.py` dưới đây tính trên nền đã có `bat_ghi`), sau 3C-C (`kiem_lai.py`, `tick_pipeline.py`), sau r47 T12 nếu T12 đã sửa `lenh.py` (đối chiếu mốc `def them_lenh_giao`).

**Files:**
- Create: `tram/giao_viec/cong_that.py` (`giet_tam`, `thu_hoi_theo_uid`, `ho_so_cai`, `env_kin`, `dung_cong`)
- Modify: `tram/giao_viec/kiem_lai.py` (`cong`, `boc_luot`; tách `_tren_ban_chep`; lỗi → `cong.dong`; xong → `cong.ra`)
- Modify: `tram/giao_viec/bo.py` (+`cong`, `boc_luot`), `tram/giao_viec/tick_pipeline.py` (truyền), `tram/giao_viec/noi_that.py` (`dung_cong`, `don_sach=giet_tam` — không còn `crontab -r` ngầm), `tram/giao_viec/lenh.py` (`mo-cong-kiem`)
- Test: `tests/test_cong_that.py`, `tests/test_kiem_lai_cong.py` (mới); sửa `tests/test_noi_giao_viec.py`

**Interfaces:** Consumes D1 `boc_luot`, D2 `CongLuot`/`CongDong`, D3 quan sát, `HO_SO_KIEM`, `tram_home`, `giu_khoa`. Produces `kiem_lai(..., cong=None, boc_luot=None)`, `BoGiaoViec.cong`, `BoGiaoViec.boc_luot`, `dung_cong(pk, goc, *, cac_du_an, thu_hoi=None)`, `thu_hoi_theo_uid(ten, *, kiem_uid, chay, han=30)` (hợp đồng P1/3C-B), CLI `tram giao mo-cong-kiem [--dong-y]`.

**Acceptance:** cổng đóng → `kiem_lai` ném `CongDong` TRƯỚC `don_sach`, chép, nhận môi trường; mọi lệnh của lượt qua `boc_luot(wt)`; lượt ném (kể cả `ten_ban_chep`) → `cong.dong`; trả kết quả → `cong.ra(giao_id)`; cổng thật quan sát `tien_trinh`, `tep_ngoai`, `goc_rong`, `cron_at`, `ho_so_cai`, `env_kin`; trong lượt chỉ giết (`kill -KILL -1`), không gỡ lịch; `mo-cong-kiem` giữ `giu_khoa`, chờ `dong-y`, chỉ mở khi thu hồi + quan sát sạch.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cong_that.py` (mới):

```python
"""3C-D4/D5: cổng thật ghép thu hồi + quan sát; thu hồi theo UID (P1/3C-B qua tham số) không gỡ lịch; hồ sơ Seatbelt
đã cài phải đúng chủ/quyền/nội dung; tệp môi trường kiểm của mọi dự án phải kín. Không chạy lệnh hệ thống thật."""
import os
from functools import partial
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import GIET, dung_cong, env_kin, giet_tam, ho_so_cai, thu_hoi_theo_uid
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, tep_ngoai, tien_trinh


def test_thu_hoi_theo_uid_kiem_uid_truoc_roi_kill_moi_tien_trinh_co_han():
    goi = []
    thu_hoi_theo_uid("tram-kiem", kiem_uid=lambda t: goi.append(("uid", t)), chay=lambda a, **kw: goi.append((a, kw)))
    assert goi == [("uid", "tram-kiem"), (["/bin/kill", "-KILL", "-1"], {"principal": "tram-kiem", "han": 30})]


def test_thu_hoi_khong_kill_khi_uid_sai_va_giet_tam_khong_go_lich():
    goi, pk = [], tu_cach_ly("user:tram-kiem")

    def sai(t):
        raise LoiBanChep("UID hiệu lực 501 ≠ UID tram-kiem")
    with pytest.raises(LoiBanChep, match="UID"):
        thu_hoi_theo_uid("tram-kiem", kiem_uid=sai, chay=lambda a, **kw: goi.append(a))
    giet_tam(pk, chay=lambda a, **kw: goi.append((a, kw["timeout"])))
    assert goi == [(pk.boc_lenh(GIET), 120)]


def test_ho_so_cai_dung_chu_quyen_noi_dung(tmp_path, tram_home_tam):
    p = tmp_path / "hs.sb"
    p.write_text(f'(version 1)\n(deny default)\n(deny file-read* (subpath "{tram_home_tam}"))\n')
    p.chmod(0o644)
    ho_so_cai(p, chu=os.getuid())
    with pytest.raises(LoiBanChep, match="sai chủ"):
        ho_so_cai(p)                                               # tệp của user đang test, không phải root
    with pytest.raises(LoiBanChep, match="không đọc"):
        ho_so_cai(tmp_path / "khong-co.sb")


@pytest.mark.parametrize("nd, quyen", [('(deny default)\n(subpath "{h}")', 0o664),
                                       ('(allow default)\n(subpath "{h}")', 0o644),
                                       ('(deny default)\n(subpath "/Users/khac/.tram")', 0o644)])
def test_ho_so_cai_sai_quyen_hoac_noi_dung(tmp_path, tram_home_tam, nd, quyen):
    p = tmp_path / "hs.sb"
    p.write_text(nd.format(h=tram_home_tam))
    p.chmod(quyen)
    with pytest.raises(LoiBanChep, match="sai chủ/quyền/nội dung"):
        ho_so_cai(p, chu=os.getuid())


def test_env_kin_doi_0600_cua_tram(tmp_path):
    f = tmp_path / "env.testing"
    f.write_text("DB=x\n")
    da = [SimpleNamespace(ten="hr", moi_truong_kiem=SimpleNamespace(file=f)),
          SimpleNamespace(ten="x", moi_truong_kiem=None)]
    f.chmod(0o640)
    with pytest.raises(LoiBanChep, match="0600"):
        env_kin(lambda: da)
    f.chmod(0o600)
    env_kin(lambda: da)
    assert os.stat(f).st_uid == os.getuid()


def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam, tmp_path):
    pk = tu_cach_ly("user:tram-kiem")
    c = dung_cong(pk, tmp_path, cac_du_an=list)
    assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is giet_tam
    ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
    assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin]
    assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
```

`tests/test_kiem_lai_cong.py` (mới):

```python
"""3C-D4 (C01, D45): kiểm lại đi qua cổng lượt và hồ sơ của lượt — lượt N để lại tàn dư (tệp con trong thư mục cha
khác owner, ngoài vùng cho ghi), lượt N lỗi giữa chừng → lượt N+1 bị từ chối TRƯỚC khi chép và nhận môi trường kiểm;
mọi lệnh của lượt đi qua `boc_luot(wt)`. git/tar/rm thật trong `tmp_path` (boc đồng nhất), quan sát giả, không sudo."""
import argparse
import os

import pytest

from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec import lenh
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.cong_that import giet_tam
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kiem_lai import kiem_lai
from tram.giao_viec.noi_that import dung_bo_that
from tram.giao_viec.principal_kiem import tu_cach_ly


def cong(tmp):
    """Quan sát giả: tàn dư = tệp `TAN_DU` (đứng cho mục của tram-kiem trong thư mục cha 0777 của user khác)."""
    def q():
        if (tmp / "TAN_DU").exists():
            raise LoiBanChep("tram-kiem còn 1 mục ngoài bản chép (vùng ghi-chung, thư mục cha khác owner)")
    c = CongLuot(tmp / "cong.json", thu_hoi=lambda: None, quan_sat=[q], ngu=lambda s: None)
    c.mo_lai()
    return c


def chay(m, c, *, kiem="exit 0\n", boc_luot=lambda wt: lambda a: a):
    k, da, tmp = m
    sha = k.day("tram/hr-1", {"kiem.sh": kiem}, tu=k.main)
    fetch(k.kho)
    return kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"],
                    chay_lenh=True, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
                    env_goc=os.environ, cong=c, boc_luot=boc_luot)


def test_luot_n_de_tan_du_thi_luot_n1_khong_chep_khong_nhan_moi_truong(m):
    tmp, goi = m[2], []
    c = cong(tmp)
    with pytest.raises(CongDong, match="ngoài bản chép"):
        chay(m, c, kiem=f"touch {tmp}/TAN_DU\n")
    assert c.trang_thai()["trang_thai"] == "dong" and ban_chep(m) == []
    (tmp / "TAN_DU").unlink()                                      # tàn dư đã biến mất: cổng VẪN đóng tới khi mở lại
    with pytest.raises(CongDong, match="dong"):
        chay(m, c, kiem=f"touch {tmp}/N1_DA_CHAY\n", boc_luot=lambda wt: goi.append(wt) or (lambda a: a))
    assert goi == [] and not (tmp / "N1_DA_CHAY").exists() and ban_chep(m) == []


def test_moi_lenh_cua_luot_di_qua_boc_luot_khong_qua_boc_chung(m):
    da_boc, c = [], cong(m[2])

    def boc_luot(wt):
        return lambda a: da_boc.append((wt, a[0].rsplit("/", 1)[-1])) or a
    assert chay(m, c, boc_luot=boc_luot).dat and c.trang_thai()["trang_thai"] == "mo"
    assert len({wt for wt, _ in da_boc}) == 1 and {"mkdir", "tar", "env", "sh", "rm"} <= {x for _, x in da_boc}


def test_luot_loi_giua_chung_thi_dong_cong_va_chan_luot_sau(m):
    c = cong(m[2])
    with pytest.raises(LoiBanChep):
        chay(m, c, boc_luot=lambda wt: lambda a: ["/usr/bin/false"] if a[0] == "/usr/bin/tar" else a)
    assert c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"}
    with pytest.raises(CongDong):
        chay(m, c)


def test_bo_that_co_cong_va_boc_luot_khi_khai_tram_kiem(tram_home_tam, tmp_path):
    pk = tu_cach_ly("user:tram-kiem")
    bo = dung_bo_that(CauHinhGiaoViec(thu_muc_kiem=tmp_path / "k", principal_kiem=pk), CauHinhTram())
    assert bo.cong.tep == tram_home_tam / "kiem-lai" / "cong.json" and bo.boc_luot == pk.boc_luot
    assert bo.don_sach.func is giet_tam                            # trong lượt chỉ giết, không gỡ lịch
    assert dung_bo_that(CauHinhGiaoViec(), CauHinhTram()).cong is None


@pytest.mark.parametrize("tan_du, ma, sau", [(False, 0, "mo"), (True, 1, "dong")])
def test_lenh_mo_cong_kiem_chi_mo_khi_sach(monkeypatch, tmp_path, tan_du, ma, sau):
    c = cong(tmp_path)
    c.dong("lượt g-1: LoiBanChep")
    if tan_du:
        (tmp_path / "TAN_DU").touch()
    monkeypatch.setattr(lenh, "_bo", lambda: (None, argparse.Namespace(cong=c)))
    assert lenh._mo_cong(argparse.Namespace(dong_y=True)) == ma and c.trang_thai()["trang_thai"] == sau
```

`tests/test_noi_giao_viec.py` (sửa — bản vá):

```diff
diff --git a/tests/test_noi_giao_viec.py b/tests/test_noi_giao_viec.py
index adac405..a6064ff 100644
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -63,7 +63,7 @@ def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach == PK.don_sach
+    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach.args == (PK,)   # 3C-D4: giet_tam
     assert bo.kill == PK.kill_nhom
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_cong_that.py tests/test_kiem_lai_cong.py tests/test_noi_giao_viec.py -q`
Expected: `2 errors` — `ModuleNotFoundError: No module named 'tram.giao_viec.cong_that'`.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_that.py` (mới):

```python
"""Cổng lượt THẬT của trạm (3C-D4/D5; C01, D45): ghép thu hồi + mọi quan sát vào `CongLuot`.

Thu hồi: `kill -KILL -1` dưới principal (giết mọi tiến trình cùng UID, kể cả `setsid`), KHÔNG gỡ lịch — lịch để
`cron_at` thấy và đóng cổng. `thu_hoi_theo_uid` (sau P1, 3C-B) thêm kiểm UID thật và primitive có hạn; tới lúc đó
`giet_tam` dùng `boc_lenh` + `subprocess.run(timeout)`. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1).
launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>`) cắm thêm khi T11 ghép và G3 đo định dạng; trước đó I1 KHÔNG bật
`giao_viec.bat`."""
import os
import subprocess
from collections.abc import Callable
from functools import partial
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, tep_ngoai, tien_trinh
from tram.tho.quyen_kiem import HO_SO_KIEM

GIET = ["/bin/kill", "-KILL", "-1"]


def giet_tam(pk, *, chay: Callable = subprocess.run) -> None:
    chay(pk.boc_lenh(GIET), capture_output=True, timeout=HAN)


def thu_hoi_theo_uid(ten: str, *, kiem_uid: Callable[[str], None], chay: Callable, han: float = 30) -> None:
    """Sau P1, 3C-B: kiểm UID thật (3C-B) RỒI `kill -KILL -1` dưới `ten` qua primitive có hạn (P1). Mã thoát không là
    bằng chứng (mã 1 = không còn gì để giết); bằng chứng là `tien_trinh` của trạm. Hết hạn/lỗi → ném."""
    kiem_uid(ten)
    chay(GIET, principal=ten, han=han)


def ho_so_cai(p: Path = HO_SO_KIEM, *, chu: int = 0) -> None:
    """Hồ sơ đã cài: root, không ai khác ghi được, cấm mặc định, cấm đọc kho trạm HIỆN TẠI (đổi TRAM_HOME → cài lại)."""
    try:
        st, nd = p.stat(), p.read_text(encoding="utf-8")
    except OSError as e:
        raise LoiBanChep(f"không đọc được hồ sơ {p}: {e.strerror}") from e
    if st.st_uid != chu or st.st_mode & 0o022 or "(deny default)" not in nd or f'(subpath "{tram_home()}")' not in nd:
        raise LoiBanChep(f"hồ sơ {p} sai chủ/quyền/nội dung — cài lại bằng `tram chu cai-dat-tho`")


def env_kin(cac_du_an: Callable[[], list]) -> None:
    for da in cac_du_an():
        mt = da.moi_truong_kiem
        if mt is None:
            continue
        try:
            st = mt.file.stat()
        except OSError as e:
            raise LoiBanChep(f"{da.ten}: không đọc được tệp môi trường kiểm: {e.strerror}") from e
        if st.st_uid != os.getuid() or st.st_mode & 0o077:
            raise LoiBanChep(f"{da.ten}: tệp môi trường kiểm phải 0600 của trạm (tram-kiem đọc được env lượt khác)")


def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
              thu_hoi: Callable[[], None] | None = None) -> CongLuot:
    goc = goc or tram_home() / "kiem"
    return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(giet_tam, pk),
                    quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
                              partial(cron_at, pk), ho_so_cai, partial(env_kin, cac_du_an)])
```

`tram/giao_viec/kiem_lai.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index 92ac80d..5760f42 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -7,7 +7,9 @@
 Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (`ban_chep.py` — `git archive` → `tar -x` dưới
 `tram-kiem`, môi trường kiểm qua stdin, `tram-kiem` tự dọn; repo git MỘT commit do `tram-kiem` tự dựng — D40 (b);
 không worktree, không trao quyền). Một lần kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không
-sạch → ném, KHÔNG trả kết quả."""
+sạch → ném, KHÔNG trả kết quả. 3C-D (C01, D45): `cong` mở mới được vào lượt (trước khi chép, nhận môi trường); mọi
+lệnh của lượt qua `boc_luot(wt)` (hồ sơ Seatbelt của lượt); lượt ném lỗi → đóng cổng; xong → `cong.ra()` thu hồi và
+quan sát."""
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
@@ -15,11 +17,13 @@ from pathlib import Path
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.lenh import khop_bat_ky
 from tram.giao_viec.ban_chep import CayKhacNguon, chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
+from tram.giao_viec.cong_luot import CongLuot
 from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
 from tram.kiem.diff import diff_cham_cam
 from tram.kiem.moi_truong import LoiMoiTruongKiem
 
 THOI_GIAN_CHO = 900
+Boc = Callable[[list[str]], list[str]]
 
 
 @dataclass(frozen=True)
@@ -36,10 +40,11 @@ class KetQuaKiemLai:
 
 def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem: list[str],
              lenh_cho_phep: list[str], chay_lenh: bool, thu_muc: Path, thu_muc_log: Path,
-             boc: Callable[[list[str]], list[str]], env_goc: Mapping[str, str],
+             boc: Boc, env_goc: Mapping[str, str],
              thoi_gian_cho: float = THOI_GIAN_CHO,
              don_sach: Callable[[], None] | None = None,
-             kill: Callable[[int, int], None] = _kill_nhom) -> KetQuaKiemLai:
+             kill: Callable[[int, int], None] = _kill_nhom,
+             cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None) -> KetQuaKiemLai:
     cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
@@ -50,23 +55,43 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
     if mt is None:
         return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")
     with giu_khoa():
-        if don_sach is not None:
-            don_sach()                       # tiến trình tram-kiem của lần trước không được sống sang lần này
-        wt = thu_muc / ten_ban_chep(giao_id)
+        if cong is not None:
+            cong.vao(giao_id)                # lượt trước chưa xác nhận sạch → không chép, không nhận môi trường kiểm
         try:
-            try:
-                chep_ban(kho_git, commit, wt, boc=boc)
-            except CayKhacNguon:
-                return KetQuaKiemLai(False, loi="cay-khac-nguon")       # R7: tất định — escalation, không thử lại mãi
-            try:
-                nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc)
-            except LoiMoiTruongKiem:
-                return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")  # không bao giờ chạy với .env có thể thật
-            env, ket_qua = moi_truong_kiem(env_goc), []
-            for i, lenh in enumerate(lenh_kiem, 1):
-                kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
-                                   log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
-                ket_qua.append(kq.sang_lenh_kiem())
-        finally:
-            don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
+            wt = thu_muc / ten_ban_chep(giao_id)
+            kq = _tren_ban_chep(kho_git, commit, mt, wt, giao_id=giao_id, lenh_kiem=lenh_kiem,
+                                lenh_cho_phep=lenh_cho_phep, thu_muc_log=thu_muc_log, env_goc=env_goc, kill=kill,
+                                boc=boc_luot(wt) if boc_luot is not None else boc, don_sach=don_sach,
+                                thoi_gian_cho=thoi_gian_cho)
+        except BaseException as e:
+            if cong is not None:
+                cong.dong(f"lượt {giao_id}: {type(e).__name__}")         # dọn không rõ → chặn lượt sau (D45)
+            raise
+        if cong is not None:
+            cong.ra(giao_id)
+    return kq
+
+
+def _tren_ban_chep(kho_git: Path, commit: str, mt, wt: Path, *, giao_id: str, lenh_kiem: list[str],
+                   lenh_cho_phep: list[str], thu_muc_log: Path, boc: Boc, env_goc: Mapping[str, str],
+                   thoi_gian_cho: float, don_sach: Callable[[], None] | None,
+                   kill: Callable[[int, int], None]) -> KetQuaKiemLai:
+    if don_sach is not None:
+        don_sach()                           # tiến trình tram-kiem của lần trước không được sống sang lần này
+    try:
+        try:
+            chep_ban(kho_git, commit, wt, boc=boc)
+        except CayKhacNguon:
+            return KetQuaKiemLai(False, loi="cay-khac-nguon")           # R7: tất định — escalation, không thử lại mãi
+        try:
+            nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc)
+        except LoiMoiTruongKiem:
+            return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
+        env, ket_qua = moi_truong_kiem(env_goc), []
+        for i, lenh in enumerate(lenh_kiem, 1):
+            kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
+                               log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
+            ket_qua.append(kq.sang_lenh_kiem())
+    finally:
+        don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
     return KetQuaKiemLai(bool(ket_qua) and all(k["ket_qua"] == "pass" for k in ket_qua), tuple(ket_qua))
```

`tram/giao_viec/bo.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/bo.py b/tram/giao_viec/bo.py
index 87e3e90..918dad6 100644
--- a/tram/giao_viec/bo.py
+++ b/tram/giao_viec/bo.py
@@ -45,6 +45,8 @@ class BoGiaoViec:
     env_goc: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
     doc_beads: DocBeads | None = None                     # 4a-2: bộ đệm beads của tram-api; None: đọc `bd` mỗi lần
     don_sach: Callable[[], None] | None = None            # 3c: giết mọi tiến trình `tram-kiem`, xác nhận sạch (D22)
+    cong: object | None = None                            # 3C-D2: CongLuot — lượt trước chưa sạch thì không kiểm lại
+    boc_luot: Callable[[Path], Callable] | None = None    # 3C-D1: PrincipalKiem.boc_luot — hồ sơ Seatbelt mỗi lượt
     adr_hop_le: Callable[[DuAn, object], bool] = lambda da, b: False
     kill: Callable[[int, int], None] = _kill_nhom        # 3a-2: kill nhóm qua principal kiểm
     thu_muc_kiem: Path | None = None                      # 4a-2: gốc bản chép kiểm lại; None: ~/.tram/kiem
```

`tram/giao_viec/tick_pipeline.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/tick_pipeline.py b/tram/giao_viec/tick_pipeline.py
index 336ab4e..3701e29 100644
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -41,7 +41,7 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
     kq = kiem_lai(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem), lenh_cho_phep=list(p.lenh_cho_phep),
                   chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                   thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
-                  don_sach=bo.don_sach, kill=bo.kill)
+                  don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot)
     if kq.loi is not None:
         tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
         if kq.loi in ("thieu-moi-truong-kiem", "cay-khac-nguon"):
```

`tram/giao_viec/noi_that.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/noi_that.py b/tram/giao_viec/noi_that.py
index b6c141e..a898f00 100644
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -7,6 +7,7 @@ import threading
 from collections.abc import Callable
 from dataclasses import replace
 from datetime import datetime, timezone
+from functools import partial
 from pathlib import Path
 
 import yaml
@@ -19,6 +20,7 @@ from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
 from tram.giao_viec.dieu_kien import ASSIGNEE
 from tram.giao_viec.doc_beads import DocBeads
 from tram.giao_viec.luong import bat_dau_luong_giao
+from tram.giao_viec.cong_that import dung_cong, giet_tam
 from tram.kiem.chay_lenh import _kill_nhom
 
 
@@ -48,11 +50,12 @@ def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
                  thu_muc_du_an: Path | None = None) -> BoGiaoViec:
     from tram.beads.bd import Bd
     from tram.phieu.kho import mo_kho_phieu
-    pk = cg.principal_kiem
-    return BoGiaoViec(cac_du_an=lambda: cac_du_an_that(thu_muc_du_an),
+    pk, cac = cg.principal_kiem, lambda: cac_du_an_that(thu_muc_du_an)
+    return BoGiaoViec(cac_du_an=cac,
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
-                      don_sach=pk.don_sach if pk else None,
+                      don_sach=partial(giet_tam, pk) if pk else None, boc_luot=pk.boc_luot if pk else None,
+                      cong=dung_cong(pk, cg.thu_muc_kiem, cac_du_an=cac) if pk else None,
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                       p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c())
```

`tram/giao_viec/lenh.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/lenh.py b/tram/giao_viec/lenh.py
index b3e02b0..4aa5e73 100644
--- a/tram/giao_viec/lenh.py
+++ b/tram/giao_viec/lenh.py
@@ -1,4 +1,5 @@
-"""Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2) —
+"""Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2),
+`tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng) —
 chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
 Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
 import sys
@@ -54,6 +55,26 @@ def _kiem(args) -> int:
     return ma
 
 
+def _mo_cong(args) -> int:
+    from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
+    _, bo = _bo()
+    if bo.cong is None:
+        print("Chưa khai cach_ly.tram_kiem — không có cổng kiểm lại.")
+        return 2
+    print(f"Trạng thái hiện tại: {bo.cong.trang_thai()}")
+    if not args.dong_y and input("Gõ dong-y để thu hồi, quan sát và mở lại: ").strip() != "dong-y":
+        print("Không làm gì.")
+        return 1
+    try:
+        with giu_khoa():
+            bo.cong.mo_lai()
+    except LoiBanChep as e:
+        print(f"Vẫn đóng: {e}", file=sys.stderr)
+        return 1
+    print("Đã mở cổng kiểm lại.")
+    return 0
+
+
 def them_lenh_giao(sub) -> None:
     g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
     t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh rồi pha Git)")
@@ -64,3 +85,6 @@ def them_lenh_giao(sub) -> None:
     k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã đọc kế hoạch)")
     k.set_defaults(ham=_kho_kiem)
     g.add_parser("kiem", help="Kiểm sẵn sàng: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
+    c = g.add_parser("mo-cong-kiem", help="Thu hồi + quan sát tram-kiem rồi mở lại cổng kiểm lại (chờ dong-y)")
+    c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã xem lý do đóng)")
+    c.set_defaults(ham=_mo_cong)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `19 passed`. `UV_OFFLINE=1 uv run pytest -q` → **2351 passed**.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/cong_that.py tram/giao_viec/kiem_lai.py tram/giao_viec/bo.py tram/giao_viec/tick_pipeline.py \
  tram/giao_viec/noi_that.py tram/giao_viec/lenh.py tests/test_cong_that.py tests/test_kiem_lai_cong.py tests/test_noi_giao_viec.py
git commit -m "feat(giao-viec): kiểm lại qua cổng lượt + hồ sơ của lượt; tram giao mo-cong-kiem (C01, D45, 3C-D4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

### Task 3C-D5, 3C-D6, hợp đồng P1 — mã TDD đầy đủ (đợt 8, 16/10/2026)

**Nền:** `main` `0e33fbf` (P1 + 3C-B + Q1/Q2 + 3c đợt 7 đã ghép). **N₀ = 2650** (`UV_OFFLINE=1 uv run pytest -q` trên bản sao, PATH chặn + audithook: 0 lần chặn). Mã/test dưới đây là NGUYÊN VĂN bản đã chạy trên bản sao tuyến tính (mỗi task một commit, thứ tự ở "Sơ đồ đợt"); RED/GREEN ở Step 2/4 là kết quả thật. File có sẵn: áp bản vá bằng `git apply` (chép đúng khối `diff` vào tệp tạm, `git apply --check` trước). Mỗi task một commit, dòng cuối `Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>`.

**Ràng buộc riêng phần này:** không sửa `tram/kiem/{vong_doi,cay_tien_trinh,lenh_ngan,chay_lenh,chay_gioi_han,danh_tinh,cong_lich,han_tong}.py` (P1 sở hữu; thiếu khả năng → task P1). Test KHÔNG chạy thật `sudo`, `crontab`, `at`, `atq`, `atrm`, `batch`, `launchctl`, `security`, `dscl`, `sysadminctl`, `pkill`, `killall`, `sandbox-exec`, `createhomedir`, `visudo`, `dseditgroup`, `kill -1` — dùng `mo_cong`/`chay`/`chup`/`xac_minh`/`thu_hoi`/`han_tong` giả. Trước khi chạy toàn bộ: kiểm fixture không tác động host như "Kết quả chạy thử đợt 8".

#### Task 3C-H2 — `PrincipalKiem.kill_nhom` có hạn tuyệt đối qua P1 (hợp đồng H2) (S)

**Files:**
- Modify: `tram/giao_viec/principal_kiem.py` (`kill_nhom` qua `chay_ngan`; bỏ tham số `chay` và `run(timeout=20)`)
- Test: `tests/test_principal_kiem_p1.py` (mới); sửa `tests/test_cau_hinh_giao_viec.py` (bỏ test argv `run(timeout=20)` cũ), `tests/test_principal_kiem_hop_nhat.py` (`kill_nhom` không còn nhận `chay`)

**Interfaces:** Consumes `tram.kiem.lenh_ngan.chay_ngan(argv, *, timeout, doc=False) -> tuple[int | None, bytes]` (P1 T1). Produces `PrincipalKiem.kill_nhom(pgid: int, sig: int) -> None` — đúng kiểu `vong_doi.Kill`; người gọi: `chay_mot_lenh`, `danh_tinh.quan_sat`, `CongLich`, `gop_kill`.

**Acceptance:** argv = `boc_lenh(["/bin/kill", "-s", SIG, "--", "-<pgid>"])` ở cả hai cơ chế, khớp dòng sudoers; `timeout=5`; `sudo kill` treo → trả về khi hết hạn (không `wait()`), `vong_doi.thu_hoi` tự xác nhận bằng ảnh chụp; không còn tham số `chay`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cau_hinh_giao_viec.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_cau_hinh_giao_viec.py b/tests/test_cau_hinh_giao_viec.py
index b409a41..f4b3ccb 100644
--- a/tests/test_cau_hinh_giao_viec.py
+++ b/tests/test_cau_hinh_giao_viec.py
@@ -51,13 +51,3 @@ def test_principal_kiem_khong_con_trao_thu_quyen():
     """D22: không helper root, không ACL — `tram-kiem` sở hữu bản chép, chỉ còn `boc`, `kill_nhom`, `don_sach`."""
     assert not hasattr(PrincipalKiem, "trao") and not hasattr(PrincipalKiem, "thu")
     assert PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).co_che == "user"
-
-
-def test_kill_nhom_chay_cung_principal_khong_qua_shell():
-    import signal
-    goi = []
-    pk = PrincipalKiem("tram-kiem", ("sudo", "-n", "-u", "tram-kiem", "--"))
-    pk.kill_nhom(123, signal.SIGKILL, chay=lambda *args, **kw: goi.append((args, kw)))
-    assert goi == [((["sudo", "-n", "-u", "tram-kiem", "--", "/bin/kill", "-s", "KILL", "--", "-123"],),
-                    {"capture_output": True, "timeout": 20})]
-
```

`tests/test_principal_kiem_hop_nhat.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_principal_kiem_hop_nhat.py b/tests/test_principal_kiem_hop_nhat.py
index 93522a1..468c046 100644
--- a/tests/test_principal_kiem_hop_nhat.py
+++ b/tests/test_principal_kiem_hop_nhat.py
@@ -95,10 +95,11 @@ def test_tai_sinh_hoac_pgrep_loi_thi_nem(pgrep, khop):
 
 
 @pytest.mark.parametrize("co_che", ["user", "sandbox"])
-def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che):
+def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che, monkeypatch):
     pk, (goi, chay) = tu_cach_ly(f"{co_che}:tram-kiem"), chay_gia([1])
     pk.don_sach(chay=chay)
-    pk.kill_nhom(123, 9, chay=lambda argv, **kw: goi.append(argv))
+    monkeypatch.setattr("tram.giao_viec.principal_kiem.chay_ngan", lambda argv, **kw: goi.append(argv) or (0, b""))
+    pk.kill_nhom(123, 9)
     mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
     goi.append(pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]))
     qua_sudo = [a for a in goi if a[0] != "/usr/bin/pgrep"]
```

`tests/test_principal_kiem_p1.py` (mới):

```python
"""Hợp đồng P1 H2 (lát 3c): `PrincipalKiem.kill_nhom` gửi tín hiệu dưới `tram-kiem` qua `chay_ngan` — hạn TUYỆT ĐỐI 5 s,
không `subprocess.run(timeout=…)` (CPython còn `wait()` trần khi `kill()` bị từ chối). Không sudo: `chay_ngan` giả."""
import fnmatch
import inspect
import signal

import pytest

from tram.giao_viec import principal_kiem
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.tho.quyen_kiem import dong_sudoers_kiem


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_kill_nhom_qua_chay_ngan_han_5_giay_khop_sudoers(monkeypatch, co_che):
    goi, pk = [], tu_cach_ly(f"{co_che}:tram-kiem")
    monkeypatch.setattr(principal_kiem, "chay_ngan", lambda argv, **kw: goi.append((argv, kw)) or (0, b""))
    pk.kill_nhom(123, signal.SIGKILL)
    assert goi == [(pk.boc_lenh(["/bin/kill", "-s", "KILL", "--", "-123"]), {"timeout": 5})]
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
    assert mau == "ALL" or fnmatch.fnmatchcase(" ".join(goi[0][0][goi[0][0].index("--") + 1:]), mau)


def test_kill_nhom_qua_han_tra_ve_khong_cho_va_khong_nhan_chay(monkeypatch):
    goi = []
    monkeypatch.setattr(principal_kiem, "chay_ngan", lambda argv, **kw: goi.append(kw) or (None, b""))  # sudo treo
    PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--")).kill_nhom(9, 15)   # không ném/chờ
    assert goi == [{"timeout": 5}] and "chay" not in inspect.signature(PrincipalKiem.kill_nhom).parameters
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_principal_kiem_p1.py tests/test_cau_hinh_giao_viec.py tests/test_principal_kiem_hop_nhat.py -q`
Expected (thật): `5 failed, 27 passed` — `AttributeError: … principal_kiem … has no attribute 'chay_ngan'` (3 ca mới + 2 ca `test_moi_argv_duoi_tram_kiem_khop_sudoers` vì `kill_nhom` còn `run(timeout=20)`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/principal_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index 1a3cfee..dec7b08 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -13,6 +13,7 @@ from dataclasses import dataclass
 from pathlib import Path
 
 from tram.giao_viec.ban_chep import LoiBanChep
+from tram.kiem.lenh_ngan import chay_ngan
 from tram.tho.principal import SANDBOX_EXEC, doc_principal
 from tram.tho.quyen_kiem import HO_SO_KIEM
 
@@ -40,10 +41,11 @@ class PrincipalKiem:
         dau = [*self.boc, *ho_so, "-D", f"LUOT={wt}", "-D", f"NHA={nha}", ENV, f"HOME={nha}", f"TMPDIR={nha}/tmp/"]
         return lambda argv: [*dau, *argv]
 
-    def kill_nhom(self, pgid: int, sig: int, *, chay=subprocess.run) -> None:
-        """S6: kill trong cùng principal; không nuốt lỗi quyền/timeout."""
-        chay(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
-                           "--", f"-{pgid}"]), capture_output=True, timeout=20)
+    def kill_nhom(self, pgid: int, sig: int) -> None:
+        """P1 (H2): gửi tín hiệu cho cả nhóm DƯỚI `tram-kiem`, hạn TUYỆT ĐỐI 5 s (`chay_ngan`) — không `run(timeout)`.
+        Kết quả gửi không là bằng chứng: `vong_doi.thu_hoi` tự chụp cây để xác nhận."""
+        chay_ngan(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"), "--", f"-{pgid}"]),
+                  timeout=5)
 
     def don_sach(self, *, chay: Callable = subprocess.run, lan: int = 5, ngu: Callable = time.sleep) -> None:
         """Gỡ crontab và giết MỌI tiến trình của `tram-kiem` (chạy dưới chính `tram-kiem`), rồi trạm tự đếm bằng
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `32 passed`. `UV_OFFLINE=1 uv run pytest -q` → **2652 passed** (N₀ + 2).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/principal_kiem.py tests/test_principal_kiem_p1.py tests/test_cau_hinh_giao_viec.py tests/test_principal_kiem_hop_nhat.py
git commit -m "fix(giao-viec): PrincipalKiem.kill_nhom qua chay_ngan 5 s, bỏ run(timeout=20) (lát 3c, P1 H2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-H6 — kiểm lại xét dấu hạn tổng và `da_thu_hoi`; chưa thu hồi được thì cổng đóng (hợp đồng H6) (S)

**Files:**
- Modify: `tram/giao_viec/kiem_lai.py` (dấu `~/.tram/kiem-lai.dong` → `LoiBanChep` ở đầu hàm; `da_thu_hoi=False` → `LoiBanChep`)
- Test: `tests/test_kiem_lai_thu_hoi.py` (mới); sửa `tests/test_kiem_lai_principal.py` (kết quả giả có `da_thu_hoi=True`)

**Interfaces:** Consumes `tram.kiem.han_tong.cong_dong(dau: Path) -> bool` (3C-B T8), `KetQuaLenh.da_thu_hoi` (P1 T3), `CongLuot`/`CongDong` (3C-D2). Produces: `kiem_lai` ném `LoiBanChep` ở hai ca — `luong.py` ghi stderr, vòng sau thử lại, cổng đã `dong` nên lượt sau `CongDong`.

**Acceptance:** dấu còn → ném TRƯỚC mọi bước (kể cả kiểm đường dẫn cấm và spike tài liệu): không `cong.vao`, không chép, không nhận môi trường kiểm; một lệnh kiểm `da_thu_hoi=False` → ném (kể cả khi lệnh báo pass), bản chép vẫn dọn, cổng `dong` (`lượt g-1: LoiBanChep`), lượt sau `CongDong`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_kiem_lai_principal.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_kiem_lai_principal.py b/tests/test_kiem_lai_principal.py
index ef02738..f223972 100644
--- a/tests/test_kiem_lai_principal.py
+++ b/tests/test_kiem_lai_principal.py
@@ -65,7 +65,7 @@ def test_kiem_lai_truyen_kill_principal(m, monkeypatch):
     goi = []
     def gia(*args, **kw):
         goi.append(kw["kill"])
-        return SimpleNamespace(sang_lenh_kiem=lambda: {"ket_qua": "pass", "digest_log": "sha256:x"})
+        return SimpleNamespace(sang_lenh_kiem=lambda: {"ket_qua": "pass", "digest_log": "sha256:x"}, da_thu_hoi=True)
     monkeypatch.setattr("tram.giao_viec.kiem_lai.chay_mot_lenh", gia)
     assert chay(m, {"kiem.sh": "true\n"}, kill=kill).dat
     assert goi == [kill]
```

`tests/test_kiem_lai_thu_hoi.py` (mới):

```python
"""Hợp đồng P1 H6 (lát 3c): kiểm lại từ chối khi dấu hạn tổng `kiem-lai.dong` còn (harness S6 chưa xác nhận dọn), và
KHÔNG công nhận kết quả lệnh kiểm khi P1 báo chưa thu hồi được cây (`da_thu_hoi=False`) — ném, cổng lượt đóng, lượt sau
bị chặn. git/tar/rm thật trong `tmp_path` (boc đồng nhất), quan sát giả, không sudo."""
import pytest

from test_kiem_lai_cong import chay, cong
from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec import kiem_lai as kl
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong
from tram.kiem.chay_lenh import KetQuaLenh


def test_dau_han_tong_con_thi_khong_vao_cong_khong_chep(m, tram_home_tam):
    c = cong(m[2])
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()                      # harness S6 quá hạn, dọn chưa xác nhận
    with pytest.raises(LoiBanChep, match="kiem-lai.dong"):
        chay(m, c)
    assert c.trang_thai() == {"trang_thai": "mo"} and ban_chep(m) == []


def test_lenh_chua_thu_hoi_thi_khong_cong_nhan_dong_cong_chan_luot_sau(m, monkeypatch):
    c = cong(m[2])
    monkeypatch.setattr(kl, "chay_mot_lenh", lambda lenh, argv, **kw: KetQuaLenh(lenh, "pass", "", "sha256:0", 0,
                                                                                 da_thu_hoi=False))
    with pytest.raises(LoiBanChep, match="chưa thu hồi"):
        chay(m, c)
    assert c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"} and ban_chep(m) == []
    with pytest.raises(CongDong):
        chay(m, c)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_kiem_lai_thu_hoi.py tests/test_kiem_lai_cong.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py -q`
Expected (thật): `2 failed, 17 passed` — `Failed: DID NOT RAISE <class 'tram.giao_viec.ban_chep.LoiBanChep'>` (cả hai ca mới)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kiem_lai.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index 5760f42..cb518b1 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -9,17 +9,21 @@ Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (
 không worktree, không trao quyền). Một lần kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không
 sạch → ném, KHÔNG trả kết quả. 3C-D (C01, D45): `cong` mở mới được vào lượt (trước khi chép, nhận môi trường); mọi
 lệnh của lượt qua `boc_luot(wt)` (hồ sơ Seatbelt của lượt); lượt ném lỗi → đóng cổng; xong → `cong.ra()` thu hồi và
-quan sát."""
+quan sát. Hợp đồng P1 (H6): dấu hạn tổng `kiem-lai.dong` còn → từ chối trước cổng; P1 báo chưa thu hồi cây của một
+lệnh (`da_thu_hoi=False`) → ném, không công nhận kết quả, cổng đóng."""
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.lenh import khop_bat_ky
-from tram.giao_viec.ban_chep import CayKhacNguon, chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
+from tram.duong_dan import tram_home
+from tram.giao_viec.ban_chep import (CayKhacNguon, LoiBanChep, chep_ban, don_ban, giu_khoa, nhan_moi_truong,
+                                     ten_ban_chep)
 from tram.giao_viec.cong_luot import CongLuot
 from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
 from tram.kiem.diff import diff_cham_cam
+from tram.kiem.han_tong import cong_dong
 from tram.kiem.moi_truong import LoiMoiTruongKiem
 
 THOI_GIAN_CHO = 900
@@ -45,6 +49,8 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
              don_sach: Callable[[], None] | None = None,
              kill: Callable[[int, int], None] = _kill_nhom,
              cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None) -> KetQuaKiemLai:
+    if cong_dong(tram_home() / "kiem-lai.dong"):                    # H6: trước mọi bước, kể cả spike tài liệu
+        raise LoiBanChep("dấu hạn tổng kiem-lai.dong còn: harness chưa xác nhận dọn — Đại ca kiểm tay rồi xoá dấu")
     cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
@@ -91,6 +97,8 @@ def _tren_ban_chep(kho_git: Path, commit: str, mt, wt: Path, *, giao_id: str, le
         for i, lenh in enumerate(lenh_kiem, 1):
             kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
                                log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
+            if not kq.da_thu_hoi:
+                raise LoiBanChep(f"lệnh kiểm {i}: chưa thu hồi được cây tiến trình — không công nhận kết quả")
             ket_qua.append(kq.sang_lenh_kiem())
     finally:
         don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `19 passed`. Toàn bộ → **2654 passed** (N₀ + 4).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kiem_lai.py tests/test_kiem_lai_thu_hoi.py tests/test_kiem_lai_principal.py
git commit -m "fix(giao-viec): kiểm lại từ chối khi còn dấu hạn tổng hoặc lệnh chưa thu hồi được (lát 3c, P1 H6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-D5a — thu hồi theo UID qua P1 rồi xác minh bằng ảnh chụp cây; `cron_at` qua `CongLich` (H3/H4) (S)

Thay "Task 3C-D5 — nối thu hồi theo UID" cũ: hàm `thu_hoi_theo_uid(ten, *, kiem_uid, chay, han)` của 3C-D4 đoán hợp đồng P1/3C-B (`chay(argv, principal=, han=)`) — khác mã thật. Viết lại theo module thật: `mo_cong_lich` (3C-B T9) chứng minh UID thực rồi chỉ cho chạy argv sau đúng tiền tố đã xác minh, chạy bằng `chay_gioi_han` (P1, có hạn, sở hữu cây). `giet_tam` (`subprocess.run(timeout)` dưới sudo — vi phạm H1) bị bỏ.

**Files:**
- Modify: `tram/giao_viec/cong_that.py` (`cho_het_uid`, `thu_hoi_theo_uid(pk, …)` mới; bỏ `giet_tam`; `dung_cong` mặc định thu hồi theo UID)
- Modify: `tram/giao_viec/quan_sat_kiem.py` (`mo_cong_kiem`; `cron_at` mặc định chạy qua `CongLich`)
- Modify: `tram/giao_viec/noi_that.py` (`don_sach=partial(thu_hoi_theo_uid, pk)`)
- Test: `tests/test_thu_hoi_uid.py` (mới); sửa `tests/test_cong_that.py` (bỏ 2 test `giet_tam`/`thu_hoi_theo_uid` cũ), `tests/test_kiem_lai_cong.py`, `tests/test_noi_giao_viec.py`

**Interfaces:**
- Consumes: `mo_cong_lich(ten, boc, kill, *, chay=None, xac_minh=xac_minh_uid) -> CongLich` và `CongLich(tien_to, uid, chay)` (3C-B T9; `CongLich.__call__(argv, **kw)` ném `LoiDanhTinh` khi argv không sau tiền tố); `chup_he() -> list[TienTrinh]` (P1 T1, `TienTrinh.uid/ruid`); `LoiDanhTinh`, `LoiThuHoi`; `PrincipalKiem.kill_nhom` (3C-H2).
- Produces: `quan_sat_kiem.mo_cong_kiem(pk, mo=None) -> CongLich` (lỗi danh tính → `LoiBanChep` thông báo cố định); `cron_at(pk, *, chay=None)` (cơ chế `sandbox` → `LoiBanChep`: sudoers ghim hồ sơ cấm exec `crontab`/`atq` cho mọi lệnh dưới `tram-kiem`, cách quan sát chưa đo — G3); `cong_that.cho_het_uid(uid, *, chup=chup_he, han=5.0, ngu=time.sleep)`; `cong_that.thu_hoi_theo_uid(pk, *, mo_cong=None, cho_het=cho_het_uid)`; `HAN_HET = 5.0`. 3C-D5b thêm tham số `don_he`.

**Acceptance:** thứ tự mở cổng (UID thực) → `kill -KILL -1` dưới `tram-kiem` qua cổng (`capture_output=True, timeout=HAN`) → ảnh chụp tới khi không còn tiến trình uid/ruid đó (xác SIGKILL được gặt trong ≤ 5 s); sai danh tính → `LoiBanChep`, không kill, không chụp; `kill -1` ném `LoiThuHoi`/`TimeoutExpired`/`LoiDanhTinh` → `LoiBanChep` thông báo cố định (H4; là `OSError` nên `don_ban` vẫn `rm` bản chép); còn tiến trình (setuid: ruid `tram-kiem`, euid root) hoặc `ps` lỗi → `LoiBanChep`; `cron_at` mặc định qua `CongLich` (cả `find` của trạm — lệnh quan sát cho phép), lỗi khi chạy (`LoiThuHoi`/`TimeoutExpired`/`LoiDanhTinh`) → `LoiBanChep` thông báo cố định; sai danh tính → không lệnh lịch nào; trong lượt KHÔNG gỡ lịch.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cong_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_cong_that.py b/tests/test_cong_that.py
index 9a1c41d..73c586a 100644
--- a/tests/test_cong_that.py
+++ b/tests/test_cong_that.py
@@ -1,4 +1,4 @@
-"""3C-D4/D5: cổng thật ghép thu hồi + quan sát; thu hồi theo UID (P1/3C-B qua tham số) không gỡ lịch; hồ sơ Seatbelt
+"""3C-D4/D5: cổng thật ghép thu hồi + quan sát; thu hồi theo UID (`test_thu_hoi_uid.py`) không gỡ lịch; hồ sơ Seatbelt
 đã cài phải đúng chủ/quyền/nội dung; tệp môi trường kiểm của mọi dự án phải kín. Không chạy lệnh hệ thống thật."""
 import os
 from functools import partial
@@ -7,28 +7,11 @@ from types import SimpleNamespace
 import pytest
 
 from tram.giao_viec.ban_chep import LoiBanChep
-from tram.giao_viec.cong_that import GIET, dung_cong, env_kin, giet_tam, ho_so_cai, thu_hoi_theo_uid
+from tram.giao_viec.cong_that import dung_cong, env_kin, ho_so_cai, thu_hoi_theo_uid
 from tram.giao_viec.principal_kiem import tu_cach_ly
 from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, tep_ngoai, tien_trinh
 
 
-def test_thu_hoi_theo_uid_kiem_uid_truoc_roi_kill_moi_tien_trinh_co_han():
-    goi = []
-    thu_hoi_theo_uid("tram-kiem", kiem_uid=lambda t: goi.append(("uid", t)), chay=lambda a, **kw: goi.append((a, kw)))
-    assert goi == [("uid", "tram-kiem"), (["/bin/kill", "-KILL", "-1"], {"principal": "tram-kiem", "han": 30})]
-
-
-def test_thu_hoi_khong_kill_khi_uid_sai_va_giet_tam_khong_go_lich():
-    goi, pk = [], tu_cach_ly("user:tram-kiem")
-
-    def sai(t):
-        raise LoiBanChep("UID hiệu lực 501 ≠ UID tram-kiem")
-    with pytest.raises(LoiBanChep, match="UID"):
-        thu_hoi_theo_uid("tram-kiem", kiem_uid=sai, chay=lambda a, **kw: goi.append(a))
-    giet_tam(pk, chay=lambda a, **kw: goi.append((a, kw["timeout"])))
-    assert goi == [(pk.boc_lenh(GIET), 120)]
-
-
 def test_ho_so_cai_dung_chu_quyen_noi_dung(tmp_path, tram_home_tam):
     p = tmp_path / "hs.sb"
     p.write_text(f'(version 1)\n(deny default)\n(deny file-read* (subpath "{tram_home_tam}"))\n')
@@ -67,7 +50,7 @@ def test_env_kin_doi_0600_cua_tram(tmp_path):
 def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam, tmp_path):
     pk = tu_cach_ly("user:tram-kiem")
     c = dung_cong(pk, tmp_path, cac_du_an=list)
-    assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is giet_tam
+    assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is thu_hoi_theo_uid
     ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
     assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin]
     assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
```

`tests/test_kiem_lai_cong.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_kiem_lai_cong.py b/tests/test_kiem_lai_cong.py
index abdae7c..94ef769 100644
--- a/tests/test_kiem_lai_cong.py
+++ b/tests/test_kiem_lai_cong.py
@@ -12,7 +12,7 @@ from tram.cau_hinh.tram import CauHinhTram
 from tram.giao_viec import lenh
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongDong, CongLuot
-from tram.giao_viec.cong_that import giet_tam
+from tram.giao_viec.cong_that import thu_hoi_theo_uid
 from tram.giao_viec.git_kiem import fetch
 from tram.giao_viec.kiem_lai import kiem_lai
 from tram.giao_viec.noi_that import dung_bo_that
@@ -72,7 +72,7 @@ def test_bo_that_co_cong_va_boc_luot_khi_khai_tram_kiem(tram_home_tam, tmp_path)
     pk = tu_cach_ly("user:tram-kiem")
     bo = dung_bo_that(CauHinhGiaoViec(thu_muc_kiem=tmp_path / "k", principal_kiem=pk), CauHinhTram())
     assert bo.cong.tep == tram_home_tam / "kiem-lai" / "cong.json" and bo.boc_luot == pk.boc_luot
-    assert bo.don_sach.func is giet_tam                            # trong lượt chỉ giết, không gỡ lịch
+    assert bo.don_sach.func is thu_hoi_theo_uid and bo.cong.thu_hoi.func is thu_hoi_theo_uid   # chỉ giết, không gỡ lịch
     assert dung_bo_that(CauHinhGiaoViec(), CauHinhTram()).cong is None
 
 
```

`tests/test_noi_giao_viec.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_noi_giao_viec.py b/tests/test_noi_giao_viec.py
index a6064ff..f8d5722 100644
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -63,7 +63,7 @@ def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach.args == (PK,)   # 3C-D4: giet_tam
+    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach.args == (PK,)   # 3C-D5: theo UID
     assert bo.kill == PK.kill_nhom
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
```

`tests/test_thu_hoi_uid.py` (mới):

```python
"""3C-D5 (C01, hợp đồng P1/3C-B): thu hồi theo UID — mở `CongLich` (UID thực đã chứng minh) rồi `kill -KILL -1` dưới
`tram-kiem` qua primitive có hạn, rồi TRẠM xác minh bằng ảnh chụp `ps`; `cron_at` mặc định cũng chạy qua `CongLich`.
Sai danh tính → không lệnh nào chạy. Không sudo/ps thật: `mo_cong`, `chup`, `chay` giả."""
import subprocess

import pytest

from tram.giao_viec import quan_sat_kiem
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import GIET, cho_het_uid, thu_hoi_theo_uid
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import HAN, cron_at
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.cong_lich import CongLich
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi


def mo_gia(pk, goi, uid=777):
    def mo(ten, boc, kill):
        goi.append(("mo", ten, boc, kill))
        return CongLich(tuple(boc([])), uid, lambda a, **kw: goi.append((a, kw)) or subprocess.CompletedProcess(a, 0))
    return mo


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_xac_minh_uid_roi_kill_moi_tien_trinh_co_han_roi_chup_cay(co_che):
    goi, pk = [], tu_cach_ly(f"{co_che}:tram-kiem")
    thu_hoi_theo_uid(pk, mo_cong=mo_gia(pk, goi), cho_het=lambda uid: goi.append(("cho_het", uid)))
    assert goi == [("mo", "tram-kiem", pk.boc_lenh, pk.kill_nhom),
                   (pk.boc_lenh(GIET), {"capture_output": True, "timeout": HAN}), ("cho_het", 777)]


@pytest.mark.parametrize("loi", [LoiDanhTinh("UID 501 trùng người vận hành"), LoiThuHoi("cây dò chưa thu hồi")])
def test_sai_danh_tinh_khong_kill_khong_chup(loi):
    goi = []

    def mo(ten, boc, kill):
        raise loi
    with pytest.raises(LoiBanChep, match="không xác minh được UID"):
        thu_hoi_theo_uid(tu_cach_ly("user:tram-kiem"), mo_cong=mo, cho_het=goi.append)
    assert goi == []


def test_cho_het_uid_doi_xac_song_duoc_gat_roi_moi_dat():
    anh, ngu = [[TienTrinh(10, 1, 10, 777, 777), TienTrinh(11, 1, 11, 0, 777)], [TienTrinh(12, 1, 12, 501, 501)]], []
    cho_het_uid(777, chup=lambda: anh.pop(0), han=5, ngu=ngu.append)
    assert ngu == [0.2] and anh == []


@pytest.mark.parametrize("chup, khop", [
    (lambda: [TienTrinh(10, 1, 10, 0, 777)], "còn 1 tiến trình uid 777"),      # setuid: ruid tram-kiem, euid root
    (lambda: (_ for _ in ()).throw(OSError("ps mã 1")), "không chụp được"),
    (lambda: (_ for _ in ()).throw(ValueError("dòng ps sai dạng")), "không chụp được")])
def test_cho_het_uid_con_hoac_ps_loi_thi_nem(chup, khop):
    with pytest.raises(LoiBanChep, match=khop):
        cho_het_uid(777, chup=chup, han=0, ngu=lambda s: None)


def test_cron_at_mac_dinh_qua_cong_lich_da_xac_minh(monkeypatch):
    goi, pk = [], tu_cach_ly("user:tram-kiem")
    kq = [(1, "", "crontab: no crontab for tram-kiem\n"), (0, "", ""), (0, "", "")]

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *kq.pop(0))
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", lambda ten, boc, kill: CongLich(tuple(boc([])), 777, chay))
    cron_at(pk)
    assert goi == [pk.boc_lenh(["/usr/bin/crontab", "-l"]), pk.boc_lenh(["/usr/bin/atq"]),
                   ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]

    def sai(ten, boc, kill):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", sai)
    with pytest.raises(LoiBanChep, match="không xác minh được UID"):
        cron_at(pk)
    assert len(goi) == 3                                           # sai danh tính: không thêm lệnh lịch nào


@pytest.mark.parametrize("loi", [LoiThuHoi("['kill'] quá hạn"), subprocess.TimeoutExpired(["sudo"], 120),
                                 LoiDanhTinh("lệnh không chạy dưới principal đã xác minh")])
def test_kill_loi_thanh_loi_ban_chep_co_dinh_khong_chup(loi):
    goi, pk = [], tu_cach_ly("user:tram-kiem")

    def chay(a, **kw):
        raise loi
    with pytest.raises(LoiBanChep, match=r"kill -1 không xác nhận được \((LoiThuHoi|TimeoutExpired|LoiDanhTinh)\)$"):
        thu_hoi_theo_uid(pk, mo_cong=lambda t, b, k: CongLich(tuple(b([])), 777, chay), cho_het=goi.append)
    assert goi == []                                               # don_ban bắt OSError → vẫn rm bản chép


def test_cron_at_co_che_sandbox_dong_cong_khong_chay_gi(monkeypatch):
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", lambda *a: pytest.fail("không được mở cổng lịch"))
    with pytest.raises(LoiBanChep, match="sandbox"):
        cron_at(tu_cach_ly("sandbox:tram-kiem"))


def test_cron_at_loi_khi_chay_thanh_loi_ban_chep_co_dinh():
    def treo(argv, **kw):
        raise LoiThuHoi("['crontab'] quá hạn")
    with pytest.raises(LoiBanChep, match=r"quan sát lịch không xác nhận được \(LoiThuHoi\)$"):
        cron_at(tu_cach_ly("user:tram-kiem"), chay=treo)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_thu_hoi_uid.py tests/test_cong_that.py tests/test_kiem_lai_cong.py tests/test_noi_giao_viec.py tests/test_quan_sat_kiem.py -q`
Expected (thật): `1 error` — `ImportError: cannot import name 'cho_het_uid' from 'tram.giao_viec.cong_that'`

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index 84bd362..f98d70e 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -1,13 +1,15 @@
 """Cổng lượt THẬT của trạm (3C-D4/D5; C01, D45): ghép thu hồi + mọi quan sát vào `CongLuot`.
 
-Thu hồi: `kill -KILL -1` dưới principal (giết mọi tiến trình cùng UID, kể cả `setsid`), KHÔNG gỡ lịch — lịch để
-`cron_at` thấy và đóng cổng. `thu_hoi_theo_uid` (sau P1, 3C-B) thêm kiểm UID thật và primitive có hạn; tới lúc đó
-`giet_tam` dùng `boc_lenh` + `subprocess.run(timeout)`. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
+Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tram-kiem` đã chứng minh — không tin env/argv), rồi
+`kill -KILL -1` dưới principal qua `chay_gioi_han` (hạn hữu hạn, sở hữu cây; giết mọi tiến trình cùng UID, kể cả
+`setsid`). Mã thoát không là bằng chứng: TRẠM chụp `ps` (cột số) tới khi không còn tiến trình nào có uid/ruid đó.
+KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
 Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1).
 launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>`) cắm thêm khi T11 ghép và G3 đo định dạng; trước đó I1 KHÔNG bật
 `giao_viec.bat`."""
 import os
 import subprocess
+import time
 from collections.abc import Callable
 from functools import partial
 from pathlib import Path
@@ -15,21 +17,40 @@ from pathlib import Path
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongLuot
-from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, tep_ngoai, tien_trinh
+from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, mo_cong_kiem, tep_ngoai, tien_trinh
+from tram.kiem.cay_tien_trinh import chup_he
+from tram.kiem.danh_tinh import LoiDanhTinh
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.quyen_kiem import HO_SO_KIEM
 
 GIET = ["/bin/kill", "-KILL", "-1"]
+HAN_HET = 5.0
 
 
-def giet_tam(pk, *, chay: Callable = subprocess.run) -> None:
-    chay(pk.boc_lenh(GIET), capture_output=True, timeout=HAN)
+def cho_het_uid(uid: int, *, chup: Callable = chup_he, han: float = HAN_HET, ngu: Callable = time.sleep) -> None:
+    """Ảnh chụp `ps` của TRẠM: không còn tiến trình nào có uid hoặc ruid = `uid` (xác của SIGKILL được gặt trong chốc
+    lát — chờ tới `han`). Còn (setuid, kẹt trong nhân) hoặc `ps` lỗi/sai dạng → `LoiBanChep`."""
+    het = time.monotonic() + han
+    while True:
+        try:
+            con = [t for t in chup() if uid in (t.uid, t.ruid)]
+        except (OSError, ValueError) as e:
+            raise LoiBanChep(f"không chụp được bảng tiến trình ({type(e).__name__})") from None
+        if not con:
+            return
+        if time.monotonic() >= het:
+            raise LoiBanChep(f"còn {len(con)} tiến trình uid {uid} sau kill -1 (setuid hoặc kẹt nhân)")
+        ngu(0.2)
 
 
-def thu_hoi_theo_uid(ten: str, *, kiem_uid: Callable[[str], None], chay: Callable, han: float = 30) -> None:
-    """Sau P1, 3C-B: kiểm UID thật (3C-B) RỒI `kill -KILL -1` dưới `ten` qua primitive có hạn (P1). Mã thoát không là
-    bằng chứng (mã 1 = không còn gì để giết); bằng chứng là `tien_trinh` của trạm. Hết hạn/lỗi → ném."""
-    kiem_uid(ten)
-    chay(GIET, principal=ten, han=han)
+def thu_hoi_theo_uid(pk, *, mo_cong: Callable | None = None, cho_het: Callable[[int], None] = cho_het_uid) -> None:
+    """UID thực (3C-B) → `kill -KILL -1` dưới `tram-kiem` có hạn (P1) → ảnh chụp không còn ai. Lỗi → ném."""
+    cong = mo_cong_kiem(pk, mo_cong)
+    try:
+        cong(pk.boc_lenh(GIET), capture_output=True, timeout=HAN)
+    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:      # P1 H4: thông báo cố định, là OSError
+        raise LoiBanChep(f"{pk.ten}: kill -1 không xác nhận được ({type(e).__name__})") from None
+    cho_het(cong.uid)
 
 
 def ho_so_cai(p: Path = HO_SO_KIEM, *, chu: int = 0) -> None:
@@ -58,6 +79,6 @@ def env_kin(cac_du_an: Callable[[], list]) -> None:
 def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
               thu_hoi: Callable[[], None] | None = None) -> CongLuot:
     goc = goc or tram_home() / "kiem"
-    return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(giet_tam, pk),
+    return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
                     quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
                               partial(cron_at, pk), ho_so_cai, partial(env_kin, cac_du_an)])
```

`tram/giao_viec/noi_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/noi_that.py b/tram/giao_viec/noi_that.py
index a898f00..f565bf6 100644
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -20,7 +20,7 @@ from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
 from tram.giao_viec.dieu_kien import ASSIGNEE
 from tram.giao_viec.doc_beads import DocBeads
 from tram.giao_viec.luong import bat_dau_luong_giao
-from tram.giao_viec.cong_that import dung_cong, giet_tam
+from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
 from tram.kiem.chay_lenh import _kill_nhom
 
 
@@ -54,7 +54,7 @@ def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
     return BoGiaoViec(cac_du_an=cac,
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
-                      don_sach=partial(giet_tam, pk) if pk else None, boc_luot=pk.boc_luot if pk else None,
+                      don_sach=partial(thu_hoi_theo_uid, pk) if pk else None, boc_luot=pk.boc_luot if pk else None,
                       cong=dung_cong(pk, cg.thu_muc_kiem, cac_du_an=cac) if pk else None,
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
```

`tram/giao_viec/quan_sat_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/quan_sat_kiem.py b/tram/giao_viec/quan_sat_kiem.py
index 3e09d80..b9548b2 100644
--- a/tram/giao_viec/quan_sat_kiem.py
+++ b/tram/giao_viec/quan_sat_kiem.py
@@ -4,14 +4,20 @@ Không phải ranh giới cách ly (ranh giới là hồ sơ Seatbelt của lư
 sát được thì ném, `CongLuot` đóng cổng. `tep_ngoai` tìm tệp của `tram-kiem` ở MỌI độ sâu trong vùng ghi-chung (sửa lỗ
 `_sot -maxdepth 1` mà Codex nêu: tệp con trong thư mục cha 0777 của user khác), cắt nhánh thư mục user khác mà trạm
 không đọc được; `goc_rong` đòi gốc bản chép trống (bản chép, nhà lượt, thứ dời đi đều phải đã dọn); `cron_at` đòi
-không có crontab/việc `at` (KHÔNG gỡ — gỡ là việc của Đại ca sau khi xem). `DARWIN_USER_*` (0700 của `tram-kiem`), thư
-mục ghi qua nhóm `staff` ngoài `GOC_CHUNG`, launchd (T11) KHÔNG nằm ở đây — chỉ hồ sơ Seatbelt chặn."""
+không có crontab/việc `at` (KHÔNG gỡ — gỡ là việc của Đại ca sau khi xem). Thư mục ghi qua nhóm `staff` ngoài
+`GOC_CHUNG` không quan sát — chỉ hồ sơ Seatbelt chặn; `DARWIN_USER_*` dọn ở thu hồi (`thu_muc_he.py`).
+3C-D5 (hợp đồng P1 H3): lệnh dưới `tram-kiem` của quan sát đi qua `CongLich` (`mo_cong_kiem` — UID thực đã chứng minh,
+`chay_gioi_han` có hạn); không chứng minh được danh tính → `LoiBanChep`, không chạy lệnh lịch nào. Cơ chế `sandbox`:
+sudoers ghim hồ sơ cấm exec `crontab`/`atq` cho MỌI lệnh dưới `tram-kiem` — cách quan sát lịch chưa đo (G3) → ném."""
 import os
 import subprocess
 from collections.abc import Callable
 from pathlib import Path
 
 from tram.giao_viec.ban_chep import LoiBanChep
+from tram.kiem.cong_lich import CongLich, mo_cong_lich
+from tram.kiem.danh_tinh import LoiDanhTinh
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.principal import USER_RE
 
 PGREP, FIND = "/usr/bin/pgrep", "/usr/bin/find"
@@ -25,6 +31,14 @@ def _ten(ten: str) -> str:
     return ten
 
 
+def mo_cong_kiem(pk, mo: Callable | None = None) -> CongLich:
+    """`CongLich` của `tram-kiem` (P1 H3/H4): lỗi danh tính/thu hồi cây dò → `LoiBanChep` thông báo cố định."""
+    try:
+        return (mo or mo_cong_lich)(pk.ten, pk.boc_lenh, pk.kill_nhom)
+    except (LoiDanhTinh, LoiThuHoi) as e:
+        raise LoiBanChep(f"{pk.ten}: không xác minh được UID thực ({type(e).__name__})") from None
+
+
 def tien_trinh(ten: str, *, chay: Callable = subprocess.run) -> None:
     """Không còn tiến trình nào có UID thực (`-U`) hoặc hiệu lực (`-u`) là `ten` — pgrep mã 1 cả hai."""
     for co in ("-U", "-u"):
@@ -56,14 +70,24 @@ def goc_rong(goc: Path) -> None:
         raise LoiBanChep(f"gốc bản chép còn {len(con)} mục của lượt trước — chưa dọn")
 
 
-def cron_at(pk, *, chay: Callable = subprocess.run) -> None:
+def _ra_lich(chay: Callable, argv: list[str]):
+    try:
+        return chay(argv, capture_output=True, text=True, timeout=HAN)
+    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
+        raise LoiBanChep(f"lệnh quan sát lịch không xác nhận được ({type(e).__name__})") from None
+
+
+def cron_at(pk, *, chay: Callable | None = None) -> None:
     """`tram-kiem` không có crontab (`crontab -l` mã 1, "no crontab for") và không có việc `at` (`atq` rỗng; trạm tự
     tìm tệp của nó trong `/usr/lib/cron/jobs`). Thấy hay không chắc → ném; không tự gỡ để quan sát không bị xoá dấu."""
-    r = chay(pk.boc_lenh(["/usr/bin/crontab", "-l"]), capture_output=True, text=True, timeout=HAN)
+    if pk.co_che == "sandbox":
+        raise LoiBanChep(f"{pk.ten}: cơ chế sandbox cấm exec crontab/atq — chưa đo cách quan sát lịch (G3), cổng đóng")
+    chay = chay or mo_cong_kiem(pk)
+    r = _ra_lich(chay, pk.boc_lenh(["/usr/bin/crontab", "-l"]))
     if r.returncode != 1 or "no crontab for" not in r.stderr:
         raise LoiBanChep(f"{pk.ten}: crontab -l mã {r.returncode} — có crontab hoặc không xác nhận được")
     for argv in (pk.boc_lenh(["/usr/bin/atq"]), [FIND, "/usr/lib/cron/jobs", "-user", _ten(pk.ten)]):
-        r = chay(argv, capture_output=True, text=True, timeout=HAN)
+        r = _ra_lich(chay, argv)
         if r.returncode or r.stdout.strip():
             raise LoiBanChep(f"{pk.ten}: {argv[-1] if argv[0] == FIND else 'atq'} mã {r.returncode} — có việc at "
                              "hoặc không xác nhận được")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `47 passed`. Toàn bộ → **2666 passed** (N₀ + 16).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/cong_that.py tram/giao_viec/quan_sat_kiem.py tram/giao_viec/noi_that.py tests/test_thu_hoi_uid.py tests/test_cong_that.py tests/test_kiem_lai_cong.py tests/test_noi_giao_viec.py
git commit -m "feat(giao-viec): thu hồi tram-kiem theo UID thực qua CongLich + chay_gioi_han, xác minh bằng ảnh chụp ps (lát 3c 3C-D5, P1 H1/H3/H4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-D5b — phần còn giữ của r47 T11: `DARWIN_USER_*` dọn + xác nhận, mã lỗi chặn (dot6-Q01) (S)

r47 T11 (`don_tram_kiem.don_tep`) kiểm returncode của `getconf`, lệnh xoá và lệnh xác nhận `DARWIN_USER_*` kèm 3 regression runner giả. Phần còn lại của T11 (gỡ lịch, nền launchd, `_sot` quét cấp một) bị thay bằng cổng lượt + hồ sơ (3C-D1…D4) và KHÔNG đưa lại. Ở đây giữ đúng sửa Q01, đặt sau thu hồi theo UID (lúc không còn tiến trình `tram-kiem`), lệnh chạy qua cùng `CongLich`. Không đóng C01 bằng sửa này.

**Files:**
- Create: `tram/giao_viec/thu_muc_he.py` (`THU_MUC_HE`, `DUONG`, `don_thu_muc_he`)
- Modify: `tram/giao_viec/cong_that.py` (`thu_hoi_theo_uid(..., don_he=don_thu_muc_he)` gọi sau `cho_het`)
- Test: `tests/test_thu_muc_he.py` (mới; 3 ca Q01, đường dẫn lạ/còn mục, lỗi `CongLich`, cơ chế `sandbox`, nối mặc định qua cùng `CongLich`); sửa `tests/test_thu_hoi_uid.py` (thứ tự có `don_he`)

**Interfaces:** Consumes `pk.boc_lenh`, `CongLich` (3C-D5a). Produces `don_thu_muc_he(pk, chay: Callable) -> None` (`chay(argv, capture_output=True, text=True, timeout=120)`); `thu_hoi_theo_uid(pk, *, mo_cong=None, cho_het=cho_het_uid, don_he=don_thu_muc_he)`.

**Acceptance:** với mỗi `DARWIN_USER_DIR/TEMP_DIR/CACHE_DIR`: `getconf` → `find p -mindepth 1 -maxdepth 1 -exec /bin/rm -rf {} +` → `find p -mindepth 1 -print -quit`, đều dưới `tram-kiem`; mã ≠ 0 ở bất kỳ bước nào (kể cả getconf in đường hợp lệ, find lỗi in rỗng), đường không đúng dạng `/(private/)var/folders/<a>/<b>/{0,T,C}` (kể cả `..`, thư mục cha), còn mục, lỗi của `CongLich` (`LoiThuHoi`/`TimeoutExpired`/`LoiDanhTinh`) → `LoiBanChep` thông báo cố định. Cơ chế `sandbox`: bỏ qua (sudoers ghim hồ sơ cấm ghi ở đây cho mọi lệnh dưới `tram-kiem`, kể cả `rm` của trạm — chạy là luôn đóng cổng). **Đánh đổi có ghi:** xoá trước khi quan sát nội dung (G3.6 đo thứ hệ thống tự tạo; sau đó mới quyết "còn mục lạ → đóng cổng").

- [ ] **Step 1: Viết test thất bại**

`tests/test_thu_hoi_uid.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_thu_hoi_uid.py b/tests/test_thu_hoi_uid.py
index a9c4b50..aa4245b 100644
--- a/tests/test_thu_hoi_uid.py
+++ b/tests/test_thu_hoi_uid.py
@@ -26,9 +26,10 @@ def mo_gia(pk, goi, uid=777):
 @pytest.mark.parametrize("co_che", ["user", "sandbox"])
 def test_xac_minh_uid_roi_kill_moi_tien_trinh_co_han_roi_chup_cay(co_che):
     goi, pk = [], tu_cach_ly(f"{co_che}:tram-kiem")
-    thu_hoi_theo_uid(pk, mo_cong=mo_gia(pk, goi), cho_het=lambda uid: goi.append(("cho_het", uid)))
+    thu_hoi_theo_uid(pk, mo_cong=mo_gia(pk, goi), cho_het=lambda uid: goi.append(("cho_het", uid)),
+                     don_he=lambda p, chay: goi.append(("don_he", p, chay.uid)))
     assert goi == [("mo", "tram-kiem", pk.boc_lenh, pk.kill_nhom),
-                   (pk.boc_lenh(GIET), {"capture_output": True, "timeout": HAN}), ("cho_het", 777)]
+                   (pk.boc_lenh(GIET), {"capture_output": True, "timeout": HAN}), ("cho_het", 777), ("don_he", pk, 777)]
 
 
 @pytest.mark.parametrize("loi", [LoiDanhTinh("UID 501 trùng người vận hành"), LoiThuHoi("cây dò chưa thu hồi")])
```

`tests/test_thu_muc_he.py` (mới):

```python
"""Phần còn giữ của r47 T11 (C01 hàng 6; dot6-Q01): dọn `DARWIN_USER_*` của `tram-kiem` dưới chính nó rồi xác nhận
rỗng — MÃ LỖI của getconf/xoá/xác nhận đều chặn, kể cả khi stdout trông hợp lệ hay rỗng. Runner giả, không sudo."""
import subprocess

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import thu_hoi_theo_uid
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.thu_muc_he import THU_MUC_HE, don_thu_muc_he
from tram.kiem.cong_lich import CongLich

PK = tu_cach_ly("user:tram-kiem")
GOC = "/private/var/folders/ab/xyz/"


def gia(hong=None, duong=GOC, con=""):
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        assert argv[:len(PK.boc)] == list(PK.boc) and kw == {"capture_output": True, "text": True, "timeout": 120}
        x = argv[len(PK.boc):]
        buoc = "getconf" if x[0] == "/usr/bin/getconf" else ("xoa" if "-exec" in x else "xac-nhan")
        ra = {"getconf": duong + {"DARWIN_USER_DIR": "0/", "DARWIN_USER_TEMP_DIR": "T/"}.get(x[-1], "C/"),
              "xoa": "", "xac-nhan": con}[buoc]                  # getconf vẫn in đường dẫn hợp lệ dù mã lỗi
        return subprocess.CompletedProcess(argv, 1 if buoc == hong else 0, ra, "")
    return goi, chay


def test_don_ba_thu_muc_duoi_tram_kiem_roi_xac_nhan_rong():
    goi, chay = gia()
    don_thu_muc_he(PK, chay)
    x = [a[len(PK.boc):] for a in goi]
    assert [a[-1] for a in x[::3]] == list(THU_MUC_HE) and len(x) == 9
    assert x[1] == ["/usr/bin/find", GOC + "0", "-mindepth", "1", "-maxdepth", "1", "-exec", "/bin/rm", "-rf", "{}",
                    "+"]
    assert x[2] == ["/usr/bin/find", GOC + "0", "-mindepth", "1", "-print", "-quit"]


@pytest.mark.parametrize("hong", ["getconf", "xoa", "xac-nhan"])
def test_lenh_loi_stdout_hop_le_hay_rong_khong_duoc_coi_la_da_don(hong):
    with pytest.raises(LoiBanChep):
        don_thu_muc_he(PK, gia(hong)[1])


@pytest.mark.parametrize("sai", [{"duong": "/tmp/x/"}, {"duong": "/private/var/folders/../../etc/"},
                                 {"duong": "/var/folders/ab/"}, {"con": GOC + "C/com.apple.x\n"}])
def test_duong_dan_la_hoac_con_muc_thi_nem(sai):
    with pytest.raises(LoiBanChep):
        don_thu_muc_he(PK, gia(**sai)[1])


def test_loi_cua_cong_lich_thanh_loi_ban_chep_va_sandbox_bo_qua():
    def treo(argv, **kw):
        raise subprocess.TimeoutExpired(["sudo"], 120)
    with pytest.raises(LoiBanChep, match="TimeoutExpired"):
        don_thu_muc_he(PK, treo)
    goi, chay = gia()
    don_thu_muc_he(tu_cach_ly("sandbox:tram-kiem"), chay)          # hồ sơ ghim cấm ghi ở đây cho mọi lệnh
    assert goi == []


def test_thu_hoi_theo_uid_mac_dinh_don_qua_cung_cong_lich():
    goi, chay = gia()
    giet = []

    def chay_cong(argv, **kw):
        return giet.append(argv) or subprocess.CompletedProcess(argv, 0) if argv[-1] == "-1" else chay(argv, **kw)
    thu_hoi_theo_uid(PK, mo_cong=lambda t, b, k: CongLich(tuple(b([])), 777, chay_cong), cho_het=lambda uid: None)
    assert giet == [PK.boc_lenh(["/bin/kill", "-KILL", "-1"])] and len(goi) == 9
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_thu_muc_he.py tests/test_thu_hoi_uid.py tests/test_cong_that.py -q`
Expected (thật): `1 error` — `ModuleNotFoundError: No module named 'tram.giao_viec.thu_muc_he'`

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index f98d70e..c7753f5 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -2,7 +2,8 @@
 
 Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tram-kiem` đã chứng minh — không tin env/argv), rồi
 `kill -KILL -1` dưới principal qua `chay_gioi_han` (hạn hữu hạn, sở hữu cây; giết mọi tiến trình cùng UID, kể cả
-`setsid`). Mã thoát không là bằng chứng: TRẠM chụp `ps` (cột số) tới khi không còn tiến trình nào có uid/ruid đó.
+`setsid`). Mã thoát không là bằng chứng: TRẠM chụp `ps` (cột số) tới khi không còn tiến trình nào có uid/ruid đó;
+rồi dọn + xác nhận rỗng `DARWIN_USER_*` của `tram-kiem` (`thu_muc_he`, phần còn giữ của r47 T11).
 KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
 Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1).
 launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>`) cắm thêm khi T11 ghép và G3 đo định dạng; trước đó I1 KHÔNG bật
@@ -18,6 +19,7 @@ from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongLuot
 from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, mo_cong_kiem, tep_ngoai, tien_trinh
+from tram.giao_viec.thu_muc_he import don_thu_muc_he
 from tram.kiem.cay_tien_trinh import chup_he
 from tram.kiem.danh_tinh import LoiDanhTinh
 from tram.kiem.vong_doi import LoiThuHoi
@@ -43,14 +45,17 @@ def cho_het_uid(uid: int, *, chup: Callable = chup_he, han: float = HAN_HET, ngu
         ngu(0.2)
 
 
-def thu_hoi_theo_uid(pk, *, mo_cong: Callable | None = None, cho_het: Callable[[int], None] = cho_het_uid) -> None:
-    """UID thực (3C-B) → `kill -KILL -1` dưới `tram-kiem` có hạn (P1) → ảnh chụp không còn ai. Lỗi → ném."""
+def thu_hoi_theo_uid(pk, *, mo_cong: Callable | None = None, cho_het: Callable[[int], None] = cho_het_uid,
+                     don_he: Callable = don_thu_muc_he) -> None:
+    """UID thực (3C-B) → `kill -KILL -1` dưới `tram-kiem` có hạn (P1) → ảnh chụp không còn ai → dọn `DARWIN_USER_*`.
+    Lỗi bất kỳ bước nào → ném (cổng đóng)."""
     cong = mo_cong_kiem(pk, mo_cong)
     try:
         cong(pk.boc_lenh(GIET), capture_output=True, timeout=HAN)
     except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:      # P1 H4: thông báo cố định, là OSError
         raise LoiBanChep(f"{pk.ten}: kill -1 không xác nhận được ({type(e).__name__})") from None
     cho_het(cong.uid)
+    don_he(pk, cong)
 
 
 def ho_so_cai(p: Path = HO_SO_KIEM, *, chu: int = 0) -> None:
```

`tram/giao_viec/thu_muc_he.py` (mới):

```python
"""Thư mục riêng `DARWIN_USER_DIR/TEMP_DIR/CACHE_DIR` của `tram-kiem` (`/var/folders/…`, 0700 — trạm không đọc được):
phần còn giữ của r47 T11 (C01 hàng 6, sửa dot6-Q01). Hồ sơ Seatbelt của lượt cấm ghi ở đây; bước này dọn thứ do lệnh
NGOÀI hồ sơ (trạm chạy `kill`, `crontab -l`, `getconf` dưới `tram-kiem`) để lại, rồi xác nhận rỗng. Mỗi bước chạy dưới
`tram-kiem` qua `chay` (`CongLich` — UID đã chứng minh, có hạn): `getconf` → `find … -exec rm` → `find … -print -quit`.
MÃ LỖI của bất kỳ bước nào (kể cả khi stdout trông hợp lệ hay rỗng), đường dẫn không đúng dạng
`/var/folders/<a>/<b>/{0,T,C}`, còn mục → `LoiBanChep`: cổng giữ đóng. Xoá TRƯỚC khi quan sát nội dung là đánh đổi có
ghi (G3.6 đo thứ hệ thống tự tạo ở đây; sau đó mới quyết "còn mục lạ → đóng cổng"). Cơ chế `sandbox`: sudoers ghim hồ sơ
cấm ghi ở đây cho MỌI lệnh dưới `tram-kiem` (kể cả `rm` của trạm) → bỏ qua, không có gì của lượt ghi được vào."""
import re
import subprocess
from collections.abc import Callable

from tram.giao_viec.ban_chep import LoiBanChep
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi

FIND, GETCONF = "/usr/bin/find", "/usr/bin/getconf"
THU_MUC_HE = ("DARWIN_USER_DIR", "DARWIN_USER_TEMP_DIR", "DARWIN_USER_CACHE_DIR")
HAN = 120
DUONG = re.compile(r"/(private/)?var/folders/[\w+-]+/[\w+-]+/[0TC]")


def _ra(chay: Callable, argv: list[str]):
    try:
        return chay(argv, capture_output=True, text=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
        raise LoiBanChep(f"lệnh dọn DARWIN_USER_* không xác nhận được ({type(e).__name__})") from None


def don_thu_muc_he(pk, chay: Callable) -> None:
    if pk.co_che == "sandbox":
        return
    for bien in THU_MUC_HE:
        g = _ra(chay, pk.boc_lenh([GETCONF, bien]))
        p = (g.stdout or "").strip().rstrip("/")
        if g.returncode or not DUONG.fullmatch(p):
            raise LoiBanChep(f"không xác nhận được {bien} của {pk.ten} (getconf mã {g.returncode})")
        x = _ra(chay, pk.boc_lenh([FIND, p, "-mindepth", "1", "-maxdepth", "1", "-exec", "/bin/rm", "-rf", "{}", "+"]))
        if x.returncode:
            raise LoiBanChep(f"không dọn được {bien} của {pk.ten} (find/rm mã {x.returncode})")
        kq = _ra(chay, pk.boc_lenh([FIND, p, "-mindepth", "1", "-print", "-quit"]))
        if kq.returncode or (kq.stdout or "").strip():
            raise LoiBanChep(f"{bien} của {pk.ten} chưa rỗng sau khi dọn (find mã {kq.returncode})")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `30 passed`. Toàn bộ → **2676 passed** (N₀ + 26).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/thu_muc_he.py tram/giao_viec/cong_that.py tests/test_thu_muc_he.py tests/test_thu_hoi_uid.py
git commit -m "fix(giao-viec): dọn DARWIN_USER_* của tram-kiem sau thu hồi, mã lỗi getconf/xoá/xác nhận đều chặn (lát 3c, r47 T11 dot6-Q01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-D6a — cài hồ sơ Seatbelt cho CẢ hai cơ chế (S)

Thay gạch đầu dòng 1 của "Task 3C-D6" cũ (r47 T6 nay đã ở source: `tram/chu/cai_dat_kiem.py`).

**Files:**
- Modify: `tram/chu/cai_dat_kiem.py` (bỏ điều kiện `co_che == "sandbox"`; cảnh báo không còn nhắc `chup-nen-lich`)
- Test: sửa `tests/test_cai_dat_tho_kiem.py` (test mới cho cơ chế `user`; sổ có 10 mục), `tests/test_go_cai_lai.py` (lọc bước "Gỡ nha" thay vì lấy hai bước cuối)

**Interfaces:** Consumes `ho_so_tram_kiem`, `HO_SO_KIEM`, `THU_MUC_CAI`, `tep_root`, `TaiNguyen` (r47 T1/T6). Produces: kế hoạch `cai-dat-tho --co-che user` có `install -d … /usr/local/tram` và `install -m 0644 -o root -g wheel … tram-kiem.sb` (có sổ R2, `go-cai-dat-tho` gỡ theo sổ như cơ chế sandbox).

**Acceptance:** cơ chế `user`: tệp soạn `tram-kiem.sb` có `(deny default)`, cấm kho trạm, dùng `(param "LUOT")`; bước cài thư mục + tệp root:wheel 0644; sudoers `user` vẫn `ALL` dưới `tram-kiem` (không ghim hồ sơ — `boc_luot` thêm hồ sơ); `ho_so_cai` của 3C-D4 không còn đóng cổng vì thiếu hồ sơ ở cơ chế `user`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cai_dat_tho_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_cai_dat_tho_kiem.py b/tests/test_cai_dat_tho_kiem.py
index 1ff7019..e00d403 100644
--- a/tests/test_cai_dat_tho_kiem.py
+++ b/tests/test_cai_dat_tho_kiem.py
@@ -29,10 +29,21 @@ def test_sudoers_chi_runas_tram_kiem_va_tram_kiem_tu_tao_thu_muc(tram_home_tam,
     assert sud.splitlines()[-1] == "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" and "root" not in sud
     buoc = [m for m, _ in kh.buoc]
     assert f"[tạo] thu_muc {tmp_path}/kiem: sudo -u tram-kiem /bin/mkdir -m 0755 {tmp_path}/kiem" in buoc
-    assert soan / HO_SO_KIEM.name not in kh.tep and not any(str(THU_MUC_CAI) in m for m in buoc)
     assert "D22" in in_ke_hoach(kh) and "go-cai-dat-tho" in in_ke_hoach(kh) and buoc[0].startswith("Đối soát")
 
 
+def test_co_che_user_cung_cai_ho_so_kiem_root_0644(tram_home_tam, tmp_path):
+    """3C-D6: mọi lệnh của lượt chạy trong `HO_SO_KIEM` ở CẢ HAI cơ chế (`boc_luot`) — thiếu hồ sơ thì `ho_so_cai` đóng
+    cổng, nên cơ chế `user` cũng phải cài. Sudoers của `user` không ghim hồ sơ (`ALL` dưới tram-kiem, D40)."""
+    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
+    hs = kh.tep[soan / HO_SO_KIEM.name].decode()
+    assert "(deny default)" in hs and f'(subpath "{tram_home_tam}")' in hs and '(param "LUOT")' in hs
+    buoc = " | ".join(m for m, _ in kh.buoc)
+    assert f"install -d -o root -g wheel -m 0755 {THU_MUC_CAI}" in buoc
+    assert f"install -m 0644 -o root -g wheel {soan / HO_SO_KIEM.name} {HO_SO_KIEM}" in buoc
+    assert "chup-nen-lich" not in in_ke_hoach(kh)                     # lệnh r47 không còn trong 3c hiện hành
+
+
 def test_sandbox_cai_ho_so_co_dinh_va_ghim_sudoers(tram_home_tam, tmp_path):
     kh, soan = ke_hoach(tmp_path, chuoi="sandbox:tram-kiem", co_che="sandbox"), tram_home_tam / "cai-dat-tho"
     hs = kh.tep[soan / HO_SO_KIEM.name].decode()
@@ -57,7 +68,7 @@ def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp
     he = HeGia()
     thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
     muc = SoCai().muc().values()
-    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 8     # 3 user, 2 nhà, thư mục kiểm, sudoers, daemon
+    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 10    # 3 user, 2 nhà, 2 thư mục, hồ sơ, sudoers, daemon
     assert sorted(m.ten for m in muc if m.kieu == "nha") == ["/Users/tram-k-1", "/Users/tram-tho"]
     assert "-home /var/empty" in next(x for x in he.lenh if "-addUser tram-kiem" in x)    # C01: không nhà ghi được
     assert not any("createhomedir -c -u tram-kiem" in x for x in he.lenh)
```

`tests/test_go_cai_lai.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_go_cai_lai.py b/tests/test_go_cai_lai.py
index 2f83951..752524a 100644
--- a/tests/test_go_cai_lai.py
+++ b/tests/test_go_cai_lai.py
@@ -71,8 +71,9 @@ def test_go_xoa_nha_ghi_da_go_va_chay_lai_rong(tram_home_tam, tmp_path):
     he = HeGia()
     cai(tmp_path, he, co_che="user")
     kh = ke_hoach_go(he, xoa_nha=True)
-    assert [m.split(":")[0] for m, _ in kh.buoc][-2:] == ["Gỡ nha /Users/tram-k-1 nếu còn đúng định danh trong sổ",
-                                                          "Gỡ nha /Users/tram-tho nếu còn đúng định danh trong sổ"]
+    assert [m.split(":")[0] for m, _ in kh.buoc if m.startswith("Gỡ nha")] == [   # 3C-D6: hồ sơ cài cả cơ chế user
+        "Gỡ nha /Users/tram-k-1 nếu còn đúng định danh trong sổ",
+        "Gỡ nha /Users/tram-tho nếu còn đúng định danh trong sổ"]
     thuc_hien(kh, chay=he.chay)
     assert {m.su for m in SoCai().muc().values()} == {"da_go"} and ke_hoach_go(he, xoa_nha=True).buoc == []
 
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_cai_dat_tho_kiem.py tests/test_go_cai_dat_tho.py tests/test_go_cai_lai.py -q`
Expected (thật): `2 failed, 25 passed` — `KeyError: …/cai-dat-tho/tram-kiem.sb` (cơ chế user chưa soạn hồ sơ) và `8 == 10` (sổ thiếu thư mục cài + hồ sơ)

- [ ] **Step 3: Viết mã**

`tram/chu/cai_dat_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/chu/cai_dat_kiem.py b/tram/chu/cai_dat_kiem.py
index 9a4bee9..7717ba9 100644
--- a/tram/chu/cai_dat_kiem.py
+++ b/tram/chu/cai_dat_kiem.py
@@ -1,6 +1,7 @@
 """Phần `tram-kiem` trong `tram chu cai-dat-tho` theo D22 (lát 3c, bead bs-urj.13) — KHÔNG helper root, không ACL.
 Thêm: thư mục gốc bản chép `thu_muc_kiem` do CHÍNH `tram-kiem` tạo (nó sở hữu, trạm chỉ đi qua được), dòng sudoers
-runas CHỈ `tram-kiem` (`dong_sudoers_kiem`), và — cơ chế `sandbox` — hồ sơ cố định root:wheel 0644 `HO_SO_KIEM`.
+runas CHỈ `tram-kiem` (`dong_sudoers_kiem`), và hồ sơ Seatbelt cố định root:wheel 0644 `HO_SO_KIEM` cho CẢ HAI cơ
+chế (3C-D6: mọi lệnh của lượt chạy trong hồ sơ — `boc_luot`; cơ chế `sandbox` ghim thêm hồ sơ ở sudoers).
 Không tự chọn cơ chế: `cach_ly.tram_kiem` phải cùng cơ chế với `--co-che` (D3: thử `user` trước, giữ hai nhánh).
 `tram-kiem` luôn là user RIÊNG: `don_sach` giết MỌI tiến trình của nó — dùng chung user với khe là giết agent khe."""
 import hashlib
@@ -50,19 +51,17 @@ def phan_kiem(*, kiem: PrincipalKiem | None, thu_muc_kiem: Path | None, co_che:
     uid_kiem = lambda i: {"chu": kiem.ten, "uid": (quan_sat("user", kiem.ten) or {}).get("uid")}  # noqa: E731
     pk = PhanKiem(tai_nguyen=[TaiNguyen("thu_muc", goc, lambda i: [["sudo", "-u", kiem.ten, "/bin/mkdir", "-m", "0755",
                                                                      goc]], uid_kiem)])
-    if co_che == "sandbox":
-        hs = ho_so_tram_kiem(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
-                             cong=cong_cam(db_nghiep_vu)).encode()
-        pk.tep[soan / HO_SO_KIEM.name] = hs
-        pk.tai_nguyen += [TaiNguyen("thu_muc", str(THU_MUC_CAI), lambda i: [
-            ["sudo", "install", "-d", "-o", "root", "-g", "wheel", "-m", "0755", str(THU_MUC_CAI)]],
-            lambda i: {"uid": 0}),
-                          tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644")]
+    hs = ho_so_tram_kiem(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
+                         cong=cong_cam(db_nghiep_vu)).encode()
+    pk.tep[soan / HO_SO_KIEM.name] = hs
+    pk.tai_nguyen += [TaiNguyen("thu_muc", str(THU_MUC_CAI), lambda i: [
+        ["sudo", "install", "-d", "-o", "root", "-g", "wheel", "-m", "0755", str(THU_MUC_CAI)]], lambda i: {"uid": 0}),
+                      tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644")]
     pk.canh_bao = [
         f"D22: KHÔNG có dòng sudoers nào chạy root — {tram} chỉ được chạy lệnh DƯỚI {kiem.ten}. {kiem.ten} tự tạo, tự "
         f"giải nén, tự dọn bản chép dưới {goc}; cây kiểm là repo git MỘT commit do {kiem.ten} tự dựng (D40).",
-        f"C01: nhà của {kiem.ten} là {NHA_KIEM} (không ghi được, không createhomedir). Sau khi cài, TRƯỚC lần kiểm lại "
-        "đầu tiên: `tram giao chup-nen-lich` ghi nền launchd của tram-kiem; thiếu nền thì kiểm lại dừng (fail-closed).",
+        f"C01: nhà của {kiem.ten} là {NHA_KIEM} (không ghi được, không createhomedir). Mọi lệnh của lượt chạy trong "
+        f"hồ sơ {HO_SO_KIEM} (cả hai cơ chế). Quan sát launchd chưa có (chờ G3 đo định dạng) — cổng kiểm lại giữ đóng.",
         f"Principal kiểm lại đọc từ cach_ly.tram_kiem ({co_che}:{kiem.ten}), thư mục kiểm từ giao_viec.thu_muc_kiem "
         f"({goc}). Cài xong chạy `tram giao kiem`: mục thư mục kiểm, sudoers, ghi bản chép phải XANH trước khi bật "
         "giao_viec.bat."]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `27 passed`. Toàn bộ → **2677 passed** (N₀ + 27).

- [ ] **Step 5: Commit**

```bash
git add tram/chu/cai_dat_kiem.py tests/test_cai_dat_tho_kiem.py tests/test_go_cai_lai.py
git commit -m "feat(chu): cai-dat-tho cài hồ sơ Seatbelt tram-kiem cho cả cơ chế user (lát 3c 3C-D6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-D6b — `tram giao kiem` dưới khoá, chỉ khi cổng chưa đóng, UID thực, probe qua lượt tạm trong hồ sơ (H7) (M)

Thay gạch đầu dòng 2 của "Task 3C-D6" cũ và hợp đồng H7. `kiem_san_sang.py` đang dùng `PrincipalKiem.don_sach` (`crontab -r` + `pkill` ngầm — xoá dấu vết trước khi quan sát), luồng + `join(15)`, `id -un` so `getpass`, `subprocess.run(timeout)` dưới sudo. Tách mục principal ra `kiem_principal.py` (giữ ≤ 120 dòng), bỏ `PrincipalKiem.don_sach`.

**Files:**
- Create: `tram/giao_viec/kiem_principal.py` (`kiem_principal`, `THU_MUC_THU`)
- Modify: `tram/giao_viec/kiem_san_sang.py` (chỉ còn `kiem_du_an`, `kiem_giao_viec`; import `kiem_principal`), `tram/giao_viec/principal_kiem.py` (bỏ `don_sach`, `PGREP`)
- Test: `tests/test_kiem_principal.py`, `tests/test_kiem_principal_dong.py` (mới); sửa `tests/test_giao_kiem.py` (mục principal chuyển sang tệp mới), `tests/test_principal_kiem_hop_nhat.py` (bỏ 3 ca `don_sach`), `tests/test_cau_hinh_giao_viec.py` (không còn `don_sach`)

**Interfaces:**
- Consumes: `xac_minh_uid` (3C-B T7), `chay_gioi_han`, `gop_kill`, `kill_cuc_bo`, `cong_dong` (P1/3C-B), `dung_cong`, `thu_hoi_theo_uid` (3C-D5a), `PrincipalKiem.boc_luot` (3C-D1), `giu_khoa`, `ten_ban_chep`, `kiem_thu_muc_goc`, `kiem_sudoers_khong_root`.
- Produces: `kiem_principal(pk, thu_muc, *, chay=None, chay_lenh=chay_mot_lenh, xac_minh=xac_minh_uid, thu_hoi=None, cong=None, uid_cua=uid_that) -> list[MucKiem]`; `kiem_giao_viec(cg, cac_du_an, *, goc_quyen=None, **kw)` chuyển `**kw` sang đó. Tên mục: `principal: danh tính (UID thực) + thu hồi trước probe`, `principal: giữ APP_ENV`, `principal: không đọc kho trạm`, `principal: ghi bản chép kiểm`, `principal: hồ sơ chặn ghi ngoài lượt`, `principal: dừng được lệnh quá hạn`, `principal: dọn lượt tạm + thu hồi theo UID`, `principal: lượt tạm`, `principal: probe`.

**Acceptance:** dưới `giu_khoa()` (đang kiểm lại → ĐỎ, không lệnh nào dưới `tram-kiem`); cổng `dong`/`dang-chay`/`hong` hoặc còn dấu `kiem-lai.dong` → ĐỎ, không probe; danh tính sai hoặc thu hồi TRƯỚC probe không xác nhận → mục đó ĐỎ, không probe nào khác, cổng `dong`; mọi probe kể cả tạo/xoá lượt tạm chạy qua `boc_luot` của lượt tạm (cùng đường `chep_ban`/`don_ban`, đúng ở cả hai cơ chế), kể cả `touch` ra gốc ngoài `LUOT` phải bị từ chối; "không đọc kho trạm" (`ls ~/.tram`) và "chặn ghi ngoài lượt" chỉ xanh khi "ghi bản chép" xanh (đối chứng dương: wrapper thật sự chạy); "dừng được" gọi thẳng `chay_lenh` trong luồng chính, xanh khi `het_gio and da_thu_hoi`; cuối cùng `tram-kiem` tự xoá rồi thu hồi theo UID; BẤT KỲ mục probe nào ĐỎ (kể cả hồ sơ không chặn, lệnh không dừng/không thu hồi được) → cổng `dong` với lý do liệt kê mục; `sudo -n -l` của trạm chạy trước khi UID được chứng minh nên qua `chay_gioi_han` chỉ với kill cục bộ (H1, không gửi gì dưới `tram-kiem`), lỗi thu hồi của nó → mục ĐỎ (không vỡ lệnh).

- [ ] **Step 1: Viết test thất bại**

`tests/test_cau_hinh_giao_viec.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_cau_hinh_giao_viec.py b/tests/test_cau_hinh_giao_viec.py
index f4b3ccb..5158735 100644
--- a/tests/test_cau_hinh_giao_viec.py
+++ b/tests/test_cau_hinh_giao_viec.py
@@ -48,6 +48,7 @@ def test_sai_bao_loi(tram_home_tam, noi_dung):
 
 
 def test_principal_kiem_khong_con_trao_thu_quyen():
-    """D22: không helper root, không ACL — `tram-kiem` sở hữu bản chép, chỉ còn `boc`, `kill_nhom`, `don_sach`."""
-    assert not hasattr(PrincipalKiem, "trao") and not hasattr(PrincipalKiem, "thu")
+    """D22: không helper root, không ACL — `tram-kiem` sở hữu bản chép, chỉ còn `boc`, `kill_nhom`, `boc_luot`. 3C-D5:
+    không còn `don_sach` (`crontab -r` + `pkill` ngầm xoá dấu vết trước khi quan sát)."""
+    assert not any(hasattr(PrincipalKiem, x) for x in ("trao", "thu", "don_sach"))
     assert PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).co_che == "user"
```

`tests/test_giao_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_giao_kiem.py b/tests/test_giao_kiem.py
index 896dabf..0fcfe19 100644
--- a/tests/test_giao_kiem.py
+++ b/tests/test_giao_kiem.py
@@ -1,45 +1,15 @@
-"""`tram giao kiem|tick|kho-kiem` (4a-2). Không chạy sudo, `bd` hay mạng thật: `chay`/`chay_lenh` giả, TRAM_REPO tạm
-(du-an/ rỗng hoặc trỏ remote bare cục bộ)."""
-import os
-import subprocess
+"""`tram giao kiem|tick|kho-kiem` (4a-2). Không chạy sudo, `bd` hay mạng thật: TRAM_REPO tạm (du-an/ rỗng hoặc trỏ
+remote bare cục bộ). Mục principal kiểm lại: `test_kiem_principal.py` (3C-D6, H7)."""
 from pathlib import Path
 
-import pytest
-
 from kho_kiem_gia import dung_kho
 from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.cli import main
-from tram.giao_viec.ban_chep import giu_khoa
 from tram.giao_viec.kho_kiem_tao import lap_ke_hoach, thuc_hien
 from tram.giao_viec.kiem_san_sang import kiem_du_an, kiem_giao_viec
-from tram.giao_viec.principal_kiem import PrincipalKiem
-from tram.kiem.chay_lenh import KetQuaLenh
 from tram.tho.kiem_may import in_ket_qua
 
-PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
-
-
-def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, pgrep=1,
-             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"):
-    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`."""
-    def chay(argv, **kw):
-        lenh = argv[len(PK.boc):] if argv[:len(PK.boc)] == list(PK.boc) else argv
-        if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
-            return subprocess.run(lenh if ghi_duoc else ["/usr/bin/false"], capture_output=True, text=True)
-        ra = {"/usr/bin/id": (0, ten), "/usr/bin/env": (0, env), "/bin/test": (0 if doc_duoc else 1, ""),
-              "/usr/bin/crontab": (1, ""), "/usr/bin/pkill": (1, ""), "/usr/bin/pgrep": (pgrep, ""),
-              "/usr/bin/sudo": (0, sudo_l)}[lenh[0]]
-        if kw.get("check") and ra[0]:
-            raise subprocess.CalledProcessError(ra[0], argv)
-        return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
-    return chay
-
-
-def dung_lenh(het_gio=True):
-    return lambda lenh, argv, **kw: KetQuaLenh(lenh, "fail", "", "sha256:0", None, het_gio)
-
-
 def muc(ds):
     return {m.muc: m.muc_do for m in ds}
 
@@ -51,44 +21,6 @@ def test_thieu_het_thi_do(tmp_path):
     assert in_ket_qua(ds)[1] == 1
 
 
-def test_principal_dat_moi_muc(tmp_path):
-    (tmp_path / "quyen").mkdir()
-    for v in ("coder", "qc"):
-        (tmp_path / "quyen" / f"{v}.json").write_text("{}")
-    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=PK)
-    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung",
-                        uid_cua=lambda ten: os.getuid())
-    assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0
-    assert not list(tmp_path.glob("tram-giao-kiem-thu*"))
-
-
-@pytest.mark.parametrize("sai, muc_do", [
-    ({"ten": "hung"}, "principal: danh tính"), ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"),
-    ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi bản chép kiểm"),
-    ({"pgrep": 0}, "principal: ghi bản chép kiểm"),
-    ({"sudo_l": "    (root) NOPASSWD: /usr/local/x\n"}, "principal: sudoers không NOPASSWD root")])
-def test_principal_sai_tung_muc_la_do(tmp_path, sai, muc_do):
-    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
-                           chay=chay_gia(**sai), chay_lenh=dung_lenh(), toi="hung"))
-    assert m[muc_do] == "do" and m["principal: dừng được lệnh quá hạn"] == "xanh"
-
-
-def test_dang_kiem_lai_thi_muc_ghi_do_khong_giet_tram_kiem(tmp_path):
-    goi = []
-    goc = chay_gia()
-    with giu_khoa():
-        m = kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
-                           chay=lambda a, **kw: goi.append(a) or goc(a, **kw), chay_lenh=dung_lenh(), toi="hung")
-    assert muc(m)["principal: ghi bản chép kiểm"] == "do" and "đang có lần kiểm lại" in str(m)
-    assert not any("/usr/bin/pkill" in a for a in goi)
-
-
-def test_khong_dung_duoc_lenh_qua_han_la_do(tmp_path):
-    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
-                           chay=chay_gia(), chay_lenh=dung_lenh(het_gio=False), toi="hung"))
-    assert m["principal: dừng được lệnh quá hạn"] == "do"
-
-
 def test_du_an_kho_kiem_va_moi_truong(tmp_path):
     k = dung_kho(tmp_path)
     (tmp_path / "env.testing").write_text("DB_DATABASE=test\n")
```

`tests/test_kiem_principal.py` (mới):

```python
"""`tram giao kiem` — mục principal kiểm lại (lát 3c; 3C-D6, hợp đồng P1 H7): dưới khoá, chỉ khi cổng chưa đóng; danh
tính bằng UID thực (sai → không probe nào chạy dưới `tram-kiem`, cổng đóng); thu hồi trước + sau; mọi probe qua
`boc_luot` của một lượt tạm (cả hai cơ chế), kể cả "hồ sơ chặn ghi ngoài lượt"; "dừng được" xanh khi `het_gio and
da_thu_hoi`, không luồng + join. Ca đóng cổng/không probe: `test_kiem_principal_dong.py`. Không sudo thật:
`chay`/`chay_lenh`/`xac_minh`/`thu_hoi` giả; mkdir/touch/rm chạy thật trong `tmp_path`."""
import os
import subprocess
import threading
from pathlib import Path

import pytest

from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.giao_viec.cong_that import dung_cong
from tram.giao_viec.kiem_san_sang import kiem_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.kiem.chay_lenh import KetQuaLenh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
SB = "/usr/bin/sandbox-exec"


def chay_gia(env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, ho_so=True, goi=None, pk=PK,
             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"):
    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`. Lệnh qua
    `boc_luot` (3C-D6, cả hai cơ chế): bỏ tiền tố + `-D LUOT/NHA` + `env HOME= TMPDIR=`; `ho_so` = hồ sơ chặn ghi ngoài
    `LUOT`/`NHA`."""
    goi = [] if goi is None else goi

    def chay(argv, **kw):
        goi.append(list(argv))
        lenh, cho = (argv[len(pk.boc):] if argv[:len(pk.boc)] == list(pk.boc) else list(argv)), None
        if "-D" in lenh and "/usr/bin/env" in lenh:
            cho = [Path(x.split("=", 1)[1]) for i, x in enumerate(lenh) if i and lenh[i - 1] == "-D"]
            lenh = lenh[lenh.index("/usr/bin/env") + 3:]
        if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
            cam = ho_so and cho is not None and not all(any(Path(x).is_relative_to(c) for c in cho)
                                                        for x in lenh[1:] if x[0] == "/")
            return subprocess.run(lenh if ghi_duoc and not cam else ["/usr/bin/false"], capture_output=True, text=True)
        ra = {"/usr/bin/env": (0, env), "/bin/ls": (0 if doc_duoc else 1, ""), "/usr/bin/sudo": (0, sudo_l)}[lenh[0]]
        return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
    return chay


def dung_lenh(het_gio=True, da_thu_hoi=True, goi=None):
    def chay_lenh(lenh, argv, **kw):
        (goi if goi is not None else []).append((threading.current_thread(), kw["boc"](["/bin/sleep"])))
        return KetQuaLenh(lenh, "fail", "", "sha256:0", None, het_gio, da_thu_hoi)
    return chay_lenh


def kiem(tmp_path, *, chay=None, chay_lenh=None, xac_minh=lambda ten, boc, kill: 777, thu_hoi=lambda: None, pk=PK,
         **kw):
    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=pk)
    return kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay or chay_gia(pk=pk), xac_minh=xac_minh,
                          chay_lenh=chay_lenh or dung_lenh(), thu_hoi=thu_hoi, uid_cua=lambda ten: os.getuid(), **kw)


def cong_tt():
    return dung_cong(PK, None, cac_du_an=list).trang_thai()["trang_thai"]


def muc(ds):
    return {m.muc: m.muc_do for m in ds}


@pytest.mark.parametrize("pk", [PK, tu_cach_ly("sandbox:tram-kiem")], ids=["user", "sandbox"])
def test_principal_dat_moi_muc_qua_luot_tam_duoi_khoa(tmp_path, pk):
    (tmp_path / "quyen").mkdir()
    for v in ("coder", "qc"):
        (tmp_path / "quyen" / f"{v}.json").write_text("{}")
    goi, lenh, thu = [], [], []
    ds = kiem(tmp_path, pk=pk, chay=chay_gia(goi=goi, pk=pk), chay_lenh=dung_lenh(goi=lenh),
              thu_hoi=lambda: thu.append(1))
    assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0 and thu == [1, 1]   # trước + sau probe
    assert sorted(p.name for p in tmp_path.iterdir()) == ["quyen", "tram-home"]          # lượt tạm đã dọn
    assert len([a for a in goi if "-D" in a]) == 8 and all("-D" in b for _, b in lenh)    # mọi probe qua boc_luot
    assert lenh[0][0] is threading.main_thread() and cong_tt() == "chua-mo"               # H7: không luồng + join


@pytest.mark.parametrize("sai, muc_do", [
    ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"), ({"doc_duoc": True}, "principal: không đọc kho trạm"),
    ({"ghi_duoc": False}, "principal: lượt tạm"), ({"ho_so": False}, "principal: hồ sơ chặn ghi ngoài lượt"),
    ({"sudo_l": "    (root) NOPASSWD: /usr/local/x\n"}, "principal: sudoers không NOPASSWD root")])
def test_principal_sai_tung_muc_la_do_va_van_don(tmp_path, sai, muc_do):
    m = muc(kiem(tmp_path, chay=chay_gia(**sai)))
    assert m[muc_do] == "do" and not list(tmp_path.glob("tram-giao-kiem-thu*"))
    assert cong_tt() == ("chua-mo" if "sudoers" in muc_do else "dong")        # probe đỏ → cổng đóng


def test_sudo_l_khong_thu_hoi_duoc_la_do_khong_vo(tmp_path):
    def chay(argv, **kw):
        if argv[0] == "/usr/bin/sudo" and argv[1:] == ["-n", "-l"]:
            raise LoiThuHoi("['sudo']: không xác nhận thu hồi cây tiến trình")
        return chay_gia()(argv, **kw)
    assert muc(kiem(tmp_path, chay=chay))["principal: sudoers không NOPASSWD root"] == "do"
```

`tests/test_kiem_principal_dong.py` (mới):

```python
"""`tram giao kiem` — mục principal (3C-D6, hợp đồng P1 H7), các ca KHÔNG chạy probe hoặc phải ĐÓNG cổng: danh tính
sai, thu hồi không xác nhận, đang kiểm lại (khoá), cổng đóng/dấu hạn tổng, lệnh quá hạn không dừng/không thu hồi được.
Dùng chung bộ giả của `test_kiem_principal.py` — không sudo thật."""
import pytest

from test_kiem_principal import PK, chay_gia, cong_tt, dung_lenh, kiem, muc
from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
from tram.giao_viec.cong_that import dung_cong
from tram.kiem.danh_tinh import LoiDanhTinh


def test_danh_tinh_sai_thi_khong_chay_probe_nao_va_dong_cong(tmp_path):
    goi, lenh, thu = [], [], []

    def sai(ten, boc, kill):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    m = muc(kiem(tmp_path, chay=chay_gia(goi=goi), chay_lenh=dung_lenh(goi=lenh), xac_minh=sai, thu_hoi=thu.append))
    assert m["principal: danh tính (UID thực) + thu hồi trước probe"] == "do" and "principal: lượt tạm" not in m
    assert goi == [["/usr/bin/sudo", "-n", "-l"]] and lenh == thu == [] and cong_tt() == "dong"


def test_thu_hoi_khong_xac_nhan_thi_do_va_dong_cong(tmp_path):
    def thu_hoi():
        raise LoiBanChep("còn 1 tiến trình uid 777 sau kill -1")
    m = muc(kiem(tmp_path, thu_hoi=thu_hoi))
    assert m["principal: danh tính (UID thực) + thu hồi trước probe"] == "do" and cong_tt() == "dong"


def test_dang_kiem_lai_thi_khong_chay_probe_duoi_tram_kiem(tmp_path):
    goi = []
    with giu_khoa():
        m = kiem(tmp_path, chay=chay_gia(goi=goi))
    assert m[-1].muc_do == "do" and "đang có lần kiểm lại" in m[-1].chi_tiet and goi == [["/usr/bin/sudo", "-n", "-l"]]


@pytest.mark.parametrize("dong", ["cong", "dau"])
def test_cong_dong_hoac_dau_han_tong_thi_khong_chay_probe(tmp_path, tram_home_tam, dong):
    goi = []
    if dong == "cong":
        dung_cong(PK, tmp_path, cac_du_an=list).dong("lượt g-1: LoiBanChep")
    else:
        tram_home_tam.mkdir(parents=True, exist_ok=True)
        (tram_home_tam / "kiem-lai.dong").touch()
    m = kiem(tmp_path, chay=chay_gia(goi=goi))
    assert m[-1].muc_do == "do" and "không chạy probe" in m[-1].chi_tiet and goi == [["/usr/bin/sudo", "-n", "-l"]]


@pytest.mark.parametrize("het_gio, da_thu_hoi", [(False, True), (True, False)])
def test_khong_dung_hoac_khong_thu_hoi_duoc_lenh_qua_han_la_do(tmp_path, het_gio, da_thu_hoi):
    m = muc(kiem(tmp_path, chay_lenh=dung_lenh(het_gio, da_thu_hoi)))
    assert m["principal: dừng được lệnh quá hạn"] == "do" and cong_tt() == "dong"
```

`tests/test_principal_kiem_hop_nhat.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_principal_kiem_hop_nhat.py b/tests/test_principal_kiem_hop_nhat.py
index 468c046..e38f779 100644
--- a/tests/test_principal_kiem_hop_nhat.py
+++ b/tests/test_principal_kiem_hop_nhat.py
@@ -1,14 +1,13 @@
 """MỘT nguồn khai báo principal kiểm lại (lát 3c, bead bs-urj.12): `cach_ly.tram_kiem` là khoá chuẩn; khoá cũ
-`giao_viec.principal_kiem` chỉ để đối chiếu. D22: không trao/thu quyền — `don_sach` giết tiến trình dưới tram-kiem, trạm
-tự đếm bằng pgrep. Không sudo — chỉ kiểm argv dựng ra, `chay` giả."""
+`giao_viec.principal_kiem` chỉ để đối chiếu. D22: không trao/thu quyền; thu hồi theo UID: `test_thu_hoi_uid.py`
+(3C-D5). Không sudo — chỉ kiểm argv dựng ra."""
 import fnmatch
-from types import SimpleNamespace
+from pathlib import Path
 
 import pytest
 
 from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
 from tram.cau_hinh.principal_kiem import doc_principal_kiem
-from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
 from tram.tho.principal import BIEN_GIU
 from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem
@@ -71,37 +70,14 @@ def test_thu_muc_kiem_symlink_bi_tu_choi(tram_home_tam, tmp_path):
         nap_cau_hinh_giao_viec()
 
 
-def chay_gia(pgrep: list[int]):
-    goi = []
-
-    def chay(argv, **kw):
-        goi.append(argv)
-        return SimpleNamespace(returncode=pgrep.pop(0) if argv[0] == "/usr/bin/pgrep" else 1)
-    return goi, chay
-
-
-def test_don_sach_giet_duoi_tram_kiem_roi_tram_tu_dem():
-    pk, (goi, chay) = tu_cach_ly("user:tram-kiem"), chay_gia([0, 1])
-    pk.don_sach(chay=chay, ngu=lambda s: None)
-    assert goi[:3] == [pk.boc_lenh(["/usr/bin/crontab", "-r"]), pk.boc_lenh(["/usr/bin/pkill", "-KILL", "-U",
-                                                                             "tram-kiem"]),
-                       ["/usr/bin/pgrep", "-U", "tram-kiem"]] and len(goi) == 6     # pgrep KHÔNG qua sudo
-
-
-@pytest.mark.parametrize("pgrep, khop", [([0] * 5, "vẫn còn"), ([2], "pgrep")])
-def test_tai_sinh_hoac_pgrep_loi_thi_nem(pgrep, khop):
-    with pytest.raises(LoiBanChep, match=khop):
-        tu_cach_ly("user:tram-kiem").don_sach(chay=chay_gia(pgrep)[1], ngu=lambda s: None)
-
-
 @pytest.mark.parametrize("co_che", ["user", "sandbox"])
 def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che, monkeypatch):
-    pk, (goi, chay) = tu_cach_ly(f"{co_che}:tram-kiem"), chay_gia([1])
-    pk.don_sach(chay=chay)
+    pk, goi = tu_cach_ly(f"{co_che}:tram-kiem"), []
     monkeypatch.setattr("tram.giao_viec.principal_kiem.chay_ngan", lambda argv, **kw: goi.append(argv) or (0, b""))
     pk.kill_nhom(123, 9)
     mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
-    goi.append(pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]))
-    qua_sudo = [a for a in goi if a[0] != "/usr/bin/pgrep"]
+    goi += [pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]), pk.boc_lenh(["/bin/kill", "-KILL", "-1"]),
+            pk.boc_luot(Path("/k/g-1"))(["sh", "kiem.sh"])]
+    qua_sudo = [a for a in goi if a[0] == "/usr/bin/sudo"]
     assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in qua_sudo) and len(qua_sudo) == 4
     assert all(mau == "ALL" or fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau) for a in qua_sudo)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_kiem_principal.py tests/test_kiem_principal_dong.py tests/test_giao_kiem.py tests/test_principal_kiem_hop_nhat.py tests/test_cau_hinh_giao_viec.py -q`
Expected (thật): `16 failed, 28 passed` — 15 × `TypeError: kiem_principal() got an unexpected keyword argument 'xac_minh'`, 1 × `PrincipalKiem` còn `don_sach`

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kiem_principal.py` (mới):

```python
"""`tram giao kiem` — các mục principal kiểm lại (lát 3c; 3C-D6, hợp đồng P1 H7). Chạy DƯỚI khoá kiểm lại và chỉ khi
cổng lượt chưa đóng (`mo`/`chua-mo`) và không còn dấu hạn tổng `kiem-lai.dong`. Danh tính: `xac_minh_uid` (UID nhân ghi
cho tiến trình dò dưới đúng `boc`; không so `id -un` với `getpass`) — sai thì KHÔNG lệnh nào khác chạy dưới
`tram-kiem`. Rồi thu hồi theo UID (3C-D5) TRƯỚC probe, rồi mọi probe — kể cả tạo/xoá lượt tạm — qua `boc_luot` của MỘT
lượt tạm (cùng đường `chep_ban`/`don_ban` của lượt thật): giữ APP_ENV, không đọc kho trạm, ghi được trong `LUOT`, ghi ra
gốc ngoài `LUOT` bị từ chối (gốc thuộc `tram-kiem`: chỉ hồ sơ chặn được); mục "bị chặn" chỉ xanh khi mục ghi được xanh
(chứng minh wrapper chạy). Lệnh có hạn qua `chay_gioi_han` (H1); "dừng được" gọi thẳng, xanh khi `het_gio and
da_thu_hoi`. BẤT KỲ mục probe nào ĐỎ (danh tính, thu hồi, lượt tạm, hồ sơ không chặn, lệnh không dừng/không thu hồi
được, dọn) → `cong.dong` (fail-closed: lượt sau bị chặn tới khi Đại ca xem). `sudo -n -l` của trạm chạy trước khi UID
được chứng minh nên chỉ kill cục bộ, không gửi gì dưới `tram-kiem`."""
import os
import subprocess
from collections.abc import Callable
from functools import partial
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
from tram.giao_viec.kiem_goc import kiem_sudoers_khong_root, kiem_thu_muc_goc, uid_that
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.han_tong import cong_dong, gop_kill
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.kiem_may import MucKiem

THU_MUC_THU = "tram-giao-kiem-thu"
LOI = (OSError, subprocess.SubprocessError, ValueError, LoiDanhTinh, LoiThuHoi)   # LoiBanChep là OSError


def _muc(ten: str, dat: bool, chi_tiet: str) -> MucKiem:
    return MucKiem(ten, "xanh" if dat else "do", chi_tiet[:200])


def _ra(chay: Callable, argv: list[str], **kw):
    return chay(argv, capture_output=True, text=True, timeout=30, **kw)


def _luot_tam(pk, wt: Path, chay: Callable, chay_lenh: Callable) -> list[MucKiem]:
    nha, ngoai, b = f"{wt}.nha", wt.with_name(wt.name + ".ngoai"), pk.boc_luot(wt)
    if any(_ra(chay, b(a)).returncode for a in (["/bin/mkdir", str(wt)], ["/bin/mkdir", "-m", "700", nha,
                                                                           f"{nha}/tmp"])):
        raise ValueError("tram-kiem không tạo được lượt tạm dưới thu_muc_kiem (qua boc_luot)")
    env = _ra(chay, b(["/usr/bin/env"]), env=moi_truong_kiem({}))
    ghi = all(_ra(chay, b(a)).returncode == 0 for a in (["/bin/mkdir", str(wt / "con")],
                                                         ["/usr/bin/touch", str(wt / "con" / "x")]))
    ghi = ghi and (wt / "con" / "x").is_file()
    doc = _ra(chay, b(["/bin/ls", str(tram_home())]))
    r = _ra(chay, b(["/usr/bin/touch", str(ngoai)]))
    kq = chay_lenh("sleep 30", ["/bin/sleep", "30"], cwd=wt, env=moi_truong_kiem({}), thoi_gian_cho=1, boc=b,
                   log=tram_home() / "log" / "giao-kiem-dung.log", cho_kill=2, kill=pk.kill_nhom)
    return [_muc("principal: giữ APP_ENV", "APP_ENV=testing" in env.stdout.splitlines(), "lệnh kiểm thấy APP_ENV"),
            _muc("principal: ghi bản chép kiểm", ghi, "ghi được trong LUOT (đối chứng dương của hai mục sau)"),
            _muc("principal: không đọc kho trạm", ghi and doc.returncode != 0, f"ls {tram_home()} phải bị từ chối"),
            _muc("principal: hồ sơ chặn ghi ngoài lượt", ghi and r.returncode != 0 and not os.path.lexists(ngoai),
                 "touch ra gốc (thuộc tram-kiem) ngoài LUOT phải bị hồ sơ từ chối"),
            _muc("principal: dừng được lệnh quá hạn", kq.het_gio and kq.da_thu_hoi, "quá hạn → thu hồi cả cây")]


def _don(pk, wt: Path, chay: Callable, thu_hoi: Callable[[], None]) -> MucKiem:
    ngoai, ten = wt.with_name(wt.name + ".ngoai"), "principal: dọn lượt tạm + thu hồi theo UID"
    try:
        r = _ra(chay, pk.boc_luot(wt)(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]))
        if os.path.lexists(ngoai):                     # chỉ có khi hồ sơ KHÔNG chặn: xoá ngoài lượt, vẫn ĐỎ
            _ra(chay, pk.boc_lenh(["/bin/rm", "-f", str(ngoai)]))
        thu_hoi()
    except LOI as e:
        return _muc(ten, False, f"{type(e).__name__}: {e}")
    sach = r.returncode == 0 and not any(map(os.path.lexists, (wt, f"{wt}.nha", ngoai)))
    return _muc(ten, sach, "tram-kiem tự xoá lượt tạm; không còn tiến trình")


def _probe(pk, thu_muc: Path | None, chay, chay_lenh, xac_minh, thu_hoi) -> list[MucKiem]:
    try:
        uid = xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
        thu_hoi()                                       # tàn dư trước probe (cổng `chua-mo`) không lẫn vào probe
    except LOI as e:
        return [_muc("principal: danh tính (UID thực) + thu hồi trước probe", False, f"{type(e).__name__}: {e}")]
    ra = [_muc("principal: danh tính (UID thực) + thu hồi trước probe", True, f"{pk.ten} uid {uid}")]
    if thu_muc is None or not thu_muc.is_dir():
        return ra + [_muc("principal: lượt tạm", False, f"thu_muc_kiem không có: {thu_muc}")]
    wt = thu_muc / ten_ban_chep(THU_MUC_THU)
    try:
        ra += _luot_tam(pk, wt, chay, chay_lenh)
    except LOI as e:
        ra.append(_muc("principal: lượt tạm", False, f"{type(e).__name__}: {e}"))
    return ra + [_don(pk, wt, chay, thu_hoi)]


def kiem_principal(pk, thu_muc: Path | None, *, chay: Callable | None = None, chay_lenh: Callable = chay_mot_lenh,
                   xac_minh: Callable = xac_minh_uid, thu_hoi: Callable[[], None] | None = None, cong=None,
                   uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
    if pk is None:
        return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
    sud_chay, cong = chay or partial(chay_gioi_han, kill=kill_cuc_bo), cong or dung_cong(pk, thu_muc, cac_du_an=list)
    chay = chay or partial(chay_gioi_han, kill=gop_kill(pk.kill_nhom, kill_cuc_bo))
    try:
        sud = kiem_sudoers_khong_root(chay=sud_chay)
    except LOI as e:
        sud = _muc("principal: sudoers không NOPASSWD root", False, f"sudo -n -l: {type(e).__name__}")
    ra, ten = [kiem_thu_muc_goc(pk, thu_muc, uid_cua=uid_cua), sud], "principal: probe"
    try:
        with giu_khoa():
            tt = cong.trang_thai()["trang_thai"]
            if tt not in ("mo", "chua-mo") or cong_dong(tram_home() / "kiem-lai.dong"):
                return ra + [_muc(ten, False, f"cổng kiểm lại {tt} hoặc còn dấu kiem-lai.dong — không chạy probe "
                                              "dưới tram-kiem; Đại ca xem rồi `tram giao mo-cong-kiem`")]
            ket = _probe(pk, thu_muc, chay, chay_lenh, xac_minh, thu_hoi or partial(thu_hoi_theo_uid, pk))
            if do := [m.muc for m in ket if m.muc_do == "do"]:
                cong.dong(f"tram giao kiem: {', '.join(do)}"[:300])
            return ra + ket
    except KiemLaiDangBan:
        return ra + [_muc(ten, False, "đang có lần kiểm lại chạy — chạy lại `tram giao kiem` sau")]
```

`tram/giao_viec/kiem_san_sang.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/kiem_san_sang.py b/tram/giao_viec/kiem_san_sang.py
index 2ce8c3e..a70a032 100644
--- a/tram/giao_viec/kiem_san_sang.py
+++ b/tram/giao_viec/kiem_san_sang.py
@@ -1,91 +1,23 @@
 """`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
 của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
 không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả).
-Lát 3c (D22): mục ghi bản chép — giữ khoá kiểm lại, `tram-kiem` tạo thư mục con + file rồi TỰ dọn, trạm thấy sạch;
-thêm thư mục gốc của `tram-kiem` và sudoers không NOPASSWD root (`kiem_goc.py`)."""
-import getpass
-import os
-import shutil
-import subprocess
-import threading
-from collections.abc import Callable
+Lát 3c: các mục principal `tram-kiem` ở `kiem_principal.py` (3C-D6, hợp đồng P1 H7 — dưới khoá, chỉ khi cổng chưa
+đóng, UID thực, probe qua lượt tạm trong hồ sơ Seatbelt)."""
 from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec
-from tram.duong_dan import tram_home
-from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
 from tram.giao_viec.git_kiem import kho_kiem
-from tram.giao_viec.kiem_goc import uid_that, kiem_sudoers_khong_root, kiem_thu_muc_goc
 from tram.giao_viec.kho_kiem_tao import url_origin
-from tram.giao_viec.principal_kiem import PrincipalKiem
+from tram.giao_viec.kiem_principal import kiem_principal
 from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen
-from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
 from tram.tho.kiem_may import MucKiem
 
-LOI_CHAY = (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError)
-THU_MUC_THU = "tram-giao-kiem-thu"
-
 
 def _muc(ten: str, dat: bool, chi_tiet: str, *, khong_dat: str = "do") -> MucKiem:
     return MucKiem(ten, "xanh" if dat else khong_dat, chi_tiet)
 
 
-def _ra(chay: Callable, argv: list[str], **kw):
-    return chay(argv, capture_output=True, text=True, timeout=30, **kw)
-
-
-def _ghi_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay: Callable) -> MucKiem:
-    ten = "principal: ghi bản chép kiểm"
-    if thu_muc is None or not thu_muc.is_dir():
-        return _muc(ten, False, f"thu_muc_kiem không có: {thu_muc}")
-    d, ghi = thu_muc / ten_ban_chep(THU_MUC_THU), False
-    try:
-        with giu_khoa():
-            pk.don_sach(chay=chay)
-            try:
-                ghi = all(_ra(chay, pk.boc_lenh(a)).returncode == 0 for a in (
-                    ["/bin/mkdir", str(d)], ["/bin/mkdir", str(d / "con")], ["/usr/bin/touch", str(d / "con" / "x")]))
-                ghi = ghi and (d / "con" / "x").is_file()
-            finally:
-                _ra(chay, pk.boc_lenh(["/bin/rm", "-rf", str(d)]))
-                pk.don_sach(chay=chay)
-    except KiemLaiDangBan:
-        return _muc(ten, False, "đang có lần kiểm lại chạy — chạy lại `tram giao kiem` sau")
-    except LOI_CHAY as e:
-        return _muc(ten, False, f"{type(e).__name__}: {e}"[:200])
-    return _muc(ten, ghi and not os.path.lexists(d), "tram-kiem tạo thư mục con + file → tự dọn → trạm thấy sạch")
-
-
-def _dung_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay_lenh: Callable) -> MucKiem:
-    kq: list = []
-    t = threading.Thread(target=lambda: kq.append(chay_lenh(
-        "sleep 30", ["/bin/sleep", "30"], cwd=thu_muc or tram_home(), env=moi_truong_kiem({}),
-        log=tram_home() / "log" / "giao-kiem-dung.log", thoi_gian_cho=1, boc=pk.boc_lenh, cho_kill=2, kill=pk.kill_nhom)), daemon=True)
-    t.start()
-    t.join(15)
-    return _muc("principal: dừng được lệnh quá hạn", bool(kq) and kq[0].het_gio, "kill cả nhóm tiến trình tram-kiem")
-
-
-def kiem_principal(pk: PrincipalKiem | None, thu_muc: Path | None, *, chay: Callable = subprocess.run,
-                   chay_lenh: Callable = chay_mot_lenh, toi: str | None = None,
-                   uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
-    if pk is None:
-        return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
-    try:
-        id_ = _ra(chay, pk.boc_lenh(["/usr/bin/id", "-un"]))
-        env = _ra(chay, pk.boc_lenh(["/usr/bin/env"]), env=moi_truong_kiem({}))
-        doc = _ra(chay, pk.boc_lenh(["/bin/test", "-r", str(tram_home() / "su-kien.db")]))
-    except LOI_CHAY as e:
-        return [_muc("principal kiểm lại", False, f"không chạy được boc: {type(e).__name__}")]
-    ten = id_.stdout.strip()
-    return [_muc("principal: danh tính", id_.returncode == 0 and ten == pk.ten != (toi or getpass.getuser()), ten[:40]),
-            _muc("principal: giữ APP_ENV", "APP_ENV=testing" in env.stdout.splitlines(), "lệnh kiểm phải thấy APP_ENV"),
-            _muc("principal: không đọc kho trạm", doc.returncode != 0, str(tram_home() / "su-kien.db")),
-            kiem_thu_muc_goc(pk, thu_muc, uid_cua=uid_cua), kiem_sudoers_khong_root(chay=chay),
-            _ghi_duoc(pk, thu_muc, chay), _dung_duoc(pk, thu_muc, chay_lenh)]
-
-
 def kiem_du_an(da: DuAn) -> list[MucKiem]:
     kg, mt = kho_kiem(da.ten), da.moi_truong_kiem
     if (kg / ".git").exists():
```

`tram/giao_viec/principal_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index dec7b08..b984988 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -4,20 +4,17 @@ Lát 3c: MỘT nguồn khai báo — `cach_ly.tram_kiem: user:<tên> | sandbox:<
 đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem`). `tu_cach_ly` dựng argv từ `Principal` của 3a-2 — không
 còn argv tự do trong cấu hình: `boc` = `sudo -n -H -u <tên> --preserve-env=… --` (cơ chế sandbox thêm `sandbox-exec -f
 HO_SO_KIEM`), khớp dòng sudoers `dong_sudoers_kiem`. D22: không trao/thu quyền — `tram-kiem` sở hữu bản chép
-(`ban_chep.py`); `don_sach` giết mọi tiến trình của `tram-kiem`, rồi TRẠM tự đếm lại bằng `pgrep` (không qua sudo)."""
+(`ban_chep.py`). Thu hồi giữa các lượt: `cong_that.thu_hoi_theo_uid` (3C-D5) — không còn `crontab -r`/`pkill` ngầm."""
 import signal
-import subprocess
-import time
 from collections.abc import Callable
 from dataclasses import dataclass
 from pathlib import Path
 
-from tram.giao_viec.ban_chep import LoiBanChep
 from tram.kiem.lenh_ngan import chay_ngan
 from tram.tho.principal import SANDBOX_EXEC, doc_principal
 from tram.tho.quyen_kiem import HO_SO_KIEM
 
-PGREP, ENV = "/usr/bin/pgrep", "/usr/bin/env"
+ENV = "/usr/bin/env"
 KHONG_LUOT = ("-D", "LUOT=/var/empty", "-D", "NHA=/var/empty")
 
 
@@ -47,20 +44,6 @@ class PrincipalKiem:
         chay_ngan(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"), "--", f"-{pgid}"]),
                   timeout=5)
 
-    def don_sach(self, *, chay: Callable = subprocess.run, lan: int = 5, ngu: Callable = time.sleep) -> None:
-        """Gỡ crontab và giết MỌI tiến trình của `tram-kiem` (chạy dưới chính `tram-kiem`), rồi trạm tự đếm bằng
-        `pgrep -U` — không tin lời `tram-kiem`. Còn tiến trình sau `lan` lần, hoặc `pgrep` lỗi → `LoiBanChep`."""
-        for _ in range(lan):
-            chay(self.boc_lenh(["/usr/bin/crontab", "-r"]), capture_output=True, timeout=30)
-            chay(self.boc_lenh(["/usr/bin/pkill", "-KILL", "-U", self.ten]), capture_output=True, timeout=30)
-            r = chay([PGREP, "-U", self.ten], capture_output=True, text=True, timeout=30)
-            if r.returncode == 1:
-                return
-            if r.returncode != 0:
-                raise LoiBanChep(f"pgrep -U {self.ten} lỗi (mã {r.returncode}) — không xác nhận được đã sạch")
-            ngu(0.5)
-        raise LoiBanChep(f"{self.ten} vẫn còn tiến trình sau {lan} lần giết (nguồn tái sinh?) — dừng kiểm lại")
-
 
 def tu_cach_ly(chuoi: str) -> PrincipalKiem:
     """`cach_ly.tram_kiem` → PrincipalKiem. Sai dạng → `ChuaCoPrincipal` (ValueError)."""
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `44 passed`. Toàn bộ → **2680 passed** (N₀ + 30).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kiem_principal.py tram/giao_viec/kiem_san_sang.py tram/giao_viec/principal_kiem.py tests/test_kiem_principal.py tests/test_kiem_principal_dong.py tests/test_giao_kiem.py tests/test_principal_kiem_hop_nhat.py tests/test_cau_hinh_giao_viec.py
git commit -m "feat(giao-viec): tram giao kiem dưới khoá, chỉ khi cổng chưa đóng, UID thực, probe qua lượt tạm trong hồ sơ; bỏ don_sach (lát 3c 3C-D6, P1 H7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-D6c — khung quan sát launchd, cổng giữ đóng tới G3 (S)

Thay gạch đầu dòng 3 của "Task 3C-D6" cũ. Định dạng `launchctl print` (`user/<uid>`, `gui/<uid>`, `login/<asid>`) chưa đo trên máy B → KHÔNG viết parser (bộ đọc `nhan_launchd` của r47 T11 là đoán, không đưa lại). Khung ném khi chưa có bộ đọc → mọi `vao`/`ra`/`mo_lai` đóng cổng. Bộ đọc là task 3C-D7 sau G3 (fixture = đầu ra thật G3.3).

**Files:**
- Modify: `tram/giao_viec/quan_sat_kiem.py` (`launchd(pk, *, doc=None)`), `tram/giao_viec/cong_that.py` (`dung_cong` cắm `partial(launchd, pk)`)
- Test: `tests/test_quan_sat_launchd.py` (mới); sửa `tests/test_cong_that.py` (danh sách quan sát có `launchd`)

**Interfaces:** Produces `quan_sat_kiem.launchd(pk, *, doc: Callable | None = None) -> None` — `doc(pk)` là bộ đọc đã đo (3C-D7 truyền qua `partial(launchd, pk, doc=…)` trong `dung_cong`).

**Acceptance:** không `doc` → `LoiBanChep` nhắc G3; trong `CongLuot`, `mo_lai` → `CongDong`, trạng thái `dong` có lý do "launchd"; có `doc` → gọi đúng `doc(pk)`, lỗi của nó lan ra; `dung_cong` luôn có quan sát này (cuối danh sách).

- [ ] **Step 1: Viết test thất bại**

`tests/test_cong_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tests/test_cong_that.py b/tests/test_cong_that.py
index 73c586a..57273c8 100644
--- a/tests/test_cong_that.py
+++ b/tests/test_cong_that.py
@@ -9,7 +9,7 @@ import pytest
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_that import dung_cong, env_kin, ho_so_cai, thu_hoi_theo_uid
 from tram.giao_viec.principal_kiem import tu_cach_ly
-from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, tep_ngoai, tien_trinh
+from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, launchd, tep_ngoai, tien_trinh
 
 
 def test_ho_so_cai_dung_chu_quyen_noi_dung(tmp_path, tram_home_tam):
@@ -52,5 +52,5 @@ def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam,
     c = dung_cong(pk, tmp_path, cac_du_an=list)
     assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is thu_hoi_theo_uid
     ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
-    assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin]
+    assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin, launchd]
     assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
```

`tests/test_quan_sat_launchd.py` (mới):

```python
"""3C-D6 (C01 hàng 20–22): khung quan sát launchd của `tram-kiem`. Định dạng `launchctl print` chưa đo (G3) → không có
bộ đọc → ném, cổng giữ đóng; KHÔNG có parser đoán (`dung_cong` luôn cắm: `test_cong_that.py`). Không chạy launchctl."""
from functools import partial

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import launchd

PK = tu_cach_ly("user:tram-kiem")


def test_chua_co_bo_doc_da_do_thi_nem_cong_giu_dong(tmp_path):
    with pytest.raises(LoiBanChep, match="G3"):
        launchd(PK)
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[partial(launchd, PK)], ngu=lambda s: None)
    with pytest.raises(CongDong):
        c.mo_lai()
    assert c.trang_thai()["trang_thai"] == "dong" and "launchd" in c.trang_thai()["ly_do"]


def test_bo_doc_sau_g3_duoc_goi_voi_principal_va_loi_cua_no_lan_ra(tmp_path):
    goi = []
    launchd(PK, doc=goi.append)
    assert goi == [PK]

    def thay(pk):
        raise LoiBanChep("user/502: dịch vụ lạ")
    with pytest.raises(LoiBanChep, match="dịch vụ lạ"):
        launchd(PK, doc=thay)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_quan_sat_launchd.py tests/test_cong_that.py -q`
Expected (thật): `2 errors` — `ImportError: cannot import name 'launchd' from 'tram.giao_viec.quan_sat_kiem'`

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_that.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index c7753f5..7ae235b 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -5,9 +5,9 @@ Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tra
 `setsid`). Mã thoát không là bằng chứng: TRẠM chụp `ps` (cột số) tới khi không còn tiến trình nào có uid/ruid đó;
 rồi dọn + xác nhận rỗng `DARWIN_USER_*` của `tram-kiem` (`thu_muc_he`, phần còn giữ của r47 T11).
 KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
-Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1).
-launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>`) cắm thêm khi T11 ghép và G3 đo định dạng; trước đó I1 KHÔNG bật
-`giao_viec.bat`."""
+Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1),
+launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>` — 3C-D6: khung, chưa có bộ đọc đã đo ở G3 thì ném, cổng giữ đóng;
+I1 KHÔNG bật `giao_viec.bat`)."""
 import os
 import subprocess
 import time
@@ -18,7 +18,7 @@ from pathlib import Path
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongLuot
-from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, mo_cong_kiem, tep_ngoai, tien_trinh
+from tram.giao_viec.quan_sat_kiem import HAN, cron_at, goc_rong, launchd, mo_cong_kiem, tep_ngoai, tien_trinh
 from tram.giao_viec.thu_muc_he import don_thu_muc_he
 from tram.kiem.cay_tien_trinh import chup_he
 from tram.kiem.danh_tinh import LoiDanhTinh
@@ -86,4 +86,4 @@ def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
     goc = goc or tram_home() / "kiem"
     return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
                     quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
-                              partial(cron_at, pk), ho_so_cai, partial(env_kin, cac_du_an)])
+                              partial(cron_at, pk), ho_so_cai, partial(env_kin, cac_du_an), partial(launchd, pk)])
```

`tram/giao_viec/quan_sat_kiem.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/quan_sat_kiem.py b/tram/giao_viec/quan_sat_kiem.py
index b9548b2..46873aa 100644
--- a/tram/giao_viec/quan_sat_kiem.py
+++ b/tram/giao_viec/quan_sat_kiem.py
@@ -91,3 +91,12 @@ def cron_at(pk, *, chay: Callable | None = None) -> None:
         if r.returncode or r.stdout.strip():
             raise LoiBanChep(f"{pk.ten}: {argv[-1] if argv[0] == FIND else 'atq'} mã {r.returncode} — có việc at "
                              "hoặc không xác nhận được")
+
+
+def launchd(pk, *, doc: Callable | None = None) -> None:
+    """Khung quan sát launchd của `tram-kiem` (3C-D6; C01 hàng 20–22: `user/<uid>`, `gui/<uid>`, `login/<asid>`).
+    Định dạng `launchctl print` CHƯA đo (G3): không có bộ đọc `doc(pk)` đã đo thì ném — cổng giữ đóng, I1 không bật
+    `giao_viec.bat`. Bộ đọc là task sau G3, kèm đầu ra thật làm fixture; không viết parser đoán."""
+    if doc is None:
+        raise LoiBanChep("quan sát launchd user/gui/login của tram-kiem chưa có — G3 chưa đo định dạng launchctl print")
+    doc(pk)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `8 passed`. Toàn bộ → **2682 passed** (N₀ + 32).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/quan_sat_kiem.py tram/giao_viec/cong_that.py tests/test_quan_sat_launchd.py tests/test_cong_that.py
git commit -m "feat(giao-viec): khung quan sát launchd của tram-kiem — chưa đo định dạng thì cổng giữ đóng (lát 3c 3C-D6, C01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

#### Task 3C-S6 — harness nghiệm thu S6 `tram giao nghiem-thu-kiem` (thay r47 T12; hợp đồng H5) (M)

Thay r47 T12 (`_nghiem_thu_kiem` luồng nền + `join(timeout)`, guard `getpass`, `don_sach` gỡ lịch, `chup-nen-lich`). Harness đi đúng đường production `kiem_lai` qua cổng lượt và `boc_luot`, chạy trong TIẾN TRÌNH CON của `chay_han_tong` (3C-B T8), xác minh UID bằng `xac_minh_uid` (3C-B T7). `chup-nen-lich` không đưa lại (mốc launchd thuộc 3C-D7 sau G3, D45: chỉ hỗ trợ quan sát).

**Files:**
- Create: `tram/giao_viec/kich_ban_nghiem_thu.py` (`KHANG_DINH`, `NGUON`, `kich_ban_tai_sinh`, `git_nhap`, `commit_nhap`), `tram/giao_viec/nghiem_thu_kiem.py` (`nghiem_thu` — phần trong tiến trình con), `tram/giao_viec/lenh_nghiem_thu.py` (`lenh_nghiem_thu`, `_don`, `them`, `CHAY_CON`)
- Modify: `tram/giao_viec/kiem_lai.py` (`chu_dau`), `tram/giao_viec/lenh.py` (đăng ký lệnh; `mo-cong-kiem` từ chối khi còn dấu `kiem-lai.dong` — xét DƯỚI khoá, sau `dong-y`)
- Test: `tests/test_nghiem_thu_kiem.py`, `tests/test_lenh_nghiem_thu.py` (mới)

**Interfaces:**
- Consumes: `kiem_lai(..., cong, boc_luot, don_sach, kill)` (3C-D4, 3C-H6), `dung_cong`, `thu_hoi_theo_uid` (3C-D5a/b, 3C-D6c), `chay_han_tong(argv, *, han, kill, dau, don, khoi=khoi_chay, **kw) -> int`, `HetHanTong(LoiThuHoi)`, `gop_kill`, `kill_cuc_bo`, `xac_minh_uid`, `giu_khoa`, `in_ket_qua`.
- Produces: `kiem_lai(..., chu_dau: bool = False)` — CHỈ harness con truyền `True` (nó là chủ dấu `kiem-lai.dong` do CLI cha tạo); `nghiem_thu(pk, goc, *, cong, boc_luot, thu_hoi, khang_dinh=KHANG_DINH, xac_minh=xac_minh_uid, cho=300, thoi_gian_cho=120, tai_sinh=False, dau_goc=Path("/Users/Shared"), ngu=time.sleep, kich_ban=kich_ban_tai_sinh) -> list[MucKiem]`; `lenh_nghiem_thu(args, *, han_tong=None, xac_minh=None) -> int` (0 không đỏ; 1 đỏ/quá hạn/chưa dọn; 2 không chạy). CLI: `tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]` (`--trong --dau-ino N --cha PID` ẩn, chỉ tiến trình con dùng).

**Acceptance:**
- CLI cha: thiếu cấu hình, `--cho` không hữu hạn/≤ 0 hoặc < 240 với `--tai-sinh`, `xac_minh_uid` ném (UID là root/người vận hành, wrapper không đổi UID) → mã 2, KHÔNG spawn gì. Không luồng: con `[sys.executable, "-I", "-c", CHAY_CON, "giao", "nghiem-thu-kiem", "--trong", "--cho", …, "--dau-ino", <inode dấu>]` (`-I`: không nạp `tram/` từ thư mục hiện tại — repo agent viết) qua `chay_han_tong(han=cho+900, kill=gop_kill(pk.kill_nhom, kill_cuc_bo), dau=~/.tram/kiem-lai.dong, don=partial(_don, pk, goc), khoi=…)`; quá hạn/chưa dọn → mã 1, báo đúng dấu còn hay đã xoá; dấu còn → kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối.
- Con (`--trong --dau-ino N --cha PID`) chỉ chạy khi `os.getppid()` đúng PID cha VÀ dấu còn, đúng inode cha vừa tạo (gọi tay, dấu cũ → mã 2) — điều kiện cho `kiem_lai(chu_dau=True)`. Cổng của harness là cổng THẬT với mọi dự án thật (`cac_du_an_that` — `env_kin` đủ), vì `ra()` của harness ghi `mo` vào chính tệp cổng production. **Đánh đổi có ghi:** Ctrl-C ở cha (`chay_han_tong` của P1 không bắt `KeyboardInterrupt`) để lại con ở phiên riêng chạy tiếp — kịch bản G3/G4 dặn không Ctrl-C, nếu lỡ thì dừng con bằng đúng PID.
- `_don` dưới `giu_khoa()`: thu hồi theo UID + HAI lượt mọi quan sát của cổng thật cách `cong.cho` (kể cả launchd — chưa có bộ đọc thì ném); lỗi → `cong.dong` rồi ném (dấu giữ); True chỉ khi không ném; không ghi `mo` (D49: chỉ Đại ca mở).
- Phần con: kịch bản lịch THẬT, hoặc bộ khẳng định có exec `crontab` thật, chỉ khi `xac_minh_uid` đạt, kiểm TRƯỚC khi tạo thư mục/kho/lượt nào; mỗi khẳng định là một lệnh kiểm qua `kiem_lai` thật (cổng + `boc_luot` + `don_sach` = thu hồi); `--tai-sinh`: chỉ khi log có `kich-ban-bat-dau` (kịch bản thật sự chạy) mới xét — từng nguồn cron/at/submit/launchd "bị chặn", setsid bị thu hồi ở `ra()`, lọt thì cổng phải đóng, sau `cho` không dấu nào chạy, lần kiểm sau đạt; không có dấu bắt đầu (cổng đóng, lỗi) → một dòng ĐỎ, không dòng tái sinh nào xanh; cuối cùng dưới khoá thu hồi + gốc rỗng; dọn thư mục tạm/dấu cả khi lỗi (tạo thư mục nằm trong `try`).
- Test không exec `crontab` thật: chạy với `KHANG_DINH` bỏ `khong-chay-cong-cu-lich`, kịch bản lịch giả; kịch bản thật chỉ kiểm nội dung và bị từ chối.

- [ ] **Step 1: Viết test thất bại**

`tests/test_lenh_nghiem_thu.py` (mới):

```python
"""CLI `tram giao nghiem-thu-kiem` (lát 3c S6; hợp đồng P1 H5): xác minh UID thực TRƯỚC mọi spawn; harness là TIẾN TRÌNH
CON dưới `chay_han_tong` (hạn `cho + 900`, kill gộp, dấu `kiem-lai.dong`, `don` dưới khoá) — không luồng + join.
`han_tong`/`xac_minh` giả: không sudo, không tiến trình con thật."""
import os
import sys
from types import SimpleNamespace

import pytest

from tram.cli import tao_parser
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.noi_that import cac_du_an_that
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.han_tong import HetHanTong


@pytest.fixture
def cau_hinh(tram_home_tam, tmp_path):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path.resolve()}/kiem\n")


def args(**kw):
    return SimpleNamespace(**{"tai_sinh": False, "cho": 300.0, "trong": False, "dau_ino": None, "cha": None, **kw})


def test_cha_chay_con_duoi_han_tong_va_dau_kiem_lai(cau_hinh, tram_home_tam):
    goi = []
    ma = lnt.lenh_nghiem_thu(args(tai_sinh=True), xac_minh=lambda *a: 777,
                             han_tong=lambda argv, **kw: goi.append((argv, kw)) or 0)
    (argv, kw), = goi
    assert ma == 0 and argv[:4] == [sys.executable, "-I", "-c", lnt.CHAY_CON]      # -I: không nạp mã ở cwd
    assert argv[4:] == ["giao", "nghiem-thu-kiem", "--trong", "--cho", "300.0", "--tai-sinh"]
    assert kw["han"] == 1200.0 and kw["dau"] == tram_home_tam / "kiem-lai.dong" and kw["don"].func is lnt._don


@pytest.mark.parametrize("sai", ["uid", "cho", "nan", "cau_hinh"])
def test_sai_uid_cho_ngan_hoac_thieu_cau_hinh_thi_ma_2_khong_spawn(tram_home_tam, tmp_path, request, sai):
    if sai != "cau_hinh":
        request.getfixturevalue("cau_hinh")

    def xac_minh(*a):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    goi = []
    cho = {"cho": 10.0, "nan": float("nan")}.get(sai, 300.0)
    ma = lnt.lenh_nghiem_thu(args(tai_sinh=True, cho=cho), han_tong=goi.append,
                             xac_minh=xac_minh if sai == "uid" else lambda *a: 777)
    assert ma == 2 and goi == []


def test_qua_han_tong_thi_do_va_bao_dung_trang_thai_dau(cau_hinh, tram_home_tam, capsys):
    def han_tong(argv, **kw):
        raise HetHanTong("harness quá hạn tổng 1200 s")
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=han_tong) == 1
    assert "dấu đã xoá" in capsys.readouterr().err
    (tram_home_tam / "kiem-lai.dong").touch()                     # dọn chưa xác nhận: dấu còn
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=han_tong) == 1
    assert "kiem-lai.dong CÒN" in capsys.readouterr().err


def test_don_thu_hoi_hai_luot_quan_sat_duoi_khoa_loi_thi_dong_cong(monkeypatch, tmp_path):
    goi = []
    c = CongLuot(tmp_path / "c.json", thu_hoi=lambda: goi.append("thu"), quan_sat=[lambda: goi.append("q")],
                 ngu=lambda s: goi.append(s))
    monkeypatch.setattr("tram.giao_viec.cong_that.dung_cong", lambda pk, goc, cac_du_an: goi.append(cac_du_an) or c)
    assert lnt._don(object(), tmp_path) is True and goi == [cac_du_an_that, "thu", "q", 5.0, "q"]
    c.quan_sat = [lambda: (_ for _ in ()).throw(OSError("launchd chưa đo"))]
    with pytest.raises(OSError):
        lnt._don(object(), tmp_path)
    assert c.trang_thai()["trang_thai"] == "dong"


def test_con_chi_chay_khi_giu_dung_dau_cua_cha(cau_hinh, tram_home_tam, monkeypatch):
    goi = []
    monkeypatch.setattr("tram.giao_viec.nghiem_thu_kiem.nghiem_thu", lambda *a, **kw: goi.append(kw) or [])
    cha = os.getppid()
    assert lnt.lenh_nghiem_thu(args(trong=True, dau_ino=1, cha=cha), xac_minh=lambda *a: 777) == 2   # không có dấu
    dau = tram_home_tam / "kiem-lai.dong"
    dau.touch()
    ino = dau.stat().st_ino
    for sai in ({"dau_ino": ino + 1, "cha": cha}, {"dau_ino": ino, "cha": cha + 1}, {"dau_ino": ino}):  # cũ/gọi tay
        assert lnt.lenh_nghiem_thu(args(trong=True, **sai), xac_minh=lambda *a: 777) == 2
    assert goi == []
    assert lnt.lenh_nghiem_thu(args(trong=True, dau_ino=ino, cha=cha), xac_minh=lambda *a: 777) == 0
    assert goi[0]["thu_hoi"].func.__name__ == "thu_hoi_theo_uid" and goi[0]["cong"].tep.name == "cong.json"
    assert any(getattr(q, "args", None) == (cac_du_an_that,) for q in goi[0]["cong"].quan_sat)   # env_kin đủ dự án


def test_cha_gan_inode_dau_vao_argv_con(cau_hinh, tram_home_tam, monkeypatch):
    kq, khoi = [], []
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: khoi.append(a))
    lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777, han_tong=lambda argv, **kw: kq.append(kw) or 0)
    (dau := tram_home_tam / "kiem-lai.dong").touch()
    kq[0]["khoi"](["con"], stdin=None)
    assert khoi == [["con", "--dau-ino", str(dau.stat().st_ino), "--cha", str(os.getpid())]]


def test_mo_cong_kiem_tu_choi_khi_con_dau(monkeypatch, tmp_path, tram_home_tam):
    from tram.giao_viec import lenh
    c = CongLuot(tmp_path / "c.json", thu_hoi=lambda: None, quan_sat=[])
    c.dong("lượt g-1: LoiBanChep")
    monkeypatch.setattr(lenh, "_bo", lambda: (None, SimpleNamespace(cong=c)))
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()
    assert lenh._mo_cong(SimpleNamespace(dong_y=True)) == 2 and c.trang_thai()["trang_thai"] == "dong"


def test_parser():
    p = tao_parser().parse_args(["giao", "nghiem-thu-kiem", "--tai-sinh", "--cho", "300"])
    assert (p.ham.__name__, p.tai_sinh, p.cho, p.trong, p.dau_ino, p.cha) == ("lenh_nghiem_thu", True, 300.0, False,
                                                                                None, None)
```

`tests/test_nghiem_thu_kiem.py` (mới):

```python
"""Harness nghiệm thu S6 (lát 3c — thay r47 T12; hợp đồng P1 H5): đúng chuỗi `kiem_lai` qua cổng lượt + `boc_luot`,
mỗi khẳng định là một lệnh kiểm. Test: `boc` đồng nhất, cổng/thu hồi giả — khẳng định cách ly phải ĐỎ ở đây (không có
hồ sơ Seatbelt), chỉ xanh dưới principal thật (G4). Kịch bản cài lịch THẬT chỉ được kiểm nội dung: harness từ chối nó
khi UID thực là người vận hành, TRƯỚC khi spawn bất cứ gì. KHÔNG crontab/at/launchctl/kill -1 thật."""
import getpass

import pytest

from tram.giao_viec import nghiem_thu_kiem as ntk
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, kich_ban_tai_sinh
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem(getpass.getuser(), ())                          # boc đồng nhất: argv chạy thẳng dưới user test
KD = {k: v for k, v in KHANG_DINH.items() if k != "khong-chay-cong-cu-lich"}   # test không exec crontab thật


def chay(tmp_path, **kw):
    (goc := tmp_path / "kiem").mkdir(exist_ok=True)
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[], ngu=lambda s: None)
    c.mo_lai()
    thu = []
    luot = lambda wt: lambda a: ["/usr/bin/env", f"HOME={wt}.nha", f"TMPDIR={wt}.nha/tmp/", *a]   # boc_luot bỏ hồ sơ
    ds = ntk.nghiem_thu(PK, goc, cong=c, boc_luot=luot, thu_hoi=lambda: thu.append(1), khang_dinh=KD,
                        dau_goc=tmp_path, **kw)
    return {x.muc: x.muc_do for x in ds}, ds, thu, goc


def test_harness_la_chu_dau_chay_du_chuoi_va_bao_do_khi_khong_co_ho_so(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()                     # dấu của chính lần nghiệm thu này (CLI cha tạo)
    m, ds, thu, goc = chay(tmp_path)
    assert {k: v for k, v in m.items() if v == "xanh"} == {f"chuỗi kiểm lại: kiem/{k}.sh": "xanh" for k in (
        "danh-tinh", "repo-mot-commit", "moi-truong-khong-thanh-git", "nha-moi")}
    assert m["chuỗi kiểm lại: kiem/khong-doc-kho-tram.sh"] == m["chuỗi kiểm lại: kiem/khong-ghi-ngoai-luot.sh"] == "do"
    assert m["dọn: gốc bản chép rỗng sau thu hồi theo UID"] == "do"   # tệp ghi lọt ra gốc còn đó
    assert thu == [1, 1, 1] and in_ket_qua(ds)[1] == 1 and not list(tmp_path.glob("tram-nghiem-thu-dau-*"))


def test_kich_ban_that_bi_tu_choi_duoi_nguoi_van_hanh_truoc_khi_spawn(tmp_path, monkeypatch):
    kb = kich_ban_tai_sinh(tmp_path / "dau")
    assert all(x in kb for x in ("| crontab -", "| at now", "launchctl submit", "launchctl bootstrap", "setsid"))
    monkeypatch.setattr(ntk, "kiem_lai", lambda *a, **kw: pytest.fail("không được chạy lượt nào"))
    with pytest.raises(ValueError, match="UID thực"):
        chay(tmp_path, tai_sinh=True)
    with pytest.raises(ValueError, match="UID thực"):                # khẳng định exec crontab thật cũng vậy
        ntk.nghiem_thu(PK, tmp_path / "kiem", cong=None, boc_luot=None, thu_hoi=None, dau_goc=tmp_path)
    with pytest.raises(ValueError, match="≥ 240"):
        chay(tmp_path, tai_sinh=True, cho=float("nan"), kich_ban=lambda dau: "exit 0\n")
    assert not list(tmp_path.glob("tram-nghiem-thu-*")) and not list((tmp_path / "kiem").iterdir())


def test_tai_sinh_lot_thi_do_tung_nguon_va_dau_chay_sau_thu_hoi(tmp_path):
    ngu = []

    def lich_chay_trong_luc_cho(s):                                # một lịch "lọt" chạy trong lúc chờ → phải ĐỎ
        ngu.append(s)
        next(tmp_path.glob("tram-nghiem-thu-dau-*")).joinpath("cron").touch()
    m, *_ = chay(tmp_path, tai_sinh=True, ngu=lich_chay_trong_luc_cho,
                 kich_ban=lambda dau: "echo kich-ban-bat-dau\necho cron-da-cai\necho setsid-da-cai\nexit 0\n")
    assert ngu == [300] and m["tái sinh: hồ sơ chặn cài cron"] == "do"
    assert m["tái sinh: hồ sơ chặn cài at"] == m["tái sinh: hồ sơ chặn cài launchd"] == "xanh"
    assert m["tái sinh: quan sát đóng cổng khi lịch lọt"] == "do"     # cổng giả không đóng
    assert m["tái sinh: tiến trình setsid bị thu hồi ở ra()"] == "xanh"  # ra() của cổng giả không ném
    assert m["tái sinh: không gì chạy sau thu hồi"] == "do" and m["tái sinh: lần kiểm sau đạt"] == "do"


def test_tai_sinh_khong_thay_dau_bat_dau_thi_khong_xanh_gi(tmp_path):
    m, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: "exit 0\n")   # cổng đóng/không chạy
    assert m["tái sinh: lượt cài lịch đã chạy"] == "do"
    assert not any(k.startswith("tái sinh:") and v != "do" for k, v in m.items())
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest tests/test_nghiem_thu_kiem.py tests/test_lenh_nghiem_thu.py -q`
Expected (thật): `2 errors` — `ImportError: cannot import name 'nghiem_thu_kiem' / 'lenh_nghiem_thu' from 'tram.giao_viec'`

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kich_ban_nghiem_thu.py` (mới):

```python
"""Kịch bản của harness nghiệm thu S6 (lát 3c — thay r47 T12; C01): khẳng định chạy DƯỚI `tram-kiem` trong bản chép
(mỗi khẳng định một lệnh kiểm, qua `boc_luot` — hồ sơ Seatbelt của lượt) và kịch bản cài lịch như mã agent sẽ làm.
`kich_ban_tai_sinh` thử cài crontab/at/launchd THẬT — chỉ chạy dưới principal `tram-kiem` đã xác minh UID thực (harness
từ chối khi UID là người vận hành); dưới hồ sơ đúng thì mọi lần cài bị chặn. Test chỉ đọc nội dung. Kho git NHÁP
của harness dựng bằng `git_nhap`/`commit_nhap` (không hook, không cấu hình global/system)."""
import subprocess
from pathlib import Path

GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=nghiem-thu", "-c", "user.email=nt@localhost",
       "-c", "commit.gpgSign=false")

KHANG_DINH = {
    "danh-tinh": 'test "$(id -un)" = "{ten}"',
    "repo-mot-commit": 'test "$(git rev-list --all --count)" = 1 && test -z "$(git remote)" && test ! -e .git/hooks '
                       '&& test ! -e .git/objects/info/alternates && test -z "$(git status --porcelain -uno)"',
    "moi-truong-khong-thanh-git": 'grep -q NGHIEM_THU=1 .env.testing && ! git ls-files --error-unmatch .env.testing',
    "nha-moi": 'case "$HOME" in *.nha) ;; *) exit 1;; esac; test -w "$HOME" && test -d "$TMPDIR" && '
               'test "$APP_ENV" = testing',
    "khong-doc-kho-tram": '! ls {kho_tram} >/dev/null 2>&1',                     # kho_tram đã shlex.quote
    "khong-ghi-ngoai-luot": 'f="$(dirname "$PWD")/ngoai-$$"; ! touch "$f" 2>/dev/null',
    "khong-chay-cong-cu-lich": '/usr/bin/crontab -l >/dev/null 2>&1; test $? -eq 126',
}
NGUON = ("cron", "at", "submit", "launchd", "setsid")


def kich_ban_tai_sinh(dau: Path) -> str:
    """Thử cài mọi nguồn lịch mà mã agent dưới `tram-kiem` có thể cài; cài được thì in `<nguồn>-da-cai`, chạy được thì
    tạo `dau/<nguồn>`. Mọi nguồn hẹn 121–180 s sau khi cài (cron/at theo ranh giới phút; submit/launchd/setsid 150 s) —
    sau thu hồi của `ra()` — để dấu chỉ xuất hiện khi lọt THẬT. Dòng đầu in `kich-ban-bat-dau` (bằng chứng kịch bản đã
    chạy). Mỗi lần cài chạy nền, chờ 20 s cho lệnh cài chậm in kết quả; còn treo thì bị thu hồi cùng lệnh kiểm."""
    plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>vn.tram.nghiem-'
             f'thu.launchd</string><key>ProgramArguments</key><array><string>/usr/bin/touch</string><string>{dau}/'
             'launchd</string></array><key>StartInterval</key><integer>150</integer></dict></plist>')
    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau}/cron" | crontab - && echo cron-da-cai',
           f'echo "/usr/bin/touch {dau}/at" | at now + 3 minutes && echo at-da-cai',
           f'launchctl submit -l vn.tram.nghiem-thu.submit -- /bin/sh -c "sleep 150; touch {dau}/submit" '
           '&& echo submit-da-cai',
           f"printf '%s' '{plist}' > \"$TMPDIR/nt.plist\" && "
           'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist" && echo launchd-da-cai',
           f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")' "
           "&& echo setsid-da-cai"]
    return "\n".join(["echo kich-ban-bat-dau", *(f"( {c} ) &" for c in cai), "sleep 20", "exit 0", ""])


def git_nhap(kho: Path, *a: str) -> str:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(kho), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run([*GIT, "-C", str(kho), *a], capture_output=True, text=True, env=env, check=True,
                          timeout=60).stdout.strip()


def commit_nhap(kho: Path, tep: dict[str, str], tu: str | None) -> str:
    if tu:
        git_nhap(kho, "checkout", "-q", "--detach", tu)
    for ten, nd in tep.items():
        (kho / ten).parent.mkdir(parents=True, exist_ok=True)
        (kho / ten).write_text(nd, encoding="utf-8")
    git_nhap(kho, "add", "-A")
    git_nhap(kho, "commit", "-q", "-m", "nghiem-thu")
    return git_nhap(kho, "rev-parse", "HEAD")
```

`tram/giao_viec/kiem_lai.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index cb518b1..6058b3b 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -9,8 +9,8 @@ Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (
 không worktree, không trao quyền). Một lần kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không
 sạch → ném, KHÔNG trả kết quả. 3C-D (C01, D45): `cong` mở mới được vào lượt (trước khi chép, nhận môi trường); mọi
 lệnh của lượt qua `boc_luot(wt)` (hồ sơ Seatbelt của lượt); lượt ném lỗi → đóng cổng; xong → `cong.ra()` thu hồi và
-quan sát. Hợp đồng P1 (H6): dấu hạn tổng `kiem-lai.dong` còn → từ chối trước cổng; P1 báo chưa thu hồi cây của một
-lệnh (`da_thu_hoi=False`) → ném, không công nhận kết quả, cổng đóng."""
+quan sát. Hợp đồng P1 (H6): dấu hạn tổng `kiem-lai.dong` còn → từ chối trước cổng (trừ `chu_dau`: chính harness S6
+đang giữ dấu đó); P1 báo chưa thu hồi cây của một lệnh (`da_thu_hoi=False`) → ném, không công nhận, cổng đóng."""
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
@@ -48,8 +48,9 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
              thoi_gian_cho: float = THOI_GIAN_CHO,
              don_sach: Callable[[], None] | None = None,
              kill: Callable[[int, int], None] = _kill_nhom,
-             cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None) -> KetQuaKiemLai:
-    if cong_dong(tram_home() / "kiem-lai.dong"):                    # H6: trước mọi bước, kể cả spike tài liệu
+             cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None,
+             chu_dau: bool = False) -> KetQuaKiemLai:
+    if not chu_dau and cong_dong(tram_home() / "kiem-lai.dong"):      # H6: trước mọi bước, kể cả spike tài liệu
         raise LoiBanChep("dấu hạn tổng kiem-lai.dong còn: harness chưa xác nhận dọn — Đại ca kiểm tay rồi xoá dấu")
     cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
```

`tram/giao_viec/lenh.py` (sửa — bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/giao_viec/lenh.py b/tram/giao_viec/lenh.py
index 4aa5e73..85f6b52 100644
--- a/tram/giao_viec/lenh.py
+++ b/tram/giao_viec/lenh.py
@@ -1,5 +1,6 @@
 """Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2),
-`tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng) —
+`tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng), `tram giao nghiem-thu-kiem`
+(harness S6, `lenh_nghiem_thu.py`) —
 chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
 Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
 import sys
@@ -61,12 +62,16 @@ def _mo_cong(args) -> int:
     if bo.cong is None:
         print("Chưa khai cach_ly.tram_kiem — không có cổng kiểm lại.")
         return 2
+    from tram.duong_dan import tram_home
     print(f"Trạng thái hiện tại: {bo.cong.trang_thai()}")
     if not args.dong_y and input("Gõ dong-y để thu hồi, quan sát và mở lại: ").strip() != "dong-y":
         print("Không làm gì.")
         return 1
     try:
         with giu_khoa():
+            if (tram_home() / "kiem-lai.dong").exists():          # harness S6 đang chạy hoặc chưa xác nhận dọn
+                print("Còn dấu ~/.tram/kiem-lai.dong — không mở cổng; xem log nghiệm thu, kiểm tay rồi mới xoá dấu.")
+                return 2
             bo.cong.mo_lai()
     except LoiBanChep as e:
         print(f"Vẫn đóng: {e}", file=sys.stderr)
@@ -88,3 +93,5 @@ def them_lenh_giao(sub) -> None:
     c = g.add_parser("mo-cong-kiem", help="Thu hồi + quan sát tram-kiem rồi mở lại cổng kiểm lại (chờ dong-y)")
     c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã xem lý do đóng)")
     c.set_defaults(ham=_mo_cong)
+    from tram.giao_viec.lenh_nghiem_thu import them
+    them(g)
```

`tram/giao_viec/lenh_nghiem_thu.py` (mới):

```python
"""`tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]` (lát 3c S6 — thay r47 T12; hợp đồng P1 H5). Trước mọi thứ:
`xac_minh_uid` của principal — sai UID, UID người vận hành/root, thiếu cấu hình, `--cho` không hữu hạn → mã 2, không
spawn gì. CLI cha KHÔNG chạy harness trong luồng: chạy lại chính CLI bằng `python -I` (không nạp mã từ thư mục hiện
tại) với `--trong --dau-ino <inode dấu> --cha <pid cha>` làm TIẾN TRÌNH CON qua `chay_han_tong` — hạn tổng `cho +
900`, quá hạn thu hồi cả cây (kill gộp principal + cục bộ). Con chỉ chạy khi cha của nó đúng là pid đó VÀ dấu
`~/.tram/kiem-lai.dong` còn, đúng inode cha vừa tạo (gọi `--trong` tay, dấu cũ → mã 2). Cổng và quan sát của harness
là cổng THẬT với mọi dự án thật (`env_kin` đủ). Sau đó `_don` dưới khoá kiểm lại: thu hồi theo UID + HAI lượt mọi quan
sát cách `cho` của cổng (kể cả launchd — chưa đo ở G3 thì ném); lỗi → `cong.dong` rồi ném. Chỉ khi xác nhận mới xoá
dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối. Đánh đổi: Ctrl-C ở cha để lại con (phiên riêng)
chạy tiếp — kịch bản G3/G4 dặn dừng con bằng đúng PID. Mã: 0 không đỏ, 1 đỏ/quá hạn/chưa dọn, 2 không chạy."""
import argparse
import math
import os
import sys
from functools import partial

from tram.duong_dan import tram_home

CHAY_CON = "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))"


def _pk_goc():
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    cg = nap_cau_hinh_giao_viec()
    if cg.principal_kiem is None or cg.thu_muc_kiem is None:
        raise ValueError("cần cach_ly.tram_kiem và giao_viec.thu_muc_kiem trong ~/.tram/cau-hinh.yaml")
    return cg.principal_kiem, cg.thu_muc_kiem


def _don(pk, goc) -> bool:
    from tram.giao_viec import cong_that
    from tram.giao_viec.ban_chep import giu_khoa
    from tram.giao_viec.noi_that import cac_du_an_that
    c = cong_that.dung_cong(pk, goc, cac_du_an=cac_du_an_that)
    with giu_khoa():
        try:
            c.thu_hoi()
            for i in range(2):
                if i:
                    c.ngu(c.cho)                     # tái sinh trễ phải lộ ra giữa hai lượt quan sát
                for q in c.quan_sat:
                    q()
        except Exception as e:                       # noqa: BLE001 — dọn không xác nhận: cổng đóng, dấu giữ
            c.dong(f"nghiệm thu S6: dọn không xác nhận ({type(e).__name__})")
            raise
    return True


def _trong(args, pk, goc) -> int:
    from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
    from tram.giao_viec.nghiem_thu_kiem import nghiem_thu
    from tram.giao_viec.noi_that import cac_du_an_that
    from tram.tho.kiem_may import in_ket_qua
    dau = tram_home() / "kiem-lai.dong"
    if os.getppid() != args.cha or args.dau_ino is None or not dau.exists() or dau.stat().st_ino != args.dau_ino:
        print("Không chạy: --trong chỉ dành cho tiến trình con của CLI cha đang giữ dấu kiem-lai.dong", file=sys.stderr)
        return 2
    cong = dung_cong(pk, goc, cac_du_an=cac_du_an_that)
    van_ban, ma = in_ket_qua(nghiem_thu(pk, goc, cong=cong, boc_luot=pk.boc_luot,
                                        thu_hoi=partial(thu_hoi_theo_uid, pk), tai_sinh=args.tai_sinh, cho=args.cho))
    print(van_ban)
    return ma


def lenh_nghiem_thu(args, *, han_tong=None, xac_minh=None) -> int:
    from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
    from tram.kiem.han_tong import chay_han_tong, gop_kill
    from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo
    dau = tram_home() / "kiem-lai.dong"
    try:
        pk, goc = _pk_goc()
        if not (math.isfinite(args.cho) and args.cho > 0) or (args.tai_sinh and args.cho < 240):
            raise ValueError("--cho phải hữu hạn, > 0, và ≥ 240 giây với --tai-sinh (lịch hẹn 121–180 s)")
        (xac_minh or xac_minh_uid)(pk.ten, pk.boc_lenh, pk.kill_nhom)
    except (ValueError, LoiDanhTinh, LoiThuHoi) as e:
        print(f"Không chạy nghiệm thu: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if args.trong:
        return _trong(args, pk, goc)
    argv = [sys.executable, "-I", "-c", CHAY_CON, "giao", "nghiem-thu-kiem", "--trong", "--cho", str(args.cho),
            *(["--tai-sinh"] if args.tai_sinh else [])]
    try:
        return (han_tong or chay_han_tong)(argv, han=args.cho + 900, kill=gop_kill(pk.kill_nhom, kill_cuc_bo), dau=dau,
                                           don=partial(_don, pk, goc), khoi=lambda a, **kw: khoi_chay(
                                               [*a, "--dau-ino", str(dau.stat().st_ino), "--cha", str(os.getpid())],
                                               **kw))
    except LoiThuHoi as e:                                  # HetHanTong là LoiThuHoi
        con = "dấu kiem-lai.dong CÒN — xem ~/.tram/log/nghiem-thu, `tram giao mo-cong-kiem` hiện trạng thái" \
            if dau.exists() else "đã thu hồi + dọn, dấu đã xoá"
        print(f"[ĐỎ] {e} — {con}", file=sys.stderr)
        return 1


def them(g) -> None:
    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
    h.add_argument("--tai-sinh", action="store_true", help="Thử cài lịch cron/at/launchd như mã agent rồi chờ (G4)")
    h.add_argument("--cho", type=float, default=300.0, help="Giây chờ quá giờ hẹn của lịch (mặc định 300, ≥ 240)")
    h.add_argument("--trong", action="store_true", help=argparse.SUPPRESS)
    h.add_argument("--dau-ino", type=int, default=None, help=argparse.SUPPRESS)
    h.add_argument("--cha", type=int, default=None, help=argparse.SUPPRESS)
    h.set_defaults(ham=lenh_nghiem_thu)
```

`tram/giao_viec/nghiem_thu_kiem.py` (mới):

```python
"""Harness nghiệm thu S6 cho kiểm lại dưới principal THẬT (lát 3c — thay r47 T12; Q03, C01). Phần TRONG tiến trình con
của `tram giao nghiem-thu-kiem` (CLI cha giữ hạn tổng — `lenh_nghiem_thu.py`). Gọi ĐÚNG đường production `kiem_lai`
qua `cong` (cổng lượt) và `boc_luot` (hồ sơ Seatbelt của lượt), `don_sach` = thu hồi theo UID, trên kho git NHÁP + môi
trường kiểm GIẢ trong thư mục tạm của trạm (không dự án thật, không cần `giao_viec.bat`). Harness là chủ dấu hạn tổng
`kiem-lai.dong` (`chu_dau=True`). Mỗi khẳng định là MỘT lệnh kiểm (`KHANG_DINH`). `--tai-sinh`: commit thứ hai thử cài
lịch như mã agent; chỉ khi log có dấu `kich-ban-bat-dau` (kịch bản THẬT SỰ chạy — cổng đóng thì không xanh gì) mới
khẳng định từng nguồn BỊ CHẶN, lọt thì quan sát đóng cổng, sau `cho` (≥ 240 s) không dấu nào chạy, lần kiểm sau vẫn
đạt. Kịch bản lịch thật hay khẳng định exec `crontab` chỉ chạy khi `xac_minh_uid` chứng minh UID thực không phải người
vận hành/root — kiểm TRƯỚC mọi spawn. Cuối cùng, dưới khoá, thu hồi theo UID rồi xem gốc rỗng; lỗi giữa chừng
vẫn dọn."""
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, NGUON, commit_nhap, git_nhap, kich_ban_tai_sinh
from tram.giao_viec.kiem_lai import kiem_lai
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.kiem_may import MucKiem

LOI = (OSError, subprocess.SubprocessError, ValueError, LoiDanhTinh, LoiThuHoi)


def _muc(ten: str, dat: bool | None, chi_tiet: str) -> MucKiem:
    return MucKiem(ten, {True: "xanh", False: "do", None: "vang"}[dat], chi_tiet[:200])


def _kiem_an_toan(kiem, *a) -> tuple[object | None, str | None]:
    try:
        kq = kiem(*a)
        return kq, kq.loi
    except LoiBanChep as e:                                # cổng đóng, dọn lỗi, chưa thu hồi: không công nhận
        return None, f"{type(e).__name__}: {e}"


def nghiem_thu(pk, goc: Path, *, cong, boc_luot, thu_hoi, khang_dinh: dict = KHANG_DINH, xac_minh=xac_minh_uid,
               cho: float = 300, thoi_gian_cho: float = 120, tai_sinh: bool = False,
               dau_goc: Path = Path("/Users/Shared"), ngu=time.sleep, kich_ban=kich_ban_tai_sinh) -> list[MucKiem]:
    if (tai_sinh and kich_ban is kich_ban_tai_sinh) or "khong-chay-cong-cu-lich" in khang_dinh:
        try:
            xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
        except (LoiDanhTinh, LoiThuHoi) as e:
            raise ValueError(f"lệnh lịch THẬT: chỉ dưới tram-kiem đã chứng minh UID thực ({e})") from None
    if tai_sinh and not cho >= 240:
        raise ValueError("--cho phải ≥ 240 giây (lịch của kịch bản hẹn 121–180 s sau khi cài)")
    tam = dau = None
    ra = []
    try:
        tam = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-"))
        dau = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-dau-", dir=dau_goc))
        os.chmod(dau, 0o777)                       # job lọt (chạy ngoài hồ sơ) ghi được dấu; `tep_ngoai` thấy tệp
        kho = tam / "kho"
        kho.mkdir()
        git_nhap(kho, "init", "-q", "-b", "main")
        goc_sha = commit_nhap(kho, {"README": "nháp\n"}, None)
        git_nhap(kho, "update-ref", "refs/remotes/origin/main", goc_sha)
        kd = {f"kiem/{k}.sh": v.format(ten=pk.ten, kho_tram=shlex.quote(str(tram_home()))) + "\n"
              for k, v in khang_dinh.items()}
        sha = commit_nhap(kho, kd, goc_sha)
        (tam / "env.testing").write_text("NGHIEM_THU=1\n")
        da = DuAn("nghiem-thu", kho, None, {}, moi_truong_kiem=MoiTruongKiem(tam / "env.testing", ".env.testing"))

        def kiem(commit: str, lenh: list[str], nhan: str):
            return kiem_lai(kho, da, giao_id=f"nghiem-thu-{nhan}", commit=commit, lenh_kiem=lenh, chay_lenh=True,
                            lenh_cho_phep=["sh *"], thu_muc=goc, boc=pk.boc_lenh, env_goc=os.environ, cong=cong,
                            thu_muc_log=tram_home() / "log" / "nghiem-thu", thoi_gian_cho=thoi_gian_cho,
                            don_sach=thu_hoi, kill=pk.kill_nhom, boc_luot=boc_luot, chu_dau=True)
        kq, loi = _kiem_an_toan(kiem, sha, [f"sh {k}" for k in kd], "1")
        ra += [_muc(f"chuỗi kiểm lại: {k['lenh'][3:]}", k["ket_qua"] == "pass", k["tom_tat"][-120:])
               for k in (kq.ket_qua if kq else ())] or [_muc("chuỗi kiểm lại", False, str(loi))]
        if tai_sinh:
            ra += _tai_sinh(kiem, kho, goc_sha, sha, kd, dau, kich_ban, cho, ngu)
    except LOI as e:
        ra.append(_muc("nghiệm thu dừng vì lỗi", False, f"{type(e).__name__}: {e}"))
    finally:
        try:
            with giu_khoa():                     # không đụng lần kiểm lại thật đang chạy
                thu_hoi()
                con = os.listdir(goc)
            ra.append(_muc("dọn: gốc bản chép rỗng sau thu hồi theo UID", not con, str(con)))
        except LOI as e:
            ra.append(_muc("dọn: thu hồi theo UID lần cuối", False, f"{type(e).__name__}: {e}"))
        for x in (tam, dau):
            if x is not None:
                shutil.rmtree(x, ignore_errors=True)
    return ra


def _tai_sinh(kiem, kho: Path, goc_sha: str, sha: str, kd: dict, dau: Path, kich_ban, cho: float, ngu) -> list:
    nk = tram_home() / "log" / "nghiem-thu" / "nghiem-thu-2-kiem-lai-1.log"
    nk.unlink(missing_ok=True)                      # không đọc nhầm log của lần nghiệm thu trước
    cai_lich = commit_nhap(kho, {"kiem/cai-lich.sh": kich_ban(dau)}, goc_sha)
    _, loi = _kiem_an_toan(kiem, cai_lich, ["sh kiem/cai-lich.sh"], "2")
    log = nk.read_text(errors="replace") if nk.exists() else ""
    if "kich-ban-bat-dau" not in log:                # cổng đóng/lỗi trước khi chạy: không có gì được chứng minh
        return [_muc("tái sinh: lượt cài lịch đã chạy", False, str(loi or "log không có dấu bắt đầu"))]
    cai = set(re.findall(r"([\w-]+)-da-cai", log))
    lot = cai - {"setsid"}                          # fork + setsid được phép; bằng chứng là `ra()` thu hồi sạch
    ra = [_muc(f"tái sinh: hồ sơ chặn cài {n}", n not in cai, "CÀI ĐƯỢC — hồ sơ không chặn" if n in cai else "bị chặn")
          for n in NGUON if n != "setsid"]
    ra.append(_muc("tái sinh: tiến trình setsid bị thu hồi ở ra()", loi is None if "setsid" in cai else None,
                   str(loi or ("ra() sạch" if "setsid" in cai else "không fork được"))))
    ra.append(_muc("tái sinh: quan sát đóng cổng khi lịch lọt", "CongDong" in str(loi) if lot else None,
                   str(loi or "không có lịch lọt để quan sát")))
    ngu(cho)
    chay = sorted(p.name for p in dau.iterdir())
    ra.append(_muc("tái sinh: không gì chạy sau thu hồi", not chay, f"đã chạy: {chay} / chờ {cho:g} s"))
    kq, loi = _kiem_an_toan(kiem, sha, [f"sh {k}" for k in kd], "3")
    return ra + [_muc("tái sinh: lần kiểm sau đạt", bool(kq and kq.dat), str(loi or ""))]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: lệnh Step 2 → `15 passed`. Toàn bộ → **2697 passed** (N₀ + 47).

**An toàn khi viết test:** không test nào chạy `kich_ban_tai_sinh` hay `khong-chay-cong-cu-lich` (exec `crontab` thật) dưới user đang test; `thu_hoi` luôn giả (không `kill -1` dưới user test); `han_tong`/`xac_minh` giả ở CLI.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kich_ban_nghiem_thu.py tram/giao_viec/nghiem_thu_kiem.py tram/giao_viec/lenh_nghiem_thu.py tram/giao_viec/kiem_lai.py tram/giao_viec/lenh.py tests/test_nghiem_thu_kiem.py tests/test_lenh_nghiem_thu.py
git commit -m "feat(giao-viec): tram giao nghiem-thu-kiem — harness S6 là tiến trình con dưới hạn tổng, UID thực trước mọi spawn (lát 3c, thay r47 T12, P1 H5)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

## Áp hợp đồng P1 (H1–H8)

Nguồn: mục "Hợp đồng cho 3c" của [plan P1](2026-10-16-lat-p1-vong-doi-tien-trinh.md) và bảng G của nó. Đối chiếu mã thật trên `main` `0e33fbf` (P1 + 3C-B + Q1/Q2 + 3c đợt 7 đã ghép). r47 T11 (`don_tram_kiem`, `lich_tram_kiem`, `launchd_kiem`) KHÔNG có trong source — thay bằng cổng lượt 3C-D2/D4 — nên H3/H4 áp lên chỗ tương ứng hiện hành. 3c không sửa `tram/kiem/{vong_doi,cay_tien_trinh,lenh_ngan,chay_lenh,chay_gioi_han,danh_tinh,cong_lich,han_tong}.py`.

| # | Chỗ của 3c trên `main` | Áp ở | Trạng thái sau plan này |
|---|---|---|---|
| H1 | spawn rồi chờ dưới `sudo` | 3C-D5a (`thu_hoi_theo_uid`, `cron_at` qua `CongLich` → `chay_gioi_han`), 3C-D6b (probe `tram giao kiem` qua `chay_gioi_han`), 3C-S6 (harness là tiến trình con của `chay_han_tong`) | **Còn một chỗ:** `ban_chep._chay` (`subprocess.run(timeout=600)` dưới `sudo` cho `mkdir`/`tar`/`git`/`rm` của lượt). Không áp ở đây: `chep_ban` nối ống `git archive` → `tar` (stdin là ống), `chay_gioi_han` chỉ nhận `input=` bytes và 3c không được sửa primitive → cần task P1 thêm `stdin=` (đề nghị bead). Hậu quả hiện tại fail-closed: treo thì `kiem_lai` giữ khoá, cổng ở `dang-chay` (đóng). `kiem_goc.kiem_sudoers_khong_root` (`sudo -n -l` của trạm) nhận `chay` = `chay_gioi_han` từ 3C-D6b. `tien_trinh`/`tep_ngoai` (pgrep/find của trạm, không sudo) giữ `subprocess.run` — ngoài phạm vi H1. |
| H2 | `PrincipalKiem.kill_nhom` | **3C-H2** | `chay_ngan(boc_lenh([... "/bin/kill" ...]), timeout=5)`; bỏ `run(timeout=20)` và tham số `chay` |
| H3 | `don_sach` + lịch (T11 r47) → hiện là `giet_tam` (thu hồi) và `cron_at` (quan sát) | **3C-D5a** | Thu hồi và `cron_at` mở `CongLich` bằng `mo_cong_lich(pk.ten, pk.boc_lenh, pk.kill_nhom)` trước lệnh đầu tiên; `uid = cong.uid` cho ảnh chụp; `LoiDanhTinh`/`LoiThuHoi` → `LoiBanChep` (không lệnh lịch nào chạy). Test dựng `CongLich(tien_to, uid, chay_gia)` trực tiếp |
| H4 | `ra()` của `lich_tram_kiem` (không có trên `main`) | **3C-D5a** `mo_cong_kiem` | Thông báo cố định `"{ten}: không xác minh được UID thực ({tên loại lỗi})"` — không argv/stdout. Lỗi khác trong `CongLuot._sach` đã đóng cổng với `{type}: {e}`; `chay_gioi_han` chỉ để tên chương trình trong thông báo (dot6-Q06) |
| H5 | harness `tram giao nghiem-thu-kiem` (r47 T12) | **3C-S6** | CLI cha: `xac_minh_uid` trước mọi spawn; con `--trong` qua `chay_han_tong(han=cho+900, kill=gop_kill(pk.kill_nhom, kill_cuc_bo), dau=~/.tram/kiem-lai.dong, don=_don)`; `_don` dưới `giu_khoa()`: thu hồi theo UID + một lượt mọi quan sát của cổng thật, True chỉ khi không ném. Guard `getpass` bỏ — kịch bản lịch thật chỉ khi `xac_minh_uid` đạt. **Lệch có chủ đích so với H5 nguyên văn:** H6 làm `kiem_lai` từ chối khi dấu `kiem-lai.dong` còn, mà chính tiến trình con của harness cần chạy `kiem_lai` trong lúc cha giữ dấu → `kiem_lai(..., chu_dau=True)` chỉ do harness con truyền (production không truyền), và con chỉ chạy khi cha của nó đúng PID cha truyền và dấu đúng inode cha vừa tạo |
| H6 | `kiem_lai` / `ban_chep` | **3C-H6** (+ `chu_dau` ở 3C-S6) | Dấu `kiem-lai.dong` còn → `LoiBanChep` ở đầu `kiem_lai` (trước kiểm đường dẫn cấm, `cong.vao`, chép, nhận môi trường); `KetQuaLenh.da_thu_hoi is False` → `LoiBanChep`, không công nhận, cổng `dong`. `ban_chep` chỉ được gọi từ `kiem_lai` nên không kiểm lại dấu ở đó; `tram giao kiem` (3C-D6b) cũng từ chối khi dấu còn |
| H7 | `kiem_san_sang._dung_duoc` + danh tính | **3C-D6b** | Gọi `chay_lenh` thẳng (không luồng + `join(15)`), xanh khi `het_gio and da_thu_hoi`; danh tính = `xac_minh_uid(pk.ten, pk.boc_lenh, pk.kill_nhom)` — sai thì không probe nào chạy dưới `tram-kiem` |
| H8 | `from tram.kiem.chay_lenh import _kill_nhom` | — | Giữ nguyên (P1 giữ bí danh); không sửa import |

Bảng G của P1 mà 3c dựa vào: G3 ("treo sau SIGKILL" → `da_thu_hoi=False` → người gọi giữ cổng đóng) ← 3C-H6; G6 (UID thực) và G7 (sai danh tính → 0 lệnh lịch) ← 3C-D5a, 3C-D6b, 3C-S6; G8 (hạn tổng + dấu cổng) ← 3C-S6; G9 (lỗi không lộ argv) ← H4. Rủi ro P1 mục 2 ("phía trạm chưa có hạn tới khi 3c áp H2/H6/H7") đóng ở mức offline sau 3C-H2, 3C-H6, 3C-D6b; mục 1 (`kiem_am`/`kiem_cong`/`kiem_cach_ly` còn `run(timeout)` có tty) không thuộc 3c.

## Bảng G bổ sung (đợt 7 — 3C-A/C/D)

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G-A1 | Ranh giới cưỡng chế của C01 trong D45 | Hồ sơ Seatbelt cấm mặc định cho MỌI lệnh của lượt (cả cơ chế `user` lẫn `sandbox`), `-D LUOT/NHA` | Cơ chế duy nhất không cần root ngăn trước ghi/IPC/tạo job cho cả cây tiến trình; chạy thử đạt trên macOS 15.6.1 | **HỢP ĐỒNG MỚI** — đổi G12/G20 r47 (trước: hồ sơ allow-default, chỉ cơ chế sandbox) |
| G-A2 | Mạng, IPC | Không mạng (chỉ unix socket trong `LUOT`), không IPC POSIX/SysV kể cả semaphore | DB/Redis dùng chung (cục bộ hay xa) và semaphore có tên là trạng thái sống qua lượt (review tái hiện) | **HỢP ĐỒNG MỚI** — hệ quả Q-A |
| G-A3 | Cổng lượt | Tệp `~/.tram/kiem-lai/cong.json`: `mo`/`dang-chay`/`dong`; chỉ `ra()` sạch mới mở; mở lại bằng `tram giao mo-cong-kiem` (chờ `dong-y`) | D45 "cleanup không rõ thì chặn lượt sau", bền qua khởi động lại | **HỢP ĐỒNG MỚI** (CLI) |
| G-A4 | Quan sát | `pgrep -U/-u`, `find` sâu vùng ghi-chung, gốc rỗng, cron/at, hồ sơ đã cài, tệp env 0600; hai lần cách `cho`=5 s, thêm một lần ở `vao` | Dây báo cho tái sinh trễ và lỗ `-maxdepth 1` | giả định (số giây đo ở G4); launchd chờ T11 + G3 |
| G-A7 | HOME/TMP mỗi lượt | `<wt>.nha` 0700 (+`tmp/`), qua `env HOME= TMPDIR=` trong `boc_luot`; dọn cùng bản chép | D45 | giả định (T11 `boc_nha` thành thừa khi ghép) |
| G-A5 | Thu hồi | `kill -KILL -1` dưới `tram-kiem` (`giet_tam`, có timeout); sau P1/3C-B: `thu_hoi_theo_uid`. Trong lượt KHÔNG gỡ lịch | Giết theo UID; gỡ lịch xoá dấu vết trước khi quan sát | giả định hợp đồng P1/3C-B; đổi `don_sach` của r47 T5 khi có cổng |
| G-A6 | Pool UID | Chưa làm; là phương án A1 nếu G4 bác | Đổi G13 và hợp đồng cài đặt | chờ G4 / Đại ca |
| G-C1 | Bằng chứng R7 | So mã cây hai phía, lệch → `CayKhacNguon` | Bằng nhau ⇔ cùng path/mode/blob | **HỢP ĐỒNG MỚI** (thay giới hạn G32 r47) |
| G-C2 | Lệch cây xử lý thế nào | `loi="cay-khac-nguon"` → escalation, không ghi `kiem.lai` | Lỗi tất định; tránh kẹt vòng tick (review đối kháng) | **HỢP ĐỒNG MỚI** (lý do escalation mới) |
| G-C3 | Cấu hình git của trạm/kho kiểm | Bỏ `GIT_*`, global/system/XDG, replace refs; ghim autocrlf/eol/ignorecase/protectHFS/NTFS; kho có `filter.*` → từ chối | Bytes bản chép chỉ theo `.gitattributes` của commit | giả định |
| G-C4 | Repo không khứ hồi được | Từ chối (danh sách ở Task 3C-C) | R7: fail-closed, không tuyên bố hỗ trợ | **Đại ca cần biết** (Q-C) |
| G-C5 | LFS | Bản chép mang con trỏ (không smudge) | Đúng cây commit | giả định — test cần nội dung LFS sẽ fail |

## Bảng G bổ sung (đợt 8 — 3C-D5, 3C-D6, hợp đồng P1)

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G-D1 | Xác minh thu hồi | Sau `kill -KILL -1`: ảnh chụp `ps` (cột số, P1) tới khi không còn tiến trình uid HOẶC ruid = UID đã chứng minh, hạn 5 s | Mã thoát của `kill` không là bằng chứng; ruid bắt cả tiến trình setuid (không giết được → cổng đóng) | giả định (5 s đo ở G3.5) |
| G-D2 | Cơ chế `sandbox` | Quan sát lịch (`cron_at`) ném → cổng luôn đóng tới G3; dọn `DARWIN_USER_*` bỏ qua | Sudoers ghim hồ sơ cho MỌI lệnh dưới `tram-kiem`: exec `crontab`/`atq` và ghi `/var/folders` luôn bị cấm; mã lỗi khi exec bị cấm chưa đo | **Đại ca cần biết**: theo D3 chạy `user` trước; `sandbox` chưa dùng được cho kiểm lại |
| G-D3 | `DARWIN_USER_*` | Dọn rồi xác nhận rỗng (giữ sửa Q01 của r47 T11), không coi "có nội dung" là bẩn | Hệ thống tự tạo thứ ở đây khi trạm chạy lệnh ngoài hồ sơ; chưa đo (G3.6) | **đánh đổi có ghi** — xoá trước khi quan sát; xét lại sau G3.6 |
| G-D4 | Quan sát launchd | Khung ném, không parser, cổng đóng tới 3C-D7 (sau G3.3) | Không viết parser đoán (yêu cầu đợt 8; review r47 chỉ ra định dạng chưa đo) | **HỢP ĐỒNG MỚI**: kiểm lại và G4 chờ 3C-D7 |
| G-D5 | Dấu hạn tổng và harness | `kiem_lai(chu_dau=True)` chỉ cho tiến trình con harness; con chỉ chạy khi dấu còn và đúng inode cha truyền | H5 dùng `kiem-lai.dong` làm dấu, H6 làm `kiem_lai` từ chối khi dấu còn — mâu thuẫn với chính lượt của harness | **HỢP ĐỒNG MỚI** — lệch H5/H6 nguyên văn, ghi ở "Áp hợp đồng P1" |
| G-D6 | `tram giao kiem` khi nghi ngờ | Danh tính/thu hồi/dọn lượt tạm không xác nhận → `cong.dong` (không chỉ dòng ĐỎ) | D45/D49 fail-closed; probe để lại tàn dư thì lượt sau phải bị chặn | **HỢP ĐỒNG MỚI** |
| G-D7 | Cổng `chua-mo` | `tram giao kiem` được chạy probe khi `mo` hoặc `chua-mo` (sau thu hồi trước probe) | Lần cài đầu chưa có lượt nào; `mo-cong-kiem` sau đó vẫn thu hồi + quan sát | giả định |
| G-D8 | Tiến trình con harness | `python -I` | Không nạp `tram/` từ thư mục hiện tại (có thể là repo agent viết) dưới tài khoản trạm | giả định |

## Review nghi ngờ đợt 8 (doubt-driven)

Người review ngữ cảnh mới chỉ nhận ARTIFACT (diff) + CONTRACT. Chéo mô hình (Codex/Gemini CLI) **bị bỏ qua: ngữ cảnh không tương tác** (Em chạy như subagent, không tự gọi CLI ngoài) — đề nghị đưa vào zip review Codex.

| Chu kỳ | Phát hiện chính | Phân loại → xử lý |
|---|---|---|
| 1 (2 người review, 14 + 17 mục) | (Chặn) cơ chế `sandbox`: dọn `DARWIN_USER_*` và `crontab -l` luôn bị hồ sơ ghim từ chối → thu hồi luôn ném; lỗi `LoiThuHoi`/`LoiDanhTinh` của `kill -1` không đổi thành `LoiBanChep` → `don_ban` bỏ `rm`; `--trong` bỏ qua hạn tổng và dấu; `--tai-sinh` xanh giả khi lượt 2 không chạy (cổng đóng); `tram giao kiem` tạo/xoá lượt tạm bằng `boc_lenh` (khác đường lượt thật, hỏng ở `sandbox`) và không đóng cổng khi nghi ngờ; con harness nạp `tram/` từ cwd; `sudo -n -l` qua `chay_gioi_han` làm vỡ lệnh; `--cho nan`; mục "bị chặn" xanh khi wrapper hỏng (thiếu đối chứng dương); `mo-cong-kiem` không xét dấu; `_don` một lượt quan sát; regex đường `/var/folders` | Sửa hết: G-D2; H4 chuyển lỗi; inode dấu (G-D5); dấu `kich-ban-bat-dau`; `boc_luot` cho tạo/xoá + đóng cổng (G-D6) + thu hồi trước probe; `-I` (G-D8); bắt lỗi `sudo -l`; kiểm hữu hạn; đối chứng dương; `mo-cong-kiem` từ chối khi còn dấu; hai lượt quan sát + `cong.dong`; regex chặt. **Đánh đổi có ghi:** xoá `DARWIN_USER_*` trước khi quan sát (G-D3); launchd khung làm mọi `mo_lai`/harness đỏ tới 3C-D7 (G-D4, đúng yêu cầu); chi phí mỗi lượt 3 lần thu hồi (dò UID + `kill` + 9 lệnh dọn) và cận xấu nhất có thể vượt `cho + 900` → `HetHanTong`, dấu giữ (fail-closed); tiến trình sót của lượt trước có thể giết cây dò UID → cổng kẹt chờ Đại ca. **Nhiễu:** "diff A không tự đứng được" (bỏ `don_sach`/`giet_tam` nằm ở task khác cùng đợt — thứ tự task đã xử lý) |
| 2 | (1 người review, 11 mục) `tram giao kiem` chỉ đóng cổng với mục có chữ "thu hồi/lượt tạm" (lệnh không thu hồi được, hồ sơ không chặn vẫn để cổng mở); `--trong` chỉ xét inode (đọc được bằng `ls -i`); cổng của harness dựng với `cac_du_an=list` mà `ra()` ghi `mo` vào tệp cổng production (bỏ `env_kin`); `cron_at` không đổi lỗi khi chạy thành thông báo cố định; `mo-cong-kiem` xét dấu ngoài khoá; H6 xét dấu sau các nhánh trả sớm; `sudo -n -l` chạy trước khi xác minh UID với kill dưới `tram-kiem`; tiến trình dò UID ngoài khoá; `sandbox` bỏ qua cả bước xác nhận `DARWIN_USER_*`; "quan sát đóng cổng" xanh với mọi `CongDong`; `python -I` + Ctrl-C để lại con | Sửa: mọi mục probe đỏ → `cong.dong`; con phải có `os.getppid()` = PID cha truyền + inode dấu; harness và `_don` dùng `cac_du_an_that`; `_ra_lich` đổi lỗi; kiểm dấu dưới khoá sau `dong-y`; H6 ở đầu hàm; `sudo -n -l` chỉ kill cục bộ. **Đánh đổi có ghi:** cây dò UID ngoài khoá có thể bị `kill -1` của lượt thật giết hoặc làm cổng đóng giả (fail-closed); `sandbox` đã đóng cổng ở `cron_at` nên bỏ xác nhận `DARWIN_USER_*` không mở đường nào; "quan sát đóng cổng" chỉ chặt sau 3C-D7; Ctrl-C để lại con (kịch bản G3/G4 dặn dừng theo PID); `-I` cần `tram` cài trong venv (`uv sync` đã làm). **Theo luật 3 chu kỳ, các sửa của chu kỳ 2 chưa qua người review mới — đưa vào zip Codex.** |

## Kết quả chạy thử đợt 8 (16/10/2026)

- Bản sao: `git clone` `main` `0e33fbf` vào thư mục scratch riêng, `.venv` riêng (`uv sync` offline). Mỗi task một commit trên nhánh tạm, áp theo thứ tự bảng "Sơ đồ đợt"; plan in nguyên văn từ các commit đó.
- **Kiểm fixture không tác động host:** plugin pytest (`sys.addaudithook`) từ chối spawn `sudo`, `crontab`, `at`, `atq`, `atrm`, `batch`, `launchctl`, `security`, `dscl`, `sysadminctl`, `pkill`, `killall`, `sandbox-exec`, `createhomedir`, `visudo`, `dseditgroup` từ tiến trình pytest; PATH giả có script cùng tên ghi nhật ký rồi thoát 97. Mọi lần chạy (baseline, từng task, RED, GREEN, toàn bộ cuối): **nhật ký chặn rỗng**.
- Baseline: `2650 passed in 203.91s` (= N₀).
- RED thật = áp test của task lên commit trước (mã cũ); GREEN = commit của task. Số ở Step 2/4 từng task. Tổng thu thập sau mỗi task (`pytest --collect-only`): 2652 → 2654 → 2666 → 2676 → 2677 → 2680 → 2682 → **2697**.
- Toàn bộ cuối: **`2697 passed in 193.46s`**, nhật ký chặn rỗng.
- Mọi file `.py` thêm/sửa ≤ 120 dòng (lớn nhất: `nghiem_thu_kiem.py` 117, `kiem_principal.py` 112), mọi dòng ≤ 120 ký tự Unicode (trừ một dòng 122 ký tự có sẵn ở `tests/test_noi_giao_viec.py:69`, không sửa).

## Sơ đồ đợt và số test

Thứ tự ghép (Đại ca đã duyệt): **1a-2 T5 (và T4, T6) → 3c**. 1a-2 T5 sửa `cac_du_an_that` trong `tram/giao_viec/noi_that.py`; mọi bản vá 3c lên `noi_that.py` (r47 T3/T5, 3C-D4) tính trên nền đã có bộ lọc `bat_ghi`. Bản chạy thử của 3C-D đã áp 1a-2 T5 (`tram/cau_hinh/bat_ghi.py` + hunk `noi_that.py` của plan 1a-2) trước khi áp 3C-D4.

```
1a-2 T5/T4/T6 ─┐
r47 T1,T3 → T5,T10 → T6,T7 → T8,T11 (+Q01) → T12   (giữ nguyên văn bản lịch sử, đối chiếu source trước khi giao)
                     │
                     ├─ 3C-C (sau T3+T10) ─────────────────────────┐
P1 → 3C-B ───────────┼─────────────────────────────────────────────┤
                     └─ 3C-D1 → 3C-D2 → 3C-D3 → 3C-D4 → 3C-D5, 3C-D6 ┴→ I1 → G3 → G4 (S6)
```

Không hai task cùng sửa một file trong một đợt: 3C-C và 3C-D4 cùng sửa `kiem_lai.py`, `tick_pipeline.py` → 3C-C trước, 3C-D4 sau. 3C-D1 sửa `quyen_kiem.py`/`principal_kiem.py` của r47 T1/T5 → sau T5. 3C-D4 sửa `noi_that.py`, `bo.py`, `lenh.py` → sau 1a-2 T5 và sau r47 T12 (T12 cũng sửa `lenh.py`; đối chiếu mốc khi ghép).

| Bước | Test mới | Tổng chạy thật trên bản thử |
|---|---|---|
| Nền `main 5da881e` | — | **2242** (N₀, đo lại 16/10 với PATH chặn cron/at/launchctl/sudo/security/pkill — không lời gọi nào) |
| + r47 đợt 1–2 (T1, T3, T5, T10) | +38 | 2280 |
| + 3C-C | +23 | **2303** |
| + 1a-2 T5 (chỉ mã, không kèm test 1a-2) | 0 | 2303 |
| + 3C-D1 | +5, −1 (bỏ test hồ sơ allow-default cũ của T1) | 2307 |
| + 3C-D2 | +14 | 2321 |
| + 3C-D3 | +16 | 2337 |
| + 3C-D4 | +14 (`test_cong_that.py` 8, `test_kiem_lai_cong.py` 6; `test_noi_giao_viec.py` chỉ sửa) | **2351** |
| 3C-D5, 3C-D6 | đợt 8 — xem bảng dưới (trên `main` `0e33fbf`, N₀ = 2650) | — |

Mỗi tổng trên là `uv run pytest -q` THẬT trên bản sao tuyến tính (mỗi task một commit), PATH chặn `crontab/at/batch/atq/atrm/launchctl/sudo/security/dscl/sysadminctl/pkill/killall/sandbox-exec/createhomedir/osascript` bằng shim ghi nhật ký — nhật ký rỗng sau mọi lần chạy.

Delta của 3c đợt 7: **N + 71** trên nền đã có r47 đợt 1–2 (N = 2280; 23 + 4 + 14 + 16 + 14). Không cộng với mốc 2370 lịch sử; r47 đợt 3–5 (T6–T8, T11, T12) chưa áp trong bản thử này. Khi triển khai: đo N₀ sau các merge trước, ghi RED/GREEN thật.

**Đợt 8 (16/10/2026) — 3C-D5, 3C-D6, hợp đồng P1 trên `main` `0e33fbf`:**

Task cùng đợt không sửa chung file. Cột "Tổng" là `uv run pytest -q` THẬT trên bản sao tuyến tính theo thứ tự trong bảng (N₀ = 2650).

| Đợt | Task | File chính | Test + | Tổng sau task |
|---|---|---|---|---|
| 8.1 | 3C-H2 | `principal_kiem` | +2 | 2652 |
| 8.1 | 3C-H6 | `kiem_lai` | +2 | 2654 |
| 8.1 | 3C-D5a | `cong_that`, `quan_sat_kiem`, `noi_that` | +12 | 2666 |
| 8.2 | 3C-D5b | `thu_muc_he` (mới), `cong_that` | +10 | 2676 |
| 8.1 | 3C-D6a | `tram/chu/cai_dat_kiem` | +1 | 2677 |
| 8.2 | 3C-D6b | `kiem_principal` (mới), `kiem_san_sang`, `principal_kiem` | +3 | 2680 |
| 8.3 | 3C-D6c | `quan_sat_kiem`, `cong_that` | +2 | 2682 |
| 8.3 | 3C-S6 | `nghiem_thu_kiem`, `kich_ban_nghiem_thu`, `lenh_nghiem_thu` (mới), `kiem_lai`, `lenh` | +15 | **2697** |

## Task 9 (S6) — kịch bản G3/G4 (CHƯA CHẠY; Đại ca duyệt từng bước trước khi chạy)

Thay Task 9 của r47 ([lịch sử](../lich-su-dot6/2026-10-15-lat-3c-principal-kiem-trao-quyen.md)): `chup-nen-lich`, `don_sach` gỡ lịch, `TramKiemGia` không còn trong 3c hiện hành. **Không phải task code. Plan này không cấp quyền chạy bất kỳ bước nào.** Mỗi bước dưới đây cần Đại ca cho phép riêng (sổ tay cổng G3), chạy trong **Terminal.app** (memory: khung Terminal của app Claude làm hỏng ô ẩn), dưới **tài khoản trạm**; lệnh dưới `tram-kiem` chỉ qua `sudo -n -u tram-kiem` (dòng sudoers runas CHỈ `tram-kiem`, D22/D40). Em không tự chạy; Em đọc transcript Đại ca dán lại. Dừng ngay ở dấu hiệu dừng đầu tiên.

**Điều kiện vào G3:** Task 3C-H2, 3C-H6, 3C-D5a/b, 3C-D6a/b/c, 3C-S6 đã ghép vào `main`, `UV_OFFLINE=1 uv run pytest -q` xanh (kỳ vọng N₀ + 47 = **2697**, nhật ký chặn rỗng); Codex review gói zip (plan này + P1 + phụ lục 3C-A); I1 xác nhận `giao_viec.bat: false`. Phiên bản OS ghi lại (`sw_vers`).

**Biến dùng chung** (Đại ca gõ một lần trong phiên Terminal.app):

```sh
GOC=/Users/Shared/tram-kiem                      # = giao_viec.thu_muc_kiem
HS=/usr/local/tram/tram-kiem.sb
UIDK=$(id -u tram-kiem)                          # chỉ đọc
TK="sudo -n -H -u tram-kiem"
mkdir -p ~/.tram/g3 && chmod 700 ~/.tram/g3      # bằng chứng G3 (không chứa bí mật)
```

**Hạn ngoài tiến trình:** mỗi bước G3 ≤ 2 phút; bước nào không trả về sau 2 phút → Ctrl-C, chạy "Dọn chung", ghi lại. G4: lệnh `nghiem-thu-kiem` tự có hạn tổng `cho + 900` s — KHÔNG Ctrl-C trong hạn đó (con chạy ở phiên riêng sẽ còn sống); Đại ca đặt đồng hồ 25 phút — quá thì Ctrl-C và dọn chung (có bước dừng con theo PID).

**Dọn chung (mọi lúc dừng giữa chừng):**

```sh
$TK /bin/kill -KILL -1; sleep 2; ps -A -o uid=,pid= | awk -v u=$UIDK '$1==u'     # rỗng mới tiếp
$TK /bin/rm -rf "$GOC"/g3-* 2>/dev/null; ls -A "$GOC"                          # rỗng
ls -d /Users/Shared/tram-nghiem-thu-dau-* 2>/dev/null && rm -rf /Users/Shared/tram-nghiem-thu-dau-*
ps -A -o pid=,ppid=,command= | grep 'nghiem-thu-kiem --trong' | grep -v grep    # con harness còn sau Ctrl-C?
# còn → kill <đúng PID in ra> (KHÔNG kill theo tên), rồi lặp dòng đầu
```

Hoàn tác toàn phần (khi S6 hỏng hoặc Đại ca muốn gỡ): `uv run tram chu go-cai-dat-tho` → đọc kế hoạch → `dong-y` (sudo hỏi mật khẩu trong Terminal.app). Nếu G4.3 có lịch lọt: gỡ lịch theo "Dọn lịch lọt" ở G4.3 TRƯỚC khi gỡ user (xoá user không xoá `/usr/lib/cron/tabs/tram-kiem`).

### G3 — chuẩn bị phép thử OS (đo, không nghiệm thu)

Mục tiêu: thu dữ liệu thật cho phần còn đoán (định dạng `launchctl print`, cây `sudo`, `kill -1`, Seatbelt dưới `sudo -u`), để viết task đọc launchd (3C-D7, plan riêng) có fixture thật. Mọi lệnh dưới `tram-kiem` ở G3 là **chỉ đọc** hoặc **chỉ ghi trong `$GOC/g3-*`**.

| Bước | UID | Lệnh (Đại ca chạy) | Kỳ vọng / ghi lại | Dừng khi | Dọn |
|---|---|---|---|---|---|
| G3.0 | trạm | `sw_vers; id; ls -ld /var/empty "$GOC" $HS; sudo -n -l` | `/var/empty` root 0755; `$GOC` của tram-kiem 0755; `$HS` root:wheel 0644; `sudo -n -l` chỉ `(tram-kiem) NOPASSWD: SETENV: ALL` | có dòng NOPASSWD root/ALL; `$HS` thiếu (chưa cài lại theo 3C-D6a) | — |
| G3.1 | tram-kiem trong hồ sơ | `W=$GOC/g3-$$; $TK /bin/mkdir $W; $TK /bin/mkdir -m 700 $W.nha $W.nha/tmp; for t in "$W/x" "$GOC/ngoai" /Users/Shared/g3-x /private/tmp/g3-x; do $TK /usr/bin/sandbox-exec -f $HS -D LUOT=$W -D NHA=$W.nha /usr/bin/touch "$t"; echo "$t → $?"; done` | `$W/x → 0`; ba đường còn lại mã ≠ 0 "Operation not permitted" | đường ngoài `$W` ghi được → **G4 điều kiện 1 hỏng → dừng S6, trình A1 (phụ lục §5)** | `$TK /bin/rm -rf $W $W.nha` |
| G3.2 | tram-kiem trong hồ sơ | `for x in "/usr/bin/crontab -l" "/bin/launchctl print user/$UIDK" "/usr/bin/at -l"; do $TK /usr/bin/sandbox-exec -f $HS -D LUOT=$W -D NHA=$W.nha /bin/sh -c "$x"; echo "$x → $?"; done` (W như G3.1, tạo lại) | cả ba mã 126 "Operation not permitted" (exec bị cấm, kể cả setuid) | một lệnh chạy được → **điều kiện 1 hỏng → dừng** | như G3.1 |
| G3.3 | tram-kiem, ngoài hồ sơ, chỉ đọc | `$TK /bin/launchctl print user/$UIDK > ~/.tram/g3/user.txt 2>&1; echo $?`; `$TK /bin/launchctl print gui/$UIDK > ~/.tram/g3/gui.txt 2>&1; echo $?`; miền `login/<asid>`: (cửa sổ 1) `$TK /bin/sleep 60 &`, (cửa sổ 2, **sudo root của Đại ca, chỉ đọc — xin phép riêng**) `sudo launchctl procinfo $(pgrep -n -U $UIDK sleep) > ~/.tram/g3/procinfo.txt` lấy asid, rồi `$TK /bin/launchctl print login/<asid> > ~/.tram/g3/login.txt 2>&1; echo $?` | mã thoát + toàn văn các tệp → fixture cho 3C-D7; ghi nguyên văn dòng lỗi khi miền không tồn tại. Em KHÔNG suy định dạng ngoài các tệp này | lệnh hỏi mật khẩu ngoài dự kiến, hộp thoại quyền | `$TK /bin/kill -KILL -1` |
| G3.4 | tram-kiem | (cửa sổ 1) `$TK /bin/sleep 60 &` ; (cửa sổ 2) `ps -A -o pid=,ppid=,pgid=,uid=,ruid=,tty= \| awk -v u=$UIDK '$4==u \|\| $5==u'` ; `ps -o pid,ppid,pgid,uid,ruid,tty,comm -p $(pgrep -n sudo)` | dạng cây `sudo(root, ruid trạm) → sleep(uid=ruid=tram-kiem)`; có/không monitor pty (`use_pty`) — khớp `danh_tinh.la_cua` | lá không phải uid tram-kiem | `$TK /bin/kill -KILL -1` |
| G3.5 | tram-kiem | `$TK /bin/kill -KILL -1; for i in 1 2 3 4 5; do sleep 1; ps -A -o uid=,pid=,comm= \| awk -v u=$UIDK '$1==u'; done` | rỗng cả 5 lần (launchd KHÔNG tự khởi động lại agent của `user/$UIDK`) | còn tiến trình sau 5 s → ghi tên; `cho_het_uid` sẽ đóng cổng mọi lượt → **điều kiện 4 hỏng → dừng, trình phương án** | — |
| G3.6 | tram-kiem, ngoài hồ sơ | `for v in DARWIN_USER_DIR DARWIN_USER_TEMP_DIR DARWIN_USER_CACHE_DIR; do p=$($TK /usr/bin/getconf $v); echo "$v=$p $?"; $TK /usr/bin/find "$p" -mindepth 1 -maxdepth 2 \| head -20; done > ~/.tram/g3/darwin.txt` | đường dưới `/var/folders/`; liệt kê thứ hệ thống tự tạo (để biết `don_thu_muc_he` xoá gì) | đường ngoài `/var/folders` | — |
| G3.7 | trạm | `find / -xdev -type d \( -perm -0002 -o -perm -0020 \) ! -perm -1000 2>/dev/null > ~/.tram/g3/ghi-chung.txt; wc -l ~/.tram/g3/ghi-chung.txt` | danh sách thư mục ghi được không sticky (C01 hàng 5) — Đại ca quyết có thêm vào `GOC_CHUNG` không | — | — |

**Ra khỏi G3:** Đại ca gửi `~/.tram/g3/*` + transcript. Em viết **3C-D7 — bộ đọc launchd** (plan riêng: parser chỉ cho định dạng đã đo, fixture là chính các tệp G3.3, định dạng khác → ném) và nối `doc=` vào `quan_sat_kiem.launchd`. Trước 3C-D7, cổng kiểm lại **luôn đóng** (khung 3C-D6c ném) — G4 không chạy được, đúng thiết kế.

### G4 — S6 cách ly (sau 3C-D7 ghép + review)

| Bước | UID | Lệnh | Kỳ vọng | Dừng khi | Dọn / lui |
|---|---|---|---|---|---|
| G4.0 | trạm | `uv run tram giao mo-cong-kiem` → đọc trạng thái → gõ `dong-y` | "Đã mở cổng kiểm lại." (thu hồi theo UID + hai lượt quan sát, kể cả launchd, sạch) | "Vẫn đóng: …" → ghi lý do, dừng | — |
| G4.1 | trạm → tram-kiem | `uv run tram giao kiem` | mọi mục `principal: …` XANH: thư mục kiểm, sudoers, danh tính (UID thực), giữ APP_ENV, không đọc kho trạm, ghi bản chép, **hồ sơ chặn ghi ngoài lượt**, dừng được lệnh quá hạn, dọn lượt tạm + thu hồi | một mục ĐỎ | dọn chung |
| G4.2 | trạm → tram-kiem | `uv run tram giao nghiem-thu-kiem; echo $?; ls ~/.tram/kiem-lai.dong` | mã 0; mọi dòng XANH (`danh-tinh`, `repo-mot-commit`, `moi-truong-khong-thanh-git`, `nha-moi`, `khong-doc-kho-tram`, `khong-ghi-ngoai-luot`, `khong-chay-cong-cu-lich`, dọn); dấu `kiem-lai.dong` KHÔNG còn; `cong.json` = `mo` | mã ≠ 0, dấu còn | dọn chung; dấu còn thì Đại ca xem log `~/.tram/log/nghiem-thu/` rồi mới `rm ~/.tram/kiem-lai.dong` |
| G4.3 | trạm → tram-kiem | `uv run tram giao nghiem-thu-kiem --tai-sinh --cho 300` (≈ 6–8 phút) | "hồ sơ chặn cài cron/at/submit/launchd" XANH; "tiến trình setsid bị thu hồi ở ra()" XANH; "quan sát đóng cổng khi lịch lọt" VÀNG (không có gì lọt); "không gì chạy sau thu hồi" XANH; "lần kiểm sau đạt" XANH; mã 0 | bất kỳ "CÀI ĐƯỢC" → **điều kiện 1/2 hỏng**: cổng phải đã `dong` (đó là bằng chứng "quan sát chặn N+1"), dừng S6, chạy "Dọn lịch lọt", trình A1 | Dọn lịch lọt (dưới đây) + dọn chung |
| G4.4 | trạm → tram-kiem | Quan sát lỗi chặn N+1: `$TK /usr/bin/touch "$GOC/tan-du"; uv run tram giao mo-cong-kiem --dong-y; uv run tram giao nghiem-thu-kiem; echo $?` | `mo-cong-kiem`: "Vẫn đóng: … gốc bản chép còn 1 mục"; nghiệm thu: dòng chuỗi kiểm lại ĐỎ `CongDong`, không bản chép nào được tạo | cổng mở được hoặc lượt chạy | `$TK /bin/rm "$GOC/tan-du"; uv run tram giao mo-cong-kiem --dong-y` → mở |
| G4.5 | tram-kiem trong hồ sơ | Bộ test HR trong hồ sơ (G4 điều kiện 3, `mach-lookup` đủ): Đại ca chọn một commit HR đã biết xanh; `W=$GOC/g4-hr-$$`; `git -C <kho kiểm HR> archive <commit> \| $TK /usr/bin/tar -x -f - -C $W` (sau `$TK /bin/mkdir $W $W.nha` + `$W.nha/tmp`); `$TK /usr/bin/sandbox-exec -f $HS -D LUOT=$W -D NHA=$W.nha /usr/bin/env HOME=$W.nha TMPDIR=$W.nha/tmp/ APP_ENV=testing /bin/sh -c 'cd '"$W"' && <lệnh kiểm mặc định của HR>'` | bộ test xanh như ngoài hồ sơ; lỗi nào do hồ sơ (EPERM, `mach-lookup` bị từ chối trong `log show --predicate 'sender=="Sandbox"' --last 5m`) thì ghi tên dịch vụ | lỗi do hồ sơ → không tự nới; trình Em danh sách dịch vụ để quyết `MACH_CHO` | `$TK /bin/rm -rf $W $W.nha`; dọn chung |

**Dọn lịch lọt** (chỉ khi G4.3 báo "CÀI ĐƯỢC"; mọi lệnh dưới `tram-kiem`, không đụng lịch của tài khoản trạm/Đại ca):

```sh
$TK /usr/bin/crontab -l; $TK /usr/bin/crontab -r                       # cron của tram-kiem
$TK /usr/bin/atq; $TK /usr/bin/atrm <số việc>                           # at
$TK /bin/launchctl bootout user/$UIDK/vn.tram.nghiem-thu.submit
$TK /bin/launchctl bootout user/$UIDK/vn.tram.nghiem-thu.launchd
$TK /bin/kill -KILL -1
uv run tram giao mo-cong-kiem            # phải mở được (quan sát sạch) — không thì gỡ toàn phần
```

**Ghi bằng chứng** (sổ tay cổng): commit/tree của `main`, phiên bản macOS, UID `tram-kiem`, thời điểm, lệnh, mã thoát, kỳ vọng/thực tế, transcript đã che bí mật, dọn và người cho phép; trạng thái `CHƯA CHẠY / ĐẠT / KHÔNG ĐẠT / BỊ CHẶN`. Kết quả ghi `docs/spikes/<ngày>-s6-principal-kiem.md`. G4 ĐẠT cả G4.0–G4.5 mới đóng C01 (phụ lục 3C-A §2 điều kiện 1–4); I1 mới được xét bật `giao_viec.bat`.

## Trình tự và bằng chứng

P1 → 3C-B; 3C-A → 3C-D; 3C-C → 3C-D. Quota Q1/Q2 dùng cùng P1. T9/T12 chạy thật chỉ sau gate.

**Thứ tự mới (Đại ca đã duyệt): 1a-2 T5, T4, T6 ghép vào `main` TRƯỚC 3c.** Thay câu cũ "1a-2 T4–T6 áp sau chuỗi 3c". Bản vá 3c lên `noi_that.py` tính trên nền đã có bộ lọc `bat_ghi` của 1a-2 T5: r47 T3/T5 một dòng `don_sach`; 3C-D4 thêm `partial`, `dung_cong`, `giet_tam`, `boc_luot`. Không song song sửa `noi_that.py` hoặc primitive process.

Không tái dùng mốc 2225/2370 làm tiêu chuẩn. Delta +128 trong lịch sử chỉ mô tả phần plan cũ, chưa gồm các task ở đây; đo baseline và ghi test thực tế khi Claude triển khai. R47 không còn “chờ Đại ca chốt sáu câu”; hướng đã chốt, độ khả thi và nghiệm thu kỹ thuật vẫn mở.

**Đợt 8 (16/10/2026) — sau khi P1, 3C-B, Q1/Q2 và 3c đợt 7 đã ghép vào `main` `0e33fbf`:**

```
main 0e33fbf (N₀ = 2650)
 ├─ 8.1: 3C-H2 · 3C-H6 · 3C-D5a · 3C-D6a        (không sửa chung file)
 ├─ 8.2: 3C-D5b (sau D5a) · 3C-D6b (sau H2, D5a)
 └─ 8.3: 3C-D6c (sau D5a/b) · 3C-S6 (sau H6, D5a/b, D6b)        → N₀ + 47 = 2697
        → Codex review (zip: plan này + plan P1 + phụ lục 3C-A) → I1 (giao_viec.bat vẫn false)
        → G3 (Task 9, đo — Đại ca duyệt từng bước) → 3C-D7 bộ đọc launchd (plan riêng, fixture G3.3)
        → G4 (Task 9) → S6 đóng C01 hay trình A1
```

Bằng chứng mỗi cổng ghi theo sổ tay (commit/tree, OS, UID `tram-kiem`, lệnh, mã thoát, kỳ vọng/thực tế, dọn, người cho phép). Plan này KHÔNG cấp quyền chạy G3/G4. Sau đợt 8, ở mức offline: H2/H6/H7 áp xong (rủi ro P1 mục 2 đóng offline); H1 còn `ban_chep._chay` (chờ task P1 `stdin=`); C01 chưa đóng (cần G4, mà G4 cần 3C-D7 sau G3).

## Ghi chú triển khai (17/10/2026, I1)

Đối chiếu với `main` `59f8281`. Nguồn số test: thân commit của từng task (đợt 7), bảng "Đợt 8" ở trên, và số `main` sau ghép do người điều phối đo. Em không chạy lại test (I1 chỉ sửa tài liệu).

**Lần ghép vào `main`:**

| Merge | Nội dung | `pytest` trước → sau |
|---|---|---|
| `036183a` | Plan đợt 7: 3C-A (thiết kế), 3C-C, 3C-D1..D4 (chỉ tài liệu) | — |
| `15472a0` | D48–D51 (chỉ tài liệu) | — |
| `9ee1ed3` | Mã đợt 7: r47 T1, T3, T5, T10; 3C-C; 3C-D1..D4; r47 T6, T7, T8 | 2398 → **2566** (+168) |
| `c80ed2c` | Plan đợt 8: 3C-H2/H6, D5a/b, D6a/b/c, S6 (chỉ tài liệu) | — |
| `236f673` | D52–D53 (chỉ tài liệu) | — |
| `59f8281` | Mã đợt 8: 3C-H2, 3C-H6, 3C-D5a, 3C-D5b, 3C-D6a, 3C-D6b, 3C-D6c, 3C-S6 | 2650 → **2697** (+47) |

Giữa hai lần ghép mã, `0e33fbf` (P1 + 3C-B + Q1/Q2) đưa `main` từ 2566 lên 2650.

**Số test từng commit của đợt 7** (thân commit, theo thứ tự ghép): r47 T1 `ed51f55` 2398 → 2405; T3 `fc4dbaa` → 2412; T5 `f83e2f1` → 2429; T10 `b869990` → 2436 (r47 đợt 1–2: +38, khớp plan); 3C-C `3df144b` → 2459 (+23); 3C-D1 `4e68980` → 2463 (+5, −1); 3C-D2 `22f5655` → 2477; 3C-D3 `847cade` → 2493; 3C-D4 `218eafa` → 2507; r47 T6 `8ce48cb` → 2535 (+28); T7 `6616821` → 2548 (+13); T8 `8be075a` → 2566 (+18). Phần 3C-C và 3C-D1..D4 đúng delta của bảng chạy thử (+71 trên nền r47 đợt 1–2).

**Đợt 8:** tám commit `5943b22` (H2), `69cda3e` (H6), `54cbd98` (D5a), `3f93a5a` (D5b), `0faaafc` (D6a), `b6e48fb` (D6b), `c38f809` (D6c), `7471eba` (S6). Thân commit không ghi số riêng; tổng trên `main` sau ghép là 2697, đúng N₀ + 47 của bảng đợt 8.

**Chỗ lệch khi code:**
- r47 T6 (`8ce48cb`): bỏ vế `and '"*:3306"' in hs` trong `tests/test_cai_dat_tho_kiem.py::test_sandbox_cai_ho_so_co_dinh_va_ghim_sudoers`. Lý do: D48 và G-A1/G-A2 cấm mạng, hồ sơ cấm mặc định của 3C-D1 không còn cổng TCP. Cùng lý do với test allow-default của r47 T1 đã bỏ ở 3C-D1 (có trong plan).
- 3C-S6: `kiem_lai(..., chu_dau=True)` chỉ do tiến trình con của harness truyền (`tram/giao_viec/nghiem_thu_kiem.py`). Đây là **lệch có chủ đích** so với H5/H6 nguyên văn của plan P1: H6 bắt `kiem_lai` từ chối khi dấu `kiem-lai.dong` còn, mà chính harness giữ dấu đó. Đã ghi ở G-D5 và cột H5 của "Áp hợp đồng P1". Production không truyền `chu_dau`.
- Đầu file (khối "Đợt 8") ghi "2650 → **2696** passed"; bảng đợt 8, mục "Kết quả chạy thử đợt 8" và `main` đều là **2697**. Số đúng là 2697. Em không sửa dòng cũ.
- Phần còn lại không thấy lệch trong thân commit (đợt 7 ghi "nguyên văn", "áp sạch"). Em không so lại từng dòng mã với plan.

**Mã đã có trên `main`** (kiểm bằng `ls`/`grep`): hồ sơ Seatbelt cấm mặc định, không mạng, không IPC (`tram/tho/quyen_kiem.py`), bọc mọi lệnh của lượt kèm HOME/TMP riêng (`PrincipalKiem.boc_luot` trong `tram/giao_viec/principal_kiem.py`); bản chép đúng cây (`cay_kiem.py`, `ban_chep.py`, `repo_ban_chep.py`); cổng lượt bền `~/.tram/kiem-lai/cong.json` (`cong_luot.py`, `cong_that.py`); quan sát tàn dư (`quan_sat_kiem.py`); `tram giao mo-cong-kiem` (`lenh.py`); R7 so mã cây, lệch thì `cay-khac-nguon` (`kiem_lai.py`, `tick_pipeline.py`); thu hồi theo UID qua `CongLich` (`cong_that.py`); dọn `DARWIN_USER_*` (`thu_muc_he.py`); `tram giao kiem` dưới khoá (`kiem_principal.py`, `kiem_san_sang.py`); khung launchd ném lỗi, cổng đóng (`quan_sat_kiem.py`); harness `tram giao nghiem-thu-kiem` (`nghiem_thu_kiem.py`, `kich_ban_nghiem_thu.py`, `lenh_nghiem_thu.py`); sổ cài/gỡ `tram chu cai-dat-tho`/`go-cai-dat-tho` (`tram/chu/{cai_dat_kiem,so_cai_tho,go_cai_dat_tho}.py`).

**Còn lại:**
- **3C-D7** — bộ đọc launchd. Chờ G3.3 có tệp đo thật. Trước 3C-D7, khung 3C-D6c luôn ném nên **cổng kiểm lại luôn đóng**, G4 không chạy được. Đúng thiết kế.
- **Task 9** — kịch bản G3/G4 ở trên. CHƯA CHẠY. G3 cần Đại ca cho phép từng bước; G3.3 có `sudo launchctl procinfo` do Đại ca tự gõ (D52). S6 chỉ thử cơ chế `user` (D53).
- **H1 còn một chỗ:** `ban_chep._chay` vẫn `subprocess.run(timeout=600)` dưới `sudo`. Chờ P1 thêm `stdin=` cho `chay_gioi_han` (`bs-863.18`). Treo thì fail-closed (cổng ở `dang-chay`).
- **Ctrl-C ở CLI cha** của `nghiem-thu-kiem` để lại con: `bs-863.19`. Kịch bản G3/G4 dặn dừng con theo PID.
- C01 **chưa đóng**. Chỉ đóng khi G4.0–G4.5 đạt.
- Sửa của chu kỳ review 2 (đợt 8) chưa qua người review mới; đưa vào zip review Codex.
- Bead `bs-urj.12`, `bs-urj.13`, `bs-urj.14` vẫn mở dù r47 T5/T6/T8 đã ghép. Người điều phối xét đóng sau review.

**Cổng đang chờ:** review Codex gói đợt 7–8 → G3 (Đại ca duyệt từng bước) → 3C-D7 → G4 (S6). `giao_viec.bat` vẫn `false` (mặc định trong `tram/cau_hinh/giao_viec.py`).
