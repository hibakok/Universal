"""lab_t_kernel.py — секция 14 батареи: ядро kernel.exe (M3-UNIVM, E7.2).

Вход:  функции kpath/kfile/kernel_host от lab_verify (путь/чтение файлов
       KERNEL/), счётчик check.
Выход: проверки T-E7-09..15 (срезы E7.2-1..2 ядра на WALL):
       сборка ядра конвейером инструментов под эмуляцией (фикс-пункт
       воспроизводимости артефактов), контракт CLI/контейнера .UP,
       диффтест ядра с оракулом lab_vm на корпусе срезов.
Функция: доказать, что ядро kernel.exe (KERNEL/L3-UNIVM) собирается из
         kernel.wall самими инструментами репозитория (wall/enc/brick/
         pegen) байт-в-байт и исполняет программы .UP в точном
         соответствии с оракулом UNIVM (консоль/код возврата/ловушки/
         счётчик шагов в диагностике).
Срез E7.2-1: halt-программы и перво-инструкция-ловушка; срез
E7.2-2: регистры + ALU (опкоды 01..0B) — декодирование (поля-
заполнители -> ловушка 1), границы выборки (обрезки -> 2, ВКЛ.
заглушки 0C..11: длина валидного опкода проверяется до заглушки),
точные счётчики шагов (программы без halt: pc за кодом ->
TRAP=2 STEPS=<число команд>) и отсутствие ложных ловушек на
ALU-программах с halt. Результаты ALU напрямую не наблюдаемы до
среза E7.2-3 (консоль-устройство) — значения регистров станут видны
через вывод; шаги нормального останова ядром не печатаются
(контракт SPEC/13 п. 4).
"""
import os
import tempfile

import lab_l2
import lab_splice
import lab_run
import lab_vm

S_USE = b"U-L3-UNIVM CMDS: KERNEL <FILE.UP>\r\n"
S_LONG = b"U-L3-UNIVM ERR=LONG NAME\r\n"
S_OUP = b"U-L3-UNIVM ERR=OPEN UP\r\n"

# --- T-E7-15: ALU-программы среза 2 (const/mov/ALU; диффтест) --------
# Сырые байты — ловушки полей (4) и обрезанные инструкции (3) в порядке
# SPEC/12 п. 7; обрезки 0C..11 доказывают, что длина валидного опкода
# проверяется ДО заглушки среза (ловушка 2, не 1).
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


def _up(mem, code, ver=1, res=0, tail=b"", sig=b"UP01", sig_pad=b""):
    """Контейнер .UP ручной сборки (байты заголовка — полями)."""
    return (sig + ver.to_bytes(4, "little") + mem.to_bytes(8, "little")
            + len(code).to_bytes(4, "little") + res.to_bytes(4, "little")
            + sig_pad + code + tail)


def build(kpath, kfile, kernel_host):
    """Сборка ядра из kernel.wall конвейером (эмуляция инструментов).

    Возврат: (ok, artefacts dict, note) — b2/brick/bin/exe или причина.
    """
    try:
        src = lab_splice.splice("L3-UNIVM/kernel.wall", kernel_host())
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
        h["s.peg"] = kfile("L3-UNIVM/kernel.peg")
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


def _krun(exe_path, up_bytes, name="t.up"):
    """Прогон ядра на .UP-файле (виртуальная ФС)."""
    return lab_run.run_kv(exe_path, [name], {name: up_bytes})


def _want_line(err):
    return b"U-L3-UNIVM ERR=" + err + b"\r\n"


def _trap_line(trap, steps):
    return b"U-L3-UNIVM TRAP=%d STEPS=%d\r\n" % (trap, steps)


def _diff(bad, kexe, name, data):
    """Диффтест ядра с оракулом на одной программе (консоль/код/шаги).

    Ожидание ядра строится из RunResult оракула: нормальный останов —
    консоль + код возврата; ловушка — консоль + TRAP/STEPS + код 1
    (контракт SPEC/13 п. 4).
    """
    o = lab_vm.run_up(data)
    if o.trap:
        want, code = o.console + _trap_line(o.trap, o.steps), 1
    else:
        want, code = o.console, o.exit_code
    r = _krun(kexe, data)
    if r.stdout != want or r.exit_code != code:
        bad.append("%s: %r код=%s (trap=%d steps=%d)"
                   % (name, r.stdout[:30], r.exit_code, o.trap, o.steps))


def run(check, kpath, kfile, kernel_host):
    """Секция 14: T-E7-09..15 (ядро kernel.exe, срезы E7.2-1..2)."""
    # T-E7-09: сборка ядра — фикс-пункт: kernel.wall -> (wall/enc/brick/
    # pegen, эмуляция) -> артефакты байт-в-байт; kernel.b2 == оракулу WALL
    ok, a, note = build(kpath, kfile, kernel_host)
    if ok:
        oracle = lab_l2.compile_wall(
            lab_splice.splice("L3-UNIVM/kernel.wall", kernel_host())
            .decode("latin1")).encode()
        ok = (a["b2"] == oracle == kfile("L3-UNIVM/kernel.b2")
              and a["brick"] == kfile("L3-UNIVM/kernel.brick")
              and a["exe"] == kfile("L3-UNIVM/kernel.exe"))
    check("T-E7-09 фикс-пункт: kernel.wall -> артефакты (байт-в-байт)",
          ok, note)
    if not ok:
        return                                    # дальше без ядра нет смысла

    fd, kexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    try:
        with open(kexe, "wb") as f:
            f.write(a["exe"])

        # T-E7-10: CLI — справка (нет аргументов), лишний аргумент,
        # длинное имя, отсутствие файла
        cases = [(b"no args", [], {}, S_USE, 2),
                 (b"extra", ["t.up", "x"], {"t.up": _up(0, b"\x12" * 6)},
                  S_USE, 2),
                 (b"long", ["a" * 128], {}, S_LONG, 3),
                 (b"open", ["x.up"], {}, S_OUP, 4)]
        bad = []
        for name, args, host, want, code in cases:
            r = lab_run.run_kv(kexe, args, host)
            if r.stdout != want or r.exit_code != code:
                bad.append("%s: %r код=%s" % (name.decode(),
                                              r.stdout[:32], r.exit_code))
        check("T-E7-10 CLI ядра: справка/лишний/длина/открытие (%d)"
              % len(cases), not bad, "; ".join(bad[:2]))

        # T-E7-11: контейнер .UP — отказы SPEC/13 п. 4 (порядок как оракул)
        goodsig = b"\x12\x00\x00\x00\x00\x00"
        conts = [
            ("короткий", b"UP0"),
            ("подпись", _up(0, goodsig, sig=b"XP01")),
            ("версия", _up(0, goodsig, ver=2)),
            ("mem+1", _up(67108865, goodsig)),
            ("mem hi", _up(4294967296, goodsig)),
            ("codesize 0", _up(0, b"")),
            ("LEN короткий", _up(0, goodsig)[:-1]),
            ("LEN длинный", _up(0, goodsig, tail=b"\x00")),
            ("res", _up(0, goodsig, res=1)),
        ]
        bad = []
        for name, data in conts:
            try:
                lab_vm.parse_up(data)
                bad.append("%s: оракул принял" % name)
                continue
            except lab_vm.UpError as e:
                want = _want_line(e.reason.encode())
            r = _krun(kexe, data)
            if r.stdout != want or r.exit_code != 6:
                bad.append("%s: %r код=%s" % (name, r.stdout[:26],
                                             r.exit_code))
        check("T-E7-11 контейнер: отказы SIG/VER/MEM/CODE0/LEN/RES (%d)"
              % len(conts), not bad, "; ".join(bad[:2]))

        # T-E7-12: halt-программы — диффтест с оракулом (консоль/код)
        halts = [
            ("halt 0", _up(0, goodsig)),
            ("halt 37", _up(0, b"\x12\x00\x25\x00\x00\x00")),
            ("halt max", _up(0, b"\x12\x00\xff\xff\xff\xff")),
            ("mem 4096", _up(4096, b"\x12\x00\x07\x00\x00\x00")),
        ]
        bad = []
        for name, data in halts:
            o = lab_vm.run_up(data)
            r = _krun(kexe, data)
            if r.stdout != o.console or r.exit_code != o.exit_code \
                    or o.trap != 0 or o.steps != 1:
                bad.append("%s: %r код=%s" % (name, r.stdout[:26],
                                              r.exit_code))
        check("T-E7-12 halt-программы: ядро == оракулу (%d)" % len(halts),
              not bad, "; ".join(bad[:2]))

        # T-E7-13: ловушки 1/2 — диффтест диагностики (trap/шаги/код 1)
        traps = [
            ("опкод 0", _up(0, b"\x00\x00\x00")),
            ("опкод 19", _up(0, b"\x13\x00\x00")),
            ("halt rd", _up(0, b"\x12\x01\x05\x00\x00\x00")),
            ("halt усечён", _up(0, b"\x12\x00")),
            ("halt 1 байт", _up(0, b"\x12")),
        ]
        bad = []
        for name, data in traps:
            o = lab_vm.run_up(data)
            want = o.console + _trap_line(o.trap, o.steps)
            r = _krun(kexe, data)
            if r.stdout != want or r.exit_code != 1 or o.trap == 0:
                bad.append("%s: %r код=%s (trap=%d steps=%d)"
                           % (name, r.stdout[:30], r.exit_code,
                              o.trap, o.steps))
        check("T-E7-13 ловушки 1/2: диагностика == оракулу (%d)"
              % len(traps), not bad, "; ".join(bad[:2]))

        # T-E7-14: детерминизм — два прогона идентичны
        data = _up(0, b"\x12\x00\x25\x00\x00\x00")
        r1 = _krun(kexe, data)
        r2 = _krun(kexe, data)
        check("T-E7-14 детерминизм ядра (2 прогона halt 37)",
              r1.stdout == r2.stdout and r1.exit_code == r2.exit_code,
              "%r код=%s" % (r1.stdout[:24], r1.exit_code))

        # T-E7-15: ALU среза 2 — диффтест (поля/обрезки/шаги/halt).
        # Обрезки 0C..11 — длина валидного опкода до заглушки (ловушка 2);
        # программы без halt — точные счётчики шагов в TRAP=2 STEPS=n;
        # ALU с halt — отсутствие ложных ловушек (консоль/код).
        bad = []
        for name, code in ALU_TRAPS:
            _diff(bad, kexe, name, lab_vm.make_up(0, code))
        for name, src in ALU_STEPS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        for name, src in ALU_HALT:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        check("T-E7-15 ALU среза 2: декод/ловушки/шаги == оракулу (%d)"
              % (len(ALU_TRAPS) + len(ALU_STEPS) + len(ALU_HALT)),
              not bad, "; ".join(bad[:2]))
    finally:
        os.unlink(kexe)
