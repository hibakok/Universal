"""bridge_labelmap.py — карта меток bridge.brick (RVA) для BYTECODE.md.

Вход:  KERNEL/L5-BRIDGE/bridge.brick (текст BRICK v1; запуск из корня).
Выход: печать «метка -> RVA hex» по возрастанию RVA (клон логики
       kernel_labelmap.py — только длины строк, без правки оракула).
Функция: диагностический инструмент обновления BYTECODE.md модуля
         M5-BRIDGE при пересборке bridge.exe (срезы E9.2+).
Запуск: python3 LAB/ai/bridge_labelmap.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

from label_map import labels_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    text = open(os.path.join(ROOT, "KERNEL", "L5-BRIDGE",
                            "bridge.brick"), "rb").read()
    labels = labels_of(text)
    pairs = sorted(((v, k) for k, v in labels.items()))
    for rva, name in pairs:
        print("%s .......... %04X" % (name, rva))
    print("всего меток: %d" % len(labels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
