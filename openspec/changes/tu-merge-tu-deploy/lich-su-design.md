> **LỊCH SỬ 18/10 — không phải yêu cầu thực thi hiện hành.** Giữ nguyên để tra quyết định và
> bằng chứng cũ; đọc `proposal.md` và plan 20/10 để biết phần đã thay. Dấu nghiệm thu cũ không chứng minh change mới.

# Design — Tự merge và tự deploy

## Context

Vì sao làm: xem `proposal.md` — Why. Yêu cầu hành vi: ba file trong `specs/`. Các lựa chọn dưới đây đã được Đại ca
chốt ở D87–D101 (18/10); mỗi chỗ ghi D-số. Ở đây chỉ nói **nối vào đâu, lưu ở
đâu, an toàn thế nào**. Mã nguyên văn sẽ ở plan TDD trong `docs/plans/`, viết sau khi Đại ca duyệt change này.

Hiện trạng (đọc từ `main` `b9e8c8d`):

- Luồng một bead: code → kiểm lại (`tram/giao_viec/kiem_lai.py`) → QC khe khác → vào cột 3 với **bộ bằng chứng**
  `(du_an, bead_id, giao_id, luot, commit_code, commit_ban_giao, digest_tieu_chi)` → trạm mở PR
  (`tram/giao_viec/pr.py` `mo_pr_bead`, sự kiện `pr.mo`) → **Đại ca merge** → trạm xác minh merge rồi đóng bead
  (`tram/giao_viec/pr_merge.py` `kiem_merge`, sự kiện `pr.da_merge` / `pr.khong_xac_minh`).
- Hai bước GitHub chạy trong `tram/giao_viec/tick_github.py` `buoc_github`, thuộc pha `vong_git` của vòng tick
  (`tram/giao_viec/tick.py`); estop bật thì pha này không chạy.
- `tram/giao_viec/gh.py` chỉ cho `gh pr list|view|create`; có test khoá "không bao giờ `gh pr merge`". Hạn 60 giây
  mỗi lệnh `gh`.
- Thao tác ghi dashboard: `tram/api/bao_mat.py` `yeu_cau_ghi` (kênh ghi, `Tailscale-User-Login` trong
  `dai_ca_logins`, `X-Tram: 1`, `Origin` máy B) + `tram/thao_tac/chay.py` `chay_thao_tac` (bảng `thao_tac`, mã
  thao tác, `expected_version`). Bật/tắt khe (`tram/thao_tac/khe.py`) lưu trạng thái **bằng sự kiện** rồi tính lúc
  đọc; estop (`tram/thao_tac/estop.py`) không kiểm `expected_version` để không hỏng vì màn hình cũ.
- Kênh ghi hiện hành `cach_ly.kenh_ghi = header` là **tạm**: tiến trình nào trên máy B cũng giả được header danh
  tính khi gọi thẳng `127.0.0.1` (`tram/api/kenh_ghi.py`). Chuyển `unix-socket` trước khi giao việc thật.
- Cấu hình dự án `du-an/<ten>.yaml` nằm trong repo trạm, Đại ca sửa tay; `bat_ghi` thiếu khoá = `false`.
- Telegram: `tram/bao_tin/` chỉ gửi tên dự án, mã bead, loại tin, link; có gộp tin và giờ yên lặng.

## Goals / Non-Goals

**Goals:**
- Nối tự merge vào **đúng chỗ đang chờ Đại ca** (giữa `pr.mo` và `kiem_merge`), không đổi kiểm lại, QC, mở PR,
  xác minh merge.
- Mọi quyết định "được merge không" tính lại từ sự kiện + Beads + GitHub ngay trước lệnh merge, như luật bằng
  chứng hiện có (spec 4 §6.7).
- Cài đặt theo dự án chỉnh được trên dashboard mà **không đổi cấu trúc DB** và không ghi file trong repo.
- Mỗi bước ghi GitHub hay chạy lệnh deploy có mã thao tác, đọc lại được sau sự cố, không làm hai lần.

**Non-Goals:**
- Không đổi luật chấm cột, hàng rào tầng chốt, kiểm lại, QC, công bố.
- Không merge queue, không tự rebase/cập nhật nhánh PR.
- Không tự chạy migration, không quản bí mật deploy thay Đại ca (khoá SSH, token của máy khách do Đại ca tự đặt
  cho tài khoản trạm, ngoài phạm vi trạm).

## Decisions

### D-1. Điểm nối: một bước "xét tự merge" chen giữa mở PR và xác minh merge
`buoc_github` hôm nay gọi `mo_pr_bead(...) or kiem_merge(...)` cho bead có `cot:cho-review`. Thêm bước thứ ba ở
giữa: `mo_pr_bead → xet_tu_merge → kiem_merge`. Bước mới chỉ làm việc khi PR đã có `pr.mo` cho
`commit_ban_giao` hiện hành và chưa merge. Sau khi merge, **luồng xác minh có sẵn** lo phần còn lại (đọc PR, kiểm
merge commit thuộc nhánh chính, đóng bead) — không viết lại.

*Phương án loại:* bật "auto-merge" của GitHub (`gh pr merge --auto`): GitHub tự merge khi CI xanh, trạm mất quyền
kiểm lại công tắc/tạm dừng/estop ngay trước lúc merge (spec `tu-merge` "Kiểm lại công tắc ngay trước lúc merge").

### D-2. Đánh giá điều kiện là một hàm thuần, trả danh sách lý do
`ly_do_chua_merge(bead, su_kien, cai_dat, pr, ci, du_an) -> list[str]` — rỗng nghĩa là được merge. Thứ tự: estop,
tạm dừng toàn trạm, tạm dừng dự án, `bat_ghi`, công tắc, khoá cứng QC, khoá cứng kiểm lại, đầu PR = commit đã kiểm,
hàng rào `schema` (D76, luôn), rồi ba điều kiện có nút. Hàm thuần nên test từng dòng như `buoc_ke_tiep`. Danh sách
lý do được ghi thành sự kiện `tu_merge.cho` **chỉ khi khác lần trước** (không ghi mỗi vòng tick) để dashboard đọc.

- **QC, kiểm lại:** dùng lại `bang_chung_hien_hanh` (`tram/giao_viec/pr_bang_chung.py`) — đã kiểm `qc.ket_qua = dat`
  sau đúng `kiem.lai` đạt của lượt code mới nhất, ref công bố, `digest_tieu_chi`.
- **CI:** đọc `statusCheckRollup` qua `gh pr view` (thêm trường vào lệnh `view` sẵn có, không thêm lệnh con). Mọi
  check `COMPLETED` + kết luận `SUCCESS`/`NEUTRAL`/`SKIPPED` = xanh; còn chạy = "chờ CI" (không phải lỗi); rỗng =
  chưa xanh. Agent không tự thêm CI giả được vì `.github/workflows/**` thuộc đường dẫn cấm (spec 4 §6.2).
- **Cột (D90):** mọi `giao.nhan` trong bằng chứng hiện hành được cấp khi bead có nhãn `cot:ai-lam` (bộ giao việc chỉ
  cấp phiếu khi điều kiện đó đúng — spec 4 §5.1) và bead không có `cot-khoa`.
- **Hàng rào (D91):** chỉ theo diff — `co-do` trên bead, tính lại tại `commit_ban_giao`: diff từ gốc nhánh
  (spec 4 §6.2 bước 0) khớp `duong_dan` của bất kỳ hàng rào nào. Từ khoá trong nội dung bead **không** tính.
- **D76/D92:** hàng rào `schema` chạy **trước** và **không** theo nút: diff khớp `duong_dan` của nó **hoặc** nội dung
  bead khớp `tu_khoa` của nó (dùng lại hàm khớp từ khoá của luật cứng 1a, bỏ qua phần "escalation đóng chốt hàng
  rào"). Mỗi dự án khai từ khoá và đường dẫn cho cấu trúc DB và xoá dữ liệu vào hàng rào này. Em hiểu D92 là từ khoá
  vẫn tính cho riêng hàng rào này, khác D91 — nếu Đại ca muốn chỉ tính đường dẫn thì bỏ nửa sau.

### D-3. Lệnh merge chặt
`gh pr merge <so> --repo <owner/repo> --merge --match-head-commit <commit_ban_giao>`. `gh.py` thêm `merge` vào lệnh
được phép; test khoá đổi thành: chỉ đúng dạng này, **cấm** `--admin`, `--squash`, `--rebase`, `--auto`,
`--delete-branch`. `--merge` vì xác minh hiện có không chứng minh được squash/rebase. `--match-head-commit` làm
GitHub từ chối nếu đầu PR đã khác commit đã kiểm.

### D-4. Cài đặt lưu bằng sự kiện trong kho sự kiện, không đổi cấu trúc DB
Mỗi lần đổi ghi một sự kiện `tu_dong.cai_dat` (dự án = tên dự án) mang **toàn bộ** cài đặt sau khi đổi + mã thao
tác (D88); giá trị hiện hành = sự kiện mới nhất; `expected_version` = id sự kiện đó. Tạm dừng: `tu_dong.tam_dung` /
`tu_dong.tiep_tuc` (dự án) và cùng loại trên dự án hệ `DU_AN_TRAM` (toàn trạm). Lịch sử "ai đổi gì" tính lúc đọc
bằng so hai bản liền nhau. Cùng mẫu với bật/tắt khe; bảng `su_kien`, `thao_tac` đã có.

*Phương án loại:* (a) tram-api ghi `du-an/<ten>.yaml` — file trong repo trạm: làm bẩn cây git, đua với Đại ca sửa
tay, không có lịch sử; (b) bảng SQLite mới — đổi cấu trúc DB (kill list mục 4) không cần thiết. **Cái giá:** cài
đặt tự động không còn nằm cạnh phần còn lại của cấu hình dự án — dashboard và một lệnh CLI chỉ đọc là chỗ xem.

Ba lệnh lưu cùng sự kiện đó. Khi lưu: mỗi lệnh tách bằng `shlex.split` phải thành công, không rỗng, ≤ 500 ký tự;
chạy qua bộ quét bí mật của memory (`tram/nho/bi_mat.py`, chỉ gọi, không sửa) — khớp thì từ chối 422 "lệnh có vẻ
chứa bí mật" (INV-001, D97).

Mọi đường dẫn tương đối trong repo mà ba lệnh nhắc tới (token argv không tuyệt đối, tồn tại trong repo tại commit
hiện hành) được cộng vào `duong_dan_cam` hiệu lực của dự án khi kiểm đường dẫn cấm (spec 4 §6.2 bước 0) — agent sửa
thì escalation `dong-file-cau-hinh` như hiện nay, không bao giờ tự merge (D89).

### D-5. Kênh ghi từ dashboard
Tuyến mới (đề xuất tên): `GET /api/tu-dong` (tóm tắt mọi dự án + tạm dừng toàn trạm), `GET /api/du-an/{ten}/tu-dong`
(cài đặt, phiên bản, sẵn sàng deploy, việc chờ kèm lý do, lịch sử, bộ đếm hỏng); ghi:
`POST /api/du-an/{ten}/tu-dong/cai-dat`, `…/tam-dung`, `…/tiep-tuc`, `…/deploy`, `POST /api/tu-dong/tam-dung`,
`…/tiep-tuc`. Mọi tuyến ghi dùng `Depends(yeu_cau_ghi)` và `chay_thao_tac`. Cài đặt và Deploy kiểm
`expected_version` / `expected_commit` (409); tạm dừng và tiếp tục **không** kiểm (như estop). Khoá cứng QC, kiểm lại
và D76 **không có trường** trong hợp đồng ghi: gửi trường lạ → 422.

**D87:** khi `cach_ly.kenh_ghi` còn là `header`, mọi tuyến ghi của tính năng này trả 403 "cần kênh ghi unix-socket" —
trừ TẠM DỪNG và Tiếp tục (chiều an toàn); `GET` trả thêm cờ để dashboard khoá nút kèm giải thích. Lý do: với kênh header, một tiến trình agent trên máy B giả được
danh tính, bật tự merge hoặc đặt lệnh deploy tuỳ ý chạy dưới tài khoản trạm.

### D-6. Deploy chạy ở luồng riêng, dưới tài khoản trạm, trong bản sạch
- **Khi nào:** sau mỗi `pr.da_merge` đã xác minh — tự merge hay Đại ca gộp tay (D96) → nếu tự deploy tắt hoặc merge
  là gộp tay: ghi `deploy.san_sang {commit_moi_nhat, so_merge}`; tự deploy bật và merge là tự merge: tạo yêu cầu
  deploy nguồn `tu_dong`. Nút Deploy tạo yêu cầu nguồn `dai_ca`. `GET /api/phe-duyet` thêm một dòng mỗi dự án đang
  sẵn sàng deploy, cộng vào số đếm (D101).
- **Luồng:** thêm pha `vong_deploy` (luồng thứ ba cạnh `vong_nhanh`, `vong_git`) để deploy dài không chặn kiểm lại
  của dự án khác. Mỗi dự án một khoá; một chuỗi một lúc. *Phương án loại:* chạy trong `vong_git` — một chuỗi xấu nhất
  ~32 phút sẽ chặn mọi kiểm lại.
- **Ở đâu:** worktree tách rời `~/.tram/kho-deploy/<du_an>` tại commit cần deploy, lấy từ kho kiểm của trạm. Lệnh
  chạy với thư mục làm việc đó, **không qua shell** (`shlex.split` → argv), môi trường tối thiểu: `PATH`, `HOME`,
  `LANG`, `TRAM_DU_AN`, `TRAM_DEPLOY_COMMIT`, `TRAM_DEPLOY_COMMIT_TRUOC` (commit của lần deploy thành công gần
  nhất; trống ở lần đầu). Không truyền biến môi trường nào của tram-api.
- **Chạy lệnh:** dùng lại phần "chạy lệnh có giới hạn, giết cả nhóm tiến trình" của `tram/kiem/` (chỉ gọi). Hạn: deploy
  15 phút, kiểm còn sống 2 phút, lùi 15 phút, hằng chung mọi dự án (D100).
- **Chuỗi:** `deploy.bat_dau {commit, commit_truoc, nguon, ma_thao_tac}` → mỗi lệnh `deploy.lenh {buoc, ma_thoat,
  giay, digest_log}` → `deploy.xong {ket_qua: dat | da_lui | lui_hong | khong_ro, dem_hong}`. Bộ đếm hỏng liên tiếp
  tính lúc đọc từ chuỗi `deploy.xong` kể từ lần `dat` hoặc lần Đại ca bật lại tự deploy. Đạt 3 → sự kiện
  `tu_dong.cai_dat` mới với tự deploy tắt, tác nhân `tram/tu-deploy`.
- **Đầu ra lệnh:** qua bộ quét bí mật rồi ghi file `~/.tram/deploy-log/<du_an>/<ma_thao_tac>.log` quyền 0600, giữ 30
  ngày. Sự kiện chỉ giữ mã thoát, thời gian, digest.

### D-7. Idempotency và đối soát
- **Merge:** mã `tm-` + sha256(dự án, bead, commit). Ghi `tu_merge.bat_dau` **trước** lệnh `gh`. Vòng sau thấy
  `bat_dau` mà chưa có `pr.da_merge`/`tu_merge.loi`: đọc PR — `MERGED` → để `kiem_merge` xác minh; `OPEN` và điều
  kiện vẫn đủ → gửi lại đúng lệnh (an toàn nhờ `--match-head-commit`); khác → `tu_merge.loi`. Lỗi `gh` ba vòng liền
  cho cùng bead → `tu_merge.loi`, ngừng thử bead đó, chờ Đại ca, báo tin "trạm lỗi".
- **Deploy:** mã `dp-` + sha256(dự án, commit, nguồn, mã yêu cầu). Lệnh deploy **không** coi là lặp được: có
  `deploy.bat_dau` mà không có `deploy.xong` khi trạm chạy lại → ghi `deploy.xong {ket_qua: khong_ro}`, tạm dừng tự
  deploy dự án, báo tin (spec `tu-deploy` "Kết quả deploy không rõ").
- **Thao tác dashboard:** bảng `thao_tac` + `ghi_su_kien_mot_lan` như mọi thao tác hiện có.

### D-8. Báo tin
Thêm loại tin vào `tram/bao_tin/tin.py` và nguồn sự kiện ở `nguon.py`: `tu_merge`, `san_sang_deploy`,
`deploy_xong`, `deploy_da_lui`, `tu_deploy_tu_tat`, `deploy_khong_ro`, `lui_hong`, `cai_dat_doi` (D99). Giờ yên lặng
(D98): tin xấu (`deploy_da_lui`, `tu_deploy_tu_tat`, `deploy_khong_ro`, `lui_hong`) gửi ngay; tin tốt (`tu_merge`,
`san_sang_deploy`, `deploy_xong`) gom gửi khi hết giờ yên lặng. Tin giữ khuôn hiện có: dự án, mã bead, nhãn loại,
link — không SHA, URL PR, đầu ra lệnh, nội dung lệnh. Không sửa `telegram.py`.

### D-9. Estop, tạm dừng
- Tự merge nằm trong `vong_git` → estop đã chặn sẵn; vẫn kiểm lại ngay trước lệnh merge (D-2).
- `vong_deploy` kiểm estop và tạm dừng **trước khi bắt đầu** chuỗi; không kiểm giữa chuỗi (làm nốt an toàn).
- Tuyến Deploy của Đại ca từ chối khi estop bật (INV-004); vẫn nhận khi chỉ tạm dừng (D97).

### D-11. Tự gộp PR spec đã duyệt (D95)
Trong `buoc_github`, nhánh feature `theo-plan` hôm nay gọi `mo_pr_spec`. Thêm bước sau nó: nếu công tắc tự merge của
dự án bật, không tạm dừng, không estop, `bat_ghi` đúng, kênh ghi không chặn, có `pr.mo` loại `spec` cho commit của
`spec.duyet` mới nhất và commit đó chưa là tổ tiên nhánh chính → cùng lệnh merge chặt của D-3 với
`--match-head-commit <commit spec.duyet>`. Không áp 5 điều kiện của việc code (spec chỉ đổi `docs/**`, đã kiểm lúc
`spec.xong`; lần duyệt của Đại ca thay cho QC). Xác minh: điều kiện 8 của spec 4 §5.1 (`spec_merge`) thấy commit đã
vào nhánh chính thì giao việc con như hiện nay; sự kiện `tu_merge.xong {loai: spec}` + tin Telegram `tu_merge`.

### D-12. Bảo vệ nhánh GitHub (D94)
Chỉ bật "bắt buộc CI xanh"; chưa bật "bắt buộc cập nhật theo nhánh chính". Hướng dẫn chỉnh tay cho tài khoản trạm
ghi vào kịch bản cổng chạy thật khi tới lúc, không ở đây.

### D-10. Giao diện
Theo mockup đã duyệt (D101): trang `#/du-an/<ten>` "Tự động" (đã khớp `mucCua` của `frontend/src/menu.js` nên mục
"Dự án" sáng), thẻ dự án ở `#/du-an` có chip tóm tắt và link sang. Nút TẠM DỪNG toàn trạm màu vàng ở thanh trên cạnh
Estop, băng cảnh báo dưới thanh trên. Trang Phê duyệt thêm dòng "sẵn sàng deploy" mỗi dự án. Thành
phần mới: công tắc (`role="switch"`), băng tạm dừng. Màu dùng token sẵn có (`--nen-canh-bao`, `--vien-canh-bao`,
`--chu-canh-bao`, `--nen-estop`…). Mockup: `docs/mockup/2026-10-18-tu-merge-tu-deploy/` (đã duyệt; khối "agent tự cập
nhật việc" trong đó thuộc spec của `bs-2bd.5`).

## Tích hợp ngoài — bốn câu của `AGENT_RULES.md` §15

| | `gh pr merge` + đọc CI (`gh pr view`) | Ba lệnh deploy / kiểm còn sống / lùi của dự án |
| --- | --- | --- |
| **Timeout, ai áp** | 60 giây mỗi lệnh, `chay_gh` áp (`subprocess.run(timeout=60)`) | 15 / 2 / 15 phút, trạm áp qua `tram/kiem/`, quá hạn giết cả nhóm tiến trình |
| **Hỏng thì Đại ca thấy gì** | Bead ở "chờ Đại ca" với lý do "GitHub lỗi khi merge — thử lại vòng sau"; sau 3 vòng: "tự merge lỗi, cần Đại ca" + Telegram "trạm lỗi". PR vẫn mở, Đại ca merge tay được | Dòng lịch sử đỏ "hỏng · mã thoát N · X giây", Telegram "đã tự lùi"; lùi hỏng: băng "tạm dừng" của dự án + tin khẩn; không rõ kết quả: dòng "không rõ — cần Đại ca kiểm" |
| **Retry có an toàn** | Có: `--match-head-commit` + đọc lại PR trước khi gửi lại; merge PR đã merge thì GitHub từ chối vô hại | **Không** tự lặp deploy hay lùi. Chỉ chạy lùi sau một deploy hỏng **đã biết**; kết quả không rõ thì dừng chờ Đại ca |
| **Log có lọt bí mật/nội dung bead** | Không ghi stdout/stderr của `gh` (như `LoiGh` hiện có, chỉ mã lỗi); tiêu đề PR không đưa vào sự kiện | Đầu ra chỉ vào file 0600 sau bộ quét bí mật; sự kiện/dashboard/Telegram chỉ mã thoát, thời gian, digest; môi trường lệnh không mang biến của tram-api; lệnh có vẻ chứa bí mật bị từ chối khi lưu |

## Vùng kill list bị chạm

| Mục `AGENT_RULES.md` §2 | Chỗ chạm | Vì sao cần |
| --- | --- | --- |
| 5 — đẩy code, PR, merge, deploy | `tram/giao_viec/gh.py` (thêm `merge`), `tick_github.py`, bước tự merge mới, package deploy mới | Lõi của tính năng |
| 7 — công tắc lớn | công tắc tự merge, tự deploy, tạm dừng dự án/toàn trạm | D69, D74, D78 |
| 1 — cửa danh tính | tuyến ghi mới dùng `yeu_cau_ghi` (`tram/api/bao_mat.py`); đòi kênh `unix-socket` trừ TẠM DỪNG (`tram/api/kenh_ghi.py`) | D79, D87 |
| 8 — chạy thật | thử trên repo nháp S7; Đại ca chỉnh bảo vệ nhánh GitHub; cổng mới trong sổ tay | D69 |
| 2 — bộ quét bí mật | **chỉ gọi** `tram/nho/bi_mat.py`, không sửa | INV-001 |
| 4 — cấu trúc DB | **không chạm**: chỉ thêm loại sự kiện | D-4 |

## Risks / Trade-offs

- [Hai PR mỗi cái xanh, gộp lại hỏng — không có merge queue] → kiểm còn sống + tự lùi; D94 chưa bật "bắt buộc cập nhật
  theo nhánh chính", bật sau nếu xảy ra.
- [Agent sửa script deploy trong repo, script chạy dưới tài khoản trạm có quyền đẩy GitHub] → file mà ba lệnh nhắc tới
  thành file cấm sửa (D89); môi trường lệnh tối thiểu. Còn hở: script gọi tiếp file khác không nhắc trong lệnh — khuyên
  Đại ca để script deploy ngoài repo (như mockup: `/Users/Shared/tram-deploy/…`).
- [Kênh ghi `header` giả được từ máy B] → chặn ghi của tính năng trừ TẠM DỪNG tới khi có `unix-socket` (D87).
- [D91 chỉ xét đường dẫn: việc nhạy cảm mà diff nằm ngoài `duong_dan` của hàng rào vẫn được tự merge] → Đại ca giữ
  `duong_dan` hàng rào đủ rộng; bắt đầu ở repo nháp (D69); tạm dừng một chạm.
- [PR spec tự gộp ngay khi duyệt (D95): duyệt nhầm thì spec đã vào nhánh chính] → việc con vẫn qua đủ 5 điều kiện;
  sửa spec bằng một feature/PR mới như hôm nay.
- [Lùi code nhưng không lùi được dữ liệu] → D76/D92 giữ mọi thay đổi cấu trúc DB và việc nói tới xoá dữ liệu chờ Đại
  ca; nhận biết bằng từ khoá vẫn có thể sót.
- [Phải nới bảo vệ nhánh GitHub cho tài khoản trạm merge] → giữ "bắt buộc CI xanh"; không bao giờ dùng `--admin`.
- [Nhiều tin Telegram khi merge dồn] → cơ chế gộp tin sẵn có (`tram/bao_tin/chong_on.py`).
- [Cài đặt tự động không nằm trong `du-an/*.yaml`] → dashboard + lệnh CLI chỉ đọc hiện đủ; lịch sử đổi có sẵn.
- [Deploy dài chặn vòng tick] → luồng `vong_deploy` riêng (D-6).

## Migration Plan

1. Code toàn bộ sau công tắc mặc định tắt (không dự án nào đổi hành vi khi ghép).
2. Điều kiện trước khi bật lần đầu: kênh ghi `unix-socket` chạy thật; cổng S7 (repo nháp GitHub, `gh`) đạt;
   `cong_bo.phuong_an` đã chọn.
3. Đại ca chỉnh tay bảo vệ nhánh của **repo nháp** để tài khoản trạm merge được: chỉ bắt buộc CI xanh (D94).
4. Thêm cổng mới vào sổ tay chạy thật (vd "G8 — tự merge/tự deploy repo nháp"): kịch bản từng bước, Đại ca cho phép
   từng kịch bản (tự merge; sẵn sàng deploy + bấm Deploy; deploy hỏng → lùi; 3 lần hỏng → tự tắt; tạm dừng; estop).
5. Chạy trên repo nháp tới khi Đại ca thấy ổn; rồi hỏi 3 lệnh của HR Codex, bật riêng cho HR Codex.
6. **Đường lui:** tắt công tắc hoặc TẠM DỪNG toàn trạm (một chạm, có hiệu lực vòng tick kế). Lui mã: revert nhánh;
   sự kiện mới chỉ là dòng ghi thêm, mã cũ bỏ qua loại lạ. Gỡ `merge` khỏi lệnh `gh` được phép là trở lại ADR-0007.
7. Khi xong và archive: ADR mới "Trạm tự merge có điều kiện" thay ADR-0007 ở phần "chỉ Đại ca merge"; sửa
   `AGENT_RULES.md` §11, `PROJECT.md`, `PRODUCT_ARCHITECTURE.md`, `MODULES.md`, `DESIGN_SYSTEM.md`.

## Open Questions

Không còn. 16 câu của bản nháp đầu đã được Đại ca trả lời (D87–D101, `docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`).
Một chỗ Em diễn giải, cần Đại ca liếc lại khi duyệt bản này: D92 cho hàng rào cấu trúc dữ liệu tính **cả từ khoá trong
nội dung việc**, trong khi D91 bỏ từ khoá cho các hàng rào còn lại (D-2).
