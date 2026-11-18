"""wall_self_canary.py — dev-прогон канареек финала E6.4d-5 (шаги 1-2).

Вход:  KERNEL/L2-WALL/wall.wall (каркас с проходом 2, срезы A+B+C-1+
         C-2/1..3+C-3 — класс полного выхода: любые тела прохода 1).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: шаг 1 финала E6.4d — канарейки круга: DEMO_MDM/DEMO_BC/
         DEMO_CC/DEMO_ARR/DEMO_WALL2/DEMO_NEST компилируются КАРКАСОМ
         (полный круг: каркас -> enc -> brick -> pegen -> эмуляция) и
         обязаны напечатать свои эталонные строки («U-MDM-OK 52» ...
         «U-NEST-OK 4C»); шаг 2 — big_source/big_source2 компилируются
         каркасом байт-в-байт == оракулу (стресс пределов: метки,
         таблицы, T-склад, nlab).
Запуск: python3 LAB/ai/wall_self_canary.py  (из корня репозитория)
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2                             # noqa: E402
import lab_l2_arr                         # noqa: E402
import lab_l2_bc                          # noqa: E402
import lab_l2_cc                          # noqa: E402
import lab_l2_mdm                         # noqa: E402
import lab_l2_prog                        # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
WALL = os.path.join(KERNEL, "L2-WALL", "wall.exe")
ENC = os.path.join(KERNEL, "L1-ENC", "enc.exe")
BRICK = os.path.join(KERNEL, "L1-BRICK", "brick.exe")
PEGEN = os.path.join(KERNEL, "L0-PEGEN", "pegen.exe")

PASS, FAIL = [], []

DEMOS = [
    ("mdm", "M", lab_l2_mdm.DEMO_MDM, lab_l2_mdm.DEMO_MDM_PEG,
     b"U-MDM-OK 52\r\n"),
    ("bc", "B", lab_l2_bc.DEMO_BC, lab_l2_bc.DEMO_BC_PEG,
     b"U-BC-OK 25\r\n"),
    ("cc", "C", lab_l2_cc.DEMO_CC, lab_l2_cc.DEMO_CC_PEG,
     b"U-CC-OK 31\r\n"),
    ("arr", "A", lab_l2_arr.DEMO_ARR, lab_l2_arr.DEMO_ARR_PEG,
     b"U-ARR-OK 45\r\n"),
    ("wall2", "W", lab_l2_prog.DEMO_WALL2, lab_l2_prog.DEMO_WALL2_PEG,
     b"U-WALL2-OK 85\r\n"),
    ("nest", "N", lab_l2_prog.DEMO_NEST, lab_l2_prog.DEMO_NEST_PEG,
     b"U-NEST-OK 4C\r\n"),
]


def check(name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print(("[OK] " if ok else "[FAIL] ") + name +
          (("  " + note) if note else ""))


def kernel_host():
    files = {}
    for base, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def build_skeleton():
    """Полный круг сборки EXE каркаса; вернуть (exe, b2)."""
    src = lab_splice.splice("L2-WALL/wall.wall", kernel_host())
    r = lab_run.run_kv(WALL, ["s.wall", "s.b2"], {"s.wall": src})
    if r.exit_code != 0:
        return None, None
    b2 = r.files["s.b2"]
    h = {"s.b2": b2}
    r2 = lab_run.run_kv(ENC, ["s.b2", "s.brick"], h)
    if r2.exit_code != 0:
        return None, None
    h["s.brick"] = r2.files["s.brick"]
    r3 = lab_run.run_kv(BRICK, ["s.brick", "s.bin"], h)
    if r3.exit_code != 0:
        return None, None
    h["s.bin"] = r3.files["s.bin"]
    h["s.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["s.bin", "s.peg", "s.exe"], h)
    if r4.exit_code != 0 or "s.exe" not in r4.files:
        return None, None
    return r4.files["s.exe"], b2


def canary_circle(skel_path, demo, peg, want_out):
    """Каркас компилирует DEMO; полный круг до эмуляции. (ok, note)."""
    h = {"d.wall": demo.encode()}
    r1 = lab_run.run_kv(skel_path, ["d.wall", "d.b2"], h)
    if r1.exit_code != 0:
        return False, "каркас: код=%s out=%r" % (r1.exit_code,
                                                 r1.stdout[:40])
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = peg.encode()
    r4 = lab_run.run_kv(PEGEN, ["d.bin", "d.peg", "d.exe"], h)
    demo_exe = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo_exe)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    ok = (r2.exit_code == 0 and r3.exit_code == 0 and r4.exit_code == 0
          and r5.stdout == want_out and r5.exit_code == 0)
    return ok, "шагов=%d+%d+%d+%d+%d" % (r1.steps, r2.steps, r3.steps,
                                         r4.steps, r5.steps)


def big_eq(skel_path, src):
    """Каркас компилирует большой исходник == оракулу. (ok, note)."""
    want = lab_l2.compile_wall(src).encode()
    r = lab_run.run_kv(skel_path, ["b.wall", "b.b2"],
                       {"b.wall": src.encode()})
    got = r.files.get("b.b2", b"")
    ok = r.exit_code == 0 and got == want
    note = "шагов=%d, %d/%d Б" % (r.steps, len(got), len(want))
    if not ok and got:
        n = min(len(got), len(want))
        for i in range(n):
            if got[i] != want[i]:
                note += ("; 1-е расхождение @%d:\n   получено: %r\n"
                         "   нужно:    %r"
                         % (i, got[max(0, i - 30):i + 30],
                            want[max(0, i - 30):i + 30]))
                break
    return ok, note


def main():
    exe, b2 = build_skeleton()
    check("сборка каркаса: полный круг (wall+enc+brick+pegen)",
          bool(exe), "s.b2=%s" % (len(b2) if b2 else "-"))
    if not exe:
        print("\nИТОГ: %d/%d — ПРОВАЛЫ" % (len(PASS), len(PASS) + len(FAIL)))
        return 1
    fd, skel = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    open(skel, "wb").write(exe)
    try:
        # шаг 1: канарейки круга — 6 DEMO программ КАРКАСОМ
        for name, _tag, demo, peg, want_out in DEMOS:
            ok, note = canary_circle(skel, demo, peg, want_out)
            check("круг %s: каркас -> enc -> brick -> pegen -> эмуляция"
                  % name, ok, note)
        # шаг 2: большие исходники == оракулу (каркас)
        for name, src in [("big_source", lab_l2_prog.big_source()),
                          ("big_source2", lab_l2_prog.big_source2())]:
            ok, note = big_eq(skel, src)
            check("%s (%d строк) == оракулу (каркас)"
                  % (name, src.count("\n")), ok, note)
    finally:
        os.unlink(skel)
    print("\nИТОГ: %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                "OK" if not FAIL else "— ПРОВАЛЫ"))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
