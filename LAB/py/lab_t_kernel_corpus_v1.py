"""lab_t_kernel_corpus_v1.py — корпуса программ дифтеста ядра: ALU v1.

Вход:  — (модуль данных; прогонщик — LAB/py/lab_t_kernel.py, T-E7-33).
Выход: списки случаев среза E7.4-2b (опкоды ISA v1 13..16 + ловушка 7).
Функция: только данные — исходники ассемблера UNIVM v1 (собираются
         lab_vm.assemble), сырые байты ловушек полей/обрезок; выделен
         из lab_t_kernel_corpus.py по лимиту 500 строк (прецедент —
         lab_t_kernel_corpus.py из lab_t_kernel.py).
Срезы: TRAPS — поля (ловушка 1) и обрезки (ловушка 2) опкодов 13..16
(длина F1 проверяется ДО исполнителя); DIV0 — деление на ноль
(ловушка 7, порядок SPEC/12 п. 7: поля ПЕРЕД исполнением; команда
с ловушкой в счётчик шагов не входит); RUNS — программы полного
охвата (консоль наблюдаема: eq-проверки полных 64-битных значений
печатают '1'/'0'; инвариант деления (a div b)*b + a mod b == a;
границы путей udivmod: b = 2^63 — цикл, b > 2^63 — частное 0/1);
STEPS — без halt: точный счётчик шагов в TRAP=2 STEPS=n.
"""

# --- Срез E7.4-2b: ловушки полей/обрезок (сырые байты) -------------------
# Опкоды 0x13..0x16 — формат F1 (3 байта): rb > 15 -> ловушка 1 ДО
# исполнения (в т.ч. ДО ловушки 7 — порядок проверок SPEC/12 п. 7);
# обрезка инструкции -> ловушка 2 (длина валидного опкода до исполнителя).
TRAPS = [
    ("mul rb=16", bytes([0x13, 0x45, 0x10])),
    ("div rb=255", bytes([0x14, 0x12, 0xFF])),
    ("mod rb=16", bytes([0x15, 0x45, 0x10])),
    ("sra rb=99", bytes([0x16, 0x12, 0x63])),
    ("mul обрезан", bytes([0x13, 0x45])),
    ("div обрезан", bytes([0x14, 0x45])),
    ("mod 1 байт", bytes([0x15])),
    ("sra 2 байта", bytes([0x16, 0x12])),
]

# --- Срез E7.4-2b: деление на ноль — ловушка 7 ---------------------------
# Поля проверены (rb = 2 — корректный номер), значение regs[rb] = 0 —
# ловушка 7 на div/mod (0/0 — тоже ловушка, не ноль); команда с ловушкой
# в счётчик шагов НЕ входит (STEPS = число исполненных до неё).
DIV0 = [
    ("div на ноль", ".mem 0\nconst r1, 5\nconst r2, 0\ndiv r3, r1, r2\n"),
    ("mod на ноль", ".mem 0\nconst r1, -1\nconst r2, 0\nmod r3, r1, r2\n"),
    ("div 0/0", ".mem 0\nconst r1, 0\nconst r2, 0\ndiv r3, r1, r2\n"),
]

# --- Срез E7.4-2b: программы полного охвата (консоль наблюдаема) ---------

# mul: заворот произведения ((2^64-1)*7 = 2^64-7; (-1)*(-1) = 1;
# 2^32*2^32 = 2^64 -> 0), малые значения, множитель 0, приёмник r0
# (r0 равноправен — SPEC/12 п. 2). Ожидаемый вывод: '11111'.
MUL_VM = """\
.mem 8
const r1, 8
const r9, 48
const r2, -1
const r3, 7
mul r4, r2, r3
const r5, -7
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
mul r4, r3, r3
const r5, 49
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
mul r4, r2, r2
const r5, 1
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r3, 0
mul r0, r2, r3
const r5, 0
eq r6, r0, r5
add r6, r6, r9
stb r1+0, r6
const r2, 32
const r3, 1
shl r2, r3, r2
mul r4, r2, r2
const r5, 0
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
halt 0
"""

# div/mod: беззнаковая семантика (2^63 div 2 = 2^62 — знаковое дало бы
# -2^62); границы путей udivmod: b = 2^63 (цикл: (2^64-1) div 2^63 = 1,
# mod = 2^63-1) и b = 2^63+5 > 2^63 (частное 0/1: (2^64-1) div B = 1,
# mod = 2^63-6; 5 div B = 0, 5 mod B = 5); деление меньшего на большее;
# инвариант деления (a div b)*b + a mod b == a на составном a.
# Ожидаемый вывод: '111111111'.
DIV_VM = """\
.mem 8
const r1, 8
const r9, 48
const r0, 1
const r2, 63
shl r2, r0, r2
const r3, 2
div r4, r2, r3
const r5, 62
shl r5, r0, r5
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
mod r4, r2, r3
const r5, 0
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r2, -1
const r3, 63
shl r3, r0, r3
div r4, r2, r3
eq r6, r4, r0
add r6, r6, r9
stb r1+0, r6
mod r4, r2, r3
sub r5, r3, r0
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
add r3, r3, r0
add r3, r3, r0
add r3, r3, r0
add r3, r3, r0
add r3, r3, r0
div r4, r2, r3
eq r6, r4, r0
add r6, r6, r9
stb r1+0, r6
mod r4, r2, r3
const r7, 63
shl r7, r0, r7
const r5, 6
sub r5, r7, r5
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r2, 5
div r4, r2, r3
const r5, 0
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
mod r4, r2, r3
eq r6, r4, r2
add r6, r6, r9
stb r1+0, r6
const r2, 62
shl r2, r0, r2
const r3, 123
add r2, r2, r3
const r3, 7
div r4, r2, r3
mod r5, r2, r3
mul r4, r4, r3
add r4, r4, r5
eq r6, r4, r2
add r6, r6, r9
stb r1+0, r6
halt 0
"""

# sra: отрицательные (знак размножается: -8 sra 1 = -4, sra 2 = -2,
# sra 63 = -1; n = 0 — без изменения; n = 70 -> 70&63 = 6 -> -1),
# положительные (12 sra 2 = 3), INT64_MIN sra 63 = -1 (граница маски).
# Ожидаемый вывод: '1111111'.
SRA_VM = """\
.mem 8
const r1, 8
const r9, 48
const r2, -8
const r3, 1
sra r4, r2, r3
const r5, -4
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r3, 2
sra r4, r2, r3
const r5, -2
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r3, 63
sra r4, r2, r3
const r5, -1
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r3, 0
sra r4, r2, r3
const r5, -8
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r3, 70
sra r4, r2, r3
const r5, -1
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r2, 12
const r3, 2
sra r4, r2, r3
const r5, 3
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
const r2, 63
const r0, 1
shl r2, r0, r2
const r3, 63
sra r4, r2, r3
const r5, -1
eq r6, r4, r5
add r6, r6, r9
stb r1+0, r6
halt 0
"""

RUNS = [
    ("mul: заворот/нули/r0", MUL_VM),
    ("div/mod: границы путей + инвариант", DIV_VM),
    ("sra: знак/маска счётчика", SRA_VM),
]

# --- Срез E7.4-2b: точный счётчик шагов (без halt) -----------------------
# 7 команд (const/const/mul/div/mod/const/sra), pc = 30 = codesize ->
# TRAP=2 STEPS=7 (ловушечная команда не исполнялась — счётчик точен).
STEPS = [
    ("шаги: v1-опкоды без halt (7)", """\
.mem 0
const r1, -1
const r2, 7
mul r3, r1, r2
div r3, r1, r2
mod r3, r1, r2
const r2, 2
sra r3, r1, r2
"""),
]
