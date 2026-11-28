"""lab_t_bridge_round.py — секция 18j батареи: ПЕРВЫЙ ЧУЖОЙ КРУГ
(E9.4-4b-5; DoD этапа E9.4: чужой EXE -> мост (t.b2 + t.peg) ->
pegen.exe(t.b2-тело, t.peg) == образ байт-в-байт) + ГРАНИЦЫ ПРЕДЕЛОВ.

Вход:  колбэк check из lab_verify + kpath (артефакты KERNEL/ под
       эмуляцией lab_run) + корпуса чужих крафтов lab_t_bridge_corpus
       (foreign/foreign2 — E9.4-3a/3b) + большой крафт big_image
       (масштаб реальных EXE: образ 0x30400 — 75% outbuf pegen v2).
Выход: проверки T-E9-33: (1) КРУГ РЕАЛЬНЫМИ ИНСТРУМЕНТАМИ — оба
       чужих крафта корпуса + большой крафт: bridge.exe -> t.b2 +
       t.peg -> enc.exe -> t.brick -> brick.exe -> t.bin -> pegen.exe
       -> t.exe == исходному образу БАЙТ-В-БАЙТ; для большого крафта
       — оракульный круг == образ («сначала истина семантики») и
       выход моста (факт-строка + t.b2 + t.peg) == оракулу;
       (2) ГРАНИЦЫ ПРЕДЕЛОВ ИНСТРУМЕНТОВ (снятие — E9.5): образ
       >= 256 КиБ — bridge.exe ERR=BIG EXE (7, отказ при чтении);
       тело > 128 КиБ (короткий код + нулевой разрыв + данные в
       хвосте — target по п. 7 SPEC/15) — brick.exe ERR=BIG OUT
       (10); отказы БЕЗ частичных выходов. Число проверок: 2.
Функция: интеграция портов E9.4-4b-1..4 (развилка/факты/обе эмиссии
         моста + ветвь v2 pegen) — круг инструментами, как T-E9-23
         для семьи: на пути сборки НИ ОДНОГО оракула; оракул —
         только эталон сравнения.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_bridge                        # noqa: E402
import lab_brick                         # noqa: E402
import lab_enc                           # noqa: E402
import lab_pegen                         # noqa: E402
import lab_run                           # noqa: E402
import lab_t_bridge_corpus as K          # noqa: E402

BIGEXE = b"U-L5-BRIDGE ERR=BIG EXE\r\n"
BIGOUT = b"U-L1-BRICK ERR=BIG OUT\r\n"


def big_image(text_raw=0x8000, rdata_raw=0x28000):
    """Большой чужой образ PE32+ (E9.4-4b-5): масштаб реальных EXE.
    Макет: .text raw 0x8000 (vaddr 0x1000, вход @0x1000) — линейный
    код из mov eax,imm32 xN + add eax,7 + xor eax,eax + ret, конец
    кода в последнем 0x200-окне секции (target = 0x7FFE — БЕЗ
    подъёма вилки п. 7 SPEC/15); .rdata raw 0x28000 — нули + три
    блоба (сворачиваются в 3 патча !sec); импортов нет (DD[1] = 0 —
    класс «импорты-как-данные» E9.4-4b-2). Файл 0x30400 = 193 КиБ —
    75% outbuf pegen v2 (0x40000)."""
    b = bytearray(0x400 + text_raw + rdata_raw)
    b[0:2] = b"MZ"
    struct.pack_into("<I", b, 0x3C, 0x100)             # e_lfanew
    b[0x100:0x104] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", b, 0x104, 0x8664, 2, 0, 0, 0, 0xF0,
                     0x0022)
    struct.pack_into("<H", b, 0x118, 0x020B)            # PE32+
    struct.pack_into("<I", b, 0x128, 0x1000)           # вход (.text)
    struct.pack_into("<Q", b, 0x130, 0x140000000)      # ImageBase
    struct.pack_into("<I", b, 0x138, 0x1000)            # SectionAlign
    struct.pack_into("<I", b, 0x13C, 0x200)            # FileAlignment
    struct.pack_into("<I", b, 0x150, 0x2B000)          # SizeOfImage
    struct.pack_into("<I", b, 0x154, 0x400)            # SizeOfHeaders
    struct.pack_into("<H", b, 0x15C, 3)                # console
    struct.pack_into("<II", b, 0x190, 0x9000, 0)      # импортов нет
    b[0x208:0x210] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", b, 0x210, text_raw, 0x1000, text_raw,
                     0x400)
    struct.pack_into("<I", b, 0x22C, 0x60000020)      # EXEC+READ
    b[0x230:0x238] = b".rdata\x00\x00"
    struct.pack_into("<IIII", b, 0x238, rdata_raw, 0x9000, rdata_raw,
                     0x400 + text_raw)
    struct.pack_into("<I", b, 0x254, 0x40000040)      # DATA+READ
    t = 0x400
    n = (text_raw - 6) // 5
    for i in range(n):
        b[t + 5 * i:t + 5 * i + 5] = bytes(
            [0xB8, i & 0xFF, (i >> 8) & 0xFF, (i >> 16) & 0xFF, 0])
    p = t + 5 * n
    b[p:p + 3] = bytes([0x83, 0xC0, 0x07])            # add eax, 7
    b[p + 3:p + 5] = bytes([0x31, 0xC0])              # xor eax, eax
    b[p + 5:p + 6] = bytes([0xC3])                    # ret
    r = 0x400 + text_raw
    b[r:r + 32] = b"rdata header blob".ljust(32, b"\x00")
    mid = r + rdata_raw // 2
    b[mid:mid + 16] = b"mid rdata blob".ljust(16, b"\x00")
    end = r + rdata_raw - 24
    b[end:end + 24] = b"tail rdata blob".ljust(24, b"\x00")
    return bytes(b)


def longbody_image(text_raw=0x20400):
    """Образ с телом СЕКЦИИ КОДА > 128 КиБ (граница brick): .text
    raw 0x20400 — короткий код в начале (mov/add/xor/ret), нулевой
    разрыв и ненулевые данные в последнем окне: target = 0x20400
    (последний ненулевый байт + 1, п. 7 SPEC/15; выравнивание уже
    совпадает — без подъёма) = 132096 > 131072 — brick обязан
    отказать ERR=BIG OUT."""
    b = bytearray(0x400 + text_raw)
    b[0:2] = b"MZ"
    struct.pack_into("<I", b, 0x3C, 0x100)
    b[0x100:0x104] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", b, 0x104, 0x8664, 1, 0, 0, 0, 0xF0,
                     0x0022)
    struct.pack_into("<H", b, 0x118, 0x020B)
    struct.pack_into("<I", b, 0x128, 0x1000)
    struct.pack_into("<Q", b, 0x130, 0x140000000)
    struct.pack_into("<I", b, 0x138, 0x1000)
    struct.pack_into("<I", b, 0x13C, 0x200)
    struct.pack_into("<I", b, 0x150, 0x22000)
    struct.pack_into("<I", b, 0x154, 0x400)
    struct.pack_into("<H", b, 0x15C, 3)
    struct.pack_into("<II", b, 0x190, 0x40000, 0)      # импортов нет
    b[0x208:0x210] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", b, 0x210, text_raw, 0x1000, text_raw,
                     0x400)
    struct.pack_into("<I", b, 0x22C, 0x60000020)
    t = 0x400
    b[t:t + 5] = bytes([0xB8, 0x0B, 0x00, 0x00, 0x00])   # mov eax,11
    b[t + 5:t + 8] = bytes([0x83, 0xC0, 0x07])           # add eax,7
    b[t + 8:t + 10] = bytes([0x31, 0xC0])               # xor eax,eax
    b[t + 10:t + 11] = bytes([0xC3])                     # ret
    end = 0x400 + text_raw - 16
    b[end:end + 16] = b"tail data blob".ljust(16, b"\x00")
    return bytes(b)


def _chain(bexe, enc_exe, brick_exe, pegen_exe, img):
    """Круг инструментами: bridge -> t.b2/t.peg -> enc -> t.brick ->
    brick -> t.bin -> pegen -> t.exe. Возврат: (ошибки, t.exe,
    результат моста) — мост возвращается для сверки с оракулом
    (БЕЗ повторного прогона)."""
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"], {"in.exe": img})
    if r.exit_code != 0:
        return (["bridge код=%s %r" % (r.exit_code, r.stdout[:40])],
                None, None)
    b2, peg = r.files.get("t.b2", b""), r.files.get("t.peg", b"")
    r1 = lab_run.run_kv(enc_exe, ["t.b2", "t.brick"], {"t.b2": b2})
    if r1.exit_code != 0:
        return ["enc код=%s %r" % (r1.exit_code, r1.stdout[:40])], None, r
    r2 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": r1.files.get("t.brick", b"")})
    if r2.exit_code != 0:
        return ["brick код=%s %r" % (r2.exit_code, r2.stdout[:40])], None, r
    r3 = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                        {"t.bin": r2.files.get("t.bin", b""),
                         "t.peg": peg})
    if r3.exit_code != 0:
        return ["pegen код=%s %r" % (r3.exit_code, r3.stdout[:40])], None, r
    return [], r3.files.get("t.exe"), r


def run(check, kpath):
    """Секция 18j: T-E9-33 — первый чужой круг + границы (E9.4-4b-5)."""
    bexe = kpath("L5-BRIDGE/bridge.exe")
    enc_exe = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # (1) круг инструментами: 2 крафта корпуса + большой крафт;
    # большой крафт за ОДИН прогон: выход моста (факт-строка +
    # t.b2 + t.peg) сверяется с оракулом тут же (без повторного
    # запуска инструмента)
    bad = []
    bigr = None
    for name, img in (("foreign", K.foreign_image()),
                      ("foreign2", K.foreign2_image()),
                      ("big", big_image())):
        errs, made, r = _chain(bexe, enc_exe, brick_exe, pegen_exe, img)
        if name == "big":
            bigr = r
        if errs:
            bad.extend("%s: %s" % (name, e) for e in errs)
        elif made != img:
            bad.append("%s: t.exe != образу (%d/%d Б)"
                       % (name, len(made or b""), len(img)))
    # большой крафт: оракул вперёд + выход моста == оракулу
    img = big_image()
    f = lab_bridge.parse_foreign(img)
    b2t, _st = lab_bridge.emit_b2_foreign(img)
    pegt = lab_bridge.emit_peg_v2(img)
    body = lab_brick.assemble(lab_enc.normalize(b2t).encode("utf-8"))
    if lab_pegen.wrap2(body, pegt) != img:
        bad.append("big: оракульный круг != образу")
    if (bigr is None or bigr.exit_code != 0
            or bigr.stdout != K.foreign_line(img)
            or bigr.files.get("t.b2") != b2t.encode("utf-8")
            or bigr.files.get("t.peg") != pegt.encode("utf-8")):
        bad.append("big: мост != оракулу (код=%s)"
                   % (bigr.exit_code if bigr else "-"))
    check("T-E9-33 ПЕРВЫЙ ЧУЖОЙ КРУГ (DoD этапа E9.4): чужой EXE ->"
          " мост (t.b2 + t.peg) -> enc -> brick -> pegen == образ"
          " байт-в-байт — крафты foreign/foreign2 + большой крафт"
          " 0x30400 Б (тело 0x7FFE — 25% предела brick, образ — 75%"
          " outbuf pegen v2, 3 патча !sec, импортов нет); большой"
          " крафт: оракульный круг + выход моста == оракулу",
          not bad, "; ".join(bad[:3]) if bad else
          "3/3 круга зелёные; big: ins=%d target=%X bss=%X"
          % (len(f["ins"]), f["target"], f["bss"]))

    # (2) границы пределов инструментов (снятие — E9.5)
    bad = []
    img = big_image(rdata_raw=0x38800)          # файл 0x41000 >= 256К
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"], {"in.exe": img})
    if (r.exit_code != 7 or r.stdout != BIGEXE
            or "t.b2" in r.files or "t.peg" in r.files):
        bad.append("BIG EXE: код=%s файлы=%r" % (r.exit_code,
                                                 sorted(r.files)))
    img = longbody_image()                      # тело 0x20400 > 128К
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"], {"in.exe": img})
    if r.exit_code != 0:
        bad.append("longbody: bridge код=%s" % r.exit_code)
    else:
        b2 = r.files.get("t.b2", b"")
        r1 = lab_run.run_kv(enc_exe, ["t.b2", "t.brick"], {"t.b2": b2})
        r2 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                            {"t.brick": r1.files.get("t.brick", b"")})
        if (r1.exit_code != 0 or r2.exit_code != 10
                or r2.stdout != BIGOUT or "t.bin" in r2.files):
            bad.append("BIG OUT: enc=%s brick=%s %r"
                       % (r1.exit_code, r2.exit_code, r2.stdout[:40]))
    check("T-E9-33 ГРАНИЦЫ пределов инструментов (круг внутри"
          " пределов: образ < 256 КиБ, тело <= 128 КиБ; снятие —"
          " E9.5): образ 0x41000 — bridge ERR=BIG EXE (7) без"
          " частичных выходов; тело 0x20400 — brick ERR=BIG OUT"
          " (10) без t.bin", not bad,
          "; ".join(bad[:2]) if bad else "BIG EXE + BIG OUT — как"
          " документировано (SPEC/07, SPEC/08)")
    return not bad


if __name__ == "__main__":
    ok = []

    def check(name, is_ok, note=""):
        ok.append(is_ok)
        print("[%s] %s %s" % ("OK" if is_ok else "FAIL", name, note))

    class KP:
        @staticmethod
        def kpath(rel):
            root = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
            return os.path.join(root, "KERNEL", rel)

    sys.exit(0 if run(check, KP.kpath) and all(ok) else 1)
