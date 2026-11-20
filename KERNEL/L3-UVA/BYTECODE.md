# BYTECODE. Модуль M3-UVA — карта образа

Паспорт файла: KERNEL/L3-UVA/BYTECODE.md | слой: L3 | роль: разбор образа uva.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L3-UVA/uva.exe, 38400 байта (0x9600) |
| SHA-256 | 6A4EFC9AB85097403886D79FF3657C455AD5D9B348EB17BD16CE86CCF0862CC5 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-3a): сборка из uva.wall — wall.exe(splice(uva.wall)) -> uva.b2 -> enc -> uva.brick -> brick -> pegen + uva.peg. Воспроизводимость закреплена в батарее (T-E7-19); uva.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L3-UVA/uva.wall — корень + 6 частей uva_self_*.wall (WALL v2, разрез SPEC/10); склейка 1318 строк, 43662 Б (17% предела входа 256 КиБ) |
| Тело секции | 37420 байт (0x924C), RVA 0x1000 |
| VirtualSize | 0x924C (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 uva. No DOS support.» (имя модуля — uva.peg) |
| Меток в исходнике | 410 из 2048 (лимит brick; карта — LAB/ai/uva_test.py) |
| Функций | 29 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E7-19: 78961480 + 16960465 + 8565575 + 5015 шагов) |

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

метки (uva_self_b.wall — E7.3-4):
  lab_skip ............. 3D24  префикс метки на [lna,lne) -> nsa/nsb
  lab_find ............. 41F3  имя [a,b) -> индекс таблицы (-1 = нет)
  lab_add .............. 43FD  регистрация метки nsa/nsb со значением pc
  parse_target ......... 456A  токен -> nval: метка таблицы или число

проходы (uva_self_l.wall / uva_self_e.wall):
  pass1 ................ 482E  структура: метки/.mem/мнемоники/длины
  enc_halt ............. 4D82  12 00 imm32 LE -> outbuf+24+at
  enc_f1 ............... 4E56  F1 op rd:ra rb -> outbuf+24+at (mov/АЛУ
                               v0 + mul/div/mod/sra v1 — E7.4-3a)
  enc_f2 ............... 5153  F2 op rd:ra imm32 (const/память, E7.3-3)
  enc_f3 ............... 55C3  F3 [16/17/23][00/rd][imm32] — jmp/jnz/
                               call (E7.4-3a: call как jmp, опкод = i+1)
  enc_f0 ............... 58F7  F0 [24] — ret, 0 операндов (E7.4-3a)
  pass2 ................ 598A  кодирование всех 24 форм (чтение ВПЕРЁД)

контейнер (uva_self_w.wall):
  put32 ................ 5DDD  LE u32 по смещению outbuf
  make_header .......... 5EB9  заголовок .UP v1 (24 Б, SPEC/13 п. 2)
  write_out ............ 6024  CREATE_ALWAYS + WriteFile(24+pc)

вход (uva.wall):
  main ................. 61C9  CLI -> чтение -> pass1 -> pass2 -> запись
```

## 3. Данные образа (RVA)

Строки (CRLF-литералы диагностики, s_hexd — hex-цифры, s_up01 = 'UP01',
s_dotmem = '.mem', s_mn — таблица 24 мнемоник ISA v0+v1 через пробел
в порядке опкодов 01..18 — E7.4-3a):

```
  s_use 65FF  s_long 6626  s_osrc 663E  s_rsrc 6655  s_big 666C
  s_fmt 6682  s_code0 6699  s_oout 66AD  s_wout 66C4  s_hexd 66DC
  s_up01 66EC  s_dotmem 66F0  s_mn 66F4
```

Глобальные переменные (DZ 8; массивы — DZ 8n; нулевой старт; moff —
смещение операнда памяти E7.3-3; nsa/nsb — имя потреблённой метки,
lcnt/lsta/lend/lval — таблица меток E7.3-4: имена — границы в srcbuf,
копии не хранятся):

```
  hstdout 6754  cmdline 675C  written 6764  wlen 676C
  arg1[64] 6774  arg2[64] 6974  w1[64] 6B74  w2[64] 6D74
  srcbuf 6F74  srclen 6F7C  outbuf 6F84  memsize 6F8C  pc 6F94
  lpos 6F9C  lln 6FA4  lna 6FAC  lne 6FB4  tcnt 6FBC
  tstart[12] 6FC4  tend[12] 7024  nval 7084  moff 708C
  nsa 7094  nsb 709C  lcnt 70A4
  lsta[512] 70AC  lend[512] 80AC  lval[512] 90AC  fmtbuf[48] A0AC
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
