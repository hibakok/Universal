"""lab_t_bridge_peg2.py — секция 18g батареи: PEG v2 — ОРАКУЛ-СБОРЩИК
(E9.4-3c-1; SPEC/07 «Рост v2»: чужие образы PE32+ — заголовки/секции/
импорты как ПАТЧИ над нулями + тело секции кода).

Вход:  колбэк check из lab_verify + kfile (артефакты и якоря KERNEL/);
       чистый Python, без эмуляции инструментов.
Выход:  проверка T-E9-30: (1) СБОРКА: якорные тексты PEG v2 (канон
       патчей SPEC/07: H = min raw_ptr; ненулевые пробеги, дырка < 4
       нулей сливается; куски <= 64 Б) для чужих крафтов E9.4-3a/3b
       собираются wrap2 (и диспетчером wrap) в образы БАЙТ-В-БАЙТ —
       тело = target-байты (у foreign2 совпадает с фактом
       parse_foreign: 0x73); (2) ОТКАЗЫ: 19 мутантов якоря + 5
       структурных синтетик (нет MZ/PE, таблица вне H, raw в
       заголовках, наложение raw, !sec на пустой raw) + граница
       версий (v1-текст с !pev2 внутри — v1-отказ); (3) НЕЙТРАЛЬНОСТЬ
       v1: все 12 артефактов семейства собираются диспетчером wrap
       по-прежнему (якорь .b2 -> normalize+assemble -> wrap(.peg)
       == EXE байт-в-байт).
Функция: «сначала истина семантики» (прецедент E9.1/E9.4-3a/3b):
         сборщик чужих обёрток — в оракуле ДО порта в pegen.exe
         (E9.4-4+); эмиссия PEG v2 мостом — срез E9.4-3c-2
         (секция 18h — T-E9-31: emit_peg_v2 == якорям байт-в-байт).
         Число проверок: 1. Якоря выведены инструментом
         scripts/session80_anchors.py (правило «числа — из
         инструментов», решение №3 сессии 77); шапки-комментарии
         сессии 81 приведены к выводимым эмиссией (директивы — те же:
         комментарии wrap2 не читает, сборка якорей не меняется).
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_brick                        # noqa: E402
import lab_bridge                       # noqa: E402
import lab_enc                          # noqa: E402
import lab_pe                           # noqa: E402
import lab_pegen                        # noqa: E402
import lab_t_bridge_corpus as K         # noqa: E402
from lab_t_anchor import ARTIFACTS      # noqa: E402

FOREIGN_PEG2 = """\
; UNIVERSAL / PEG v2 / мост BRIDGE v1 (SPEC/15)
; Исходник: чужой PE32+ (секций 2, DLL 2)
!pev2 400
!hdr 0 4D5A
!hdr 3D 010000466F726569676E20504533322B20696D616765202845392E342D3361292E0D0D0A24
!hdr 100 50450000648602
!hdr 114 F00022000B02
!hdr 128 2010
!hdr 133 8001
!hdr 139 1000000002
!hdr 151 3000000004
!hdr 15C 03
!hdr 191 2000003C
!hdr 1E8 6820000028
!hdr 208 2E74657874
!hdr 211 04000000100000000400000004
!hdr 22C 200000602E726461746100000002000000200000000200000008
!hdr 254 40000040
!body 0
!sec 1 0 4020
!sec 1 C 90200000682000005820
!sec 1 20 A02000008020
!sec 1 40 B020
!sec 1 48 C020
!sec 1 58 D020
!sec 1 68 B020
!sec 1 70 C020
!sec 1 80 D020
!sec 1 90 6B65726E656C33322E646C6C
!sec 1 A0 7573657233322E646C6C
!sec 1 B0 3A024578697450726F63657373000000660247657453746448616E646C6500009A014D657373616765426F7841
"""

FOREIGN2_PEG2 = """\
; UNIVERSAL / PEG v2 / мост BRIDGE v1 (SPEC/15)
; Исходник: чужой PE32+ (секций 2, DLL 2)
!pev2 400
!hdr 0 4D5A
!hdr 3D 010000466F726569676E20504533322B20696D616765202845392E342D3362292E0D0D0A24
!hdr 100 50450000648602
!hdr 114 F00022000B02
!hdr 128 2010
!hdr 133 8001
!hdr 139 1000000002
!hdr 151 3000000004
!hdr 15C 03
!hdr 191 2000003C
!hdr 1E8 6820000028
!hdr 208 2E74657874
!hdr 211 04000000100000000200000004
!hdr 22C 200000602E726461746100000002000000200000000200000006
!hdr 254 40000040
!body 0
!sec 1 0 4020
!sec 1 C 90200000682000005820
!sec 1 20 A02000008020
!sec 1 40 B020
!sec 1 48 C020
!sec 1 58 D020
!sec 1 68 B020
!sec 1 70 C020
!sec 1 80 D020
!sec 1 90 6B65726E656C33322E646C6C
!sec 1 A0 7573657233322E646C6C
!sec 1 B0 3A024578697450726F63657373000000660247657453746448616E646C6500009A014D657373616765426F7841
"""


def _target_body(image):
    """Тело секции кода до target: ненулевой префикс (последний
    ненулевой байт + 1; оба крафта спускаются внутри него)."""
    body = lab_pe.parse(image)["body"]
    nz = max(i for i, b in enumerate(body) if b)
    return body[:nz + 1]


def _synth(nsec_slots=1, nsec_field=None, sig=b"PE\x00\x00",
           raw0=(0x100, 0x10), raw1=None, mz=True, sec1=False):
    """МИНИМАЛЬНЫЙ v2-текст (структурные мутанты): e_lfanew 0x40,
    sizeopt 0, слоты по параметрам; nsec_field — подмена поля COFF
    (мутант «таблица вне H»); sec1 — добавить !sec на секцию 1."""
    n = nsec_slots
    H = 0x40 + 4 + 0x14 + 40 * n
    hdr = bytearray(H)
    if mz:
        hdr[0:2] = b"MZ"
    struct.pack_into("<I", hdr, 0x3C, 0x40)
    hdr[0x40:0x44] = sig
    struct.pack_into("<HHIIIHH", hdr, 0x44, 0x8664,
                     n if nsec_field is None else nsec_field,
                     0, 0, 0, 0, 0x22)
    raws = [raw0] + ([raw1] if raw1 else [])
    for i, (rp, rs) in enumerate(raws[:n]):
        s = 0x58 + 40 * i
        struct.pack_into("<I", hdr, s + 0x10, rs)       # SizeOfRawData
        struct.pack_into("<I", hdr, s + 0x14, rp)       # PointerToRawData
    lines = ["!pev2 %X" % H]
    for c in range(0, H, 64):
        lines.append("!hdr %X %s" % (c, bytes(hdr[c:c + 64]).hex().upper()))
    lines.append("!body 0")
    if sec1:
        lines.append("!sec 1 0 90")
    return "\n".join(lines) + "\n"


def _mutants():
    """Тексты-мутанты якоря FOREIGN2_PEG2 -> (имя, текст | тело)."""
    t = FOREIGN2_PEG2

    def sub(old, new):
        assert old in t, old[:40]
        return t.replace(old, new, 1)

    pev2_line = "!pev2 400\n"
    first_hdr = "!hdr 0 4D5A\n"
    return [
        ("!pev2 не первая директива",
         sub(pev2_line, "").replace(first_hdr,
                                     first_hdr + pev2_line, 1), None),
        ("повтор !pev2", t + "!pev2 400\n", None),
        ("нет !body", sub("!body 0\n", ""), None),
        ("повтор !body", t + "!body 1\n", None),
        ("!body за таблицей секций", sub("!body 0", "!body 2"), None),
        ("тело больше raw секции", t, b"\x90" * 0x201),
        ("!hdr за границами H", t + "!hdr 400 90\n", None),
        ("!hdr наложение патчей", t + "!hdr 0 90\n", None),
        ("блоб нечётной длины", sub("!hdr 0 4D5A", "!hdr 0 4D5"), None),
        ("блоб строчными hex", sub("!hdr 0 4D5A", "!hdr 0 4d5a"), None),
        ("блоб длиннее 64 байт", sub("!hdr 0 4D5A",
                                     "!hdr 0 " + "90" * 65), None),
        ("неизвестная директива", t + "!foo 1\n", None),
        ("нет MZ", sub(first_hdr, ""), None),
        ("!sec на секции !body", t + "!sec 0 100 90\n", None),
        ("!sec за границами raw", t + "!sec 1 1FF 9090\n", None),
        ("!sec наложение в секции", t + "!sec 1 90 90\n", None),
        ("!sec за таблицей секций", t + "!sec 5 0 90\n", None),
        ("пустой текст", "", None),
        ("только комментарии", "; пусто\n", None),
    ]


def run(check, kfile):
    """Секция 18g: T-E9-30 — PEG v2, оракул-сборщик (E9.4-3c-1)."""
    bad = []
    # (1) сборка: якорные тексты -> образы байт-в-байт (wrap2 + wrap)
    img1, img2 = K.foreign_image(), K.foreign2_image()
    b1, b2 = _target_body(img1), _target_body(img2)
    for name, img, body, text in [
            ("foreign", img1, b1, FOREIGN_PEG2),
            ("foreign2", img2, b2, FOREIGN2_PEG2)]:
        if lab_pegen.wrap2(body, text) != img:
            bad.append("%s: wrap2 != образу" % name)
        if lab_pegen.wrap(body, text) != img:
            bad.append("%s: диспетчер wrap != образу" % name)
    # тело foreign2 == факту parse_foreign (связь с T-E9-29)
    f2 = lab_bridge.parse_foreign(img2)
    if len(b2) != f2["target"] or \
            f2["body"][:f2["target"]] != b2:
        bad.append("foreign2: тело != target parse_foreign")
    # (2) отказы: 19 мутантов якоря + 5 структурных синтетик + v1-граница
    for name, text, body in _mutants():
        try:
            lab_pegen.wrap2(body if body is not None else b2, text)
            bad.append("нет отказа: %s" % name)
        except ValueError:
            pass
    for name, text in [
            ("нет MZ (синтетика)", _synth(mz=False)),
            ("нет PE-сигнатуры", _synth(sig=b"XX\x00\x00")),
            ("таблица секций вне H", _synth(nsec_field=2)),
            ("raw залезает в заголовки", _synth(raw0=(0x40, 0x10))),
            ("наложение raw областей", _synth(
                nsec_slots=2, raw0=(0x100, 0x10), raw1=(0x104, 0x10)))]:
        try:
            lab_pegen.wrap2(b"\xC3", text)
            bad.append("нет отказа: %s" % name)
        except ValueError:
            pass
    # граница версий: v1-текст с !pev2 ВНУТРИ — v1-отказ (диспетчер)
    v1_with_v2 = "!module x\n!entry 1000\n!idata 1100 28\n" \
                 "!iat 1130 20\n!pev2 400\n"
    try:
        lab_pegen.wrap(b"\x90", v1_with_v2)
        bad.append("нет отказа: v1-текст с !pev2 внутри")
    except ValueError:
        pass
    # (3) нейтральность v1: 12 артефактов — диспетчер ведёт себя как
    # раньше (якорь .b2 -> тело -> wrap(.anchor.peg) == EXE)
    for m in ARTIFACTS:
        b2t = kfile("%s.anchor.b2" % m).decode("utf-8")
        body = lab_brick.assemble(lab_enc.normalize(b2t)
                                  .encode("utf-8"))
        exe = lab_pegen.wrap(body,
                             kfile("%s.anchor.peg" % m)
                             .decode("latin1"))
        if exe != kfile("%s.exe" % m):
            bad.append("%s: v1-нейтральность" % m)
    check("T-E9-30 PEG v2 оракул-сборщик: якорные тексты чужих крафтов "
          "-> образы байт-в-байт (wrap2 + диспетчер; H=400, тела "
          "24/73 Б) + 25 отказов (мутанты/синтетика/v1-граница) + "
          "нейтральность v1 на 12 артефактах (E9.4-3c-1)", not bad,
          "; ".join(bad[:3]) if bad else
          "чужие: 2/2 байт-в-байт; отказы 25/25; семья: 12/12 через "
          "диспетчер")
    return not bad


if __name__ == "__main__":
    ok = []

    def check(name, is_ok, note=""):
        ok.append(is_ok)
        print("[%s] %s %s" % ("OK" if is_ok else "FAIL", name, note))

    class KF:
        @staticmethod
        def kfile(rel):
            return open(os.path.join(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(
                    __file__)))), "KERNEL", rel), "rb").read()

    run(check, KF.kfile)
    sys.exit(0 if all(ok) else 1)
