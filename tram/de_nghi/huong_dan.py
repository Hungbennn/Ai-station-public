"""Hướng dẫn gửi đề nghị trong lớp 2 của gói ngữ cảnh (design D-8; tasks 3.3) — CHỈ cho loại đang bật lúc dựng phiếu
(nút dự án + nút con; dự án `bat_ghi: false` không bao giờ được giao việc). Phiếu `spec` không có (D103: không đề nghị
việc mới). Đây chỉ là hướng dẫn: quyết định thật ở lúc nhận và lúc ghi. Không đổi quyền vai (`bd` vẫn bị cấm)."""
from tram.de_nghi.cai_dat import CaiDatTuCapNhat

TIEN_DO = ('- Tiến độ: `tram bao --tien-do "<đã làm gì, đang làm gì>"` — tối đa 20 dòng mỗi phiếu, mỗi dòng ≤ 1.000 ký'
           " tự; trạm thêm vào ghi chú của chính việc này.")
VIEC_MOI = ('- Việc mới phát hiện ra: `tram bao --viec-moi --tieu-de "<một dòng, ≤ 200 ký tự>" --mo-ta "<≤ 4.000>"'
            ' --loai bug|task|chore [--tieu-chi "<≤ 2.000>"]` — tối đa 5 mỗi phiếu; chỉ được tạo khi lượt này đạt kiểm'
            " lại và QC; không chọn được ưu tiên, nhãn hay việc cha.")
BI_CHAN = ('- Bị chặn: vẫn `tram bao --bi "<lý do>"` hoặc `--can-hoi` như trên; trạm ghi thêm dòng "bị chặn" vào'
           " việc này.")
CHUNG = ("- Không gọi `bd`; không đóng việc, không sửa việc khác; không ghi bí mật, `<!--`, `-->` hay ký tự điều khiển"
         " — đề nghị như vậy bị từ chối.")


def huong_dan(cd: CaiDatTuCapNhat, *, buoc: str) -> str:
    if buoc not in ("code", "qc"):
        return ""
    dong = [d for loai, d in (("tien_do", TIEN_DO), ("viec_moi", VIEC_MOI), ("bi_chan", BI_CHAN)) if cd.cho_ghi(loai)]
    return "### Tự cập nhật việc (trạm ghi Beads thay bạn)\n" + "\n".join([*dong, CHUNG]) if dong else ""
