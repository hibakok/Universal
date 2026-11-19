# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 15360 байт (0x3C00) |
| SHA-256 | 97D2EAC6E3F33F29D414D43CE08E0CB2B681D061F9BBC8D465CCCB80B0EDF537 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.3-1): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 5 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 717 строк, 21164 Б (8% предела входа 256 КиБ) |
| Тело секции | 14681 байт (0x3959), RVA 0x1000, SRD 0x3A00 |
| VirtualSize | 0x3959 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 240 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 18 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 40033371 + 8770334 + 3685750 + 5015 шагов) |

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

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 2EA0  структура: .mem/halt, pc; «нет .mem» = 0001
  enc_halt ............. 32CA  12 00 imm32 LE -> outbuf+24+at
  pass2 ................ 339E  кодирование halt (чтение ВПЕРЁД)

контейнер (uva_self_w.wall):
  put32 ................ 3586  LE u32 по смещению outbuf
  make_header .......... 3662  заголовок .UP v1 (24 Б, SPEC/13 п. 2)
  write_out ............ 37CD  CREATE_ALWAYS + WriteFile(24+pc)

вход (uva.wall):
  main ................. 3972  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_halt = 'halt' — ключевые слова среза):

```
  s_use 3DA8  s_long 3DCF  s_osrc 3DE7  s_rsrc 3DFE  s_big 3E15
  s_fmt 3E2B  s_code0 3E42  s_oout 3E56  s_wout 3E6D  s_hexd 3E85
  s_up01 3E95  s_dotmem 3E99  s_halt 3E9D
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт):

```
  hstdout 3EA1  cmdline 3EA9  written 3EB1  wlen 3EB9
  arg1[64] 3EC1  arg2[64] 3FC1  w1[64] 40C1  w2[64] 41C1
  srcbuf 42C1  srclen 42C9  outbuf 42D1  memsize 42D9  pc 42E1
  lpos 42E9  lln 42F1  lna 42F9  lne 4301  tcnt 4309
  tstart[12] 4311  tend[12] 4371  nval 43D1  fmtbuf[48] 43D9
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
