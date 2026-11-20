"""lab_t_l4.py — секция 16 батареи: оракул библиотеки L4 (SPEC/14, LIB-1).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; kfile читает реальные части KERNEL/L4-LIB).
Выход: проверки T-E8-01..16 (+ делегирование T-E8-17..21):
         (E8.1) T-E8-01..07 — оракул против якорей (прецедент E7.1);
         (E8.2a) T-E8-08..11 — диффтест ветви C: реальные байты части
         lib_c.uva компонуются с программой (оракулом splice в 08..10;
         самим splice.exe в 11), прогоняются (lab_vm.run_asm в 08..10;
         цепочкой uva.exe -> kernel.exe под эмуляцией в 11) —
         консоль/регистры/ловушки обязаны совпасть с оракулом lab_l4;
         (E8.2b) T-E8-12..16 — диффтест ветви N (числа): реальные байты
         lib_n.uva; программа включает ОБЕ части (N002/N003 вызывают
         кирпичи C — зависимость ветвей); значения шире imm32 грузятся
         из .data через ldq; r13 = sp ставит программа (кирпичи N
         сохраняют адрес буфера в слоте [sp-8, sp) — конвенция
         SPEC/12 п. 3.4; баланс стека проверяет T-E8-15);
         (E8.2c) T-E8-17..21 — диффтест ветви S (строки) — ДЕЛЕГИРОВАН
         в lab_t_l4_s.py (лимит 500 строк секции 16; прецедент
         lab_t_wallself_final.py — секция 12b; вызов — в конце run).
Функция: сверка оракула lab_l4.py с якорями lab_l4_cases.py
         (третий свидетель — ручные литералы):
         (1) T-E8-01 print_u64: 13 значений — края разрядов,
             степени двойки, максимум u64;
         (2) T-E8-02 print_i64: 6 значений — край -2^63, -1, -10;
         (3) T-E8-03 u64_to_dec_rev: реверс-порядок цифр + длина
             (0; 10; максимум — 20 цифр);
         (4) T-E8-04 str_len/str_out: до ПЕРВОГО NUL (хвост невидим);
         (5) T-E8-05 mem_copy: перекрытия обоих направлений по формуле
             SPEC/14 п. 4, n=0, копия сам на себя;
         (6) T-E8-06 mem_fill: r2 AND 255, n=0;
         (7) T-E8-07 консоль-кирпичи chr/crlf/buf/buf_rev + композиция
             печати числа с CRLF;
         (8) T-E8-08 диффтест chr_out/crlf_out: байт r1 AND 255
             (0x141 -> 'A'; 0; 255) + CRLF;
         (9) T-E8-09 диффтест buf_out/buf_out_rev: все якоря BUF
             (прямой и обратный порядок, len=0, палиндром);
         (10) T-E8-10 диффтест ABI: r5..r13/r15 нетронуты, r14 = memsize,
              консоль композиции == оракулу;
         (11) T-E8-11 сквозной круг ИНСТРУМЕНТАМИ (эмуляция): splice.exe
              склеивает !include -> uva.exe == ассемблеру оракула байтом
              в байт -> kernel.exe печатает == оракулу lab_l4;
         (12) T-E8-12 диффтест u64_to_dec_rev: якоря REV — r1 = len и
              RAM-цифры после прогона (полный контракт карточки);
         (13) T-E8-13 диффтест print_u64: все якоря DEC + CRLF — консоль
              == оракулу И якорным литералам (CMP ⊂ DEC+CRLF);
         (14) T-E8-14 диффтест print_i64: все якоря I64 + CRLF — край
              -2^63, -1, -10 == оракулу и литералам;
         (15) T-E8-15 диффтест ABI ветви N: сентинелы r5..r12/r15 целы,
              r14 = memsize, sp = r13 СБАЛАНСИРОВАН (слоты сняты),
              RAM-след внутреннего N001 кирпича print_i64;
         (16) T-E8-16 сквозной круг ИНСТРУМЕНТАМИ ветви N: ДВЕ части
              (lib_c + lib_n) — splice.exe -> uva.exe -> kernel.exe,
              консоль == оракулу (0; -1; край -2^63);
         (17..21) T-E8-17..21 — в lab_t_l4_s.py (автономная ветвь S,
              self-contained; полный список — докстринг того файла):
              str_len/str_out на якорях STR, композиция ТРЁХ ветвей
              C+N+S, ABI с r13-сентинелом, сквозной круг с ОДНОЙ
              частью (splice.exe -> uva.exe -> kernel.exe).
"""
import lab_l4 as L
import lab_run
import lab_splice
import lab_t_l4_s
import lab_vm
from lab_l4_cases import (DEC, I64, REV, STR, BUF, CPY, FILL,
                          CMP_U64, CMP_I64)

_ROOT = "projects/demo/demo.uva"       # программа-потребитель (виртуальный путь)
_LIB_C = "projects/demo/../../KERNEL/L4-LIB/lib_c.uva"   # !include SPEC/14 п. 2
_LIB_N = "projects/demo/../../KERNEL/L4-LIB/lib_n.uva"   # ветвь N (E8.2b)
_MEM = 4096                            # memsize программ диффтеста
_SP = 4000                             # r13 = sp: слот стека N — RAM[3992..4000)
_BUF = 200                             # буфер цифр: RAM[200..220) (>= 20 Б)


def _data64(v):
    """u64 -> 8 байтов LE строкой .data (значения шире imm32 грузятся
    ldq — const умеет только знаковый imm32, SPEC/12 п. 5)."""
    return " ".join("%02X" % b for b in (v & 0xFFFFFFFFFFFFFFFF)
                    .to_bytes(8, "little"))


def _flat(kfile, prog):
    """Композиция SPEC/14 п. 2: программа + !include частей L4 (оракул
    splice, SPEC/10 — та же семантика, что у splice.exe) -> плоский
    текст. Хост содержит обе части (C и N): программа включает нужные
    ей; ветвь N зависит от C (print_* вызывают lib_chr_out/
    lib_buf_out_rev), поэтому N-программы включают ОБЕ строки !include
    (ветвь S — автономная: её диффтесты — lab_t_l4_s.py, своя
    композиция). Оракул не нормализует ../ лексически — ключ host =
    полный путь."""
    host = {_ROOT: prog.encode("utf-8"),
            _LIB_C: kfile("L4-LIB/lib_c.uva"),
            _LIB_N: kfile("L4-LIB/lib_n.uva")}
    return lab_splice.splice(_ROOT, host).decode("utf-8")


def _print_prog(vals, brick):
    """Программа печати всех значений .data + CRLF: значения грузятся
    ldq; курсор/шаг/конец — в СОХРАНЯЕМЫХ r5/r6/r7 (кирпичи обязаны
    вернуть их — само ABI проверяется выполнением цикла)."""
    lines = [".mem %d" % _MEM]
    lines += [".data " + _data64(v) for v in vals]
    lines += [
        "const r13, %d" % _SP,
        "const r14, %d" % _MEM,
        "const r5, 8",
        "const r6, 0",
        "const r7, %d" % (8 * len(vals)),
        "n_loop:",
        "ldq r1, r6+0",
        "const r2, %d" % _BUF,
        "call lib_%s" % brick,
        "call lib_crlf_out",
        "add r6, r6, r5",
        "lt r8, r6, r7",
        "jnz r8, n_loop",
        "halt 0",
        "!include ../../KERNEL/L4-LIB/lib_c.uva",
        "!include ../../KERNEL/L4-LIB/lib_n.uva",
    ]
    return "\n".join(lines) + "\n"


def _run_c(kfile, prog):
    """Плоский текст -> прогон оракулом UNIVM (lab_vm.run_asm)."""
    return lab_vm.run_asm(_flat(kfile, prog))


def run(check, kpath, kfile, kernel_host):
    """Секция 16: T-E8-01..16 + делегирование T-E8-17..21 в
    lab_t_l4_s.py (диффтесты ветвей C/N/S, SPEC/14)."""

    # T-E8-01: print_u64 == якорям DEC (десятичная запись u64)
    bad = []
    for v, want in DEC:
        got = L.print_u64(v)
        if got != want.encode("ascii"):
            bad.append("%d: %r != %r" % (v, got, want))
    check("T-E8-01 print_u64 == якорям (%d)" % len(DEC), not bad,
          "; ".join(bad[:2]))

    # T-E8-02: print_i64 == якорям I64 (знаковая запись)
    bad = []
    for v, want in I64:
        got = L.print_i64(v)
        if got != want.encode("ascii"):
            bad.append("%d: %r != %r" % (v, got, want))
    check("T-E8-02 print_i64 == якорям (%d)" % len(I64), not bad,
          "; ".join(bad[:2]))

    # T-E8-03: u64_to_dec_rev == якорям REV (реверс цифр + длина)
    bad = []
    for v, rev, ln in REV:
        got, gotln = L.u64_to_dec_rev(v)
        if got != rev.encode("ascii") or gotln != ln:
            bad.append("%d: %r/%d != %r/%d" % (v, got, gotln, rev, ln))
    check("T-E8-03 u64_to_dec_rev == якорям (%d)" % len(REV), not bad,
          "; ".join(bad[:2]))

    # T-E8-04: str_len/str_out == якорям STR (до первого NUL)
    bad = []
    for full, want, ln in STR:
        got_out, got_len = L.str_out(full), L.str_len(full)
        if got_out != want.encode("ascii") or got_len != ln:
            bad.append("%r: out=%r/%d != %r/%d"
                       % (full, got_out, got_len, want, ln))
    check("T-E8-04 str_len/str_out == якорям (%d)" % len(STR), not bad,
          "; ".join(bad[:2]))

    # T-E8-05: mem_copy == якорям CPY (формула по возрастанию)
    bad = []
    for init, dst, src, n, want in CPY:
        got = L.mem_copy(bytearray(init), dst, src, n)
        if bytes(got) != want:
            bad.append("dst=%d src=%d n=%d: %r != %r"
                       % (dst, src, n, bytes(got), want))
    check("T-E8-05 mem_copy == якорям (%d, вкл. перекрытия)" % len(CPY),
          not bad, "; ".join(bad[:2]))

    # T-E8-06: mem_fill == якорям FILL (r2 AND 255)
    bad = []
    for init, dst, b, n, want in FILL:
        got = L.mem_fill(bytearray(init), dst, b, n)
        if bytes(got) != want:
            bad.append("dst=%d b=%X n=%d: %r != %r"
                       % (dst, b, n, bytes(got), want))
    check("T-E8-06 mem_fill == якорям (%d)" % len(FILL), not bad,
          "; ".join(bad[:2]))

    # T-E8-07: консоль-кирпичи + композиция печати числа с CRLF
    bad = []
    if L.chr_out(0x141) != b"A" or L.chr_out(0) != b"\x00":
        bad.append("chr_out: AND 255")
    if L.crlf_out() != b"\r\n":
        bad.append("crlf_out")
    for buf, direct, rev in BUF:
        if L.buf_out(buf) != direct.encode("ascii") \
                or L.buf_out_rev(buf) != rev.encode("ascii"):
            bad.append("buf %r" % buf)
    for v, want in CMP_U64:
        got = L.print_u64(v) + L.crlf_out()
        if got != want.encode("ascii"):
            bad.append("cmp %d: %r != %r" % (v, got, want))
    for v, want in CMP_I64:
        got = L.print_i64(v) + L.crlf_out()
        if got != want.encode("ascii"):
            bad.append("cmp %d: %r != %r" % (v, got, want))
    check("T-E8-07 консоль-кирпичи + композиция (%d+%d+%d)"
          % (len(BUF), len(CMP_U64), len(CMP_I64)), not bad,
          "; ".join(bad[:2]))

    # T-E8-08: диффтест chr_out/crlf_out — lib_c.uva == оракулу
    prog = (
        ".mem %d\n"
        "const r14, %d\n"
        "const r1, 321\n"                # 0x141 -> байт 0x41 'A' (AND 255)
        "call lib_chr_out\n"
        "const r1, 0\n"
        "call lib_chr_out\n"
        "const r1, 255\n"
        "call lib_chr_out\n"
        "call lib_crlf_out\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
    ) % (_MEM, _MEM)
    r = _run_c(kfile, prog)
    want = L.chr_out(321) + L.chr_out(0) + L.chr_out(255) + L.crlf_out()
    check("T-E8-08 диффтест C: chr_out/crlf_out (splice+run_asm)",
          r.trap == 0 and r.exit_code == 0 and r.console == want,
          "trap=%d code=%d console=%r != %r"
          % (r.trap, r.exit_code, r.console, want))

    # T-E8-09: диффтест buf_out/buf_out_rev — все якоря BUF (+ len=0)
    bad = []
    for buf, direct, rev in BUF:
        lines = [".mem %d" % _MEM]
        if buf:                          # пустой буфер — без .data (нет байтов)
            lines.append(".data " + " ".join("%02X" % b for b in buf))
        lines += [
            "const r14, %d" % _MEM,
            "const r1, 0",
            "const r2, %d" % len(buf),
            "call lib_buf_out",
            "const r1, 0",
            "const r2, %d" % len(buf),
            "call lib_buf_out_rev",
            "call lib_crlf_out",
            "halt 0",
            "!include ../../KERNEL/L4-LIB/lib_c.uva",
        ]
        r = _run_c(kfile, "\n".join(lines) + "\n")
        want = (direct.encode("latin1") + rev.encode("latin1")
                + L.crlf_out())
        if r.trap != 0 or r.exit_code != 0 or r.console != want:
            bad.append("%r: trap=%d code=%d %r != %r"
                       % (buf, r.trap, r.exit_code, r.console, want))
    check("T-E8-09 диффтест C: buf_out/buf_out_rev == якорям BUF (%d)"
          % len(BUF), not bad, "; ".join(bad[:2]))

    # T-E8-10: диффтест ABI — сохраняемые r5..r13/r15 нетронуты, r14 жив
    prog = (
        ".mem %d\n"
        ".data 41 42 43 44 45\n"         # "ABCDE" -> RAM[0..5)
        "const r14, %d\n"
        "const r5, 5005\n"
        "const r6, 5006\n"
        "const r7, 5007\n"
        "const r8, 5008\n"
        "const r9, 5009\n"
        "const r10, 5010\n"
        "const r11, 5011\n"
        "const r12, 5012\n"
        "const r13, 5013\n"
        "const r15, 5015\n"
        "const r1, 321\n"                # 0x141 -> 'A'
        "call lib_chr_out\n"
        "call lib_crlf_out\n"
        "const r1, 0\n"                  # r1/r2 затёрты вызовом — перезагружаем
        "const r2, 5\n"                  # (ABI: r1..r4 — временные)
        "call lib_buf_out\n"
        "const r1, 0\n"
        "const r2, 5\n"
        "call lib_buf_out_rev\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
    ) % (_MEM, _MEM)
    r = _run_c(kfile, prog)
    want = (L.chr_out(321) + L.crlf_out() + L.buf_out(b"ABCDE")
            + L.buf_out_rev(b"ABCDE"))
    saved = [r.regs[i] for i in range(5, 14)] + [r.regs[15]]
    want_saved = list(range(5005, 5014)) + [5015]
    ok = (r.trap == 0 and r.exit_code == 0 and r.console == want
          and saved == want_saved and r.regs[14] == _MEM)
    check("T-E8-10 диффтест C: ABI — r5..r13/r15 сохранены, r14 = memsize",
          ok, "trap=%d code=%d console=%r saved=%r r14=%d"
          % (r.trap, r.exit_code, r.console, saved, r.regs[14]))

    # T-E8-11: сквозной круг инструментами (эмуляция) — композиция
    # SPEC/14 п. 2 реальным splice.exe, сборка реальным uva.exe
    # (байты .UP == ассемблеру оракула), исполнение реальным kernel.exe
    # (консоль == оракулу библиотеки). Ядро не пересобирается —
    # библиотека внешние исходники (правило R7).
    prog = (
        ".mem %d\n"
        ".data 41 42 43 44 45\n"          # "ABCDE" -> RAM[0..5)
        "const r14, %d\n"
        "const r1, 321\n"                 # 0x141 -> 'A' (AND 255)
        "call lib_chr_out\n"
        "call lib_crlf_out\n"
        "const r1, 0\n"
        "const r2, 5\n"
        "call lib_buf_out\n"
        "const r1, 0\n"
        "const r2, 5\n"
        "call lib_buf_out_rev\n"
        "call lib_crlf_out\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
    ) % (_MEM, _MEM)
    want = (L.chr_out(321) + L.crlf_out() + L.buf_out(b"ABCDE")
            + L.buf_out_rev(b"ABCDE") + L.crlf_out())
    try:
        rs = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                            ["projects/demo/demo.uva", "demo.flat.uva"],
                            {_ROOT: prog.encode("utf-8"),
                             _LIB_C: kfile("L4-LIB/lib_c.uva")})
        flat = rs.files.get("demo.flat.uva", b"")
        ru = lab_run.run_kv(kpath("L3-UVA/uva.exe"),
                            ["demo.flat.uva", "demo.up"],
                            {"demo.flat.uva": flat})
        up = ru.files.get("demo.up", b"")
        rk = lab_run.run_kv(kpath("L3-UNIVM/kernel.exe"), ["demo.up"],
                            {"demo.up": up})
        ok = (rs.exit_code == 0 and ru.exit_code == 0
              and rk.exit_code == 0 and rk.stdout == want
              and up == lab_vm.assemble(flat.decode("utf-8")))
        detail = ("splice=%d uva=%d kernel=%d up=%dБ console=%r"
                  % (rs.exit_code, ru.exit_code, rk.exit_code,
                     len(up), rk.stdout))
    except Exception as e:                     # noqa: BLE001 — любая = провал
        ok, detail = False, "EXC:" + repr(e)
    check("T-E8-11 круг инструментами: splice->uva->kernel == оракулу",
          ok, detail)

    # T-E8-12: диффтест N: u64_to_dec_rev — якоря REV (r1 = len + RAM)
    bad = []
    for v, rev, ln in REV:
        prog = (
            ".mem %d\n"
            ".data %s\n"                # значение u64 -> RAM[0..8) (LE)
            "const r13, %d\n"           # sp — ветвь N использует стек
            "const r2, 0\n"
            "ldq r1, r2+0\n"            # r1 = значение (шире imm32)
            "const r2, %d\n"            # буфер цифр
            "call lib_u64_to_dec_rev\n"
            "halt 0\n"
            "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
            "!include ../../KERNEL/L4-LIB/lib_n.uva\n"
        ) % (_MEM, _data64(v), _SP, _BUF)
        r = _run_c(kfile, prog)
        digits = r.mem[_BUF:_BUF + ln]
        if r.trap != 0 or r.exit_code != 0 or r.regs[1] != ln \
                or digits != rev.encode("ascii"):
            bad.append("%d: trap=%d len=%d mem=%r != %r/%d"
                       % (v, r.trap, r.regs[1], digits.decode("latin1"),
                          rev, ln))
    check("T-E8-12 диффтест N: u64_to_dec_rev == якорям REV (%d; RAM+r1)"
          % len(REV), not bad, "; ".join(bad[:2]))

    # T-E8-13: диффтест N: print_u64 — все якоря DEC + CRLF (CMP ⊂ DEC)
    vals = [v for v, _w in DEC]
    r = _run_c(kfile, _print_prog(vals, "print_u64"))
    want = b"".join(L.print_u64(v) + L.crlf_out() for v in vals)
    anchor = b"".join((s + "\r\n").encode("ascii") for _v, s in DEC)
    check("T-E8-13 диффтест N: print_u64 == оракулу и якорям DEC (%d)"
          % len(vals),
          r.trap == 0 and r.exit_code == 0 and r.console == want
          and r.console == anchor,
          "trap=%d code=%d console=%r" % (r.trap, r.exit_code,
                                           r.console[:40]))

    # T-E8-14: диффтест N: print_i64 — все якоря I64 + CRLF (край -2^63)
    vals = [v for v, _w in I64]
    r = _run_c(kfile, _print_prog(vals, "print_i64"))
    want = b"".join(L.print_i64(v) + L.crlf_out() for v in vals)
    anchor = b"".join((s + "\r\n").encode("ascii") for _v, s in I64)
    check("T-E8-14 диффтест N: print_i64 == оракулу и якорям I64 (%d)"
          % len(vals),
          r.trap == 0 and r.exit_code == 0 and r.console == want
          and r.console == anchor,
          "trap=%d code=%d console=%r" % (r.trap, r.exit_code,
                                           r.console[:40]))

    # T-E8-15: диффтест N: ABI — сентинелы r5..r12/r15, sp = r13 баланс
    prog = (
        ".mem %d\n"
        ".data %s\n"                # 12345
        ".data %s\n"                # 2^64-10 (знаковое -10)
        "const r13, %d\n"
        "const r14, %d\n"
        "const r5, 5005\n"
        "const r6, 5006\n"
        "const r7, 5007\n"
        "const r8, 5008\n"
        "const r9, 5009\n"
        "const r10, 5010\n"
        "const r11, 5011\n"
        "const r12, 5012\n"
        "const r15, 5015\n"
        "const r2, 0\n"
        "ldq r1, r2+0\n"
        "const r2, %d\n"
        "call lib_print_u64\n"     # 12345
        "const r2, 8\n"
        "ldq r1, r2+0\n"
        "const r2, %d\n"
        "call lib_print_i64\n"     # -10
        "call lib_crlf_out\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
        "!include ../../KERNEL/L4-LIB/lib_n.uva\n"
    ) % (_MEM, _data64(12345), _data64(18446744073709551606), _SP, _MEM,
         _BUF, _BUF)
    r = _run_c(kfile, prog)
    want = (L.print_u64(12345) + L.print_i64(18446744073709551606)
            + L.crlf_out())
    saved = [r.regs[i] for i in range(5, 13)]
    ok = (r.trap == 0 and r.exit_code == 0 and r.console == want
          and saved == list(range(5005, 5013)) and r.regs[13] == _SP
          and r.regs[14] == _MEM and r.regs[15] == 5015
          and r.mem[_BUF:_BUF + 2] == b"01")   # цифры 10 — внутренний N001 print_i64
    check("T-E8-15 диффтест N: ABI — r5..r12/r15 сохранены, sp сбалансирован",
          ok, "trap=%d code=%d console=%r saved=%r r13=%d r14=%d"
          % (r.trap, r.exit_code, r.console, saved, r.regs[13],
             r.regs[14]))

    # T-E8-16: сквозной круг инструментами ветви N — ДВЕ части (C+N):
    # splice.exe склеивает обе !include -> uva.exe (байты .UP ==
    # ассемблеру оракула) -> kernel.exe (stdout == оракулу lab_l4).
    # Ядро не пересобирается — библиотека внешние исходники (R7).
    prog = (
        ".mem %d\n"
        ".data %s\n"                # 0
        ".data %s\n"                # 2^64-1
        ".data %s\n"                # 2^63 — край i64
        "const r13, %d\n"
        "const r14, %d\n"
        "const r2, 0\n"
        "ldq r1, r2+0\n"
        "const r2, %d\n"
        "call lib_print_u64\n"      # "0"
        "const r2, 8\n"
        "ldq r1, r2+0\n"
        "const r2, %d\n"
        "call lib_print_i64\n"     # "-1"
        "const r2, 16\n"
        "ldq r1, r2+0\n"
        "const r2, %d\n"
        "call lib_print_i64\n"     # "-9223372036854775808" (край)
        "call lib_crlf_out\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
        "!include ../../KERNEL/L4-LIB/lib_n.uva\n"
    ) % (_MEM, _data64(0), _data64(18446744073709551615),
          _data64(9223372036854775808), _SP, _MEM, _BUF, _BUF, _BUF)
    want = (L.print_u64(0) + L.print_i64(18446744073709551615)
            + L.print_i64(9223372036854775808) + L.crlf_out())
    try:
        rs = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                            ["projects/demo/demo.uva", "demo.flat.uva"],
                            {_ROOT: prog.encode("utf-8"),
                             _LIB_C: kfile("L4-LIB/lib_c.uva"),
                             _LIB_N: kfile("L4-LIB/lib_n.uva")})
        flat = rs.files.get("demo.flat.uva", b"")
        ru = lab_run.run_kv(kpath("L3-UVA/uva.exe"),
                            ["demo.flat.uva", "demo.up"],
                            {"demo.flat.uva": flat})
        up = ru.files.get("demo.up", b"")
        rk = lab_run.run_kv(kpath("L3-UNIVM/kernel.exe"), ["demo.up"],
                            {"demo.up": up})
        ok = (rs.exit_code == 0 and ru.exit_code == 0
              and rk.exit_code == 0 and rk.stdout == want
              and up == lab_vm.assemble(flat.decode("utf-8")))
        detail = ("splice=%d uva=%d kernel=%d up=%dБ console=%r"
                  % (rs.exit_code, ru.exit_code, rk.exit_code,
                     len(up), rk.stdout))
    except Exception as e:                     # noqa: BLE001 — любая = провал
        ok, detail = False, "EXC:" + repr(e)
    check("T-E8-16 круг инструментами N (2 части): splice->uva->kernel",
          ok, detail)

    # T-E8-17..21 — диффтесты ветви S (E8.2c): lab_t_l4_s.py
    # (выделен по лимиту 500 строк секции 16; прецедент —
    # lab_t_wallself_final.py, секция 12b; self-contained — своя
    # композиция _flat с тремя частями C/N/S)
    lab_t_l4_s.run(check, kpath, kfile, kernel_host)

