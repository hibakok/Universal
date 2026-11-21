# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 28672 байта (0x7000) |
| SHA-256 | AC59A297C56010E971826DFFEE8E33FB9FFAA02750958AA7F9B08081A9029161 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 4 части bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 43594 Б (17% предела входа 256 КиБ; 1448 строк — заголовок bridge.b2) |
| Тело секции | 27881 байт (0x6CE9), RVA 0x1000, SRD 0x6E00 |
| VirtualSize | 0x6CE9 (одна секция); target 0x6C01, bss 0xE8 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 5996 (bridge.b2; 100% M — H=0, круг T-E9-20: M=5996 H=0) |
| Меток в исходнике | 457 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 42 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 105876311 + 20681812 + 11653166 + 5046 шагов) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* —
MAP/M5-BRIDGE.md и MAP/M5-BRIDGE-D.md).

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
  check_opt ............ 2640  Machine/NSections/OptHdr/Chars/Magic/Subsys
  check_base ........... 27FB  ImageBase (2 dword)/SectAlign/FileAlign
  check_sect ........... 292A  имя .text/vaddr/chars; vsize/raw/rawptr
  check_size ........... 2C71  SizeOfImage/Headers/Raw/файл; вход в секции
  check_body ........... 2ED5  тело не пустое и не全-нулевое
  stub_name ............ 2FE9  префикс + игла заглушки; имя 1..31 без
                               пробельных байтов -> modlen
  rva_off .............. 33FA  RVA тела -> файловое смещение
  walk_descs ........... 343C  IDT: ровно один дескриптор + терминатор;
                               INT/IAT -> thunk; имя DLL -> dllfile
  cstr_len ............. 3832  длина C-строки (quirk len-1 оракула)
  check_dll ............ 3911  kernel32.dll без учёта регистра (| 32)
  walk_funcs ........... 3A7A  счёт записей INT/IAT + чётность hint-RVA
  print_facts .......... 3CEB  факт-строка MODULE/ENTRY/VSIZE/RAW/IMP/
                               INS/TARGET/BSS (E9.2-2 — расширина)

декодер x86-подмножества SPEC/05 (bridge_self_d.wall — срез E9.2-2):
  fb ................... 41AF  байт файла по смещению с границей (-1)
  rel8 ................. 4240  знаковое расширение байта
  rel32 ................ 42B7  знаковое расширение dword (2^32 — 16777216*256)
  modrm_skip ........... 4440  modrm+SIB+disp по длине; mreg с REX.R
  dec0f ............... 49C0  0F: jcc rel32 / movzx B6,B7 / imul AF
  decalu ............... 4C7D  ALU 00..3D: r/m-формы, AL,imm8, eAX,imm32
  decmod ............... 4E44  modrm-без-imm: test/mov/lea

декодер, часть 2 (bridge_self_d2.wall — срез E9.2-2):
  decimm ............... 4EBB  push/pop/98/99/B0..BF/ret/int3 (терминалы)
  decshift ............. 51A2  C0/C1 с imm8, D3 по cl; reg {rol,shl,shr,sar}
  decgrp ............... 536F  80/81/83: reg {add,or,and,sub,xor,cmp}; imm 1/4
  decgrp2 .............. 55B7  C6/C7/F6/F7/FF: neg/idiv/inc/dec/call
  decbr ................ 58D1  E8/E9/EB/70..7F: цели -> dtgt, классы
  decode_ins ........... 5C72  диспетчер: REX, 0F, таблица классов/длин

спуск от входа (bridge_self_w.wall — срез E9.2-2):
  walk_code ............ 6A79  стек целей (куча), проход, тени/нули/терминалы
  sweep_ins ............ 6FF6  выжившие (младший адрес), inscount/maxend
  calc_target .......... 718D  target (вилка raw-0x1FF) и bss

вход (bridge.wall):
  main ................. 73C7  CLI -> чтение EXE -> проверки -> спуск ->
                               факты
```

## 3. Данные образа (RVA)

```
строки (19): s_use 779A (54Б) s_long 77D0 (27Б) s_oexe 77EB (26Б)
  s_rexe 7805 (26Б) s_family 781F (24Б) s_big 7837 (25Б) s_f1 7850
  (19Б) s_f2 7863 (7Б) s_f3 786A (7Б) s_f4 7871 (6Б) s_f5 7876 (5Б)
  s_f6 787B (5Б) s_f7 7880 (8Б) s_f8 7888 (5Б) s_crlf 788D (2Б)
  s_pref 788F (13Б) s_needle 789C (16Б) s_dll 78AC (12Б)
глобали (34): hstdout 78B9 cmdline 78C1 written 78C9 wlen 78D1
  exebuf 78D9 exelen 78E1 entryrva 78E9 vsize 78F1 rawsize 78F9
  rawptr 7901 modlen 7909 thunk 7911 dllfile 7919 impn 7921 insmap
  7929 lenmap 7931 pend 7939 rawlim 7941 psp 7949 inscount 7951
  maxend 7959 swcur 7961 target 7969 bss 7971 dlen 7979 dcls 7981
  dtgt 7989 dpos 7991 mpos 7999 mreg 79A1
  arg1[16] 79A9 (0x80) arg2[16] 7A29 (0x80) arg3[16] 7AA9 (0x80)
  factbuf[24] 7B29 (0xC0) w1[32] 7BE9 (0x100)
конец тела: 7CC9 (vsize 0x6CE9)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[32] (урок E9.2-2:
при factbuf последним рост тела срезом спуска сдвинул vsize mod 0x200
с 0xBF на 0xE9 > 0xC1 — выравнивающий хвост (0x6C01..0x6CE9) начинался
ДО базы factbuf, 18 lea [rip+$factbuf] расширенной print_facts остались
без меток, H=18; при w1 последнем (0x100 Б) хвост падает внутрь w1 и
все базы массивов ниже target — разбор моста над bridge.exe даёт 0
H-строк (M=5996; как kernel/uva — T-E9-20). Инвариант держится при
vsize mod 0x200 <= 0x101 — при росте строк/глобалей пересчитывать.

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 08C83CB3…63B7DBB, bridge.brick —
E7A3FAE7…C61C2D, bridge.exe — AC59A297…02 9161 (полные — VERIFY.md).
