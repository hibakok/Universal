"""probe_heap.py — (частное) диагностика E9.2-3b: прогон bridge.exe на
seed под эмулятором с журналом GlobalAlloc; после выхода — дамп кучи
(labmap/sstate/semstate/semrows/hhrv) и скаляров. Цель: почему метки
импорта не создаются (impbad? imp_hints?).
"""
import os
import sys
import tempfile

sys.path.insert(0, "LAB/py")

import lab_win                       # noqa: E402

NAMES = ["hstdout", "cmdline", "written", "wlen", "exebuf", "exelen",
         "entryrva", "vsize", "rawsize", "rawptr", "modlen", "thunk",
         "dllfile", "impn", "insmap", "lenmap", "pend", "rawlim",
         "psp", "inscount", "maxend", "swcur", "target", "bss",
         "dlen", "dcls", "dtgt", "dpos", "mpos", "mreg", "dname",
         "dcc", "dargc", "da1k", "da2k", "da1r", "da2r", "da1s",
         "da2s", "da1v", "da2v", "damem", "ombase", "omidx",
         "omscale", "omdisp", "omsize", "omrip", "mkind", "mrreg",
         "mrdip", "mripon", "sdump", "outmem", "outbuf", "outcur",
         "iatoff", "intoff", "nameoff", "idtoff", "impbad", "kn",
         "snlen", "semcnt", "semacc", "hhrv", "hno", "hnl", "snam",
         "noffs", "knownoff", "semrows", "labmap", "sstate", "semstate"]


def main():
    allocs = []
    orig = lab_win.Machine._api_globalalloc

    def spy(self, cpu):
        orig(self, cpu)
        allocs.append(((cpu.r[2] + 15) & ~15, cpu.r[0]))

    lab_win.Machine._api_globalalloc = spy

    bexe = open("KERNEL/L5-BRIDGE/bridge.exe", "rb").read()
    fd, tmp = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(tmp, "wb") as f:
        f.write(bexe)
    seed = open("KERNEL/L0-SEED/seed.exe", "rb").read()
    m = lab_win.Machine(tmp, ["in.exe", "t.b2", "t.peg"],
                        {"in.exe": seed})
    r = m.run(max_steps=2_000_000_000)
    lab_win.Machine._api_globalalloc = orig
    print("выход: код=%s шагов=%s" % (r.exit_code, r.steps))
    print("аллокации (размер -> ptr):")
    for size, ptr in allocs:
        print("   %8d -> %X" % (size, ptr))

    def rd(addr, n):
        return m.cpu.read(addr, n)

    def rdb(addr, n):
        buf, off = m.cpu._region(addr, n)
        return bytes(buf[off:off + n])

    sys.path.insert(0, "LAB/ai")
    from label_map import labels_of
    lbl = labels_of(open("KERNEL/L5-BRIDGE/bridge.brick", "rb").read())
    g = {}
    for n in NAMES:
        if n in lbl:
            g[n] = rd(0x140000000 + 0x1000 + lbl[n], 8)
    for n in ("thunk", "impn", "target", "iatoff", "intoff", "nameoff",
              "idtoff", "impbad", "kn", "snlen", "semcnt", "semacc",
              "hhrv", "hno", "hnl", "snam", "noffs", "knownoff",
              "semrows", "labmap", "sstate", "semstate"):
        print("  %-9s = %X" % (n, g[n]))
    print("labmap[0x100..0x1B9]:",
          list(rdb(g["labmap"] + 0x100, 0xBA)))
    print("sstate[0x100..0x1B9]:",
          list(rdb(g["sstate"] + 0x100, 0xBA)))
    print("semstate[0x100..0x1B9]:",
          list(rdb(g["semstate"] + 0x100, 0xBA)))
    print("hhrv[0..2]:", [hex(rd(g["hhrv"] + i * 8, 8))
                           for i in range(3)])
    print("hno[0..2]:", [hex(rd(g["hno"] + i * 8, 8))
                         for i in range(3)])
    print("hnl[0..2]:", [rd(g["hnl"] + i * 8, 8) for i in range(3)])
    print("semrows[0..8]:", [hex(rd(g["semrows"] + i * 8, 8))
                             for i in range(min(27, 3 * g["semcnt"]))])
    print("snam байты:", list(rdb(g["snam"], min(96, g["snlen"]))))
    os.unlink(tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
