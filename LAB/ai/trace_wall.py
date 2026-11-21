"""trace_wall.py — точная транслитерация WALL-кода ветви L (E9.2-3b)
на Python для поиска логического дефекта: прогон на seed.exe с трассой
значений (impbad/iatoff/hhrv/labels/semrows) против ожиданий оракула.
"""
import sys

sys.path.insert(0, "LAB/py")

import lab_bridge          # noqa: E402

SECT = 0x1000


class Tool:
    """Модель ветви L: глобали + функции 1:1 с bridge_self_l.wall."""

    def __init__(self, data):
        fam = lab_bridge.parse_family(data)
        self.exebuf = data
        self.exelen = len(data)
        self.rawptr = fam["pe"]["sec_raw_ptr"]
        self.rawsize = fam["pe"]["sec_raw_size"]
        self.vsize = fam["vsize"]
        self.target = fam["target"]
        self.inscount = len(fam["ins"])
        self.sdump = sorted(fam["ins"])
        self.lenmap = {a: fam["ins"][a][1] for a in fam["ins"]}
        pe = fam["pe"]
        imp = pe["imports"][0]
        self.thunk = imp["oft_rva"] if imp["oft_rva"] else imp["iat_rva"]
        self.impn = len(imp["funcs"])
        self.labmap = {}
        self.sstate = {}
        self.semstate = {}
        self.knownoff = []
        self.semrows = []
        self.semacc = 0
        self.snlen = 0
        self.noffs = {}
        self.snam = bytearray()
        self.impbad = 0
        self.kn = 0

    def fb(self, o):
        return self.exebuf[o]

    def u32(self, p):
        return int.from_bytes(self.exebuf[p:p + 4], "little")

    def u64(self, p):
        v = int.from_bytes(self.exebuf[p:p + 8], "little")
        return v - (1 << 64) if v >= (1 << 63) else v   # WALL qword

    def rva_off(self, rva):
        return rva - 4096 + self.rawptr

    # ---- imp_hints (K5-L001)
    def imp_hints(self):
        self.hhrv, self.hno, self.hnl = [], [], []
        for k in range(self.impn):
            f = self.thunk + 8 * k - 4096 + self.rawptr
            v = self.u64(f)
            if v < 0:
                v += 16777216 * 256 * 16777216 * 256
            if v >= 16777216 * 256 * 16777216 * 128:
                v -= 16777216 * 256 * 16777216 * 128
            self.hhrv.append(v)
            no = v + 2 - 4096 + self.rawptr
            if no < 0 or no >= self.exelen:
                self.hno.append(-1)
                self.hnl.append(1)
            else:
                self.hno.append(no)
                j = no
                while j < self.exelen:
                    if self.fb(j) == 0:
                        self.hnl.append(j - no)
                        break
                    j += 1
                else:
                    self.hnl.append(self.exelen - 1 - no)

    # ---- imp_offs (K5-L003)
    def imp_offs(self):
        f = self.rva_off(self.u32(272 + 0))          # rd32(exebuf, 272)
        self.iatoff = self.u32(f + 16) - 4096
        self.nameoff = self.u32(f + 12) - 4096
        self.idtoff = self.u32(272) - 4096
        self.intoff = self.thunk - 4096

    # ---- imp_labels (K5-L004)
    def imp_labels(self):
        self.impbad = 0
        if self.iatoff < 0:
            self.impbad = 1
        if self.iatoff + 8 * (self.impn + 1) > self.target:
            self.impbad = 1
        if self.nameoff < 0 or self.nameoff >= self.target:
            self.impbad = 1
        if self.impbad == 0:
            for k in range(self.impn):
                h = self.hhrv[k] - 4096
                if h < 0 or h >= self.target:
                    self.impbad = 1
        print("  imp_offs: iatoff=%X intoff=%X nameoff=%X idtoff=%X "
              "impn=%d target=%X hhrv=%s -> impbad=%d"
              % (self.iatoff, self.intoff, self.nameoff, self.idtoff,
                 self.impn, self.target,
                 [hex(x) for x in self.hhrv], self.impbad))
        if self.impbad != 0:
            return
        for k in range(self.impn):
            self.san_put(k)
            if self.sstate.get(self.iatoff + 8 * k, 0) != 2:
                self.labmap[self.iatoff + 8 * k] = 3
            h = self.hhrv[k] - 4096
            if self.sstate.get(h, 0) != 2:
                if self.labmap.get(h, 0) == 0:
                    self.labmap[h] = 1
                self.knownoff.append(h)
                self.kn += 1
        if self.sstate.get(self.nameoff, 0) != 2:
            if self.labmap.get(self.nameoff, 0) == 0:
                self.labmap[self.nameoff] = 1
            self.knownoff.append(self.nameoff)
            self.kn += 1
        if self.intoff != self.iatoff and \
                self.sstate.get(self.intoff, 0) != 2:
            if self.labmap.get(self.intoff, 0) == 0:
                self.labmap[self.intoff] = 1
        if self.labmap.get(self.intoff, 0) != 0:
            self.knownoff.append(self.intoff)
            self.kn += 1
        if self.labmap.get(self.iatoff, 0) != 0:
            self.knownoff.append(self.iatoff)
            self.kn += 1

    # ---- san_put (K5-L002)
    def san_put(self, k):
        self.noffs[k] = self.snlen
        for ch in b"iat_":
            self.snam.append(ch)
            self.snlen += 1
        cnt = 0
        if self.hno[k] < 0:
            self.snam.append(95)
            self.snlen += 1
            cnt = 1
        else:
            n = self.hnl[k]
            j = 0
            while j < n and cnt < 59:
                c = self.fb(self.hno[k] + j)
                if 65 <= c <= 90:
                    c += 32
                if c < 48 or 57 < c < 97 or c > 122:
                    c = 95
                self.snam.append(c)
                self.snlen += 1
                cnt += 1
                j += 1
        if cnt == 0:
            self.snam.append(102)
            self.snlen += 1
        self.snam.append(0)
        self.snlen += 1

    # ---- build_sstate (K5-L005)
    def build_sstate(self):
        for a in self.sdump:
            self.sstate[a] = 1
            for j in range(a + 1, a + self.lenmap[a]):
                self.sstate[j] = 2

    # ---- sem_add (K5-L006)
    def sem_add(self, off, kind, h):
        for i in range(len(self.semrows)):
            if self.semrows[i][0] == off:
                self.semrows[i] = (off, kind, h)
                return
        self.semrows.append((off, kind, h))

    # ---- dq_base (K5-L007)
    def dq_base(self, base):
        for k in range(self.impn):
            v = self.u64(self.rawptr + base + 8 * k)
            if v < 0:
                v += 16777216 * 256 * 16777216 * 256
            if v != self.hhrv[k]:
                return
            h = self.hhrv[k] - 4096
            if self.labmap.get(h, 0) == 0:
                return
        v = self.u64(self.rawptr + base + 8 * self.impn)
        if v < 0:
            v += 16777216 * 256 * 16777216 * 256
        if v != 0:
            return
        for k in range(self.impn):
            self.sem_add(base + 8 * k, 2, self.hhrv[k] - 4096)
        self.sem_add(base + 8 * self.impn, 2, -1)

    # ---- dd_idt (K5-L008)
    def dd_idt(self):
        if self.idtoff >= 0:
            if self.idtoff + 20 <= self.target:
                self.sem_add(self.idtoff, 1, self.idtoff)

    # ---- sem_filter (K5-L009)
    def sem_filter(self):
        self.semrows.sort(key=lambda t: t[0])
        acc = []
        for (o, kind, h) in self.semrows:
            size = 20 if kind == 1 else 8
            clash = any(self.sstate.get(j, 0) != 0
                        or self.semstate.get(j, 0) != 0
                        for j in range(o, o + size))
            if not clash:
                clash = any(self.labmap.get(j, 0) != 0
                            for j in range(o + 1, o + size))
            if not clash:
                acc.append((o, kind, h))
                self.semstate[o] = 1
                for j in range(o + 1, o + size):
                    self.semstate[j] = 2
        self.semrows = acc
        self.semacc = len(acc)

    # ---- ins_labels (K5-L010) — модель: берём операнды из оракула
    def ins_labels(self):
        fam = lab_bridge.parse_family(self.exebuf)
        for a in self.sdump:
            name, ln, args = fam["ins"][a]
            for op in args:
                if not isinstance(op, tuple):
                    continue
                if op[0] == "t":
                    off = op[1]
                elif op[0] == "m" and op[6] is not None:
                    off = op[6][1]
                else:
                    continue
                if off != -4096 and 0 <= off < self.target:
                    if self.labmap.get(off, 0) == 0:
                        if self.sstate.get(off, 0) == 1 or \
                                self.semstate.get(off, 0) == 1:
                            self.labmap[off] = 2
                        elif self.sstate.get(off, 0) != 2 and \
                                self.semstate.get(off, 0) != 2:
                            self.labmap[off] = 1

    def build_maps(self):
        self.build_sstate()
        self.imp_hints()
        self.imp_offs()
        self.imp_labels()
        if self.impbad == 0:
            self.dd_idt()
            self.dq_base(self.iatoff)
            if self.intoff != self.iatoff:
                self.dq_base(self.intoff)
            self.sem_filter()
        self.ins_labels()


def main():
    data = open("KERNEL/L0-SEED/seed.exe", "rb").read()
    t = Tool(data)
    t.build_maps()
    print("  labmap (импортные):",
          {hex(k): v for k, v in sorted(t.labmap.items())
           if k >= 0x100})
    print("  semrows:", [(hex(o), k, hex(h) if h > 0 else h)
                         for (o, k, h) in t.semrows])
    print("  knownoff:", [hex(x) for x in t.knownoff])
    # сверка с оракулом
    want, st = lab_bridge.emit_b2(data, mode="H")
    print("  оракул: lab=%d sem=%d" % (st["lab"], st["sem"]))
    print("  модель: lab=%d sem=%d" % (len(t.labmap), t.semacc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
