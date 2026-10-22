from dataclasses import dataclass

UU_TIEN_COT = ("cot:cho-review", "cot:can-chot", "cot:ai-lam")


@dataclass(frozen=True)
class PhuThuoc:
    depends_on_id: str
    loai: str


def _so_nguyen(x) -> int | None:
    return x if isinstance(x, int) and not isinstance(x, bool) else None


@dataclass(frozen=True)
class Bead:
    id: str
    title: str
    description: str
    acceptance_criteria: str
    design: str
    notes: str
    status: str
    issue_type: str
    labels: tuple[str, ...]
    phu_thuoc: tuple[PhuThuoc, ...]
    updated_at: str
    # Lát 2a (spec phần 2 §12.2): bd bỏ trường rỗng khỏi JSON → mặc định khi thiếu.
    priority: int | None = None
    parent: str = ""
    assignee: str = ""
    created_at: str = ""
    close_reason: str = ""
    closed_at: str = ""

    @classmethod
    def tu_json(cls, d: dict) -> "Bead":
        return cls(
            id=d["id"],
            title=d.get("title") or "",
            description=d.get("description") or "",
            acceptance_criteria=d.get("acceptance_criteria") or "",
            design=d.get("design") or "",
            notes=d.get("notes") or "",
            status=d.get("status") or "",
            issue_type=d.get("issue_type") or "",
            labels=tuple(d.get("labels") or ()),
            phu_thuoc=tuple(
                PhuThuoc(x["depends_on_id"], x.get("type") or "")
                for x in d.get("dependencies") or ()
            ),
            updated_at=d["updated_at"],
            priority=_so_nguyen(d.get("priority")),
            parent=d.get("parent") or "",
            assignee=d.get("assignee") or "",
            created_at=d.get("created_at") or "",
            close_reason=d.get("close_reason") or "",
            closed_at=d.get("closed_at") or "",
        )

    def nhan_cot(self) -> str | None:
        """Nhãn cột; lỡ có nhiều thì chọn cột an toàn hơn (bd trả nhãn a→z)."""
        cot = [n for n in self.labels if n.startswith("cot:")]
        return next((n for n in UU_TIEN_COT if n in cot), cot[0] if cot else None)

    def van_ban(self) -> str:
        return "\n".join(
            p for p in (self.title, self.description, self.acceptance_criteria, self.design) if p
        )
