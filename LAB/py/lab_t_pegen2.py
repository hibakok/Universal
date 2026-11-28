"""lab_t_pegen2.py — секция 8d батареи: ПОРТ wrap2 (PEG v2) в pegen.exe
(E9.4-4b-4; SPEC/07 «Рост v2», оракул lab_pegen.wrap2 — E9.4-3c-1)
+ ПОДЪЁМ ПРЕДЕЛОВ ИНСТРУМЕНТА (E9.5-1, сессия 89: outbuf/файл 4 МиБ,
тело 1 МиБ, peg-текст 4 МиБ, спаны 256, записи !sec 16384, сек-данные
1 МиБ; пересборка — LAB/ai/pegen_build_e95.py).

Вход:  колбэк check из lab_verify; артефакт pegen.exe + корпуса крафтов
       lab_t_bridge_peg2 (якорные тексты PEG v2 + мутанты + синтетика).
Выход: проверка T-M5-18: (1) ПОРТ: два чужих крафта (тела target-байтов +
       якорные тексты) — pegen.exe под ЭМУЛЯЦИЕЙ == lab_pegen.wrap2
       байт-в-байт (== исходным чужим образам); (2) ОТКАЗЫ: 19 мутантов
       якоря + 5 структурных синтетик + v1-текст с !pev2 внутри — код 9
       ERR=FORMAT, оракул ValueError; (3) E9.5-1 СТРЕСС: большой
       синтетический крафт (спаны > 64, записи > 128, сек-данные > 8К,
       образ > 256К, текст > 64К) — pegen == wrap2 == образу;
       (4) E9.5-1 ПРЕДЕЛЫ: спаны 257 / peg-текст 0x400000
       — инструментальные отказы (у оракула пределов нет — как T-E6-53,
       без сравнения с оракулом). Число проверок: 4.
Функция: «оракул впереди» (прецедент E9.1): сборщик был закреплён оракулом
         ДО порта; инструмент повторяет его на телах крафтов. Нейтральность
         v1 (9 кругов модулей) — секция 7-8c (lab_t_exe, T-M5-02..06).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_pegen                            # noqa: E402
import lab_run                              # noqa: E402
import lab_t_bridge_corpus as K             # noqa: E402
from lab_t_bridge_peg2 import (             # noqa: E402
    FOREIGN_PEG2, FOREIGN2_PEG2, _mutants, _synth, _target_body)

ERRFMT = b"U-L0-PEGEN ERR=FORMAT\r\n"


# ------------------------------------------------ E9.5-1: стресс + пределы
def _stress():
    """БОЛЬШОЙ синтетический чужой крафт (E9.5-1 — стресс всех подъёмов).

    Образ: H=0x1000 (заголовки: MZ/PE32+/2 секции + острова 8Б/32Б —
    спанов > 64), .text raw 0x20000 (тело — 128 КиБ, старый предел
    imagebuf), .rdata raw 0x24000 (патчи 64Б-через-64Б нулей: 1152
    записи > 128, сек-данные 72К > 8К), файл 0x45000 (образ > 256К —
    старый предел outbuf), текст ~180К (> 64К — старый предел filebuf).
    Возврат: (img, body, text, n_spans, n_secs)."""
    h_size, body_len, rdata_len, period = 0x1000, 0x20000, 0x24000, 128
    hdr = bytearray(h_size)
    hdr[0:2] = b"MZ"
    hdr[0x3C:0x40] = (0x100).to_bytes(4, "little")
    pe = 0x100
    hdr[pe:pe + 4] = b"PE\x00\x00"
    hdr[pe + 4:pe + 6] = (0x8664).to_bytes(2, "little")   # Machine
    hdr[pe + 6:pe + 8] = (2).to_bytes(2, "little")        # NumberOfSections
    hdr[pe + 0x14:pe + 0x16] = (0xF0).to_bytes(2, "little")  # SizeOfOptHdr
    hdr[pe + 0x18:pe + 0x1A] = b"\x0B\x02"                # Magic PE32+
    tbl = pe + 0x18 + 0xF0                                # 0x208
    for i, (nm, vs, rs, rp) in enumerate([
            (b".text", body_len, body_len, 0x1000),
            (b".rdata", rdata_len, rdata_len, 0x1000 + body_len)]):
        a = tbl + 40 * i
        hdr[a:a + 8] = nm.ljust(8, b"\x00")
        hdr[a + 8:a + 12] = vs.to_bytes(4, "little")      # VirtualSize
        hdr[a + 12:a + 16] = (0x1000 * (i + 1)).to_bytes(4, "little")
        hdr[a + 16:a + 20] = rs.to_bytes(4, "little")     # SizeOfRawData
        hdr[a + 20:a + 24] = rp.to_bytes(4, "little")     # PointerToRaw
    for off in range(tbl + 80, h_size, 32):               # острова 8Б/32Б
        for k in range(8):
            hdr[off + k] = (k % 7) + 1
    body = bytes((i % 251) + 1 for i in range(body_len))
    rdata = bytearray(rdata_len)
    for off in range(0, rdata_len, period):              # 64Б-через-64Б
        for k in range(64):
            rdata[off + k] = ((off + k) % 199) + 1
    img = bytes(hdr) + body + bytes(rdata)

    def fold(buf, base):
        """Ненулевые пробеги (дырка >= 1 нуля разделяет) кусками <= 64 Б
        -> [(off, bytes)]; проще канона SPEC/07 (мост сливает дырки < 4
        нулей) — для сборщика это эквивалентно."""
        out, run = [], []
        for i, b in enumerate(buf):
            if b:
                run.append((i, b))
            elif run:
                out.append(run)
                run = []
        if run:
            out.append(run)
        lines = []
        for r in out:
            for k in range(0, len(r), 64):
                chunk = r[k:k + 64]
                lines.append((base + chunk[0][0],
                              bytes(b for _i, b in chunk)))
        return lines

    lines = ["; UNIVERSAL / PEG v2 / стресс пределов E9.5-1", "!pev2 %X"
             % h_size]
    spans = fold(hdr, 0)
    for off, blob in spans:
        lines.append("!hdr %X %s" % (off, blob.hex().upper()))
    lines.append("!body 0")
    secs = fold(rdata, 0)
    for off, blob in secs:
        lines.append("!sec 1 %X %s" % (off, blob.hex().upper()))
    return img, body, "\n".join(lines) + "\n", len(spans), len(secs)


def _limits():
    """Тексты ПРЕДЕЛОВ v2 (E9.5-1; у оракула пределов нет): спаны 257
    (256+1-й — отказ). Граница записей !sec (16384/16385) поведенчески
    НЕ тестируется: попарная проверка наложений O(n^2) — 16385 записей
    ≈ 800 млн шагов эмуляции (нативно — миллисекунды); та же форма
    инструкции (cmp счётчик, предел; jae) покрыта спан-границей, а
    рост предела (> 128) — стресс-крафтом с 1152 записями."""
    return [
        ("спаны 257 (предел 256)", "!pev2 1000\n" + "".join(
            "!hdr %X 41\n" % (0x40 + 4 * i) for i in range(257))),
    ]


def _oracle_rejects(body, text):
    try:
        lab_pegen.wrap2(body, text)
        return False
    except ValueError:
        return True


def run(check, kpath):
    """Секция 8d: T-M5-18 — порт PEG v2 (wrap2) в pegen.exe (E9.4-4b-4)."""
    pegen_exe = kpath("L0-PEGEN/pegen.exe")
    # (1) ПОРТ: чужие крафты -> pegen.exe == wrap2 байт-в-байт
    bad = []
    img1, img2 = K.foreign_image(), K.foreign2_image()
    b1, b2 = _target_body(img1), _target_body(img2)
    for name, img, body, text in [
            ("foreign", img1, b1, FOREIGN_PEG2),
            ("foreign2", img2, b2, FOREIGN2_PEG2)]:
        want = lab_pegen.wrap2(body, text)
        if want != img:
            bad.append("%s: оракул != образу (якорь T-E9-30)" % name)
        r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": text.encode("utf-8")})
        if not (r.exit_code == 0 and r.files.get("t.exe") == want):
            bad.append("%s: pegen != wrap2 (код=%s)" % (name, r.exit_code))
    check("T-M5-18 ПОРТ wrap2: 2 чужих крафта — pegen.exe =="
          " оракулу байт-в-байт (эмуляция)", not bad,
          "; ".join(bad) if bad else "тела foreign/foreign2 как T-E9-30")

    # (2) ОТКАЗЫ: мутанты + синтетика + граница версий
    cases = [(nm, txt, body) for nm, txt, body in _mutants()]
    for nm, txt in [
            ("нет MZ (_synth)", _synth(mz=False)),
            ("нет PE (_synth)", _synth(sig=b"XX\x00\x00")),
            ("таблица вне H", _synth(nsec_field=1, nsec_slots=1)),
            ("raw в заголовках", _synth(raw0=(0x40, 0x10))),
            ("наложение raw", _synth(raw0=(0x100, 0x10),
                                    raw1=(0x108, 0x10), nsec_slots=2)),
            ("!sec на пустой raw", _synth(sec1=True)),
            ("v1-текст с !pev2 внутри", "; v\n!module seed\n!entry 1000\n"
             "!pev2 40\n!idata 1100 28\n!iat 1130 20\n")]:
        cases.append((nm, txt, None))
    bad = []
    for nm, txt, body in cases:
        body = body if body is not None else b"\x90" * 0x40
        r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": txt.encode("utf-8")})
        if not (r.exit_code == 9 and r.stdout == ERRFMT
                and _oracle_rejects(body, txt)):
            bad.append("%s (код=%s, оракул %s)" % (
                nm, r.exit_code, "принял" if not _oracle_rejects(
                    body, txt) else "отказ"))
    check("T-M5-18 ОТКАЗЫ: %d мутантов/синтетик v2 — ERR=FORMAT, оракул"
          " ValueError" % len(cases), not bad,
          "; ".join(bad[:3]) if bad else "все отказы совпали")

    # (3) E9.5-1 СТРЕСС: большой синтетический крафт — все подъёмы разом
    img, body, text, spans, secs = _stress()
    want = lab_pegen.wrap2(body, text)
    r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                       {"t.bin": body, "t.peg": text.encode("utf-8")})
    check("T-M5-18 СТРЕСС E9.5-1: спанов %d (>64), записей %d (>128),"
          " сек-данных %dК (>8К), образ %d (>256К), текст %dК (>64К)"
          " — pegen == оракулу" % (spans, secs, secs * 64 // 1024,
                                   len(img), len(text) // 1024),
          want == img and r.exit_code == 0 and r.files.get("t.exe") ==
          want, "шагов=%d" % r.steps)

    # (4) E9.5-1 ПРЕДЕЛЫ v2: инструментальные отказы (оракул пределов
    #     не имеет — без сравнения, как T-E6-53). Спаны 257 — граница
    #     (256+1-й); записи 16385 — см. _limits() (стоимость O(n^2));
    #     peg-текст ровно 0x400000 — READ PEG (строго меньше).
    bad = []
    for nm, txt in _limits():
        r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": b"\x90" * 0x40,
                            "t.peg": txt.encode("utf-8")})
        if not (r.exit_code == 9 and r.stdout == ERRFMT):
            bad.append("%s (код=%s)" % (nm, r.exit_code))
    txt = ";" + "x" * (0x400000 - 3) + "\r\n"     # ровно 4 МиБ — READ PEG
    r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                       {"t.bin": b"\x90" * 0x40,
                        "t.peg": txt.encode("utf-8")})
    if not (r.exit_code == 8 and
            r.stdout == b"U-L0-PEGEN ERR=READ PEG\r\n"):
        bad.append("peg-текст 0x400000 (код=%s)" % r.exit_code)
    check("T-M5-18 ПРЕДЕЛЫ E9.5-1: спаны 257 / peg-текст 0x400000 —"
          " отказы", not bad,
          "; ".join(bad) if bad else "спаны — FORMAT, текст — READ PEG;"
          " записи 16384/16385 — форма покрыта спан-границей (O(n^2))")
