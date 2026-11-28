#!/usr/bin/env python3
"""enc_build_lim4.py — пересборка артефактов M1-ENC после подъёма предела
входа 2 МиБ -> 8 МиБ (E9.5-2; мотив — синхронизация конвейера под тела
1 МиБ: канон b2 чужого тела 1 МиБ ~6 МБ > 2 МиБ — enc отверг бы BIG
SRC и круг bridge -> enc -> brick -> pegen разорвался бы; план —
«Наработки/E9.5», срез E9.5-2).

Частный инструмент ИИ (LAB/ai/; НЕ часть системы UNIVERSAL): читает
разрез KERNEL/L1-ENC/enc.b2 (splice-оракул), нормализует оракулом
lab_enc, раскладывает метки, собирает тело (lab_brick) и EXE
(lab_pegen), записывает enc.brick / enc.peg / enc.exe и прогоняет
dev-тесты эмуляцией: якоря, ошибки, большой исходник, НОВЫЙ предел
(вход 0x200020 принят — старый предел 2 МиБ отверг бы; 0x800000 —
ТОЧНЫЙ КРАЙ — отвергнут ERR=BIG SRC; максимум 0x7FFFFF принят —
dev-only), самохостинг (обратная круговая сборка через НОВЫЙ
brick.exe E9.5-2), регресс корней splice/wall, демо-круг.
Синхронные пределы среза: filebuf 0x200100 -> 0x800100, outbuf
0x440100 -> 0x1100400 (х4; вход x 23/11 + 1 = 0x10BA2EA для 8 МиБ —
запас 0x46116); выход enc <= 0x10BA2EA покрывается входом brick
0x1100000 (E9.5-2) — круг не разрывается ни на одном допустимом
входе enc.
Повторный запуск после изменения enc.b2 воспроизводит артефакты и
печатает новый SHA-256 (обновить: lab_verify.py SHA, README, VERIFY.md).
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # корень репозитория
LAB = os.path.join(ROOT, "LAB", "py")
sys.path.insert(0, LAB)

import lab_brick          # noqa: E402
import lab_enc            # noqa: E402
import lab_enc_cases      # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402
import lab_splice         # noqa: E402

KDIR = os.path.join(ROOT, "KERNEL", "L1-ENC")
BRICK_EXE = os.path.join(ROOT, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN_EXE = os.path.join(ROOT, "KERNEL", "L0-PEGEN", "pegen.exe")

SRC_CAP = 0x800000         # новый предел входа (E9.5-2)
OUT_CAP = 0x1100400        # новый outbuf (х4 от 0x440100; оценка
# вход x 23/11 + 1 = 0x10BA2EA для 8 МиБ — запас 0x46116)


def kernel_host():
    files = {}
    for root, _d, fs in os.walk(os.path.join(ROOT, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(ROOT, "KERNEL")) \
                .replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def layout(brick_text):
    """Раскладка меток/длин по плоскому BRICK v1 (как enc_build_imul)."""
    labels, cur, filelen = {}, 0, None
    for line in brick_text.split("\n"):
        st = line.strip()
        if not st or st.startswith(";"):
            continue
        if st.startswith(":"):
            labels[st[1:].split(";")[0].strip()] = cur
            continue
        toks = st.split()
        d, body = toks[0], []
        for t in toks[1:]:
            if t.startswith(";"):
                break
            body.append(t)
        if d == "H":
            n = 0
            for t in body:
                if t.startswith("$"):
                    n += 1 if t.endswith(":1") else 4
                else:
                    n += 1
            cur += n
        elif d == "DB":
            cur += len(body)
        elif d == "DZ":
            cur += int(body[0], 16)
        elif d == "DBZ":
            if filelen is None:
                filelen = cur
            cur += int(body[0], 16)
        elif d == "DD":
            cur += 4 * len(body)
        elif d == "DQ":
            cur += 8 * len(body)
        else:
            raise ValueError("bad directive: " + st)
    return labels, filelen, cur


def build():
    host = kernel_host()
    flat = lab_splice.splice("l1-enc/enc.b2", host).decode("utf-8")
    assert len(flat.encode("utf-8")) < SRC_CAP, "enc.b2 >= 8 МиБ"
    brick = lab_enc.normalize(flat)
    # сверка ожидаемых строк E9.5-2 (imm32 0x800000 той же длины)
    lines = brick.split("\n")
    assert any(li.startswith(
        "H 41 B8 00 00 80 00 ; K1-G011 вместимость 0x800000")
        for li in lines), "нет mov r8d 0x800000"
    assert any(li.startswith(
        "H 48 81 F8 00 00 80 00 ; K1-G011 предел 8 МиБ")
        for li in lines), "нет cmp rax 0x800000"
    assert "DBZ 800100 ; текст входа (8 МиБ + сентинел, E9.5-2)" in lines
    assert "DBZ 1100400 ; вывод (<= вход x 23/11 + 1; 8 МиБ ->" \
        " 0x10BA2EA — запас 0x46116, E9.5-2)" in lines
    labels, filelen, vsize = layout(brick)
    assert filelen is not None
    assert filelen == 0x2CCE, hex(filelen)   # тело не изменилось
    body = lab_brick.assemble(brick.encode("utf-8"))
    assert len(body) == filelen, (len(body), filelen)
    peg = ("; UNIVERSAL / PEG v1 / слой L1 / модуль M1-ENC\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg>"
           " <out.exe>\n"
           "!module enc\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n" % (labels["idt"] + 0x1000,
                                labels["iat"] + 0x1000, vsize))
    assert vsize == 0x1903606, hex(vsize)   # виртуальный конец (cur) —
    # !bss по прецеденту enc_build_lim3; PE VirtualSize = 0x2CCE + 0x1903606
    # = 0x19062D4 (0x645FD4 + 0x12C0300 — прирост filebuf+outbuf)
    exe = lab_pegen.wrap(body, peg)
    assert len(exe) == 12288               # размер файла не изменился
    with open(os.path.join(KDIR, "enc.brick"), "wb") as f:
        f.write(brick.encode("utf-8"))
    with open(os.path.join(KDIR, "enc.peg"), "wb") as f:
        f.write(peg.encode())
    with open(os.path.join(KDIR, "enc.exe"), "wb") as f:
        f.write(exe)
    print("enc.b2 (flat): %d строк, %d байт" %
          (len(flat.splitlines()), len(flat.encode())))
    print("тело: %d байт (0x%X); !bss=0x%X; idt=0x%X iat=0x%X; exe=%d"
          % (len(body), filelen, vsize, labels["idt"] + 0x1000,
             labels["iat"] + 0x1000, len(exe)))
    print("SHA-256 enc.exe: %s" % hashlib.sha256(exe).hexdigest().upper())
    return brick, exe, host


def run_enc(host, args):
    return lab_run.run_kv(os.path.join(KDIR, "enc.exe"), args, host)


def dev_tests(host):
    ok = fail = 0

    def check(name, cond, note=""):
        nonlocal ok, fail
        ok += bool(cond)
        fail += not bool(cond)
        print("[%s] %s %s" % ("OK " if cond else "FAIL", name, note))

    # 1. справка
    r = run_enc({}, [])
    check("справка", r.stdout == b"U-L1-ENC CMDS: ENC <SRC.B2> <OUT.BRICK>"
           b"\r\n" and r.exit_code == 2,
          "%r код=%s" % (r.stdout[:44], r.exit_code))

    # 2. все якоря одним файлом
    synth = "\n".join(m for m, _ in lab_enc_cases.CASES) + "\n"
    want = lab_enc.normalize(synth).encode()
    r = run_enc({"t.b2": synth.encode()}, ["t.b2", "t.brick"])
    check("якоря (%d) == оракул" % len(lab_enc_cases.CASES),
          r.exit_code == 0 and r.files.get("t.brick") == want,
          "шагов=%d" % r.steps)

    # 3. отвержение — те же номера строк, что у оракула
    bad = []
    for e in lab_enc_cases.ERRORS:
        text = "M ret\nM int3\n" + e + "\n"
        try:
            lab_enc.normalize(text)
            bad.append(e + " (принят оракулом)")
            continue
        except lab_enc.EncError as ex:
            want_out = ("U-L1-ENC ERR=" + str(ex) + "\r\n").encode()
        r = run_enc({"t.b2": text.encode()}, ["t.b2", "t.brick"])
        if not (r.exit_code == 6 and r.stdout == want_out):
            bad.append(e)
    check("отвержение (%d)" % len(lab_enc_cases.ERRORS), not bad,
          "; ".join(bad[:2]))

    # 4. большой исходник (~24 КиБ) == оракулу
    big, _lines = lab_enc_cases.big_source(24000)
    want = lab_enc.normalize(big).encode()
    r = run_enc({"t.b2": big.encode()}, ["t.b2", "t.brick"])
    check("большой исходник (%d КиБ) == оракул" % (len(big) // 1024),
          r.exit_code == 0 and r.files.get("t.brick") == want,
          "строк=%d шагов=%d" % (len(_lines), r.steps))

    # 5. НОВЫЙ ПРЕДЕЛ (E9.5-2): 0x200020 байт одной строкой — принят
    #    (старый предел 2 МиБ E6.4g-5 отверг бы его); выход == вход + LF
    line2m = b";" + b"A" * (0x200020 - 2) + b"\n"
    assert len(line2m) == 0x200020
    r = run_enc({"t.b2": line2m}, ["t.b2", "t.brick"])
    check("предел: вход 0x%X байт принят (старый предел 0x200000)"
          % len(line2m),
          r.exit_code == 0 and r.files.get("t.brick") == line2m,
          "шагов=%d" % r.steps)

    # 6. НОВЫЙ ПРЕДЕЛ: максимум 0x7FFFFF — принят (сентинел в filebuf
    #    0x800100; dev-only — в батарею не включён, дорого ~70 млн шагов)
    line_max = b";" + b"A" * (0x7FFFFF - 2) + b"\n"
    assert len(line_max) == 0x7FFFFF
    r = run_enc({"t.b2": line_max}, ["t.b2", "t.brick"])
    check("предел: максимум 0x7FFFFF принят",
          r.exit_code == 0 and r.files.get("t.brick") == line_max,
          "шагов=%d" % r.steps)

    # 7. НОВЫЙ ПРЕДЕЛ: 0x800000 — ТОЧНЫЙ КРАЙ, отвергнут ERR=BIG SRC
    #    (код 7; O(1))
    line_big = b";" + b"A" * (0x800000 - 2) + b"\n"
    assert len(line_big) == 0x800000
    r = run_enc({"t.b2": line_big}, ["t.b2", "t.brick"])
    check("предел: вход 0x800000 отвергнут (BIG SRC)",
          r.exit_code == 7 and
          r.stdout == b"U-L1-ENC ERR=BIG SRC\r\n",
          "код=%s %r" % (r.exit_code, r.stdout[:30]))

    # 8. самохостинг: splice -> новый enc(splice(enc.b2)) == enc.brick;
    #    круг -> exe (через НОВЫЙ brick.exe E9.5-2 — пределы 1 МиБ/17 МиБ)
    kh = kernel_host()
    flat_enc = lab_splice.splice("l1-enc/enc.b2", kh)
    r1 = run_enc({"e.b2": flat_enc}, ["e.b2", "e.brick"])
    art = open(os.path.join(KDIR, "enc.brick"), "rb").read()
    check("самохостинг: enc(splice(enc.b2)) == enc.brick",
          r1.exit_code == 0 and r1.files.get("e.brick") == art,
          "%d байт, шагов=%d" % (len(art), r1.steps))
    h = dict(kh)
    h["e.brick"] = art
    h["e.peg"] = open(os.path.join(KDIR, "enc.peg"), "rb").read()
    h["brick.exe"] = open(BRICK_EXE, "rb").read()
    h["pegen.exe"] = open(PEGEN_EXE, "rb").read()
    r2 = lab_run.run_kv(BRICK_EXE, ["e.brick", "e.bin"], h)
    h["e.bin"] = r2.files.get("e.bin", b"")
    r3 = lab_run.run_kv(PEGEN_EXE, ["e.bin", "e.peg", "e2.exe"], h)
    exe = open(os.path.join(KDIR, "enc.exe"), "rb").read()
    check("самохостинг: круг -> enc.exe",
          r2.exit_code == 0 and r3.exit_code == 0 and
          r3.files.get("e2.exe") == exe,
          "шагов=%d+%d" % (r2.steps, r3.steps))

    # 9. регресс: корни репозитория == старым .brick (wall.b2 —
    #    ГЕНЕРИРУЕМЫЙ плоский артефакт ~1 МБ, с E6.4d-5/3-2 выше предела
    #    splice — подаётся НАПРЯМУЮ; заодно доказывает: 1 МБ b2-текст
    #    переваривается новым enc — класс тел 1 МиБ из плана E9.5-2)
    bad = []
    for src_name, art_path in [
            ("l1-splice/splice.b2", "KERNEL/L1-SPLICE/splice.brick"),
            ("l2-wall/wall.b2", "KERNEL/L2-WALL/wall.brick")]:
        want = open(os.path.join(ROOT, art_path), "rb").read()
        if src_name == "l1-splice/splice.b2":
            data = lab_splice.splice(src_name, kh)
        else:
            data = kh[src_name]
        r = run_enc({"t.b2": data}, ["t.b2", "t.brick"])
        if not (r.exit_code == 0 and r.files.get("t.brick") == want):
            bad.append(src_name)
    check("регресс: splice.b2 (разрез) + wall.b2 (1 МБ, плоско)"
          " == старым .brick", not bad, "; ".join(bad))

    # 10. демо-круг настоящими инструментами -> U-ENC-OK
    h2 = {"d.b2": lab_enc_cases.DEMO_B2.encode(),
          "d.peg": lab_enc_cases.DEMO_PEG.encode(),
          "brick.exe": h["brick.exe"], "pegen.exe": h["pegen.exe"]}
    r1 = run_enc(h2, ["d.b2", "d.brick"])
    h2["d.brick"] = r1.files.get("d.brick", b"")
    r2 = lab_run.run_kv(BRICK_EXE, ["d.brick", "d.bin"], h2)
    h2["d.bin"] = r2.files.get("d.bin", b"")
    r3 = lab_run.run_kv(PEGEN_EXE, ["d.bin", "d.peg", "d.exe"], h2)
    demo = os.path.join(KDIR, "_demo_tmp.exe")
    with open(demo, "wb") as f:
        f.write(r3.files.get("d.exe", b""))
    r4 = lab_run.run_kv(demo, [], {})
    os.unlink(demo)
    check("демо-круг enc+brick+pegen -> U-ENC-OK",
          r1.exit_code == 0 and r2.exit_code == 0 and r3.exit_code == 0 and
          r4.stdout == b"U-ENC-OK\r\n" and r4.exit_code == 0,
          "%r шагов=%d" % (r4.stdout[:20], r4.steps))

    print("\nИТОГ dev: %d OK, %d FAIL" % (ok, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    _brick, _exe, _host = build()
    sys.exit(dev_tests(_host))
