"""lab_t_l4.py — секция 16 батареи: оракул библиотеки L4 (SPEC/14, LIB-1).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; kfile читает реальные части KERNEL/L4-LIB).
Выход: проверки T-E8-01..11:
         (E8.1) T-E8-01..07 — оракул против якорей (прецедент E7.1);
         (E8.2a) T-E8-08..11 — диффтест ветви C: реальные байты части
         lib_c.uva компонуются с программой (оракулом splice в 08..10;
         самим splice.exe в 11), прогоняются (lab_vm.run_asm в 08..10;
         цепочкой uva.exe -> kernel.exe под эмуляцией в 11) —
         консоль/регистры/ловушки обязаны совпасть с оракулом lab_l4.
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
              в байт -> kernel.exe печатает == оракулу lab_l4.
"""
import lab_l4 as L
import lab_run
import lab_splice
import lab_vm
from lab_l4_cases import (DEC, I64, REV, STR, BUF, CPY, FILL,
                          CMP_U64, CMP_I64)

_ROOT = "projects/demo/demo.uva"       # программа-потребитель (виртуальный путь)
_LIB_C = "projects/demo/../../KERNEL/L4-LIB/lib_c.uva"   # !include SPEC/14 п. 2
_MEM = 4096                            # memsize программ диффтеста


def _flat(kfile, prog):
    """Композиция SPEC/14 п. 2: программа + !include lib_c.uva (оракул
    splice, SPEC/10 — та же семантика, что у splice.exe) -> плоский текст.
    Оракул не нормализует ../ лексически — ключ host = полный путь."""
    host = {_ROOT: prog.encode("utf-8"), _LIB_C: kfile("L4-LIB/lib_c.uva")}
    return lab_splice.splice(_ROOT, host).decode("utf-8")


def _run_c(kfile, prog):
    """Плоский текст -> прогон оракулом UNIVM (lab_vm.run_asm)."""
    return lab_vm.run_asm(_flat(kfile, prog))


def run(check, kpath, kfile, kernel_host):
    """Секция 16: T-E8-01..10 (оракул L4 + диффтест ветви C, SPEC/14)."""

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
