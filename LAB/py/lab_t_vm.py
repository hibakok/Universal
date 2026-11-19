"""lab_t_vm.py — секция 13 батареи: оракул UNIVM (SPEC/12 ISA v0 + SPEC/13).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; здесь не используются: у оракула нет
         артефактов KERNEL — ядро kernel.exe появится на E7.2).
Выход: проверки T-E7-01..08 (E7.1).
Функция: (1) якорные кодировки всех 18 опкодов, выписанные вручную
         по SPEC/12 п. 4-5 (независимый свидетель — как якоря ENC);
         (2) отвержение некорректных исходников ассемблера с номерами
         строк; (3) отвержение контейнеров .UP (причины SPEC/13 п. 4);
         (4) демо-круг: сумма 1..10 = 55 = 0x37, строка строится
         в RAM, печать через регистр консоли — «U-VM-OK 37»,
         142 шага; (5) ловушки 1-4 (поля-заполнители, выборка,
         границы RAM/окна) с точными счётчиками шагов; (6) детерминизм
         — два прогона идентичны целиком (консоль/код/шаги/регистры/
         память); (7) ops-программа: mov/sub/or/xor/shl/shr/eq/jmp/
         stq/ldq, эталоны регистров и памяти, код возврата 7;
         (8) окно устройств: консоль по окно+0, окно+1 игнорируется,
         чтение окна = 0. Границы: заворот адреса, memsize=0,
         предел шагов (trap 6) — в блоке 8.
"""
import lab_vm

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
    ver = 2 if name == "версия" else 1
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


def run(check, kpath, kfile, kernel_host):
    """Секция 13: T-E7-01..08 (оракул UNIVM, SPEC/12 + SPEC/13)."""
    # T-E7-01: якорные кодировки — ассемблер == ручным байтам SPEC/12
    bad = []
    for line, want in ANCHORS:
        data = lab_vm.assemble(".mem 4096\n%s\nhalt 0\n" % line)
        _mem, code = lab_vm.parse_up(data)
        got = code[:len(want) // 2].hex().upper()
        if got != want:
            bad.append("%s: %s != %s" % (line, got, want))
    check("T-E7-01 якорные кодировки ISA v0 (18 опкодов)", not bad,
          "; ".join(bad[:2]))

    # T-E7-02: отвержение ассемблера с номерами строк
    bad = []
    for name, src, line in ASM_ERRORS:
        try:
            lab_vm.assemble(src)
            bad.append("%s: не отвергнуто" % name)
        except lab_vm.AsmError as e:
            if e.line != line:
                bad.append("%s: строка %d, ждали %d"
                           % (name, e.line, line))
    check("T-E7-02 отвержение ассемблера (%d)" % len(ASM_ERRORS),
          not bad, "; ".join(bad[:2]))

    # T-E7-03: отвержение контейнеров .UP (причины SPEC/13 п. 4)
    bad = []
    for name in UP_ERRORS:
        try:
            lab_vm.parse_up(_up_err(name))
            bad.append("%s: не отвергнуто" % name)
        except lab_vm.UpError:
            pass
    check("T-E7-03 отвержение .UP (%d причин)" % len(UP_ERRORS),
          not bad, "; ".join(bad[:2]))

    # T-E7-04: демо — строка, сумма, hex, консоль
    r = lab_vm.run_asm(DEMO_VM)
    check("T-E7-04 демо: сумма 1..10 -> 'U-VM-OK 37' (142 шага)",
          r.console == b"U-VM-OK 37\r\n" and r.exit_code == 0
          and r.trap == 0 and r.steps == 142,
          "консоль=%r код=%d trap=%d шаги=%d"
          % (r.console, r.exit_code, r.trap, r.steps))

    # T-E7-05: ловушки 1-4 (поля, выборка, границы) с шагами
    traps = [
        ("опкод 00", lab_vm.make_up(4096, bytes([0x00])), 1, 0),
        ("mov rb!=0", lab_vm.make_up(4096, bytes([0x02, 0x23, 0x05])), 1, 0),
        ("const ra!=0",
         lab_vm.make_up(4096, bytes([0x01, 0x11, 0, 0, 0, 0])), 1, 0),
        ("jmp rd!=0",
         lab_vm.make_up(4096, bytes([0x10, 0x03, 0, 0, 0, 0])), 1, 0),
        ("jnz rd=16",
         lab_vm.make_up(4096, bytes([0x11, 0x10, 0, 0, 0, 0])), 1, 0),
        ("add rb=16", lab_vm.make_up(4096, bytes([0x03, 0x45, 0x10])), 1, 0),
        ("pc за концом",
         lab_vm.make_up(4096, bytes([0x01, 0x10, 5, 0, 0, 0])), 2, 1),
        ("обрезанная инструкция",
         lab_vm.make_up(4096, bytes([0x01, 0x10, 5])), 2, 0),
        ("ldb addr 2^64-1",
         lab_vm.assemble(".mem 4096\nconst r1, -1\nldb r2, r1+0\n"
                         "halt 0\n"), 3, 1),
        ("ldb за окном",
         lab_vm.assemble(".mem 4096\nconst r1, 8192\nldb r2, r1+0\n"
                         "halt 0\n"), 3, 1),
        ("stb за окном",
         lab_vm.assemble(".mem 4096\nconst r1, 9000\nconst r2, 65\n"
                         "stb r1+0, r2\nhalt 0\n"), 4, 2),
        ("ldq в окно",
         lab_vm.assemble(".mem 4096\nconst r1, 4096\nldq r2, r1+0\n"
                         "halt 0\n"), 3, 1),
        ("stq через край RAM",
         lab_vm.assemble(".mem 4096\nconst r1, 4092\nconst r2, 1\n"
                         "stq r1+0, r2\nhalt 0\n"), 4, 2),
        ("jnz на плохую цель",
         lab_vm.assemble(".mem 4096\nconst r1, 1\njnz r1, 999999\n"
                         "halt 0\n"), 2, 2),
    ]
    bad = []
    for name, data, want_trap, want_steps in traps:
        rr = lab_vm.run_up(data)
        if rr.trap != want_trap or rr.steps != want_steps:
            bad.append("%s: trap=%d шаги=%d" % (name, rr.trap, rr.steps))
    check("T-E7-05 ловушки 1-4 (%d случаев)" % len(traps), not bad,
          "; ".join(bad[:2]))

    # T-E7-06: детерминизм — два прогона идентичны целиком
    a = lab_vm.run_asm(DEMO_VM)
    b = lab_vm.run_asm(DEMO_VM)
    check("T-E7-06 детерминизм демо (2 прогона идентичны)",
          (a.console, a.exit_code, a.steps, a.trap, a.regs, a.mem)
          == (b.console, b.exit_code, b.steps, b.trap, b.regs, b.mem)
          and a.steps == 142, "шаги=%d" % a.steps)

    # T-E7-07: ops-программа — регистры/память/код/шаги
    r = lab_vm.run_asm(OPS_VM)
    mem100 = int.from_bytes(r.mem[100:108], "little")
    check("T-E7-07 ops: ALU+jmp+слова (r3/r4/r15/r6=88, 19 шагов)",
          r.exit_code == 7 and r.trap == 0 and r.steps == 19
          and r.regs[3] == 88 and r.regs[4] == 1 and r.regs[15] == 88
          and r.regs[6] == 88 and mem100 == 88,
          "код=%d r3=%d r4=%d r15=%d r6=%d mem100=%d шаги=%d"
          % (r.exit_code, r.regs[3], r.regs[4], r.regs[15], r.regs[6],
             mem100, r.steps))

    # T-E7-08: окно устройств + границы (заворот, mem=0, предел шагов)
    r = lab_vm.run_asm(DEV_VM)
    w = lab_vm.run_asm(".mem 4096\nconst r1, -1\nldb r2, r1+1\n"
                       "halt 0\n")                    # заворот -> addr 0
    z = lab_vm.run_asm(".mem 0\nconst r1, 0\nconst r2, 66\nstb r1+0, r2\n"
                       "halt 5\n")                    # консоль = адрес 0
    q = lab_vm.run_asm(".mem 0\nconst r1, 0\nldq r2, r1+0\nhalt 0\n")
    s = lab_vm.run_asm(".mem 4096\nloop:\njmp loop\n", max_steps=100)
    check("T-E7-08 устройства и границы (консоль/окно/заворот/mem=0)"
          " + предел шагов",
          r.console == b"AA" and r.regs[3] == 0 and r.steps == 7
          and w.trap == 0 and w.regs[2] == 0 and w.steps == 3
          and z.console == b"B" and z.exit_code == 5
          and q.trap == 3
          and s.trap == 6 and s.steps == 100,
          "AA=%r r3=%d заворот trap=%d mem0=%r ldq trap=%d цикл trap=%d"
          % (r.console, r.regs[3], w.trap, z.console, q.trap, s.trap))
