"""dev_t22.py — (частное) прогон Т-E9-22/23 в отрыве от сборки: мост
bridge.exe УЖЕ пересобран в репозитории (build_bridge_only.py /
bridge_test.py фаза 1); здесь только диффтест эмиссии (с E9.2-3c —
КАНОН mode=None: M-строки при точном воспроизведении enc, иначе
H-фолбэк; до 3c был mode="H") на 12 артефактах + синтетике
(synthm/hint-ins/imp0). Хронометраж — решение о группах батареи.
"""
import os
import sys
import time
import tempfile

sys.path.insert(0, "LAB/py")

import lab_bridge       # noqa: E402
import lab_run          # noqa: E402

ARTIFACTS = [("L0-SEED/seed", "seed"), ("L0-SEED2/seed2", "seed2"),
             ("L0-HXDUMP/hxdump", "hxdump"), ("L0-HEXGEN/hexgen", "hexgen"),
             ("L0-PEGEN/pegen", "pegen"), ("L1-BRICK/brick", "brick"),
             ("L1-ENC/enc", "enc"), ("L1-SPLICE/splice", "splice"),
             ("L2-WALL/wall", "wall"), ("L3-UNIVM/kernel", "kernel"),
             ("L3-UVA/uva", "uva"), ("L5-BRIDGE/bridge", "bridge")]


def read(p):
    return open(os.path.join("KERNEL", p + ".exe"), "rb").read()


def main():
    bexe = read("L5-BRIDGE/bridge")
    fd, tmp = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(tmp, "wb") as f:
        f.write(bexe)
    seed = read("L0-SEED/seed")
    fam = lab_bridge.parse_family(seed)
    imp = fam["pe"]["imports"][0]
    intf = imp["oft_rva"] - 0x1000 + fam["pe"]["sec_raw_ptr"]
    mut_hint = bytearray(seed)
    mut_hint[intf:intf + 8] = (0x102C).to_bytes(8, "little")
    mut_hint = bytes(mut_hint)
    mut_imp0 = bytearray(seed)
    mut_imp0[intf:intf + 8] = (0).to_bytes(8, "little")
    mut_imp0 = bytes(mut_imp0)
    synth = lab_pegen_wrap = None
    import lab_pegen                              # noqa: E402
    binbody = open("KERNEL/L5-BRIDGE/bridge.brick", "rb").read()
    # synth как в T-E9-21: тело bridge + craft (берём из bin моста)
    import lab_t_bridge as T                      # noqa: E402
    synth = T._synth_of(bexe) if hasattr(T, "_synth_of") else None
    if synth is None:
        # собственная сборка synthm: как в lab_t_bridge (T-E9-21)
        with open("KERNEL/L5-BRIDGE/bridge.exe", "rb") as f:
            pass
        synth = _make_synth(bexe)
    cases = [(p, read(p)) for p, _n in ARTIFACTS]
    cases.append(("synthm", synth))
    cases.append(("hint-ins", mut_hint))
    cases.append(("imp0", mut_imp0))
    t0 = time.time()
    for name, data in cases:
        t1 = time.time()
        want, st = lab_bridge.emit_b2(data)
        r = lab_run.run_kv(tmp, ["in.exe", "t.b2", "t.peg"],
                           {"in.exe": data})
        got = r.files.get("t.b2")
        ok = r.exit_code == 0 and got == want.encode("utf-8")
        print("%-8s %s  (%.1f c; %d строк; M=%d H=%d lab=%d sem=%d)"
              % (name, "OK" if ok else "FAIL", time.time() - t1,
                 want.count("\n"), st["m"], st["h"], st["lab"],
                 st["sem"]))
        if not ok:
            print("   код %s; размер %s (нужно %s)"
                  % (r.exit_code, len(got or b""), len(want)))
            if got:
                gw = want.encode("utf-8")
                for i in range(min(len(gw), len(got))):
                    if gw[i] != got[i]:
                        print("   первое расхождение @%d:" % i)
                        print("   оракул: %r" % gw[max(0, i - 60):i + 60])
                        print("  工具:    %r" % got[max(0, i - 60):i + 60])
                        break
    print("итого %.1f c" % (time.time() - t0))
    os.unlink(tmp)
    return 0


def _make_synth(bexe):
    """synthm как в T-E9-21 (тело моста[:0x200] + craft)."""
    import lab_brick, lab_pegen
    body = lab_brick.assemble(
        open("KERNEL/L5-BRIDGE/bridge.brick", "rb").read())
    craft = bytes([0x74, 0x02, 0xB8, 0x05, 0x05, 0x05, 0x05,
                   0xC3, 0x00, 0x00])
    return lab_pegen.wrap(
        body[:0x200] + craft,
        "; synth\n!module synthm\n!entry 1200\n"
        "!idata 1000 28\n!iat 1028 48\n")


if __name__ == "__main__":
    sys.exit(main())
