"""lab_t_bridge_peg2e.py — секция 18h батареи: PEG v2 — ЭМИССИЯ МОСТОМ
(E9.4-3c-2; SPEC/15 п. 10 / SPEC/07 «Канон патчей»: чужие факты
parse_foreign -> текст канона патчей; оракул вперёд — ДО b2 чужого
тела и ДО портов в инструменты bridge.exe/pegen.exe).

Вход:  колбэк check из lab_verify + kfile (артефакты KERNEL/); чистый
       Python, без эмуляции инструментов.
Выход:  проверка T-E9-31: (1) ЭМИССИЯ == ЯКОРЯМ: lab_bridge.emit_peg_v2
       обоих чужих крафтов == якорным текстам T-E9-30 байт-в-байт
       (шапки якорей — выводимые, сессия 81); (2) КРУГ ЧЕРЕЗ ВЫХОД
       МОСТА (DoD среза): wrap2(тело-target, текст) == образ
       байт-в-байт (оба крафта); (3) УНИВЕРСАЛЬНОСТЬ: все 12
       артефактов семейства проходят ЧУЖОЙ ПУТЬ — wrap2(тело,
       emit_peg_v2) == EXE (модель «нули + патчи» покрывает и
       семью — PEG v1 остаётся частным случаем); (4) ОТКАЗ: файл
       короче raw прочих секций (обрезка .rdata чужого крафта при
       целом коде — parse_foreign пропускает, эмиссия обязана
       отвергнуть: байто-точность круга невозможна). Число
       проверок: 1.
Функция: «оракул вперёд» (прецедент E9.1/E9.4-3c-1): канон патчей
         закреплён якорями T-E9-30 ДО эмиссии — мост обязан повторить
         их текст; порт эмиссии в bridge.exe — при первом чужом круге.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_bridge                       # noqa: E402
import lab_pegen                        # noqa: E402
import lab_t_bridge_corpus as K         # noqa: E402
from lab_t_anchor import ARTIFACTS      # noqa: E402
from lab_t_bridge_peg2 import (         # noqa: E402
    FOREIGN_PEG2, FOREIGN2_PEG2)


def run(check, kfile):
    """Секция 18h: T-E9-31 — PEG v2, эмиссия мостом (E9.4-3c-2)."""
    bad = []
    # (1)+(2) крафты: эмиссия == якорям + круг через ВЫХОД моста
    for name, img, anchor in [
            ("foreign", K.foreign_image(), FOREIGN_PEG2),
            ("foreign2", K.foreign2_image(), FOREIGN2_PEG2)]:
        text = lab_bridge.emit_peg_v2(img)
        if text != anchor:
            bad.append("%s: эмиссия != якорю" % name)
        f = lab_bridge.parse_foreign(img)
        body = f["body"][:f["target"]]
        if lab_pegen.wrap2(body, text) != img:
            bad.append("%s: круг wrap2 != образу" % name)
    # (3) универсальность: 12 артефактов семьи через ЧУЖОЙ путь
    for m in ARTIFACTS:
        exe = kfile("%s.exe" % m)
        text = lab_bridge.emit_peg_v2(exe)
        f = lab_bridge.parse_foreign(exe)
        if lab_pegen.wrap2(f["body"][:f["target"]], text) != exe:
            bad.append("%s: чужой путь семьи" % m)
    # (4) отказ: файл короче raw прочих секций (код цел, .rdata обрезан)
    trunc = K.foreign_image()[:0x900]
    try:
        lab_bridge.emit_peg_v2(trunc)
        bad.append("нет отказа: файл короче raw прочих секций")
    except ValueError:
        pass
    check("T-E9-31 PEG v2 эмиссия мостом: emit_peg_v2 чужих крафтов == "
          "якорям T-E9-30 байт-в-байт + круг wrap2(тело, текст) == "
          "образу (DoD среза) + семья 12/12 через ЧУЖОЙ путь + отказ "
          "«файл короче raw прочих секций» (E9.4-3c-2)", not bad,
          "; ".join(bad[:3]) if bad else
          "крафты: 2/2 (якорь и круг); семья: 12/12; отказ: 1/1")
    return not bad


if __name__ == "__main__":
    ok = []

    def check(name, is_ok, note=""):
        ok.append(is_ok)
        print("[%s] %s %s" % ("OK" if is_ok else "FAIL", name, note))

    class KF:
        @staticmethod
        def kfile(rel):
            return open(os.path.join(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(
                    __file__)))), "KERNEL", rel), "rb").read()

    run(check, KF.kfile)
    sys.exit(0 if all(ok) else 1)
