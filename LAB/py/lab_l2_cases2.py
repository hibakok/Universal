"""lab_l2_cases2.py — эталоны оракула WALL v2 (SPEC/11, этап E6.4c).

Вход:  нет (модуль-данные).
Выход: CASES_FULL2 — (имя, исходник, ПОЛНЫЙ ожидаемый .b2); CASES_FRAG2 —
       (имя, исходник, обязательный непрерывный фрагмент .b2).
Функция: якоря НОВЫХ конструкций v2 (массивы var a[n], qword-индексация
         e[i] / e[i] = v, * / %, break/continue, цепочки && / ||),
         выписанные вручную по правилам SPEC/11 v2 — независимо от
         lab_l2/lab_l2_gen; расхождение оракула с якорем — находка, а не
         повод править якорь. Якоря v1 (без новых конструкций) —
         lab_l2_cases.py; инструмент wall.exe (E6.4b, v1) сверяется
         батареей только с ними (T-E6-26) — эти списки НЕ подставляются
         инструменту до его обновления (E6.4c-3).
Вывод раскладок (проверено вручную): B1 — базовые слоты a[0..2]+x = 4,
         T1..T3 (maxd 3), S0..S2; framesize 0x80. B2 — i,s + T1; 0x50.
"""

# Полные якоря: compile_wall(исходник) == ожидаемый текст байт-в-байт.
CASES_FULL2 = [
    ("B1 массив + astore/index + * / %", """\
func main
    var a[3]
    var x
    a[0] = 10
    a[1] = a[0] * 3
    a[2] = a[1] / 4 % 3
    x = a[2]
end
""", """\
; UNIVERSAL / WALL v2 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 8 строк; функций: 1; ext: 0; str: 0; глобальных var: 0
; --- импорты: фиксированная область 0x200 байт (SPEC/11) ---
:_idt
DD 0 0 0 0 0 ; без импортов
DZ 14 ; терминатор IDT
:_iat
DQ 0 0 0 0 0 0 0 0 0
:_intt
DQ 0 0 0 0 0 0 0 0 0
DZ 148 ; без импортов: выравнивание области до 0x200
; --- код ---
:_entry
M sub rsp, 8 ; вход: выравнивание стека для вызова main
M call $main ; вход: вызов main
M int3 ; вход: возврат из main без ExitProcess — ловушка
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 80 ; кадр main
M lea r10, [rbp-18] ; a[0] = 10
M mov [rbp-40], r10 ; a[0] = 10
M mov r10, 0 ; a[0] = 10
M mov [rbp-48], r10 ; a[0] = 10
M mov r10, A ; a[0] = 10
M mov [rbp-50], r10 ; a[0] = 10
M mov r10, [rbp-40] ; a[0] = 10
M mov r11, [rbp-48] ; a[0] = 10
M shl r11, 3 ; a[0] = 10
M add r10, r11 ; a[0] = 10
M mov r11, [rbp-50] ; a[0] = 10
M mov [r10], r11 ; a[0] = 10
M lea r10, [rbp-18] ; a[1] = a[0] * 3
M mov [rbp-40], r10 ; a[1] = a[0] * 3
M mov r10, 1 ; a[1] = a[0] * 3
M mov [rbp-48], r10 ; a[1] = a[0] * 3
M lea r10, [rbp-18] ; a[1] = a[0] * 3
M mov [rbp-30], r10 ; a[1] = a[0] * 3
M mov r10, 0 ; a[1] = a[0] * 3
M shl r10, 3 ; a[1] = a[0] * 3
M mov r11, r10 ; a[1] = a[0] * 3
M mov r10, [rbp-30] ; a[1] = a[0] * 3
M add r10, r11 ; a[1] = a[0] * 3
M mov r10, [r10] ; a[1] = a[0] * 3
M mov [rbp-28], r10 ; a[1] = a[0] * 3
M mov r10, 3 ; a[1] = a[0] * 3
M mov r11, r10 ; a[1] = a[0] * 3
M mov r10, [rbp-28] ; a[1] = a[0] * 3
M imul r10, r11 ; a[1] = a[0] * 3
M mov [rbp-50], r10 ; a[1] = a[0] * 3
M mov r10, [rbp-40] ; a[1] = a[0] * 3
M mov r11, [rbp-48] ; a[1] = a[0] * 3
M shl r11, 3 ; a[1] = a[0] * 3
M add r10, r11 ; a[1] = a[0] * 3
M mov r11, [rbp-50] ; a[1] = a[0] * 3
M mov [r10], r11 ; a[1] = a[0] * 3
M lea r10, [rbp-18] ; a[2] = a[1] / 4 % 3
M mov [rbp-40], r10 ; a[2] = a[1] / 4 % 3
M mov r10, 2 ; a[2] = a[1] / 4 % 3
M mov [rbp-48], r10 ; a[2] = a[1] / 4 % 3
M lea r10, [rbp-18] ; a[2] = a[1] / 4 % 3
M mov [rbp-38], r10 ; a[2] = a[1] / 4 % 3
M mov r10, 1 ; a[2] = a[1] / 4 % 3
M shl r10, 3 ; a[2] = a[1] / 4 % 3
M mov r11, r10 ; a[2] = a[1] / 4 % 3
M mov r10, [rbp-38] ; a[2] = a[1] / 4 % 3
M add r10, r11 ; a[2] = a[1] / 4 % 3
M mov r10, [r10] ; a[2] = a[1] / 4 % 3
M mov [rbp-30], r10 ; a[2] = a[1] / 4 % 3
M mov r10, 4 ; a[2] = a[1] / 4 % 3
M mov r11, r10 ; a[2] = a[1] / 4 % 3
M mov r10, [rbp-30] ; a[2] = a[1] / 4 % 3
M mov rax, r10 ; a[2] = a[1] / 4 % 3
M cqo ; a[2] = a[1] / 4 % 3
M idiv r11 ; a[2] = a[1] / 4 % 3
M mov r10, rax ; a[2] = a[1] / 4 % 3
M mov [rbp-28], r10 ; a[2] = a[1] / 4 % 3
M mov r10, 3 ; a[2] = a[1] / 4 % 3
M mov r11, r10 ; a[2] = a[1] / 4 % 3
M mov r10, [rbp-28] ; a[2] = a[1] / 4 % 3
M mov rax, r10 ; a[2] = a[1] / 4 % 3
M cqo ; a[2] = a[1] / 4 % 3
M idiv r11 ; a[2] = a[1] / 4 % 3
M mov r10, rdx ; a[2] = a[1] / 4 % 3
M mov [rbp-50], r10 ; a[2] = a[1] / 4 % 3
M mov r10, [rbp-40] ; a[2] = a[1] / 4 % 3
M mov r11, [rbp-48] ; a[2] = a[1] / 4 % 3
M shl r11, 3 ; a[2] = a[1] / 4 % 3
M add r10, r11 ; a[2] = a[1] / 4 % 3
M mov r11, [rbp-50] ; a[2] = a[1] / 4 % 3
M mov [r10], r11 ; a[2] = a[1] / 4 % 3
M lea r10, [rbp-18] ; x = a[2]
M mov [rbp-28], r10 ; x = a[2]
M mov r10, 2 ; x = a[2]
M shl r10, 3 ; x = a[2]
M mov r11, r10 ; x = a[2]
M mov r10, [rbp-28] ; x = a[2]
M add r10, r11 ; x = a[2]
M mov r10, [r10] ; x = a[2]
M mov [rbp-20], r10 ; x = a[2]
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("B2 break/continue и цепочки && / ||", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 6 && s < 100
        i = i + 1
        if i == 3
            continue
        end
        if i == 5 || s == 999
            break
        end
        s = s + i
    end
end
""", """\
; UNIVERSAL / WALL v2 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 16 строк; функций: 1; ext: 0; str: 0; глобальных var: 0
; --- импорты: фиксированная область 0x200 байт (SPEC/11) ---
:_idt
DD 0 0 0 0 0 ; без импортов
DZ 14 ; терминатор IDT
:_iat
DQ 0 0 0 0 0 0 0 0 0
:_intt
DQ 0 0 0 0 0 0 0 0 0
DZ 148 ; без импортов: выравнивание области до 0x200
; --- код ---
:_entry
M sub rsp, 8 ; вход: выравнивание стека для вызова main
M call $main ; вход: вызов main
M int3 ; вход: возврат из main без ExitProcess — ловушка
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 50 ; кадр main
M mov r10, 0 ; i = 0
M mov [rbp-8], r10 ; i = 0
M mov r10, 0 ; s = 0
M mov [rbp-10], r10 ; s = 0
:_w1
M mov r10, [rbp-8] ; while i < 6 && s < 100
M mov [rbp-18], r10 ; while i < 6 && s < 100
M mov r10, 6 ; while i < 6 && s < 100
M mov r11, r10 ; while i < 6 && s < 100
M mov r10, [rbp-18] ; while i < 6 && s < 100
M cmp r10, r11 ; while i < 6 && s < 100
M jge $_w1e ; while i < 6 && s < 100
M mov r10, [rbp-10] ; while i < 6 && s < 100
M mov [rbp-18], r10 ; while i < 6 && s < 100
M mov r10, 64 ; while i < 6 && s < 100
M mov r11, r10 ; while i < 6 && s < 100
M mov r10, [rbp-18] ; while i < 6 && s < 100
M cmp r10, r11 ; while i < 6 && s < 100
M jge $_w1e ; while i < 6 && s < 100
M mov r10, [rbp-8] ; i = i + 1
M mov [rbp-18], r10 ; i = i + 1
M mov r10, 1 ; i = i + 1
M mov r11, r10 ; i = i + 1
M mov r10, [rbp-18] ; i = i + 1
M add r10, r11 ; i = i + 1
M mov [rbp-8], r10 ; i = i + 1
M mov r10, [rbp-8] ; if i == 3
M mov [rbp-18], r10 ; if i == 3
M mov r10, 3 ; if i == 3
M mov r11, r10 ; if i == 3
M mov r10, [rbp-18] ; if i == 3
M cmp r10, r11 ; if i == 3
M jne $_if2e ; if i == 3
M jmp $_w1 ; continue
:_if2e
M mov r10, [rbp-8] ; if i == 5 || s == 999
M mov [rbp-18], r10 ; if i == 5 || s == 999
M mov r10, 5 ; if i == 5 || s == 999
M mov r11, r10 ; if i == 5 || s == 999
M mov r10, [rbp-18] ; if i == 5 || s == 999
M cmp r10, r11 ; if i == 5 || s == 999
M jne $_if3d2 ; if i == 5 || s == 999
M jmp $_if3t ; if i == 5 || s == 999
:_if3d2
M mov r10, [rbp-10] ; if i == 5 || s == 999
M mov [rbp-18], r10 ; if i == 5 || s == 999
M mov r10, 3E7 ; if i == 5 || s == 999
M mov r11, r10 ; if i == 5 || s == 999
M mov r10, [rbp-18] ; if i == 5 || s == 999
M cmp r10, r11 ; if i == 5 || s == 999
M jne $_if3e ; if i == 5 || s == 999
:_if3t
M jmp $_w1e ; break
:_if3e
M mov r10, [rbp-10] ; s = s + i
M mov [rbp-18], r10 ; s = s + i
M mov r10, [rbp-8] ; s = s + i
M mov r11, r10 ; s = s + i
M mov r10, [rbp-18] ; s = s + i
M add r10, r11 ; s = s + i
M mov [rbp-10], r10 ; s = s + i
M jmp $_w1 ; while i < 6 && s < 100
:_w1e
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
]

# Фрагментные якоря: выход обязан СОДЕРЖАТЬ фрагмент байт-в-байт.
CASES_FRAG2 = [
    ("F11 глобальный массив: len и rip-адрес базы", """\
var g[5]
func main
    var n
    n = len(g)
    g[0] = 7
end
""", """\
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 50 ; кадр main
M mov r10, 5 ; n = len(g)
M mov [rbp-8], r10 ; n = len(g)
M lea r10, [rip+$g] ; g[0] = 7
M mov [rbp-10], r10 ; g[0] = 7
M mov r10, 0 ; g[0] = 7
M mov [rbp-18], r10 ; g[0] = 7
M mov r10, 7 ; g[0] = 7
M mov [rbp-20], r10 ; g[0] = 7
M mov r10, [rbp-10] ; g[0] = 7
M mov r11, [rbp-18] ; g[0] = 7
M shl r11, 3 ; g[0] = 7
M add r10, r11 ; g[0] = 7
M mov r11, [rbp-20] ; g[0] = 7
M mov [r10], r11 ; g[0] = 7
"""),
    ("F11d данные: глобальный массив DZ 8n", """\
var g[5]
func main
    var n
    n = len(g)
    g[0] = 7
end
""", """\
; --- данные: глобальные переменные (нулевые ячейки) ---
:g
DZ 28 ; var g[5]
"""),
    ("F12 указатель в переменной: p = &buf; p[1] = 42", """\
var buf
func main
    var p
    p = &buf
    p[1] = 42
end
""", """\
M mov r10, [rbp-8] ; p[1] = 42
M mov [rbp-10], r10 ; p[1] = 42
M mov r10, 1 ; p[1] = 42
M mov [rbp-18], r10 ; p[1] = 42
M mov r10, 2A ; p[1] = 42
M mov [rbp-20], r10 ; p[1] = 42
M mov r10, [rbp-10] ; p[1] = 42
M mov r11, [rbp-18] ; p[1] = 42
M shl r11, 3 ; p[1] = 42
M add r10, r11 ; p[1] = 42
M mov r11, [rbp-20] ; p[1] = 42
M mov [r10], r11 ; p[1] = 42
"""),
    ("F13 приоритет: * выше +, скобки", """\
func main
    var x
    x = 2 * 3 + 4 * 5
    x = 1 + 2 * 3
    x = 2 * (3 + 4)
end
""", """\
M mov r10, 2 ; x = 2 * 3 + 4 * 5
M mov [rbp-18], r10 ; x = 2 * 3 + 4 * 5
M mov r10, 3 ; x = 2 * 3 + 4 * 5
M mov r11, r10 ; x = 2 * 3 + 4 * 5
M mov r10, [rbp-18] ; x = 2 * 3 + 4 * 5
M imul r10, r11 ; x = 2 * 3 + 4 * 5
M mov [rbp-10], r10 ; x = 2 * 3 + 4 * 5
M mov r10, 4 ; x = 2 * 3 + 4 * 5
M mov [rbp-18], r10 ; x = 2 * 3 + 4 * 5
M mov r10, 5 ; x = 2 * 3 + 4 * 5
M mov r11, r10 ; x = 2 * 3 + 4 * 5
M mov r10, [rbp-18] ; x = 2 * 3 + 4 * 5
M imul r10, r11 ; x = 2 * 3 + 4 * 5
M mov r11, r10 ; x = 2 * 3 + 4 * 5
M mov r10, [rbp-10] ; x = 2 * 3 + 4 * 5
M add r10, r11 ; x = 2 * 3 + 4 * 5
M mov [rbp-8], r10 ; x = 2 * 3 + 4 * 5
M mov r10, 1 ; x = 1 + 2 * 3
M mov [rbp-10], r10 ; x = 1 + 2 * 3
M mov r10, 2 ; x = 1 + 2 * 3
M mov [rbp-18], r10 ; x = 1 + 2 * 3
M mov r10, 3 ; x = 1 + 2 * 3
M mov r11, r10 ; x = 1 + 2 * 3
M mov r10, [rbp-18] ; x = 1 + 2 * 3
M imul r10, r11 ; x = 1 + 2 * 3
M mov r11, r10 ; x = 1 + 2 * 3
M mov r10, [rbp-10] ; x = 1 + 2 * 3
M add r10, r11 ; x = 1 + 2 * 3
M mov [rbp-8], r10 ; x = 1 + 2 * 3
M mov r10, 2 ; x = 2 * (3 + 4)
M mov [rbp-10], r10 ; x = 2 * (3 + 4)
M mov r10, 3 ; x = 2 * (3 + 4)
M mov [rbp-18], r10 ; x = 2 * (3 + 4)
M mov r10, 4 ; x = 2 * (3 + 4)
M mov r11, r10 ; x = 2 * (3 + 4)
M mov r10, [rbp-18] ; x = 2 * (3 + 4)
M add r10, r11 ; x = 2 * (3 + 4)
M mov r11, r10 ; x = 2 * (3 + 4)
M mov r10, [rbp-10] ; x = 2 * (3 + 4)
M imul r10, r11 ; x = 2 * (3 + 4)
M mov [rbp-8], r10 ; x = 2 * (3 + 4)
"""),
    ("F14 while с ||: метки _wd2/_wt", """\
func main
    var i
    i = 0
    while i < 3 || i > 100
        i = i + 1
    end
end
""", """\
:_w1
M mov r10, [rbp-8] ; while i < 3 || i > 100
M mov [rbp-10], r10 ; while i < 3 || i > 100
M mov r10, 3 ; while i < 3 || i > 100
M mov r11, r10 ; while i < 3 || i > 100
M mov r10, [rbp-10] ; while i < 3 || i > 100
M cmp r10, r11 ; while i < 3 || i > 100
M jge $_w1d2 ; while i < 3 || i > 100
M jmp $_w1t ; while i < 3 || i > 100
:_w1d2
M mov r10, [rbp-8] ; while i < 3 || i > 100
M mov [rbp-10], r10 ; while i < 3 || i > 100
M mov r10, 64 ; while i < 3 || i > 100
M mov r11, r10 ; while i < 3 || i > 100
M mov r10, [rbp-10] ; while i < 3 || i > 100
M cmp r10, r11 ; while i < 3 || i > 100
M jle $_w1e ; while i < 3 || i > 100
:_w1t
"""),
    ("F15 цепочка индексов: p[0][1] = 5", """\
func main
    var p
    p[0][1] = 5
end
""", """\
M mov r10, [rbp-8] ; p[0][1] = 5
M mov [rbp-10], r10 ; p[0][1] = 5
M mov r10, 0 ; p[0][1] = 5
M shl r10, 3 ; p[0][1] = 5
M mov r11, r10 ; p[0][1] = 5
M mov r10, [rbp-10] ; p[0][1] = 5
M add r10, r11 ; p[0][1] = 5
M mov r10, [r10] ; p[0][1] = 5
M mov [rbp-18], r10 ; p[0][1] = 5
M mov r10, 1 ; p[0][1] = 5
M mov [rbp-20], r10 ; p[0][1] = 5
M mov r10, 5 ; p[0][1] = 5
M mov [rbp-28], r10 ; p[0][1] = 5
M mov r10, [rbp-18] ; p[0][1] = 5
M mov r11, [rbp-20] ; p[0][1] = 5
M shl r11, 3 ; p[0][1] = 5
M add r10, r11 ; p[0][1] = 5
M mov r11, [rbp-28] ; p[0][1] = 5
M mov [r10], r11 ; p[0][1] = 5
"""),
    ("F16 смешанное условие: a || b && c (&& сильнее)", """\
func main
    var x
    if x == 1 || x == 2 && x == 3
        x = 0
    end
end
""", """\
M mov r10, [rbp-8] ; if x == 1 || x == 2 && x == 3
M mov [rbp-10], r10 ; if x == 1 || x == 2 && x == 3
M mov r10, 1 ; if x == 1 || x == 2 && x == 3
M mov r11, r10 ; if x == 1 || x == 2 && x == 3
M mov r10, [rbp-10] ; if x == 1 || x == 2 && x == 3
M cmp r10, r11 ; if x == 1 || x == 2 && x == 3
M jne $_if1d2 ; if x == 1 || x == 2 && x == 3
M jmp $_if1t ; if x == 1 || x == 2 && x == 3
:_if1d2
M mov r10, [rbp-8] ; if x == 1 || x == 2 && x == 3
M mov [rbp-10], r10 ; if x == 1 || x == 2 && x == 3
M mov r10, 2 ; if x == 1 || x == 2 && x == 3
M mov r11, r10 ; if x == 1 || x == 2 && x == 3
M mov r10, [rbp-10] ; if x == 1 || x == 2 && x == 3
M cmp r10, r11 ; if x == 1 || x == 2 && x == 3
M jne $_if1e ; if x == 1 || x == 2 && x == 3
M mov r10, [rbp-8] ; if x == 1 || x == 2 && x == 3
M mov [rbp-10], r10 ; if x == 1 || x == 2 && x == 3
M mov r10, 3 ; if x == 1 || x == 2 && x == 3
M mov r11, r10 ; if x == 1 || x == 2 && x == 3
M mov r10, [rbp-10] ; if x == 1 || x == 2 && x == 3
M cmp r10, r11 ; if x == 1 || x == 2 && x == 3
M jne $_if1e ; if x == 1 || x == 2 && x == 3
:_if1t
"""),
]
