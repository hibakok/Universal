"""probe_e94_4b5.py — зонд E9.4-4b-5 (ПЕРВЫЙ ЧУЖОЙ КРУГ; крафты
корпуса + большой крафт big_image из lab_t_bridge_round):
  (1) КРУГ ИНСТРУМЕНТАМИ под эмулятором lab_run — чужой EXE ->
      bridge.exe -> t.b2 + t.peg -> enc.exe -> t.brick -> brick.exe
      -> t.bin -> pegen.exe -> t.exe == образу БАЙТ-В-БАЙТ; шаги
      каждого инструмента; большой крафт — масштаб реальных EXE
      (0x30400 Б = 75% outbuf pegen v2; тело 0x7FFE; 3 патча !sec;
      импортов нет — класс E9.4-4b-2);
  (2) ОРАКУЛ большого крафта (parse_foreign + emit_b2_foreign +
      emit_peg_v2 + enc+brick + wrap2) == образ — «сначала истина
      семантики»; факт-строка моста == оракулу (K.foreign_line);
  (3) ГРАНИЦЫ ПРЕДЕЛОВ (снятие — E9.5): образ >= 256 КиБ —
      bridge.exe ERR=BIG EXE (7) без частичных выходов; тело
      > 128 КиБ (longbody_image) — brick.exe ERR=BIG OUT (10)
      без t.bin.

Выход: таблица [OK]/[FAIL] + сводка шагов эмуляции.
Запуск: python3 LAB/ai/probe_e94_4b5.py  (из корня репозитория)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_bridge                        # noqa: E402
import lab_brick                         # noqa: E402
import lab_enc                           # noqa: E402
import lab_pegen                         # noqa: E402
import lab_run                           # noqa: E402
import lab_t_bridge_corpus as K          # noqa: E402
from lab_t_bridge_round import (         # noqa: E402
    big_image, longbody_image)

OK = []


def check(name, is_ok, note=""):
    OK.append(is_ok)
    print("[%s] %s %s" % ("OK" if is_ok else "FAIL", name, note))


def main():
    root = os.path.dirname(os.path.dirname(HERE))
    bexe = os.path.join(root, "KERNEL", "L5-BRIDGE", "bridge.exe")
    enc_exe = os.path.join(root, "KERNEL", "L1-ENC", "enc.exe")
    brick_exe = os.path.join(root, "KERNEL", "L1-BRICK", "brick.exe")
    pegen_exe = os.path.join(root, "KERNEL", "L0-PEGEN", "pegen.exe")

    # (1) круг инструментами: 2 крафта корпуса + большой крафт
    for name, img in (("foreign", K.foreign_image()),
                      ("foreign2", K.foreign2_image()),
                      ("big", big_image())):
        steps = []
        r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                           {"in.exe": img})
        steps.append(r.steps)
        ok = r.exit_code == 0
        b2, peg = r.files.get("t.b2", b""), r.files.get("t.peg", b"")
        r1 = lab_run.run_kv(enc_exe, ["t.b2", "t.brick"], {"t.b2": b2})
        steps.append(r1.steps)
        ok = ok and r1.exit_code == 0
        r2 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                            {"t.brick": r1.files.get("t.brick", b"")})
        steps.append(r2.steps)
        ok = ok and r2.exit_code == 0
        tbin = r2.files.get("t.bin", b"")
        r3 = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                            {"t.bin": tbin, "t.peg": peg})
        steps.append(r3.steps)
        made = r3.files.get("t.exe", b"")
        check("круг инструментами: %s (%d Б) == образу"
              % (name, len(img)),
              ok and r3.exit_code == 0 and made == img,
              "шаги bridge+enc+brick+pegen=%s; t.b2=%d Б t.peg=%d Б"
              " t.bin=%d Б t.exe=%d Б"
              % ("+".join(str(s) for s in steps), len(b2), len(peg),
                 len(tbin), len(made)))

    # (2) оракул большого крафта + факт-строка моста == оракулу
    img = big_image()
    f = lab_bridge.parse_foreign(img)
    b2t, _st = lab_bridge.emit_b2_foreign(img)
    pegt = lab_bridge.emit_peg_v2(img)
    body = lab_brick.assemble(lab_enc.normalize(b2t).encode("utf-8"))
    check("оракул big: parse/emit/сборка == образу",
          lab_pegen.wrap2(body, pegt) == img,
          "ins=%d target=%X bss=%X; тело %d Б; t.peg %d Б"
          % (len(f["ins"]), f["target"], f["bss"], len(body),
             len(pegt)))
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                       {"in.exe": img})
    check("мост big: факт-строка + t.b2 + t.peg == оракулу",
          r.exit_code == 0 and r.stdout == K.foreign_line(img)
          and r.files.get("t.b2") == b2t.encode("utf-8")
          and r.files.get("t.peg") == pegt.encode("utf-8"),
          r.stdout.decode("latin1").strip()[:96])

    # (3) границы пределов (снятие — E9.5)
    img = big_image(rdata_raw=0x38800)      # файл 0x41000 >= 256 КиБ
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                       {"in.exe": img})
    check("граница bridge: образ 0x41000 — ERR=BIG EXE (7),"
          " без частичных выходов",
          r.exit_code == 7 and r.stdout == b"U-L5-BRIDGE ERR=BIG"
          b" EXE\r\n" and "t.b2" not in r.files
          and "t.peg" not in r.files,
          "шагов=%d; файлы=%r" % (r.steps, sorted(r.files)))
    img = longbody_image()                   # тело 0x20400 > 128 КиБ
    r = lab_run.run_kv(bexe, ["in.exe", "t.b2", "t.peg"],
                       {"in.exe": img})
    b2 = r.files.get("t.b2", b"")
    r1 = lab_run.run_kv(enc_exe, ["t.b2", "t.brick"], {"t.b2": b2})
    r2 = lab_run.run_kv(brick_exe, ["t.brick", "t.bin"],
                        {"t.brick": r1.files.get("t.brick", b"")})
    check("граница brick: тело 0x20400 — ERR=BIG OUT (10), без"
          " t.bin (enc при этом успешен)",
          r.exit_code == 0 and r1.exit_code == 0
          and r2.exit_code == 10
          and r2.stdout == b"U-L1-BRICK ERR=BIG OUT\r\n"
          and "t.bin" not in r2.files,
          "bridge=%d enc=%d brick=%d шагов; t.b2=%d Б"
          % (r.exit_code, r1.exit_code, r2.exit_code, len(b2)))

    n = len(OK)
    print("\nИТОГ ЗОНДА: %d/%d %s" % (n, n, "OK" if n == len(OK)
                                     else "— ПРОВАЛЫ"))
    return 0 if n == len(OK) else 1


if __name__ == "__main__":
    sys.exit(main())
