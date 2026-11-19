"""uva_syntax_check.py — быстрая проверка исходника uva.wall (LAB/ai).

Вход:  KERNEL/L3-UVA/uva.wall + части uva_self_*.wall.
Выход: [OK]/[FAIL] — склейка splice-оракулом + компиляция оракулом
       WALL (lab_l2.compile_wall) без эмуляции; печать счётчиков.
Функция: быстрый фильтр синтаксиса перед полной сборкой (как
         ai/wall_syntax_check.py для wall.wall).
Запуск: python3 LAB/ai/uva_syntax_check.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2            # noqa: E402
import lab_splice        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))


def host():
    files = {}
    kdir = os.path.join(ROOT, "KERNEL")
    for root, _dirs, fs in os.walk(kdir):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, kdir).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def main():
    flat = lab_splice.splice("L3-UVA/uva.wall", host())
    print("склейка: %d строк, %d байт" % (flat.count(b"\n") + 1, len(flat)))
    try:
        out = lab_l2.compile_wall(flat.decode("latin1"))
    except Exception as e:                        # noqa: BLE001
        print("[FAIL] оракул WALL: %r" % (e,))
        return 1
    print("[OK] компиляция оракулом WALL: %d строк выхода"
          % out.count("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
