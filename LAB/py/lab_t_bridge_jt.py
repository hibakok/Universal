"""lab_t_bridge_jt.py — секция 18d батареи: таблицы переходов в оракуле
(E9.4-2; SPEC/15 п. 3/10).

Вход:  колбэк check из lab_verify + kfile (тело bridge.brick — префикс
       синтетики, как T-E9-21/26; оракул — ЧИСТЫЙ Python, без эмуляции
       инструментов).
Выход:  проверка T-E9-27 — рост спуска для чужих EXE на стороне
         оракула: косвенный jmp qword [rip+X] (X — в данных) даёт
         цели-кандидаты из qword-строк данных: (1) synth6 —
         switch-таблица: 2 цели (ret @0x20B/0x20C) -> спуск ровно
         4 инструкции, терминатор — нулевой qword; (2) synth7 —
         терминатор «qword вне тела» (0x9000): qword 0x20C ПОСЛЕ
         терминатора — НЕ кандидат (спуск ровно 3 инструкции,
         0x20C — данные); (3) факты (module/target/bss/vsize/raw)
         и строки региона >= 0x200 (H-строка jmp, M ret, данные
         таблицы DB/DZ, d-метка от rip-операнда) и PEG == якорям
         K; (4) круг оракула enc -> brick -> pegen == образу
         байт-в-байт (H-строки байто-точны всегда).
Функция: «сначала истина семантики» (прецедент E9.1): таблицы
         закреплены оракулом ДО порта в инструмент bridge.exe
         (E9.4+ при первом чужом круге). На СЕМЕЙСТВЕ срез
         нейтрален (снимок сессии 76: 12 артефактов — выходы
         до/после совпадают; FF /4 в семействе нет; инструмент
         == оракулу — T-E9-22/24/25). Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                          # noqa: E402
import lab_bridge                          # noqa: E402
import lab_enc                             # noqa: E402
import lab_pegen                           # noqa: E402
import lab_t_bridge_corpus as K            # noqa: E402 — данные E9.4-2


def run(check, kfile):
    """Секция 18d: T-E9-27 — таблицы переходов в оракуле моста."""
    bad = []
    body = lab_brick.assemble(kfile("L5-BRIDGE/bridge.brick"))
    cases = (("synth6", K.JT_CRAFT6, K.JT_FACTS6, K.JT_LINES6, K.JT_PEG6),
             ("synth7", K.JT_CRAFT7, K.JT_FACTS7, K.JT_LINES7, K.JT_PEG7))
    for name, craft, facts, lines, peg in cases:
        img = lab_pegen.wrap(body[:0x200] + craft, K.JT_PEG % name)
        try:
            fam = lab_bridge.parse_family(img)
            ins = [(a, fam["ins"][a][0], fam["ins"][a][1])
                   for a in sorted(fam["ins"])]
            if ins != facts["ins"]:
                bad.append("%s: спуск %r" % (name, ins))
            elif fam["ins"][0x205][2] != facts["arg"]:
                bad.append("%s: операнд jmp %r" % (name,
                                                  fam["ins"][0x205][2]))
            if (fam["module"] != facts["module"]
                    or fam["target"] != facts["target"]
                    or fam["bss"] != facts["bss"]
                    or fam["vsize"] != facts["vsize"]
                    or fam["raw"] != facts["raw"]):
                bad.append("%s: факты %s t=%X bss=%X v=%X r=%X"
                           % (name, fam["module"], fam["target"],
                              fam["bss"], fam["vsize"], fam["raw"]))
            b2, _st = lab_bridge.emit_b2(img)
            got = [ln for ln in b2.splitlines()
                   if "@02" in ln or "@03" in ln]
            if got != lines:
                bad.append("%s: строки %r" % (name, got[:2]))
            if lab_bridge.emit_peg(img) != peg:
                bad.append("%s: PEG" % name)
            # круг оракула: H-строки байто-точны (SPEC/15 п. 5)
            bb = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
            if lab_pegen.wrap(bb, lab_bridge.emit_peg(img)) != img:
                bad.append("%s: круг" % name)
        except Exception as e:                    # noqa: BLE001 — любой крах
            bad.append("%s: EXC %r" % (name, e))
    check("T-E9-27 таблицы переходов: jmp qword [rip+X] — цели-кандидаты"
          " из данных, «до первого non-code qword» (synth6/synth7)",
          not bad, "; ".join(bad[:3]) if bad else
          "2 образа; спуск 4/3 инструкции; круги байт-в-байт")
