"""Trạm tự mở PR (spec 4 §6.4 mục 4, §7.3; kiến trúc Q7) — lát 4c. Chỉ MỞ, không merge: merge là của Đại ca.

Bead ở cột 3: PR head `tram/<bead>` → base `<nhanh_chinh>`, chỉ ghi khi head của PR ĐÚNG `commit_ban_giao` của
`bead.vao_cot_3` mới nhất (sau `cot.tra_ve` gần nhất) và ref công bố hiện tại vẫn là commit đó. Sự kiện
`pr.mo` (ID thao tác theo dự án + bead + commit) rồi "điền pr": thêm vào notes một khối `<!-- ban-giao -->` là
bàn giao cũ với `pr` = URL của trạm (dashboard đọc khối CUỐI) + dấu `<!-- pr: <ma> -->` để đối soát.
Spec đã duyệt (4b): PR `tram/spec-<feature>` tại commit trong `spec.duyet` mới nhất, khi chưa vào nhánh chính."""
import hashlib
from datetime import datetime
from pathlib import Path

from tram.ban_giao.schema import doc_khoi_ban_giao
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.gh import GhCli, LoiGh, PrInfo
from tram.giao_viec.git_kiem import la_to_tien, sha_cua
from tram.giao_viec.pr_bang_chung import bang_chung_hien_hanh
from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, ref_cong_bo
from tram.phieu.kho import KhoPhieu

NHAN_REVIEW, NHAN_THEO_PLAN = "cot:cho-review", "theo-plan"


def ma_pr(du_an: str, bead_id: str, commit: str) -> str:
    return "pr-" + hashlib.sha256(f"{du_an}:{bead_id}:{commit}".encode()).hexdigest()[:20]


def _pr_mo(gh: GhCli, repo: str, nhanh: str, base: str) -> list[PrInfo]:
    return [p for p in gh.ds_pr(repo, nhanh)
            if p.trang_thai in ("OPEN", "MERGED") and p.nhanh == nhanh and p.base == base and not p.ngoai_repo]


def dam_bao_pr(gh: GhCli, repo: str, nhanh: str, base: str, commit: str, tieu_de: str, than: str, *,
               cho_tao: bool = True) -> PrInfo | None:
    """PR mở duy nhất của `nhanh` → `base`; chưa có thì tạo rồi ĐỌC LẠI (kết quả tạo không rõ vẫn đối soát được).
    Trả None khi head chưa đúng `commit` — không ghi gì, vòng sau thử lại."""
    mo = _pr_mo(gh, repo, nhanh, base)
    if not mo and not cho_tao:
        return None
    if not mo:
        try:
            gh.tao_pr(repo, nhanh, base, tieu_de, than)
        except LoiGh:
            pass
        mo = _pr_mo(gh, repo, nhanh, base)
    return mo[0] if len(mo) == 1 and mo[0].head == commit else None


def _than(bead_id: str, d: dict, loai: str) -> str:
    dong = [f"PR do Trạm điều phối mở cho {loai} `{bead_id}`. Chỉ Đại ca merge (Q7).", ""]
    dong += [f"- {k}: `{d[k]}`" for k in ("commit_ban_giao", "commit_code", "digest_tieu_chi", "commit") if k in d]
    dong += ["- cờ đỏ: CÓ — xem kỹ vùng nhạy cảm" if d.get("co_do") else "- cờ đỏ: không"] if loai == "bead" else []
    return "\n".join(dong + ["", "Trạm chỉ tự đóng bead khi xác minh PR đã merge đúng commit trên."])


def _ghi(kho: KhoPhieu, du_an: str, bead_id: str, loai: str, pr: PrInfo, commit: str, luc: datetime) -> dict:
    d = {"bead_id": bead_id, "loai": loai, "pr": pr.so, "url": pr.url, "nhanh": pr.nhanh, "commit": commit,
         "ma_thao_tac": ma_pr(du_an, bead_id, commit)}
    ghi_mot_lan(kho, du_an, "pr.mo", d, bead_id=bead_id, luc=luc, khoa=("ma_thao_tac",))
    return d


def dien_pr(bd, b: Bead, d: dict) -> None:
    dau = f"<!-- pr: {d['ma_thao_tac']} -->"
    if dau in (b.notes or ""):
        return
    bg = doc_khoi_ban_giao(b.notes or "")
    khoi = (f"<!-- ban-giao -->\n{bg.model_copy(update={'pr': d['url']}).model_dump_json()}\n<!-- ban-giao -->\n"
            if bg is not None else "")
    bd.cap_nhat_nhan(b.id, ghi_chu=f"{khoi}{dau}\nPR #{d['pr']}: {d['url']}")


def mo_pr_bead(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
               luc: datetime) -> str | None:
    w = cua_so(ds)
    v = bang_chung_hien_hanh(b, ds)
    if v is None:
        return None
    c = v.du_lieu["commit_ban_giao"]
    if (mo := moi_nhat(w, "pr.mo", lambda s: s.du_lieu["commit"] == c)) is not None:
        dien_pr(bd, b, mo.du_lieu)
        return None
    cho_tao = sha_cua(kg, f"origin/tram/{b.id}") == c
    tieu_de = f"{b.id}: {' '.join(b.title.split())}"[:200]
    pr = dam_bao_pr(gh, repo, f"tram/{b.id}", da.nhanh_chinh, c, tieu_de, _than(b.id, v.du_lieu, "bead"),
                     cho_tao=cho_tao)
    if pr is None:
        return "pr_cho"
    dien_pr(bd, b, _ghi(kho, da.ten, b.id, "bead", pr, c, luc))
    return "pr_mo"


def mo_pr_spec(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, b: Bead, ds: list[SK],
               luc: datetime) -> str | None:
    dy = moi_nhat(ds, "spec.duyet")
    if dy is None or b.status == "closed" or NHAN_THEO_PLAN not in b.labels:
        return None
    c = dy.du_lieu["commit"]
    if (moi_nhat(ds, "pr.mo", lambda s: s.du_lieu["commit"] == c) is not None or ref_cong_bo(ds) != c
            or la_to_tien(kg, c, f"origin/{da.nhanh_chinh}")):
        return None
    tieu_de = f"Spec {b.id}: {' '.join(b.title.split())}"[:200]
    if sha_cua(kg, f"origin/tram/spec-{b.id}") != c:
        return "pr_cho"
    pr = dam_bao_pr(gh, repo, f"tram/spec-{b.id}", da.nhanh_chinh, c, tieu_de, _than(b.id, dy.du_lieu, "spec"))
    if pr is None:
        return "pr_cho"
    _ghi(kho, da.ten, b.id, "spec", pr, c, luc)
    return "pr_mo"
