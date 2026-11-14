"""wall_self_test.py — dev-прогон секции 12 батареи вне CI (E6.4d-1).

Вход:  KERNEL/L2-WALL/wall.wall (само-исходник каркаса, WALL v2).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: тот же набор проверок, что T-E6-49a/b/c в батарее
         (LAB/py/lab_t_wallself.py — единый источник эталонов):
         компиляция каркаса wall.exe == оракулу, полный круг до EXE,
         CLI-поведение каркаса == wall.exe на матрице путей.
Запуск: python3 LAB/ai/wall_self_test.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_t_wallself  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print(("[OK] " if ok else "[FAIL] ") + name +
          (("  " + note) if note else ""))


def kfile(rel):
    return open(os.path.join(KERNEL, rel), "rb").read()


def kpath(rel):
    return os.path.join(KERNEL, rel)


def kernel_host():
    files = {}
    for base, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def main():
    lab_t_wallself.run(check, kpath, kfile, kernel_host)
    print("\nИТОГ: %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                "OK" if not FAIL else "— ПРОВАЛЫ"))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
