"""lab_t_uva_corpus.py — корпуса диффтеста ассемблера uva.exe (E7.3..E7.4-3b).

Вход:  — (константы-корпуса; конструируются при импорте).
Выход: OK_CASES — успех: out.up == lab_vm.assemble(текст) байт-в-байт
       (124: срезы 1-4 + v1-корпус E7.4-3a + .data-корпус E7.4-3b);
       ERR_CASES — отвержение: uva ERR=FORMAT AT=XXXX == строка
       AsmError оракула (127); DATA_CASES — данные длиннее RAM:
       UpError("DATA") оракула == ERR=DATA код 6 у uva (3 — E7.4-3b);
       CODE0_CASES — .mem без инструкций (5).
Функция: данные секции 15 батареи (LAB/py/lab_t_uva.py); выделены из
         него по лимиту 500 строк (E7.4-3a; прецедент
         lab_t_vm_corpus.py / lab_t_kernel_corpus.py). Состав корпусов
         — TESTS/T-L3-UVA.md; свидетели-якоря — ANCHORS/V1_ANCHORS
         lab_t_vm_corpus.py (общие с секцией 13).
"""

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
    # F3 (срез E7.3-4): jmp/jnz + метки
    (b"jmp num", b".mem 8\njmp 100\nhalt 0\n"),
    (b"jmp hex", b".mem 8\njmp 0x10\nhalt 0\n"),
    (b"jmp +5", b".mem 8\njmp +5\nhalt 0\n"),
    (b"jmp -1", b".mem 8\njmp -1\nhalt 0\n"),
    (b"jmp min i32", b".mem 8\njmp -2147483648\nhalt 0\n"),
    (b"jmp max u32", b".mem 8\njmp 4294967295\nhalt 0\n"),
    (b"jnz num", b".mem 8\njnz r3, 200\nhalt 0\n"),
    (b"jnz r15", b".mem 8\njnz r15, 0\nhalt 0\n"),
    (b"label back", b".mem 8\nloop:\nadd r1, r1, r2\nlt r3, r1, r4\n"
                      b"jnz r3, loop\nhalt 0\n"),
    (b"label fwd", b".mem 8\njmp fwd\nhalt 1\nfwd: halt 2\n"),
    (b"two labels one pc", b".mem 8\na: b: halt 5\njmp a\njmp b\n"),
    (b"label before mem", b"base: .mem 8\nhalt 0\n"),
    (b"trailing label", b".mem 8\nhalt 3\nend:\n"),
    (b"label = mnemonic", b".mem 8\nadd:\nhalt 0\njmp add\n"),
    (b"label = r5", b".mem 8\nr5:\njmp r5\nhalt 0\n"),
    (b"label _x1", b".mem 8\n_x1:\njmp _x1\nhalt 0\n"),
    (b"label cr after colon", b".mem 8\na:\rhalt 7\n"),
    (b"label sep rest", b".mem 8\na: , ,\nhalt 0\n"),
    (b"label + instr", b".mem 8\nx: const r1, 5\nhalt 0\n"),
    (b"f3 no final lf", b".mem 8\njmp 0\nhalt 0"),
    # v1 (срез E7.4-3a): mul/div/mod/sra (F1) + call (F3) + ret (F0);
    # первые четыре — якорные формы T-E7-26
    (b"mul", b".mem 8\nmul r1, r2, r3\nhalt 0\n"),
    (b"div", b".mem 8\ndiv r1, r2, r3\nhalt 0\n"),
    (b"mod", b".mem 8\nmod r4, r5, r6\nhalt 0\n"),
    (b"sra", b".mem 8\nsra r7, r8, r9\nhalt 0\n"),
    (b"v1 alu r15", b".mem 8\nmul r15, r14, r13\ndiv r10, r11, r12\n"
                      b"mod r1, r15, r0\nsra r0, r10, r15\nhalt 0\n"),
    (b"v1 alu mixed", b".mem 64\nconst r1, 12345\nconst r2, 6789\n"
                        b"mul r3, r1, r2\ndiv r4, r1, r2\nmod r5, r1, r2\n"
                        b"sra r6, r3, r2\nhalt 0\n"),
    (b"call num", b".mem 8\ncall 100\nhalt 0\n"),
    (b"call hex", b".mem 8\ncall 0x10\nhalt 0\n"),
    (b"call -1", b".mem 8\ncall -1\nhalt 0\n"),
    (b"call max u32", b".mem 8\ncall 4294967295\nhalt 0\n"),
    (b"ret only", b".mem 8\nret\nhalt 0\n"),
    (b"call label fwd", b".mem 8\ncall sub\nhalt 1\nsub:\nhalt 2\n"),
    (b"call label back", b".mem 8\nsub:\ncall sub\nhalt 0\n"),
    (b"call + ret", b".mem 8\ncall sub\nhalt 5\nsub:\nret\n"),
    (b"two calls one sub", b".mem 8\ncall sub\nhalt 1\ncall sub\n"
                            b"halt 2\nsub:\nret\n"),
    (b"call label = mnemonic", b".mem 8\nmul:\ncall mul\nhalt 0\n"),
    (b"call r5 declared", b".mem 8\nr5:\ncall r5\nhalt 0\n"),
    (b"ret last no lf", b".mem 8\nhalt 0\nret"),
    (b"v1 no spaces", b".mem 8\nmul r1,r2,r3\ncall 5\nret\nhalt 0\n"),
    # .data (срез E7.4-3b): секция данных .UP v2 — байты hex2; контейнер
    # v2 (версия 2 + dataoff = 24+codesize) == оракулу байт-в-байт
    (b"data basic", b".mem 8\n.data 41\nhalt 0\n"),
    (b"data two bytes", b".mem 8\n.data 41 42\nhalt 0\n"),
    (b"data comma", b".mem 8\n.data 41,42\nhalt 0\n"),
    (b"data comma+space", b".mem 8\n.data 41 , 42\nhalt 0\n"),
    (b"data lowercase", b".mem 8\n.data ab\nhalt 0\n"),
    (b"data mixed case", b".mem 8\n.data Ab aB 0f FF\nhalt 0\n"),
    (b"data 00 FF", b".mem 8\n.data 00 FF\nhalt 0\n"),
    (b"data multiple", b".mem 8\n.data 41\nhalt 0\n.data 42\nhalt 1\n"),
    (b"data between instr", b".mem 8\nhalt 0\n.data 41\nhalt 1\n.data 42\nhalt 2\n"),
    (b"data before code", b".mem 8\n.data 41 42 43\nhalt 0\n"),
    (b"data label line", b".mem 8\nx: .data 41\nhalt 0\n"),
    (b"data comment", b".mem 8\n.data 41 42 ; c\nhalt 0\n"),
    (b"data trailing comma", b".mem 8\n.data 41,\nhalt 0\n"),
    (b"data no final lf", b".mem 8\nhalt 0\n.data 41"),
    (b"data CR sep", b".mem 8\n.data 41\r42\nhalt 0\n"),
    (b"data tab sep", b".mem 8\n.data\t41\t42\nhalt 0\n"),
    (b"data == memsize", b".mem 3\n.data 41 42 43\nhalt 0\n"),
    (b"data 40 one line", b".mem 64\n.data "
                     + b" ".join([b"41"] * 40) + b"\nhalt 0\n"),
    (b"data 00..3f", b".mem 4096\n.data "
                     + b" ".join(b"%02X" % i for i in range(64))
                     + b"\nhalt 0\n"),
    (b"data crlf lines", b".mem 8\r\n.data 41\r\nhalt 0\r\n"),
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
    # F3/метки (срез E7.3-4): синтаксис меток, таблица, операнды переходов
    ("метка запятая после :", b".mem 8\na:,halt 0\n"),
    ("метка запятая вторая", b".mem 8\na:, b: halt 0\n"),
    ("метка пробел перед :", b".mem 8\na : halt 0\n"),
    ("метка без пробела", b".mem 8\na:halt 0\n"),
    ("метка заглавная", b".mem 8\nA: halt 0\n"),
    ("метка с цифры", b".mem 8\n1a: halt 0\n"),
    ("пустое имя метки", b".mem 8\n: halt 0\n"),
    ("неизвестная метка jmp", b".mem 8\njmp nowhere\nhalt 0\n"),
    ("jmp r5 без объявления", b".mem 8\njmp r5\nhalt 0\n"),
    ("jnz r1, r5 без объявления", b".mem 8\njnz r1, r5\nhalt 0\n"),
    ("дубликат метки", b".mem 8\nl:\nl:\nhalt 0\n"),
    ("дубликат на одной строке", b".mem 8\na: a: halt 0\n"),
    ("дубликат раньше ошибки", b".mem 8\na:\nhalt 0\na: foo\n"),
    ("jmp без операндов", b".mem 8\njmp\nhalt 0\n"),
    ("jmp 2 операнда", b".mem 8\njmp a, b\nhalt 0\n"),
    ("jnz 1 операнд", b".mem 8\njnz r1\nhalt 0\n"),
    ("jnz 3 операнда", b".mem 8\njnz r1, a, b\nhalt 0\n"),
    ("jnz плохой reg", b".mem 8\njnz r19, 5\nhalt 0\n"),
    ("jnz число-регистр", b".mem 8\njnz 1, 5\nhalt 0\n"),
    ("jmp не число", b".mem 8\njmp a+b\nhalt 0\n"),
    ("jmp дробное", b".mem 8\njmp 1.5\nhalt 0\n"),
    ("jmp вне imm32", b".mem 8\njmp 4294967296\nhalt 0\n"),
    ("jmp ниже imm32", b".mem 8\njmp -2147483649\nhalt 0\n"),
    ("jmp hex без цифр", b".mem 8\njmp 0x\nhalt 0\n"),
    ("halt метка", b".mem 8\nx:\nhalt x\n"),
    # v1 (срез E7.4-3a): операнды mul/div/mod/sra + call/ret
    ("v1 alu 2 операнда", b".mem 8\nmul r1, r2\nhalt 0\n"),
    ("v1 alu 4 операнда", b".mem 8\ndiv r1, r2, r3, r4\nhalt 0\n"),
    ("mul плохой rd", b".mem 8\nmul r16, r1, r2\nhalt 0\n"),
    ("div плохой ra", b".mem 8\ndiv r1, r16, r2\nhalt 0\n"),
    ("mod плохой rb", b".mem 8\nmod r1, r2, r16\nhalt 0\n"),
    ("sra число-операнд", b".mem 8\nsra r1, r2, 3\nhalt 0\n"),
    ("call без операндов", b".mem 8\ncall\nhalt 0\n"),
    ("call 2 операнда", b".mem 8\ncall a, b\nhalt 0\n"),
    ("call неизвестная метка", b".mem 8\ncall nowhere\nhalt 0\n"),
    ("call r5 без объявления", b".mem 8\ncall r5\nhalt 0\n"),
    ("call дробное", b".mem 8\ncall 1.5\nhalt 0\n"),
    ("call вне imm32", b".mem 8\ncall 4294967296\nhalt 0\n"),
    ("ret с операндом", b".mem 8\nret 1\nhalt 0\n"),
    ("ret 2 операнда", b".mem 8\nhalt 0\nret 1 2\n"),
    ("заглавный MUL", b".mem 8\nMUL r1, r2, r3\nhalt 0\n"),
    ("callx префикс", b".mem 8\ncallx 5\nhalt 0\n"),
    # .data (срез E7.4-3b): синтаксис байтов и директивы
    ("пустая .data", b".mem 8\n.data\nhalt 0\n"),
    ("пустая .data в конце", b".mem 8\nhalt 0\n.data\n"),
    (".data один символ", b".mem 8\n.data 4\nhalt 0\n"),
    (".data три цифры", b".mem 8\n.data 414\nhalt 0\n"),
    (".data 0x41", b".mem 8\n.data 0x41\nhalt 0\n"),
    (".data ZZ", b".mem 8\n.data ZZ\nhalt 0\n"),
    (".data 41 ZZ", b".mem 8\n.data 41 ZZ\nhalt 0\n"),
    (".data 41g", b".mem 8\n.data 41g\nhalt 0\n"),
    (".data до .mem", b".data 41\n.mem 8\nhalt 0\n"),
    (".DATA заглавная", b".mem 8\n.DATA 41\nhalt 0\n"),
    (".dataX директива", b".mem 8\n.dataX 41\nhalt 0\n"),
    (".data ошибка в 4-й строке", b".mem 8\n.data 41\nhalt 0\n.data 4\n"),
    (".data ошибка раньше операндной", b".mem 8\nhalt 1 2\n.data ZZ\n"),
    (".data только разделители", b".mem 8\n.data , ,\nhalt 0\n"),
]

# CODE0: .mem есть, инструкций нет (как make_up оракула; только метки —
# тоже CODE0: pc == 0; .data без инструкций — тоже: CODE0 раньше DATA)
CODE0_CASES = [
    ("только .mem", b".mem 8\n"),
    (".mem + комментарий", b".mem 8\n; comment\n\n"),
    (".mem + разделители", b".mem 8\n,,,\n"),
    ("только метка", b".mem 8\nonly:\n"),
    (".mem + .data без кода", b".mem 8\n.data 41\n"),
]

# DATA (E7.4-3b): длина данных > memsize — как make_up оракула
# (UpError("DATA"), ПОСЛЕ ошибок операндов и CODE0); uva.exe обязан
# печатать ERR=DATA (код 6) и не создавать файл
DATA_CASES = [
    ("данные > memsize", b".mem 1\n.data 41 42\nhalt 0\n"),
    ("memsize 0 с данными", b".mem 0\n.data 41\nhalt 0\n"),
    ("много .data переполняют", b".mem 2\n.data 41 42\nhalt 0\n.data 43\n"),
]


