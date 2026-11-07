# BYTECODE.md — байт-за-байтом разбор hxdump.exe

Паспорт файла: KERNEL/L0-HXDUMP/BYTECODE.md | слой: L0 | роль: полный разбор образа.

Источник истины — `hxdump.hex`. Структура DOS/COFF/опционального заголовков
идентична `KERNEL/L0-SEED/BYTECODE.md` (пояснения каждого поля — там);
здесь приводятся значения и отличия M0-HXDUMP от M0-SEED2.

## 0. Сводка

| Свойство | Значение |
|---|---|
| Размер файла | 3584 байта (0xE00) |
| SHA-256 | F0CEE97E45B1399FF13151BF4587BA2A02465E793FB9C92F525CDD69A7B4A8E3 |
| Точка входа | файл 0x200 (RVA 0x1000, K0-X021) |
| Код | 0x370 байт (RVA 0x1000..0x136F), 240 записей, 39 меток |
| Данные | 0x530 байт @ RVA 0x1370 (буферы, строки, служебные ячейки) |
| Импорты | 0x11A байт @ RVA 0x18D0 (7 функций) |
| Смещение → RVA | заголовки: файл = RVA; секция: RVA = файл − 0x200 + 0x1000 |

## 1. Заголовки (отличия от M0-SEED2)

| Поле | Смещение | Значение | Пояснение |
|---|---|---|---|
| DOS-заглушка | 0x040 | «Universal L0 hxdump. No DOS support.» | текст, 39 байт |
| SizeOfCode | 0x09C | 0xC00 | секция выросла с 0x600 |
| SizeOfImage | 0x0D0 | 0x2000 | 0x1000 + 0xA0A, округлено до 0x1000 |
| DD[1] Import | 0x110 | RVA 0x18D0, размер 0x28 | IDT в секции |
| DD[12] IAT | 0x168 | RVA 0x1918, размер 0x40 | 7 функций + терминатор |
| VirtualSize (.text) | 0x190 | 0xA0A | код + данные + импорты |
| SizeOfRawData | 0x198 | 0xC00 | файл = 0x200 + 0xC00 = 0xE00 |

Импорт kernel32.dll расширен до семи функций: + CreateFileA, ReadFile,
CloseHandle (ветвь F — файловый ввод-вывод). Формулы и порядок работы
загрузчика — `SPEC/04-PE-MINIMAL.md`.

## 2. Раскладка внутри .text

```
RVA 0x1000  код: главный поток, диспетчер, подпрограммы (0x370 байт)
RVA 0x1370  linebuf: буфер строки дампа (77 байт)
RVA 0x13C0  fname: буфер имени файла (128 байт: 127 + NUL)
RVA 0x1440  filebuf: буфер чтения чанка (0x400 байт)
RVA 0x1840  digits: таблица 16 hex-цифр
RVA 0x1850  hstdout/written/nread: служебные ячейки (по 8 байт)
RVA 0x1870  строки: справка, ERR=LONG/OPEN/READ (по 33/27/27/27 байт)
RVA 0x18D0  IDT: описатель импорта kernel32.dll + терминатор
RVA 0x1918  IAT: 7 адресов функций + терминатор (заполняет загрузчик)
RVA 0x1958  INT: копия IAT до заполнения (по ней ищутся имена)
RVA 0x1998  имя DLL; далее hint-записи 7 функций
RVA 0x1A0A  конец содержимого; далее нули до 0x1C00 (VirtualSize 0xA0A)
```

## 3. Код: все инструкции

### Таблица кода (автогенерация из ведомости)
| Файл | RVA | Байты | Мнемоника | Кирпич |
|---|---|---|---|---|
| 0x200 | 0x1000 | `48 83 EC 48` | sub rsp,0x48 (тень + 3 стековых аргумента CreateFileA) | K0-X021 |
| 0x204 | 0x1004 | `48 8D 1D F5 EF FF FF` | lea rbx,[rip+disp] (RBX = база образа (RVA 0)) | K0-S021 |
| 0x20B | 0x100B | `48 C7 C1 F5 FF FF FF` | mov rcx,-11 (STD_OUTPUT_HANDLE) | init |
| 0x212 | 0x1012 | `FF 15 00 09 00 00` | call [rip]GetStdHandle (RAX = хэндл stdout) | init |
| 0x218 | 0x1018 | `48 89 05 31 08 00 00` | mov [rip+hstdout],rax (сохранить хэндл) | init |
| 0x21F | 0x101F | `FF 15 0B 09 00 00` | call [rip]GetCommandLineA (RAX = командная строка) | K0-C011 |
| 0x225 | 0x1025 | `48 89 C7` | mov rdi,rax (RDI = курсор чтения) | K0-C011 |
| 0x228 | 0x1028 | `0F B6 07` | movzx eax,byte [rdi] (первый символ) | K0-C012 |
| 0x22B | 0x102B | `3C 22` | cmp al,'" (кавычка?) | K0-C012 |
| 0x22D | 0x102D | `75 13` | jne s2_unq (путь без кавычек) | K0-C012 |
| 0x22F | 0x102F | `48 FF C7` | inc rdi (пропуск открывающей кавычки) | K0-C012 |
| 0x232 | 0x1032 | `0F B6 07` | movzx eax,byte [rdi] | K0-C012 |
| 0x235 | 0x1035 | `84 C0` | test al,al | K0-C012 |
| 0x237 | 0x1037 | `74 30` | jz noargs (конец строки — аргументов нет) | K0-C012 |
| 0x239 | 0x1039 | `3C 22` | cmp al,'" | K0-C012 |
| 0x23B | 0x103B | `74 27` | je s2_adv (закрывающая кавычка: пропустить её и разделители) | K0-C012 |
| 0x23D | 0x103D | `48 FF C7` | inc rdi | K0-C012 |
| 0x240 | 0x1040 | `EB F0` | jmp s2_quote | K0-C012 |
| 0x242 | 0x1042 | `84 C0` | test al,al | K0-C012 |
| 0x244 | 0x1044 | `74 23` | jz noargs | K0-C012 |
| 0x246 | 0x1046 | `3C 20` | cmp al,' (пробел) | K0-C012 |
| 0x248 | 0x1048 | `74 09` | je s2_delims | K0-C012 |
| 0x24A | 0x104A | `3C 09` | cmp al,9 (табуляция) | K0-C012 |
| 0x24C | 0x104C | `74 05` | je s2_delims | K0-C012 |
| 0x24E | 0x104E | `48 FF C7` | inc rdi | K0-C012 |
| 0x251 | 0x1051 | `EB D5` | jmp skip_argv0 | K0-C012 |
| 0x253 | 0x1053 | `0F B6 07` | movzx eax,byte [rdi] | K0-C012 |
| 0x256 | 0x1056 | `84 C0` | test al,al | K0-C012 |
| 0x258 | 0x1058 | `74 0F` | jz noargs | K0-C012 |
| 0x25A | 0x105A | `3C 20` | cmp al,' | K0-C012 |
| 0x25C | 0x105C | `74 06` | je s2_adv | K0-C012 |
| 0x25E | 0x105E | `3C 09` | cmp al,9 | K0-C012 |
| 0x260 | 0x1060 | `74 02` | je s2_adv | K0-C012 |
| 0x262 | 0x1062 | `EB 14` | jmp word_start (начало слова команды) | K0-C012 |
| 0x264 | 0x1064 | `48 FF C7` | inc rdi | K0-C012 |
| 0x267 | 0x1067 | `EB EA` | jmp s2_delims | K0-C012 |
| 0x269 | 0x1069 | `E8 DC 02 00 00` | call print_usage (справка |  |
| 0x26E | 0x106E | `B9 02 00 00 00` | mov ecx,2 (код возврата: нет аргумента) | K0-X022 |
| 0x273 | 0x1073 | `E9 AF 00 00 00` | jmp exit_proc | K0-G021 |
| 0x278 | 0x1078 | `48 89 FE` | mov rsi,rdi (RSI = слово) | K0-C013 |
| 0x27B | 0x107B | `0F B6 07` | movzx eax,byte [rdi] | K0-C013 |
| 0x27E | 0x107E | `84 C0` | test al,al | K0-C013 |
| 0x280 | 0x1080 | `74 0D` | jz rw_end | K0-C013 |
| 0x282 | 0x1082 | `3C 20` | cmp al,' | K0-C013 |
| 0x284 | 0x1084 | `74 09` | je rw_end | K0-C013 |
| 0x286 | 0x1086 | `3C 09` | cmp al,9 | K0-C013 |
| 0x288 | 0x1088 | `74 05` | je rw_end | K0-C013 |
| 0x28A | 0x108A | `48 FF C7` | inc rdi | K0-C013 |
| 0x28D | 0x108D | `EB EC` | jmp rw_loop | K0-C013 |
| 0x28F | 0x108F | `E8 6D 01 00 00` | call copy_word (K0-C014 |  |
| 0x294 | 0x1094 | `48 85 C0` | test rax,rax | K0-G021 |
| 0x297 | 0x1097 | `0F 85 36 00 00 00` | jnz err_long (имя длиннее 127 байт) | K0-G021 |
| 0x29D | 0x109D | `48 8D 0D 1C 03 00 00` | lea rcx,[rip+fname] (имя файла, NUL-terminated) | K0-G021 |
| 0x2A4 | 0x10A4 | `E8 11 01 00 00` | call open_file_read (K0-F001 |  |
| 0x2A9 | 0x10A9 | `48 83 F8 FF` | cmp rax,-1 (INVALID_HANDLE_VALUE?) | K0-G021 |
| 0x2AD | 0x10AD | `0F 84 3C 00 00 00` | je err_open (файл не открыт) | K0-G021 |
| 0x2B3 | 0x10B3 | `49 89 C4` | mov r12,rax (R12 = хэндл файла) | K0-G021 |
| 0x2B6 | 0x10B6 | `E8 73 00 00 00` | call dump_loop (K0-B001 |  |
| 0x2BB | 0x10BB | `48 85 C0` | test rax,rax | K0-G021 |
| 0x2BE | 0x10BE | `0F 85 47 00 00 00` | jnz err_read | K0-G021 |
| 0x2C4 | 0x10C4 | `4C 89 E1` | mov rcx,r12 | K0-G021 |
| 0x2C7 | 0x10C7 | `E8 26 01 00 00` | call close_file (K0-F003) | K0-G021 |
| 0x2CC | 0x10CC | `31 C9` | xor ecx,ecx (код возврата 0: успех) | K0-X022 |
| 0x2CE | 0x10CE | `E9 54 00 00 00` | jmp exit_proc | K0-G021 |
| 0x2D3 | 0x10D3 | `48 8D 15 B7 07 00 00` | lea rdx,[rip+err_long_str] | K0-G021 |
| 0x2DA | 0x10DA | `41 B8 1B 00 00 00` | mov r8d,27 (длина строки ошибки) | K0-G021 |
| 0x2E0 | 0x10E0 | `E8 3F 02 00 00` | call print_line (K0-P021) | K0-G021 |
| 0x2E5 | 0x10E5 | `B9 03 00 00 00` | mov ecx,3 (код: имя слишком длинное) | K0-X022 |
| 0x2EA | 0x10EA | `E9 38 00 00 00` | jmp exit_proc | K0-G021 |
| 0x2EF | 0x10EF | `48 8D 15 B6 07 00 00` | lea rdx,[rip+err_open_str] | K0-G021 |
| 0x2F6 | 0x10F6 | `41 B8 1B 00 00 00` | mov r8d,27 | K0-G021 |
| 0x2FC | 0x10FC | `E8 23 02 00 00` | call print_line | K0-G021 |
| 0x301 | 0x1101 | `B9 04 00 00 00` | mov ecx,4 (код: файл не открыт) | K0-X022 |
| 0x306 | 0x1106 | `E9 1C 00 00 00` | jmp exit_proc | K0-G021 |
| 0x30B | 0x110B | `48 8D 15 B5 07 00 00` | lea rdx,[rip+err_read_str] | K0-G021 |
| 0x312 | 0x1112 | `41 B8 1B 00 00 00` | mov r8d,27 | K0-G021 |
| 0x318 | 0x1118 | `E8 07 02 00 00` | call print_line | K0-G021 |
| 0x31D | 0x111D | `B9 05 00 00 00` | mov ecx,5 (код: ошибка чтения) | K0-X022 |
| 0x322 | 0x1122 | `E9 00 00 00 00` | jmp exit_proc | K0-G021 |
| 0x327 | 0x1127 | `FF 15 FB 07 00 00` | call [rip]ExitProcess (завершение |  |
| 0x32D | 0x112D | `CC` | int3 (страховка) | K0-X022 |
| 0x32E | 0x112E | `45 31 FF` | xor r15d,r15d (R15 = абсолютное смещение в файле = 0) | K0-B001 |
| 0x331 | 0x1131 | `E8 42 00 00 00` | call read_chunk (K0-F002 |  |
| 0x336 | 0x1136 | `48 83 F8 FF` | cmp rax,-1 | K0-B001 |
| 0x33A | 0x113A | `74 36` | je dl_rerr (ошибка чтения) | K0-B001 |
| 0x33C | 0x113C | `48 85 C0` | test rax,rax | K0-B001 |
| 0x33F | 0x113F | `74 2E` | jz dl_done (конец файла) | K0-B001 |
| 0x341 | 0x1141 | `49 89 C6` | mov r14,rax (R14 = байтов в чанке) | K0-B001 |
| 0x344 | 0x1144 | `48 8D 3D F5 02 00 00` | lea rdi,[rip+filebuf] (RDI = курсор данных) | K0-B001 |
| 0x34B | 0x114B | `45 85 F6` | test r14d,r14d | K0-B001 |
| 0x34E | 0x114E | `74 E1` | jz dl_read (чанк исчерпан — читать следующий) | K0-B001 |
| 0x350 | 0x1150 | `41 BD 10 00 00 00` | mov r13d,16 (байт в строке по умолчанию) | K0-B001 |
| 0x356 | 0x1156 | `41 83 FE 10` | cmp r14d,16 | K0-B001 |
| 0x35A | 0x115A | `73 03` | jae dl_full (полная строка) | K0-B001 |
| 0x35C | 0x115C | `45 89 F5` | mov r13d,r14d (R13 = остаток < 16) | K0-B001 |
| 0x35F | 0x115F | `E8 DD 00 00 00` | call build_line (K0-B002 |  |
| 0x364 | 0x1164 | `4C 01 EF` | add rdi,r13 | K0-B001 |
| 0x367 | 0x1167 | `4D 01 EF` | add r15,r13 | K0-B001 |
| 0x36A | 0x116A | `4D 29 EE` | sub r14,r13 | K0-B001 |
| 0x36D | 0x116D | `EB DC` | jmp dl_lines | K0-B001 |
| 0x36F | 0x116F | `31 C0` | xor eax,eax (успех) | K0-B001 |
| 0x371 | 0x1171 | `C3` | ret | K0-B001 |
| 0x372 | 0x1172 | `B8 01 00 00 00` | mov eax,1 (ошибка чтения) | K0-B001 |
| 0x377 | 0x1177 | `C3` | ret | K0-B001 |
| 0x378 | 0x1178 | `48 83 EC 28` | sub rsp,0x28 (кадр: тень + 5-й аргумент) | K0-F002 |
| 0x37C | 0x117C | `4C 89 E1` | mov rcx,r12 (хэндл) | K0-F002 |
| 0x37F | 0x117F | `48 8D 15 BA 02 00 00` | lea rdx,[rip+filebuf] (буфер) | K0-F002 |
| 0x386 | 0x1186 | `41 B8 00 04 00 00` | mov r8d,0x400 (размер чанка 1024) | K0-F002 |
| 0x38C | 0x118C | `4C 8D 0D CD 06 00 00` | lea r9,[rip+nread] (куда писать счётчик) | K0-F002 |
| 0x393 | 0x1193 | `48 C7 44 24 20 00 00 00 00` | mov qword [rsp+0x20],0 (5-й аргумент NULL) | K0-F002 |
| 0x39C | 0x119C | `FF 15 9E 07 00 00` | call [rip]ReadFile | K0-F002 |
| 0x3A2 | 0x11A2 | `48 83 C4 28` | add rsp,0x28 | K0-F002 |
| 0x3A6 | 0x11A6 | `48 85 C0` | test rax,rax (BOOL: 0 = ошибка) | K0-F002 |
| 0x3A9 | 0x11A9 | `75 08` | jnz rc_ok (BOOL не ноль — успех) | K0-F002 |
| 0x3AB | 0x11AB | `48 C7 C0 FF FF FF FF` | mov rax,-1 | K0-F002 |
| 0x3B2 | 0x11B2 | `C3` | ret | K0-F002 |
| 0x3B3 | 0x11B3 | `8B 05 A7 06 00 00` | mov eax,[rip+nread] (RAX = число прочитанных байт) | K0-F002 |
| 0x3B9 | 0x11B9 | `C3` | ret | K0-F002 |
| 0x3BA | 0x11BA | `48 83 EC 38` | sub rsp,0x38 (кадр: тень + 3 стековых аргумента) | K0-F001 |
| 0x3BE | 0x11BE | `BA 00 00 00 80` | mov edx,0x80000000 (dwDesiredAccess = GENERIC_READ) | K0-F001 |
| 0x3C3 | 0x11C3 | `41 B8 01 00 00 00` | mov r8d,1 (dwShareMode = FILE_SHARE_READ) | K0-F001 |
| 0x3C9 | 0x11C9 | `45 31 C9` | xor r9d,r9d (lpSecurityAttributes = NULL) | K0-F001 |
| 0x3CC | 0x11CC | `48 C7 44 24 20 03 00 00 00` | mov qword [rsp+0x20],3 (dwCreationDisposition = OPEN_EXISTING) | K0-F001 |
| 0x3D5 | 0x11D5 | `48 C7 44 24 28 80 00 00 00` | mov qword [rsp+0x28],0x80 (dwFlagsAndAttributes = FILE_ATTRIBUTE_NORMAL) | K0-F001 |
| 0x3DE | 0x11DE | `48 C7 44 24 30 00 00 00 00` | mov qword [rsp+0x30],0 (hTemplateFile = NULL) | K0-F001 |
| 0x3E7 | 0x11E7 | `FF 15 4B 07 00 00` | call [rip]CreateFileA (RAX = хэндл | -1) |
| 0x3ED | 0x11ED | `48 83 C4 38` | add rsp,0x38 | K0-F001 |
| 0x3F1 | 0x11F1 | `C3` | ret | K0-F001 |
| 0x3F2 | 0x11F2 | `48 83 EC 28` | sub rsp,0x28 (кадр для вызова) | K0-F003 |
| 0x3F6 | 0x11F6 | `FF 15 4C 07 00 00` | call [rip]CloseHandle (хэндл в RCX) | K0-F003 |
| 0x3FC | 0x11FC | `48 83 C4 28` | add rsp,0x28 | K0-F003 |
| 0x400 | 0x1200 | `C3` | ret | K0-F003 |
| 0x401 | 0x1201 | `48 8D 05 B8 01 00 00` | lea rax,[rip+fname] (начало буфера имён) | K0-C014 |
| 0x408 | 0x1208 | `49 89 C2` | mov r10,rax (R10 = курсор записи) | K0-C014 |
| 0x40B | 0x120B | `48 39 FE` | cmp rsi,rdi (слово скопировано полностью?) | K0-C014 |
| 0x40E | 0x120E | `74 20` | je cw_done | K0-C014 |
| 0x410 | 0x1210 | `48 8D 15 A9 01 00 00` | lea rdx,[rip+fname] | K0-C014 |
| 0x417 | 0x1217 | `4C 89 D0` | mov rax,r10 | K0-C014 |
| 0x41A | 0x121A | `48 29 D0` | sub rax,rdx (RAX = скопировано байт) | K0-C014 |
| 0x41D | 0x121D | `48 83 F8 7F` | cmp rax,0x7F (буфер заполнен до предела?) | K0-C014 |
| 0x421 | 0x1221 | `73 13` | jae cw_long (слово длиннее 127 — дальше некуда) | K0-C014 |
| 0x423 | 0x1223 | `8A 16` | mov dl,[rsi] | K0-C014 |
| 0x425 | 0x1225 | `41 88 12` | mov [r10],dl | K0-C014 |
| 0x428 | 0x1228 | `48 FF C6` | inc rsi | K0-C014 |
| 0x42B | 0x122B | `49 FF C2` | inc r10 | K0-C014 |
| 0x42E | 0x122E | `EB DB` | jmp cw_loop | K0-C014 |
| 0x430 | 0x1230 | `31 C0` | xor eax,eax (флаг 0 |  |
| 0x432 | 0x1232 | `41 88 02` | mov [r10],al (NUL-терминатор) | K0-C014 |
| 0x435 | 0x1235 | `C3` | ret | K0-C014 |
| 0x436 | 0x1236 | `31 D2` | xor edx,edx (DL = 0) | K0-C014 |
| 0x438 | 0x1238 | `41 88 12` | mov [r10],dl (NUL на границе буфера) | K0-C014 |
| 0x43B | 0x123B | `B8 01 00 00 00` | mov eax,1 (флаг: слово длиннее 127) | K0-C014 |
| 0x440 | 0x1240 | `C3` | ret | K0-C014 |
| 0x441 | 0x1241 | `48 8D 35 28 01 00 00` | lea rsi,[rip+linebuf] (курсор записи строки) | K0-B002 |
| 0x448 | 0x1248 | `44 89 F8` | mov eax,r15d (смещение строки) | K0-B002 |
| 0x44B | 0x124B | `48 8D 15 1E 01 00 00` | lea rdx,[rip+linebuf] (поле 8 цифр смещения) | K0-B002 |
| 0x452 | 0x1252 | `E8 78 00 00 00` | call hex32_to_ascii8 (K0-H021 |  |
| 0x457 | 0x1257 | `B0 3A` | mov al,':' | K0-B002 |
| 0x459 | 0x1259 | `88 06` | mov [rsi],al | K0-B002 |
| 0x45B | 0x125B | `48 FF C6` | inc rsi | K0-B002 |
| 0x45E | 0x125E | `B0 20` | mov al,' (пробел) | K0-B002 |
| 0x460 | 0x1260 | `88 06` | mov [rsi],al | K0-B002 |
| 0x462 | 0x1262 | `48 FF C6` | inc rsi | K0-B002 |
| 0x465 | 0x1265 | `49 89 FA` | mov r10,rdi (курсор чтения hex-части) | K0-B002 |
| 0x468 | 0x1268 | `44 89 E9` | mov ecx,r13d (счётчик байт) | K0-B002 |
| 0x46B | 0x126B | `41 0F B6 12` | movzx edx,byte [r10] | K0-B002 |
| 0x46F | 0x126F | `E8 82 00 00 00` | call hex8_to_ascii2 (K0-H022 |  |
| 0x474 | 0x1274 | `B0 20` | mov al,' (пробел после байта) | K0-B002 |
| 0x476 | 0x1276 | `88 06` | mov [rsi],al | K0-B002 |
| 0x478 | 0x1278 | `48 FF C6` | inc rsi | K0-B002 |
| 0x47B | 0x127B | `49 FF C2` | inc r10 | K0-B002 |
| 0x47E | 0x127E | `FF C9` | dec ecx | K0-B002 |
| 0x480 | 0x1280 | `75 E9` | jnz bl_hex | K0-B002 |
| 0x482 | 0x1282 | `B0 20` | mov al,' (разделитель перед ASCII) | K0-B002 |
| 0x484 | 0x1284 | `88 06` | mov [rsi],al | K0-B002 |
| 0x486 | 0x1286 | `48 FF C6` | inc rsi | K0-B002 |
| 0x489 | 0x1289 | `49 89 FA` | mov r10,rdi (курсор чтения ASCII-части) | K0-B002 |
| 0x48C | 0x128C | `44 89 E9` | mov ecx,r13d | K0-B002 |
| 0x48F | 0x128F | `41 0F B6 02` | movzx eax,byte [r10] | K0-B002 |
| 0x493 | 0x1293 | `3C 20` | cmp al,0x20 (ниже пробела — непечатное) | K0-B002 |
| 0x495 | 0x1295 | `72 04` | jb bl_dot | K0-B002 |
| 0x497 | 0x1297 | `3C 7E` | cmp al,0x7E (выше '~' — непечатное) | K0-B002 |
| 0x499 | 0x1299 | `76 02` | jbe bl_put (печатное: 0x20..0x7E) | K0-B002 |
| 0x49B | 0x129B | `B0 2E` | mov al,'. (замена непечатного) | K0-B002 |
| 0x49D | 0x129D | `88 06` | mov [rsi],al | K0-B002 |
| 0x49F | 0x129F | `48 FF C6` | inc rsi | K0-B002 |
| 0x4A2 | 0x12A2 | `49 FF C2` | inc r10 | K0-B002 |
| 0x4A5 | 0x12A5 | `FF C9` | dec ecx | K0-B002 |
| 0x4A7 | 0x12A7 | `75 E6` | jnz bl_asc | K0-B002 |
| 0x4A9 | 0x12A9 | `B0 0D` | mov al,0x0D (CR) | K0-B002 |
| 0x4AB | 0x12AB | `88 06` | mov [rsi],al | K0-B002 |
| 0x4AD | 0x12AD | `48 FF C6` | inc rsi | K0-B002 |
| 0x4B0 | 0x12B0 | `B0 0A` | mov al,0x0A (LF) | K0-B002 |
| 0x4B2 | 0x12B2 | `88 06` | mov [rsi],al | K0-B002 |
| 0x4B4 | 0x12B4 | `48 FF C6` | inc rsi | K0-B002 |
| 0x4B7 | 0x12B7 | `45 89 E8` | mov r8d,r13d (длина = f(n)) | K0-B002 |
| 0x4BA | 0x12BA | `41 C1 E0 02` | shl r8d,2 (n*4) | K0-B002 |
| 0x4BE | 0x12BE | `41 83 C0 0D` | add r8d,13 (+ 13 байт служебных) | K0-B002 |
| 0x4C2 | 0x12C2 | `48 8D 15 A7 00 00 00` | lea rdx,[rip+linebuf] | K0-B002 |
| 0x4C9 | 0x12C9 | `E8 56 00 00 00` | call print_line (K0-P021) | K0-B002 |
| 0x4CE | 0x12CE | `C3` | ret | K0-B002 |
| 0x4CF | 0x12CF | `48 89 D6` | mov rsi,rdx (курсор hex-поля) | K0-H021 |
| 0x4D2 | 0x12D2 | `4C 8D 05 67 05 00 00` | lea r8,[rip+digits] (таблица 16 цифр) | K0-H021 |
| 0x4D9 | 0x12D9 | `B9 08 00 00 00` | mov ecx,8 | K0-H021 |
| 0x4DE | 0x12DE | `C1 C0 04` | rol eax,4 (старшая тетрада вниз) | K0-H021 |
| 0x4E1 | 0x12E1 | `48 89 C2` | mov rdx,rax | K0-H021 |
| 0x4E4 | 0x12E4 | `83 E2 0F` | and edx,0xF (номер цифры) | K0-H021 |
| 0x4E7 | 0x12E7 | `41 0F B6 14 10` | movzx rdx,byte [r8+rdx] (символ цифры) | K0-H021 |
| 0x4EC | 0x12EC | `88 16` | mov [rsi],dl (запись цифры) | K0-H021 |
| 0x4EE | 0x12EE | `48 FF C6` | inc rsi | K0-H021 |
| 0x4F1 | 0x12F1 | `FF C9` | dec ecx | K0-H021 |
| 0x4F3 | 0x12F3 | `75 E9` | jnz h_loop | K0-H021 |
| 0x4F5 | 0x12F5 | `C3` | ret | K0-H021 |
| 0x4F6 | 0x12F6 | `0F B6 C2` | movzx eax,dl (EAX = байт) | K0-H022 |
| 0x4F9 | 0x12F9 | `41 89 C3` | mov r11d,eax (копия байта) | K0-H022 |
| 0x4FC | 0x12FC | `C0 C0 04` | rol al,4 (старшая тетрада байта вниз, 8-битная ротация) | K0-H022 |
| 0x4FF | 0x12FF | `89 C2` | mov edx,eax | K0-H022 |
| 0x501 | 0x1301 | `83 E2 0F` | and edx,0xF | K0-H022 |
| 0x504 | 0x1304 | `4C 8D 05 35 05 00 00` | lea r8,[rip+digits] | K0-H022 |
| 0x50B | 0x130B | `41 0F B6 14 10` | movzx rdx,byte [r8+rdx] (символ старшей цифры) | K0-H022 |
| 0x510 | 0x1310 | `88 16` | mov [rsi],dl | K0-H022 |
| 0x512 | 0x1312 | `48 FF C6` | inc rsi | K0-H022 |
| 0x515 | 0x1315 | `41 83 E3 0F` | and r11d,0xF (младшая тетрада) | K0-H022 |
| 0x519 | 0x1319 | `43 0F B6 14 03` | movzx edx,byte [r8+r11] (символ младшей цифры) | K0-H022 |
| 0x51E | 0x131E | `88 16` | mov [rsi],dl | K0-H022 |
| 0x520 | 0x1320 | `48 FF C6` | inc rsi | K0-H022 |
| 0x523 | 0x1323 | `C3` | ret | K0-H022 |
| 0x524 | 0x1324 | `48 83 EC 28` | sub rsp,0x28 (кадр: тень + выравнивание) | K0-P021 |
| 0x528 | 0x1328 | `48 8B 0D 21 05 00 00` | mov rcx,[rip+hstdout] (хэндл вывода) | K0-P021 |
| 0x52F | 0x132F | `4C 8D 0D 22 05 00 00` | lea r9,[rip+written] (куда писать счётчик) | K0-P021 |
| 0x536 | 0x1336 | `48 C7 44 24 20 00 00 00 00` | mov qword [rsp+0x20],0 (5-й аргумент NULL) | K0-P021 |
| 0x53F | 0x133F | `FF 15 DB 05 00 00` | call [rip]WriteFile | K0-P021 |
| 0x545 | 0x1345 | `48 83 C4 28` | add rsp,0x28 | K0-P021 |
| 0x549 | 0x1349 | `C3` | ret | K0-P021 |
| 0x54A | 0x134A | `48 83 EC 28` | sub rsp,0x28 (кадр для вызова) | K0-U021 |
| 0x54E | 0x134E | `48 8D 15 1B 05 00 00` | lea rdx,[rip+usage_str] | K0-U021 |
| 0x555 | 0x1355 | `41 B8 21 00 00 00` | mov r8d,33 (длина справки (инвариант)) | K0-U021 |
| 0x55B | 0x135B | `E8 C4 FF FF FF` | call print_line | K0-U021 |
| 0x560 | 0x1360 | `48 83 C4 28` | add rsp,0x28 | K0-U021 |
| 0x564 | 0x1364 | `C3` | ret | K0-U021 |



## 4. Поток исполнения (по кирпичам)

1. **K0-X021 → K0-S021 → init.** Кадр 0x48 (тень + 0x28 под три стековых
   аргумента CreateFileA); RBX = база; GetStdHandle → `hstdout`;
   GetCommandLineA → RDI.
2. **K0-C012 skip_argv0** (реинкарнация K0-C002): пропуск argv[0] с
   кавычками; пустая строка → `noargs` (справка K0-U021, код 2).
3. **K0-C013 read_word** (реинкарнация K0-C003): RSI = начало слова,
   RDI = за словом.
4. **K0-C014 copy_word.** Копирует слово в `fname` + NUL; RAX = 0 ок,
   RAX = 1 — длиннее 127 → `err_long` (код 3).
5. **K0-F001 open_file_read.** CreateFileA(GENERIC_READ, SHARE_READ,
   NULL, OPEN_EXISTING, NORMAL, NULL); аргументы 5–7 на стеке
   [rsp+0x20..0x30]. RAX = хэндл | −1 → `err_open` (код 4).
6. **K0-B001 dump_loop.** Чанки по 0x400 (K0-F002): RAX = байты | −1
   (→ `err_read`, код 5). R14 — остаток, R15 — смещение, R13 =
   min(16, R14), RDI — курсор; K0-B002 печатает строку.
7. **K0-F003 close_file** и код возврата 0.

## 5. Формат строки дампа (инвариант K0-B002)

`XXXXXXXX: XX XX ... XX  AAAA...
` — 8 hex-цифр смещения (K0-H021),
«: », N × «XX » (K0-H022), пробел, N символов ASCII (байт 0x20..0x7E
как есть, иначе «.»), CRLF. Длина = 13 + 4×N (N=16 → 77 байт);
вычисляется арифметически: shl r8d,2 + 13 — буфер не сканируется.

## 6. Расчёт rip-смещений (цель − конец инструкции)

### Таблица rip-смещений (цель − конец инструкции)
| Инструкция | RVA конца | Цель | Цель RVA | disp32 |
|---|---|---|---|---|
| lea/mov/call [rip] @ 0x204 | 0x100B | BASE0 | 0x0 | 0x100B |
| lea/mov/call [rip] @ 0x212 | 0x1018 | IAT_GSH | 0x1918 | +0x900 |
| lea/mov/call [rip] @ 0x218 | 0x101F | hstdout | 0x1850 | +0x831 |
| lea/mov/call [rip] @ 0x21F | 0x1025 | IAT_GCLA | 0x1930 | +0x90B |
| lea/mov/call [rip] @ 0x29D | 0x10A4 | fname | 0x13C0 | +0x31C |
| lea/mov/call [rip] @ 0x2D3 | 0x10DA | err_long_str | 0x1891 | +0x7B7 |
| lea/mov/call [rip] @ 0x2EF | 0x10F6 | err_open_str | 0x18AC | +0x7B6 |
| lea/mov/call [rip] @ 0x30B | 0x1112 | err_read_str | 0x18C7 | +0x7B5 |
| lea/mov/call [rip] @ 0x327 | 0x112D | IAT_EP | 0x1928 | +0x7FB |
| lea/mov/call [rip] @ 0x344 | 0x114B | filebuf | 0x1440 | +0x2F5 |
| lea/mov/call [rip] @ 0x37F | 0x1186 | filebuf | 0x1440 | +0x2BA |
| lea/mov/call [rip] @ 0x38C | 0x1193 | nread | 0x1860 | +0x6CD |
| lea/mov/call [rip] @ 0x39C | 0x11A2 | IAT_RF | 0x1940 | +0x79E |
| lea/mov/call [rip] @ 0x3B3 | 0x11B9 | nread | 0x1860 | +0x6A7 |
| lea/mov/call [rip] @ 0x3E7 | 0x11ED | IAT_CFA | 0x1938 | +0x74B |
| lea/mov/call [rip] @ 0x3F6 | 0x11FC | IAT_CH | 0x1948 | +0x74C |
| lea/mov/call [rip] @ 0x401 | 0x1208 | fname | 0x13C0 | +0x1B8 |
| lea/mov/call [rip] @ 0x410 | 0x1217 | fname | 0x13C0 | +0x1A9 |
| lea/mov/call [rip] @ 0x441 | 0x1248 | linebuf | 0x1370 | +0x128 |
| lea/mov/call [rip] @ 0x44B | 0x1252 | linebuf | 0x1370 | +0x11E |
| lea/mov/call [rip] @ 0x4C2 | 0x12C9 | linebuf | 0x1370 | +0xA7 |
| lea/mov/call [rip] @ 0x4D2 | 0x12D9 | digits | 0x1840 | +0x567 |
| lea/mov/call [rip] @ 0x504 | 0x130B | digits | 0x1840 | +0x535 |
| lea/mov/call [rip] @ 0x528 | 0x132F | hstdout | 0x1850 | +0x521 |
| lea/mov/call [rip] @ 0x52F | 0x1336 | written | 0x1858 | +0x522 |
| lea/mov/call [rip] @ 0x53F | 0x1345 | IAT_WF | 0x1920 | +0x5DB |
| lea/mov/call [rip] @ 0x54E | 0x1355 | usage_str | 0x1870 | +0x51B |


## 7. Метки кода

### Метки кода
| Метка | RVA | Файл |
|---|---|---|
| entry | 0x1000 | 0x200 |
| skip_argv0 | 0x1028 | 0x228 |
| s2_quote | 0x1032 | 0x232 |
| s2_unq | 0x1042 | 0x242 |
| s2_delims | 0x1053 | 0x253 |
| s2_adv | 0x1064 | 0x264 |
| noargs | 0x1069 | 0x269 |
| word_start | 0x1078 | 0x278 |
| rw_loop | 0x107B | 0x27B |
| rw_end | 0x108F | 0x28F |
| err_long | 0x10D3 | 0x2D3 |
| err_open | 0x10EF | 0x2EF |
| err_read | 0x110B | 0x30B |
| exit_proc | 0x1127 | 0x327 |
| dump_loop | 0x112E | 0x32E |
| dl_read | 0x1131 | 0x331 |
| dl_lines | 0x114B | 0x34B |
| dl_full | 0x115F | 0x35F |
| dl_done | 0x116F | 0x36F |
| dl_rerr | 0x1172 | 0x372 |
| read_chunk | 0x1178 | 0x378 |
| rc_err | 0x11AB | 0x3AB |
| rc_ok | 0x11B3 | 0x3B3 |
| open_file_read | 0x11BA | 0x3BA |
| close_file | 0x11F2 | 0x3F2 |
| copy_word | 0x1201 | 0x401 |
| cw_loop | 0x120B | 0x40B |
| cw_done | 0x1230 | 0x430 |
| cw_long | 0x1236 | 0x436 |
| build_line | 0x1241 | 0x441 |
| bl_hex | 0x126B | 0x46B |
| bl_asc | 0x128F | 0x48F |
| bl_dot | 0x129B | 0x49B |
| bl_put | 0x129D | 0x49D |
| hex32_to_ascii8 | 0x12CF | 0x4CF |
| h_loop | 0x12DE | 0x4DE |
| hex8_to_ascii2 | 0x12F6 | 0x4F6 |
| print_line | 0x1324 | 0x524 |
| print_usage | 0x134A | 0x54A |



## 8. Данные

### Данные
| Метка | Файл | RVA | Длина | Комментарий |
|---|---|---|---|---|
| linebuf | 0x570 | 0x1370 | 77 | нулевая заливка () |
| fname | 0x5C0 | 0x13C0 | 128 | нулевая заливка () |
| filebuf | 0x640 | 0x1440 | 1024 | нулевая заливка () |
| digits | 0xA40 | 0x1840 | 16 | таблица 16 hex-цифр (K0-D024) |
| hstdout | 0xA50 | 0x1850 | 8 | нулевая заливка () |
| written | 0xA58 | 0x1858 | 8 | нулевая заливка () |
| nread | 0xA60 | 0x1860 | 8 | нулевая заливка () |
| usage_str | 0xA70 | 0x1870 | 33 | справка (33 байта) (K0-D025) |
| err_long_str | 0xA91 | 0x1891 | 27 | ошибка: имя длиннее 127 (27) (K0-D025) |
| err_open_str | 0xAAC | 0x18AC | 27 | ошибка: файл не открыт (27) (K0-D025) |
| err_read_str | 0xAC7 | 0x18C7 | 27 | ошибка чтения (27) (K0-D025) |
| IDT | 0xAF0 | 0x18F0 | 20 | описатель импорта (INT, время, цепочка, имя, IAT) (K0-D026) |
| — | 0xB04 | 0x1904 | 20 | нулевая заливка () |
| IAT_GSH | 0xB18 | 0x1918 | 8 | IAT[0] GetStdHandle (RVA + нули до qword) (K0-D026) |
| IAT_WF | 0xB20 | 0x1920 | 8 | IAT[1] WriteFile (K0-D026) |
| IAT_EP | 0xB28 | 0x1928 | 8 | IAT[2] ExitProcess (K0-D026) |
| IAT_GCLA | 0xB30 | 0x1930 | 8 | IAT[3] GetCommandLineA (K0-D026) |
| IAT_CFA | 0xB38 | 0x1938 | 8 | IAT[4] CreateFileA (K0-D026) |
| IAT_RF | 0xB40 | 0x1940 | 8 | IAT[5] ReadFile (K0-D026) |
| IAT_CH | 0xB48 | 0x1948 | 8 | IAT[6] CloseHandle (K0-D026) |
| — | 0xB50 | 0x1950 | 8 | нулевая заливка () |
| INT_GSH | 0xB58 | 0x1958 | 8 | INT[0] (копия IAT до заполнения) (K0-D026) |
| INT_WF | 0xB60 | 0x1960 | 8 | INT[1] (K0-D026) |
| INT_EP | 0xB68 | 0x1968 | 8 | INT[2] (K0-D026) |
| INT_GCLA | 0xB70 | 0x1970 | 8 | INT[3] (K0-D026) |
| INT_CFA | 0xB78 | 0x1978 | 8 | INT[4] (K0-D026) |
| INT_RF | 0xB80 | 0x1980 | 8 | INT[5] (K0-D026) |
| INT_CH | 0xB88 | 0x1988 | 8 | INT[6] (K0-D026) |
| — | 0xB90 | 0x1990 | 8 | нулевая заливка () |
| DLLNAME | 0xB98 | 0x1998 | 13 | имя DLL (K0-D026) |
| — | 0xBA5 | 0x19A5 | 1 | нулевая заливка () |
| HINT_GSH | 0xBA6 | 0x19A6 | 15 | hint=0 + имя (K0-D026) |
| — | 0xBB5 | 0x19B5 | 1 | нулевая заливка () |
| HINT_WF | 0xBB6 | 0x19B6 | 12 | hint=0 + имя (K0-D026) |
| HINT_EP | 0xBC2 | 0x19C2 | 14 | hint=0 + имя (K0-D026) |
| HINT_GCLA | 0xBD0 | 0x19D0 | 18 | hint=0 + имя (K0-D026) |
| HINT_CFA | 0xBE2 | 0x19E2 | 14 | hint=0 + имя (K0-D026) |
| HINT_RF | 0xBF0 | 0x19F0 | 11 | hint=0 + имя (K0-D026) |
| — | 0xBFB | 0x19FB | 1 | нулевая заливка () |
| HINT_CH | 0xBFC | 0x19FC | 14 | hint=0 + имя (K0-D026) |



### Инварианты кода и данных

1. Длина usage-строки = 33 — зашита в `mov r8d,33`.
2. Длина каждой строки ошибки = 27 — зашита в `mov r8d,27`.
3. Размер чанка чтения = 0x400 — зашит в `mov r8d,0x400`.
4. Максимум байт в строке = 16 — зашит в `mov r13d,16` и `cmp r14d,16`.
5. Предел длины имени = 127 — зашит в `cmp rax,0x7F`.
6. Регистровые соглашения модуля: RBX — база образа; RDI — курсор
   чтения; RSI — курсор записи; R10 — рабочий курсор подпрограмм;
   R11 — копия байта в K0-H022; R12 — хэндл файла; R13 — байт в строке;
   R14 — остаток чанка; R15 — абсолютное смещение. RCX/RDX/R8/R9/RAX —
   волатильные (передача аргументов Win64).

## 9. Импорты

| Метка | Файл | RVA | Комментарий |
|---|---|---|---|
| IDT | 0x18D0-файл 0xAD0 | 0x18D0 | K0-D026: описатель импорта |
| IAT | 0x1918-файл 0xB18 | 0x1918 | K0-D026: IAT (7 функций + терминатор) |
| INT | 0x1958-файл 0xB58 | 0x1958 | K0-D026: INT (копия IAT до заполнения) |
| DLLNAME | 0x1998-файл 0xB98 | 0x1998 | K0-D026: «kernel32.dll\0» |
| hint-записи | 0x19A6.. | 0x19A6+ | K0-D026: hint=0 + имена 7 функций |

| Индекс IAT | RVA | Функция |
|---|---|---|
| [0] | 0x1918 | GetStdHandle |
| [1] | 0x1920 | WriteFile |
| [2] | 0x1928 | ExitProcess |
| [3] | 0x1930 | GetCommandLineA |
| [4] | 0x1938 | CreateFileA |
| [5] | 0x1940 | ReadFile |
| [6] | 0x1948 | CloseHandle |
| [7] | — | терминатор (ноль) |

Порядок IAT совпадает с порядком INT.

## 10. Хвост

0x1A0A–0xDFF — нули до 0xE00. Покрытие полное: наложений и дыр нет,
листинг воспроизводит exe байт-в-байт (SHA-256 выше).
