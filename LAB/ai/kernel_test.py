"""kernel_test.py — построитель и dev-тест ядра kernel.exe (E7.2, LAB/ai;
НЕ часть системы UNIVERSAL — частный инструмент ИИ, как enc_build.py).

Вход:  KERNEL/L3-UNIVM/kernel.wall (+ части kernel_self_*.wall + kernel.peg).
Выход: 1) артефакты KERNEL/L3-UNIVM/{kernel.b2, kernel.brick, kernel.exe}
          — сборка конвейером РЕАЛЬНЫХ инструментов под эмуляцией
          (wall.exe -> enc.exe -> brick.exe -> pegen.exe; фикс-пункт
          воспроизводимости закреплён в батарее — T-E7-09);
       2) отчёт [OK]/[FAIL] по корпусу срезов 1-2 (CLI, контейнер .UP,
          halt-программы, ловушки 1/2, ALU среза 2 — диффтест с
          оракулом lab_vm);
       3) карта меток kernel.brick (для BYTECODE.md — лениво: импорт
          label_map) и SHA-256 артефактов (для VERIFY.md).
Запуск: python3 LAB/ai/kernel_test.py  (из корня репозитория)
"""
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2            # noqa: E402
import lab_splice        # noqa: E402
import lab_t_kernel      # noqa: E402
import lab_vm            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
K3 = os.path.join(KERNEL, "L3-UNIVM")


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
    print("=== kernel_test: сборка ядра M3-UNIVM (E7.2-3) ===")
    ok, a, note = lab_t_kernel.build(kpath, kfile, kernel_host)
    print("[OK] сборка" if ok else "[FAIL] сборка", note)
    if not ok:
        return 1
    oracle = lab_l2.compile_wall(
        lab_splice.splice("l3-univm/kernel.wall", kernel_host())
        .decode("latin1")).encode()
    print("kernel.b2: %d байт; == оракулу WALL: %s"
          % (len(a["b2"]), a["b2"] == oracle))

    # запись артефактов (фикс-пункт: батарея T-E7-09 сверяет их с этой
    # сборкой каждый пуш)
    for name, data in (("kernel.b2", a["b2"]), ("kernel.brick", a["brick"]),
                       ("kernel.exe", a["exe"])):
        with open(os.path.join(K3, name), "wb") as f:
            f.write(data)
        print("записан %s (%d байт, SHA-256 %s)"
              % (name, len(data), hashlib.sha256(data).hexdigest().upper()))
    print("тело: %d байт" % len(a["bin"]))

    # корпус среза 1 — прогон секции 14 с локальным check (без батареи)
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
    fd, kexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(kexe, "wb") as f:
        f.write(a["exe"])
    try:
        lab_t_kernel.run(chk, kpath, kfile, kernel_host)
    finally:
        os.unlink(kexe)
    print("корпус: %d проверок" % chk.n)
    return 0 if not chk.fails else 1


if __name__ == "__main__":
    sys.exit(main())
