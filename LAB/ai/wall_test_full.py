"""test_wall_full.py — стресс и полный круг wall.exe (sandbox-инструмент).

Вход:  собранный wall.exe.
Выход: big_source == оракулу; DEMO полный круг до эмуляции; тайминги.
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))
import lab_brick                    # noqa: E402
import lab_enc                      # noqa: E402
import lab_l2                       # noqa: E402
import lab_l2_prog                  # noqa: E402
import lab_pe                       # noqa: E402
import lab_pegen                    # noqa: E402
import lab_run                      # noqa: E402

U = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WALL = os.path.join(U, "KERNEL", "L2-WALL", "wall.exe")


def main():
    # 1) big_source == оракулу
    src = lab_l2_prog.big_source()
    t0 = time.time()
    oracle = lab_l2.compile_wall(src).encode()
    t_oracle = time.time() - t0
    t0 = time.time()
    r = lab_run.run_kv(WALL, ["big.wall", "big.b2"],
                       {"big.wall": src.encode()})
    t_tool = time.time() - t0
    got = r.files.get("big.b2", b"")
    ok = (r.exit_code == 0 and got == oracle)
    print("[%s] big_source (%d строк) == оракулу  %d байт, шагов=%d"
          % ("OK" if ok else "FAIL", src.count("\n"), len(got), r.steps))
    print("   время: оракул %.1fs / инструмент (эмуляция) %.1fs"
          % (t_oracle, t_tool))
    if not ok:
        gl, wl = got.split(b"\n"), oracle.split(b"\n")
        for i, (a, b) in enumerate(zip(gl, wl)):
            if a != b:
                print("   строка %d:\n     got:    %r\n     oracle: %r"
                      % (i + 1, a[:80], b[:80]))
                break
        return 1

    # 2) DEMO полный круг: wall -> enc -> brick -> pegen -> эмуляция
    demo = lab_l2_prog.DEMO_WALL
    t0 = time.time()
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"],
                        {"d.wall": demo.encode()})
    b2 = r1.files.get("d.b2", b"")
    print("[%s] wall(DEMO) шагов=%d" % ("OK" if r1.exit_code == 0 else
                                        "FAIL", r1.steps))
    # enc
    r2 = lab_run.run_kv(os.path.join(U, "KERNEL/L1-ENC/enc.exe"),
                        ["d.b2", "d.brick"], {"d.b2": b2})
    brick_txt = r2.files.get("d.brick", b"")
    print("[%s] enc(DEMO.b2) шагов=%d" % ("OK" if r2.exit_code == 0 else
                                          "FAIL", r2.steps))
    # brick
    r3 = lab_run.run_kv(os.path.join(U, "KERNEL/L1-BRICK/brick.exe"),
                        ["d.brick", "d.bin"], {"d.brick": brick_txt})
    body = r3.files.get("d.bin", b"")
    print("[%s] brick(DEMO) шагов=%d, тело %d байт"
          % ("OK" if r3.exit_code == 0 else "FAIL", r3.steps, len(body)))
    # pegen
    r4 = lab_run.run_kv(os.path.join(U, "KERNEL/L0-PEGEN/pegen.exe"),
                        ["d.bin", "d.peg", "d.exe"],
                        {"d.bin": body,
                         "d.peg": lab_l2_prog.DEMO_WALL_PEG.encode()})
    exe = r4.files.get("d.exe", b"")
    print("[%s] pegen(DEMO) шагов=%d, EXE %d байт"
          % ("OK" if r4.exit_code == 0 else "FAIL", r4.steps, len(exe)))
    # эмуляция
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, exe)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    ok5 = (r5.stdout == b"U-WALL-OK 37\r\n" and r5.exit_code == 0)
    print("[%s] эмуляция: %r код=%s шагов=%d"
          % ("OK" if ok5 else "FAIL", r5.stdout, r5.exit_code, r5.steps))
    print("   полный круг: %.1fs (эмуляция конвейера)" % (time.time() - t0))
    # PE-инварианты
    pe = lab_pe.parse(exe) if hasattr(lab_pe, "parse") else None
    if pe:
        bad = [b for b in lab_pe.check_spec04(pe)
               if b != "точка входа != 0x1000"]
        print("[%s] PE-инварианты: entry=%X"
              % ("OK" if not bad and pe["addr_entry_point"] == 0x1200
                 else "FAIL", pe["addr_entry_point"]))
    return 0 if (ok and ok5) else 1


if __name__ == "__main__":
    sys.exit(main())
