#!/usr/bin/env python3
"""splice_build_lim.py — пересборка артефактов M1-SPLICE после роста
пределов FILECAP/OUTCAP и буферов уровней 128 -> 256 КиБ (E6.4e-2).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL): читает
разрез KERNEL/L1-SPLICE/splice.b2 (splice-оракул с новыми пределами),
нормализует оракулом lab_enc, раскладывает метки, собирает тело
(lab_brick) и EXE (lab_pegen), записывает splice.brick / splice.peg /
splice.exe и прогоняет dev-тесты эмуляцией: якоря, ошибки, большой
исходник, самосклейка, самохостинг, регресс корней enc/wall и НОВЫЕ
проверки пределов (корень и включение 132 КиБ приняты — раньше 128 КиБ
был потолком; включение 256 КиБ отвергнуто ERR=BIG SRC; максимум
0x3FFFF принят; выход 132 КиБ и крупнейший корень wall.b2 — тоже).
Повторный запуск после изменения splice.b2 воспроизводит артефакты и
печатает новый SHA-256 (обновить: lab_verify.py SHA, README, VERIFY.md).
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
LAB = os.path.join(ROOT, "LAB", "py")
sys.path.insert(0, LAB)

import lab_brick                          # noqa: E402
import lab_enc                            # noqa: E402
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402
import lab_splice_cases                   # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L1-SPLICE")
ENC_EXE = os.path.join(ROOT, "KERNEL", "L1-ENC", "enc.exe")
BRICK_EXE = os.path.join(ROOT, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-PEGEN", "pegen.exe")

SRC_CAP = 0x40000          # новый предел файла (E6.4e-2)
OUT_CAP = 0x40000          # новый предел выхода (E6.4e-2)


def kernel_host():
    files = {}
    for root, _d, fs in os.walk(os.path.join(ROOT, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(ROOT, "KERNEL")) \
                .replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def layout(brick_text):
    """Карта меток/длин (пасс 1 SPEC/08) — как enc_build_lim.layout."""
    labels, cur, filelen = {}, 0, None
    for line in brick_text.split("\n"):
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
            n = 0
            for t in body:
                if t.startswith("$"):
                    n += 1 if t.endswith(":1") else 4
                else:
                    n += 1
            cur += n
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


def build():
    """Собрать артефакты из разрезанного исходника (корень + части)."""
    with open(os.path.join(KERNEL_DIR, "splice.b2"), "rb") as f:
        root = f.read().decode("utf-8")
    # склейка корня с включениями (оракул с новыми пределами E6.4e-2)
    host = {"splice.b2": root.encode("utf-8")}
    for line in root.splitlines():
        if line.startswith("!include "):
            name = line[len("!include "):].strip()
            with open(os.path.join(KERNEL_DIR, name), "rb") as f:
                host[name] = f.read()
    src = lab_splice.splice("splice.b2", host).decode("utf-8")
    assert len(src.encode("utf-8")) < SRC_CAP, "splice.b2 >= 256 КиБ"
    brick = lab_enc.normalize(src)
    labels, filelen, vsize = layout(brick)
    assert filelen is not None, "нет DBZ — нет bss"
    body = lab_brick.assemble(brick.encode("utf-8"))
    assert len(body) == filelen, (len(body), filelen)
    idt_rva = labels["idt"] + 0x1000
    iat_rva = labels["iat"] + 0x1000
    peg = ("; UNIVERSAL / PEG v1 / слой L1 / модуль M1-SPLICE\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg>"
           " <out.exe>\n"
           "!module splice\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n" % (idt_rva, iat_rva, vsize - filelen))
    exe = lab_pegen.wrap(body, peg)
    for name, data in [("splice.brick", brick.encode("utf-8")),
                       ("splice.peg", peg.encode()),
                       ("splice.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)
    stats = dict(labels=labels, filelen=filelen, vsize=vsize,
                 bss=vsize - filelen, idt=idt_rva, iat=iat_rva,
                 body=len(body), exe=len(exe),
                 src=len(src.encode("utf-8")), lines=len(src.splitlines()))
    return stats


# ---------------------------------------------------------------- тесты
def dev_tests():
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-58s %s" % ("OK " if cond else "FAIL", name, note))

    exe = os.path.join(KERNEL_DIR, "splice.exe")

    def run_sp(args, host):
        return lab_run.run_kv(exe, args, host)

    # 1. справка без аргументов
    r = run_sp([], {})
    check("справка",
          r.stdout == b"U-L1-SPLICE CMDS: SPLICE <ROOT.SRC> <OUT.FLAT>\r\n"
          and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:48], r.exit_code))

    # 2. нормальные случаи: инструмент == якорь (якорь == оракулу — п. 6)
    bad, steps = [], 0
    for name, root, host, want in lab_splice_cases.CASES:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = run_sp([root, "t.flat"], host)
        steps += r.steps
        if not (r.exit_code == 0 and r.stdout == b"" and
                r.files.get("t.flat") == want):
            bad.append("%s: код=%s файл=%r" % (name, r.exit_code,
                                               (r.files.get("t.flat")
                                                or b"")[:24]))
    check("CASES: %d якорей (инструмент == якорям)"
          % len(lab_splice_cases.CASES), not bad,
          "; ".join(bad[:2]) if bad else "шагов=%d" % steps)

    # 3. ошибки: инструмент == якорям (код + строка)
    bad = []
    for name, root, host, code, msg in lab_splice_cases.ERRORS:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = run_sp([root, "t.flat"], host)
        want_out = ("U-L1-SPLICE ERR=%s\r\n" % msg).encode()
        if not (r.exit_code == code and r.stdout == want_out):
            bad.append("%s: код=%s out=%r" % (name, r.exit_code,
                                              r.stdout[:40]))
    check("ERRORS: %d случаев (коды и строки; BIG SRC/OUT 256 КиБ)"
          % len(lab_splice_cases.ERRORS), not bad, "; ".join(bad[:2]))

    # 4. большой исходник (~24 КиБ)
    root, host, want = lab_splice_cases.big_case(24000)
    host = {k.decode("latin1") if isinstance(k, bytes) else k: v
            for k, v in host.items()}
    r = run_sp([root, "t.flat"], host)
    check("большой исходник (%d КиБ)" % (len(want) // 1024),
          r.exit_code == 0 and r.files.get("t.flat") == want,
          "строк=%d шагов=%d" % (want.count(b"\n"), r.steps))

    # 5. НОВЫЙ ПРЕДЕЛ (E6.4e-2): корень 0x20020 байт одной строкой —
    #    принят (старые FILECAP и OUTCAP 0x20000 отвергли бы);
    #    выход == вход (одна строка + LF)
    line132 = b";" + b"A" * (0x20020 - 2) + b"\n"
    assert len(line132) == 0x20020
    r = run_sp(["r.b2", "t.flat"], {"r.b2": line132})
    check("предел: корень 0x%X байт принят (старые пределы 0x20000)"
          % len(line132),
          r.exit_code == 0 and r.files.get("t.flat") == line132,
          "шагов=%d" % r.steps)

    # 6. НОВЫЙ ПРЕДЕЛ: включение 0x20020 байт — принят (буфер уровня 1,
    #    адресация shl 18; старый уровень 0x20000 отверг бы)
    part132 = b";" + b"B" * (0x20020 - 2) + b"\n"
    r = run_sp(["r.b2", "t.flat"],
               {"r.b2": b"!include p.b2\n", "p.b2": part132})
    check("предел: включение 0x%X байт принято (уровень 1)"
          % len(part132),
          r.exit_code == 0 and r.files.get("t.flat") == part132,
          "шагов=%d" % r.steps)

    # 7. НОВЫЙ ПРЕДЕЛ: включение 0x40000 — отвергнуто ERR=BIG SRC (код 7)
    big = b"C" * 0x40000
    r = run_sp(["r.b2", "t.flat"],
               {"r.b2": b"!include big.b2\n", "big.b2": big})
    check("предел: включение 0x40000 отвергнуто (BIG SRC)",
          r.exit_code == 7 and
          r.stdout == b"U-L1-SPLICE ERR=BIG SRC\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 8. НОВЫЙ ПРЕДЕЛ: выход 0x20020 через ДВА включения — принят
    #    (OUTCAP; суммарный выход > 0x20000, старый предел отверг бы)
    p1 = b"D" * 0x1000F + b"\n"
    p2 = b"E" * 0x1000F + b"\n"
    want_out = p1 + p2
    assert len(want_out) == 0x20020
    r = run_sp(["r.b2", "t.flat"],
               {"r.b2": b"!include p1.b2\n!include p2.b2\n",
                "p1.b2": p1, "p2.b2": p2})
    check("предел: выход 0x%X байт принят (два включения)"
          % len(want_out),
          r.exit_code == 0 and r.files.get("t.flat") == want_out,
          "шагов=%d" % r.steps)

    # 9. НОВЫЙ ПРЕДЕЛ (dev-only, дорого): максимум 0x3FFFF — принят
    line_max = b";" + b"F" * (0x3FFFF - 2) + b"\n"
    assert len(line_max) == 0x3FFFF
    r = run_sp(["r.b2", "t.flat"], {"r.b2": line_max})
    check("предел: максимум 0x3FFFF принят",
          r.exit_code == 0 and r.files.get("t.flat") == line_max,
          "шагов=%d" % r.steps)

    # 10. склейка собственного разрезанного исходника == плоской форме
    root_b = open(os.path.join(KERNEL_DIR, "splice.b2"), "rb").read()
    host10 = {"splice.b2": root_b}
    for line in root_b.decode("utf-8").splitlines():
        if line.startswith("!include "):
            host10[line[9:].strip()] = open(
                os.path.join(KERNEL_DIR, line[9:].strip()), "rb").read()
    want10 = lab_splice.splice("splice.b2", host10)
    r = run_sp(["splice.b2", "t.flat"], host10)
    check("склейка splice.b2 (корень+части) == плоской форме",
          r.exit_code == 0 and r.files.get("t.flat") == want10,
          "%d байт, шагов=%d" % (len(want10), r.steps))

    # 11. оракул == якорям (двойная сверка, чистый Python)
    bad = lab_splice_cases.check_oracle()
    check("оракул == якорям (двойная сверка)", not bad,
          "; ".join(bad[:2]))

    # 12. крупнейший корень репозитория wall.b2 (127 КиБ вывода) —
    #     инструмент == оракулу (реальный потребитель новых пределов)
    kh = kernel_host()
    want_wall = lab_splice.splice("l2-wall/wall.b2", kh)
    r = run_sp(["l2-wall/wall.b2", "t.flat"], kh)
    check("крупнейший корень wall.b2 (%d КиБ) == оракулу"
          % (len(want_wall) // 1024),
          r.exit_code == 0 and r.files.get("t.flat") == want_wall,
          "%d байт, шагов=%d" % (len(want_wall), r.steps))

    # 13. самохостинг: splice(splice.b2) -> enc -> brick -> pegen ->
    #     splice.exe (круг на новых артефактах)
    h = dict(kh)
    r0 = run_sp(["splice.b2", "t_flat.b2"], host10)
    h["s.b2"] = r0.files.get("t_flat.b2", b"")
    h["s.peg"] = open(os.path.join(KERNEL_DIR, "splice.peg"), "rb").read()
    h["brick.exe"] = open(BRICK_EXE, "rb").read()
    h["pegen.exe"] = open(PEGEN_EXE, "rb").read()
    r1 = lab_run.run_kv(ENC_EXE, ["s.b2", "s.brick"], h)
    art = open(os.path.join(KERNEL_DIR, "splice.brick"), "rb").read()
    h["s.brick"] = r1.files.get("s.brick", b"")
    r2 = lab_run.run_kv(BRICK_EXE, ["s.brick", "s.bin"], h)
    h["s.bin"] = r2.files.get("s.bin", b"")
    r3 = lab_run.run_kv(PEGEN_EXE, ["s.bin", "s.peg", "s.exe"], h)
    exe_art = open(os.path.join(KERNEL_DIR, "splice.exe"), "rb").read()
    check("самохостинг: круг -> splice.exe",
          r0.exit_code == 0 and r1.exit_code == 0 and
          r1.files.get("s.brick") == art and
          r2.exit_code == 0 and r3.exit_code == 0 and
          r3.files.get("s.exe") == exe_art,
          "шагов=%d+%d+%d+%d" % (r0.steps, r1.steps, r2.steps, r3.steps))

    # 14. регресс: корни enc.b2/brick.brick старыми инструментами конвейера
    bad = []
    for root, art_path in [
            ("l1-enc/enc.b2", "KERNEL/L1-ENC/enc.brick"),
            ("l1-brick/brick.brick", "KERNEL/L1-BRICK/brick.brick")]:
        want_flat = lab_splice.splice(root, kh)
        r = run_sp([root, "t.flat"], kh)
        got = r.files.get("t.flat", b"")
        if not (r.exit_code == 0 and got == want_flat):
            bad.append(root + " (splice)")
    # enc(плоско) == старым .brick (артефакты enc не менялись)
    for root, art_path in [
            ("l1-enc/enc.b2", "KERNEL/L1-ENC/enc.brick"),
            ("l2-wall/wall.b2", "KERNEL/L2-WALL/wall.brick")]:
        flat = lab_splice.splice(root, kh)
        r = lab_run.run_kv(ENC_EXE, ["t.b2", "t.brick"],
                           {"t.b2": flat})
        want_art = open(os.path.join(ROOT, art_path), "rb").read()
        if not (r.exit_code == 0 and
                r.files.get("t.brick") == want_art):
            bad.append(root + " (enc)")
    check("регресс: корни enc/brick/wall не изменились", not bad,
          "; ".join(bad))

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


def main():
    print("=== splice_build_lim: сборка M1-SPLICE (E6.4e-2) ===")
    stats = build()
    print("тело %d байт (0x%X); bss %d (0x%X); vsize 0x%X; exe %d байт"
          % (stats["body"], stats["body"], stats["bss"], stats["bss"],
             stats["vsize"], stats["exe"]))
    print("idata RVA 0x%X; iat RVA 0x%X; строк исходника %d"
          % (stats["idt"], stats["iat"], stats["lines"]))
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "splice.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 splice.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
