# anchor_gen.py — генератор ЯКОРЕЙ МОСТА (E9.3-1, сессия 74).
# Паспорт: LAB/ai/anchor_gen.py | частная зона ИИ | роль: пишет якоря
# выхода моста для всех 12 артефактов семейства UNIVERSAL.
#
# Якорь — СТАТИЧЕСКИЙ файл-свидетель в репозитории (как листинги .hex
# у L0): KERNEL/<м>/<имя>.anchor.b2 + KERNEL/<м>/<имя>.anchor.peg ==
# выходу ОРАКУЛА lab_bridge (канон SPEC/15 п. 4-8, байт-в-байт, UTF-8,
# LF). Равенство «инструмент == оракул» на том же корпусе доказано
# батареей (T-E9-22/24), поэтому якорь фиксирует выход ОБОИХ
# (транзитивно: инструмент == оракул == якорь).
#
# Регенерация — ТОЛЬКО при намеренном изменении выхода моста (правка
# инструмента/оракула/артефакта): отдельный коммит «E9.3: якоря ...»
# + зелёный T-E9-25. Случайная регенерация = потеря свидетеля.
#
# Запуск: python3 LAB/ai/anchor_gen.py   (из корня репозитория)

import os
import sys

sys.path.insert(0, os.path.join("LAB", "py"))

import lab_bridge                             # noqa: E402

KERNEL = "KERNEL"

# все артефакты семейства (по порядку слоёв; bridge — 12-й член)
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]


def main():
    rows = []
    tot_b2 = tot_peg = 0
    for m in ARTIFACTS:
        name = m.split("/")[-1]
        with open(os.path.join(KERNEL, "%s.exe" % m), "rb") as f:
            data = f.read()
        b2, st = lab_bridge.emit_b2(data)
        peg = lab_bridge.emit_peg(data)
        pb2 = b2.encode("utf-8")
        ppeg = peg.encode("utf-8")
        with open(os.path.join(KERNEL, "%s.anchor.b2" % m), "wb") as f:
            f.write(pb2)
        with open(os.path.join(KERNEL, "%s.anchor.peg" % m), "wb") as f:
            f.write(ppeg)
        tot_b2 += len(pb2)
        tot_peg += len(ppeg)
        rows.append("%-8s anchor.b2 %7d Б / %5d строк (M=%5d H=%4d)"
                    " | anchor.peg %3d Б"
                    % (name, len(pb2), len(b2.splitlines()),
                       st["m"], st["h"], len(ppeg)))
    for r in rows:
        print(r)
    print("ИТОГО: 24 файла; b2 %d Б (%.2f МБ), peg %d Б"
          % (tot_b2, tot_b2 / 1048576.0, tot_peg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
