"""bs-2bd.1.10: canh giữ vòng import cấp MODULE và `__init__.py` không import gì.

Cạnh = import chạy LÚC NẠP module: thân module, kể cả trong `if`/`try`/`with` và thân `class` (chúng chạy khi nạp);
không tính thân hàm/lambda (import trễ). Phân giải theo DANH SÁCH module thật: `import tram.a.b` → `tram.a.b` (+ các
package cha `tram.a`, `tram`); `from tram.a import x` → `tram.a`, và thêm `tram.a.x` nếu `x` là module; import tương
đối (`from . import x`, `from .y import f`, `from ..z import g`) phân giải theo package của file. Giới hạn ghi rõ:
import có điều kiện (`if`/`try`) được tính như luôn chạy — thừa chứ không sót, trừ khối `if TYPE_CHECKING:` (không bao
giờ chạy lúc nạp) bị bỏ qua; import động (`importlib.import_module`, `__import__`) không thấy được — test cuối kiểm
`tram/` không dùng chúng ở thân module."""
import ast
from pathlib import Path

GOC = Path(__file__).resolve().parents[1] / "tram"


def _ten(goc: Path, p: Path) -> str:
    return ".".join(("tram", *p.relative_to(goc).with_suffix("").parts)).removesuffix(".__init__")


def _import_luc_nap(cay: ast.AST):
    """Nút import chạy lúc nạp module: không vào thân hàm/lambda, bỏ khối `if TYPE_CHECKING:`."""
    hang = list(ast.iter_child_nodes(cay))
    while hang:
        n = hang.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            yield n
        elif isinstance(n, ast.If) and ast.unparse(n.test) in ("TYPE_CHECKING", "typing.TYPE_CHECKING"):
            hang += n.orelse
        else:
            hang += ast.iter_child_nodes(n)


def _goc_tuong_doi(ten: str, la_init: bool, n: ast.ImportFrom) -> str:
    phan = ten.split(".") if la_init else ten.split(".")[:-1]       # package chứa file
    phan = phan[:len(phan) - (n.level - 1)]
    return ".".join([*phan, *([n.module] if n.module else [])])


def do_thi(goc: Path) -> dict[str, set[str]]:
    """module `tram.*` → các module `tram.*` nó nạp lúc nạp (đã phân giải theo danh sách module thật)."""
    tep = {_ten(goc, p): p for p in goc.rglob("*.py")}
    ra = {}
    for ten, p in tep.items():
        den = set()
        for n in _import_luc_nap(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Import):
                dich = [a.name for a in n.names]
            else:
                cha = _goc_tuong_doi(ten, p.name == "__init__.py", n) if n.level else n.module
                dich = [cha] + [f"{cha}.{a.name}" for a in n.names if f"{cha}.{a.name}" in tep]
            for d in dich:
                phan = d.split(".")
                den |= {m for m in (".".join(phan[:i]) for i in range(1, len(phan) + 1)) if m in tep}
        ra[ten] = den - {ten}
    return ra


def vong(dt: dict[str, set[str]]) -> list[list[str]]:
    """Các thành phần liên thông mạnh > 1 nút (Tarjan, lặp — không đệ quy)."""
    chi_so, thap, tren, ngan, ra, dem = {}, {}, set(), [], [], 0
    for goc in dt:
        if goc in chi_so:
            continue
        cong = [(goc, iter(sorted(dt.get(goc, ()))))]
        chi_so[goc] = thap[goc] = dem
        dem += 1
        ngan.append(goc)
        tren.add(goc)
        while cong:
            v, con = cong[-1]
            w = next(con, None)
            if w is None:
                cong.pop()
                if cong:
                    thap[cong[-1][0]] = min(thap[cong[-1][0]], thap[v])
                if thap[v] == chi_so[v]:
                    tp = []
                    while True:
                        x = ngan.pop()
                        tren.discard(x)
                        tp.append(x)
                        if x == v:
                            break
                    if len(tp) > 1:
                        ra.append(sorted(tp))
            elif w not in chi_so:
                chi_so[w] = thap[w] = dem
                dem += 1
                ngan.append(w)
                tren.add(w)
                cong.append((w, iter(sorted(dt.get(w, ())))))
            elif w in tren:
                thap[v] = min(thap[v], chi_so[w])
    return ra


def _cay(tmp_path, tep: dict[str, str]) -> Path:
    goc = tmp_path / "tram"
    for ten, nd in {"__init__.py": "", "a/__init__.py": "", "b/__init__.py": "", **tep}.items():
        (goc / ten).parent.mkdir(parents=True, exist_ok=True)
        (goc / ten).write_text(nd)
    return goc


def test_bat_duoc_moi_dang_import_luc_nap(tmp_path):
    goc = _cay(tmp_path, {
        "a/x.py": "from tram.a import y\n",                                   # from-package lấy module con
        "a/y.py": "from . import x\n",                                        # tương đối, cùng package
        "a/p.py": "try:\n    from .q import f\nexcept ImportError:\n    pass\n",          # trong try
        "a/q.py": "class K:\n    from tram.a.p import g\n",                   # thân class chạy lúc nạp
        "b/m.py": "if True:\n    from ..a import z\nimport tram.b.n\n",       # tương đối 2 bậc + trong if
        "a/z.py": "from tram.b.m import h\n",
        "b/n.py": "def f():\n    import tram.b.m\n",                          # import trễ trong hàm: không tính
        "b/t.py": "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import tram.b.u\n",
        "b/u.py": "import tram.b.t\n"})                                       # TYPE_CHECKING: không tính
    assert sorted(vong(do_thi(goc))) == [["tram.a.p", "tram.a.q"], ["tram.a.x", "tram.a.y"],
                                         ["tram.a.z", "tram.b.m"]]


def test_tram_khong_co_vong_cap_module_va_init_khong_import():
    assert vong(do_thi(GOC)) == []
    assert [str(p.relative_to(GOC)) for p in GOC.rglob("__init__.py") if any(
        isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))))] == []


def test_dieu_kien_chua_type_checking_khong_duoc_bo_qua(tmp_path):
    goc = _cay(tmp_path, {
        "a/x.py": "from typing import TYPE_CHECKING\nif not TYPE_CHECKING:\n    from . import y\n",
        "a/y.py": "from . import x\n",
        "b/m.py": "from typing import TYPE_CHECKING\nif TYPE_CHECKING or True:\n    from . import n\n",
        "b/n.py": "from . import m\n"})
    assert sorted(vong(do_thi(goc))) == [["tram.a.x", "tram.a.y"], ["tram.b.m", "tram.b.n"]]


def test_tram_khong_import_dong_luc_nap():
    dong = []
    for p in GOC.rglob("*.py"):
        cay = ast.parse(p.read_text(encoding="utf-8"))
        ham = {id(x) for f in ast.walk(cay) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
               for x in ast.walk(f)}
        dong += [f"{p.relative_to(GOC)}:{n.lineno}" for n in ast.walk(cay) if isinstance(n, ast.Call)
                 and id(n) not in ham and ast.unparse(n.func) in ("importlib.import_module", "import_module",
                                                                  "__import__")]
    assert dong == []
