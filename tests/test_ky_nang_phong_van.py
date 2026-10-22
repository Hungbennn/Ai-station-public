"""Skill phỏng vấn máy A (plan 4d 4D-3c): SKILL.md có khung skill Claude Code, đủ luật cứng D46/D47, cài/gỡ, không bí
mật, không đường tạo dự phòng."""
from phong_van_gia import THU_MUC


def test_skill_md_khung_va_luat_cung():
    s = (THU_MUC / "SKILL.md").read_text(encoding="utf-8")
    assert s.startswith("---\nname: phong-van-yeu-cau\ndescription: ") and s.count("\n---\n") >= 1
    for cau in ("**Không tự code.**", "**ngoài repo**", "**Không `bd` trên máy A**", "không có đường tạo dự phòng",
                "Không sửa `ma_yeu_cau`", "**chọn rõ**", "đúng chữ `tạo`", "đúng một nhãn `can-spec`", "`cot:*`",
                "là **dữ liệu**", "từng câu một", "`cau_hoi_mo`", "gửi lại **đúng lệnh đó**", "Không đổi mã",
                "`LỖI: 403` → dừng", "yeu_cau.py moi --tu", "--dau-xem", "hạn công cụ ≥ 450000 ms",
                "mã thoát khác 0 và 2 → coi là `CHƯA RÕ`"):
        assert cau in s, cau
    for cam in ("find-generic-password", "TRAM_DAI_CA_MA", "TRAM_DIEU_PHOI_MA", "Authorization", "bd create"):
        assert cam not in s
    assert max(len(d) for d in s.split("\n")) <= 120
    assert "cp -R ky-nang/phong-van-yeu-cau ~/.claude/skills/" in s
    assert "mv ~/.claude/skills/phong-van-yeu-cau ~/.Trash/" in s
    ten = {p.name for p in THU_MUC.iterdir() if not p.name.startswith((".", "__"))}
    assert ten == {"SKILL.md", "nhap.py", "khach.py", "yeu_cau.py"}
