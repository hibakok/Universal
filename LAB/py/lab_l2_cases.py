"""lab_l2_cases.py — эталоны оракула WALL v1 (SPEC/11).

Вход:  нет (модуль-данные).
Выход: CASES_FULL — (имя, исходник, ПОЛНЫЙ ожидаемый .b2); CASES_FRAG —
       (имя, исходник, обязательный непрерывный фрагмент .b2).
Функция: якоря выписаны ВРУЧНУЮ по правилам SPEC/11 (независимо от
         lab_l2/lab_l2_gen); расхождение оракула с якорем — находка,
         а не повод править якорь. Единая точка правды для тестов
         T-E6-19 (батарея) и будущего wall.exe (E6.4b: обязан совпадать
         байт-в-байт). ERRORS/DEMO/big_source — lab_l2_prog.py.
"""

# Полные якоря: compile_wall(исходник) == ожидаемый текст байт-в-байт.
CASES_FULL = [
    ("A1 минимум: пустая main", """\
func main
end
""", """\
; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 2 строк; функций: 1; ext: 0; str: 0; глобальных var: 0
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
M sub rsp, 30 ; кадр main
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("A2 локаль/присваивание/темпы/глобаль/str/len", """\
var g
str s = 'AB'
func main
    var x
    x = 1 + 2
    g = len(s)
end
""", """\
; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 7 строк; функций: 1; ext: 0; str: 1; глобальных var: 1
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
M sub rsp, 40 ; кадр main
M mov r10, 1 ; x = 1 + 2
M mov [rbp-10], r10 ; x = 1 + 2
M mov r10, 2 ; x = 1 + 2
M mov r11, r10 ; x = 1 + 2
M mov r10, [rbp-10] ; x = 1 + 2
M add r10, r11 ; x = 1 + 2
M mov [rbp-8], r10 ; x = 1 + 2
M mov r10, 2 ; g = len(s)
M mov [rip+$g], r10 ; g = len(s)
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
; --- данные: строки ---
:s
DB 41 42 ; str s = 'AB'
; --- данные: глобальные переменные (нулевые ячейки) ---
:g
DZ 8 ; var g
"""),
    ("A3 if/else и while: метки и обратные переходы", """\
func main
    var a
    a = 5
    if a == 5
        a = 1
    else
        a = 2
    end
    while a > 0
        a = a - 1
    end
end
""", """\
; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 12 строк; функций: 1; ext: 0; str: 0; глобальных var: 0
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
M sub rsp, 40 ; кадр main
M mov r10, 5 ; a = 5
M mov [rbp-8], r10 ; a = 5
M mov r10, [rbp-8] ; if a == 5
M mov [rbp-10], r10 ; if a == 5
M mov r10, 5 ; if a == 5
M mov r11, r10 ; if a == 5
M mov r10, [rbp-10] ; if a == 5
M cmp r10, r11 ; if a == 5
M jne $_if1 ; if a == 5
M mov r10, 1 ; a = 1
M mov [rbp-8], r10 ; a = 1
M jmp $_if1e ; if a == 5
:_if1
M mov r10, 2 ; a = 2
M mov [rbp-8], r10 ; a = 2
:_if1e
:_w2
M mov r10, [rbp-8] ; while a > 0
M mov [rbp-10], r10 ; while a > 0
M mov r10, 0 ; while a > 0
M mov r11, r10 ; while a > 0
M mov r10, [rbp-10] ; while a > 0
M cmp r10, r11 ; while a > 0
M jle $_w2e ; while a > 0
M mov r10, [rbp-8] ; a = a - 1
M mov [rbp-10], r10 ; a = a - 1
M mov r10, 1 ; a = a - 1
M mov r11, r10 ; a = a - 1
M mov r10, [rbp-10] ; a = a - 1
M sub r10, r11 ; a = a - 1
M mov [rbp-8], r10 ; a = a - 1
M jmp $_w2 ; while a > 0
:_w2e
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("A5 ext: импорты, 5-й аргумент, вызов оператором", """\
ext WriteFile
func main
    WriteFile(1, 2, 3, 4, 5)
end
""", """\
; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)
; исходник: 4 строк; функций: 1; ext: 1; str: 0; глобальных var: 0
; --- импорты: фиксированная область 0x200 байт (SPEC/11) ---
:_idt
DD $_intt 0 0 $_dll $_iat ; описатель импорта kernel32
DZ 14 ; терминатор IDT
:_iat
:_iat_writefile
DQ $_hint_writefile
DQ 0 0 0 0 0 0 0 0
:_intt
DQ $_hint_writefile 0 0 0 0 0 0 0 0
:_dll
DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00 ; "kernel32.dll\\0"
DZ 1 ; выравнивание
:_hint_writefile
DB 00 00 57 72 69 74 65 46 69 6C 65 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ; "WriteFile"
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 22 ; свободный слот импорта
DZ 2A ; выравнивание области до 0x200
; --- код ---
:_entry
M sub rsp, 8 ; вход: выравнивание стека для вызова main
M call $main ; вход: вызов main
M int3 ; вход: возврат из main без ExitProcess — ловушка
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 60 ; кадр main
M mov r10, 1 ; WriteFile(1, 2, 3, 4, 5)
M mov [rbp-8], r10 ; WriteFile(1, 2, 3, 4, 5)
M mov r10, 2 ; WriteFile(1, 2, 3, 4, 5)
M mov [rbp-10], r10 ; WriteFile(1, 2, 3, 4, 5)
M mov r10, 3 ; WriteFile(1, 2, 3, 4, 5)
M mov [rbp-18], r10 ; WriteFile(1, 2, 3, 4, 5)
M mov r10, 4 ; WriteFile(1, 2, 3, 4, 5)
M mov [rbp-20], r10 ; WriteFile(1, 2, 3, 4, 5)
M mov r10, 5 ; WriteFile(1, 2, 3, 4, 5)
M mov [rbp-40], r10 ; WriteFile(1, 2, 3, 4, 5)
M mov rcx, [rbp-8] ; WriteFile(1, 2, 3, 4, 5)
M mov rdx, [rbp-10] ; WriteFile(1, 2, 3, 4, 5)
M mov r8, [rbp-18] ; WriteFile(1, 2, 3, 4, 5)
M mov r9, [rbp-20] ; WriteFile(1, 2, 3, 4, 5)
M mov r10, [rbp-40] ; WriteFile(1, 2, 3, 4, 5)
M mov [rsp+20], r10 ; WriteFile(1, 2, 3, 4, 5)
M call [rip+$_iat_writefile] ; WriteFile(1, 2, 3, 4, 5)
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
]

# Фрагментные якоря: выход обязан СОДЕРЖАТЬ фрагмент байт-в-байт.
CASES_FRAG = [
    ("F4 параметры/return/вызов: стейдинг C-слотов", """\
func add2(a, b)
    return a + b
end

func main
    var r
    r = add2(3, 4)
end
""", """\
:add2
M push rbp ; кадр add2
M mov rbp, rsp ; кадр add2
M sub rsp, 50 ; кадр add2
M mov [rbp-8], rcx ; кадр add2
M mov [rbp-10], rdx ; кадр add2
M mov r10, [rbp-8] ; return a + b
M mov [rbp-18], r10 ; return a + b
M mov r10, [rbp-10] ; return a + b
M mov r11, r10 ; return a + b
M mov r10, [rbp-18] ; return a + b
M add r10, r11 ; return a + b
M mov rax, r10 ; return a + b
M mov rsp, rbp ; выход add2
M pop rbp ; выход add2
M ret ; выход add2
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 50 ; кадр main
M mov r10, 3 ; r = add2(3, 4)
M mov [rbp-10], r10 ; r = add2(3, 4)
M mov r10, 4 ; r = add2(3, 4)
M mov [rbp-18], r10 ; r = add2(3, 4)
M mov rcx, [rbp-10] ; r = add2(3, 4)
M mov rdx, [rbp-18] ; r = add2(3, 4)
M call $add2 ; r = add2(3, 4)
M mov r10, rax ; r = add2(3, 4)
M mov [rbp-8], r10 ; r = add2(3, 4)
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("F6 getb/setb: S-слоты и байтовый доступ", """\
str s = 'AB'
var buf
func main
    var c
    c = getb(s, 1)
    setb(&buf, 0, c)
end
""", """\
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 60 ; кадр main
M lea r10, [rip+$s] ; c = getb(s, 1)
M mov [rbp-10], r10 ; c = getb(s, 1)
M mov r10, 1 ; c = getb(s, 1)
M mov r11, r10 ; c = getb(s, 1)
M mov r10, [rbp-10] ; c = getb(s, 1)
M movzx r10d, byte [r10+r11] ; c = getb(s, 1)
M mov [rbp-8], r10 ; c = getb(s, 1)
M lea r10, [rip+$buf] ; setb(&buf, 0, c)
M mov [rbp-18], r10 ; setb(&buf, 0, c)
M mov r10, 0 ; setb(&buf, 0, c)
M mov [rbp-20], r10 ; setb(&buf, 0, c)
M mov r10, [rbp-8] ; setb(&buf, 0, c)
M mov [rbp-28], r10 ; setb(&buf, 0, c)
M mov r10, [rbp-18] ; setb(&buf, 0, c)
M mov r11, [rbp-20] ; setb(&buf, 0, c)
M mov al, [rbp-28] ; setb(&buf, 0, c)
M mov [r10+r11], al ; setb(&buf, 0, c)
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("F7 сдвиги через cl, унарный минус, вложенность T", """\
func main
    var x
    var y
    x = 1 << 2
    y = -x
    x = ((x >> 1) + 1) & 3
end
""", """\
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 60 ; кадр main
M mov r10, 1 ; x = 1 << 2
M mov [rbp-18], r10 ; x = 1 << 2
M mov r10, 2 ; x = 1 << 2
M mov r11, r10 ; x = 1 << 2
M mov r10, [rbp-18] ; x = 1 << 2
M mov rcx, r11 ; x = 1 << 2
M shl r10, cl ; x = 1 << 2
M mov [rbp-8], r10 ; x = 1 << 2
M mov r10, [rbp-8] ; y = -x
M neg r10 ; y = -x
M mov [rbp-10], r10 ; y = -x
M mov r10, [rbp-8] ; x = ((x >> 1) + 1) & 3
M mov [rbp-28], r10 ; x = ((x >> 1) + 1) & 3
M mov r10, 1 ; x = ((x >> 1) + 1) & 3
M mov r11, r10 ; x = ((x >> 1) + 1) & 3
M mov r10, [rbp-28] ; x = ((x >> 1) + 1) & 3
M mov rcx, r11 ; x = ((x >> 1) + 1) & 3
M shr r10, cl ; x = ((x >> 1) + 1) & 3
M mov [rbp-20], r10 ; x = ((x >> 1) + 1) & 3
M mov r10, 1 ; x = ((x >> 1) + 1) & 3
M mov r11, r10 ; x = ((x >> 1) + 1) & 3
M mov r10, [rbp-20] ; x = ((x >> 1) + 1) & 3
M add r10, r11 ; x = ((x >> 1) + 1) & 3
M mov [rbp-18], r10 ; x = ((x >> 1) + 1) & 3
M mov r10, 3 ; x = ((x >> 1) + 1) & 3
M mov r11, r10 ; x = ((x >> 1) + 1) & 3
M mov r10, [rbp-18] ; x = ((x >> 1) + 1) & 3
M and r10, r11 ; x = ((x >> 1) + 1) & 3
M mov [rbp-8], r10 ; x = ((x >> 1) + 1) & 3
"""),
    ("F8 данные: пустая строка и экраны", """\
str e = ''
str n = 'a\\nb\\tc'
func main
end
""", """\
; --- данные: строки ---
:e
DZ 0 ; str e = ''
:n
DB 61 0A 62 09 63 ; str n = 'a\\nb\\tc'
"""),
    ("F9 return без значения, вызов-оператор, порядок функций", """\
func f
    return
end
func main
    f()
end
""", """\
:f
M push rbp ; кадр f
M mov rbp, rsp ; кадр f
M sub rsp, 30 ; кадр f
M mov rsp, rbp ; выход f
M pop rbp ; выход f
M ret ; выход f
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 30 ; кадр main
M call $f ; f()
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
    ("F10 if без else: один джамп на конец", """\
func main
    var a
    if a != 0
        a = 1
    end
end
""", """\
:main
M push rbp ; кадр main
M mov rbp, rsp ; кадр main
M sub rsp, 40 ; кадр main
M mov r10, [rbp-8] ; if a != 0
M mov [rbp-10], r10 ; if a != 0
M mov r10, 0 ; if a != 0
M mov r11, r10 ; if a != 0
M mov r10, [rbp-10] ; if a != 0
M cmp r10, r11 ; if a != 0
M je $_if1e ; if a != 0
M mov r10, 1 ; a = 1
M mov [rbp-8], r10 ; a = 1
:_if1e
M mov rsp, rbp ; выход main
M pop rbp ; выход main
M ret ; выход main
"""),
]
