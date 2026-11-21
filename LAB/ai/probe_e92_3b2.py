"""probe_e92_3b2.py — (частное) зонд среза E9.2-3b №2: поведение оракула,
когда метка импорта попадает СТРОГО ВНУТРЬ инструкции (d* по hint-RVA).
Сегодняшний _emit_lines: cut внутри сегмента инструкции -> наложение
(метка + данные поверх уже покрытых байтов)? Круг цел?
"""
import sys

sys.path.insert(0, "LAB/py")

import lab_brick     # noqa: E402
import lab_bridge    # noqa: E402
import lab_enc       # noqa: E402
import lab_pegen     # noqa: E402


def main():
    data = open("KERNEL/L0-SEED/seed.exe", "rb").read()
    fam = lab_bridge.parse_family(data)
    imp = fam["pe"]["imports"][0]
    print("seed: oft=%X iat=%X name=%X funcs=%s"
          % (imp["oft_rva"], imp["iat_rva"], imp["name_rva"],
             [(f, hex(h)) for f, h in imp["funcs"]]))
    # INT (oft) файловое смещение записи 0
    int_off = imp["oft_rva"] - 0x1000 + fam["pe"]["sec_raw_ptr"]
    # цель: чётное смещение ВНУТРЬ инструкции (выжившей) — например
    # инструкция @0x2B len 3 (rol eax,4): внутренний офсет 0x2C (RVA 102C)
    patched = bytearray(data)
    patched[int_off:int_off + 8] = (0x102C).to_bytes(8, "little")
    patched = bytes(patched)
    for mode in (None, "H"):
        try:
            text, st = lab_bridge.emit_b2(patched, mode=mode)
            peg = lab_bridge.emit_peg(patched)
            try:
                body = lab_brick.assemble(
                    lab_enc.normalize(text).encode("utf-8"))
                exe2 = lab_pegen.wrap(body, peg)
                res = "круг %s" % ("OK" if exe2 == patched else "БАЙТЫ ≠")
            except Exception as e:                # noqa: BLE001
                res = "АССЕМБЛЕР ОТКАЗ: %s" % e
            lines = [l for l in text.splitlines()
                     if ":d102c" in l or "@002B" in l or "@002C" in l]
            print("mode=%s: %s; lab=%d; строки у 2B/2C: %s"
                  % (mode, res, st["lab"], lines))
        except Exception as e:                    # noqa: BLE001
            print("mode=%s: ОРАКУЛ ОТКАЗ: %r" % (mode, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
