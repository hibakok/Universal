"""lab_t_bridge.py — секция 18 батареи: мост BRIDGE v1 (SPEC/15, E9.1).

Вход:  колбэк check из lab_verify (kpath/kfile — единая сигнатура
         секций); артефакты читаются ИЗ РЕПОЗИТОРИЯ напрямую (правка
         EXE без обновления якоря = красный тест).
Выход:  проверки T-E9-01..16 — мост EXE -> BRICK v2 + PEG v1:
         (1) T-E9-01 — факты разбора seed.exe == якорю (поля тела,
             импорты, !bss) + детерминированный отказ чужому образу;
         (2) T-E9-02/03 — ПОЛНЫЕ тексты моста seed (b2 и peg) ==
             ручным якорям lab_bridge_cases.py (сверены с BYTECODE.md);
         (3) T-E9-04..14 — оракульный круг ВСЕХ 11 артефактов
             семейства: enc -> brick -> pegen (оракулы LAB) ==
             исходному EXE байт-в-байт (DoD среза E9.1, SPEC/15 п. 9);
         (4) T-E9-15/16 — сквозной круг РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ
             (эмуляция LAB): enc.exe -> brick.exe -> pegen.exe на
             мосте seed и hxdump — EXE == исходному, коды 0.
Функция: DoD E9.1 — «сначала истина семантики» (прецедент E7.1/E8.1):
         семантика моста закреплена оракулом и якорями ДО инструмента
         bridge.exe (срез E9.2+). Число проверок: 16.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                          # noqa: E402
import lab_bridge                         # noqa: E402
import lab_bridge_cases as C              # noqa: E402
import lab_enc                            # noqa: E402
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402

# все артефакты семейства (KERNEL/*/...exe) — по порядку слоёв
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva"]


def _oracle_circle(check, kfile, m, tid):
    """Оракульный круг одного артефакта: compose(enc,brick,pegen)
    на выходе моста == исходный EXE байт-в-байт (SPEC/15 п. 9)."""
    data = kfile("%s.exe" % m)
    name = m.split("/")[-1]
    try:
        b2, peg = lab_bridge.bridge(data)
        body = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
        exe = lab_pegen.wrap(body, peg)
        _t, st = lab_bridge.emit_b2(data)
        ok = exe == data
        note = ("M=%d H=%d lab=%d %X Б"
                % (st["m"], st["h"], st["lab"], len(body)))
    except Exception as e:                     # noqa: BLE001
        ok, note = False, "EXC:" + repr(e)
    check("%s круг оракула: %s.exe == байт-в-байт" % (tid, name),
          ok, note)


def _tool_circle(check, kpath, kfile, m, tid):
    """Сквозной круг реальными инструментами (эмуляция LAB):
    enc.exe -> brick.exe -> pegen.exe; итог == исходному EXE."""
    data = kfile("%s.exe" % m)
    name = m.split("/")[-1]
    try:
        b2, peg = lab_bridge.bridge(data)
        r1 = lab_run.run_kv(kpath("L1-ENC/enc.exe"),
                            ["t.b2", "t.brick"], {"t.b2": b2.encode()})
        r2 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                            ["t.brick", "t.bin"],
                            {"t.brick": r1.files.get("t.brick", b"")})
        r3 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                            ["t.bin", "t.peg", "t.exe"],
                            {"t.bin": r2.files.get("t.bin", b""),
                             "t.peg": peg.encode()})
        made = r3.files.get("t.exe", b"")
        ok = (r1.exit_code == 0 and r2.exit_code == 0
              and r3.exit_code == 0 and made == data)
        note = ("enc=%d brick=%d pegen=%d шаги=%d+%d+%d"
                % (r1.exit_code, r2.exit_code, r3.exit_code,
                   r1.steps, r2.steps, r3.steps))
    except Exception as e:                     # noqa: BLE001
        ok, note = False, "EXC:" + repr(e)
    check("%s круг инструментами: %s.exe == оригиналу" % (tid, name),
          ok, note)


def run(check, kpath, kfile, kernel_host):
    """Секция 18: T-E9-01..16 — мост BRIDGE v1 (E9.1)."""
    seed = kfile("L0-SEED/seed.exe")

    # T-E9-01: факты разбора == якорю; чужой образ — отказ
    fam = lab_bridge.parse_family(seed)
    f = C.SEED_FACTS
    facts_ok = (fam["module"] == f["module"]
                and fam["entry_off"] == f["entry_off"]
                and fam["vsize"] == f["vsize"] and fam["raw"] == f["raw"]
                and fam["target"] == f["target"] and fam["bss"] == f["bss"]
                and [n for n, _r in fam["pe"]["imports"][0]["funcs"]]
                == f["imports"])
    try:
        lab_bridge.parse_family(b"MZ\x00" * 64)
        reject_ok = False
    except lab_bridge.BridgeError:
        reject_ok = True
    check("T-E9-01 разбор seed.exe == якорю (+отказ чужому)",
          facts_ok and reject_ok,
          "цель=%X bss=%X имп=%d" % (fam["target"], fam["bss"],
                                     len(f["imports"])))

    # T-E9-02/03: полные тексты моста == ручным якорям
    b2, _st = lab_bridge.emit_b2(seed)
    check("T-E9-02 мост seed.exe -> BRICK v2 == якорю",
          b2 == C.SEED_B2, "%d строк" % len(b2.splitlines()))
    peg = lab_bridge.emit_peg(seed)
    check("T-E9-03 мост seed.exe -> PEG v1 == якорю", peg == C.SEED_PEG,
          peg.splitlines()[-1])

    # T-E9-04..14: оракульный круг всех артефактов семейства
    for i, m in enumerate(ARTIFACTS):
        _oracle_circle(check, kfile, m, "T-E9-%02d" % (i + 4))

    # T-E9-15/16: сквозной круг реальными инструментами
    _tool_circle(check, kpath, kfile, "L0-SEED/seed", "T-E9-15")
    _tool_circle(check, kpath, kfile, "L0-HXDUMP/hxdump", "T-E9-16")
