"""lab_t_wall2.py — секция 10 батареи: инструмент wall.exe (E6.4b).

Вход:  колбэки check/kpath/kfile из lab_verify, оракулы LAB.
Выход: проверки T-E6-25..30 (печать через check).
Функция: (1) справка; (2) все якоря компиляции — wall.exe == оракулу
         байт-в-байт (4 полных + 6 фрагментных, каждый исходник);
         (3) отвержение 26 некорректных программ с кодами и строками;
         (4) полный круг wall -> enc -> brick -> pegen -> эмуляция
         ("U-WALL-OK 37"); (5) big_source (1203 строки) == оракулу;
         (6) SHA-256 + PE-инварианты wall.exe.
"""
import hashlib
import os
import tempfile

import lab_brick
import lab_enc
import lab_l2
import lab_l2_cases
import lab_l2_prog
import lab_pe
import lab_pegen
import lab_run

WALL_SHA = ("0129BED660F49323E3E8EB7A03E8FF80929F3052FA8D046FBB2224F6E65307C6")


def _t_wall_exe(check, kpath, kfile, kernel_host):
    wall = kpath("L2-WALL/wall.exe")
    enc_exe = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # T-E6-25: справка
    r = lab_run.run_kv(wall, [], {})
    check("T-E6-25 wall справка",
          r.stdout == b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n" and
          r.exit_code == 2, "%r код=%s" % (r.stdout[:44], r.exit_code))

    # T-E6-26: все якоря — wall.exe == оракулу байт-в-байт
    bad = []
    for name, src, want in lab_l2_cases.CASES_FULL:
        r = lab_run.run_kv(wall, ["t.wall", "t.b2"],
                           {"t.wall": src.encode()})
        if not (r.exit_code == 0 and r.files.get("t.b2") ==
                want.encode()):
            bad.append(name)
    for name, src, frag in lab_l2_cases.CASES_FRAG:
        r = lab_run.run_kv(wall, ["t.wall", "t.b2"],
                           {"t.wall": src.encode()})
        if not (r.exit_code == 0 and frag.encode() in
                (r.files.get("t.b2") or b"")):
            bad.append(name)
    check("T-E6-26 wall == оракулу, якоря (%d)"
          % (len(lab_l2_cases.CASES_FULL) + len(lab_l2_cases.CASES_FRAG)),
          not bad, "; ".join(bad[:3]))

    # T-E6-27: отвержение — коды 6 и строки FORMAT AT=
    bad = []
    for name, src, line in lab_l2_prog.ERRORS:
        r = lab_run.run_kv(wall, ["t.wall", "t.b2"],
                           {"t.wall": src.encode()})
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            bad.append(name)
    check("T-E6-27 wall отвержение (%d) с номерами строк"
          % len(lab_l2_prog.ERRORS), not bad, "; ".join(bad[:3]))

    # T-E6-28: полный круг DEMO_WALL -> EXE -> эмуляция
    h = {"d.wall": lab_l2_prog.DEMO_WALL.encode()}
    r1 = lab_run.run_kv(wall, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(enc_exe, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(brick_exe, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
    r4 = lab_run.run_kv(pegen_exe, ["d.bin", "d.peg", "d.exe"], h)
    demo = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check("T-E6-28 полный круг wall->EXE->эмуляция (U-WALL-OK 37)",
          r1.exit_code == 0 and r2.exit_code == 0 and r3.exit_code == 0 and
          r4.exit_code == 0 and r5.stdout == b"U-WALL-OK 37\r\n" and
          r5.exit_code == 0,
          "шагов=%d+%d+%d+%d+%d" % (r1.steps, r2.steps, r3.steps,
                                     r4.steps, r5.steps))

    # T-E6-29: big_source == оракулу
    src = lab_l2_prog.big_source()
    want = lab_l2.compile_wall(src).encode()
    r = lab_run.run_kv(wall, ["big.wall", "big.b2"],
                       {"big.wall": src.encode()})
    check("T-E6-29 big_source (%d строк) == оракулу" % src.count("\n"),
          r.exit_code == 0 and r.files.get("big.b2") == want,
          "шагов=%d" % r.steps)

    # T-E6-30: SHA-256 + PE-инварианты wall.exe
    data = kfile("L2-WALL/wall.exe")
    got = hashlib.sha256(data).hexdigest().upper()
    check("T-E6-30 SHA-256 wall.exe", got == WALL_SHA, got[:16] + "…")
    pe = lab_pe.load(kpath("L2-WALL/wall.exe"))
    bad = [b for b in lab_pe.check_spec04(pe) if b != "точка входа != 0x1000"]
    check("T-E6-30 PE инварианты SPEC/04 wall.exe", not bad,
          "; ".join(bad) if bad else "vsize=%X" % pe["sec_vsize"])


def run(check, kpath, kfile, kernel_host):
    _t_wall_exe(check, kpath, kfile, kernel_host)
