# Spike: đọc hạn mức Claude Code và Codex (chỉ đọc, máy A)

Ngày: 2026-10-12 · Claude Code 2.1.227 · codex-cli 0.162.0-alpha.17.2 · không gọi model, không mở file đăng nhập.

## Kết luận

| CLI | Nguồn chính | Nguồn lùi | Cần kiểm trên máy B |
|---|---|---|---|
| Claude Code | `claude -p --output-format stream-json`: sự kiện `rate_limit_event` (`status` allowed/allowed_warning/rejected, `resetsAt`, `rateLimitType` five_hour/seven_day…, `utilization`) — **chưa xác minh khi chạy thật** | Log `projects/*.jsonl` có `quotaLimits` / `apiErrorParams.rate_limit_info` khi đã bị chặn (có `resetsAt`); hook `StopFailure` matcher `rate_limit` (không có giờ reset). Statusline có `rate_limits.five_hour/seven_day.{used_percentage, resets_at}` nhưng chỉ chạy trong phiên tương tác | Một lần `claude -p` thật xem có `rate_limit_event` (tốn ít quota, Đại ca duyệt) |
| Codex | `codex app-server` → `account/rateLimits/read` (`usedPercent`, `windowDurationMins`, `resetsAt`) — hỏi lúc khe rảnh, không cần gửi tin | `$CODEX_HOME/sessions/**/rollout-*.jsonl`: `token_count.rate_limits.primary/secondary{used_percent, window_minutes, resets_at}` (thấy thật) | Chạy dưới launchd với `CODEX_HOME` riêng |

## Lưu ý thiết kế
- Codex: vai trò `primary`/`secondary` đổi theo gói (plus: 300 phút + 10080 phút; prolite: chỉ 10080) → **đọc theo `window_minutes`**, không ngầm định.
- Hai tài khoản một máy: Claude dùng `CLAUDE_CONFIG_DIR` (Keychain gắn theo thư mục; lùi về `$CLAUDE_CONFIG_DIR/.credentials.json`); headless có `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN` (1 năm). Codex dùng `CODEX_HOME`.
- **Không dùng** endpoint OAuth/cookie không tài liệu (`api.anthropic.com/api/oauth/usage`, `chatgpt.com/backend-api/wham/usage`) như CodexBar — phải đọc token.
- ccusage chỉ cho token/chi phí ước lượng, không cho % hạn mức thật → dùng cho màn Usage, không dùng để chặn giao việc.
- ~~Máy A có `model_providers.9router` trong config Codex — kiểm xem route có làm mất `rate_limits` không.~~ Bỏ 13/10/2026: Đại ca không dùng 9router nữa.

## Việc kiểm trên máy B
1. LaunchAgent (phiên GUI) có đọc được Keychain không; nếu không → `CLAUDE_CODE_OAUTH_TOKEN` (lưu Keychain của trạm, nạp vào môi trường tiến trình con).
2. `rate_limit_event` có trong stream-json với token setup-token không.
3. `account/rateLimits/read` dưới launchd + `CODEX_HOME` riêng.
4. Đường dẫn tuyệt đối `CLAUDE_CONFIG_DIR`/`CODEX_HOME` trong plist.

> **Ghi chú 15/10/2026 — mục 1 chưa áp cho LaunchDaemon.** Mục 1 và cách lùi `CLAUDE_CODE_OAUTH_TOKEN` được viết khi giả định thợ chạy dưới **LaunchAgent** (phiên GUI). Sau đó, plan 3a-2 (G32, G35) cài thợ máy B dưới **LaunchDaemon** `vn.tram.tho` có `UserName`. Daemon không có login Keychain của phiên GUI. Plan 3b G4 chỉ giữ LaunchAgent cho Mac thợ từ xa. Vậy kết luận và cách lùi ở mục 1 **chưa được kiểm** cho daemon. Phải kiểm lại ở S2/S6 (spec 3 §12), dưới đúng principal và đúng loại service, trước và sau reboot. 3a-2 G35 ghi: không đọc được Keychain thì **dừng**, không tự chuyển sang lưu token ra file. Rủi ro token khe nằm trong môi trường đã được Đại ca chấp nhận khi duyệt spec 3 (§13 mục 13, 13/10). Tuy vậy, chỉ đưa `CLAUDE_CODE_OAUTH_TOKEN` vào danh sách biến môi trường sau khi S2 xác nhận là cần (3a-2 "Bổ sung review tĩnh đợt 3"). Văn bản spike ở trên giữ nguyên.

Nguồn: code.claude.com/docs/en/{statusline,hooks,env-vars,authentication,agent-sdk/typescript}; learn.chatgpt.com/docs/app-server; README ccusage, Claude-Code-Usage-Monitor, CodexBar.
