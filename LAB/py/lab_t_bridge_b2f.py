"""lab_t_bridge_b2f.py — секция 18i батареи: b2 ЧУЖОГО ТЕЛА — эмиссия
M/H-строк секции кода (E9.4-3c-3; SPEC/15 п. 4-6/10: факты ins/labels
parse_foreign -> канон тела; base = vaddr секции кода — имена меток
l/d — RVA; шапка без module/stackcom/heapcom — их у чужих образов нет).

Вход:  колбэк check из lab_verify + kfile (артефакты KERNEL/); чистый
       Python, без эмуляции инструментов.
Выход:  проверка T-E9-32: (1) ЧУЖОЙ КРУГ ЧЕРЕЗ ОБА ВЫХОДА МОСТА — DoD
       среза: оба чужих крафта — enc+brick(emit_b2_foreign) ==
       target-тело байт-в-байт + wrap2(тело, emit_peg_v2) == образ;
       (2) ДВОЙНОЙ ПУТЬ СЕМЬИ: 12 артефактов — строки тела чужого b2 ==
       строкам СЕМЕЙНОГО канона (после 3-строчных шапок; base 0x1000 —
       общая: чужой путь — обобщение семейного) + круг wrap2 == EXE;
       (3) наследование отказов parse_foreign (Machine не x86-64 —
       эмиссия обязана отвергнуть до рендера). Число проверок: 1.
Функция: «оракул вперёд» (прецедент E9.1/E9.4-3c-1/2): канон тела
         закреплён ДО порта эмиссии в bridge.exe — при первом чужом
         круге; импорты ВНЕ тела секции кода — сырыми байтами
         (обёртка чужого образа — PEG v2, секция 18h).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                        # noqa: E402
import lab_bridge                       # noqa: E402
import lab_enc                          # noqa: E402
import lab_pegen                        # noqa: E402
import lab_t_bridge_corpus as K         # noqa: E402
from lab_t_anchor import ARTIFACTS      # noqa: E402


def run(check, kfile):
    """Секция 18i: T-E9-32 — b2 чужого тела (E9.4-3c-3)."""
    bad = []
    # (1) чужой круг через ОБА выхода моста (b2 + PEG v2) — DoD среза
    for name, img in [
            ("foreign", K.foreign_image()),
            ("foreign2", K.foreign2_image())]:
        text, _st = lab_bridge.emit_b2_foreign(img)
        body = lab_brick.assemble(lab_enc.normalize(text)
                                  .encode("utf-8"))
        f = lab_bridge.parse_foreign(img)
        if body != f["body"][:f["target"]]:
            bad.append("%s: b2 != target-телу" % name)
        if lab_pegen.wrap2(body, lab_bridge.emit_peg_v2(img)) != img:
            bad.append("%s: круг b2+peg v2 != образу" % name)
    # (2) двойной путь семьи: тело чужого b2 == семейному канону
    #     (3 строки шапки у обоих; тела — с 4-й) + круг wrap2 == EXE
    for m in ARTIFACTS:
        exe = kfile("%s.exe" % m)
        fam_txt, _ = lab_bridge.emit_b2(exe)
        for_txt, _ = lab_bridge.emit_b2_foreign(exe)
        if fam_txt.split("\n", 3)[3] != for_txt.split("\n", 3)[3]:
            bad.append("%s: тело чужого b2 != семейному" % m)
        body = lab_brick.assemble(lab_enc.normalize(for_txt)
                                  .encode("utf-8"))
        if lab_pegen.wrap2(body, lab_bridge.emit_peg_v2(exe)) != exe:
            bad.append("%s: круг семьи через b2-выход" % m)
    # (3) отказы parse_foreign наследуются (эмиссия — рендер над фактами)
    mut = bytearray(K.foreign2_image())
    mut[0x104:0x106] = b"\x4C\x01"               # Machine 0x014C
    try:
        lab_bridge.emit_b2_foreign(bytes(mut))
        bad.append("нет отказа: Machine не x86-64")
    except ValueError:
        pass
    check("T-E9-32 b2 чужого тела: emit_b2_foreign крафтов == "
          "target-телу байт-в-байт (M/H-строки секции кода, base = "
          "vaddr) + ЧУЖОЙ КРУГ через ОБА выхода моста — enc+brick(b2) "
          "+ wrap2(тело, PEG v2) == образ (DoD среза) + семья 12/12 "
          "ДВОЙНЫМ ПУТЁМ (тела b2 == семейному канону) + наследование "
          "отказов parse_foreign (E9.4-3c-3)", not bad,
          "; ".join(bad[:3]) if bad else
          "крафты: 2/2 (тело и круг); семья: 12/12 двойным путём; "
          "отказ: 1/1")
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
