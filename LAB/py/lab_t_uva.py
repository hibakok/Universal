"""lab_t_uva.py — секция 15 батареи: ассемблер uva.exe (M3-UVA, E7.3).

Вход:  функции kpath/kfile/kernel_host от lab_verify (путь/чтение файлов
       KERNEL/), счётчик check.
Выход: проверки T-E7-19..24 (срезы E7.3-1..3 — каркас ассемблера .uva ->
       .UP на WALL + таблица мнемоник/регистры/кодировка F1 + F2 const/
       память): сборка конвейером инструментов под эмуляцией (фикс-пункт
       воспроизводимости артефактов), контракт CLI, диффтест с ассемблером
       оракула lab_vm.assemble байт-в-байт (halt-корпус среза 1 + F1-корпус
       среза 2 + F2-корпус среза 3: const/ldb/stb/ldq/stq, операнды памяти
       rA[+смещ] со знаком и hex, смещения без проверки диапазона —
       маскируются, ошибки операндов/регистров), отвержение с номерами
       строк (== AsmError.line оракула), контракт CODE0 (пустая программа)
       и сквозной круг uva -> kernel.exe (в т.ч. F2 с выводом в консоль
       через окно устройств).
Функция: доказать, что ассемблер uva.exe (KERNEL/L3-UVA) собирается из
         uva.wall самими инструментами репозитория байт-в-байт и
         повторяет ассемблер оракула на классе срезов 1-3 (.mem + halt +
         mov/АЛУ + const/память).
Срез 3: F2 кодируются целиком (const + ldb/stb/ldq/stq); операнд памяти
         rA[+смещ] — с бэктрекингом rN/r1X и накоплением mod 2^64 без
         проверки диапазона (маска младших 32 бит — при кодировании,
         как _i32 оракула); jmp/jnz + метки — срез E7.3-4 (диффтест на
         них не входит в корпус: валидные программы этих форм оракул
         собирает, а uva — ещё нет; строки ошибок совпадают на любом
         невалидном операнде этих строк — оба отвергают на строке).
"""
import os
import tempfile

import lab_l2
import lab_splice
import lab_run
import lab_vm

S_USE = b"U-L3-UVA CMDS: UVA <SRC.UVA> <OUT.UP>\r\n"
S_LONG = b"U-L3-UVA ERR=LONG NAME\r\n"
S_OSRC = b"U-L3-UVA ERR=OPEN SRC\r\n"
S_BIG = b"U-L3-UVA ERR=BIG SRC\r\n"
S_CODE0 = b"U-L3-UVA ERR=CODE0\r\n"


def build(kpath, kfile, kernel_host):
    """Сборка ассемблера из uva.wall конвейером (эмуляция инструментов).

    Возврат: (ok, artefacts dict, note) — b2/brick/bin/exe/steps или причина.
    """
    try:
        src = lab_splice.splice("L3-UVA/uva.wall", kernel_host())
        h = {"s.wall": src}
        r1 = lab_run.run_kv(kpath("L2-WALL/wall.exe"),
                            ["s.wall", "s.b2"], h)
        if r1.exit_code != 0:
            return False, None, "wall: код %s" % r1.exit_code
        h["s.b2"] = r1.files.get("s.b2", b"")
        r2 = lab_run.run_kv(kpath("L1-ENC/enc.exe"),
                            ["s.b2", "s.brick"], h)
        if r2.exit_code != 0:
            return False, None, "enc: код %s" % r2.exit_code
        h["s.brick"] = r2.files.get("s.brick", b"")
        r3 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                            ["s.brick", "s.bin"], h)
        if r3.exit_code != 0:
            return False, None, "brick: код %s" % r3.exit_code
        h["s.bin"] = r3.files.get("s.bin", b"")
        h["s.peg"] = kfile("L3-UVA/uva.peg")
        r4 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                            ["s.bin", "s.peg", "s.exe"], h)
        if r4.exit_code != 0 or "s.exe" not in r4.files:
            return False, None, "pegen: код %s" % r4.exit_code
        a = {"b2": h["s.b2"], "brick": h["s.brick"],
             "bin": h["s.bin"], "exe": r4.files["s.exe"],
             "steps": (r1.steps, r2.steps, r3.steps, r4.steps)}
        return True, a, "шаги %d+%d+%d+%d" % a["steps"]
    except Exception as e:                      # noqa: BLE001 — любая = провал
        return False, None, "EXC:" + repr(e)


def _fmt_line(line):
    return b"U-L3-UVA ERR=FORMAT AT=" + ("%04X" % line).encode() + b"\r\n"


def _uva(uexe, src, name="a.uva", out="b.up"):
    """Прогон ассемблера: (stdout, код, файл b.up или None)."""
    r = lab_run.run_kv(uexe, [name, out], {name: src})
    return r.stdout, r.exit_code, r.files.get(out)


# --- корпуса среза 1 (данные) ------------------------------------------
# успех: out.up == lab_vm.assemble(текст) байт-в-байт
OK_CASES = [
    (b"base", b".mem 4096\nhalt 0\n"),
    (b"mem 0", b".mem 0\nhalt 37\n"),
    (b"halt max i32", b".mem 64\nhalt 2147483647\n"),
    (b"halt -1", b".mem 64\nhalt -1\n"),
    (b"halt min", b".mem 64\nhalt -2147483648\n"),
    (b"halt max u32", b".mem 64\nhalt 4294967295\n"),
    (b"halt hex", b".mem 64\nhalt 0x10\n"),
    (b"halt -hex", b".mem 64\nhalt -0x10\n"),
    (b"halt +5", b".mem 64\nhalt +5\n"),
    (b"mem max", b".mem 67108864\nhalt 0\n"),
    (b"mem hex", b".mem 0x1000\nhalt 0\n"),
    (b"crlf", b".mem 8\r\nhalt 5\r\n"),
    (b"comments", b"; c\n.mem 8\n\n\nhalt 3\n; tail\n"),
    (b"no final lf", b".mem 8\nhalt 0"),
    (b"many halt", b".mem 16\nhalt 1\nhalt 2\nhalt 3\n"),
    (b"sep line", b".mem 8\n,,,\nhalt 0\n"),
    (b"comma sep", b".mem 8\nhalt , 0\n"),
    # F1 (срез E7.3-2): mov + 9 АЛУ, регистры r0..r15
    (b"mov", b".mem 8\nmov r1, r2\nhalt 0\n"),
    (b"mov r0 r15", b".mem 8\nmov r0, r15\nhalt 0\n"),
    (b"mov r15", b".mem 8\nmov r15, r15\nhalt 0\n"),
    (b"add", b".mem 8\nadd r1, r2, r3\nhalt 0\n"),
    (b"sub r15", b".mem 8\nsub r15, r15, r14\nhalt 0\n"),
    (b"alu all 9", b".mem 8\nadd r1, r2, r3\nsub r4, r5, r6\n"
                     b"and r7, r8, r9\nor r10, r11, r12\nxor r13, r14, r15\n"
                     b"shl r1, r2, r3\nshr r4, r5, r6\nlt r7, r8, r9\n"
                     b"eq r10, r11, r12\nhalt 0\n"),
    (b"mov + alu", b".mem 8\nmov r1, r2\nadd r3, r1, r2\nhalt 5\n"),
    (b"f1 no spaces", b".mem 8\nmov r1,r2\nadd r3,r1,r2\nhalt 5\n"),
    (b"f1 crlf", b".mem 8\r\nmov r1, r2\r\nhalt 0\r\n"),
    (b"f1 comment", b".mem 8\nmov r1, r2 ; c\nadd r3, r1, r2\nhalt 0\n"),
    (b"f1 no final lf", b".mem 8\nmov r1, r2\nhalt 0"),
    (b"f1 r10-15", b".mem 8\nmov r10, r11\nadd r12, r13, r14\n"
                     b"lt r15, r0, r1\nhalt 0\n"),
    # F2 (срез E7.3-3): const + ldb/stb/ldq/stq, операнды rA[+смещ]
    (b"const", b".mem 8\nconst r1, 5\nhalt 0\n"),
    (b"const r0", b".mem 8\nconst r0, 0\nhalt 0\n"),
    (b"const r15 -1", b".mem 8\nconst r15, -1\nhalt 0\n"),
    (b"const hex", b".mem 8\nconst r1, 0x10\nhalt 0\n"),
    (b"const -hex", b".mem 8\nconst r1, -0x10\nhalt 0\n"),
    (b"const max u32", b".mem 8\nconst r1, 4294967295\nhalt 0\n"),
    (b"const min i32", b".mem 8\nconst r1, -2147483648\nhalt 0\n"),
    (b"const +5", b".mem 8\nconst r1, +5\nhalt 0\n"),
    (b"ldb no off", b".mem 8\nldb r1, r2\nhalt 0\n"),
    (b"ldb +16", b".mem 8\nldb r1, r2+16\nhalt 0\n"),
    (b"ldb -8", b".mem 8\nldb r1, r2-8\nhalt 0\n"),
    (b"ldb r15", b".mem 8\nldb r1, r15\nhalt 0\n"),
    (b"ldb r15 hex", b".mem 8\nldb r0, r15+0x100\nhalt 0\n"),
    (b"ldb r11 bare", b".mem 8\nldb r1, r11\nhalt 0\n"),
    (b"ldb r10+5", b".mem 8\nldb r1, r10+5\nhalt 0\n"),
    (b"ldb r15+3", b".mem 8\nldb r1, r15+3\nhalt 0\n"),
    (b"ldb lead zeros", b".mem 8\nldb r1, r2+007\nhalt 0\n"),
    (b"ldb -0", b".mem 8\nldb r1, r2-0\nhalt 0\n"),
    (b"ldb hex AB", b".mem 8\nldb r1, r2+0xAB\nhalt 0\n"),
    (b"ldb hex ab", b".mem 8\nldb r1, r2+0xab\nhalt 0\n"),
    (b"stb", b".mem 8\nstb r2+16, r1\nhalt 0\n"),
    (b"stb -hex", b".mem 8\nstb r2-0x10, r1\nhalt 0\n"),
    (b"stq", b".mem 8\nstq r2-1, r15\nhalt 0\n"),
    (b"stq r11 bare", b".mem 8\nstq r11, r1\nhalt 0\n"),
    (b"ldq", b".mem 8\nldq r0, r15+3\nhalt 0\n"),
    (b"f2 all 5", b".mem 64\nconst r1, 7\nldb r2, r1+8\nstb r1+16, r2\n"
                     b"ldq r3, r1+24\nstq r1+32, r3\nhalt 0\n"),
    (b"f2+f1 mixed", b".mem 64\nconst r1, 5\nmov r2, r1\nadd r3, r1, r2\n"
                       b"stq r3, r1\nldb r4, r1\nhalt 9\n"),
    # смещения без проверки диапазона — маскируются (как _i32 оракула;
    # накопление mod 2^64 даёт те же младшие 32 бита)
    (b"off 2^31", b".mem 8\nldb r1, r2+2147483648\nhalt 0\n"),
    (b"off max u32", b".mem 8\nldb r1, r2+4294967295\nhalt 0\n"),
    (b"off 2^32", b".mem 8\nldb r1, r2+4294967296\nhalt 0\n"),
    (b"off huge", b".mem 8\nldb r1, r2+99999999999999999999\nhalt 0\n"),
    (b"off 2^32 hex", b".mem 8\nstb r2+0x100000000, r1\nhalt 0\n"),
    (b"stb off 2^32", b".mem 8\nstb r2+4294967296, r1\nhalt 0\n"),
    (b"f2 crlf", b".mem 8\r\nconst r1, 5\r\nstb r1+0, r1\r\nhalt 0\r\n"),
    (b"f2 comment", b".mem 8\nconst r1, 5 ; c\nstb r1+0, r1\nhalt 0\n"),
    (b"f2 no final lf", b".mem 8\nconst r1, 5\nstb r1+0, r1\nhalt 0"),
]

# отвержение: uva AT=XXXX == строка AsmError оракула (первая ошибка)
ERR_CASES = [
    ("пустой вход", b""),
    ("только комментарии", b"; c\n; c\n"),
    ("нет .mem", b"halt 0\nhalt 1\n"),
    ("нет .mem после комментария", b"; c\nhalt 0\n"),
    ("неизвестная мнемоника", b".mem 8\nhalt 0\nfoo r1\n"),
    ("мнемоника раньше .mem", b"foo r1, 5\nhalt 0\n"),
    ("лишний операнд halt", b".mem 8\nhalt 0\nhalt 1 2\n"),
    ("мало операндов", b".mem 8\nhalt\n"),
    ("плохое число", b".mem 8\nhalt abc\n"),
    ("вне imm32", b".mem 8\nhalt 9999999999\n"),
    ("hex без цифр", b".mem 8\nhalt 0x\n"),
    ("повторная .mem", b".mem 8\nhalt 0\n.mem 16\nhalt 1\n"),
    (".mem без числа", b".mem\nhalt 0\n"),
    (".mem два числа", b".mem 8 16\nhalt 0\n"),
    (".mem отрицательная", b".mem -1\nhalt 0\n"),
    (".mem сверх предела", b".mem 999999999\nhalt 0\n"),
    (".mem вне imm32", b".mem 9999999999\nhalt 0\n"),
    ("неизвестная директива", b".foo 8\nhalt 0\n"),
    ("не halt (r16)", b".mem 8\nconst r16, 5\nhalt 0\n"),
    ("заглавный HALT", b".mem 8\nHALT 0\n"),
    ("CR внутри строки", b".mem 8\rhalt 0\n"),
    # F1 (срез E7.3-2): счёт операндов, регистры r0..r15
    ("mov до .mem", b"mov r1, r2\nhalt 0\n"),
    ("mov 1 операнд", b".mem 8\nmov r1\nhalt 0\n"),
    ("mov 3 операнда", b".mem 8\nmov r1, r2, r3\nhalt 0\n"),
    ("mov плохой rd", b".mem 8\nmov r16, r1\nhalt 0\n"),
    ("mov плохой ra", b".mem 8\nmov r1, r16\nhalt 0\n"),
    ("alu 2 операнда", b".mem 8\nadd r1, r2\nhalt 0\n"),
    ("alu 4 операнда", b".mem 8\nadd r1, r2, r3, r4\nhalt 0\n"),
    ("alu плохой rb", b".mem 8\nadd r1, r2, r16\nhalt 0\n"),
    ("alu плохой ra", b".mem 8\nadd r1, r16, r2\nhalt 0\n"),
    ("alu плохой rd", b".mem 8\nadd r16, r1, r2\nhalt 0\n"),
    ("mov число", b".mem 8\nmov r1, 2\nhalt 0\n"),
    ("alu число-операнд", b".mem 8\nadd r1, r2, 3\nhalt 0\n"),
    ("регистр r01", b".mem 8\nmov r01, r2\nhalt 0\n"),
    ("регистр заглавный", b".mem 8\nmov R1, r2\nhalt 0\n"),
    ("регистр r0x", b".mem 8\nmov r0x, r1\nhalt 0\n"),
    ("регистр r-1", b".mem 8\nmov r-1, r1\nhalt 0\n"),
    ("мнемоника-префикс (haltx)", b".mem 8\nhaltx 0\nhalt 0\n"),
    ("mov + константа r16 позже", b".mem 8\nmov r1, r2\nconst r16, 5\n"),
    # F2 (срез E7.3-3): счёт операндов, регистры, операнды памяти
    ("const 1 операнд", b".mem 8\nconst r1\nhalt 0\n"),
    ("const 3 операнда", b".mem 8\nconst r1, 5, 6\nhalt 0\n"),
    ("const плохой reg", b".mem 8\nconst r16, 5\nhalt 0\n"),
    ("const плохое число", b".mem 8\nconst r1, abc\nhalt 0\n"),
    ("const вне imm32", b".mem 8\nconst r1, 9999999999\nhalt 0\n"),
    ("const число первым", b".mem 8\nconst 5, r1\nhalt 0\n"),
    ("const memop значением", b".mem 8\nconst r1, r2+5\nhalt 0\n"),
    ("const reg вместо числа", b".mem 8\nconst r1, r2\nhalt 0\n"),
    ("ldb 1 операнд", b".mem 8\nldb r1\nhalt 0\n"),
    ("ldb 3 операнда", b".mem 8\nldb r1, r2, r3\nhalt 0\n"),
    ("ldb плохой rd", b".mem 8\nldb r16, r2\nhalt 0\n"),
    ("ldb rd заглавный", b".mem 8\nldb R1, r2\nhalt 0\n"),
    ("ldb плохой memop", b".mem 8\nldb r1, x2\nhalt 0\n"),
    ("ldb число-адрес", b".mem 8\nldb r1, 5\nhalt 0\n"),
    ("ldb знак без числа", b".mem 8\nldb r1, r2+\nhalt 0\n"),
    ("ldb плюс-минус", b".mem 8\nldb r1, r2+-5\nhalt 0\n"),
    ("ldb двойной плюс", b".mem 8\nldb r1, r2++5\nhalt 0\n"),
    ("ldb r16 memop", b".mem 8\nldb r1, r16+5\nhalt 0\n"),
    ("ldb r01 memop", b".mem 8\nldb r1, r01+5\nhalt 0\n"),
    ("ldb r19 memop", b".mem 8\nldb r1, r19\nhalt 0\n"),
    ("ldb r3x memop", b".mem 8\nldb r1, r3x\nhalt 0\n"),
    ("ldb hex без цифр", b".mem 8\nldb r1, r2+0x\nhalt 0\n"),
    ("ldb 0X заглавная", b".mem 8\nldb r1, r2+0X10\nhalt 0\n"),
    ("ldb memop первым", b".mem 8\nldb r2+5, r1\nhalt 0\n"),
    ("memop с пробелом", b".mem 8\nldb r1, r2 +5\nhalt 0\n"),
    ("stb 1 операнд", b".mem 8\nstb r2\nhalt 0\n"),
    ("stb 3 операнда", b".mem 8\nstb r2+1, r1, r3\nhalt 0\n"),
    ("stb плохой memop", b".mem 8\nstb r2*, r1\nhalt 0\n"),
    ("stb плохой val reg", b".mem 8\nstb r2+1, r16\nhalt 0\n"),
    ("stq плохой memop", b".mem 8\nstq x1+2, r3\nhalt 0\n"),
    ("ldq 3 операнда", b".mem 8\nldq r1, r2, r3\nhalt 0\n"),
    ("f2 ошибка в 3-й строке", b".mem 8\nconst r1, 5\nldb r1, r2+\nhalt 0\n"),
    ("stq hex без цифр", b".mem 8\nstq r2+0x, r1\nhalt 0\n"),
]

# CODE0: .mem есть, инструкций нет (как make_up оракула)
CODE0_CASES = [
    ("только .mem", b".mem 8\n"),
    (".mem + комментарий", b".mem 8\n; comment\n\n"),
    (".mem + разделители", b".mem 8\n,,,\n"),
]


def run(check, kpath, kfile, kernel_host):
    """Секция 15: T-E7-19..24 (ассемблер uva.exe, срез E7.3-1)."""
    # T-E7-19: сборка — фикс-пункт: uva.wall -> (wall/enc/brick/pegen,
    # эмуляция) -> артефакты байт-в-байт; uva.b2 == оракулу WALL
    ok, a, note = build(kpath, kfile, kernel_host)
    if ok:
        oracle = lab_l2.compile_wall(
            lab_splice.splice("L3-UVA/uva.wall", kernel_host())
            .decode("latin1")).encode()
        ok = (a["b2"] == oracle == kfile("L3-UVA/uva.b2")
              and a["brick"] == kfile("L3-UVA/uva.brick")
              and a["exe"] == kfile("L3-UVA/uva.exe"))
    check("T-E7-19 фикс-пункт: uva.wall -> артефакты (байт-в-байт)",
          ok, note)
    if not ok:
        return                                    # дальше без uva нет смысла

    fd, uexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    try:
        with open(uexe, "wb") as f:
            f.write(a["exe"])

        # T-E7-20: CLI — справка (0/1/3 аргумента), длинное имя,
        # отсутствие входа, предел входа 65536/65537 (BIG SRC)
        big_ok = (b".mem 8\nhalt 0\n" + b";" + b"A" * (65536 - 16)
                  + b"\n")
        cases = [(b"no args", [], {}, S_USE, 2),
                 (b"one arg", ["a.uva"], {}, S_USE, 2),
                 (b"three args", ["a.uva", "b.up", "x"], {}, S_USE, 2),
                 (b"long", ["a" * 128], {}, S_LONG, 3),
                 (b"open src", ["x.uva", "y.up"], {}, S_OSRC, 4),
                 (b"big src", ["a.uva", "b.up"], {"a.uva": b"x" * 65537},
                  S_BIG, 7),
                 (b"max src ok", ["a.uva", "b.up"], {"a.uva": big_ok},
                  b"", 0)]
        bad = []
        for name, args, host, want, code in cases:
            r = lab_run.run_kv(uexe, args, host)
            if r.stdout != want or r.exit_code != code:
                bad.append("%s: %r код=%s" % (name,
                                              r.stdout[:32], r.exit_code))
        check("T-E7-20 CLI ассемблера: справка/имя/вход/предел (%d)"
              % len(cases), not bad, "; ".join(bad[:2]))

        # T-E7-21: корпус — uva(b.up) == ассемблеру оракула
        bad = []
        for name, src in OK_CASES:
            try:
                want = lab_vm.assemble(src.decode("latin1"))
            except lab_vm.AsmError:
                bad.append("%s: оракул отверг" % name)
                continue
            out, code, got = _uva(uexe, src)
            if code != 0 or got != want:
                bad.append("%s: код=%s %r" % (name, code,
                                              (got or b"")[:30]))
        check("T-E7-21 корпус: uva == оракулу assemble (%d)"
              % len(OK_CASES), not bad, "; ".join(bad[:2]))

        # T-E7-22: отвержение — AT=XXXX == строке AsmError оракула
        bad = []
        for name, src in ERR_CASES:
            try:
                lab_vm.assemble(src.decode("latin1"))
                bad.append("%s: оракул принял" % name)
                continue
            except lab_vm.AsmError as e:
                want_line = e.line
            out, code, got = _uva(uexe, src)
            if (code != 6 or got is not None
                    or out != _fmt_line(want_line)):
                bad.append("%s: %r код=%s (ждали строка %d)"
                           % (name, out[:30], code, want_line))
        check("T-E7-22 отвержение: строки == оракулу AsmError (%d)"
              % len(ERR_CASES), not bad, "; ".join(bad[:2]))

        # T-E7-23: CODE0 — .mem без инструкций (как make_up оракула);
        # пустой вход — не CODE0, а FORMAT AT=0001 (нет .mem — строка 1)
        bad = []
        for name, src in CODE0_CASES:
            try:
                lab_vm.assemble(src.decode("latin1"))
                bad.append("%s: оракул принял" % name)
                continue
            except lab_vm.UpError as e:
                if e.reason != "CODE0":
                    bad.append("%s: причина %s" % (name,
                                                   e.reason))
                    continue
            out, code, got = _uva(uexe, src)
            if out != S_CODE0 or code != 6 or got is not None:
                bad.append("%s: %r код=%s" % (name, out[:26],
                                              code))
        out, code, got = _uva(uexe, b"")
        if out != _fmt_line(1) or code != 6:
            bad.append("пустой вход: %r код=%s (ждали AT=0001)"
                       % (out[:30], code))
        check("T-E7-23 CODE0: .mem без инструкций (%d) + пустой вход"
              % len(CODE0_CASES), not bad, "; ".join(bad[:2]))

        # T-E7-24: сквозной круг uva -> kernel.exe (внешняя программа
        # собирается ассемблером и исполняется ядром; F1 — срез 2,
        # F2 — срез 3: const/stb/stq/ldq + вывод в консоль окном
        # устройств) + детерминизм
        bad = []
        for name, src, want_code, want_out in [
                (b"halt 42", b".mem 8\nhalt 42\n", 42, b""),
                (b"halt 37 mem0", b".mem 0\nhalt 37\n", 37, b""),
                (b"first halt", b".mem 4096\nhalt 0\nhalt 1\n", 0, b""),
                (b"mov+add", b".mem 8\nmov r1, r2\nadd r3, r1, r2\n"
                              b"halt 7\n", 7, b""),
                (b"f2 console", b".mem 8\nconst r1, 8\nconst r2, 65\n"
                                 b"stb r1+0, r2\nhalt 0\n", 0, b"A"),
                (b"f2 ram+dev", b".mem 4096\nconst r1, 0\nconst r2, 5\n"
                                 b"stq r1+0, r2\nldq r3, r1\nconst r4, 65\n"
                                 b"add r5, r3, r4\nconst r6, 4096\n"
                                 b"stb r6+0, r5\nhalt 0\n", 0, b"F")]:
            out, code, got = _uva(uexe, src)
            if code != 0 or got is None:
                bad.append("%s: сборка код=%s" % (name, code))
                continue
            k = lab_run.run_kv(kpath("L3-UNIVM/kernel.exe"),
                               ["t.up"], {"t.up": got})
            if k.exit_code != want_code or k.stdout != want_out:
                bad.append("%s: ядро код=%s %r" % (name,
                                                   k.exit_code,
                                                   k.stdout[:20]))
        o1, c1, g1 = _uva(uexe, OK_CASES[0][1])
        o2, c2, g2 = _uva(uexe, OK_CASES[0][1])
        if not (c1 == c2 == 0 and g1 == g2 and g1 is not None):
            bad.append("детерминизм: код %s/%s" % (c1, c2))
        check("T-E7-24 круг uva -> kernel.exe (6) + детерминизм",
              not bad, "; ".join(bad[:2]))
    finally:
        os.unlink(uexe)
