#!/usr/bin/env python3
"""enc_build.py — построитель модуля M1-ENC (частный инструмент ИИ, LAB/ai/;
НЕ часть системы UNIVERSAL: ядро воспроизводит артефакты само — см. батарею).

Вход:  scripts/enc_part1..3.txt (код M1-ENC на BRICK v2, M-строки).
Выход: KERNEL/L1-ENC/{enc.b2, enc.brick, enc.peg, enc.exe} + отчёт.
Функция: 1) генерирует данные (regtab/mnemtab/sizetab/errtab/строки/импорты/bss);
         2) enc.b2 = код + данные; enc.brick = lab_enc.normalize(enc.b2) (оракул
            E6.1, якоря сверены с реальными байтами);
         3) раскладка (метки/длины) -> enc.peg; тело = lab_brick.assemble;
            enc.exe = lab_pegen.wrap;
         4) прогоняет dev-тесты эмуляцией (справка, якоря, ошибки, демо-круг,
            самохостинг, концы строк, большой исходник).
"""
import os
import sys

# Размещение: LAB/ai/enc_build.py (частная зона ИИ; не часть системы).
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
LAB = os.path.join(ROOT, "LAB", "py")
SCR = os.path.join(ROOT, "LAB", "ai")     # части исходника enc_part*.txt
sys.path.insert(0, LAB)

import lab_enc              # noqa: E402
import lab_enc_cases        # noqa: E402
import lab_brick            # noqa: E402
import lab_pegen            # noqa: E402
import lab_run              # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L1-ENC")

# ---------------------------------------------------------------- данные
REGS = []
for _i, (_n64, _n32) in enumerate(zip(
        "rax rcx rdx rbx rsp rbp rsi rdi".split(),
        "eax ecx edx ebx esp ebp esi edi".split())):
    REGS.append((_n64, _i, 64))
    REGS.append((_n32, _i, 32))
for _i in range(8, 16):
    REGS.append(("r%d" % _i, _i, 64))
    REGS.append(("r%dd" % _i, _i, 32))
for _n, _i in zip("al cl dl bl".split(), range(4)):
    REGS.append((_n, _i, 8))
for _n, _i in zip("sil dil spl bpl".split(), (6, 7, 4, 5)):
    REGS.append((_n, _i, 8))
for _i in range(8, 16):
    REGS.append(("r%db" % _i, _i, 8))

F_ALU, F_SHIFT, F_JCC, F_MOV, F_MOVZX, F_LEA, F_TEST, F_CALL, F_UN, \
    F_PUSH, F_POP, F_JMP, F_SIM = range(1, 14)
MNEMS = []
for _n, _b, _e in [("add", 0x00, 0), ("or", 0x08, 1), ("and", 0x20, 4),
                   ("sub", 0x28, 5), ("xor", 0x30, 6), ("cmp", 0x38, 7)]:
    MNEMS.append((_n, F_ALU, _b | _e << 8))
for _n, _e in [("rol", 0), ("ror", 1), ("shl", 4), ("shr", 5), ("sar", 7)]:
    MNEMS.append((_n, F_SHIFT, _e))
for _n, _cc in [("jo", 0), ("jno", 1), ("jb", 2), ("jae", 3), ("jz", 4),
                ("jnz", 5), ("jbe", 6), ("ja", 7), ("js", 8), ("jns", 9),
                ("jl", 0xC), ("jge", 0xD), ("jle", 0xE), ("jg", 0xF),
                ("je", 4), ("jne", 5)]:
    MNEMS.append((_n, F_JCC, _cc))
MNEMS += [("mov", F_MOV, 0), ("movzx", F_MOVZX, 0), ("lea", F_LEA, 0),
          ("test", F_TEST, 0), ("call", F_CALL, 0),
          ("neg", F_UN, 0xF7 | 3 << 8), ("inc", F_UN, 0xFF | 0 << 8),
          ("dec", F_UN, 0xFF | 1 << 8),
          ("push", F_PUSH, 0x50), ("pop", F_POP, 0x58), ("jmp", F_JMP, 0),
          ("cdqe", F_SIM, 0x9848), ("ret", F_SIM, 0x00C3),
          ("int3", F_SIM, 0x00CC)]

SIZETAB = [("byte ", 8), ("word ", 16), ("dword ", 32), ("qword ", 64)]

USAGE = "U-L1-ENC CMDS: ENC <SRC.B2> <OUT.BRICK>\r\n"
ERRSTRS = [
    ("err_long", "U-L1-ENC ERR=LONG NAME\r\n"),
    ("err_opensrc", "U-L1-ENC ERR=OPEN SRC\r\n"),
    ("err_readsrc", "U-L1-ENC ERR=READ SRC\r\n"),
    ("err_bigsrc", "U-L1-ENC ERR=BIG SRC\r\n"),
    ("err_openout", "U-L1-ENC ERR=OPEN OUT\r\n"),
    ("err_writeout", "U-L1-ENC ERR=WRITE OUT\r\n"),
]
FMT_PFX = "U-L1-ENC ERR=FORMAT AT="
ERRTAB = [("usage_str", len(USAGE), 2), ("err_long", 24, 3),
          ("err_opensrc", 23, 4), ("err_readsrc", 23, 5),
          ("err_bigsrc", 22, 7), ("err_openout", 23, 8),
          ("err_writeout", 24, 9)]


def _lo_hi(name):
    b = name.encode()
    lo = int.from_bytes(b[:4].ljust(4, b"\0"), "little")
    hi = int.from_bytes(b[4:8].ljust(4, b"\0"), "little")
    return lo, hi


def db_lines(label, data, com):
    out = [":%s ; %s" % (label, com)]
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        out.append("DB " + " ".join("%02X" % b for b in chunk) +
                   (" ; %s" % com if i == 0 else ""))
    return out


def gen_data():
    L = []
    L.append("")
    L.append("; ===== K1-D011 таблица цифр =====")
    L.append(":digits")
    L.append("DB " + " ".join("%02X" % ord(c) for c in "0123456789ABCDEF"))
    L.append("")
    L.append("; ===== K1-D012 regtab: 48 записей {имя(8Б), длина, код|размер<<8, 0} =====")
    L.append(":regtab")
    for name, code, size in REGS:
        lo, hi = _lo_hi(name + " ")
        L.append("DD %X %X %X %X ; %s" % (lo, hi, len(name),
                                          code | size << 8, name))
    L.append("")
    L.append("; ===== K1-D013 mnemtab: 41 запись {имя(8Б), длина, семейство|параметр<<8, 0} =====")
    L.append(":mnemtab")
    for name, fam, param in MNEMS:
        lo, hi = _lo_hi(name)
        L.append("DD %X %X %X %X ; %s" % (lo, hi, len(name),
                                          fam | param << 8, name))
    L.append("")
    L.append("; ===== K1-D014 sizetab: 4 записи {ключ с пробелом(8Б), длина, размер, 0} =====")
    L.append(":sizetab")
    for kw, size in SIZETAB:
        lo, hi = _lo_hi(kw)
        L.append("DD %X %X %X %X ; %s" % (lo, hi, len(kw), size, kw.strip()))
    L.append("")
    L.append("; ===== K1-D015 errtab: 7 записей {RVA, длина, код, 0} =====")
    L.append(":errtab")
    for lbl, ln, code in ERRTAB:
        L.append("DD $%s %X %X 0 ; код %d" % (lbl, ln, code, code))
    L.append("")
    L.append("; ===== K1-D016 строки вывода =====")
    L += db_lines("usage_str", USAGE.encode(), "справка")
    for lbl, s in ERRSTRS:
        L += db_lines(lbl, s.encode(), lbl.replace("err_", ""))
    L += db_lines("fmt_pfx", FMT_PFX.encode(), "префикс FORMAT (23 Б)")
    L.append("")
    L.append("; ===== K1-D017 таблица импортов kernel32.dll =====")
    L.append(":idt")
    L.append("DD $intt 0 0 $dll_name $iat ; описатель импорта")
    L.append("DZ 14 ; терминатор IDT (нулевая запись)")
    L.append(":iat")
    L.append(":iat_gsh")
    L.append("DQ $hint_gsh ; IAT: GetStdHandle")
    L.append(":iat_wf")
    L.append("DQ $hint_wf ; IAT: WriteFile")
    L.append(":iat_ep")
    L.append("DQ $hint_ep ; IAT: ExitProcess")
    L.append(":iat_gcl")
    L.append("DQ $hint_gcl ; IAT: GetCommandLineA")
    L.append(":iat_cf")
    L.append("DQ $hint_cf ; IAT: CreateFileA")
    L.append(":iat_rf")
    L.append("DQ $hint_rf ; IAT: ReadFile")
    L.append(":iat_ch")
    L.append("DQ $hint_ch ; IAT: CloseHandle")
    L.append("DQ 0 ; IAT: терминатор")
    L.append(":intt")
    L.append("DQ $hint_gsh $hint_wf $hint_ep $hint_gcl $hint_cf $hint_rf"
             " $hint_ch 0 ; INT: копия IAT")
    L.append(":dll_name")
    L.append("DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00 ; kernel32.dll")
    L.append("DZ 1 ; чётность RVA hint-записей")
    L.append(":hint_gsh")
    L.append("DB 00 00 47 65 74 53 74 64 48 61 6E 64 6C 65 00 ; GetStdHandle")
    L.append("DZ 1 ; выравнивание")
    L.append(":hint_wf")
    L.append("DB 00 00 57 72 69 74 65 46 69 6C 65 00 ; WriteFile")
    L.append(":hint_ep")
    L.append("DB 00 00 45 78 69 74 50 72 6F 63 65 73 73 00 ; ExitProcess")
    L.append(":hint_gcl")
    L.append("DB 00 00 47 65 74 43 6F 6D 6D 61 6E 64 4C 69 6E 65 ; GetCommandLineA")
    L.append("DB 41 00 ; GetCommandLineA (конец)")
    L.append(":hint_cf")
    L.append("DB 00 00 43 72 65 61 74 65 46 69 6C 65 41 00 ; CreateFileA")
    L.append(":hint_rf")
    L.append("DB 00 00 52 65 61 64 46 69 6C 65 00 ; ReadFile")
    L.append("DZ 1 ; выравнивание")
    L.append(":hint_ch")
    L.append("DB 00 00 43 6C 6F 73 65 48 61 6E 64 6C 65 00 ; CloseHandle")
    L.append("")
    L.append("; ===== K1-D018 виртуальные нули (bss; загрузчик обнуляет) =====")
    for cell in ["hstdout", "written", "srclen", "curline", "wa_len"]:
        L.append(":%s" % cell)
        L.append("DBZ 8")
    for cell, sz in [("fname_in", 0x80), ("fname_out", 0x80),
                     ("opbuf", 0x80), ("linebuf", 0x40)]:
        L.append(":%s" % cell)
        L.append("DBZ %X" % sz)
    cells = ["el_p1", "el_p2", "el_b0", "el_b1", "el_cpos", "el_m1",
             "el_o0", "el_o1", "el_ps", "el_pe", "el_s", "el_e", "el_oi",
             "opcnt", "m_family", "m_param",
             "po_s", "po_e", "po_dst", "po_size", "po_q",
             "pm_s", "pm_e", "pm_dst", "pm_cs", "pm_cur", "pm_n",
             "pr_s", "pr_e", "pr_dst", "pr_p", "pr_len", "pr_slot",
             "pn_s", "pn_e",
             "mr_regv", "mr_mod", "mr_rm", "mr_sib", "mr_sibf", "mr_tlen",
             "mr_tail", "mr_x", "mr_b", "mr_modrm", "mr_slotf", "mr_sptr",
             "mr_slen", "mr_ssz",
             "er_opc", "er_flags", "er_imm", "er_pre",
             "rr_opc", "rr_src", "rr_dst", "rr_size",
             "si_size", "si_val", "im_opc", "im_len", "im_b0",
             "t_opc", "t_sub", "ei_val", "sh_immf"]
    for cell in cells:
        L.append(":%s" % cell)
        L.append("DBZ 8")
    for cell in ["seg_a", "seg_b"]:
        L.append(":%s" % cell)
        L.append("DBZ 20")
    L.append(":filebuf")
    L.append("DBZ 20100 ; текст входа (128 КиБ + сентинел)")
    L.append(":outbuf")
    L.append("DBZ 44010 ; вывод (<= вход x 23/11 + 1)")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- раскладка
def layout(brick_text):
    labels, cur, filelen = {}, 0, None
    for line in brick_text.splitlines():
        st = line.strip()
        if not st or st.startswith(";"):
            continue
        if st.startswith(":"):
            name = st[1:].split(";")[0].strip()
            labels[name] = cur
            continue
        toks = st.split()
        d = toks[0]
        body = []
        for t in toks[1:]:
            if t.startswith(";"):
                break
            body.append(t)
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


# ---------------------------------------------------------------- сборка
def build():
    parts = []
    for i in (1, 2, 3):
        with open(os.path.join(SCR, "enc_part%d.txt" % i),
                  encoding="utf-8") as f:
            parts.append(f.read().rstrip("\n"))
    src = "\n".join(parts) + "\n" + gen_data()
    assert len(src.encode("utf-8")) < 0x20000, "enc.b2 > 128 КиБ"
    brick = lab_enc.normalize(src)
    labels, filelen, vsize = layout(brick)
    assert filelen is not None
    body = lab_brick.assemble(brick.encode("utf-8"))
    assert len(body) == filelen, (len(body), filelen)
    idt_rva = labels["idt"] + 0x1000
    iat_rva = labels["iat"] + 0x1000
    peg = ("; UNIVERSAL / PEG v1 / слой L1 / модуль M1-ENC\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg>"
           " <out.exe>\n"
           "!module enc\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n" % (idt_rva, iat_rva, vsize))
    exe = lab_pegen.wrap(body, peg)
    os.makedirs(KERNEL_DIR, exist_ok=True)
    for name, data in [("enc.b2", src.encode("utf-8")),
                       ("enc.brick", brick.encode("utf-8")),
                       ("enc.peg", peg.encode()),
                       ("enc.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)
    stats = dict(labels=labels, filelen=filelen, vsize=vsize,
                 idt=idt_rva, iat=iat_rva, body=len(body), exe=len(exe),
                 src=len(src.encode("utf-8")), lines=len(src.splitlines()))
    return stats


# ---------------------------------------------------------------- тесты
def run_enc(host, args):
    return lab_run.run_kv(os.path.join(KERNEL_DIR, "enc.exe"), args, host)


def dev_tests(stats):
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += cond is True or cond == 1
        fail += not (cond is True or cond == 1)
        print("[%s] %s %s" % ("OK " if cond else "FAIL", name, note))

    # 1. справка
    r = run_enc({}, [])
    check("справка", r.stdout == USAGE.encode() and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:44], r.exit_code))

    # 2. все якоря одним файлом
    synth = "\n".join(m for m, _ in lab_enc_cases.CASES) + "\n"
    want = lab_enc.normalize(synth)
    r = run_enc({"t.b2": synth.encode()}, ["t.b2", "t.brick"])
    check("якоря (%d) == оракул" % len(lab_enc_cases.CASES),
          r.exit_code == 0 and r.files.get("t.brick") == want.encode(),
          "шагов=%d" % r.steps)

    # 3. отвержение (ошибка на строке 3)
    bad = []
    for e in lab_enc_cases.ERRORS:
        text = "M ret\nM int3\n" + e + "\n"
        try:
            lab_enc.normalize(text)
            bad.append(e + " (принят оракулом)")
            continue
        except lab_enc.EncError as ex:
            want_out = ("U-L1-ENC ERR=" + str(ex) + "\r\n").encode()
        r = run_enc({"t.b2": text.encode()}, ["t.b2", "t.brick"])
        if not (r.exit_code == 6 and r.stdout == want_out):
            bad.append("%s: %r код=%s (ожидалось %r)" %
                       (e, r.stdout, r.exit_code, want_out))
    check("отвержение (%d)" % len(lab_enc_cases.ERRORS), not bad,
          "; ".join(bad[:2]))

    # 4. демо-круг настоящими инструментами
    h = {"d.b2": lab_enc_cases.DEMO_B2.encode(),
         "d.peg": lab_enc_cases.DEMO_PEG.encode(),
         "brick.exe": open(os.path.join(ROOT, "KERNEL/L1-BRICK/brick.exe"),
                           "rb").read(),
         "pegen.exe": open(os.path.join(ROOT, "KERNEL/L0-PEGEN/pegen.exe"),
                           "rb").read()}
    r1 = run_enc(h, ["d.b2", "d.brick"])
    h["d.brick"] = r1.files.get("d.brick", b"")
    r2 = lab_run.run_kv(os.path.join(ROOT, "KERNEL/L1-BRICK/brick.exe"),
                        ["d.brick", "d.bin"], h)
    h["d.bin"] = r2.files.get("d.bin", b"")
    r3 = lab_run.run_kv(os.path.join(ROOT, "KERNEL/L0-PEGEN/pegen.exe"),
                        ["d.bin", "d.peg", "d.exe"], h)
    h["d.exe"] = r3.files.get("d.exe", b"")
    r4 = lab_run.run_kv(os.path.join(KERNEL_DIR, "enc.exe"), [], {}) \
        if False else None
    fd = os.path.join(KERNEL_DIR, "enc_demo_tmp.exe")
    with open(fd, "wb") as f:
        f.write(h["d.exe"])
    r4 = lab_run.run_kv(fd, [], {})
    os.unlink(fd)
    check("демо-круг enc+brick+pegen -> U-ENC-OK",
          r1.exit_code == 0 and r2.exit_code == 0 and r3.exit_code == 0 and
          r4.stdout == b"U-ENC-OK\r\n" and r4.exit_code == 0,
          "%r шагов=%d+%d+%d+%d" % (r4.stdout[:20], r1.steps, r2.steps,
                                    r3.steps, r4.steps))

    # 5. самохостинг: enc(enc.b2) == enc.brick; brick+pegen -> enc.exe
    src = open(os.path.join(KERNEL_DIR, "enc.b2"), "rb").read()
    art = open(os.path.join(KERNEL_DIR, "enc.brick"), "rb").read()
    exe = open(os.path.join(KERNEL_DIR, "enc.exe"), "rb").read()
    h = {"e.b2": src, "e.peg": open(os.path.join(KERNEL_DIR, "enc.peg"),
                                    "rb").read(),
         "brick.exe": open(os.path.join(ROOT, "KERNEL/L1-BRICK/brick.exe"),
                           "rb").read(),
         "pegen.exe": open(os.path.join(ROOT, "KERNEL/L0-PEGEN/pegen.exe"),
                           "rb").read()}
    r1 = run_enc(h, ["e.b2", "e.brick"])
    check("самохостинг: enc(enc.b2) == enc.brick",
          r1.exit_code == 0 and r1.files.get("e.brick") == art,
          "шагов=%d" % r1.steps)
    h["e.brick"] = art
    r2 = lab_run.run_kv(os.path.join(ROOT, "KERNEL/L1-BRICK/brick.exe"),
                        ["e.brick", "e.bin"], h)
    h["e.bin"] = r2.files.get("e.bin", b"")
    r3 = lab_run.run_kv(os.path.join(ROOT, "KERNEL/L0-PEGEN/pegen.exe"),
                        ["e.bin", "e.peg", "e2.exe"], h)
    check("самохостинг: круг -> enc.exe",
          r2.exit_code == 0 and r3.exit_code == 0 and
          r3.files.get("e2.exe") == exe,
          "шагов=%d+%d" % (r2.steps, r3.steps))

    # 6. граничные концы строк
    edges = [b"", b"M ret", b"M ret\r\nM int3", b"M ret\rM int3", b"\n",
             b"H 48\r\n", b"  M ret  \n", b"M mov rax, 5 ; c\r\n"]
    bad = []
    for e in edges:
        try:
            want = lab_enc.normalize(e.decode("latin1")).encode("latin1")
        except lab_enc.EncError as ex:
            want = ("U-L1-ENC ERR=" + str(ex) + "\r\n").encode()
        r = run_enc({"t.b2": e}, ["t.b2", "t.brick"])
        if not (r.files.get("t.brick") == want):
            bad.append("%r: %r != %r" % (e, r.files.get("t.brick"), want))
    check("концы строк (%d случаев)" % len(edges), not bad,
          "; ".join(bad[:2]))

    # 7. большой исходник (~40 КиБ, смесь форм)
    import random
    rnd = random.Random(20261108)
    regs64 = "rax rcx rdx rbx rsi rdi r8 r9 r10 r11 r12 r13 r14 r15".split()
    regs32 = "eax ecx edx ebx esi edi r8d r9d r10d r11d r12d r13d r14d" \
             " r15d".split()
    lines = []
    while sum(len(l) + 1 for l in lines) < 40000:
        k = rnd.randrange(8)
        if k == 0:
            lines.append("M mov %s, %X" % (rnd.choice(regs64),
                                           rnd.randrange(0, 0x7FFFFFFF)))
        elif k == 1:
            lines.append("M add %s, %d" % (rnd.choice(regs32),
                                           rnd.randrange(-0x7F, 0x7F)))
        elif k == 2:
            lines.append("M mov %s, [%s+%X]" %
                         (rnd.choice(regs64), rnd.choice(regs64),
                          rnd.randrange(0, 0x100)))
        elif k == 3:
            lines.append("M movzx eax, byte [%s]" % rnd.choice(regs64))
        elif k == 4:
            lines.append("M cmp %s, %X" % (rnd.choice(regs64),
                                           rnd.randrange(0, 0xFFFF)))
        elif k == 5:
            lines.append("M test %s, %s" % (rnd.choice(regs32),
                                            rnd.choice(regs32)))
        elif k == 6:
            lines.append("M jz $lbl_%d" % rnd.randrange(100))
        else:
            lines.append("; комментарий %d" % rnd.randrange(1000))
    big = "\n".join(lines) + "\n"
    want = lab_enc.normalize(big)
    r = run_enc({"t.b2": big.encode()}, ["t.b2", "t.brick"])
    check("большой исходник (%d КиБ)" % (len(big) // 1024),
          r.exit_code == 0 and r.files.get("t.brick") == want.encode(),
          "строк=%d шагов=%d" % (len(lines), r.steps))
    return ok, fail


def main():
    stats = build()
    print("enc.b2: %d строк, %d байт" % (stats["lines"], stats["src"]))
    print("тело: %d байт (0x%X); vsize=0x%X; idt=0x%X iat=0x%X; exe=%d байт"
          % (stats["body"], stats["filelen"], stats["vsize"], stats["idt"],
             stats["iat"], stats["exe"]))
    ok, fail = dev_tests(stats)
    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
