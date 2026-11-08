#!/usr/bin/env python3
"""splice_build.py — построитель модуля M1-SPLICE (частный инструмент ИИ,
LAB/ai/; НЕ часть системы UNIVERSAL: ядро воспроизводит артефакты само —
см. батарею LAB/py/lab_verify.py).

Вход:  KERNEL/L1-SPLICE/splice.b2 (BRICK v2, написан вручную на M-строках).
Выход: KERNEL/L1-SPLICE/{splice.brick, splice.peg, splice.exe} + отчёт.
Функция: 1) splice.brick = lab_enc.normalize(splice.b2) (оракул E6.1,
            якоря сверены с реальными байтами);
         2) раскладка (метки/длины) -> splice.peg; тело = lab_brick.assemble;
            splice.exe = lab_pegen.wrap;
         3) dev-тесты эмуляцией: все CASES/ERRORS из lab_splice_cases
            (инструмент == якорям == оракулу), большой исходник,
            самосклейка splice(splice.b2) == splice.b2.
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


def layout(brick_text):
    """Карта меток/длин (пасс 1 SPEC/08) — как enc_build.layout."""
    labels, cur, filelen = {}, 0, None
    for line in brick_text.splitlines():
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
    # склейка корня с включениями (оракул; части лежат рядом с корнем)
    host = {"splice.b2": root.encode("utf-8")}
    for line in root.splitlines():
        if line.startswith("!include "):
            name = line[len("!include "):].strip()
            with open(os.path.join(KERNEL_DIR, name), "rb") as f:
                host[name] = f.read()
    src = lab_splice.splice("splice.b2", host).decode("utf-8")
    assert len(src.encode("utf-8")) < 0x20000, "splice.b2 > 128 КиБ"
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
def dev_tests(stats):
    results = []

    def check(name, ok, note=""):
        results.append((name, ok, note))
        print("[%s] %-56s %s" % ("OK" if ok else "FAIL", name, note))

    exe = os.path.join(KERNEL_DIR, "splice.exe")

    # 1) справка без аргументов
    r = lab_run.run_kv(exe, [], {})
    check("справка",
          r.stdout == b"U-L1-SPLICE CMDS: SPLICE <ROOT.SRC> <OUT.FLAT>\r\n"
          and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:48], r.exit_code))

    # 2) нормальные случаи: инструмент == якорь (и якорь == оракулу)
    bad = []
    steps = 0
    for name, root, host, want in lab_splice_cases.CASES:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = lab_run.run_kv(exe, [root, "t.flat"], host)
        steps += r.steps
        if not (r.exit_code == 0 and r.stdout == b"" and
                r.files.get("t.flat") == want):
            bad.append("%s: код=%s файл=%r" % (name, r.exit_code,
                                               (r.files.get("t.flat")
                                                or b"")[:24]))
    check("CASES: %d якорей (инструмент == якорям)"
          % len(lab_splice_cases.CASES), not bad,
          "; ".join(bad[:2]) if bad else "шагов=%d" % steps)

    # 3) ошибки: инструмент == якорям (код + строка)
    bad = []
    for name, root, host, code, msg in lab_splice_cases.ERRORS:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = lab_run.run_kv(exe, [root, "t.flat"], host)
        want_out = ("U-L1-SPLICE ERR=%s\r\n" % msg).encode()
        if not (r.exit_code == code and r.stdout == want_out):
            bad.append("%s: код=%s out=%r" % (name, r.exit_code,
                                              r.stdout[:40]))
    check("ERRORS: %d случаев (коды и строки)"
          % len(lab_splice_cases.ERRORS), not bad, "; ".join(bad[:2]))

    # 4) большой исходник (~24 КиБ)
    root, host, want = lab_splice_cases.big_case(24000)
    host = {k.decode("latin1") if isinstance(k, bytes) else k: v
            for k, v in host.items()}
    r = lab_run.run_kv(exe, [root, "t.flat"], host)
    check("большой исходник (%d КиБ)" % (len(want) // 1024),
          r.exit_code == 0 and r.files.get("t.flat") == want,
          "строк=%d шагов=%d" % (want.count(b"\n"), r.steps))

    # 5) склейка собственного разрезанного исходника == плоской форме
    root_b = open(os.path.join(KERNEL_DIR, "splice.b2"), "rb").read()
    host5 = {"splice.b2": root_b}
    for line in root_b.decode("utf-8").splitlines():
        if line.startswith("!include "):
            host5[line[9:].strip()] = open(
                os.path.join(KERNEL_DIR, line[9:].strip()), "rb").read()
    want5 = lab_splice.splice("splice.b2", host5)
    r = lab_run.run_kv(exe, ["splice.b2", "t.flat"], host5)
    check("склейка splice.b2 (корень+части) == плоской форме",
          r.exit_code == 0 and r.files.get("t.flat") == want5,
          "%d байт, шагов=%d" % (len(want5), r.steps))

    # 6) инструмент == оракулу на всех случаях (двойная сверка)
    bad = []
    for name, root, host, want in lab_splice_cases.CASES:
        got_oracle = lab_splice.splice(root, host)
        if got_oracle != want:
            bad.append(name + " (оракул)")
    for name, root, host, code, msg in lab_splice_cases.ERRORS:
        try:
            lab_splice.splice(root, host)
            bad.append(name + " (оракул: нет ошибки)")
        except lab_splice.SpliceError as e:
            if e.code != code or str(e) != msg:
                bad.append(name + " (оракул: код/строка)")
    check("оракул == якорям (двойная сверка)", not bad,
          "; ".join(bad[:2]))

    return results


def main():
    print("=== splice_build: сборка M1-SPLICE ===")
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
    results = dev_tests(stats)
    n = sum(1 for _n, ok, _t in results if ok)
    print("\nИТОГ: %d/%d %s" % (n, len(results), "OK" if n == len(results)
                               else "— ЕСТЬ ПРОВАЛЫ"))
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
