"""lab_t_l4_s.py — секция 16-S батареи: диффтесты ветви S (E8.2c).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; kfile читает реальные части KERNEL/L4-LIB);
         вызывается из lab_t_l4.run (секция 16 — конец, делегирование
         по лимиту 500 строк; прецедент lab_t_wallself_final.py —
         секция 12b). Self-contained: собственная композиция _flat
         (хост — все три части C/N/S) и прогон _run_c.
Выход: проверки T-E8-17..21 — диффтест ветви S (строки): реальные
         байты lib_s.uva; кирпичи атомарны и АВТОНОМНЫ (без
         зависимости от C — ОДНО !include; стек НЕ используется —
         r13 программе не нужен), r14 = memsize — только печатающему
         str_out; строки — байты .data (NUL-терминированные; строка
         без NUL кончается нулевой RAM за .data).
Функция: сверка реализации ветви S с оракулом lab_l4.py на якорях
         STR (lab_l4_cases.py):
         (17) T-E8-17 str_len — все якоря STR: r1 = длина (вкл. 0;
              хвост после NUL невидим; без NUL — до нулевой RAM),
              консоль пуста, r14/r13 программе НЕ нужны;
         (18) T-E8-18 str_out — все якоря STR: консоль == оракулу
              (байты до первого 0), r14 = memsize;
         (19) T-E8-19 композиция ТРЁХ ветвей (C+N+S — первая
              трёхчастная программа): «строка пробел длина CRLF»
              для всех якорей STR — str_out + chr_out + str_len +
              print_u64 + crlf_out == оракулу lab_l4;
         (20) T-E8-20 ABI — сентинелы r5..r13/r15 (r13 — сентинелом:
              ветвь S стек НЕ использует, r13 обязан вернуться
              НЕТРОНУТЫМ), r14 = memsize, RAM-слог длины после
              str_len;
         (21) T-E8-21 сквозной круг ИНСТРУМЕНТАМИ ветви S: ОДНА часть
              (lib_s.uva) — splice.exe -> uva.exe -> kernel.exe,
              консоль == оракулу (якоря 1/3/5: хвост после NUL
              невидим; строка без NUL — до нулевой RAM).
"""
import lab_l4 as L
import lab_run
import lab_splice
import lab_vm
from lab_l4_cases import STR

_ROOT = "projects/demo/demo.uva"       # программа-потребитель (виртуальный путь)
_LIB_C = "projects/demo/../../KERNEL/L4-LIB/lib_c.uva"   # !include SPEC/14 п. 2
_LIB_N = "projects/demo/../../KERNEL/L4-LIB/lib_n.uva"   # ветвь N (E8.2b)
_LIB_S = "projects/demo/../../KERNEL/L4-LIB/lib_s.uva"   # ветвь S (E8.2c)
_MEM = 4096                            # memsize программ диффтеста
_SP = 4000                             # r13 = sp: слот стека N — RAM[3992..4000)
_BUF = 200                             # буфер цифр: RAM[200..220) (>= 20 Б)
_LEN = 300                             # RAM-слог длины строки: [300..308)


def _hex2(bs):
    """Байты -> строка .data (hex2 через пробел; E7.4-3b)."""
    return " ".join("%02X" % b for b in bs)


def _flat(kfile, prog):
    """Композиция SPEC/14 п. 2 (дублирует lab_t_l4._flat — self-contained
    по лимиту 500 строк): хост — все три части (C, N, S): T-E8-19
    включает их все; S-программы — только lib_s. Оракул не нормализует
    ../ лексически — ключ host = полный путь."""
    host = {_ROOT: prog.encode("utf-8"),
            _LIB_C: kfile("L4-LIB/lib_c.uva"),
            _LIB_N: kfile("L4-LIB/lib_n.uva"),
            _LIB_S: kfile("L4-LIB/lib_s.uva")}
    return lab_splice.splice(_ROOT, host).decode("utf-8")


def _run_c(kfile, prog):
    """Плоский текст -> прогон оракулом UNIVM (lab_vm.run_asm)."""
    return lab_vm.run_asm(_flat(kfile, prog))


def run(check, kpath, kfile, kernel_host):
    """Секция 16-S: T-E8-17..21 (диффтест ветви S, E8.2c, SPEC/14)."""

    # T-E8-17: диффтест S: str_len — все якоря STR (r1 = длина;
    # консоль пуста — str_len НЕ печатающий кирпич, r14 не нужен)
    bad = []
    for full, want, ln in STR:
        prog = (
            ".mem %d\n"
            ".data %s\n"
            "const r1, 0\n"
            "call lib_str_len\n"
            "halt 0\n"
            "!include ../../KERNEL/L4-LIB/lib_s.uva\n"
        ) % (_MEM, _hex2(full))
        r = _run_c(kfile, prog)
        if r.trap != 0 or r.exit_code != 0 or r.regs[1] != ln \
                or r.console != b"":
            bad.append("%r: trap=%d len=%d console=%r"
                       % (full, r.trap, r.regs[1], r.console))
    check("T-E8-17 диффтест S: str_len == якорям STR (%d; r1=len)"
          % len(STR), not bad, "; ".join(bad[:2]))

    # T-E8-18: диффтест S: str_out — все якоря STR (консоль == оракулу;
    # хвост после NUL невидим; без NUL — до нулевой RAM за .data)
    bad = []
    for full, want, ln in STR:
        prog = (
            ".mem %d\n"
            ".data %s\n"
            "const r14, %d\n"
            "const r1, 0\n"
            "call lib_str_out\n"
            "halt 0\n"
            "!include ../../KERNEL/L4-LIB/lib_s.uva\n"
        ) % (_MEM, _hex2(full), _MEM)
        r = _run_c(kfile, prog)
        want_b = L.str_out(full)
        if r.trap != 0 or r.exit_code != 0 or r.console != want_b:
            bad.append("%r: trap=%d console=%r != %r"
                       % (full, r.trap, r.console, want_b))
    check("T-E8-18 диффтест S: str_out == оракулу на якорях STR (%d)"
          % len(STR), not bad, "; ".join(bad[:2]))

    # T-E8-19: диффтест S: композиция ТРЁХ ветвей (C+N+S) — «строка
    # пробел длина CRLF» для всех якорей: str_out + chr_out(' ') +
    # str_len + print_u64(len) + crlf_out; консоль == оракулу lab_l4.
    # Якоря кладутся в .data ПОДРЯД с байтом-разделителем 00 между
    # ними (якорь без NUL обязан иметь терминатор — иначе съел бы
    # хвост следующего якоря).
    lines = [".mem %d" % _MEM]
    addrs = []
    off = 0
    for full, want, ln in STR:
        addrs.append(off)
        lines.append(".data %s" % _hex2(full + b"\x00"))   # + разделитель
        off += len(full) + 1
    lines += [
        "const r13, %d" % _SP,              # sp — ветвь N в композиции
        "const r14, %d" % _MEM,
    ]
    for a, (full, want, ln) in zip(addrs, STR):
        lines += [
            "const r1, %d" % a,
            "call lib_str_out",             # S: строка
            "const r1, 32",
            "call lib_chr_out",             # C: пробел ' '
            "const r1, %d" % a,
            "call lib_str_len",             # S: r1 = длина
            "const r2, %d" % _BUF,
            "call lib_print_u64",           # N: длина цифрами
            "call lib_crlf_out",            # C: CRLF
        ]
    lines += [
        "halt 0",
        "!include ../../KERNEL/L4-LIB/lib_c.uva",
        "!include ../../KERNEL/L4-LIB/lib_n.uva",
        "!include ../../KERNEL/L4-LIB/lib_s.uva",
    ]
    r = _run_c(kfile, "\n".join(lines) + "\n")
    want = b"".join(L.str_out(f) + b" " + L.print_u64(ln) + L.crlf_out()
                    for f, _w, ln in STR)
    check("T-E8-19 диффтест S: композиция 3 ветвей C+N+S == оракулу (%d)"
          % len(STR),
          r.trap == 0 and r.exit_code == 0 and r.console == want,
          "trap=%d code=%d console=%r != %r" % (r.trap, r.exit_code,
                                                 r.console[:40], want[:40]))

    # T-E8-20: диффтест S: ABI — сентинелы r5..r13/r15 (r13 — СЕНТИНЕЛОМ:
    # ветвь S стек НЕ использует — r13 обязан вернуться нетронутым),
    # r14 = memsize, RAM-слог длины после str_len
    prog = (
        ".mem %d\n"
        ".data 55 2D 4C 34 2D 4F 4B 00 58 58\n"   # "U-L4-OK" + NUL + «XX»
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
        "const r1, 0\n"
        "call lib_str_out\n"                # консоль += "U-L4-OK"
        "const r1, 0\n"
        "call lib_str_len\n"                # r1 = 7 (NUL на 7-м байте)
        "const r2, %d\n"
        "stq r2+0, r1\n"                    # RAM[_LEN.._LEN+8) = 7 (LE)
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_s.uva\n"
    ) % (_MEM, _MEM, _LEN)
    r = _run_c(kfile, prog)
    saved = [r.regs[i] for i in range(5, 14)] + [r.regs[15]]
    want_saved = list(range(5005, 5014)) + [5015]
    ok = (r.trap == 0 and r.exit_code == 0 and r.console == b"U-L4-OK"
          and saved == want_saved and r.regs[14] == _MEM
          and bytes(r.mem[_LEN:_LEN + 8]) == (7).to_bytes(8, "little"))
    check("T-E8-20 диффтест S: ABI — r5..r13/r15 нетронуты (S без стека), "
          "r14 = memsize, RAM-слог len",
          ok, "trap=%d code=%d console=%r saved=%r r14=%d"
          % (r.trap, r.exit_code, r.console, saved, r.regs[14]))

    # T-E8-21: сквозной круг инструментами ветви S — ОДНА часть
    # (lib_s.uva; ветвь автономна — зависимостей нет): splice.exe
    # склеивает единственное !include -> uva.exe (байты .UP ==
    # ассемблеру оракула) -> kernel.exe (stdout == оракулу lab_l4).
    # Якоря 1/3/5: хвост после NUL невидим; якорь без NUL — последний
    # (кончается нулевой RAM за .data) — реальный контейнер .UP v2.
    # Ядро не пересобирается — библиотека внешние исходники (R7).
    pick = [STR[0], STR[2], STR[4]]  # «U-L4-OK\0XX», «AB\0CD\0», «1234567890»
    lines = [".mem %d" % _MEM]
    addrs = []
    off = 0
    for full, want, ln in pick:
        addrs.append(off)
        lines.append(".data %s" % _hex2(full + b"\x00"))
        off += len(full) + 1
    lines += ["const r14, %d" % _MEM]
    for a in addrs:
        lines += ["const r1, %d" % a, "call lib_str_out"]
    lines += ["halt 0", "!include ../../KERNEL/L4-LIB/lib_s.uva"]
    prog = "\n".join(lines) + "\n"
    want = b"".join(L.str_out(f) for f, _w, _l in pick)
    try:
        rs = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                            ["projects/demo/demo.uva", "demo.flat.uva"],
                            {_ROOT: prog.encode("utf-8"),
                             _LIB_S: kfile("L4-LIB/lib_s.uva")})
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
    check("T-E8-21 круг инструментами S (1 часть): splice->uva->kernel",
          ok, detail)
