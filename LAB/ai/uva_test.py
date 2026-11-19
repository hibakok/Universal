"""uva_test.py — построитель и dev-тест ассемблера uva.exe (E7.3-2, LAB/ai;
НЕ часть системы UNIVERSAL — частный инструмент ИИ, как kernel_test.py).

Вход:  KERNEL/L3-UVA/uva.wall (+ части uva_self_*.wall + uva.peg).
Выход: 1) артефакты KERNEL/L3-UVA/{uva.b2, uva.brick, uva.exe} — сборка
          конвейером РЕАЛЬНЫХ инструментов под эмуляцией (wall.exe ->
          enc.exe -> brick.exe -> pegen.exe; фикс-пункт закреплён
          в батарее — T-E7-19);
       2) сверка uva.b2 с оракулом WALL (lab_l2.compile_wall);
       3) отчёт [OK]/[FAIL] по корпусу срезов 1-2 (CLI, .mem/halt,
          кодировки F1/halt, отвержение с номерами строк, CODE0,
          сквозной круг uva -> kernel.exe) — прогон секции 15 батареи;
       4) карта меток uva.brick (для BYTECODE.md — импорт label_map)
          и SHA-256 артефактов (для VERIFY.md).
Запуск: python3 LAB/ai/uva_test.py  (из корня репозитория)
"""
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2            # noqa: E402
import lab_splice        # noqa: E402
import lab_t_uva         # noqa: E402

from label_map import labels_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
L3U = os.path.join(KERNEL, "L3-UVA")


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
    print("=== uva_test: сборка ассемблера M3-UVA (E7.3-1) ===")
    ok, a, note = lab_t_uva.build(kpath, kfile, kernel_host)
    print("[OK] сборка" if ok else "[FAIL] сборка", note)
    if not ok:
        return 1
    oracle = lab_l2.compile_wall(
        lab_splice.splice("l3-uva/uva.wall", kernel_host())
        .decode("latin1")).encode()
    print("uva.b2: %d байт; == оракулу WALL: %s"
          % (len(a["b2"]), a["b2"] == oracle))

    for name, data in (("uva.b2", a["b2"]), ("uva.brick", a["brick"]),
                       ("uva.exe", a["exe"])):
        with open(os.path.join(L3U, name), "wb") as f:
            f.write(data)
        print("записан %s (%d байт, SHA-256 %s)"
              % (name, len(data), hashlib.sha256(data).hexdigest().upper()))
    print("тело: %d байт" % len(a["bin"]))

    # карта меток (для BYTECODE.md §2; RVA = смещение + 0x1000 —
    # конвенция kernel_labelmap)
    labels = labels_of(open(os.path.join(L3U, "uva.brick"), "rb").read())
    print("--- карта меток (для BYTECODE.md; RVA = метка + 0x1000) ---")
    for off, name in sorted((v, k) for k, v in labels.items()):
        print("%s .......... %04X" % (name, 0x1000 + off))
    print("всего меток: %d" % len(labels))

    # корпус среза 1 — секция 15 с локальным check
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
    fd, uexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(uexe, "wb") as f:
        f.write(a["exe"])
    try:
        lab_t_uva.run(chk, kpath, kfile, kernel_host)
    finally:
        os.unlink(uexe)
    print("корпус: %d проверок" % chk.n)
    return 0 if not chk.fails else 1


if __name__ == "__main__":
    sys.exit(main())
