# CURRENT_STATE
> Bộ nhớ ngắn hạn của agent. Ghi **trạng thái hệ thống**, không ghi việc và không ghi nhật ký.
> Cập nhật cuối mỗi phiên — **viết đè**, không nối thêm. Trần 150 dòng **và mỗi dòng ≤ 300 ký tự**.
> **Việc còn dở nằm ở Beads (`bd ready`), không chép vào đây.** Chi tiết từng đợt ở `docs/handovers/`.
> Cập nhật: 2026-10-21 (tối).

## Đang ở đâu
- **2026-10-21** — tối: **giao việc theo cỡ BẬT** cho ben-station (`45ed7b1`), khe khai Sonnet/Opus; việc nhỏ `bs-ie0` chạy đúng Sonnet. Đang làm: effort theo cỡ, tăng tốc test (bỏ G3 + 6 nhân).
- **2026-10-21** — chiều: **đội ngũ thợ B chạy thật**: R0–R4, R6 ĐẠT; `vn.tram.tho` chạy, 2 khe Claude (token file), giao việc BẬT cho ben-station. R7 việc thử `bs-8zi`: code + Uq + QC đạt, chờ PR. R5 reboot chưa đo.
- **2026-10-21** — khuya: R5 reboot (thợ không tự lên → sửa); trạm mở PR + chặn Duyệt; chấm cột bật; test 6 nhân 2,5 phút; 6 lỗi đội ngũ lộ qua bs-ie0 đã sửa (bs-ie0 còn kẹt quyền xoá file).
- **2026-10-21** — rạng sáng: ghép main **đội ngũ thợ** (`67dd6aa`, 2 khe Claude trên B, sổ tay `cong-cu/doi_ngu_b.py`, ADR-0009) và **giao việc theo cỡ** (`49b167b`, mặc định tắt). Cả hai mới code + test offline; đội ngũ chờ chạy thật R0–R7 (`bs-2bd.12`).
- **2026-10-20** — ngày: bộ quản lý kiểm (Uq, `vn.tram.quan-kiem`) **chính thức**: G4 ĐẠT 5 lượt, Đại ca ký bằng chứng; reboot máy B đã kiểm (Uq, api, nho, bao-tin tự chạy). Code tự merge/deploy ghép main, công tắc TẮT. Ben-station `bat_ghi: true`.
- **2026-10-20** — repo GitHub riêng `Hungbennn/ben-station` (remote `github`); dashboard qua tailnet; máy A có passkey, hook điều phối, skill phỏng vấn. Chỉ mục GitNexus cho repo trạm (`.gitnexus/`, git bỏ qua).
- **2026-10-19** — G3 đo xong (lỗ submit→UID 501 khi bật từ phiên GUI → tách phiên bằng daemon system); D157–D162; siết đọc ghép main.
- **2026-10-18** — code + ghép TM-1…TM-4 (tự merge/deploy, giao diện Tự động), TC (agent tự cập nhật việc), V2–V5, passkey (D135); G6 ĐẠT trừ G6.7; D69–D157.
- **2026-10-17** `57159d6` — dựng bộ docs theo khung (định tuyến, Tầng 1/2, 8 ADR hồi tố, OpenSpec 1.14.0); review Codex đợt 7.
- **2026-10-16/17** `59f8281` — code xong đợt 6–8: cách ly 3c, vòng đời tiến trình P1, hạn mức đúng principal, 4d.

**Bàn giao gần nhất:** [R5, mở PR, chặn Duyệt, sửa đội ngũ](handovers/2026-10-21-khuya-sua-doi-ngu-mo-pr.md)

## Status
- **Commit:** xem `git log -1`.
- **Test** (21/10 khuya, ngoài sandbox, main): cả bộ **4819 passed** (+1 chập chờn, đã sửa), **2 phút 34 giây** 6 nhân; G3 (123 test) tắt mặc định, `TRAM_TEST_G3=1` chạy kèm. `pytest-xdist` 3.6.1 chỉ cài riêng `.venv` — KHÔNG vào uv.lock.
- **Mức hoàn thành:** mọi lát đã code (0+1a … 4d, P1, quota, V1–V5, TM-1…4, TC, passkey, Uq). Thêm đội ngũ thợ B và giao việc theo cỡ (21/10). Khoảng 85% sản phẩm; còn chạy thật đội ngũ + theo cỡ, nối HR Codex.
- **Chạy thật:** G3 xong, **G4 ĐẠT (chính thức)**, G6 ĐẠT trừ G6.7; G5/G7 chưa. Nguồn: sổ tay `docs/handovers/2026-10-15-so-tay-chay-that.md` và `docs/handovers/2026-10-20-g4-chay-that-dat.md`.
- **Module:** 22+ package trong `tram/`, SPA trong `frontend/`. Bản đồ: `MODULES.md`.

## Working features
- Danh sách lát và trạng thái: [FEATURE_SPEC.md](FEATURE_SPEC.md). Đa số mới ở mức **đã code + test offline**.
- Đang chạy thật trên máy B: `vn.tram.api` (dashboard + nhận yêu cầu máy A qua tailnet), `vn.tram.nho` (7710), `vn.tram.bao-tin`, `vn.tram.quan-kiem` (Uq, daemon system, cổng kiểm mở).
- Đội ngũ B **đang bật**: `vn.tram.tho` (daemon system, UserName tram-tho), khe `B/claude-1`, `B/claude-2`; `giao_viec.bat: true`, `du_an: [ben-station]`; chấm cột **bật** (`vn.tram.quet`, 21/10); trạm **tự mở PR** (`phu_thuoc_4c.github`), Đại ca merge (merge commit), Duyệt chỉ đóng khi mã đã vào main. Tự merge/deploy, TC tắt. Reboot: thợ tự chờ tram-api (sửa 21/10, chưa đo lại).

Lệnh cấm, kiểm chứng → `AGENT_RULES.md` §11, §13 · sự cố đã trả giá → `ENGINEERING_STANDARDS.md` · cài/gỡ dịch vụ → `DEPLOY.md`.

## Recent decisions
- D1–D162 trong `docs/quyet-dinh/`; 8 ADR hồi tố trong `docs/decisions/`. QĐ của change đang làm nằm trong `openspec/changes/<tên>/QUYET-DINH.md` (đội ngũ: QĐ1–4=A, QĐ5=B; theo cỡ: QĐ1–3,5=A, QĐ4=C).
- Hay quên: cửa ghi thật là **passkey** (đã đăng ký trên máy A); kênh `header` chỉ là tạm. Tắt giao việc **không** tắt `bat_ghi` ben-station (máy A vẫn gửi yêu cầu được).

## Môi trường & vận hành
- **Máy B** (Mac mini 24/7, trạm chủ): launchd nạp `vn.tram.api`, `vn.tram.nho`, `vn.tram.bao-tin`, `vn.tram.quan-kiem`. `vn.tram.tho` **đang chạy** (dừng: `cong-cu/doi_ngu_b.py tat-giao` rồi `dung`). Chưa nạp `vn.tram.quet`, `vn.tram.sao-luu`.
- **Tài khoản máy B:** `tram-tho` (504), `tram-khe1` (502), `tram-khe2` (506), `tram-kiem` (503), `tram-quan-kiem` (505). Token Claude khe: `/Users/tram-kheN/claude/oauth-token` (0600); token máy B: file của tram-tho.
- **Runtime thợ:** `/Users/Shared/tram-tho-code`; bộ thư viện root `/usr/local/tram/deps/ben-station/<digest>/`.
- **`~/.tram/cau-hinh.yaml` máy B:** `telegram`, `ten_may_b`, `dashboard_url`, `dai_ca_logins`; giao việc tắt; `cong_bo.phuong_an` chưa chọn; `usage.ccusage` chưa cài.
- **Dự án:** `du-an/ben-station.yaml` `bat_ghi: true`; `du-an/hr-codex.yaml` `bat_ghi: false` (máy B chưa có repo HR — phòng máy chủ báo đỏ beads hr-codex, để tới lượt HR).
- **Tailscale:** máy A và B đã đăng nhập; B mở Tailscale qua Login Items, chỉ lên sau khi đăng nhập máy B. Dashboard: `https://may-b.tailnet-vi-du.ts.net`.
- **CLI:** Claude Code 2.1.227 ở `/opt/homebrew/bin/claude` (thợ đọc/chạy được); Codex CLI `/opt/homebrew/bin/codex`, đăng nhập ChatGPT; GitNexus 1.6.12 (`gitnexus analyze --skip-agents-md --skip-skills`).
- **Mục Keychain, khối cấu hình, dịch vụ:** [DEPLOY.md](DEPLOY.md). **Sao lưu memory:** `~/.tram/sao-luu/`.
- **Test:** `tests/chan_host/chay.sh -q` (KHÔNG `uv run pytest` trần); `cd frontend && npm run kiem && npm run build && npm run kiem-dist`.
- **Xem giao diện với dữ liệu giả:** `uv run --offline python tests/chay_thu_giao_dien.py 7798 --dai-ca` rồi mở `http://127.0.0.1:7798`.
- **Xem mockup:** trong `docs/mockup/2026-10-15-giao-dien/` chạy `python3 -m http.server 7801 --bind 127.0.0.1`.

## Việc còn dở
Tất cả ở Beads: `bd ready`, `bd list --status=open`. Phần 20% còn lại: epic `bs-2bd`. Quy ước ở [BEADS.md](BEADS.md).
