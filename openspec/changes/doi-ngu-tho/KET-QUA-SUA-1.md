# Kết quả sửa QC đội ngũ thợ — lần 1

Ngày 20/10/2026, worktree `code-doi-ngu`, nhánh `code/doi-ngu-tho`, nền `f22cbf0`.
Phạm vi: 21 lỗi người điều phối đo ngoài sandbox trên máy B; cả 21 xanh trên main `a96bc13`.
Không chạy toàn suite, commit, push, `bd`, sudo hay launchctl ghi. Chỉ sửa cây hiện tại.
Chỉ ghi báo cáo ở đây theo yêu cầu mới nhất; không sửa CURRENT_STATE hoặc bàn giao cũ.

## Từng lỗi và cách sửa

| Lỗi QC | Nguyên nhân gốc | Sửa | Kiểm chứng |
|---|---|---|---|
| 5 ca `test_theo_doi_dung.py` | Fixture `nc.ch` thiếu `tren_may_b`; `_moc` lỗi trước khi gửi hoặc handshake | Thêm `tren_may_b=False` vào fixture chung; giữ nguyên toàn bộ assertion | Cả file xanh trong nhóm 55 |
| 9 ca `test_deploy_review_v2.py` (5 `khach`, 4 `doi`) | Fixture kết thúc xong thiếu cùng thuộc tính | Thêm `tren_may_b=False`; giữ nguyên assertion về chặn runner, đường cấm, SHA, nội dung báo cáo | Cả file xanh trong nhóm 55 |
| `test_de_nghi_tho.py::test_bo_doc_hang_doi_gui_ngay_khong_dung_phieu` | Dùng lại fixture `dung` ở `test_theo_doi_dung.py` | Sửa đúng fixture chung bên trên; không sửa file hoặc assertion của ca này | Xanh trong nhóm 55 |
| `test_phieu_chay_thu_hoi.py::test_loi_thu_hoi_lan_sau_khong_don_phieu` | Ngữ cảnh giả chỉ có `don_khe`, thiếu `ch`; nhánh `finally` che mất `LoiThuHoi` gốc bằng AttributeError | Thêm `ch=SimpleNamespace(tren_may_b=False)`; giữ assertion về lần chạy, không dọn và tháo khoá | Xanh trong nhóm 55 |
| `test_kich_ban_3a2.py::test_thieu_moi_truong_kiem_bao_bi_khong_chay_cli` | `LoiMoiTruongKiem` kế thừa ValueError nên bị nhánh B gom thành `LoiThuHoi`; không đi tới `bao_khong_chay` | B bắt riêng lỗi môi trường trước khi đánh dấu sẵn sàng/trao quyền, đóng cổng, dọn cây và đăng ký worktree, trả `thieu-moi-truong-kiem`; luồng cũ gửi `bao.bi` và xoá sổ | Ca tích hợp **giữ nguyên nguyên văn**, xanh trong nhóm 55; hai test B riêng RED→GREEN |
| `test_kich_ban_3a2.py::test_tron_vong_code_moc_cong_bo_xong_lenh_kiem` | Test vẫn đòi hai lần công bố và một `bao.moc` trên B; QĐ3-A đã chuyển mốc B thành tiến độ cục bộ | Tham số hoá B/từ xa. B chỉ một công bố khi xong, không `bao.moc`; từ xa giữ hai công bố/một mốc. Giữ kiểm SHA, lệnh kiểm, phiếu/hộp thư/PID | Có trong lượt hồi quy; căn cứ từng assertion bên dưới |
| `test_kich_ban_3a2.py::test_cli_thoat_giua_chung_lan_sau_co_ban_giao_tam_roi_xong` | Đọc prompt sau xong tại worktree kiểu cũ; B dùng cây riêng rồi dọn sau kết thúc | B/từ xa cùng ghi nhận nội dung stdin thật sau CLI lần hai, trước dọn. B xác nhận cây đã mất; từ xa giữ assertion đọc file ở đường dẫn cũ | Có trong lượt hồi quy; giữ kỳ vọng hai kết quả `loi`, `xong` và nội dung “Lần chạy 2” |
| `test_kich_ban_3a2.py::test_thu_hoi_dung_cung_khong_push_khong_bao_va_push_tre_khong_doi_ref_h2` | Chờ `bao.moc` để thu hồi, nhưng B không gửi sự kiện đó; hết chờ dẫn đến tắt daemon/giữ phiếu. Giả định ref công bố đã có cũng không còn đúng trên B | B đợi sổ đã đọc mốc rồi thu hồi; xác nhận không mốc/công bố và ref vẫn chưa tồn tại sau báo push trễ bị 409. Từ xa giữ điều kiện mốc và ref đã công bố cũ | Có trong lượt hồi quy; assertion không `bao.bi`/`bao.xong`, xoá phiếu, từ chối push trễ vẫn giữ |
| `test_v5_sudo_khong_tuong_tac.py::test_lenh_trang_thai_khong_nhan_mat_khau[0]` | Task 4 kiểm JSON `loggedIn is True`; fixture cũ chỉ trả chuỗi `GIA_LAP_KHONG_DUOC_IN`, nên đỏ đúng theo hợp đồng mới | Fixture trả JSON `loggedIn:true`, vẫn có dấu dữ liệu không được lọt trong email/stderr. Không sửa mã auth hoặc assertion | Cả file và test auth âm ở `test_doi_ngu_nen.py` xanh trong nhóm 55 |

`NguCanhTho.ch` là trường bắt buộc; `CauHinhTho.tren_may_b` là property suy từ URL,
không phải cờ mới cần có trong YAML. Máy từ xa/cấu hình cũ nạp bằng đối tượng thật vẫn có property.
Vì vậy không thêm `getattr(..., False)` vào mã sản phẩm để che fixture sai hình dạng.

## Phân biệt thiếu môi trường và lỗi hệ thống

Trong `tram/tho/luot_b.py`, chỉ nhánh `LoiMoiTruongKiem` khi tạo nội dung cây mới được dọn
và trả lý do. CLI chưa chạy, khe chưa được cấp quyền, nên không cần chạy thu hồi lần nữa.
Lỗi OSError/quyền/Git, lỗi dependency hoặc dọn thất bại vẫn đi qua `LoiThuHoi`, giữ phiếu.
Đây là quyết định sửa của người điều phối trong chat, thắng cách bắt lỗi gộp của Task 6.

Tìm thêm một đường phân loại sai có liên quan: `loai_khoi_git` biến mã lỗi `git ls-files`
khác 0/1 thành `LoiMoiTruongKiem`. Nếu giữ nguyên, lỗi Git sẽ bị nhánh mới hiểu nhầm là thiếu môi trường.
Sửa đúng một dòng để ném `subprocess.CalledProcessError` với tên lệnh cố định, không mang đầu ra/đường dẫn.
Nhánh B giữ phiếu bằng `LoiThuHoi`; nhánh từ xa vốn bắt SubprocessError nên vẫn trả lý do cũ.
File môi trường đã tracked vẫn ném `LoiMoiTruongKiem` như trước.

Tám ca mới trong `tests/test_doi_ngu_vong_doi.py`:

- Thiếu file hoặc thiếu cấu hình: gửi `bao.bi`, xoá phiếu/cây/đăng ký worktree, không ACL mở cổng,
  không trao quyền cây, không gọi CLI; principal giả có `user` để không bỏ qua nhánh cấp quyền.
- OSError, PermissionError, Git CalledProcessError: giữ phiếu/cây, cổng 0700, chưa sẵn sàng.
- Thiếu môi trường nhưng dọn lỗi: giữ phiếu, cổng đóng, ném `LoiThuHoi`.
- Git `ls-files` trả 128: B ném `LoiThuHoi`, từ xa trả lý do cũ.

## Assertion đổi và căn cứ đã chốt

Nguồn: [QĐ3-A](QUYET-DINH.md), [spec đội ngũ](specs/doi-ngu-tho/spec.md), [design §4](design.md).

1. **Số `giao.cong_bo`: B 2→1; số `bao.moc`: B 1→0.**
   Requirement **“Khe sửa mã mà không ghi kho Git chung”**, scenario **“Mốc tạm hoặc báo cáo giả SHA”**:
   > B không tin SHA do khe gửi; mốc chỉ lưu tiến độ trong lượt.
   > Không hứa mốc tạm đã được công bố.

   Design §4 nói rõ:
   > Mốc tạm giữ trong sổ phiếu, chưa công bố.

   Scenario **“Hoàn tất một việc”** đặt chốt SHA/công bố sau thu hồi.
   B vẫn kiểm cùng SHA ở công bố và báo xong, lệnh kiểm pass, đúng lượt và dọn phiếu.
   Nhánh từ xa vẫn kiểm **2 công bố, 1 mốc** như assertion cũ.

2. **Prompt lần hai: B đọc trước dọn rồi xác nhận cây mất.**
   Giữ nguyên kỳ vọng nội dung `## Lần chạy 2`, đọc file stdin do CLI giả ghi, không dựng nội dung thay thế.
   Design §4 **C1**:
   > Kết thúc đóng cổng bằng `chmod -N`
   > xoá cây và registration Git của đúng lượt.

   Requirement trên, scenario **“Đổi lượt code sang QC hoặc đổi khe”** yêu cầu cây riêng và dọn khi kết thúc.
   Không còn dùng sự tồn tại của cây sau xong để nghiệm thu B. Từ xa vẫn đọc nguyên đường dẫn cũ sau xong.

3. **Thu hồi: B chờ mốc trong sổ; ref công bố trước/sau push trễ đều rỗng.**
   Cùng scenario **“Mốc tạm hoặc báo cáo giả SHA”** và design §4 đã trích ở mục 1:
   B không có mốc công bố để làm tín hiệu thu hồi hoặc tạo ref trong lượt này.
   Đợi `vi_tri_hang_doi >= 1` chứng minh quản lý đã đọc mốc thật trước thu hồi.
   Giữ nguyên kiểm dừng cứng không báo kết thúc, phiếu được xoá và push trễ trả 409.
   Dùng `for-each-ref` kiểm ref vắng trên B; từ xa vẫn đòi ref đã có và SHA không đổi.

Không đổi assertion nào khác. Các fixture thuộc nhóm 16 ca và ca sudo giữ toàn bộ assertion.
Fixture auth theo nguyên văn Task 4 của [plan](../../../docs/plans/2026-10-20-doi-ngu-tho.md):
`json.loads(kq.stdout).get("loggedIn") is True`; các fixture auth khác trong plan đã được đổi sang JSON thật.

## Bằng chứng test

Mọi lệnh dùng tiền tố:

```bash
PYTHONPATH="$PWD" \
UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv' \
UV_NO_SYNC=1 UV_CACHE_DIR=/private/tmp/codex-doi-ngu-20261020/uv-cache \
tests/chan_host/chay.sh -q <files> tests/test_do_dai_ma.py
```

Log trong `/private/tmp/codex-doi-ngu-20261020/`:

| Lượt | Kết quả thực đo | Log |
|---|---|---|
| Baseline phạm vi lỗi, trước sửa | 25 failed, 14 passed; gồm 21 lỗi QC và 4 ca CLI khác đỏ trong sandbox; 0 dòng chặn mới | `sua-1-baseline.log` |
| RED môi trường B | 2 failed, 4 passed, 12 deselected: hai ca thiếu file/cấu hình nhận `LoiThuHoi` thay vì báo `bi`; 0 dòng chặn mới | `sua-1-moi-truong-red.log` |
| GREEN fixture + môi trường B ban đầu | 52 passed; 0 dòng chặn mới | `sua-1-unit-green.log` |
| RED phân loại Git | 1 failed, 4 passed: B “DID NOT RAISE LoiThuHoi”; đối chứng từ xa xanh; 0 dòng chặn mới | `sua-1-git-red.log` |
| GREEN môi trường/Git và tương thích cũ | 22 passed; 0 dòng chặn mới | `sua-1-moi-truong-green.log` |
| Trọng tâm cuối, gồm test tích hợp thiếu môi trường **không sửa** | 55 passed; 0 dòng chặn mới, 0 điểm mù, 36 push giả lập | `sua-1-focused-final.log` |
| Hồi quy rộng theo yêu cầu | 138 passed, 15 failed trong 433,54 giây; 0 dòng chặn mới, 18 điểm mù, 102 push giả lập | `sua-1-regression.log` |
| Đối chiếu thu thập sau thêm test Git | 155 tests collected; 0 dòng chặn mới | `sua-1-collection.log` |

RED môi trường dùng `-k 'thieu_moi_truong or loi_he_thong'`, nên bộ kiểm độ dài được chỉ định nhưng bị deselect;
các lượt GREEN không dùng bộ lọc này và chạy đủ bộ kiểm độ dài.

Lệnh hồi quy rộng (cùng tiền tố môi trường ở trên):

```bash
tests/chan_host/chay.sh -q \
  tests/test_theo_doi_dung.py tests/test_deploy_review_v2.py \
  tests/test_de_nghi_tho.py tests/test_phieu_chay_thu_hoi.py \
  tests/test_v5_sudo_khong_tuong_tac.py tests/test_doi_ngu*.py \
  tests/test_kich_ban_3a2.py tests/test_tho_*.py \
  tests/test_vong_import.py tests/test_do_dai_ma.py
```

Lượt rộng đã thu thập 153 ca trước khi thêm hai ca phân loại lỗi Git. Hai ca mới và mã sửa Git
được kiểm tiếp bằng lượt GREEN 22 và lượt trọng tâm cuối 55; không cộng các lượt chồng nhau thành tổng passed.
Trần dòng và vòng import xanh trong lượt rộng; `git diff --check` đạt sau toàn bộ thay đổi.

18/21 ca QC gốc đã xanh trực tiếp trong lượt trọng tâm cuối (16 fixture + môi trường + sudo).
Ba ca tích hợp còn lại đã sửa cách nghiệm thu B theo spec và có thêm nhánh từ xa; chưa có bằng chứng
xanh trọn ba ca này trong sandbox. Cần người điều phối chạy lại chúng trên máy B để xác nhận.

15 lỗi ở lượt rộng đều đi qua nhánh không xác nhận thu hồi CLI/lệnh kiểm, gồm:

- 10 biến thể của `test_kich_ban_3a2.py`: sáu biến thể B/từ xa của ba ca đã sửa cách nghiệm thu,
  cùng bốn ca dừng mềm/hạn mức/cần hỏi/restart. Log đều có câu “Không xác nhận thu hồi tiến trình của khe”.
- Hai ca chạy CLI ở `test_tho_chuan_bi.py`, một ca vòng máy ở `test_tho_lenh_chay.py`.
- Hai ca chạy lệnh kiểm sau xong ở `test_tho_theo_doi_ket_thuc.py`, ném `LoiThuHoi` từ `kiem/lenh_tho.py`.

Theo kết quả ngoài sandbox Đại ca đã cung cấp, không tính nhóm thu hồi này thành lỗi bản vá mới;
không sửa thu hồi/sysctl/bind, không tăng timeout hoặc bỏ assertion để làm xanh trong sandbox.
Số 138/15 là số đo runner thực tế, không phải kết luận có thêm 15 lỗi sản phẩm hoặc toàn nhóm đã xanh.

## Tự kiểm và phạm vi còn lại

- Mã sản phẩm chỉ đổi `tram/tho/luot_b.py` và `tram/tho/chuan_bi.py`, trong package `tho`.
- Không đổi schema, quyền khe, công tắc, cấu hình thật, route, Uq hoặc luồng GitHub.
- Không thêm dependency, import vòng hay cơ chế dự phòng cho cấu hình giả.
- Giữ giới hạn thời gian và cách che dữ liệu lỗi; trần 120 dòng của mã sản phẩm được kiểm bằng test.
- Ba ca tích hợp đổi kỳ vọng đều có thêm nhánh máy từ xa giữ hành vi cũ. Cần đọc số liệu hồi quy cuối
  cùng bằng chứng QC ngoài sandbox; không lấy lỗi thu hồi/sysctl/bind trong sandbox làm lỗi bản vá mới.
- Đây là tự kiểm của người sửa, không thay QC độc lập của người điều phối hoặc bằng chứng máy thật.
