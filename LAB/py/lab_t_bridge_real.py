"""lab_t_bridge_real.py — секция 18k батареи: РЕАЛЬНЫЙ ПАДДИНГ
raw > vsize (E9.5-3a; SPEC/15 п. 7 «вилка raw>bss» — обобщение
оракула под образы, собранные настоящими компиляторами).

Вход:  колбэк check из lab_verify (инструмент bridge.exe на этом
       срезе НЕ трогается — порт обобщения — следующий срез
       E9.5-3b; здесь истина семантики оракула, прецедент E9.4-3b).
Выход: проверка T-E9-34: крафт realpad_image
       (lab_t_bridge_corpus — .text vsize 0x40 < raw 0x200, хвост —
       ПАДДИНГ 0xCC int3-заливки, как mingw/MSVC; файл = край raw):
         (1) parse_foreign ПРИНИМАЕТ образ (до E9.5-3a — ложный отказ
         «длина тела больше VirtualSize»: nz-подъём target вытаскивал
         НЕ-нулевый паддинг за vsize); факты == якорям REALPAD_*
         (target = raw — вся raw-область — тело; bss = 0: vsize <
         target, виртуальных нулей НЕТ); спуск — 6 инструкций ==
         якорям; границы инструкций — по-прежнему VirtualSize
         (спуск/тени НЕ пересекают vsize — паддинг не декодируется);
         (2) ОРАКУЛЬНЫЙ КРУГ: emit_b2_foreign + emit_peg_v2 ->
         enc.normalize + brick.assemble -> pegen.wrap2 == образу
         БАЙТ-В-БАЙТ (включая паддинг 0xCC — теперь ЧАСТЬ тела);
         (3) НЕЙТРАЛЬНОСТЬ: все 12 артефактов семейства — общие
         ключи parse_family / parse_foreign СОВПАДАЮТ (обобщение
         не задело семейную вилку vsize > raw); крафты foreign /
         foreign2 (E9.4-3a/3b) — факты == прежним якорям
         (FOREIGN2_FACTS: target 73 / bss 38D).
Функция: «сначала истина семантики» (прецедент E9.1/E9.4-3b):
         реальный конфликт образов mingw/MSVC (raw > vsize, паддинг
         НЕ нули) закрыт в ОРАКУЛЕ до порта в bridge.exe (E9.5-3b).
         Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_bridge                         # noqa: E402
import lab_brick                          # noqa: E402
import lab_enc                            # noqa: E402
import lab_pegen                          # noqa: E402
import lab_t_bridge_corpus as K           # noqa: E402 — данные E9.4-3a/3b
from lab_t_bridge_realpad import (REALPAD_FACTS, REALPAD_INS,   # noqa: E402
                                  REALPAD_SECTIONS, realpad_image)

# общие ключи фактов parse_family / parse_foreign (как 18f)
SHARED = ("body", "vsize", "raw", "target", "bss", "entry_off", "ins")
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]


def run(check, kfile):
    """Секция 18k: T-E9-34 — реальный паддинг raw > vsize (E9.5-3a)."""
    bad = []
    img = realpad_image()

    # (1) факты оракула == якорям (приём образа + развилка паддинга)
    f = lab_bridge.parse_foreign(img)
    if any(f[k] != v for k, v in REALPAD_FACTS.items()):
        bad.append("факты %r != якорям %r"
                   % ({k: f[k] for k in REALPAD_FACTS},
                      REALPAD_FACTS))
    ins_got = sorted((a, v[0], v[1]) for a, v in f["ins"].items())
    if ins_got != REALPAD_INS:
        bad.append("спуск %r != якорям %r" % (ins_got, REALPAD_INS))
    if f["pe"]["sections"] != REALPAD_SECTIONS:
        bad.append("секции != якорям")
    if f["target"] != f["raw"] or f["bss"] != 0:
        bad.append("вилка raw>bss: target %X != raw %X / bss %X"
                   % (f["target"], f["raw"], f["bss"]))

    # (2) оракульный круг: b2 + PEG v2 -> enc -> brick -> wrap2 == образ
    b2t, _st = lab_bridge.emit_b2_foreign(img)
    pegt = lab_bridge.emit_peg_v2(img)
    body = lab_brick.assemble(lab_enc.normalize(b2t).encode("utf-8"))
    if lab_pegen.wrap2(body, pegt) != img:
        bad.append("оракульный круг != образу")

    # (3) нейтральность: семья (общие ключи) + прежние чужие крафты
    for a in ARTIFACTS:
        d = kfile(a + ".exe")
        fam = lab_bridge.parse_family(d)
        fore = lab_bridge.parse_foreign(d)
        if any(fam[k] != fore[k] for k in SHARED):
            bad.append("%s: семья/чужой разошлись" % a)
    for name, img2 in (("foreign", K.foreign_image()),
                       ("foreign2", K.foreign2_image())):
        f2 = lab_bridge.parse_foreign(img2)
        if name == "foreign2" and (f2["target"], f2["bss"]) != (0x73,
                                                                0x38D):
            bad.append("foreign2: вилка изменилась (%X/%X)"
                       % (f2["target"], f2["bss"]))
    check("T-E9-34 РЕАЛЬНЫЙ ПАДДИНГ raw > vsize (E9.5-3a: развилка "
          "SPEC/15 п. 7 «вилка raw>bss» — образы mingw/MSVC с хвостом "
          "0xCC): parse_foreign принимает (было — ложный отказ «длина "
          "тела больше VirtualSize»), факты/спуск == якорям (target = "
          "raw — ВСЯ raw-область, bss = 0 — виртуальных нулей нет; "
          "границы инструкций — по VirtualSize), оракульный круг "
          "b2+PEG v2 -> enc -> brick -> wrap2 == образу байт-в-байт "
          "(паддинг 0xCC — часть тела), нейтральность: 12 артефактов "
          "семьи + крафты 3a/3b == прежним якорям",
          not bad, "; ".join(bad[:3]) if bad else
          "круг зелёный: ins=%d target=%X bss=0; семья 12/12; "
          "foreign2 73/38D" % (len(f["ins"]), f["target"]))
    return not bad


if __name__ == "__main__":
    ok = []

    def check(name, is_ok, note=""):
        ok.append(is_ok)
        print("[%s] %s %s" % ("OK" if is_ok else "FAIL", name, note))

    def kfile(rel):
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        return open(os.path.join(root, "KERNEL", rel), "rb").read()

    sys.exit(0 if run(check, kfile) and all(ok) else 1)
