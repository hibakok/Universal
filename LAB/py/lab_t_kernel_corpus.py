"""lab_t_kernel_corpus.py — корпуса программ диффтеста ядра kernel.exe.

Вход:  — (модуль данных; прогонщик — LAB/py/lab_t_kernel.py).
Выход: списки программ/случаев срезов E7.2-2..4 (секция 14 батареи).
Функция: только данные — исходники ассемблера UNIVM (собираются
         lab_vm.assemble), сырые байты ловушек и кортежи пределов
         шагов; выделен из lab_t_kernel.py по лимиту 500 строк
         (по образцу lab_t_wallself_corpus.py). Срезы: 2 — ALU
         (поля/обрезки/шаги), 3 — память и устройства, 4 — переходы
         jmp/jnz + предел шагов (trap 6, лимит — 2-й аргумент CLI).
"""
import lab_t_vm

# --- Срез 2 (E7.2-2): ALU-программы ------------------------------------
# Сырые байты — ловушки полей (4) и обрезанные инструкции (3) в порядке
# SPEC/12 п. 7; обрезки 0C..11 доказывают, что длина валидного опкода
# проверяется ДО исполнителя (ловушка 2, не 1).
ALU_TRAPS = [
    ("const ra!=0", bytes([0x01, 0x11, 0, 0, 0, 0])),
    ("mov rb!=0", bytes([0x02, 0x23, 0x05])),
    ("add rb=16", bytes([0x03, 0x45, 0x10])),
    ("xor rb=255", bytes([0x07, 0x12, 0xFF])),
    ("const обрезан", bytes([0x01, 0x10, 0x05])),
    ("add обрезан", bytes([0x03, 0x45])),
    ("mov 1 байт", bytes([0x02])),
    ("ldb обрезан", bytes([0x0C, 0x12, 0x00])),
    ("jmp обрезан", bytes([0x10, 0x00, 0x05])),
    ("jnz обрезан", bytes([0x11, 0x03])),
    ("jmp rd!=0", bytes([0x10, 0x03, 0, 0, 0, 0])),
    ("jnz rd=16", bytes([0x11, 0x10, 0, 0, 0, 0])),
]

# ALU-программа полного охвата среза 2 (по образцу OPS_VM T-E7-07,
# без jmp/памяти — срезы 3-4): ((20-6)|1)^4 = 11; 11<<6 = 704;
# 704>>3 = 88; eq с эталоном 88 -> 1; lt 6<20 -> 1; 88&1 = 0.
ALU_VM = """\
.mem 0
const r1, 20
const r2, 6
mov r3, r1
sub r3, r3, r2
const r4, 1
or r3, r3, r4
const r4, 4
xor r3, r3, r4
shl r3, r3, r2
const r4, 3
shr r3, r3, r4
const r4, 88
eq r4, r3, r4
lt r5, r2, r1
and r6, r3, r4
halt 7
"""

# Без halt: pc за кодом -> TRAP=2 STEPS=15 — точный счётчик шагов ALU.
ALU_RUNOFF = ALU_VM.replace("halt 7\n", "")

# Знаковые пути: sext(imm32) для -1/-5/0xFFFFFFFF; сложение/вычитание
# с заворотом; знаковые lt/eq на отрицательных регистрах.
NEG_VM = """\
.mem 0
const r1, -1
const r2, -5
mov r3, r1
add r4, r1, r2
sub r5, r2, r1
const r6, 0xFFFFFFFF
eq r7, r6, r1
lt r8, r1, r2
"""

# Сдвиги с маской счётчика 63: 1<<(70&63)=64; 1>>63=0; 8<<63;
# 0xFFFF..FF>>8 (логический, старшие нули).
SHIFT_VM = """\
.mem 0
const r1, 1
const r2, 70
shl r3, r1, r2
const r4, -1
shr r5, r1, r4
const r6, 8
shl r7, r6, r4
shr r8, r4, r6
"""

# r0 равноправен (SPEC/12 п. 2: r0 не спец) + арифметика; без halt —
# счётчик шагов 8 наблюдаем в TRAP=2.
R0_VM = """\
.mem 0
const r0, 5
mov r1, r0
eq r2, r1, r0
const r1, 20
const r2, 6
mov r3, r1
sub r3, r3, r2
add r4, r3, r3
"""

ALU_STEPS = [
    ("шаги: r0 равноправен + арифметика (8)", R0_VM),
    ("ALU полный без halt (15 шагов)", ALU_RUNOFF),
    ("знаковые: sext imm32, lt/eq (8)", NEG_VM),
    ("сдвиги: маска счётчика 63 (8)", SHIFT_VM),
]

ALU_HALT = [
    ("ALU полный halt 7", ALU_VM),
]

# --- Срез 3 (E7.2-3): память и устройства ------------------------------
# Консоль (окно+0) делает значения регистров/RAM наблюдаемыми: программы
# печатают «'0'/'1'» eq-проверок — расхождение с оракулом видно в любом
# наблюдаемом байте. Границы — SPEC/12 п. 3.3/6.


def _console_prog(text, code):
    """Программа: печать text через stb в окно+0 (r1 = memsize), halt."""
    out = [".mem 8", "const r1, 8"]
    for ch in text:
        out.append("const r2, %d" % ord(ch))
        out.append("stb r1+0, r2")
    out.append("halt %d" % code)
    return "\n".join(out) + "\n"


# RAM: sext8 (байт 0x80 -> -128), нулевой старт (RAM[6] = 0 == r0);
# печать результатов — через консоль (окно+0, r1 = memsize).
MEM_SEXT = """\
.mem 16
const r1, 5
const r2, 128
stb r1+0, r2
ldb r3, r1+0
const r4, -128
eq r5, r3, r4
const r6, 48
add r5, r5, r6
const r1, 16
stb r1+0, r5
const r7, 6
ldb r8, r7+0
eq r9, r8, r0
const r6, 48
add r9, r9, r6
stb r1+0, r9
halt 0
"""

# Слова: stq/ldq по невыровненному адресу 3; байтовая раскладка LE
# (0xFF на 0, 0x80 на 7); слово целиком == источнику.
MEM_QWORD = """\
.mem 24
const r1, 1
const r2, 63
shl r1, r1, r2
const r2, 255
or r1, r1, r2
const r3, 3
stq r3+0, r1
ldb r4, r3+0
const r5, -1
eq r6, r4, r5
const r7, 48
add r6, r6, r7
const r9, 24
stb r9+0, r6
ldb r8, r3+7
const r5, -128
eq r6, r8, r5
add r6, r6, r7
stb r9+0, r6
ldq r10, r3+0
eq r11, r10, r1
add r11, r11, r7
stb r9+0, r11
halt 3
"""

# Заворот адреса: r1 = -16 -> (r1 + 16) mod 2^64 = 0 — RAM[0].
MEM_WRAP = """\
.mem 16
const r1, -16
const r4, 55
stb r1+16, r4
ldb r2, r1+16
eq r3, r2, r4
const r5, 48
add r3, r3, r5
const r6, 16
stb r6+0, r3
halt 0
"""

# Окно: запись в окно+1 игнорируется (без ловушки), чтение окна
# (окно+1 и окно+0) = 0.
MEM_WINDOW = """\
.mem 8
const r1, 9
const r2, 65
stb r1+0, r2
ldb r3, r1+0
eq r4, r3, r0
ldb r5, r1-1
eq r6, r5, r0
const r7, 48
add r4, r4, r7
add r6, r6, r7
const r8, 8
stb r8+0, r4
stb r8+0, r6
halt 5
"""

# memsize = 0: консоль по адресу 0 (окно+0); ldq — ловушка 3 сразу.
MEM_M0 = """\
.mem 0
const r1, 0
const r2, 88
stb r1+0, r2
ldq r3, r1+0
"""

# Границы (ловушки 3/4) — SPEC/12 п. 3.3: слова за верхом и в окне,
# байт за окном / бит 31 / заворот; шаги до ловушки — точные.
MEM_TRAPS = [
    ("ldq за верхом (12+8>16)",
     ".mem 16\nconst r1, 12\nldq r2, r1+0\n"),
    ("stq за верхом (12+8>16)",
     ".mem 16\nconst r1, 12\nconst r2, 1\nstq r1+0, r2\n"),
    ("ldq в окне (слова запрещены)",
     ".mem 8\nconst r1, 8\nldq r2, r1+0\n"),
    ("stq в окне (слова запрещены)",
     ".mem 8\nconst r1, 8\nconst r2, 1\nstq r1+0, r2\n"),
    ("ldb ровно за окном (memsize+4096)",
     ".mem 16\nconst r1, 4112\nldb r2, r1+0\n"),
    ("stb ровно за окном (memsize+4096)",
     ".mem 16\nconst r1, 4112\nconst r2, 1\nstb r1+0, r2\n"),
    ("stb бит31 ровно (2^31-1)",
     ".mem 16\nconst r1, 2147483647\nstb r1+0, r1\n"),
    ("stb бит31 задет (4e9)",
     ".mem 16\nconst r1, 2000000000\nconst r2, 2000000000\n"
     "add r3, r1, r2\nstb r3+0, r1\n"),
    ("ldb заворот (-1 -> 2^64-1)",
     ".mem 16\nconst r1, -1\nldb r2, r1+0\n"),
]

MEM_RUNS = [
    ("консоль: строка через окно+0 (halt 37)",
     _console_prog("MEM-OK\r\n", 37)),
    ("RAM: sext8 + нулевой старт", MEM_SEXT),
    ("слова: stq/ldq невыровнено + LE-байты", MEM_QWORD),
    ("заворот адреса (-16 + 16 = 0)", MEM_WRAP),
    ("окно: резерв игнорируется, чтение = 0", MEM_WINDOW),
    ("memsize=0: консоль на 0, ldq — ловушка 3", MEM_M0),
]

# --- Срез 4 (E7.2-4): переходы jmp/jnz ----------------------------------
# Полный корпус программ оракула T-E7-04..08 (demo/ops/dev — петли jnz
# вперёд/назад, jmp через мёртвый код) + собственные случаи: jnz вперёд
# через ловушку / не взят / петля назад / граница кода; цели за кодом.

# jnz ВПЕРЁД через ловушку (взят: r1 = 1; ldb r2, 99+0 — чтение вне
# памяти, пропускается): 3 шага, halt 5.
JMP_FWD = """\
.mem 0
const r1, 1
jnz r1, skip
const r2, 99
ldb r3, r2+0
skip:
halt 5
"""

# jnz НЕ ВЗЯТ (r1 = 0): pc += 6 — падение в halt 9; цель 999999 не
# проверяется (переход не исполнен).
JMP_NT = """\
.mem 0
const r1, 0
jnz r1, 999
halt 9
"""

# Конечная петля НАЗАД (3 итерации jnz): r1 = 3 -> 0.
JMP_LOOP3 = """\
.mem 0
const r1, 3
loop:
const r2, 1
sub r1, r1, r2
jnz r1, loop
halt 4
"""

# jmp на границу кода: pc = 6 == codesize -> ловушка 2 (шаг 1).
JMP_EDGE = ".mem 0\njmp 6\n"

JMP_RUNS = [
    ("демо: петли jnz + печать (U-VM-OK 37)", lab_t_vm.DEMO_VM),
    ("ops: ALU + jmp через мёртвый код (код 7)", lab_t_vm.OPS_VM),
    ("окно: печать AA (код 0)", lab_t_vm.DEV_VM),
    ("jnz вперёд через ловушку (взят)", JMP_FWD),
    ("jnz не взят: pc+6 в halt", JMP_NT),
    ("петля назад: 3 итерации jnz (код 4)", JMP_LOOP3),
    ("jmp на границу кода (pc == codesize)", JMP_EDGE),
]

JMP_TRAPS = [
    ("jmp за код (цель 999999)", ".mem 4096\njmp 999999\n"),
    ("jnz на плохую цель (999999)",
     ".mem 4096\nconst r1, 1\njnz r1, 999999\nhalt 0\n"),
]

# --- Срез 4 (E7.2-4): предел шагов (trap 6; лимит — 2-й аргумент CLI) --
# Проверка предела — ДО выборки очередной инструкции (как оракул
# run(max_steps)): сток кода, совпавший с пределом, даёт trap 6, а не
# trap 2; halt ровно на пределе — нормальный останов (исполнен ДО
# следующей проверки); предел 0 — trap 6 до первой инструкции.

# Вечные циклы (обе формы переходов).
LIM_LOOP_JMP = ".mem 4096\nloop:\njmp loop\n"
LIM_LOOP_JNZ = ".mem 0\nconst r1, 1\nloop:\njnz r1, loop\n"

# Ровно 100 инструкций (99 const + halt 42): предел 100 — нормальный
# останов (код 42); предел 99 — trap 6 (halt не исполнен).
LIM_HALTED = ".mem 0\n" + "const r1, 1\n" * 99 + "halt 42\n"

# Сток кода: 5 const без halt — предел 5 -> trap 6 (НЕ trap 2 —
# порядок проверок: предел прежде выборки); предел 6 -> trap 2.
LIM_RUNOFF = (".mem 0\nconst r1, 1\nconst r2, 2\nconst r3, 3\n"
              "const r4, 4\nconst r5, 5\n")

LIM_RUNS = [
    ("вечный jmp, предел 100", LIM_LOOP_JMP, 100),
    ("вечный jnz, предел 7", LIM_LOOP_JNZ, 7),
    ("halt ровно на пределе 100 (норм. останов)", LIM_HALTED, 100),
    ("та же программа, предел 99 -> trap 6", LIM_HALTED, 99),
    ("сток кода на пределе 5 -> trap 6 (не 2)", LIM_RUNOFF, 5),
    ("сток кода, предел 6 -> trap 2", LIM_RUNOFF, 6),
    ("предел 0: trap 6 до первой инструкции", LIM_HALTED, 0),
    ("предел 1: один шаг перехода", LIM_LOOP_JMP, 1),
]

# --- Срез E7.4-2a: контейнер v2 — секция данных -> RAM --------------------
# Программы v0 (только опкоды ISA v0: v1-опкоды ядру ещё не поданы —
# срезы E7.4-2b/c): ассемблер оракула с .data собирает v2 (make_up);
# данные наблюдаемы через ldb (RAM[0:datalen]) и печать окном+0.

# Печать данных: .data «HELLO!» -> RAM[0:6], ldb по адресам 0..5,
# вывод окном+0, halt 7.
DATA_ECHO = """\
.mem 64
.data 48 45 4C 4C 4F 21
const r1, 64
const r3, 0
ldb r2, r3+0
stb r1+0, r2
ldb r2, r3+1
stb r1+0, r2
ldb r2, r3+2
stb r1+0, r2
ldb r2, r3+3
stb r1+0, r2
ldb r2, r3+4
stb r1+0, r2
ldb r2, r3+5
stb r1+0, r2
halt 7
"""

# Порядок байтов данных: .data 16 Б, печать позиций 0/15/8/7 — байты
# попадают в RAM в порядке файла (data[15] в RAM[15], data[8] в RAM[8]).
DATA_LE = """\
.mem 128
.data 11 22 33 44 55 66 77 88 FE DC BA 98 76 54 32 10
const r1, 128
const r3, 0
ldb r2, r3+0
stb r1+0, r2
ldb r2, r3+15
stb r1+0, r2
ldb r2, r3+8
stb r1+0, r2
ldb r2, r3+7
stb r1+0, r2
halt 5
"""

# Данные + перезапись кодом: RAM[2] = 'B' поверх 'A'; чтение 0/2/3 —
# 'A''B''A' (перезапись не задевает соседние байты данных).
DATA_OVERWRITE = """\
.mem 64
.data 41 41 41 41
const r1, 64
const r3, 0
const r4, 66
stb r3+2, r4
ldb r2, r3+0
stb r1+0, r2
ldb r2, r3+2
stb r1+0, r2
ldb r2, r3+3
stb r1+0, r2
halt 3
"""

# datalen == memsize (данные заполняют RAM ровно: у ядра зонд за
# границей — got = 0, валид): печать 7-го и 0-го байтов.
DATA_EXACT = """\
.mem 8
.data 31 32 33 34 35 36 37 38
const r1, 8
const r3, 0
ldb r2, r3+7
stb r1+0, r2
ldb r2, r3+0
stb r1+0, r2
halt 6
"""

DATA_RUNS = [
    ("data: печать HELLO! (halt 7)", DATA_ECHO),
    ("data: порядок байтов (0/15/8/7)", DATA_LE),
    ("data + перезапись RAM кодом", DATA_OVERWRITE),
    ("data: datalen == memsize (ровно RAM)", DATA_EXACT),
]

# Данные длиннее куска чтения ядра (4096 Б): 4196 = 1 + 4096 + 99,
# печать data[4095]/data[4096]/data[4195]/data[0] -> QZZQ. Контейнер
# собирается вручную (прогонщик: код без .data + 4196 Б данных —
# заголовок v2 полями, как _up у refuzals).
DATA_CHUNK_SRC = """\
.mem 8192
const r1, 8192
const r3, 4095
ldb r2, r3+0
stb r1+0, r2
ldb r2, r3+1
stb r1+0, r2
const r3, 4195
ldb r2, r3+0
stb r1+0, r2
const r3, 0
ldb r2, r3+0
stb r1+0, r2
halt 9
"""
DATA_CHUNK = b"Q" * 4096 + b"Z" * 100      # 4196 Б; вывод QZZQ

# v2 без данных (dataoff = 0) — v1-эквивалент: печать A, halt 0
# (сборка v1 и v2-без-данных из одного кода — вывод идентичный).
DATA_NODATA_SRC = """\
.mem 4096
const r1, 4096
const r2, 65
stb r1+0, r2
halt 0
"""
