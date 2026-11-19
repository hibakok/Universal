# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 24576 байт (0x6000) |
| SHA-256 | 23713EEE32A8B98CF4726FE5EF97A493C1602C6606A77D1DE2014F97F138E24E |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-2a): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 5 частей kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 1293 строки, 42073 Б (16% предела входа 256 КиБ) |
| Тело секции | 23575 байт (0x5C17), RVA 0x1000, SRD 0x5E00 |
| VirtualSize | 0x5C17 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 4774 (kernel.b2 — 5224 строки; плоский, генерируемый) |
| Меток в исходнике | 269 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 33 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 76801855 + 16671867 + 6741793 + 4997 шагов) |

## 2. Карта функций (RVA — LAB/ai/kernel_labelmap.py по kernel.brick)

Группировка — по частям kernel.wall (состав — CARD.md; кирпичи K3-* —
MAP/M3-UNIVM.md).

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

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 439B  копия n байтов в буфер (диагностика)
  out_dec .............. 4472  десятичная запись числа в буфер
  fail_trap ............ 474F  диагностика ловушки + выход 1
  op_const ............. 4923  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 4AFE  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 4C89  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 4E42  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 4FFB  0x05: rd := ra AND rb
  op_or ................ 51B4  0x06: rd := ra OR rb
  op_xor ............... 536D  0x07: rd := ra XOR rb
  op_shl ............... 5526  0x08: rd := ra << (rb AND 63)
  op_shr ............... 56F7  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 58C8  0x0A: rd := ra < rb (знаково)
  op_eq ................ 5AC7  0x0B: rd := ra = rb
  op_halt .............. 5CC6  0x12: поля + imm32 = код возврата
  interp ............... 5DBB  цикл: предел шагов (trap 6) + порядок
                              проверок SPEC/12 п. 7 (все 18 опкодов)

вход (kernel.wall):
  main ................. 629C  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (14): s_use 645A (43Б) s_long 6485 s_oup 649F s_rup 64B7
  s_sig 64CF s_ver 64E3 s_mem 64F7 s_code0 650B s_len 6521 s_res 6535
  s_data 6549 (21Б, E7.4-2a) s_trap 655E s_steps 656E (8Б) s_crlf 6575 (2Б)
глобали (17): hstdout 6577 cmdline 657F written 6587 wlen 658F
  arg1[64] 6597 (0x200) w1[64] 6797 (0x200) hdrbuf[8] 6997 (0x40)
  codebuf 69D7 codesize 69DF memsize 69E7 ram 69EF pc 69F7 steps 69FF
  steplim 6A07 regs[16] 6A0F (0x80) got 6A8F trapbuf[48] 6A97 (0x180)
конец тела: 6C17 (vsize 0x5C17)
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

SHA-256 артефактов: kernel.b2 — E460ECD3…CAC0F8E05, kernel.brick —
2277D183…6C8DEA1EB, kernel.exe — 23713EEE…F138E24E (полные — VERIFY.md).
