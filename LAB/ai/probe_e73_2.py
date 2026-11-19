"""probe_e73_2.py — быстрая проверка поведения оракула на F1-случаях.

НЕ часть системы: диагностический скрипт (LAB/ai), проверяет порядок
ошибок _enc_f1 оракула и вид кодировок, чтобы uva.exe среза 2 был
согласован с оракулом до реализации.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
import lab_vm  # noqa: E402

OK = [
    ".mem 8\nmov r1, r2\nhalt 0\n",
    ".mem 8\nmov r0, r15\nhalt 0\n",
    ".mem 8\nadd r1, r2, r3\nhalt 0\n",
    ".mem 8\nsub r15, r15, r14\nhalt 0\n",
    ".mem 8\nmov r1,r2\nadd r3,r1,r2\nhalt 5\n",
    ".mem 8\r\nmov r1, r2\r\nhalt 0\r\n",
    ".mem 8\nmov r1, r2 ; c\nhalt 0\n",
    ".mem 8\nmov r1, r2\nhalt 0",
    ".mem 8\nand r1, r2, r3\nor r4, r5, r6\nxor r7, r8, r9\nhalt 0\n",
    ".mem 8\nshl r1, r2, r3\nshr r4, r5, r6\nlt r7, r8, r9\neq r10, r11, r12\nhalt 0\n",
    ".mem 8\nmov r10, r11\nadd r12, r13, r14\nhalt 0\n",
    ".mem 8\nmov r15, r15\nhalt 0\n",
]
for i, src in enumerate(OK):
    up = lab_vm.assemble(src)
    print("OK %2d %-28r -> %s" % (i, src[:24], up[24:].hex()))
    m, code, dat = lab_vm.parse_up(up)   # 3-кортеж с E7.4-1 (lab_up)
    r = lab_vm.run_up(up)
    print("        код=%d" % r.exit_code)

ERR = [
    ".mem 8\nmov r1\nhalt 0\n",
    ".mem 8\nmov r1, r2, r3\nhalt 0\n",
    ".mem 8\nmov r16, r1\nhalt 0\n",
    ".mem 8\nmov r1, r16\nhalt 0\n",
    ".mem 8\nadd r1, r2\nhalt 0\n",
    ".mem 8\nadd r1, r2, r3, r4\nhalt 0\n",
    ".mem 8\nadd r1, r2, r16\nhalt 0\n",
    ".mem 8\nadd r1, r16, r2\nhalt 0\n",
    ".mem 8\nmov r01, r2\nhalt 0\n",
    ".mem 8\nmov R1, r2\nhalt 0\n",
    ".mem 8\nmov r0x, r1\nhalt 0\n",
    "mov r1, r2\nhalt 0\n",
    ".mem 8\nconst r16, 5\nhalt 0\n",
    ".mem 8\nHALT 0\n",
    ".mem 8\nmov r1, r2\nconst r16, 5\n",
    ".mem 8\nadd r1, r2, 3\nhalt 0\n",
    ".mem 8\nmov r1, +2\nhalt 0\n",
]
for i, src in enumerate(ERR):
    try:
        up = lab_vm.assemble(src)
        print("ERR %2d %-38r -> ПРИНЯТ?! %s" % (i, src[:34], up[24:].hex()))
    except lab_vm.AsmError as e:
        print("ERR %2d %-38r -> строка %d (%s)"
              % (i, src[:34], e.line, e.msg))
    except lab_vm.UpError as e:
        print("ERR %2d %-38r -> UpError %s" % (i, src[:34], e.reason))
