# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 36352 байт (0x8E00) |
| SHA-256 | 9F5696178E26452D66B3F0FCC3BFDE0704D926AA12B61C9A0B351EFF51BE4799 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-2c): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 7 частей kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 56232 Б (21% предела входа 256 КиБ; 1545 строк — заголовок kernel.b2) |
| Тело секции | 35474 байта (0x8A92), RVA 0x1000, SRD 0x8C00 |
| VirtualSize | 0x8A92 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 5627 (kernel.b2 — 6142 строки; плоский, генерируемый) |
| Меток в исходнике | 306 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 40 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 94575184 + 19505794 + 8202669 + 4997 шагов) |

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

стек вызовов (kernel_self_call.wall — срез E7.4-2c):
  op_call .............. 4E58  0x17: pc+6 -> cstack[csp++], pc := imm32
  op_ret ............... 4FEE  0x18: pc := cstack[--csp] (F0 — 1 Б)

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 50AB  копия n байтов в буфер (диагностика)
  out_dec .............. 5182  десятичная запись числа в буфер
  fail_trap ............ 545F  диагностика ловушки + выход 1
  op_const ............. 5633  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 580E  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 5999  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 5B52  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 5D0B  0x05: rd := ra AND rb
  op_or ................ 5EC4  0x06: rd := ra OR rb
  op_xor ............... 607D  0x07: rd := ra XOR rb
  op_shl ............... 6236  0x08: rd := ra << (rb AND 63)
  op_shr ............... 6407  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 65D8  0x0A: rd := ra < rb (знаково)
  op_eq ................ 67D7  0x0B: rd := ra = rb
  op_halt .............. 69D6  0x12: поля + imm32 = код возврата
  interp ............... 6ACB  цикл: предел шагов (trap 6) + порядок
                              проверок SPEC/12 п. 7 (v0 01..12 + v1
                              13..18 — 24 опкода, E7.4-2c)

вход (kernel.wall):
  main ................. 70FF  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (14): s_use 72BD (43Б) s_long 72E8 s_oup 7302 s_rup 731A
  s_sig 7332 s_ver 7346 s_mem 735A s_code0 736E s_len 7384 s_res 7398
  s_data 73AC (21Б, E7.4-2a) s_trap 73C1 s_steps 73D1 (8Б) s_crlf 73D8 (2Б)
глобали (21): hstdout 73DA cmdline 73E2 written 73EA wlen 73F2
  arg1[64] 73FA (0x200) w1[64] 75FA (0x200) hdrbuf[8] 77FA (0x40)
  codebuf 783A codesize 7842 memsize 784A ram 7852 pc 785A steps 7862
  steplim 786A uq 7872 ur 787A (E7.4-2b — результат udivmod)
  csp 7882 (E7.4-2c — глубина стека вызовов)
  regs[16] 788A (0x80) got 790A trapbuf[48] 7912 (0x180)
  cstack[1024] 7A92 (0x2000 — стек вызовов, E7.4-2c)
конец тела: 9A92 (vsize 0x8A92)
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

SHA-256 артефактов: kernel.b2 — B9BE24A9…76654A, kernel.brick —
A76E42FF…1B9FE32E, kernel.exe — 9F569617…1BE4799 (полные — VERIFY.md).
