"""battery_groups.py — прогон батареи группами секций (LAB/ai; песочница
ограничивает вызов 10 минутами — как сессии 48/49/71/72: 1-11 / 12 /
13-17 / 18 / 18-сборка). С E9.2-3b секция 18 выделена в группу 4; с
E9.2-3c сборка моста выросла (352 -> ~595 млн шагов wall) и секция 18
целиком перестала вмещаться в лимит — T-E9-17 (фикс-пункт сборки)
выделен в группу 5, группа 4 гоняет остальные 23 проверки (с E9.2-4
— T-E9-24) секции 18 на артефакте репозитория bridge.exe
(lab_t_bridge.run(use_repo=True); полный прогон секции — CI /
lab_verify).

Запуск: python3 LAB/ai/battery_groups.py <1|2|3|4|5>
  1 — секции 1-11 (целостность/PE/сценарии/оракулы/круги/enc/wall)
  2 — секция 12 (каркас wall.wall: ФИКСПУНКТ ~0.55 млрд шагов)
  3 — секции 13-17 (оракул UNIVM / ядро kernel.exe / ассемблер
      uva.exe / оракул библиотеки L4 / проекты PROJECTS — E8.3)
  4 — секция 18 БЕЗ сборки (мост BRIDGE v1 — E9.1/E9.2 на артефакте
      репозитория: диффтесты фактов (M=/H=)/CLI/канона и PEG
      T-E9-22/24/23) + секция 18b — якоря (E9.3-1: T-E9-25, чистый
      Python без эмуляции) + секция 18c — FF /4 (E9.4-1: T-E9-26,
      оракул, чистый Python без эмуляции) + секция 18d — таблицы
      переходов (E9.4-2: T-E9-27, оракул, чистый Python без эмуляции)
      + секция 18e — произвольный PE32+ в оракуле (E9.4-3a: T-E9-28,
      lab_pe.parse — e_lfanew/все секции/импорты многих DLL; чистый
      Python без эмуляции) + секция 18f — спуск в чужом теле
      (E9.4-3b: T-E9-29, lab_t_bridge_foreign — parse_foreign:
      исполняемая секция по точке входа + спуск + факты PEG v2
      + согласованность с parse_family; чистый Python без эмуляции)
      + секция 18g — PEG v2 оракул-сборщик (E9.4-3c-1: T-E9-30,
      lab_t_bridge_peg2 — якорные тексты чужих крафтов -> образы
      байт-в-байт + 25 отказов + нейтральность v1 на 12 артефактах;
      чистый Python без эмуляции)
  5 — T-E9-17 (фикс-пункт сборки моста: bridge.wall -> артефакты;
      с E9.2-4 — ~640 млн шагов wall)
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
    elif grp == "4":
        V.lab_t_bridge.run(V.check, V.kpath, V.kfile, V.kernel_host,
                           use_repo=True)
        V.lab_t_anchor.run(V.check, V.kfile)   # секция 18b — E9.3-1
        V.lab_t_bridge_ff.run(V.check, V.kfile)   # 18c — E9.4-1
        V.lab_t_bridge_jt.run(V.check, V.kfile)   # 18d — E9.4-2
        V.lab_t_bridge_pe.run(V.check, V.kfile)   # 18e — E9.4-3a
        V.lab_t_bridge_foreign.run(V.check, V.kfile)   # 18f — 3b
        V.lab_t_bridge_peg2.run(V.check, V.kfile)   # 18g — 3c-1
    elif grp == "5":
        V.lab_t_bridge.run_fixpoint(V.check, V.kpath, V.kfile,
                                   V.kernel_host)
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
