"""trace_wall.py — трассировка вызова fail_format/краша wall.exe.

Вход: исходник .wall (аргумент или stdin).
Выход: стек вызовов по меткам перед первым fail_format / крашем.
Запуск: python3 LAB/ai/wall_trace.py [файл.wall] (из любого каталога).
Изменение E6.4d-3/1: починен сломанный с прошлого этапа build_lbl
       (ссылка на несуществующий lab_brick_lbl) — карта меток берётся
       актуальным инструментом label_map.labels_of по артефакту
       wall.brick; CWD-независимость — от __file__.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))
sys.path.insert(0, HERE)
import lab_splice                    # noqa: E402
import lab_run                       # noqa: E402
import lab_win                       # noqa: E402
import lab_cpu                       # noqa: E402
import label_map                     # noqa: E402

U = os.path.join(HERE, "..", "..")
WALL = os.path.join(U, "KERNEL", "L2-WALL", "wall.exe")


def build_lbl():
    brick = open(os.path.join(U, "KERNEL", "L2-WALL", "wall.brick"),
                 "rb").read()
    return label_map.labels_of(brick)


def main():
    src = sys.argv[1].encode() if len(sys.argv) > 1 else \
        sys.stdin.buffer.read()
    lbl = build_lbl()
    fail_rva = 0x1000 + lbl["fail_format"]
    m = lab_win.Machine(WALL, ["t.wall", "t.b2"], {"t.wall": src})
    cpu = m.cpu
    hist = []
    try:
        for i in range(60_000_000):
            hist.append(cpu.rip)
            cpu.step()
    except lab_cpu.ExitProcess as e:
        print("ExitProcess(%s) после %d шагов" % (e.code, len(hist)))
        if e.code != 6:
            return
    except Exception as e:
        print("CRASH после %d шагов: %s" % (len(hist), e))
    # найти вход в fail_format
    lo = 0x140000000 + fail_rva
    hi = lo + 0x80
    for i in range(1, len(hist)):
        if lo <= hist[i] < hi and not (lo <= hist[i - 1] < hi):
            print("вход в fail_format из %X (шаг %d):"
                  % (hist[i - 1] - 0x140000000, i))
            for x in hist[max(0, i - 20):i]:
                off = x - 0x140000000 - 0x1000
                best = max(((o, n) for n, o in lbl.items() if o <= off),
                           default=(0, "?"))
                print("  %X (%s+%X)" % (x - 0x140000000, best[1],
                                        off - best[0]))
            return
    # краш без fail_format — последние адреса
    print("последние адреса:")
    for x in hist[-20:]:
        off = x - 0x140000000 - 0x1000
        best = max(((o, n) for n, o in lbl.items() if o <= off),
                   default=(0, "?"))
        print("  %X (%s+%X)" % (x - 0x140000000, best[1], off - best[0]))


if __name__ == "__main__":
    main()
