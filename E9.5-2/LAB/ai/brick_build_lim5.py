#!/usr/bin/env python3
"""brick_build_lim5.py — пересборка артефактов M1-BRICK после подъёма
пределов этапа E9.5-2 (синхронизация конвейера под тела 1 МиБ):

- ТЕЛО 128 КиБ -> 1 МиБ (cmp eax 0x20000 -> 0x100000; jb -> jbe —
  принят и ровно 0x100000, синхронно pegen (E6.4g-3) и мосту
  BIG BODY (E9.5-1b): bridge 1 МиБ == brick 1 МиБ == pegen 1 МиБ);
- ИСХОДНИК 2 МиБ -> 17 МиБ (0x1100000; mov r8d/cmp rax + DBZ
  filebuf 0x200008 -> 0x1100008) — покрывает ЛЮБОЙ допустимый выход
  enc (вход enc < 8 МиБ => выход <= 23/11 x 8 МиБ + 1 = 0x10BA2EA):
  круг bridge -> enc -> brick -> pegen не разрывается на текстах;
- МЕТКИ 2048 -> 131072 (cmp r11d 0x800 -> 0x20000; DBZ labtab
  0x8000 -> 0x200000) + НОВЫЙ ЯВНЫЙ отказ ERR=BIG LABELS (код 11,
  errtab[8] + строка; было молчаливое ERR=FORMAT — урок E9.5-1b:
  неявный предел хуже явного отказа);
- imagebuf 0x200010 НЕ меняется (тела 1 МиБ с запасом 2x).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL): читает
разрез KERNEL/L1-BRICK/brick.brick (splice-оракул), собирает тело
оракулом lab_brick (предел меток синхронизирован: 131072/BIG LABELS,
зеркало imagebuf 0x200010), сверяет ожидаемые строки констант,
регенерирует текст brick.hex (прямое соответствие строк исходник ->
строки @-листинга), собирает EXE (lab_pegen, peg с новым !bss) и
прогоняет dev-тесты эмуляцией: круги E5 (самохостинг + pegen), якоря
оракула, ошибки, НОВЫЕ пределы (тело 0x100000 — jbe-край; 0x100001
отвергнуто; метки 2049 — старый предел отверг бы; исходник 0x200020
принят dev-only; 0x1100000 отвергнуто), ФОРМ-проверки imm32 BIG
LABELS/тела/исходника (пины байтов тела — дёшево вместо
O(n^2)-прогона 131073 меток), регресс enc.brick/wall.brick.
Повторный запуск воспроизводит артефакты и печатает SHA-256
(обновить: lab_verify.py, README, VERIFY.md).
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
LAB = os.path.join(ROOT, "LAB", "py")
sys.path.insert(0, LAB)

import lab_atom                            # noqa: E402
import lab_brick                           # noqa: E402
import lab_pegen                           # noqa: E402
import lab_run                             # noqa: E402
import lab_splice                          # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L1-BRICK")
SPLICE_EXE = os.path.join(ROOT, "KERNEL", "L1-SPLICE", "splice.exe")
PEGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-PEGEN", "pegen.exe")
HEXGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-HEXGEN", "hexgen.exe")
WALL_DIR = os.path.join(ROOT, "KERNEL", "L2-WALL")
ENC_DIR = os.path.join(ROOT, "KERNEL", "L1-ENC")

BODY_NEW = 0xBC8            # тело (0xB98 + 5 код + 16 errtab + 27 строка)
BSS_NEW = 0x1500178         # 0x408178 + labtab 0x1F8000 + filebuf 0xF00000
VSIZE_NEW = 0x1500D40
EXE_SIZE = 0xE00            # файл не изменился (SRD 0xC00)


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
    """Проход пасса 1: [(смещение, [токены], комментарий)] строк."""
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
        comment = ""
        if ";" in line:
            comment = line.split(";", 1)[1].strip()
        d = toks[0]
        out.append((cur, [d] + body, comment))
        cur += line_size(d, body)
    return out


def line_size(d, body):
    """Размер материализации одной строки-директивы."""
    if d == "H":
        n = 0
        for t in body:
            if t.startswith("$"):
                n += 1 if t.endswith(":1") else 4
            else:
                n += 1
        return n
    if d == "DB":
        return len(body)
    if d in ("DZ", "DBZ"):
        return int(body[0], 16)
    if d == "DD":
        return 4 * len(body)
    if d == "DQ":
        return 8 * len(body)
    raise ValueError(d)


def gen_hex_text(flat, body):
    """Регенерация brick.hex: 1 @-строка на строку-директиву файла."""
    head = (
        "; UNIVERSAL / ATOM v1 / слой L1 / модуль M1-BRICK (телесная форма)\n"
        "; Исходник тела секции brick.exe. Смещения — от начала СЕКЦИИ\n"
        "; (RVA = смещение + 0x1000). PE-заголовки генерирует pegen по файлу\n"
        "; brick.peg (SPEC/07-PEG-FORMAT). Эквивалентный BRICK-исходник —\n"
        "; brick.brick (сборка: brick.exe brick.brick body.bin).\n"
        "; Виртуальные нули (bss, 0x%X байт) в файл не входят — директива"
        " !bss.\n" % BSS_NEW)
    lines = [head]
    for off, toks, comment in walk_lines(flat):
        d, body_toks = toks[0], toks[1:]
        if d == "DBZ":
            break                     # дальше — виртуальные нули (bss)
        n = line_size(d, body_toks)
        chunk = body[off:off + n]
        assert len(chunk) == n, (hex(off), d)
        bys = " ".join("%02X" % b for b in chunk)
        ln = "@%04X %s" % (off, bys)
        if comment:
            ln += " ; " + comment
        lines.append(ln + "\n")
    return "".join(lines)


def build():
    """Собрать новые артефакты; вернуть статистику."""
    flat = flat_source().decode("utf-8")
    # сверка ожидаемых строк E9.5-2 (константы пределов)
    lines = flat.split("\n")
    assert "H 41 B8 00 00 10 01 ; K1-G001 mov r8d,0x1100000" \
        " (вместимость, E9.5-2)" in lines, "нет mov r8d 0x1100000"
    assert any(li.startswith("H 48 3D 00 00 10 01 ; K1-G001 cmp"
                             " rax,0x1100000") for li in lines)
    assert any(li.startswith("H 3D 00 00 10 00 ; K1-G001 cmp"
                             " eax,0x100000") for li in lines)
    assert any(li.startswith("H 76 $ok4:1 ; K1-G001 jbe ok4")
               for li in lines), "нет jbe ok4"
    assert any(li.startswith("H 41 81 FB 00 00 02 00 ; K1-N001 cmp"
                             " r11d,0x20000") for li in lines)
    assert any(li.startswith("H B9 08 00 00 00 ; K1-N001 mov ecx,8"
                             " (индекс errtab[8])") for li in lines)
    assert any(li.startswith("DD $err_biglab 1B B 0") for li in lines)
    assert "DBZ 200000 ; виртуальные нули (bss; 131072 метки, E9.5-2)" \
        in lines
    assert "DBZ 1100008 ; виртуальные нули (bss; 17 МиБ + сентинел," \
        " E9.5-2)" in lines
    assert "DBZ 200010 ; виртуальные нули (bss; покрывает тела 1 МиБ" \
        " с запасом 2x, E9.5-2)" in lines

    labels, filelen, vsize = layout(flat)
    assert filelen == BODY_NEW, hex(filelen)
    assert vsize == VSIZE_NEW, hex(vsize)
    bss = vsize - filelen
    assert bss == BSS_NEW, hex(bss)
    new_body = lab_brick.assemble(flat.encode("utf-8"))
    assert len(new_body) == filelen, (len(new_body), filelen)

    # ФОРМ-проверки тела (пины байтов — дешёвая альтернатива
    # O(n^2)-прогону 131073 меток):
    assert b"\x3D\x00\x00\x10\x00\x76" in new_body, "cmp eax/jbe 1 МиБ"
    assert b"\x48\x3D\x00\x00\x10\x01" in new_body, "cmp rax 17 МиБ"
    assert b"\x41\x81\xFB\x00\x00\x02\x00" in new_body, "cmp r11d метки"
    assert b"\x55\x2D\x4C\x31\x2D\x42\x52\x49\x43\x4B\x20\x45\x52\x52" \
        b"\x3D\x42\x49\x47\x20\x4C\x41\x42\x45\x4C\x53" in new_body, \
        "строка BIG LABELS"
    # errtab[8] = {RVA err_biglab, длина 0x1B, код 0xB, 0}
    rva_bl = labels["err_biglab"] + 0x1000
    want_e = rva_bl.to_bytes(4, "little") + \
        (0x1B).to_bytes(4, "little") + (0xB).to_bytes(4, "little") + \
        b"\x00\x00\x00\x00"
    assert want_e in new_body, "errtab[8] BIG LABELS"
    print("  форм-проверки тела: cmp/jbe 1 МиБ, 17 МиБ, метки 131072,"
          " errtab[8], строка BIG LABELS — ОК")

    # diff старое -> новое тело: префикс до первого изменённого байта
    old_body = lab_atom.assemble(open(os.path.join(KERNEL_DIR, "brick.hex"),
                                "r", encoding="latin1").read())
    same = 0
    for a, b in zip(old_body, new_body):
        if a != b:
            break
        same += 1
    print("  тело: %d -> %d байт (+%d); общий префикс %d (0x%X)"
          % (len(old_body), len(new_body), len(new_body) - len(old_body),
             same, same))

    # регенерация brick.hex (1:1 по строкам исходника)
    new_hex_text = gen_hex_text(flat, new_body)
    assert lab_atom.assemble(new_hex_text) == new_body, \
        "hexgen(новый brick.hex) != новое тело"

    peg = ("; UNIVERSAL / PEG v1 / слой L1 / модуль M1-BRICK\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg>"
           " <out.exe>\n"
           "!module brick\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n" % (labels["idt"] + 0x1000,
                                labels["iat"] + 0x1000, bss))
    exe = lab_pegen.wrap(new_body, peg)
    assert len(exe) == EXE_SIZE, hex(len(exe))

    for name, data in [("brick.hex",
                        new_hex_text.encode("utf-8")),
                       ("brick.peg", peg.encode()),
                       ("brick.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)
    print("  peg: !idata %X !iat %X !bss %X" %
          (labels["idt"] + 0x1000, labels["iat"] + 0x1000, bss))

    return dict(labels=labels, filelen=filelen, vsize=vsize, bss=bss,
                body=len(new_body), exe=len(exe),
                src=len(flat.encode("utf-8")))


# ---------------------------------------------------------------- тесты
def dev_tests():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-64s %s" % ("OK " if cond else "FAIL", name, note))

    exe = os.path.join(KERNEL_DIR, "brick.exe")

    def run_br(args, host, max_steps=200_000_000):
        return lab_run.run_kv(exe, args, host, max_steps=max_steps)

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
          r0.exit_code == 0 and len(self_bin) == BODY_NEW,
          "%d байт, шагов=%d+%d" % (len(self_bin), r0.steps, r1.steps))

    # 5. круг E5: pegen(brick(brick.brick)) == brick.exe
    h["t_self.bin"] = self_bin
    r3 = lab_run.run_kv(PEGEN_EXE, ["t_self.bin", "b.peg", "t.exe"], h)
    check("DoD E5: pegen-круг brick.exe",
          r3.files.get("t.exe") ==
          open(os.path.join(KERNEL_DIR, "brick.exe"), "rb").read(),
          "шагов=%d" % r3.steps)

    # 6. НОВЫЙ ПРЕДЕЛ ТЕЛА (E9.5-2): 0x100000 — jbe-край, принят
    #    (старый предел 128 КиБ отверг бы уже 0x20000; jb отверг бы
    #    ровно 0x100000 — jbe синхронен pegen/мосту)
    src = b"DZ 100000\n"
    want = lab_brick.assemble(src)
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел тела: 0x100000 (1 МиБ) принят — jbe-край",
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 7. НОВЫЙ ПРЕДЕЛ ТЕЛА: 0x100001 — отвергнут ERR=BIG OUT (код 10)
    src = b"DZ 100001\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": src})
    check("предел тела: 0x100001 отвергнут (BIG OUT)",
          r.exit_code == 10 and
          r.stdout == b"U-L1-BRICK ERR=BIG OUT\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 8. НОВЫЙ ПРЕДЕЛ МЕТОК: 2049 — принят (старый предел 2048
    #    ВКЛ. base = 2047 пользовательских — отверг бы; O(n^2) ~21 млн
    #    шагов — dev-only; точный край 131072/131073 форм-проверками)
    src2049 = b"".join((b":k%d\n" % i) + b"H 90\n" for i in range(2049))
    want = lab_brick.assemble(src2049)
    r = run_br(["t.brick", "t.bin"], {"t.brick": src2049})
    check("предел меток: 2049 принята (старый предел 2048)",
          r.exit_code == 0 and r.files.get("t.bin") == want,
          "тело=%d шагов=%d" % (len(want), r.steps))

    # 9. НОВЫЙ ПРЕДЕЛ ИСХОДНИКА: 0x200020 байт одной строкой — принят
    #    (старый предел 2 МиБ отверг бы; dev-only — ~34 млн шагов)
    line2m = b";" + b"A" * (0x200020 - 2) + b"\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": line2m})
    check("предел исходника: 0x200020 (2 МиБ+32) принят (старый 2 МиБ)",
          r.exit_code == 0 and r.files.get("t.bin") == b"",
          "шагов=%d" % r.steps)

    # 10. НОВЫЙ ПРЕДЕЛ ИСХОДНИКА: 0x1100000 — ТОЧНЫЙ КРАЙ, отвергнут
    #     ERR=BIG SRC (код 7; O(1))
    line17m = b";" + b"A" * (0x1100000 - 2) + b"\n"
    r = run_br(["t.brick", "t.bin"], {"t.brick": line17m})
    check("предел исходника: 0x1100000 (17 МиБ) отвергнут (BIG SRC)",
          r.exit_code == 7 and
          r.stdout == b"U-L1-BRICK ERR=BIG SRC\r\n",
          "код=%s" % r.exit_code)

    # 11. BIG LABELS — форм-проверка (дёшево вместо O(n^2) прогона
    #     131073 меток ~млрд шагов): imm32 предела + errtab[8] +
    #     строка + mov ecx,8 уже сверены в build(); пин SHA секции 1
    body = open(exe, "rb").read()[0x200:0x200 + BODY_NEW]
    assert b"\x41\x81\xFB\x00\x00\x02\x00" in body
    check("BIG LABELS: форм-пин тела (imm32 0x20000 + errtab[8])",
          True, "байты в теле сверены")

    # 12. регресс: крупнейшие потребители — wall.brick и enc.brick
    #     (каркас wall.wall — кругом батареи T-E6-49b на CI)
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
    print("=== brick_build_lim5: сборка M1-BRICK (E9.5-2) ===")
    stats = build()
    print("тело %d байт (0x%X); bss 0x%X; vsize 0x%X; exe %d байт"
          % (stats["body"], stats["body"], stats["bss"], stats["vsize"],
             stats["exe"]))
    print("исходник %d Б; меток в исходнике %d"
          % (stats["src"], len(stats["labels"])))
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "brick.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 brick.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
