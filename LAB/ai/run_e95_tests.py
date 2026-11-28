#!/usr/bin/env python3
"""run_e95_tests.py — автономный прогон затронутых секций батареи после
E9.5-1a (сессия 89): T-E6-53 (предел образа pegen 1 МиБ), T-M5-18 (порт
wrap2 + стресс-крафт + пределы v2), T-E9-25 (якоря моста), секция 18j
(первый чужой круг — pegen инструмент конвейера). Полная батарея (246+2)
— CI на GitHub Actions. Частный инструмент (LAB/ai/)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))

import lab_verify as V                    # noqa: E402


def main():
    import lab_t_anchor
    import lab_t_bridge_round
    import lab_t_exe
    import lab_t_pegen2
    lab_t_exe._t_pegen_lim(V.check, V.kpath, V.kfile, V.kernel_host())
    lab_t_pegen2.run(V.check, V.kpath)
    lab_t_anchor.run(V.check, V.kfile)
    lab_t_bridge_round.run(V.check, V.kpath)
    n, m = len(V.PASS), len(V.PASS) + len(V.FAIL)
    print("\nИТОГ: %d/%d %s" % (n, m, "OK" if n == m else "— ПРОВАЛЫ:"))
    for f in V.FAIL:
        print("  FAIL:", f)
    return 0 if n == m else 1


if __name__ == "__main__":
    sys.exit(main())
