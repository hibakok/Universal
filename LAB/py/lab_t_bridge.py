"""lab_t_bridge.py — секция 18 батареи: мост BRIDGE v1 (SPEC/15, E9.1/E9.2).

Вход:  колбэк check из lab_verify (kpath/kfile — единая сигнатура
         секций); артефакты читаются ИЗ РЕПОЗИТОРИЯ напрямую.
Выход:  проверки T-E9-01..21 — мост EXE -> BRICK v2 + PEG v1:
         (1) T-E9-01 — факты разбора seed.exe == якорю (поля тела,
             импорты, !bss) + детерминированный отказ чужому образу;
         (2) T-E9-02/03 — ПОЛНЫЕ тексты моста seed (b2 и peg) ==
             ручным якорям lab_bridge_cases.py (сверены с BYTECODE.md);
         (3) T-E9-04..14 — оракульный круг ВСЕХ 11 артефактов
             семейства: enc -> brick -> pegen (оракулы LAB) ==
             исходному EXE байт-в-байт (DoD среза E9.1, SPEC/15 п. 9);
         (4) T-E9-15/16 — сквозной круг РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ
             (эмуляция): enc.exe -> brick.exe -> pegen.exe на seed
             и hxdump — EXE == исходному, коды 0;
         (5) E9.2-1 (КАРКАС bridge.exe, M5-BRIDGE на WALL):
             T-E9-17 — фикс-пункт: сборка bridge.wall конвейером
             инструментов (wall -> enc -> brick -> pegen + bridge.peg)
             == артефактам репозитория байт-в-байт, bridge.b2 ==
             оракулу WALL; T-E9-18 — факт-строка каркаса (CLI 3
             аргумента, чтение EXE, разбор PE, семейная проверка) ==
             фактам оракула parse_family на ВСЕХ 11 артефактах +
             самом bridge.exe (12 прогонов); T-E9-19 — контракт CLI и
             отказы/перевёртыши (чужие: ОБА выхода == оракулу —
             E9.4-4b-3); T-E9-20 — круг над bridge.exe (12-й);
         (6) E9.2-2 (СПУСК — декодер + тени + target/bss): факт-строка
             расширена INS/TARGET/BSS (T-E9-18/19 — с новыми отказами
             спуска: инструкция за VirtualSize, длина тела больше
             VirtualSize — мутанты vsize);
             T-E9-21 — синтетика спуска: тень (цель jz ВНУТРИ соседней
             инструкции — младший адрес побеждает), нули — данные,
             терминал ret; факты == оракулу (в реальных артефактах
             теней нет — синтетика закрывает правила SPEC/15 п. 3);
         (7) E9.2-3a (RAW-ЭМИССИЯ): T-E9-22 — t.b2 (H-строки + DZ/DB,
             режим RAW emit_b2) == оракулу на 12 артефактах +
             синтетике спуска (полное операндное расширение
             декодера); T-E9-23 —
             сквозной круг raw-текста РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ
             (enc -> brick -> pegen) на мосте seed и hxdump —
             EXE == исходному (H-режим байто-точен всегда,
             SPEC/15 п. 5);
         (8) E9.2-3b (МЕТКИ И СЕМАНТИКА — режим "H"): T-E9-22 —
             выход t.b2 == оракулу emit_b2(mode="H") на ВСЕХ 12
             артефактах + синтетике спуска + синтетике меток
             (мутанты seed: hint-RVA СТРОГО ВНУТРЬ инструкции — метка
             не создаётся, таблицы DQ — сырыми байтами, b2 валиден
             (правило представимости SPEC/15 п. 6, зонд
             probe_e92_3b2); ПУСТАЯ таблица импорта impn=0 — без
             отказа: d*-метки имени/DLL, DD, DQ «0» терминатора) —
             для мутантов ДОПОЛНИТЕЛЬНО круг оракула (текст ->
             enc -> brick -> pegen == мутанту — валидность b2);
             T-E9-23 — сквозной круг H-текста (метки + DD/DQ +
             разрезы) РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ на мосте seed и hxdump;
         (9) E9.2-3c (M-СТРОКИ — КАНОН, mode=None): T-E9-22 — выход
             t.b2 == оракулу КАНОНА emit_b2 (M-строка при точном
             воспроизведении enc, иначе H-фолбэк — контроль
             повторным кодированием в инструменте: ветвь M
             bridge_self_m*.wall, 28 кирпичей; транслитерация-свидетель
             LAB/ai/trace_m.py — 46470/46470) на 12 артефактах +
             синтетике; факт-строка расширена ВЫХОДОМ M=<м>/H=<h>
             (T-E9-18 — статистика == оракулу); T-E9-23 —
             сквозной круг КАНОННОГО текста (M-строки парсятся enc)
             РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ на мосте seed и hxdump.
         (10) E9.2-4 (PEG-ВЫХОД — приёмка DoD этапа E9.2): T-E9-24 —
             выход t.peg == оракулу emit_peg (регенерация обёртки
             PEG v1, SPEC/15 п. 8: шапка/!module/!entry/!idata/
             !iat/!bss/!stackcom/!heapcom — опциональные только в
             хвосте) на ВСЕХ 12 артефактах + синтетике — тем же
             прогоном инструмента, что и T-E9-22 (оба файла по одному
             запуску — бюджет группы 4 не меняется); T-E9-23 — круг
             С PEG МОСТА (мост -> enc -> brick -> pegen == вход).
Функция: DoD E9.1 — «сначала истина семантики» (прецедент E7.1/E8.1):
         семантика моста закреплена оракулом и якорями ДО инструмента
         bridge.exe. E9.2-1 — каркас; E9.2-2 — спуск от входа:
         диффтест фактов == оракулу; E9.2-3a — raw-эмиссия; E9.2-3b —
         метки l/d/iat_ + семантика DD/DQ + разрезы (режим "H");
         E9.2-3c — M-строки канона + выход M=/H=; E9.2-4 — PEG-выход
         + приёмка DoD — ЭТАП E9.2 ЗАКРЫТ.
         ДАННЫЕ тестов (CLI-кейсы/мутанты/синтетика) — с E9.4-1 в
         lab_t_bridge_corpus.py (решение №4 сессии 74: этот файл был
         591 строк > лимита 500). FF /4 (косвенный jmp, E9.4-1) —
         секция 18c: lab_t_bridge_ff.py (T-E9-26); якоря — секция 18b
         lab_t_anchor.py (T-E9-25).
         Число проверок: 24.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                          # noqa: E402
import lab_bridge                         # noqa: E402
import lab_bridge_cases as C              # noqa: E402
import lab_enc                            # noqa: E402
import lab_l2                             # noqa: E402 — сборка (E9.2-1)
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402 — сборка (E9.2-1)
import lab_t_bridge_corpus as K           # noqa: E402 — данные (E9.4-1)
import lab_win                            # noqa: E402 — лимит шагов (E9.2-3a)

# все артефакты семейства (KERNEL/*/...exe) — по порядку слоёв
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva"]

# константы stdout каркаса и кейсы мутантов — K (данные секции 18
# вынесены в lab_t_bridge_corpus.py по лимиту 500 строк — решение №4
# сессии 74, срез E9.4-1; FF /4 — секция 18c lab_t_bridge_ff.py)

def _oracle_circle(check, kfile, m, tid):
    """Оракульный круг одного артефакта: compose(enc,brick,pegen)
    на выходе моста == исходный EXE байт-в-байт (SPEC/15 п. 9)."""
    data = kfile("%s.exe" % m)
    name = m.split("/")[-1]
    try:
        b2, peg = lab_bridge.bridge(data)
        body = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
        exe = lab_pegen.wrap(body, peg)
        _t, st = lab_bridge.emit_b2(data)
        ok = exe == data
        note = ("M=%d H=%d lab=%d %X Б"
                % (st["m"], st["h"], st["lab"], len(body)))
    except Exception as e:                     # noqa: BLE001
        ok, note = False, "EXC:" + repr(e)
    check("%s круг оракула: %s.exe == байт-в-байт" % (tid, name),
          ok, note)


def _tool_circle(check, kpath, kfile, m, tid):
    """Сквозной круг реальными инструментами (эмуляция LAB):
    enc.exe -> brick.exe -> pegen.exe; итог == исходному EXE."""
    data = kfile("%s.exe" % m)
    name = m.split("/")[-1]
    try:
        b2, peg = lab_bridge.bridge(data)
        r1 = lab_run.run_kv(kpath("L1-ENC/enc.exe"),
                            ["t.b2", "t.brick"], {"t.b2": b2.encode()})
        r2 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                            ["t.brick", "t.bin"],
                            {"t.brick": r1.files.get("t.brick", b"")})
        r3 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                            ["t.bin", "t.peg", "t.exe"],
                            {"t.bin": r2.files.get("t.bin", b""),
                             "t.peg": peg.encode()})
        made = r3.files.get("t.exe", b"")
        ok = (r1.exit_code == 0 and r2.exit_code == 0
              and r3.exit_code == 0 and made == data)
        note = ("enc=%d brick=%d pegen=%d шаги=%d+%d+%d"
                % (r1.exit_code, r2.exit_code, r3.exit_code,
                   r1.steps, r2.steps, r3.steps))
    except Exception as e:                     # noqa: BLE001
        ok, note = False, "EXC:" + repr(e)
    check("%s круг инструментами: %s.exe == оригиналу" % (tid, name),
          ok, note)


# ------------------------------------------------------- сборка (E9.2-1)
def build(kpath, kfile, kernel_host):
    """Сборка моста из bridge.wall конвейером (эмуляция инструментов).

    Возврат: (ok, artefacts dict, note) — b2/brick/bin/exe или причина.
    Шаг wall — с E9.2-3a выше лимита lab_run 200 млн шагов: прямой
    lab_win с лимитом 2 млрд (как T-E6-49a над wall.wall).
    """
    try:
        src = lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
        h = {"s.wall": src}
        # E9.2-3a: компиляция bridge.wall выше лимита lab_run 200 млн
        # шагов (операндное расширение: ~247 млн) — прямой lab_win
        # с лимитом 2 млрд (прецедент — фикс-пункт T-E6-49a)
        m = lab_win.Machine(kpath("L2-WALL/wall.exe"),
                            ["s.wall", "s.b2"], h)
        r1 = m.run(max_steps=2_000_000_000)
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
        h["s.peg"] = kfile("L5-BRIDGE/bridge.peg")
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


def facts_line(data):
    """Ожидаемая факт-строка — из оракула parse_family (E9.2-2: с
    полями спуска INS/TARGET/BSS; E9.2-3c: с выходом моста M=/H=
    — статистика emit_b2 канона: замена факт-строки реальным
    выходом, SPEC/15 п. 10)."""
    fam = lab_bridge.parse_family(data)
    pe = fam["pe"]
    _t, st = lab_bridge.emit_b2(data)
    return ("U-L5-BRIDGE MODULE=%s ENTRY=%08X VSIZE=%08X RAW=%08X IMP=%d"
            " INS=%d TARGET=%08X BSS=%08X M=%d H=%d\r\n"
            % (fam["module"], pe["addr_entry_point"], fam["vsize"],
               fam["raw"], len(pe["imports"][0]["funcs"]),
               len(fam["ins"]), fam["target"], fam["bss"],
               st["m"], st["h"])
            ).encode("latin1")


def _facts(check, bexe, data, label, tid=None):
    """Один прогон: факты + выход M=/H= == оракулу (или отказ)."""
    try:
        want = facts_line(data)
        err = False
    except lab_bridge.BridgeError:
        want, err = K.S_FAMILY, True
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                       {"in.exe": data})
    ok = r.stdout == want and r.exit_code == (6 if err else 0)
    if tid:
        check("%s %s: факты == оракулу" % (tid, label), ok,
              "%r код=%s" % (r.stdout[:44], r.exit_code))
    return ok


def _tool_cli(check, bexe, kfile):
    """T-E9-19: контракт CLI + семейные отказы (мутанты seed.exe —
    кейсы в corpus, вынесены по лимиту 500 — сессия 74)."""
    cases, legal = K.cli_cases(kfile("L0-SEED/seed.exe"))
    bad = []
    for name, args, host, want, code in cases:
        r = lab_run.run_kv(bexe, args, host)
        if r.stdout != want or r.exit_code != code:
            bad.append("%s: %r код=%s" % (name, r.stdout[:30],
                                          r.exit_code))
        elif want.startswith(b"U-L5-BRIDGE FOREIGN"):
            # ПОРТ 4b-2/3: перевёртыш — ОБА чужих выхода (t.b2 ==
            # emit_b2_foreign, t.peg == emit_peg_v2) == оракулу
            wtxt, _st = lab_bridge.emit_b2_foreign(host["in.exe"])
            wpeg = lab_bridge.emit_peg_v2(host["in.exe"])
            if (r.files.get("t.b2") != wtxt.encode("utf-8")
                    or r.files.get("t.peg") != wpeg.encode("utf-8")):
                bad.append("%s: чужой выход != оракулу" % name)
    # легальные отклонения семейства — успех с фактами == оракулу
    for name, data in legal:
        if not _facts(None, bexe, data, name):
            bad.append("легально отклонение %s — расхождение" % name)
    check("T-E9-19 CLI каркаса: справка/отказы/легальные отклонения (%d)"
          % (len(cases) + len(legal)), not bad, "; ".join(bad[:2]))


def run(check, kpath, kfile, kernel_host, use_repo=False):
    """Секция 18: T-E9-01..23 — мост BRIDGE v1 (E9.1 + E9.2-1..3c).

    use_repo (группа 4 песочницы, с E9.2-3c: сборка моста выросла до
    ~595 млн шагов wall и секция 18 целиком не вмещается в 10-минутный
    лимит песочницы — прецедент выделения секции 18 в группу 4):
    True — БЕЗ сборки: T-E9-18..23 гоняются на артефакте репозитория
    bridge.exe (фикс-пункт T-E9-17 — отдельная группа 5 / полный прогон
    в CI); тело синтетики — сборка bridge.brick оракулом brick.
    """
    seed = kfile("L0-SEED/seed.exe")

    # T-E9-01: факты разбора == якорю; чужой образ — отказ
    fam = lab_bridge.parse_family(seed)
    f = C.SEED_FACTS
    facts_ok = (fam["module"] == f["module"]
                and fam["entry_off"] == f["entry_off"]
                and fam["vsize"] == f["vsize"] and fam["raw"] == f["raw"]
                and fam["target"] == f["target"] and fam["bss"] == f["bss"]
                and [n for n, _r in fam["pe"]["imports"][0]["funcs"]]
                == f["imports"])
    try:
        lab_bridge.parse_family(b"MZ\x00" * 64)
        reject_ok = False
    except lab_bridge.BridgeError:
        reject_ok = True
    check("T-E9-01 разбор seed.exe == якорю (+отказ чужому)",
          facts_ok and reject_ok,
          "цель=%X bss=%X имп=%d" % (fam["target"], fam["bss"],
                                     len(f["imports"])))

    # T-E9-02/03: полные тексты моста == ручным якорям
    b2, _st = lab_bridge.emit_b2(seed)
    check("T-E9-02 мост seed.exe -> BRICK v2 == якорю",
          b2 == C.SEED_B2, "%d строк" % len(b2.splitlines()))
    peg = lab_bridge.emit_peg(seed)
    check("T-E9-03 мост seed.exe -> PEG v1 == якорю", peg == C.SEED_PEG,
          peg.splitlines()[-1])

    # T-E9-04..14: оракульный круг всех артефактов семейства
    for i, m in enumerate(ARTIFACTS):
        _oracle_circle(check, kfile, m, "T-E9-%02d" % (i + 4))

    # T-E9-15/16: сквозной круг реальными инструментами
    _tool_circle(check, kpath, kfile, "L0-SEED/seed", "T-E9-15")
    _tool_circle(check, kpath, kfile, "L0-HXDUMP/hxdump", "T-E9-16")

    # T-E9-17: сборка моста — фикс-пункт (E9.2-1): bridge.wall ->
    # (wall/enc/brick/pegen + bridge.peg) -> артефакты байт-в-байт;
    # при use_repo сборка пропускается (группа 4 — артефакт репо;
    # фикс-пункт — группа 5 / CI — run_fixpoint)
    a = None
    if not use_repo:
        ok, a, note = build(kpath, kfile, kernel_host)
        if ok:
            oracle = lab_l2.compile_wall(
                lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
                .decode("latin1")).encode()
            ok = (a["b2"] == oracle == kfile("L5-BRIDGE/bridge.b2")
                  and a["brick"] == kfile("L5-BRIDGE/bridge.brick")
                  and a["exe"] == kfile("L5-BRIDGE/bridge.exe"))
        check("T-E9-17 фикс-пункт: bridge.wall -> артефакты (байт-в-байт)",
              ok, note)
        if not ok:
            return                               # дальше без моста нет смысла

    fd, bexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    try:
        if use_repo:
            with open(bexe, "wb") as f:
                f.write(kfile("L5-BRIDGE/bridge.exe"))
        else:
            with open(bexe, "wb") as f:
                f.write(a["exe"])

        # тело для синтетики T-E9-21: сборка (или артефакт репо)
        if use_repo:
            body = lab_brick.assemble(kfile("L5-BRIDGE/bridge.brick"))
        else:
            body = a["bin"]

        # T-E9-18: факт-строка каркаса == оракулу на всём семействе
        # (11 артефактов + bridge.exe — 12-й член семейства)
        bad = []
        for m in ARTIFACTS:
            if not _facts(None, bexe, kfile("%s.exe" % m), m):
                bad.append(m)
        if not _facts(None, bexe, kfile("L5-BRIDGE/bridge.exe"),
                      "L5-BRIDGE/bridge"):
            bad.append("bridge")
        check("T-E9-18 факты (каркас+спуск) == оракулу (12 артефактов)",
              not bad, "; ".join(bad[:3]) if bad else "MODULE/ENTRY/"
              "VSIZE/RAW/IMP/INS/TARGET/BSS")

        # T-E9-19: контракт CLI + семейные отказы + легальные отклонения
        _tool_cli(check, bexe, kfile)

        # T-E9-21 (E9.2-2): синтетика спуска — тень (цель jz ВНУТРИ
        # соседней mov — младший адрес побеждает), нули — данные,
        # терминал ret; факты (INS/TARGET/BSS) == оракулу. В реальных
        # артефактах теней нет (probe оракулом) — синтетика закрывает
        # правила теней/нулей спуска (SPEC/15 п. 3): 0x200 jz +2,
        # 0x202 mov eax,imm32, 0x204 (цель jz) — add eax,imm32 — ТЕНЬ,
        # 0x207 ret, 0x208 нули — данные (крафт — корпус K)
        synth = K.synth_image(body[:0x200])
        _facts(check, bexe, synth, "synthm (тень/нули/ret)",
               tid="T-E9-21")

        # T-E9-22/24 (E9.2-3a/b/c + E9.2-4): эмиссия — выходные файлы
        # t.b2 и t.peg (ОДИН прогон инструмента на случай — оба файла
        # сверяются по одному запуску: бюджет группы 4 не меняется):
        # t.b2 == оракулу КАНОНА emit_b2 (без mode — E9.2-3c: M-строки
        # при точном воспроизведении enc, иначе H-фолбэк; метки
        # l/d/iat_ + семантика DD/DQ + разрезы — E9.2-3b; шапка/
        # H-строки/DZ/DB — E9.2-3a), t.peg == оракулу emit_peg
        # (E9.2-4 — регенерация обёртки PEG v1, SPEC/15 п. 8) на ВСЕХ
        # 12 артефактах семейства + синтетике спуска + синтетике меток:
        # мутант hint-ins (INT[0] указывает СТРОГО ВНУТРЬ выжившей
        # инструкции 0x2B+1 — метка d102c не создаётся, обе таблицы DQ
        # сырыми байтами, b2 ВАЛИДЕН — правило представимости
        # SPEC/15 п. 6) и мутант imp0 (таблица INT пуста — impn=0: без
        # отказа, DD + DQ «0»); для мутантов — и круг оракула
        # (enc -> brick -> pegen == мутанту — валидность текста);
        # сами мутанты — корпус K (lab_t_bridge_corpus.py, E9.4-1)
        mut_hint, mut_imp0 = K.seed_hints(kfile("L0-SEED/seed.exe"))
        bad_b2 = []
        bad_peg = []
        for m in ARTIFACTS:
            data = kfile("%s.exe" % m)
            want, _st = lab_bridge.emit_b2(data)
            wpeg = lab_bridge.emit_peg(data)
            r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": data})
            if r.exit_code != 0 or \
                    r.files.get("t.b2") != want.encode("utf-8"):
                bad_b2.append("%s (код %s, %d Б)"
                              % (m, r.exit_code,
                                 len(r.files.get("t.b2") or b"")))
            if r.exit_code != 0 or \
                    r.files.get("t.peg") != wpeg.encode("utf-8"):
                bad_peg.append("%s (код %s, %d Б)"
                               % (m, r.exit_code,
                                  len(r.files.get("t.peg") or b"")))
        synth_cases = [(synth, "synthm"), (mut_hint, "hint-ins"),
                       (mut_imp0, "imp0")]
        for data, mname in synth_cases:
            want, _st = lab_bridge.emit_b2(data)
            wpeg = lab_bridge.emit_peg(data)
            r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": data})
            ok = (r.exit_code == 0
                  and r.files.get("t.b2") == want.encode("utf-8")
                  and r.files.get("t.peg") == wpeg.encode("utf-8"))
            if not ok and (r.exit_code != 0
                           or r.files.get("t.b2") != want.encode("utf-8")):
                bad_b2.append("%s (код %s)" % (mname, r.exit_code))
            if not ok and (r.exit_code != 0
                           or r.files.get("t.peg") != wpeg.encode("utf-8")):
                bad_peg.append("%s (код %s)" % (mname, r.exit_code))
            if ok and mname != "synthm":      # круг = валидность b2
                try:
                    _b = lab_brick.assemble(
                        lab_enc.normalize(want).encode("utf-8"))
                    ok = lab_pegen.wrap(_b, lab_bridge.emit_peg(data)) \
                        == data
                except Exception as _e:         # noqa: BLE001
                    ok = False
            if not ok and mname != "synthm":
                bad_b2.append("%s (круг)" % mname)
        check("T-E9-22 эмиссия .b2 (КАНОН: M-строки при точном"
              " воспроизведении enc + метки + семантика) == оракулу"
              " (12 артефактов + синтетика)", not bad_b2,
              "; ".join(bad_b2[:2]) if bad_b2 else "шапка; M/H/DZ/DB/DD/DQ;"
              " метки")
        check("T-E9-24 эмиссия .peg (регенерация PEG v1, SPEC/15 п. 8)"
              " == оракулу (12 артефактов + синтетика)", not bad_peg,
              "; ".join(bad_peg[:2]) if bad_peg else
              "module/entry/idata/iat/bss/stackcom/heapcom")

        # T-E9-23 (E9.2-3a/b/c + E9.2-4 — ПРИЁМКА DoD ЭТАПА E9.2):
        # сквозной круг КАНОННОГО текста РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ
        # (M-строки + метки + семантика + разрезы байто-точны,
        # SPEC/15 п. 5/6/8): bridge.exe -> t.b2 + t.peg (ОБА ВЫХОДА
        # МОСТА — E9.2-4: peg берётся из выхода инструмента, не из
        # оракула) -> enc -> brick -> pegen(+peg моста) == исходный
        # EXE (seed и hxdump) — интеграция enc: M-строки парсятся
        # кодировщиком; круг Инструментами = DoD этапа E9.2
        bad = []
        for m in ("L0-SEED/seed", "L0-HXDUMP/hxdump"):
            data = kfile("%s.exe" % m)
            r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": data})
            b2 = r.files.get("t.b2", b"")
            peg = r.files.get("t.peg", b"")
            r1 = lab_run.run_kv(kpath("L1-ENC/enc.exe"),
                                ["t.b2", "t.brick"], {"t.b2": b2})
            r2 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                                ["t.brick", "t.bin"],
                                {"t.brick": r1.files.get("t.brick", b"")})
            r3 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                                ["t.bin", "t.peg", "t.exe"],
                                {"t.bin": r2.files.get("t.bin", b""),
                                 "t.peg": peg})
            made = r3.files.get("t.exe", b"")
            if not (r1.exit_code == 0 and r2.exit_code == 0
                    and r3.exit_code == 0 and made == data):
                bad.append("%s (enc=%s brick=%s pegen=%s)"
                           % (m.split("/")[-1], r1.exit_code,
                              r2.exit_code, r3.exit_code))
        check("T-E9-23 круг канонного текста инструментами: seed/hxdump =="
              " оригиналу", not bad, "; ".join(bad) if bad
              else "enc -> brick -> pegen")
    finally:
        os.unlink(bexe)

    # T-E9-20: оракульный круг моста над bridge.exe — 12-й артефакт
    _oracle_circle(check, kfile, "L5-BRIDGE/bridge", "T-E9-20")


def run_fixpoint(check, kpath, kfile, kernel_host):
    """Группа 5 песочницы (с E9.2-3c): ТОЛЬКО T-E9-17 — фикс-пункт
    сборки моста (bridge.wall -> wall/enc/brick/pegen -> артефакты
    байт-в-байт + b2 == оракулу WALL); вызывается отдельно, т.к. сборка
    (~595 млн шагов wall) + прогоны инструмента не вмещаются в один
    10-минутный вызов песочницы (группа 4 — остальные 22 проверки
    секции 18 на артефакте репозитория; полный прогон — CI/lab_verify).
    """
    ok, a, note = build(kpath, kfile, kernel_host)
    if ok:
        oracle = lab_l2.compile_wall(
            lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
            .decode("latin1")).encode()
        ok = (a["b2"] == oracle == kfile("L5-BRIDGE/bridge.b2")
              and a["brick"] == kfile("L5-BRIDGE/bridge.brick")
              and a["exe"] == kfile("L5-BRIDGE/bridge.exe"))
    check("T-E9-17 фикс-пункт: bridge.wall -> артефакты (байт-в-байт)",
          ok, note)
    return ok
