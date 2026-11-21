"""probe_e92_3c.py — зонд E9.2-3c №1 (ДО инструмента): статистика M/H
по 12 артефактам семейства в режиме канона (mode=None) оракула
_emit_lines: какие формы дают M (мнемоника + вид операндов), какие
дают H и ПОЧЕМУ (нет метки цели / форма не отображается / байты не
воспроизводит enc). Материал для плана кирпичей ветви M моста.

Выход: таблица по артефактам (M/H/DZ/DB/sem/lab) + сводный словарь
форм M (классифицированные) и причин H.
"""
import bisect
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "py"))

import lab_bridge                             # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..")

ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]

BASE_OFF = lab_bridge.BASE_OFF
SECT = lab_bridge.SECT
DZ_MIN = lab_bridge.DZ_MIN


def opkind(a):
    """Короткий вид операнда для классификации формы."""
    if isinstance(a, str):
        return "cl" if a == "cl" else "s?" + a
    if isinstance(a, int):
        return "cnt"
    k = a[0]
    if k == "r":
        return "r%d" % a[2]
    if k == "i":
        return "i%d" % a[2]
    if k == "t":
        return "t"
    if k == "m":
        if a[6] is not None:
            return "mrip"
        parts = []
        if a[1] is not None:
            parts.append("b")
        if a[2] is not None:
            parts.append("x%d" % a[3])
        if a[4]:
            parts.append("d")
        return "m[%s]" % "+".join(parts)
    return "?"


def labels_of(fam):
    """Точная копия вычисления меток/семантики из _emit_lines."""
    ins = fam["ins"]
    limit = fam["target"]
    labels, semantic, _known = lab_bridge._import_map(fam)
    ins_ranges = [(a, a + ins[a][1]) for a in ins]
    sem = {}
    for o in sorted(semantic):
        v = semantic[o]
        size = 4 * len(v[1]) if v[0] == "DD" else 8 * len(v[1])
        clash = any(o < e and s < o + size for s, e in ins_ranges)
        if not clash:
            clash = any(o < e and s < o + size for s, e in
                        ((q, q + (4 if w[0] == "DD" else 8) * len(w[1]))
                         for q, w in sem.items()))
        if not clash:
            clash = any(o < q < o + size for q in labels)
        if not clash:
            sem[o] = v
    starts_sorted = sorted(ins)
    sem_ranges = [(o, o + (4 if v[0] == "DD" else 8) * len(v[1]))
                  for o, v in sem.items()]

    def inside_ins(o):
        i = bisect.bisect_right(starts_sorted, o) - 1
        return i >= 0 and starts_sorted[i] < o < \
            starts_sorted[i] + ins[starts_sorted[i]][1]

    def inside_sem(o):
        return any(s < o < e for s, e in sem_ranges)

    for a in starts_sorted:
        for op in ins[a][2]:
            if not isinstance(op, tuple):
                continue
            if op[0] == "t":
                offs = [op[1]]
            elif op[0] == "m" and op[6] is not None:
                offs = [op[6][1]]
            else:
                continue
            for off in offs:
                if off == BASE_OFF or off in labels:
                    continue
                if off in ins or off in sem:
                    labels[off] = "l%x" % (off + SECT)
                elif 0 <= off < limit and not inside_ins(off) \
                        and not inside_sem(off):
                    labels[off] = "d%x" % (off + SECT)
    return labels


def main():
    mforms = collections.Counter()
    hwhy = collections.Counter()
    print("%-16s %6s %6s %6s %6s %6s %6s" % ("артефакт", "M", "H", "dz",
                                              "db", "sem", "lab"))
    for m in ARTIFACTS:
        path = os.path.join(ROOT, "KERNEL", "%s.exe" % m)
        data = open(path, "rb").read()
        fam = lab_bridge.parse_family(data)
        lines, st = lab_bridge._emit_lines(fam, None)
        print("%-16s %6d %6d %6d %6d %6d %6d"
              % (m.split("/")[-1], st["m"], st["h"], st["dz"], st["db"],
                 st["sem"], st["lab"]))
        labels = labels_of(fam)
        rlabels = {v: k for k, v in labels.items()}
        for a in sorted(fam["ins"]):
            name, ln, args = fam["ins"][a]
            mt = lab_bridge._mtext(name, args, ln, labels)
            if mt and lab_bridge._template(mt[0], mt[1], fam["body"], a,
                                           ln, rlabels):
                fk = (name, tuple(opkind(x) for x in args))
                mforms[fk] += 1
            else:
                if mt is None:
                    hwhy["none:" + name] += 1
                elif not lab_bridge._template(mt[0], mt[1], fam["body"],
                                              a, ln, rlabels):
                    hwhy["bytes:" + name] += 1
    print()
    print("=== ФОРМЫ M (мнемоника, виды операндов -> счёт) ===")
    for (name, kinds), n in sorted(mforms.items(),
                                   key=lambda kv: -kv[1]):
        print("%-8s %-28s %6d" % (name, ",".join(kinds), n))
    print()
    print("=== ПРИЧИНЫ H (none=форма не отображается,"
          " bytes=enc не воспроизводит) ===")
    for k, n in sorted(hwhy.items(), key=lambda kv: -kv[1]):
        print("%-24s %6d" % (k, n))


if __name__ == "__main__":
    main()
