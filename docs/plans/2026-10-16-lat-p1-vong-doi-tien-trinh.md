# Lát P1 + 3C-B — vòng đời tiến trình có hạn, UID thực, cổng lịch — Implementation Plan

> **Review đợt 7 (17/10/2026):** trạng thái vận hành hiện hành theo [phụ lục cổng](../handovers/2026-10-17-cong-sau-review-dot7.md) và [plan V2](../plans/2026-10-17-lat-v2-va-sau-review-dot7.md). Các chữ ĐẠT/count bên dưới giữ làm lịch sử tác giả; không vượt blockers review mới. Khi khác nhau về lệnh thử/cleanup hoặc readiness, phụ lục đợt 7 ưu tiên; quyết định D1–D53 giữ nguyên.


> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Trạng thái: PLAN đã chạy thử trọn trên bản sao `main` `5da881e` (RED/GREEN thật, số ở từng task); CHƯA áp vào `main`; CHƯA chạy thật trên OS (G3/G4/G5 ĐÓNG).**

**Goal:** Một primitive tiến trình DUY NHẤT có hạn hữu hạn và sở hữu cả cây con (P1), rồi trên đó: xác minh UID thực của principal, cổng thao tác lịch, hạn tổng harness có cổng dọn bền (3C-B).

**Architecture:** `tram/kiem/vong_doi.py` (`Nhom`, `khoi_chay`, `thu_hoi`) là đầu mối kill/wait; ảnh chụp cây bằng `ps` cột số (`cay_tien_trinh.py`), lệnh hệ thống ngắn có hạn tuyệt đối (`lenh_ngan.py`). Mọi chỗ spawn-rồi-chờ của lệnh kiểm, CLI phiếu và app-server đi qua nó (thăm dò cách ly `kiem_am`/`kiem_cong` chưa — xem Rủi ro). 3C-B thêm `chay_gioi_han` (hình dạng `subprocess.run`), `danh_tinh.xac_minh_uid` (UID nhân ghi cho tiến trình dò), `cong_lich.CongLich` (chỉ chạy dưới tiền tố đã xác minh) và `han_tong.chay_han_tong` (harness là tiến trình con + dấu cổng O_EXCL). 3c nối các khối này theo mục "Hợp đồng cho 3c".

**Tech Stack:** Python 3.12 stdlib (`subprocess`, `select`, `os`, `pwd`, `signal`), pytest 8; macOS `/bin/ps`, `/usr/bin/sudo -n`, `/bin/kill`.

**Spec / nguồn:** [D45–D47](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md) (D1–D44 ở [chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md)); [kế hoạch tích hợp](../../tasks/plan.md) (P1, 3C-B); review Codex đợt 6 C02 + Q02 (`.handover/review-codex-dot6/REVIEW-CODEX.md`); [plan 3c hiện hành](2026-10-15-lat-3c-principal-kiem-trao-quyen.md) (T12 r47 ở [lịch sử](../lich-su-dot6/2026-10-15-lat-3c-principal-kiem-trao-quyen.md), "Câu hỏi r47" câu 5); [sổ tay cổng](../handovers/2026-10-15-so-tay-chay-that.md); quota Q1/Q2 ở [bs-78r.10](2026-10-16-bs-78r-10-quota-dung-principal.md) (cùng primitive này).

## Global Constraints

- **N₀ = 2242** (`UV_OFFLINE=1 uv run pytest -q` trên `main` `5da881e`, đo 16/10 trên bản sao, kèm plugin chặn spawn host: 0 lần chặn). Lát này **+69 → 2311**; cộng Q1/Q2 (plan bs-78r.10) **+15 → 2326**. Đo lại trước Task 1; lệch thì dừng, báo người điều phối.
- TDD: test trước, chạy thấy fail (thông báo ở Step 2 là kết quả THẬT trên bản sao), viết mã, chạy thấy pass. Mã trong plan là nguyên văn file/bản vá đã chạy — áp đúng như in, không "viết lại tương đương".
- Mỗi file nguồn ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự Unicode (lớn nhất sau plan: `tram/tho/vong_khe.py` 120, `tram/chay_cli/codex/app_server.py` 119, `tram/kiem/vong_doi.py` 119, `tests/test_han_muc_principal.py` 118, `tests/test_chay_cli_vong_doi.py` 117).
- Không phụ thuộc mới. Định danh tiếng Việt không dấu. Thông báo lỗi không chép argv, đường dẫn, stdout/stderr hay chữ do tiến trình con gửi (dot6-Q06).
- **Test không bao giờ:** chạy `sudo`, `crontab`, `at`, `atq`, `atrm`, `batch`, `launchctl`, `dscl`/`sysadminctl` ghi, `pkill`, `killall`, `security`; tạo user; đụng Keychain, mạng, `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`). Tiến trình thật chỉ là `python -c`/`/bin/sleep` của chính user đang test, trong `tmp_path`, tự thu hồi (test có `finally` giết đúng PID mình tạo). Ca sudo/root/kill bị từ chối dùng Popen/ps/kill GIẢ.
- Một task một commit, trên nhánh tạo từ `main` sau khi ghép đợt trước. Task cùng đợt không sửa chung file. Không push, không merge.
- Không sửa plan/mã thuộc 3c (`tram/giao_viec/{principal_kiem,kiem_lai,kiem_san_sang,noi_that,ban_chep}.py`, harness T11/T12): chỉ ghi "Hợp đồng cho 3c". Không sửa 4d.
- Lệnh test: `UV_OFFLINE=1 uv run pytest -q` từ gốc worktree. Trước khi chạy toàn bộ: kiểm fixture không tác động host (cách đã dùng khi chạy thử: plugin `sys.addaudithook` chặn spawn các lệnh cấm + PATH giả cho tên trần — xem "Kết quả chạy thử").

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline | Còn chờ OS |
|---|---|---|---|---|
| G1 | Không `wait()`/`join()` vô hạn, không Timer/luồng hẹn giờ trong primitive | `vong_doi`, `lenh_ngan`, `chay_lenh`, `app_server`, `claude`, `codex/chay` | `test_treo_sau_sigkill_tra_false_trong_han`, `test_kill_cham_nhieu_nhom_…`, `test_chay_ngan_qua_han_…`, `test_treo_thu_hoi_qua_kill_nguoi_goi_khong_de_luong_nen` | thời gian thật của `sudo kill`/`ps` |
| G2 | Hết hạn/xong → thu hồi cả cây: cháu ở phiên mới (như pty), cháu bỏ qua SIGTERM, cha thoát bình thường để lại cháu | `Nhom.cho` chụp mỗi 1 s; `thu_hoi` TERM→KILL theo nhóm | `test_thu_hoi_chau_bo_qua_sigterm[*]` (3 ca), `test_chau_tu_tach_phien_…` | dạng cây thật dưới `sudo` có/không pty |
| G3 | "Treo sau SIGKILL" (r47 câu 5) xử lý được: trả về trong hạn, báo chưa thu hồi; người gọi giữ cổng đóng (khe dừng, giữ pid + worktree/phiếu) | `thu_hoi` → False; `KetQuaLenh.da_thu_hoi`; `LoiThuHoi` → `VongKhe.hong` | `test_goc_treo_sau_sigkill_van_tra_ve_co_han`, `test_kill_bi_tu_choi_thi_dung_khe_trong_han[*]`, `test_cli_khong_thu_hoi_duoc_giu_pid_va_dung_khe`, `test_loi_thu_hoi_lan_sau_khong_don_phieu` | có xảy ra với sudoers thật không |
| G4 | Không gửi tín hiệu ra ngoài cây: chỉ nhóm thấy còn sống trong ảnh chụp thành công ≤ 2 s + nhóm gốc chưa gặt; không nhóm 0/1/của quản lý; không theo username | `Nhom._gui`, `Nhom.cay` | `test_ps_loi_van_gui_nhom_thay_lan_truoc…`, `test_ps_loi_lau_thi_chi_gui_nhom_goc`, `test_doc_ps_dong_hong_hoac_gia_mao_thi_nem[*]` | — |
| G5 | Một đầu mối kill/wait (`_kill_nhom`, `mo_coi.kill_cuc_bo` là bí danh) | `vong_doi` | grep trong review | — |
| G6 | UID THỰC: đọc uid/ruid nhân ghi cho cây dò dưới `boc`; env/argv giả không qua | `danh_tinh` | `test_boc_dong_nhat_va_env_gia_mao_bi_tu_choi` (thật, user test), `test_sai_uid_hoac_cay_la_bi_tu_choi[*]` | `ps` thấy đúng uid `tram-kiem` dưới sudo |
| G7 | Sai danh tính → 0 lệnh cron/at/launchctl; lệnh lịch trần/dưới tiền tố khác/qua shell bị từ chối trước khi chạy | `cong_lich` | `test_sai_danh_tinh_khong_goi_lenh_nao[*]`, `test_lenh_ngoai_principal_bi_chan_truoc_khi_chay` | G4 (3c nối `CongLich`) |
| G8 | Hạn tổng harness thu hồi được cây; `don()` luôn chạy; dọn không xác nhận → dấu cổng còn, lượt sau bị từ chối không spawn | `han_tong` | `test_qua_han_thu_hoi_ca_chau_roi_don_va_mo_cong`, `test_don_khong_xac_nhan…[*]`, `test_kill_bi_tu_choi_van_don_lich_va_cong_giu_dong` | G4 |
| G9 | Lỗi không lộ argv/stderr/chữ con (dot6-Q06); dot6-Q01 (returncode của 3c T11) không bị đụng | `chay_gioi_han`, `app_server`, `chay_lenh`, `claude` | `test_qua_han_thu_hoi_roi_nem_timeout_khong_kem_argv`, `test_loi_khoi_chay_khong_chep_duong_dan`, `test_loi_khong_chep_chu_cua_app_server` | log launchd thật |
| G10 | Hạn chờ phải hữu hạn trước khi spawn (`inf`/`nan` bị từ chối) | `Nhom.cho`, `chay_lenh`, `chay_gioi_han`, `han_tong` | `test_han_khong_huu_han…` (3 file) | — |

## Review nghi ngờ (doubt-driven) — 3 chu kỳ, người review ngữ cảnh mới

Chéo mô hình (Codex/Gemini CLI) **bị bỏ qua: ngữ cảnh không tương tác** (Em chạy như subagent, không được tự gọi CLI ngoài). Người review chỉ nhận ARTIFACT + CONTRACT, không nhận kết luận của Em.

| Chu kỳ | Phát hiện chính | Phân loại → xử lý |
|---|---|---|
| 1 (19 mục) | (B) ảnh chụp đầu tiên chỉ sau khi gốc đã được gặt → cháu tự setsid thoát; (B) `subprocess.run(timeout)` còn `wait()` trần sau `kill()` bị từ chối; một hạn chung làm bỏ cả pha KILL; `ps` lỗi không gửi nhóm đã biết; `comm` của `ps` giả được dòng; `mot_lan` xoá pid khi CLI chưa thu hồi; `da_thu_hoi` mất ở `lenh_tho`; lỗi giữa spawn và chờ; `{e}` lộ đường dẫn | Sửa: chụp mỗi 1 s trong `cho`; `lenh_ngan`; ngân sách gửi theo pha; giữ nhóm của ảnh chụp thành công gần nhất; bỏ `comm`, chỉ cột số; giữ pid; `lenh_tho` → `LoiThuHoi`; `try/except` sau spawn; chỉ tên loại lỗi; `VongKhe.hong`. Đánh đổi có ghi: `cho_den_dung` dựa bộ hẹn `dung` của `mot_lan`; luồng đọc stdout có thể còn kẹt khi tiến trình ngoài cây giữ ống (chỉ xảy ra khi đã `LoiThuHoi` → khe dừng). Ngoài phạm vi: `mo_coi` (pid file từ lần chạy trước — bead riêng), `kiem_san_sang`/`kiem_lai` (3c, ghi vào Hợp đồng) |
| 2 (22 mục) | `PrincipalKiem.kill_nhom` còn `run(timeout=20)`; `kiem_am` thăm dò bằng `run`; `kiem_lai` bỏ `da_thu_hoi`; 5 bản kill; `chay_gioi_han`/app-server không chụp định kỳ; lỗi sau spawn bỏ qua kết quả thu hồi; `han_tong` không gọi `don()` khi thu hồi lỗi; lọc chữ lịch bị vượt qua shell; PATH quota lấy từ env quản lý; `user:<quản lý>` lọt; ghi sổ hạn mức ngoài `try`; `join` 35 s < 45 s | Sửa: bí danh kill; `kiem_am` qua `chay_gioi_han` (chu kỳ 3 hoàn tác); chụp định kỳ trong `chay_gioi_han` và `_dong`; `LoiThuHoi` thay lỗi gốc khi chưa thu hồi; `don()` luôn chạy, hạn phải hữu hạn; `CongLich` thành danh sách đóng (không lọc chữ); `path` theo cấu hình thợ; `xac_minh_uid` lần đọc quota đầu; `luu_han_muc` trong `try`; `join` +60 s; `thu_hoi(1, 3, 2)` cho app-server (cận 43 s; chu kỳ 3 tính lại 48 s). 3c (H2/H6/H7 dưới đây): `PrincipalKiem`, `kiem_lai`, `kiem_san_sang`. Đánh đổi: thứ tự gửi theo nhóm khi `sudo kill` chậm (kết thúc False, đóng cổng); `chay_ngan` bỏ lại `sudo` treo (khe đã dừng nên không dồn) |
| 3 (13 mục) | cây dò UID không thu hồi → `LoiDanhTinh` nên khe không dừng; `tram tho kiem` hỏi quota chưa xác minh UID; `kiem_am` dùng `start_new_session` làm `sudo -u` hỏi mật khẩu hỏng (hồi quy do chính bản sửa chu kỳ 2); `text=True` giải mã chặt bỏ qua thu hồi; cổng lịch dùng kill principal cho lệnh quan sát của quản lý; `LoiThuHoi` ở lần chạy thứ 2 vẫn `don_phieu`; hạn vô hạn; ảnh chụp cũ khi `ps` lỗi; cận 43 s bỏ sót dò UID; giữ pid cả khi lỗi khác; dữ liệu app-server hỏng làm sập `tram tho kiem` | Sửa: `LoiThuHoi` cho cây dò; `kiem_3b` xác minh UID; **hoàn tác** thay đổi `kiem_am` (đưa ra Rủi ro — cần thiết kế riêng vì Đại ca gõ mật khẩu sudo trong Terminal); đọc bytes + `replace`; kill gộp trong `CongLich`; `except LoiThuHoi` trong `chay_phieu`; kiểm hữu hạn trước spawn; nhóm đã biết chỉ dùng khi ảnh chụp ≤ 2 s; nhịp đầu chỉ xác minh UID, cận 48 s; giữ pid chỉ khi `LoiThuHoi`; `except Exception` → vàng. Đánh đổi: luồng đọc stdout có thể kẹt khi tiến trình ngoài cây giữ ống (khe đã dừng); `CongLich` dựng trực tiếp chỉ dành cho test. **Theo luật 3 chu kỳ, các sửa của chu kỳ 3 CHƯA qua người review mới — đề nghị review lại phần này khi gom zip cho Codex.** |

## File Structure

```
tram/kiem/
  lenh_ngan.py        (mới, T1)  chay_ngan: lệnh hệ thống ngắn có hạn TUYỆT ĐỐI (ps, sudo kill) — không wait() trần
  cay_tien_trinh.py   (mới, T1)  TienTrinh, doc_ps (chỉ cột số), chup_he, cay (ppid + nhóm đã biết)
  vong_doi.py         (mới, T2; T5 thêm cho_den_dung)  Nhom/khoi_chay/thu_hoi, LoiThuHoi, kill_cuc_bo — ĐẦU MỐI kill/wait
  chay_lenh.py        (sửa, T3)  chay_mot_lenh qua Nhom; KetQuaLenh.da_thu_hoi; _kill_nhom = bí danh
  lenh_tho.py         (sửa, T3)  lệnh kiểm phía thợ: chưa thu hồi → LoiThuHoi
  chay_gioi_han.py    (mới, T6)  run có hạn, chụp định kỳ, lỗi chỉ mang tên chương trình
  danh_tinh.py        (mới, T7)  quan_sat / xac_minh_uid — UID nhân ghi cho cây dò dưới boc
  han_tong.py         (mới, T8)  chay_han_tong, cong_dong, gop_kill, HetHanTong — hạn tổng harness + dấu cổng
  cong_lich.py        (mới, T9)  CongLich, mo_cong_lich, duoc_chay — cổng lệnh lịch/dọn của tram-kiem
tram/tho/
  principal.py        (sửa, T3)  Principal.kill_nhom qua chay_ngan (5 s)
  mo_coi.py           (sửa, T5)  kill_cuc_bo = bí danh của vong_doi
  mot_lan.py          (sửa, T5)  giữ dang-chay.pid khi CLI ném
  vong_khe.py         (sửa, T5; Q1-b, Q2 ở plan bs-78r.10)  hong: LoiThuHoi → dừng khe và nhịp
  phieu_chay.py       (sửa, T5)  LoiThuHoi → không don_phieu, chỉ gỡ khoá
tram/chay_cli/
  claude.py           (sửa, T5)  ChayClaude qua khoi_chay/cho_den_dung
  codex/chay.py       (sửa, T5)  ChayCodex như trên
  codex/app_server.py (sửa, T4; Q1-a)  đọc theo hạn bằng select, không Timer; lỗi cố định
tests/
  test_cay_tien_trinh.py (mới, T1) · test_vong_doi.py, test_vong_doi_ps.py (mới, T2) · test_chay_lenh_p1.py (mới),
  test_principal.py, test_lenh_tho.py (sửa, T3) · test_codex_app_server.py + du_lieu/codex/app_server_gia.py (sửa,
  T4) · test_chay_cli_vong_doi.py, test_phieu_chay_thu_hoi.py (mới), test_codex_chay.py (sửa, T5) ·
  test_chay_gioi_han.py (mới, T6) · test_danh_tinh.py (mới, T7) · test_han_tong.py (mới, T8) · test_cong_lich.py (mới, T9)
```

Ranh giới: `vong_doi` không biết principal là gì — nhận `kill(pgid, sig)` của người gọi. Principal/PrincipalKiem chỉ là
"vận chuyển tín hiệu" (sudo kill có hạn). 3C-B xây trên primitive, không tự kill/wait.

## Sơ đồ đợt và số test

Task cùng đợt không sửa chung file. Cột "tổng" là số thu thập THẬT (`pytest --collect-only`) trên bản sao khi áp theo
thứ tự T1…T9 rồi Q1-a, Q1-b, Q2 (thứ tự khác trong cùng đợt cho cùng tổng cuối).

| Đợt | Task | File chính | Test + | Tổng sau task (thứ tự chạy thử) |
|---|---|---|---|---|
| 1 | T1 | lenh_ngan, cay_tien_trinh | +10 | 2252 |
| 2 | T2 | vong_doi | +9 | 2261 |
| 3 | T3 | chay_lenh, lenh_tho, principal | +4 | 2265 |
| 3 | T4 | app_server (+ app-server giả) | +4 | 2269 |
| 4 | T5 | claude, codex/chay, vong_doi, mo_coi, mot_lan, phieu_chay, vong_khe | +8 | 2277 |
| 3 | T6 | chay_gioi_han | +6 | 2283 |
| 4 | T7 | danh_tinh | +13 | 2296 |
| 4 | T8 | han_tong | +9 | 2305 |
| 5 | T9 | cong_lich | +6 | 2311 |
| 4 | Q1-a (bs-78r.10) | app_server, bo, bo_cli, kiem_3b | +3 | 2314 |
| 5 | Q1-b (bs-78r.10) | han_muc_ranh, vong_khe | +2 | 2316 |
| 6 | Q2 (bs-78r.10) | han_muc_ranh, vong_khe, app-server giả | +10 | 2326 |

Tổng lát P1 + 3C-B: **N₀ + 69 = 2311**; cộng Q1/Q2 (plan bs-78r.10): **N₀ + 84 = 2326**.

## Tasks

### Task 1: Ảnh chụp tiến trình chỉ cột số + lệnh ngắn có hạn tuyệt đối (P1-a)

**Đợt:** 1 · **Song song với:** — · **Phải xong trước:** Task 2. `ps` chỉ lấy 5 cột số (tên lệnh do agent đặt được, có thể chứa xuống dòng để giả dòng `ps`); `chay_ngan` thay `subprocess.run(timeout)` cho `ps`/`sudo kill` vì `run()` còn `wait()` trần khi `kill()` bị từ chối.

**Files:**
- Create: `tests/test_cay_tien_trinh.py`
- Create: `tram/kiem/cay_tien_trinh.py`
- Create: `tram/kiem/lenh_ngan.py`

**Interfaces:**
- Consumes: —
- Produces: `lenh_ngan.chay_ngan(argv, *, timeout, doc=False) -> tuple[int | None, bytes]`; `cay_tien_trinh.TienTrinh(pid, ppid, pgid, uid, ruid)`, `PS`, `doc_ps(bytes) -> list[TienTrinh]` (ValueError khi dòng không đúng 5 số), `chup_he(*, chay=chay_ngan)` (OSError khi `ps` lỗi/quá hạn), `cay(ds, goc: int | None, nhom: set[int]) -> list[TienTrinh]`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cay_tien_trinh.py` (mới):

```python
"""Ảnh chụp tiến trình và cây con của MỘT lần chạy (lát P1): chỉ đọc `ps` (cột số), không gửi tín hiệu."""
import subprocess
import sys
import time

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he, doc_ps
from tram.kiem.lenh_ngan import chay_ngan

PS = (b"    0     0     0     0     0\n"
      b"    1     0     1     0     0\n"
      b"  500     1   500   501   501\n"
      b"  600   500   600     0   501\n"
      b"  601   600   601   502   502\n"
      b"  602   601   602   502   502\n"
      b"  603     1   601   502   502\n"
      b"  700     1   700   502   502\n")


def test_doc_ps_chi_cot_so():
    ds = doc_ps(PS)
    assert ds[4] == TienTrinh(601, 600, 601, 502, 502) and len(ds) == 8


@pytest.mark.parametrize("hong", [b"abc 1 1 1 1\n", b"1 2 3\n", b"5 1 -7 0 0\n", b"5 1 5 0 0 x\n",
                                  b"5 1 5 0 0\r9 5 1 501 501\n"])
def test_doc_ps_dong_hong_hoac_gia_mao_thi_nem(hong):
    with pytest.raises(ValueError):
        doc_ps(PS + hong)


def test_cay_theo_ppid_va_nhom_da_biet():
    ds = doc_ps(PS)
    # gốc 600 còn sống: con 601 (nhóm mới, như pty của sudo), cháu 602 (phiên mới), 603 mồ côi nhưng cùng nhóm 601
    assert [t.pid for t in cay(ds, 600, {600})] == [600, 601, 602, 603]
    # gốc đã được gặt: chỉ còn đi theo nhóm đã biết (và con của chúng); 700 không thuộc cây
    assert [t.pid for t in cay(ds, None, {601})] == [601, 602, 603]
    assert cay(ds, None, set()) == []
    assert 500 not in {t.pid for t in cay(ds, 600, {600})}


def test_chup_he_doc_ps_that_thay_tien_trinh_con_cua_minh():
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        con = cay(chup_he(), p.pid, {p.pid})
        assert [t.pid for t in con] == [p.pid] and con[0].pgid == p.pid
    finally:
        p.kill()
        p.wait(5)


def test_chup_he_ps_loi_thi_nem():
    def chay(argv, **kw):
        assert argv[0] == "/bin/ps" and kw == {"timeout": 5, "doc": True}
        return None, b""
    with pytest.raises(OSError):
        chup_he(chay=chay)


def test_chay_ngan_qua_han_tra_ve_ngay_khong_cho():
    t0 = time.monotonic()
    assert chay_ngan([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.3) == (None, b"")
    assert time.monotonic() - t0 < 3
    assert chay_ngan([sys.executable, "-c", "print(7)"], timeout=10, doc=True) == (0, b"7\n")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_cay_tien_trinh.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.cay_tien_trinh'
ERROR tests/test_cay_tien_trinh.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/cay_tien_trinh.py` (mới):

```python
"""Ảnh chụp tiến trình (lát P1, dot6-C02/Q02): `ps` của hệ thống — người dùng thường đọc được pid/ppid/pgid/uid/ruid
của MỌI tiến trình trên macOS, không cần sudo, không gửi tín hiệu. `uid` là UID HIỆU LỰC nhân ghi cho tiến trình,
không phải tên trong env. CHỈ lấy cột số (không `comm`): tên chương trình do agent đặt được, có thể chứa xuống dòng để
giả một dòng `ps` — dòng nào không đúng 5 số nguyên không âm làm cả ảnh chụp hỏng (người gọi coi như không xác nhận).
Cây của một lần chạy = gốc (khi chưa gặt) + mọi tiến trình có cha trong cây hoặc thuộc một nhóm đã biết của cây — gồm
cả con mà `sudo` đặt vào nhóm/phiên mới (pty). Tiến trình đã rời cả cây lẫn mọi nhóm đã biết GIỮA hai lần chụp (fork +
setsid rồi cha thoát trong < 1 s) không thấy được: đó là ranh giới cách ly C01/3C-A, không phải lời hứa của P1."""
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from tram.kiem.lenh_ngan import chay_ngan

PS = ("/bin/ps", "-A", "-o", "pid=,ppid=,pgid=,uid=,ruid=")


@dataclass(frozen=True)
class TienTrinh:
    pid: int
    ppid: int
    pgid: int
    uid: int
    ruid: int


def doc_ps(van_ban: bytes) -> list[TienTrinh]:
    ds = []
    for dong in van_ban.split(b"\n"):
        if not dong.strip():
            continue
        phan = dong.split()
        if len(phan) != 5 or not all(x.isdigit() for x in phan):
            raise ValueError("dòng ps sai dạng")
        ds.append(TienTrinh(*map(int, phan)))
    return ds


def chup_he(*, chay: Callable = chay_ngan) -> list[TienTrinh]:
    ma, ra = chay(list(PS), timeout=5, doc=True)
    if ma != 0:
        raise OSError(f"ps mã {ma}")
    return doc_ps(ra)


def cay(ds: Iterable[TienTrinh], goc: int | None, nhom: set[int]) -> list[TienTrinh]:
    ds, pids, nhom = list(ds), set(), set(nhom)
    doi = True
    while doi:
        doi = False
        for t in ds:
            if t.pid not in pids and (t.pid == goc or t.ppid in pids or t.pgid in nhom):
                pids.add(t.pid)
                nhom.add(t.pgid)
                doi = True
    return [t for t in ds if t.pid in pids]
```

`tram/kiem/lenh_ngan.py` (mới):

```python
"""Lệnh hệ thống NGẮN có hạn TUYỆT ĐỐI (lát P1). `subprocess.run(timeout=…)` khi quá hạn gọi `kill()` rồi `wait()`
không hạn — nếu `kill()` bị từ chối (tiến trình là `sudo` chạy root) thì `Popen.__exit__` còn `wait()` trần, treo
mãi. Ở đây quá hạn → thử kill, đóng ống, KHÔNG chờ, trả mã None; đối tượng bỏ lại được `subprocess` tự gặt về sau.
Chỉ dùng cho `ps` (`cay_tien_trinh`) và `sudo -n -u … /bin/kill` (`Principal.kill_nhom`)."""
import subprocess


def chay_ngan(argv: list[str], *, timeout: float, doc: bool = False) -> tuple[int | None, bytes]:
    p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE if doc else subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        ra, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            p.kill()
        except OSError:
            pass
        if p.stdout is not None:
            p.stdout.close()
        return None, b""
    return p.returncode, ra or b""
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_cay_tien_trinh.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2252 tests collected in 9.68s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cay_tien_trinh.py tram/kiem/cay_tien_trinh.py tram/kiem/lenh_ngan.py
git commit -m "feat(kiem): ảnh chụp tiến trình cột số và lệnh ngắn có hạn tuyệt đối (P1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: Primitive `vong_doi` — Nhom, thu hồi cả cây có hạn (P1-b)

**Đợt:** 2 · **Phải xong trước:** Task 3–9 và Q1. Đầu mối DUY NHẤT của kill/wait. Chụp cây mỗi giây khi gốc còn sống (bắt cháu tự setsid trước khi cha thoát); `thu_hoi` TERM → chờ → KILL → chờ, mỗi pha có ngân sách gửi riêng; True chỉ khi gốc đã gặt và ảnh chụp cuối rỗng. Ca treo sau SIGKILL → False trong hạn. `ps` lỗi: chỉ gửi cho nhóm thấy ở ảnh chụp thành công ≤ 2 s trước, cũ hơn chỉ nhóm gốc chưa gặt (PID tái dùng).

**Files:**
- Create: `tests/test_vong_doi.py`
- Create: `tests/test_vong_doi_ps.py`
- Create: `tram/kiem/vong_doi.py`

**Interfaces:**
- Consumes: Task 1 (`TienTrinh`, `cay`, `chup_he`).
- Produces: `Kill = Callable[[int, int], None]`; `LOI_GUI`; `CHU_KY_CHUP = 1.0`; `class LoiThuHoi(RuntimeError)`; `kill_cuc_bo(pgid, sig)`; `class Nhom(p, *, kill, chup=chup_he)` với `.p`, `.cho(giay) -> int | None` (ValueError nếu không hữu hạn), `.cay() -> list[TienTrinh] | None`, `.thu_hoi(*, cho_term=2.0, cho_cuoi=2.0, han_gui=10.0) -> bool`; `khoi_chay(argv, *, kill, popen=subprocess.Popen, chup=chup_he, **kw) -> Nhom` (luôn `start_new_session=True`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_vong_doi.py` (mới):

```python
"""Primitive vòng đời tiến trình (lát P1): hạn hữu hạn, thu hồi cả cây. Tiến trình thật chỉ là `python -c` của chính
user đang test, trong tmp_path, tự thu hồi; ca sudo/root/kill bị từ chối dùng Popen/ps/kill GIẢ."""
import os
import signal
import subprocess
import sys
import time

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom, khoi_chay, kill_cuc_bo

PY = sys.executable
SUDO = TienTrinh(4242, 1, 4242, 0, 501)
CHAU = ("import subprocess, sys, time\n"
        "c = subprocess.Popen([sys.executable, '-c', 'import signal, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'], start_new_session={moi})\n"
        "open('chau.pid', 'w').write(str(c.pid)); time.sleep({ngu})\n")


class PopenGia:
    """Gốc không bao giờ thoát (vd. `sudo` root không nhận tín hiệu của tiến trình quản lý)."""
    pid, returncode = 4242, None

    def wait(self, timeout=None):
        time.sleep(min(timeout or 0, 0.05))
        raise subprocess.TimeoutExpired("x", timeout)

    def poll(self):
        return None


def _song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _chau(tmp_path, *, moi: bool, ngu: float):
    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill_cuc_bo, cwd=tmp_path)
    het = time.monotonic() + 10
    while not (tmp_path / "chau.pid").exists() and time.monotonic() < het:
        time.sleep(0.02)
    return n, int((tmp_path / "chau.pid").read_text())


def test_treo_sau_sigkill_tra_false_trong_han():
    gui = []

    def kill(g, sig):
        gui.append((g, sig))
        raise PermissionError
    n, t0 = Nhom(PopenGia(), kill=kill, chup=lambda: [SUDO]), time.monotonic()
    assert n.thu_hoi(cho_term=0.2, cho_cuoi=0.2, han_gui=0.2) is False
    assert time.monotonic() - t0 < 1.5 and gui == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]
    with pytest.raises(ValueError):
        n.cho(float("inf"))


def test_kill_cham_nhieu_nhom_moi_pha_van_gui_va_co_han():
    cay = [SUDO, *(TienTrinh(5000 + i, 4242, 5000 + i, 502, 502) for i in range(50))]
    gui = []

    def kill(g, sig):
        gui.append(sig)
        time.sleep(0.1)
        raise subprocess.TimeoutExpired(["kill"], 0.1)
    t0 = time.monotonic()
    assert Nhom(PopenGia(), kill=kill, chup=lambda: cay).thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.3) is False
    assert time.monotonic() - t0 < 2 and signal.SIGKILL in gui and len(gui) < 20


def test_da_thoat_cay_rong_khong_gui_gi():
    p = subprocess.Popen([PY, "-c", "pass"], start_new_session=True)
    p.wait(10)
    gui = []
    assert Nhom(p, kill=lambda g, s: gui.append(g), chup=lambda: []).thu_hoi() is True and gui == []


@pytest.mark.parametrize("moi, ngu, cha_thoat", [(True, 60, False), (False, 0, True), (True, 1.5, True)])
def test_thu_hoi_chau_bo_qua_sigterm(tmp_path, moi, ngu, cha_thoat):
    """Cháu ở phiên mới (như pty của sudo) hoặc cùng nhóm; cha còn chạy hoặc đã thoát bình thường."""
    n, chau = _chau(tmp_path, moi=moi, ngu=ngu)
    try:
        assert (n.cho(10) == 0) if cha_thoat else (n.cho(0.3) is None)
        t0 = time.monotonic()
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=3) is True and time.monotonic() - t0 < 6 and not _song(chau)
    finally:
        kill_cuc_bo(n.p.pid, signal.SIGKILL)
        if _song(chau):
            os.kill(chau, signal.SIGKILL)


def test_khoi_chay_luon_nhom_rieng():
    goi = []

    def popen(argv, **kw):
        goi.append(kw)
        return PopenGia()
    khoi_chay(["x"], kill=kill_cuc_bo, popen=popen, start_new_session=False, cwd="/")
    assert goi == [{"start_new_session": True, "cwd": "/"}]
```

`tests/test_vong_doi_ps.py` (mới):

```python
"""Primitive P1 khi `ps` lỗi: vẫn gửi nhóm thấy trong ảnh chụp thành công GẦN (≤ 2 s); ảnh chụp cũ hơn → chỉ nhóm gốc
chưa gặt (số nhóm đã chết có thể bị tái dùng). Popen/ps/kill GIẢ."""
import signal

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom


def test_ps_loi_van_gui_nhom_thay_lan_truoc_va_khong_xac_nhan():
    gui, lan = [], []

    def chup():
        lan.append(1)
        if len(lan) > 1:
            raise OSError("ps")
        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append((g, s)), chup=chup)
    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False
    assert (5000, signal.SIGKILL) in gui and (4242, signal.SIGKILL) in gui


def test_ps_loi_lau_thi_chi_gui_nhom_goc():
    gui, lan = [], []

    def chup():
        lan.append(1)
        if len(lan) > 1:
            raise OSError("ps")
        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g), chup=chup)
    n.cay()
    n.lan_dung -= 10                                     # ảnh chụp thành công gần nhất đã cũ: nhóm 5000 có thể tái dùng
    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False and set(gui) == {4242}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_vong_doi.py tests/test_vong_doi_ps.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.vong_doi'
E   ModuleNotFoundError: No module named 'tram.kiem.vong_doi'
ERROR tests/test_vong_doi.py
ERROR tests/test_vong_doi_ps.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.08s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/vong_doi.py` (mới):

```python
"""Vòng đời MỘT tiến trình con có hạn hữu hạn (lát P1, dot6-C02/Q02) — primitive DUY NHẤT cho mọi chỗ spawn rồi
chờ/giết: lệnh kiểm (`chay_lenh`), quota app-server, CLI của phiếu, dò danh tính và hạn tổng harness (3C-B).

- `khoi_chay` LUÔN đặt `start_new_session`: nhóm riêng, KHÔNG terminal điều khiển → `sudo` không có tty để cấp pty
  (theo man sudoers, `use_pty` chỉ áp khi sudo chạy trong terminal — G3 đo trên macOS thật).
- `cho` chụp cây mỗi `CHU_KY_CHUP` giây khi gốc còn sống: con/cháu (kể cả nhóm/phiên mới do sudo/pty hay do lệnh tự
  setsid) được ghi nhận TRƯỚC khi cha thoát và mất liên kết ppid. Nhóm đã biết chỉ giữ nhóm còn thành viên trong ảnh
  chụp thành công gần nhất — số nhóm đã chết không bị dùng lại khi PID quay vòng.
- `thu_hoi` không bao giờ chờ vô hạn: SIGTERM mọi nhóm còn sống của cây, chờ `cho_term`, SIGKILL nhóm còn sống, chờ
  `cho_cuoi`; mỗi pha gửi qua `kill(pgid, sig)` của người gọi (principal khác user → `sudo -n … /bin/kill`, có hạn
  tuyệt đối `lenh_ngan`) và thôi gửi khi pha đó quá `han_gui`. True CHỈ khi gốc đã được gặt VÀ ảnh chụp sau cùng không
  còn ai trong cây. Ca "treo sau SIGKILL" (gốc là `sudo` root không nhận tín hiệu của ta, tiến trình kẹt trong nhân):
  hết `cho_cuoi` → False, người gọi giữ cổng đóng — không `wait()` trần ở bất kỳ đâu.
- Chỉ gửi cho nhóm THẤY CÒN SỐNG trong ảnh chụp thành công ≤ 2 s trước (cũ hơn → chỉ nhóm gốc) và nhóm của gốc khi
  gốc chưa gặt (PID chưa gặt không bị tái dùng). Không nhóm 0/1, nhóm của tiến trình quản lý, không theo username.
Cận trên của `thu_hoi`: cho_term + cho_cuoi + 2 × (han_gui + một lần `kill`) + 3 lần `ps` (mỗi lần ≤ 5 s)."""
import math
import os
import signal
import subprocess
import time
from collections.abc import Callable

from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he

Kill = Callable[[int, int], None]
LOI_GUI = (OSError, subprocess.SubprocessError)
CHU_KY_CHUP = 1.0


class LoiThuHoi(RuntimeError):
    """Không xác nhận được cây tiến trình đã hết — kết quả không được công nhận, cổng giữ đóng."""


def kill_cuc_bo(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass


class Nhom:
    def __init__(self, p: subprocess.Popen, *, kill: Kill, chup: Callable[[], list[TienTrinh]] = chup_he):
        self.p, self.kill, self.chup = p, kill, chup
        self.nhom_biet: set[int] = {p.pid}
        self.lan_dung = time.monotonic()                                # lần chụp thành công gần nhất
        self.lan_chup = time.monotonic() - CHU_KY_CHUP + 0.2          # lần chụp đầu sau 0,2 s

    def cho(self, giay: float) -> int | None:
        if not math.isfinite(giay):
            raise ValueError("hạn chờ phải hữu hạn")
        het = time.monotonic() + max(0.0, giay)
        while True:
            try:
                return self.p.wait(timeout=max(0.0, min(het, self.lan_chup + CHU_KY_CHUP) - time.monotonic()))
            except subprocess.TimeoutExpired:
                if time.monotonic() >= self.lan_chup + CHU_KY_CHUP:
                    self.cay()
                if time.monotonic() >= het:
                    return None

    def cay(self) -> list[TienTrinh] | None:
        """Cây hiện tại; None khi `ps` lỗi (không xác nhận được gì, giữ nhóm đã biết)."""
        self.lan_chup = time.monotonic()
        try:
            ds = self.chup()
        except (OSError, subprocess.SubprocessError, ValueError):
            return None
        song, self.lan_dung = self.p.poll() is None, time.monotonic()
        con = cay(ds, self.p.pid if song else None, self.nhom_biet)
        self.nhom_biet = {t.pgid for t in con} | ({self.p.pid} if song else set())
        return con

    def _gui(self, sig: int, han: float) -> None:
        moi = time.monotonic() - self.lan_dung <= 2 * CHU_KY_CHUP
        nhom = (self.nhom_biet if moi else set()) | ({self.p.pid} if self.p.poll() is None else set())
        for g in sorted(nhom - {0, 1, os.getpgrp()}):
            if time.monotonic() >= han:
                return
            try:
                self.kill(g, sig)
            except LOI_GUI:
                pass

    def _cho_het(self, giay: float) -> list[TienTrinh] | None:
        het = time.monotonic() + giay
        try:
            self.p.wait(timeout=giay)
        except subprocess.TimeoutExpired:
            pass
        while True:
            con = self.cay()
            if (con == [] and self.p.poll() is not None) or time.monotonic() >= het:
                return con
            time.sleep(0.05)

    def thu_hoi(self, *, cho_term: float = 2.0, cho_cuoi: float = 2.0, han_gui: float = 10.0) -> bool:
        con = self.cay()
        for sig, cho in ((signal.SIGTERM, cho_term), (signal.SIGKILL, cho_cuoi)):
            if con == [] and self.p.poll() is not None:
                return True
            self._gui(sig, time.monotonic() + han_gui)
            con = self._cho_het(cho)
        return con == [] and self.p.poll() is not None


def khoi_chay(argv: list[str], *, kill: Kill, popen: Callable = subprocess.Popen,
              chup: Callable[[], list[TienTrinh]] = chup_he, **kw) -> Nhom:
    kw["start_new_session"] = True
    return Nhom(popen(argv, **kw), kill=kill, chup=chup)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_vong_doi.py tests/test_vong_doi_ps.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2261 tests collected in 3.24s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_vong_doi.py tests/test_vong_doi_ps.py tram/kiem/vong_doi.py
git commit -m "feat(kiem): primitive vòng đời tiến trình có hạn, thu hồi cả cây (P1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: Lệnh kiểm và kill của principal đi qua P1 (P1-c)

**Đợt:** 3 · **Song song với:** Task 4, 6 (khác file) · **Phải sau:** Task 2. `chay_mot_lenh` dùng `khoi_chay`/`thu_hoi` — bỏ `_ket_thuc` có `p.wait()` trần (dot6-C02); thêm `KetQuaLenh.da_thu_hoi`; chưa xác nhận thu hồi → "fail". `Principal.kill_nhom` dùng `chay_ngan`. `_kill_nhom` thành bí danh của `vong_doi.kill_cuc_bo` (một định nghĩa; giữ tên cho import của 3c/4a). Lỗi khởi chạy chỉ ghi tên loại lỗi. Lệnh kiểm phía thợ (`kiem_sau_xong`) gặp `da_thu_hoi=False` → `LoiThuHoi` (dừng khe). Đổi test cũ `test_lenh_kiem_kill_qua_ham_cua_principal`: lệnh con bỏ qua SIGTERM để vẫn khẳng định [TERM, KILL] — primitive mới không gửi KILL cho nhóm đã chết sau TERM. Hạn chờ không hữu hạn bị từ chối trước khi spawn. Test P1 của `chay_mot_lenh` ở file mới `test_chay_lenh_p1.py` (file cũ không đổi).

**Files:**
- Create: `tests/test_chay_lenh_p1.py`
- Modify: `tests/test_lenh_tho.py`
- Modify: `tests/test_principal.py`
- Modify: `tram/kiem/chay_lenh.py`
- Modify: `tram/kiem/lenh_tho.py`
- Modify: `tram/tho/principal.py`

**Interfaces:**
- Consumes: Task 1 `chay_ngan`; Task 2 `khoi_chay`, `LoiThuHoi`.
- Produces: `KetQuaLenh(..., het_gio=False, da_thu_hoi=True)`; `chay_mot_lenh(..., kill=_kill_nhom, khoi=khoi_chay)`; `_kill_nhom` GIỮ tên (= `vong_doi.kill_cuc_bo`); `Principal.kill_nhom` có hạn 5 s.

- [ ] **Step 1: Viết test thất bại**

`tests/test_chay_lenh_p1.py` (mới):

```python
"""`chay_mot_lenh` trên primitive P1: chưa xác nhận thu hồi → "fail"; gốc treo sau SIGKILL vẫn trả về có hạn; hạn chờ
phải hữu hạn. Popen/ps/kill GIẢ — không sudo thật."""
import os
import time

import pytest

from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem


def _chay(tmp_path, argv, **kw):
    kw.setdefault("thoi_gian_cho", 20)
    return chay_mot_lenh("lệnh x", argv, cwd=tmp_path, env=moi_truong_kiem(os.environ),
                         log=tmp_path / "log/kiem/g-1-1.log", boc=lambda a: a, **kw)


class _NhomGia:
    """Lệnh xong mã 0 nhưng cây không xác nhận thu hồi được (vd. sudo root còn sống)."""
    p = type("P", (), {"returncode": 0})()

    def cho(self, giay):
        return 0

    def thu_hoi(self, **kw):
        return False


def test_khong_xac_nhan_thu_hoi_thi_fail(tmp_path):
    kq = _chay(tmp_path, ["x"], khoi=lambda argv, **kw: _NhomGia())
    assert kq.ket_qua == "fail" and kq.ma_thoat == 0 and kq.da_thu_hoi is False
    assert "KHÔNG xác nhận" in kq.tom_tat


def test_goc_treo_sau_sigkill_van_tra_ve_co_han(tmp_path):
    from test_vong_doi import SUDO, PopenGia
    from tram.kiem.vong_doi import khoi_chay

    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: PopenGia(), chup=lambda: [SUDO], **kw)

    def tu_choi(g, s):
        raise PermissionError
    t0 = time.monotonic()
    kq = _chay(tmp_path, ["sudo", "x"], thoi_gian_cho=0.2, cho_kill=0.2, kill=tu_choi, khoi=khoi)
    assert time.monotonic() - t0 < 5 and kq.het_gio and kq.ket_qua == "fail" and kq.da_thu_hoi is False



def test_han_khong_huu_han_bi_tu_choi_truoc_khi_chay(tmp_path):
    goi = []
    with pytest.raises(ValueError):
        _chay(tmp_path, ["x"], thoi_gian_cho=float("inf"), khoi=lambda *a, **k: goi.append(1))
    assert goi == []
```

`tests/test_lenh_tho.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_lenh_tho.py b/tests/test_lenh_tho.py
index d164f04..5fece0b 100644
--- a/tests/test_lenh_tho.py
+++ b/tests/test_lenh_tho.py
@@ -98,3 +98,12 @@ def test_worktree_ban_thi_tu_choi(wt, tmp_path):
     (wt / "src/a.txt").write_text("chưa commit")
     with pytest.raises(ValueError):
         _kiem(wt, phieu(), ban_giao(), tmp_path)
+
+
+def test_lenh_kiem_khong_xac_nhan_thu_hoi_thi_dung_khe(wt, tmp_path, monkeypatch):
+    from tram.kiem.chay_lenh import KetQuaLenh
+    from tram.kiem.vong_doi import LoiThuHoi
+    monkeypatch.setattr("tram.kiem.lenh_tho.chay_mot_lenh",
+                        lambda lenh, argv, **kw: KetQuaLenh(lenh, "fail", "", "sha256:0", 0, False, False))
+    with pytest.raises(LoiThuHoi, match="dừng khe"):
+        _kiem(wt, phieu(), ban_giao(), tmp_path)
```

`tests/test_principal.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_principal.py b/tests/test_principal.py
index 0e925de..74c6684 100644
--- a/tests/test_principal.py
+++ b/tests/test_principal.py
@@ -50,9 +50,10 @@ def test_ho_so_tu_choi_dau_vao_nguy_hiem(cam, cong):
 
 def test_principal_kill_nhom_chay_kill_duoi_quyen_principal(monkeypatch):
     goi = []
-    monkeypatch.setattr("tram.tho.principal.subprocess.run", lambda argv, **kw: goi.append(argv))
+    monkeypatch.setattr("tram.tho.principal.chay_ngan", lambda argv, **kw: goi.append((argv, kw)))
     doc_principal("user:tram-k-b-claude-1").kill_nhom(4321, signal.SIGTERM)
-    assert goi == [["/usr/bin/sudo", "-n", "-u", "tram-k-b-claude-1", "/bin/kill", "-s", "TERM", "--", "-4321"]]
+    assert goi == [(["/usr/bin/sudo", "-n", "-u", "tram-k-b-claude-1", "/bin/kill", "-s", "TERM", "--", "-4321"],
+                    {"timeout": 5})]
 
 
 def test_lenh_kiem_kill_qua_ham_cua_principal(tmp_path):
@@ -68,7 +69,8 @@ def test_lenh_kiem_kill_qua_ham_cua_principal(tmp_path):
             os.killpg(pgid, sig)
         except ProcessLookupError:
             pass
-    kq = chay_mot_lenh("ngu", [sys.executable, "-c", "import time; time.sleep(30)"], cwd=tmp_path,
+    ma = "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"
+    kq = chay_mot_lenh("ngu", [sys.executable, "-c", ma], cwd=tmp_path,
                        env=dict(os.environ), log=tmp_path / "l.log", thoi_gian_cho=0.3, boc=lambda a: a, cho_kill=1,
                        kill=kill)
     assert kq.het_gio and kq.ket_qua == "fail" and da[:2] == [signal.SIGTERM, signal.SIGKILL]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_lenh.py tests/test_chay_lenh_p1.py tests/test_principal.py tests/test_lenh_tho.py`

Kết quả THẬT trên bản sao (trích):

```text
E       TypeError: chay_mot_lenh() got an unexpected keyword argument 'khoi'
E       TypeError: chay_mot_lenh() got an unexpected keyword argument 'khoi'
E       TypeError: chay_mot_lenh() got an unexpected keyword argument 'khoi'
E           AttributeError: module 'tram.tho.principal' has no attribute 'chay_ngan'
E           AttributeError: 'module' object at tram.tho.principal has no attribute 'chay_ngan'
E   TypeError: KetQuaLenh.__init__() takes from 6 to 7 positional arguments but 8 were given
FAILED tests/test_chay_lenh_p1.py::test_khong_xac_nhan_thu_hoi_thi_fail - Typ...
FAILED tests/test_chay_lenh_p1.py::test_goc_treo_sau_sigkill_van_tra_ve_co_han
FAILED tests/test_chay_lenh_p1.py::test_han_khong_huu_han_bi_tu_choi_truoc_khi_chay
FAILED tests/test_principal.py::test_principal_kill_nhom_chay_kill_duoi_quyen_principal
FAILED tests/test_lenh_tho.py::test_lenh_kiem_khong_xac_nhan_thu_hoi_thi_dung_khe
5 failed, 30 passed in 4.57s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/chay_lenh.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/kiem/chay_lenh.py b/tram/kiem/chay_lenh.py
index 125d728..a3443e6 100644
--- a/tram/kiem/chay_lenh.py
+++ b/tram/kiem/chay_lenh.py
@@ -1,16 +1,19 @@
 """Chạy MỘT lệnh kiểm (spec 3 §7.5 bước 2, spec 4 §6.2 bước 4): danh sách đối số, KHÔNG qua shell, nhóm tiến trình
-riêng, có timeout; quá hạn → SIGTERM cả nhóm, chờ, SIGKILL; xong cũng kill phần còn lại của nhóm (test sinh tiến
-trình con giữ file). `boc` BẮT BUỘC: người gọi quyết principal chạy lệnh (thợ: principal thực thi của khe; trạm:
-`tram-kiem`) — chốt sau spike S6; mã này không bao giờ tự chọn chạy dưới quyền của chính nó."""
+riêng, có timeout; quá hạn hay xong đều thu hồi cả cây qua `vong_doi` (lát P1 — mọi lần chờ có hạn; không xác nhận
+được đã thu hồi → `da_thu_hoi=False`, kết quả "fail"). `boc` BẮT BUỘC: người gọi quyết principal chạy lệnh (thợ:
+principal thực thi của khe; trạm: `tram-kiem`) — chốt sau spike S6; mã này không bao giờ tự chọn chạy dưới quyền của
+chính nó."""
 import hashlib
-import os
-import signal
+import math
 import subprocess
 import time
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
 
+from tram.kiem.vong_doi import khoi_chay
+from tram.kiem.vong_doi import kill_cuc_bo as _kill_nhom          # tên cũ — 3c/4a import, một định nghĩa ở P1
+
 BIEN_GIU = ("PATH", "HOME", "LANG", "TMPDIR", "USER")
 
 
@@ -22,6 +25,7 @@ class KetQuaLenh:
     digest_log: str         # "sha256:<hex>" của log
     ma_thoat: int | None
     het_gio: bool = False
+    da_thu_hoi: bool = True
 
     def sang_lenh_kiem(self) -> dict:
         """Dòng `lenh_kiem[]` của khối bàn giao (spec 0+1a §4.3)."""
@@ -37,35 +41,20 @@ def moi_truong_kiem(goc: Mapping[str, str], them: Mapping[str, str] | None = Non
     return env
 
 
-def _kill_nhom(pgid: int, sig: int) -> None:
-    try:
-        os.killpg(pgid, sig)
-    except (ProcessLookupError, PermissionError):
-        pass
-
-
-def _ket_thuc(p: subprocess.Popen, cho_kill: float, kill: Callable[[int, int], None]) -> None:
-    kill(p.pid, signal.SIGTERM)
-    try:
-        p.wait(timeout=cho_kill)
-    except subprocess.TimeoutExpired:
-        pass
-    kill(p.pid, signal.SIGKILL)
-    p.wait()
-
-
-def _ket_qua(lenh: str, log: Path, ma: int | None, het_gio: bool) -> KetQuaLenh:
+def _ket_qua(lenh: str, log: Path, ma: int | None, het_gio: bool, sach: bool = True) -> KetQuaLenh:
     du_lieu = log.read_bytes()
     dong = [d for d in du_lieu.decode("utf-8", "replace").splitlines() if d.strip()]
-    return KetQuaLenh(lenh, "pass" if ma == 0 and not het_gio else "fail", "\n".join(dong[-3:]),
-                      "sha256:" + hashlib.sha256(du_lieu).hexdigest(), ma, het_gio)
+    return KetQuaLenh(lenh, "pass" if ma == 0 and not het_gio and sach else "fail", "\n".join(dong[-3:]),
+                      "sha256:" + hashlib.sha256(du_lieu).hexdigest(), ma, het_gio, sach)
 
 
 def chay_mot_lenh(lenh: str, argv: list[str] | None, *, cwd: Path, env: Mapping[str, str], log: Path,
                   thoi_gian_cho: float, boc: Callable[[list[str]], list[str]], cho_kill: float = 10.0,
-                  kill: Callable[[int, int], None] = _kill_nhom) -> KetQuaLenh:
+                  kill: Callable[[int, int], None] = _kill_nhom, khoi: Callable = khoi_chay) -> KetQuaLenh:
     """`argv` None = lệnh không khớp `lenh_cho_phep` → KHÔNG chạy, coi là fail. `kill(pgid, sig)`: cách kill cả nhóm —
     mặc định cùng user; chạy dưới principal khác user thì truyền `Principal.kill_nhom` (3a-2, chờ S6)."""
+    if not math.isfinite(thoi_gian_cho):
+        raise ValueError("thoi_gian_cho phải hữu hạn")
     log.parent.mkdir(parents=True, exist_ok=True)
     with open(log, "wb") as f:
         if argv is None:
@@ -73,21 +62,20 @@ def chay_mot_lenh(lenh: str, argv: list[str] | None, *, cwd: Path, env: Mapping[
             f.flush()
             return _ket_qua(lenh, log, None, False)
         try:
-            p = subprocess.Popen(boc(argv), cwd=cwd, env=dict(env), stdin=subprocess.DEVNULL, stdout=f,
-                                 stderr=subprocess.STDOUT, start_new_session=True)
+            n = khoi(boc(argv), kill=kill, cwd=cwd, env=dict(env), stdin=subprocess.DEVNULL, stdout=f,
+                     stderr=subprocess.STDOUT)
         except OSError as e:
-            f.write(f"[tram] lỗi khởi chạy: {type(e).__name__}: {e}\n".encode())
+            f.write(f"[tram] lỗi khởi chạy: {type(e).__name__}\n".encode())     # không chép argv/đường dẫn
             f.flush()
             return _ket_qua(lenh, log, None, False)
-        het_gio, bat_dau = False, time.monotonic()
-        try:
-            ma = p.wait(timeout=thoi_gian_cho)
-        except subprocess.TimeoutExpired:
-            het_gio = True
-            _ket_thuc(p, cho_kill, kill)
-            ma = p.returncode
-        kill(p.pid, signal.SIGKILL)                # con cháu còn sống sau khi lệnh chính thoát
+        bat_dau = time.monotonic()
+        ma = n.cho(thoi_gian_cho)
+        het_gio = ma is None
+        sach = n.thu_hoi(cho_term=cho_kill)        # quá hạn, hoặc con cháu còn sống sau khi lệnh chính thoát
+        ma = n.p.returncode if het_gio else ma
         if het_gio:
             f.write(f"\n[tram] quá hạn {thoi_gian_cho:g} s (đã chạy {time.monotonic() - bat_dau:.1f} s)"
                     " — đã kill cả nhóm tiến trình\n".encode())
-    return _ket_qua(lenh, log, ma, het_gio)
+        if not sach:
+            f.write("\n[tram] KHÔNG xác nhận được đã thu hồi cả cây tiến trình — không công nhận kết quả\n".encode())
+    return _ket_qua(lenh, log, ma, het_gio, sach)
```

`tram/kiem/lenh_tho.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/kiem/lenh_tho.py b/tram/kiem/lenh_tho.py
index 91b7b6c..db7e68e 100644
--- a/tram/kiem/lenh_tho.py
+++ b/tram/kiem/lenh_tho.py
@@ -14,6 +14,7 @@ from tram.ban_giao.schema import BanGiao, kiem_ban_giao
 from tram.cau_hinh.lenh import khop_bat_ky
 from tram.kiem.chay_lenh import chay_mot_lenh
 from tram.kiem.diff import diff_cham_cam
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 
 GIT = ("git", "-c", "core.hooksPath=/dev/null")
@@ -49,6 +50,8 @@ def kiem_sau_xong(wt: Path, phieu: Phieu, ban_giao: BanGiao, *, thu_muc_log: Pat
             kq = chay_mot_lenh(lenh, argv, cwd=wt, env=env, boc=boc, thoi_gian_cho=thoi_gian_cho,
                                log=thu_muc_log / f"{phieu.giao_id}-{phieu.luot}-{i}.log",
                                **({"kill": kill} if kill else {}))
+            if not kq.da_thu_hoi:           # P1: tiến trình lệnh kiểm có thể còn sống dưới principal → dừng khe
+                raise LoiThuHoi("Không dọn được nhóm lệnh kiểm; dừng khe để kiểm principal")
             ket_qua.append(kq.sang_lenh_kiem())
     bg = BanGiao.model_validate({**ban_giao.model_dump(), "lenh_kiem": ket_qua, "luot": phieu.luot,
                                  "commit": commit, "vuong_mac": vuong})
```

`tram/tho/principal.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/principal.py b/tram/tho/principal.py
index 8b0cc0b..0e8eed9 100644
--- a/tram/tho/principal.py
+++ b/tram/tho/principal.py
@@ -6,11 +6,12 @@ Cả hai chạy qua `sudo -n` (không hỏi mật khẩu; sudoers do `tram chu c
 giữ các biến trong `BIEN_GIU` — giá trị biến KHÔNG BAO GIỜ nằm trong argv (`ps` của user khác thấy argv)."""
 import re
 import signal
-import subprocess
 from dataclasses import dataclass, replace
 from pathlib import Path
 from typing import Literal
 
+from tram.kiem.lenh_ngan import chay_ngan
+
 SUDO = "/usr/bin/sudo"
 SANDBOX_EXEC = "/usr/bin/sandbox-exec"
 BIEN_GIU = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "TRAM_MA_GIAO", "TRAM_NHO_URL",
@@ -45,8 +46,8 @@ class Principal:
     def kill_nhom(self, pgid: int, sig: int) -> None:
         """Gửi tín hiệu cho cả nhóm tiến trình DƯỚI QUYỀN principal (tiến trình quản lý khác user không kill được
         con cháu của principal). Cách sudo xếp nhóm tiến trình (`use_pty`) — CHỜ S6."""
-        subprocess.run([SUDO, "-n", "-u", self.user, "/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
-                        "--", f"-{pgid}"], capture_output=True, timeout=20)
+        chay_ngan([SUDO, "-n", "-u", self.user, "/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
+                   "--", f"-{pgid}"], timeout=5)                     # P1: có hạn tuyệt đối, không wait() trần
 
 
 def doc_principal(chuoi: str | None) -> Principal:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_lenh.py tests/test_chay_lenh_p1.py tests/test_principal.py tests/test_lenh_tho.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2265 tests collected in 3.23s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chay_lenh_p1.py tests/test_lenh_tho.py tests/test_principal.py tram/kiem/chay_lenh.py tram/kiem/lenh_tho.py tram/tho/principal.py
git commit -m "fix(kiem): lệnh kiểm và kill principal có hạn, báo chưa thu hồi (P1, dot6-C02)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: Adapter app-server — đọc theo hạn tổng, không Timer, lỗi cố định (P1-d)

**Đợt:** 3 · **Song song với:** Task 3, 6. Bỏ `threading.Timer` + `_giet` (`p.wait()` trần trong luồng hẹn giờ). Đọc stdout bằng `select` theo một hạn; dòng > 1 MiB bị chặn; mọi đường ra `thu_hoi` qua `kill` của người gọi; chưa xác nhận → `LoiThuHoi`. Thông báo lỗi chỉ mang mã số JSON-RPC (dot6-Q06). App-server giả thêm chế độ `dai`, `lo`; `GHI` thành tuỳ chọn. Đổi test cũ `test_loi_hoac_dong_som[loi]`: thông báo không còn chép chữ của server.

**Files:**
- Modify: `tests/du_lieu/codex/app_server_gia.py`
- Modify: `tests/test_codex_app_server.py`
- Modify: `tram/chay_cli/codex/app_server.py`

**Interfaces:**
- Consumes: Task 2 `Kill`, `LoiThuHoi`, `khoi_chay`, `kill_cuc_bo`.
- Produces: `hoi_app_server(argv, *, env, thoi_gian_cho=THOI_GIAN_CHO, kill=kill_cuc_bo, khoi=khoi_chay) -> dict`; `THOI_GIAN_CHO = 10.0`, `DONG_TOI_DA`. `doc_han_muc_ranh` CHƯA đổi (Q1).

- [ ] **Step 1: Viết test thất bại**

`tests/du_lieu/codex/app_server_gia.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/du_lieu/codex/app_server_gia.py b/tests/du_lieu/codex/app_server_gia.py
index 8facb34..9fa404b 100644
--- a/tests/du_lieu/codex/app_server_gia.py
+++ b/tests/du_lieu/codex/app_server_gia.py
@@ -1,6 +1,7 @@
 """`codex app-server` GIẢ — CHỈ DÙNG TRONG TEST (chạy bằng sys.executable). Mỗi dòng stdin một JSON; ghi lại mọi
-tin nhận được + CODEX_HOME vào file $GHI. CHE_DO: ok | loi | treo | dong.
-Hình dạng tin theo hiểu biết hiện tại — chờ spike S5."""
+tin nhận được + CODEX_HOME vào file $GHI (không có $GHI thì không ghi). CHE_DO: ok | loi | treo | dong | dai (một
+dòng 2 MiB không xuống dòng) | lo (lỗi mang nguyên văn $LO, kèm in $LO ra stderr). Hình dạng tin theo hiểu biết hiện
+tại — chờ spike S5."""
 import json
 import os
 import sys
@@ -8,7 +9,7 @@ import time
 from pathlib import Path
 
 MAU = json.loads((Path(__file__).parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))
-che_do, ghi = os.environ.get("CHE_DO", "ok"), Path(os.environ["GHI"])
+che_do, ghi = os.environ.get("CHE_DO", "ok"), Path(os.environ.get("GHI", os.devnull))
 nhan = [{"CODEX_HOME": os.environ.get("CODEX_HOME")}]
 
 
@@ -28,6 +29,14 @@ for dong in sys.stdin:
         tra({"id": 0, "result": {"userAgent": "gia/0"}})
         if che_do == "treo":
             time.sleep(60)
+        if che_do == "dai":
+            sys.stdout.write("x" * (2 << 20))
+            sys.stdout.flush()
+            time.sleep(60)
     elif tin.get("method") == "account/rateLimits/read":
-        tra({"id": 1, "error": {"code": -32600, "message": "chưa đăng nhập"}} if che_do == "loi"
-            else {"id": 1, "result": MAU["plus"]})
+        if che_do == "lo":
+            print(os.environ.get("LO", ""), file=sys.stderr, flush=True)
+            tra({"id": 1, "error": {"code": 401, "message": os.environ.get("LO", "")}})
+        else:
+            tra({"id": 1, "error": {"code": -32600, "message": "chưa đăng nhập"}} if che_do == "loi"
+                else {"id": 1, "result": MAU["plus"]})
```

`tests/test_codex_app_server.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_codex_app_server.py b/tests/test_codex_app_server.py
index fb9ac93..86e2e8d 100644
--- a/tests/test_codex_app_server.py
+++ b/tests/test_codex_app_server.py
@@ -27,7 +27,7 @@ def test_bat_tay_roi_hoi_rate_limits(tmp_path):
     assert nhan[1]["params"]["clientInfo"]["name"] == "tram"
 
 
-@pytest.mark.parametrize("che_do, mau", [("loi", "chưa đăng nhập"), ("dong", "đóng trước")])
+@pytest.mark.parametrize("che_do, mau", [("loi", r"trả lỗi \(mã -32600\)"), ("dong", "đóng trước")])
 def test_loi_hoac_dong_som(tmp_path, che_do, mau):
     with pytest.raises(LoiAppServer, match=mau):
         _hoi(tmp_path, che_do)
@@ -55,3 +55,47 @@ def test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu(tmp_path, monkeypatc
         raise LoiAppServer("x")
     assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=hong) is None
     assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=lambda a, env: {}) is None
+
+
+def test_treo_thu_hoi_qua_kill_nguoi_goi_khong_de_luong_nen(tmp_path):
+    import threading
+    from tram.kiem.vong_doi import kill_cuc_bo
+    gui, truoc = [], threading.active_count()
+
+    def kill(g, sig):
+        gui.append((g, sig))
+        kill_cuc_bo(g, sig)
+    with pytest.raises(LoiAppServer, match="không trả lời"):
+        _hoi(tmp_path, "treo", thoi_gian_cho=0.5, kill=kill)
+    assert gui and threading.active_count() == truoc
+
+
+def test_dong_qua_dai_bi_chan(tmp_path):
+    with pytest.raises(LoiAppServer, match="quá dài"):
+        _hoi(tmp_path, "dai", thoi_gian_cho=5)
+
+
+def test_khong_thu_hoi_duoc_thi_nem_loi_thu_hoi(tmp_path):
+    import os
+    import signal
+    from tram.kiem.vong_doi import LoiThuHoi
+    pid = []
+
+    def khoi(argv, **kw):
+        from tram.kiem.vong_doi import khoi_chay
+        n = khoi_chay(argv, **kw)
+        pid.append(n.p.pid)
+        return n
+    try:
+        with pytest.raises(LoiThuHoi):
+            _hoi(tmp_path, "treo", thoi_gian_cho=0.3, kill=lambda g, s: None, khoi=khoi)
+    finally:
+        os.killpg(pid[0], signal.SIGKILL)
+
+
+def test_loi_khong_chep_chu_cua_app_server(tmp_path, capfd):
+    bi_mat = "SENTINEL-APP-SERVER-7f3a"
+    env = {"CHE_DO": "lo", "LO": bi_mat, "CODEX_HOME": str(tmp_path / "khe")}
+    with pytest.raises(LoiAppServer) as e:
+        hoi_app_server([sys.executable, str(GIA)], env=env)
+    assert "mã 401" in str(e.value) and bi_mat not in str(e.value) and bi_mat not in "".join(capfd.readouterr())
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_codex_app_server.py`

Kết quả THẬT trên bản sao (trích):

```text
E                   tram.chay_cli.codex.app_server.LoiAppServer: app-server trả lỗi: chưa đăng nhập
E       AssertionError: Regex pattern did not match.
E        Regex: 'trả lỗi \\(mã -32600\\)'
E        Input: 'app-server trả lỗi: chưa đăng nhập'
E       TypeError: hoi_app_server() got an unexpected keyword argument 'kill'
E               tram.chay_cli.codex.app_server.LoiAppServer: app-server không trả lời trong 5 giây
E       AssertionError: Regex pattern did not match.
E        Regex: 'quá dài'
E        Input: 'app-server không trả lời trong 5 giây'
E       TypeError: hoi_app_server() got an unexpected keyword argument 'kill'
E           IndexError: list index out of range
E       AssertionError: assert ('mã 401' in 'app-server trả lỗi: SENTINEL-APP-SERVER-7f3a')
E        +  where 'app-server trả lỗi: SENTINEL-APP-SERVER-7f3a' = str(LoiAppServer('app-server trả lỗi: SENTINEL-APP-SERVER-7f3a'))
E        +    where LoiAppServer('app-server trả lỗi: SENTINEL-APP-SERVER-7f3a') = <ExceptionInfo LoiAppServer('app-server trả lỗi: SENTINEL-APP-SERVER-7f3a') tblen=4>.value
5 failed, 4 passed in 6.28s
```

- [ ] **Step 3: Viết mã**

`tram/chay_cli/codex/app_server.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/codex/app_server.py b/tram/chay_cli/codex/app_server.py
index b75380a..9970057 100644
--- a/tram/chay_cli/codex/app_server.py
+++ b/tram/chay_cli/codex/app_server.py
@@ -2,21 +2,27 @@
 
 Giao thức theo tài liệu app-server (JSON-RPC qua stdio, mỗi dòng một JSON, không trường `jsonrpc`): `initialize` (id 0)
 → chờ trả lời → thông báo `initialized` → `account/rateLimits/read` (id 1). CHƯA chạy thật — chờ spike S5 (dưới launchd,
-`CODEX_HOME` riêng của khe). Tiến trình chạy trong nhóm riêng, quá hạn thì giết cả nhóm. Môi trường tối thiểu: không
-mang token máy hay biến `TRAM_*`."""
+`CODEX_HOME` riêng của khe). Lát P1: tiến trình đi qua `vong_doi` — đọc stdout bằng `select` theo MỘT hạn tổng (không
+Timer/luồng nền), chụp cây mỗi giây trong lúc chờ, xong hay lỗi đều `thu_hoi` cả cây qua `kill` của người gọi; không xác
+nhận thu hồi → `LoiThuHoi`. Cận trên một lần hỏi: 10 s (+ ≤ 5 s một lần `ps` lố hạn) + `thu_hoi(1, 3, 2)` ≤ 1 + 3 +
+2 × (2 + 5) + 3 × 5 = 33 s → 48 s.
+Thông báo lỗi cố định: không chép argv, stderr hay chữ do app-server gửi về (dot6-Q06)."""
 import json
 import os
-import signal
+import select
 import subprocess
-import threading
+import time
 from datetime import datetime
 from pathlib import Path
 
 from tram.chay_cli.codex.han_muc import han_muc_app_server
 from tram.han_muc.mo_hinh import HanMuc
+from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, LoiThuHoi, khoi_chay, kill_cuc_bo
 
 PHUONG_THUC = "account/rateLimits/read"
 CHU_KY_RANH_GIAY = 300
+THOI_GIAN_CHO = 10.0
+DONG_TOI_DA = 1 << 20
 BIEN_GIU = ("PATH", "HOME", "LANG", "USER", "TMPDIR")
 
 
@@ -24,13 +30,41 @@ class LoiAppServer(RuntimeError):
     pass
 
 
+class _HetGio(Exception):
+    pass
+
+
 def _gui(p, tin: dict) -> None:
-    p.stdin.write(json.dumps(tin) + "\n")
+    p.stdin.write((json.dumps(tin) + "\n").encode())
     p.stdin.flush()
 
 
-def _cho(p, ma: int) -> dict:
-    for dong in p.stdout:
+def _dong(n, han: float, dem: bytearray) -> bytes | None:
+    """Một dòng stdout trước `han` (monotonic); None khi EOF. Chụp cây mỗi `CHU_KY_CHUP` giây khi chưa có dữ liệu."""
+    fd = n.p.stdout.fileno()
+    while b"\n" not in dem:
+        con = han - time.monotonic()
+        if con <= 0:
+            raise _HetGio
+        if not select.select([fd], [], [], min(con, CHU_KY_CHUP))[0]:
+            n.cay()
+            continue
+        khuc = os.read(fd, 65536)
+        if not khuc:
+            ra = bytes(dem)
+            dem.clear()
+            return ra or None
+        dem += khuc
+        if len(dem) > DONG_TOI_DA:
+            raise LoiAppServer("app-server gửi dòng quá dài")
+    i = dem.index(b"\n") + 1
+    ra = bytes(dem[:i])
+    del dem[:i]
+    return ra
+
+
+def _cho(n, ma: int, han: float, dem: bytearray) -> dict:
+    while (dong := _dong(n, han, dem)) is not None:
         try:
             tin = json.loads(dong)
         except ValueError:
@@ -38,45 +72,35 @@ def _cho(p, ma: int) -> dict:
         if isinstance(tin, dict) and tin.get("id") == ma:
             if "error" in tin:
                 loi = tin["error"] if isinstance(tin["error"], dict) else {}
-                raise LoiAppServer(f"app-server trả lỗi: {str(loi.get('message', ''))[:120]}")
+                so = loi.get("code") if type(loi.get("code")) is int else "?"
+                raise LoiAppServer(f"app-server trả lỗi (mã {so})")
             return tin["result"] if isinstance(tin.get("result"), dict) else {}
     raise LoiAppServer("app-server đóng trước khi trả lời")
 
 
-def _giet(p) -> None:
-    if p.poll() is not None:
-        return
-    try:
-        os.killpg(p.pid, signal.SIGTERM)
-        p.wait(2)
-    except subprocess.TimeoutExpired:
-        os.killpg(p.pid, signal.SIGKILL)
-        p.wait()
-    except ProcessLookupError:
-        pass
-
-
-def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float = 20.0,
-                   popen=subprocess.Popen) -> dict:
-    p = popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, text=True,
-              start_new_session=True)
-    qua_gio = threading.Event()
-    hen = threading.Timer(thoi_gian_cho, lambda: (qua_gio.set(), _giet(p)))
-    hen.start()
+def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float = THOI_GIAN_CHO,
+                   kill: Kill = kill_cuc_bo, khoi=khoi_chay) -> dict:
+    n = khoi(argv, kill=kill, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
+    han, dem = time.monotonic() + thoi_gian_cho, bytearray()
     try:
-        _gui(p, {"method": "initialize", "id": 0, "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi",
-                                                                             "version": "3b"}}})
-        _cho(p, 0)
-        _gui(p, {"method": "initialized"})
-        _gui(p, {"method": PHUONG_THUC, "id": 1})
-        return _cho(p, 1)
-    except (LoiAppServer, OSError) as e:
-        if qua_gio.is_set():
-            raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
-        raise e if isinstance(e, LoiAppServer) else LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
+        _gui(n.p, {"method": "initialize", "id": 0, "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi",
+                                                                               "version": "3b"}}})
+        _cho(n, 0, han, dem)
+        _gui(n.p, {"method": "initialized"})
+        _gui(n.p, {"method": PHUONG_THUC, "id": 1})
+        return _cho(n, 1, han, dem)
+    except _HetGio:
+        raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
+    except OSError as e:
+        raise LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
     finally:
-        hen.cancel()
-        _giet(p)
+        for f in (n.p.stdin, n.p.stdout):
+            try:
+                f.close()
+            except OSError:
+                pass
+        if not n.thu_hoi(cho_term=1.0, cho_cuoi=3.0, han_gui=2.0):
+            raise LoiThuHoi("không xác nhận thu hồi tiến trình app-server")
 
 
 def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, codex: str = "codex",
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_codex_app_server.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2269 tests collected in 3.24s`.

- [ ] **Step 5: Commit**

```bash
git add tests/du_lieu/codex/app_server_gia.py tests/test_codex_app_server.py tram/chay_cli/codex/app_server.py
git commit -m "fix(codex): app-server đọc theo hạn tổng, thu hồi qua primitive, lỗi cố định (P1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5: CLI của phiếu đi qua P1; không thu hồi được → dừng khe (P1-e)

**Đợt:** 4 · **Song song với:** Task 7, 8, Q1-a · **Phải sau:** Task 2. `ChayClaude`/`ChayCodex` bỏ luồng `_canh` + `p.wait()` trần: `cho_den_dung` chờ thoát hoặc `dung`, rồi `thu_hoi`; lỗi giữa spawn và chờ vẫn thu hồi (chưa xác nhận → `LoiThuHoi` thay lỗi gốc); chưa xác nhận → `LoiThuHoi`. `mot_lan` GIỮ `dang-chay.pid` CHỈ khi `LoiThuHoi` (dọn mồ côi lần khởi động sau còn dữ liệu), lỗi khác vẫn xoá. `chay_phieu` gặp `LoiThuHoi` (kể cả ở lần chạy thứ hai) không `don_phieu` — giữ worktree/phiếu, chỉ gỡ khoá. `VongKhe` bắt `LoiThuHoi` → `hong`: vòng chính và nhịp dừng. Lỗi khởi chạy chỉ ghi tên loại lỗi. `mo_coi.kill_cuc_bo` thành bí danh của `vong_doi.kill_cuc_bo`. Đổi test cũ `test_xong_dem_token_va_log_che_ma_giao`: sau khi CLI thoát sạch không còn tín hiệu nào phải gửi.

**Files:**
- Create: `tests/test_chay_cli_vong_doi.py`
- Modify: `tests/test_codex_chay.py`
- Create: `tests/test_phieu_chay_thu_hoi.py`
- Modify: `tram/chay_cli/claude.py`
- Modify: `tram/chay_cli/codex/chay.py`
- Modify: `tram/kiem/vong_doi.py`
- Modify: `tram/tho/mo_coi.py`
- Modify: `tram/tho/mot_lan.py`
- Modify: `tram/tho/phieu_chay.py`
- Modify: `tram/tho/vong_khe.py`

**Interfaces:**
- Consumes: Task 2 (`khoi_chay`, `LoiThuHoi`), Task 3 (`KetQuaLenh.da_thu_hoi`).
- Produces: `vong_doi.cho_den_dung(n, dung, *, cho_term) -> tuple[int | None, bool]`; `ChayClaude(..., khoi=khoi_chay)`; `VongKhe.hong: bool`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_chay_cli_vong_doi.py` (mới):

```python
"""CLI của phiếu dùng primitive vòng đời P1: `dung` → thu hồi có hạn; không xác nhận thu hồi → dừng khe (RuntimeError),
không treo ở `wait()`. CLI giả là `python` của chính user đang test; `kill` không làm gì = principal bị từ chối."""
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

import pytest

from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.claude import NguonHanMucClaude
from tram.tho.mo_coi import kill_cuc_bo

CLI = str(Path(__file__).parent / "cli_gia.py")
EXEC = str(Path(__file__).parent / "du_lieu" / "codex" / "exec_gia.py")
FIXTURE = str(Path(__file__).parent / "du_lieu" / "codex" / "exec_xong.jsonl")


def _dung_sau(giay: float) -> threading.Event:
    d = threading.Event()
    threading.Timer(giay, d.set).start()
    return d


def _claude(tmp_path, kill):
    (tmp_path / "kb.json").write_text(json.dumps([{"ngu": 60}]))
    env = dict(os.environ, CLI_GIA_KICH_BAN=str(tmp_path / "kb.json"))
    return ChayClaude(lambda a: [sys.executable, CLI], khe_id="B/claude-1", kill=kill, cho_kill=0.3,
                      khi_bat_dau=_PID.append), env, NguonHanMucClaude()


def _codex(tmp_path, kill):
    env = {"FIXTURE": FIXTURE, "GHI": str(tmp_path / "stdin.txt"), "CHE_DO": "treo"}
    return ChayCodex(lambda a: [sys.executable, EXEC], kill=kill, cho_dung_giay=0.3,
                     khi_bat_dau=_PID.append), env, NguonHanMucCodex()


_PID: list[int] = []


@pytest.mark.parametrize("dung_cli", [_claude, _codex])
def test_kill_bi_tu_choi_thi_dung_khe_trong_han(tmp_path, dung_cli):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    r, env, nguon = dung_cli(tmp_path, lambda g, s: None)
    t0 = time.monotonic()
    try:
        with pytest.raises(RuntimeError, match="Không dọn được nhóm CLI"):
            r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
                   dung=_dung_sau(0.3), nguon=nguon)
        assert time.monotonic() - t0 < 10
    finally:
        os.killpg(_PID[0], signal.SIGKILL)


@pytest.mark.parametrize("dung_cli", [_claude, _codex])
def test_dung_thu_hoi_ca_cay_qua_kill_cua_principal(tmp_path, dung_cli):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    gui = []
    r, env, nguon = dung_cli(tmp_path, lambda g, s: gui.append((g, s)) or kill_cuc_bo(g, s))
    kq = r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
                dung=_dung_sau(0.3), nguon=nguon)
    assert kq.bi_dung and (_PID[0], signal.SIGTERM) in gui
    with pytest.raises(ProcessLookupError):
        os.killpg(_PID[0], 0)


def test_loi_giua_spawn_va_cho_van_thu_hoi(tmp_path):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    r, env, nguon = _codex(tmp_path, kill_cuc_bo)

    def hong(pid):
        _PID.append(pid)
        raise OSError("đĩa đầy")
    r.khi_bat_dau = hong
    with pytest.raises(OSError):
        r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
               dung=threading.Event(), nguon=nguon)
    with pytest.raises(ProcessLookupError):
        os.killpg(_PID[0], 0)


def test_cli_khong_thu_hoi_duoc_giu_pid_va_dung_khe(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from tho_chay_gia import dung_may, lay_phieu
    from tram.kiem.vong_doi import LoiThuHoi
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    from tram.tho.vong_khe import VongKhe
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)

    def tao(boc, **kw):
        def chay(argv, **k2):
            kw["khi_bat_dau"](999999)                              # PID không tồn tại trên macOS
            raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
        return SimpleNamespace(chay=chay)
    m.nc.tao_cli = tao
    with pytest.raises(LoiThuHoi):
        chay_mot_lan(pc, m.nc, threading.Event())
    assert json.loads(so.pid.read_text())["pid"] == 999999             # dọn mồ côi lần khởi động sau còn dữ liệu
    vk, tat = VongKhe(m.nc, k), threading.Event()
    vk.khoi_dong, vk.nhip, vk.phieu_moi, vk.da_xac_nhan = (lambda: None), (lambda: None), tt, True
    monkeypatch.setattr("tram.tho.vong_khe.chay_phieu", lambda *a: (_ for _ in ()).throw(LoiThuHoi("x")))
    hen = threading.Timer(10, tat.set)
    hen.start()
    vk.chay(tat)
    hen.cancel()
    assert vk.hong and not tat.is_set()
```

`tests/test_codex_chay.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tests/test_codex_chay.py b/tests/test_codex_chay.py
index 7d4ff2c..d9c8860 100644
--- a/tests/test_codex_chay.py
+++ b/tests/test_codex_chay.py
@@ -29,7 +29,7 @@ def test_xong_dem_token_va_log_che_ma_giao(tmp_path):
         kill_cuc_bo(p, sig)
     kq = _chay(tmp_path, "exec_xong.jsonl", boc=lambda a: (boc.append(a) or a),
                khe_id="C/codex-1", khi_bat_dau=pid.append, kill=kill)
-    assert len(boc) == len(pid) == 1 and kills[-1][0] == pid[0]
+    assert len(boc) == len(pid) == 1 and all(g == pid[0] for g, _ in kills)      # chỉ nhóm của CLI, nếu còn sống
     assert isinstance(ChayCodex(), ChayCLI) and ket_thuc_tu(kq) == "xong"
     assert (kq.ma_thoat, kq.co_assistant, kq.het_han_muc, kq.chua_dang_nhap) == (0, True, False, False)
     assert (kq.token_vao, kq.token_cache_doc, kq.token_ra) == (315, 24448, 1122)
```

`tests/test_phieu_chay_thu_hoi.py` (mới):

```python
"""P1 ở tầng phiếu: `LoiThuHoi` ở lần chạy thứ hai không dọn worktree/phiếu (tiến trình có thể còn sống) và nổi lên
cho vòng khe dừng; lỗi khác của CLI (đã thu hồi) không giữ pid cũ. Toàn bộ bằng bản giả — không spawn gì."""
import threading
from types import SimpleNamespace

import pytest

import tram.tho.phieu_chay as pcm
from tram.kiem.vong_doi import LoiThuHoi


def test_loi_thu_hoi_lan_sau_khong_don_phieu(monkeypatch):
    lan, don, khoa = [], [], []

    def mot_vong(pc, nc, vk):
        lan.append(1)
        if len(lan) == 1:
            return None
        raise LoiThuHoi("x")
    monkeypatch.setattr(pcm, "_mot_vong", mot_vong)
    monkeypatch.setattr(pcm, "chuan_bi", lambda *a: SimpleNamespace(wt="/khong-dung", p=SimpleNamespace(giao_id="g")))
    monkeypatch.setattr(pcm, "dat_khoa", lambda *a, **k: True)
    monkeypatch.setattr(pcm, "go_khoa", khoa.append)
    monkeypatch.setattr(pcm, "don_phieu", lambda *a: don.append(1))
    with pytest.raises(LoiThuHoi):
        pcm.chay_phieu(None, SimpleNamespace(k=None, so=None, hop=None), None)
    assert lan == [1, 1] and don == [] and khoa == ["/khong-dung"]


def test_cli_loi_khac_sau_khi_thu_hoi_thi_xoa_pid(tmp_path, monkeypatch):
    from tho_chay_gia import dung_may, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)

    def tao(boc, **kw):
        def chay(argv, **k2):
            kw["khi_bat_dau"](999999)
            raise OSError("đọc log hỏng")
        return SimpleNamespace(chay=chay)
    m.nc.tao_cli = tao
    with pytest.raises(OSError):
        chay_mot_lan(pc, m.nc, threading.Event())
    assert not so.pid.exists()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_cli_vong_doi.py tests/test_codex_chay.py tests/test_phieu_chay_thu_hoi.py`

Kết quả THẬT trên bản sao (trích):

```text
E           Failed: DID NOT RAISE <class 'RuntimeError'>
E           ProcessLookupError: [Errno 3] No such process
E           Failed: DID NOT RAISE <class 'RuntimeError'>
E           ProcessLookupError: [Errno 3] No such process
E       Failed: DID NOT RAISE <class 'ProcessLookupError'>
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
mode = 'r', buffering = -1, encoding = 'locale', errors = None, newline = None
             errors=None, newline=None):
>       return io.open(self, mode, buffering, encoding, errors, newline)
E       FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/9x/sm85c3qn3dbgfx_23q1lnvr40000gn/T/pytest-of-hungle/pytest-744/test_cli_khong_thu_hoi_duoc_gi0/worker/tho-home/tho/B/claude-1/dang-chay.pid'
E       assert ([1, 1] == [1, 1]
E         
E         Use -v to get more diff and [1] == []
E         
5 failed, 7 passed in 93.95s (0:01:33)
```

- [ ] **Step 3: Viết mã**

`tram/chay_cli/claude.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/claude.py b/tram/chay_cli/claude.py
index dd48bf0..e3c1e56 100644
--- a/tram/chay_cli/claude.py
+++ b/tram/chay_cli/claude.py
@@ -1,11 +1,10 @@
 """Bản THẬT của Protocol `ChayCLI` (3a-1, spec 3 §7.2, §7.8) cho Claude Code — CHỜ SPIKE S2–S4 trước khi chạy thật.
 Một lần chạy = một tiến trình con dưới principal của khe (`boc`), nhóm tiến trình riêng, stdin = gói của lần chạy,
 stdout+stderr che `ma_giao` trước khi ghi vào log `~/.tram/log/chay/<giao_id>-<luot>-<lan>.jsonl` (digest gửi trong
-`chay.xong`) và đọc từng dòng (`DocStream`). `dung` được đặt (dừng cứng/mềm, hết trần thời gian, vượt `token_ra`) →
-SIGTERM cả nhóm, chờ, SIGKILL — qua `kill` của principal (tiến trình quản lý khác user không kill được con cháu của
-principal)."""
+`chay.xong`) và đọc từng dòng (`DocStream`). `dung` được đặt (dừng cứng/mềm, hết trần thời gian, vượt `token_ra`) hay
+CLI thoát → thu hồi cả cây có hạn (`vong_doi`, lát P1) qua `kill` của principal (tiến trình quản lý khác user không kill
+được con cháu của principal); không xác nhận thu hồi → `LoiThuHoi`, vòng khe dừng để kiểm principal."""
 import hashlib
-import signal
 import subprocess
 import threading
 import time
@@ -17,16 +16,17 @@ from tram.chay_cli.stream import DocStream
 from tram.phieu.mo_hinh import che_ma_giao
 from tram.han_muc.mo_hinh import HanMuc
 from tram.han_muc.nguon import NguonHanMuc
-from tram.tho.mo_coi import Kill, dung_nhom, kill_cuc_bo
+from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
+from tram.tho.mo_coi import Kill, kill_cuc_bo
 
 
 class ChayClaude:
     def __init__(self, boc: Callable[[list[str]], list[str]], *, khe_id: str, kill: Kill = kill_cuc_bo,
                  khi_bat_dau: Callable[[int], None] | None = None,
                  khi_han_muc: Callable[[HanMuc], None] | None = None,
-                 tran_token_ra: int | None = None, cho_kill: float = 10.0):
+                 tran_token_ra: int | None = None, cho_kill: float = 10.0, khoi: Callable = khoi_chay):
         self.boc, self.khe_id, self.kill, self.khi_bat_dau = boc, khe_id, kill, khi_bat_dau
-        self.khi_han_muc, self.tran_token_ra, self.cho_kill = khi_han_muc, tran_token_ra, cho_kill
+        self.khi_han_muc, self.tran_token_ra, self.cho_kill, self.khoi = khi_han_muc, tran_token_ra, cho_kill, khoi
 
     @staticmethod
     def _doc(p: subprocess.Popen, f, doc: DocStream, ma_giao: str | None) -> None:
@@ -36,12 +36,6 @@ class ChayClaude:
             f.flush()
             doc.an(sach)
 
-    def _canh(self, pid: int, dung: threading.Event, xong: threading.Event) -> None:
-        while not xong.wait(0.05):
-            if dung.is_set():
-                dung_nhom(pid, kill=self.kill, cho=self.cho_kill)
-                return
-
     def chay(self, argv: list[str], *, cwd: Path, env: dict[str, str], stdin: Path, log: Path,
              dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
         doc = DocStream(nguon, khe_id=self.khe_id, khi_han_muc=self.khi_han_muc, tran_token_ra=self.tran_token_ra,
@@ -50,23 +44,25 @@ class ChayClaude:
         bat_dau, ma = time.monotonic(), None
         with open(stdin, "rb") as vao, open(log, "wb") as f:
             try:
-                p = subprocess.Popen(self.boc(argv), cwd=cwd, env=env, stdin=vao, stdout=subprocess.PIPE,
-                                     stderr=subprocess.STDOUT, start_new_session=True)
+                n = self.khoi(self.boc(argv), kill=self.kill, cwd=cwd, env=env, stdin=vao, stdout=subprocess.PIPE,
+                              stderr=subprocess.STDOUT)
             except OSError as e:
-                f.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}: {e}\n".encode())
+                f.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
             else:
-                if self.khi_bat_dau:
-                    self.khi_bat_dau(p.pid)
-                xong = threading.Event()
-                canh = threading.Thread(target=self._canh, args=(p.pid, dung, xong), daemon=True)
-                doc_t = threading.Thread(target=self._doc, args=(p, f, doc, env.get("TRAM_MA_GIAO")), daemon=True)
-                canh.start()
-                doc_t.start()
-                ma = p.wait()
-                xong.set()
-                canh.join()
-                self.kill(p.pid, signal.SIGKILL)       # con cháu còn sót (và giữ stdout) sau khi CLI thoát
+                try:
+                    if self.khi_bat_dau:
+                        self.khi_bat_dau(n.p.pid)
+                    doc_t = threading.Thread(target=self._doc, args=(n.p, f, doc, env.get("TRAM_MA_GIAO")),
+                                             daemon=True)
+                    doc_t.start()
+                except BaseException:                       # lỗi giữa spawn và chờ: không để CLI sống ngoài quản lý
+                    if not n.thu_hoi(cho_term=self.cho_kill):
+                        raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal") from None
+                    raise
+                ma, sach = cho_den_dung(n, dung, cho_term=self.cho_kill)   # kể cả con cháu giữ stdout sau khi CLI thoát
                 doc_t.join(timeout=self.cho_kill)
+                if not sach or doc_t.is_alive():
+                    raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
         digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
         return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - bat_dau) * 1000),
                            digest_log=digest)
```

`tram/chay_cli/codex/chay.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/chay_cli/codex/chay.py b/tram/chay_cli/codex/chay.py
index 9e18cce..dcb6100 100644
--- a/tram/chay_cli/codex/chay.py
+++ b/tram/chay_cli/codex/chay.py
@@ -1,7 +1,6 @@
-"""Codex dưới principal, callback pid, budget và dọn nhóm con (S5/S6 chưa kiểm thật)."""
+"""Codex dưới principal, callback pid, budget và dọn cả cây con có hạn qua `vong_doi` (lát P1; S5/S6 chưa kiểm thật)."""
 import hashlib
 import json
-import signal
 import subprocess
 import threading
 import time
@@ -12,7 +11,8 @@ from tram.chay_cli.codex.luong import DocLuongCodex
 from tram.chay_cli.giao_dien import KetQuaChay
 from tram.han_muc.nguon import NguonHanMuc
 from tram.phieu.mo_hinh import che_ma_giao
-from tram.tho.mo_coi import dung_nhom, kill_cuc_bo
+from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
+from tram.tho.mo_coi import kill_cuc_bo
 
 
 class ChayCodex:
@@ -22,12 +22,6 @@ class ChayCodex:
         self.khi_bat_dau, self.khi_han_muc = khi_bat_dau, khi_han_muc
         self.tran_token_ra, self.popen, self.cho_dung_giay = tran_token_ra, popen, cho_dung_giay
 
-    def _canh(self, pid, dung, xong):
-        while not xong.wait(0.05):
-            if dung.is_set():
-                dung_nhom(pid, kill=self.kill, cho=self.cho_dung_giay)
-                return
-
     def _doc(self, p, ghi, doc, dung, nguon, ma_giao):
         for tho in p.stdout:
             dong = che_ma_giao(tho.decode("utf-8", errors="replace"), ma_giao)
@@ -52,26 +46,25 @@ class ChayCodex:
         log.parent.mkdir(parents=True, exist_ok=True)
         with open(stdin, "rb") as vao, open(log, "wb") as ghi:
             try:
-                p = self.popen(self.boc(argv), cwd=cwd, env=env, stdin=vao, stdout=subprocess.PIPE,
-                               stderr=subprocess.STDOUT, start_new_session=True)
+                n = khoi_chay(self.boc(argv), kill=self.kill, popen=self.popen, cwd=cwd, env=env, stdin=vao,
+                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
             except OSError as e:
                 ghi.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
             else:
-                if self.khi_bat_dau:
-                    self.khi_bat_dau(p.pid)
-                xong = threading.Event()
-                canh = threading.Thread(target=self._canh, args=(p.pid, dung, xong), daemon=True)
-                doc_t = threading.Thread(target=self._doc,
-                    args=(p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
-                canh.start()
-                doc_t.start()
-                ma = p.wait()
-                xong.set()
-                canh.join()
-                self.kill(p.pid, signal.SIGKILL)
+                try:
+                    if self.khi_bat_dau:
+                        self.khi_bat_dau(n.p.pid)
+                    doc_t = threading.Thread(target=self._doc,
+                        args=(n.p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
+                    doc_t.start()
+                except BaseException:
+                    if not n.thu_hoi(cho_term=self.cho_dung_giay):
+                        raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal") from None
+                    raise
+                ma, sach = cho_den_dung(n, dung, cho_term=self.cho_dung_giay)
                 doc_t.join(timeout=self.cho_dung_giay)
-                if doc_t.is_alive():
-                    raise RuntimeError("Không dọn được nhóm CLI; dừng khe để kiểm principal")
+                if not sach or doc_t.is_alive():
+                    raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
         digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
         return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - t0) * 1000),
                            digest_log=digest)
```

`tram/kiem/vong_doi.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/kiem/vong_doi.py b/tram/kiem/vong_doi.py
index adc850a..9c642d7 100644
--- a/tram/kiem/vong_doi.py
+++ b/tram/kiem/vong_doi.py
@@ -108,3 +108,12 @@ def khoi_chay(argv: list[str], *, kill: Kill, popen: Callable = subprocess.Popen
               chup: Callable[[], list[TienTrinh]] = chup_he, **kw) -> Nhom:
     kw["start_new_session"] = True
     return Nhom(popen(argv, **kw), kill=kill, chup=chup)
+
+
+def cho_den_dung(n: Nhom, dung, *, cho_term: float) -> tuple[int | None, bool]:
+    """CLI của phiếu: chờ thoát hoặc `dung` được đặt (hạn của lần chạy là bộ hẹn đặt `dung` — `mot_lan`), rồi thu hồi cả
+    cây trong hạn hữu hạn. Trả (mã thoát | None, đã xác nhận thu hồi)."""
+    while (ma := n.cho(0.05)) is None and not dung.is_set():
+        pass
+    sach = n.thu_hoi(cho_term=cho_term)
+    return (n.p.returncode if ma is None else ma), sach
```

`tram/tho/mo_coi.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/mo_coi.py b/tram/tho/mo_coi.py
index 5e77750..3b7ea24 100644
--- a/tram/tho/mo_coi.py
+++ b/tram/tho/mo_coi.py
@@ -10,14 +10,9 @@ import time
 from collections.abc import Callable
 from pathlib import Path
 
-Kill = Callable[[int, int], None]
-
+from tram.kiem.vong_doi import kill_cuc_bo  # noqa: F401 — tên cũ; một định nghĩa ở primitive P1
 
-def kill_cuc_bo(pgid: int, sig: int) -> None:
-    try:
-        os.killpg(pgid, sig)
-    except (ProcessLookupError, PermissionError):
-        pass
+Kill = Callable[[int, int], None]
 
 
 def con_song(pid: int) -> bool:
```

`tram/tho/mot_lan.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/mot_lan.py b/tram/tho/mot_lan.py
index 797fcb7..02cee89 100644
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -11,6 +11,7 @@ from tram.duong_dan import doc_luc
 from tram.han_muc.log_claude import doc_log_claude, gop_han_muc
 from tram.han_muc.luat import cham_nguong_ngung
 from tram.han_muc.mo_hinh import lam_moi
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.ban_giao_tam import goi_lan_sau
 from tram.tho.chuan_bi import PhieuDangChay, gui_su_kien
 from tram.tho.mo_coi import ghi_pid
@@ -66,9 +67,14 @@ def chay_mot_lan(pc: PhieuDangChay, nc: NguCanhTho, dung: threading.Event) -> Ke
                               lenh_cho_phep=p.lenh_cho_phep, settings=pc.settings, mcp=pc.mcp), cwd=pc.wt, env=env,
                       stdin=_goi(pc, lan), log=nc.goc / "log" / "chay" / f"{p.giao_id}-{p.luot}-{lan}.jsonl",
                       dung=dung, nguon=nc.nguon_han_muc(pc.k.cli))
+    except LoiThuHoi:
+        raise                           # P1: chưa xác nhận thu hồi → GIỮ pid cho dọn mồ côi lần khởi động sau
+    except BaseException:
+        so.pid.unlink(missing_ok=True)
+        raise
     finally:
         hen.cancel()
-        so.pid.unlink(missing_ok=True)
+    so.pid.unlink(missing_ok=True)
     tt.token_ra += kq.token_ra
     pc.luu()
     kt = ket_thuc_tu(kq)
```

`tram/tho/phieu_chay.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/phieu_chay.py b/tram/tho/phieu_chay.py
index 539ee4e..1112039 100644
--- a/tram/tho/phieu_chay.py
+++ b/tram/tho/phieu_chay.py
@@ -8,6 +8,7 @@ import threading
 import subprocess
 from pathlib import Path
 
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.chuan_bi import PhieuDangChay, chuan_bi
 from tram.tho.day import xoa_ref_tam
@@ -87,6 +88,9 @@ def chay_phieu(nc: NguCanhTho, vk, tt: TrangThaiPhieu) -> str:
     try:
         while (kt := _mot_vong(pc, nc, vk)) is None:
             pass
+    except LoiThuHoi:
+        kt = "tat-tho"                          # P1: tiến trình có thể còn sống — giữ worktree/phiếu, vòng khe dừng
+        raise
     finally:
         vk.pc, vk.buoc = None, "ranh"
         if kt == "tat-tho":
```

`tram/tho/vong_khe.py` (sửa — bản vá áp bằng `git apply`):

```diff
diff --git a/tram/tho/vong_khe.py b/tram/tho/vong_khe.py
index 59ace4f..6d17dd0 100644
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -7,6 +7,7 @@ import time
 
 from tram.chay_cli.bo_cli import BO_CLI
 from tram.duong_dan import doc_luc
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.cau_hinh import KheCauHinh
 from tram.tho.hop_thu import HopThu
@@ -31,6 +32,7 @@ class VongKhe:
         self.da_xac_nhan = False
         self.han_giu = None
         self.han_muc_doc_lai = 0.0
+        self.hong = False                       # P1: CLI chưa xác nhận thu hồi → dừng khe (cả nhịp tim)
 
     def khoi_dong(self) -> None:
         tt = don_mo_coi_khe(self.nc, self.k, self.so, self.hop)
@@ -77,7 +79,7 @@ class VongKhe:
         return kq
 
     def _vong_nhip(self, tat: threading.Event) -> None:
-        while not tat.is_set():
+        while not tat.is_set() and not self.hong:
             self.nhip()
             toi = time.monotonic() + self.nc.chu_ky_nhip
             while not tat.is_set() and time.monotonic() < toi:
@@ -105,6 +107,10 @@ class VongKhe:
             tt = self.phieu_moi
             try:
                 chay_phieu(self.nc, self, tt)
+            except LoiThuHoi:                   # P1: tiến trình dưới principal có thể còn sống → dừng khe
+                print("Không xác nhận thu hồi tiến trình của khe; dừng khe — khởi động lại sẽ dọn mồ côi")
+                self.hong = True
+                break
             except Exception:                   # noqa: BLE001 — lỗi một phiếu không giết vòng của khe
                 print("Lỗi xử lý phiếu; giữ sổ để đối soát, không in dữ liệu credential")
             self.phieu_moi = None
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_cli_vong_doi.py tests/test_codex_chay.py tests/test_phieu_chay_thu_hoi.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2277 tests collected in 3.22s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chay_cli_vong_doi.py tests/test_codex_chay.py tests/test_phieu_chay_thu_hoi.py tram/chay_cli/claude.py tram/chay_cli/codex/chay.py tram/kiem/vong_doi.py tram/tho/mo_coi.py tram/tho/mot_lan.py tram/tho/phieu_chay.py tram/tho/vong_khe.py
git commit -m "fix(tho): CLI của phiếu thu hồi cả cây có hạn, chưa thu hồi thì dừng khe (P1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6: `chay_gioi_han` — run có hạn, sở hữu cây (3C-B-a)

**Đợt:** 3 · **Song song với:** Task 3, 4. Cùng hình dạng gọi `subprocess.run(argv, capture_output, text, timeout, input, check)` mà mã dọn của 3c dùng, nhưng qua `vong_doi`; trong lúc chờ vẫn chụp cây mỗi giây (gọi lại `communicate` không mất dữ liệu ra); luôn đọc bytes, giải mã `errors="replace"` (đầu ra không UTF-8 không bỏ qua thu hồi); `timeout` phải hữu hạn. Ngoại lệ chỉ mang tên chương trình.

**Files:**
- Create: `tests/test_chay_gioi_han.py`
- Create: `tram/kiem/chay_gioi_han.py`

**Interfaces:**
- Consumes: Task 2.
- Produces: `chay_gioi_han(argv, *, kill, timeout, capture_output=False, text=False, input=None, env=None, cwd=None, check=False, khoi=khoi_chay) -> CompletedProcess` (ValueError / OSError / TimeoutExpired / LoiThuHoi / CalledProcessError).

- [ ] **Step 1: Viết test thất bại**

`tests/test_chay_gioi_han.py` (mới):

```python
"""`chay_gioi_han` (3C-B): như `subprocess.run` nhưng có hạn, thu hồi cả cây, ngoại lệ không mang argv/stdout."""
import subprocess
import sys
import time

import pytest

from test_vong_doi import CHAU, SUDO, PopenGia, _song
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable


def test_giong_run_capture_text_input_check():
    r = chay_gioi_han([PY, "-c", "import sys; print(sys.stdin.read().upper()); sys.exit(3)"], kill=kill_cuc_bo,
                      timeout=10, capture_output=True, text=True, input="abc")
    assert (r.returncode, r.stdout) == (3, "ABC\n")
    with pytest.raises(subprocess.CalledProcessError) as e:
        chay_gioi_han([PY, "-c", "import sys; sys.exit(2)"], kill=kill_cuc_bo, timeout=10, check=True)
    assert e.value.cmd == [PY.rsplit("/", 1)[-1]]


def test_qua_han_thu_hoi_roi_nem_timeout_khong_kem_argv():
    t0 = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired) as e:
        chay_gioi_han([PY, "-c", "import time; time.sleep(60)", "BI-MAT-ARGV"], kill=kill_cuc_bo, timeout=0.3,
                      capture_output=True)
    assert time.monotonic() - t0 < 6 and "BI-MAT-ARGV" not in str(e.value)


def test_goc_khong_chet_thi_loi_thu_hoi():
    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: _PopenTreo(), chup=lambda: [SUDO], **kw)

    def tu_choi(g, s):
        raise PermissionError
    with pytest.raises(LoiThuHoi):
        chay_gioi_han(["/usr/bin/sudo", "x"], kill=tu_choi, timeout=0.1, khoi=khoi)


def test_chau_tu_tach_phien_khi_dang_chay_van_bi_thu_hoi(tmp_path):
    chay_gioi_han([PY, "-c", CHAU.format(moi=True, ngu=1.5)], kill=kill_cuc_bo, timeout=20, cwd=tmp_path)
    assert not _song(int((tmp_path / "chau.pid").read_text()))


def test_loi_khoi_chay_khong_chep_duong_dan():
    with pytest.raises(OSError) as e:
        chay_gioi_han(["/BI-MAT-THU-MUC/x"], kill=kill_cuc_bo, timeout=1)
    assert "BI-MAT" not in str(e.value)


def test_dau_ra_khong_phai_utf8_van_thu_hoi_va_timeout_phai_huu_han():
    r = chay_gioi_han([PY, "-c", "import sys; sys.stdout.buffer.write(bytes([0xff, 0x41]))"], kill=kill_cuc_bo,
                      timeout=10, capture_output=True, text=True)
    assert r.stdout == "\ufffdA"
    goi = []
    with pytest.raises(ValueError):
        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=float("inf"), khoi=lambda *a, **k: goi.append(1))
    assert goi == []


class _PopenTreo(PopenGia):
    stdin = stdout = stderr = None

    def communicate(self, input=None, timeout=None):
        time.sleep(timeout)
        raise subprocess.TimeoutExpired("x", timeout)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_gioi_han.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.chay_gioi_han'
ERROR tests/test_chay_gioi_han.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.06s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/chay_gioi_han.py` (mới):

```python
"""`subprocess.run` có hạn và sở hữu cây (lát 3C-B, dot6-C02) — cùng hình dạng gọi `chay(argv, capture_output=…,
text=…, timeout=…)` mà mã dọn lịch/tiến trình của 3c đã dùng, nhưng đi qua `vong_doi`: trong lúc chờ vẫn chụp cây mỗi
`CHU_KY_CHUP` giây; quá hạn → thu hồi cả cây qua `kill` của principal rồi ném `TimeoutExpired`; không xác nhận thu hồi
→ `LoiThuHoi`. Ngoại lệ chỉ mang TÊN chương trình, không argv/đường dẫn/stdout/stderr (dot6-Q06). Luôn đọc bytes rồi
giải mã `errors="replace"` khi `text=True` — đầu ra không phải UTF-8 không làm bỏ qua bước thu hồi."""
import math
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, LoiThuHoi, khoi_chay


def chay_gioi_han(argv: list[str], *, kill: Kill, timeout: float, capture_output: bool = False, text: bool = False,
                  input=None, env=None, cwd=None, check: bool = False,
                  khoi: Callable = khoi_chay) -> subprocess.CompletedProcess:
    if not math.isfinite(timeout):
        raise ValueError("timeout phải hữu hạn")
    ten = [Path(str(argv[0])).name] if argv else []
    ong = subprocess.PIPE if capture_output else subprocess.DEVNULL
    if text and isinstance(input, str):
        input = input.encode()
    try:
        n = khoi(list(argv), kill=kill, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                 stdout=ong, stderr=ong, env=env, cwd=cwd)
    except OSError as e:
        raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
    het = time.monotonic() + timeout
    while True:
        try:
            ra, loi = n.p.communicate(input, timeout=max(0.0, min(CHU_KY_CHUP, het - time.monotonic())))
            break
        except subprocess.TimeoutExpired:
            input = None                    # đã gửi ở lần gọi đầu; gọi lại `communicate` không mất dữ liệu ra
            if time.monotonic() < het:
                n.cay()
                continue
            for f in (n.p.stdin, n.p.stdout, n.p.stderr):
                if f is not None:
                    f.close()
            if not n.thu_hoi():
                raise LoiThuHoi(f"{ten} quá hạn và không xác nhận thu hồi cây tiến trình") from None
            raise subprocess.TimeoutExpired(ten, timeout) from None
    if not n.thu_hoi():
        raise LoiThuHoi(f"{ten}: không xác nhận thu hồi cây tiến trình")
    if check and n.p.returncode:
        raise subprocess.CalledProcessError(n.p.returncode, ten)
    if text:
        ra, loi = (None if x is None else x.decode("utf-8", "replace") for x in (ra, loi))
    return subprocess.CompletedProcess(list(argv), n.p.returncode, ra, loi)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_chay_gioi_han.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2283 tests collected in 3.22s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chay_gioi_han.py tram/kiem/chay_gioi_han.py
git commit -m "feat(kiem): chạy lệnh hệ thống có hạn và thu hồi cây (3C-B)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7: UID thực của principal (3C-B-b)

**Đợt:** 4 · **Song song với:** Task 5, 8, Q1-a. Dò bằng `/bin/sleep` qua đúng `boc`, đọc uid/ruid NHÂN ghi cho cây (không env, không argv); chờ tới khi mọi lá của cây rời root; lá phải có uid = ruid = UID đích, nút trong chỉ là root. Cây dò không thu hồi được → `LoiThuHoi` (người gọi dừng như mọi ca chưa thu hồi), không phải `LoiDanhTinh`.

**Files:**
- Create: `tests/test_danh_tinh.py`
- Create: `tram/kiem/danh_tinh.py`

**Interfaces:**
- Consumes: Task 1, 2.
- Produces: `class LoiDanhTinh(RuntimeError)`; `SLEEP`; `la_cua(cay)`; `quan_sat(boc, kill, *, khoi, chup, han=10.0) -> list[TienTrinh]`; `uid_cua(ten)`; `xac_minh_uid(ten, boc, kill, *, toi=None, tra_uid=uid_cua, quan_sat_=quan_sat) -> int`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_danh_tinh.py` (mới):

```python
"""UID THỰC của principal (3C-B): đọc uid/ruid nhân ghi cho cây dò dưới `boc`, không tin env/argv. Ca thật chỉ chạy
`/bin/sleep` của chính user đang test với `boc` đồng nhất — phải BỊ TỪ CHỐI vì trùng người vận hành."""
import os
import subprocess

import pytest

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh, quan_sat, xac_minh_uid
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo


def _ngu(uid, ruid, pid=4243, cha=4242):
    return TienTrinh(pid, cha, 4242, uid, ruid)


def test_boc_dong_nhat_va_env_gia_mao_bi_tu_choi(monkeypatch):
    monkeypatch.setenv("USER", "tram-kiem")
    monkeypatch.setenv("LOGNAME", "tram-kiem")
    with pytest.raises(LoiDanhTinh, match="UID thực"):
        xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, tra_uid=lambda t: 64999)
    con = [x for x in subprocess.run(["/bin/ps", "-A", "-o", "ppid=,comm="], capture_output=True, text=True).stdout
           .splitlines() if x.split()[0] == str(os.getpid()) and x.endswith("sleep")]
    assert con == []                                        # tiến trình dò đã được thu hồi


def test_dung_uid_qua_quan_sat_gia():
    pty = [SUDO, TienTrinh(4250, 4242, 4250, 0, 0), _ngu(502, 502, 4251, cha=4250)]   # sudo → monitor pty → lệnh
    for cay in ([SUDO, _ngu(502, 502)], pty):
        assert xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, toi=501, tra_uid=lambda t: 502,
                            quan_sat_=lambda b, k: cay) == 502


@pytest.mark.parametrize("cay", [[SUDO, _ngu(502, 501)], [_ngu(501, 501)], [SUDO], [],
                                 [TienTrinh(9, 1, 9, 501, 501), _ngu(502, 502, cha=9)],
                                 [SUDO, _ngu(502, 502), _ngu(503, 503, 4244)]])
def test_sai_uid_hoac_cay_la_bi_tu_choi(cay):
    with pytest.raises(LoiDanhTinh):
        xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, toi=501, tra_uid=lambda t: 502, quan_sat_=lambda b, k: cay)


@pytest.mark.parametrize("tra", [lambda t: 0, lambda t: 501, lambda t: (_ for _ in ()).throw(KeyError(t))])
def test_tai_khoan_khong_hop_le_khong_spawn(tra):
    goi = []
    with pytest.raises(LoiDanhTinh):
        xac_minh_uid("x", lambda a: a, kill_cuc_bo, toi=501, tra_uid=tra, quan_sat_=lambda b, k: goi.append(1))
    assert goi == []


class _DaThoat(PopenGia):
    """Wrapper thoát ngay (vd. `sudo -n` bị từ chối): không bao giờ có tiến trình dò để đọc UID."""
    returncode = 1

    def wait(self, timeout=None):
        return 1

    def poll(self):
        return 1


def test_quan_sat_khong_thay_tien_trinh_do_hoac_khong_khoi_chay_duoc():
    with pytest.raises(LoiDanhTinh, match="không thấy"):
        quan_sat(lambda a: a, kill_cuc_bo, khoi=lambda argv, **kw: khoi_chay(argv, popen=lambda *x, **y: _DaThoat(),
                                                                             **kw), chup=lambda: [])
    with pytest.raises(LoiDanhTinh, match="không khởi chạy"):
        quan_sat(lambda a: ["/khong/co/chuong-trinh"], kill_cuc_bo)


def test_quan_sat_khong_thu_hoi_duoc_cay_do():
    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: PopenGia(), **kw)
    with pytest.raises(LoiThuHoi, match="thu hồi"):
        quan_sat(lambda a: a, lambda g, s: None, khoi=khoi, chup=lambda: [SUDO, _ngu(502, 502)])
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_danh_tinh.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.danh_tinh'
ERROR tests/test_danh_tinh.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.06s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/danh_tinh.py` (mới):

```python
"""Danh tính THỰC của principal (lát 3C-B, dot6-C02). Không tin tên (`getpass.getuser()` đọc env), không so argv của
`boc`: chạy `/bin/sleep` qua ĐÚNG `boc` của principal, đọc UID hiệu lực + UID thực mà NHÂN ghi cho cả cây đó (`ps`,
chỉ cột số), rồi thu hồi cây (P1). Chờ tới khi mọi LÁ của cây (tiến trình không có con trong cây) không còn là root —
tức `sudo` đã đổi UID và exec xong. Đạt khi: tài khoản đích có thật, không phải root, không phải người vận hành; mọi lá
có uid = ruid = UID đích; mọi tiến trình không phải lá là root (chính `sudo`, monitor pty). Sai lệch, wrapper không đổi
UID, không thấy tiến trình dò, quá hạn hay lỗi `ps` → `LoiDanhTinh`; không thu hồi được cây dò → `LoiThuHoi` (người gọi
dừng như mọi ca chưa thu hồi). Cả hai: KHÔNG được chạm lịch."""
import os
import pwd
import subprocess
import time
from collections.abc import Callable

from tram.kiem.cay_tien_trinh import TienTrinh, chup_he
from tram.kiem.vong_doi import Kill, LoiThuHoi, khoi_chay

SLEEP = "/bin/sleep"


class LoiDanhTinh(RuntimeError):
    """Chưa chứng minh được tiến trình chạy dưới đúng UID của principal."""


def la_cua(cay: list[TienTrinh]) -> list[TienTrinh]:
    cha = {t.ppid for t in cay}
    return [t for t in cay if t.pid not in cha]


def quan_sat(boc: Callable[[list[str]], list[str]], kill: Kill, *, khoi: Callable = khoi_chay,
             chup: Callable[[], list[TienTrinh]] = chup_he, han: float = 10.0) -> list[TienTrinh]:
    """Cây của tiến trình dò lúc mọi lá đã rời UID root."""
    try:
        n = khoi(boc([SLEEP, "30"]), kill=kill, chup=chup, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"})
    except (OSError, ValueError) as e:
        raise LoiDanhTinh(f"không khởi chạy được tiến trình dò: {type(e).__name__}") from None
    het = time.monotonic() + han
    try:
        while time.monotonic() < het and n.p.poll() is None:
            con = n.cay()
            if con and all(t.uid != 0 for t in la_cua(con)):
                return con
            time.sleep(0.05)
        raise LoiDanhTinh("không thấy tiến trình dò dưới boc (wrapper lỗi, bị từ chối hoặc quá hạn)")
    finally:
        if not n.thu_hoi(cho_term=1.0, cho_cuoi=1.0, han_gui=2.0):
            raise LoiThuHoi("không xác nhận thu hồi tiến trình dò")


def uid_cua(ten: str) -> int:
    return pwd.getpwnam(ten).pw_uid


def xac_minh_uid(ten: str, boc: Callable[[list[str]], list[str]], kill: Kill, *, toi: int | None = None,
                 tra_uid: Callable[[str], int] = uid_cua, quan_sat_: Callable = quan_sat) -> int:
    """UID đã chứng minh của principal `ten`."""
    toi = os.getuid() if toi is None else toi
    try:
        mong = tra_uid(ten)
    except (KeyError, OSError, TypeError):
        raise LoiDanhTinh("tài khoản principal không có trên máy") from None
    if mong in (0, toi):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành — không phải tài khoản cách ly")
    cay = quan_sat_(boc, kill)
    la = la_cua(cay)
    uid_la = {(t.uid, t.ruid) for t in la}
    khac = {t.uid for t in cay if t not in la and t.uid != 0}
    if uid_la != {(mong, mong)} or khac:
        raise LoiDanhTinh(f"UID thực của tiến trình dò {sorted(uid_la)} (khác: {sorted(khac)}) ≠ {mong}")
    return mong
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_danh_tinh.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2296 tests collected in 3.21s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_danh_tinh.py tram/kiem/danh_tinh.py
git commit -m "feat(kiem): xác minh UID thực của principal bằng tiến trình dò (3C-B, dot6-C02)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 8: Hạn tổng harness bằng tiến trình con + cổng dọn bền (3C-B-c)

**Đợt:** 4 · **Song song với:** Task 5, 7, Q1-a. Thay `daemon thread + join(timeout)` của T12 r47: harness là tiến trình con nhóm riêng; quá hạn thu hồi cả cây qua `kill` gộp; `don()` phải trả đúng True; dấu cổng O_EXCL chỉ xoá khi cả hai xác nhận. `don()` LUÔN chạy sau khi đã thử thu hồi (gỡ lịch kể cả khi cây chưa thu hồi); hạn không hữu hạn bị từ chối trước khi đặt dấu.

**Files:**
- Create: `tests/test_han_tong.py`
- Create: `tram/kiem/han_tong.py`

**Interfaces:**
- Consumes: Task 2.
- Produces: `gop_kill(*kill) -> Kill`; `class HetHanTong(LoiThuHoi)`; `cong_dong(dau) -> bool`; `chay_han_tong(argv, *, han, kill, dau, don, khoi=khoi_chay, **kw) -> int`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_han_tong.py` (mới):

```python
"""Hạn tổng harness (3C-B): tiến trình con thay luồng nền; quá hạn thu hồi cả cây; cổng chỉ mở khi dọn xác nhận.
Harness giả là `python -c` của chính user đang test; `don` là spy (không chạm lịch thật)."""
import os
import signal
import sys
import time

import pytest

from tram.kiem.han_tong import HetHanTong, chay_han_tong, cong_dong
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable
TREO = ("import subprocess, sys, time\n"
        "c = subprocess.Popen([sys.executable, '-c', 'import signal, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'], start_new_session=True)\n"
        "open('chau.pid', 'w').write(str(c.pid)); time.sleep(60)\n")


def _song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_qua_han_thu_hoi_ca_chau_roi_don_va_mo_cong(tmp_path):
    don, dau, t0 = [], tmp_path / "cong" / "kiem.dong", time.monotonic()
    with pytest.raises(HetHanTong, match="đã thu hồi và dọn"):
        chay_han_tong([PY, "-c", TREO], han=1.0, kill=kill_cuc_bo, dau=dau, don=lambda: don.append(1) or True,
                      cwd=tmp_path)
    chau = int((tmp_path / "chau.pid").read_text())
    assert time.monotonic() - t0 < 10 and not _song(chau) and don == [1] and not cong_dong(dau)


@pytest.mark.parametrize("don", [lambda: False, lambda: None, lambda: 1 / 0])
def test_don_khong_xac_nhan_thi_cong_giu_dong_va_luot_sau_bi_tu_choi(tmp_path, don):
    dau = tmp_path / "kiem.dong"
    with pytest.raises(LoiThuHoi, match="cổng giữ đóng"):
        chay_han_tong([PY, "-c", "pass"], han=10, kill=kill_cuc_bo, dau=dau, don=don)
    assert cong_dong(dau)
    goi = []
    with pytest.raises(LoiThuHoi, match="cổng đang đóng"):
        chay_han_tong([PY, "-c", "pass"], han=10, kill=kill_cuc_bo, dau=dau, don=lambda: True,
                      khoi=lambda *a, **k: goi.append(1))
    assert goi == []


def test_xong_trong_han_tra_ma_va_mo_cong(tmp_path):
    dau = tmp_path / "kiem.dong"
    assert chay_han_tong([PY, "-c", "import sys; sys.exit(1)"], han=10, kill=kill_cuc_bo, dau=dau,
                         don=lambda: True) == 1
    assert not cong_dong(dau)


def test_kill_bi_tu_choi_van_don_lich_va_cong_giu_dong(tmp_path):
    dau, pid, don = tmp_path / "kiem.dong", [], []

    def khoi(argv, **kw):
        n = khoi_chay(argv, **kw)
        pid.append(n.p.pid)
        return n
    try:
        with pytest.raises(HetHanTong, match="CỔNG GIỮ ĐÓNG"):
            chay_han_tong([PY, "-c", "import time; time.sleep(60)"], han=0.3, kill=lambda g, s: None, dau=dau,
                          don=lambda: don.append(1) or True, khoi=khoi)
        assert cong_dong(dau) and don == [1]                    # vẫn gỡ lịch dù cây chưa thu hồi được
    finally:
        os.killpg(pid[0], signal.SIGKILL)


@pytest.mark.parametrize("han", [float("inf"), float("nan"), 0])
def test_han_khong_huu_han_bi_tu_choi_truoc_khi_dat_dau(tmp_path, han):
    with pytest.raises(ValueError):
        chay_han_tong([PY, "-c", "pass"], han=han, kill=kill_cuc_bo, dau=tmp_path / "d", don=lambda: True)
    assert not cong_dong(tmp_path / "d")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_han_tong.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.han_tong'
ERROR tests/test_han_tong.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/han_tong.py` (mới):

```python
"""Hạn TỔNG cho harness dài (lát 3C-B, dot6-C02) — thay `daemon thread + join(timeout)` (chỉ thôi chờ, không thu
hồi). Harness chạy trong TIẾN TRÌNH CON nhóm riêng (`vong_doi`); quá hạn → thu hồi cả cây qua `kill` gộp (quản lý +
principal); sau đó, kể cả khi harness tự xong, `don()` (gỡ lịch + tiến trình của principal qua `CongLich` — mã 3c)
phải trả đúng True. Cổng = file dấu `dau`, tạo O_EXCL TRƯỚC khi spawn, chỉ xoá khi cả thu hồi cây lẫn `don()` xác
nhận. Còn dấu → lượt sau bị từ chối không spawn (`cong_dong`), chờ Đại ca dọn và kiểm tay."""
import math
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.kiem.vong_doi import LOI_GUI, Kill, LoiThuHoi, khoi_chay


def gop_kill(*ds: Kill) -> Kill:
    """Gửi lần lượt qua từng cách (principal rồi cục bộ) — cây harness có cả tiến trình của quản lý lẫn principal."""
    def kill(pgid: int, sig: int) -> None:
        for k in ds:
            try:
                k(pgid, sig)
            except LOI_GUI:
                pass
    return kill


class HetHanTong(LoiThuHoi):
    """Harness vượt hạn tổng — đã thu hồi + dọn; kết quả không được công nhận (cổng còn đóng nếu dọn chưa xác nhận)."""


def cong_dong(dau: Path) -> bool:
    return dau.exists()


def _don(don: Callable[[], bool]) -> bool:
    try:
        return don() is True
    except Exception:                       # noqa: BLE001 — lỗi dọn nào cũng là "không xác nhận", cổng giữ đóng
        return False


def chay_han_tong(argv: list[str], *, han: float, kill: Kill, dau: Path, don: Callable[[], bool],
                  khoi: Callable = khoi_chay, **kw) -> int:
    """Mã thoát của harness khi xong trong hạn VÀ dọn xác nhận; ngược lại ném (HetHanTong | LoiThuHoi). `don()` LUÔN
    chạy sau khi đã thử thu hồi — kể cả khi thu hồi không xác nhận — để gỡ lịch harness đã cài."""
    if not (math.isfinite(han) and han > 0):
        raise ValueError("hạn tổng phải hữu hạn, dương")
    dau.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.close(os.open(dau, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    except FileExistsError:
        raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
    try:
        n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, **kw)
    except OSError:
        n = None
    ma = n.cho(han) if n else None
    sach = n.thu_hoi() if n else True
    xong = _don(don) and sach
    if xong:
        dau.unlink()
    if n is None:
        raise LoiThuHoi("không khởi chạy được harness")
    if ma is None:
        raise HetHanTong(f"harness quá hạn tổng {han:g} s — " + ("đã thu hồi và dọn" if xong else "CỔNG GIỮ ĐÓNG"))
    if not xong:
        raise LoiThuHoi("harness xong nhưng chưa xác nhận thu hồi/dọn — cổng giữ đóng")
    return ma
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_han_tong.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2305 tests collected in 3.27s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_han_tong.py tram/kiem/han_tong.py
git commit -m "feat(kiem): hạn tổng harness bằng tiến trình con, cổng dọn bền (3C-B, dot6-C02)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 9: Cổng thao tác lịch (3C-B-d)

**Đợt:** 5 · **Song song với:** Q1-b · **Phải sau:** Task 6, 7, 8 (`gop_kill`). Mọi lệnh của bước dọn/harness `tram-kiem` đi qua `CongLich`: mở cổng = `xac_minh_uid` đạt; chỉ chuyển lệnh nằm sau đúng tiền tố `boc` đã xác minh, hoặc lệnh quan sát trong danh sách đóng (`find` không `-exec/-ok/-delete`, `pgrep`, `ps`, `stat`). Không lọc chữ trong shell (review chu kỳ 2: `sh -c "echo x|crontab -"` lọt bộ lọc chữ). Spy chứng minh sai danh tính → 0 lệnh. Mặc định chạy bằng `chay_gioi_han` với kill gộp principal + cục bộ (lệnh quan sát chạy dưới quyền quản lý).

**Files:**
- Create: `tests/test_cong_lich.py`
- Create: `tram/kiem/cong_lich.py`

**Interfaces:**
- Consumes: Task 6 `chay_gioi_han`, Task 8 `gop_kill`, Task 7 `LoiDanhTinh`, `xac_minh_uid`.
- Produces: `LICH`, `CHO_QUAN_LY`, `CAM_FIND`; `duoc_chay(argv, tien_to) -> bool`; `CongLich(tien_to, uid, chay)` callable như `subprocess.run` (LoiDanhTinh trước khi chạy); `mo_cong_lich(ten, boc, kill, *, chay=None, xac_minh=xac_minh_uid) -> CongLich`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cong_lich.py` (mới):

```python
"""Cổng thao tác lịch (3C-B): spy chứng minh sai danh tính → KHÔNG gọi cron/at/launchctl; lệnh lịch ngoài tiền tố đã
xác minh bị từ chối trước khi chạy. Không có lệnh lịch thật nào được spawn trong file này."""
import pytest

from tram.kiem.cong_lich import CongLich, duoc_chay, mo_cong_lich
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import kill_cuc_bo

BOC = ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--")


def boc(argv):
    return [*BOC, *argv]


class Spy:
    def __init__(self):
        self.argv = []

    def __call__(self, argv, **kw):
        self.argv.append(list(argv))
        return "ok"


def _sai(*a):
    raise LoiDanhTinh("UID thực khác")


@pytest.mark.parametrize("xac_minh", [_sai, lambda *a: (_ for _ in ()).throw(LoiDanhTinh("quá hạn"))])
def test_sai_danh_tinh_khong_goi_lenh_nao(xac_minh):
    spy = Spy()
    with pytest.raises(LoiDanhTinh):
        cong = mo_cong_lich("tram-kiem", boc, kill_cuc_bo, chay=spy, xac_minh=xac_minh)
        cong(boc(["/usr/bin/crontab", "-l"]))
    assert spy.argv == []


def test_lenh_ngoai_principal_bi_chan_truoc_khi_chay():
    spy = Spy()
    cong = mo_cong_lich("tram-kiem", boc, kill_cuc_bo, chay=spy, xac_minh=lambda *a: 502)
    for sai in (["/usr/bin/crontab", "-r"], ["crontab", "-l"], ["/bin/launchctl", "bootout", "gui/501"],
                ["/usr/bin/sudo", "-n", "-u", "dai-ca", "--", "/usr/bin/atrm", "1"], ["/bin/sh", "-c", "at now"],
                ["/usr/bin/env", "batch"], ["/bin/sh", "-c", "echo x|crontab -"], list(BOC),
                ["/usr/bin/find", "/", "-exec", "/usr/bin/crontab", "-r", ";"], ["find", "/usr/lib/cron/jobs"]):
        with pytest.raises(LoiDanhTinh):
            cong(sai, capture_output=True, text=True, timeout=30)
    assert spy.argv == []
    assert cong(boc(["/usr/bin/crontab", "-l"]), timeout=30) == "ok"
    assert cong(["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]) == "ok"
    assert spy.argv == [boc(["/usr/bin/crontab", "-l"]), ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]
    assert cong.uid == 502 and cong.tien_to == BOC


@pytest.mark.parametrize("b", [lambda a: a, lambda a: ["/usr/bin/crontab", *a]])
def test_boc_rong_hoac_chua_lich_khong_mo_cong(b):
    goi = []
    with pytest.raises(LoiDanhTinh):
        mo_cong_lich("tram-kiem", b, kill_cuc_bo, chay=Spy(), xac_minh=lambda *a: goi.append(1) or 502)
    assert goi == []


def test_danh_sach_quan_sat_dong():
    assert duoc_chay(["/usr/bin/pgrep", "-f", "at"], BOC) and duoc_chay(["/bin/ps", "-A"], BOC)
    assert not duoc_chay(["/usr/bin/find", "/tmp", "-delete"], BOC) and not duoc_chay([], BOC)
    assert CongLich(BOC, 502, Spy())(boc(["/bin/launchctl", "print", "user/502"])) == "ok"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_cong_lich.py`

Kết quả THẬT trên bản sao (trích):

```text
E   ModuleNotFoundError: No module named 'tram.kiem.cong_lich'
ERROR tests/test_cong_lich.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
```

- [ ] **Step 3: Viết mã**

`tram/kiem/cong_lich.py` (mới):

```python
"""Cổng thao tác LỊCH (lát 3C-B, dot6-C02 — sau sự cố subagent chạy crontab dưới tài khoản người vận hành): mọi lệnh
của bước dọn/harness `tram-kiem` (kể cả cron/at/batch/launchctl) đi qua `CongLich`. Mở cổng = `xac_minh_uid` đạt (UID
thực, không tin env/argv). Cổng chỉ chuyển:
- lệnh nằm SAU đúng tiền tố `boc` đã xác minh (chạy dưới principal — gỡ lịch của chính nó là việc được phép);
- hoặc lệnh QUAN SÁT của tài khoản quản lý trong danh sách đóng `CHO_QUAN_LY` (đường dẫn tuyệt đối), `find` không có
  `-exec/-ok/-delete`. Không lọc theo chữ trong shell (`sh -c "…|crontab -"` lọt được bộ lọc chữ): mọi shell, mọi lệnh
  khác chạy dưới quyền quản lý bị từ chối TRƯỚC khi chạy.
Mặc định mọi lệnh chạy bằng `chay_gioi_han` (có hạn) với kill GỘP principal + cục bộ (lệnh quan sát chạy dưới quyền
quản lý). Chỉ test dựng `CongLich` trực tiếp; mã chạy thật phải mở bằng `mo_cong_lich`."""
import functools
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.han_tong import gop_kill
from tram.kiem.vong_doi import Kill, kill_cuc_bo

LICH = frozenset({"crontab", "at", "atq", "atrm", "batch", "launchctl"})
CHO_QUAN_LY = frozenset({"/usr/bin/find", "/usr/bin/pgrep", "/bin/ps", "/usr/bin/stat"})
CAM_FIND = frozenset({"-exec", "-execdir", "-ok", "-okdir", "-delete"})


def duoc_chay(argv: list[str], tien_to: tuple[str, ...]) -> bool:
    if len(argv) > len(tien_to) and tuple(argv[:len(tien_to)]) == tien_to:
        return True
    return bool(argv) and argv[0] in CHO_QUAN_LY and not CAM_FIND & set(argv)


@dataclass(frozen=True)
class CongLich:
    tien_to: tuple[str, ...]
    uid: int
    chay: Callable

    def __call__(self, argv: list[str], **kw):
        argv = [str(a) for a in argv]
        if not duoc_chay(argv, self.tien_to):
            raise LoiDanhTinh("lệnh không chạy dưới principal đã xác minh UID và không phải lệnh quan sát cho phép")
        return self.chay(argv, **kw)


def mo_cong_lich(ten: str, boc: Callable[[list[str]], list[str]], kill: Kill, *, chay: Callable | None = None,
                 xac_minh: Callable = xac_minh_uid) -> CongLich:
    tien_to = tuple(boc([]))
    if not tien_to or any(Path(a).name in LICH for a in tien_to):
        raise LoiDanhTinh("boc rỗng hoặc tự chứa lệnh lịch — lệnh sẽ không đổi principal")
    uid = xac_minh(ten, boc, kill)
    return CongLich(tien_to, uid, chay or functools.partial(chay_gioi_han, kill=gop_kill(kill, kill_cuc_bo)))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_cong_lich.py`

Kết quả THẬT: `0`. Sau task, toàn bộ thu thập được: `2311 tests collected in 3.23s`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cong_lich.py tram/kiem/cong_lich.py
git commit -m "feat(kiem): cổng thao tác lịch chỉ mở sau khi xác minh UID thực (3C-B)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Hợp đồng cho 3c (nhánh 3c tự sửa plan của mình; plan P1 KHÔNG sửa file 3c)

P1 là đầu mối DUY NHẤT của kill/wait. Các file dưới đây thuộc plan 3c (T3/T5/T7/T10–T12 bản r47 và 3C-C/3C-D); khi
3c triển khai sau P1/3C-B phải theo đúng các điểm này, không viết lại vòng đời tiến trình riêng:

| # | Chỗ của 3c | Phải làm | Lý do (finding) |
|---|---|---|---|
| H1 | Mọi chỗ spawn rồi chờ (`kiem_lai`, `ban_chep`, `don_tram_kiem`, `lich_tram_kiem`, `launchd_kiem`, harness) | Dùng `chay_mot_lenh` (lệnh kiểm), `chay_gioi_han` (lệnh hệ thống ngắn có hạn, cùng hình dạng `subprocess.run`) hoặc `khoi_chay`/`Nhom`. Không thêm `p.wait()` trần, `Thread(daemon)+join(timeout)` làm hạn, hay `subprocess.run(timeout=…)` cho lệnh có thể chạy dưới `sudo` | dot6-C02; CPython `run()` còn `wait()` trần khi `kill()` bị từ chối |
| H2 | `PrincipalKiem.kill_nhom` (3c Task 5 viết lại) | Gửi bằng `chay_ngan([*boc, "/bin/kill", "-s", SIG, "--", f"-{pgid}"], timeout=5)`; không `subprocess.run(…, timeout=20)` | cận trên của `thu_hoi` (P1 Task 2) |
| H3 | `don_sach` + `lich_tram_kiem.ra/don_cron/don_at` + `launchd_kiem` (3c Task 11) | Đầu `don_sach`, TRƯỚC lệnh đầu tiên: `cong = mo_cong_lich(pk.ten, pk.boc_lenh, pk.kill_nhom)`; truyền `chay=cong` cho mọi lệnh; `uid = cong.uid` thay `uid_cua` tra passwd riêng. `LoiDanhTinh`/`LoiThuHoi` → `LoiBanChep` (không đụng lịch). Test 3c dựng `CongLich(tien_to, uid, chay_gia)` trực tiếp | dot6-C02 UID thực; spy "sai danh tính không gọi cron/at/launchctl" đã có ở P1 Task 9 |
| H4 | `ra()` của `lich_tram_kiem` | Bắt thêm `LoiThuHoi` (và `LoiDanhTinh`) → `LoiBanChep` với thông báo cố định | dot6-Q06 không lộ argv |
| H5 | Harness `tram giao nghiem-thu-kiem` (3c Task 12) | Bỏ `_nghiem_thu_kiem` luồng nền. CLI cha gọi `chay_han_tong([sys.executable, "-c", "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))", "giao", "nghiem-thu-kiem", "--trong", …], han=args.cho + 900, kill=gop_kill(pk.kill_nhom, kill_cuc_bo), dau=tram_home() / "kiem-lai.dong", don=…)`; `don` chạy `don_sach` dưới `giu_khoa()` và chỉ trả True khi không ném. Guard `boc(["x"]) == ["x"] or pk.ten == getpass.getuser()` thay bằng `mo_cong_lich(...)` trước `--tai-sinh` | dot6-C02 hạn tổng + thu hồi lịch |
| H6 | `kiem_lai` / `ban_chep` | Từ chối (`LoiBanChep`) khi `cong_dong(tram_home() / "kiem-lai.dong")`; `KetQuaLenh.da_thu_hoi is False` → `LoiBanChep`, không công nhận kết quả | cleanup không xác nhận giữ cổng đóng |
| H7 | `kiem_san_sang._dung_duoc` + mục danh tính | Bỏ luồng + `join(15)`: gọi `chay_lenh` trực tiếp (đã có hạn); xanh khi `het_gio and da_thu_hoi`. Danh tính: `xac_minh_uid(pk.ten, pk.boc_lenh, pk.kill_nhom)` thay so `id -un` với `getpass.getuser()` | dot6-C02; review chu kỳ 1 mục 9 |
| H8 | Import cũ `from tram.kiem.chay_lenh import _kill_nhom` | Giữ nguyên tên (P1 không xoá) — 3c không phải sửa import | tránh vỡ chéo nhánh |

3c KHÔNG sửa `tram/kiem/{vong_doi,cay_tien_trinh,lenh_ngan,chay_lenh,chay_gioi_han,danh_tinh,cong_lich,han_tong}.py`.
Thiếu khả năng gì ở primitive → mở task cho P1 (một đầu mối), không vá tại chỗ.

## Cổng G2/G3/G5 — offline chứng minh được gì, phần nào CHỈ chứng minh trên OS thật

Trạng thái mọi cổng dưới đây: **CHƯA CHẠY** trên OS thật. Plan không cấp quyền chạy `sudo`, cron/at/launchctl.

| Cổng | Offline (G2) đã có test | Chỉ chứng minh được trên macOS thật (G3 xin quyền kịch bản; G4/G5 nghiệm thu) |
|---|---|---|
| P1 hạn hữu hạn | Mọi chờ có hạn, kể cả gốc không bao giờ chết (Popen giả), `kill` bị từ chối/treo, `ps` lỗi; cận trên đo được | Thời gian thật của `sudo -n … /bin/kill` và `ps` trên máy B; tiến trình kẹt trong nhân (không giả lập được) |
| P1 thu hồi cây | Cháu ở phiên mới (giống pty), cháu bỏ qua SIGTERM, cha thoát bình thường để lại cháu — đều bị thu hồi với tiến trình cùng user | Dưới `sudo -n -u <principal>`: (a) `start_new_session` có thật sự khiến sudo KHÔNG cấp pty dù `Defaults use_pty`; (b) nhóm/phiên của lệnh khi có pty; (c) tiến trình quản lý có gửi được tín hiệu tới `sudo` root không; (d) `sudo` tự thoát sau khi lệnh bị principal giết; (e) sandbox-exec giữ nguyên pid/nhóm |
| P1 "treo sau SIGKILL" (r47 câu 5) | Gốc giả không chết → `thu_hoi` False trong hạn; `chay_mot_lenh` fail + `da_thu_hoi=False`; CLI → `LoiThuHoi` → vòng khe dừng, giữ pid cho dọn mồ côi | Có xảy ra thật với cấu hình sudoers của `tram chu cai-dat-tho` không; nếu có, `don_mo_coi_khe` lần khởi động sau có dọn được không |
| 3C-B UID thực | Boc đồng nhất + env `USER=tram-kiem` giả bị từ chối bằng UID nhân ghi; spy: sai danh tính/không xác nhận → 0 lệnh cron/at/launchctl; lệnh lịch trần hay dưới tiền tố khác bị chặn trước khi chạy | `ps` thấy đúng uid/ruid của tiến trình `tram-kiem` dưới `sudo -n -u tram-kiem`; cây dò có đúng dạng `sudo(root) → /bin/sleep(uid tram-kiem)` (và monitor pty nếu có); `pwd.getpwnam` trả đúng UID sau `sysadminctl` |
| 3C-B hạn tổng | Harness con quá hạn → cả cây (kể cả cháu phiên mới) bị thu hồi; `don()` lỗi/False/ném → dấu cổng còn, lượt sau bị từ chối không spawn | Harness thật của 3c dưới `tram-kiem` + gỡ lịch thật qua `CongLich` (G4, sau 3C-A/3C-D) |
| G5 quota principal | Argv/env/kill theo đúng principal của hai khe, hai cơ chế; thiếu principal không spawn; hồ sơ sandbox `wt=None` cấm thư mục khe khác; lỗi/treo/không thu hồi không làm chết nhịp; sentinel token không vào env con/log/nhịp | `codex app-server` thật dưới `sudo -n -H -u <khe>`: đọc được `CODEX_HOME` của khe, KHÔNG dùng auth của tài khoản quản lý; sandbox profile thật cho phép app-server chạy; thời gian thật một lần đọc; log launchd không chứa token |

## Rủi ro còn lại / việc ngoài phạm vi (không tuyên bố đã đóng)

1. **Thăm dò cách ly `tram/tho/kiem_am.py`, `kiem_cong.dang_nhap`, `tram/chu/kiem_cach_ly.py`** vẫn `subprocess.run(…, timeout=…)` dưới `sudo` — có thể `wait()` trần nếu `sudo` treo và kill bị từ chối. Đã thử đưa qua primitive ở chu kỳ 2 nhưng HOÀN TÁC ở chu kỳ 3: `start_new_session` lấy mất tty nên `sudo -u` không hỏi được mật khẩu Đại ca gõ trong Terminal.app. Đây là lệnh tương tác (Đại ca Ctrl-C được), không nằm trên đường thợ/quota/harness. Đề nghị bead riêng: thiết kế cách chạy thăm dò có hạn mà vẫn giữ tty khi cần mật khẩu.
2. **Phía trạm chưa có hạn cho tới khi 3c áp Hợp đồng H2/H6/H7:** `PrincipalKiem.kill_nhom` còn `run(timeout=20)`, `kiem_lai` chưa xét `da_thu_hoi`, `kiem_san_sang._dung_duoc` còn luồng + `join(15)`. G4 không được qua khi các điểm này chưa áp.
3. **`tram/tho/mo_coi.py`** (dọn mồ côi từ file pid lần chạy trước) không kiểm thời điểm khởi động của PID — sau reboot PID có thể đã thuộc tiến trình khác. Có trước P1; P1 giữ pid khi `LoiThuHoi` nên đường này quan trọng hơn. Đề nghị bead riêng (so `ps -o lstart` hoặc uid trước khi giết).
4. **`tram/tho/theo_doi.py`** còn `join()` trần và Timer daemon (review chu kỳ 2 nêu, có trước P1) — bead riêng.
5. Cửa sổ thoát: tiến trình fork + setsid rồi cha thoát trong < 1 s giữa hai lần chụp (≤ 0,2 s ở đầu lần chạy) không thấy được — ranh giới C01/3C-A, không phải lời hứa P1.
6. Khi đã `LoiThuHoi`, luồng đọc stdout của CLI có thể còn kẹt nếu tiến trình ngoài cây giữ ống; `chay_ngan` bỏ lại `sudo kill` treo cho `subprocess` tự gặt. Cả hai chỉ xảy ra khi khe đã dừng.
7. Hồ sơ sandbox `wt=None` giữ `allow default` cho đọc gốc worktree (quyết định S6 có trước) — không nới thêm, chưa thu hẹp.
8. `codex login status` của `tram tho kiem` (`do_cli`) vẫn chạy dưới tài khoản quản lý với `CODEX_HOME` của khe — cùng loại bs-78r.10, ngoài đường quota; bead riêng.
9. Lời khẳng định `use_pty` chỉ áp khi sudo có terminal lấy từ man sudoers — G3 phải đo.
10. Các sửa của review chu kỳ 3 chưa qua người review mới (đã đủ 3 chu kỳ) — đưa vào zip review Codex.

## Kết quả chạy thử trên bản sao (16/10/2026)

- Bản sao: `git clone` nhánh `plan/6/p1` (= `main` `5da881e`) vào thư mục scratch, `.venv` riêng (`uv sync` offline).
- **Kiểm fixture không tác động host trước khi chạy toàn bộ:** plugin pytest tạm (`sys.addaudithook`) từ chối mọi spawn `sudo`, `crontab`, `at`, `atq`, `atrm`, `batch`, `launchctl`, `dscl`, `sysadminctl`, `pkill`, `killall`, `security`, `createhomedir`, `visudo`, `dseditgroup` từ tiến trình pytest; thêm thư mục PATH giả có script cùng tên ghi log và thoát 97. Mọi lần chạy toàn bộ (baseline, bản phát triển, bản chạy lại): **0 lần bị chặn**, log PATH giả rỗng; sau mỗi lần không còn tiến trình `sleep(60)`/app-server giả/CLI giả nào.
- Baseline: `2242 passed in 135.14s` (khớp N₀).
- Từng task, áp nguyên văn theo thứ tự T1…T9 (RED thật → GREEN thật):

| Task | RED | GREEN | Tổng thu thập |
|---|---|---|---|
| T1 | 1 error (ModuleNotFoundError) | 10 passed | 2252 |
| T2 | 2 errors (ModuleNotFoundError) | 9 passed | 2261 |
| T3 | 5 failed, 30 passed | 35 passed | 2265 |
| T4 | 5 failed, 4 passed | 9 passed | 2269 |
| T5 | 5 failed, 7 passed (94 s — CLI giả treo 60 s với mã cũ) | 12 passed | 2277 |
| T6 | 1 error (ModuleNotFoundError) | 6 passed | 2283 |
| T7 | 1 error (ModuleNotFoundError) | 13 passed | 2296 |
| T8 | 1 error (ModuleNotFoundError) | 9 passed | 2305 |
| T9 | 1 error (ModuleNotFoundError) | 6 passed | 2311 |

- Sau Q1-a, Q1-b, Q2 (plan bs-78r.10): suite đầy đủ trên bản chạy lại **`2326 passed in 172.25s`**; cây file của bản chạy lại trùng từng byte với bản phát triển (`diff -r` rỗng).
- Mọi file `.py` thêm/sửa ≤ 120 dòng, mọi dòng ≤ 120 ký tự Unicode (đếm bằng script).
- Lặp 5 lần 9 file test có tiến trình thật/giả (`test_vong_doi*`, `test_cay_tien_trinh`, `test_chay_gioi_han`, `test_han_tong`, `test_danh_tinh`, `test_chay_cli_vong_doi`, `test_codex_app_server`, `test_nhip_han_muc`): cả 5 lần `71 passed`, không fail chập chờn; không bỏ qua test nào.

## Ghi chú triển khai (17/10/2026, I1)

Đối chiếu với `main` `59f8281`. Em không chạy lại test (I1 chỉ sửa tài liệu).

**Lần ghép:**

| Merge | Nội dung | `pytest` trước → sau |
|---|---|---|
| `4f55ec2` | Plan P1 + 3C-B (`1c33b10`) và plan bs-78r.10 Q1/Q2 (`f295eba`) — chỉ tài liệu | — |
| `0e33fbf` | Mã P1 T1–T5, 3C-B T6–T9, Q1-a, Q1-b, Q2 (nhánh `p1/code`, đã nhận `main` `9ee1ed3` qua `49108d1` trước khi ghép) | 2566 → **2650** (+84) |

Commit mã: T1 `f21b069`, T2 `f19e5e3`, T3 `482a29f`, T4 `c6c811f`, T5 `b028676`, T6 `edf1a71`, T7 `e7005e0`, T8 `87d27fe`, T9 `2ece816`; Q1-a `1ebb493`, Q1-b `e51ea65`, Q2 `fead2e1`. Thân commit không ghi số test. 2566 là `main` sau 3c đợt 7 (`9ee1ed3`); 2650 là N₀ của 3c đợt 8 đo trên `0e33fbf`. Delta +84 đúng bảng "Sơ đồ đợt" (+69 P1/3C-B, +15 Q1/Q2).

**Chỗ lệch khi code:** không ghi nhận. Khác duy nhất là nền: plan chạy thử trên `5da881e` (2242 → 2326); khi ghép, `main` đã có V1, 1a-2, 4d và 3c đợt 7. Em không so lại từng dòng mã với plan.

**Hợp đồng cho 3c (H1–H8):** 3c áp ở đợt 8 (`59f8281`). H2, H6, H7 xong → rủi ro mục 2 ở trên **đóng ở mức offline**. H5 áp có lệch chủ đích: `kiem_lai(chu_dau=True)` chỉ cho tiến trình con của harness (plan 3c, G-D5). H1 còn `ban_chep._chay` (xem dưới).

**Còn lại — bead đã mở (con của `bs-863`):**

| Bead | Việc | Nguồn |
|---|---|---|
| `bs-863.14` | `kiem_am`/`kiem_cong`/`kiem_cach_ly` còn `subprocess.run(timeout)` dưới `sudo`, cần tty cho mật khẩu (đang làm, 17/10) | Rủi ro mục 1 |
| `bs-863.15` | `mo_coi` dọn theo file pid, không kiểm thời điểm khởi động — PID tái dùng sau reboot | Rủi ro mục 3 |
| `bs-863.16` | `theo_doi.py` còn `join()` không hạn | Rủi ro mục 4 |
| `bs-863.17` | `codex login status` của `tram tho kiem` chạy dưới tài khoản quản lý | Rủi ro mục 8 |
| `bs-863.18` | `chay_gioi_han` nhận `stdin=` để `ban_chep._chay` đi qua primitive (H1 còn mở) | Plan 3c, "Áp hợp đồng P1" H1 |
| `bs-863.19` | `chay_han_tong` bắt `KeyboardInterrupt` — Ctrl-C ở CLI cha không để con chạy tiếp | Plan 3c, review chu kỳ 2 đợt 8 |

Rủi ro mục 5, 6, 7, 9 giữ nguyên (không bead riêng). Mục 10: các sửa chu kỳ 3 vẫn chờ review Codex.

**Cổng đang chờ:** G3 (đo trên macOS thật: `use_pty`, cây `sudo`, `kill -1`; kịch bản ở plan 3c Task 9 và sổ tay), G4 (S6), G5 (quota dưới principal thật, xem plan bs-78r.10 và sổ tay). Tất cả **CHƯA CHẠY**.
