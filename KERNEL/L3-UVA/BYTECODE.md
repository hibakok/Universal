# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 17920 байт (0x4600) |
| SHA-256 | 83F76ED9ECD9908CB1A12CC72D39B7F747E7192CB4A2427A158765C0639BAB67 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.3-2): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 5 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 870 строк, 26438 Б (10% предела входа 256 КиБ) |
| Тело секции | 17293 байта (0x438D), RVA 0x1000 |
| VirtualSize | 0x438D (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 275 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 21 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 49237826 + 10810897 + 4680888 + 5015 шагов) |

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

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 3476  структура: .mem/мнемоники/длины; «нет .mem» = 0001
  enc_halt ............. 38EE  12 00 imm32 LE -> outbuf+24+at
  enc_f1 ............... 39C2  F1 op rd:ra rb -> outbuf+24+at (mov/АЛУ)
  pass2 ................ 3CBF  кодирование F1 + halt (чтение ВПЕРЁД)

контейнер (uva_self_w.wall):
  put32 ................ 3F77  LE u32 по смещению outbuf
  make_header .......... 4053  заголовок .UP v1 (24 Б, SPEC/13 п. 2)
  write_out ............ 41BE  CREATE_ALWAYS + WriteFile(24+pc)

вход (uva.wall):
  main ................. 4363  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_mn — таблица 18 мнемоник ISA v0 через пробел
в порядке опкодов 01..12):

```
  s_use 4799  s_long 47C0  s_osrc 47D8  s_rsrc 47EF  s_big 4806
  s_fmt 481C  s_code0 4833  s_oout 4847  s_wout 485E  s_hexd 4876
  s_up01 4886  s_dotmem 488A  s_mn 488E
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт):

```
  hstdout 48D5  cmdline 48DD  written 48E5  wlen 48ED
  arg1[64] 48F5  arg2[64] 4AF5  w1[64] 4CF5  w2[64] 4EF5
  srcbuf 50F5  srclen 50FD  outbuf 5105  memsize 510D  pc 5115
  lpos 511D  lln 5125  lna 512D  lne 5135  tcnt 513D
  tstart[12] 5145  tend[12] 51A5  nval 5205  fmtbuf[48] 520D
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
