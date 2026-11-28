"""run_e95_1b_tests.py — прогон затронутых секций батареи для E9.5-1b
(прецедент run_e95_tests.py сессии 89): целостность (SHA + PE),
секция 18/18b..18i (мост: якоря, корпус, мутанты, FF/jt/PE/чужие
крафты, PEG v2, b2 чужого тела) + секция 8d (pegen v2). Группа 5
(фикс-пункт T-E9-17 — пересборка моста) и полная батарея — CI.
"""
import os
import sys

ROOT = "/home/z/my-project/Universal"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))

import lab_verify as V                     # noqa: E402

V.t_integrity()
V.t_pe_invariants()
V.lab_t_bridge.run(V.check, V.kpath, V.kfile, V.kernel_host)
V.lab_t_anchor.run(V.check, V.kfile)
V.lab_t_bridge_ff.run(V.check, V.kpath, V.kfile)
V.lab_t_bridge_jt.run(V.check, V.kpath, V.kfile)
V.lab_t_bridge_pe.run(V.check, V.kfile)
V.lab_t_bridge_foreign.run(V.check, V.kpath, V.kfile)
V.lab_t_bridge_peg2.run(V.check, V.kfile)
V.lab_t_bridge_peg2e.run(V.check, V.kfile)
V.lab_t_bridge_b2f.run(V.check, V.kfile)
V.lab_t_pegen2.run(V.check, V.kpath)

n, m = len(V.PASS), len(V.PASS) + len(V.FAIL)
print("\nИТОГ затронутых секций: %d/%d %s" % (n, m, "OK" if n == m else
                                              "— ЕСТЬ ПРОВАЛЫ:"))
for f in V.FAIL:
    print("  FAIL:", f)
sys.exit(0 if n == m else 1)
