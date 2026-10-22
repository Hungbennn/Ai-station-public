"""gitnexus giả cho test lát 4c (CHỈ DÙNG TRONG TEST): cùng giao diện `GitnexusCli` — không chạy gitnexus, không
index. Ghi lại worktree/base nhận được và kiểm worktree thật sự đang ở commit cần xét lúc được gọi."""
import subprocess

from tram.giao_viec.gitnexus import LoiGitnexus, ThayDoi


class GnGia:
    def __init__(self, tep=(), *, khong_chac=False, loi=False, luong=()):
        self.tep, self.khong_chac, self.loi, self._luong = frozenset(tep), khong_chac, loi, list(luong)
        self.goi: list[tuple] = []

    def thay_doi(self, worktree, base, repo):
        head = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
        self.goi.append((worktree, base, repo, head))
        if self.loi:
            raise LoiGitnexus("gitnexus giả lỗi")
        return ThayDoi(self.tep, self.khong_chac)

    def luong(self, truy_van, repo):
        self.goi.append(("luong", truy_van, repo))
        return self._luong
