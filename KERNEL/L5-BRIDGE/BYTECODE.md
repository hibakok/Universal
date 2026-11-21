# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 48128 байта (0xBC00) |
| SHA-256 | B553660745D90891445DBF30F4B351B11F46747E3B99039A58593AC56E3086DD |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 5 частей bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 68177 Б (26% предела входа 256 КиБ; 2411 строк — заголовок bridge.b2) |
| Тело секции | 47278 байт (0xB8AE), RVA 0x1000, SRD 0xBA00 |
| VirtualSize | 0xB8AE (одна секция); target 0xB801, bss 0xAD (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 9696 (bridge.b2; 100% M — H=0, круг T-E9-20: M=9696 H=0) |
| Меток в исходнике | 703 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 70 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 247712334 + 33744322 + 23049909 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* —
MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md и MAP/M5-BRIDGE-E.md).

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

декодер x86-подмножества SPEC/05 (bridge_self_d.wall — срезы E9.2-2/3a):
  fb ................... 41AF  байт файла по смещению с границей (-1)
  rel8 ................. 4240  знаковое расширение байта
  rel32 ................ 42B7  знаковое расширение dword (2^32 — 16777216*256)
  u32 .................. 4440  БЕЗзнаковый dword (imm32/disp32-SIB)
  u64 .................. 456B  БЕЗзнаковый qword (imm64; два u32)
  modrm_read ........... 45F6  ПОЛНЫЙ modrm+SIB+disp (E9.2-3a): reg mod=3
                               или память base/index/scale/disp/rip-rel;
                               mreg с REX.R (замена modrm_skip E9.2-2)
  set_reg .............. 4E7D  операнд-регистр в слот 1/2
  set_rm ............... 4F16  операнд из modrm (reg/память) в слот 1/2
  set_imm .............. 5037  непосредственный в слот (знаковая печать)
  set_immu ............. 50D0  imm64 в слот (БЕЗзнаковая печать, вид 7)
  set_tgt ............... 5169  операнд-цель перехода (смещение тела)
  set_cl ............... 51AB  операнд «cl» (сдвиг по CL)
  set_cnt .............. 51DE  счётчик сдвига (целое-маска 63/31)
  alu_id ............... 5220  id мнемоники ALU по base = b & 248
  dec0f ................ 5321  0F: jcc rel32 / movzx B6,B7 / imul AF
  decalu ............... 57CA  ALU 00..3D: r/m-формы, AL,imm8, eAX,imm32
  decmod ............... 5CEB  modrm-без-imm: test 84/85 / mov 88..8B /
                               lea 8D (операнды по биту d)

декодер, часть 2 (bridge_self_d2.wall — срезы E9.2-2/3a):
  decimm ............... 60D2  push/pop/98/99/B0..BF/ret/int3 (терминалы;
                               imm64 при W — вид 7 беззнаковый)
  decshift ............. 6872  C0/C1 с imm8, D3 по cl; reg {rol,shl,shr,sar}
  decgrp ............... 6C3B  80/81/83: reg {add,or,and,sub,xor,cmp}; imm 1/4
  decgrp2 .............. 71B4  C6/C7/F6/F7/FF: neg/idiv/inc/dec/call
  decbr ................ 795F  E8/E9/EB/70..7F: цели -> dtgt, классы, dcc
  decode_ins ........... 7DA8  диспетчер: REX (W/R/X/B), 0F, таблица
                               семейств; ОПЕРАНДЫ da1*/da2*/om*; omrip =
                               конец инструкции + disp32 (riprel)

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a):
  walk_code ............ 8A03  стек целей (куча), проход, тени/нули/терминалы
  sweep_ins ............ 8F80  выжившие (младший адрес), inscount/maxend;
                               СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target .......... 91FB  target (вилка raw-0x1FF) и bss

эмиссия b2, raw-режим (bridge_self_e.wall — срез E9.2-3a):
  fill_offs ............ 9435  смещения NUL-имён блоба -> массив offs
  init_tables .......... 957D  таблицы мнемоник/условий/регистров + шапка
  tpl_dec .............. 96C5  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch ............... 98C0  байт в буфер вывода
  app_name ............. 992B  имя из блоба по таблице смещений
  app_reg .............. 99E9  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv ............. 9B4E  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs .............. 9DF9  знаковый hex (imm/цель/счётчик)
  out_hxu64 ............ 9E63  hex u64 (отрицательное = битовый образ)
  out_hex2 ............. 9F0D  ровно 2 hex-цифры (байты H/DB)
  out_hex4m ............ A058  минимум 4 hex-цифры (@смещения)
  out_sdec ............. A3C5  знаковый dec со знаком +/-
  note_op .............. A470  примечание одного операнда (== _note)
  emit_note ............ A7F5  примечание H-строки (jcc/имена/[rip±d])
  emit_h ............... AAAC  H-строка выжившей инструкции
  emit_data ............ ACA0  данные сегмента DZ/DB (== оракул)
  app_tpl .............. B16B  кусок шаблона шапки из tplb
  emit_raw ............. B1F8  шапка + H/DZ/DB по sdump + запись .b2

вход (bridge.wall):
  main ................. B6C1  CLI -> чтение EXE -> проверки -> спуск ->
                               таблицы -> raw-эмиссия .b2 -> факты
```

## 3. Данные образа (RVA)

```
строки (36): s_use AAB5 (54Б) s_long AAEB (27Б) s_oexe AB06 (26Б)
  s_rexe AB20 (26Б) s_family AB3A (24Б) s_big AB52 (25Б) s_oout AB6B
  (26Б) s_wout AB85 (27Б) s_f1 ABA0 (19Б) s_f2 ABB3 (7Б) s_f3 ABBA
  (7Б) s_f4 ABC1 (5Б) s_f5 ABC6 (5Б) s_f6 ABCB (5Б) s_f7 ABD0 (8Б)
  s_f8 ABD8 (5Б) s_crlf ABDD (2Б) s_pref ABDF (13Б) s_needle ABEC
  (17Б) s_dll ABFD (12Б) s_h AC09 (2Б) s_at AC0B (4Б) s_dz AC0F
  (3Б) s_db AC12 (3Б) s_mem AC15 (5Б) s_rip AC1A (4Б) s_cl AC1E
  (2Б) s_j AC20 (1Б) s_comma AC21 (2Б) s_mn AC23 (121Б) s_cc AC9C
  (40Б) s_r64 ACC4 (62Б) s_r8 AD02 (66Б) s_r16 AD44 (62Б) s_r32
  AD82 (70Б) s_tpl ADC8 (398Б HEX-текст шапки)
глобали (59): hstdout AF56 cmdline AF5E written AF66 wlen AF6E
  exebuf AF76 exelen AF7E entryrva AF86 vsize AF8E rawsize AF96
  rawptr AF9E modlen AFA6 thunk AFAE dllfile AFB6 impn AFBE insmap
  AFC6 lenmap AFCE pend AFD6 rawlim AFDE psp AFE6 inscount AFEE
  maxend AFF6 swcur AFFE target B006 bss B00E dlen B016 dcls B01E
  dtgt B026 dpos B02E mpos B036 mreg B03E dname B046 dcc B04E dargc
  B056 da1k B05E da2k B066 da1r B06E da2r B076 da1s B07E da2s B086
  da1v B08E da2v B096 damem B09E ombase B0A6 omidx B0AE omscale B0B6
  omdisp B0BE omsize B0C6 omrip B0CE mkind B0D6 mrreg B0DE mrdip B0E6
  mripon B0EE sdump B0F6 outmem B0FE outbuf B106 outcur B10E
  arg1[16] B116 (0x80) arg2[16] B196 (0x80) arg3[16] B216 (0x80)
  factbuf[24] B296 (0xC0) o_mn[29] B356 (0xE8) o_cc[17] B43E (0x88)
  o_r64[17] B4C6 (0x88) o_r8[17] B54E (0x88) o_r16[17] B5D6 (0x88)
  o_r32[17] B65E (0x88) tplb[25] B6E6 (0xC8) w1[32] B7AE (0x100)
конец тела: B8AE (vsize 0xB8AE)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[32] (урок E9.2-2,
подтверждён ростом E9.2-3a): выравнивающий хвост (0xB801..0xB8AE,
0xAD Б) падает внутрь w1 — rip-ссылок внутрь хвоста нет (lea — только
базы массивов, они ниже target), разбор моста над bridge.exe даёт 0
H-строк (M=9696; как kernel/uva — T-E9-20). Инвариант держится при
vsize mod 0x200 <= 0x101 (сейчас 0xAE) — при росте строк/глобалей
пересчитывать (срезы E9.2-3b/c добавят метки/эмиссию M-строк).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 238A77AE…8358FD49, bridge.brick —
E0ECB804…4B75E34B5, bridge.exe — B5536607…E3086DD (полные — VERIFY.md).
