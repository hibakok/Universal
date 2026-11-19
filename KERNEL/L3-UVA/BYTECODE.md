# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 21504 байта (0x5400) |
| SHA-256 | C438E6ED0150CB772E11FC7E816BD7638F663CD5917F546FB7E8C59EF694F72A |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.3-3): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 5 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 1049 строк, 31823 Б (12% предела входа 256 КиБ) |
| Тело секции | 20820 байт (0x5154), RVA 0x1000 |
| VirtualSize | 0x5154 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 331 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 23 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 60722618 + 13582177 + 6189268 + 5015 шагов) |

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

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 3D24  структура: .mem/мнемоники/длины; «нет .mem» = 0001
  enc_halt ............. 419C  12 00 imm32 LE -> outbuf+24+at
  enc_f1 ............... 4270  F1 op rd:ra rb -> outbuf+24+at (mov/АЛУ)
  enc_f2 ............... 456D  F2 op rd:ra imm32 (const/память, E7.3-3)
  pass2 ................ 49DD  кодирование F1 + F2 + halt (чтение ВПЕРЁД)

контейнер (uva_self_w.wall):
  put32 ................ 4D36  LE u32 по смещению outbuf
  make_header .......... 4E12  заголовок .UP v1 (24 Б, SPEC/13 п. 2)
  write_out ............ 4F7D  CREATE_ALWAYS + WriteFile(24+pc)

вход (uva.wall):
  main ................. 5122  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_mn — таблица 18 мнемоник ISA v0 через пробел
в порядке опкодов 01..12):

```
  s_use 5558  s_long 557F  s_osrc 5597  s_rsrc 55AE  s_big 55C5
  s_fmt 55DB  s_code0 55F2  s_oout 5606  s_wout 561D  s_hexd 5635
  s_up01 5645  s_dotmem 5649  s_mn 564D
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт; moff —
смещение операнда памяти E7.3-3):

```
  hstdout 5694  cmdline 569C  written 56A4  wlen 56AC
  arg1[64] 56B4  arg2[64] 58B4  w1[64] 5AB4  w2[64] 5CB4
  srcbuf 5EB4  srclen 5EBC  outbuf 5EC4  memsize 5ECC  pc 5ED4
  lpos 5EDC  lln 5EE4  lna 5EEC  lne 5EF4  tcnt 5EFC
  tstart[12] 5F04  tend[12] 5F64  nval 5FC4  moff 5FCC  fmtbuf[48] 5FD4
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
