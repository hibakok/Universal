# BYTECODE.md — байт-за-байтом разбор seed2.exe

Паспорт файла: KERNEL/L0-SEED2/BYTECODE.md | слой: L0 | роль: полный разбор образа.

Источник истины — `seed2.hex`. Структура DOS/COFF/опционального заголовков
идентична `KERNEL/L0-SEED/BYTECODE.md` (пояснения каждого поля — там);
здесь приводятся значения и отличия M0-SEED2 от M0-SEED.

## 0. Сводка

| Свойство | Значение |
|---|---|
| Размер файла | 2048 байт (0x800) |
| SHA-256 | 190DE94E3F3227D421B6779B34985FD1762E127EC50EF864C4ED84814B05EE87 |
| Точка входа | файл 0x200 (RVA 0x1000, K0-X011) |
| Код | 617 байт (0x269), 185 инструкций, 30 меток |
| Данные | 320 байт @ RVA 0x1270 |
| Импорты | 210 байт @ RVA 0x13B0 |
| Смещение → RVA | заголовки: файл = RVA; секция: RVA = файл − 0x200 + 0x1000 |
| Вывод (по команде) | `U-L0-SEED2 ENTRY=0x00001000` и т.п.; коды 0/2 |

## 1. Заголовки (отличия от семени M0-SEED)

| Поле | Смещение | Значение | Пояснение |
|---|---|---|---|
| DOS-заглушка | 0x040 | «Universal L0 seed2. No DOS support.» | текст, 38 байт |
| SizeOfCode | 0x09C | 0x600 | секция выросла с 0x200 |
| SizeOfImage | 0x0D0 | 0x2000 | как у семени: 0x1000 + выравнивание |
| DD[1] Import | 0x110 | RVA 0x13B0, размер 0x28 | IDT в секции |
| DD[12] IAT | 0x168 | RVA 0x13E0, размер 0x28 | 4 функции + терминатор |
| VirtualSize (.text) | 0x190 | 0x482 | код+данные+импорты |
| SizeOfRawData | 0x198 | 0x600 | файл = 0x200 + 0x600 = 0x800 |

Импорт kernel32.dll расширен четвёртой функцией `GetCommandLineA`
(индекс IAT[3]). Формулы и порядок работы загрузчика — `SPEC/04-PE-MINIMAL.md`.

## 2. Раскладка внутри .text

```
RVA 0x1000  код: главный поток, диспетчер, подпрограммы (0x269 байт)
RVA 0x1270  данные: 6 строк вывода, таблица цифр, служебные ячейки
RVA 0x1360  таблица команд: 5 записей по 16 байт (K0-D012)
RVA 0x13B0  IDT: описатель импорта kernel32.dll + терминатор
RVA 0x13E0  IAT: 4 адреса функций + терминатор (заполняет загрузчик)
RVA 0x1410  INT: копия IAT до заполнения (по ней ищутся имена)
RVA 0x1438  имена: kernel32.dll, hint-записи 4 функций
RVA 0x1482  конец содержимого; далее нули до 0x1600 (VirtualSize 0x482)
```

## 3. Код: все инструкции

## Таблица кода (автогенерация)
| Файл | RVA | Байты | Мнемоника | Кирпич |
|---|---|---|---|---|
| 0x200 | 0x1000 | `48 83 EC 28` | `sub rsp,0x28` | K0-X011 |
| 0x204 | 0x1004 | `48 8D 1D F5 EF FF FF` | `lea rbx,[rip+disp]` | K0-S011 |
| 0x20B | 0x100B | `48 C7 C1 F5 FF FF FF` | `mov rcx,-11` | — |
| 0x212 | 0x1012 | `FF 15 C8 03 00 00` | `call [rip]GetStdHandle` | — |
| 0x218 | 0x1018 | `48 89 05 29 03 00 00` | `mov [rip+hstdout],rax` | — |
| 0x21F | 0x101F | `FF 15 D3 03 00 00` | `call [rip]GetCommandLineA` | K0-C001 |
| 0x225 | 0x1025 | `48 89 C7` | `mov rdi,rax` | — |
| 0x228 | 0x1028 | `0F B6 07` | `movzx eax,byte [rdi]` | K0-C002 |
| 0x22B | 0x102B | `3C 22` | `cmp al,'"'` | — |
| 0x22D | 0x102D | `75 13` | `jne s2_unq` | — |
| 0x22F | 0x102F | `48 FF C7` | `inc rdi` | — |
| 0x232 | 0x1032 | `0F B6 07` | `movzx eax,byte [rdi]` | — |
| 0x235 | 0x1035 | `84 C0` | `test al,al` | — |
| 0x237 | 0x1037 | `74 30` | `jz noargs` | — |
| 0x239 | 0x1039 | `3C 22` | `cmp al,'"'` | — |
| 0x23B | 0x103B | `74 27` | `je s2_adv` | — |
| 0x23D | 0x103D | `48 FF C7` | `inc rdi` | — |
| 0x240 | 0x1040 | `EB F0` | `jmp s2_quote` | — |
| 0x242 | 0x1042 | `84 C0` | `test al,al` | — |
| 0x244 | 0x1044 | `74 23` | `jz noargs` | — |
| 0x246 | 0x1046 | `3C 20` | `cmp al,' '` | — |
| 0x248 | 0x1048 | `74 09` | `je s2_delims` | — |
| 0x24A | 0x104A | `3C 09` | `cmp al,9` | — |
| 0x24C | 0x104C | `74 05` | `je s2_delims` | — |
| 0x24E | 0x104E | `48 FF C7` | `inc rdi` | — |
| 0x251 | 0x1051 | `EB D5` | `jmp skip_argv0` | — |
| 0x253 | 0x1053 | `0F B6 07` | `movzx eax,byte [rdi]` | — |
| 0x256 | 0x1056 | `84 C0` | `test al,al` | — |
| 0x258 | 0x1058 | `74 0F` | `jz noargs` | — |
| 0x25A | 0x105A | `3C 20` | `cmp al,' '` | — |
| 0x25C | 0x105C | `74 06` | `je s2_adv` | — |
| 0x25E | 0x105E | `3C 09` | `cmp al,9` | — |
| 0x260 | 0x1060 | `74 02` | `je s2_adv` | — |
| 0x262 | 0x1062 | `EB 11` | `jmp word_start` | — |
| 0x264 | 0x1064 | `48 FF C7` | `inc rdi` | — |
| 0x267 | 0x1067 | `EB EA` | `jmp s2_delims` | — |
| 0x269 | 0x1069 | `E8 BA 01 00 00` | `call print_usage` | — |
| 0x26E | 0x106E | `31 C9` | `xor ecx,ecx` | K0-X012 |
| 0x270 | 0x1070 | `E9 39 01 00 00` | `jmp exit_proc` | — |
| 0x275 | 0x1075 | `48 89 FE` | `mov rsi,rdi` | K0-C003 |
| 0x278 | 0x1078 | `0F B6 07` | `movzx eax,byte [rdi]` | — |
| 0x27B | 0x107B | `84 C0` | `test al,al` | — |
| 0x27D | 0x107D | `74 0D` | `jz rw_end` | — |
| 0x27F | 0x107F | `3C 20` | `cmp al,' '` | — |
| 0x281 | 0x1081 | `74 09` | `je rw_end` | — |
| 0x283 | 0x1083 | `3C 09` | `cmp al,9` | — |
| 0x285 | 0x1085 | `74 05` | `je rw_end` | — |
| 0x287 | 0x1087 | `48 FF C7` | `inc rdi` | — |
| 0x28A | 0x108A | `EB EC` | `jmp rw_loop` | — |
| 0x28C | 0x108C | `E8 24 01 00 00` | `call find_command` | K0-C004 |
| 0x291 | 0x1091 | `48 85 C0` | `test rax,rax` | K0-G001 |
| 0x294 | 0x1094 | `0F 84 08 01 00 00` | `jz unknown` | — |
| 0x29A | 0x109A | `49 89 C4` | `mov r12,rax` | — |
| 0x29D | 0x109D | `41 0F B6 44 24 08` | `movzx eax,byte [r12+8]` | — |
| 0x2A3 | 0x10A3 | `3C 01` | `cmp al,1` | — |
| 0x2A5 | 0x10A5 | `74 0D` | `je do_fd` | — |
| 0x2A7 | 0x10A7 | `3C 02` | `cmp al,2` | — |
| 0x2A9 | 0x10A9 | `74 5C` | `je do_fa` | — |
| 0x2AB | 0x10AB | `3C 03` | `cmp al,3` | — |
| 0x2AD | 0x10AD | `74 18` | `je do_fw` | — |
| 0x2AF | 0x10AF | `E9 EE 00 00 00` | `jmp unknown` | — |
| 0x2B4 | 0x10B4 | `8B 43 3C` | `mov eax,[rbx+0x3C]` | K0-S012 |
| 0x2B7 | 0x10B7 | `48 98` | `cdqe` | — |
| 0x2B9 | 0x10B9 | `48 01 D8` | `add rax,rbx` | — |
| 0x2BC | 0x10BC | `41 0F B6 54 24 09` | `movzx edx,byte [r12+9]` | — |
| 0x2C2 | 0x10C2 | `8B 04 10` | `mov eax,[rax+rdx]` | — |
| 0x2C5 | 0x10C5 | `EB 12` | `jmp field_print` | — |
| 0x2C7 | 0x10C7 | `8B 43 3C` | `mov eax,[rbx+0x3C]` | K0-S012 |
| 0x2CA | 0x10CA | `48 98` | `cdqe` | — |
| 0x2CC | 0x10CC | `48 01 D8` | `add rax,rbx` | — |
| 0x2CF | 0x10CF | `41 0F B6 54 24 09` | `movzx edx,byte [r12+9]` | — |
| 0x2D5 | 0x10D5 | `0F B7 04 10` | `movzx eax,word [rax+rdx]` | — |
| 0x2D9 | 0x10D9 | `45 8B 5C 24 0C` | `mov r11d,[r12+12]` | K0-P012 |
| 0x2DE | 0x10DE | `41 0F B6 54 24 0A` | `movzx edx,byte [r12+10]` | — |
| 0x2E4 | 0x10E4 | `4C 01 DA` | `add rdx,r11` | — |
| 0x2E7 | 0x10E7 | `48 01 DA` | `add rdx,rbx` | — |
| 0x2EA | 0x10EA | `E8 12 01 00 00` | `call hex32_to_ascii8` | K0-H011 |
| 0x2EF | 0x10EF | `4C 89 DA` | `mov rdx,r11` | — |
| 0x2F2 | 0x10F2 | `48 01 DA` | `add rdx,rbx` | — |
| 0x2F5 | 0x10F5 | `45 0F B6 44 24 0B` | `movzx r8d,byte [r12+11]` | — |
| 0x2FB | 0x10FB | `E8 43 01 00 00` | `call print_line` | K0-P011 |
| 0x300 | 0x1100 | `31 C9` | `xor ecx,ecx` | K0-X012 |
| 0x302 | 0x1102 | `E9 A7 00 00 00` | `jmp exit_proc` | — |
| 0x307 | 0x1107 | `0F B6 07` | `movzx eax,byte [rdi]` | K0-A001 |
| 0x30A | 0x110A | `84 C0` | `test al,al` | — |
| 0x30C | 0x110C | `74 0F` | `jz fa_empty` | — |
| 0x30E | 0x110E | `3C 20` | `cmp al,' '` | — |
| 0x310 | 0x1110 | `74 06` | `je fa_adv` | — |
| 0x312 | 0x1112 | `3C 09` | `cmp al,9` | — |
| 0x314 | 0x1114 | `74 02` | `je fa_adv` | — |
| 0x316 | 0x1116 | `EB 2E` | `jmp fa_tail` | — |
| 0x318 | 0x1118 | `48 FF C7` | `inc rdi` | — |
| 0x31B | 0x111B | `EB EA` | `jmp do_fa` | — |
| 0x31D | 0x111D | `41 8B 54 24 0C` | `mov edx,[r12+12]` | — |
| 0x322 | 0x1122 | `48 01 DA` | `add rdx,rbx` | — |
| 0x325 | 0x1125 | `45 0F B6 44 24 0B` | `movzx r8d,byte [r12+11]` | — |
| 0x32B | 0x112B | `E8 13 01 00 00` | `call print_line` | K0-P011 |
| 0x330 | 0x1130 | `48 8D 15 0B 02 00 00` | `lea rdx,[rip+crlf]` | — |
| 0x337 | 0x1137 | `41 B8 02 00 00 00` | `mov r8d,2` | — |
| 0x33D | 0x113D | `E8 01 01 00 00` | `call print_line` | K0-P011 |
| 0x342 | 0x1142 | `31 C9` | `xor ecx,ecx` | K0-X012 |
| 0x344 | 0x1144 | `EB 68` | `jmp exit_proc` | — |
| 0x346 | 0x1146 | `49 89 FD` | `mov r13,rdi` | — |
| 0x349 | 0x1149 | `41 8B 54 24 0C` | `mov edx,[r12+12]` | — |
| 0x34E | 0x114E | `48 01 DA` | `add rdx,rbx` | — |
| 0x351 | 0x1151 | `45 0F B6 44 24 0B` | `movzx r8d,byte [r12+11]` | — |
| 0x357 | 0x1157 | `E8 E7 00 00 00` | `call print_line` | K0-P011 |
| 0x35C | 0x115C | `31 C9` | `xor ecx,ecx` | K0-C005 |
| 0x35E | 0x115E | `0F B6 07` | `movzx eax,byte [rdi]` | K0-C005 |
| 0x361 | 0x1161 | `84 C0` | `test al,al` | — |
| 0x363 | 0x1163 | `74 07` | `jz ct_end` | — |
| 0x365 | 0x1165 | `48 FF C7` | `inc rdi` | — |
| 0x368 | 0x1168 | `FF C1` | `inc ecx` | — |
| 0x36A | 0x116A | `EB F2` | `jmp ct_loop` | — |
| 0x36C | 0x116C | `49 89 CE` | `mov r14,rcx` | — |
| 0x36F | 0x116F | `48 8D 15 CA 01 00 00` | `lea rdx,[rip+space]` | — |
| 0x376 | 0x1176 | `41 B8 01 00 00 00` | `mov r8d,1` | — |
| 0x37C | 0x117C | `E8 C2 00 00 00` | `call print_line` | K0-P011 |
| 0x381 | 0x1181 | `4C 89 EA` | `mov rdx,r13` | — |
| 0x384 | 0x1184 | `4D 89 F0` | `mov r8,r14` | — |
| 0x387 | 0x1187 | `E8 B7 00 00 00` | `call print_line` | K0-P011 |
| 0x38C | 0x118C | `48 8D 15 AF 01 00 00` | `lea rdx,[rip+crlf]` | — |
| 0x393 | 0x1193 | `41 B8 02 00 00 00` | `mov r8d,2` | — |
| 0x399 | 0x1199 | `E8 A5 00 00 00` | `call print_line` | K0-P011 |
| 0x39E | 0x119E | `31 C9` | `xor ecx,ecx` | K0-X012 |
| 0x3A0 | 0x11A0 | `EB 0C` | `jmp exit_proc` | — |
| 0x3A2 | 0x11A2 | `E8 81 00 00 00` | `call print_usage` | K0-U001 |
| 0x3A7 | 0x11A7 | `B9 02 00 00 00` | `mov ecx,2` | K0-X012 |
| 0x3AC | 0x11AC | `EB 00` | `jmp exit_proc` | — |
| 0x3AE | 0x11AE | `FF 15 3C 02 00 00` | `call [rip]ExitProcess` | K0-X012 |
| 0x3B4 | 0x11B4 | `CC` | `int3` | — |
| 0x3B5 | 0x11B5 | `4C 8D 05 A4 01 00 00` | `lea r8,[rip+cmdtable]` | K0-C004 |
| 0x3BC | 0x11BC | `41 B9 05 00 00 00` | `mov r9d,5` | — |
| 0x3C2 | 0x11C2 | `45 85 C9` | `test r9d,r9d` | — |
| 0x3C5 | 0x11C5 | `74 33` | `jz fc_zero` | — |
| 0x3C7 | 0x11C7 | `4D 89 C2` | `mov r10,r8` | — |
| 0x3CA | 0x11CA | `48 89 F1` | `mov rcx,rsi` | — |
| 0x3CD | 0x11CD | `41 0F B6 12` | `movzx edx,byte [r10]` | — |
| 0x3D1 | 0x11D1 | `84 D2` | `test dl,dl` | — |
| 0x3D3 | 0x11D3 | `74 0E` | `jz fc_nend` | — |
| 0x3D5 | 0x11D5 | `8A 01` | `mov al,[rcx]` | — |
| 0x3D7 | 0x11D7 | `38 D0` | `cmp al,dl` | — |
| 0x3D9 | 0x11D9 | `75 16` | `jne fc_mis` | — |
| 0x3DB | 0x11DB | `49 FF C2` | `inc r10` | — |
| 0x3DE | 0x11DE | `48 FF C1` | `inc rcx` | — |
| 0x3E1 | 0x11E1 | `EB EA` | `jmp fc_cmp` | — |
| 0x3E3 | 0x11E3 | `8A 01` | `mov al,[rcx]` | — |
| 0x3E5 | 0x11E5 | `84 C0` | `test al,al` | — |
| 0x3E7 | 0x11E7 | `74 14` | `jz fc_found` | — |
| 0x3E9 | 0x11E9 | `3C 20` | `cmp al,' '` | — |
| 0x3EB | 0x11EB | `74 10` | `je fc_found` | — |
| 0x3ED | 0x11ED | `3C 09` | `cmp al,9` | — |
| 0x3EF | 0x11EF | `74 0C` | `je fc_found` | — |
| 0x3F1 | 0x11F1 | `49 83 C0 10` | `add r8,16` | — |
| 0x3F5 | 0x11F5 | `41 FF C9` | `dec r9d` | — |
| 0x3F8 | 0x11F8 | `EB C8` | `jmp fc_next` | — |
| 0x3FA | 0x11FA | `31 C0` | `xor eax,eax` | — |
| 0x3FC | 0x11FC | `C3` | `ret` | — |
| 0x3FD | 0x11FD | `4C 89 C0` | `mov rax,r8` | — |
| 0x400 | 0x1200 | `C3` | `ret` | — |
| 0x401 | 0x1201 | `48 89 D6` | `mov rsi,rdx` | K0-H011 |
| 0x404 | 0x1204 | `4C 8D 05 25 01 00 00` | `lea r8,[rip+digits]` | — |
| 0x40B | 0x120B | `B9 08 00 00 00` | `mov ecx,8` | — |
| 0x410 | 0x1210 | `C1 C0 04` | `rol eax,4` | — |
| 0x413 | 0x1213 | `48 89 C2` | `mov rdx,rax` | — |
| 0x416 | 0x1216 | `83 E2 0F` | `and edx,0xF` | — |
| 0x419 | 0x1219 | `41 0F B6 14 10` | `movzx rdx,byte [r8+rdx]` | — |
| 0x41E | 0x121E | `88 16` | `mov [rsi],dl` | — |
| 0x420 | 0x1220 | `48 FF C6` | `inc rsi` | — |
| 0x423 | 0x1223 | `FF C9` | `dec ecx` | — |
| 0x425 | 0x1225 | `75 E9` | `jnz h_loop` | — |
| 0x427 | 0x1227 | `C3` | `ret` | — |
| 0x428 | 0x1228 | `48 83 EC 28` | `sub rsp,0x28` | K0-U001 |
| 0x42C | 0x122C | `48 8D 15 C0 00 00 00` | `lea rdx,[rip+usage_str]` | — |
| 0x433 | 0x1233 | `41 B8 2E 00 00 00` | `mov r8d,46` | — |
| 0x439 | 0x1239 | `E8 05 00 00 00` | `call print_line` | K0-P011 |
| 0x43E | 0x123E | `48 83 C4 28` | `add rsp,0x28` | — |
| 0x442 | 0x1242 | `C3` | `ret` | — |
| 0x443 | 0x1243 | `48 83 EC 28` | `sub rsp,0x28` | K0-P011 |
| 0x447 | 0x1247 | `48 8B 0D FA 00 00 00` | `mov rcx,[rip+hstdout]` | — |
| 0x44E | 0x124E | `4C 8D 0D FB 00 00 00` | `lea r9,[rip+written]` | — |
| 0x455 | 0x1255 | `48 C7 44 24 20 00 00 00 00` | `mov qword [rsp+0x20],0` | — |
| 0x45E | 0x125E | `FF 15 84 01 00 00` | `call [rip]WriteFile` | — |
| 0x464 | 0x1264 | `48 83 C4 28` | `add rsp,0x28` | — |
| 0x468 | 0x1268 | `C3` | `ret` | — |

Пояснение: переходы короткие (rel8) автоматически; четыре дальних
переключения кодированы rel32 (E9/0F 84). «—» в графе «Кирпич» —
внутренний шаг кирпича, указанного выше.

## 4. Поток исполнения (по кирпичам)

1. **K0-X011 → K0-S011 → init.** Кадр 0x28; RBX = база образа;
   GetStdHandle(−11) → ячейка `hstdout`; GetCommandLineA → RDI.
2. **K0-C002 skip_argv0.** Если строка начинается с `'"'` — сканировать
   до закрывающей кавычки, затем `s2_adv` (пропуск кавычки и
   разделителей); иначе сканировать до пробела/табуляции. Разделители
   (0x20, 0x09) пропускаются; NUL → `noargs` (справка, код 0).
3. **K0-C003 read_word.** RSI = начало слова; RDI доводится до
   разделителя или NUL.
4. **K0-C004 find_command.** R8 = cmdtable, R9 = 5 записей. Цикл
   сравнения: байт имени = 0 → имя закончилось → проверить, что слово
   тоже закончилось (NUL/пробел/таб) → совпадение; иначе следующая
   запись (+16). Не найдено → RAX = 0.
5. **K0-G001 диспетчер.** R12 = запись; байт [r12+8] — действие:
   1 = поле заголовка 32 бита, 3 = поле 16 бит, 2 = эхо аргументов.
6. **Действия 1/3 (K0-S012, K0-P012).** RAX = база + e_lfanew;
   [r12+9] — смещение поля от PE-сигнатуры; значение читается
   (mov/movzx), K0-H011 вписывает 8 hex-цифр в поле строки
   ([r12+10] — смещение поля, [r12+12] — RVA строки), K0-P011
   печатает строку длиной [r12+11]; код возврата 0.
7. **Действие 2 (K0-A001).** Пропуск разделителей от RDI; пусто →
   префикс ARGS + CRLF. Иначе R13 = хвост; печать префикса; K0-C005
   считает длину до NUL (сохраняется в R14 — rcx волатилен!);
   печать пробела, хвоста (RDX=R13, R8=R14), CRLF; код 0.
8. **K0-X012.** ExitProcess(ecx); страховочный int3. Неизвестное
   слово → K0-U001 (справка) и код 2.

## 5. Расчёт rip-смещений (цель − конец инструкции)

## Таблица rip-смещений (цель − конец инструкции)
| Инструкция (RVA конца) | Цель | Цель RVA | disp32 |
|---|---|---|---|
| lea rbx,[rip+disp] (0x100B) | BASE0 | 0x0000 | -0x100b |
| call [rip]GetStdHandle (0x1018) | IAT_GSH | 0x13E0 | +0x3c8 |
| mov [rip+hstdout],rax (0x101F) | hstdout | 0x1348 | +0x329 |
| call [rip]GetCommandLineA (0x1025) | IAT_GCLA | 0x13F8 | +0x3d3 |
| lea rdx,[rip+crlf] (0x1137) | crlf | 0x1342 | +0x20b |
| lea rdx,[rip+space] (0x1176) | space | 0x1340 | +0x1ca |
| lea rdx,[rip+crlf] (0x1193) | crlf | 0x1342 | +0x1af |
| call [rip]ExitProcess (0x11B4) | IAT_EP | 0x13F0 | +0x23c |
| lea r8,[rip+cmdtable] (0x11BC) | cmdtable | 0x1360 | +0x1a4 |
| lea r8,[rip+digits] (0x120B) | digits | 0x1330 | +0x125 |
| lea rdx,[rip+usage_str] (0x1233) | usage_str | 0x12F3 | +0xc0 |
| mov rcx,[rip+hstdout] (0x124E) | hstdout | 0x1348 | +0xfa |
| lea r9,[rip+written] (0x1255) | written | 0x1350 | +0xfb |
| call [rip]WriteFile (0x1264) | IAT_WF | 0x13E8 | +0x184 |

## 6. Метки кода

## Метки кода
| Метка | RVA | Файл |
|---|---|---|
| entry | 0x1000 | 0x200 |
| skip_argv0 | 0x1028 | 0x228 |
| s2_quote | 0x1032 | 0x232 |
| s2_unq | 0x1042 | 0x242 |
| s2_delims | 0x1053 | 0x253 |
| s2_adv | 0x1064 | 0x264 |
| noargs | 0x1069 | 0x269 |
| noargs_cont | 0x106E | 0x26E |
| word_start | 0x1075 | 0x275 |
| rw_loop | 0x1078 | 0x278 |
| rw_end | 0x108C | 0x28C |
| do_fd | 0x10B4 | 0x2B4 |
| do_fw | 0x10C7 | 0x2C7 |
| field_print | 0x10D9 | 0x2D9 |
| do_fa | 0x1107 | 0x307 |
| fa_adv | 0x1118 | 0x318 |
| fa_empty | 0x111D | 0x31D |
| fa_tail | 0x1146 | 0x346 |
| ct_loop | 0x115E | 0x35E |
| ct_end | 0x116C | 0x36C |
| unknown | 0x11A2 | 0x3A2 |
| exit_proc | 0x11AE | 0x3AE |
| find_command | 0x11B5 | 0x3B5 |
| fc_next | 0x11C2 | 0x3C2 |
| fc_cmp | 0x11CD | 0x3CD |
| fc_nend | 0x11E3 | 0x3E3 |
| fc_mis | 0x11F1 | 0x3F1 |
| fc_zero | 0x11FA | 0x3FA |
| fc_found | 0x11FD | 0x3FD |
| hex32_to_ascii8 | 0x1201 | 0x401 |
| h_loop | 0x1210 | 0x410 |
| print_usage | 0x1228 | 0x428 |
| print_line | 0x1243 | 0x443 |

## 7. Данные

## Данные
| Метка | Файл | RVA | Длина | Комментарий |
|---|---|---|---|---|
| entry_str | 0x470 | 0x1270 | 29 | K0-D011: ENTRY: префикс 19 + hex-поле 8 + CRLF |
| image_str | 0x48D | 0x128D | 29 | K0-D011: IMAGE |
| align_str | 0x4AA | 0x12AA | 29 | K0-D011: ALIGN |
| sect_str | 0x4C7 | 0x12C7 | 28 | K0-D011: SECT (префикс 18) |
| args_str | 0x4E3 | 0x12E3 | 16 | K0-D011: префикс эха аргументов (16) |
| usage_str | 0x4F3 | 0x12F3 | 46 | K0-D011: справка (46, инвариант кода) |
| digits | 0x530 | 0x1330 | 16 | K0-D013: таблица 16 hex-цифр |
| space | 0x540 | 0x1340 | 1 | K0-D013: пробел |
| crlf | 0x542 | 0x1342 | 2 | K0-D013: перевод строки |
| hstdout | 0x548 | 0x1348 | 8 | K0-D013: хэндл stdout (заполняет init) |
| written | 0x550 | 0x1350 | 8 | K0-D013: счётчик WriteFile |
| cmdtable | 0x560 | 0x1360 | 16 | K0-D012[0]: entry; действие 1; поле PE+0x28; hex@0x13; длина 0x1D |
| — | 0x570 | 0x1370 | 16 | K0-D012[1]: image; действие 1; поле PE+0x50 |
| — | 0x580 | 0x1380 | 16 | K0-D012[2]: align; действие 1; поле PE+0x38 |
| — | 0x590 | 0x1390 | 16 | K0-D012[3]: sect; действие 3 (word); поле PE+0x06 |
| — | 0x5A0 | 0x13A0 | 16 | K0-D012[4]: args; действие 2 (эхо); длина префикса 0x10 |

### Формат записи таблицы команд (16 байт)

| Смещение | Размер | Смысл |
|---|---|---|
| +0 | 8 | имя команды (ASCII, NUL-дополненное) |
| +8 | 1 | действие: 1 = поле dword, 3 = поле word, 2 = эхо аргументов |
| +9 | 1 | смещение поля от PE-сигнатуры (действия 1/3) |
| +10 | 1 | смещение hex-поля в строке вывода (действия 1/3) |
| +11 | 1 | длина строки вывода / длина префикса (действие 2) |
| +12 | 4 | RVA строки вывода (dword, little-endian) |

Смещения полей от PE-сигнатуры: ENTRY = PE+0x28 (OH+0x10),
IMAGE = PE+0x50 (OH+0x38), ALIGN = PE+0x38 (OH+0x20),
SECT = PE+0x06 (COFF+2, слово). Чтение e_lfanew динамическое —
образ работает при любом e_lfanew.

### Инварианты кода и данных

1. Длина usage-строки = 46 (0x2E) — зашита в `mov r8d,46`.
2. Число записей таблицы = 5 — зашито в `mov r9d,5`.
3. Размер записи = 16 — зашит в `add r8,16`.
4. Команды различаются регистром: только строчные буквы.
5. Регистровые соглашения модуля: RBX — база образа; RDI — курсор
   чтения; RSI — курсор записи hex; R12 — запись таблицы команд;
   R13 — хвост аргументов; R14 — длина хвоста; R11 — RVA строки.
   RCX/RDX/R8/R9/RAX — волатильные: их нельзя хранить через вызовы
   Win64 (урок теста T-M2-06: rcx затирался хэндлом в print_line).

## 8. Импорты

## Импорты
| Метка | Файл | RVA | Комментарий |
|---|---|---|---|
| IDT | 0x5B0 | 0x13B0 | K0-D014: описатель импорта (заполняет сборка) |
| IAT | 0x5E0 | 0x13E0 | K0-D014: IAT (4 функции + терминатор) |
| INT | 0x610 | 0x1410 | K0-D014: INT (копия IAT до заполнения) |
| dllname | 0x638 | 0x1438 | K0-D014: имя DLL |
| hint_GSH | 0x646 | 0x1446 | K0-D014: hint=0 |
| hint_WF | 0x656 | 0x1456 | K0-D014: hint=0 |
| hint_EP | 0x662 | 0x1462 | K0-D014: hint=0 |
| hint_GCLA | 0x670 | 0x1470 | K0-D014: hint=0 |

| Индекс IAT | RVA | Функция |
|---|---|---|
| [0] | 0x13E0 | GetStdHandle |
| [1] | 0x13E8 | WriteFile |
| [2] | 0x13F0 | ExitProcess |
| [3] | 0x13F8 | GetCommandLineA |
| [4] | — | терминатор (ноль) |

Порядок IAT совпадает с порядком INT; имена hint-записей выровнены
на чётные RVA (инвариант S04-7).

## 9. Хвост

0x682–0x7FF — нули до размера 0x800. Полное покрытие файла байтами
проверено сборкой: наложений и дыр нет, ATOM-листинг воспроизводит
exe байт-в-байт.
