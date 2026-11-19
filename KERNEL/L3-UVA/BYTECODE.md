# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 37888 байта (0x9400) |
| SHA-256 | 2545730938D07371BC9D534DCBA636738CAB7B2065047BFF21E326A2BE5EF31B |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.3-4): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 6 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 1279 строк, 41386 Б (16% предела входа 256 КиБ) |
| Тело секции | 36907 байт (0x901B), RVA 0x1000 |
| VirtualSize | 0x901B (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 398 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 28 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 77376430 + 16565621 + 8229880 + 5015 шагов) |

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
  mn_find .............. 2EA0  токен -> индекс мнемоники 0..17 (-1 = нет)
  parse_reg ............ 315C  токен -> nval = регистр r0..r15
  parse_memop .......... 3476  токен -> nval = рег, moff = смещ (E7.3-3)

метки (uva_self_b.wall — E7.3-4):
  lab_skip ............. 3D24  префикс метки на [lna,lne) -> nsa/nsb
  lab_find ............. 41F3  имя [a,b) -> индекс таблицы (-1 = нет)
  lab_add .............. 43FD  регистрация метки nsa/nsb со значением pc
  parse_target ......... 456A  токен -> nval: метка таблицы или число

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 482E  структура: метки/.mem/мнемоники/длины
  enc_halt ............. 4CF8  12 00 imm32 LE -> outbuf+24+at
  enc_f1 ............... 4DCC  F1 op rd:ra rb -> outbuf+24+at (mov/АЛУ)
  enc_f2 ............... 50C9  F2 op rd:ra imm32 (const/память, E7.3-3)
  enc_f3 ............... 5539  F3 [16/17][00/rd][imm32] — jmp/jnz (E7.3-4)
  pass2 ................ 5837  кодирование всех 18 форм (чтение ВПЕРЁД)

контейнер (uva_self_w.wall):
  put32 ................ 5BF5  LE u32 по смещению outbuf
  make_header .......... 5CD1  заголовок .UP v1 (24 Б, SPEC/13 п. 2)
  write_out ............ 5E3C  CREATE_ALWAYS + WriteFile(24+pc)

вход (uva.wall):
  main ................. 5FE1  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_mn — таблица 18 мнемоник ISA v0 через пробел
в порядке опкодов 01..12):

```
  s_use 6417  s_long 643E  s_osrc 6456  s_rsrc 646D  s_big 6484
  s_fmt 649A  s_code0 64B1  s_oout 64C5  s_wout 64DC  s_hexd 64F4
  s_up01 6504  s_dotmem 6508  s_mn 650C
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт; moff —
смещение операнда памяти E7.3-3; nsa/nsb — имя потреблённой метки,
lcnt/lsta/lend/lval — таблица меток E7.3-4: имена — границы в srcbuf,
копии не хранятся):

```
  hstdout 6553  cmdline 655B  written 6563  wlen 656B
  arg1[64] 6573  arg2[64] 6773  w1[64] 6973  w2[64] 6B73
  srcbuf 6D73  srclen 6D7B  outbuf 6D83  memsize 6D8B  pc 6D93
  lpos 6D9B  lln 6DA3  lna 6DAB  lne 6DB3  tcnt 6DBB
  tstart[12] 6DC3  tend[12] 6E23  nval 6E83  moff 6E8B
  nsa 6E93  nsb 6E9B  lcnt 6EA3
  lsta[512] 6EAB  lend[512] 7EAB  lval[512] 8EAB  fmtbuf[48] 9EAB
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
