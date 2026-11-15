#!/usr/bin/env python3
"""pegen_build_lim.py — пересборка артефактов M0-PEGEN после подъёма
предела ОБРАЗА 64 КиБ -> 128 КиБ — этап E6.4g-3 (мотив: тело каркаса
wall.wall после среза C превысит 64 КиБ (~71-77 КБ эмиттеров статов) —
круг каркаса упадёт на шаге pegen ERR=BIG IMAGE; найдено при разборе
плана E6.4g-2: предыдущий план поднимал только BIG OUT brick).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL). Изменения
тела pegen (3 слова, ровно 3 байта):
  @00D6 imm32 вместимости imagebuf 0x10001 -> 0x20001 (mov r8d, K0-G041);
  @00F8 imm32 предела образа      0x10000 -> 0x20000 (cmp rax, K0-G041;
         jbe — принят и ровно 0x20000);
  @020F disp32 lea zeropad         +0x10000 (imagebuf 0x10010 -> 0x20010
         в bss — zeropad сместился; единственная ссылка проверена сканом
         всех lea/mov-форм тела).
DBZ/bss: pegen.peg !bss 0x20402 -> 0x30402 (файл не растёт — виртуальные
нули). Скрипт: патчит текст pegen.hex (байты + комментарии), сверяет
побайтовый diff (ровно 3 слова), проверяет hexgen-эквивалентность,
собирает EXE (lab_pegen), прогоняет dev-тесты эмуляцией: круг E4
(самосборка pegen), НОВЫЙ предел (0x10001 и 0x20000 приняты — старый
предел отверг бы уже 0x10001; 0x20001 отвергнут ERR=BIG IMAGE), регресс
обёртки всех модулей KERNEL (9 кругов == артефактам). Повторный запуск
воспроизводит артефакты и печатает SHA-256 (обновить: lab_verify.py,
README, VERIFY.md).
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
LAB = os.path.join(ROOT, "LAB", "py")
sys.path.insert(0, LAB)

import lab_atom                            # noqa: E402
import lab_brick                          # noqa: E402
import lab_pe                             # noqa: E402
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L0-PEGEN")
HEXGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-HEXGEN", "hexgen.exe")
PEGEN_EXE = os.path.join(KERNEL_DIR, "pegen.exe")

BODY = 0xD7A               # файловая длина тела pegen (не меняется)
OLD_BSS = 0x20402
NEW_BSS = 0x30402          # imagebuf 0x10010 -> 0x20010

# слова патча: (смещение в теле, старое, новое, пояснение)
WORDS = [
    (0x0D6, 0x00010001, 0x00020001, "imm32 вместимости imagebuf"),
    (0x0F8, 0x00010000, 0x00020000, "imm32 предела образа BIG IMAGE"),
    (0x20F, 0x00020D69, 0x00030D69, "disp32 lea zeropad (+0x10000)"),
]


def patch_hex_bytes(hex_text, words):
    """Патч @OFFSET-строк: заменить 4 байта слова @off (ATOM v1)."""
    lines = hex_text.split("\n")
    line_at = {}
    for idx, ln in enumerate(lines):
        if ln.startswith("@"):
            line_at[int(ln[1:5], 16)] = idx
    for off, _old, new, _d in words:
        w = new.to_bytes(4, "little")
        starts = [s for s in line_at if s <= off]
        assert starts, "нет строки @%04X" % off
        s = max(starts)
        idx = line_at[s]
        ln = lines[idx]
        toks = ln.split()
        assert toks[0].startswith("@"), ln
        out = [toks[0]]
        pos = s
        k = 1
        while k < len(toks) and not toks[k].startswith(";"):
            assert len(toks[k]) == 2, ln
            if off <= pos < off + 4:
                out.append("%02X" % w[pos - off])
            else:
                out.append(toks[k])
            pos += 1
            k += 1
        assert pos >= off + 4, "слово @%04X выходит за строку" % off
        rest = ln.split(";", 1)
        comment = ";" + rest[1] if len(rest) == 2 else ""
        lines[idx] = " ".join(out) + (" " + comment if comment else "")
    return "\n".join(lines)


def build():
    """Собрать новые артефакты; вернуть статистику."""
    old_hex_text = open(os.path.join(KERNEL_DIR, "pegen.hex"), "r",
                        encoding="latin1").read()
    old_body = lab_atom.assemble(old_hex_text)
    assert len(old_body) == BODY, hex(len(old_body))

    # старые значения на местах патча (или уже новые — повторный запуск)
    words = []
    already = True
    for off, old, new, desc in WORDS:
        cur = int.from_bytes(old_body[off:off + 4], "little")
        if cur == old:
            already = False
            words.append((off, old, new, desc))
        else:
            assert cur == new, "неожиданное слово @%04X: %X" % (off, cur)
    if not already:
        for off, old, new, desc in words:
            print("  @%04X %-36s %08X -> %08X" % (off, desc, old, new))
        nb = bytearray(old_body)
        for off, _o, new, _d in words:
            nb[off:off + 4] = new.to_bytes(4, "little")
        new_body = bytes(nb)
        diff = sum(1 for a, b in zip(old_body, new_body) if a != b)
        assert diff == len(words), "diff != %d байт: %d" % (len(words), diff)
        print("diff старое->новое тело: ровно %d слова (%d байта) — "
              "подтверждено" % (len(words), diff))
        new_hex_text = patch_hex_bytes(old_hex_text, words)

        def _rp(rus_from, rus_to):
            nonlocal new_hex_text
            f = rus_from.encode("utf-8").decode("latin1")
            t = rus_to.encode("utf-8").decode("latin1")
            if f in new_hex_text:
                new_hex_text = new_hex_text.replace(f, t)
            else:
                assert t in new_hex_text, "нет шаблона: " + rus_from

        _rp("mov r8d,0x10001 (вместимость)",
            "mov r8d,0x20001 (вместимость, E6.4g-3)")
        _rp("cmp rax,0x10000 (предел образа)",
            "cmp rax,0x20000 (предел образа 128 КиБ, E6.4g-3)")
        assert lab_atom.assemble(new_hex_text) == new_body, \
            "hexgen(новый pegen.hex) != новое тело"
    else:
        print("pegen.hex уже содержит новое тело (повторный запуск)")
        new_body = old_body
        new_hex_text = old_hex_text

    peg = open(os.path.join(KERNEL_DIR, "pegen.peg"), "r",
               encoding="latin1").read()
    if ("!bss %X" % OLD_BSS) in peg:
        peg = peg.replace("!bss %X" % OLD_BSS, "!bss %X" % NEW_BSS)
    else:
        assert ("!bss %X" % NEW_BSS) in peg, "peg: !bss не найден"
    exe = lab_pegen.wrap(new_body, peg)

    pe = lab_pe.load_bytes(exe) if hasattr(lab_pe, "load_bytes") else None
    vsize = int.from_bytes(exe[0x190:0x194], "little")
    assert vsize == BODY + NEW_BSS, hex(vsize)

    for name, data in [("pegen.hex",
                        new_hex_text.encode("latin1")),
                       ("pegen.peg", peg.encode("latin1")),
                       ("pegen.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)

    return dict(body=len(new_body), bss=NEW_BSS, vsize=vsize,
                exe=len(exe), words=len(words))


# ---------------------------------------------------------------- тесты
def dev_tests():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-64s %s" % ("OK " if cond else "FAIL", name, note))

    # 1. справка без аргументов
    r = lab_run.run_kv(PEGEN_EXE, [], {})
    check("справка",
          r.stdout == b"U-L0-PEGEN CMDS: PEGEN <IMAGE.BIN> <CTRL.PEG> "
          b"<OUT.EXE>\r\n" and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:48], r.exit_code))

    # 2. круг E4: hexgen(pegen.hex) == тело; pegen(тело, peg) == pegen.exe
    h = {"p.hex": open(os.path.join(KERNEL_DIR, "pegen.hex"), "rb").read(),
         "p.peg": open(os.path.join(KERNEL_DIR, "pegen.peg"), "rb").read()}
    body = lab_atom.assemble(h["p.hex"].decode("latin1"))
    r2 = lab_run.run_kv(HEXGEN_EXE, ["p.hex", "p.bin"], h)
    check("круг E4: hexgen(pegen.hex) == тело (%d Б)" % len(body),
          r2.exit_code == 0 and r2.files.get("p.bin") == body,
          "шагов=%d" % r2.steps)
    h["p.bin"] = body
    r3 = lab_run.run_kv(PEGEN_EXE, ["p.bin", "p.peg", "p.exe"], h)
    check("круг E4: самосборка pegen (pegen(тело, peg) == pegen.exe)",
          r3.exit_code == 0 and r3.files.get("p.exe") ==
          open(os.path.join(KERNEL_DIR, "pegen.exe"), "rb").read(),
          "шагов=%d" % r3.steps)

    peg = h["p.peg"]
    peg_s = peg.decode("latin1")

    # 3. НОВЫЙ ПРЕДЕЛ: образ 0x10001 (65537) — принят (старый предел
    #    0x10000 из E4 отверг бы: jbe — принято <= 0x10000)
    img = b"\x41" * 0x10001
    want = lab_pegen.wrap(img, peg_s)
    r = lab_run.run_kv(PEGEN_EXE, ["a.bin", "p.peg", "o.exe"],
                       {"a.bin": img, "p.peg": peg})
    check("предел образа: 0x10001 (65537) принят (старый: 64 КиБ)",
          r.exit_code == 0 and r.files.get("o.exe") == want,
          "exe=%d шагов=%d" % (len(want), r.steps))

    # 4. НОВЫЙ ПРЕДЕЛ: образ 0x20000 (131072) — максимум, принят
    img = b"\x42" * 0x20000
    want = lab_pegen.wrap(img, peg_s)
    r = lab_run.run_kv(PEGEN_EXE, ["a.bin", "p.peg", "o.exe"],
                       {"a.bin": img, "p.peg": peg})
    check("предел образа: 0x20000 (131072) принят — максимум (jbe)",
          r.exit_code == 0 and r.files.get("o.exe") == want,
          "exe=%d шагов=%d" % (len(want), r.steps))

    # 5. НОВЫЙ ПРЕДЕЛ: образ 0x20001 — отвергнут ERR=BIG IMAGE (код 6)
    img = b"\x43" * 0x20001
    r = lab_run.run_kv(PEGEN_EXE, ["a.bin", "p.peg", "o.exe"],
                       {"a.bin": img, "p.peg": peg})
    check("предел образа: 0x20001 (131073) отвергнут (BIG IMAGE)",
          r.exit_code == 6 and
          r.stdout == b"U-L0-PEGEN ERR=BIG IMAGE\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 6. регресс: обёртка всех модулей KERNEL (9 кругов == артефактам)
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
                open(base + "hex", "rb").read().decode("latin1"))
        elif m == "L1-BRICK/brick":
            # корень с !include — склейка splice-оракулом (как в батарее)
            import lab_splice
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

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


def main():
    print("=== pegen_build_lim: сборка M0-PEGEN (E6.4g-3) ===")
    stats = build()
    print("тело %d байт (0x%X); bss 0x%X (был 0x%X); vsize 0x%X; "
          "exe %d байт (не изменился)"
          % (stats["body"], stats["body"], stats["bss"], OLD_BSS,
             stats["vsize"], stats["exe"]))
    print("слов патча %d" % stats["words"])
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "pegen.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 pegen.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
