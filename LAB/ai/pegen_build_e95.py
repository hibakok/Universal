#!/usr/bin/env python3
"""pegen_build_e95.py — E9.5-1a: ПОДЪЁМ ПРЕДЕЛОВ pegen.exe под реальные
чужие EXE (срез E9.5-1, часть A — pegen; часть B — bridge.exe — следующая
сессия; тело brick — E9.5-2; реальный образец — E9.5-3).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL). Что делает:

(1) ПРЕДЕЛЫ v1 (инструкции диспетчера G041, 4 слова-иммедиата):
    imagebuf 0x20000 -> 0x100000 (тело <= 1 МиБ — синхронно плану E9.5-2
    подъёма тела brick; было 128 КиБ с E6.4g-3);
    filebuf   0x10000 -> 0x400000 (peg-текст < 4 МиБ — текст PEG v2
    реальных EXE мегабайтный; было 64 КиБ с E4).
(2) ПРЕДЕЛЫ v2 (константы листинга pegen_v2_code.py — истина ветви):
    outbuf 0x40000 -> 0x400000 (образ/файл/H <= 4 МиБ);
    спаны 64 -> 256 (spantab 0x200 -> 0x800);
    записи !sec 128 -> 16384 (sectab 0x800 -> 0x40000);
    сек-данные 0x2000 -> 0x100000 (= 16384 x 64 Б);
    rawtab 4096 записей — БЕЗ ИЗМЕНЕНИЙ (реальные EXE < 100 секций).
(3) ВЕТВЬ v2 ПЕРЕИЗЛУЧЕНА из листинга: SPANMAX=256 не влезает в imm8
    (было cmp rcx,64 — 4 Б) — форма растёт до imm32 (7 Б), адреса меток
    v2 сдвигаются; мини-ассемблер pegen_v2_asm пересчитывает всё сам
    (два прохода, round-trip контроль каждой инструкции).
(4) bss ВЫРОС (filebuf +0x3F0000, imagebuf +0xE0000, буферы v2) —
    rip-ссылки v1-кода на imagebuf/zeropad переточены декодер-обходом
    lab_x86 (прецедент pegen_build_v2.py, сессия 87): ячейки v1/filebuf
    сдвигаются на дельту тела (+3), imagebuf — ещё на рост filebuf,
    zeropad — ещё и на рост imagebuf; vdesc — дельта ячеек.
(5) pegen.peg: !bss 0x7AE3E -> 0xA48C41; pegen.exe = wrap(тело, peg)
    (размер файла НЕ меняется — 0x1800: рост уходит в виртуальные нули).

Тесты — dev_tests(): круг E4 самосборки, регресс 9 модулей, границы
образа/peg-текста, 2 чужих крафта v2 == wrap2, БОЛЬШОЙ стресс-крафт
(спаны > 64, записи > 128, сек-данные > 8К, образ > 256К, текст > 64К),
пределы v2 (спаны 257 / записи 16385 / peg 4 МиБ — отказы).
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_atom                            # noqa: E402
import lab_pegen                           # noqa: E402
import lab_x86                             # noqa: E402

KERNEL_DIR = os.path.join(ROOT, "KERNEL", "L0-PEGEN")
OLD_BODY = 0x1544                # текущая файловая длина тела (v1+v2)
OLD_DELTA = 0x7CA                # текущий сдвиг bss (порт v2, сессия 87)
V1_FILE = 0xD7A                  # длина v1-части (не меняется)
OLD_BSS = 0x7AE3E

# ---- новые пределы (v2 — из листинга; v1 — здесь) --------------------
from pegen_v2_code import (                 # noqa: E402
    OUTLIM, SPANMAX, SECMAX, SECLEN)
NEW_FILECAP = 0x400000           # filebuf: peg-текст < 4 МиБ (строго)
NEW_IMGCAP = 0x100000            # imagebuf: тело <= 1 МиБ (jbe)
G_FILE = 0x400000 - 0x10000      # рост filebuf
G_IMG = NEW_IMGCAP - 0x20000     # рост imagebuf

# до-портовые (E6.4g-3) телесные адреса v1-символов — ТИРЫ перетачивания
P_IMAGEBUF = 0x10F6C             # imagebuf (тир 2: +G_FILE)
P_ZEROPAD = 0x30F6C              # zeropad  (тир 3: +G_FILE+G_IMG)
P_V2CELLS = 0x3117C              # база ячеек v2 (тир 3)

# код v1 (адреса фиксированы — код не сдвигается)
CODE_SYMS = {"parse_peg": 0x3FF, "read_hexv": 0x4F9, "hex_digit": 0x533,
             "expect_eol": 0x553, "skip_spaces": 0x598,
             "print_error": 0x33E, "create_file_write": 0x271,
             "write_all": 0x2DD, "close_file": 0x2A6,
             "iat_write": 0xC90, "iat_exit": 0xC98}
# до-портовые адреса v1-символов bss (тир 1: +дельта)
BSS_PRE = {"filebuf": 0xF6C, "imgsize": 0xF30, "pegsize": 0xF38,
           "fname_out": 0xE80, "imagebuf": 0x10F6C}

# слова-иммедиаты v1: (адрес imm32, старое, новое, пояснение)
IMM_WORDS = [
    (0x0D6, 0x00020001, NEW_IMGCAP + 1,
     "mov r8d,<cap> (вместимость imagebuf)"),
    (0x0F8, 0x00020000, NEW_IMGCAP,
     "cmp rax,<lim> (предел образа BIG IMAGE)"),
    (0x13B, 0x00010000, NEW_FILECAP,
     "mov r8d,<cap> (вместимость filebuf)"),
    (0x15D, 0x00010000, NEW_FILECAP,
     "cmp rax,<lim> (peg-текст < cap, сентинел)"),
]


def _disp_off(bs):
    """Смещение disp32/rel32 внутри ОДНОЙ инструкции (как pegen_build_v2)."""
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


def _new_target(t):
    """Старая (текущая) цель bss -> новая: дельта тела + рост буферов."""
    p = t - OLD_DELTA                     # до-портовая координата
    if p < P_IMAGEBUF:                    # ячейки v1 / filebuf
        return p + NEW_DELTA
    if p < P_ZEROPAD:                     # imagebuf
        return p + NEW_DELTA + G_FILE
    return p + NEW_DELTA + G_FILE + G_IMG  # zeropad / ячейки v2 / буферы


def build():
    """Собрать новые pegen.hex/pegen.peg/pegen.exe; вернуть статистику."""
    global NEW_DELTA
    old_hex = open(os.path.join(KERNEL_DIR, "pegen.hex"), "r",
                   encoding="utf-8").read()
    old_body = lab_atom.assemble(old_hex)
    assert len(old_body) == OLD_BODY, hex(len(old_body))

    from pegen_v2_code import build_v2_code
    assert (OUTLIM, SPANMAX, SECMAX, SECLEN) == (
        0x400000, 256, 16384, 0x100000), "константы листинга не E9.5-1"

    # --- проход 1: длина нового кода v2 (ширины форм от иммедиатов) ---
    A = build_v2_code({})
    A.emit(V1_FILE)
    code_len = sum(len(bs) for _a, bs, _c in A.out)

    # данные файловой части: v2kwtab (4 qword RVA) + строки
    strs = [b"pev2\x00", b"hdr\x00", b"body\x00", b"sec\x00"]
    data_base = V1_FILE + code_len
    kw_rvas = [data_base + 32 + 0x1000, data_base + 37 + 0x1000,
               data_base + 41 + 0x1000, data_base + 46 + 0x1000]
    data_len = 32 + sum(len(s) for s in strs)
    NEW_DELTA = code_len + data_len

    # --- символы (новые координаты) ---
    cells2 = P_V2CELLS + NEW_DELTA + G_FILE + G_IMG
    syms = dict(CODE_SYMS)
    for k, v in BSS_PRE.items():
        syms[k] = v + NEW_DELTA + (G_FILE if v >= P_IMAGEBUF else 0)
    syms.update({
        "v2kwtab": data_base, "v2h": cells2, "v2nsec": cells2 + 4,
        "v2tbl": cells2 + 8, "v2fsz": cells2 + 12, "v2brp": cells2 + 16,
        "v2brs": cells2 + 20, "v2rp": cells2 + 24, "v2rs": cells2 + 28,
        "bodyn": cells2 + 32, "spancnt": cells2 + 36, "secnt": cells2 + 40,
        "secdpos": cells2 + 44, "sawpev2": cells2 + 48,
        "sawbody": cells2 + 52, "rawcnt": cells2 + 56,
        "outbuf": cells2 + 60, "spantab": cells2 + 60 + OUTLIM,
        "sectab": cells2 + 60 + OUTLIM + SPANMAX * 8,
        "secdata": cells2 + 60 + OUTLIM + SPANMAX * 8 + SECMAX * 16,
        "rawtab": cells2 + 60 + OUTLIM + SPANMAX * 8 + SECMAX * 16 +
        SECLEN})

    # --- проход 2: реальная эмиссия v2 ---
    A2 = build_v2_code(syms)
    A2.emit(V1_FILE)
    assert sum(len(bs) for _a, bs, _c in A2.out) == code_len

    # --- патч v1-части: rip-ссылки на bss + imm-слова + вызов sniff_v2 --
    body = bytearray(old_body[:V1_FILE])
    fetch = lambda a, n: int.from_bytes(body[a:a + n], "little")
    sites = []
    i = 0
    while i < 0x7AD:                       # только КОД v1 (не данные)
        name, ln, args = lab_x86.decode(fetch, i)
        bs = bytes(body[i:i + ln])
        for arg in args:
            tgt = None
            if isinstance(arg, tuple) and arg and arg[0] == "t":
                continue                   # переходы по коду — не трогаем
            if (isinstance(arg, tuple) and len(arg) >= 7 and
                    isinstance(arg[6], tuple) and arg[6][0] == "abs"):
                tgt = arg[6][1]
            if tgt is None or tgt < OLD_BODY:      # bss = хвост тела
                continue
            off = _disp_off(bs)
            assert off is not None, "@%X: форма без disp32 (%s)" % (i, name)
            od = int.from_bytes(bs[off:off + 4], "little", signed=True)
            # дельта цели: конец инструкции НЕ меняется (длины v1 форм
            # стабильны) — disp сдвигается ровно на сдвиг цели (прецедент
            # pegen_build_v2.py; НЕ пересчитывать от конца поля: у форм
            # C7 05 disp32 imm32 за disp идёт иммедиат!)
            nd = od + (_new_target(tgt) - tgt)
            body[i + off:i + off + 4] = nd.to_bytes(4, "little",
                                                     signed=True)
            sites.append((i + off, nd))
        i += ln
    # вызов sniff_v2 @0x175 (развилка v2) — на НОВУЮ метку
    assert body[0x175] == 0xE8
    rel = A2.labels["sniff_v2"] - (0x175 + 5)
    body[0x176:0x17A] = rel.to_bytes(4, "little", signed=True)
    sites.append((0x176, rel))
    # vdesc (12 RVA ячеек bss): дельта ячеек = NEW_DELTA - OLD_DELTA
    for a in range(0x7E8, 0x848, 4):
        v = int.from_bytes(body[a:a + 4], "little")
        assert v == 0 or v >= 0x1F40, "vdesc @%X: %X" % (a, v)
        if v:
            body[a:a + 4] = (v + NEW_DELTA - OLD_DELTA).to_bytes(
                4, "little")
            sites.append((a, v + NEW_DELTA - OLD_DELTA))
    # imm-слова пределов v1
    for off, old, new, _d in IMM_WORDS:
        cur = int.from_bytes(body[off:off + 4], "little")
        assert cur == old, "@%X: %X (ожидалось %X)" % (off, cur, old)
        body[off:off + 4] = new.to_bytes(4, "little")
        sites.append((off, new))

    # --- сборка тела ---
    kwbytes = b"".join((v & 0xFFFFFFFFFFFF).to_bytes(8, "little")
                       for v in kw_rvas)
    new_code = b"".join(bs for _a, bs, _c in A2.out)
    new_body = bytes(body) + new_code + kwbytes + b"".join(strs)

    # --- hex-текст: строки v1 (патч байтов) + новые строки v2 ----------
    hex_text = regen_hex(old_hex, sites, V1_FILE)
    code_lines = ["@%04X %s ; K0-%s" % (a, _h(bs), c) for a, bs, c in
                  A2.out]
    kwline = ("@%04X %s ; K0-D047 v2kwtab: RVA слов (pev2,hdr,body,sec)"
              % (data_base, _h(kwbytes)))
    data_lines = [kwline]
    p = data_base + 32
    for n, s in zip(("pev2", "hdr", "body", "sec"), strs):
        data_lines.append("@%04X %s ; K0-D047 kw_%s" % (p, _h(s), n))
        p += len(s)
    hex_text = hex_text + "\n" + "\n".join(code_lines) + "\n" + \
        "\n".join(data_lines) + "\n"
    assert lab_atom.assemble(hex_text) == new_body, "hexgen != телу"

    # --- pegen.peg: рост bss ---
    peg = open(os.path.join(KERNEL_DIR, "pegen.peg"), "r",
               encoding="latin1").read()
    new_vsize = syms["rawtab"] + 0x8000
    NEW_BSS = new_vsize - len(new_body)
    if ("!bss %X" % OLD_BSS) in peg:
        peg = peg.replace("!bss %X" % OLD_BSS, "!bss %X" % NEW_BSS)
    else:
        assert ("!bss %X" % NEW_BSS) in peg, "peg: !bss не найден"
    exe = lab_pegen.wrap(new_body, peg)
    vsize = int.from_bytes(exe[0x190:0x194], "little")
    assert vsize == len(new_body) + NEW_BSS, (hex(vsize),
                                              hex(len(new_body)))

    for name, data in [("pegen.hex", hex_text.encode("utf-8")),
                       ("pegen.peg", peg.encode("latin1")),
                       ("pegen.exe", exe)]:
        with open(os.path.join(KERNEL_DIR, name), "wb") as f:
            f.write(data)
    return dict(code=code_len, delta=NEW_DELTA, body=len(new_body),
                bss=NEW_BSS, vsize=vsize, exe=len(exe), sites=len(sites),
                cells2=cells2)


def _h(bs):
    return " ".join("%02X" % b for b in bs)


def regen_hex(old_hex, sites, v1_len):
    """Строки v1-части (офсет < v1_len) с байтовыми патчами [(абс, dword)];
    строки v2 выбрасываются (переизлучаются сборщиком). Комментарии
    иммедиатов пределов обновлены."""
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
        if off0 >= v1_len:                 # старая ветвь v2 — прочь
            continue
        bs = list(toks[1:])
        cm = parts[1] if len(parts) == 2 else None
        for aoff, nd in sites:
            if off0 <= aoff < off0 + len(bs):
                p = aoff - off0
                assert p + 4 <= len(bs), "слово @%X через край строки" % aoff
                bs[p:p + 4] = ["%02X" % b for b in nd.to_bytes(
                    4, "little", signed=True)]
        if cm is not None:
            for f, t in (("0x20001 (вместимость, E6.4g-3)",
                          "0x100001 (вместимость, E9.5-1)"),
                         ("0x20000 (предел образа 128 КиБ, E6.4g-3)",
                          "0x100000 (предел образа 1 МиБ, E9.5-1)"),
                         ("mov r8d,0x10000 (вместимость)",
                          "mov r8d,0x400000 (вместимость, E9.5-1)"),
                         ("cmp rax,0x10000 (сентинелу нужен запас)",
                          "cmp rax,0x400000 (сентинелу нужен запас,"
                          " E9.5-1)"),
                         ("call sniff_v2 (развилка v2 E9.4-4b-4)",
                          "call sniff_v2 (развилка v2 E9.4-4b-4;"
                          " переточен E9.5-1)")):
                cm = cm.replace(f, t)
        out.append("%s %s ;%s" % (toks[0], " ".join(bs), cm)
                   if cm is not None else "%s %s" % (toks[0], " ".join(bs)))
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- тесты
def dev_tests():
    """Быстрые проверки нового артефакта (эмуляция)."""
    import lab_brick
    import lab_pe
    import lab_run
    import lab_splice
    from lab_t_bridge_peg2 import FOREIGN_PEG2, FOREIGN2_PEG2, \
        _target_body
    import lab_t_bridge_corpus as K
    import lab_t_pegen2

    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %-70s %s" % ("OK " if cond else "FAIL", name, note))

    PEGEN_EXE = os.path.join(KERNEL_DIR, "pegen.exe")
    HEXGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-HEXGEN", "hexgen.exe")

    # 1. справка
    r = lab_run.run_kv(PEGEN_EXE, [], {})
    check("справка", r.stdout == b"U-L0-PEGEN CMDS: PEGEN <IMAGE.BIN> "
          b"<CTRL.PEG> <OUT.EXE>\r\n" and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:48], r.exit_code))

    # 2. круг E4: hexgen(pegen.hex) == тело; pegen(тело, peg) == exe
    h = {"p.hex": open(os.path.join(KERNEL_DIR, "pegen.hex"), "rb").read(),
         "p.peg": open(os.path.join(KERNEL_DIR, "pegen.peg"), "rb").read()}
    body = lab_atom.assemble(h["p.hex"].decode("utf-8"))
    r2 = lab_run.run_kv(HEXGEN_EXE, ["p.hex", "p.bin"], h)
    check("круг E4: hexgen(pegen.hex) == тело (%d Б)" % len(body),
          r2.exit_code == 0 and r2.files.get("p.bin") == body,
          "шагов=%d" % r2.steps)
    h["p.bin"] = body
    r3 = lab_run.run_kv(PEGEN_EXE, ["p.bin", "p.peg", "p.exe"], h)
    check("круг E4: самосборка pegen (pegen(тело, peg) == pegen.exe)",
          r3.exit_code == 0 and r3.files.get("p.exe") ==
          open(PEGEN_EXE, "rb").read(), "шагов=%d" % r3.steps)

    # 3. регресс: обёртка всех модулей KERNEL == артефактам
    mods = [("L0-SEED/seed", "hex"), ("L0-SEED2/seed2", "hex"),
            ("L0-HXDUMP/hxdump", "hex"), ("L0-HEXGEN/hexgen", "hex"),
            ("L0-PEGEN/pegen", "hex"), ("L1-BRICK/brick", "brick"),
            ("L1-ENC/enc", "brick"), ("L1-SPLICE/splice", "brick"),
            ("L2-WALL/wall", "brick")]
    bad = []
    for m, kind in mods:
        base = os.path.join(ROOT, "KERNEL", m + ".")
        if kind == "hex":
            body_m = lab_atom.assemble(
                open(base + "hex", "rb").read().decode("latin1"))
        elif m == "L1-BRICK/brick":
            kh = {}
            kdir = os.path.join(ROOT, "KERNEL", "L1-BRICK")
            for n in ("brick.brick", "brick_p1.brick", "brick_p2.brick",
                      "brick_p3.brick"):
                kh["l1-brick/" + n] = open(os.path.join(kdir, n),
                                           "rb").read()
            body_m = lab_brick.assemble(
                lab_splice.splice("l1-brick/brick.brick", kh))
        else:
            body_m = lab_brick.assemble(open(base + "brick", "rb").read())
        peg_m = open(base + "peg", "rb").read()
        exe_m = open(base + "exe", "rb").read()
        r = lab_run.run_kv(PEGEN_EXE, ["m.bin", "m.peg", "m.exe"],
                           {"m.bin": body_m, "m.peg": peg_m})
        if not (r.exit_code == 0 and r.files.get("m.exe") == exe_m):
            bad.append(m)
    check("регресс: обёртка 9 модулей KERNEL == артефактам", not bad,
          "; ".join(bad))

    # 4. границы v1: тело 0x100000 принято == wrap / 0x100001 BIG IMAGE
    peg = h["p.peg"]
    peg_s = peg.decode("latin1")
    img = b"\x41" * 0x100000
    want = lab_pegen.wrap(img, peg_s)
    r = lab_run.run_kv(PEGEN_EXE, ["a.bin", "p.peg", "o.exe"],
                       {"a.bin": img, "p.peg": peg})
    check("предел образа: 0x100000 (1 МиБ) принят == оракулу",
          r.exit_code == 0 and r.files.get("o.exe") == want,
          "exe=%d шагов=%d" % (len(want), r.steps))
    img = b"\x43" * 0x100001
    r = lab_run.run_kv(PEGEN_EXE, ["a.bin", "p.peg", "o.exe"],
                       {"a.bin": img, "p.peg": peg})
    check("предел образа: 0x100001 отвергнут (BIG IMAGE)",
          r.exit_code == 6 and
          r.stdout == b"U-L0-PEGEN ERR=BIG IMAGE\r\n",
          "код=%s" % r.exit_code)

    # 5. v2 регресс: 2 чужих крафта == wrap2 (как T-M5-18)
    img1, img2 = K.foreign_image(), K.foreign2_image()
    bad = []
    for name, img, text in [
            ("foreign", img1, FOREIGN_PEG2), ("foreign2", img2,
                                              FOREIGN2_PEG2)]:
        bd = _target_body(img)
        want = lab_pegen.wrap2(bd, text)
        r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": bd, "t.peg": text.encode("utf-8")})
        if not (r.exit_code == 0 and r.files.get("t.exe") == want):
            bad.append("%s (код=%s)" % (name, r.exit_code))
    check("v2 регресс: 2 чужих крафта == wrap2 байт-в-байт", not bad,
          "; ".join(bad))

    # 6. v2 СТРЕСС (генератор — как в T-M5-18) + пределы v2 + peg-текст
    res = lab_t_pegen2._stress()
    img, bd, text, spans, secs = res
    want = lab_pegen.wrap2(bd, text)
    check("стресс-крафт: оракул wrap2 == образу (round-trip)",
          want == img, "спанов=%d (>64), записей=%d (>128)" % (spans,
                                                               secs))
    r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                       {"t.bin": bd, "t.peg": text.encode("utf-8")})
    check("стресс-крафт: pegen.exe == wrap2 (эмуляция)",
          r.exit_code == 0 and r.files.get("t.exe") == want,
          "файл=%d текст=%d шагов=%d" % (len(img), len(text), r.steps))
    lim = lab_t_pegen2._limits()
    bad = []
    for nm, txt in lim:
        r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": b"\x90" * 0x40,
                            "t.peg": txt.encode("utf-8")})
        if not (r.exit_code == 9 and
                r.stdout == b"U-L0-PEGEN ERR=FORMAT\r\n"):
            bad.append("%s (код=%s)" % (nm, r.exit_code))
    txt = ";" + "x" * (0x400000 - 3) + "\r\n"
    r = lab_run.run_kv(PEGEN_EXE, ["t.bin", "t.peg", "t.exe"],
                       {"t.bin": b"\x90" * 0x40,
                        "t.peg": txt.encode("utf-8")})
    if not (r.exit_code == 8 and
            r.stdout == b"U-L0-PEGEN ERR=READ PEG\r\n"):
        bad.append("peg-текст 0x400000 (код=%s)" % r.exit_code)
    check("пределы v2: спаны 257 / записи 16385 / peg 0x400000 — отказы",
          not bad, "; ".join(bad))

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


def main():
    print("=== pegen_build_e95: подъём пределов M0-PEGEN (E9.5-1a) ===")
    stats = build()
    print("код v2 %d Б (было 0x798); delta %X (была %X); тело %d Б"
          " (было %d)" % (stats["code"], stats["delta"], OLD_DELTA,
                          stats["body"], OLD_BODY))
    print("bss %X (была %X); vsize %X; exe %d Б; сайтов патча %d;"
          " ячейки v2 @%X" % (stats["bss"], OLD_BSS, stats["vsize"],
                              stats["exe"], stats["sites"],
                              stats["cells2"]))
    sha = hashlib.sha256(open(os.path.join(KERNEL_DIR, "pegen.exe"),
                              "rb").read()).hexdigest().upper()
    print("SHA-256 pegen.exe: %s" % sha)
    print("\n=== dev-тесты (эмуляция) ===")
    return dev_tests()


if __name__ == "__main__":
    sys.exit(main())
