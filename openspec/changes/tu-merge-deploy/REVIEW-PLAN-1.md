# Review độc lập — plan tự merge/deploy

Ngày 20/10/2026; nhánh `spec/tu-merge-deploy`, nền `f098d4a`.
Đã sửa trực tiếp [plan](docs/plans/2026-10-20-tu-merge-deploy.md).
Chỉ hai tài liệu này thay đổi trong worktree; không sửa mã sản phẩm/test, commit, gọi `bd` hay push.
Mã nguyên văn của plan được áp và chạy trong bản sao tạm, dùng bộ chặn host và Git giả.

Đã đọc CLAUDE, bộ tài liệu đầu phiên, ENGINEERING_STANDARDS, toàn bộ change
`openspec/changes/tu-merge-deploy/`, QĐ1–QĐ4, plan và các điểm nối mã thật.
QĐ1–QĐ4 giữ nguyên; không mở lại quyết định, không coi review là quyền chạy thật.

## Lỗi tìm được, nặng → nhẹ

Các đường dẫn mã dưới đây chỉ vị trí **đoạn mã đề xuất trong plan**, không phải mã đã sửa ở worktree.

| Mức | Lỗi và hậu quả | Đã sửa trong plan |
|---|---|---|
| P1 | `api/doi_soat_deploy`: ghi đối soát/mở chốt trước khi ledger kiểm mã thao tác. Mã sai vẫn có tác dụng; mã dùng lại cho lượt khác có thể mở lượt mới. | Đưa toàn bộ ghi vào `chay_thao_tac`; nội dung idempotency chứa lượt và SHA xác nhận. Test mã sai và mã cũ/lượt mới. |
| P1 | `deploy/thuc_hien`: chỉ ghi sau khi gọi đích. Crash khi đang rollback làm mất dấu bước lùi; auto merge còn có thể chạy trước khi vòng deploy khôi phục chốt. | Ghi ý định `deploy.lenh` trước từng lời gọi; kết quả ghi sau. UI bỏ qua dòng ý định. Auto merge kiểm cả `chuoi_dang_do` lẫn chốt đối soát. Test crash trước kết quả và rollback chưa rõ. |
| P1 | `deploy/trang_thai`: bật auto trước lần polling đầu có thể ăn merge cũ, trái D123. `vong/chay`: trigger auto cũ có thể cấp quyền deploy bản merge tay mới hơn. | Chỉ nhận sự kiện sau mốc bật gần nhất; trigger phải trùng M đã chọn, kiểm lại trước tác dụng phụ. Giữ ca merge mới chen vào lượt đang chạy. |
| P1 | `deploy/chay`: đọc L trước Uq dài khiến L có thể lỗi thời; hàng rào schema/đường cấm chưa bao phủ Deploy tay trên bản đã merge. | Dời một lần probe sẵn có xuống sau Uq; kiểm diff L..M qua cơ chế đường cấm/schema hiện có cho cả tay và tự động. Hợp đồng đích buộc khoá dự án và so L nguyên tử trước chuyển bản; cần R3/R4 chứng minh thật. |
| P1 | `giao_viec/tu_merge_tuoi`: chốt hiện hành không kiểm đủ phụ thuộc decision/escalation còn mở hoặc mất dữ liệu. | Dùng `bi_chan_boi` với snapshot bead đầy đủ; thiếu/open đều chặn. Test ba trạng thái open/missing/closed. |
| P1 | `gh_bao_ve`: chỉ đọc trang đầu rules nên bỏ sót merge queue ở trang sau. `gh pr merge` có thể đưa PR vào queue dù không truyền `--auto`. | Dùng phân trang của `gh`, kiểm đủ các trang; test queue ở trang hai. Không tự dựng bộ phân trang/queue. |
| P2 | `deploy/ban`: mã kiểm Uq không phân biệt dự án có cùng M và chính sách. | Thêm tên dự án vào dữ liệu tạo mã lượt; test hai dự án không dùng chung mã. |
| P2 | UI điền sẵn SHA cũ vào hộp xác nhận đối soát, dễ biến thao tác đọc bản thực tế thành bấm OK. | Bỏ giá trị mặc định; người vận hành nhập bản đã quan sát. Wrapper vẫn phải chứng minh bản đó và hết writer. |
| P2 | TDD có test thu thập lỗi vì thiếu module; fixture/API/UI chỉ được sửa muộn ở Task 8. Áp tất cả rồi xanh không chứng minh từng task RED → GREEN. | Chuyển test/fixture về đúng task; phân biệt collection error với RED hành vi, yêu cầu khai báo tối thiểu nếu cần. Task 8 chỉ kiểm tích hợp. Khôi phục hồi quy Estop, pause khi Uq, khoá dự án và merge chen ngang; không bỏ test OS. |
| P2 | R0 đòi bằng chứng hoàn tất trước khi được áp mã; lẫn cổng ghép mã tắt với cổng chạy thật. | Tách baseline trước áp, RED/GREEN + QC trước ghép, R1–R5 trước bật/archive. Nêu rõ chưa có N₀ toàn bộ xanh và chưa rehearsal tuần tự toàn bộ. |
| P3 | Nhiều file có bản trung gian rồi vá lại ở task sau, làm khó đối chiếu và lặp mã. | Gom mỗi file thành đúng một bản cuối, theo task sở hữu; bỏ lệnh commit lặp và phần vá cứu task trước ở Task 8. |

GitHub xác nhận endpoint rules có phân trang; dùng chức năng có sẵn của CLI.
Nguồn: [REST rules](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch),
[gh api](https://cli.github.com/manual/gh_api),
[gh merge](https://cli.github.com/manual/gh_pr_merge).

## Đã bỏ phần rườm rà

- Từ 71 khối mã còn 61 khối, mỗi file đúng một khối; không phải giảm số file sản phẩm.
  Số dòng plan giảm dù đã thêm ca an toàn và bằng chứng còn thiếu.
- Dùng ledger `chay_thao_tac`, kiểm phụ thuộc `bi_chan_boi`, sự kiện `deploy.lenh`,
  hàng rào đường cấm và Uq hiện có; không tạo sổ idempotency, queue hay daemon mới.
- Một lần probe L sau Uq, cộng điều kiện nguyên tử tại đích; không thêm vòng polling phía trạm.
- GitHub chọn required checks và phân trang; launchd/đường deploy của dự án giữ nhiệm vụ triển khai.
  Không thêm dependency, schema hay hệ thống deploy chung.

Ba wrapper vẫn là hợp đồng đầu vào của đường deploy sẵn có, chưa phải hạ tầng đã tồn tại.
Nếu đích thực tế cần một nền deploy mới để đáp ứng hợp đồng thì phải thu hẹp adapter theo đích đó,
không triển khai một nền mới dưới danh nghĩa “wrapper”.

## Bằng chứng thực chạy và giới hạn

Đã trích mã nguyên văn, áp từng unified diff bằng `git apply --check` rồi áp trên bản sao nền.
Lượt cuối có **61/61 khối áp được**, không trùng file; byte của 61 file khớp bản sao chạy test,
Python parse được. Đây là đối chiếu mã thật/import/chữ ký qua runtime, không chỉ đọc bằng mắt.

Mọi lệnh Python đi qua `tests/chan_host/chay.sh`, dùng môi trường đã cài và cache tạm:
`UV_CACHE_DIR=/tmp/tm-review-uv-cache UV_NO_SYNC=1`.
Không gọi GitHub thật, push/merge thật hay đích deploy thật. Bộ giả ghi rõ số push giả lập.

| Phép kiểm | Kết quả |
|---|---|
| Plan gốc áp toàn bộ, nhóm test liên quan | 232 passed; cho thấy nhóm test gốc chưa bắt các lỗi review |
| Ca tái hiện review trước sửa | 7 failed, 1 passed bằng assertion đúng hành vi; log `/tmp/tm-review-red.log` |
| Decision open/missing | 2 failed trước sửa; closed vẫn qua |
| Crash chưa có kết quả deploy | 1 failed trước sửa; nhóm sau sửa 11 passed |
| Merge queue trang hai | 1 failed trước sửa bằng assertion cổng trả xanh sai |
| Nhóm cuối sau mọi sửa | **300 passed**; 0 dòng chặn mới, 0 điểm mù Python con; 308 push giả lập, không push thật |
| Frontend bản sửa | `npm run kiem`: 155 passed; `npm run build` và `npm run kiem-dist`: đạt |
| Nhóm rộng có runner tiến trình | 4 failed, 242 passed; chưa thể gọi toàn bộ xanh |
| Đối chứng một ca trên worktree nền chưa sửa | Cùng lỗi `da_thu_hoi=False`; 1 failed |

Lệnh nhóm cuối, chạy ở bản sao tạm; log `/tmp/tm-review-final-green.log`:

```bash
tests/chan_host/chay.sh -q tests/test_tm20*.py \
  tests/test_gh.py tests/test_gh_tu_merge.py tests/test_tu_dong_cai_dat.py \
  tests/test_tu_merge*.py tests/test_deploy_vong.py tests/test_deploy_race.py \
  tests/test_deploy_cong_tac_v2.py tests/test_api_deploy.py tests/test_passkey_tm_tc.py \
  tests/test_bao_tin_tu_dong.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

Các ca lỗi tiến trình trong lượt rộng:

- `test_dat_chay_trong_thu_muc_va_khong_mang_bien_cua_tram_api`
- `test_bi_mat_khong_cham_dia_khi_lenh_dang_chay_hay_qua_han`
- `test_dau_ra_lon_co_tran_khong_giu_het_trong_ram`
- `test_qua_han_giet_ca_nhom_tinh_la_hong`

Đã đối chứng ca đầu trên nền; chưa đối chứng riêng ba ca còn lại, chưa kết luận nguyên nhân OS.
Lượt rộng ghi hai điểm mù Python con từ test `deploy_cam` hiện có; không dùng lượt đó làm chứng cứ
bộ chặn hoàn hảo. Không xoá hay skip test để đổi kết luận. Log: `/tmp/tm-review-wide.log`,
`/tmp/tm-review-baseline.log`. Pytest còn báo dọn thư mục ACL cũ không được phép.

Các ca review mới đã có RED hành vi như trên; ca API mới chưa tồn tại gây collection error
không được tính RED. Chưa chạy trọn chuỗi test-trước-mã từng Task 1–7, toàn bộ Python,
browser dưới CSP thật, OpenSpec đúng bản pin 1.14.0 hoặc nghiệm thu OS/đích thật.
Build frontend có cảnh báo kích thước bundle; không thay bằng chứng kiểm UI.

## Còn mở, ai xử lý

1. **Agent thực hiện/maintainer:** xác định nguyên nhân baseline thu hồi tiến trình, đo N₀ toàn bộ
   đúng HEAD ở môi trường thích hợp. Giữ test và bộ chặn; không xin nới quyền để né assertion.
2. **Agent thực hiện:** rehearsal đúng thứ tự RED → GREEN, toàn bộ hồi quy, browser/CSP,
   OpenSpec đúng bản pin và QC. Lượt review này không thay các cổng đó.
3. **Đại ca trước bật thật:** cung cấp/chọn đường deploy đang dùng của dự án đầu tiên,
   principal và miền/nhãn launchd, artifact L, phép thử chức năng và quyền riêng thực tế.
   Đo R1–R5 trên repo/đích thử được cho phép; thiếu thì giữ công tắc tắt.

Không có QĐ1–QĐ4 cần chốt lại. Các lỗi nội dung phát hiện đã sửa vào plan; phần còn mở là
bằng chứng baseline/TDD toàn bộ và điều kiện đích thật. Chưa đủ cơ sở duyệt thực thi nguyên plan.

CHƯA ĐẠT để code.

## Em (Claude) QC 20/10
Bốn test baseline lỗi thu hồi tiến trình (tests/test_deploy_lenh.py) chạy NGOÀI sandbox Codex trên main: 9 passed — lỗi do sandbox không quan sát được tiến trình, không phải baseline đỏ. Plan đủ điều kiện code; RED→GREEN/QC/R1–R5 là cổng của giai đoạn thực thi.
