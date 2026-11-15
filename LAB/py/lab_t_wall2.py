"""lab_t_wall2.py — секция 10 батареи: инструмент wall.exe (E6.4b).

Вход:  колбэки check/kpath/kfile из lab_verify, оракулы LAB.
Выход: проверки T-E6-25..30 + T-E6-50 (печать через check).
Функция: (1) справка; (2) все якоря компиляции — wall.exe == оракулу
         байт-в-байт (4 полных + 6 фрагментных, каждый исходник);
         (3) отвержение 26 некорректных программ с кодами и строками;
         (4) полный круг wall -> enc -> brick -> pegen -> эмуляция
         ("U-WALL-OK 37"); (5) big_source (1203 строки) == оракулу;
         (6) SHA-256 + PE-инварианты wall.exe; (7) предел меток
         выхода nlab <= 2000 — точная граница 2000/2001 (T-E6-50,
         E6.4d-3/3-1).
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

WALL_SHA = ("8541FD9DC6F48ABE6DC821F18BD53C39A7FA4AE36AB1AFC3CF5D0171480881AD")


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

    # T-E6-30: SHA-256 + PE-инварианты wall.exe (+ цепочка импортов:
    # E6.4c-3/4b поймал сдвиг idata на 0x17 (ложное совпадение побайтового
    # поиска в wall_build); имена функций в hint-записях вылавливают класс)
    data = kfile("L2-WALL/wall.exe")
    got = hashlib.sha256(data).hexdigest().upper()
    check("T-E6-30 SHA-256 wall.exe", got == WALL_SHA, got[:16] + "…")
    pe = lab_pe.load(kpath("L2-WALL/wall.exe"))
    bad = [b for b in lab_pe.check_spec04(pe) if b != "точка входа != 0x1000"]
    if not pe["imports"] or not pe["imports"][0]["funcs"]:
        bad.append("цепочка импортов пуста (idata мимо :idt)")
    else:
        names = [n for n, _r in pe["imports"][0]["funcs"]]
        if names[:2] != ["GetStdHandle", "WriteFile"] or \
                names[-1] != "CloseHandle" or len(names) != 7:
            bad.append("имена импортов не kernel32-семёрка: %r" % names[:2])
    check("T-E6-30 PE инварианты SPEC/04 wall.exe", not bad,
          "; ".join(bad) if bad else "vsize=%X" % pe["sec_vsize"])

    # T-E6-50: предел меток выхода nlab <= 2000 (E6.4d-3/3-1: 500 ->
    # 2000; ёмкость brick 2048 вкл. base -> запас 48; мотив: каркас
    # wall.wall на 493 метках, статы if/while/break/continue добавят
    # ~30). Граница точная, обе стороны через инструмент + оракул:
    # 2000 меток (var i + 997 пустых while: 2 метки на while — _w<k> и
    # _w<k>e; служебные _idt/_iat/_intt/_entry/main + var i) — принят,
    # выход == оракулу байт-в-байт; 2001 (+ str s) — отвергнут
    # ERR=FORMAT AT=0000 (строка 0 — единственная ошибка строки 0,
    # оракул «больше 2000 меток»). Генератор на while, а не на str:
    # метки _w<k> не попадают в ntab — квадратичного скана таблицы
    # имён нет (12 млн шагов против 37 у эквивалента на str).
    def _mk_wlabs(n, extra_str=False):
        lines = ["var i"]
        if extra_str:
            lines.append("str s = 'x'")
        lines.append("func main")
        for _ in range(n):
            lines.append("    while i < 3")
            lines.append("    end")
        lines.append("end")
        return "\n".join(lines) + "\n"

    src_ok = _mk_wlabs(997)                 # ровно 2000 меток
    r1 = lab_run.run_kv(wall, ["t.wall", "t.b2"],
                        {"t.wall": src_ok.encode()})
    want = lab_l2.compile_wall(src_ok).encode()
    ok1 = r1.exit_code == 0 and r1.files.get("t.b2") == want
    src_no = _mk_wlabs(997, True)           # 2001 метка
    r2 = lab_run.run_kv(wall, ["t.wall", "t.b2"],
                        {"t.wall": src_no.encode()})
    try:
        lab_l2.compile_wall(src_no)
        orcl_rej = False                    # оракул обязан отвергнуть
    except lab_l2.WallError:
        orcl_rej = True
    ok2 = orcl_rej and r2.exit_code == 6 and \
        r2.stdout == b"U-L2-WALL ERR=FORMAT AT=0000\r\n"
    check("T-E6-50 предел меток выхода 2000 (граница 2000/2001)",
          ok1 and ok2, "код=%s/%s шагов=%d+%d" % (r1.exit_code, r2.exit_code,
                                                r1.steps, r2.steps))


def run(check, kpath, kfile, kernel_host):
    _t_wall_exe(check, kpath, kfile, kernel_host)
