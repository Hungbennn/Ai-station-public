"""Khoá chung trước mọi thao tác tự động (design D-2 năm dòng đầu, D-9, D97; INV-004, INV-005) — hàm thuần.

TM-2 (tự merge) và TM-3 (tự deploy, nút Deploy) đọc `doc_trang_thai` + `estop.dang_bat()` + `bat_ghi` NGAY TRƯỚC
lệnh rồi gọi hàm này; danh sách rỗng mới được làm. Thứ tự lý do cố định: estop → tạm dừng toàn trạm → tạm dừng dự
án → `bat_ghi` → công tắc → đủ 3 lệnh. Mã lý do là hợp đồng với dashboard (nhãn ở `NHAN_LY_DO`)."""
from tram.tu_dong.luu import TrangThaiTuDong

VIEC = ("merge", "deploy", "deploy_tay")
NHAN_LY_DO = {"estop": "Estop đang bật", "tam_dung_tram": "Tự merge · tự deploy đang tạm dừng toàn trạm",
              "tam_dung_du_an": "Dự án đang tạm dừng", "bat_ghi": "Dự án chỉ quét thử (bat_ghi: false)",
              "tu_merge_tat": "Công tắc tự merge tắt", "tu_deploy_tat": "Tự deploy tắt",
              "thieu_lenh": "Chưa khai đủ 3 lệnh"}


def ly_do_chan(tt: TrangThaiTuDong, *, viec: str, bat_ghi: bool, estop_bat: bool) -> list[str]:
    """`merge`: tự merge (cả PR spec D95). `deploy`: tự deploy sau tự merge. `deploy_tay`: nút Deploy của Đại ca —
    không xét tạm dừng, công tắc (D97), vẫn khoá khi estop, `bat_ghi: false`, thiếu lệnh (D73)."""
    if viec not in VIEC:
        raise ValueError(f"việc không hợp lệ: {viec!r}")
    tu_dong, cd = viec != "deploy_tay", tt.cai_dat
    co = (("estop", estop_bat),
          ("tam_dung_tram", tu_dong and tt.tam_dung_tram is not None),
          ("tam_dung_du_an", tu_dong and tt.tam_dung_du_an is not None),
          ("bat_ghi", not bat_ghi),
          ("tu_merge_tat", viec == "merge" and not cd.tu_merge),
          ("tu_deploy_tat", viec == "deploy" and not cd.tu_deploy),
          ("thieu_lenh", viec != "merge" and not cd.du_lenh))
    return [ma for ma, chan in co if chan]
