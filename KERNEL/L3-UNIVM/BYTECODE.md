# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 10240 байт (0x2800) |
| SHA-256 | 5D8CD3DE26D136F7B8609395B8E771E45A9685E5F508E0742361A36B747F2D52 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.2-1): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 3 части kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 435 строк, 13958 Б (5% предела входа 256 КиБ) |
| Тело секции | 9549 байт (0x254D), RVA 0x1000, SRD 0x2600 |
| VirtualSize | 0x254D (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 1590 (kernel.b2 — 1797 строк; плоский, генерируемый) |
| Меток в исходнике | 141 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 13 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB |

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
  read_up .............. 1DAD  чтение + разбор SPEC/13 (отказы п. 4)

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 24F4  копия n байтов в буфер (диагностика)
  out_dec .............. 25CB  десятичная запись числа в буфер
  fail_trap ............ 28A8  диагностика ловушки + выход 1
  op_halt .............. 2A7C  halt: поля + imm32 = код возврата
  interp ............... 2B71  цикл: порядок проверок SPEC/12 п. 7

вход (kernel.wall):
  main ................. 2C97  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (13): s_use 2E3D (35Б) s_long 2E60 s_oup 2E7A s_rup 2E92
  s_sig 2EAA s_ver 2EBE s_mem 2ED2 s_code0 2EE6 s_len 2EFC s_res 2F10
  s_trap 2F24 s_steps 2F34 (8Б) s_crlf 2F3B (2Б)
глобали (14): hstdout 2F3D cmdline 2F45 written 2F4D wlen 2F55
  arg1[64] 2F5D (0x200) w1[64] 315D (0x200) hdrbuf[8] 335D (0x40)
  codebuf 339D codesize 33A5 memsize 33AD pc 33B5 steps 33BD
  got 33C5 trapbuf[48] 33CD (0x180)
конец тела: 354D (vsize 0x254D)
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

SHA-256 артефактов: kernel.b2 — B8C99245…E3044337, kernel.brick —
ACE82FE3…1C56940, kernel.exe — 5D8CD3DE…47F2D52 (полные — VERIFY.md).
