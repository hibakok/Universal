# BYTECODE.md — байт-за-байтом разбор hexgen.exe

Паспорт файла: KERNEL/L0-HEXGEN/BYTECODE.md | слой: L0 | роль: полный разбор образа.

Источник истины — `hexgen.hex`. Структура заголовков идентична
`KERNEL/L0-HXDUMP/BYTECODE.md` (пояснения каждого поля — там); здесь —
значения, отличия M0-HEXGEN и новый механизм виртуальных нулей (bss).

## 0. Сводка

| Свойство | Значение |
|---|---|
| Размер файла | 2560 байт (0xA00) |
| SHA-256 | 947AD0182A0162CB402CB4D92A7932681CE6B2BF16B5B524ACCE07AB3FD241BF |
| Точка входа | файл 0x200 (RVA 0x1000, K0-X031) |
| Код | 0x53D байта (RVA 0x1000..0x153D), 370 записей, 61 метка |
| Данные | 0x120 байта @ RVA 0x1540 (таблица цифр, ячейки, строки) |
| Импорты | 0x11A байта @ RVA 0x1660 (7 функций) |
| Виртуальные нули | 0x20100 байта @ RVA 0x1780: fname_in, fname_out, filebuf, imagebuf |
| Смещение → RVA | заголовки: файл = RVA; секция: RVA = файл − 0x200 + 0x1000 |

## 1. Заголовки (отличия от M0-HXDUMP)

| Поле | Смещение | Значение | Пояснение |
|---|---|---|---|
| DOS-заглушка | 0x040 | «Universal L0 hexgen. No DOS support.» | текст, 39 байт |
| SizeOfCode | 0x09C | 0x800 | SizeOfRawData (файловая часть) |
| SizeOfImage | 0x0D0 | 0x22000 | 0x1000 + 0x20880, округлено до 0x1000 |
| DD[1] Import | 0x110 | RVA 0x1660, размер 0x28 | IDT в секции |
| DD[12] IAT | 0x168 | RVA 0x1688, размер 0x40 | 7 функций + терминатор |
| VirtualSize (.text) | 0x190 | 0x20880 | 0x780 файловых + 0x20000 виртуальных нулей |
| SizeOfRawData | 0x198 | 0x800 | файл = 0x200 + 0x800 = 0xA00 |

**Виртуальные нули (новое в E3).** Впервые SizeOfRawData < VirtualSize:
хвост секции сверх файловой части загрузчик Windows заполняет нулями
(механизм bss). Большие буферы (fname, filebuf 64 КиБ, imagebuf 64 КиБ)
не занимают места в файле: образ остаётся 2560 байт и самодостаточно
описывается ATOM-листингом с 4-значными смещениями. Инвариант 4
SPEC/04-PE-MINIMAL.md обновлён: raw ≤ virtual (было: raw ≥ virtual).

## 2. Раскладка внутри .text

```
RVA 0x1000  код: главный поток, диспетчер, подпрограммы разбора (0x53D байт)
RVA 0x1540  digits: таблица 16 hex-цифр
RVA 0x1550  hstdout/written/nread/imgtop: служебные ячейки (по 8 байт)
RVA 0x1570  строки: справка (45) + 7 ошибок (24..30)
RVA 0x1660  IDT: описатель импорта kernel32.dll + терминатор
RVA 0x1688  IAT: 7 адресов функций + терминатор (заполняет загрузчик)
RVA 0x16C8  INT: копия IAT до заполнения (по ней ищутся имена)
RVA 0x1708  имя DLL; далее hint-записи 7 функций
RVA 0x1780  [виртуальные нули] fname_in (0x80)
RVA 0x1800  fname_out (0x80)
RVA 0x1880  filebuf: буфер ATOM-текста (0x10000)
RVA 0x11880  imagebuf: собираемый образ (0x10000)
RVA 0x21880  конец секции (VirtualSize 0x20880)
```

## 3. Код: все инструкции

### Таблица кода (автогенерация из ведомости)
| Файл | RVA | Байты | Мнемоника | Кирпич |
|---|---|---|---|---|
| 0x200 | 0x1000 | `48 83 EC 38` | sub rsp,0x38 | K0-X031 |
| 0x204 | 0x1004 | `48 8D 1D F5 EF FF FF` | lea rbx,[rip+disp] | K0-S031 |
| 0x20B | 0x100B | `48 C7 C1 F5 FF FF FF` | mov rcx,-11 | init |
| 0x212 | 0x1012 | `FF 15 70 06 00 00` | call [rip]GetStdHandle | init |
| 0x218 | 0x1018 | `48 89 05 31 05 00 00` | mov [rip+hstdout],rax | init |
| 0x21F | 0x101F | `FF 15 7B 06 00 00` | call [rip]GetCommandLineA | K0-C021 |
| 0x225 | 0x1025 | `48 89 C7` | mov rdi,rax | K0-C021 |
| 0x228 | 0x1028 | `0F B6 07` | movzx eax,byte [rdi] | K0-C022 |
| 0x22B | 0x102B | `3C 22` | cmp al,'"' | K0-C022 |
| 0x22D | 0x102D | `75 13` | jnz sa_unq | K0-C022 |
| 0x22F | 0x102F | `48 FF C7` | inc rdi | K0-C022 |
| 0x232 | 0x1032 | `0F B6 07` | movzx eax,byte [rdi] | K0-C022 |
| 0x235 | 0x1035 | `84 C0` | test al,al | K0-C022 |
| 0x237 | 0x1037 | `74 30` | jz noargs | K0-C022 |
| 0x239 | 0x1039 | `3C 22` | cmp al,'"' | K0-C022 |
| 0x23B | 0x103B | `74 27` | jz sa_adv | K0-C022 |
| 0x23D | 0x103D | `48 FF C7` | inc rdi | K0-C022 |
| 0x240 | 0x1040 | `EB F0` | jmp sa_qloop | K0-C022 |
| 0x242 | 0x1042 | `84 C0` | test al,al | K0-C022 |
| 0x244 | 0x1044 | `74 23` | jz noargs | K0-C022 |
| 0x246 | 0x1046 | `3C 20` | cmp al,' ' | K0-C022 |
| 0x248 | 0x1048 | `74 09` | jz sa_delims | K0-C022 |
| 0x24A | 0x104A | `3C 09` | cmp al,9 | K0-C022 |
| 0x24C | 0x104C | `74 05` | jz sa_delims | K0-C022 |
| 0x24E | 0x104E | `48 FF C7` | inc rdi | K0-C022 |
| 0x251 | 0x1051 | `EB D5` | jmp skip_argv0 | K0-C022 |
| 0x253 | 0x1053 | `0F B6 07` | movzx eax,byte [rdi] | K0-C022 |
| 0x256 | 0x1056 | `84 C0` | test al,al | K0-C022 |
| 0x258 | 0x1058 | `74 0F` | jz noargs | K0-C022 |
| 0x25A | 0x105A | `3C 20` | cmp al,' ' | K0-C022 |
| 0x25C | 0x105C | `74 06` | jz sa_adv | K0-C022 |
| 0x25E | 0x105E | `3C 09` | cmp al,9 | K0-C022 |
| 0x260 | 0x1060 | `74 02` | jz sa_adv | K0-C022 |
| 0x262 | 0x1062 | `EB 14` | jmp word1 | K0-C022 |
| 0x264 | 0x1064 | `48 FF C7` | inc rdi | K0-C022 |
| 0x267 | 0x1067 | `EB EA` | jmp sa_delims | K0-C022 |
| 0x269 | 0x1069 | `E8 B4 04 00 00` | call print_usage | K0-G031 |
| 0x26E | 0x106E | `B9 02 00 00 00` | mov ecx,2 | K0-X032 |
| 0x273 | 0x1073 | `E9 72 01 00 00` | jmp exit_proc | K0-G031 |
| 0x278 | 0x1078 | `E8 25 04 00 00` | call read_word | K0-G031 |
| 0x27D | 0x107D | `4C 8D 05 FC 06 00 00` | lea r8,[rip+fname_in] | K0-G031 |
| 0x284 | 0x1084 | `E8 42 04 00 00` | call copy_word_dst | K0-G031 |
| 0x289 | 0x1089 | `48 85 C0` | test rax,rax | K0-G031 |
| 0x28C | 0x108C | `0F 85 A6 00 00 00` | jnz err_long | K0-G031 |
| 0x292 | 0x1092 | `E8 23 04 00 00` | call skip_seps | K0-G031 |
| 0x297 | 0x1097 | `0F B6 07` | movzx eax,byte [rdi] | K0-G031 |
| 0x29A | 0x109A | `84 C0` | test al,al | K0-G031 |
| 0x29C | 0x109C | `74 CB` | jz noargs | K0-G031 |
| 0x29E | 0x109E | `E8 FF 03 00 00` | call read_word | K0-G031 |
| 0x2A3 | 0x10A3 | `4C 8D 05 56 07 00 00` | lea r8,[rip+fname_out] | K0-G031 |
| 0x2AA | 0x10AA | `E8 1C 04 00 00` | call copy_word_dst | K0-G031 |
| 0x2AF | 0x10AF | `48 85 C0` | test rax,rax | K0-G031 |
| 0x2B2 | 0x10B2 | `0F 85 80 00 00 00` | jnz err_long | K0-G031 |
| 0x2B8 | 0x10B8 | `48 8D 0D C1 06 00 00` | lea rcx,[rip+fname_in] | K0-G031 |
| 0x2BF | 0x10BF | `E8 6F 01 00 00` | call open_file_read | K0-G031 |
| 0x2C4 | 0x10C4 | `48 83 F8 FF` | cmp rax,-1 | K0-G031 |
| 0x2C8 | 0x10C8 | `0F 84 86 00 00 00` | jz err_openin | K0-G031 |
| 0x2CE | 0x10CE | `49 89 C4` | mov r12,rax | K0-G031 |
| 0x2D1 | 0x10D1 | `E8 1B 01 00 00` | call read_whole | K0-G031 |
| 0x2D6 | 0x10D6 | `48 83 F8 FF` | cmp rax,-1 | K0-G031 |
| 0x2DA | 0x10DA | `0F 84 8D 00 00 00` | jz err_read | K0-G031 |
| 0x2E0 | 0x10E0 | `48 3D 00 00 01 00` | cmp rax,0x10000 | K0-G031 |
| 0x2E6 | 0x10E6 | `0F 83 9A 00 00 00` | jae err_big | K0-G031 |
| 0x2EC | 0x10EC | `4C 89 E1` | mov rcx,r12 | K0-G031 |
| 0x2EF | 0x10EF | `E8 77 01 00 00` | call close_file | K0-G031 |
| 0x2F4 | 0x10F4 | `E8 03 02 00 00` | call parse_atom | K0-G031 |
| 0x2F9 | 0x10F9 | `48 85 C0` | test rax,rax | K0-G031 |
| 0x2FC | 0x10FC | `0F 85 9D 00 00 00` | jnz err_format | K0-G031 |
| 0x302 | 0x1102 | `48 8D 0D F7 06 00 00` | lea rcx,[rip+fname_out] | K0-G031 |
| 0x309 | 0x1109 | `E8 6C 01 00 00` | call create_file_write | K0-G031 |
| 0x30E | 0x110E | `48 83 F8 FF` | cmp rax,-1 | K0-G031 |
| 0x312 | 0x1112 | `0F 84 A0 00 00 00` | jz err_openout | K0-G031 |
| 0x318 | 0x1118 | `49 89 C4` | mov r12,rax | K0-G031 |
| 0x31B | 0x111B | `E8 8F 01 00 00` | call write_image | K0-G031 |
| 0x320 | 0x1120 | `48 85 C0` | test rax,rax | K0-G031 |
| 0x323 | 0x1123 | `0F 85 A8 00 00 00` | jnz err_write | K0-G031 |
| 0x329 | 0x1129 | `4C 89 E1` | mov rcx,r12 | K0-G031 |
| 0x32C | 0x112C | `E8 3A 01 00 00` | call close_file | K0-G031 |
| 0x331 | 0x1131 | `31 C9` | xor ecx,ecx | K0-X032 |
| 0x333 | 0x1133 | `E9 B2 00 00 00` | jmp exit_proc | K0-G031 |
| 0x338 | 0x1138 | `48 8D 15 5E 04 00 00` | lea rdx,[rip+err_long_str] | K0-G031 |
| 0x33F | 0x113F | `41 B8 1B 00 00 00` | mov r8d,27 | K0-G031 |
| 0x345 | 0x1145 | `E8 B2 03 00 00` | call print_line | K0-G031 |
| 0x34A | 0x114A | `B9 03 00 00 00` | mov ecx,3 | K0-X032 |
| 0x34F | 0x114F | `E9 96 00 00 00` | jmp exit_proc | K0-G031 |
| 0x354 | 0x1154 | `48 8D 15 5D 04 00 00` | lea rdx,[rip+err_openin_str] | K0-G031 |
| 0x35B | 0x115B | `41 B8 1C 00 00 00` | mov r8d,28 | K0-G031 |
| 0x361 | 0x1161 | `E8 96 03 00 00` | call print_line | K0-G031 |
| 0x366 | 0x1166 | `B9 04 00 00 00` | mov ecx,4 | K0-X032 |
| 0x36B | 0x116B | `EB 7D` | jmp exit_proc | K0-G031 |
| 0x36D | 0x116D | `48 8D 15 60 04 00 00` | lea rdx,[rip+err_read_str] | K0-G031 |
| 0x374 | 0x1174 | `41 B8 1C 00 00 00` | mov r8d,28 | K0-G031 |
| 0x37A | 0x117A | `E8 7D 03 00 00` | call print_line | K0-G031 |
| 0x37F | 0x117F | `B9 05 00 00 00` | mov ecx,5 | K0-X032 |
| 0x384 | 0x1184 | `EB 64` | jmp exit_proc | K0-G031 |
| 0x386 | 0x1186 | `48 8D 15 63 04 00 00` | lea rdx,[rip+err_big_str] | K0-G031 |
| 0x38D | 0x118D | `41 B8 1B 00 00 00` | mov r8d,27 | K0-G031 |
| 0x393 | 0x1193 | `E8 64 03 00 00` | call print_line | K0-G031 |
| 0x398 | 0x1198 | `B9 06 00 00 00` | mov ecx,6 | K0-X032 |
| 0x39D | 0x119D | `EB 4B` | jmp exit_proc | K0-G031 |
| 0x39F | 0x119F | `48 8D 15 65 04 00 00` | lea rdx,[rip+err_format_str] | K0-G031 |
| 0x3A6 | 0x11A6 | `41 B8 18 00 00 00` | mov r8d,24 | K0-G031 |
| 0x3AC | 0x11AC | `E8 4B 03 00 00` | call print_line | K0-G031 |
| 0x3B1 | 0x11B1 | `B9 07 00 00 00` | mov ecx,7 | K0-X032 |
| 0x3B6 | 0x11B6 | `EB 32` | jmp exit_proc | K0-G031 |
| 0x3B8 | 0x11B8 | `48 8D 15 64 04 00 00` | lea rdx,[rip+err_openout_str] | K0-G031 |
| 0x3BF | 0x11BF | `41 B8 1D 00 00 00` | mov r8d,29 | K0-G031 |
| 0x3C5 | 0x11C5 | `E8 32 03 00 00` | call print_line | K0-G031 |
| 0x3CA | 0x11CA | `B9 08 00 00 00` | mov ecx,8 | K0-X032 |
| 0x3CF | 0x11CF | `EB 19` | jmp exit_proc | K0-G031 |
| 0x3D1 | 0x11D1 | `48 8D 15 68 04 00 00` | lea rdx,[rip+err_write_str] | K0-G031 |
| 0x3D8 | 0x11D8 | `41 B8 1E 00 00 00` | mov r8d,30 | K0-G031 |
| 0x3DE | 0x11DE | `E8 19 03 00 00` | call print_line | K0-G031 |
| 0x3E3 | 0x11E3 | `B9 09 00 00 00` | mov ecx,9 | K0-X032 |
| 0x3E8 | 0x11E8 | `EB 00` | jmp exit_proc | K0-G031 |
| 0x3EA | 0x11EA | `FF 15 A8 04 00 00` | call [rip]ExitProcess | K0-X032 |
| 0x3F0 | 0x11F0 | `CC` | int3 | K0-X032 |
| 0x3F1 | 0x11F1 | `48 83 EC 28` | sub rsp,0x28 | K0-F004 |
| 0x3F5 | 0x11F5 | `4C 89 E1` | mov rcx,r12 | K0-F004 |
| 0x3F8 | 0x11F8 | `48 8D 15 81 06 00 00` | lea rdx,[rip+filebuf] | K0-F004 |
| 0x3FF | 0x11FF | `41 B8 00 00 01 00` | mov r8d,0x10000 | K0-F004 |
| 0x405 | 0x1205 | `4C 8D 0D 54 03 00 00` | lea r9,[rip+nread] | K0-F004 |
| 0x40C | 0x120C | `48 C7 44 24 20 00 00 00 00` | mov qword [rsp+0x20],0 | K0-F004 |
| 0x415 | 0x1215 | `FF 15 95 04 00 00` | call [rip]ReadFile | K0-F004 |
| 0x41B | 0x121B | `48 83 C4 28` | add rsp,0x28 | K0-F004 |
| 0x41F | 0x121F | `48 85 C0` | test rax,rax | K0-F004 |
| 0x422 | 0x1222 | `75 08` | jnz rwf_ok | K0-F004 |
| 0x424 | 0x1224 | `48 C7 C0 FF FF FF FF` | mov rax,-1 | K0-F004 |
| 0x42B | 0x122B | `C3` | ret | K0-F004 |
| 0x42C | 0x122C | `8B 05 2E 03 00 00` | mov eax,[rip+nread] | K0-F004 |
| 0x432 | 0x1232 | `C3` | ret | K0-F004 |
| 0x433 | 0x1233 | `48 83 EC 38` | sub rsp,0x38 | K0-F011 |
| 0x437 | 0x1237 | `BA 00 00 00 80` | mov edx,0x80000000 | K0-F011 |
| 0x43C | 0x123C | `41 B8 01 00 00 00` | mov r8d,1 | K0-F011 |
| 0x442 | 0x1242 | `45 31 C9` | xor r9d,r9d | K0-F011 |
| 0x445 | 0x1245 | `48 C7 44 24 20 03 00 00 00` | mov qword [rsp+0x20],3 | K0-F011 |
| 0x44E | 0x124E | `48 C7 44 24 28 80 00 00 00` | mov qword [rsp+0x28],0x80 | K0-F011 |
| 0x457 | 0x1257 | `48 C7 44 24 30 00 00 00 00` | mov qword [rsp+0x30],0 | K0-F011 |
| 0x460 | 0x1260 | `FF 15 42 04 00 00` | call [rip]CreateFileA | K0-F011 |
| 0x466 | 0x1266 | `48 83 C4 38` | add rsp,0x38 | K0-F011 |
| 0x46A | 0x126A | `C3` | ret | K0-F011 |
| 0x46B | 0x126B | `48 83 EC 28` | sub rsp,0x28 | K0-F013 |
| 0x46F | 0x126F | `FF 15 43 04 00 00` | call [rip]CloseHandle | K0-F013 |
| 0x475 | 0x1275 | `48 83 C4 28` | add rsp,0x28 | K0-F013 |
| 0x479 | 0x1279 | `C3` | ret | K0-F013 |
| 0x47A | 0x127A | `48 83 EC 38` | sub rsp,0x38 | K0-F005 |
| 0x47E | 0x127E | `BA 00 00 00 40` | mov edx,0x40000000 | K0-F005 |
| 0x483 | 0x1283 | `45 31 C0` | xor r8d,r8d | K0-F005 |
| 0x486 | 0x1286 | `45 31 C9` | xor r9d,r9d | K0-F005 |
| 0x489 | 0x1289 | `48 C7 44 24 20 02 00 00 00` | mov qword [rsp+0x20],2 | K0-F005 |
| 0x492 | 0x1292 | `48 C7 44 24 28 80 00 00 00` | mov qword [rsp+0x28],0x80 | K0-F005 |
| 0x49B | 0x129B | `48 C7 44 24 30 00 00 00 00` | mov qword [rsp+0x30],0 | K0-F005 |
| 0x4A4 | 0x12A4 | `FF 15 FE 03 00 00` | call [rip]CreateFileA | K0-F005 |
| 0x4AA | 0x12AA | `48 83 C4 38` | add rsp,0x38 | K0-F005 |
| 0x4AE | 0x12AE | `C3` | ret | K0-F005 |
| 0x4AF | 0x12AF | `48 83 EC 28` | sub rsp,0x28 | K0-F006 |
| 0x4B3 | 0x12B3 | `4C 89 E1` | mov rcx,r12 | K0-F006 |
| 0x4B6 | 0x12B6 | `48 8D 15 C3 05 01 00` | lea rdx,[rip+imagebuf] | K0-F006 |
| 0x4BD | 0x12BD | `4C 8B 05 A4 02 00 00` | mov r8,[rip+imgtop] | K0-F006 |
| 0x4C4 | 0x12C4 | `4C 8D 0D 8D 02 00 00` | lea r9,[rip+written] | K0-F006 |
| 0x4CB | 0x12CB | `48 C7 44 24 20 00 00 00 00` | mov qword [rsp+0x20],0 | K0-F006 |
| 0x4D4 | 0x12D4 | `FF 15 B6 03 00 00` | call [rip]WriteFile | K0-F006 |
| 0x4DA | 0x12DA | `48 83 C4 28` | add rsp,0x28 | K0-F006 |
| 0x4DE | 0x12DE | `48 85 C0` | test rax,rax | K0-F006 |
| 0x4E1 | 0x12E1 | `74 13` | jz wi_err | K0-F006 |
| 0x4E3 | 0x12E3 | `48 8B 05 6E 02 00 00` | mov rax,[rip+written] | K0-F006 |
| 0x4EA | 0x12EA | `48 3B 05 77 02 00 00` | cmp rax,[rip+imgtop] | K0-F006 |
| 0x4F1 | 0x12F1 | `75 03` | jnz wi_err | K0-F006 |
| 0x4F3 | 0x12F3 | `31 C0` | xor eax,eax | K0-F006 |
| 0x4F5 | 0x12F5 | `C3` | ret | K0-F006 |
| 0x4F6 | 0x12F6 | `B8 01 00 00 00` | mov eax,1 | K0-F006 |
| 0x4FB | 0x12FB | `C3` | ret | K0-F006 |
| 0x4FC | 0x12FC | `4C 8D 3D 7D 05 01 00` | lea r15,[rip+imagebuf] | K0-R001 |
| 0x503 | 0x1303 | `48 8D 35 76 05 00 00` | lea rsi,[rip+filebuf] | K0-R001 |
| 0x50A | 0x130A | `8B 05 50 02 00 00` | mov eax,[rip+nread] | K0-R001 |
| 0x510 | 0x1310 | `48 98` | cdqe | K0-R001 |
| 0x512 | 0x1312 | `48 8D 0D 67 05 00 00` | lea rcx,[rip+filebuf] | K0-R001 |
| 0x519 | 0x1319 | `48 01 C1` | add rcx,rax | K0-R001 |
| 0x51C | 0x131C | `C6 01 00` | mov byte [rcx],0 | K0-R001 |
| 0x51F | 0x131F | `45 31 ED` | xor r13d,r13d | K0-R001 |
| 0x522 | 0x1322 | `0F B6 06` | movzx eax,byte [rsi] | K0-R001 |
| 0x525 | 0x1325 | `84 C0` | test al,al | K0-R001 |
| 0x527 | 0x1327 | `74 4C` | jz pa_ok | K0-R001 |
| 0x529 | 0x1329 | `3C 3B` | cmp al,';' | K0-R001 |
| 0x52B | 0x132B | `74 33` | jz pa_skip | K0-R001 |
| 0x52D | 0x132D | `3C 0D` | cmp al,0x0D | K0-R001 |
| 0x52F | 0x132F | `74 2F` | jz pa_skip | K0-R001 |
| 0x531 | 0x1331 | `3C 0A` | cmp al,0x0A | K0-R001 |
| 0x533 | 0x1333 | `74 0A` | jz pa_lf | K0-R001 |
| 0x535 | 0x1335 | `3C 40` | cmp al,'@' | K0-R001 |
| 0x537 | 0x1337 | `74 0B` | jz pa_data | K0-R001 |
| 0x539 | 0x1339 | `3C 5A` | cmp al,'Z' | K0-R001 |
| 0x53B | 0x133B | `74 16` | jz pa_zero | K0-R001 |
| 0x53D | 0x133D | `EB 40` | jmp pa_bad | K0-R001 |
| 0x53F | 0x133F | `48 FF C6` | inc rsi | K0-R001 |
| 0x542 | 0x1342 | `EB DE` | jmp pa_next | K0-R001 |
| 0x544 | 0x1344 | `48 FF C6` | inc rsi | K0-R001 |
| 0x547 | 0x1347 | `E8 8D 00 00 00` | call parse_data_line | K0-R001 |
| 0x54C | 0x134C | `48 85 C0` | test rax,rax | K0-R001 |
| 0x54F | 0x134F | `75 2E` | jnz pa_bad | K0-R001 |
| 0x551 | 0x1351 | `EB 0D` | jmp pa_skip | K0-R001 |
| 0x553 | 0x1353 | `48 FF C6` | inc rsi | K0-R001 |
| 0x556 | 0x1356 | `E8 EF 00 00 00` | call parse_zero_line | K0-R001 |
| 0x55B | 0x135B | `48 85 C0` | test rax,rax | K0-R001 |
| 0x55E | 0x135E | `75 1F` | jnz pa_bad | K0-R001 |
| 0x560 | 0x1360 | `0F B6 06` | movzx eax,byte [rsi] | K0-R001 |
| 0x563 | 0x1363 | `84 C0` | test al,al | K0-R001 |
| 0x565 | 0x1365 | `74 0E` | jz pa_ok | K0-R001 |
| 0x567 | 0x1367 | `3C 0A` | cmp al,0x0A | K0-R001 |
| 0x569 | 0x1369 | `74 05` | jz pa_skiplf | K0-R001 |
| 0x56B | 0x136B | `48 FF C6` | inc rsi | K0-R001 |
| 0x56E | 0x136E | `EB F0` | jmp pa_skip | K0-R001 |
| 0x570 | 0x1370 | `48 FF C6` | inc rsi | K0-R001 |
| 0x573 | 0x1373 | `EB AD` | jmp pa_next | K0-R001 |
| 0x575 | 0x1375 | `4C 89 2D EC 01 00 00` | mov [rip+imgtop],r13 | K0-R001 |
| 0x57C | 0x137C | `31 C0` | xor eax,eax | K0-R001 |
| 0x57E | 0x137E | `C3` | ret | K0-R001 |
| 0x57F | 0x137F | `B8 01 00 00 00` | mov eax,1 | K0-R001 |
| 0x584 | 0x1384 | `C3` | ret | K0-R001 |
| 0x585 | 0x1385 | `80 3E 20` | cmp byte [rsi],' ' | K0-R006 |
| 0x588 | 0x1388 | `75 05` | jnz ssp_done | K0-R006 |
| 0x58A | 0x138A | `48 FF C6` | inc rsi | K0-R006 |
| 0x58D | 0x138D | `EB F6` | jmp ssp_loop | K0-R006 |
| 0x58F | 0x138F | `C3` | ret | K0-R006 |
| 0x590 | 0x1390 | `3C 30` | cmp al,'0' | K0-R002 |
| 0x592 | 0x1392 | `72 14` | jb hd_bad | K0-R002 |
| 0x594 | 0x1394 | `3C 39` | cmp al,'9' | K0-R002 |
| 0x596 | 0x1396 | `77 04` | ja hd_letter | K0-R002 |
| 0x598 | 0x1398 | `83 E8 30` | sub eax,0x30 | K0-R002 |
| 0x59B | 0x139B | `C3` | ret | K0-R002 |
| 0x59C | 0x139C | `3C 41` | cmp al,'A' | K0-R002 |
| 0x59E | 0x139E | `72 08` | jb hd_bad | K0-R002 |
| 0x5A0 | 0x13A0 | `3C 46` | cmp al,'F' | K0-R002 |
| 0x5A2 | 0x13A2 | `77 04` | ja hd_bad | K0-R002 |
| 0x5A4 | 0x13A4 | `83 E8 37` | sub eax,0x37 | K0-R002 |
| 0x5A7 | 0x13A7 | `C3` | ret | K0-R002 |
| 0x5A8 | 0x13A8 | `48 C7 C0 FF FF FF FF` | mov rax,-1 | K0-R002 |
| 0x5AF | 0x13AF | `C3` | ret | K0-R002 |
| 0x5B0 | 0x13B0 | `45 31 D2` | xor r10d,r10d | K0-R003 |
| 0x5B3 | 0x13B3 | `B9 04 00 00 00` | mov ecx,4 | K0-R003 |
| 0x5B8 | 0x13B8 | `0F B6 06` | movzx eax,byte [rsi] | K0-R003 |
| 0x5BB | 0x13BB | `E8 D0 FF FF FF` | call hex_digit | K0-R003 |
| 0x5C0 | 0x13C0 | `48 83 F8 FF` | cmp rax,-1 | K0-R003 |
| 0x5C4 | 0x13C4 | `74 12` | jz rh4_bad | K0-R003 |
| 0x5C6 | 0x13C6 | `41 C1 E2 04` | shl r10d,4 | K0-R003 |
| 0x5CA | 0x13CA | `41 01 C2` | add r10d,eax | K0-R003 |
| 0x5CD | 0x13CD | `48 FF C6` | inc rsi | K0-R003 |
| 0x5D0 | 0x13D0 | `FF C9` | dec ecx | K0-R003 |
| 0x5D2 | 0x13D2 | `75 E4` | jnz rh4_loop | K0-R003 |
| 0x5D4 | 0x13D4 | `44 89 D0` | mov eax,r10d | K0-R003 |
| 0x5D7 | 0x13D7 | `C3` | ret | K0-R003 |
| 0x5D8 | 0x13D8 | `C3` | ret | K0-R003 |
| 0x5D9 | 0x13D9 | `E8 D2 FF FF FF` | call read_hex4 | K0-R004 |
| 0x5DE | 0x13DE | `48 83 F8 FF` | cmp rax,-1 | K0-R004 |
| 0x5E2 | 0x13E2 | `74 5E` | jz pdl_bad | K0-R004 |
| 0x5E4 | 0x13E4 | `41 89 C4` | mov r12d,eax | K0-R004 |
| 0x5E7 | 0x13E7 | `E8 99 FF FF FF` | call skip_spaces | K0-R004 |
| 0x5EC | 0x13EC | `0F B6 06` | movzx eax,byte [rsi] | K0-R004 |
| 0x5EF | 0x13EF | `84 C0` | test al,al | K0-R004 |
| 0x5F1 | 0x13F1 | `74 4C` | jz pdl_ok | K0-R004 |
| 0x5F3 | 0x13F3 | `3C 0D` | cmp al,0x0D | K0-R004 |
| 0x5F5 | 0x13F5 | `74 48` | jz pdl_ok | K0-R004 |
| 0x5F7 | 0x13F7 | `3C 0A` | cmp al,0x0A | K0-R004 |
| 0x5F9 | 0x13F9 | `74 44` | jz pdl_ok | K0-R004 |
| 0x5FB | 0x13FB | `3C 3B` | cmp al,';' | K0-R004 |
| 0x5FD | 0x13FD | `74 40` | jz pdl_ok | K0-R004 |
| 0x5FF | 0x13FF | `E8 8C FF FF FF` | call hex_digit | K0-R004 |
| 0x604 | 0x1404 | `48 83 F8 FF` | cmp rax,-1 | K0-R004 |
| 0x608 | 0x1408 | `74 38` | jz pdl_bad | K0-R004 |
| 0x60A | 0x140A | `89 C2` | mov edx,eax | K0-R004 |
| 0x60C | 0x140C | `C1 E2 04` | shl edx,4 | K0-R004 |
| 0x60F | 0x140F | `48 FF C6` | inc rsi | K0-R004 |
| 0x612 | 0x1412 | `0F B6 06` | movzx eax,byte [rsi] | K0-R004 |
| 0x615 | 0x1415 | `E8 76 FF FF FF` | call hex_digit | K0-R004 |
| 0x61A | 0x141A | `48 83 F8 FF` | cmp rax,-1 | K0-R004 |
| 0x61E | 0x141E | `74 22` | jz pdl_bad | K0-R004 |
| 0x620 | 0x1420 | `01 C2` | add edx,eax | K0-R004 |
| 0x622 | 0x1422 | `41 81 FC 00 00 01 00` | cmp r12d,0x10000 | K0-R004 |
| 0x629 | 0x1429 | `73 17` | jae pdl_bad | K0-R004 |
| 0x62B | 0x142B | `43 88 14 27` | mov [r15+r12],dl | K0-R004 |
| 0x62F | 0x142F | `49 FF C4` | inc r12 | K0-R004 |
| 0x632 | 0x1432 | `48 FF C6` | inc rsi | K0-R004 |
| 0x635 | 0x1435 | `45 39 EC` | cmp r12d,r13d | K0-R004 |
| 0x638 | 0x1438 | `76 03` | jbe pdl_cont | K0-R004 |
| 0x63A | 0x143A | `45 89 E5` | mov r13d,r12d | K0-R004 |
| 0x63D | 0x143D | `EB A8` | jmp pdl_loop | K0-R004 |
| 0x63F | 0x143F | `31 C0` | xor eax,eax | K0-R004 |
| 0x641 | 0x1441 | `C3` | ret | K0-R004 |
| 0x642 | 0x1442 | `48 C7 C0 FF FF FF FF` | mov rax,-1 | K0-R004 |
| 0x649 | 0x1449 | `C3` | ret | K0-R004 |
| 0x64A | 0x144A | `E8 36 FF FF FF` | call skip_spaces | K0-R005 |
| 0x64F | 0x144F | `E8 5C FF FF FF` | call read_hex4 | K0-R005 |
| 0x654 | 0x1454 | `48 83 F8 FF` | cmp rax,-1 | K0-R005 |
| 0x658 | 0x1458 | `74 40` | jz pz_bad | K0-R005 |
| 0x65A | 0x145A | `41 89 C4` | mov r12d,eax | K0-R005 |
| 0x65D | 0x145D | `E8 23 FF FF FF` | call skip_spaces | K0-R005 |
| 0x662 | 0x1462 | `E8 49 FF FF FF` | call read_hex4 | K0-R005 |
| 0x667 | 0x1467 | `48 83 F8 FF` | cmp rax,-1 | K0-R005 |
| 0x66B | 0x146B | `74 2D` | jz pz_bad | K0-R005 |
| 0x66D | 0x146D | `41 89 C3` | mov r11d,eax | K0-R005 |
| 0x670 | 0x1470 | `45 39 E3` | cmp r11d,r12d | K0-R005 |
| 0x673 | 0x1473 | `72 25` | jb pz_bad | K0-R005 |
| 0x675 | 0x1475 | `45 39 DD` | cmp r13d,r11d | K0-R005 |
| 0x678 | 0x1478 | `73 03` | jae pz_tail | K0-R005 |
| 0x67A | 0x147A | `45 89 DD` | mov r13d,r11d | K0-R005 |
| 0x67D | 0x147D | `E8 03 FF FF FF` | call skip_spaces | K0-R005 |
| 0x682 | 0x1482 | `0F B6 06` | movzx eax,byte [rsi] | K0-R005 |
| 0x685 | 0x1485 | `84 C0` | test al,al | K0-R005 |
| 0x687 | 0x1487 | `74 0E` | jz pz_ok | K0-R005 |
| 0x689 | 0x1489 | `3C 0D` | cmp al,0x0D | K0-R005 |
| 0x68B | 0x148B | `74 0A` | jz pz_ok | K0-R005 |
| 0x68D | 0x148D | `3C 0A` | cmp al,0x0A | K0-R005 |
| 0x68F | 0x148F | `74 06` | jz pz_ok | K0-R005 |
| 0x691 | 0x1491 | `3C 3B` | cmp al,';' | K0-R005 |
| 0x693 | 0x1493 | `74 02` | jz pz_ok | K0-R005 |
| 0x695 | 0x1495 | `EB 03` | jmp pz_bad | K0-R005 |
| 0x697 | 0x1497 | `31 C0` | xor eax,eax | K0-R005 |
| 0x699 | 0x1499 | `C3` | ret | K0-R005 |
| 0x69A | 0x149A | `48 C7 C0 FF FF FF FF` | mov rax,-1 | K0-R005 |
| 0x6A1 | 0x14A1 | `C3` | ret | K0-R005 |
| 0x6A2 | 0x14A2 | `48 89 FE` | mov rsi,rdi | K0-C023 |
| 0x6A5 | 0x14A5 | `0F B6 07` | movzx eax,byte [rdi] | K0-C023 |
| 0x6A8 | 0x14A8 | `84 C0` | test al,al | K0-C023 |
| 0x6AA | 0x14AA | `74 0D` | jz rw_end | K0-C023 |
| 0x6AC | 0x14AC | `3C 20` | cmp al,' ' | K0-C023 |
| 0x6AE | 0x14AE | `74 09` | jz rw_end | K0-C023 |
| 0x6B0 | 0x14B0 | `3C 09` | cmp al,9 | K0-C023 |
| 0x6B2 | 0x14B2 | `74 05` | jz rw_end | K0-C023 |
| 0x6B4 | 0x14B4 | `48 FF C7` | inc rdi | K0-C023 |
| 0x6B7 | 0x14B7 | `EB EC` | jmp rw_loop | K0-C023 |
| 0x6B9 | 0x14B9 | `C3` | ret | K0-C023 |
| 0x6BA | 0x14BA | `0F B6 07` | movzx eax,byte [rdi] | K0-C025 |
| 0x6BD | 0x14BD | `3C 20` | cmp al,' ' | K0-C025 |
| 0x6BF | 0x14BF | `74 05` | jz ss_adv | K0-C025 |
| 0x6C1 | 0x14C1 | `3C 09` | cmp al,9 | K0-C025 |
| 0x6C3 | 0x14C3 | `74 01` | jz ss_adv | K0-C025 |
| 0x6C5 | 0x14C5 | `C3` | ret | K0-C025 |
| 0x6C6 | 0x14C6 | `48 FF C7` | inc rdi | K0-C025 |
| 0x6C9 | 0x14C9 | `EB EF` | jmp ss_loop | K0-C025 |
| 0x6CB | 0x14CB | `4D 89 C2` | mov r10,r8 | K0-C024 |
| 0x6CE | 0x14CE | `39 FE` | cmp rsi,rdi | K0-C024 |
| 0x6D0 | 0x14D0 | `74 1A` | jz cwd_done | K0-C024 |
| 0x6D2 | 0x14D2 | `4C 89 D2` | mov rdx,r10 | K0-C024 |
| 0x6D5 | 0x14D5 | `4C 29 C2` | sub rdx,r8 | K0-C024 |
| 0x6D8 | 0x14D8 | `48 83 FA 7F` | cmp rdx,0x7F | K0-C024 |
| 0x6DC | 0x14DC | `73 14` | jae cwd_long | K0-C024 |
| 0x6DE | 0x14DE | `0F B6 16` | movzx edx,byte [rsi] | K0-C024 |
| 0x6E1 | 0x14E1 | `41 88 12` | mov [r10],dl | K0-C024 |
| 0x6E4 | 0x14E4 | `48 FF C6` | inc rsi | K0-C024 |
| 0x6E7 | 0x14E7 | `49 FF C2` | inc r10 | K0-C024 |
| 0x6EA | 0x14EA | `EB E2` | jmp cwd_loop | K0-C024 |
| 0x6EC | 0x14EC | `31 C0` | xor eax,eax | K0-C024 |
| 0x6EE | 0x14EE | `41 88 02` | mov [r10],al | K0-C024 |
| 0x6F1 | 0x14F1 | `C3` | ret | K0-C024 |
| 0x6F2 | 0x14F2 | `41 C6 02 00` | mov byte [r10],0 | K0-C024 |
| 0x6F6 | 0x14F6 | `B8 01 00 00 00` | mov eax,1 | K0-C024 |
| 0x6FB | 0x14FB | `C3` | ret | K0-C024 |
| 0x6FC | 0x14FC | `48 83 EC 28` | sub rsp,0x28 | K0-P031 |
| 0x700 | 0x1500 | `48 8B 0D 49 00 00 00` | mov rcx,[rip+hstdout] | K0-P031 |
| 0x707 | 0x1507 | `4C 8D 0D 4A 00 00 00` | lea r9,[rip+written] | K0-P031 |
| 0x70E | 0x150E | `48 C7 44 24 20 00 00 00 00` | mov qword [rsp+0x20],0 | K0-P031 |
| 0x717 | 0x1517 | `FF 15 73 01 00 00` | call [rip]WriteFile | K0-P031 |
| 0x71D | 0x151D | `48 83 C4 28` | add rsp,0x28 | K0-P031 |
| 0x721 | 0x1521 | `C3` | ret | K0-P031 |
| 0x722 | 0x1522 | `48 83 EC 28` | sub rsp,0x28 | K0-U031 |
| 0x726 | 0x1526 | `48 8D 15 43 00 00 00` | lea rdx,[rip+usage_str] | K0-U031 |
| 0x72D | 0x152D | `41 B8 2D 00 00 00` | mov r8d,45 | K0-U031 |
| 0x733 | 0x1533 | `E8 C4 FF FF FF` | call print_line | K0-U031 |
| 0x738 | 0x1538 | `48 83 C4 28` | add rsp,0x28 | K0-U031 |
| 0x73C | 0x153C | `C3` | ret | K0-U031 |

## 4. Данные

| Файл | RVA | Байты | Содержимое | Кирпич |
|---|---|---|---|---|
| 0x740 | 0x1540 | `30 31 32 33 34 35 36 37 38 39 41 42 43 44 45 46` | таблица 16 hex-цифр | K0-D031 |
| 0x750 | 0x1550 | `00 00 00 00 00 00 00 00` | hstdout: хэндл stdout (заполняет init) | K0-D031 |
| 0x758 | 0x1558 | `00 00 00 00 00 00 00 00` | written: счётчик WriteFile | K0-D031 |
| 0x760 | 0x1560 | `00 00 00 00 00 00 00 00` | nread: счётчик ReadFile | K0-D031 |
| 0x768 | 0x1568 | `00 00 00 00 00 00 00 00` | imgtop: размер собранного образа | K0-D031 |
| 0x770 | 0x1570 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 43 4D 44 53 3A 20 48 45 58 47 45 4E 20 3C 49 4E 2E 48 45 58 3E 20 3C 4F 55 54 2E 42 49 4E 3E 0D 0A` | справка (45 байт) | K0-D032 |
| 0x79D | 0x159D | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 4C 4F 4E 47 20 4E 41 4D 45 0D 0A` | ошибка: имя длиннее 127 (27) | K0-D032 |
| 0x7B8 | 0x15B8 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 4F 50 45 4E 20 49 4E 50 55 54 0D 0A` | ошибка: вход не открыт (28) | K0-D032 |
| 0x7D4 | 0x15D4 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 52 45 41 44 20 49 4E 50 55 54 0D 0A` | ошибка чтения входа (28) | K0-D032 |
| 0x7F0 | 0x15F0 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 42 49 47 20 49 4E 50 55 54 0D 0A` | ошибка: вход больше 64 КиБ (27) | K0-D032 |
| 0x80B | 0x160B | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 46 4F 52 4D 41 54 0D 0A` | ошибка: плохой формат ATOM (24) | K0-D032 |
| 0x823 | 0x1623 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 4F 50 45 4E 20 4F 55 54 50 55 54 0D 0A` | ошибка: выход не создан (29) | K0-D032 |
| 0x840 | 0x1640 | `55 2D 4C 30 2D 48 45 58 47 45 4E 20 45 52 52 3D 57 52 49 54 45 20 4F 55 54 50 55 54 0D 0A` | ошибка записи выхода (30) | K0-D032 |

## 5. Импорты (kernel32.dll, 7 функций)

| Файл | RVA | Байты | Содержимое | Кирпич |
|---|---|---|---|---|
| 0x860 | 0x1660 | `C8 16 00 00 00 00 00 00 00 00 00 00 08 17 00 00 88 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00` | описатель импорта (INT, время, цепочка, имя, IAT) + терминатор | K0-D037 |
| 0x888 | 0x1688 | `16 17 00 00 00 00 00 00` | IAT[0] GetStdHandle (RVA + нули до qword) | K0-D037 |
| 0x890 | 0x1690 | `26 17 00 00 00 00 00 00` | IAT[1] WriteFile (RVA + нули до qword) | K0-D037 |
| 0x898 | 0x1698 | `32 17 00 00 00 00 00 00` | IAT[2] ExitProcess (RVA + нули до qword) | K0-D037 |
| 0x8A0 | 0x16A0 | `40 17 00 00 00 00 00 00` | IAT[3] GetCommandLineA (RVA + нули до qword) | K0-D037 |
| 0x8A8 | 0x16A8 | `52 17 00 00 00 00 00 00` | IAT[4] CreateFileA (RVA + нули до qword) | K0-D037 |
| 0x8B0 | 0x16B0 | `60 17 00 00 00 00 00 00` | IAT[5] ReadFile (RVA + нули до qword) | K0-D037 |
| 0x8B8 | 0x16B8 | `6C 17 00 00 00 00 00 00` | IAT[6] CloseHandle (RVA + нули до qword) | K0-D037 |
| 0x8C0 | 0x16C0 | `00 00 00 00 00 00 00 00` | IAT: терминатор | K0-D037 |
| 0x8C8 | 0x16C8 | `16 17 00 00 00 00 00 00` | INT[0] (копия IAT до заполнения) | K0-D037 |
| 0x8D0 | 0x16D0 | `26 17 00 00 00 00 00 00` | INT[1] (копия IAT до заполнения) | K0-D037 |
| 0x8D8 | 0x16D8 | `32 17 00 00 00 00 00 00` | INT[2] (копия IAT до заполнения) | K0-D037 |
| 0x8E0 | 0x16E0 | `40 17 00 00 00 00 00 00` | INT[3] (копия IAT до заполнения) | K0-D037 |
| 0x8E8 | 0x16E8 | `52 17 00 00 00 00 00 00` | INT[4] (копия IAT до заполнения) | K0-D037 |
| 0x8F0 | 0x16F0 | `60 17 00 00 00 00 00 00` | INT[5] (копия IAT до заполнения) | K0-D037 |
| 0x8F8 | 0x16F8 | `6C 17 00 00 00 00 00 00` | INT[6] (копия IAT до заполнения) | K0-D037 |
| 0x900 | 0x1700 | `00 00 00 00 00 00 00 00` | INT: терминатор | K0-D037 |
| 0x908 | 0x1708 | `6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00` | имя DLL | K0-D037 |
| 0x916 | 0x1716 | `00 00 47 65 74 53 74 64 48 61 6E 64 6C 65 00` | hint=0 + имя GetStdHandle | K0-D037 |
| 0x926 | 0x1726 | `00 00 57 72 69 74 65 46 69 6C 65 00` | hint=0 + имя WriteFile | K0-D037 |
| 0x932 | 0x1732 | `00 00 45 78 69 74 50 72 6F 63 65 73 73 00` | hint=0 + имя ExitProcess | K0-D037 |
| 0x940 | 0x1740 | `00 00 47 65 74 43 6F 6D 6D 61 6E 64 4C 69 6E 65 41 00` | hint=0 + имя GetCommandLineA | K0-D037 |
| 0x952 | 0x1752 | `00 00 43 72 65 61 74 65 46 69 6C 65 41 00` | hint=0 + имя CreateFileA | K0-D037 |
| 0x960 | 0x1760 | `00 00 52 65 61 64 46 69 6C 65 00` | hint=0 + имя ReadFile | K0-D037 |
| 0x96C | 0x176C | `00 00 43 6C 6F 73 65 48 61 6E 64 6C 65 00` | hint=0 + имя CloseHandle | K0-D037 |

