"""bridge_syntax_check.py — быстрая проверка синтаксика bridge.wall без
эмуляции (прецедент wall_syntax_check.py / uva_syntax_check.py):
splice-оракул (склейка разреза) + compile_wall (оракул WALL v1/v2) —
ловит ошибки грамматики/имен/типов за секунды, ДО дорогостоящей
пересборки конвейером под эмуляцией (срезы E9.2-3c+).

Выход: код 0 — компиляция ок (печать размеров b2); 1 — ошибка
(печать исключения WallError).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "py"))

import lab_l2                             # noqa: E402
import lab_splice                         # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..")


def main():
    try:
        host = {}
        for root, _dirs, fs in os.walk(os.path.join(ROOT, "KERNEL")):
            for f in fs:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, os.path.join(ROOT, "KERNEL")) \
                    .replace(os.sep, "/").lower()
                host[rel] = open(p, "rb").read()
        flat = lab_splice.splice("L5-BRIDGE/bridge.wall", host)
        b2 = lab_l2.compile_wall(flat.decode("latin1"))
        print("OK: bridge.wall компилируется оракулом WALL: "
              "b2 %d Б, %d строк"
              % (len(b2.encode()), flat.decode("latin1").count("\n")))
        return 0
    except Exception as e:                  # noqa: BLE001
        print("FAIL: %s: %s" % (type(e).__name__, e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
