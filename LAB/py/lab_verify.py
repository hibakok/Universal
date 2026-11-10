"""lab_verify.py — батарея полной верификации репозитория (главный вход).

Вход:  корень репозитория (текущая папка).
Выход: отчёт [OK]/[FAIL] по всем проверкам; код возврата 0/1.
Функция: автоматизировать три уровня SPEC/02 и круги DoD E3–E5:
         1) целостность артефактов (SHA-256 из VERIFY.md);
         2) инварианты PE (SPEC/04);
         3) эмуляция всех документированных сценариев TESTS/;
         4) оракулы форматов против инструментов (ATOM/BRICK/PEG/ENC);
         5) круги воспроизведения E4 (hexgen+pegen == EXE) и
            самохостинг E5 (brick(brick.brick) == hexgen(brick.hex));
         6) оракул ENC (SPEC/09): якорные кодировки, отвержение
            ошибок, декодер lab_x86, полный круг v2 -> EXE -> эмуляция;
         7-9) инструменты enc/splice (lab_t_exe) и оракул WALL v1
            (SPEC/11, lab_t_wall): якоря, ошибки, круг до эмуляции;
         10) инструмент wall.exe (lab_t_wall2, E6.4b): равенство
            оракулу на якорях/big_source, отвержение, полный круг
            WALL -> EXE -> эмуляция, SHA и PE-инварианты.
Запуск: python3 LAB/py/lab_verify.py   (из корня репозитория)
"""
import hashlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_atom
import lab_brick
import lab_enc
import lab_enc_cases
import lab_pe
import lab_pegen
import lab_run
import lab_splice
import lab_t_exe
import lab_t_wall
import lab_t_wall2
import lab_x86

KERNEL = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "KERNEL")

# Эталоны SHA-256 (KERNEL/*/VERIFY.md, актуальны после E5a)
SHA = {
    "L0-SEED/seed": "615D3292CCDD08664F7ACFCF9EF39E55F37443D1BF5A5F3E40"
                    "D1CC796E64DBDF",
    "L0-SEED2/seed2": "190DE94E3F3227D421B6779B34985FD1762E127EC50EF864"
                      "C4ED84814B05EE87",
    "L0-HXDUMP/hxdump": "F0CEE97E45B1399FF13151BF4587BA2A02465E793FB9C92"
                        "F525CDD69A7B4A8E3",
    "L0-HEXGEN/hexgen": "947AD0182A0162CB402CB4D92A7932681CE6B2BF16B5B524"
                        "ACCE07AB3FD241BF",
    "L0-PEGEN/pegen": "39B7D78C344B2FAC0000AD929764EBF418D9EF98D39445782"
                      "6E5B8C806F1906C",
    "L1-BRICK/brick": "5F7F9EFD3398B735E762B37610ED1F197C383DA7252A3CD0"
                      "C73DD3EE31A5C857",
    "L1-ENC/enc": "01A7B19280E3E581938E714C23A109559A26BE87A9B2F5EC"
                "9F0B5E90C4BAF696",
    "L1-SPLICE/splice": "387B5B63650205E4B16D270CD91FE0EADCAD644E67087C61E11D2"
                       "2D32D27AF92",
    "L2-WALL/wall": "A40A5FF668CE010BF6042D8D59E7F2589AE92F9500302A4D0A4E44D92724181D",
}
# модули с .hex-листингами ATOM (для оракулов/кругов E4); enc и splice
# ведут исходники в BRICK v2 (enc.b2/splice.b2 с !include)
MODS = [m for m in SHA if m not in ("L1-ENC/enc", "L1-SPLICE/splice",
                        "L2-WALL/wall")]

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print("[%s] %-52s %s" % ("OK" if ok else "FAIL", name, note))


def kfile(rel):
    return open(os.path.join(KERNEL, rel), "rb").read()


def kpath(rel):
    return os.path.join(KERNEL, rel)


def kernel_host():
    """Все файлы KERNEL как виртуальная ФС (ключи в нижнем регистре)."""
    files = {}
    for root, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def emu(exe, args, host):
    return lab_run.run_kv(kpath("L0-HEXGEN/hexgen.exe"), [], {}) if exe \
        is None else lab_run.run_kv(kpath(exe), args, host)


# ------------------------------------------------------------------ 1
def t_integrity():
    for m in SHA:                       # все образы, вкл. enc и splice
        data = kfile("%s.exe" % m)
        got = hashlib.sha256(data).hexdigest().upper()
        check("SHA-256 %s.exe" % m.split("/")[-1], got == SHA[m],
              got[:16] + "…" if got == SHA[m] else "ожидался " +
              SHA[m][:16] + "…")


# ------------------------------------------------------------------ 2
def t_pe_invariants():
    for m in SHA:                       # включая enc (E6.2)
        pe = lab_pe.load(kpath("%s.exe" % m))
        bad = lab_pe.check_spec04(pe)
        check("PE инварианты SPEC/04 %s" % m.split("/")[-1], not bad,
              "; ".join(bad) if bad else "vsize=%X" % pe["sec_vsize"])


# ------------------------------------------------------------------ 3
def t_scenarios():
    """Документированные сценарии TESTS/ (уровень 3 SPEC/02)."""
    def out_is(exe, args, want_out, want_code, host=None):
        r = lab_run.run_kv(kpath(exe), args, host or {})
        return (r.stdout == want_out and r.exit_code == want_code,
                "%r код=%s шагов=%d" % (r.stdout[:40], r.exit_code,
                                        r.steps))

    ok, note = out_is("L0-SEED/seed.exe", [],
                      b"U-L0-SEED OK IMAGE=0x00002000\r\n", 0)
    check("T-M0-02 seed: вывод и код", ok, note)

    for cmd, line in [("entry", "ENTRY=0x00001000"),
                      ("image", "IMAGE=0x00002000"),
                      ("align", "ALIGN=0x00001000"),
                      ("sect", "SECT=0x00000001")]:
        ok, note = out_is("L0-SEED2/seed2.exe", [cmd],
                          ("U-L0-SEED2 %s\r\n" % line).encode(), 0)
        check("T-M2 seed2 %s" % cmd, ok, note)
    ok, note = out_is("L0-SEED2/seed2.exe", ["args", "hello", "world"],
                      b"U-L0-SEED2 ARGS: hello world\r\n", 0)
    check("T-M2-06 seed2 args", ok, note)
    ok, note = out_is("L0-SEED2/seed2.exe", [],
                      b"U-L0-SEED2 CMDS: ENTRY IMAGE ALIGN SECT ARGS\r\n",
                      0)
    check("T-M2-08 seed2 справка", ok, note)
    ok, note = out_is("L0-SEED2/seed2.exe", ["bogus"],
                      b"U-L0-SEED2 CMDS: ENTRY IMAGE ALIGN SECT ARGS\r\n",
                      2)
    check("T-M2-09 seed2 bogus -> код 2", ok, note)

    seed_exe = kfile("L0-SEED/seed.exe")
    r = lab_run.run_kv(kpath("L0-HXDUMP/hxdump.exe"), ["s.exe"],
                       {"s.exe": seed_exe})
    # эталон дампа: генерируем сами (формат T-M3-02)
    want = b""
    for off in range(0, len(seed_exe), 16):
        chunk = seed_exe[off:off + 16]
        hexs = " ".join("%02X" % b for b in chunk)
        asci = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        want += ("%08X: %-47s  %s\r\n" % (off, hexs, asci)).encode()
    check("T-M3-02/03 hxdump дамп seed.exe (64 строки)",
          r.exit_code == 0 and r.stdout == want,
          "строк=%d, шагов=%d" % (r.stdout.count(b"\r\n"), r.steps))
    ok, note = out_is("L0-HXDUMP/hxdump.exe", ["t.bin"],
                      b"00000000: 68 65 6C 6C 6F  hello\r\n", 0,
                      {"t.bin": b"hello"})
    check("T-M3-04 hxdump короткий файл", ok, note)
    ok, note = out_is("L0-HXDUMP/hxdump.exe", ["no.bin"],
                      b"U-L0-HXDUMP ERR=OPEN FILE\r\n", 4)
    check("T-M3-07 hxdump нет файла", ok, note)
    ok, note = out_is("L0-HXDUMP/hxdump.exe", [],
                      b"U-L0-HXDUMP CMDS: HXDUMP <FILE>\r\n", 2)
    check("T-M3-06 hxdump справка", ok, note)

    ok, note = out_is("L0-HEXGEN/hexgen.exe", [],
                      b"U-L0-HEXGEN CMDS: HEXGEN <IN.HEX> <OUT.BIN>\r\n",
                      2)
    check("T-M4 hexgen справка", ok, note)
    ok, note = out_is("L0-HEXGEN/hexgen.exe", ["no.hex", "t.bin"],
                      b"U-L0-HEXGEN ERR=OPEN INPUT\r\n", 4)
    check("T-M4 hexgen нет входа", ok, note)
    ok, note = out_is("L0-HEXGEN/hexgen.exe", ["bad.hex", "t.bin"],
                      b"U-L0-HEXGEN ERR=FORMAT\r\n", 7,
                      {"bad.hex": b"@0000 8d\n"})
    check("T-M4 hexgen строчная цифра", ok, note)

    ok, note = out_is("L0-PEGEN/pegen.exe", [],
                      b"U-L0-PEGEN CMDS: PEGEN <IMAGE.BIN> <CTRL.PEG> "
                      b"<OUT.EXE>\r\n", 2)
    check("T-M5-07 pegen справка", ok, note)
    ok, note = out_is("L0-PEGEN/pegen.exe", ["no.bin", "t.peg", "o.exe"],
                      b"U-L0-PEGEN ERR=OPEN IMAGE\r\n", 4)
    check("T-M5-09 pegen нет образа", ok, note)
    ok, note = out_is("L0-PEGEN/pegen.exe", ["a.bin", "no.peg", "o.exe"],
                      b"U-L0-PEGEN ERR=OPEN PEG\r\n", 7, {"a.bin": b"\x00"})
    check("T-M5-10 pegen нет peg", ok, note)

    ok, note = out_is("L1-BRICK/brick.exe", [],
                      b"U-L1-BRICK CMDS: BRICK <SRC.BRICK> <OUT.BIN>\r\n",
                      2)
    check("T-M6-04 brick справка", ok, note)
    for name, src, want in [
        ("T-M6-12 строчная цифра", b"H 48 8d\n", 1),
        ("T-M6-13 дубликат метки", b":a\n:a\n", 2),
        ("T-M6-14 неопределённая метка", b"H 74 $zz:1\n", 1),
        ("T-M6-15 слот не в конце", b"H 48 $x 90\n", 1)]:
        r = lab_run.run_kv(kpath("L1-BRICK/brick.exe"), ["t.brick",
                                                         "t.bin"],
                           {"t.brick": src})
        want_out = ("U-L1-BRICK ERR=FORMAT AT=%04X\r\n" % want).encode()
        check(name + " (AT=%04X)" % want,
              r.stdout == want_out and r.exit_code == 6,
              "%r код=%s" % (r.stdout, r.exit_code))


# ------------------------------------------------------------------ 4
def t_oracles():
    host = kernel_host()
    for m in MODS:
        rel = m.lower()
        # ATOM: оракул == телу из EXE
        body = lab_atom.assemble(kfile("%s.hex" % m).decode("latin1"))
        pe = lab_pe.load(kpath("%s.exe" % m))
        check("оракул ATOM == тело %s.hex" % rel,
              body == pe["body"][:len(body)], "%d байт" % len(body))
        # ATOM: hexgen.exe (эмуляция) == оракулу
        r = lab_run.run_kv(kpath("L0-HEXGEN/hexgen.exe"),
                           ["%s.hex" % rel, "t.bin"], host)
        check("hexgen.exe == оракул ATOM (%s)" % rel,
              r.exit_code == 0 and r.files.get("t.bin") == body,
              "шагов=%d" % r.steps)
        # PEGEN: оракул == EXE
        exe = lab_pegen.wrap(body, kfile("%s.peg" % m)
                             .decode("latin1"))
        check("оракул PEGEN == %s.exe" % rel, exe == kfile("%s.exe" % m),
              "%d байт" % len(exe))
    # BRICK: оракул == brick.exe на склейке brick.brick (разрез E6.3)
    flat = lab_splice.splice("l1-brick/brick.brick", host)
    body = lab_brick.assemble(flat)
    r = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                       ["b.brick", "t.bin"], {"b.brick": flat})
    check("оракул BRICK == brick.exe (splice(brick.brick))",
          r.exit_code == 0 and r.files.get("t.bin") == body,
          "%d байт, шагов=%d" % (len(body), r.steps))
    # BRICK: семантика слотов/директив (мини-оракул SPEC/08)
    for name, src in [
        ("слот rip $base", b":e\nH 48 8D 1D $base\n"),
        ("rel8", b":a\nH 74 $b:1\nH 90\n:b\nH CC\n"),
        ("DD/DQ RVA", b":x\nDB 41\n:y\nDQ $x\nDD $y 20\n"),
        ("DBZ-виртуальность", b"DZ 3\n:far\nDBZ 10\nH 90\n")]:
        try:
            o = lab_brick.assemble(src)
            r = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                               ["t.brick", "t.bin"], {"t.brick": src})
            check("оракул BRICK: %s" % name,
                  r.exit_code == 0 and r.files.get("t.bin") == o,
                  "%d байт" % len(o))
        except lab_brick.BrickError as e:
            check("оракул BRICK: %s" % name, False, str(e))


# ------------------------------------------------------------------ 5
def t_cycles():
    host = kernel_host()
    total_steps = 0
    for m in MODS:
        rel = m.lower()
        r1 = lab_run.run_kv(kpath("L0-HEXGEN/hexgen.exe"),
                            ["%s.hex" % rel, "t_body.bin"], host)
        host2 = dict(host)
        host2["t_body.bin"] = r1.files.get("t_body.bin", b"")
        r2 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                            ["t_body.bin", "%s.peg" % rel, "t.exe"],
                            host2)
        made = r2.files.get("t.exe", b"")
        total_steps += r1.steps + r2.steps
        check("круг E4: hexgen+pegen -> %s.exe" % rel,
              made == kfile("%s.exe" % m) and r1.exit_code == 0 and
              r2.exit_code == 0, "шагов=%d+%d" % (r1.steps, r2.steps))
    # самосборка pegen (E4): pegen(pegen.hex) + pegen -> pegen.exe
    body = lab_atom.assemble(kfile("L0-PEGEN/pegen.hex")
                             .decode("latin1"))
    r = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                       ["t.bin", "p.peg", "t2.exe"],
                       {"t.bin": body,
                        "p.peg": kfile("L0-PEGEN/pegen.peg")})
    check("круг E4: самосборка pegen",
          r.files.get("t2.exe") == kfile("L0-PEGEN/pegen.exe"),
          "шагов=%d" % r.steps)
    # E5: самохостинг brick — через разрез (splice -> brick -> hexgen)
    host = kernel_host()
    r0 = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                        ["l1-brick/brick.brick", "t_flat.brick"], host)
    h = {"b.brick": r0.files.get("t_flat.brick", b""),
         "b.hex": kfile("L1-BRICK/brick.hex"),
         "b.peg": kfile("L1-BRICK/brick.peg")}
    r1 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                        ["b.brick", "t_self.bin"], h)
    r2 = lab_run.run_kv(kpath("L0-HEXGEN/hexgen.exe"),
                        ["b.hex", "t_body.bin"], h)
    self_bin = r1.files.get("t_self.bin", b"")
    body_bin = r2.files.get("t_body.bin", b"")
    check("DoD E5: brick(splice(brick.brick)) == hexgen(brick.hex)",
          self_bin == body_bin and r1.exit_code == 0 and r0.exit_code == 0,
          "%d байт, шагов=%d+%d" % (len(self_bin), r0.steps, r1.steps))
    h["t_self.bin"] = self_bin
    r3 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                        ["t_self.bin", "b.peg", "t.exe"], h)
    check("DoD E5: pegen-круг brick.exe",
          r3.files.get("t.exe") == kfile("L1-BRICK/brick.exe"),
          "шагов=%d" % r3.steps)


# ------------------------------------------------------------------ 6
def t_enc():
    """Оракул ENC (SPEC/09): якоря, ошибки, декодер, круг v2->EXE."""
    bad = []
    for m, h in lab_enc_cases.CASES:
        try:
            if lab_enc.normalize(m + "\n").strip() != h:
                bad.append(m)
        except lab_enc.EncError:
            bad.append(m + " (ошибка)")
    check("ENC: якорные кодировки SPEC/05 (%d)" % len(lab_enc_cases.CASES),
          not bad, "; ".join(bad[:3]) if bad else "")

    bad = [e for e in lab_enc_cases.ERRORS
           if not _enc_rejects(e)]
    check("ENC: отвержение некорректных M-строк (%d)"
          % len(lab_enc_cases.ERRORS), not bad,
          "; ".join(bad[:3]) if bad else "")

    # структурный контроль: каждая кодировка декодируется обратно
    # декодером lab_x86 ровно той же длины (слоты заменяются нулями)
    bad = []
    for m, _h in lab_enc_cases.CASES:
        toks = lab_enc.encode_m(*_enc_parse(m), 1)
        bs = bytearray()
        for t in toks:
            if isinstance(t, int):
                bs.append(t)
            else:
                bs += b"\x00" * t[2]
        fetch = lambda a, n: int.from_bytes(bs[a:a + n], "little")
        try:
            _name, length, _args = lab_x86.decode(fetch, 0)
            if length != len(bs):
                bad.append(m)
        except Exception:
            bad.append(m)
    check("ENC: декодер lab_x86 подтверждает структуру (%d)"
          % len(lab_enc_cases.CASES), not bad,
          "; ".join(bad[:3]) if bad else "")

    # полный круг: DEMO_B2 -> enc -> brick -> pegen -> эмуляция
    v1 = lab_enc.normalize(lab_enc_cases.DEMO_B2)
    body = lab_brick.assemble(v1.encode("utf-8"))
    exe = lab_pegen.wrap(body, lab_enc_cases.DEMO_PEG)
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, exe)
        os.close(fd)
        r = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check("ENC: полный круг v2->EXE->эмуляция (U-ENC-OK)",
          r.stdout == b"U-ENC-OK\r\n" and r.exit_code == 0,
          "%r код=%s шагов=%d" % (r.stdout[:24], r.exit_code, r.steps))


def _enc_parse(m):
    """'M mov rax, 5' -> ('mov', ['rax', '5']) без проверки."""
    body = m[1:].strip()
    parts = body.split(None, 1)
    rest = parts[1].strip() if len(parts) > 1 else ""
    return parts[0], [p.strip() for p in rest.split(",")] if rest else []


def _enc_rejects(m):
    try:
        lab_enc.normalize(m + "\n")
        return False
    except lab_enc.EncError:
        return True


# ------------------------------------------------------------------ 7+8
# Секции 7 (enc.exe) и 8 (splice.exe) — в LAB/py/lab_t_exe.py (лимит 500)
# Секция 9 (оракул WALL v1, E6.4a) — в LAB/py/lab_t_wall.py (лимит 500)


def main():
    print("=== UNIVERSAL / LAB: батарея верификации ===")
    t_integrity()
    t_pe_invariants()
    t_scenarios()
    t_oracles()
    t_cycles()
    t_enc()
    lab_t_exe.run(check, kpath, kfile, kernel_host)
    lab_t_wall.run(check, kpath, kfile, kernel_host)
    lab_t_wall2.run(check, kpath, kfile, kernel_host)
    n, m = len(PASS), len(PASS) + len(FAIL)
    print("\nИТОГ: %d/%d %s" % (n, m, "OK" if n == m else
                               "— ЕСТЬ ПРОВАЛЫ:"))
    for f in FAIL:
        print("  FAIL:", f)
    return 0 if n == m else 1


if __name__ == "__main__":
    sys.exit(main())
