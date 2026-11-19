# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 16384 байт (0x4000) |
| SHA-256 | 9B33FDFDBD3C20C00CF4CF2C39950FD1F0DF5485A5F9CDD2525E9179379BDBF7 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.2-2): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 3 части kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 757 строк, 23307 Б (9% предела входа 256 КиБ) |
| Тело секции | 15384 байт (0x3C18), RVA 0x1000, SRD 0x3E00 |
| VirtualSize | 0x3C18 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 2909 (kernel.b2 — 3163 строк; плоский, генерируемый) |
| Меток в исходнике | 186 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 24 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 46761507 + 10200280 + 3866085 + 4997 шагов) |

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
  op_const ............. 2A7C  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 2C57  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 2DE2  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 2F9B  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 3154  0x05: rd := ra AND rb
  op_or ................ 330D  0x06: rd := ra OR rb
  op_xor ............... 34C6  0x07: rd := ra XOR rb
  op_shl ............... 367F  0x08: rd := ra << (rb AND 63)
  op_shr ............... 3850  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 3A21  0x0A: rd := ra < rb (знаково)
  op_eq ................ 3C20  0x0B: rd := ra = rb
  op_halt .............. 3E1F  0x12: поля + imm32 = код возврата
  interp ............... 3F14  цикл: порядок проверок SPEC/12 п. 7

вход (kernel.wall):
  main ................. 42E2  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (13): s_use 4488 (35Б) s_long 44AB s_oup 44C5 s_rup 44DD
  s_sig 44F5 s_ver 4509 s_mem 451D s_code0 4531 s_len 4547 s_res 455B
  s_trap 456F s_steps 457F (8Б) s_crlf 4586 (2Б)
глобали (15): hstdout 4588 cmdline 4590 written 4598 wlen 45A0
  arg1[64] 45A8 (0x200) w1[64] 47A8 (0x200) hdrbuf[8] 49A8 (0x40)
  codebuf 49E8 codesize 49F0 memsize 49F8 pc 4A00 steps 4A08
  regs[16] 4A10 (0x80) got 4A90 trapbuf[48] 4A98 (0x180)
конец тела: 4C18 (vsize 0x3C18)
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

SHA-256 артефактов: kernel.b2 — 71A47AE6…638430C43, kernel.brick —
99319802…C06B7E1DB, kernel.exe — 9B33FDFD…379BDBF7 (полные — VERIFY.md).
