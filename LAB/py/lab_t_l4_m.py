"""lab_t_l4_m.py — секция 16-M батареи: диффтесты ветви M (E8.2d).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; kfile читает реальные части KERNEL/L4-LIB);
         вызывается из lab_t_l4.run (секция 16 — делегирование ветвей
         S и M по лимиту 500 строк; прецедент lab_t_l4_s.py — E8.2c).
         Self-contained: собственная композиция _flat (хост — все
         четыре части C/N/S/M) и прогон _run_c.
Выход: проверки T-E8-22..26 — диффтест ветви M (память): реальные
         байты lib_m.uva; кирпичи атомарны и АВТОНОМНЫ (без
         зависимостей — ОДНО !include; стек НЕ используется — r13
         программе не нужен; консоль НЕ трогается — r14 не нужен:
         эффект наблюдается в RAM — сверка по r.mem ПОСЛЕ прогона).
Функция: сверка реализации ветви M с оракулом lab_l4.py на якорях
         CPY/FILL (lab_l4_cases.py) — тройной свидетель: программа ==
         оракулу (ВСЯ RAM), оракул == якорю (голова RAM):
         (22) T-E8-22 mem_copy — все якоря CPY: эффект RAM, вкл.
              перекрытия обоих направлений (формула SPEC/14 п. 4 —
              байт читается до записи), n = 0, копия сам на себя;
         (23) T-E8-23 mem_fill — все якоря FILL: эффект RAM
              (r2 AND 255: 0x141 -> 0x41), n = 0;
         (24) T-E8-24 композиция ЧЕТЫРЁХ ветвей (C+N+S+M — первая
              четырёхчастная программа): str_out + mem_fill + buf_out
              + mem_copy (перекрытие вперёд) + str_len + print_u64 +
              crlf_out — консоль == оракулу И ВСЯ RAM == модели
              оракула (вкл. цифры буфера N001 и стек-слоты [sp-16,sp));
         (25) T-E8-25 ABI — сентинелы r5..r13/r15 (r13 — сентинелом:
              ветвь M стек НЕ использует), r14 = memsize, эффект RAM
              copy+fill (источник копии цел — вся RAM == модели);
         (26) T-E8-26 сквозной круг ИНСТРУМЕНТАМИ ветви M: ОДНА часть
              (lib_m.uva) — splice.exe -> uva.exe -> kernel.exe;
              программа печатает эффекты копии/заполнения НАПРЯМУЮ
              (stb r14+0 — окно устройств, без других библиотек),
              stdout == модели оракула (ядро НЕ пересобирается, R7).
"""
import lab_l4 as L
import lab_run
import lab_splice
import lab_vm
from lab_l4_cases import CPY, FILL

_ROOT = "projects/demo/demo.uva"       # программа-потребитель (виртуальный путь)
_LIB_C = "projects/demo/../../KERNEL/L4-LIB/lib_c.uva"   # !include SPEC/14 п. 2
_LIB_N = "projects/demo/../../KERNEL/L4-LIB/lib_n.uva"   # ветвь N (E8.2b)
_LIB_S = "projects/demo/../../KERNEL/L4-LIB/lib_s.uva"   # ветвь S (E8.2c)
_LIB_M = "projects/demo/../../KERNEL/L4-LIB/lib_m.uva"   # ветвь M (E8.2d)
_MEM = 4096                            # memsize программ диффтеста
_SP = 4000                             # r13 = sp: слот стека N — RAM[3992..4000)
_BUF = 200                             # буфер цифр: RAM[200..220) (>= 20 Б)


def _hex2(bs):
    """Байты -> строка .data (hex2 через пробел; E7.4-3b)."""
    return " ".join("%02X" % b for b in bs)


def _flat(kfile, prog):
    """Композиция SPEC/14 п. 2 (как lab_t_l4_s._flat — self-contained
    по лимиту 500 строк): хост — все четыре части (C, N, S, M):
    T-E8-24 включает их все; M-программы — только lib_m. Оракул не
    нормализует ../ лексически — ключ host = полный путь."""
    host = {_ROOT: prog.encode("utf-8"),
            _LIB_C: kfile("L4-LIB/lib_c.uva"),
            _LIB_N: kfile("L4-LIB/lib_n.uva"),
            _LIB_S: kfile("L4-LIB/lib_s.uva"),
            _LIB_M: kfile("L4-LIB/lib_m.uva")}
    return lab_splice.splice(_ROOT, host).decode("utf-8")


def _run_c(kfile, prog):
    """Плоский текст -> прогон оракулом UNIVM (lab_vm.run_asm)."""
    return lab_vm.run_asm(_flat(kfile, prog))


def _ram_ok(r, model, head):
    """Тройной свидетель RAM: прогон чист (trap/code 0), программа ==
    оракулу (ВСЯ RAM), оракул == якорю (голова RAM == литералу)."""
    return (r.trap == 0 and r.exit_code == 0
            and bytes(r.mem) == bytes(model)
            and bytes(model[:len(head)]) == head)


def run(check, kpath, kfile, kernel_host):
    """Секция 16-M: T-E8-22..26 (диффтест ветви M, E8.2d, SPEC/14)."""

    # T-E8-22: диффтест M: mem_copy — все якоря CPY (эффект RAM по
    # r.mem ПОСЛЕ прогона; перекрытия обоих направлений, n = 0,
    # копия сам на себя — формула SPEC/14 п. 4: чтение до записи)
    bad = []
    for init, dst, src, n, want in CPY:
        prog = (
            ".mem %d\n"
            ".data %s\n"
            "const r1, %d\n"
            "const r2, %d\n"
            "const r3, %d\n"
            "call lib_mem_copy\n"
            "halt 0\n"
            "!include ../../KERNEL/L4-LIB/lib_m.uva\n"
        ) % (_MEM, _hex2(init), dst, src, n)
        r = _run_c(kfile, prog)
        model = bytearray(_MEM)
        model[0:len(init)] = init
        L.mem_copy(model, dst, src, n)
        if not _ram_ok(r, model, want):
            bad.append("dst=%d src=%d n=%d: trap=%d ram=%r != %r"
                       % (dst, src, n, r.trap,
                          bytes(r.mem[:len(want)]), want))
    check("T-E8-22 диффтест M: mem_copy == якорям CPY (%d; RAM, "
          "перекрытия)" % len(CPY), not bad, "; ".join(bad[:2]))

    # T-E8-23: диффтест M: mem_fill — все якоря FILL (эффект RAM;
    # r2 AND 255 — stb обрезает сам, SPEC/12 п. 5: 0x141 -> 0x41;
    # n = 0 — нет эффекта)
    bad = []
    for init, dst, b, n, want in FILL:
        prog = (
            ".mem %d\n"
            ".data %s\n"
            "const r1, %d\n"
            "const r2, %d\n"
            "const r3, %d\n"
            "call lib_mem_fill\n"
            "halt 0\n"
            "!include ../../KERNEL/L4-LIB/lib_m.uva\n"
        ) % (_MEM, _hex2(init), dst, b, n)
        r = _run_c(kfile, prog)
        model = bytearray(_MEM)
        model[0:len(init)] = init
        L.mem_fill(model, dst, b, n)
        if not _ram_ok(r, model, want):
            bad.append("dst=%d b=%X n=%d: trap=%d ram=%r != %r"
                       % (dst, b, n, r.trap,
                          bytes(r.mem[:len(want)]), want))
    check("T-E8-23 диффтест M: mem_fill == якорям FILL (%d; RAM, "
          "AND 255)" % len(FILL), not bad, "; ".join(bad[:2]))

    # T-E8-24: диффтест M: композиция ЧЕТЫРЁХ ветвей (C+N+S+M) — первая
    # четырёхчастная программа: str_out + mem_fill + buf_out +
    # mem_copy (перекрытие ВПЕРЁД) + buf_out + str_len + print_u64 +
    # crlf_out. Модель оракула: ВСЯ RAM после прогона (fill/copy —
    # формулы, цифры буфера N001 + стек-слоты N002/N001 — карточки).
    prog = (
        ".mem %d\n"
        ".data 55 2D 4C 34 2D 4D 20 00\n"    # "U-L4-M " + NUL -> RAM[0..8)
        ".data 41 42 43 44 45 46\n"          # "ABCDEF" -> RAM[8..14)
        "const r13, %d\n"                    # sp — ветвь N в композиции
        "const r14, %d\n"
        "const r1, 0\n"
        "call lib_str_out\n"                 # S: "U-L4-M "
        "const r1, 100\n"
        "const r2, 65\n"
        "const r3, 3\n"
        "call lib_mem_fill\n"                # M: RAM[100..103) = "AAA"
        "const r1, 100\n"
        "const r2, 3\n"
        "call lib_buf_out\n"                 # C: "AAA"
        "const r1, 9\n"
        "const r2, 8\n"
        "const r3, 3\n"
        "call lib_mem_copy\n"                # M: вперёд — "AAAAEF"
        "const r1, 8\n"
        "const r2, 6\n"
        "call lib_buf_out\n"                 # C: "AAAAEF"
        "const r1, 8\n"
        "call lib_str_len\n"                 # S: r1 = 6 (RAM[14] = 0)
        "const r2, %d\n"
        "call lib_print_u64\n"               # N: "6" (+ буфер и слоты)
        "call lib_crlf_out\n"                # C: CRLF
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_c.uva\n"
        "!include ../../KERNEL/L4-LIB/lib_n.uva\n"
        "!include ../../KERNEL/L4-LIB/lib_s.uva\n"
        "!include ../../KERNEL/L4-LIB/lib_m.uva\n"
    ) % (_MEM, _SP, _MEM, _BUF)
    r = _run_c(kfile, prog)
    model = bytearray(_MEM)
    model[0:8] = b"U-L4-M \x00"
    model[8:14] = b"ABCDEF"
    L.mem_fill(model, 100, 65, 3)            # M: RAM[100..103) = "AAA"
    L.mem_copy(model, 9, 8, 3)               # M: вперёд — "AAAAEF"
    ln = L.str_len(bytes(model[8:16]))       # S: длина (NUL за .data)
    digits, dlen = L.u64_to_dec_rev(ln)      # N001: цифры в буфер
    model[_BUF:_BUF + dlen] = digits
    model[_SP - 16:_SP - 8] = _BUF.to_bytes(8, "little")   # слот N001
    model[_SP - 8:_SP] = _BUF.to_bytes(8, "little")        # слот N002
    want = (L.str_out(bytes(model[0:8])) + L.buf_out(bytes(model[100:103]))
            + L.buf_out(bytes(model[8:14])) + L.print_u64(ln)
            + L.crlf_out())
    ok = (r.trap == 0 and r.exit_code == 0 and r.console == want
          and bytes(r.mem) == bytes(model))
    check("T-E8-24 диффтест M: композиция 4 ветвей C+N+S+M == оракулу "
          "(консоль + ВСЯ RAM)", ok,
          "trap=%d code=%d console=%r ram=%r" % (r.trap, r.exit_code,
                                                 r.console[:40],
                                                 bytes(r.mem[:16])))

    # T-E8-25: диффтест M: ABI — сентинелы r5..r13/r15 (r13 — СЕНТИНЕЛОМ:
    # ветвь M стек НЕ использует — r13 обязан вернуться нетронутым),
    # r14 = memsize; RAM-эффект copy+fill == модели (источник цел)
    prog = (
        ".mem %d\n"
        ".data 41 42 43 44 45 46\n"          # "ABCDEF" -> RAM[0..6)
        "const r5, 5005\n"
        "const r6, 5006\n"
        "const r7, 5007\n"
        "const r8, 5008\n"
        "const r9, 5009\n"
        "const r10, 5010\n"
        "const r11, 5011\n"
        "const r12, 5012\n"
        "const r13, 5013\n"                  # сентинел (M без стека)
        "const r14, %d\n"
        "const r15, 5015\n"
        "const r1, 10\n"
        "const r2, 0\n"
        "const r3, 3\n"
        "call lib_mem_copy\n"                # RAM[10..13) = "ABC"
        "const r1, 20\n"
        "const r2, 321\n"                    # 0x141 -> 0x41 'A' (AND 255)
        "const r3, 2\n"
        "call lib_mem_fill\n"                # RAM[20..22) = "AA"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_m.uva\n"
    ) % (_MEM, _MEM)
    r = _run_c(kfile, prog)
    model = bytearray(_MEM)
    model[0:6] = b"ABCDEF"
    L.mem_copy(model, 10, 0, 3)              # M: копия (источник цел)
    L.mem_fill(model, 20, 321, 2)            # M: 0x141 -> 0x41
    saved = [r.regs[i] for i in range(5, 14)] + [r.regs[15]]
    want_saved = list(range(5005, 5014)) + [5015]
    ok = (r.trap == 0 and r.exit_code == 0 and bytes(r.mem) == bytes(model)
          and saved == want_saved and r.regs[14] == _MEM)
    check("T-E8-25 диффтест M: ABI — r5..r13/r15 нетронуты (M без "
          "стека), r14 = memsize, RAM == модели", ok,
          "trap=%d code=%d saved=%r r14=%d ram=%r"
          % (r.trap, r.exit_code, saved, r.regs[14], bytes(r.mem[:24])))

    # T-E8-26: сквозной круг инструментами ветви M — ОДНА часть
    # (lib_m.uva; ветвь автономна): splice.exe склеивает единственное
    # !include -> uva.exe (байты .UP == ассемблеру оракула) ->
    # kernel.exe (stdout == модели оракула). Программа печатает
    # эффекты копии/заполнения НАПРЯМУЮ (stb r14+0 — окно устройств,
    # без других библиотек — автономность доказана кругом): копия
    # строки "M4-M-OK" -> RAM[100..107), заливка "---" -> RAM[200..203).
    # Ядро не пересобирается (R7).
    prog = (
        ".mem %d\n"
        ".data 4D 34 2D 4D 2D 4F 4B 00\n"    # "M4-M-OK" + NUL -> RAM[0..8)
        "const r14, %d\n"
        "const r1, 100\n"
        "const r2, 0\n"
        "const r3, 8\n"
        "call lib_mem_copy\n"                # M: копия -> RAM[100..108)
        "const r1, 200\n"
        "const r2, 45\n"
        "const r3, 3\n"
        "call lib_mem_fill\n"                # M: RAM[200..203) = "---"
        "const r5, 100\n"                    # курсор p (сохраняемый)
        "const r6, 1\n"                      # шаг
        "const r7, 107\n"                    # конец (эксклюзивно)
        "m_print:\n"
        "ldb r8, r5\n"
        "stb r14+0, r8\n"                    # консоль += RAM[p]
        "add r5, r5, r6\n"
        "lt r9, r5, r7\n"
        "jnz r9, m_print\n"
        "const r5, 200\n"
        "const r7, 203\n"
        "m_dash:\n"
        "ldb r8, r5\n"
        "stb r14+0, r8\n"
        "add r5, r5, r6\n"
        "lt r9, r5, r7\n"
        "jnz r9, m_dash\n"
        "halt 0\n"
        "!include ../../KERNEL/L4-LIB/lib_m.uva\n"
    ) % (_MEM, _MEM)
    model = bytearray(_MEM)
    model[0:8] = b"M4-M-OK\x00"
    L.mem_copy(model, 100, 0, 8)             # M: копия строки
    L.mem_fill(model, 200, 45, 3)            # M: "---"
    want = bytes(model[100:107]) + bytes(model[200:203])
    try:
        rs = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                            ["projects/demo/demo.uva", "demo.flat.uva"],
                            {_ROOT: prog.encode("utf-8"),
                             _LIB_M: kfile("L4-LIB/lib_m.uva")})
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
    check("T-E8-26 круг инструментами M (1 часть): splice->uva->kernel",
          ok, detail)
