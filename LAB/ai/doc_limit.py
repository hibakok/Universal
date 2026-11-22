"""doc_limit.py — контроль лимита строк методологии R2 (LAB/ai).

Вход:  корень репозитория (текущая папка).
Выход: отчёт [OK]/[FAIL]: все .md (кроме растущего журнала
       LAB/ai/JOURNAL.md) и все .py лаборатории — не более 500
       строк; список нарушителей с счётчиками; код возврата 0/1.
Функция: постоянный санитарный контроль правила «файл — не более
         500 строк» (DOCS/01 п. 7 «деградация структуры»; создан
         сессией 77 при чистке долгов лимита). Данные-артефакты
         (.b2/.brick/.hex/.peg/.wall/.uva/.exe/.anchor.*) лимитом
         не обложены: правило методологии — о документах и коде.
Запуск: python3 LAB/ai/doc_limit.py  (из корня репозитория)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIMIT = 500
# журнал сессий растёт appending-only; разрезы истории — 03-серии;
# trace_m.py — ЗАМОРОЖЕННЫЙ свидетель-транслитерация 1:1 плана WALL
# (E9.2-3c, сессия 72): размер зеркален bridge_self_m*.wall, разрез
# исказил бы свидетельство (правка = только при перезапуске следствия)
EXEMPT = {"LAB/ai/JOURNAL.md", "LAB/ai/trace_m.py"}


def collect():
    md, py = [], []
    for root, _dirs, fs in os.walk(ROOT):
        if os.path.sep + ".git" + os.path.sep in root + os.path.sep:
            continue
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
            if rel.startswith(".git"):
                continue
            if f.endswith(".md"):
                if rel not in EXEMPT:
                    md.append(rel)
            elif f.endswith(".py"):
                if rel.startswith("LAB/") and rel not in EXEMPT:
                    py.append(rel)
    return sorted(md), sorted(py)


def count_lines(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def main():
    md, py = collect()
    bad = []
    checked = 0
    for rel in md + py:
        n = count_lines(os.path.join(ROOT, rel))
        checked += 1
        if n > LIMIT:
            bad.append((rel, n))
    print("проверено файлов: %d (.md %d + LAB .py %d); лимит %d строк"
           % (checked, len(md), len(py), LIMIT))
    if bad:
        for rel, n in bad:
            print("[FAIL] %s — %d строк (превышение на %d)"
                  % (rel, n, n - LIMIT))
        print("ИТОГ: %d нарушителей лимита — разрезать по прецедентам"
              " (03-серии, corpus, INDEX-LAB)" % len(bad))
        return 1
    print("[OK] лимит методологии R2 соблюдён во всех файлах")
    return 0


if __name__ == "__main__":
    sys.exit(main())
