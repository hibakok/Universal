#!/usr/bin/env python3
"""brick_build_lim3.py — пересборка артефактов M1-BRICK после подъёма
предела ТЕЛА 64 КиБ -> 128 КиБ — этап E6.4g-2 (мотив: тело каркаса
wall.wall после среза B 60967/64К = 93%, срез C добавит ~10-15 КБ —
без подъёма круг каркаса упадёт ERR=BIG OUT).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL): склеивает
разрез KERNEL/L1-BRICK/brick.brick (splice-оракул), собирает тело
оракулом lab_brick, сверяет побайтовый diff со СТАРЫМ телом (ожидание:
ровно 1 слово — imm32 BIG OUT 0x10000 -> 0x20000 в K1-G001; imagebuf
0x100010 НЕ меняется — 1 МиБ покрывает тела до 128 КиБ с запасом 8x,
его размер привязан к пределу ИСХОДНИКА, а не тела), патчит текст
brick.hex (байты + комментарии), проверяет hexgen-эквивалентность,
собирает EXE (lab_pegen, peg без изменений — bss не тронут) и прогоняет
dev-тесты эмуляцией: круги E5 (самохостинг + pegen), якоря оракула,
ошибки, НОВЫЙ предел тела (0x10000 и 0x1FFFF приняты — старый предел
отверг бы уже 0x10000; 0x20000 отвергнут ERR=BIG OUT), регресс
wall.brick/enc.brick/.brick каркаса. Повторный запуск воспроизводит
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
WALL_EXE = os.path.join(ROOT, "KERNEL", "L2-WALL", "wall.exe")
ENC_EXE = os.path.join(ROOT, "KERNEL", "L1-ENC", "enc.exe")

SRC_CAP = 0x100000         # предел исходника (E6.4g-1, не меняется)

# цель патча: (токены НОВОЙ H-строки, смещение слова в инструкции)
TARGETS = [
    ("3D 00 00 02 00", 1, "imm32 BIG OUT 0x20000 (предел тела)"),
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
        else:
            raise ValueError("bad directive: " + st)
    return labels, filelen, cur


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
    return out, cur


def patch_words(body, words):
    b = bytearray(body)
    for off, w in words.items():
        assert len(w) == 4
        b[off:off + 4] = w
    return bytes(b)


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
    flat = flat_source().decode("utf-8")
    assert len(flat.encode("utf-8")) < SRC_CAP, "brick.brick >= 1 МиБ"
    labels, filelen, vsize = layout(flat)
    assert filelen is not None, "нет DBZ — нет bss"
    bss = vsize - filelen
    new_body = lab_brick.assemble(flat.encode("utf-8"))
    assert len(new_body) == filelen, (len(new_body), filelen)

    old_hex_text = open(os.path.join(KERNEL_DIR, "brick.hex"),
                        "r", encoding="latin1").read()
    old_body = lab_atom.assemble(old_hex_text)

    lines, _ = walk_lines(flat)
    words = {}
    if old_body != new_body:
        for tokens, woff, desc in TARGETS:
            want = ["H"] + tokens.split()
            hits = [off for off, tk in lines if tk == want]
            assert len(hits) == 1, (tokens, hits)
            off = hits[0] + woff
            old_w = old_body[off:off + 4]
            assert old_w == (0x10000).to_bytes(4, "little"), \
                "старое слово не 0x10000: %s" % desc
            new_w = (0x20000).to_bytes(4, "little")
            words[off] = new_w
            print("  @%04X %-36s %s -> %s" % (
                off, desc,
                " ".join("%02X" % c for c in old_w),
                " ".join("%02X" % c for c in new_w)))
        expect_body = patch_words(old_body, words)
        assert expect_body == new_body, "diff != ожидаемого 1 слова"
        print("diff старое->новое тело: ровно %d слово — подтверждено"
              % len(words))
    else:
        print("brick.hex уже содержит новое тело (повторный запуск)")

    new_hex_text = patch_hex_text(old_hex_text, words)

    def _rp(rus_from, rus_to):
        nonlocal new_hex_text
        f = rus_from.encode("utf-8").decode("latin1")
        t = rus_to.encode("utf-8").decode("latin1")
        if f in new_hex_text:
            new_hex_text = new_hex_text.replace(f, t)
        else:
            assert t in new_hex_text, "нет шаблона: " + rus_from

    _rp("cmp eax,0x10000 (предел imagebuf)",
        "cmp eax,0x20000 (предел тела 128 КиБ, E6.4g-2)")
    assert lab_atom.assemble(new_hex_text) == new_body, \
        "hexgen(новый brick.hex) != новое тело"

    # peg НЕ меняется: bss/imagebuf не тронуты (образец E6.4g-1 не нужен)
    peg = open(os.path.join(KERNEL_DIR, "brick.peg"), "r",
               encoding="latin1").read()
    assert ("!bss %X" % bss) in peg, "peg: !bss %X не найден" % bss
    exe = lab_pegen.wrap(new_body, peg)

    for name, data in [("brick.hex",
                        new_hex_text.encode("latin1")),
                       ("brick.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)

    return dict(labels=labels, filelen=filelen, vsize=vsize, bss=bss,
                body=len(new_body), exe=len(exe),
                src=len(flat.encode("utf-8")), words=len(words))


# ---------------------------------------------------------------- тесты
def dev_tests():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-64s %s" % ("OK " if cond else "FAIL", name, note))

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

    # 6. НОВЫЙ ПРЕДЕЛ ТЕЛА: 0x10000 байт — принят (старый предел
    #    0x10000 из E5 отверг бы: jb — принято < 0x10000)
    src = b"DZ 10000\n"
    want = lab_brick.assemble(src)
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел тела: 0x10000 (65536) принят (старый: 64 КиБ)",
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 7. НОВЫЙ ПРЕДЕЛ ТЕЛА: 0x1FFFF — максимум, принят
    src = b"DZ 1FFFF\n"
    want = lab_brick.assemble(src)
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел тела: 0x1FFFF (131071) принят — максимум",
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 8. НОВЫЙ ПРЕДЕЛ ТЕЛА: 0x20000 — отвергнут ERR=BIG OUT (код 10)
    src = b"DZ 20000\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел тела: 0x20000 (131072) отвергнут (BIG OUT)",
          r.exit_code == 10 and
          r.stdout == b"U-L1-BRICK ERR=BIG OUT\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 9. регресс: крупнейший потребитель — .brick каркаса wall.wall
    #    (мотив подъёма: тело 60967/64К = 93% после среза B)
    src_flat = lab_splice.splice("l2-wall/wall.wall", kh)
    rw = lab_run.run_kv(WALL_EXE, ["s.wall", "s.b2"], {"s.wall": src_flat})
    assert rw.exit_code == 0, rw.stdout
    h2 = {"s.b2": rw.files["s.b2"]}
    re_ = lab_run.run_kv(ENC_EXE, ["s.b2", "s.brick"], h2)
    wall_self = re_.files.get("s.brick", b"")
    want = lab_brick.assemble(wall_self)
    r = run_br(["t.brick", "t.bin"], {"t.brick": wall_self})
    nlabs = sum(1 for l in wall_self.decode("latin-1").split("\n")
                if l.startswith(":"))
    check("регресс: .brick каркаса (%d Б, %d меток) == оракулу; тело %d"
          % (len(wall_self), nlabs, len(want)),
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "шагов=%d" % r.steps)

    # 10. регресс: wall.brick и enc.brick == оракулу
    for rel, note in [("l2-wall/wall.brick", "wall.brick"),
                      ("l1-enc/enc.brick", "enc.brick")]:
        src_b = kh[rel]
        want = lab_brick.assemble(src_b)
        r = run_br(["t.brick", "t.bin"], {"t.brick": src_b})
        check("регресс: %s (%d Б) == оракулу" % (note, len(src_b)),
              r.exit_code == 0 and r.files.get("t.bin") == want,
              "шагов=%d" % r.steps)

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


def main():
    print("=== brick_build_lim3: сборка M1-BRICK (E6.4g-2) ===")
    stats = build()
    print("тело %d байт (0x%X); bss 0x%X (не изменился); exe %d байт"
          % (stats["body"], stats["body"], stats["bss"], stats["exe"]))
    print("слов патча %d; исходник %d Б" % (stats["words"], stats["src"]))
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "brick.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 brick.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
