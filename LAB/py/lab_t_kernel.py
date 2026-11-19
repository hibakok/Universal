"""lab_t_kernel.py — секция 14 батареи: ядро kernel.exe (M3-UNIVM, E7.2).

Вход:  функции kpath/kfile/kernel_host от lab_verify (путь/чтение файлов
       KERNEL/), счётчик check.
Выход: проверки T-E7-09..18 + T-E7-32 (срезы E7.2-1..4 ядра на WALL
       + E7.4-2a контейнер v2): сборка ядра конвейером инструментов
       под эмуляцией (фикс-пункт воспроизводимости артефактов), контракт
       CLI/контейнера .UP, диффтест ядра с оракулом lab_vm на корпусе
       срезов.
Функция: доказать, что ядро kernel.exe (KERNEL/L3-UNIVM) собирается из
         kernel.wall самими инструментами репозитория (wall/enc/brick/
         pegen) байт-в-байт и исполняет программы .UP в точном
         соответствии с оракулом UNIVM (консоль/код возврата/ловушки/
         счётчик шагов в диагностике).
Срез E7.2-1: halt-программы и перво-инструкция-ловушка; срез
E7.2-2: регистры + ALU (опкоды 01..0B) — декодирование (поля-
заполнители -> ловушка 1), границы выборки (обрезки -> 2), точные
счётчики шагов и отсутствие ложных ловушек. Срез E7.2-3: память и
устройства — опкоды 0C..0F (RAM, sext8, невыровненные слова, окно
устройств: окно+0 = консоль; чтение окна = 0, резерв игнорируется),
границы SPEC/12 п. 3.3 (ловушки 3/4), memsize = 0. Срез E7.2-4
(ФИНАЛ этапа): переходы jmp/jnz (10..11 — петли вперёд/назад, не
взят, границы кода; полный корпус программ T-E7-04..08 — demo/ops/
dev) и ПРЕДЕЛ ШАГОВ: trap 6, лимит — необязательный 2-й аргумент
CLI (0..2147483647, умолчание 200 млн), проверка ДО выборки
инструкции — как параметр max_steps оракула run().
Срез E7.4-2a: контейнер .UP v2 — ядро принимает версии {1, 2} и
секцию данных (dataoff = 24+codesize): данные -> RAM[0:datalen]
при загрузке; отказы LEN/RES/DATA — в порядке оракула parse_up;
диффтест v0-программ с .data (данные наблюдаемы ldb + консоль).
Корпуса программ — lab_t_kernel_corpus.py (данные; лимит 500 строк).
"""
import os
import tempfile

import lab_l2
import lab_splice
import lab_run
import lab_vm
import lab_t_kernel_corpus as corpus

S_USE = b"U-L3-UNIVM CMDS: KERNEL <FILE.UP> [STEPS]\r\n"
S_LONG = b"U-L3-UNIVM ERR=LONG NAME\r\n"
S_OUP = b"U-L3-UNIVM ERR=OPEN UP\r\n"


def _up(mem, code, ver=1, res=0, tail=b"", sig=b"UP01", sig_pad=b""):
    """Контейнер .UP ручной сборки (байты заголовка — полями)."""
    return (sig + ver.to_bytes(4, "little") + mem.to_bytes(8, "little")
            + len(code).to_bytes(4, "little") + res.to_bytes(4, "little")
            + sig_pad + code + tail)


def _v2(mem, code, data):
    """Контейнер v2 с секцией данных (dataoff = 24+codesize)."""
    return (b"UP01" + (2).to_bytes(4, "little") + mem.to_bytes(8, "little")
            + len(code).to_bytes(4, "little")
            + (24 + len(code)).to_bytes(4, "little") + code + data)


def _v2n(mem, code):
    """Контейнер v2 без данных (dataoff = 0 — v1-эквивалент)."""
    return (b"UP01" + (2).to_bytes(4, "little") + mem.to_bytes(8, "little")
            + len(code).to_bytes(4, "little")
            + (0).to_bytes(4, "little") + code)


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


def _krun(exe_path, up_bytes, name="t.up", args=None):
    """Прогон ядра на .UP-файле (виртуальная ФС; args — CLI-аргументы)."""
    return lab_run.run_kv(exe_path, args if args is not None else [name],
                          {name: up_bytes})


def _want_line(err):
    return b"U-L3-UNIVM ERR=" + err + b"\r\n"


def _trap_line(trap, steps):
    return b"U-L3-UNIVM TRAP=%d STEPS=%d\r\n" % (trap, steps)


def _diff(bad, kexe, name, data, lim=None):
    """Диффтест ядра с оракулом на одной программе (консоль/код/шаги).

    Ожидание ядра строится из RunResult оракула: нормальный останов —
    консоль + код возврата; ловушка — консоль + TRAP/STEPS + код 1
    (контракт SPEC/13 п. 4). lim — предел шагов (E7.2-4): оракулу —
    параметр run(max_steps), ядру — второй аргумент CLI; None —
    умолчание 200 млн у обоих.
    """
    if lim is None:
        o = lab_vm.run_up(data)
        r = _krun(kexe, data)
    else:
        o = lab_vm.run_up(data, max_steps=lim)
        r = _krun(kexe, data, args=["t.up", str(lim)])
    if o.trap:
        want, code = o.console + _trap_line(o.trap, o.steps), 1
    else:
        want, code = o.console, o.exit_code
    if r.stdout != want or r.exit_code != code:
        bad.append("%s: %r код=%s (trap=%d steps=%d)"
                   % (name, r.stdout[:30], r.exit_code, o.trap, o.steps))


def run(check, kpath, kfile, kernel_host):
    """Секция 14: T-E7-09..18 (ядро kernel.exe, срезы E7.2-1..4)."""
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
        # длинное имя, отсутствие файла; срез 4: необязательный предел
        # шагов — приятие (100 / максимум 2147483647 / 0), отвержение
        # (не-цифры, переполнение, знак, третий аргумент)
        halt0 = _up(0, b"\x12\x00\x00\x00\x00\x00")
        cases = [(b"no args", [], {}, S_USE, 2),
                 (b"extra", ["t.up", "x"], {"t.up": _up(0, b"\x12" * 6)},
                  S_USE, 2),
                 (b"long", ["a" * 128], {}, S_LONG, 3),
                 (b"open", ["x.up"], {}, S_OUP, 4),
                 (b"limit ok", ["t.up", "100"], {"t.up": halt0}, b"", 0),
                 (b"limit max", ["t.up", "2147483647"],
                  {"t.up": halt0}, b"", 0),
                 (b"limit 0", ["t.up", "0"], {"t.up": halt0},
                  _trap_line(6, 0), 1),
                 (b"limit text", ["t.up", "12x"], {}, S_USE, 2),
                 (b"limit big", ["t.up", "99999999999"], {}, S_USE, 2),
                 (b"limit 2^31", ["t.up", "2147483648"], {}, S_USE, 2),
                 (b"limit neg", ["t.up", "-5"], {}, S_USE, 2),
                 (b"limit 3rd", ["t.up", "5", "x"], {}, S_USE, 2)]
        bad = []
        for name, args, host, want, code in cases:
            r = lab_run.run_kv(kexe, args, host)
            if r.stdout != want or r.exit_code != code:
                bad.append("%s: %r код=%s" % (name.decode(),
                                              r.stdout[:32], r.exit_code))
        check("T-E7-10 CLI ядра: справка/лишний/длина/открытие/предел (%d)"
              % len(cases), not bad, "; ".join(bad[:2]))

        # T-E7-11: контейнер .UP — отказы SPEC/13 п. 4 (порядок как оракул);
        # E7.4-2a: v2 — отказы LEN (код обрезан/лишний байт при dataoff=0),
        # RES (dataoff-мусор, данные заявлены и отсутствуют), DATA
        # (длиннее RAM; memsize = 0)
        goodsig = b"\x12\x00\x00\x00\x00\x00"
        conts = [
            ("короткий", b"UP0"),
            ("подпись", _up(0, goodsig, sig=b"XP01")),
            ("версия", _up(0, goodsig, ver=3)),   # v2 валидна с E7.4-2a
            ("mem+1", _up(67108865, goodsig)),
            ("mem hi", _up(4294967296, goodsig)),
            ("codesize 0", _up(0, b"")),
            ("LEN короткий", _up(0, goodsig)[:-1]),
            ("LEN длинный", _up(0, goodsig, tail=b"\x00")),
            ("res", _up(0, goodsig, res=1)),
            ("v2 LEN: код обрезан", _up(0, goodsig, ver=2, res=30)[:-1]),
            ("v2 LEN: лишний байт при dataoff=0",
             _up(0, goodsig, ver=2, tail=b"\x00")),
            ("v2 RES: dataoff мусор", _up(0, goodsig, ver=2, res=999)),
            ("v2 RES: dataoff мусор + данные",
             _up(8, goodsig, ver=2, res=999, tail=b"\x41")),
            ("v2 RES: данные заявлены, нет байтов",
             _up(0, goodsig, ver=2, res=30)),
            ("v2 DATA: 9 Б > memsize 8",
             _up(8, goodsig, ver=2, res=30, tail=b"\x01" * 9)),
            ("v2 DATA: 1 Б > memsize 0",
             _up(0, goodsig, ver=2, res=30, tail=b"\x41")),
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
        check("T-E7-11 контейнер: отказы SIG/VER/MEM/CODE0/LEN/RES/DATA (%d)"
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
            ("опкод 25", _up(0, b"\x19\x00\x00")),  # 13..18 — v1 (E7.4-1)
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
        # Обрезки 0C..11 — длина валидного опкода до исполнителя
        # (ловушка 2); программы без halt — точные счётчики шагов в
        # TRAP=2 STEPS=n; ALU с halt — отсутствие ложных ловушек.
        bad = []
        for name, code in corpus.ALU_TRAPS:
            _diff(bad, kexe, name, lab_vm.make_up(0, code))
        for name, src in corpus.ALU_STEPS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        for name, src in corpus.ALU_HALT:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        check("T-E7-15 ALU среза 2: декод/ловушки/шаги == оракулу (%d)"
              % (len(corpus.ALU_TRAPS) + len(corpus.ALU_STEPS)
                 + len(corpus.ALU_HALT)),
              not bad, "; ".join(bad[:2]))

        # T-E7-16: память и устройства среза 3 — диффтест (консоль/код/
        # ловушки 3-4/шаги). Консоль (окно+0) делает значения регистров
        # и RAM наблюдаемыми: программы печатают результат eq-проверок
        # (расхождение с оракулом — в любом наблюдаемом байте).
        bad = []
        for name, src in corpus.MEM_RUNS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        for name, src in corpus.MEM_TRAPS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        check("T-E7-16 память/устройства: RAM+окно+границы == оракулу (%d)"
              % (len(corpus.MEM_RUNS) + len(corpus.MEM_TRAPS)),
              not bad, "; ".join(bad[:2]))

        # T-E7-17: переходы среза 4 — диффтест (jmp/jnz: петли вперёд/
        # назад, не взят, граница кода; цели за кодом — trap 2 после
        # выполненного перехода). Полный корпус программ оракула
        # T-E7-04..08: demo («U-VM-OK 37», 142 шага), ops (jmp через
        # мёртвый код), dev (окно); консоль делает значения наблюдаемыми.
        bad = []
        for name, src in corpus.JMP_RUNS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        for name, src in corpus.JMP_TRAPS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        check("T-E7-17 переходы jmp/jnz: корпус == оракулу (%d)"
              % (len(corpus.JMP_RUNS) + len(corpus.JMP_TRAPS)),
              not bad, "; ".join(bad[:2]))

        # T-E7-18: предел шагов — trap 6 (диагностика хозяина
        # исполнения, SPEC/12 п. 7; лимит — 2-й аргумент CLI, как
        # max_steps оракула): вечные циклы (jmp/jnz), halt ровно на
        # пределе — нормальный останов, сток кода на пределе — trap 6
        # (НЕ trap 2: предел проверяется до выборки pc), предел 0/1.
        bad = []
        for name, src, lim in corpus.LIM_RUNS:
            _diff(bad, kexe, name, lab_vm.assemble(src), lim)
        check("T-E7-18 предел шагов: trap 6 == оракулу (%d)"
              % len(corpus.LIM_RUNS), not bad, "; ".join(bad[:2]))

        # T-E7-32: контейнер v2 — секция данных -> RAM[0:datalen]
        # (E7.4-2a): диффтест с оракулом на v0-программах (.data —
        # сборка ассемблера оракула, контейнер v2); данные 4196 Б —
        # длиннее куска чтения ядра (4096: граница цикла read_data);
        # v2 dataoff=0 — v1-эквивалент (вывод == v1-контейнеру).
        bad = []
        for name, src in corpus.DATA_RUNS:
            _diff(bad, kexe, name, lab_vm.assemble(src))
        _mem, _code, _d = lab_vm.parse_up(
            lab_vm.assemble(corpus.DATA_CHUNK_SRC))
        _diff(bad, kexe, "data 4196 Б (куски чтения 4096)",
              _v2(_mem, _code, corpus.DATA_CHUNK))
        _mem, _code, _d = lab_vm.parse_up(
            lab_vm.assemble(corpus.DATA_NODATA_SRC))
        _diff(bad, kexe, "v1-контейнер (регрессия)",
              lab_vm.make_up(_mem, _code))
        _diff(bad, kexe, "v2 dataoff=0 (v1-эквивалент)", _v2n(_mem, _code))
        check("T-E7-32 контейнер v2: данные -> RAM == оракулу (%d)"
              % (len(corpus.DATA_RUNS) + 3), not bad, "; ".join(bad[:2]))
    finally:
        os.unlink(kexe)
