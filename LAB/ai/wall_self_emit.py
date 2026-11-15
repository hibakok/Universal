"""wall_self_emit.py — dev-прогон эмитции каркаса (E6.4d-4/3b, срез B).

Вход:  KERNEL/L2-WALL/wall.wall (каркас с проходом 2, срезы A+B).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: сборка каркаса полным кругом (wall.exe -> enc -> brick -> pegen,
         эмуляция LAB) и прогон EXE каркаса на матрице источников.
         Срез B (функции): на классе источников, тела которых содержат
         только var / голый return / end, выход каркаса обязан быть
         байт-в-байт равен выходу оракула ЦЕЛИКОМ (если нет глобальных
         str/var) или ТОЧНЫМ ПРЕФИКСОМ до секции «; --- данные: ...»
         (секции данных — срез C). Матрица покрывает: 0..8 ext (все
         ветви импортов), 0..4 параметра (ARGREG rcx/rdx/r8/r9),
         локальные массивы (nslots/framesize), v1/v2 (заголовок),
         многозначные счётчики, пустую str, var-локали. Источник с
         статами-выражениями (вне класса среза B) — регресс: код 0,
         stdout пуст, отсутствие краха (bstk-механика).
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


def oracle_full_prefix(src):
    """(полный выход оракула; префикс среза B — до секции данных).

    Секции данных («; --- данные: ...») — срез C: префикс среза B
    кончается на последней строке последнего эпилога функции.
    """
    out = lab_l2.compile_wall(src)
    lines = out.split("\n")
    cut = None
    for i, ln in enumerate(lines):
        if ln.startswith("; --- данные:"):
            cut = i
            break
    if cut is None:
        enc = out.encode()
        return enc, enc
    prefix = ("\n".join(lines[:cut]) + "\n").encode()
    return out.encode(), prefix


SRC_8EXT = """\
ext GetStdHandle
ext WriteFile
ext ExitProcess
ext GetCommandLineA
ext CreateFile2
ext ReadFile
ext CloseHandle
ext GlobalAlloc
func f0(a, b, c, d)
end

func main
  return
end
"""

SRC_LOCAL_ARR = """\
func work(x)
  var r
  var a[4]
  var t[2]
  return
end

func main
  var i
  var a[12]
  return
end
"""


def _multi():
    """Многозначные счётчики: 12 функций, 15 str, 12 var, ~130 строк."""
    parts = []
    parts.append("\n".join("var v%d" % i for i in range(10)))
    parts.append("\n".join("str m%d = 'X%d'" % (i, i) for i in range(12)))
    parts.append("\n".join("ext E%d" % i for i in range(6)))
    for i in range(11):
        parts.append("func f%d(x)\nend" % i)
    parts.append("func main\n  return\nend")
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
        ("0 ext, 2 функции, голый return (полный)",
         "func add(a, b)\nend\nfunc main\n  return\nend\n"),
        ("1 параметр + 0 параметров (полный)",
         "func work(x)\nend\nfunc main\n  var i\n  return\nend\n"),
        ("4 параметра (r9, полный)",
         "func q(a, b, c, d)\nend\nfunc main\n  return\nend\n"),
        ("8 ext (полные hints, префикс: 10 var)",
         "\n".join("var v%d" % i for i in range(10)) + "\n" + SRC_8EXT),
        ("локальные массивы (v2, framesize, полный)", SRC_LOCAL_ARR),
        ("v2 глобальный массив + str (заголовок v2, префикс)",
         "var a[3]\nvar s\nstr m = 'HI'\nfunc main\n  return\nend\n"),
        ("многозначные счётчики (12 функций, префикс)", _multi()),
        ("пустая str (префикс)", "str e = ''\nfunc main\n  return\nend\n"),
    ]
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    open(path, "wb").write(exe)
    bad = []
    for name, src in cases:
        src_b = src.encode("utf-8")
        out, prefix = oracle_full_prefix(src)
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
        full = "ПОЛНЫЙ" if out == prefix else "префикс"
        print("   %-44s %d Б / %d Б (%s; шагов=%d)"
              % (name, len(got), len(prefix), full, rs.steps))
    check("T-E6-52/dev: пролог+функции == оракулу (%d источников)"
          % len(cases), not bad, "; ".join(bad[:3]))

    # регресс: статы-выражения вне класса среза B — код 0, без краха
    src = ("func main\n  var i\n  i = 0\n  while i < 3\n    i = i + 1\n"
           "    if i == 2\n      i = 5\n    end\n  end\n  return 0\n"
           "end\n")
    rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                         {"t.wall": src.encode("utf-8")}).run()
    check("статы вне класса: код 0, stdout пуст (bstk-механика)",
          rs.exit_code == 0 and rs.stdout == b"",
          "код=%s out=%r" % (rs.exit_code, rs.stdout[:40]))
    os.unlink(path)

    print("\nИТОГ: %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                "OK" if not FAIL else "— ПРОВАЛЫ"))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
