"""wall_fix23_build.py — пересборка артефактов M2-WALL после фикса №23 (E7.2-2F, LAB/ai).

Вход:  репозиторий Universal (текущая копия) с ИСПРАВЛЁННЫМ исходником
       KERNEL/L2-WALL/wall_self_pp.wall (pp_pcount: двухсимвольный
       оператор глубины 0 — завершитель скана пар).
Выход: новые KERNEL/L2-WALL/wall.b2, wall.brick, wall.exe (артефакты
       фикс-пункта самосборки); протокол: SHA-256, размеры, шаги.
Функция: фаза build — РЕПОЗИТОРНЫЙ wall.exe (старый, с дефектом №23;
         дефект меняет только ПРИНИМАЕМЫЕ программы — k пар для уже
         принятых совпадает, поэтому выход детерминирован) компилирует
         исправленный wall.wall -> s.b2 (сверка с оракулом lab_l2
         байт-в-байт), затем enc -> brick -> pegen + wall.peg (КОНСТАНТА
         SPEC/11 п.6 — не регенерируется!) -> новый wall.exe.
         Фаза --fixpoint (после подмены артефактов): НОВЫЙ wall.exe
         компилирует wall.wall -> s2.b2; приёмка — s2.b2 == wall.b2
         байт-в-байт (то же делает батарея T-E6-49a на каждом пуше).
Запуск: python3 LAB/ai/wall_fix23_build.py            (фаза build)
        python3 LAB/ai/wall_fix23_build.py --fixpoint (фаза приёмки)
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_brick          # noqa: E402
import lab_l2             # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402
import lab_splice         # noqa: E402
import lab_win            # noqa: E402

UNI = os.path.abspath(os.path.join(HERE, "..", ".."))
K = os.path.join(UNI, "KERNEL", "L2-WALL")


def kernel_host():
    files = {}
    for root, _d, fs in os.walk(os.path.join(UNI, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(UNI, "KERNEL"))
            rel = rel.replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def _sha(b):
    return hashlib.sha256(b).hexdigest().upper()


def build():
    print("=== фаза build: старый wall.exe компилирует исправленный wall.wall ===")
    src = lab_splice.splice("l2-wall/wall.wall", kernel_host())
    print("splice(оракул): %d байт" % len(src))
    m = lab_win.Machine(os.path.join(K, "wall.exe"), ["s.wall", "s.b2"],
                        {"s.wall": src})
    r = m.run(max_steps=2_000_000_000)
    assert r.exit_code == 0, "wall.exe упал: код=%s" % r.exit_code
    b2 = r.files.get("s.b2", b"")
    oracle = lab_l2.compile_wall(src.decode("latin1")).encode()
    assert b2 == oracle, "wall.b2 != оракулу (%d vs %d байт)" % (
        len(b2), len(oracle))
    print("wall.b2: %d байт == оракулу; шагов %d" % (len(b2), m.cpu.steps))

    h = {"s.b2": b2}
    r2 = lab_run.run_kv(os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe"),
                        ["s.b2", "s.brick"], h)
    assert r2.exit_code == 0, "enc.exe: код=%s" % r2.exit_code
    brick = r2.files.get("s.brick", b"")
    print("wall.brick: %d байт; шагов %d" % (len(brick), r2.steps))

    h = {"s.brick": brick}
    r3 = lab_run.run_kv(os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe"),
                        ["s.brick", "s.bin"], h)
    assert r3.exit_code == 0, "brick.exe: код=%s" % r3.exit_code
    body = r3.files.get("s.bin", b"")
    assert body == lab_brick.assemble(brick), "brick.exe != оракулу"
    print("тело: %d байт == оракулу; шагов %d" % (len(body), r3.steps))

    peg = open(os.path.join(K, "wall.peg"), "rb").read()   # КОНСТАНТА п.6
    h = {"s.bin": body, "s.peg": peg}
    r4 = lab_run.run_kv(os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe"),
                        ["s.bin", "s.peg", "s.exe"], h)
    assert r4.exit_code == 0, "pegen.exe: код=%s" % r4.exit_code
    exe = r4.files.get("s.exe", b"")
    assert exe == lab_pegen.wrap(body, peg.decode("latin1")), \
        "pegen.exe != оракулу"
    print("wall.exe: %d байт == оракулу; шагов %d" % (len(exe), r4.steps))

    for name, data in (("wall.b2", b2), ("wall.brick", brick),
                       ("wall.exe", exe)):
        with open(os.path.join(K, name), "wb") as f:
            f.write(data)
        print("записан %s: %d байт, SHA-256 %s" % (name, len(data), _sha(data)))
    return 0


def fixpoint():
    print("=== фаза fixpoint: НОВЫЙ wall.exe компилирует wall.wall ===")
    src = lab_splice.splice("l2-wall/wall.wall", kernel_host())
    m = lab_win.Machine(os.path.join(K, "wall.exe"), ["s.wall", "s.b2"],
                        {"s.wall": src})
    r = m.run(max_steps=2_000_000_000)
    assert r.exit_code == 0, "wall.exe упал: код=%s" % r.exit_code
    s2 = r.files.get("s.b2", b"")
    b2 = open(os.path.join(K, "wall.b2"), "rb").read()
    print("s2.b2: %d байт (шагов %d); wall.b2: %d байт"
          % (len(s2), m.cpu.steps, len(b2)))
    if s2 == b2:
        print("ФИКС-ПУНКТ ПОДТВЕРЖДЁН: s2.b2 == wall.b2 байт-в-байт")
        return 0
    print("ПРОВАЛ: s2.b2 != wall.b2")
    for i in range(min(len(s2), len(b2))):
        if s2[i] != b2[i]:
            print("первое расхождение @ %d: %02X vs %02X"
                  % (i, s2[i], b2[i]))
            break
    return 1


if __name__ == "__main__":
    sys.exit(fixpoint() if "--fixpoint" in sys.argv else build())
