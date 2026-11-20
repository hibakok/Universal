"""lab_t_uva.py — секция 15 батареи: ассемблер uva.exe (M3-UVA, E7.3..E7.4-4).

Вход:  функции kpath/kfile/kernel_host от lab_verify (путь/чтение файлов
       KERNEL/), счётчик check.
Выход: проверки T-E7-19..25, T-E7-35 (срезы E7.3-1..4 + E7.4-3a +
       E7.4-3b + ПРИЁМКА DoD ЭТАПА 7.4 — E7.4-4 — каркас ассемблера
       .uva -> .UP на WALL + таблица
       мнемоник/регистры/кодировка F1 + F2 const/память + F3 jmp/jnz
       с метками + МНЕМОНИКИ ISA v1: mul/div/mod/sra — F1 по 3
       операнда, call — F3 с целью метка|число, ret — F0, 1 байт без
       операндов + ДИРЕКТИВА .data и контейнер .UP v2: байты hex2
       копятся по порядку появления, выход — версия 2 с dataoff =
       24+codesize, без .data — v1 байт-в-байт): сборка конвейером
       инструментов под эмуляцией (фикс-пункт воспроизводимости
       артефактов), контракт CLI, диффтест с ассемблером оракула
       lab_vm.assemble байт-в-байт (halt-корпус среза 1 + F1-корпус
       среза 2 + F2-корпус среза 3 + F3-корпус среза 4 + v1-корпус
       E7.4-3a + .data-корпус E7.4-3b: успехи — контейнер v2 ==
       оракулу, отвержение — строки == AsmError.line), отвержение
       с номерами строк (== AsmError.line оракула), контракт CODE0
       (пустая программа, в тч. только метки, .mem+.data без кода)
       и контракт DATA (данные длиннее RAM — как make_up оракула,
       ПОСЛЕ ошибок операндов: ERR=DATA код 6, T-E7-35) и сквозной
       круг uva -> kernel.exe (вкл. jnz-цикл, jmp-переход,
       mul в консоль окном устройств, call/ret-подпрограмму, демо
       DATA_VM «U-DATA-OK 61» — секция данных -> RAM при загрузке —
       И ЛОВУШЕЧНЫЕ круги TRAP_VMS: ловушки 5/7 с точными шагами
       — двойной свидетель T-E7-29/34, путь ЦЕЛИКОМ uva -> ядро);
       T-E7-25 — ПРИЁМКА DoD ЭТАПА 7.4: якорные кодировки всех 24
       опкодов (T-E7-01/26, ручные свидетели) и ВСЕ программы
       секции 13 (DEMO_VM/OPS_VM/DEV_VM + OPS2_VM/FACT_VM + DATA_VM
       — T-E7-04..08/27/28/30 + ловушечные TRAP_VMS — T-E7-29)
       собираются uva == оракулу байт-в-байт.
Функция: доказать, что ассемблер uva.exe (KERNEL/L3-UVA) собирается из
         uva.wall самими инструментами репозитория байт-в-байт и
         повторяет ассемблер оракула на полном классе этапа 7.3
         (.mem + все 18 мнемоник ISA v0 + метки), срезов E7.4-3a
         (мнемоники v1 — все 24 инструкции ISA v0+v1) и E7.4-3b
         (директива .data + контейнер .UP v2) — и на ПОЛНОМ корпусе
         v0+v1 (E7.4-4: DATA_VM + ловушечные программы — приёмка
         DoD этапа 7.4).
"""
import os
import tempfile

import lab_l2
import lab_splice
import lab_run
import lab_t_vm
import lab_vm
from lab_t_uva_corpus import CODE0_CASES, DATA_CASES, ERR_CASES, OK_CASES

S_USE = b"U-L3-UVA CMDS: UVA <SRC.UVA> <OUT.UP>\r\n"
S_LONG = b"U-L3-UVA ERR=LONG NAME\r\n"
S_OSRC = b"U-L3-UVA ERR=OPEN SRC\r\n"
S_BIG = b"U-L3-UVA ERR=BIG SRC\r\n"
S_CODE0 = b"U-L3-UVA ERR=CODE0\r\n"
S_DATA = b"U-L3-UVA ERR=DATA\r\n"


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


def run(check, kpath, kfile, kernel_host):
    """Секция 15: T-E7-19..25 (ассемблер uva.exe, срезы E7.3-1..4)."""
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

        # T-E7-23: CODE0 — .mem без инструкций (как make_up оракула;
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

        # T-E7-35 (E7.4-3b): DATA — данные длиннее RAM (datalen >
        # memsize — как make_up оракула; ПОСЛЕ ошибок операндов —
        # make_header после прохода 2; ПОСЛЕ CODE0 — проход 1):
        # uva обязан печатать ERR=DATA (код 6) и не создавать файл
        bad = []
        for name, src in DATA_CASES:
            try:
                lab_vm.assemble(src.decode("latin1"))
                bad.append("%s: оракул принял" % name)
                continue
            except lab_vm.UpError as e:
                if e.reason != "DATA":
                    bad.append("%s: причина %s" % (name, e.reason))
                    continue
            out, code, got = _uva(uexe, src)
            if out != S_DATA or code != 6 or got is not None:
                bad.append("%s: %r код=%s" % (name, out[:26], code))
        check("T-E7-35 DATA: данные > memsize (%d)" % len(DATA_CASES),
              not bad, "; ".join(bad[:2]))

        # T-E7-24: сквозной круг uva -> kernel.exe (внешняя программа
        # собирается ассемблером и исполняется ядром; F1 — срез 2,
        # F2 — срез 3: const/stb/stq/ldq + вывод в консоль окном
        # устройств; F3 — срез 4: jnz-цикл и jmp-переход; v1 — срез
        # E7.4-3a: mul в консоль и call/ret-подпрограмма; v2 — срез
        # E7.4-3b: демо DATA_VM — секция данных .data -> RAM при
        # загрузке, печать «U-DATA-OK 61» — как T-E7-30 секции 13;
        # E7.4-4 — ЛОВУШЕЧНЫЕ круги TRAP_VMS: ловушки 5/7 с точными
        # шагами и код 1 — двойной свидетель T-E7-29/34, путь ЦЕЛИКОМ
        # uva -> kernel.exe)
        # + детерминизм
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
                                 b"stb r6+0, r5\nhalt 0\n", 0, b"F"),
                (b"f3 jnz loop", b".mem 8\nconst r1, 0\nconst r2, 1\n"
                                  b"const r3, 3\nl:\nadd r1, r1, r2\n"
                                  b"lt r4, r1, r3\njnz r4, l\nhalt 5\n",
                 5, b""),
                (b"f3 jmp skip", b".mem 8\njmp skip\nhalt 1\nskip:\nhalt 2\n",
                 2, b""),
                (b"v1 mul console", b".mem 4096\nconst r2, 6\nconst r3, 7\n"
                                     b"mul r1, r2, r3\nconst r4, 4096\n"
                                     b"stb r4+0, r1\nhalt 0\n", 0, b"*"),
                (b"v1 call/ret", b".mem 8\ncall sub\nhalt 5\nsub:\n"
                                   b"const r1, 65\nconst r2, 8\nstb r2+0, r1\n"
                                   b"ret\n", 5, b"A"),
                (b"v2 data demo", lab_t_vm.DATA_VM.encode("utf-8"),
                 0, b"U-DATA-OK 61\r\n")]:
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
        # ловушечные круги (E7.4-4): программы TRAP_VMS — путь ЦЕЛИКОМ
        # uva -> kernel.exe; ядро печатает TRAP=код STEPS=шаги и
        # возвращает 1 (двойной свидетель T-E7-29/34 — те же программы,
        # те же шаги; исходники БЕЗ кириллицы — latin1 == utf-8)
        for name, src, trap, steps in lab_t_vm.TRAP_VMS:
            want_out = b"U-L3-UNIVM TRAP=%d STEPS=%d\r\n" % (trap,
                                                                 steps)
            out, code, got = _uva(uexe, src.encode("latin1"))
            if code != 0 or got is None:
                bad.append("%s: сборка код=%s" % (name, code))
                continue
            k = lab_run.run_kv(kpath("L3-UNIVM/kernel.exe"),
                               ["t.up"], {"t.up": got})
            if k.exit_code != 1 or k.stdout != want_out:
                bad.append("%s: ядро код=%s %r" % (name, k.exit_code,
                                                   k.stdout[:24]))
        o1, c1, g1 = _uva(uexe, OK_CASES[0][1])
        o2, c2, g2 = _uva(uexe, OK_CASES[0][1])
        if not (c1 == c2 == 0 and g1 == g2 and g1 is not None):
            bad.append("детерминизм: код %s/%s" % (c1, c2))
        check("T-E7-24 круг uva -> kernel.exe (15) + детерминизм",
              not bad, "; ".join(bad[:2]))

        # T-E7-25: ПРИЁМКА DoD ЭТАПА 7.4 (расширение приёмки 7.3 —
        # полный корпус v0+v1): якорные кодировки всех 24 опкодов
        # (T-E7-01 — v0 + T-E7-26 — v1, ручные свидетели, сверяются
        # с байтами ВЫХОДА uva напрямую), ВСЕ демо-программы секции
        # 13 (DEMO_VM/OPS_VM/DEV_VM — T-E7-04..08; OPS2_VM/FACT_VM —
        # T-E7-27/28, v1; DATA_VM — T-E7-30, v2 .data) и ЛОВУШЕЧНЫЕ
        # программы TRAP_VMS (T-E7-29 — ловушки 5/7) собираются
        # uva == оракулу байт-в-байт
        bad = []
        for line, want_hex in lab_t_vm.ANCHORS + lab_t_vm.V1_ANCHORS:
            src = (".mem 64\n" + line + "\n").encode("latin1")
            out, code, got = _uva(uexe, src)
            if code != 0 or got is None or \
                    got[24:].hex().upper() != want_hex:
                bad.append("якорь %r: код=%s" % (line, code))
        for name, prog in (("DEMO_VM", lab_t_vm.DEMO_VM),
                           ("OPS_VM", lab_t_vm.OPS_VM),
                           ("DEV_VM", lab_t_vm.DEV_VM),
                           ("OPS2_VM", lab_t_vm.OPS2_VM),
                           ("FACT_VM", lab_t_vm.FACT_VM),
                           ("DATA_VM", lab_t_vm.DATA_VM)):
            # UTF-8: кириллица в комментариях программ секции 13 — байты
            # комментариев обрезаются до разбора (комментарий ';')
            want = lab_vm.assemble(prog)
            out, code, got = _uva(uexe, prog.encode("utf-8"))
            if code != 0 or got != want:
                bad.append("%s: код=%s" % (name, code))
        # ловушечные программы (T-E7-29): оракул собирает, uva —
        # байт-в-байт то же (исходники без кириллицы)
        for name, src, _trap, _steps in lab_t_vm.TRAP_VMS:
            want = lab_vm.assemble(src)
            out, code, got = _uva(uexe, src.encode("latin1"))
            if code != 0 or got != want:
                bad.append("%s: код=%s" % (name, code))
        check("T-E7-25 DoD 7.4: якоря T-E7-01/26 (24) + программы "
              "T-E7-04..08/27/28/30 + TRAP (10) — uva == оракулу",
              not bad, "; ".join(bad[:2]))
    finally:
        os.unlink(uexe)
