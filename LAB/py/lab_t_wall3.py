"""lab_t_wall3.py — секция 11 батареи: инструмент wall.exe — v2, срезы 1-3.

Вход:  колбэки check/kpath/kfile из lab_verify, оракулы LAB.
Выход: проверки T-E6-37..45 (печать через check).
Функция: (E6.4c-3/3b) регрессионная защита срезов 1-3 WALL v2 в
         wall.exe — перенесено из dev-тестов LAB/ai в батарею ДО
         начала среза 4 (массивы — «самая тонкая часть» по журналу):
         (1) якоря всех срезов + B2-полный + регресс дефекта №15 —
         wall == оракулу байт-в-байт; (2) фрагменты F13/F14/F16 и
         B2-фрагменты break/continue; (3) большие исходники
         big_mdm/big_bc/big_cc == оракулу; (4) отвержение 19 v2-ошибок
         с точными строками; (5) заголовки v1/v2; (6)-(8) полные круги
         DEMO_MDM/DEMO_BC/DEMO_CC до эмуляции; (9) кодируемость
         big-выходов оракулами enc+brick (инструменты равны оракулам —
         секции 7-8b и T-E6-39; инструментальный прогон отклонён
         профилем: +50 с при нулевой добавочной гарантии).
"""
import os
import tempfile

import lab_brick
import lab_enc
import lab_l2
import lab_l2_bc
import lab_l2_cc
import lab_l2_cases
import lab_l2_cases2
import lab_l2_mdm
import lab_l2_prog
import lab_run


def _run_wall(wall, src, name="t.wall"):
    return lab_run.run_kv(wall, [name, "t.b2"], {name: src.encode()})


def _eq_oracle(wall, src):
    """(ok, note): wall == оракулу байт-в-байт (полный выход)."""
    want = lab_l2.compile_wall(src).encode()
    r = _run_wall(wall, src)
    return (r.exit_code == 0 and r.files.get("t.b2") == want,
            "шагов=%d" % r.steps)


def _circle(check, wall, enc_exe, brick_exe, pegen_exe, demo, peg,
            want_out, name):
    """Полный круг WALL -> enc -> brick -> pegen -> эмуляция."""
    h = {"d.wall": demo.encode()}
    r1 = lab_run.run_kv(wall, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(enc_exe, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(brick_exe, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = peg.encode()
    r4 = lab_run.run_kv(pegen_exe, ["d.bin", "d.peg", "d.exe"], h)
    demo_exe = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo_exe)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check(name, r1.exit_code == 0 and r2.exit_code == 0 and
          r3.exit_code == 0 and r4.exit_code == 0 and
          r5.stdout == want_out and r5.exit_code == 0,
          "шагов=%d+%d+%d+%d+%d" % (r1.steps, r2.steps, r3.steps,
                                     r4.steps, r5.steps))


def _t_wall_v2(check, kpath, kfile, kernel_host):
    wall = kpath("L2-WALL/wall.exe")
    enc_exe = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # T-E6-37: якоря срезов 1-3 + B2-полный + регресс дефекта №15
    b2full = lab_l2_cases2.CASES_FULL2[1][1]
    d15 = b2full.replace("while i < 6 && s < 100", "while i < 6").replace(
        "if i == 5 || s == 999", "if i == 5")
    srcs = [("mdm " + n, s) for n, s in lab_l2_mdm.MDM_ANCHORS]
    srcs += [("bc " + n, s) for n, s in lab_l2_bc.BC_ANCHORS]
    srcs += [("cc " + n, s) for n, s in lab_l2_cc.CC_ANCHORS]
    srcs.append(("B2 полный (cases2)", b2full))
    srcs.append(("регресс №15: if в while (bstk 32)", d15))
    bad = [n for n, s in srcs if not _eq_oracle(wall, s)[0]]
    check("T-E6-37 wall == оракулу, якоря срезов 1-3 (%d)" % len(srcs),
          not bad, "; ".join(bad[:3]))

    # T-E6-38: фрагменты F13/F14/F16 (cases2) + B2 break/continue
    bad = []
    nfrag = 0
    for want_name, src, frag in lab_l2_cases2.CASES_FRAG2:
        if not (want_name.startswith("F13") or want_name.startswith("F14")
                or want_name.startswith("F16")):
            continue
        nfrag += 1
        r = _run_wall(wall, src)
        if not (r.exit_code == 0 and
                frag.encode() in (r.files.get("t.b2") or b"")):
            bad.append(want_name)
    core = next(s for n, s in lab_l2_bc.BC_ANCHORS
                if n.startswith("bc_B2_ядро"))
    r = _run_wall(wall, core)
    got = r.files.get("t.b2", b"")
    if not (r.exit_code == 0 and b"M jmp $_w1 ; continue" in got and
            b"M jmp $_w1e ; break" in got):
        bad.append("B2-фрагменты break/continue")
    check("T-E6-38 wall фрагменты F13/F14/F16 + B2 break/continue (%d)"
          % (nfrag + 1), not bad, "; ".join(bad[:3]))

    # T-E6-39: большие исходники срезов == оракулу
    bigs = [("mdm", lab_l2_mdm.big_mdm()), ("bc", lab_l2_bc.big_bc()),
            ("cc", lab_l2_cc.big_cc())]
    bad = [n for n, s in bigs if not _eq_oracle(wall, s)[0]]
    check("T-E6-39 wall == оракулу, big (%d: %s)" % (
        len(bigs), "/".join(str(s.count("\n")) for _n, s in bigs)),
        not bad, "; ".join(bad))

    # T-E6-40: отвержение v2-ошибок с точными строками
    errs = list(lab_l2_mdm.MDM_ERRORS)                 # (имя, исходник)
    errs += [(n, s) for n, s, _l in lab_l2_prog.ERRORS2
             if n in lab_l2_bc.BC_ERR_NAMES]
    errs.append(lab_l2_bc.BC_BREAK_TAIL)
    errs += list(lab_l2_cc.CC_ERRORS)
    bad = []
    for name, src in errs:
        line = next((l for n, s, l in lab_l2_prog.ERRORS2
                     if n == name), None)
        if line is None:                               # строка из оракула
            try:
                lab_l2.compile_wall(src)
                bad.append(name + " (оракул принял)")
                continue
            except lab_l2.WallError as e:
                line = e.line
        r = _run_wall(wall, src)
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            bad.append(name)
    check("T-E6-40 wall v2 отвержение (%d) с номерами строк" % len(errs),
          not bad, "; ".join(bad[:3]))

    # T-E6-41: заголовки v1/v2 (флаг v2 по наличию конструкций)
    hdrs = [("v1 (cases A1)", lab_l2_cases.CASES_FULL[0][1], b"WALL v1"),
            ("v2 mdm", lab_l2_mdm.MDM_ANCHORS[0][1], b"WALL v2"),
            ("v2 bc", lab_l2_bc.BC_ANCHORS[0][1], b"WALL v2"),
            ("v2 cc", lab_l2_cc.CC_ANCHORS[0][1], b"WALL v2")]
    bad = []
    for name, src, marker in hdrs:
        h = (_run_wall(wall, src).files.get("t.b2") or b"").split(b"\n")[0]
        oh = lab_l2.compile_wall(src).encode().split(b"\n")[0]
        if not (h == oh and marker in h):
            bad.append(name)
    check("T-E6-41 wall заголовки v1/v2 (%d)" % len(hdrs), not bad,
          "; ".join(bad))

    # T-E6-42..44: полные круги DEMO_MDM / DEMO_BC / DEMO_CC
    _circle(check, wall, enc_exe, brick_exe, pegen_exe,
            lab_l2_mdm.DEMO_MDM, lab_l2_mdm.DEMO_MDM_PEG,
            b"U-MDM-OK 52\r\n", "T-E6-42 полный круг mdm (U-MDM-OK 52)")
    _circle(check, wall, enc_exe, brick_exe, pegen_exe,
            lab_l2_bc.DEMO_BC, lab_l2_bc.DEMO_BC_PEG,
            b"U-BC-OK 25\r\n", "T-E6-43 полный круг bc (U-BC-OK 25)")
    _circle(check, wall, enc_exe, brick_exe, pegen_exe,
            lab_l2_cc.DEMO_CC, lab_l2_cc.DEMO_CC_PEG,
            b"U-CC-OK 31\r\n", "T-E6-44 полный круг cc (U-CC-OK 31)")

    # T-E6-45: big-выходы срезов кодируются — оракулы enc+brick
    # (достаточно: wall == оракулу — T-E6-39, а enc.exe/brick.exe ==
    # своим оракулам — секции 7-8b; ловит класс «имя метки вне
    # [a-z0-9_]» — урок среза 3, pcd_chk7C)
    bad = []
    for name, src in bigs:
        try:
            out = lab_l2.compile_wall(src)
            lab_brick.assemble(lab_enc.normalize(out).encode())
        except Exception as e:
            bad.append("%s (%s)" % (name, e))
    check("T-E6-45 big-выходы срезов кодируются enc+brick (%d)"
          % len(bigs), not bad, "; ".join(bad))


def run(check, kpath, kfile, kernel_host):
    _t_wall_v2(check, kpath, kfile, kernel_host)
