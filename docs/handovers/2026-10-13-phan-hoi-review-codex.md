# Phản hồi review Codex 13/10/2026 — bộ spec ben-station

Status: `ACTIVE`
Nguồn: `REVIEW-CODEX.md` và `GUI-CLAUDE.md` trong gói `ben-station-gui-claude-sua-spec-2026-10-13.zip` (Đại ca gửi 13/10; bản sao để ở `.handover/review-codex/`, git bỏ qua). Quyết định gốc: [docs/quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) (nguyên văn, đánh số #1–#21).

**Phạm vi đã làm:** chỉ sửa tài liệu trong `docs/` trên nhánh `main` (commit từng nhóm, không push). Không sửa mã, test, cấu hình, Beads dữ liệu dự án; không chạy spike, test hay gọi mạng. Đây là **kiểm tài liệu tĩnh** — không có gì ở đây là kết quả test hay triển khai đã kiểm chứng. Đại ca đã trả lời câu hỏi nhưng **toàn văn các spec vẫn chờ duyệt**.

Ký hiệu file: **KT** = `docs/specs/2026-10-12-tram-dieu-phoi-kien-truc.md` · **P0** = `docs/specs/2026-10-12-phan-0-1a-cham-cot.md` · **P2** = `docs/specs/2026-10-12-phan-2-dashboard.md` · **P3** = `docs/specs/2026-10-13-phan-3-may-tho-han-muc.md` · **P4** = `docs/specs/2026-10-13-phan-4-giao-viec.md` · **1b** = `docs/specs/2026-10-13-phan-1b-memory.md`. Số dòng theo bản sau sửa (commit `7e28d73`).

## 1. Xử lý 25 phát hiện

Cột "Xử lý": **Tiếp nhận** (làm theo đề xuất) · **Điều chỉnh** (làm, có đổi cách) · **Còn mở** (cần spike hoặc Đại ca chốt). Không có phát hiện nào Em không đồng ý.

### Chặn

| # | Xử lý | Lý do / cách làm | Vị trí sau sửa | Ca kiểm dự kiến |
|---|---|---|---|---|
| C01 | Tiếp nhận | Kiểm lại của trạm từng chạy mã test dưới quyền trạm; tách user cho thợ mà backend vẫn tin header trên TCP localhost là chưa đạt #3. Ghi ba nhóm quyền, lệnh kiểm (cả của trạm) chạy dưới principal thực thi, cổng trước 3a có kiểm chứng âm. Cơ chế proxy/socket ghi là **đề xuất cần spike** | KT:31; P2:48; P3:44, P3:252 (§7.3); P4:127 (§6.2 bước 1, 4) | test giả đọc khoá nội bộ, gọi API Duyệt với header giả, kết nối DB nghiệp vụ đều bị chặn; test hợp lệ chạy được với DB test |
| C02 | Tiếp nhận | Bỏ token khỏi môi trường không phải ranh giới hệ điều hành. Tách tiến trình quản lý (có credential) khỏi tiến trình agent/test (không credential); khe tách khe bằng quyền thật; quyền CLI là lớp bổ sung; thu hồi token máy vô hiệu phiếu và `ma_giao`. Cơ chế user/khe hay sandbox chọn sau S6 | P3:64 (§4), P3:98, P3:252 (§7.3 mục 1–3, 7) | khe A đọc/thay hàng đợi khe B, gọi `security`, gọi `tram` sau khi xoá `TRAM_GIAO_ID`, chạy git hook — đều không lấy được quyền |
| C03 | Tiếp nhận (dạng **đề xuất**) | `xin-push` + `--force-with-lease` chỉ giảm xung đột. Đề xuất ref tạm theo lượt, chỉ trạm cập nhật ref công bố bằng CAS; mọi bước sau dùng SHA trạm đã công bố. Có phương án lùi nếu GitHub không giới hạn được quyền theo mẫu ref. Chờ S7 và Đại ca chốt | KT:29, KT:150; P3:176 (§6.4), P3:501 (§14) | push treo qua lúc thu hồi; thu hồi không có push mới; remote nhận Git nhưng mất phản hồi HTTP |
| C04 | Tiếp nhận | Thêm kho phiếu bền: cấp phiếu một giao dịch, ràng buộc một phiếu hiệu lực/bead/khe, `request_id` cho mọi báo, công việc chờ bền, ID thao tác + đối soát cho Beads/Git. Thao tác ghi của dashboard có `ma_thao_tac` + `expected_version` | KT:151; P3:197 (§6.6); P2:203 (§12.3); P4 §5.4, §7.3 (P4:245) | hai nhịp tim đồng thời; HTTP gửi lại; restart sau `--claim`, sau `bd create`, sau `bao.xong`; phát lại không đếm ngân sách hai lần |
| C05 | Tiếp nhận | Một định nghĩa phiếu hiệu lực do phần 3 sở hữu; `giao.ket_thuc` chỉ là xác nhận. Kết thúc phiếu ghi yêu cầu chấm lại bền; 1a kiểm lại version bead + phiếu trước khi ghi | KT:152; P3:64, P3:156 (§6.3); P0:175, P0:244, P0:249; P4 §5.1 | kết thúc rồi crash trước xử lý; `updated_at` không đổi; 1a đang gọi LLM thì có phiếu mới; lỗi chấm không làm mất yêu cầu chấm lại |
| C06 | Tiếp nhận | Luật `chinh-thuc` mới: mọi tiêu chí đúng một lần, `dat: true`, bằng chứng; mọi lệnh bắt buộc của phiếu pass; timeout/lỗi khởi chạy/bị loại = fail; lệnh agent không thay lệnh bắt buộc. Bead thiếu `acceptance_criteria` máy đọc được thì không giao. **Mã hiện tại chưa có** — ghi ở P0 §11 | P0:123; P0:292 (§11); P3:285 (§7.5); P4:72, P4:141 | một tiêu chí `false` + lint pass; suite bắt buộc fail + test nhỏ pass; thiếu lệnh bắt buộc; tất cả lệnh bị bỏ; tiêu chí rỗng |
| C07 | Tiếp nhận | Bộ bằng chứng `(du_an, bead_id, giao_id, luot, commit_code, commit_ban_giao, digest_tieu_chi)`; QC chỉ được đổi `docs/handovers/**` so với commit đã kiểm; PR trỏ commit cuối đã xác minh; HEAD hoặc tiêu chí đổi → bằng chứng hết hiệu lực; Duyệt spec mang `expected_commit` + digest, khác → 409; xác nhận merge tay ở 2a ghi rõ là thao tác của Đại ca | KT:28 (Q6); P4:144 (§6.3), P4:161 (§6.4), P4:169, P4:193 (§6.7), P4:245 (§7.3); P2:78, P2:79 | QC lén đổi file nguồn; push mới sau QC đạt; dashboard mở spec A mà server nhận spec B; bàn giao mang SHA của bead khác |

### Quan trọng

| # | Xử lý | Lý do / cách làm | Vị trí sau sửa | Ca kiểm dự kiến |
|---|---|---|---|---|
| Q01 | Tiếp nhận | `cham_cot.thu_lai` vừa reset chuỗi lỗi vừa tạo yêu cầu chấm lại bền, độc lập `updated_at`; chỉ đánh dấu xong sau khi đã thử chấm | P0:244; P2:82, P2:217 (§12.5) | bead 3 lỗi không đổi nội dung, bấm thử lại → lượt sau chấm đúng một lần |
| Q02 | Tiếp nhận | Decision mà bead phụ thuộc `blocks` được đóng/mở lại/đổi `close_reason` → yêu cầu chấm lại bền (so snapshot decision giữa hai lượt). Phụ thuộc không có trong snapshot → fail-closed (mã hiện tại bỏ qua — P0 §11) | P0:195, P0:244 | đóng decision bằng `bd` tay chỉ đổi timestamp decision; mở lại decision; dependency ID thiếu |
| Q03 | Tiếp nhận | Spike được giao `code`; spike đi cột 3 qua kiểm đường dẫn cấm, bàn giao, SHA — không qua cổng lệnh hay QC. Phiếu spec và spike tài liệu không cần môi trường kiểm (`can_moi_truong_kiem`) | P4:71, P4 §4, P4:127 (bước 2), P4:174 (dòng 4); P3:137, P3:219 | spike tài liệu không test; spec khi dự án chưa có DB test; spike đòi chạy mã |
| Q04 | Tiếp nhận | Prompt chấm v2 đưa `{id, title, description, close_reason}` của decision đã đóng; mở rộng `Bead` có `close_reason` ở lát 2a | P0:205; P2:181 (§12.2) | decision có/không `close_reason` |
| Q05 | Tiếp nhận | Bảng lát sở hữu dữ liệu (2a nâng `Bead`, `SuKien.id`, `sau_id`, cột token/model; 3a khoá lệnh/môi trường) + bảng sự kiện 2a có producer/consumer; `khe.han_muc` có `khe_id`; `giao.nhan` tham chiếu phiếu bền | P2:181; P3 §10; P4 §12 | trường thiếu có mặc định; SSE đọc theo `sau_id` |
| Q06 | Tiếp nhận | Bộ đọc app-server dùng `usedPercent/windowDurationMins/resetsAt`; bộ đọc log dùng `used_percent/window_minutes/resets_at`; cửa sổ lạ giữ nguyên; S1 phải chốt thang `utilization` | P3:331 (§8.1) | fixture từng bộ đọc |
| Q07 | Tiếp nhận | Mỗi cửa sổ `biet`/`chua_biet`; qua reset hoặc quá tuổi → chưa biết, không ghi 0%. H4 chỉ áp cho số đo còn hiệu lực; chưa biết vẫn nhận theo #15; trần lần chạy kiểm trước mỗi lần, kể cả lần 2–3 | P3:331, P3:355, P3:368; P3 §2 H4 | số đo quá `reset_luc`/quá tuổi; lần chạy thứ 3 vượt trần giờ |
| Q08 | Tiếp nhận | Đường dẫn chuẩn hoá POSIX, diff NUL, xét cả tên cũ/mới khi rename, mẫu cấm khớp mọi cấp, ngoại lệ chỉ theo từng đường dẫn; `file_ban_giao` là file thường dưới `docs/handovers/`; đích môi trường kiểm không thoát qua symlink; hook Git tắt; allowlist giới hạn cả tham số thực thi | P4:131 (§6.2 bước 0, 4); P0:123; P3:219 | `erp/package.json`, `AGENTS.md` lồng, đổi tên sang file cấm, symlink bàn giao/`.env.testing`, git hook trong clone |
| Q09 | Tiếp nhận | `can_hoi` có loại `can_quyet_dinh`/`thao_tac_nguy_hiem`; mặc định mọi câu hỏi làm phiếu dừng mềm (4a không cấp phạm vi làm tiếp); trả lời escalation không mở quyền nguy hiểm. Ghi rủi ro #6: trả lời escalation về chuyện khác cũng gỡ hàng rào readiness | P4:297, P4:302; P3 §7.4, P3 §6.3; KT:28 | câu hỏi thao tác nguy hiểm → phiếu dừng ngay; escalation quota đóng gỡ hàng rào nhưng `co-do` còn |
| Q10 | Tiếp nhận | Giữ trước ngân sách là bản ghi bền; đếm lần chạy theo `chay.bat_dau`; thiếu `chay.xong` thì quyết toán không bằng 0; trần wall-clock phiếu gồm chuẩn bị/CLI/kiểm/push; dừng mềm có hạn chót riêng (đề xuất 3 phút); nhịp tim không kéo dài hạn | P3:313 (§7.6); P4:257 (§8) | mất sự kiện kết thúc; gửi lại `chay.bat_dau`; push treo khi estop; test sinh tiến trình con; đồng hồ máy thợ đổi |
| Q11 | Tiếp nhận | Nội dung do gộp/thay/thăng cấp qua lại schema + luật cứng trên nội dung cuối rồi embed lại; LLM không sửa metadata; ghi giới hạn của luật cứng và rủi ro còn lại của #19 | 1b:128 | gộp sinh câu có số tiền → ép `nghiep-vu`; vector khớp nội dung đã lưu |
| Q12 | Tiếp nhận | Lấy tối đa 50 ứng viên **trong từng nhóm** rồi chọn 3/1/1; đo lại M6 | 1b:150 | 100 ký ức dự án gần truy vấn hơn mọi ký ức vai/chung, mỗi nhóm vai/chung vẫn có một ứng viên |
| Q13 | Tiếp nhận | §6.4 mới: đơn vị một sự kiện nguồn, ID thao tác bền, ID ký ức ổn định, nhật ký thao tác, tiến mốc sau cùng, đối soát khi khởi động, tuần tự hoá trong tiến trình ghi, sao lưu nhất quán | 1b:131 | crash ở từng bước; phát lại hai lần không đổi số bản; `ghi_nho` trong lúc dọn phiên bản |
| Q14 | Tiếp nhận | 1b-1 chỉ cần `tram-nho-token` + sự kiện 1a/2a + Ollama, không cần phần 3; adapter nguồn của phần 3/4 bật khi có; trước 1b-2 thợ không cấu hình MCP memory, không truyền URL giả; lớp 5 gọi HTTP recall ở 4c | 1b:33–34; P3 §7.2 (bảng môi trường); P4 §11 lớp 5 | 1b-1 chạy khi chưa có phần 3 |
| Q15 | Tiếp nhận | Tách ngân sách thực thi (reset khi trả lời/trả về, kể cả `spec.tra_ve` với feature) và đợt sửa spec (bộ đếm riêng, không reset bởi `spec.tra_ve`); sự kiện mở chu kỳ có ID nguồn | P4:257 (§8) | trả về spec hai lần → escalation; phát lại không mở chu kỳ hai lần |

### Nhỏ

| # | Xử lý | Lý do / cách làm | Vị trí sau sửa |
|---|---|---|---|
| N01 | Tiếp nhận | Mô tả C5 sửa: mã **đã** đọc nhãn theo ưu tiên an toàn; phần thiếu là bên **ghi** — mọi writer thay toàn bộ tập `cot:*`; "một nhãn" = tối đa một | P2:167 (§12.1 C5); P0:224; P4 §5.4; KT:47 |
| N02 | Tiếp nhận | Spike `bd` mục 3: câu kết luận ngược chiều lệnh đã chạy — thêm đính chính, giữ nguyên ghi chép gốc; #9 không dựa vào mục này | `docs/spikes/2026-10-13-bd-cli.md` mục 3; P2:167 (C4) |
| N03 | Tiếp nhận | M2 ghi rõ ngoại lệ cache 30 giây và test trước/trong/sau; phiếu chứa `ma_giao` là credential — không ghi toàn phiếu vào sự kiện/log/dashboard, che trong header/tên file/lỗi | 1b:21; P3:137; 1b §9.2 |

## 2. 21 quyết định — đã ghi ở đâu

| # | Quyết định | Vị trí chính | Cổng còn đóng |
|---|---|---|---|
| 1 | Beads từ xa: spike trên bản sao, chuyển thật sau duyệt | KT §7 (KT:224), §9; P0:150 | spike chờ Tailscale (#5) |
| 2 | GitHub ngay; branch protection; thợ chỉ push `tram/*`; sửa Q15 | KT:29, KT:34; P3:44 (cổng 2), §6.4; P4 §3, §15 | quyền ref chờ S7 |
| 3 | Tách tài khoản thực thi trước 3a; Mac thợ gắn tag | KT:31, KT:78; P2:48; P3:44, P3:252, §9.2; P4 §6.2 | cơ chế chờ S6 |
| 4 | 4a thử trên repo nháp 3 bug trước HR Codex | KT:37; P4 §2 G8, §3 | — |
| 5 | **Chưa duyệt**: Tailscale B, S1–S4, Ollama + bge-m3, mã Đại ca A | KT:34; P0:141; P3:44, §12; 1b §13, §15 | **toàn bộ vẫn đóng** |
| 6 | Decision đóng (kể cả escalation) chốt mọi hàng rào | KT:53; P0:195; P4:302 (kèm rủi ro) | — |
| 7 | Nút Chốt gỡ mọi nhãn cột; prompt v2 có câu trả lời | P0:205; P2:66, P2:167 | — |
| 8 | Tối đa một nhãn `cot:*`; khối chèn hai chế độ | KT:47, KT:240; P0:224, P0:271; P2 §12.1; P4 §5.4, §6.4 | mã `KHOI` đổi ở plan 2a |
| 9 | Bộ chấm bỏ qua epic | P0:175; P2:62 | — |
| 10 | Bỏ qua bead có phiếu hiệu lực, chấm lại khi phiếu kết thúc | KT:152; P0:175, P0:244, P0:289; P3:64; P4 §5.1, §15 | mã 1a chưa có (P0 §11) |
| 11 | Nút Trả lời escalation có trong 2a | P2:80, §7, §12.1; P4 §3, §9 | — |
| 12 | Telegram có trong 2a | P2:114, §12.1 | token bot do Đại ca tạo |
| 13 | Tối đa 3 lần chạy CLI mỗi phiếu | KT:152; P3 §4, §7.2, §14; P4 §8 | — |
| 14 | Dừng mềm khi tắt khe/estop | P0:141; P3 §6.3, §7.6, §14 | — |
| 15 | Hạn mức chưa biết: chạy tiếp, cảnh báo vàng | KT:157; P3:355 (§8.2), §14 | — |
| 16 | Feature cha Đại ca đóng; ngân sách bắt đầu lại khi trả lời/trả về | P4 §7.3, §8, §15 | — |
| 17 | QC hai khe cùng Claude: chấp nhận | KT:85; P4 §5.3, §15 | — |
| 18 | `/vai/*` chỉ qua thăng cấp/ghi tay; ký ức Đại ca bất khả xâm phạm; lọc `pham_vi IN` | KT:133, KT:135; 1b §4, §6.3, §13 | — |
| 19 | Thăng cấp tự động, chờ 7 ngày | KT:133; 1b:165, §13 | — |
| 20 | `tu_khoa_khach` tuỳ chọn; phiên A chỉ đọc | KT:78, KT:133; 1b §9.3, §13 | — |
| 21 | Giữ con số mặc định | P3 §2, §14; P4 §2, §8; 1b §13 | — |

## 3. Giả định cần spike (chưa chạy)

Đều ghi trong spec với trạng thái duyệt. Không spike nào đã chạy.

| Spike | Ở đâu | Duyệt |
|---|---|---|
| S1 `rate_limit_event` của Claude headless (trường, thang `utilization`, đủ cửa sổ) | P3 §12 | #5 — chưa duyệt |
| S2 LaunchAgent + Keychain dưới đúng principal, sau reboot | P3 §12 | #5 — chưa duyệt |
| S3 hai `CLAUDE_CONFIG_DIR`/hai tài khoản tách thật | P3 §12 | #5 — chưa duyệt |
| S4 cờ headless, cấm thắng cho phép ở mọi nguồn, lệnh bị cấm không treo | P3 §12 | #5 — chưa duyệt |
| S5 Codex app-server + `codex exec` sandbox | P3 §12 | cần cho phép |
| S6 cơ chế cách ly + kiểm chứng âm H9 | P3 §12 | cần cho phép (tạo tài khoản) |
| S7 quyền ref GitHub + push treo/mất ACK | P3 §12 | cần cho phép (repo nháp) |
| S8 hook `PreCompact` | P3 §12 | #5 — chưa duyệt |
| Spike beads từ xa trên bản sao | P0 §4.6 | chờ Tailscale (#5) |
| N1 LanceDB lọc trước + cập nhật + dọn phiên bản | 1b §14 | chờ Ollama (#5) |
| N2 MCP header từ biến môi trường; `tailscale serve` nhiều đường | 1b §14 | chờ Tailscale (#5) |
| Môi trường test dùng DB test, đủ dependency khi offline | P4 §6.2 bước 3 | cùng S6 |
| Tham số API Anthropic thật (structured output + fallback) | P0 §6.2, plan 0+1a Task 9 | cần cho phép gọi API (Task 14) |

## 4. Đề xuất kỹ thuật mới cần Đại ca chốt

Các mục này đến từ review Codex, đã viết vào spec dưới dạng **đề xuất**, chưa phải quyết định:

1. **Ref tạm theo lượt + trạm công bố bằng CAS**, hay phương án lùi "trạm fetch từ kho thợ rồi tự push" — sau S7 (P3 §6.4).
2. **Cơ chế cách ly**: một user macOS cho mỗi khe, hay một user thực thi chung + sandbox mỗi khe — sau S6 (P3 §7.3). Kèm cách dashboard nhận yêu cầu qua đường không giả được (Unix socket hay proxy) — P2 §4 mục 2b.
3. **QC chỉ được đổi `docs/handovers/**`**, đổi mã → escalation `qc-doi-ma` (P4 §6.3). **Đại ca chốt 13/10**.
4. **Mọi câu hỏi của agent dừng mềm phiếu ở 4a** (P4 §9). **Đại ca chốt 13/10**.
5. **Đợt sửa spec là bộ đếm riêng** (P4 §8). **Đại ca chốt 13/10**.
6. **Hạn chót dừng mềm mặc định 3 phút; tuổi tối đa của số đo hạn mức 6 giờ** (P3 §7.6, §8.1). **Đại ca chốt 13/10**.
7. **Cấu hình MCP phiên tay**: `.mcp.json` trong repo hay `claude mcp add --scope local` — câu cũ của 1b, thuộc phần việc đang bị giữ bởi #5 (1b §13 câu 10).
8. **Principal kiểm lại riêng của trạm `tram-kiem`** — lệnh kiểm lại của phần 4 chạy dưới principal này, không credential, chịu cùng kiểm chứng âm H9 (P3 §7.3 mục 5, P3 §13 mục 12). Thêm sau review Fable; chốt cùng mục 2.
9. **Chấp nhận rủi ro token khe trong môi trường** nếu S2 buộc dùng `CLAUDE_CODE_OAUTH_TOKEN` (P3 §13 mục 13).

Ảnh hưởng tới việc viết plan: mục 1–2 và 8 quyết định khung code của 3a; plan 3a viết được nhưng các bước công bố ref và cách ly phải để dạng "chờ S6/S7". Mục 3–6 Đại ca đã chốt 13/10.

## 5. Kết luận theo spec

Tách bạch hai câu hỏi: tài liệu đã đủ để **viết plan** chưa, và hành vi đã được **kiểm chứng** chưa (chưa — không có spike hay test nào chạy).

- **Phần 2 §12 — đủ tài liệu để viết plan 2a**, sau khi Đại ca duyệt toàn văn spec. Phần chạy thật qua tailnet chờ #5. Lát 2a kéo theo các sửa mã 1a liệt kê ở P0 §11.
- **Phần 3 — đủ tài liệu để viết plan 3a ở mức hợp đồng**; còn thiếu lựa chọn cơ chế cho cách ly (S6) và công bố ref (S7), và kết quả S1–S4 cho bộ đọc hạn mức và file quyền. Plan phải để các bước đó dạng chờ.
- **Phần 4 — đủ tài liệu để viết plan 4a/4b** sau đợt sửa theo review Fable (§7): luật bàn giao của phiếu `qc`, spike tài liệu có `lenh_cho_phep` rỗng, principal kiểm lại. Phụ thuộc hợp đồng phần 3 ở trên; cần Đại ca chốt các đề xuất 3–5 và 8 ở §4.
- **Phần 1b — đủ tài liệu để viết plan 1b-1**; 1b-2 chờ #5 (Tailscale, mã Đại ca) và N2; triển khai 1b-1 chờ Ollama (#5) và N1.

## 6. File đã sửa

- `docs/quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md` (mới, nguyên văn quyết định)
- `docs/specs/2026-10-12-tram-dieu-phoi-kien-truc.md`
- `docs/specs/2026-10-12-phan-0-1a-cham-cot.md` (thêm §11 thay đổi mã chưa triển khai)
- `docs/specs/2026-10-12-phan-2-dashboard.md` (§12 viết lại)
- `docs/specs/2026-10-13-phan-3-may-tho-han-muc.md` (viết lại)
- `docs/specs/2026-10-13-phan-4-giao-viec.md` (viết lại)
- `docs/specs/2026-10-13-phan-1b-memory.md`
- `docs/spikes/2026-10-13-bd-cli.md` (chỉ thêm đính chính N02)
- `docs/plans/2026-10-12-phan-0-1a-cham-cot.md` (chỉ thêm ghi chú trỏ P0 §11)
- `docs/handovers/2026-10-13-sang-sau-dem-chay.md` (chỉ thêm khối cập nhật)
- `docs/handovers/2026-10-13-phan-hoi-review-codex.md` (file này)

Không file mã, test, cấu hình hay dữ liệu nào bị đổi trong đợt này.

## 7. Review Fable sau đợt sửa (13/10/2026)

Fable 5.1 review tĩnh toàn bộ đợt sửa: 25 phát hiện của Codex đều xử lý đúng; 21 quyết định đều nằm trong đoạn quy định chính; gate #5 không bị mở lặng lẽ. Không có lỗi chặn. Em đã sửa:

- **Quan trọng (4):** luật `chinh-thuc` cho phiếu `qc` — được `dat: false` khi `tra_ve`, bàn giao QC lỗi coi như `tra_ve` (P0 §4.3, P4 §6.3); principal kiểm lại `tram-kiem` (P3 §7.3, P4 §6.2); spike tài liệu có `lenh_cho_phep = []` và file quyền nạp từ phiếu (P4 §6.1, P3 §6.1, §7.2); bảng `thao_tac` do 2a sở hữu (P2 §12.2, §12.3).
- **Nhỏ (15):** cửa sổ đua chỉ thu hẹp, không đóng hẳn (P0 §5.6); `lan < ngan_sach.so_lan_chay` (P3 §7.6); tự đóng từ 4c (P2 bảng Phê duyệt, lát 2a); API Duyệt có `digest_bead`, câu "Mọi POST" dời ra sau bảng (P2 §7); `khop_lenh` cấm token bắt đầu bằng `-`, đường dẫn tuyệt đối, `..` (P4 §6.2, P3 §6.1); `can_hoi` dừng mềm ngay ở thợ (P3 §7.4); ba nhóm quyền ở KT bảng máy và P2 §4 mục 2b; `commit` trong khối `bao.xong` = HEAD cuối sẽ push (P3 §7.5); 1b sót chữ "cùng user", `tram-noi-bo-token` chỉ từ 1b-2, hai chỗ "chờ duyệt / duyệt thăng cấp" theo #19; đính chính spike bd không kết luận chiều; rủi ro token khe đưa vào P3 §13; `bd ready` loại `in_progress` ghi "plan kiểm"; `digest_tieu_chi` đổi → bằng chứng hết hiệu lực ở `buoc_ke_tiep` dòng 3, 4, 6 (P4 §6.6); bảng thành phần KT trỏ đúng file; danh sách trường `bd list` (P0 §5.1).
- **Gate:** P0 §4.6 và §8 mục 0 ghi rõ spike beads từ xa chỉ làm khi gate #5 mở.

Đây vẫn là kiểm tài liệu tĩnh; không có test, spike hay triển khai nào chạy.

**Vòng Fable kiểm lại (13/10, sau commit 60add5c):** mọi mục đã khép, còn một chỗ quan trọng: thợ (P3 §7.5 bước 4) chưa áp luật bàn giao bản QC. Em đã sửa, cùng 7 chỗ nhỏ: thứ tự chép môi trường kiểm trước khi trao quyền cho `tram-kiem` (P3 §7.3, P4 §6.2), P4 §15 dòng 4, S6 thêm `tram-kiem`, bảng `can_hoi` và dừng mềm do thợ (P3 §7.4, §7.6), `lan ≤ ngan_sach.so_lan_chay` ở P3 §7.2, file quyền của phiếu, `kiem.lai` của spike đủ trường, tham chiếu `digest_bead` → P4 §7.3, KT `tram chu cai-dat` ba nhóm quyền, câu đầu đính chính spike bd. Fable kết luận các chỗ còn lại đều là chữ, không đụng quyết định nào.
