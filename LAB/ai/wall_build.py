"""wall_build.py — сборка KERNEL/L2-WALL/wall.exe через эмулированный конвейер (LAB/ai).

Вход:  репозиторий Universal (текущая копия).
Выход: wall.brick, wall-body.bin, wall.peg, wall.exe в KERNEL/L2-WALL/.
Функция: sandbox-инструмент разработчика: splice (оракул) -> enc.exe ->
         brick.exe -> pegen.exe (все — эмуляция LAB); поиск RVA :idt в теле;
         генерация wall.peg; сверка с оракулами на каждом шаге.
"""
import os
import sys

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))

import lab_brick          # noqa: E402
import lab_enc            # noqa: E402
import lab_pe             # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402
import lab_splice         # noqa: E402

K = os.path.join(UNI, "KERNEL", "L2-WALL")


def run_tool(exe, args, files):
    r = lab_run.run_kv(os.path.join(UNI, "KERNEL", exe), args, files)
    return r


def main():
    # 1) splice: wall.b2 -> плоский текст (оракул + инструмент)
    host = {}
    for root, _d, fs in os.walk(os.path.join(UNI, "KERNEL")):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, os.path.join(UNI, "KERNEL"))
            rel = rel.replace(os.sep, "/").lower()
            host[rel] = open(p, "rb").read()
    flat_oracle = lab_splice.splice("l2-wall/wall.b2", host)
    r = run_tool("L1-SPLICE/splice.exe", ["l2-wall/wall.b2", "t_flat.b2"], host)
    assert r.exit_code == 0, "splice.exe упал: %r" % r.stdout
    flat = r.files.get("t_flat.b2", b"")
    assert flat == flat_oracle, \
        "splice.exe != оракул (%d vs %d байт)" % (len(flat),
                                                  len(flat_oracle))
    print("splice OK: %d строк" % flat.count(b"\n"))

    # 2) enc: плоский .b2 -> .brick (реальный инструмент; оракул lab_enc
    #    режет строки по NEL/VT (quirk splitlines) и расходится на UTF-8
    #    букве «х» (D1 85) в комментариях — enc.exe прав по SPEC/09)
    r = run_tool("L1-ENC/enc.exe", ["t.b2", "t.brick"], {"t.b2": flat})
    assert r.exit_code == 0, "enc.exe упал: %r" % r.stdout
    brick_txt = r.files.get("t.brick", b"")
    print("enc OK: %d байт .brick" % len(brick_txt))

    # 3) brick: .brick -> тело (реальный инструмент + оракул)
    r = run_tool("L1-BRICK/brick.exe", ["t.brick", "t.bin"],
                 {"t.brick": brick_txt})
    assert r.exit_code == 0, "brick.exe упал: %r" % r.stdout
    body = r.files.get("t.bin", b"")
    oracle_body = lab_brick.assemble(brick_txt)
    assert body == oracle_body, "brick.exe != оракул"
    print("brick OK: тело %d байт, шагов %d" % (len(body), r.steps))

    # 4) RVA :idt: точная метка из карты brick (E6.4c-3/4b: прежний
    #    побайтовый поиск по структуре описателя дал ЛОЖНОЕ совпадение
    #    внутри strtab2 — новые смещения строк случайно удовлетворили
    #    шаблон, idata уехал на 0x17 раньше; метка надёжна всегда)
    sys.path.insert(0, os.path.join(UNI, "LAB", "ai"))
    import label_map            # noqa: E402
    import io, contextlib       # noqa: E402
    with contextlib.redirect_stdout(io.StringIO()):
        lbl = label_map.labels_of(brick_txt)
    idt = lbl["idt"]                 # смещение в теле; RVA = +0x1000
    idata = 0x1000 + idt
    print("idt RVA: %X (idata %X, iat %X)" % (idata, idata, idata + 0x28))

    # 5) bss: сумма DBZ из плоского текста
    bss = 0
    for ln in flat.decode("latin1").splitlines():
        if ln.startswith("DBZ "):
            bss += int(ln.split()[1], 16)
    print("bss: 0x%X" % bss)

    # 6) wall.peg
    peg = ("; UNIVERSAL / PEG v1 / слой L2 / модуль M2-WALL\n"
           "; Управляющий файл обёртки: pegen.exe <image.bin> <ctrl.peg> "
           "<out.exe>\n"
           "!module wall\n"
           "!entry 1000\n"
           "!idata %X 28\n"
           "!iat %X 40\n"
           "!bss %X\n"
           "!stackcom 4000\n"
           "!heapcom 4000\n") % (idata, idata + 0x28, bss)
    open(os.path.join(K, "wall.peg"), "w", newline="\n").write(peg)

    # 7) pegen: тело + peg -> exe (реальный инструмент + оракул)
    r = run_tool("L0-PEGEN/pegen.exe", ["t.bin", "p.peg", "t.exe"],
                 {"t.bin": body, "p.peg": peg.encode()})
    assert r.exit_code == 0, "pegen.exe упал: %r" % r.stdout
    exe = r.files.get("t.exe", b"")
    oracle_exe = lab_pegen.wrap(body, peg)
    assert exe == oracle_exe, "pegen.exe != оракул"
    pe = lab_pe.load_bytes(exe) if hasattr(lab_pe, "load_bytes") else None
    print("pegen OK: %d байт EXE" % len(exe))

    # 8) сохранение артефактов
    open(os.path.join(K, "wall.brick"), "wb").write(brick_txt)
    open(os.path.join(K, "wall.exe"), "wb").write(exe)
    print("сохранено: wall.brick, wall.peg, wall.exe")
    return exe


if __name__ == "__main__":
    main()
