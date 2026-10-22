import json
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from tram.beads.doc_ds import doc_ds, doc_ds_yeu_cau
from tram.beads.loi import KhongThayBead, LoiBd
from tram.beads.mo_hinh import Bead

Runner = Callable[[Sequence[str]], str]


def chay_bd(args: Sequence[str]) -> str:
    try:
        kq = subprocess.run(["bd", *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise LoiBd(f"Không chạy được bd: {e}") from e
    if kq.returncode != 0:
        raise LoiBd(f"bd {' '.join(args[:4])} lỗi {kq.returncode}: {kq.stderr.strip()[:500]}")
    return kq.stdout


class Bd:
    def __init__(self, repo: Path, *, actor: str = "tram/cham-cot", runner: Runner | None = None):
        self.repo = repo
        self.actor = actor
        self._runner = runner or chay_bd

    def _chay(self, *args: str) -> str:
        return self._runner(["-C", str(self.repo), *args])

    def tat_ca(self) -> list[Bead]:
        return doc_ds(self._chay("list", "--json", "--all", "--limit", "0"))

    def tat_ca_yeu_cau(self) -> list[Bead]:
        """Đối soát trước create: schema lạ không đồng nghĩa danh sách rỗng."""
        return doc_ds_yeu_cau(self._chay("list", "--json", "--all", "--limit", "0"))

    def phien_ban(self, bead_id: str) -> str:
        """`updated_at` hiện tại của một bead — version để kiểm lại trước khi ghi (spec §5.6).
        Chỉ đọc `updated_at`: dạng các trường khác của `bd show` chưa được spike."""
        ra = self._chay("show", bead_id, "--json")
        try:
            d = json.loads(ra)
            d = d[0] if isinstance(d, list) else d  # bd 1.2.2 trả mảng một phần tử
            if d["id"] != bead_id:
                raise ValueError(f"trả về bead {d['id']!r}")
            return str(d["updated_at"])
        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise LoiBd(f"bd show {bead_id}: kết quả không dùng được ({type(e).__name__}: {e})") from e

    def cap_nhat_nhan(self, bead_id: str, *, them: Sequence[str] = (), bo: Sequence[str] = (),
                      ghi_chu: str | None = None) -> None:
        if not (them or bo or ghi_chu):
            return
        args = ["update", bead_id, "--actor", self.actor]
        for n in them:
            args += ["--add-label", n]
        for n in bo:
            args += ["--remove-label", n]
        if ghi_chu:
            args += ["--append-notes", ghi_chu]
        self._chay(*args)

    def mot(self, bead_id: str) -> Bead:
        """Đọc một bead qua `bd list` — dạng JSON đã spike; chưa dựng Bead từ `bd show` (plan 1a G3)."""
        for b in self.tat_ca():
            if b.id == bead_id:
                return b
        raise KhongThayBead(f"Không thấy bead {bead_id}")

    def tao(self, tieu_de: str, *, loai: str, mo_ta: str, nhan: Sequence[str] = (), uu_tien: int | None = None,
            nghiem_thu: str | None = None, cha: str | None = None) -> str:
        """`bd create` (spike bd). `uu_tien`, `nghiem_thu`, `cha` cho bead con tạo từ plan (spec 4 §7.3)."""
        args = ["create", tieu_de, "-t", loai, "-d", mo_ta, "--silent", "--actor", self.actor]
        if nhan:
            args += ["-l", ",".join(nhan)]
        if uu_tien is not None:
            args += ["-p", str(uu_tien)]
        if nghiem_thu:
            args += ["--acceptance", nghiem_thu]
        if cha:
            args += ["--parent", cha]
        ra = self._chay(*args).strip()
        if len(ra.split()) != 1:
            raise LoiBd(f"bd create không trả về một mã bead: {ra[:100]!r}")
        return ra

    def san_sang(self) -> set[str]:
        """`bd ready --json --limit 0` (spike bd): id các bead `open` không bị chặn — KHÔNG gồm `in_progress`."""
        ra = self._chay("ready", "--json", "--limit", "0")
        try:
            return {str(d["id"]) for d in json.loads(ra)}
        except (ValueError, KeyError, TypeError) as e:
            raise LoiBd(f"bd ready: JSON không đọc được ({type(e).__name__}: {e})") from e

    def nhan_viec(self, bead_id: str) -> None:
        """`bd update <id> --claim` (spike bd): nguyên tử, đã có người nhận → LoiBd. Người gọi đối soát trước
        (bead đã `in_progress` với assignee = actor thì không gọi lại — spec 4 §5.4)."""
        self._chay("update", bead_id, "--claim", "--actor", self.actor)

    def dong(self, bead_id: str, ly_do: str) -> None:
        self._chay("close", bead_id, "--reason", ly_do, "--actor", self.actor)

    def them_phu_thuoc(self, bead_id: str, phu_thuoc_vao: str) -> None:
        """`bd dep add A B`: A phụ thuộc B (B chặn A). Lặp cặp cũ vẫn 'Added' — người gọi tự kiểm trùng."""
        self._chay("dep", "add", bead_id, phu_thuoc_vao, "--actor", self.actor)
