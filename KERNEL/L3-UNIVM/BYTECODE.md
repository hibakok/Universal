# BYTECODE. Модуль M3-UNIVM — карта образа

Паспорт файла: KERNEL/L3-UNIVM/BYTECODE.md | слой: L3 | роль: разбор образа kernel.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UNIVM/kernel.exe, 23040 байт (0x5A00) |
| SHA-256 | 8AFF54B8FDE402A0E8383E3C1A060588F1D3EC6130E444B963546ADAC66F4D19 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.2-4): сборка из kernel.wall — wall.exe(splice(kernel.wall)) -> kernel.b2 -> enc -> kernel.brick -> brick -> pegen + kernel.peg. Воспроизводимость закреплена в батарее (T-E7-09); kernel.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UNIVM/kernel.wall — корень + 5 частей kernel_self_*.wall (WALL v2, разрез SPEC/10); склейка 1138 строк, 37761 Б (14% предела входа 256 КиБ) |
| Тело секции | 22244 байта (0x56F4), RVA 0x1000, SRD 0x5800 |
| VirtualSize | 0x56F4 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 kernel. No DOS support.» (имя модуля — kernel.peg) |
| M-строк в исходнике | 4492 (kernel.b2 — 4813 строк; плоский, генерируемый) |
| Меток в исходнике | 251 из 2048 (лимит brick; карта — LAB/ai/kernel_labelmap.py) |
| Функций | 32 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-09: 71148653 + 15667419 + 6182260 + 4997 шагов) |

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

контейнер .UP (kernel_self_up.wall):
  rd32 ................. 203E  LE u32 по байтовому смещению
  read_up .............. 2161  чтение + разбор SPEC/13 (отказы п. 4) + RAM

память и устройства (kernel_self_mem.wall — срез E7.2-3):
  get_ram .............. 28AD  RAM: GlobalAlloc(0, memsize) + обнуление
  op_ldb ............... 2AA7  0x0C: rd := sext8(RAM) / окно -> 0
  op_stb ............... 2DD3  0x0D: байт в RAM / окно+0 = консоль
  op_ldq ............... 3175  0x0E: слово LE (только RAM, целиком)
  op_stq ............... 369F  0x0F: слово LE в RAM (только целиком)

переходы (kernel_self_j.wall — срез E7.2-4):
  op_jmp ............... 3C3E  0x10: pc := imm32 (беззнаковое)
  op_jnz ............... 3D2C  0x11: pc := imm32 / pc+6 по regs[rd]

интерпретатор (kernel_self_vm.wall):
  copy_str ............. 3E7D  копия n байтов в буфер (диагностика)
  out_dec .............. 3F54  десятичная запись числа в буфер
  fail_trap ............ 4231  диагностика ловушки + выход 1
  op_const ............. 4405  0x01: rd := sext(imm32) (сдвиг порога)
  op_mov ............... 45E0  0x02: rd := ra (rb-заполнитель = 0)
  op_add ............... 476B  0x03: rd := (ra + rb) mod 2^64
  op_sub ............... 4924  0x04: rd := (ra - rb) mod 2^64
  op_and ............... 4ADD  0x05: rd := ra AND rb
  op_or ................ 4C96  0x06: rd := ra OR rb
  op_xor ............... 4E4F  0x07: rd := ra XOR rb
  op_shl ............... 5008  0x08: rd := ra << (rb AND 63)
  op_shr ............... 51D9  0x09: rd := ra >> (rb AND 63) — логический
  op_lt ................ 53AA  0x0A: rd := ra < rb (знаково)
  op_eq ................ 55A9  0x0B: rd := ra = rb
  op_halt .............. 57A8  0x12: поля + imm32 = код возврата
  interp ............... 589D  цикл: предел шагов (trap 6) + порядок
                              проверок SPEC/12 п. 7 (все 18 опкодов)

вход (kernel.wall):
  main ................. 5D7E  CLI -> чтение -> разбор -> исполнение
```

## 3. Данные образа (RVA)

```
строки (13): s_use 5F3C (43Б) s_long 5F67 s_oup 5F81 s_rup 5F99
  s_sig 5FB1 s_ver 5FC5 s_mem 5FD9 s_code0 5FED s_len 6003 s_res 6017
  s_trap 602B s_steps 603B (8Б) s_crlf 6042 (2Б)
глобали (17): hstdout 6044 cmdline 604C written 6054 wlen 605C
  arg1[64] 6064 (0x200) w1[64] 6264 (0x200) hdrbuf[8] 6464 (0x40)
  codebuf 64A4 codesize 64AC memsize 64B4 ram 64BC pc 64C4 steps 64CC
  steplim 64D4 regs[16] 64DC (0x80) got 655C trapbuf[48] 6564 (0x180)
конец тела: 66F4 (vsize 0x56F4)
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

SHA-256 артефактов: kernel.b2 — E4E3774D…1E3D87, kernel.brick —
8EF7C93F…ED03699A, kernel.exe — 8AFF54B8…ADAC66F4D19 (полные — VERIFY.md).
