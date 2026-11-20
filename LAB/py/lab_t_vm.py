"""lab_t_vm.py — секция 13 батареи: оракул UNIVM (SPEC/12 v0+v1 + SPEC/13 v1/v2).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; здесь не используются: у оракула нет
         артефактов KERNEL — ядро kernel.exe появится на E7.2).
Выход: проверки T-E7-01..08 (E7.1, ISA v0 + .UP v1) + T-E7-26..31
         (E7.4-1, ISA v1 + .UP v2).
Функция: (1) якорные кодировки всех 18 опкодов v0, выписанные вручную
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
         предел шагов (trap 6) — в блоке 8; (9) E7.4-1: якоря 6
         опкодов v1 (mul/div/mod/sra/call/ret — T-E7-26), семантика
         mul/div/mod/sra с заворотом и знаковым sra (T-E7-27),
         демо-факториал 5 рекурсией через стек вызовов + программный
         стек r13 (T-E7-28, «U-VM1-OK 78»), ловушки 5/7 с точными
         шагами и порядком проверок (T-E7-29 — источники ловушечных
         программ в TRAP_VMS корпуса, единый свидетель с секцией 15 —
         E7.4-4), контейнер v2:
         секция данных .data -> RAM[0:datalen] + отказы VER/RES/LEN/
         DATA (T-E7-30, «U-DATA-OK 61»), детерминизм v1/v2 (T-E7-31).
"""
import lab_vm
import lab_up
from lab_t_vm_corpus import (ANCHORS, V1_ANCHORS, DEMO_VM, OPS_VM,
                              DEV_VM, OPS2_VM, FACT_VM, DATA_VM,
                              TRAP_VMS, ASM_ERRORS, UP_ERRORS,
                              V2_ERRORS, _up_err)

def run(check, kpath, kfile, kernel_host):
    """Секция 13: T-E7-01..08 + T-E7-26..31 (оракул UNIVM, SPEC/12-13)."""
    # T-E7-01: якорные кодировки — ассемблер == ручным байтам SPEC/12
    bad = []
    for line, want in ANCHORS:
        data = lab_vm.assemble(".mem 4096\n%s\nhalt 0\n" % line)
        _mem, code, _dat = lab_vm.parse_up(data)
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

    # T-E7-26: якорные кодировки v1 — ассемблер == ручным байтам SPEC/12
    bad = []
    for line, want in V1_ANCHORS:
        data = lab_vm.assemble(".mem 4096\n%s\nhalt 0\n" % line)
        _mem, code, _dat = lab_vm.parse_up(data)
        got = code[:len(want) // 2].hex().upper()
        if got != want:
            bad.append("%s: %s != %s" % (line, got, want))
    check("T-E7-26 якорные кодировки ISA v1 (6 опкодов)", not bad,
          "; ".join(bad[:2]))

    # T-E7-27: семантика mul/div/mod/sra — регистры-эталоны
    r = lab_vm.run_asm(OPS2_VM)
    check("T-E7-27 mul/div/mod/sra: заворот, частные, знаковый sra"
          " (24 шага)",
          r.exit_code == 0 and r.trap == 0 and r.steps == 24
          and r.regs[3] == 0 and r.regs[4] == 83810205
          and r.regs[5] == 14 and r.regs[6] == 2 and r.regs[7] == 0
          and r.regs[8] == 0 and r.regs[9] == 16
          and r.regs[10] == (1 << 64) - 16 and r.regs[11] == (1 << 64) - 1
          and r.regs[12] == (1 << 64) - 256,
          "r3=%d r4=%d r5=%d r6=%d r10=%X r11=%X шаги=%d"
          % (r.regs[3], r.regs[4], r.regs[5], r.regs[6], r.regs[10],
             r.regs[11], r.steps))

    # T-E7-28: демо v1 — факториал рекурсией (стек вызовов + r13)
    r = lab_vm.run_asm(FACT_VM)
    check("T-E7-28 демо v1: 5! рекурсией -> 'U-VM1-OK 78' (188 шагов,"
          " r13 баланс)",
          r.console == b"U-VM1-OK 78\r\n" and r.exit_code == 0
          and r.trap == 0 and r.steps == 188 and r.regs[4] == 120
          and r.regs[13] == 4096,
          "консоль=%r r4=%d r13=%d шаги=%d"
          % (r.console, r.regs[4], r.regs[13], r.steps))

    # T-E7-29: ловушки 5/7 с точными шагами и порядком проверок
    # (источники ловушечных программ — TRAP_VMS корпуса: единый
    # свидетель с секцией 15, приёмка DoD 7.4 — E7.4-4)
    v1_traps = [(n, lab_vm.assemble(s), t, st)
                for n, s, t, st in TRAP_VMS] + [
        ("call rd!=0 (поле, не стек)",
         lab_vm.make_up(4096, bytes([0x17, 0x03, 0, 0, 0, 0])), 1, 0),
        ("call обрезан (ловушка 2 до исполнения)",
         lab_vm.make_up(4096, bytes([0x17, 0x00, 0])), 2, 0),
        ("div rb=16 (поле, не ноль)",
         lab_vm.make_up(4096, bytes([0x14, 0x12, 0x10])), 1, 0),
        ("опкод 0x19 вне v1",
         lab_vm.make_up(4096, bytes([0x19, 0x00, 0x00])), 1, 0),
    ]
    bad = []
    for name, data, want_trap, want_steps in v1_traps:
        rr = lab_vm.run_up(data)
        if rr.trap != want_trap or rr.steps != want_steps:
            bad.append("%s: trap=%d шаги=%d" % (name, rr.trap, rr.steps))
    check("T-E7-29 ловушки 5/7 (%d случаев)" % len(v1_traps), not bad,
          "; ".join(bad[:2]))

    # T-E7-30: контейнер v2 — секция данных: сборка/разбор/инициализация
    up = lab_vm.assemble(DATA_VM)
    ver = int.from_bytes(up[4:8], "little")
    off = int.from_bytes(up[20:24], "little")
    mem, code, dat = lab_vm.parse_up(up)
    want_dat = bytes.fromhex("552D444154412D4F4B2030300D0A")
    v2_ok = (ver == 2 and off == 24 + len(code) and len(up) == off + 14
             and dat == want_dat and up == lab_up.make_up(4096, code, dat))
    r = lab_vm.run_up(up)
    d0 = lab_vm.assemble(DEMO_VM)              # без .data — остаётся v1
    bad = []
    for name, make, want in V2_ERRORS:
        try:
            lab_up.parse_up(make())
            bad.append("%s: не отвергнуто" % name)
        except lab_up.UpError as e:
            if e.reason != want:
                bad.append("%s: %s != %s" % (name, e.reason, want))
    check("T-E7-30 контейнер v2: .data -> RAM + отказы (%d)" % len(V2_ERRORS),
          v2_ok and r.console == b"U-DATA-OK 61\r\n" and r.exit_code == 0
          and r.trap == 0 and r.steps == 89
          and r.mem[:10] == want_dat[:10] and r.mem[10] == 0x36
          and r.mem[11] == 0x31 and r.mem[12:14] == b"\r\n"
          and d0[:8] == b"UP01\x01\x00\x00\x00" and d0[20:24] == b"\x00" * 4
          and not bad,
          "консоль=%r шаги=%d; %s" % (r.console, r.steps,
                                      "; ".join(bad[:2])))

    # T-E7-31: детерминизм v1/v2 — два прогона идентичны целиком
    a1, a2 = lab_vm.run_asm(FACT_VM), lab_vm.run_asm(FACT_VM)
    b1, b2 = lab_vm.run_asm(DATA_VM), lab_vm.run_asm(DATA_VM)
    check("T-E7-31 детерминизм v1/v2 (факториал + данные)",
          (a1.console, a1.exit_code, a1.steps, a1.trap, a1.regs, a1.mem)
          == (a2.console, a2.exit_code, a2.steps, a2.trap, a2.regs, a2.mem)
          and (b1.console, b1.exit_code, b1.steps, b1.trap, b1.regs, b1.mem)
          == (b2.console, b2.exit_code, b2.steps, b2.trap, b2.regs, b2.mem)
          and a1.steps == 188 and b1.steps == 89,
          "FACT шаги=%d DATA шаги=%d" % (a1.steps, b1.steps))
