# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 27136 байт (0x6A00) |
| SHA-256 | D0E8F698D361EE5A670E56047193B7059FDA18AFB567375F5D59E74BAC7165A3 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-2b): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 6 частей kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 1455 строк, 51209 Б (20% предела входа 256 КиБ) |
| Тело секции | 26566 байт (0x67C6), RVA 0x1000, SRD 0x6800 |
| VirtualSize | 0x67C6 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 5471 (kernel.b2 — 5841 строка; плоский, генерируемый) |
| Меток в исходнике | 296 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 38 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 90176415 + 19013790 + 7823150 + 4997 шагов) |

## 2. Карта функций (RVA — LAB/ai/kernel_labelmap.py по kernel.brick)

Группировка — по частям kernel.wall (состав — CARD.md; кирпичи K3-* —
MAP/M3-UNIVM.md + MAP/M3-UNIVM-V.md).

```
сервис (kernel_self_c.wall — реинкарнации K2-C001/C003/C005):
  print_error .......... 120A  печать сообщения + ExitProcess(код)
  skip0 ................ 1285  пропуск argv0 + разделителей
  read_arg ............. 1658  слово-аргумент (>= 128 -> код 3)
  check_end ............ 198F  не более двух аргументов (иначе справка, код 2)
  widen ................ 1AD8  имя -> UTF-16LE для CreateFile2
  read_lim ............. 1C8A  предел шагов: 2-й аргумент CLI -> steplim (E7.2-4)

контейнер .UP (kernel_self_up.wall; v2 — срез E7.4-2a):
  rd32 ................. 203E  LE u32 по байтовому смещению
  read_up .............. 2161  чтение + разбор SPEC/13 v1/v2 (отказы п. 4)
  read_data ............ 2A9C  секция данных v2 -> RAM[0:datalen] (E7.4-2a)

память и устройства (kernel_self_mem.wall — срез E7.2-3):
  get_ram .............. 2DCB  RAM: GlobalAlloc(0, memsize) + обнуление
  op_ldb ............... 2FC5  0x0C: rd := sext8(RAM) / окно -> 0
  op_stb ............... 32F1  0x0D: байт в RAM / окно+0 = консоль
  op_ldq ............... 3693  0x0E: слово LE (только RAM, целиком)
  op_stq ............... 3BBD  0x0F: слово LE в RAM (только целиком)

переходы (kernel_self_j.wall — срез E7.2-4):
  op_jmp ............... 415C  0x10: pc := imm32 (беззнаковое)
  op_jnz ............... 424A  0x11: pc := imm32 / pc+6 по regs[rd]

ALU v1 (kernel_self_alu.wall — срез E7.4-2b):
  udivmod .............. 439B  беззнаковое деление: uq/ur (фундамент)
  op_mul ............... 45FF  0x13: rd := (ra × rb) mod 2^64
  op_div ............... 47B9  0x14: rd := ra div rb; 0 — ловушка 7
  op_mod ............... 49C3  0x15: rd := a mod b; 0 — ловушка 7
  op_sra ............... 4BCD  0x16: rd := sext(ra) >> (rb AND 63)

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 4E58  копия n байтов в буфер (диагностика)
  out_dec .............. 4F2F  десятичная запись числа в буфер
  fail_trap ............ 520C  диагностика ловушки + выход 1
  op_const ............. 53E0  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 55BB  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 5746  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 58FF  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 5AB8  0x05: rd := ra AND rb
  op_or ................ 5C71  0x06: rd := ra OR rb
  op_xor ............... 5E2A  0x07: rd := ra XOR rb
  op_shl ............... 5FE3  0x08: rd := ra << (rb AND 63)
  op_shr ............... 61B4  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 6385  0x0A: rd := ra < rb (знаково)
  op_eq ................ 6584  0x0B: rd := ra = rb
  op_halt .............. 6783  0x12: поля + imm32 = код возврата
  interp ............... 6878  цикл: предел шагов (trap 6) + порядок
                              проверок SPEC/12 п. 7 (v0 01..12 + v1 13..16)

вход (kernel.wall):
  main ................. 6E3B  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (14): s_use 6FF9 (43Б) s_long 7024 s_oup 703E s_rup 7056
  s_sig 706E s_ver 7082 s_mem 7096 s_code0 70AA s_len 70C0 s_res 70D4
  s_data 70E8 (21Б, E7.4-2a) s_trap 70FD s_steps 710D (8Б) s_crlf 7114 (2Б)
глобали (19): hstdout 7116 cmdline 711E written 7126 wlen 712E
  arg1[64] 7136 (0x200) w1[64] 7336 (0x200) hdrbuf[8] 7536 (0x40)
  codebuf 7576 codesize 757E memsize 7586 ram 758E pc 7596 steps 759E
  steplim 75A6 uq 75AE ur 75B6 (E7.4-2b — результат udivmod)
  regs[16] 75BE (0x80) got 763E trapbuf[48] 7646 (0x180)
конец тела: 77C6 (vsize 0x67C6)
```

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E7-09):

```
splice.exe kernel.wall kernel_s.flat
wall.exe   kernel_s.flat kernel_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    kernel_s.b2   kernel_s.brick
brick.exe  kernel_s.brick kernel_s.bin
pegen.exe  kernel_s.bin  kernel.peg kernel.exe   (== артефакт)
```

SHA-256 артефактов: kernel.b2 — 362B2F70…71EFD02D, kernel.brick —
C624AB45…84D0257D, kernel.exe — D0E8F698…BAC7165A3 (полные — VERIFY.md).
