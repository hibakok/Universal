"""wall_ppc_probe.py — матрица воспроизведений дефекта №23 (pp_pcount).

Вход:  ничего (файлы репозитория по стандартным путям).
Выход: таблица сниппетов WALL: оракул lab_l2 против wall.exe (эмуляция)
       — OK/ERR по каждому случаю; расхождения помечены «->».
Функция: диагностический инструмент дефекта №23 (ОТКРЫТ; найден
         сессией 46 в E7.2-2; полное описание и план фикса E7.2-2F —
         KERNEL/L2-WALL/VERIFY.md §4 п. 17). Причина: pp_pcount
         (K2-P01B, wall_self_pp.wall) завершает скан пар [..] только
         на односимвольных токенах глубины 0 — двухсимвольные
         операторы (== != <= >= && || << >>) просматриваются насквозь,
         пары правого операнда засчитываются в цепочку левого
         (k завышено) -> pp_pairs требует вторую «[» -> ложный
         ERR=FORMAT. После фикса ВСЕ строки матрицы обязаны быть OK
         в обоих свидетелях (-> исчезают) — это приёмный критерий
         среза E7.2-2F вместе с якорями в секциях 10/11 батареи.
Запуск: python3 LAB/ai/wall_ppc_probe.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2          # noqa: E402
import lab_run         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
WALL_EXE = os.path.join(ROOT, "KERNEL", "L2-WALL", "wall.exe")


def _case(name, body):
    """Сниппет: глобальные массивы g/h, main с одним условием/выражением."""
    return name, ("var g[4]\nvar h[4]\nfunc main\n  var i\n  var x\n"
                  "  i = 1\n  x = 2\n" + body + "  return 0\nend\n")


# матрица: (имя, тело main) — левый операнд x var / g[i] индекс,
# оператор односимвольный/двухсимвольный, правый операнд var/число/
# индекс/скобки/выражение; отдельно << в выражении и && в условии
CASES = [
    _case("x < g[i] (односимв., левый var)", "  if x < g[i]\n    i = 3\n  end\n"),
    _case("g[i] < h[i] (односимв., оба индекса)", "  if g[i] < h[i]\n    i = 3\n  end\n"),
    _case("x == g[i] (двухсимв., левый var)", "  if x == g[i]\n    i = 3\n  end\n"),
    _case("g[i] == 5 (правое число)", "  if g[i] == 5\n    i = 3\n  end\n"),
    _case("g[i] == x (правый var)", "  if g[i] == x\n    i = 3\n  end\n"),
    _case("g[i] == h[i] (оба индекса)", "  if g[i] == h[i]\n    i = 3\n  end\n"),
    _case("g[i] != h[i]", "  if g[i] != h[i]\n    i = 3\n  end\n"),
    _case("g[i] <= h[i]", "  if g[i] <= h[i]\n    i = 3\n  end\n"),
    _case("g[i] >= h[i]", "  if g[i] >= h[i]\n    i = 3\n  end\n"),
    _case("g[i] == (h[i]) скобки", "  if g[i] == (h[i])\n    i = 3\n  end\n"),
    _case("g[i] == h[i] + 1 (скобка правее)", "  if g[i] == h[i] + 1\n    i = 3\n  end\n"),
    _case("g[i] == h[j] && x < 3 (цепочка)", "  if g[i] == h[i] && x < 3\n    i = 3\n  end\n"),
    _case("g[i] == h[i] || x < 3 (дизъюнкт)", "  if g[i] == h[i] || x < 3\n    i = 3\n  end\n"),
    _case("g[i] = g[i] << h[i] (выражение)", "  g[i] = g[i] << h[i]\n"),
    _case("g[i] = g[i] << (h[i]) скобки", "  g[i] = g[i] << (h[i])\n"),
    _case("g[i] = g[i] + h[i] (односимв.)", "  g[i] = g[i] + h[i]\n"),
    _case("g[h[i]] вложенный индекс", "  if g[h[i]] == 5\n    i = 3\n  end\n"),
]


def main():
    bad = 0
    print("=== дефект №23 (pp_pcount): оракул vs wall.exe ===")
    for name, src in CASES:
        try:
            lab_l2.compile_wall(src)
            o = "OK"
        except Exception:                       # noqa: BLE001 — любая = ERR
            o = "ERR"
        r = lab_run.run_kv(WALL_EXE, ["s.wall", "s.b2"],
                           {"s.wall": src.encode()})
        w = "OK" if r.exit_code == 0 else "код%d" % r.exit_code
        diverged = (o == "OK") != (r.exit_code == 0)
        if diverged:
            bad += 1
        print("%s %-42s оракул: %-4s wall: %s"
              % ("->" if diverged else "  ", name, o, w))
    print("=== расхождений: %d из %d (%s) ==="
          % (bad, len(CASES),
             "ДЕФЕКТ ЖИВ — фикс E7.2-2F не применён" if bad
             else "фикс E7.2-2F работает: оба свидетеля сходятся"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
