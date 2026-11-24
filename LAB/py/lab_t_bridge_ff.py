"""lab_t_bridge_ff.py — секция 18c батареи: FF /4 — косвенный jmp
(E9.4-1 — оракул; ПОРТ В ИНСТРУМЕНТ — E9.4-4a; SPEC/05 «Расширение
E9.4»; SPEC/15 п. 3/10).

Вход:  колбэк check из lab_verify + kpath/kfile (тело bridge.brick —
       префикс синтетики, как T-E9-21; с E9.4-4a — ИНСТРУМЕНТ:
       bridge.exe из репозитория под эмуляцией lab_run).
Выход:  проверка T-E9-26 — рост декодера для чужих EXE: (1) якоря
         декодера FF /4 — r64 (mod11), REX.B r64, [rip+disp32] —
         кортежи == ручным якорям (корпус K); (2) спуск: косвенный
         jmp — ТЕРМИНАЛ без кандидатов — байты после него НЕ
         декодируются (synth5: 41 FF E4 C3 — данные); (3) синтетика
         synth4 ([rip+0] -> слот-таблица: H-строка, d-метка от
         rip-операнда, слот — данные) и synth5 (jmp rax: H-строка
         jmp rax, данные после терминала) — факты/строки/PEG ==
         якорям K; (4) круг оракула enc -> brick -> pegen == образу
         байт-в-байт (H-строки байто-точны всегда); (5) ПОРТ
         E9.4-4a — bridge.exe на synth4/synth5: факт-строка
         (INS/TARGET/BSS + M=/H=) + t.b2 + t.peg == оракулу —
         декодер decff (K5-D024), терминал dcls 5, дедупликация
         push_tgt (K5-W005) и H-фолбэк m_bjmp (K5-M011) инструментом.
Функция: «сначала истина семантики» (прецедент E9.1): семантика
         закреплена оракулом (E9.4-1, сессия 75); срез E9.4-4a —
         ПОРТ в инструмент (диффтест инструмент == оракулу —
         «оракул впереди» замкнут). На СЕМЕЙСТВЕ порт нейтрален
         (FF /4 в теле инструментов нет; T-E9-18/22/24/25 на 12
         артефактах — тем же прогоном батареи). Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                          # noqa: E402
import lab_bridge                          # noqa: E402
import lab_enc                           # noqa: E402
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402 — порт E9.4-4a
import lab_t_bridge                        # noqa: E402 — facts_line
import lab_t_bridge_corpus as K           # noqa: E402 — данные E9.4-1


def _decode_ok(bs, want):
    """Один якорь декодера: decode(bs @ 0) == кортежу."""
    def fetch(a, n):
        return int.from_bytes(bs[a:a + n], "little")

    return lab_bridge.lab_x86.decode(fetch, 0) == want


def run(check, kpath, kfile):
    """Секция 18c: T-E9-26 — FF /4 (косвенный jmp): оракул + ПОРТ."""
    bad = []
    # 1) якоря декодера (SPEC/05 «Расширение E9.4»)
    for bs, want in K.FF4_DECODE:
        if not _decode_ok(bs, want):
            bad.append("decode %s" % bs.hex())
    # 2-4) синтетика: спуск/факты/строки/PEG/круг на двух образах
    body = lab_brick.assemble(kfile("L5-BRIDGE/bridge.brick"))
    cases = (("synth4", K.FF4_CRAFT4, K.FF4_FACTS4, K.FF4_LINES4,
              K.FF4_PEG4),
             ("synth5", K.FF4_CRAFT5, K.FF4_FACTS5, K.FF4_LINES5,
              K.FF4_PEG5))
    for name, craft, facts, lines, peg in cases:
        img = lab_pegen.wrap(body[:0x200] + craft, K.FF4_PEG % name)
        try:
            fam = lab_bridge.parse_family(img)
            ins = [(a, fam["ins"][a][0], fam["ins"][a][1])
                   for a in sorted(fam["ins"])]
            if ins != facts["ins"]:
                bad.append("%s: спуск %r" % (name, ins))
            elif fam["ins"][0x205][2] != facts["arg"]:
                bad.append("%s: операнд jmp %r" % (name,
                                                  fam["ins"][0x205][2]))
            if (fam["module"] != facts["module"]
                    or fam["target"] != facts["target"]
                    or fam["bss"] != facts["bss"]
                    or fam["vsize"] != facts["vsize"]
                    or fam["raw"] != facts["raw"]):
                bad.append("%s: факты %s t=%X bss=%X v=%X r=%X"
                           % (name, fam["module"], fam["target"],
                              fam["bss"], fam["vsize"], fam["raw"]))
            b2, _st = lab_bridge.emit_b2(img)
            got = [ln for ln in b2.splitlines()
                   if "@02" in ln or "@03" in ln]
            if got != lines:
                bad.append("%s: строки %r" % (name, got[:2]))
            if lab_bridge.emit_peg(img) != peg:
                bad.append("%s: PEG" % name)
            # круг оракула: H-строки байто-точны (SPEC/15 п. 5)
            bb = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
            if lab_pegen.wrap(bb, lab_bridge.emit_peg(img)) != img:
                bad.append("%s: круг" % name)
        except Exception as e:                    # noqa: BLE001 — любой крах
            bad.append("%s: EXC %r" % (name, e))
    # 5) ПОРТ E9.4-4a: bridge.exe на тех же образах — факты/t.b2/t.peg
    # == оракулу (полный диффтест порта декодера/спуска/эмиссии)
    for name, craft, _f, _l, _p in cases:
        img = lab_pegen.wrap(body[:0x200] + craft, K.FF4_PEG % name)
        try:
            want_b2, _st = lab_bridge.emit_b2(img)
            want_peg = lab_bridge.emit_peg(img)
            want_fact = lab_t_bridge.facts_line(img)
            r = lab_run.run_kv(kpath("L5-BRIDGE/bridge.exe"),
                               ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": img})
            if (r.exit_code != 0
                    or r.stdout != want_fact
                    or r.files.get("t.b2") != want_b2.encode("utf-8")
                    or r.files.get("t.peg") != want_peg.encode("utf-8")):
                bad.append("%s: ПОРТ (код %s, факт %r, b2 %d/%d, peg"
                           " %d/%d)" % (name, r.exit_code, r.stdout[:44],
                                        len(r.files.get("t.b2") or b""),
                                        len(want_b2.encode()),
                                        len(r.files.get("t.peg") or b""),
                                        len(want_peg.encode())))
        except Exception as e:                    # noqa: BLE001 — любой крах
            bad.append("%s: ПОРТ EXC %r" % (name, e))
    check("T-E9-26 FF /4 (косвенный jmp): декодер+спуск(терминал)+"
          "эмиссия+круг оракула + ПОРТ bridge.exe (synth4 [rip]/"
          "synth5 r64)", not bad,
          "; ".join(bad[:3]) if bad else
          "3 якоря декодера; 2 образа; круги байт-в-байт; ПОРТ 2/2"
          " == оракулу (факты+строки+PEG)")
