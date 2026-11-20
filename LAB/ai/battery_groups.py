"""battery_groups.py — прогон батареи группами секций (LAB/ai; песочница
ограничивает вызов 10 минутами — как сессии 48/49: 1-11 / 12 / 13-17).

Запуск: python3 LAB/ai/battery_groups.py <1|2|3>
  1 — секции 1-11 (целостность/PE/сценарии/оракулы/круги/enc/wall)
  2 — секция 12 (каркас wall.wall: ФИКСПУНКТ ~0.55 млрд шагов)
  3 — секции 13-18 (оракул UNIVM / ядро kernel.exe / ассемблер
      uva.exe / оракул библиотеки L4 / проекты PROJECTS — E8.3 /
      мост BRIDGE v1 — E9.1)
"""
import sys

sys.path.insert(0, "LAB/py")
sys.path.insert(0, "LAB/ai")

import lab_verify as V            # noqa: E402


def main():
    grp = sys.argv[1] if len(sys.argv) > 1 else "1"
    print("=== батарея, группа %s ===" % grp)
    if grp == "1":
        V.t_integrity()
        V.t_pe_invariants()
        V.t_scenarios()
        V.t_oracles()
        V.t_cycles()
        V.t_enc()
        V.lab_t_exe.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_wall.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_wall2.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_wall3.run(V.check, V.kpath, V.kfile, V.kernel_host)
    elif grp == "2":
        V.lab_t_wallself.run(V.check, V.kpath, V.kfile, V.kernel_host)
    elif grp == "3":
        V.lab_t_vm.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_kernel.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_uva.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_l4.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_prj.run(V.check, V.kpath, V.kfile, V.kernel_host)
        V.lab_t_bridge.run(V.check, V.kpath, V.kfile, V.kernel_host)
    else:
        print("группа?") 
        return 2
    n, m = len(V.PASS), len(V.PASS) + len(V.FAIL)
    print("\nИТОГ группы %s: %d/%d %s" % (grp, n, m,
                                          "OK" if n == m else "— ПРОВАЛЫ:"))
    for f in V.FAIL:
        print("  FAIL:", f)
    return 0 if n == m else 1


if __name__ == "__main__":
    sys.exit(main())
