"""lab_t_anchor.py — секция 18b батареи: ЯКОРНАЯ ФИКСАЦИЯ МОСТА (E9.3-1).

Вход:  колбэк check из lab_verify (+ kfile — байты артефактов и якорей
         KERNEL/); оракул lab_bridge (канон SPEC/15 п. 4-8).
Выход:  проверка T-E9-25 — выход оракула (канон .b2 + PEG .peg) для
         ВСЕХ 12 артефактов семейства байт-в-байт равен файлам якорей
         KERNEL/<м>/<имя>.anchor.b2 / KERNEL/<м>/<имя>.anchor.peg.
Функция: якорь — СТАТИЧЕСКИЙ свидетель (как листинги .hex у L0,
         ROADMAP E9.3): фиксирует одновременно (а) поведение оракула,
         (б) артефакты KERNEL/ и — транзитивно через T-E9-22/24
         («инструмент == оракул» на том же корпусе) — (в) выход
         инструмента bridge.exe. Изменение якоря видно в git одним
         diff'ом; случайная регенерация = потеря свидетеля
         (генератор — LAB/ai/anchor_gen.py, только при намеренном
         изменении выхода моста — отдельным коммитом).
         Ошибки чтения/декодирования = провал (не пропуск).
         Число проверок: 1. Секция дешёвая (чистый Python, без
         эмуляции) — входит в группу 4 песочницы и полный прогон CI.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_bridge                          # noqa: E402

# все артефакты семейства (по порядку слоёв; bridge — 12-й член,
# = ARTIFACTS из lab_t_bridge + сам мост)
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]


def run(check, kfile):
    """T-E9-25: якоря репозитория == выходу оракула (12 артефактов)."""
    bad = []
    m_tot = h_tot = 0
    try:
        for m in ARTIFACTS:
            name = m.split("/")[-1]
            data = kfile("%s.exe" % m)
            b2, st = lab_bridge.emit_b2(data)
            peg = lab_bridge.emit_peg(data)
            m_tot += st["m"]
            h_tot += st["h"]
            ab2 = kfile("%s.anchor.b2" % m)
            apeg = kfile("%s.anchor.peg" % m)
            if b2.encode("utf-8") != ab2:
                bad.append("%s.anchor.b2" % name)
            if peg.encode("utf-8") != apeg:
                bad.append("%s.anchor.peg" % name)
    except Exception as e:                  # noqa: BLE001
        bad.append("EXC:" + repr(e))
    check("T-E9-25 якоря моста: оракул == файлам .anchor.b2/.peg "
          "(12 артефактов, E9.3)", not bad,
          "M=%d H=%d; %s" % (m_tot, h_tot,
                             "все 24 файла сходятся" if not bad
                             else "; ".join(bad[:4])))
    return not bad
