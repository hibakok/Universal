"""lab_t_wall.py — секция 9 батареи: оракул WALL v1/v2 (SPEC/11).

Вход:  колбэки check/kpath/kfile из lab_verify, оракулы LAB.
Выход: проверки T-E6-19..24 (v1) и T-E6-31..35 (v2, E6.4c).
Функция: (1) якоря компиляции — полные и фрагментные, выписанные вручную
         в lab_l2_cases / lab_l2_cases2 (независимые свидетели);
         (2) отвержение ошибок с номерами строк (v1: 26 — инструмент
         wall.exe сверяется только с ними; v2: 13); (3) полные круги
         DEMO_WALL -> ... -> эмуляция ("U-WALL-OK 37") и DEMO_WALL2
         (массивы, * / %, break/continue, && / ||, куча — "U-WALL2-OK
         85"); (4) PE-инварианты демо-EXE по SPEC/11; (5) все M-строки
         всех выходов кодируются оракулом enc; (6) большие исходники
         (v1: 1203 строки; v2: 705 строк с массивами и арифметикой).
"""
import os
import tempfile

import lab_brick
import lab_enc
import lab_l2
import lab_l2_cases
import lab_l2_cases2
import lab_l2_prog
import lab_pe
import lab_pegen
import lab_run

WALL_PEG_ENTRY = 0x1200
WALL_PEG_IDATA = (0x1000, 0x28)
WALL_PEG_IAT = (0x1028, 0x48)


def _compile_all(check):
    """T-E6-19: якоря; T-E6-20: отвержение; все исходники компилируются."""
    bad = []
    for name, src, want in lab_l2_cases.CASES_FULL:
        try:
            if lab_l2.compile_wall(src) != want:
                bad.append(name)
        except lab_l2.WallError as e:
            bad.append("%s (ошибка: %s)" % (name, e))
    for name, src, frag in lab_l2_cases.CASES_FRAG:
        try:
            if frag not in lab_l2.compile_wall(src):
                bad.append(name)
        except lab_l2.WallError as e:
            bad.append("%s (ошибка: %s)" % (name, e))
    check("T-E6-19 якоря компиляции WALL (%d)"
          % (len(lab_l2_cases.CASES_FULL) + len(lab_l2_cases.CASES_FRAG)),
          not bad, "; ".join(bad[:3]) if bad else "")

    bad = []
    for name, src, line in lab_l2_prog.ERRORS:
        try:
            lab_l2.compile_wall(src)
            bad.append("%s: не отвергнуто" % name)
        except lab_l2.WallError as e:
            if e.line != line:
                bad.append("%s: строка %d, ожидалась %d"
                           % (name, e.line, line))
    check("T-E6-20 отвержение некорректных программ (%d)"
          % len(lab_l2_prog.ERRORS), not bad,
          "; ".join(bad[:3]) if bad else "")


def _demo_circle(check):
    """T-E6-21: полный круг; T-E6-22: PE-инварианты демо-EXE."""
    b2 = lab_l2.compile_wall(lab_l2_prog.DEMO_WALL)
    body = lab_brick.assemble(lab_enc.normalize(b2).encode())
    exe = lab_pegen.wrap(body, lab_l2_prog.DEMO_WALL_PEG)
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, exe)
        os.close(fd)
        r = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check("T-E6-21 полный круг WALL->EXE->эмуляция (U-WALL-OK 37)",
          r.stdout == b"U-WALL-OK 37\r\n" and r.exit_code == 0,
          "%r код=%s шагов=%d" % (r.stdout[:24], r.exit_code, r.steps))

    pe = lab_pe.parse(exe)
    bad = [b for b in lab_pe.check_spec04(pe)
           if b != "точка входа != 0x1000"]
    ok = (not bad and pe["addr_entry_point"] == WALL_PEG_ENTRY and
          pe["dd1_import_rva"] == WALL_PEG_IDATA[0] and
          pe["dd1_import_size"] == WALL_PEG_IDATA[1] and
          pe["dd12_iat_rva"] == WALL_PEG_IAT[0] and
          pe["dd12_iat_size"] == WALL_PEG_IAT[1])
    check("T-E6-22 PE-инварианты демо-EXE по SPEC/11", ok,
          "; ".join(bad) if bad else "entry=%X vsize=%X"
          % (pe["addr_entry_point"], pe["sec_vsize"]))


def _m_forms(check):
    """T-E6-24: каждая строка каждого выхода — корректный вход enc."""
    bad = []
    texts = [s for _n, s, _w in lab_l2_cases.CASES_FULL] + \
            [s for _n, s, _f in lab_l2_cases.CASES_FRAG] + \
            [lab_l2_prog.DEMO_WALL]
    for src in texts:
        try:
            out = lab_l2.compile_wall(src)
            lab_enc.normalize(out)          # все M-строки обязаны кодироваться
            lab_brick.assemble(lab_enc.normalize(out).encode())
        except Exception as e:              # noqa: BLE001
            bad.append("%r: %s" % (src.split("\n")[0][:24], e))
    check("T-E6-24 все выходы WALL кодируются enc и собираются brick",
          not bad, "; ".join(bad[:2]) if bad else "")


def _big(check):
    """T-E6-23: большой детерминированный исходник."""
    src = lab_l2_prog.big_source()
    b2 = lab_l2.compile_wall(src)
    body = lab_brick.assemble(lab_enc.normalize(b2).encode())
    b2b = lab_l2.compile_wall(lab_l2_prog.big_source())
    check("T-E6-23 большой исходник (%d строк) компилируется и собирается"
          % src.count("\n"), b2 == b2b and len(body) > 4000,
          "тело %d байт" % len(body))


# ------------------------------------------------------------ v2 (E6.4c)
def _v2_anchors(check):
    """T-E6-31: якоря v2; T-E6-32: отвержение v2."""
    bad = []
    for name, src, want in lab_l2_cases2.CASES_FULL2:
        try:
            if lab_l2.compile_wall(src) != want:
                bad.append(name)
        except lab_l2.WallError as e:
            bad.append("%s (ошибка: %s)" % (name, e))
    for name, src, frag in lab_l2_cases2.CASES_FRAG2:
        try:
            if frag not in lab_l2.compile_wall(src):
                bad.append(name)
        except lab_l2.WallError as e:
            bad.append("%s (ошибка: %s)" % (name, e))
    check("T-E6-31 якоря компиляции WALL v2 (%d)"
          % (len(lab_l2_cases2.CASES_FULL2) + len(lab_l2_cases2.CASES_FRAG2)),
          not bad, "; ".join(bad[:3]) if bad else "")

    bad = []
    for name, src, line in lab_l2_prog.ERRORS2:
        try:
            lab_l2.compile_wall(src)
            bad.append("%s: не отвергнуто" % name)
        except lab_l2.WallError as e:
            if e.line != line:
                bad.append("%s: строка %d, ожидалась %d"
                           % (name, e.line, line))
    check("T-E6-32 отвержение некорректных программ v2 (%d)"
          % len(lab_l2_prog.ERRORS2), not bad,
          "; ".join(bad[:3]) if bad else "")


def _v2_demo_circle(check):
    """T-E6-33: полный круг DEMO_WALL2; заголовок v2; PE-инварианты."""
    b2 = lab_l2.compile_wall(lab_l2_prog.DEMO_WALL2)
    ok_hdr = b2.splitlines()[0] == \
        "; UNIVERSAL / WALL v2 / сгенерировано компилятором WALL (SPEC/11)"
    v1 = lab_l2.compile_wall(lab_l2_prog.DEMO_WALL)
    ok_hdr = ok_hdr and v1.splitlines()[0] == \
        "; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)"
    body = lab_brick.assemble(lab_enc.normalize(b2).encode())
    exe = lab_pegen.wrap(body, lab_l2_prog.DEMO_WALL2_PEG)
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, exe)
        os.close(fd)
        r = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    check("T-E6-33 полный круг WALL v2->EXE->эмуляция (U-WALL2-OK 85)",
          r.stdout == b"U-WALL2-OK 85\r\n" and r.exit_code == 0 and ok_hdr,
          "%r код=%s шагов=%d" % (r.stdout[:24], r.exit_code, r.steps))

    pe = lab_pe.parse(exe)
    bad = [b for b in lab_pe.check_spec04(pe)
           if b != "точка входа != 0x1000"]
    ok = (not bad and pe["addr_entry_point"] == WALL_PEG_ENTRY and
          pe["dd1_import_rva"] == WALL_PEG_IDATA[0] and
          pe["dd1_import_size"] == WALL_PEG_IDATA[1] and
          pe["dd12_iat_rva"] == WALL_PEG_IAT[0] and
          pe["dd12_iat_size"] == WALL_PEG_IAT[1])
    check("T-E6-33 PE-инварианты демо-EXE v2 по SPEC/11", ok,
          "; ".join(bad) if bad else "entry=%X vsize=%X"
          % (pe["addr_entry_point"], pe["sec_vsize"]))


def _v2_m_forms(check):
    """T-E6-34: все M-строки всех выходов v2 кодируются enc (включая
    imul/idiv/cqo — рост ISA E6.4c) и собираются brick."""
    bad = []
    texts = [s for _n, s, _w in lab_l2_cases2.CASES_FULL2] + \
            [s for _n, s, _f in lab_l2_cases2.CASES_FRAG2] + \
            [lab_l2_prog.DEMO_WALL2, lab_l2_prog.big_source2()]
    for src in texts:
        try:
            out = lab_l2.compile_wall(src)
            lab_enc.normalize(out)          # все M-строки обязаны кодироваться
            lab_brick.assemble(lab_enc.normalize(out).encode())
        except Exception as e:              # noqa: BLE001
            bad.append("%r: %s" % (src.split("\n")[0][:24], e))
    check("T-E6-34 все выходы WALL v2 кодируются enc (imul/idiv/cqo)",
          not bad, "; ".join(bad[:2]) if bad else "")


def _v2_big(check):
    """T-E6-35: большой детерминированный исходник v2."""
    src = lab_l2_prog.big_source2()
    b2 = lab_l2.compile_wall(src)
    body = lab_brick.assemble(lab_enc.normalize(b2).encode())
    b2b = lab_l2.compile_wall(lab_l2_prog.big_source2())
    check("T-E6-35 большой исходник v2 (%d строк) компилируется"
          % src.count("\n"),
          b2 == b2b and 4000 < len(body) < 0x10000,
          "тело %d байт" % len(body))


def run(check, kpath, kfile, kernel_host):
    _compile_all(check)
    _demo_circle(check)
    _big(check)
    _m_forms(check)
    _v2_anchors(check)
    _v2_demo_circle(check)
    _v2_m_forms(check)
    _v2_big(check)
