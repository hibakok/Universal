"""Быстрая проверка новых .wall-файлов каркаса (dev, E6.4d-2/2).

1. splice-оракул клеит wall.wall (корень + wall_self_c + wall_self_n).
2. Оракул WALL компилирует плоский текст (синтаксис + семантика имён).
3. Печать счётчиков (строки частей, размер выхода, флаг v2).
Запуск: python3 LAB/ai/wall_syntax_check.py (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_splice  # noqa: E402
import lab_l2      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
K = os.path.join(ROOT, "KERNEL")


def main():
    host = {}
    for base, _d, fs in os.walk(K):
        for f in fs:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, K).replace(os.sep, "/").lower()
            host[rel] = open(p, "rb").read()
    flat = lab_splice.splice("l2-wall/wall.wall", host)
    for part in ("wall.wall", "wall_self_c.wall", "wall_self_n.wall"):
        n = open(os.path.join(K, "L2-WALL", part), "rb").read()
        print("%-20s %4d строк" % (part, n.count(b"\n")))
    print("плоский: %d строк, %d байт (предел 131072)" %
          (flat.count(b"\n"), len(flat)))
    out = lab_l2.compile_wall(flat.decode("latin1"))
    print("оракул: OK, выход %d байт" % len(out.encode()))
    print(out.splitlines()[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
