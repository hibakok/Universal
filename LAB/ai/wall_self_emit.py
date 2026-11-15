"""wall_self_emit.py — dev-прогон эмитции каркаса (E6.4d-4/3a, срез A).

Вход:  KERNEL/L2-WALL/wall.wall (каркас с проходом 2, срез A).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: сборка каркаса полным кругом (wall.exe -> enc -> brick -> pegen,
         эмуляция LAB) и прогон EXE каркаса на матрице источников: выход
         .b2 обязан быть ТОЧНЫМ ПРЕФИКСОМ выхода оракула — от заголовка
         до конца строки входа int3 (срез A = фиксированный пролог:
         заголовок с счётчиками/версией, область импортов 0x200, секция
         кода + :_entry). Матрица покрывает: 0/1/3/8 ext (все ветви
         импортов), v1/v2 (заголовок), многозначные счётчики, пустые
         str/var, комментарии-строки.
Запуск: python3 LAB/ai/wall_self_emit.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2                             # noqa: E402
import lab_l2_prog                        # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402
import lab_win                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
WALL = os.path.join(KERNEL, "L2-WALL", "wall.exe")
ENC = os.path.join(KERNEL, "L1-ENC", "enc.exe")
BRICK = os.path.join(KERNEL, "L1-BRICK", "brick.exe")
PEGEN = os.path.join(KERNEL, "L0-PEGEN", "pegen.exe")

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print(("[OK] " if ok else "[FAIL] ") + name +
          (("  " + note) if note else ""))


def kernel_host():
    files = {}
    for base, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def build_skeleton():
    """Полный круг сборки EXE каркаса; вернуть (exe, b2)."""
    src = lab_splice.splice("L2-WALL/wall.wall", kernel_host())
    r = lab_run.run_kv(WALL, ["s.wall", "s.b2"], {"s.wall": src})
    if r.exit_code != 0:
        return None, None
    b2 = r.files["s.b2"]
    h = {"s.b2": b2}
    r2 = lab_run.run_kv(ENC, ["s.b2", "s.brick"], h)
    h["s.brick"] = r2.files["s.brick"]
    r3 = lab_run.run_kv(BRICK, ["s.brick", "s.bin"], h)
    h["s.bin"] = r3.files["s.bin"]
    h["s.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["s.bin", "s.peg", "s.exe"], h)
    if not (r2.exit_code == 0 and r3.exit_code == 0 and
            r4.exit_code == 0 and r4.files.get("s.exe")):
        return None, b2
    return r4.files["s.exe"], b2


def oracle_prefix(src_bytes):
    """Выход оракула; префикс среза A — до конца строки int3 входа."""
    out = lab_l2.compile_wall(src_bytes.decode("utf-8"))
    lines = out.split("\n")
    i = lines.index(":_entry")
    prefix = "\n".join(lines[:i + 4]) + "\n"
    return out.encode(), prefix.encode()


SRC_8EXT = """\
ext GetStdHandle
ext WriteFile
ext ExitProcess
ext GetCommandLineA
ext CreateFile2
ext ReadFile
ext CloseHandle
ext GlobalAlloc
var g
str msg = 'HI\\r\\n'
func main
  g = 7
  ExitProcess(0)
end
"""

SRC_V2 = """\
var a[3]
var s
func work(x, y)
  var r
  r = x * y + x % 3
  return r
end
func main
  var i
  i = 0
  s = 0
  while i < 3
    a[i] = work(i + 2, 5)
    if a[i] > 6 && s != 2 || a[i] == 1
      s = s + a[i]
    end
    i = i + 1
  end
  s = a[0] + a[1] + a[2]
  s = s / 2
  return 0
end
"""

def _multi():
    """Многозначные счётчики: 12 функций, 15 str, 12 var, ~130 строк."""
    parts = []
    parts.append("\n".join("var v%d" % i for i in range(10)))
    parts.append("\n".join("str m%d = 'X%d'" % (i, i) for i in range(12)))
    parts.append("\n".join("ext E%d" % i for i in range(6)))
    for i in range(11):
        parts.append("func f%d(x)\n  return x + %d\nend" % (i, i))
    body = ["func main", "  v0 = 0"]
    for i in range(11):
        body.append("  v0 = f%d(v0)" % i)
    body.append("  return 0")
    body.append("end")
    parts.append("\n".join(body))
    parts.append("; " + "z" * 40)
    parts.append("; " + "y" * 40)
    return "\n".join(parts) + "\n"


def main():
    exe, b2 = build_skeleton()
    check("сборка каркаса: полный круг (wall+enc+brick+pegen)",
          bool(exe), "s.b2=%s" % (len(b2) if b2 else "-"))
    if not exe:
        print("\nИТОГ: %d/%d — ПРОВАЛЫ" % (len(PASS), len(PASS) + len(FAIL)))
        return 1

    cases = [
        ("0 ext, 1 var, без str", "var g\nfunc main\n  g = 1\n"
         "  return 0\nend\n"),
        ("1 ext", "ext ExitProcess\nvar g\nstr m = 'A'\nfunc main\n"
         "  g = 2\n  ExitProcess(0)\nend\n"),
        ("3 ext (DEMO_WALL)", lab_l2_prog.DEMO_WALL),
        ("8 ext (полные hints)", SRC_8EXT),
        ("v2 (массивы, * / %, && ||)", SRC_V2),
        ("многозначные счётчики (12 функций)", _multi()),
        ("пустая str", "str e = ''\nfunc main\n  return 0\nend\n"),
    ]
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    open(path, "wb").write(exe)
    bad = []
    for name, src in cases:
        src_b = src.encode("utf-8")
        out, prefix = oracle_prefix(src_b)
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": src_b}).run()
        got = rs.files.get("t.b2", b"")
        if rs.exit_code != 0 or rs.stdout != b"":
            bad.append("%s (код=%s out=%r)" % (name, rs.exit_code,
                                               rs.stdout[:40]))
        elif got != prefix:
            bad.append("%s (префикс: получено %d Б, нужно %d Б)"
                       % (name, len(got), len(prefix)))
            if got:
                n = min(len(got), len(prefix))
                for i in range(n):
                    if got[i] != prefix[i]:
                        print("   первое расхождение @%d:\n"
                              "   получено: %r\n   нужно:    %r"
                              % (i, got[max(0, i - 30):i + 30],
                                 prefix[max(0, i - 30):i + 30]))
                        break
        print("   %-38s %d Б / %d Б (шагов=%d)"
              % (name, len(got), len(prefix), rs.steps))
    os.unlink(path)
    check("T-E6-52/dev: префикс эмитции == оракулу (%d источников)"
          % len(cases), not bad, "; ".join(bad[:3]))

    print("\nИТОГ: %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                "OK" if not FAIL else "— ПРОВАЛЫ"))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
