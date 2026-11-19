"""probe_e73_4.py — быстрая проверка поведения оракула на метках и F3.

НЕ часть системы: диагностический скрипт (LAB/ai), проверяет разбор
меток (regex ^([a-z_][a-z0-9_]*):(\\s+(.*))?$), порядок ошибок
(дубликат/неизвестная метка/счёт операндов/регистр) и кодировки
jmp/jnz, чтобы uva.exe среза 4 был согласован с оракулом до
реализации. Снимает вопросы: метка до .mem, метки на одной строке,
запятая после ':' (не \\s — вся строка не метка!), 'jmp r5' (r5 —
ИМЯ метки, не число: неизвестная метка, а не плохое число),
хвостовая метка (pc за концом), прямые/обратные ссылки.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
import lab_vm  # noqa: E402

OK = [
    # прямая ссылка назад
    ".mem 8\nloop:\nadd r1, r1, r2\nlt r3, r1, r4\njnz r3, loop\nhalt 0\n",
    # прямая ссылка вперёд + метка перед инструкцией на строке
    ".mem 8\njmp fwd\nhalt 1\nfwd: halt 2\n",
    # две метки на одной строке (один pc)
    ".mem 8\na: b: halt 5\njmp a\njmp b\n",
    # метка до .mem на одной строке
    "base: .mem 8\nhalt 0\n",
    # хвостовая метка (без инструкции) — pc за концом кода
    ".mem 8\nhalt 3\nend:\n",
    # имя метки = мнемоника; ссылка на неё
    ".mem 8\nadd:\nhalt 0\njmp add\n",
    # имя-регистр как метка
    ".mem 8\nr5:\njmp r5\nhalt 0\n",
    # имя с _ и цифрами
    ".mem 8\n_x1:\njmp _x1\nhalt 0\n",
    # числовые цели: hex, +, u32-максимум, минимумы
    ".mem 8\njmp 0x10\nhalt 0\n",
    ".mem 8\njmp +5\nhalt 0\n",
    ".mem 8\njmp 4294967295\nhalt 0\n",
    ".mem 8\njmp -1\nhalt 0\n",
    ".mem 8\njmp -2147483648\nhalt 0\n",
    # jnz: регистр затем цель; rd = r15
    ".mem 8\njnz r15, 0\nhalt 0\n",
    # ':' затем CR (CR — \s): метка + инструкция на строке
    ".mem 8\na:\rhalt 7\n",
    # после метки только разделители (запятые) — метка без инструкции
    ".mem 8\na: , ,\nhalt 0\n",
    # метка и .mem на строке, метка до первой инструкции
    ".mem 8\nx: const r1, 5\nhalt 0\n",
]
for i, src in enumerate(OK):
    try:
        up = lab_vm.assemble(src)
        print("OK %2d %-40r -> %s" % (i, src[:36], up[24:].hex()))
    except lab_vm.AsmError as e:
        print("OK %2d %-40r -> AsmError line=%d %s"
              % (i, src[:36], e.line, e.msg))
    except lab_vm.UpError as e:
        print("OK %2d %-40r -> UpError %s" % (i, src[:36], e.reason))

ERR = [
    # запятая после ':' — НЕ метка (не \s): неизвестная мнемоника
    (".mem 8\na:,halt 0\n", None),
    # 'a:,' как первый токен
    (".mem 8\na:, b: halt 0\n", None),
    # пробел перед ':' — не метка
    (".mem 8\na : halt 0\n", None),
    # без пробела после ':'
    (".mem 8\na:halt 0\n", None),
    # заглавная метка
    (".mem 8\nA: halt 0\n", None),
    # имя с цифры
    (".mem 8\n1a: halt 0\n", None),
    # пустое имя
    (".mem 8\n: halt 0\n", None),
    # неизвестная метка (jmp)
    (".mem 8\njmp nowhere\nhalt 0\n", None),
    # r5 как цель БЕЗ объявления — неизвестная метка (не плохое число!)
    (".mem 8\njmp r5\nhalt 0\n", None),
    # r5 как цель jnz
    (".mem 8\njnz r1, r5\nhalt 0\n", None),
    # дубликат метки — строка ВТОРОГО вхождения
    (".mem 8\nl:\nl:\nhalt 0\n", None),
    # дубликат на одной строке
    (".mem 8\na: a: halt 0\n", None),
    # дубликат РАНЬШЕ плохой мнемоники на строке
    (".mem 8\na:\nhalt 0\na: foo\n", None),
    # счёт операндов jmp/jnz
    (".mem 8\njmp\nhalt 0\n", None),
    (".mem 8\njmp a, b\nhalt 0\n", None),
    (".mem 8\njnz r1\nhalt 0\n", None),
    (".mem 8\njnz r1, a, b\nhalt 0\n", None),
    # плохой регистр jnz (до цели)
    (".mem 8\njnz r19, 5\nhalt 0\n", None),
    (".mem 8\njnz 1, 5\nhalt 0\n", None),
    # цель не имя и не число
    (".mem 8\njmp a+b\nhalt 0\n", None),
    (".mem 8\njmp 1.5\nhalt 0\n", None),
    # число вне imm32
    (".mem 8\njmp 4294967296\nhalt 0\n", None),
    (".mem 8\njmp -2147483649\nhalt 0\n", None),
    (".mem 8\njmp 0x\nhalt 0\n", None),
    # метка без инструкций — CODE0 (UpError), не AsmError
    (".mem 8\nonly:\n", "CODE0"),
    # halt с операндом-меткой — halt принимает ТОЛЬКО число
    (".mem 8\nx:\nhalt x\n", None),
]
for i, (src, kind) in enumerate(ERR):
    try:
        up = lab_vm.assemble(src)
        print("ERR %2d %-40r -> ПРИНЯТ?! %s" % (i, src[:36],
                                                up[24:].hex()[:24]))
    except lab_vm.AsmError as e:
        print("ERR %2d %-40r -> AsmError line=%d %s"
              % (i, src[:36], e.line, e.msg))
    except lab_vm.UpError as e:
        print("ERR %2d %-40r -> UpError %s" % (i, src[:36], e.reason))
