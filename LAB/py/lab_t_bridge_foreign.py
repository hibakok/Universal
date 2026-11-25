"""lab_t_bridge_foreign.py — секция 18f батареи: СПУСК В ЧУЖОМ ТЕЛЕ
(E9.4-3b; SPEC/15 п. 10 — parse_foreign: исполняемая секция по точке
входа + спуск + факты для PEG v2; ПОРТ В ИНСТРУМЕНТ — E9.4-4b-1:
развилка «семья | чужой» + чужая факт-строка).

Вход:  колбэк check из lab_verify + kpath/kfile (артефакты семейства —
       согласованность путей; с E9.4-4b-1 — ИНСТРУМЕНТ: bridge.exe из
       репозитория под эмуляцией lab_run).
Выход:  проверка T-E9-29: чужой путь моста:
         (1) чужой образ с ЖИВЫМ кодом (крафт foreign2_image —
         lab_t_bridge_corpus: вход 0x1020, спуск охватывает mov /
         call rel32 / jz rel32 / КОСВЕННЫЙ jmp [rip+X] с таблицей
         переходов (3 цели из данных) / add / xor / ret): секция кода
         выбирается по точке входа (.text, EXECUTE), факты
         entry_off/target/bss == якорям (vsize 0x400 > raw 0x200 —
         НАСТОЯЩАЯ bss-вилка чужого образа: вилка п. 7 обобщена на
         FileAlignment образа), спуск — 11 инструкций == якорям
         (включая операнды: цели call/jz, rip-таблица), импорты ОБЕИХ
         DLL и ОБЕ секции — в фактах (фундамент PEG v2);
         (2) отказы (7 мутантов foreign2): вход вне секций, нет
         EXECUTE, вход в bss, файл короче raw, Machine, FileAlignment
         не степень 2, num_sections 0;
         (3) СОГЛАСОВАННОСТЬ с parse_family: на всех 12 артефактах
         семейства факты обоих путей СОВПАДАЮТ на общих ключах
         (body/vsize/raw/target/bss/entry_off/ins) — обобщение вилки
         на FileAlignment верно семейству (0x200), спуск не изменился;
         (4) ПОРТ E9.4-4b-1/2/3 — bridge.exe на крафтах 3a/3b: ЧУЖАЯ
         факт-строка «U-L5-BRIDGE FOREIGN=1 SECT=… M=… H=…» == фактам
         parse_foreign + ВЫХОД M=/H= (K.foreign_line — статистика
         emit_b2_foreign, как семейная строка с E9.2-3c), код 0,
         ЗАПИСАН <выход>.b2 == тексту emit_b2_foreign байт-в-байт
         (E9.4-4b-2 — ПОРТ ЭМИССИИ b2 ЧУЖОГО ТЕЛА: шапка из
         выводимых фактов + M/H-строки, base = vaddr секции кода) и
         <выход>.peg == тексту emit_peg_v2 байт-в-байт (E9.4-4b-3 —
         ПОРТ PEG v2 ВЕТВИ G: канон патчей !pev2/!hdr/!body/!sec —
         сворачивание _fold/_chunks64 оракула); 7 мутантов —
         ERR=FAMILY, код 6 (отказы семьи и чужого фронта сходятся в
         общий код); НОВЫЙ отказ E9.4-4b-3 «файл короче raw прочих
         секций» (чужой крафт, обрезка .rdata при целом коде — у
         оракула отказ emit_peg_v2; у инструмента peg2_check ДО
         спуска/эмиссии): ERR=FAMILY, код 6, БЕЗ частичных выходов
         (t.b2/t.peg не создаются).
Функция: «сначала истина семантики» (прецедент E9.1/E9.4-3a): чужой
         путь — в оракуле ДО инструмента; срезы E9.4-4b-1..3 — ПОРТЫ
         развилки/фактов/эмиссий в bridge.exe (диффтест инструмент ==
         оракулу — «оракул впереди» замкнут; мутанты-«перевёртыши»
         T-E9-19 — тем же прогоном батареи). Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_bridge                         # noqa: E402
import lab_run                            # noqa: E402 — порт E9.4-4b-1
import lab_t_bridge_corpus as K           # noqa: E402 — данные E9.4-3b

# общие ключи фактов parse_family / parse_foreign (E9.4-3b)
SHARED = ("body", "vsize", "raw", "target", "bss", "entry_off", "ins")
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]

FAMILY_MSG = b"U-L5-BRIDGE ERR=FAMILY\r\n"


def run(check, kpath, kfile):
    """Секция 18f: T-E9-29 — спуск в чужом теле (E9.4-3b) + ПОРТ (4-4b-1)."""
    bad = []
    # (1) чужой образ: секция кода по входу + спуск + факты для PEG v2
    f = lab_bridge.parse_foreign(K.foreign2_image())
    if f["code"] != K.FOREIGN2_CODE:
        bad.append("секция кода %r" % (f["code"],))
    for k, v in K.FOREIGN2_FACTS.items():
        if f[k] != v:
            bad.append("факт %s: %r != %X" % (k, f[k], v))
    got = [(a, f["ins"][a][0], f["ins"][a][1]) for a in sorted(f["ins"])]
    if got != K.FOREIGN2_INS:
        bad.append("спуск %r" % (got,))
    for a, args in K.FOREIGN2_ARGS.items():
        if f["ins"][a][2] != args:
            bad.append("операнды @%X: %r" % (a, (f["ins"][a][2],)))
    if f["pe"]["sections"] != K.FOREIGN2_SECTIONS:
        bad.append("секции %r" % (f["pe"]["sections"],))
    if f["pe"]["imports"] != K.FOREIGN_IMPORTS:
        bad.append("импорты (факты для PEG v2)")
    # (2) отказы: мутанты foreign2 — все BridgeError
    for name, data in K.foreign2_rejects():
        try:
            lab_bridge.parse_foreign(data)
            bad.append("нет отказа: %s" % name)
        except lab_bridge.BridgeError:
            pass
    # (3) согласованность с parse_family на семействе (12 артефактов)
    for m in ARTIFACTS:
        data = kfile("%s.exe" % m)
        fam = lab_bridge.parse_family(data)
        fore = lab_bridge.parse_foreign(data)
        for k in SHARED:
            if fam[k] != fore[k]:
                bad.append("%s: %s != parse_family" % (m, k))
    # (4) ПОРТ E9.4-4b-1/2/3: bridge.exe — чужая факт-строка с M=/H=
    # == оракулу, код 0, t.b2 == emit_b2_foreign И t.peg ==
    # emit_peg_v2 байт-в-байт (E9.4-4b-3 — ПОРТ PEG v2, ветвь G);
    # мутанты + НОВЫЙ «файл короче raw прочих секций» (обрезка .rdata
    # при целом коде — peg2_check ДО эмиссии) — ERR=FAMILY (6) БЕЗ
    # частичных выходов
    bexe = kpath("L5-BRIDGE/bridge.exe")
    for name, img in (("foreign", K.foreign_image()),
                      ("foreign2", K.foreign2_image())):
        want_b2, _st = lab_bridge.emit_b2_foreign(img)
        want_peg = lab_bridge.emit_peg_v2(img)
        r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                           {"in.exe": img})
        if (r.exit_code != 0 or r.stdout != K.foreign_line(img)
                or r.files.get("t.b2") != want_b2.encode("utf-8")
                or r.files.get("t.peg") != want_peg.encode("utf-8")):
            bad.append("%s: ПОРТ (код %s, факт %r, b2 %s Б, peg %s Б,"
                       " файлы %r)"
                       % (name, r.exit_code, r.stdout[:60],
                          len(r.files.get("t.b2") or b""),
                          len(r.files.get("t.peg") or b""),
                          sorted(r.files)))
    trunc = K.foreign_image()[:0x900]
    try:
        lab_bridge.emit_peg_v2(trunc)
        bad.append("нет отказа оракула: файл короче raw прочих секций")
    except ValueError:
        pass
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                       {"in.exe": trunc})
    if (r.exit_code != 6 or r.stdout != FAMILY_MSG
            or "t.b2" in r.files or "t.peg" in r.files):
        bad.append("trunc-rdata: ПОРТ отказ (код %s, файлы %r)"
                   % (r.exit_code, sorted(r.files)))
    for name, data in K.foreign2_rejects():
        r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                           {"in.exe": data})
        if r.exit_code != 6 or r.stdout != FAMILY_MSG:
            bad.append("%s: ПОРТ отказ (код %s)" % (name, r.exit_code))
    check("T-E9-29 спуск в чужом теле: parse_foreign (секция по входу"
          " + спуск 11 инструкций вкл. таблицу переходов + факты"
          " PEG v2) + 7 отказов + согласованность 12 артефактов с"
          " parse_family + ПОРТ bridge.exe (чужая факт-строка с M=/H="
          " + t.b2 == emit_b2_foreign + t.peg == emit_peg_v2;"
          " отказы 8/8 без частичных выходов)", not bad,
          "; ".join(bad[:3]) if bad else
          "чужой: .text по входу, target 73/bss 38D, импорты 2 DLL;"
          " отказы 7/7 + trunc-rdata; семья: 12x7 общих ключей =="
          " parse_family; ПОРТ 2/2 крафта (факты+M/H+b2+peg)")
