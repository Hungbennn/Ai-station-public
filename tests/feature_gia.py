"""`*.beads.json` mẫu cho test luồng feature (CHỈ DÙNG TRONG TEST)."""
import json

SPEC = "docs/specs/2026-10-14-hoa-hong-tam-tinh.md"
PLAN = "docs/plans/2026-10-14-hoa-hong-tam-tinh.md"


def bead_de_xuat(khoa: str, **sua) -> dict:
    return {"khoa": khoa, "tieu_de": f"Việc {khoa}", "loai": "task", "uu_tien": 2,
            "mo_ta": f"Làm Task {khoa} của plan", "nghiem_thu": f"- Tiêu chí của {khoa}", "phu_thuoc": [], "nhan": [],
            **sua}


def ke_hoach(feature: str = "hr-f", **sua) -> dict:
    return {"phien_ban": 1, "feature": feature, "spec_file": SPEC, "plan_file": PLAN,
            "bead": [bead_de_xuat("t1", nhan=["b2b"]), bead_de_xuat("t2", phu_thuoc=["t1"], uu_tien=1)], **sua}


def ke_hoach_json(feature: str = "hr-f", **sua) -> str:
    return json.dumps(ke_hoach(feature, **sua), ensure_ascii=False, indent=1)
