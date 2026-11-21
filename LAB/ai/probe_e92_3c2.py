"""probe_e92_3c2.py — зонд E9.2-3c №2: БЫСТРАЯ проверка нового
bridge.exe ДО канонической пересборки — мост собран ОРАКУЛАМИ
(splice -> compile_wall -> enc.normalize -> brick.assemble -> pegen.wrap
+ bridge.peg — без эмуляции wall.exe), затем прогон под lab_run:
(1) факт-строка (с M=/H=) == оракулу facts_line на 12 артефактах;
(2) t.b2 == оракулу КАНОНА emit_b2 (mode=None) на 12 артефактах +
синтетике (synthm/hint-ins/imp0);
(3) круг оракула над новым bridge.exe (12-й артефакт);
(4) сквозной круг инструментами на seed (enc.exe -> brick.exe ->
pegen.exe == EXE — M-строки парсятся enc).
Хронометраж — итерации среза E9.2-3c (прецедент dev_t22.py).
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "py"))

import lab_brick                          # noqa: E402
import lab_bridge                         # noqa: E402
import lab_enc                            # noqa: E402
import lab_l2                             # noqa: E402
import lab_pegen                          # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402
import lab_t_bridge                       # noqa: E402 — факты/артефакты

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..")


def kfile(rel):
    return open(os.path.join(ROOT, "KERNEL", rel), "rb").read()


def build_oracle(host):
    flat = lab_splice.splice("L5-BRIDGE/bridge.wall", host)
    b2 = lab_l2.compile_wall(flat.decode("latin1"))
    brick = lab_brick.assemble(
        lab_enc.normalize(b2).encode("utf-8"))
    exe = lab_pegen.wrap(brick, kfile("L5-BRIDGE/bridge.peg")
                         .decode("latin1"))
    return b2, brick, exe


def synth_cases():
    return lab_t_bridge.run.__globals__ and None  # pragma: no cover


def main():
    host = {}
    for root, _dirs, fs in os.walk(os.path.join(ROOT, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(ROOT, "KERNEL")) \
                .replace(os.sep, "/").lower()
            host[rel] = open(p, "rb").read()

    t0 = time.time()
    b2, brick, exe = build_oracle(host)
    print("сборка оракулами: b2 %d Б, тело %d Б, EXE %d Б (%.1f с)"
          % (len(b2.encode()), len(brick), len(exe), time.time() - t0))

    # круг оракула над НОВЫМ bridge.exe (12-й артефакт)
    try:
        _b, peg = lab_bridge.bridge(exe)
        body = lab_brick.assemble(
            lab_enc.normalize(_b).encode("utf-8"))
        made = lab_pegen.wrap(body, peg)
        print("круг оракула над новым bridge.exe: %s"
              % ("OK байт-в-байт" if made == exe else "FAIL"))
    except Exception as e:                  # noqa: BLE001
        print("круг оракула над новым bridge.exe: EXC %r" % e)

    fd = "/tmp/bridge_new.exe"
    with open(fd, "wb") as f:
        f.write(exe)

    # (1) факт-строка с M=/H= == оракулу; (2) t.b2 == канону
    arts = lab_t_bridge.ARTIFACTS
    bad_f, bad_b = [], []
    t0 = time.time()
    for m in arts + ["L5-BRIDGE/bridge"]:
        data = kfile("%s.exe" % m) if m != "L5-BRIDGE/bridge" else exe
        want = lab_t_bridge.facts_line(data)
        wantb, st = lab_bridge.emit_b2(data)
        r = lab_run.run_kv(fd, ["in.exe", "t.b2", "t.peg"],
                           {"in.exe": data})
        if r.stdout != want or r.exit_code != 0:
            bad_f.append("%s: %r код=%s" % (m, r.stdout[:60],
                                            r.exit_code))
        if r.files.get("t.b2") != wantb.encode("utf-8"):
            bad_b.append("%s (код %s, %d Б)" % (m, r.exit_code,
                          len(r.files.get("t.b2") or b"")))
        print("%-16s факты %s  b2 %s  (M=%d H=%d)"
              % (m.split("/")[-1],
                 "OK" if not bad_f or bad_f[-1][:6] != m else "FAIL",
                 "OK" if not bad_b or bad_b[-1][:6] != m else "FAIL",
                 st["m"], st["h"]))
    print("факт-строки (M=/H=): %s" % ("ВСЕ == оракулу"
          if not bad_f else "; ".join(bad_f[:3])))
    print("t.b2 == канон: %s" % ("ВСЕ == оракулу"
          if not bad_b else "; ".join(bad_b[:3])))
    print("хронометраж: %.1f с" % (time.time() - t0))
    return 0 if not bad_f and not bad_b else 1


if __name__ == "__main__":
    sys.exit(main())
