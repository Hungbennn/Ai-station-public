"""GitHub giả trong bộ nhớ cho test lát 4c (CHỈ DÙNG TRONG TEST): cùng giao diện `GhCli` — không gọi `gh`, không
mạng. Head của PR mới lấy từ remote Git cục bộ (`head_cua(nhanh)`), như GitHub đọc nhánh trên remote.
TM-2: `merge_pr` như `gh pr merge --merge --match-head-commit` (PR không mở hay đầu PR khác commit → lỗi);
`lam_merge(pr)` làm merge thật trên remote cục bộ và trả merge commit; `khi_xem(so)` chạy mỗi lần đọc PR (giả
Đại ca bấm gì đó trong lúc lệnh `gh` đang chạy)."""
from dataclasses import replace

from tram.giao_viec.gh import LoiGh, PrInfo

REPO = "dai-ca/hr-codex"


class GhGia:
    def __init__(self, head_cua, *, mat_phan_hoi_khi_tao=False, loi=False, lam_merge=None, loi_merge=False,
                 mat_phan_hoi_khi_merge=False, khi_xem=None):
        self.head_cua, self.mat, self.loi = head_cua, mat_phan_hoi_khi_tao, loi
        self.lam_merge, self.loi_merge, self.mat_merge, self.khi_xem = (lam_merge, loi_merge, mat_phan_hoi_khi_merge,
                                                                        khi_xem)
        self.prs: dict[int, PrInfo] = {}
        self.goi: list[tuple] = []

    def _kiem(self, ten, *args):
        self.goi.append((ten, *args))
        if self.loi:
            raise LoiGh("gh giả lỗi")

    def ds_pr(self, repo, nhanh):
        self._kiem("ds_pr", repo, nhanh)
        return [p for p in self.prs.values() if p.nhanh == nhanh]

    def xem_pr(self, repo, so):
        self._kiem("xem_pr", repo, so)
        if self.khi_xem is not None:
            self.khi_xem(so)
        return self.prs[so]

    def cong_merge(self, repo, pr):
        return pr.ci or "xanh"

    def merge_pr(self, repo, so, commit):
        self._kiem("merge_pr", repo, so, commit)
        p = self.prs[so]
        if self.loi_merge or p.trang_thai != "OPEN" or p.head != commit:
            raise LoiGh("gh giả: merge bị từ chối")
        self.prs[so] = replace(p, trang_thai="MERGED", merge_commit=self.lam_merge(p) if self.lam_merge else None)
        if self.mat_merge:
            raise LoiGh("mất phản hồi sau khi GitHub đã merge")

    def tao_pr(self, repo, nhanh, base, tieu_de, than):
        self._kiem("tao_pr", repo, nhanh, base, tieu_de, than)
        so = len(self.prs) + 1
        self.prs[so] = PrInfo(so, f"https://github.com/{repo}/pull/{so}", "OPEN", nhanh, self.head_cua(nhanh), base,
                              False, None)
        if self.mat:
            raise LoiGh("mất phản hồi sau khi GitHub đã tạo PR")

    def dat(self, pr_so, **kw):
        """Đổi trạng thái PR như Đại ca thao tác trên GitHub (merge, đóng, đẩy nhánh)."""
        self.prs[pr_so] = replace(self.prs[pr_so], **kw)
