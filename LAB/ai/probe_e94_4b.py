"""probe_e94_4b.py — зонд E9.4-4b-1 (ДО канонической пересборки): сборка
bridge.exe ОРАКУЛОМ (splice + compile_wall -> b2; lab_enc/lab_brick/
lab_pegen — чистый Python, без эмуляции конвейера) и прогоны под
эмулятором lab_run:
  (1) НЕЙТРАЛЬНОСТЬ семейства — 12 артефактов: факт-строка + t.b2 +
      t.peg == оракулу (развилка «семья | чужой» не меняет семейный
      путь: вычисляемые смещения при e_lfanew == 0x80 дают те же
      значения, fend == exelen — инвариант размеров, вилка falign ==
      512);
  (2) ПОРТ чужого пути — крафты E9.4-3a/3b (foreign_image/
      foreign2_image из lab_t_bridge_corpus): bridge.exe печатает
      ЧУЖУЮ факт-строку FOREIGN=1 SECT=… == фактам parse_foreign
      оракула, код 0, ВЫХОДНЫЕ ФАЙЛЫ НЕ СОЗДАЮТСЯ (эмиссия чужих —
      срезы E9.4-4b-2+);
  (3) ОТКАЗЫ чужого фронта — 7 мутантов foreign2: ERR=FAMILY, код 6
      (порядок проверок SPEC/15 п. 10; отказы семьи и чужого фронта
      сходятся в общий код).

Выход: таблица [OK]/[FAIL] + сводка шагов эмуляции.
Запуск: python3 LAB/ai/probe_e94_4b.py  (из корня репозитория)
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_brick                             # noqa: E402
import lab_bridge                            # noqa: E402
import lab_enc                               # noqa: E402
import lab_l2                                # noqa: E402
import lab_pegen                             # noqa: E402
import lab_run                               # noqa: E402
import lab_splice                            # noqa: E402
import lab_t_bridge_corpus as K              # noqa: E402

ROOT = os.path.join(os.path.dirname(HERE), "..")
KERNEL = os.path.join(ROOT, "KERNEL")

ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]

FAMILY_MSG = b"U-L5-BRIDGE ERR=FAMILY\r\n"


def kpath(rel):
    return os.path.join(KERNEL, rel)


def kfile(rel):
    return open(os.path.join(KERNEL, rel), "rb").read()


def kernel_host():
    files = {}
    for root, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def build_oracle():
    """Быстрая сборка моста оракулами LAB (без эмуляции конвейера)."""
    src = lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
    b2 = lab_l2.compile_wall(src.decode("latin1"))
    body = lab_brick.assemble(lab_enc.normalize(b2).encode("utf-8"))
    exe = lab_pegen.wrap(body, kfile("L5-BRIDGE/bridge.peg").decode())
    return b2, body, exe


def fact_line(data):
    """Ожидаемая семейная факт-строка (копия facts_line lab_t_bridge)."""
    fam = lab_bridge.parse_family(data)
    pe = fam["pe"]
    _t, st = lab_bridge.emit_b2(data)
    return ("U-L5-BRIDGE MODULE=%s ENTRY=%08X VSIZE=%08X RAW=%08X IMP=%d"
            " INS=%d TARGET=%08X BSS=%08X M=%d H=%d\r\n"
            % (fam["module"], pe["addr_entry_point"], fam["vsize"],
               fam["raw"], len(pe["imports"][0]["funcs"]),
               len(fam["ins"]), fam["target"], fam["bss"],
               st["m"], st["h"])
            ).encode("latin1")


def foreign_line(data):
    """Ожидаемая ЧУЖАЯ факт-строка (E9.4-4b-1): факты parse_foreign."""
    f = lab_bridge.parse_foreign(data)
    pe = f["pe"]
    return ("U-L5-BRIDGE FOREIGN=1 SECT=%d ENTRY=%08X VSIZE=%08X RAW=%08X"
            " INS=%d TARGET=%08X BSS=%08X\r\n"
            % (pe["sections"].index(f["code"]), pe["addr_entry_point"],
               f["vsize"], f["raw"], len(f["ins"]), f["target"], f["bss"])
            ).encode("latin1")


def run_family(bexe, data, total):
    """Один семейный прогон: факты + t.b2 + t.peg == оракулу."""
    want_b2, _st = lab_bridge.emit_b2(data)
    want_peg = lab_bridge.emit_peg(data)
    want_fact = fact_line(data)
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"], {"in.exe": data})
    total[0] += r.steps
    ok = (r.exit_code == 0
          and r.files.get("t.b2") == want_b2.encode("utf-8")
          and r.files.get("t.peg") == want_peg.encode("utf-8")
          and r.stdout == want_fact)
    return ok, r, want_fact


def run_foreign(bexe, data, total):
    """Один ЧУЖОЙ прогон: факт-строка FOREIGN == оракулу, код 0,
    выходные файлы НЕ создаются (эмиссия — срезы E9.4-4b-2+)."""
    want_fact = foreign_line(data)
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"], {"in.exe": data})
    total[0] += r.steps
    ok = (r.exit_code == 0
          and r.stdout == want_fact
          and "t.b2" not in r.files
          and "t.peg" not in r.files)
    return ok, r, want_fact


def main():
    print("=== probe E9.4-4b-1: сборка моста оракулом (развилка + "
          "чужие факты) ===")
    b2, body, exe = build_oracle()
    print("b2 %d Б, тело %d Б, exe %d Б" % (len(b2.encode()), len(body),
                                            len(exe)))
    fd, bexe = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    with open(bexe, "wb") as f:
        f.write(exe)
    fails = []
    total = [0]
    try:
        print("--- (1) нейтральность семейства (12 артефактов) ---")
        for m in ARTIFACTS:
            data = kfile("%s.exe" % m)
            ok, r, want_fact = run_family(bexe, data, total)
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails.append(m)
            print("[%s] %-10s шаги %8d  %r" % (tag, m.split("/")[-1],
                                               r.steps, r.stdout[:64]))
            if not ok:
                print("     код=%s факт: got=%r want=%r"
                      % (r.exit_code, r.stdout[:80], want_fact[:80]))
                print("     b2 %d Б, peg %d Б"
                      % (len(r.files.get("t.b2") or b""),
                         len(r.files.get("t.peg") or b"")))
        print("--- (2) ПОРТ: чужой путь (крафты 3a/3b) ---")
        for name, img in (("foreign", K.foreign_image()),
                          ("foreign2", K.foreign2_image())):
            ok, r, want_fact = run_foreign(bexe, img, total)
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails.append(name)
            print("[%s] %-9s шаги %8d  %r" % (tag, name, r.steps,
                                              r.stdout[:72]))
            if not ok:
                print("     код=%s факт: got=%r want=%r"
                      % (r.exit_code, r.stdout[:90], want_fact[:90]))
                print("     файлы: %r" % sorted(r.files))
        print("--- (3) отказы чужого фронта (7 мутантов foreign2) ---")
        for name, data in K.foreign2_rejects():
            r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                               {"in.exe": data})
            total[0] += r.steps
            ok = r.exit_code == 6 and r.stdout == FAMILY_MSG
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails.append("reject:%s" % name)
            print("[%s] %-24s код %s  %r" % (tag, name, r.exit_code,
                                             r.stdout[:40]))
    finally:
        os.unlink(bexe)
    print("итог: %d провалов, шагов %d" % (len(fails), total[0]))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
