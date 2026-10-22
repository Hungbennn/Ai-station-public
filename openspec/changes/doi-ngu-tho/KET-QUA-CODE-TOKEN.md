# Kết quả Codex — triển khai token file, 21/10/2026

Thực hiện trong worktree `code-token`, nhánh `code/token-file`, nền `8825e1b`.
Đã đọc `../../.handover/codex-viec/CHUNG.md`, quy định dự án, plan và quyết định token file.
Task 1 → 4 đã triển khai lần lượt, mỗi task áp test → thấy RED → áp mã → thấy GREEN.
Chưa commit, ghép hoặc chạy thật.

## Kết quả từng task

Mỗi lượt dưới đây đều kèm `tests/test_do_dai_ma.py` (3 test), nên số passed tăng 3 so với plan.
Tất cả lượt RED/GREEN đều có **0 dòng chặn mới**.

| Task | RED đo được | GREEN đo được | Nội dung đã xong |
| --- | --- | --- | --- |
| 1 | 13 failed, 3 passed; `Thiếu kho token file an toàn` | 16 passed | Kho file đúng chủ, 0700/0600, no-follow, chặn hardlink/FIFO, ghi nguyên tử và dọn file tạm khi rename lỗi |
| 2 | 6 failed, 9 passed; thiếu keyword `tren_may_b`, bootstrap báo `nhan-token B vẫn gọi Keychain` | 15 passed | B chọn file theo passwd của UID; từ xa giữ Keychain; bootstrap `nhan-token --may-b` và cập nhật các caller |
| 3 | 8 failed, 13 passed; thiếu wrapper FD, auth/do-nen chưa qua wrapper | 21 passed | Helper mở FD dưới UID khe sau sudo, lọc env, exec Claude; nối vào auth, do-nen và luồng phiếu B |
| 4 | 8 failed, 18 passed, 1 deselected; thiếu sổ tay token file, vẫn còn bước/hàm Keychain | 26 passed, 1 deselected | setup-token/ô ẩn/stdin, bỏ bước Keychain, cập nhật token máy và S6 sáu phép âm có đối chứng |

Nhật ký đầy đủ: `/private/tmp/codex-token/code-token-logs/t{1..4}-{red,green}.log`.

## Hồi quy và đối chiếu

Lệnh chạy trong worktree, không dùng pytest trần:

```bash
export PYTHONPATH="$PWD"
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1 UV_CACHE_DIR=/private/tmp/codex-token/uv
tests/chan_host/chay.sh -q \
  tests/test_token_file.py tests/test_token_may_file.py \
  tests/test_claude_token_file.py tests/test_doi_ngu_token_file.py \
  tests/test_doi_ngu*.py tests/test_kiem_cong.py tests/test_dang_nhap_principal.py \
  tests/test_launchd_token_tho.py tests/test_token_may.py tests/test_principal.py \
  tests/test_tho_lenh_chay.py tests/test_do_dai_ma.py tests/test_vong_import.py \
  -k 'not test_kho_kiem_kho_tho_bang_quyen_tram_tho and not test_chay_may_tron_vong_roi_don_worktree_bead_da_dong'
```

Kết quả: **166 passed, 2 deselected, 14.99s**, mã thoát 0, **0 dòng chặn mới**.
Runner báo 11 điểm mù Python con ở các test dependency cũ và 44 push giả lập; không push thật.
Nhật ký: `/private/tmp/codex-token/code-token-logs/final-related.log`.

Trích lại đủ 8 patch từ plan, `git apply --check` trước mỗi lần áp. Áp lại tuần tự trên bản sao
HEAD rồi so nội dung: **26/26 file khớp từng byte**, không lệch mã/test nguyên văn.
`git diff --check` đạt; kiểm độ dài và vòng import nằm trong nhóm hồi quy đã đạt.
Tự rà diff và caller theo skill code-review-and-quality: kho token, đường FD sau sudo,
lọc env và log công cụ bám plan. Đây không thay QC độc lập hoặc phép đo UID/ACL thật.

## Chỗ lệch plan

- **Không lệch mã/test, thiết kế hoặc kỳ vọng test.** Không phải sửa patch khi áp.
- Theo lệnh thực hiện hiện tại, áp trong worktree thay vì chỉ bản sao như phiên soạn plan;
  bỏ toàn bộ bước commit/chạy cả suite và kèm test độ dài ở mọi lượt RED/GREEN.
- Báo cáo đặt tại file này theo chỉ định cuối của Đại ca, thay tên báo cáo chung `KET-QUA-CODEX.md`.
- Ranh giới sudo đã được Đại ca chốt trong yêu cầu 21/10: agent dưới UID khe không được đọc
  token khe khác/token máy; quản lý tram-tho là mã trạm đã có quyền sudo sang khe từ trước,
  không cần chống sudo. Không đổi sudoers; token không đi vào env/argv/log của quản lý.

## Baseline, test đỏ cũ và sandbox

Trước sửa, chạy nhóm `test_doi_ngu_nen`, `test_kiem_cong`, `test_token_may`,
`test_doi_ngu_cong_cu` và `test_do_dai_ma`: **33 passed, 1 failed**, 0 dòng chặn mới.
Ca đỏ `test_kho_kiem_kho_tho_bang_quyen_tram_tho` nhận
`kho-da-co-can-doi-soat-khong-ghi-de` thay `dung-sau-kiem` do đường kho thật tồn tại;
đúng lỗi baseline trong plan, **không phải lỗi sandbox**. Không sửa ca này.
Nhật ký: `/private/tmp/codex-token/code-token-logs/baseline.log`.

Hai ca bị loại khỏi hồi quy giữ đúng plan. Ca vòng thợ
`test_chay_may_tron_vong_roi_don_worktree_bead_da_dong` đã được phiên soạn ghi lỗi
`Không xác nhận thu hồi tiến trình của khe`; phiên này không chạy lại hoặc đối chứng dài.
Chưa kết luận nguyên nhân mới cho ca đó. Không gặp thêm lỗi ps/sysctl/bind trong nhóm đã chạy;
không chạy `tests/test_deploy_lenh.py`, không sửa code để né sandbox.

## Việc còn lại

- Người điều phối QC độc lập, chạy hai ca bị loại và toàn suite ngoài sandbox trước ghép.
- Đo thật R2/R4/R5: FD qua sudo/CLI, đúng hai account, quyền UID/ACL, không credential ngoài
  file đã duyệt, headless và tự lên sau reboot không unlock/cấp lại token. Chưa nghiệm thu S2/S6/R5,
  chưa có bằng chứng giải xong `bs-2bd.11`.
- Không chạm frontend, không thêm dependency; không gọi sudo/Keychain/GitHub/deploy thật,
  không chạy sổ tay thật, không đụng `~/.tram` hoặc `/usr/local/tram` thật, không bật công tắc.
  Không dùng `bd`, không sửa CURRENT_STATE hoặc tạo handover.
