# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 15360 байт (0x3C00) |
| SHA-256 | CE071BE15F36263467ED173E1FD5C74375474B670BBA31A6411603814A98362F |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 2 части bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 22442 Б (9% предела входа 256 КиБ; 761 строка — заголовок bridge.b2) |
| Тело секции | 14527 байт (0x38BF), RVA 0x1000, SRD 0x3A00 |
| VirtualSize | 0x38BF (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 2893 (bridge.b2 — 3209 строк; плоский, генерируемый) |
| Меток в исходнике | 243 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 26 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 52136070 + 10350286 + 4545673 + 5046 шагов) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* —
MAP/M5-BRIDGE.md).

```
сервис (bridge_self_c.wall — реинкарнации K3-C001..C007 ядра kernel.wall):
  print_error .......... 120A  печать сообщения + ExitProcess(код)
  skip0 ................ 1285  пропуск argv0 + разделителей
  read_arg ............. 1658  слово-аргумент (>= 128 -> код 3)
  check_end ............ 198F  ровно три аргумента (иначе справка, код 2)
  widen ................ 1AD8  имя -> UTF-16LE для CreateFile2
  copy_str ............. 1C8A  копия n байтов в буфер (факт-строка)
  out_dec .............. 1D61  десятичная запись числа в буфер
  out_hex .............. 203E  8 ЗАГЛАВНЫХ hex-цифр в буфер

разбор PE и семейство (bridge_self_pe.wall — срез E9.2-1):
  rd16 ................. 21AB  LE u16 по байтовому смещению
  rd32 ................. 222C  LE u32 по байтовому смещению
  fail_family .......... 234F  ERR=FAMILY + выход 6 (единственный отказ)
  guard ................ 2398  границы чтения [off, off+n) из exebuf
  check_head ........... 2411  MZ + PE-сигнатура по e_lfanew + длина 0x1B0
  check_opt ............. 2640  Machine/NSections/OptHdr/Chars/Magic/Subsys
  check_base ............ 27FB  ImageBase (2 dword)/SectAlign/FileAlign
  check_sect ............ 292A  имя .text/vaddr/chars; vsize/raw/rawptr
  check_size ............ 2C71  SizeOfImage/Headers/Raw/файл; вход в секции
  check_body ............ 2ED5  тело не пустое и не全-нулевое
  stub_name ............. 2FE9  префикс + игла заглушки; имя 1..31 без
                               пробельных байтов -> modlen
  rva_off .............. 33FA  RVA тела -> файловое смещение
  walk_descs ........... 343C  IDT: ровно один дескриптор + терминатор;
                               INT/IAT -> thunk; имя DLL -> dllfile
  cstr_len ............. 3832  длина C-строки (quirk len-1 оракула)
  check_dll ............ 3911  kernel32.dll без учёта регистра (| 32)
  walk_funcs ........... 3A7A  счёт записей INT/IAT + чётность hint-RVA
  print_facts .......... 3CEB  факт-строка MODULE/ENTRY/VSIZE/RAW/IMP

вход (bridge.wall):
  main ................. 403E  CLI -> чтение EXE -> проверки -> факты
```

## 3. Данные образа (RVA)

```
строки (16): s_use 4402 (54Б) s_long 4438 s_oexe 4453 s_rexe 446D
  s_family 4487 s_big 449F s_f1 44B8 (20Б) s_f2 44CB (7Б) s_f3 44D2
  (7Б) s_f4 44D9 (6Б) s_f5 44DE (5Б) s_crlf 44E3 (2Б) s_pref 44E5
  (13Б) s_needle 44F2 (16Б) s_dll 4503 (12Б)
глобали (19): hstdout 450F cmdline 4517 written 451F wlen 4527
  exebuf 452F exelen 4537 entryrva 453F vsize 4547 rawsize 454F
  rawptr 4557 modlen 455F thunk 4567 dllfile 456F impn 4577
  arg1[16] 457F (0x80) arg2[16] 45FF (0x80) arg3[16] 467F (0x80)
  w1[32] 46FF (0x100) factbuf[24] 47FF (0xC0)
конец тела: 48BF (vsize 0x38BF)
```

Массивы объявлены ПОСЛЕ скаляров (factbuf — последним): выравнивающий
хвост тела (0x3801..0x38BF — 0xBE байт) падает внутрь factbuf, чья
база 0x37FF+0x1000 ниже target 0x3801 — все rip-ссылки глобалей
получают метки, разбор моста над bridge.exe даёт 0 H-строк (M=2893;
как kernel/uva — T-E9-20).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 2E2A6844…37D766F, bridge.brick —
0F5E608B…953A0, bridge.exe — CE071BE1…A98362F (полные — VERIFY.md).
