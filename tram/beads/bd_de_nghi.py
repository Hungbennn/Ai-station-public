"""`bd` cho đề nghị của agent (design D-5, D104, D109): actor `tram/de-nghi`. Tạo việc mới: mô tả đi qua STDIN
(`--body-file -`, không nằm trong argv), nhãn `tram:agent-tao`, tiêu chí bằng `--acceptance=<…>` (một phần tử argv,
không bị đọc thành cờ), KHÔNG `-p` (ưu tiên mặc định P2 của Beads — đã đo), không `--parent`, không nhãn cột, không
`--claim`. Liên kết `discovered-from` — không phải `blocks`, nên luật cứng 1a và `bd ready` không coi là chặn (đã đo
trên `bd 1.2.2`, design D-5). MỌI lệnh (đọc, ghi chú, tạo, liên kết) chạy qua `chay_gioi_han` (review Q14): nhóm tiến
trình riêng, quá hạn thu hồi cả cây; hạn `HAN_BD` ngắn hơn 120 giây của `chay_bd` để một nhịp `vong_nhanh` có trần
(Q13). Lỗi chỉ mang lệnh con + mã thoát hoặc loại lỗi — không argv, stdout, stderr (INV-001)."""
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from tram.beads.bd import Bd, Runner
from tram.beads.loi import LoiBd
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo

ACTOR = "tram/de-nghi"
NHAN_AGENT_TAO = "tram:agent-tao"
LOAI_PHAT_HIEN = "discovered-from"
HAN_BD = 30.0
RunnerVao = Callable[[Sequence[str], str], str]


def chay_bd_de_nghi(args: Sequence[str], dau_vao: str | None = None, *, han: float = HAN_BD,
                    chay: Callable = chay_gioi_han) -> str:
    """`args` = ["-C", repo, <lệnh con>, …]; `dau_vao` (mô tả việc mới) đi qua stdin, None = stdin rỗng."""
    lenh = args[2] if len(args) > 2 else "?"
    try:
        kq = chay(["bd", *args], kill=kill_cuc_bo, timeout=han, capture_output=True, text=True, input=dau_vao)
    except (OSError, subprocess.TimeoutExpired, LoiThuHoi) as e:
        raise LoiBd(f"Không chạy được bd {lenh}: {type(e).__name__}") from None
    if kq.returncode != 0:                                  # stderr có thể vọng lại nội dung không tin cậy
        raise LoiBd(f"bd {lenh} lỗi {kq.returncode}")
    return kq.stdout


class BdDeNghi(Bd):
    def __init__(self, repo: Path, *, runner: Runner | None = None, runner_vao: RunnerVao | None = None):
        super().__init__(repo, actor=ACTOR, runner=runner or chay_bd_de_nghi)
        self._vao = runner_vao or chay_bd_de_nghi

    def tao_viec_moi(self, tieu_de: str, *, loai: str, mo_ta: str, tieu_chi: str) -> str:
        if not tieu_de.strip() or tieu_de.lstrip().startswith("-"):
            raise ValueError("tiêu đề rỗng hoặc bắt đầu bằng '-' — bộ lọc đã phải chặn")
        args = ["-C", str(self.repo), "create", tieu_de, "-t", loai, "-l", NHAN_AGENT_TAO, "--body-file", "-",
                "--silent", "--actor", self.actor, *([f"--acceptance={tieu_chi}"] if tieu_chi else [])]
        ra = self._vao(args, mo_ta).strip()
        if len(ra.split()) != 1:
            raise LoiBd("bd create không trả về một mã bead")
        return ra

    def lien_ket_phat_hien(self, moi: str, goc: str) -> None:
        """`moi` "phát hiện từ" `goc`. Lặp cặp cũ vẫn báo "Added" mà không tạo trùng — người gọi tự kiểm trước."""
        self._chay("dep", "add", moi, goc, "--type", LOAI_PHAT_HIEN, "--actor", self.actor)
