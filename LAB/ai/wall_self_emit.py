"""wall_self_emit.py — dev-прогон эмитции каркаса (E6.4d-4/3c-2/3, срез C-2/3).

Вход:  KERNEL/L2-WALL/wall.wall (каркас с проходом 2, срезы A+B+C-1+
         C-2/1+C-2/2+C-2/3).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: сборка каркаса полным кругом (wall.exe -> enc -> brick -> pegen,
         эмуляция LAB) и прогон EXE каркаса на матрице источников.
         Срез C-2/3 (СТАТЫ-ИМЕНА эмит-режимом: НОВАЯ часть wall_self_t.wall
         — K2-E02D emit_sstore + K2-Y009 p2s_setb + K2-Y00B p2_namestmt;
         плечи диспетчера p2_line; ДЕФЕКТ №22 закрыт — astore_chk копирует
         lay-окно только в стате pc_mode == 0, как P01D wall.exe)
         расширяет класс ПОЛНОГО выхода на статы-имена в телах:
         присваивания локали/глобали (цель — валидация прохода 2:
         массив/str/func/ext/неизвестное — ERR), вызовы-утверждения
         func/ext 0..5 аргументов (want 0), astore имя[выр]... = выр
         (k == 1 — emit_load-база; k > 1 — pp_prim0(k) + pp_pairs(1,
         k-1); последняя пара и значение ПОРОЗНЬ через S0/S1/S2 +
         хвост shl 3 / add / mov [r10], r11) и setb(выр, выр, выр)
         (S0/S1/S2 + байтовая запись [r10+r11] = al — индекс БЕЗ *8).
         Матрица: 13 источников срезов A+B+C-1 + 14 return-выражений
         C-2/1 + 13 вызовов/getb/индексации C-2/2 + 10 статов-имён
         C-2/3 (канарейка №22 — astore локального массива в функции,
         отличной от последней функции прохода 1). Источник со
         статами вне класса (if/while/else/break/continue) — регресс:
         код 0, stdout пуст, отсутствие краха (bstk-механика;
         guard-эмитция — срез C-3).
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
        # ---- срез C-2/2: вызовы / getb / индексация в return ----
        ("C22: вызов 1 аргумент + вызов 0 аргументов",
         "func f(x)\n  return x + 1\nend\nfunc g\n  return 7\nend\n"
         "func main\n  return f(2) + g()\nend\n"),
        ("C22: вызов 4 аргументов (ARGREG r9)",
         "func q(a, b, c, d)\n  return a + b + c + d\nend\n"
         "func main\n  return q(1, 2, 3, 4)\nend\n"),
        ("C22: вложенные вызовы (фикс №19, базы C-слотов)",
         "func h(x)\n  return x * 2\nend\nfunc g(x, y)\n  return x + y\nend\n"
         "func f(x, y)\n  return x - y\nend\n"
         "func main\n  return f(g(h(1), 2), h(g(3, h(4))))\nend\n"),
        ("C22: ext 0/4 аргументов в выражении",
         "ext GetTickCount\next ReadFile\n"
         "func main\n  return GetTickCount() + ReadFile(1, 2, 3, 4)\nend\n"),
        ("C22: ext 5 аргументов (S5 + [rsp+20])",
         "ext WriteFile\n"
         "func main\n  return WriteFile(1, 2, 3, 4, 5)\nend\n"),
        ("C22: getb простые и с выражениями",
         "str s = 'ABC'\nfunc f(x)\n  var a[4]\n"
         "  return getb(&s, 1) + getb(a, x + 1)\nend\n"
         "func main\n  return getb(&s, 2)\nend\n"),
        ("C22: индексация массива и цепочки указателей",
         "var m[3]\nfunc f(x)\n  var a[4]\n  var p[2]\n"
         "  return a[x] + p[0][1]\nend\n"
         "func main\n  return m[2] + f(1)\nend\n"),
        ("C22: индексация с выражением-индексом и вызовом",
         "var g[4]\nfunc f(x)\n  return x * 2\nend\n"
         "func main\n  return g[f(1) + 1]\nend\n"),
        ("C22: вызов-база индексации (откат+перепознание)",
         "var t[4]\nfunc f(x)\n  return t[x]\nend\n"
         "func main\n  return f(0)[1]\nend\n"),
        ("C22: скобочная база индексации",
         "var a[4]\nfunc main\n  return (a + 0)[2]\nend\n"),
        ("C22: getb с вызовами в аргументах",
         "str s = 'XY'\nfunc f(x)\n  return x\nend\n"
         "func main\n  return getb(&s, f(1))\nend\n"),
        ("C22: смесь: вызовы + индексация + getb + операции",
         "str s = 'Q'\nvar a[4]\nfunc f(x, y)\n  return x + y\nend\n"
         "func g(x)\n  return a[x]\nend\n"
         "func main\n  return f(g(1), getb(&s, 0)) * a[2] - f(1, 2)\nend\n"),
        ("C22: глубокая вложенность (вызов в индексе вызова)",
         "var a[4]\nfunc f(x)\n  return x + 1\nend\n"
         "func main\n  return a[f(f(a[0]))]\nend\n"),
        # ---- срез C-2/3: статы-имена эмит-режимом ----
        ("C23: присваивание локали и глобали",
         "var g\nfunc main\n  var i\n  i = 5\n  g = 7\n  return 0\nend\n"),
        ("C23: присваивание с выражениями (вызовы/индексация/getb)",
         "str s = 'AB'\nvar g[4]\nfunc f(x)\n  return x * 2\nend\n"
         "func main\n  var i\n  i = f(3) + g[1] + getb(&s, 0)\n"
         "  g[2] = i + 1\n  return i\nend\n"),
        ("C23: вызов-утверждение func 0..4 аргументов",
         "func a\n  return 1\nend\nfunc b(x)\n  return x\nend\n"
         "func q(x, y, z, w)\n  return x + y + z + w\nend\n"
         "func main\n  a()\n  b(9)\n  q(1, 2, 3, 4)\n  return 0\nend\n"),
        ("C23: вызов-утверждение ext 0/4/5 аргументов",
         "ext GetTickCount\next ReadFile\next WriteFile\n"
         "func main\n  GetTickCount()\n  ReadFile(1, 2, 3, 4)\n"
         "  WriteFile(1, 2, 3, 4, 5)\n  return 0\nend\n"),
        ("C23: astore локальный/глобальный массив (k = 1)",
         "var m[3]\nfunc main\n  var a[4]\n  a[0] = 11\n"
         "  a[1 + 1] = a[0] + 5\n  m[1] = a[2]\n  m[2] = m[1]\n"
         "  return a[0]\nend\n"),
        ("C23: astore цепочка k=2/k=3 + индекс-выражения",
         "var g[4]\nfunc main\n  var p[2]\n  var q[2]\n"
         "  p[0][1] = 9\n  q[0][g[0]][1] = 8\n  g[1] = p[0][1]\n"
         "  return 0\nend\n"),
        ("C23: setb простые и с выражениями/вызовами",
         "str s = 'AB'\nfunc f(x)\n  return x\nend\n"
         "func main\n  var a[4]\n  setb(&s, 0, 65)\n"
         "  setb(a, 1 + 1, 66)\n  setb(&s, f(1), f(2))\n  return 0\nend\n"),
        ("C23: setb + astore + ext5 в одной функции (S + S5)",
         "ext WriteFile\nstr s = 'Q'\nvar g[2]\nfunc f(x)\n  return x\nend\n"
         "func main\n  var i\n  var a[4]\n  i = f(2)\n  a[i] = i + 1\n"
         "  g[0] = a[i]\n  setb(&s, f(0), 81)\n"
         "  WriteFile(1, 2, 3, 4, 5)\n  return i\nend\n"),
        ("C23: канарейка №22 — astore локали не в последней функции",
         "func f(x)\n  var aaa[4]\n  var b\n  aaa[x] = x + 1\n  b = aaa[x]\n"
         "  return b\nend\n"
         "func main\n  var zzz[8]\n  zzz[3] = f(1)\n  return zzz[3]\nend\n"),
        ("C23: смесь всего (присваивания + вызовы + astore + setb)",
         "ext ReadFile\nstr s = 'XYZ'\nvar g[4]\nvar v\n"
         "func f(x, y)\n  return x + y\nend\n"
         "func h(x)\n  var t[2]\n  t[0] = x\n  setb(&s, x, 65)\n"
         "  return t[0]\nend\n"
         "func main\n  var i\n  i = f(1, 2)\n  g[i] = h(i)\n"
         "  v = g[i] + len(s)\n  ReadFile(1, 2, 3, 4)\n  setb(&s, 1, 66)\n"
         "  return v\nend\n"),
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
    check("T-E6-52+54+55+56+57/dev: функции+данные+выражения+статы == "
          "оракулу (%d источников)" % len(cases), not bad, "; ".join(bad[:3]))

    # регресс: статы вне класса (guard-эмитция if/while — срез C-3) —
    # код 0, без краха; присваивания внутри тел уже эмитятся (C-2/3),
    # if/while/else/break/continue — нет (bstk-механика цела)
    src = ("func main\n  var i\n  i = 0\n  while i < 3\n    i = i + 1\n"
           "    if i == 2\n      i = 5\n    end\n  end\n  return 0\n"
           "end\n")
    rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                         {"t.wall": src.encode("utf-8")}).run()
    check("статы вне класса (if/while): код 0, stdout пуст (bstk)",
          rs.exit_code == 0 and rs.stdout == b"",
          "код=%s out=%r" % (rs.exit_code, rs.stdout[:40]))
    os.unlink(path)

    print("\nИТОГ: %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                "OK" if not FAIL else "— ПРОВАЛЫ"))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
