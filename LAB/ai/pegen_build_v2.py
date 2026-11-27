#!/usr/bin/env python3
"""pegen_build_v2.py — ПОРТ wrap2 (PEG v2, SPEC/07 «Рост v2») в pegen.exe:
срез E9.4-4b-4. Оракул lab_pegen.wrap2 закреплён якорями T-E9-30 (E9.4-3c-1)
ДО порта — «оракул впереди» (прецедент E9.1/E9.4-3a/3b/3c).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL). Что делает:
  (1) NEW: ветвь v2 в теле pegen (сборщик wrap2): кирпичи K0-Q012..Q019
      (развилка версий sniff_v2 / слова v2 / блоб / директивы / цикл строк),
      K0-E005..E007 (самоописание / тело / патчи !sec), K0-G043 (драйвер);
      код ПРИПИСАН в конец файловой части (0xD7A) — существующий код и его
      адреса НЕ сдвигаются.
  (2) PATCH: bss сдвигается на длину нового блока (delta): rip-ссылки
      старого КОДА на bss (цель >= 0xD7A) перетачиваются disp32 += delta
      (обход по декодированию lab_x86 — без ложных срабатываний в данных);
      vdesc (12 RVA ячеек) += delta; call parse_peg @0175 -> call sniff_v2.
  (3) Данные: v2kwtab (4 RVA) + строки «pev2/hdr/body/sec» в файловой части;
      НОВЫЙ bss: 15 ячеек v2 + outbuf 0x40000 + spantab 64*8 + sectab
      128*16 + secdata 0x2000 + rawtab 0x8000; !bss pegen.peg растёт.
  (4) pegen.hex перегенерирован (старые строки с патченными байтами + новые
      @-строки с K-ID); pegen.exe = lab_pegen.wrap(тело, pegen.peg).
Кодировки форм — мини-ассемблер pegen_v2_asm.py (принцип e4_ledger: ручные
кодировки, компоновка лишь разрешает rip-смещения; каждая инструкция
проверяется обратным декодированием lab_x86). Тесты — pegen_v2_probe.py.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_atom                            # noqa: E402
import lab_pegen                            # noqa: E402
import lab_x86                              # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L0-PEGEN")
OLD_FILE = 0xD7A                 # старая файловая длина тела
OLD_VSIZE = 0x3117C              # старый VirtualSize (0xD7A + bss 0x30402)
OUTLIM = 0x40000                # вместимость outbuf (предел инструмента)
SPANMAX = 64                      # предел !hdr-патчей (спан-таблица)
SECMAX = 128                      # предел !sec-записей (таблица)
SECLEN = 0x2000                   # буфер сек-данных (128 x 64 Б)

# существующие символы тела: код НЕ сдвигается; bss — на delta
CODE_SYMS = {"parse_peg": 0x3FF, "read_hexv": 0x4F9, "hex_digit": 0x533,
             "expect_eol": 0x553, "skip_spaces": 0x598,
             "print_error": 0x33E, "create_file_write": 0x271,
             "write_all": 0x2DD, "close_file": 0x2A6,
             "iat_write": 0xC90, "iat_exit": 0xC98}
BSS_OLD = {"filebuf": 0xF6C, "imgsize": 0xF30, "pegsize": 0xF38,
           "imagebuf": 0x10F6C, "fname_out": 0xE80}


def build_v2_code(syms):
    """Список инструкций ветви v2 — вынесен в pegen_v2_code.py (лимит 500)."""
    from pegen_v2_code import build_v2_code as _impl
    return _impl(syms)


# ---------------------------------------------------------------- патчинг
def _disp_off(bs):
    """Смещение disp32/rel32 внутри ОДНОЙ инструкции (форма по байтам):
    любое число REX-префиксов, затем код операции и modrm с rm=101."""
    p = 0
    while p < len(bs) and (bs[p] & 0xF0) == 0x40:
        p += 1
    op = bs[p]
    if op in (0xE8, 0xE9):
        return p + 1
    if op == 0xFF and bs[p + 1] in (0x15, 0x25):
        return p + 2
    MODRM_OPS = set([0x00, 0x01, 0x02, 0x03, 0x08, 0x09, 0x0A, 0x0B,
                     0x10, 0x11, 0x12, 0x13, 0x18, 0x19, 0x1A, 0x1B,
                     0x20, 0x21, 0x22, 0x23, 0x28, 0x29, 0x2A, 0x2B,
                     0x30, 0x31, 0x32, 0x33, 0x38, 0x39, 0x3A, 0x3B,
                     0x80, 0x81, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88,
                     0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E,
                     0xC0, 0xC1, 0xC6, 0xC7, 0xFE, 0xFF])
    if op in MODRM_OPS and (bs[p + 1] & 0xC7) == 0x05:
        return p + 2
    return None


def patch_old_body(old_body, delta, sniff):
    """Перетачивание rip-ссылок старого кода на bss (+delta); вызов
    parse_peg @0175 -> sniff_v2. Возврат: тело с патчами + список сайтов."""
    body = bytearray(old_body)
    fetch = lambda a, n: int.from_bytes(body[a:a + n], "little")
    sites = []
    i = 0
    while i < 0x7AD:                       # только КОД (не данные)
        name, ln, args = lab_x86.decode(fetch, i)
        bs = bytes(body[i:i + ln])
        for arg in args:
            tgt = None
            if not isinstance(arg, tuple) or not arg:
                continue
            if arg[0] == "t":
                tgt = arg[1]
            elif arg[0] == "m" and len(arg) >= 7 and isinstance(
                    arg[6], tuple) and arg[6][0] == "abs":
                tgt = arg[6][1]
            if tgt is None or tgt < OLD_FILE:
                continue
            off = _disp_off(bs)
            assert off is not None, "@%X: форма без disp32 (%s)" % (i, name)
            od = int.from_bytes(bs[off:off + 4], "little", signed=True)
            nd = od + delta
            body[i + off:i + off + 4] = nd.to_bytes(4, "little",
                                                     signed=True)
            sites.append((i + off, nd))
        i += ln
    # вызов parse_peg -> sniff_v2 (развилка версий E9.4-4b-4)
    assert body[0x175] == 0xE8
    rel = sniff - (0x175 + 5)
    body[0x176:0x17A] = rel.to_bytes(4, "little", signed=True)
    sites.append((0x176, rel))
    # vdesc: 6 описателей x {qword перем.1, qword перем.2} — nonzero-поля
    # это RVA ячеек bss (перем.2 == 0 — одно значение), данные, не инструкции
    for a in range(0x7E8, 0x848, 4):
        v = int.from_bytes(body[a:a + 4], "little")
        assert v == 0 or v >= 0x1F40, "vdesc @%X: %X" % (a, v)
        if v:
            body[a:a + 4] = (v + delta).to_bytes(4, "little")
            sites.append((a, v + delta))
    return bytes(body), sites



# ---------------------------------------------------------------- эмиссия
def parse_hex(text):
    """Старый pegen.hex -> [(@смещение, [байты], комментарий|None)] + Z."""
    entries, zlines, head = [], [], []
    for raw in text.split("\n"):
        s = raw.rstrip("\r")
        if not s or s.startswith(";"):
            head.append(s)
            continue
        if s.startswith("Z"):
            zlines.append(s)
            continue
        assert s.startswith("@"), s[:20]
        parts = s.split(";", 1)
        toks = parts[0].split()
        off = int(toks[0][1:], 16)
        bs = [int(t, 16) for t in toks[1:]]
        cm = (";" + parts[1]) if len(parts) == 2 else None
        entries.append((off, bs, cm))
    return head, zlines, entries


def _h(bs):
    return " ".join("%02X" % b for b in bs)


# ---------------------------------------------------------------- эмиссия
def regen_hex(old_hex, sites):
    """Старый hex + байтовые патчи [(абс_офсет, dword)] -> новый текст:
    порядок строк сохранён, патченные @-строки переписаны, комментарий
    вызова parse_peg обновлён (развилка v2)."""
    lines = old_hex.split("\n")
    out = []
    for raw in lines:
        s = raw.rstrip("\r")
        if not s.startswith("@"):
            out.append(s)
            continue
        parts = s.split(";", 1)
        toks = parts[0].split()
        off0 = int(toks[0][1:], 16)
        bs = list(toks[1:])
        cm = parts[1] if len(parts) == 2 else None
        for aoff, nd in sites:
            if off0 <= aoff < off0 + len(bs):
                p = aoff - off0
                bs[p:p + 4] = ["%02X" % b for b in nd.to_bytes(
                    4, "little", signed=True)]
        if cm is not None and "call parse_peg" in cm:
            cm = cm.replace("call parse_peg",
                            "call sniff_v2 (развилка v2 E9.4-4b-4)")
        out.append("%s %s ;%s" % (toks[0], " ".join(bs), cm)
                   if cm is not None else "%s %s" % (toks[0], " ".join(bs)))
    return "\n".join(out)


def build():
    """Собрать новые pegen.hex/pegen.peg/pegen.exe; вернуть статистику."""
    old_hex = open(os.path.join(KERNEL_DIR, "pegen.hex"), "r",
                   encoding="utf-8").read()
    old_body = lab_atom.assemble(old_hex)
    assert len(old_body) == OLD_FILE, hex(len(old_body))

    A = build_v2_code({})                   # проход 1: размеры/метки
    A.emit(OLD_FILE)
    code_len = sum(len(bs) for _a, bs, _c in A.out)

    # данные файловой части: v2kwtab (4 qword RVA) + строки
    strs = [b"pev2\x00", b"hdr\x00", b"body\x00", b"sec\x00"]
    data_base = OLD_FILE + code_len
    kw_rvas = [data_base + 32 + 0x1000, data_base + 37 + 0x1000,
               data_base + 41 + 0x1000, data_base + 46 + 0x1000]
    data_len = 32 + sum(len(s) for s in strs)
    delta = code_len + data_len

    # символы: существующий код (фикс), bss (+delta), новый bss
    cells = OLD_VSIZE + delta
    syms = dict(CODE_SYMS)
    for k, v in BSS_OLD.items():
        syms[k] = v + delta
    syms.update({
        "v2kwtab": data_base, "v2h": cells, "v2nsec": cells + 4,
        "v2tbl": cells + 8, "v2fsz": cells + 12, "v2brp": cells + 16,
        "v2brs": cells + 20, "v2rp": cells + 24, "v2rs": cells + 28,
        "bodyn": cells + 32, "spancnt": cells + 36, "secnt": cells + 40,
        "secdpos": cells + 44, "sawpev2": cells + 48,
        "sawbody": cells + 52, "rawcnt": cells + 56,
        "outbuf": cells + 60, "spantab": cells + 60 + OUTLIM,
        "sectab": cells + 60 + OUTLIM + 0x200,
        "secdata": cells + 60 + OUTLIM + 0xA00,
        "rawtab": cells + 60 + OUTLIM + 0x2A00})
    A2 = build_v2_code(syms)               # проход 2: реальные смещения
    A2.emit(OLD_FILE)
    assert sum(len(bs) for _a, bs, _c in A2.out) == code_len

    new_body, sites = patch_old_body(old_body, delta,
                                     A2.labels["sniff_v2"])
    new_code = b"".join(bs for _a, bs, _c in A2.out)

    # hex: старые строки (с патчами) + новые строки кода и данных
    hex_text = regen_hex(old_hex, sites)
    code_lines = ["@%04X %s ; K0-%s" % (a, _h(bs), c)
                  for a, bs, c in A2.out]
    kwline = "@%04X %s ; K0-D047 v2kwtab: RVA слов (pev2,hdr,body,sec)" % (
        data_base, _h(b"".join((v & 0xFFFFFFFFFFFF).to_bytes(8, "little")
                                for v in kw_rvas)))
    data_lines = [kwline]
    p = data_base + 32
    for n, s in zip(("pev2", "hdr", "body", "sec"), strs):
        data_lines.append("@%04X %s ; K0-D047 kw_%s" % (p, _h(s), n))
        p += len(s)
    hex_text = hex_text + "\n" + "\n".join(code_lines) + "\n" + \
        "\n".join(data_lines) + "\n"

    kwbytes = b"".join((v & 0xFFFFFFFFFFFF).to_bytes(8, "little")
                       for v in kw_rvas)
    body = new_body + new_code + kwbytes + b"".join(strs)
    assert lab_atom.assemble(hex_text) == body, "hexgen != телу"
    peg = open(os.path.join(KERNEL_DIR, "pegen.peg"), "r",
               encoding="latin1").read()
    OLD_BSS = 0x30402
    NEW_BSS = OLD_BSS + (cells + 60 + OUTLIM + 0x2A00 + 0x8000) - \
        (OLD_VSIZE + delta)
    if ("!bss %X" % OLD_BSS) in peg:
        peg = peg.replace("!bss %X" % OLD_BSS, "!bss %X" % NEW_BSS)
    else:
        assert ("!bss %X" % NEW_BSS) in peg, "peg: !bss не найден"
    exe = lab_pegen.wrap(body, peg)
    vsize = int.from_bytes(exe[0x190:0x194], "little")
    assert vsize == len(body) + NEW_BSS, (hex(vsize), hex(len(body)))

    for name, data in [("pegen.hex", hex_text.encode("utf-8")),
                       ("pegen.peg", peg.encode("latin1")),
                       ("pegen.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)
    return dict(code=code_len, data=data_len, delta=delta, body=len(body),
                bss=NEW_BSS, vsize=vsize, exe=len(exe), sites=len(sites))


if __name__ == "__main__":
    s = build()
    print("код %+d Б; данные %d Б; delta %X; тело %d Б; "
          "bss %X; vsize %X; exe %d Б; сайтов патча %d" % (
        s["code"], s["data"], s["delta"], s["body"],
        s["bss"], s["vsize"], s["exe"], s["sites"]))
