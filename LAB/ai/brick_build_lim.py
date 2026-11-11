#!/usr/bin/env python3
"""brick_build_lim.py — пересборка артефактов M1-BRICK после роста пределов
исходника 128 -> 256 КиБ, таблицы меток 512 -> 1024 и буферов bss
(labtab 0x2000 -> 0x4000, filebuf 0x20008 -> 0x40008, imagebuf
0x20010 -> 0x40010) — этап E6.4e-3.

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL): склеивает
разрез KERNEL/L1-BRICK/brick.brick (splice-оракул), собирает тело
оракулом lab_brick (с новыми пределами), сверяет побайтовый diff со
СТАРЫМ телом (ожидание: ровно 8 слов — imm32 x3 и disp32 x5, смещения
слов вычисляются проходом по исходнику), патчит текст brick.hex (байты
+ комментарии), проверяет hexgen-эквивалентность, собирает EXE
(lab_pegen) и прогоняет dev-тесты эмуляцией: круги E5 (самохостинг +
pegen), якоря оракула, ошибки, НОВЫЕ пределы (0x20020 + 600 меток
принято / 0x40000 отвергнуто), dev-only максимумы (0x3FFFF, 1025-я
метка), регресс wall.brick и enc.brick. Повторный запуск воспроизводит
артефакты и печатает SHA-256 (обновить: lab_verify.py, README,
VERIFY.md).
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
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L1-BRICK")
SPLICE_EXE = os.path.join(ROOT, "KERNEL", "L1-SPLICE", "splice.exe")
PEGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-PEGEN", "pegen.exe")
HEXGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-HEXGEN", "hexgen.exe")

SRC_CAP = 0x40000          # новый предел исходника (E6.4e-3)
MAX_LABELS = 1024          # новый предел меток (E6.4e-3)

# цели патча: (токены H-строки, смещение слова внутри инструкции)
TARGETS = [
    ("41 B8 00 00 04 00", 2, "imm32 вместимости 0x40000"),
    ("48 3D 00 00 04 00", 2, "imm32 BIG SRC 0x40000"),
    ("41 81 FB 00 04 00 00", 3, "imm32 предела меток 0x400"),
    ("48 8D 15 $filebuf", 3, "disp32 filebuf (+0x2000)"),
    ("48 8D 05 $filebuf", 3, "disp32 filebuf (+0x2000)"),
    ("48 8D 35 $filebuf", 3, "disp32 filebuf (+0x2000)"),
    ("48 8D 15 $imagebuf", 3, "disp32 imagebuf (+0x22000)"),
    ("4C 8D 15 $imagebuf", 3, "disp32 imagebuf (+0x22000)"),
]


def kernel_host():
    files = {}
    for root, _d, fs in os.walk(os.path.join(ROOT, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(ROOT, "KERNEL")) \
                .replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def flat_source():
    """Склейка brick.brick (корень + 3 части) оракулом splice."""
    host = {"l1-brick/brick.brick":
            open(os.path.join(KERNEL_DIR, "brick.brick"), "rb").read()}
    for name in ("brick_p1.brick", "brick_p2.brick", "brick_p3.brick"):
        host["l1-brick/" + name] = open(os.path.join(KERNEL_DIR, name),
                                        "rb").read()
    return lab_splice.splice("l1-brick/brick.brick", host)


def walk_lines(flat):
    """Проход пасса 1: [(смещение, [токены])] для строк-директив."""
    out, cur = [], 0
    for line in flat.split("\n"):
        st = line.strip()
        if not st or st.startswith(";") or st.startswith(":"):
            continue
        toks = st.split()
        body = []
        for t in toks[1:]:
            if t.startswith(";"):
                break
            body.append(t)
        d = toks[0]
        out.append((cur, [d] + body))
        if d == "H":
            for t in body:
                if t.startswith("$"):
                    cur += 1 if t.endswith(":1") else 4
                else:
                    cur += 1
        elif d == "DB":
            cur += len(body)
        elif d in ("DZ", "DBZ"):
            cur += int(body[0], 16)
        elif d == "DD":
            cur += 4 * len(body)
        elif d == "DQ":
            cur += 8 * len(body)
        else:
            raise ValueError("bad directive: " + st)
    return out, cur


def layout(flat):
    """Карта меток/длин (пасс 1 SPEC/08)."""
    labels, cur, filelen = {}, 0, None
    for line in flat.split("\n"):
        st = line.strip()
        if not st or st.startswith(";"):
            continue
        if st.startswith(":"):
            labels[st[1:].split(";")[0].strip()] = cur
            continue
        toks = st.split()
        body = []
        for t in toks[1:]:
            if t.startswith(";"):
                break
            body.append(t)
        d = toks[0]
        if d == "H":
            for t in body:
                if t.startswith("$"):
                    cur += 1 if t.endswith(":1") else 4
                else:
                    cur += 1
        elif d == "DB":
            cur += len(body)
        elif d == "DZ":
            cur += int(body[0], 16)
        elif d == "DBZ":
            if filelen is None:
                filelen = cur
            cur += int(body[0], 16)
        elif d == "DD":
            cur += 4 * len(body)
        elif d == "DQ":
            cur += 8 * len(body)
    return labels, filelen, cur


def patch_words(body, words):
    """Применить {(смещение): 4 байта} к копии тела."""
    b = bytearray(body)
    for off, w in words.items():
        assert len(w) == 4
        b[off:off + 4] = w
    return bytes(b)


def build():
    """Собрать новые артефакты; вернуть статистику."""
    flat = flat_source().decode("utf-8")
    assert len(flat.encode("utf-8")) < SRC_CAP, "brick.brick >= 256 КиБ"
    labels, filelen, vsize = layout(flat)
    assert filelen is not None, "нет DBZ — нет bss"
    bss = vsize - filelen
    new_body = lab_brick.assemble(flat.encode("utf-8"))
    assert len(new_body) == filelen, (len(new_body), filelen)

    old_hex_text = open(os.path.join(KERNEL_DIR, "brick.hex"),
                        "r", encoding="latin1").read()
    old_body = lab_atom.assemble(old_hex_text)

    # смещения 8 слов-целей по проходу исходника; идемпотентность:
    # если brick.hex уже содержит новое тело — слов для патча нет
    lines, _ = walk_lines(flat)
    words = {}
    if old_body != new_body:
        for tokens, woff, desc in TARGETS:
            want = ["H"] + tokens.split()
            hits = [off for off, tk in lines if tk == want]
            assert len(hits) == 1, (tokens, hits)
            off = hits[0] + woff
            old_w = old_body[off:off + 4]
            if "imm32" in desc and "0x40000" in desc:
                new_w = (0x40000).to_bytes(4, "little")
            elif "imm32" in desc:
                new_w = (0x400).to_bytes(4, "little")
            elif "filebuf" in desc:
                new_w = (int.from_bytes(old_w, "little") +
                         0x2000).to_bytes(4, "little")
            else:
                new_w = (int.from_bytes(old_w, "little") +
                         0x22000).to_bytes(4, "little")
            words[off] = new_w
            print("  @%04X %-32s %s -> %s" % (
                off, desc,
                " ".join("%02X" % c for c in old_w),
                " ".join("%02X" % c for c in new_w)))

        # ожидание: старое тело + 8 слов == новое тело (и ничего больше)
        expect_body = patch_words(old_body, words)
        assert expect_body == new_body, "diff != ожидаемых 8 слов"
        print("diff старое->новое тело: ровно %d слов — подтверждено"
              % len(words))
    else:
        print("brick.hex уже содержит новое тело (повторный запуск)")

    # патч текста brick.hex (байты слов) + комментарии (файл читается
    # в latin1: кириллические паттерны кодируем utf-8 -> latin1)
    new_hex_text = patch_hex_text(old_hex_text, words)

    def _rp(rus_from, rus_to):
        nonlocal new_hex_text
        f = rus_from.encode("utf-8").decode("latin1")
        t = rus_to.encode("utf-8").decode("latin1")
        if f in new_hex_text:
            new_hex_text = new_hex_text.replace(f, t)
        else:
            assert t in new_hex_text, "нет шаблона: " + rus_from

    _rp("Виртуальные нули (bss, 0x42178 байт)",
        "Виртуальные нули (bss, 0x%X байт)" % bss)
    _rp("lea rdx,[rip+filebuf] (буфер 128 КиБ)",
        "lea rdx,[rip+filebuf] (буфер 256 КиБ)")
    _rp("mov r8d,0x20000 (вместимость)",
        "mov r8d,0x40000 (вместимость)")
    _rp("cmp rax,0x20000 (сентинелу нужен запас)",
        "cmp rax,0x40000 (сентинелу нужен запас)")
    _rp("cmp r11d,0x200 (предел 512)",
        "cmp r11d,0x400 (предел 1024)")
    _rp("исходник больше 128 КиБ", "исходник больше 256 КиБ")
    assert lab_atom.assemble(new_hex_text) == new_body, \
        "hexgen(новый brick.hex) != новое тело"

    # peg: bss из раскладки; idata/iat не изменились (до bss)
    idt_rva = labels["idt"] + 0x1000
    iat_rva = labels["iat"] + 0x1000
    peg = ("; UNIVERSAL / PEG v1 / слой L1 / модуль M1-BRICK\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg>"
           " <out.exe>\n"
           "!module brick\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n" % (idt_rva, iat_rva, bss))
    exe = lab_pegen.wrap(new_body, peg)

    for name, data in [("brick.hex",
                        new_hex_text.encode("latin1")),
                       ("brick.peg", peg.encode()),
                       ("brick.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)

    return dict(labels=labels, filelen=filelen, vsize=vsize, bss=bss,
                idt=idt_rva, iat=iat_rva, body=len(new_body),
                exe=len(exe), src=len(flat.encode("utf-8")),
                words=len(words))


def patch_hex_text(hex_text, words):
    """Патч @OFFSET-строк brick.hex: заменить 4 байта слова @off."""
    lines = hex_text.split("\n")
    line_at = {}
    for idx, ln in enumerate(lines):
        if ln.startswith("@"):
            line_at[int(ln[1:5], 16)] = idx
    for off in sorted(words):
        w = words[off]
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
            assert len(toks[k]) == 2, ln      # в .hex только байты
            if s <= pos < s + len(toks) - 1 and off <= pos < off + 4:
                pass                          # заменяется ниже по позиции
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


# ---------------------------------------------------------------- тесты
def dev_tests():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-58s %s" % ("OK " if cond else "FAIL", name, note))

    exe = os.path.join(KERNEL_DIR, "brick.exe")

    def run_br(args, host):
        return lab_run.run_kv(exe, args, host)

    # 1. справка без аргументов
    r = run_br([], {})
    check("справка",
          r.stdout == b"U-L1-BRICK CMDS: BRICK <SRC.BRICK> <OUT.BIN>\r\n"
          and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:48], r.exit_code))

    # 2. якоря семантики SPEC/08 (регресс батареи)
    bad = []
    for name, src in [
        ("слот rip $base", b":e\nH 48 8D 1D $base\n"),
        ("rel8", b":a\nH 74 $b:1\nH 90\n:b\nH CC\n"),
        ("DD/DQ RVA", b":x\nDB 41\n:y\nDQ $x\nDD $y 20\n"),
        ("DBZ-виртуальность", b"DZ 3\n:far\nDBZ 10\nH 90\n")]:
        try:
            o = lab_brick.assemble(src)
            r = run_br(["t.brick", "t.bin"], {"t.brick": src})
            if not (r.exit_code == 0 and r.files.get("t.bin") == o):
                bad.append(name)
        except lab_brick.BrickError as e:
            bad.append(name + ": " + str(e))
    check("якоря оракула (4, регресс)", not bad, "; ".join(bad))

    # 3. ошибки формата (регресс T-M6-12..15)
    bad = []
    for name, src, want in [
        ("строчная цифра", b"H 48 8d\n", 1),
        ("дубликат метки", b":a\n:a\n", 2),
        ("неопределённая метка", b"H 74 $zz:1\n", 1),
        ("слот не в конце", b"H 48 $x 90\n", 1)]:
        r = run_br(["t.brick", "t.bin"], {"t.brick": src})
        want_out = ("U-L1-BRICK ERR=FORMAT AT=%04X\r\n" % want).encode()
        if not (r.stdout == want_out and r.exit_code == 6):
            bad.append(name)
    check("ошибки формата (4, регресс)", not bad, "; ".join(bad))

    # 4. круг E5: brick(splice(brick.brick)) == hexgen(brick.hex)
    kh = kernel_host()
    r0 = lab_run.run_kv(SPLICE_EXE, ["l1-brick/brick.brick",
                                     "t_flat.brick"], kh)
    h = {"b.brick": r0.files.get("t_flat.brick", b""),
         "b.hex": open(os.path.join(KERNEL_DIR, "brick.hex"), "rb").read(),
         "b.peg": open(os.path.join(KERNEL_DIR, "brick.peg"), "rb").read()}
    r1 = run_br(["b.brick", "t_self.bin"], h)
    r2 = lab_run.run_kv(HEXGEN_EXE, ["b.hex", "t_body.bin"], h)
    self_bin = r1.files.get("t_self.bin", b"")
    body_bin = r2.files.get("t_body.bin", b"")
    check("DoD E5: brick(splice(brick.brick)) == hexgen(brick.hex)",
          self_bin == body_bin and r1.exit_code == 0 and
          r0.exit_code == 0 and len(self_bin) == 0xB98,
          "%d байт, шагов=%d+%d" % (len(self_bin), r0.steps, r1.steps))

    # 5. круг E5: pegen(brick(brick.brick)) == brick.exe
    h["t_self.bin"] = self_bin
    r3 = lab_run.run_kv(PEGEN_EXE, ["t_self.bin", "b.peg", "t.exe"], h)
    check("DoD E5: pegen-круг brick.exe",
          r3.files.get("t.exe") ==
          open(os.path.join(KERNEL_DIR, "brick.exe"), "rb").read(),
          "шагов=%d" % r3.steps)

    # 6. НОВЫЙ ПРЕДЕЛ: исходник 0x20020 байт с 600 метками — принят
    #    (старые пределы: BIG SRC при 0x20000 и метки 512 — оба
    #    отвергли бы этот исходник)
    src = bytearray()
    for i in range(600):
        src += (":l%d\n" % i).encode()
    n_fill = (0x20020 - len(src)) // 5
    src += b"H 90\n" * n_fill
    assert 0x20001 <= len(src) < SRC_CAP
    want = lab_brick.assemble(bytes(src))
    assert want == b"\x90" * n_fill
    r = run_br(["t.brick", "t.bin"], {"t.brick": bytes(src)})
    check("предел: исходник %d Б с %d метками принят (старые: 128К/512)"
          % (len(src), 600),
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 7. НОВЫЙ ПРЕДЕЛ: исходник 0x40000 — отвергнут ERR=BIG SRC (код 7)
    line256 = b";" + b"A" * (0x40000 - 2) + b"\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": line256})
    check("предел: исходник 0x40000 отвергнут (BIG SRC)",
          r.exit_code == 7 and
          r.stdout == b"U-L1-BRICK ERR=BIG SRC\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 8. dev-only максимум: исходник 0x3FFFF — принят
    line_max = b";" + b"B" * (0x3FFFF - 2) + b"\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": line_max})
    check("предел: максимум 0x3FFFF принят (dev-only)",
          r.exit_code == 0 and r.files.get("t.bin") == b"",
          "шагов=%d" % r.steps)

    # 9. dev-only: 1024-я запись labtab — отвергнута (FORMAT; предел
    #    1024 записи ВКЛ. base -> максимум 1023 пользовательских метки)
    src = b""
    for i in range(1024):
        src += (":m%d\n" % i).encode()
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел: 1024-я запись labtab отвергнута (dev-only)",
          r.exit_code == 6 and
          r.stdout == b"U-L1-BRICK ERR=FORMAT AT=0400\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:40]))

    # 10. регресс: крупнейший потребитель — wall.brick (507 меток)
    wall_src = kh["l2-wall/wall.brick"]
    want = lab_brick.assemble(wall_src)
    r = run_br(["t.brick", "t.bin"], {"t.brick": wall_src})
    check("регресс: wall.brick (%d Б, 507 меток) == оракулу"
          % len(wall_src),
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 11. регресс: enc.brick == оракулу (второй потребитель)
    enc_src = kh["l1-enc/enc.brick"]
    want = lab_brick.assemble(enc_src)
    r = run_br(["t.brick", "t.bin"], {"t.brick": enc_src})
    check("регресс: enc.brick (%d Б) == оракулу" % len(enc_src),
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


def main():
    print("=== brick_build_lim: сборка M1-BRICK (E6.4e-3) ===")
    stats = build()
    print("тело %d байт (0x%X); bss 0x%X; vsize 0x%X; exe %d байт"
          % (stats["body"], stats["body"], stats["bss"], stats["vsize"],
             stats["exe"]))
    print("idata RVA 0x%X; iat RVA 0x%X; слов патча %d"
          % (stats["idt"], stats["iat"], stats["words"]))
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "brick.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 brick.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
