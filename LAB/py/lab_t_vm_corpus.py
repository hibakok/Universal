"""lab_t_vm_corpus.py — корпуса секции 13 батареи: оракул UNIVM (данные).

Вход:  нет (константы-данные для прогонщика LAB/py/lab_t_vm.py).
Выход: якоря кодировок v0/v1, демо-программы (DEMO_VM «U-VM-OK 37»,
       OPS_VM, DEV_VM, OPS2_VM, FACT_VM «U-VM1-OK 78» — факториал
       рекурсией через стек вызовов + sp = r13, DATA_VM «U-DATA-OK 61»
       — секция данных .UP v2), корпуса отвержений ассемблера/
       контейнеров v1/v2 и построители повреждённых контейнеров
       (_up_err/_rawup).
Функция: только данные — выделены из lab_t_vm.py по лимиту 500 строк
         (E7.4-1; прецедент lab_t_kernel_corpus.py). Прогонщик —
         lab_t_vm.py; семантика — SPEC/12 + SPEC/13.
"""

# --- T-E7-01: якорные кодировки (ручные, SPEC/12 п. 4-5) ---------------
# (строка ассемблера, hex-байты инструкции; выписано вручную по SPEC)
ANCHORS = [
    ("const r1, 65536", "011000000100"),
    ("mov r2, r3", "022300"),
    ("add r4, r5, r6", "034506"),
    ("sub r7, r8, r9", "047809"),
    ("and r1, r2, r3", "051203"),
    ("or r1, r2, r3", "061203"),
    ("xor r1, r2, r3", "071203"),
    ("shl r1, r2, r3", "081203"),
    ("shr r1, r2, r3", "091203"),
    ("lt r1, r2, r3", "0A1203"),
    ("eq r1, r2, r3", "0B1203"),
    ("ldb r1, r2+16", "0C1210000000"),
    ("stb r1+16, r2", "0D1210000000"),
    ("ldq r1, r2-8", "0E12F8FFFFFF"),
    ("stq r1+0, r2", "0F1200000000"),
    ("jmp 100", "100064000000"),
    ("jnz r3, 200", "1103C8000000"),
    ("halt 0", "120000000000"),
]

# --- T-E7-04: демо (аналог DEMO_WALL «U-WALL-OK 37» на UNIVM) ---------
DEMO_VM = """\
; UNIVERSAL / UNIVM v0 / демонстрация ISA: строка в RAM через stb,
; сумма 1..10 = 55 = 0x37, hex-цифры, печать регистром консоли.
; Печатает "U-VM-OK 37\\r\\n" и выходит (142 шага).
.mem 65536

const r1, 0          ; база строки
const r2, 85         ; 'U'
stb r1+0, r2
const r2, 45         ; '-'
stb r1+1, r2
const r2, 86         ; 'V'
stb r1+2, r2
const r2, 77         ; 'M'
stb r1+3, r2
const r2, 45         ; '-'
stb r1+4, r2
const r2, 79         ; 'O'
stb r1+5, r2
const r2, 75         ; 'K'
stb r1+6, r2
const r2, 32         ; ' '
stb r1+7, r2
const r2, 13         ; '\\r'
stb r1+10, r2
const r2, 10         ; '\\n'
stb r1+11, r2

const r3, 1          ; i
const r4, 0          ; s
const r5, 1          ; шаг
const r6, 11         ; граница: i < 11
loop:
add r4, r4, r3
add r3, r3, r5
lt r7, r3, r6
jnz r7, loop

const r2, 4          ; старшая тетрада: 55 >> 4 = 3
shr r7, r4, r2
const r2, 15
and r7, r7, r2
const r2, 48
add r7, r7, r2       ; '3'
stb r1+8, r7
const r2, 15         ; младшая: 55 & 15 = 7
and r7, r4, r2
const r2, 48
add r7, r7, r2       ; '7'
stb r1+9, r7

const r3, 65536      ; devbase: регистр консоли (окно+0)
const r1, 0          ; индекс
const r5, 1
const r6, 12
print:
ldb r2, r1+0         ; байт строки
stb r3+0, r2         ; вывод в консоль
add r1, r1, r5
lt r7, r1, r6
jnz r7, print
halt 0
"""

# --- T-E7-07: ops-программа (покрытие остальных опкодов) ---------------
OPS_VM = """\
; mov/sub/or/xor/shl/shr/eq/jmp/stq/ldq: ((20-6)|1)^4 = 11; 11<<6 = 704;
; 704>>3 = 88; проверка eq; слово в RAM и обратно. halt 7.
; Эталоны: r3=88, r4=1, r15=88, r6=88, mem64[100]=88; 19 шагов.
.mem 4096

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
mov r15, r3
jmp skip
const r15, 0         ; пропускается jmp
skip:
const r5, 100
stq r5+0, r15
ldq r6, r5+0
halt 7
"""

# --- T-E7-08: окно устройств -------------------------------------------
DEV_VM = """\
; консоль = окно+0 (memsize); окно+1 — резерв (запись игнорируется);
; чтение окна = 0. Печатает "AA"; r3 = 0; 7 шагов.
.mem 4096

const r1, 4096
const r2, 65
stb r1+0, r2
stb r1+1, r2
ldb r3, r1+0
stb r1+0, r2
halt 0
"""

# --- T-E7-26: якорные кодировки v1 (ручные, SPEC/12 п. 4-5; E7.4-1) ---
V1_ANCHORS = [
    ("mul r1, r2, r3", "131203"),
    ("div r1, r2, r3", "141203"),
    ("mod r1, r2, r3", "151203"),
    ("sra r1, r2, r3", "161203"),
    ("call 100", "170064000000"),
    ("ret", "18"),
]

# --- T-E7-27: семантика mul/div/mod/sra (E7.4-1) ------------------------
# 2^32*2^2 = 0 mod 2^64; 12345*6789; 100/7 и 100%7; 0/x; sra:
# 256>>4 = 16, -256>>4 = -16 (0xFFFF..F0), -256>>63 = -1, сдвиг 0.
# Эталоны: r3=0, r4=83810205, r5=14, r6=2, r7=0, r8=0, r9=16,
# r10=r12=-256-подобные; 24 шага; halt 0.
OPS2_VM = """\
; UNIVERSAL / UNIVM v1 / mul+div+mod+sra: заворот произведения
; (2^32*2^32 mod 2^64 = 0), 12345*6789 = 83810205, 100/7 = 14,
; 100%7 = 2, 0/x; sra: 256>>4 = 16, -256>>4 = -16, -256>>63 = -1,
; сдвиг 0 — тождество. 24 шага; halt 0.
.mem 4096
const r2, 32
const r1, 1
shl r1, r1, r2       ; r1 = 2^32
mul r3, r1, r1       ; 2^64 mod 2^64 = 0
const r1, 12345
const r2, 6789
mul r4, r1, r2
const r1, 100
const r2, 7
div r5, r1, r2       ; 14
mod r6, r1, r2        ; 2
const r1, 0
div r7, r1, r2        ; 0
mod r8, r1, r2        ; 0
const r1, 256
const r2, 4
sra r9, r1, r2        ; 16
const r1, -256
sra r10, r1, r2       ; -16
const r2, 63
sra r11, r1, r2       ; -1
const r2, 0
sra r12, r1, r2       ; сдвиг 0
halt 0
"""

# --- T-E7-28: демо v1 «U-VM1-OK 78» — факториал 5 рекурсией (E7.4-1) ---
# Адреса возврата — стек вызовов (SPEC/12 п. 3.4); локальное n —
# программный стек в RAM (sp = r13 — конвенция v1, растёт вниз).
# 5! = 120 = 0x78; 188 шагов; r13 возвращается к 4096 (баланс).
FACT_VM = """\
; UNIVERSAL / UNIVM v1 / демонстрация call/ret+mul: факториал 5 = 120
; = 0x78. Рекурсия fact: адреса возврата — стек вызовов; n — на
; программном стеке RAM (sp = r13 — конвенция v1, растёт вниз).
; Печатает "U-VM1-OK 78\\r\\n" и выходит (188 шага).
.mem 4096
const r13, 4096      ; sp — вершина RAM (стек растёт вниз)
const r1, 5          ; n
call fact            ; r4 = 120
const r1, 0          ; база строки
const r2, 85
stb r1+0, r2
const r2, 45
stb r1+1, r2
const r2, 86
stb r1+2, r2
const r2, 77
stb r1+3, r2
const r2, 49         ; '1'
stb r1+4, r2
const r2, 45
stb r1+5, r2
const r2, 79
stb r1+6, r2
const r2, 75
stb r1+7, r2
const r2, 32
stb r1+8, r2
const r2, 13         ; '\\r'
stb r1+11, r2
const r2, 10         ; '\\n'
stb r1+12, r2
const r2, 4
shr r5, r4, r2       ; 120 >> 4 = 7
const r2, 15
and r5, r5, r2
const r2, 48
add r5, r5, r2       ; '7'
stb r1+9, r5
const r2, 15
and r5, r4, r2       ; 120 & 15 = 8
const r2, 48
add r5, r5, r2       ; '8'
stb r1+10, r5
const r3, 4096       ; devbase
const r1, 0
const r2, 1
const r6, 13
print:
ldb r5, r1+0
stb r3+0, r5
add r1, r1, r2
lt r7, r1, r6
jnz r7, print
halt 0
fact:
const r2, 1
lt r3, r1, r2        ; r3 = (n < 1)
jnz r3, fbase
const r2, 8
sub r13, r13, r2     ; push: sp -= 8
stq r13+0, r1        ; [sp] = n
const r2, 1
sub r1, r1, r2       ; n -= 1
call fact            ; r4 = (n-1)!
ldq r1, r13+0        ; pop n
const r2, 8
add r13, r13, r2     ; sp += 8
mul r4, r1, r4       ; r4 = n * (n-1)!
jmp fdone
fbase:
const r4, 1          ; 0! = 1
fdone:
ret
"""

# --- T-E7-30: демо v2 «U-DATA-OK 61» — секция данных .UP v2 (E7.4-1) -
# Строка "U-DATA-OK 00" (14 Б) приходит из .data -> RAM[0:14]; код
# дописывает hex-цифры 97 = 0x61 и печатает 14 байт регистром
# консоли; 89 шагов.
DATA_VM = """\
; UNIVERSAL / UNIVM v1 / .UP v2: секция данных инициализирует
; RAM при загрузке. Строка "U-DATA-OK 00" лежит в RAM[0..13] из
; .data; код дописывает hex-цифры 97 = 0x61 и печатает 14 байт
; регистром консоли. Печатает "U-DATA-OK 61\\r\\n" (89 шага).
.mem 4096
.data 55 2D 44 41 54 41 2D 4F 4B 20 30 30 0D 0A
const r5, 97
const r2, 4
shr r6, r5, r2       ; 97 >> 4 = 6
const r2, 15
and r6, r6, r2
const r2, 48
add r6, r6, r2       ; '6'
const r1, 10
stb r1+0, r6
const r2, 15
and r6, r5, r2       ; 97 & 15 = 1
const r2, 48
add r6, r6, r2       ; '1'
stb r1+1, r6
const r1, 0          ; индекс
const r3, 4096        ; devbase
const r2, 1
const r7, 14
print:
ldb r6, r1+0
stb r3+0, r6
add r1, r1, r2
lt r8, r1, r7
jnz r8, print
halt 0
"""

# --- T-E7-02: отвержение ассемблера (номер строки с 1) -----------------
ASM_ERRORS = [
    ("неизвестная мнемоника", ".mem 4096\nfoo r1, 5\nhalt 0\n", 2),
    ("регистр вне диапазона", ".mem 4096\nconst r16, 5\nhalt 0\n", 2),
    ("заглавный регистр", ".mem 4096\nconst R1, 5\nhalt 0\n", 2),
    ("imm вне int32", ".mem 4096\nconst r1, 9999999999\nhalt 0\n", 2),
    ("нет директивы .mem", "const r1, 5\nhalt 0\n", 1),
    ("повторная .mem", ".mem 4096\n.mem 8192\nhalt 0\n", 2),
    ("неизвестная метка", ".mem 4096\njmp nowhere\nhalt 0\n", 2),
    ("дубликат метки", ".mem 4096\nl:\nl:\nhalt 0\n", 3),
    ("лишний операнд", ".mem 4096\nadd r1, r2, r3, r4\nhalt 0\n", 2),
    ("мало операндов", ".mem 4096\nadd r1, r2\nhalt 0\n", 2),
    ("stb: значение первым", ".mem 4096\nstb r2, r1+0\nhalt 0\n", 2),
    ("отрицательная память", ".mem -1\nhalt 0\n", 1),
    ("память сверх предела", ".mem 999999999\nhalt 0\n", 1),
]


def _up_err(name):
    """Контейнер с полем по имени (заголовок 24 Б + 1 байт кода)."""
    head = {
        "сигнатура": b"XP01", "версия": b"UP01",
    }[name] if name in ("сигнатура", "версия") else b"UP01"
    ver = 3 if name == "версия" else 1      # v2 валидна с E7.4-1
    mem = 67108865 if name == "memsize сверх" else 4096
    code = 0 if name == "codesize 0" else 1
    res = 1 if name == "res != 0" else 0
    body = b"\x12" if code else b""
    if name == "короткий файл":
        return b"UP0"
    data = (head + ver.to_bytes(4, "little") + mem.to_bytes(8, "little")
            + code.to_bytes(4, "little") + res.to_bytes(4, "little") + body)
    if name == "лишние байты":
        data += b"\x00"
    return data


UP_ERRORS = ["короткий файл", "сигнатура", "версия", "memsize сверх",
             "codesize 0", "лишние байты", "res != 0"]


def _rawup(mem, code, dat=b"", ver=2, off=None):
    """Сырой v2-контейнер для проверки отказов (dataoff — вручную)."""
    off = (24 + len(code) if dat else 0) if off is None else off
    return (b"UP01" + ver.to_bytes(4, "little")
            + mem.to_bytes(8, "little") + len(code).to_bytes(4, "little")
            + off.to_bytes(4, "little") + code + dat)


V2_ERRORS = [
    ("VER: версия 3", lambda: _rawup(4096, b"\x12" * 6, b"AA", ver=3),
     "VER"),
    ("RES: dataoff мусор", lambda: _rawup(4096, b"\x12" * 6, b"AA",
                                           off=31), "RES"),
    ("RES: данные заявлены, байтов нет",
     lambda: _rawup(4096, b"\x12" * 6, b"", off=30), "RES"),
    ("LEN: код обрезан", lambda: _rawup(4096, b"\x12" * 6, b"AA")[:-3],
     "LEN"),
    ("LEN: dataoff=0 и лишние байты",
     lambda: _rawup(4096, b"\x12" * 6, b"", off=0) + b"\x00", "LEN"),
    ("DATA: данные длиннее RAM", lambda: _rawup(4, b"\x12" * 6, b"12345"),
     "DATA"),
]
