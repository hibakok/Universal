# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 21504 байт (0x5400) |
| SHA-256 | FB84E14F4787E03086A5CD2805E1D4634ED813E58EAE62CD7E935698F21E39A2 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.2-3): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 4 части kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 1008 строк, 32573 Б (12% предела входа 256 КиБ) |
| Тело секции | 20570 байт (0x505A), RVA 0x1000, SRD 0x5200 |
| VirtualSize | 0x505A (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 4120 (kernel.b2 — 4408 строк; плоский, генерируемый) |
| Меток в исходнике | 220 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 29 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 64390902 + 14434406 + 5500623 + 4997 шагов) |

## 2. Карта функций (RVA — LAB/ai/kernel_labelmap.py по kernel.brick)

Группировка — по частям kernel.wall (состав — CARD.md; кирпичи K3-* —
MAP/M3-UNIVM.md).

```
сервис (kernel_self_c.wall — реинкарнации K2-C001/C003/C005):
  print_error .......... 120A  печать сообщения + ExitProcess(код)
  skip0 ................ 1285  пропуск argv0 + разделителей
  read_arg ............. 1658  слово-аргумент (>= 128 -> код 3)
  check_end ............ 198F  один аргумент строго (иначе справка, код 2)
  widen ................ 1AD8  имя -> UTF-16LE для CreateFile2

контейнер .UP (kernel_self_up.wall):
  rd32 ................. 1C8A  LE u32 по байтовому смещению
  read_up .............. 1DAD  чтение + разбор SPEC/13 (отказы п. 4) + RAM

память и устройства (kernel_self_mem.wall — срез E7.2-3):
  get_ram .............. 24F9  RAM: GlobalAlloc(0, memsize) + обнуление
  op_ldb ............... 26F3  0x0C: rd := sext8(RAM) / окно -> 0
  op_stb ............... 2A1F  0x0D: байт в RAM / окно+0 = консоль
  op_ldq ............... 2DC1  0x0E: слово LE (только RAM, целиком)
  op_stq ............... 32EB  0x0F: слово LE в RAM (только целиком)

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 388A  копия n байтов в буфер (диагностика)
  out_dec .............. 3961  десятичная запись числа в буфер
  fail_trap ............ 3C3E  диагностика ловушки + выход 1
  op_const ............. 3E12  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 3FED  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 4178  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 4331  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 44EA  0x05: rd := ra AND rb
  op_or ................ 46A3  0x06: rd := ra OR rb
  op_xor ............... 485C  0x07: rd := ra XOR rb
  op_shl ............... 4A15  0x08: rd := ra << (rb AND 63)
  op_shr ............... 4BE6  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 4DB7  0x0A: rd := ra < rb (знаково)
  op_eq ................ 4FB6  0x0B: rd := ra = rb
  op_halt .............. 51B5  0x12: поля + imm32 = код возврата
  interp ............... 52AA  цикл: порядок проверок SPEC/12 п. 7

вход (kernel.wall):
  main ................. 571C  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (13): s_use 58C2 (35Б) s_long 58E5 s_oup 58FF s_rup 5917
  s_sig 592F s_ver 5943 s_mem 5957 s_code0 596B s_len 5981 s_res 5995
  s_trap 59A9 s_steps 59B9 (8Б) s_crlf 59C0 (2Б)
глобали (16): hstdout 59C2 cmdline 59CA written 59D2 wlen 59DA
  arg1[64] 59E2 (0x200) w1[64] 5BE2 (0x200) hdrbuf[8] 5DE2 (0x40)
  codebuf 5E22 codesize 5E2A memsize 5E32 ram 5E3A pc 5E42 steps 5E4A
  regs[16] 5E52 (0x80) got 5ED2 trapbuf[48] 5EDA (0x180)
конец тела: 605A (vsize 0x505A)
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

SHA-256 артефактов: kernel.b2 — C5C05643…73C32145, kernel.brick —
8AE157DE…9A945588, kernel.exe — FB84E14F…98F21E39A2 (полные — VERIFY.md).
