"""bridge_test.py — построитель и dev-тест моста bridge.exe (E9.2-1/2,
LAB/ai; НЕ часть системы UNIVERSAL — частный инструмент ИИ, как
kernel_test.py).

Вход:  KERNEL/L5-BRIDGE/bridge.wall (+ части bridge_self_*.wall
       + bridge.peg).
Выход: 1) артефакты KERNEL/L5-BRIDGE/{bridge.b2, bridge.brick,
          bridge.exe} — сборка конвейером РЕАЛЬНЫХ инструментов под
          эмуляцией (wall.exe -> enc.exe -> brick.exe -> pegen.exe;
          фикс-пункт воспроизводимости закреплён в батарее — T-E9-17);
       2) отчёт [OK]/[FAIL] секции 18 батареи целиком (LAB/py/
          lab_t_bridge.py: T-E9-01..21 — оракул E9.1 + КАРКАС E9.2-1
          + СПУСК E9.2-2: фикс-пункт сборки, факт-строки (с
          INS/TARGET/BSS) == оракулу на 12 артефактах, CLI-контракт +
          мутант-отказы (вкл. отказы спуска) + легальные отклонения,
          синтетика теней T-E9-21, круг оракула над bridge.exe);
       3) карта меток bridge.brick (для BYTECODE.md — лениво: импорт
          label_map) и SHA-256 артефактов (для VERIFY.md).
Запуск: python3 LAB/ai/bridge_test.py  (из корня репозитория)
"""
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_t_bridge                      # noqa: E402
from label_map import labels_of          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
L5 = os.path.join(KERNEL, "L5-BRIDGE")


def kpath(rel):
    return os.path.join(KERNEL, rel)


def kfile(rel):
    return open(os.path.join(KERNEL, rel), "rb").read()


def kernel_host():
    files = {}
    for root, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def main():
    print("=== bridge_test: сборка моста M5-BRIDGE (E9.2-1) ===")
    ok, a, note = lab_t_bridge.build(kpath, kfile, kernel_host)
    print("[OK] сборка" if ok else "[FAIL] сборка", note)
    if not ok:
        return 1

    # запись артефактов (фикс-пункт: батарея T-E9-17 сверяет их с этой
    # сборкой каждый пуш)
    for name, data in (("bridge.b2", a["b2"]),
                       ("bridge.brick", a["brick"]),
                       ("bridge.exe", a["exe"])):
        with open(os.path.join(L5, name), "wb") as f:
            f.write(data)
        print("записан %s (%d байт, SHA-256 %s)"
              % (name, len(data), hashlib.sha256(data).hexdigest().upper()))
    print("тело: %d байт" % len(a["bin"]))

    # карта меток (для BYTECODE.md)
    text = open(os.path.join(L5, "bridge.brick"), "rb").read()
    labels = labels_of(text)
    pairs = sorted(((v, k) for k, v in labels.items()))
    print("меток: %d; первые:" % len(labels))
    for rva, name in pairs[:8]:
        print("  %s .......... %04X" % (name, rva))

    # полный прогон секции 18 (как в батарее) с локальным check
    class _C:
        def __init__(self):
            self.n = 0
            self.fails = []

        def __call__(self, name, ok_, note_=""):
            self.n += 1
            print("[%s] %s  %s" % ("OK" if ok_ else "FAIL", name, note_))
            if not ok_:
                self.fails.append(name)

    chk = _C()
    lab_t_bridge.run(chk, kpath, kfile, kernel_host)
    print("секция 18: %d проверок, провалов: %d" % (chk.n, len(chk.fails)))
    return 0 if not chk.fails else 1


if __name__ == "__main__":
    sys.exit(main())
