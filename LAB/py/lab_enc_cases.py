"""lab_enc_cases.py — сценарии проверки оракула ENC (SPEC/09).

Вход:  нет (модуль-данные).
Выход: CASES — якорные пары (M-строка, H-строка), байты сверены с
       реестром SPEC/05 и реальными H-строками brick.brick; ERRORS —
       M-строки, которые обязаны отвергаться; DEMO_B2/DEMO_PEG —
       мини-программа полного круга v2 -> v1 -> тело -> EXE -> эмуляция.
Функция: эталоны батареи t_enc() в lab_verify.py; единая точка правды
         для будущих тестов T-M7-* инструмента enc.exe (этап E6.2):
         оракул и инструмент обязаны давать эти же результаты.
"""

# (M-строка; ожидаемая H-строка). Отклонения от исторических листингов
# (короткие опкоды, REX.W на 32-бит) оговорены в SPEC/09.
CASES = [
    # --- реальный код brick.brick (байты совпадают) ---
    ("M sub rsp, 38", "H 48 83 EC 38"),
    ("M lea rbx,[rip+$base]", "H 48 8D 1D $base"),
    ("M mov rcx, -B", "H 48 C7 C1 F5 FF FF FF"),
    ("M call [rip+$iat_gsh]", "H FF 15 $iat_gsh"),
    ("M mov [rip+$hstdout], rax", "H 48 89 05 $hstdout"),
    ("M mov rdi, rax", "H 48 89 C7"),
    ("M movzx eax, byte [rdi]", "H 0F B6 07"),
    ("M test al, al", "H 84 C0"),
    ("M jnz $sa_unq:1", "H 75 $sa_unq:1"),
    ("M inc rdi", "H 48 FF C7"),
    ("M dec ecx", "H FF C9"),
    ("M mov ecx, 0", "H B9 00 00 00 00"),
    ("M mov r8d, 20000", "H 41 B8 00 00 02 00"),
    ("M mov dword [r9+8], 4", "H 41 C7 41 08 04 00 00 00"),
    ("M mov dword [r9+C], -1000", "H 41 C7 41 0C 00 F0 FF FF"),
    ("M mov rcx, r12", "H 4C 89 E1"),
    ("M mov r8d, [rip+$outlen]", "H 44 8B 05 $outlen"),
    ("M cmp rax, [rip+$outlen]", "H 48 3B 05 $outlen"),
    ("M movzx rdx, byte [r8+rdx]", "H 41 0F B6 14 10"),
    ("M push r8", "H 41 50"),
    ("M pop r11", "H 41 5B"),
    ("M jle $ph_lo:1", "H 7E $ph_lo:1"),
    ("M jge $ph_ok:1", "H 7D $ph_ok:1"),
    ("M jmp $sa_start", "H E9 $sa_start"),
    ("M ret", "H C3"),
    ("M int3", "H CC"),
    # --- реестр SPEC/05, расширения E1–E4 ---
    ("M mov rdx, [r11]", "H 49 8B 13"),
    ("M mov r8, [r11]", "H 4D 8B 03"),
    ("M mov rdx, [r11+8]", "H 49 8B 53 08"),
    ("M mov [r10], dl", "H 41 88 12"),
    ("M mov [rdx], eax", "H 89 02"),
    ("M mov dl, [rsi]", "H 8A 16"),
    ("M movzx eax, dl", "H 0F B6 C2"),
    ("M movzx eax, word [rsi+rdx]", "H 0F B7 04 16"),
    ("M mov r8d, [rdx+8]", "H 44 8B 42 08"),
    ("M lea rsi, [rsi+r10]", "H 4A 8D 34 16"),
    ("M lea eax, [rax+rcx-1]", "H 8D 44 08 FF"),
    ("M neg ecx", "H F7 D9"),
    ("M shl eax, cl", "H D3 E0"),
    ("M shl r8d, 2", "H 41 C1 E0 02"),
    ("M rol al, 4", "H C0 C0 04"),
    ("M add r11, 8", "H 49 83 C3 08"),
    ("M add r8, 10", "H 49 83 C0 10"),
    ("M sub r14, r13", "H 4D 29 EE"),
    ("M cmp rsi, rdi", "H 48 39 FE"),
    ("M cmp r12d, 10000", "H 41 81 FC 00 00 01 00"),
    ("M cmp rax, 10000", "H 48 81 F8 00 00 01 00"),
    ("M cmp edx, 80", "H 81 FA 80 00 00 00"),
    ("M cmp byte [rsi], 20", "H 80 3E 20"),
    ("M cmp qword [r11+8], 0", "H 49 83 7B 08 00"),
    ("M mov byte [rcx], 0", "H C6 01 00"),
    ("M and r11d, 0F", "H 41 83 E3 0F"),
    ("M or eax, 1", "H 83 C8 01"),
    ("M test r8d, r8d", "H 45 85 C0"),
    ("M test rax, rax", "H 48 85 C0"),
    ("M inc r8d", "H 41 FF C0"),
    ("M inc r12d", "H 41 FF C4"),
    ("M mov r13d, r12d", "H 45 89 E5"),
    ("M cmp r12d, r13d", "H 45 39 EC"),
    ("M mov eax, r10d", "H 44 89 D0"),
    ("M mov r12d, eax", "H 41 89 C4"),
    ("M mov r13, r8", "H 4D 89 C5"),
    ("M mov rax, r9", "H 4C 89 C8"),
    ("M mov rsi, rdi", "H 48 89 FE"),
    ("M mov eax, [rip+$nread]", "H 8B 05 $nread"),
    ("M mov r8, [rip+$x]", "H 4C 8B 05 $x"),
    ("M mov [rip+$x], r13", "H 4C 89 2D $x"),
    ("M lea r8, [rip+$x]", "H 4C 8D 05 $x"),
    ("M call $x", "H E8 $x"),
    ("M je $x:1", "H 74 $x:1"),
    ("M jne $x", "H 0F 85 $x"),
    ("M jb $x:1", "H 72 $x:1"),
    ("M jae $x:1", "H 73 $x:1"),
    ("M jbe $x:1", "H 76 $x:1"),
    ("M ja $x:1", "H 77 $x:1"),
    ("M jz $x:1", "H 74 $x:1"),
    ("M push rbp", "H 55"),
    ("M cdqe", "H 48 98"),
    # --- канонические формы (отличаются от исторических, SPEC/09) ---
    ("M xor ecx, ecx", "H 31 C9"),
    ("M xor r9d, r9d", "H 45 31 C9"),
    ("M and eax, FFFF", "H 81 E0 FF FF 00 00"),
    ("M cmp al, 22", "H 80 F8 22"),
    ("M mov rax, 1", "H 48 C7 C0 01 00 00 00"),
    ("M mov al, 20", "H B0 20"),
    ("M mov ecx, -1", "H B9 FF FF FF FF"),
    ("M neg rax", "H 48 F7 D8"),
    ("M sar eax, 1", "H C1 F8 01"),
    ("M shr rdx, 3", "H 48 C1 EA 03"),
    ("M add [rsi], dl", "H 00 16"),
    ("M or eax, [rip+$x]", "H 0B 05 $x"),
    ("M add eax, [rip+$bssv]", "H 03 05 $bssv"),
    ("M mov r12, [rsp+8]", "H 4C 8B 64 24 08"),
    ("M mov [rsp+20], rax", "H 48 89 44 24 20"),
    ("M mov dword [rsp+20], 0", "H C7 44 24 20 00 00 00 00"),
    ("M mov [r15+r12], dl", "H 43 88 14 27"),
    ("M movzx ecx, byte [r8+r10]", "H 43 0F B6 0C 10"),
    ("M movzx eax, byte [rsi+r10]", "H 42 0F B6 04 16"),
    ("M lea eax, [rcx-1]", "H 8D 41 FF"),
    ("M jmp $x:1", "H EB $x:1"),
    ("M mov qword [r11+8], 0", "H 49 C7 43 08 00 00 00 00"),
    ("M cmp rbp, 0", "H 48 83 FD 00"),
    ("M add rbp, 0", "H 48 83 C5 00"),
]

# M-строки, которые обязаны отвергаться (ErrError FORMAT AT=...).
ERRORS = [
    "M bogus rax, rax",          # неизвестная мнемоника
    "M mov rax, rax, rax",       # неверное число операндов
    "M mov rax",                 # неверное число операндов
    "M mov rax, $x",             # ссылка вне перехода/памяти
    "M mov rax, [rax+rsp]",      # rsp/r12 как индекс
    "M mov rax, [rip]",          # rip без $ссылки
    "M mov rax, [rip+5]",        # то же (число вместо ссылки)
    "M mov eax, ax",             # 16-битных регистров в v1 нет
    "M mov ah, al",              # ah/dh/ch/bh в v1 нет
    "M mov rax, 1FFFFFFFFF",     # 9 цифр — вне диапазона
    "M mov rcx, 80000000",      # r64 imm вне знакового int32
    "M cmp qword [rip+$x], 0",   # imm при rip: слот не в конце
    "M mov dword [rip+$x], 5",   # то же
    "M movzx ax, byte [rsi]",    # 16-бит приёмник
    "M movzx eax, word ax",      # слово-регистр источника
    "M call $x:1",               # call — только rel32
    "M push eax",                # push — только r64
    "M shl rax, bl",             # сдвиг только по cl
    "M mov rax, [rbx+rcx+rsi]",  # два индекса
    "M mov rax, [rbx+rsi*4]",    # scale в v1 нет
    "M ret rax",                 # у ret нет операндов
]

# Полный круг: мини-программа «U-ENC-OK» целиком на M-строках.
# Раскладка тела (RVA = смещение + 0x1000): импорты в начале —
# фиксированные RVA для .peg; код с 0xA0; файловая длина 0xF0.
DEMO_B2 = """\
; UNIVERSAL / BRICK v2 / демонстрация конвейера ENC (SPEC/09)
; Печатает U-ENC-OK и выходит. Круг: enc -> brick -> pegen -> эмуляция.
:idt
DD $intt 0 0 $dll_name $iat ; описатель импорта kernel32
DZ 14 ; терминатор IDT (нулевая запись)
:iat
:iat_gsh
DQ $hint_gsh ; IAT: GetStdHandle
:iat_wf
DQ $hint_wf ; IAT: WriteFile
:iat_ep
DQ $hint_ep ; IAT: ExitProcess
DQ 0 ; IAT: терминатор
:intt
DQ $hint_gsh $hint_wf $hint_ep 0 ; INT — копия IAT
:dll_name
DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00 ; "kernel32.dll\\0"
DZ 1 ; выравнивание hint-записей на чётные RVA
:hint_gsh
DB 00 00 47 65 74 53 74 64 48 61 6E 64 6C 65 00 ; hint + GetStdHandle
DZ 1 ; выравнивание
:hint_wf
DB 00 00 57 72 69 74 65 46 69 6C 65 00 ; hint + WriteFile
:hint_ep
DB 00 00 45 78 69 74 50 72 6F 63 65 73 73 00 ; hint + ExitProcess
:entry
M sub rsp, 28 ; кадр: тень 0x20 + выравнивание вызова
M mov rcx, -B ; STD_OUTPUT_HANDLE (-11)
M call [rip+$iat_gsh] ; rax = хэндл stdout
M mov rcx, rax ; арг 1: хэндл
M lea rdx,[rip+$msg] ; арг 2: буфер
M mov r8d, A ; арг 3: длина (10)
M lea r9,[rip+$ncnt] ; арг 4: &число записанных
M mov dword [rsp+20], 0 ; арг 5: без перекрытия
M call [rip+$iat_wf] ; WriteFile
M xor ecx, ecx ; код выхода 0
M call [rip+$iat_ep] ; ExitProcess
:msg
DB 55 2D 45 4E 43 2D 4F 4B 0D 0A ; "U-ENC-OK\\r\\n"
:ncnt
DZ 8 ; ячейка «записано байт» (перезаписывается)
"""

DEMO_PEG = """\
; UNIVERSAL / PEG v1 / демонстрация ENC (полный круг батареи)
!module encdemo
!entry 10A0
!idata 1000 28
!iat 1028 20
!stackcom 4000
!heapcom 4000
"""
