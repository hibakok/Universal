"""lab_t_wallself_final.py — секция 12b батареи: финал E6.4d (E6.4d-5).

Вход:  колбэк check из lab_verify; skel_path — EXE каркаса (собран
         секцией 12: splice -> wall -> enc -> brick -> pegen);
         пути инструментов enc/brick/pegen.
Выход: проверка T-E6-59 (печать через check).
Функция: шаг 1 финала E6.4d — канарейки круга: шесть демо-программ
         (DEMO_MDM/BC/CC/ARR/WALL2/NEST — те же, что секция 11 гоняет
         инструментом wall.exe в T-E6-42..44/46/47/51) компилируются
         КАРКАСОМ wall.wall: каркас -> .b2 -> enc -> brick -> pegen ->
         эмуляция; эталоны — строки «U-MDM-OK 52» ... «U-NEST-OK 4C».
         Класс: каркас обязан не только совпасть с оракулом байт-в-байт
         (доказано T-E6-49a..58 на 61+3 источниках), но и произвести
         РАБОЧИЙ код: круг до эмуляции ловит ошибки, невидимые на
         уровне текста .b2 (неверный порядок эмитции, битые ссылки
         слотов — их бы поймал brick, но семантика адресов/выравнивания
         проверяется только исполнением). Шаг 2 финала (big_source/
         big_source2 == оракулу каркасом, ~234 млн шагов) — приёмочная
         проверка E6.4d-5:_POLICY «секунда — предел», исполняется
         дев-скриптом LAB/ai/wall_self_canary.py при смене этапа.
Запуск: вызывается из lab_t_wallself.run() (не напрямую).
"""
import os
import tempfile

import lab_l2_arr
import lab_l2_bc
import lab_l2_cc
import lab_l2_mdm
import lab_l2_prog
import lab_run

# (имя, DEMO-исходник, PEG-обёртка, эталонный вывод)
DEMOS = [
    ("mdm", lab_l2_mdm.DEMO_MDM, lab_l2_mdm.DEMO_MDM_PEG,
     b"U-MDM-OK 52\r\n"),
    ("bc", lab_l2_bc.DEMO_BC, lab_l2_bc.DEMO_BC_PEG, b"U-BC-OK 25\r\n"),
    ("cc", lab_l2_cc.DEMO_CC, lab_l2_cc.DEMO_CC_PEG, b"U-CC-OK 31\r\n"),
    ("arr", lab_l2_arr.DEMO_ARR, lab_l2_arr.DEMO_ARR_PEG,
     b"U-ARR-OK 45\r\n"),
    ("wall2", lab_l2_prog.DEMO_WALL2, lab_l2_prog.DEMO_WALL2_PEG,
     b"U-WALL2-OK 85\r\n"),
    ("nest", lab_l2_prog.DEMO_NEST, lab_l2_prog.DEMO_NEST_PEG,
     b"U-NEST-OK 4C\r\n"),
]


def _fw_circle(skel, enc_exe, brick_exe, pegen_exe, demo, peg, want_out):
    """Каркас компилирует DEMO; полный круг до эмуляции. (ok, note)."""
    h = {"d.wall": demo.encode()}
    r1 = lab_run.run_kv(skel, ["d.wall", "d.b2"], h)
    if r1.exit_code != 0:
        return False, "каркас: код=%s out=%r" % (r1.exit_code,
                                                 r1.stdout[:40])
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(enc_exe, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(brick_exe, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = peg.encode()
    r4 = lab_run.run_kv(pegen_exe, ["d.bin", "d.peg", "d.exe"], h)
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


def run(check, skel_path, enc_exe, brick_exe, pegen_exe):
    """T-E6-59: канарейки круга — 6 DEMO КАРКАСОМ до эмуляции."""
    bad = []
    for name, demo, peg, want_out in DEMOS:
        ok, note = _fw_circle(skel_path, enc_exe, brick_exe, pegen_exe,
                              demo, peg, want_out)
        if not ok:
            bad.append("%s (%s)" % (name, note))
    check("T-E6-59 канарейки круга: 6 DEMO каркасом -> эмуляция",
          not bad, "провалы: %s" % "; ".join(bad[:3]) if bad else
          "mdm/bc/cc/arr/wall2/nest OK")
