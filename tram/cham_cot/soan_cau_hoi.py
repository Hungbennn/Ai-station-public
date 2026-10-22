"""LLM chế độ rút gọn (spec 0+1a §5.2 bước 4): bead đã bị luật cứng xếp cột 2 — chỉ soạn câu hỏi, không chấm.

Prompt ngắn: vai `soan-cau-hoi` + bối cảnh dự án + chỗ chạm + bead; không bài học, không checklist.
Không bao giờ ném lỗi LLM/vai: lỗi → câu hỏi dự phòng (`cau_hoi.cau_hoi_du_phong`).
"""
import anthropic

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot import prompt
from tram.cham_cot.cau_hoi import DAU_RA_CAU_HOI, cau_hoi_du_phong
from tram.cham_cot.luat_cung import KetQuaLuat
from tram.llm.claude import KetQuaGoi, LoiChamLLM, cham_bang_llm

VAI_SOAN = "soan-cau-hoi"
# Lỗi gọi LLM (refusal, hết lượt guardrail, API/mạng) và lỗi nạp vai (thiếu file, sai frontmatter).
LOI_SOAN = (LoiChamLLM, anthropic.APIError, OSError, ValueError, StopIteration)


def noi_dung_soan(bead: Bead, luat: KetQuaLuat) -> str:
    cho = "\n".join(f"- {c}" for c in luat.cham)
    du_lieu = (f"ID: {bead.id}\nLoại: {bead.issue_type}\nTiêu đề: {bead.title}\nMô tả:\n{bead.description}\n"
               f"Tiêu chí nghiệm thu:\n{bead.acceptance_criteria or '(trống)'}\n"
               f"Thiết kế:\n{bead.design or '(trống)'}")
    return (f"## Luật cứng đã xếp bead này vào cột can-chot\n{luat.ly_do()}\nChỗ chạm:\n{cho}\n\n"
            + prompt.boc_khong_tin_cay(du_lieu))


def soan_cau_hoi(bead: Bead, luat: KetQuaLuat, *, du_an: DuAn, client,
                 vai_soan: tuple[str, str] | None = None) -> tuple[list[str], dict, KetQuaGoi | None]:
    """Trả (câu hỏi, dữ liệu thêm cho sự kiện, lần gọi — None khi đã lùi về câu hỏi dự phòng)."""
    du_lieu: dict = {"che_do": "soan_cau_hoi", "phien_ban_vai_soan": vai_soan[0] if vai_soan else None}
    try:
        phien_ban, than = vai_soan or prompt.nap_vai(VAI_SOAN)
        du_lieu["phien_ban_vai_soan"] = phien_ban
        goi = cham_bang_llm(client, prompt.he_thong(than, du_an), noi_dung_soan(bead, luat), DAU_RA_CAU_HOI)
    except LOI_SOAN as e:
        du_lieu.update(nguon_cau_hoi="du_phong", llm_loi=f"{type(e).__name__}: {str(e)[:500]}")
        return cau_hoi_du_phong(luat, bead.title), du_lieu, None
    du_lieu.update(nguon_cau_hoi="llm", so_lan=goi.so_lan, token_cache_doc=goi.token_cache_doc)
    return [q.strip() for q in goi.ket_qua.cau_hoi_can_chot], du_lieu, goi
