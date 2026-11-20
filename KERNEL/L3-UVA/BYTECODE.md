# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 40960 байт (0xA000) |
| SHA-256 | 32ABF177E0C01AA019E05244A0E12FEB18E13CE0A28DBFA4F59C3805802145EE |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-3b): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 6 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 1471 строка, 51064 Б (20% предела входа 256 КиБ) |
| Тело секции | 40022 байта (0x9C56), RVA 0x1000 |
| VirtualSize | 0x9C56 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 454 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 30 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 89848915 + 18898356 + 10155733 + 5015 шагов) |

## 2. Карта функций (RVA — LAB/ai/uva_test.py по uva.brick)

Группировка — по частям uva.wall (состав — CARD.md; кирпичи K3-* —
MAP/M3-UVA.md).

```
сервис (uva_self_c.wall — реинкарнации K3-C001..C005 ядра + fail_format):
  print_error .......... 120A  печать сообщения + ExitProcess(код)
  skip0 ................ 1285  пропуск argv0 + разделителей
  read_arg ............. 1658  слово-аргумент (>= 128 -> код 3)
  check_end ............ 198F  ровно два аргумента (иначе справка, код 2)
  widen ................ 1AD8  имя -> UTF-16LE для CreateFile2
  fail_at .............. 1C8A  ERR=FORMAT AT=hex4 + CRLF, код 6

токены и числа (uva_self_t.wall):
  tok_is ............... 1F2A  токен == литерал (длина + байты)
  tokenize ............. 20AA  сегмент -> tstart/tend + tcnt
  parse_num ............ 2466  токен -> nval (imm32, переполнение в цикле)
  line_trim ............ 2A5F  ';' + края-разделители -> lna/lne
  line_next ............ 2D66  итератор строк по LF (lln, lpos)
  mn_find .............. 2EA0  токен -> индекс мнемоники 0..23 (-1 = нет;
                               E7.4-3a: 24 имени ISA v0+v1)
  parse_reg ............ 315C  токен -> nval = регистр r0..r15
  parse_memop .......... 3476  токен -> nval = рег, moff = смещ (E7.3-3)
  data_next ............ 3D24  итератор байтов .data: dpos -> nval, ровно
                               2 hex-цифры (E7.4-3b; 0 = строка исчерпана)

метки (uva_self_b.wall — E7.3-4):
  lab_skip ............. 439D  префикс метки на [lna,lne) -> nsa/nsb
  lab_find ............. 486C  имя [a,b) -> индекс таблицы (-1 = нет)
  lab_add .............. 4A76  регистрация метки nsa/nsb со значением pc
  parse_target ......... 4BE3  токен -> nval: метка таблицы или число

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 4EA7  структура: метки/.mem/.data (dcnt)/
                               мнемоники/длины (E7.4-3b: + .data)
  enc_halt ............. 5553  12 00 imm32 LE -> outbuf+24+at
  enc_f1 ............... 5627  F1 op rd:ra rb -> outbuf+24+at (mov/АЛУ
                               v0 + mul/div/mod/sra v1 — E7.4-3a)
  enc_f2 ............... 5924  F2 op rd:ra imm32 (const/память, E7.3-3)
  enc_f3 ............... 5D94  F3 [16/17/23][00/rd][imm32] — jmp/jnz/
                               call (E7.4-3a: call как jmp, опкод = i+1)
  enc_f0 ............... 60C8  F0 [24] — ret, 0 операндов (E7.4-3a)
  pass2 ................ 615B  кодирование всех 24 форм + эмиссия байтов
                               .data в outbuf+24+pc+dcnt (E7.4-3b)

контейнер (uva_self_w.wall):
  put32 ................ 66F4  LE u32 по смещению outbuf
  make_header .......... 67D0  заголовок .UP v1/v2 (24 Б, SPEC/13 п. 2:
                               dcnt > 0 — версия 2 + dataoff = 24+pc;
                               отказ DATA — dcnt > memsize, E7.4-3b)
  write_out ............ 6A11  CREATE_ALWAYS + WriteFile(24+pc+dcnt)

вход (uva.wall):
  main ................. 6BCB  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_dotdata = '.data' — E7.4-3b, s_data — ERR=DATA,
s_mn — таблица 24 мнемоник ISA v0+v1 через пробел в порядке опкодов
01..18 — E7.4-3a):

```
  s_use 7001  s_long 7028  s_osrc 7040  s_rsrc 7057  s_big 706E
  s_fmt 7084  s_code0 709B  s_data 70AF  s_oout 70C2  s_wout 70D9
  s_hexd 70F1  s_up01 7101  s_dotmem 7105  s_dotdata 7109  s_mn 710E
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт; moff —
смещение операнда памяти E7.3-3; nsa/nsb — имя потреблённой метки,
lcnt/lsta/lend/lval — таблица меток E7.3-4: имена — границы в srcbuf,
копии не хранятся; dcnt/dpos — счёт и позиция итератора байтов .data,
E7.4-3b):

```
  hstdout 716E  cmdline 7176  written 717E  wlen 7186
  arg1[64] 718E  arg2[64] 738E  w1[64] 758E  w2[64] 778E
  srcbuf 798E  srclen 7996  outbuf 799E  memsize 79A6  pc 79AE
  dcnt 79B6  dpos 79BE  lpos 79C6  lln 79CE  lna 79D6  lne 79DE
  tcnt 79E6  tstart[12] 79EE  tend[12] 7A4E  nval 7AAE  moff 7AB6
  nsa 7ABE  nsb 7AC6  lcnt 7ACE
  lsta[512] 7AD6  lend[512] 8AD6  lval[512] 9AD6  fmtbuf[48] AAD6
```

## 4. Инварианты

1. Артефакты воспроизводимы фикс-пунктом T-E7-19: сборка из uva.wall
   конвейером (эмуляция) == uva.b2 == uva.brick == uva.exe байт-в-байт.
2. uva.b2 == оракулу WALL (lab_l2.compile_wall(splice(uva.wall))).
3. Точка входа 0x1200 (отклонение от SPEC/04 — SPEC/11 п. 6, инвариант
   8 SPEC/04: hint-имена на чётных RVA — фильтр батареи T-E6-22/33).
4. Правка любой части uva_self_*.wall без пересборки артефактов
   (LAB/ai/uva_test.py) и зелёного прогона батареи — незавершённое
   изменение (правило DOCS/04).
