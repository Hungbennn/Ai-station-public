# DEPLOY — cài và vận hành trạm trên Mac của Đại ca

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-18`

## Mục đích và sở hữu
Sở hữu **quy trình chung**: cài và gỡ dịch vụ launchd, cấu hình `~/.tram`, tên mục Keychain, `tailscale serve`,
sao lưu, đường lui, kiểm sau cài. Tier 2: chỉ đọc khi task là cài, chạy thật, hạ tầng.
Không sở hữu: **cổng chạy thật G0–G7 và kịch bản từng bước** — ở sổ tay
[`handovers/2026-10-15-so-tay-chay-that.md`](handovers/2026-10-15-so-tay-chay-that.md) và phụ lục mới nhất
[`handovers/2026-10-17-cong-sau-review-dot7.md`](handovers/2026-10-17-cong-sau-review-dot7.md) (phụ lục thắng sổ
tay ở phần nó ghi) · trạng thái máy hiện tại (`CURRENT_STATE.md`) · lệnh cấm (`AGENT_RULES.md` §11).
Ghi chú riêng của từng đợt chạy thật để ở bàn giao của đợt đó, không nối vào đây.

> Nguyên tắc không thương lượng: **Đại ca cho phép từng kịch bản trước khi chạy · sao lưu trước khi đụng dữ liệu
> thật · chốt đường lui trước lệnh đầu tiên · kiểm và ghi bằng chứng sau khi xong.**

**Hiện trạng (17/10/2026):** chưa cổng chạy thật nào đạt ở mức OS. Máy B chỉ đang chạy `vn.tram.bao-tin` và
`vn.tram.nho`. Chi tiết và cập nhật: `CURRENT_STATE.md` mục Môi trường.

## 0. Phải quyết trước khi chạy lệnh đầu tiên
- Đúng cổng nào trong sổ tay, cổng trước đã đạt chưa (có bằng chứng: lệnh, giờ, kết quả).
- Kịch bản cụ thể đã trình và Đại ca cho phép **riêng kịch bản đó** (`AGENT_RULES.md` §2, mục 8 kill list).
- Lệnh có `sudo`, tạo user, Keychain, `launchctl` ghi: **Đại ca tự gõ** trong Terminal.app; agent chỉ soạn.
- Đường lui (mục 6) và bản sao lưu (mục 5) đã sẵn.

## 1. Chuẩn bị máy
**Máy B** (Mac mini 24/7, trạm chủ, chạy dưới tài khoản trạm của Đại ca):
- `uv`, repo trạm ở `/Users/dai-ca/Developer/Ben Station`. Dịch vụ chạy `uv run --project <repo> tram …`.
- `bd` ở `~/.local/bin` — plist tự thêm đường này vào `PATH` vì launchd không có sẵn (`tram/chu/launchd.py`).
- Tắt chế độ ngủ (System Settings → Energy); lệnh cài cảnh báo nếu `pmset` còn bật ngủ.
- Tailscale đã đăng nhập (danh tính Đại ca cho API ghi).
- Memory: Ollama nghe **chỉ** `127.0.0.1:11434`, model bge-m3; `tram chu cai-dat --nho` cài nếu thiếu.
- Máy thợ trên B (khi tới G3): user `tram-tho` (quản lý thợ), user principal mỗi khe, `tram-kiem` — do
  `tram chu cai-dat-tho` tạo, cần `sudo`.

**Máy A** (Mac làm việc): Tailscale, skill phỏng vấn trong `ky-nang/`, hook trong `may-a/`. Cài theo cổng G6.

**Mac thợ từ xa:** `uv tool install` trạm, chạy thẳng `~/.local/bin/tram`; ghép bằng `tram chu cap-ma <may_id>`
trên B rồi `tram tho dang-ky` trên máy thợ (mã dùng một lần, hết hạn 10 phút).

## 2. Cấu hình và bí mật
**`~/.tram/cau-hinh.yaml`** (máy B; không chứa bí mật; thiếu file thì dashboard chỉ đọc, không báo tin). Các khối:

| Khối | Dùng cho | Đọc ở |
| --- | --- | --- |
| `dai_ca_logins`, `ten_may_b`, `dashboard_url` (phải `https://`) | danh tính ghi, Origin, link trong tin | `tram/cau_hinh/tram.py` |
| `telegram` (`chat_id`, `gio_yen_lang`) | báo tin | `tram/cau_hinh/tram.py` |
| `han_muc`, `tho` | ngưỡng hạn mức, trần lượt, cầu dao (có giới hạn hợp lệ) | `tram/cau_hinh/tram.py` |
| `cach_ly` (`kenh_ghi`, `socket`, `db_nghiep_vu`, `tram_kiem`) | kênh ghi, principal kiểm lại | `tram/cau_hinh/cach_ly.py` |
| `giao_viec` (`bat`, `chu_ky_giay`, `thu_muc_kiem`) | công tắc giao việc | `tram/cau_hinh/giao_viec.py` |
| `cong_bo` (`phuong_an`, `kho_tho`) | cách công bố nhánh | `tram/cau_hinh/cong_bo.py` |
| `usage` (`ccusage`, `ccusage_phien_ban`, `gia_usd_moi_trieu_token`) | màn Usage | `tram/cau_hinh/usage.py` |
| `ma_dai_ca_sha256`, `dieu_phoi_ma_sha256` | bản băm mã, đặt bằng `tram chu dat-ma-dai-ca`, `dat-ma-dieu-phoi` | `tram/nho/ma_dai_ca.py` |

Khoá thiếu → giá trị an toàn (tắt, `kenh_ghi: header`, chưa chọn công bố; `du-an/*.yaml` thiếu `bat_ghi` = tắt
ghi, `tram/cau_hinh/bat_ghi.py`). `giao_viec.bat`, `bat_ghi` và ngưỡng hạn mức thuộc kill list. Máy thợ có
`~/.tram/tho.yaml` riêng (`tram/tho/cau_hinh.py`). Dự án con: `du-an/<ten>.yaml` trong repo, tạo bằng
`tram du-an them <repo>` (mặc định `bat_ghi: false`), gỡ khối trạm bằng `tram du-an go <repo>`.

**Keychain — chỉ tên mục**, của tài khoản trạm trừ khi ghi khác. Đại ca tự tạo qua Terminal.app; agent không đọc:

| Mục | Ai dùng |
| --- | --- |
| `tram-anthropic-api-key` | chấm cột, memory tách/gộp (`tram/llm/claude.py`) |
| `tram-telegram-bot-token` | `vn.tram.bao-tin` |
| `tram-nho-token` | memory service 7710; tạo ngẫu nhiên lúc `cai-dat --nho` |
| `tram-noi-bo-token` | API nội bộ, memory tra phiếu; tạo ngẫu nhiên lúc `cai-dat --nho` |
| `tram-tho-token` | tiến trình quản lý thợ (Keychain của tài khoản quản lý thợ) |
| `tram-dieu-phoi-ma` | hook điều phối, **Keychain máy A** |

Agent và mã dự án chạy dưới principal khác, không có các mục này.

## 3. Dịch vụ launchd
Nhãn và lệnh lấy từ `tram/chu/launchd.py`, `tram/chu/dich_vu_tram.py`, `tram/chu/cai_dat.py`, `tram/chu/cai_dat_nho.py`,
`tram/chu/cai_dat_tho.py`, `tram/tho/launchd_tho.py`. Log ở `~/.tram/log/<tên>.log`.

| Nhãn | Chạy | Kiểu | Cài bằng |
| --- | --- | --- | --- |
| `vn.tram.quet` | `tram quet --ghi` | mỗi 120 giây | `tram chu cai-dat --dich-vu quet` |
| `vn.tram.api` | `tram api` (127.0.0.1:7700) | thường trực | `tram chu cai-dat --dich-vu api` |
| `vn.tram.bao-tin` | `tram bao-tin` | thường trực | `tram chu cai-dat --dich-vu bao-tin` |
| `vn.tram.sao-luu` | `tram chu sao-luu` | hằng ngày 03:15 | `tram chu cai-dat --dich-vu sao-luu` |
| `vn.tram.nho` | `tram nho chay` (127.0.0.1:7710) | thường trực | `tram chu cai-dat --nho` |
| `vn.tram.tho` | `tram tho chay` | thường trực | B: `tram chu cai-dat-tho` (LaunchDaemon có `UserName`); Mac thợ: plist `tram/tho/launchd_tho.py` |

Sau reboot, thợ tự chờ tram-api (không giới hạn — tram-api chỉ lên khi Đại ca đăng nhập Mac) và đăng nhập nền
hai khe (tối đa ~15 phút; hết hạn thì nhắc và giữ tắt).

- Bốn dịch vụ đầu là LaunchAgent trong `~/Library/LaunchAgents`, miền `gui/<uid>`. `tram chu cai-dat` cài **đúng
  dịch vụ chọn** bằng `--dich-vu` (lặp lại được, không có mặc định; `--nho` là lệnh riêng, không đi cùng `--dich-vu`).
  Chọn `quet` (chạy `--ghi`): kế hoạch in từng dự án sẽ bị ghi / chỉ đọc; không đọc được `du-an/*.yaml` hay khoá
  `bat_ghi` của một dự án thì thoát 2, không cài gì.
- Mọi lệnh cài in kế hoạch (file sẽ ghi, bước, lệnh sẽ chạy, cảnh báo) rồi chờ gõ `dong-y`. `cai-dat --dich-vu`:
  ghi plist kèm **biên nhận** `~/.tram/dich-vu/<nhãn>.json` (sha256 plist — chứng cứ sở hữu cho lệnh gỡ), siết quyền
  `~/.tram` theo phạm vi `siet-quyen` bên dưới, rồi `launchctl bootout` (bỏ qua mã lỗi) và `launchctl bootstrap`.
- Hạn từng tích hợp: `MODULES.md` mục Tích hợp ngoài (Keychain, launchctl, tải/cài memory). Quá hạn trong
  thực hiện kế hoạch → dừng, lệnh sau không chạy, thoát 3; cần đối soát phần đã làm trước khi thử lại.
  Timeout của subprocess không chứng minh toàn bộ cây con đã dừng; xác nhận ở cổng sổ tay.
- Thường trực dùng `KeepAlive` chỉ khi thoát lỗi: `tram bao-tin` thoát mã 0 khi thiếu token hay `chat_id` nên launchd
  **không tự bật lại** — cấu hình xong, Đại ca chạy `launchctl kickstart -k gui/<uid>/vn.tram.bao-tin`.
- Sau khởi động máy, Keychain còn khoá tới khi đăng nhập: `vn.tram.nho` không đọc được token, tự dừng; đăng nhập
  xong kickstart lại. tram-api đọc `tram-noi-bo-token` một lần ở yêu cầu đầu; đổi token thì kickstart `vn.tram.api`.
- Xem (chỉ đọc): `tram chu trang-thai`, `launchctl list | grep vn.tram`, log trong `~/.tram/log/`.
- Quyền `~/.tram` cũ: `tram chu siet-quyen` (liệt kê, chờ `dong-y`); phạm vi bảo đảm và mục bỏ qua ở
  `ENGINEERING_STANDARDS.md` mục Quy tắc bảo mật. Cài `--dich-vu` gọi bước này trước khi nạp dịch vụ.

**Gỡ:**
- Máy thợ: `tram chu go-cai-dat-tho [--xoa-nha]` — chỉ gỡ thứ sổ cài ghi đã tạo, còn đúng định danh; user luôn
  giữ nhà trừ khi `--xoa-nha`. Thu hồi token và phiếu của một máy: `tram chu go-may <may_id>`.
- Dịch vụ trên B: `tram chu go-dich-vu --dich-vu <api|quet|bao-tin|sao-luu|nho>` (lặp lại được; liệt kê, chờ
  `dong-y`). Chỉ gỡ dịch vụ có biên nhận khớp plist (cài trước khi có biên nhận: chạy lại `cai-dat` trước); thiếu hay
  lệch chứng cứ → từ chối cả kế hoạch. Đang nạp từ plist khác → dừng, không bootout. Sau `bootout` đọc lại
  `launchctl print`: chỉ khi đã vắng mới cất plist vào `~/.tram/go-dich-vu/` (không xoá, không ghi đè); còn nạp hay
  không rõ → dừng, plist giữ nguyên. Nguồn: `tram/chu/go_dich_vu.py`, `tram/chu/chung_cu_go.py`.

## 4. Tailscale serve
tram-api và memory chỉ nghe localhost; ra tailnet **chỉ** qua `tailscale serve`. Trạm chỉ **in** lệnh, Đại ca tự chạy
khi cổng cho phép: `tailscale serve --bg --https=443 http://127.0.0.1:7700` (kiểm cú pháp với bản Tailscale trên
máy B; nguồn `LENH_TAILSCALE_SERVE` trong `tram/chu/cai_dat.py`). Đường `/nho` → `127.0.0.1:7710` cho MCP máy A
chờ spike N2. `dashboard_url` trong cấu hình phải là địa chỉ `https://` của tailnet.

## 5. Sao lưu và khôi phục — chốt TRƯỚC khi chạy
- **Kho sự kiện:** `tram chu sao-luu [--giu 14]` → `~/.tram/sao-luu/su-kien-<thời điểm>.db` (online backup có hạn,
  file mới độc quyền 600 trong thư mục 700), giữ 14 bản; `vn.tram.sao-luu` chạy 03:15 mỗi ngày khi đã cài. Mã mới
  nâng số phiên bản cấu trúc kho thì để bản `truoc-nang-v<cũ>-v<mới>-*.db` cạnh đó.
- **Khôi phục kho sự kiện:** ghi lại dịch vụ đang nạp; dừng mọi bên mở kho, kể cả CLI. Chỉ gỡ dịch vụ có biên nhận
  hợp lệ theo mục 3; thiếu chứng cứ thì Đại ca dừng theo kịch bản sổ tay, không cài/bật thêm để lấy biên nhận.
  Chạy `tram chu khoi-phuc-su-kien <tên bản trong ~/.tram/sao-luu>`: kiểm toàn vẹn/phiên bản/cấu trúc, khoá bảo trì,
  chép kho cũ ra `truoc-khoi-phuc-*.db`, thay và so vân tay. Chỉ khởi động lại dịch vụ đã chạy trước bảo trì và được
  duyệt ở cổng; giữ dịch vụ vốn tắt. Nguồn: `tram/chu/khoi_phuc_su_kien.py` (khoá từ chối khi còn bên mở kho WAL).
- **Memory:** `vn.tram.nho` tự bảo trì mỗi ngày sau 3 giờ sáng giờ VN: thăng cấp, dọn, chụp LanceDB + nhật ký thao
  tác cùng một điểm → `~/.tram/sao-luu/nho-<thời điểm>`, giữ 14 bản. Khôi phục: dừng dịch vụ
  (`launchctl bootout gui/<uid>/vn.tram.nho`), `tram nho khoi-phuc <bản>`; bản đang có được giữ lại, không xoá.
- **Beads của repo trạm:** `.beads/backup/` — xem `BEADS.md`. Beads dự án con: sao lưu theo dự án đó.
- Đổi dữ liệu thật: sao lưu trước, chạy thử không ghi, đối chiếu sau (`AGENT_RULES.md` §14).

## 6. Đường lui chung
Đường lui riêng của từng cổng (thu hồi tiến trình, dọn lịch, gỡ principal) ở phụ lục cổng mục "Thu hồi và đường lui".
1. **Dừng khẩn cấp:** `tram chu estop` (vòng quét, tick giao việc, cấp phiếu, thợ đều dừng); bỏ: `tram chu tiep-tuc`.
2. **Tắt công tắc:** `giao_viec.bat: false`; dự án về `bat_ghi: false`; khe: `tram tho tat-khe <khe>`.
3. **Dừng dịch vụ:** `launchctl bootout gui/<uid>/<nhãn>` (Đại ca gõ); gỡ hẳn: `tram chu go-dich-vu` (mục 3).
4. **Thu hồi máy thợ:** `tram chu go-may <may_id>`; gỡ cài đặt thợ: `tram chu go-cai-dat-tho`.
5. **Dữ liệu:** khôi phục từ mục 5. Cổng kiểm lại đã đóng thì **chỉ Đại ca mở lại** sau đối soát (D49).
6. **Dừng đội ngũ thợ B:** `cong-cu/doi_ngu_b.py tat-giao` — ngừng phát việc mới, giữ nguyên `bat_ghi`
   ben-station để máy A vẫn gửi yêu cầu được; `cong-cu/doi_ngu_b.py dung` — tắt hai khe dừng mềm, chờ hết
   phiếu B rồi bootout + disable `vn.tram.tho`.

## 7. Kiểm sau khi cài
- `tram chu trang-thai`: estop, lần quét cuối, lỗi gần nhất mỗi dự án. Đọc log `~/.tram/log/`.
- Memory: `tram nho tim "thử" --du-an <tên>`; `lsof -nP -iTCP:11434 -sTCP:LISTEN` phải chỉ thấy `127.0.0.1` (thấy
  `*:11434` thì dừng, báo).
- Máy thợ: `tram tho kiem` (xanh/vàng/đỏ).
- Dashboard: mở qua tailnet; thử một thao tác ghi **thiếu** danh tính phải bị 403.
- Ghi bằng chứng (lệnh, giờ, kết quả, người cho phép) vào sổ tay cổng, mục "Ghi bằng chứng".
