"""probe_e92_3b.py — (частное) зонд среза E9.2-3b ДО реализации инструмента:
режим "H" оракула на всех артефактах семейства: статистика (метки/
семантика/H), круг enc->brick->pegen == исходник (байто-точность H-строк
с метками и DD/DQ), устойчивость к краям (импорты на границах target).
"""
import os
import sys

sys.path.insert(0, "LAB/py")

import lab_brick     # noqa: E402
import lab_bridge    # noqa: E402
import lab_enc       # noqa: E402
import lab_pegen     # noqa: E402

ARTS = ["seed", "hxdump", "hexgen", "pegen", "brick", "enc", "splice",
        "wall", "kernel", "uva", "bridge"]
DIRS = {
    "seed": "KERNEL/L0-SEED", "hxdump": "KERNEL/L0-HXDUMP",
    "hexgen": "KERNEL/L0-HEXGEN", "pegen": "KERNEL/L0-PEGEN",
    "brick": "KERNEL/L1-BRICK", "enc": "KERNEL/L1-ENC",
    "splice": "KERNEL/L1-SPLICE", "wall": "KERNEL/L2-WALL",
    "kernel": "KERNEL/L3-UNIVM", "uva": "KERNEL/L3-UVA",
    "bridge": "KERNEL/L5-BRIDGE",
}


def read_exe(name):
    d = os.path.join(DIRS[name], name + ".exe")
    with open(d, "rb") as f:
        return f.read()


def circle_h(name):
    """Режим H: текст -> enc -> brick -> pegen(+peg) == исходный EXE?"""
    data = read_exe(name)
    text, stats = lab_bridge.emit_b2(data, mode="H")
    peg = lab_bridge.emit_peg(data)
    body = lab_brick.assemble(lab_enc.normalize(text).encode("utf-8"))
    exe2 = lab_pegen.wrap(body, peg)
    return data == exe2, stats, text


def main():
    total_lab = 0
    for name in ARTS:
        ok, stats, text = circle_h(name)
        nlines = text.count("\n")
        nl = sum(1 for l in text.splitlines() if l.startswith(":"))
        ndd = sum(1 for l in text.splitlines() if l.startswith("DD"))
        ndq = sum(1 for l in text.splitlines() if l.startswith("DQ"))
        print("%-8s круг=%s M=%d H=%d DZ=%d DB=%d sem=%d lab=%d "
              "строк=%d (меток-строк %d DD %d DQ %d)"
              % (name, "OK" if ok else "FAIL", stats["m"], stats["h"],
                 stats["dz"], stats["db"], stats["sem"], stats["lab"],
                 nlines, nl, ndd, ndq))
        if not ok:
            print("  !! ПРОВАЛ КРУГА:", name)
            return 1
        total_lab += stats["lab"]
    print("все круги режима H байто-точны; всего меток:", total_lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
