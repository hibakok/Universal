"""probe_e94_4a.py — зонд E9.4-4a №1 (ДО канонической пересборки): сборка
bridge.exe ОРАКУЛОМ (splice + compile_wall -> b2; lab_enc/lab_brick/
lab_pegen — чистый Python, без эмуляции конвейера) и прогоны под
эмулятором lab_run:
  (1) НЕЙТРАЛЬНОСТЬ семейства — 12 артефактов: факт-строка + t.b2 +
      t.peg == оракулу (декодер FF /4, jtab-кандидаты и дедупликация
      push_tgt НЕ меняют поведение семейного пути — FF /4 в теле
      инструментов не встречается, прямые цели дедуплицированы
      без изменения семантики спуска);
  (2) ПОРТ FF /4 + таблицы — синтетика synth4/synth5 (T-E9-26, секция
      18c) и synth6/synth7 (T-E9-27, секция 18d): факты/строки/PEG ==
      оракулу — терминал dcls 5, кандидаты _jtab, H-строки FF /4
      (M невозможна — m_bjmp отказ по виду операнда).

Выход: таблица [OK]/[FAIL] + сводка шагов эмуляции.
Запуск: python3 LAB/ai/probe_e94_4a.py  (из корня репозитория)
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
    """Ожидаемая факт-строка (копия facts_line lab_t_bridge)."""
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


def synth_images(body):
    """Синтетика FF /4 и таблиц (как lab_t_bridge_ff/_jt): образы из
    префикса тела bridge + крафт + PEG-шаблон."""
    pfx = body[:0x200]
    return [("synth4", lab_pegen.wrap(pfx + K.FF4_CRAFT4,
                                       K.FF4_PEG % "synth4")),
            ("synth5", lab_pegen.wrap(pfx + K.FF4_CRAFT5,
                                       K.FF4_PEG % "synth5")),
            ("synth6", lab_pegen.wrap(pfx + K.JT_CRAFT6,
                                       K.JT_PEG % "synth6")),
            ("synth7", lab_pegen.wrap(pfx + K.JT_CRAFT7,
                                       K.JT_PEG % "synth7"))]


def run_case(bexe, data, total):
    """Один прогон моста: факты + t.b2 + t.peg == оракулу."""
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


def main():
    print("=== probe E9.4-4a: сборка моста оракулом (FF /4 + jtab) ===")
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
            ok, r, want_fact = run_case(bexe, data, total)
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails.append(m)
            print("[%s] %-10s шаги %8d  %r" % (tag, m.split("/")[-1],
                                               r.steps, r.stdout[:64]))
            if not ok:
                print("     код=%s факт: got=%r want=%r"
                      % (r.exit_code, r.stdout[:80], want_fact[:80]))
                print("     b2 %d Б (want %d), peg %d Б (want %d)"
                      % (len(r.files.get("t.b2") or b""),
                         len(lab_bridge.emit_b2(data)[0].encode()),
                         len(r.files.get("t.peg") or b""),
                         len(lab_bridge.emit_peg(data).encode())))
        print("--- (2) порт FF /4 + таблицы (synth4/5/6/7) ---")
        for name, img in synth_images(body):
            ok, r, want_fact = run_case(bexe, img, total)
            tag = "OK" if ok else "FAIL"
            if not ok:
                fails.append(name)
            print("[%s] %-8s шаги %8d  %r" % (tag, name, r.steps,
                                             r.stdout[:64]))
            if not ok:
                print("     код=%s факт: got=%r want=%r"
                      % (r.exit_code, r.stdout[:80], want_fact[:80]))
                want_b2, _st = lab_bridge.emit_b2(img)
                got_b2 = (r.files.get("t.b2") or b"").decode("utf-8",
                                                             "replace")
                want_l = want_b2.splitlines()
                got_l = got_b2.splitlines()
                for i, (w, g) in enumerate(zip(want_l, got_l)):
                    if w != g:
                        print("     строка %d: got=%r want=%r" % (i, g, w))
                        break
                print("     строк: got=%d want=%d"
                      % (len(got_l), len(want_l)))
    finally:
        os.unlink(bexe)
    print("итог: %d провалов, шагов %d" % (len(fails), total[0]))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
