"""probe_e92_4.py — зонд E9.2-4 №1 (ДО пересборки инструментов): сборка
bridge.exe ОРАКУЛОМ (splice + compile_wall -> b2; lab_enc/lab_brick/
lab_pegen — чистый Python, без эмуляции конвейера) и прогон под
эмулятором lab_run на артефактах семейства: выход t.peg == оракулу
emit_peg (SPEC/15 п. 8), t.b2 == канону emit_b2 (контроль, что ветвь
G ничего не сломала), факт-строка == оракулу.

Выход: таблица [OK]/[FAIL] по артефактам + сводка шагов эмуляции.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_brick                             # noqa: E402
import lab_bridge                            # noqa: E402
import lab_enc                               # noqa: E402
import lab_l2                                # noqa: E402
import lab_pegen                             # noqa: E402
import lab_run                               # noqa: E402
import lab_splice                            # noqa: E402

ROOT = os.path.join(os.path.dirname(HERE), "..")
KERNEL = os.path.join(ROOT, "KERNEL")

ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]


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


def build_oracle():
    """Быстрая сборка моста оракулами LAB (без эмуляции конвейера)."""
    src = lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
    b2 = lab_l2.compile_wall(src.decode("latin1"))
    body = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
    exe = lab_pegen.wrap(body, kfile("L5-BRIDGE/bridge.peg").decode())
    return b2, exe


def main():
    print("=== probe E9.2-4: сборка моста оракулом ===")
    b2, exe = build_oracle()
    print("b2 %d Б, exe %d Б" % (len(b2.encode()), len(exe)))
    fd, bexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(bexe, "wb") as f:
        f.write(exe)
    fails = 0
    total_steps = 0
    try:
        for m in ARTIFACTS:
            data = kfile("%s.exe" % m)
            want_b2, _st = lab_bridge.emit_b2(data)
            want_peg = lab_bridge.emit_peg(data)
            want_fact = lab_t_bridge_fact(data)
            r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": data})
            total_steps += r.steps
            ok = (r.exit_code == 0
                  and r.files.get("t.b2") == want_b2.encode("utf-8")
                  and r.files.get("t.peg") == want_peg.encode("utf-8")
                  and r.stdout == want_fact)
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails += 1
            print("[%s] %-10s шаги %8d  peg %3d Б  факт %r"
                  % (tag, m.split("/")[-1], r.steps,
                     len(r.files.get("t.peg") or b""),
                     r.stdout[:60]))
            if not ok:
                print("     код=%s peg=%r" % (r.exit_code,
                                              (r.files.get("t.peg")
                                               or b"")[:80]))
                print("     want=%r" % want_peg.encode("utf-8")[:80])
                print("     факт: got=%r want=%r" % (r.stdout, want_fact))
    finally:
        os.unlink(bexe)
    print("итог: %d провалов, шагов %d" % (fails, total_steps))
    return 1 if fails else 0


def lab_t_bridge_fact(data):
    """Ожидаемая факт-строка (копия facts_line lab_t_bridge — без импорта
    секции, чтобы зонд жил автономно)."""
    fam = lab_bridge.parse_family(data)
    pe = fam["pe"]
    _t, st = lab_bridge.emit_b2(data)
    return ("U-L5-BRIDGE MODULE=%s ENTRY=%08X VSIZE=%08X RAW=%08X IMP=%d"
            " INS=%d TARGET=%08X BSS=%08X M=%d H=%d\r\n"
            % (fam["module"], pe["addr_entry_point"], fam["vsize"],
               fam["raw"], len(pe["imports"][0]["funcs"]),
               len(fam["ins"]), fam["target"], fam["bss"],
               st["m"], st["h"])
            ).encode("latin1")


if __name__ == "__main__":
    sys.exit(main())
