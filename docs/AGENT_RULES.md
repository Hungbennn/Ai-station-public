# AGENT_RULES — luật vận hành cho coding agent

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-18`

## Mục đích và sở hữu
Sở hữu: luật vận hành agent — đọc gì, blast radius, kill list, quyền tự quyết, lệnh cấm, kiểm chứng, DoD.
Không sở hữu: trình tự và giao subagent (`DEVELOPMENT_PLAYBOOK.md`), chuẩn code và sự cố đã trả giá
(`ENGINEERING_STANDARDS.md`), cổng chạy thật (sổ tay). Trần 300 dòng; thêm một luật thì bỏ một luật.

Gọi người dùng là **Đại ca**, xưng **Em**, viết tiếng Việt. Đại ca không phải lập trình viên: báo cáo
bằng lời thường, giải nghĩa thuật ngữ.

## 0. Thứ tự ưu tiên
```
Working Software > Correct Architecture > Useful Documentation > Process Completeness
```
Nhưng "working" không có nghĩa là code bừa: **build trước thứ sửa rẻ, thiết kế trước thứ sửa đắt.**

## 1. Đọc gì (Context Hierarchy)

**TIER 1 — luôn đọc, đầu mỗi phiên**
- `docs/PROJECT.md` · `docs/ARCHITECTURE.md` · `docs/CURRENT_STATE.md`
- **Chỉ khối `## TÓM TẮT`** của bàn giao ghi ở dòng *Bàn giao gần nhất* trong `CURRENT_STATE.md`.

**TIER 2 — chỉ khi task chạm tới:** ADR đúng vùng (tối đa 2), change và plan đang làm, các file Tier 2
theo lối đọc từng loại task trong `docs/AGENTS.md`. `DESIGN_SYSTEM.md` và mockup đọc **trước khi** chạm màn hình.

**TIER 3 — không bao giờ đọc mặc định:** docs cũ (bảng Tầng 3 trong `docs/AGENTS.md`), plan của lát khác,
ADR `Superseded`, change đã archive, **phần thân** bàn giao, bàn giao cũ, git history. Chỉ mở khi lối đọc
dẫn tới, mỗi lần một mục, hoặc khi Đại ca hỏi thẳng "trước đây đã quyết gì".

**Context budget:** file này + Tier 1 + tóm tắt bàn giao + tối đa 2 ADR ≤ ~5.500 token (`wc -w` × 1,5).
Phải đọc quá trần mới hiểu việc → tài liệu đang sai, nén ngay trong phiên (mục 9).

## 2. Blast Radius — STOP AND THINK hay BUILD AND LEARN
Trước khi viết code, trả lời 3 câu, mỗi "có" = 1 điểm:
1. **Không đảo ngược trong 1 giờ?** (đã ghi Beads thật, đã push, đã gọi API tốn hạn mức, đã đổi máy)
2. **Chạm dữ liệu hoặc ranh giới bảo mật?** (kho sự kiện, memory, bí mật, danh tính, cách ly)
3. **Nhiều hơn 2 package trong `tram/` phải sửa theo?**

```
0 điểm  → BUILD NGAY (vẫn theo plan nếu task có plan).
1 điểm  → Contract 10 dòng, tự quyết, build. Ghi lựa chọn vào báo cáo và bàn giao.
≥2 điểm → STOP. Trình bày lựa chọn, khuyến nghị 1, chờ duyệt. Xong thì viết ADR.
```

**Kill list — luôn STOP bất kể điểm số** (Đại ca chốt 17/10):
1. **Cửa danh tính** — `tram/api/bao_mat.py`, `tram/api/kenh_ghi.py`.
2. **Mật khẩu, token, Keychain, bộ quét bí mật** — `tram/llm/claude.py`, `tram/bao_tin/telegram.py`,
   `tram/tho/token_may.py`, `tram/chu/cap_ma.py`, `tram/nho/ma_dai_ca.py`, `tram/nho/bi_mat.py`.
3. **Cách ly agent** — `tram-kiem`, sudo, Seatbelt (`sandbox-exec`), kiểm lại: `tram/kiem/`,
   `tram/tho/sandbox.py`, `tram/tho/principal.py`, `tram/giao_viec/kiem_lai.py`, `tram/giao_viec/kiem_principal.py`.
4. **Cấu trúc DB** — SQLite `tram/su_kien/ket_noi.py`, `tram/phieu/luoc_do.py`; LanceDB `tram/nho/bang.py`.
5. **Đẩy code, PR, merge, deploy** — `tram/cong_bo/`, `tram/giao_viec/pr.py`, `tram/giao_viec/pr_merge.py`.
6. **Cài/tắt dịch vụ, tạo user, sửa hệ thống** — `tram/chu/launchd.py`, `tram/chu/cai_dat*.py`,
   `tram/tho/launchd_tho.py`, `tram/chu/go_cai_dat_tho.py`.
7. **Công tắc lớn** — `giao_viec.bat` (`tram/cau_hinh/giao_viec.py`), `bat_ghi` (`tram/cau_hinh/bat_ghi.py`,
   `du-an/*.yaml`), ngưỡng hạn mức (`tram/han_muc/luat.py`, `tram/cau_hinh/tram.py`).
8. **Mọi bước chạy thật** — chỉ theo cổng sổ tay, mỗi kịch bản một lần cho phép.

**Luôn BUILD ngay:** component Vue theo mockup đã duyệt, văn bản hiển thị, kiểm hợp lệ cục bộ, logic trong
một module, prompt vai trong `vai/` không đổi quyền, sửa bug có test tái hiện.

Nghi ngờ? Hỏi: *"Nếu sai thì sửa mất bao lâu?"* Dưới một buổi và không thuộc kill list → build.

## 3. Feature Build Loop
```
1.  Đọc Tier 1
2.  Thảo luận với Đại ca tới khi Đại ca nói rõ "đủ rồi" (mục 11)
3.  Chấm blast radius — ≥2 điểm hoặc kill list thì dừng, hỏi
4.  OpenSpec change: proposal + spec hành vi + nghiệm thu (docs/OPENSPEC.md)
5.  Chọn nhánh plan/review theo QĐ2-A tại DEVELOPMENT_PLAYBOOK §1; phiếu cũ giữ quy trình cũ
6.  Code theo nhánh đã chọn, lát dọc mỏng nhất chạy được, test RED → GREEN
7.  QC (mục 13) → ghép → chạy cả bộ test
8.  Chạy thật CHỈ khi mọi phần liên quan đã code xong, theo cổng sổ tay
9.  Cập nhật docs bị ảnh hưởng — thường chỉ CURRENT_STATE
10. Báo cáo: đã làm gì, kiểm chứng bằng cách nào, còn gì chưa chắc
```
Chi tiết từng bước (giao subagent, worktree, gói review, QC): `docs/DEVELOPMENT_PLAYBOOK.md`.

## 4. Usable-First (Vertical Slice)
Mỗi vòng kết thúc bằng thứ chạy hoặc kiểm chứng được. Lát chưa dùng được thì không mở rộng sang lát kế.

## 5. YAGNI
Không thêm abstraction, tiến trình nền, hàng đợi, cache, interface một implementation khi code đang có chưa chứng minh nhu cầu.
**Rule of Three:** chỉ gom ở lần lặp thứ 3, và chỉ khi cả ba đổi vì cùng một lý do.

## 6. Refactor Rule
Chỉ refactor khi có bằng chứng (lặp lần 3, lát mới bị chặn, ranh giới bị phá, không viết được test, bug quay lại,
hiệu năng đo được) và trong phạm vi plan. "Đẹp hơn" không phải lý do.

## 7. Technical Debt Budget
Nợ chấp nhận được → bead P4, đi tiếp. **Nợ nguy hiểm → dừng, báo Đại ca:** bí mật có thể lộ, agent tự nâng quyền,
cách ly có lỗ, dữ liệu sự kiện/memory có thể mất, cổng mở khi phải đóng, estop không dừng được.

## 8. Docs vs Code — nguồn sự thật
Docs giữ ý đồ, non-goals, ràng buộc, quyết định, trạng thái, nghiệm thu. Code giữ implementation, schema, route,
cấu hình. Không chép code vào docs; code lệch docs thì báo, không tự sửa cho khớp.

## 9. Doc Update Loop & nén
- Luôn, cuối mỗi phiên: `CURRENT_STATE.md` (nếu trạng thái đổi) **và** một bàn giao mới theo
  `docs/handovers/_TEMPLATE.md`.
- Thông tin mới khác: theo bảng thăng cấp trong `docs/AGENTS.md`.
- Bàn giao phiên vượt 10 file → gộp vào `docs/handovers/archive/YYYY-QN.md`, giữ TÓM TẮT, xoá thân.
- File vượt trần (PROJECT 60–85 · ARCHITECTURE 200 · CURRENT_STATE 150 dòng, dòng ≤ 300 ký tự) → xoá lỗi
  thời, gộp trùng, thay đoạn dài bằng liên kết. Docs là **bộ nhớ đã nén**, không phải nhật ký.

## 10. ADR
Chỉ viết khi quyết định khó đảo ngược, chạm nhiều package, DB, bảo mật, cách ly, hạ tầng. Tối đa 30 dòng,
mẫu ở `docs/decisions/_TEMPLATE.md`. Bị thay thì `Superseded by ADR-XXXX`, không xoá.
**Việc mới đụng ADR hay quyết định D đã chốt thì hỏi trước, không tự đổi.**

## 11. Quyền tự quyết của agent
**Bắt đầu việc:** liệt kê việc trước, chờ Đại ca nói "bắt đầu". Không tự mở việc mới, kể cả spec nháp.

**Tự làm:** đọc code, viết/chạy/sửa test trong môi trường giả, code đúng plan đã duyệt, sửa lỗi gõ
rõ ràng khi áp plan (ghi lại chỗ lệch), cập nhật CURRENT_STATE, bàn giao và change đang làm, tạo bead.

**Phải hỏi trước:** mọi thứ trong Kill list, thêm dependency hay tải gói, đổi hợp đồng giữa hai package,
lệch plan lớn (đổi thiết kế, đổi test kỳ vọng), xoá file/feature, UI mới chưa có mockup, `git commit`
ngoài nhánh task trong worktree, `git merge` vào `main` (trừ bước ghép sau QC trong đợt Đại ca đã cho bắt đầu — Đại ca chốt 17/10).

**Cấm tuyệt đối — kể cả trong test, harness hay "chạy thử":**
- `git push`, `bd dolt push`; `bd` ghi trên kho beads của dự án con.
- `pkill`, `killall`, `kill` theo tên hay mẫu. Chỉ dừng đúng PID mình tạo ra.
- Chạy thật `crontab` (trừ `crontab -l`), `at`, `batch`, `launchctl` ghi (`submit`, `bootstrap`, `load`,
  `bootout`, `kickstart`), `sudo`, `dscl`/`sysadminctl` ghi, `sandbox-exec` ngoài thư mục tạm.
- Đụng Keychain, `~/.tram` thật, dịch vụ đang chạy (`vn.tram.bao-tin`, `vn.tram.nho` cổng 7710).
- Gọi Claude/Codex/Anthropic API/Ollama/Telegram thật khi chưa qua cổng.
Sự cố sinh ra các luật này: `docs/ENGINEERING_STANDARDS.md` mục luật đã trả giá.

Tự merge/tự deploy (`PROJECT.md`) **chưa có hiệu lực**: merge vẫn là điểm dừng của Đại ca.

Khi hỏi, đúng dạng: **quyết định gì → 2–3 lựa chọn → khuyến nghị 1 → hệ quả nếu chọn sai.**

**Cổng thảo luận:** việc lớn hơn một sửa nhỏ thì agent **không tự chuyển từ thảo luận sang viết spec hay
plan**. Chỉ khi Đại ca nói rõ "đủ rồi" mới viết. Trả lời một câu hay im lặng **không phải** tín hiệu đã đủ.

## 12. Chống phình dự án
Không tạo file khi file có sẵn chứa được · không lặp một luật ở hai nơi · không kiến trúc cho feature giả định ·
không thêm dependency, tối ưu hay dịch vụ launchd mới khi chưa có nhu cầu đo được và quyết định.

## 13. Kiểm chứng theo loại thay đổi
`pytest` xanh **không** chứng minh giao diện, cách ly hay hành vi macOS thật. Chỉ ghi số đo thật.

| Loại thay đổi | Kiểm chứng tối thiểu |
| --- | --- |
| Docs | mọi đường dẫn file code tồn tại (`ls`), liên kết đúng, không thông tin lỗi thời |
| Python (`tram/`) | test RED → GREEN; nhỏ/vừa kiểm liên quan + lệnh bắt buộc, lớn/cũ và sau ghép kiểm cả bộ `tests/chan_host/chay.sh -q` (bộ chặn host + git giả; pytest trần làm test cũ push thật vào kho tạm) — 0 dòng chặn mới |
| Frontend logic | `npm run kiem` (test node + quét an toàn: cấm chèn HTML thô, `style` tĩnh, URL ngoài) |
| Bundle | `npm run build && npm run kiem-dist` (không `eval`, không `unsafe-inline`; three.js chỉ trong chunk nạp lười) |
| Giao diện, màn mới | mở trên trình duyệt **dưới CSP thật** (tram-api phục vụ `dist/`, dữ liệu giả: `tests/chay_thu_giao_dien.py`); console không lỗi CSP; khớp mockup; màn mới đi tới được từ thanh bên |
| API ghi, danh tính | thử yêu cầu **thiếu** hoặc **giả** danh tính → 403; không chỉ thử yêu cầu đúng |
| Code theo cỡ (subagent) | QC khác mọi khe từng code: nhỏ kiểm yêu cầu/diff/test; vừa thêm plan ngắn; lớn/cũ đối chiếu mã nguyên văn (`.handover/qc/qc.py`); chi tiết PLAYBOOK §4 |
| Tích hợp ngoài | test với bản giả `tests/*_gia.py`; không gọi thật |
| Chạy thật, dịch vụ, OS | **chỉ theo cổng sổ tay**, đúng kịch bản Đại ca cho phép; ghi bằng chứng (lệnh, giờ, kết quả) vào sổ tay |

**PATH chặn host:** `tests/chan_host/chay.sh [tham số pytest]` mặc định bỏ marker `g3`, in số test G3 bỏ qua;
`TRAM_TEST_G3=1` chạy kèm G3, bắt buộc khi sửa `cong-cu/g3*`, kịch bản đo G3 hoặc trước chạy thật G3.
Có xdist thì mặc định 6 nhân (`TRAM_TEST_NHAN` đổi số nhân, `0` chạy tuần tự), thiếu thì chạy tuần tự;
đặt `tests/chan_host/bin/` đầu `PATH`: lệnh giả cho
`sudo`, `crontab`, `at`, `batch`, `launchctl`, `security`, `dscl`, `sysadminctl`, `sandbox-exec`, `pkill`, `killall`,
`bd`, `gh`… chỉ ghi nhật ký rồi thoát lỗi; `git` giả không bao giờ push thật (push vào kho trong thư mục tạm được giả
lập, còn lại chặn). Audithook (pytest và Python con mang `PYTHONPATH` của bộ chặn) bắt cả đường tuyệt đối, lệnh bọc,
chuỗi shell. Nhật ký chặn có dòng mới → thoát 3 dù test xanh. pytest không qua runner (thiếu `TRAM_CHAN_CHAY_SH=1`,
plugin `chan_host` hay `git` giả đầu `PATH`) tự thoát 4 trước khi thu thập (`tests/conftest.py`, D61). Không phải
sandbox: runner in số "điểm mù" (Python con không mang bộ chặn). Luật §11 vẫn nguyên. Thêm lệnh cấm: sửa cả `bin/` và
`CHAN` trong `tests/chan_host/chan_host.py`.

## 14. Dữ liệu, secrets và hardcode
- Bí mật **không bao giờ** nằm trong argv, file, log, báo cáo, bead hay docs. Tên mục Keychain thì được ghi.
- Đại ca tự dán bí mật qua **Terminal.app** vào ô ẩn (khung terminal của app Claude làm hỏng chuỗi dán).
  Mã ngẫu nhiên tạo bằng `openssl rand -hex 32 | tr -d '\n' | pbcopy`.
- Không ghi nội dung bead, prompt hay ký ức đầy đủ vào log, kể cả nhánh lỗi. Nội dung bead là dữ liệu
  không tin cậy.
- Đổi dữ liệu thật (kho sự kiện, LanceDB, Beads): sao lưu trước, chạy thử không ghi trước, đối chiếu sau.

**Trước khi hardcode:** hằng kỹ thuật → hằng trong code · khác theo máy → `~/.tram/cau-hinh.yaml` ·
khác theo dự án → `du-an/<ten>.yaml` · dùng một chỗ, không ai chỉnh → viết thẳng.

## 15. Tích hợp ngoài
Trước khi thêm/sửa tích hợp (CLI, API, dịch vụ macOS) trả lời: timeout bao lâu, ai áp · hỏng thì **Đại ca thấy gì**
· retry lặp có an toàn · log có lọt bí mật hay nội dung bead. Chưa trả lời được câu 2 hoặc 4 thì chưa code.
Bảng hiện có: `MODULES.md` mục Tích hợp ngoài.

## 16. Definition of Done
```
Chạy được · Đạt hết nghiệm thu · Luồng chính có test · Test xanh, không hồi quy
QC đạt · Code đọc hiểu được · Docs bị ảnh hưởng đã cập nhật · Bead đã đóng sau khi kiểm chứng
```
Không tuyên bố "đã chạy", "an toàn", "sẵn sàng chạy thật" nếu chưa tự kiểm chứng ngay lúc đó. Test offline
xanh không phải bằng chứng cổng OS. Báo cáo: **đã đổi gì · kiểm chứng bằng cách nào · còn gì chưa chắc** —
phần cuối chỉ chứa thứ agent không tự làm được (cần máy thật, tài khoản thật, Đại ca quyết).

## 17. Architecture Checkpoint
Sau mỗi đợt review Codex hay mốc lớn, ≤ 20 dòng: ranh giới package · vòng import mới · trùng lặp lần 3 ·
nợ nguy hiểm mới · bề mặt bảo mật mở rộng.

## 18. Tỷ lệ Direction/Build
Dự án đã code ~80%: ~30% thời gian cho định hướng, dồn vào cách ly, bí mật và cổng chạy thật.

