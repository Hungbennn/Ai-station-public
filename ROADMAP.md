# Bảng ý tưởng và mục tiêu

Đây là bản đồ cho người muốn góp tay. Mỗi ô ghi rõ **vì sao đáng làm**, **khó cỡ nào** và **bắt đầu đọc từ đâu**.
Chọn một ô, mở issue nói bạn nhận, rồi làm theo [CONTRIBUTING.md](CONTRIBUTING.md).

Độ khó: 🟢 làm quen được trong một buổi · 🟡 cần đọc hiểu một khối · 🔴 chạm bảo mật, tiến trình hay kiến trúc.

---

## Đích đến

Một trạm mà **bất kỳ ai có một chiếc Mac** cũng dựng được, để cả đội agent AI làm việc an toàn cho mình suốt
ngày đêm, và người chỉ phải quyết những việc thật sự cần người quyết.

## Các cột mốc

| # | Cột mốc | Đạt khi | Hiện tại |
| --- | --- | --- | --- |
| **M1** | **Trọn vòng chạy thật** | Một feature đi hết đường: phiếu yêu cầu → spec → duyệt → code → QC → kiểm lại trong sandbox → PR → merge, trên máy thật, không ai can tay giữa chừng. | Đang chạy trên chính repo này: hai khe Claude nhận việc, QC, tự mở PR. Đội thợ đã qua cổng R0–R4, R6; cổng khởi động lại máy (R5) đã sửa, chưa đo lại. |
| **M2** | **Mọi cổng hệ điều hành đạt** | Cổng G0–G7 trong [sổ tay chạy thật](docs/handovers/2026-10-15-so-tay-chay-that.md) đều có bằng chứng. | G3, G4 đạt; G6 đạt trừ G6.7; **G5 (Codex dưới tài khoản riêng) và G7 (dự án thật thứ hai) chưa chạy.** |
| **M3** | **Tự merge + tự deploy** | Bật trên ít nhất một dự án; deploy hỏng thì tự lùi, có bằng chứng chạy thật. | Đã code và ghép `main`, công tắc đang **tắt**. |
| **M4** | **Chọn model theo độ khó** | Việc nhỏ tự vào khe Sonnet, việc lớn vào khe Opus, chọn cả mức effort. | Đang bật thử cho repo này; phần effort theo cỡ đang làm. |
| **M5** | **Người lạ dựng được trạm** | Một người ngoài làm theo tài liệu, dựng trạm trên Mac của họ và chạy được M1. | Chưa có. Cài đặt hiện còn gắn với máy của người chủ trạm. **Cộng đồng là người đo được mốc này.** |
| **M6** | **Trạm chung nhiều người** | Mỗi người có dự án, quyền, hạn mức, dữ liệu và bí mật tách biệt. | Giai đoạn kế tiếp, chưa có spec. Cửa ghi passkey đã thiết kế sẵn danh sách người + quyền. |

---

## 🛠 Sửa ngay: việc tốt để làm quen

| Việc | Vì sao đáng làm | Độ khó | Bắt đầu từ |
| --- | --- | --- | --- |
| **Bộ test từ chối chạy khi đường dẫn repo có dấu tiếng Việt** ([#1](https://github.com/Hungbennn/Ai-station-public/issues/1)) | `tests/conftest.py` so đường dẫn `git` giả bằng chuỗi; macOS trả một bên dạng Unicode NFC, một bên NFD, nên clone vào `~/Dự án/…` là test thoát 4. Dự án tiếng Việt mà vấp chữ tiếng Việt thì hơi buồn. | 🟢 | `tests/conftest.py:15-18`, `tests/chan_host/chay.sh` |
| **67 test đỏ trên máy không phải máy trạm** ([#2](https://github.com/Hungbennn/Ai-station-public/issues/2)) | Các test kiểm lại, bản chép (`test_ban_chep*`, `test_kiem_lai*`, `test_nghiem_thu_kiem`…) gọi tài khoản `tram-kiem` và toolchain `/usr/local/tram/toolchains/` thật. Trên máy người đóng góp chúng đỏ, làm người mới tưởng mình làm hỏng. Cần đánh dấu riêng và tự bỏ qua có lý do khi thiếu môi trường, giống cách nhóm test G3 đang làm. | 🟡 | `tram/kiem/toolchain.py`, `tests/conftest.py` (marker `g3`), `tests/test_ban_chep_cay.py` |
| **Văn phòng 3D nặng 878 KB** ([#3](https://github.com/Hungbennn/Ai-station-public/issues/3)) | Bundle `VanPhong-*.js` chứa nguyên three.js; Vite cảnh báo chunk quá lớn. Tách nhỏ, nạp trễ hay bỏ phần thừa đều giúp dashboard mở nhanh hơn. | 🟢 | `frontend/src/van_phong/`, `frontend/vite.config.js` |
| **Đồng bộ lại `FEATURE_SPEC.md`** ([#4](https://github.com/Hungbennn/Ai-station-public/issues/4)) | Bảng feature dừng ở 17/10: vẫn ghi V2 là "đề xuất" trong khi V2–V5, tự merge/deploy, passkey, đội ngũ thợ đã code xong. Người mới đọc sẽ hiểu sai. | 🟢 | [docs/FEATURE_SPEC.md](docs/FEATURE_SPEC.md) đối chiếu [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) |
| **Link gãy tới nhật ký phiên** ([#5](https://github.com/Hungbennn/Ai-station-public/issues/5)) | Bản public không đăng nhật ký phiên làm việc, nên vài link trong `docs/plans/` và `docs/quyet-dinh/` trỏ vào khoảng không. Viết một kịch bản dò link gãy rồi sửa hoặc chú thích. | 🟢 | `docs/handovers/README.md` |
| **Chạy thử trên Mac của bạn và báo lỗi** | Mọi lỗi "chỉ xảy ra trên máy người khác" đều quý. Chạy test, chạy dashboard dữ liệu giả, ghi lại chỗ vấp. | 🟢 | [README.md](README.md) mục *Bắt đầu trong 10 phút* |

## 🎯 Mục tiêu gần

| Việc | Vì sao đáng làm | Độ khó | Bắt đầu từ |
| --- | --- | --- | --- |
| **Hướng dẫn dựng trạm cho người lạ** (mốc M5) | Hiện chỉ người chủ trạm cài được. Viết hướng dẫn từ máy trắng: tài khoản macOS cho thợ, Keychain, launchd, Tailscale, dự án đầu tiên. Ai làm được ô này mở cửa cho cả cộng đồng. | 🟡 | [docs/DEPLOY.md](docs/DEPLOY.md), `tram/chu/`, `cong-cu/` |
| **Đưa kênh ghi `header` về hưu** | Kênh header là tạm: header giả được từ localhost. Đích là passkey (đã có) cùng unix-socket cho công cụ cục bộ. | 🔴 | [ADR-0004](docs/decisions/ADR-0004-danh-tinh-tailscale-kenh-ghi.md), `tram/api/bao_mat.py`, `tram/api/passkey*` |
| **Phiên bản schema cho memory** | `su-kien.db` có `PRAGMA user_version` và lối nâng cấp an toàn; `nhat-ky.db` của memory và LanceDB thì chưa. Đổi cấu trúc sau này sẽ khó nếu không làm sớm. | 🟡 | `tram/su_kien/phien_ban.py` (mẫu), `tram/nho/bang.py` |
| **Test cưỡng chế ranh giới package** | Đang có vòng import cấp package (`giao_viec ↔ tho`, `api ↔ chu`…) chạy được nhờ import trễ. Một test kiến trúc sẽ giữ không cho vòng mới mọc thêm, rồi gỡ dần vòng cũ. | 🟡 | [docs/MODULES.md](docs/MODULES.md) mục *Vòng import*, `tests/test_vong_import.py` |
| **Chạy thật cổng G5: Codex dưới tài khoản riêng** | Khe Codex phải đọc hạn mức và chạy đúng danh tính của khe, không lộ token. Mã đã có, chưa ai đo trên máy thật. | 🔴 | [sổ tay](docs/handovers/2026-10-15-so-tay-chay-that.md) mục G5, `tram/tho/han_muc_ranh.py`, `tram/chay_cli/codex/` |
| **Chạy thật tự merge + tự deploy** (mốc M3) | Code đã sẵn, chờ người dám bật trên một dự án thử và ghi lại bằng chứng. | 🔴 | [openspec/changes/tu-merge-tu-deploy/](openspec/changes/tu-merge-tu-deploy/), `tram/deploy/`, `tram/tu_dong/` |
| **Agent tự cập nhật danh sách việc** | Agent phát hiện việc mới thì đề nghị, trạm lọc rồi mới ghi. Code đã có, đang tắt; cần chạy thật và tinh chỉnh bộ lọc. | 🟡 | [openspec/changes/agent-tu-cap-nhat-viec/](openspec/changes/agent-tu-cap-nhat-viec/), `tram/de_nghi/` |

## 🚀 Ý tưởng lớn: cần thảo luận trước khi code

Những ô này đổi kiến trúc hay đổi luật. Hãy mở issue thảo luận và viết đề xuất theo [OpenSpec](docs/OPENSPEC.md)
trước, đừng gửi PR thẳng.

| Ý tưởng | Vì sao hấp dẫn | Câu hỏi còn mở |
| --- | --- | --- |
| **Trạm chung nhiều người** (mốc M6) | Một trạm cho cả nhóm: mỗi người dự án, quyền, hạn mức, bí mật riêng. | Tách dữ liệu và bí mật ra sao mà không phá sáu bất biến? |
| **Subagent cho vai coder và spec** | Agent chia nhỏ việc cho subagent, làm nhanh hơn. QC vẫn giữ một agent. | Lệnh cấm và quyền vai có áp đúng vào subagent không? Cần đo trước (spike S4). |
| **Thêm loại agent mới** | Trạm hiện chạy Claude Code và Codex. Thêm CLI agent khác mở rộng lựa chọn hạn mức. | Mỗi CLI cần bản giả cho test, đọc hạn mức, quyền theo vai. Xem `tram/chay_cli/`. |
| **Văn phòng 3D sống động hơn** | Nhân vật đi lại khi đổi việc, hiệu ứng khi PR được merge, phòng theo từng dự án. Làm cho việc "canh agent" thành vui. | Giữ CSP chặt và chế độ giảm chuyển động. Xem [DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md). |

## Ngoài phạm vi hiện tại

Để khỏi mất công, đây là những thứ dự án **chủ động không làm** ở giai đoạn này (nguồn:
[docs/PROJECT.md](docs/PROJECT.md)):

- Chạy trên cloud, Linux hay Windows: trạm dựa vào tài khoản macOS, Seatbelt, launchd và Keychain.
- Khung chat hay IDE: trạm không thay app Claude, nó lo phần chạy.
- Tích hợp Jira.

Bạn vẫn có thể mở issue thảo luận nếu thấy một điểm trong số này đáng xem lại.
