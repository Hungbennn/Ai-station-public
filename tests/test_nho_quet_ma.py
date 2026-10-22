"""M7b: chỉ mã trong tram/nho/ được import lancedb (spec 1b §2)."""
import ast
from pathlib import Path

import tram

GOC = Path(tram.__file__).parent


def _import_lancedb(p: Path) -> bool:
    for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "lancedb" for a in n.names):
            return True
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "lancedb":
            return True
    return False


def test_chi_tram_nho_import_lancedb():
    ngoai = [p.relative_to(GOC) for p in GOC.rglob("*.py") if "nho" not in p.relative_to(GOC).parts[:1]
             and _import_lancedb(p)]
    assert ngoai == []


def test_bo_quet_bat_duoc_import(tmp_path):
    for i, ma in enumerate(["import lancedb", "import lancedb.index", "from lancedb import connect",
                            "def f():\n    import lancedb\n"]):
        (tmp_path / f"a{i}.py").write_text(ma)
        assert _import_lancedb(tmp_path / f"a{i}.py")
    (tmp_path / "b.py").write_text("import lancedbx\n# import lancedb\n")
    assert not _import_lancedb(tmp_path / "b.py")


def test_lancedb_da_cai_dung_phien_ban():
    import importlib.metadata as m
    assert m.version("lancedb") == "0.40.0"
