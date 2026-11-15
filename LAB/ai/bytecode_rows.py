"""bytecode_rows.py — перенос адресов карты ветвей BYTECODE.md (LAB/ai).

Вход:  два текста .brick (старый и новый сборки wall) + BYTECODE.md.
Выход: BYTECODE.md с переведёнными RVA (печать diff-плана; файл
       перезаписывается только с --write).
Функция: инструмент обновления §2 «Карта ветвей» KERNEL/L2-WALL/
         BYTECODE.md при пересборке wall.exe: адреса переводятся по
         якорям МЕТОК (адрес A: наибольшая метка L <= A -> новый A =
         RVA_new(L) + (A - RVA_old(L))) — вставки/удаления строк между
         метками переносимы; колонка адресов строк-заголовков секции
         переводится по ИМЕНИ первой метки строки; inline-адреса — по
         правилу «имя-метка + адрес» и «(адрес)» в скобках.
Правила: метки — из LAB/ai/label_map.py (labels_of); старый .brick —
         git HEAD (rev-parse), новый — текущий файл; скаляры [r13+X]
         НЕ переводятся (это смещения данных, не RVA).
Запуск: python3 LAB/ai/bytecode_rows.py [--write]
"""
import os
import re
import subprocess
import sys

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))
sys.path.insert(0, os.path.join(UNI, "LAB", "ai"))
from label_map import labels_of          # noqa: E402

DOC = os.path.join(UNI, "KERNEL", "L2-WALL", "BYTECODE.md")
BRICK = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.brick")

_HEX = r"[0-9A-F]{4,6}"


def _sorted_labels(text):
    if isinstance(text, str):
        text = text.encode("latin1")
    labs = labels_of(text)
    # labels_of даёт смещения от начала тела; BYTECODE.md — RVA (+1000)
    return sorted((rva + 0x1000, name) for name, rva in labs.items())


def _anchor_map(sorted_labs):
    """(rva, name) список -> функция старый-адрес -> новый-адрес."""
    rvas = [r for r, _n in sorted_labs]

    def translate(a, other_sorted):
        # наибольшая метка <= a в ЭТОЙ карте; перенос через парную
        i = bisect_right(rvas, a) - 1
        if i < 0:
            return a                      # до первой метки — не сдвигается
        r, name = sorted_labs[i]
        j = [n for _rr, n in other_sorted].index(name)
        rr = other_sorted[j][0]
        return rr + (a - r)
    return translate


from bisect import bisect_right         # noqa: E402


def main():
    old_txt = subprocess.run(
        ["git", "-C", UNI, "show", "HEAD:KERNEL/L2-WALL/wall.brick"],
        capture_output=True).stdout.decode("latin1")
    new_txt = open(BRICK, "r", encoding="latin1").read()
    old_labs = _sorted_labels(old_txt)
    new_labs = _sorted_labels(new_txt)
    old_names = {n for _r, n in old_labs}
    new_names = {n for _r, n in new_labs}
    gone = old_names - new_names
    added = new_names - old_names
    print("меток: старых %d, новых %d, исчезло %d, появилось %d"
          % (len(old_labs), len(new_labs), len(gone), len(added)))
    if gone:
        print("  исчезли: %s" % ", ".join(sorted(gone)))
    if added:
        print("  появились: %s" % ", ".join(sorted(added)))

    new_by_name = {n: r for r, n in new_labs}
    old_rvas = [r for r, _n in old_labs]
    old_list = old_labs

    def tr(a):
        """старый RVA -> новый RVA (якорь — наибольшая старая метка <= a)."""
        i = bisect_right(old_rvas, a) - 1
        if i < 0:
            return a
        r, name = old_list[i]
        nr = new_by_name.get(name)
        if nr is None:
            return None                   # якорь исчез — не переводим
        return nr + (a - r)

    doc = open(DOC, encoding="utf-8").read()
    lines = doc.split("\n")
    out = []
    changes = 0
    in_map = False
    for ln in lines:
        if ln.startswith("## 2."):
            in_map = True
            out.append(ln)
            continue
        if ln.startswith("## 3."):
            in_map = False
            out.append(ln)
            continue
        if not in_map or not ln.strip() or ln.startswith("```"):
            out.append(ln)
            continue
        m = re.match(r"^  (\S+?)(?:[. ]+ )(" + _HEX + r")(-(" + _HEX +
                     r"))?(.*)$", ln)
        if m and not ln.lstrip().startswith(";"):
            # строка-заголовок ветви: первая метка -> точный новый RVA
            first = re.split(r"/|\.\.", m.group(1))[0]
            start = int(m.group(2), 16)
            end = int(m.group(4), 16) if m.group(4) else None
            ns = new_by_name.get(first)
            if ns is not None:
                ne = tr(end) if end is not None else None
                if ne is None and end is not None:
                    ne = end
                repl = "%X" % ns + (("-" + "%X" % ne) if ne is not None
                                     else "")
                oldr = "%X" % start + (("-" + "%X" % end)
                                       if end is not None else "")
                if repl != oldr:
                    changes += 1
                    ln = ln.replace(oldr, repl, 1)
        else:
            # inline: «имя-метка ADDR» и «(ADDR)» — только hex в скобках
            def sub_lab(mm):
                nm = mm.group(1)
                a = int(mm.group(2), 16)
                if nm in new_by_name and nm in old_names:
                    na = tr(a)
                    if na is not None:
                        return "%s %X" % (nm, na)
                return mm.group(0)

            def sub_par(mm):
                a = int(mm.group(1), 16)
                na = tr(a)
                return "(%X)" % na if na is not None else mm.group(0)

            ln2 = re.sub(r"([A-Za-z_][A-Za-z_0-9]*) (" + _HEX + r")",
                        sub_lab, ln)
            ln2 = re.sub(r"\((" + _HEX + r")\)", sub_par, ln2)
            if ln2 != ln:
                changes += 1
                ln = ln2
        out.append(ln)
    print("строк изменено: %d" % changes)
    if "--write" in sys.argv:
        open(DOC, "w", encoding="utf-8").write("\n".join(out))
        print("BYTECODE.md перезаписан")
    else:
        # показать первые различия
        for a, b in zip(lines, out):
            if a != b:
                print("  - %s" % a[:100])
                print("  + %s" % b[:100])


main()
