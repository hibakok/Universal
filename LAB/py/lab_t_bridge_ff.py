"""lab_t_bridge_ff.py — секция 18c батареи: FF /4 — косвенный jmp
(E9.4-1; SPEC/05 «Расширение E9.4»; SPEC/15 п. 3/10).

Вход:  колбэк check из lab_verify + kfile (тело bridge.brick —
       префикс синтетики, как T-E9-21; оракул — ЧИСТЫЙ Python, без
       эмуляции инструментов).
Выход:  проверка T-E9-26 — рост декодера для чужих EXE на стороне
         оракула: (1) якоря декодера FF /4 — r64 (mod11), REX.B r64,
         [rip+disp32] — кортежи == ручным якорям (корпус K);
         (2) спуск: косвенный jmp — ТЕРМИНАЛ без кандидатов — байты
         после него НЕ декодируются (synth5: 41 FF E4 C3 — данные);
         (3) синтетика synth4 ([rip+0] -> слот-таблица: H-строка,
         d-метка от rip-операнда, слот — данные) и synth5 (jmp rax:
         H-строка jmp rax, данные после терминала) — факты/строки/
         PEG == якорям K; (4) круг оракула enc -> brick -> pegen ==
         образу байт-в-байт (H-строки байто-точны всегда).
Функция: «сначала истина семантики» (прецедент E9.1): семантика
         закреплена оракулом ДО порта декодера в инструмент
         bridge.exe (E9.4-2+). На СЕМЕЙСТВЕ расширение нейтрально
         (снимок сессии 75: 12 артефактов — выходы до/после
         совпадают; инструмент == оракулу — T-E9-22/24/25).
         Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                          # noqa: E402
import lab_bridge                         # noqa: E402
import lab_enc                           # noqa: E402
import lab_pegen                          # noqa: E402
import lab_t_bridge_corpus as K           # noqa: E402 — данные E9.4-1


def _decode_ok(bs, want):
    """Один якорь декодера: decode(bs @ 0) == кортежу."""
    def fetch(a, n):
        return int.from_bytes(bs[a:a + n], "little")

    return lab_bridge.lab_x86.decode(fetch, 0) == want


def run(check, kfile):
    """Секция 18c: T-E9-26 — FF /4 (косвенный jmp) в оракуле моста."""
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
    check("T-E9-26 FF /4 (косвенный jmp): декодер+спуск(терминал)+"
          "эмиссия+круг оракула (synth4 [rip]/synth5 r64)", not bad,
          "; ".join(bad[:3]) if bad else
          "3 якоря декодера; 2 образа; круги байт-в-байт")
