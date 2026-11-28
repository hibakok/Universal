"""lab_t_exe.py — секции 7-8b батареи: инструменты enc.exe, splice.exe,
brick.exe и pegen.exe.

Вход:  run(check, kpath, kfile, kernel_host) — колбэк и хелперы батареи.
Выход: заполняет PASS/FAIL через check; секции описаны в TESTS/T-L1-ENC.md,
       TESTS/T-L1-SPLICE.md, TESTS/T-L1-BRICK.md и TESTS/T-L0-PEGEN.md.
Функция: T-E6-05..11 (enc == оракулу, самохостинг на разрезе),
         T-E6-12..18 (splice: якоря, отвержение, разрезы репозитория,
         самохостинг собственного include), T-E6-36 (brick: пределы
         1 МиБ / 2048 меток / тело 128 КиБ — E6.4g-1/E6.4g-2) и
         T-E6-53 (pegen: предел образа 128 КиБ — E6.4g-3). Выделено из
         lab_verify.py по лимиту 500 строк (методология LAB).
"""
import os
import tempfile

import lab_brick
import lab_enc
import lab_enc_cases
import lab_pegen
import lab_run
import lab_splice
import lab_splice_cases


# ------------------------------------------------------------------ 7
def _t_enc_exe(check, kpath, kfile, kernel_host):
    """Инструмент enc.exe (E6.2): равенство оракулу и самохостинг."""
    enc = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # T-E6-05: справка без аргументов
    r = lab_run.run_kv(enc, [], {})
    check("T-E6-05 enc справка",
          r.stdout == b"U-L1-ENC CMDS: ENC <SRC.B2> <OUT.BRICK>\r\n" and
          r.exit_code == 2, "%r код=%s" % (r.stdout[:44], r.exit_code))

    # T-E6-06: все якоря одним файлом — байт-в-байт с оракулом
    synth = "\n".join(m for m, _ in lab_enc_cases.CASES) + "\n"
    want = lab_enc.normalize(synth).encode()
    r = lab_run.run_kv(enc, ["t.b2", "t.brick"], {"t.b2": synth.encode()})
    check("T-E6-06 enc == оракул (%d якорей)" % len(lab_enc_cases.CASES),
          r.exit_code == 0 and r.files.get("t.brick") == want,
          "шагов=%d" % r.steps)

    # T-E6-07/T-E6-11: отвержение — та же строка ERR=FORMAT AT=, что у оракула
    bad = []
    for e in lab_enc_cases.ERRORS:
        text = "M ret\nM int3\n" + e + "\n"
        try:
            lab_enc.normalize(text)
            bad.append(e + " (принят оракулом)")
            continue
        except lab_enc.EncError as ex:
            want_out = ("U-L1-ENC ERR=" + str(ex) + "\r\n").encode()
        r = lab_run.run_kv(enc, ["t.b2", "t.brick"],
                           {"t.b2": text.encode()})
        if not (r.exit_code == 6 and r.stdout == want_out):
            bad.append(e)
    check("T-E6-07/11 enc отвержение (%d) с номерами строк"
          % len(lab_enc_cases.ERRORS), not bad, "; ".join(bad[:2]))

    # T-E6-08: круг конвейера на реальных инструментах (DEMO_B2)
    h = {"d.b2": lab_enc_cases.DEMO_B2.encode(),
         "d.peg": lab_enc_cases.DEMO_PEG.encode(),
         "brick.exe": kfile("L1-BRICK/brick.exe"),
         "pegen.exe": kfile("L0-PEGEN/pegen.exe")}
    r1 = lab_run.run_kv(enc, ["d.b2", "d.brick"], h)
    h["d.brick"] = r1.files.get("d.brick", b"")
    r2 = lab_run.run_kv(brick_exe, ["d.brick", "d.bin"], h)
    h["d.bin"] = r2.files.get("d.bin", b"")
    r3 = lab_run.run_kv(pegen_exe, ["d.bin", "d.peg", "d.exe"], h)
    demo = r3.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r4 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check("T-E6-08 круг enc+brick+pegen (U-ENC-OK)",
          r1.exit_code == 0 and r2.exit_code == 0 and r3.exit_code == 0 and
          r4.stdout == b"U-ENC-OK\r\n" and r4.exit_code == 0,
          "шагов=%d+%d+%d" % (r1.steps, r2.steps, r3.steps))

    # T-E6-09: самохостинг — splice+enc(enc.b2) == enc.brick; круг -> enc.exe
    kh = kernel_host()
    r0 = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                        ["l1-enc/enc.b2", "t_flat.b2"], kh)
    h = {"e.b2": r0.files.get("t_flat.b2", b""),
         "e.peg": kfile("L1-ENC/enc.peg"),
         "brick.exe": kfile("L1-BRICK/brick.exe"),
         "pegen.exe": kfile("L0-PEGEN/pegen.exe")}
    r1 = lab_run.run_kv(enc, ["e.b2", "e.brick"], h)
    art = kfile("L1-ENC/enc.brick")
    check("T-E6-09 самохостинг: enc(splice(enc.b2)) == enc.brick",
          r0.exit_code == 0 and r1.exit_code == 0 and
          r1.files.get("e.brick") == art,
          "%d байт, шагов=%d+%d" % (len(art), r0.steps, r1.steps))
    h["e.brick"] = art
    r2 = lab_run.run_kv(brick_exe, ["e.brick", "e.bin"], h)
    h["e.bin"] = r2.files.get("e.bin", b"")
    r3 = lab_run.run_kv(pegen_exe, ["e.bin", "e.peg", "e2.exe"], h)
    check("T-E6-09 самохостинг: круг -> enc.exe",
          r2.exit_code == 0 and r3.exit_code == 0 and
          r3.files.get("e2.exe") == kfile("L1-ENC/enc.exe"),
          "шагов=%d+%d" % (r2.steps, r3.steps))

    # T-E6-10: большой исходник (~24 КиБ смеси форм) == оракулу
    big, lines = lab_enc_cases.big_source(24000)
    want = lab_enc.normalize(big).encode()
    r = lab_run.run_kv(enc, ["t.b2", "t.brick"], {"t.b2": big.encode()})
    check("T-E6-10 большой исходник (%d КиБ) == оракул" % (len(big) // 1024),
          r.exit_code == 0 and r.files.get("t.brick") == want,
          "строк=%d шагов=%d" % (len(lines), r.steps))

    # T-E6-10b: предел входа 8 МиБ (E9.5-2 — синхронно подъёму тела
    # brick до 1 МиБ: канон b2 чужого тела 1 МиБ ~6 МБ не влезал в 2 МиБ
    # и круг bridge -> enc -> brick -> pegen разорвался бы): 0x80020
    # байт одной строкой приняты (регресс семантики jb-края «< предела»),
    # 0x800000 — ТОЧНЫЙ КРАЙ — отвергнут ERR=BIG SRC (код 7; jb->jbe
    # был бы пойман). Точки 0x200020 (старый предел 2 МиБ E6.4g-5
    # отверг бы) и максимум 0x7FFFFF — dev LAB/ai/enc_build_lim4.py
    # (34-134 млн шагов — вне бюджета батареи на каждый пуш); имм32
    # предела дополнительно защищён пином SHA-256 enc.exe (секция 1)
    # и ФОРМ-пином байтов тела ниже; синхронно outbuf 0x1100400
    # (вход x 23/11 + 1 = 0x10BA2EA для 8 МиБ) и filebuf 0x800100.
    line520 = b";" + b"A" * (0x80020 - 2) + b"\n"
    r1 = lab_run.run_kv(enc, ["t.b2", "t.brick"], {"t.b2": line520})
    line8m = b";" + b"A" * (0x800000 - 2) + b"\n"
    r2 = lab_run.run_kv(enc, ["t.b2", "t.brick"], {"t.b2": line8m})
    # ФОРМ-пины imm32 (E9.5-2): вместимость/предел 0x800000 в байтах тела
    enc_body = open(kpath("L1-ENC/enc.exe"), "rb").read()[
        0x200:0x200 + 0x2CCE]
    pins = (b"\x41\xB8\x00\x00\x80\x00" in enc_body and
            b"\x48\x81\xF8\x00\x00\x80\x00" in enc_body)
    check("T-E6-10b предел входа 8 МиБ (520К принят / 8М отвергнут"
          " + imm32-пины)",
          r1.exit_code == 0 and r1.files.get("t.brick") == line520 and
          r2.exit_code == 7 and r2.stdout == b"U-L1-ENC ERR=BIG SRC\r\n" and
          pins,
          "шагов=%d+%d" % (r1.steps, r2.steps))

    # концы строк: пустой вход, без LF, CRLF, одиночный CR (как splitlines)
    bad = []
    for e in [b"", b"M ret", b"M ret\r\nM int3", b"M ret\rM int3", b"\n",
              b"H 48\r\n", b"  M ret  \n", b"M mov rax, 5 ; c\r\n"]:
        try:
            want = lab_enc.normalize(e.decode("latin1")).encode("latin1")
        except lab_enc.EncError as ex:
            want = ("U-L1-ENC ERR=" + str(ex) + "\r\n").encode()
        r = lab_run.run_kv(enc, ["t.b2", "t.brick"], {"t.b2": e})
        if r.files.get("t.brick") != want:
            bad.append(repr(e))
    check("enc концы строк (8 граничных случаев)", not bad,
          "; ".join(bad[:2]))


# ------------------------------------------------------------------ 8
def _t_splice(check, kpath, kfile, kernel_host):
    """Инструмент splice.exe (E6.3): оракул, якоря, разрезы, самохостинг."""
    splice_exe = kpath("L1-SPLICE/splice.exe")
    enc_exe = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # T-E6-12: справка без аргументов
    r = lab_run.run_kv(splice_exe, [], {})
    check("T-E6-12 splice справка",
          r.stdout == b"U-L1-SPLICE CMDS: SPLICE <ROOT.SRC> <OUT.FLAT>\r\n"
          and r.exit_code == 2, "%r код=%s" % (r.stdout[:48], r.exit_code))

    # T-E6-13: оракул == якорям (CASES + ERRORS, чистый Python)
    bad = lab_splice_cases.check_oracle()
    check("T-E6-13 оракул SPLICE == якорям (%d+%d)"
          % (len(lab_splice_cases.CASES), len(lab_splice_cases.ERRORS)),
          not bad, "; ".join(bad[:2]))

    # T-E6-14: инструмент == якорям (нормальные склейки)
    bad, steps = [], 0
    for name, root, host, want in lab_splice_cases.CASES:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = lab_run.run_kv(splice_exe, [root, "t.flat"], host)
        steps += r.steps
        if not (r.exit_code == 0 and r.stdout == b"" and
                r.files.get("t.flat") == want):
            bad.append(name)
    check("T-E6-14 splice == якорям (%d случаев)"
          % len(lab_splice_cases.CASES), not bad,
          "; ".join(bad[:2]) if bad else "шагов=%d" % steps)

    # T-E6-15: отвержение — коды возврата и строки ошибок
    bad = []
    for name, root, host, code, msg in lab_splice_cases.ERRORS:
        host = {k.decode("latin1") if isinstance(k, bytes) else k: v
                for k, v in host.items()}
        r = lab_run.run_kv(splice_exe, [root, "t.flat"], host)
        if not (r.exit_code == code and
                r.stdout == ("U-L1-SPLICE ERR=%s\r\n" % msg).encode()):
            bad.append(name)
    check("T-E6-15 splice отвержение (%d) с кодами и строками"
          % len(lab_splice_cases.ERRORS), not bad, "; ".join(bad[:2]))

    # T-E6-16: большой исходник (~24 КиБ)
    root, host, want = lab_splice_cases.big_case(24000)
    host = {k.decode("latin1") if isinstance(k, bytes) else k: v
            for k, v in host.items()}
    r = lab_run.run_kv(splice_exe, [root, "t.flat"], host)
    check("T-E6-16 большой исходник (%d КиБ)" % (len(want) // 1024),
          r.exit_code == 0 and r.files.get("t.flat") == want,
          "строк=%d шагов=%d" % (want.count(b"\n"), r.steps))

    # T-E6-16b: пределы 256 КиБ (E6.4e-2): корень и включение 0x20020
    # байт приняты (старые FILECAP/OUTCAP 0x20000 отвергли бы; включение
    # проверяет адресацию уровня shl 18 и буфер уровня 1); включение
    # 0x40000 отвергнуто ERR=BIG SRC (код 7)
    line132 = b";" + b"A" * (0x20020 - 2) + b"\n"
    r1 = lab_run.run_kv(splice_exe, ["r.b2", "t.flat"],
                        {"r.b2": line132})
    part132 = b";" + b"B" * (0x20020 - 2) + b"\n"
    r2 = lab_run.run_kv(splice_exe, ["r.b2", "t.flat"],
                        {"r.b2": b"!include p.b2\n", "p.b2": part132})
    r3 = lab_run.run_kv(splice_exe, ["r.b2", "t.flat"],
                        {"r.b2": b"!include big.b2\n",
                         "big.b2": b"C" * 0x40000})
    check("T-E6-16b пределы 256 КиБ (корень+включение 132К приняты /"
          " 256К отвергнут)",
          r1.exit_code == 0 and r1.files.get("t.flat") == line132 and
          r2.exit_code == 0 and r2.files.get("t.flat") == part132 and
          r3.exit_code == 7 and
          r3.stdout == b"U-L1-SPLICE ERR=BIG SRC\r\n",
          "шагов=%d+%d+%d" % (r1.steps, r2.steps, r3.steps))

    # T-E6-17: инструмент == оракулу на корнях репозитория (4 разреза;
    #    с E6.4d-5/3-2 — l2-wall/wall.wall: wall.b2 теперь ГЕНЕРИРУЕМЫЙ
    #    плоский артефакт ~1 МБ (выше предела splice), крупнейший
    #    потребитель пределов — корень каркаса wall.wall, 19 частей)
    kh = kernel_host()
    bad = []
    for root in ("l1-enc/enc.b2", "l1-brick/brick.brick",
                 "l1-splice/splice.b2", "l2-wall/wall.wall"):
        want = lab_splice.splice(root, kh)
        r = lab_run.run_kv(splice_exe, [root, "t.flat"], kh)
        if not (r.exit_code == 0 and r.files.get("t.flat") == want):
            bad.append(root)
    check("T-E6-17 splice == оракулу на корнях репозитория (4)",
          not bad, "; ".join(bad))

    # T-E6-18: самохостинг — splice(splice.b2) -> enc -> brick -> pegen
    r0 = lab_run.run_kv(splice_exe, ["l1-splice/splice.b2", "t_flat.b2"], kh)
    h = {"s.b2": r0.files.get("t_flat.b2", b""),
         "s.peg": kfile("L1-SPLICE/splice.peg"),
         "brick.exe": kfile("L1-BRICK/brick.exe"),
         "pegen.exe": kfile("L0-PEGEN/pegen.exe")}
    r1 = lab_run.run_kv(enc_exe, ["s.b2", "s.brick"], h)
    art = kfile("L1-SPLICE/splice.brick")
    h["s.brick"] = r1.files.get("s.brick", b"")
    r2 = lab_run.run_kv(brick_exe, ["s.brick", "s.bin"], h)
    h["s.bin"] = r2.files.get("s.bin", b"")
    r3 = lab_run.run_kv(pegen_exe, ["s.bin", "s.peg", "s.exe"], h)
    check("T-E6-18 самохостинг splice: круг -> splice.exe",
          r0.exit_code == 0 and r1.exit_code == 0 and
          r1.files.get("s.brick") == art and
          r2.exit_code == 0 and r3.exit_code == 0 and
          r3.files.get("s.exe") == kfile("L1-SPLICE/splice.exe"),
          "шагов=%d+%d+%d+%d" % (r0.steps, r1.steps, r2.steps, r3.steps))


# ------------------------------------------------------------------ 8b
def _t_brick(check, kpath, kfile, kernel_host):
    """Инструмент brick.exe: пределы E6.4g-6/E6.4g-2/E6.4f-2."""
    brick_exe = kpath("L1-BRICK/brick.exe")

    # T-E6-36: пределы 17 МиБ и 131072 меток и тело 1 МиБ (E9.5-2:
    # подъём под реальные чужие EXE — тела .text до 1 МиБ; синхронно
    # pegen E9.5-1a и мосту E9.5-1b: bridge BODY 1 МиБ == brick 1 МиБ
    # == pegen imagebuf 1 МиБ; исходник 17 МиБ покрывает ВЕСЬ допустимый
    # выход enc — вход enc < 8 МиБ => выход <= 23/11 x 8 МиБ + 1 =
    # 0x10BA2EA < 0x1100000): исходник 0x80020 байт одной
    # строкой-комментарием принят (регресс семантики jb-края); 1025 меток
    # приняты; исходник 0x1100000 — ТОЧНЫЙ КРАЙ нового предела — отвергнут
    # ERR=BIG SRC (код 7; точки 0x200020/0x1100000-1 — dev-only в
    # LAB/ai/brick_build_lim5.py: 29-34 млн шагов вне бюджета пуша;
    # константные imm32 дополнительно защищены пином SHA секции 1
    # и ФОРМ-пином байтов ниже)
    line512 = b";" + b"A" * (0x80020 - 2) + b"\n"
    r1 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": line512})
    src1025 = b"".join((b":k%d\n" % i) + b"H 90\n" for i in range(1025))
    want1025 = lab_brick.assemble(src1025)
    r2 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": src1025})
    line17m = b";" + b"A" * (0x1100000 - 2) + b"\n"
    r3 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": line17m})
    # E9.5-2: предел ТЕЛА 128 КиБ -> 1 МиБ (jbe — принят и ровно 0x100000,
    # синхронно pegen E6.4g-3 и мосту BIG BODY E9.5-1b): 0x100000 —
    # jbe-край — принят; 0x100001 отвергнут ERR=BIG OUT (код 10).
    # Регресс прежних точек: 0x10000 и 0x1FFFF (приняты с E6.4g-2)
    src64 = b"DZ 10000\n"
    want64 = lab_brick.assemble(src64)
    r4 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": src64})
    src127 = b"DZ 1FFFF\n"
    want127 = lab_brick.assemble(src127)
    r5 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": src127})
    src1m = b"DZ 100000\n"
    want1m = lab_brick.assemble(src1m)
    r6 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": src1m})
    src1m1 = b"DZ 100001\n"
    r7 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": src1m1})
    # ФОРМ-пины imm32 (E9.5-2): байты тела фиксируют новые пределы —
    # cmp eax,0x100000 + jbe (тело 1 МиБ), cmp rax,0x1100000 (исходник
    # 17 МиБ), cmp r11d,0x20000 (метки 131072), errtab[8] BIG LABELS
    # (код 11) + строка. Точный край меток 131073 — O(n^2) ~млрд шагов,
    # поэтому предел меток пинится ФОРМОЙ (прецедент — imm32-пины
    # SHA секции 1); семантика 2049+ меток — dev LAB/ai/brick_build_lim5.py
    exe_body = open(brick_exe, "rb").read()[0x200:0x200 + 0xBC8]
    pins = (b"\x3D\x00\x00\x10\x00\x76" in exe_body and
            b"\x48\x3D\x00\x00\x10\x01" in exe_body and
            b"\x41\x81\xFB\x00\x00\x02\x00" in exe_body and
            b"U-L1-BRICK ERR=BIG LABELS" in exe_body)
    check("T-E6-36 пределы brick 17 МиБ/131072 меток/тело 1 МиБ"
          " (512К+20 и 1025 меток и тела 64К/128К-1/1М приняты /"
          " 17М и тело 1М+1 отвергнуты; imm32-пины меток)",
          r1.exit_code == 0 and r1.files.get("t.bin") == b"" and
          r2.exit_code == 0 and r2.files.get("t.bin") == want1025 and
          r3.exit_code == 7 and
          r3.stdout == b"U-L1-BRICK ERR=BIG SRC\r\n" and
          r4.exit_code == 0 and r4.files.get("t.bin") == want64 and
          r5.exit_code == 0 and r5.files.get("t.bin") == want127 and
          r6.exit_code == 0 and r6.files.get("t.bin") == want1m and
          r7.exit_code == 10 and
          r7.stdout == b"U-L1-BRICK ERR=BIG OUT\r\n" and
          pins,
          "шагов=%d+%d+%d+%d+%d+%d+%d" % (r1.steps, r2.steps, r3.steps,
                                           r4.steps, r5.steps, r6.steps,
                                           r7.steps))


# ------------------------------------------------------------------ 8c
def _t_pegen_lim(check, kpath, kfile, kernel_host):
    """Инструмент pegen.exe: предел образа 1 МиБ (E9.5-1a; было 128 КиБ
    с E6.4g-3 и 64 КиБ с E4 — мотив роста: тела чужих EXE до 1 МиБ,
    синхронно плану E9.5-2 подъёма тела brick)."""
    pegen_exe = kpath("L0-PEGEN/pegen.exe")
    peg = kfile("L0-PEGEN/pegen.peg").decode("latin1")

    # T-E6-53 (E9.5-1a): 0x10001 (старый предел 64 КиБ — отверг бы),
    # 0x20000 (старый предел 128 КиБ — отверг бы) и 0x100000 (максимум)
    # приняты и == оракулу wrap; 0x100001 отвергнут ERR=BIG IMAGE
    img65 = b"\x41" * 0x10001
    want65 = lab_pegen.wrap(img65, peg)
    r1 = lab_run.run_kv(pegen_exe, ["a.bin", "p.peg", "o.exe"],
                        {"a.bin": img65, "p.peg": peg.encode()})
    img128 = b"\x42" * 0x20000
    want128 = lab_pegen.wrap(img128, peg)
    r2 = lab_run.run_kv(pegen_exe, ["a.bin", "p.peg", "o.exe"],
                        {"a.bin": img128, "p.peg": peg.encode()})
    img1m = b"\x44" * 0x100000
    want1m = lab_pegen.wrap(img1m, peg)
    r3 = lab_run.run_kv(pegen_exe, ["a.bin", "p.peg", "o.exe"],
                        {"a.bin": img1m, "p.peg": peg.encode()})
    img_over = b"\x43" * 0x100001
    r4 = lab_run.run_kv(pegen_exe, ["a.bin", "p.peg", "o.exe"],
                        {"a.bin": img_over, "p.peg": peg.encode()})
    check("T-E6-53 предел образа pegen 1 МиБ (64К+1 и 128К и 1М приняты =="
          " оракулу / 1М+1 отвергнут)",
          r1.exit_code == 0 and r1.files.get("o.exe") == want65 and
          r2.exit_code == 0 and r2.files.get("o.exe") == want128 and
          r3.exit_code == 0 and r3.files.get("o.exe") == want1m and
          r4.exit_code == 6 and
          r4.stdout == b"U-L0-PEGEN ERR=BIG IMAGE\r\n",
          "шагов=%d+%d+%d+%d" % (r1.steps, r2.steps, r3.steps, r4.steps))


def run(check, kpath, kfile, kernel_host):
    """Исполнить секции 7-8c (инструменты enc/splice/brick/pegen)."""
    _t_enc_exe(check, kpath, kfile, kernel_host)
    _t_splice(check, kpath, kfile, kernel_host)
    _t_brick(check, kpath, kfile, kernel_host)
    _t_pegen_lim(check, kpath, kfile, kernel_host)
