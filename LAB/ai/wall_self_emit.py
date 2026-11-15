"""wall_self_emit.py — dev-прогон эмитции каркаса (E6.4d-4/3c-2/1, срез C-2/1).

Вход:  KERNEL/L2-WALL/wall.wall (каркас с проходом 2, срезы A+B+C-1+C-2/1).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: сборка каркаса полным кругом (wall.exe -> enc -> brick -> pegen,
         эмуляция LAB) и прогон EXE каркаса на матрице источников.
         Срез C-2/1 (ВЫРАЖЕНИЯ эмит-режимом: pc_mode/chain_count/
         p_expr-p_mul-p_mdm-p_unary эмит-плечи + emit_alu/shift/imul/
         divmod/addr/len/load) расширяет класс ПОЛНОГО выхода на
         return <выражение> из чисел / имён (load/addr/len) / скобок /
         унарного '-' и операций + - | ^ & << >> * / % (вход — E6.4g-4:
         сборка требует предел входа wall.exe 256 КиБ — исходник каркаса
         перешёл 128 КиБ). Матрица: старые 13 источников срезов A+B+C-1
         + новые 14 return-выражений (число/параметры/все 10 операций/
         цепочки K>1/скобки/унарный/globals var+массив/&локали и
;         &глобали/len str+varr+larr/глубокая вложенность). Источник со
         статами вне класса — регресс: код 0, stdout пуст, отсутствие
         краха (bstk-механика; эмитция неполна — вызовы/getb/индексация
         — срезы C-2/2+).
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
    if r2.exit_code != 0:
        return None, None
    h["s.brick"] = r2.files["s.brick"]
    r3 = lab_run.run_kv(BRICK, ["s.brick", "s.bin"], h)
    if r3.exit_code != 0:
        return None, None
    h["s.bin"] = r3.files["s.bin"]
    h["s.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["s.bin", "s.peg", "s.exe"], h)
    if r4.exit_code != 0 or "s.exe" not in r4.files:
        return None, None
    return r4.files["s.exe"], b2


def oracle_full(src):
    """Полный выход оракула (срез C-1: сравнение ЦЕЛИКОМ, без префикса)."""
    return lab_l2.compile_wall(src).encode("utf-8")


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
    """Многозначные счётчики: 12 функций, 15 str, 22 var, ~130 строк."""
    parts = []
    parts.append("\n".join("var v%d" % i for i in range(10)))
    parts.append("\n".join("var w%d[3]" % i for i in range(6)))
    parts.append("\n".join("str m%d = 'X%d'" % (i, i) for i in range(12)))
    parts.append("\n".join("str n%d = 'Y%d,Z%d'" % (i, i, i)
                           for i in range(3)))
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
        ("0 ext, 2 функции, голый return",
         "func add(a, b)\nend\nfunc main\n  return\nend\n"),
        ("1 параметр + 0 параметров",
         "func work(x)\nend\nfunc main\n  var i\n  return\nend\n"),
        ("4 параметра (r9)",
         "func q(a, b, c, d)\nend\nfunc main\n  return\nend\n"),
        ("8 ext + 10 var (полные hints + DZ-секция)",
         "\n".join("var v%d" % i for i in range(10)) + "\n" + SRC_8EXT),
        ("локальные массивы (v2, framesize)", SRC_LOCAL_ARR),
        ("v2 глобальный массив + str",
         "var a[3]\nvar s\nstr m = 'HI'\nfunc main\n  return\nend\n"),
        ("многозначные счётчики (12 функций, 15 str, 22 var)", _multi()),
        ("пустая str (DZ 0)", "str e = ''\nfunc main\n  return\nend\n"),
        ("str-only: экраны всех 6 видов",
         "str s = 'a\\nb\\rc\\td\\0e\\\\f'\nfunc main\n  return\nend\n"),
        ("граница DB-строки: 16/17 байтов",
         "str a = '0123456789ABCDEF'\n"
         "str b = '0123456789ABCDEFG'\nfunc main\n  return\nend\n"),
        ("длинная str 42 Б — 3 строки DB (класс дефекта №16)",
         "str u = 'U-L2-WALL CMDS: WALL <SRC.WALL> "
         "<OUT.B2>'\nfunc main\n  return\nend\n"),
        ("var-only: скаляр + массив",
         "var g\nvar a[3]\nvar z[1]\nfunc main\n  return\nend\n"),
        ("отступы и «;»-хвосты объявлений (карта текстов)",
         "  var g ; комментарий\n\tstr s = 'ab' ; ещё\n"
         "  func main\n    return\n  end\n"),
        # ---- срез C-2/1: return <выражение> (полный выход) ----
        ("C2: return число", "func main\n  return 42\nend\n"),
        ("C2: return параметр + параметр",
         "func add(a, b)\n  return a + b\nend\nfunc main\n  return 0\nend\n"),
        ("C2: все 5 ALU-операций в цепочке",
         "func f(a, b, c, d)\n  return a + b - c | d ^ a & b\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: сдвиги << >>",
         "func f(a, b)\n  return a << 2 >> 3 & b\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: v2 * / % (заголовок v2)",
         "func f(a, b, c, d)\n  return a * b / c % d + 1\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: скобки и приоритеты",
         "func f(a, b, c, d)\n  return (a + b) * (c - d)\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: унарный минус (в т.ч. двойной)",
         "func f(a)\n  return -a + -3 - --a\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: глобальные var + массив",
         "var g\nvar h[3]\nfunc main\n  return g + 1\nend\n"),
        ("C2: &локальный массив и &глобаль",
         "var g\nfunc f(x)\n  var a[4]\n  return &a\nend\n"
         "func main\n  return &g\nend\n"),
        ("C2: len str + глобальный + локальный массив",
         "str s = 'abc'\nvar h[5]\nfunc f(x)\n  var a[7]\n"
         "  return len(s) + len(h) + len(a)\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: длинная левая цепочка (K=5)",
         "func f(a, b, c, d)\n  return a + b + c + d + 1 + 2\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: вложенная смесь уровней",
         "func f(a, b, c, d)\n"
         "  return ((a + b) * 2 - (c << 1)) % 7 ^ (d & (a - b))\nend\n"
         "func main\n  return 0\nend\n"),
        ("C2: деление без скобок (уровни ниже)",
         "func f(a, b, c)\n  return a & b + c / 2\nend\n"
         "func main\n  return 0\nend\n"),
    ]
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    open(path, "wb").write(exe)
    bad = []
    for name, src in cases:
        src_b = src.encode("utf-8")
        out = oracle_full(src)
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": src_b}).run()
        got = rs.files.get("t.b2", b"")
        if rs.exit_code != 0 or rs.stdout != b"":
            bad.append("%s (код=%s out=%r)" % (name, rs.exit_code,
                                               rs.stdout[:40]))
        elif got != out:
            bad.append("%s (получено %d Б, нужно %d Б)"
                       % (name, len(got), len(out)))
            if got:
                n = min(len(got), len(out))
                for i in range(n):
                    if got[i] != out[i]:
                        print("   первое расхождение @%d:\n"
                              "   получено: %r\n   нужно:    %r"
                              % (i, got[max(0, i - 30):i + 30],
                                 out[max(0, i - 30):i + 30]))
                        break
        else:
            print("   %-56s %d Б (шагов=%d)" % (name, len(got), rs.steps))
    check("T-E6-52+54+55/dev: функции+данные+выражения == оракулу "
          "(%d источников)" % len(cases), not bad, "; ".join(bad[:3]))

    # регресс: статы-выражения вне класса среза — код 0, без краха
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
