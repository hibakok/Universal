#!/usr/bin/env python3
"""pegen_v2_probe.py — зонди_PORT wrap2 в pegen.exe (срез E9.4-4b-4):
(1) самосборка pegen (круг E4: hexgen+pegen == pegen.exe, эмуляция);
(2) регресс обёртки 9 модулей KERNEL == артефактам (нейтральность v1);
(3) ПОРТ: два чужих крафта (тела из corpus + якорные тексты PEG v2
    FOREIGN_PEG2/FOREIGN2_PEG2) -> pegen.exe == lab_pegen.wrap2
    байт-в-байт (== исходным чужим образам);
(4) ОТКАЗЫ: 19 мутантов якоря + 5 структурных синтетик _synth() +
    v1-текст с !pev2 внутри — pegen.exe код 9 (ERR=FORMAT), оракул
    ValueError;
(5) сценарии v1 (справка/аргументы) — как до порта.
Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))

import lab_atom                            # noqa: E402
import lab_pegen                           # noqa: E402
import lab_run                             # noqa: E402
import lab_t_bridge_corpus as K            # noqa: E402
from lab_t_bridge_peg2 import (            # noqa: E402
    FOREIGN_PEG2, FOREIGN2_PEG2, _mutants, _synth, _target_body)

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L0-PEGEN")
PEGEN_EXE = os.path.join(KERNEL_DIR, "pegen.exe")
HEXGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-HEXGEN", "hexgen.exe")


def main():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-66s %s" % ("OK " if cond else "FAIL", name, note))

    # (1) круг E4: самосборка pegen (эмуляция новых кирпичей v2 в коде)
    h = {"p.hex": open(os.path.join(KERNEL_DIR, "pegen.hex"), "rb").read(),
         "p.peg": open(os.path.join(KERNEL_DIR, "pegen.peg"), "rb").read()}
    body = lab_atom.assemble(h["p.hex"].decode("utf-8"))
    r2 = lab_run.run_kv(HEXGEN_EXE, ["p.hex", "p.bin"], h)
    check("круг E4: hexgen(pegen.hex) == тело (%d Б)" % len(body),
          r2.exit_code == 0 and r2.files.get("p.bin") == body,
          "шагов=%d" % r2.steps)
    h["p.bin"] = body
    r3 = lab_run.run_kv(PEGEN_EXE, ["p.bin", "p.peg", "p.exe"], h)
    check("круг E4: самосборка pegen (pegen(тело,peg) == pegen.exe)",
          r3.exit_code == 0 and r3.files.get("p.exe") ==
          open(PEGEN_EXE, "rb").read(), "шагов=%d" % r3.steps)

    # (2) регресс: обёртка 9 модулей KERNEL == артефактам (нейтральность v1)
    import lab_brick
    import lab_splice
    mods = [("L0-SEED/seed", "hex"), ("L0-SEED2/seed2", "hex"),
            ("L0-HXDUMP/hxdump", "hex"), ("L0-HEXGEN/hexgen", "hex"),
            ("L0-PEGEN/pegen", "hex"), ("L1-BRICK/brick", "brick"),
            ("L1-ENC/enc", "brick"), ("L1-SPLICE/splice", "brick"),
            ("L2-WALL/wall", "brick")]
    bad = []
    for m, kind in mods:
        base = os.path.join(ROOT, "KERNEL", m + ".")
        if kind == "hex":
            body_m = lab_atom.assemble(
                open(base + "hex", "rb").read().decode("utf-8"))
        elif m == "L1-BRICK/brick":
            kh = {}
            kdir = os.path.join(ROOT, "KERNEL", "L1-BRICK")
            for n in ("brick.brick", "brick_p1.brick", "brick_p2.brick",
                      "brick_p3.brick"):
                kh["l1-brick/" + n] = open(os.path.join(kdir, n),
                                           "rb").read()
            body_m = lab_brick.assemble(
                lab_splice.splice("l1-brick/brick.brick", kh))
        else:
            body_m = lab_brick.assemble(open(base + "brick", "rb").read())
        peg_m = open(base + "peg", "rb").read()
        exe_m = open(base + "exe", "rb").read()
        r = lab_run.run_kv(PEGEN_EXE, ["m.bin", "m.peg", "m.exe"],
                           {"m.bin": body_m, "m.peg": peg_m})
        if not (r.exit_code == 0 and r.files.get("m.exe") == exe_m):
            bad.append(m)
    check("регресс: обёртка 9 модулей KERNEL == артефактам", not bad,
          "; ".join(bad))

    # (3) ПОРТ: чужие крафты -> pegen.exe == wrap2 байт-в-байт
    img1, img2 = K.foreign_image(), K.foreign2_image()
    b1, b2 = _target_body(img1), _target_body(img2)
    bad = []
    for name, img, body, text in [
            ("foreign", img1, b1, FOREIGN_PEG2),
            ("foreign2", img2, b2, FOREIGN2_PEG2)]:
        want = lab_pegen.wrap2(body, text)
        if want != img:
            bad.append("%s: оракул wrap2 != образу (якорь)" % name)
        r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": text.encode("utf-8")})
        if not (r.exit_code == 0 and r.files.get("t.exe") == want):
            bad.append("%s: pegen != wrap2 (код=%s, %r)" % (
                name, r.exit_code, r.stdout[:40]))
    check("ПОРТ: 2 чужих крафта — pegen.exe == wrap2 байт-в-байт",
          not bad, "; ".join(bad) if bad else
          "шаги: тела как в T-E9-30")

    # (4) ОТКАЗЫ: мутанты + синтетика + v1-граница
    cases = [(nm, txt, body) for nm, txt, body in _mutants()]
    for nm, txt in [
            ("нет MZ (_synth)", _synth(mz=False)),
            ("нет PE (_synth)", _synth(sig=b"XX\x00\x00")),
            ("таблица вне H", _synth(nsec_field=1, nsec_slots=1)),
            ("raw в заголовках", _synth(raw0=(0x40, 0x10))),
            ("наложение raw", _synth(raw0=(0x100, 0x10),
                                    raw1=(0x108, 0x10), nsec_slots=2)),
            ("!sec на пустой raw", _synth(sec1=True)),
            ("v1-текст с !pev2 внутри", "; v\n!module seed\n!entry 1000\n"
             "!pev2 40\n!idata 1100 28\n!iat 1130 20\n")]:
        cases.append((nm, txt, None))
    bad = []
    for nm, txt, body in cases:
        body = body if body is not None else b"\x90" * 0x40
        r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": txt.encode("utf-8")})
        rejected = r.exit_code == 9 and \
            r.stdout == b"U-L0-PEGEN ERR=FORMAT\r\n"
        try:
            lab_pegen.wrap2(body, txt)
            oracle = "принял"
        except ValueError:
            oracle = "отказ"
        if not rejected:
            bad.append("%s: код=%s %r (оракул %s)" % (
                nm, r.exit_code, r.stdout[:36], oracle))
    check("ОТКАЗЫ: %d мутантов/синтетик — код 9, оракул ValueError" %
          len(cases), not bad, "; ".join(bad[:3]) if bad else "все")

    # (5) сценарии v1 (нейтральность)
    r = lab_run.run_kv(PEGEN_EXE, [], {})
    check("v1: справка без аргументов (код 2)",
          r.stdout == b"U-L0-PEGEN CMDS: PEGEN <IMAGE.BIN> <CTRL.PEG> "
          b"<OUT.EXE>\r\n" and r.exit_code == 2, "код=%s" % r.exit_code)
    r = lab_run.run_kv(PEGEN_EXE, ["no.bin", "no.peg", "o.exe"], {})
    check("v1: несуществующий образ (код 4)",
          r.exit_code == 4 and r.stdout == b"U-L0-PEGEN ERR=OPEN IMAGE\r\n")

    print("\nИТОГ зонда: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
