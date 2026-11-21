# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 62976 байта (0xF600) |
| SHA-256 | 283CA3D75D1A7A946C5FD88FBC93F7DB5D755616DA8B9831E76EF639D2A0ED1F |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 8 частей bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 89709 Б (33% предела входа 256 КиБ; 3074 строки — заголовок bridge.b2) |
| Тело секции | 62354 байта (0xF392), RVA 0x1000, SRD 0xF400 |
| VirtualSize | 0xF392 (одна секция); target 0xF201, bss 0x191 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 12998 (bridge.b2; 100% M — H=0, круг T-E9-20: M=12998 H=0) |
| Меток в исходнике | 885 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 86 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 351949143 + 45361314 + 34316664 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* — MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md, MAP/M5-BRIDGE-E.md и MAP/M5-BRIDGE-L.md).

```
сервис (bridge_self_c.wall — реинкарнации K3-C001..C007 ядра kernel.wall):
  print_error        020A  печать сообщения + ExitProcess(код)
  skip0              0285  пропуск argv0 + разделителей
  read_arg           0658  слово-аргумент (>= 128 -> код 3)
  check_end          098F  ровно три аргумента (иначе справка, код 2)
  widen              0AD8  имя -> UTF-16LE для CreateFile2
  copy_str           0C8A  копия n байтов в буфер (факт-строка)
  out_dec            0D61  десятичная запись числа в буфер
  out_hex            103E  8 ЗАГЛАВНЫХ hex-цифр в буфер

разбор PE и семейство (bridge_self_pe.wall — срез E9.2-1):
  rd16               11AB  LE u16 по байтовому смещению
  rd32               122C  LE u32 по байтовому смещению
  fail_family        134F  ERR=FAMILY + выход 6 (единственный отказ)
  guard              1398  границы чтения [off, off+n) из exebuf
  check_head         1411  MZ + PE-сигнатура по e_lfanew + длина 0x1B0
  check_opt          1640  Machine/NSections/OptHdr/Chars/Magic/Subsys
  check_base         17FB  ImageBase (2 dword)/SectAlign/FileAlign
  check_sect         192A  имя .text/vaddr/chars; vsize/raw/rawptr
  check_size         1C71  SizeOfImage/Headers/Raw/файл; вход в секции
  check_body         1ED5  тело не пустое и не из одних нулей
  stub_name          1FE9  имя модуля из DOS-заглушки (префикс/игла)
  rva_off            23FA  RVA тела (0x1000+) -> файловое смещение
  walk_descs         243C  дескрипторы IDT (1 шт + терминатор), thunk
  cstr_len           2832  длина C-строки (quirk: без NUL -> len-1)
  check_dll          2911  имя DLL == kernel32.dll (без регистра)
  walk_funcs         2A7A  счёт записей INT/IAT (терминатор/чётность)
  print_facts        2CEB  факт-строка MODULE/ENTRY/.../BSS в stdout

декодер x86-подмножества SPEC/05, часть 1 (bridge_self_d.wall — E9.2-2/3a):
  fb                 31AF  байт файла с границей (отказ — данные)
  rel8               3240  знаковый байт
  rel32              32B7  знаковый dword (2^32 — произведением)
  u32                3440  БЕЗзнаковый dword (imm32/disp32 SIB)
  u64                356B  БЕЗзнаковый qword (imm64; 2^32 множителем)
  modrm_read         35F6  полный разбор modrm+SIB+disp -> om*
  set_reg            3E7D  операнд-регистр в слот 1/2
  set_rm             3F16  операнд из modrm (рег mod=3 | память)
  set_imm            4037  непосредственный в слот (знаковая печать)
  set_immu           40D0  imm64 в слот (БЕЗзнаковая печать, вид 7)
  set_tgt            4169  операнд-цель перехода в слот 1
  set_cl             41AB  операнд «cl» в слот 2
  set_cnt            41DE  счётчик сдвига (целое) в слот 2
  alu_id             4220  id мнемоники ALU по байту (таблица)
  dec0f              4321  группа 0F (movzx/test/imul)
  decalu             47CA  семейство ALU 00..3D
  decmod             4CEB  test/mov/lea 84..8D

декодер, часть 2 (bridge_self_d2.wall — E9.2-3a):
  decimm             50D2  push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC
  decshift           5872  сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)
  decgrp             5C3B  imm-группа 80/81/83 (reg с REX.R)
  decgrp2            61B4  хвостовые C6/C7/F6/F7/FF (call косвенный)
  decbr              695F  переходы E8/E9/EB/jcc rel8 (классы 2/3/4)
  decode_ins         6DA8  диспетчер: REX, 0F, множества байтов; da*/om*

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a):
  walk_code          7A03  стек целей (куча), проход, тени/нули/терминалы
  sweep_ins          7F80  выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target        81FB  target (вилка raw-0x1FF) и bss

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b):
  fill_offs          8435  смещения NUL-имён блоба -> массив offs
  init_tables        857D  таблицы мнемоник/условий/регистров + шапка
  tpl_dec            86C5  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             88C0  байт в буфер вывода
  app_name           892B  имя из блоба по таблице смещений
  app_reg            89E9  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           8B4E  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            8DF9  знаковый hex (imm/цель/счётчик)
  out_hxu64          8E63  hex u64 (отрицательное = битовый образ)
  out_hex2           8F0D  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          9058  минимум 4 hex-цифры (@смещения)
  out_sdec           93C5  знаковый dec со знаком +/-
  note_op            9470  примечание одного операнда (== _note)
  emit_note          97F5  примечание H-строки (jcc/имена/[rip±d])
  emit_h             9AAC  H-строка выжившей инструкции
  emit_data          9CA0  данные сегмента DZ/DB (== оракул)
  app_tpl            A16B  кусок шаблона шапки из tplb

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          A1F8  записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            A69B  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           AB40  базы импортов: iatoff/intoff/nameoff/idtoff
  imp_labels         AC9E  метки iat_/d* (представимость!) + knownoff; impbad
  build_sstate       B40B  карта выживших: 1 старт / 2 внутри
  sem_add            B5F5  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            B89E  твонки IAT/INT: валидность значений + меток hint
  dd_idt             BCD2  дескриптор IDT — кандидат DD
  sem_filter         BD74  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         C7C5  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)
  out_hexl           CB5A  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       CE05  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           CFFC  строка разреза «:имя ; @смещ4»
  emit_dollar        D0AC  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D1C1  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         D52A  сборка карт: кучи + sstate + импорты + семантика + метки операндов

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b):
  out_hexl           CB5A  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       CE05  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           CFFC  строка разреза «:имя ; @смещ4»
  emit_dollar        D0AC  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D1C1  строка DD (5 значений) / DQ ($имя | 0)
  emit_body          D937  ДРАЙВЕР: шапка + проход по разрезам [0, target) + запись .b2 (коды 8/9)

вход (bridge.wall):
  main ................. DFFE  CLI -> чтение EXE -> проверки -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (H) -> факты
```

## 3. Данные образа (RVA)

```
строки (39): s_use E3F7 s_long E42D s_oexe E448 s_rexe E462
  s_family E47C s_big E494 s_oout E4AD s_wout E4C7 s_f1 E4E2
  s_f2 E4F5 s_f3 E4FC s_f4 E503 s_f5 E508 s_f6 E50D
  s_f7 E512 s_f8 E51A s_crlf E51F s_pref E521 s_needle E52E
  s_dll E53F s_h E54B s_at E54D s_dz E551 s_db E554
  s_iat E557 s_dd E55B s_dq E55E s_mem E561 s_rip E566
  s_cl E56A s_j E56C s_comma E56D s_mn E56F s_cc E5E8
  s_r64 E610 s_r8 E64E s_r16 E690 s_r32 E6CE s_tpl E714
глобали (78): hstdout E8A2 cmdline E8AA written E8B2 wlen E8BA
  exebuf E8C2 exelen E8CA entryrva E8D2 vsize E8DA rawsize E8E2 rawptr E8EA
  modlen E8F2 thunk E8FA dllfile E902 impn E90A insmap E912 lenmap E91A
  pend E922 rawlim E92A psp E932 inscount E93A maxend E942 swcur E94A
  target E952 bss E95A dlen E962 dcls E96A dtgt E972 dpos E97A
  mpos E982 mreg E98A dname E992 dcc E99A dargc E9A2 da1k E9AA
  da2k E9B2 da1r E9BA da2r E9C2 da1s E9CA da2s E9D2 da1v E9DA
  da2v E9E2 damem E9EA ombase E9F2 omidx E9FA omscale EA02 omdisp EA0A
  omsize EA12 omrip EA1A mkind EA22 mrreg EA2A mrdip EA32 mripon EA3A
  sdump EA42 outmem EA4A outbuf EA52 outcur EA5A iatoff EA62 intoff EA6A
  nameoff EA72 idtoff EA7A impbad EA82 kn EA8A snlen EA92 semcnt EA9A
  semacc EAA2 hhrv EAAA hno EAB2 hnl EABA snam EAC2 noffs EACA
  knownoff EAD2 semrows EADA labmap EAE2 sstate EAEA semstate EAF2
  arg1 EAFA (0x80) arg2 EB7A (0x80) arg3 EBFA (0x80)
  factbuf EC7A (0xC0) o_mn ED3A (0xE8) o_cc EE22 (0x88)
  o_r64 EEAA (0x88) o_r8 EF32 (0x88) o_r16 EFBA (0x88)
  o_r32 F042 (0x88) tplb F0CA (0xC8) w1 F192 (0x200)
конец тела: F392 (vsize 0xF392)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0xF201..0xF392, 0x191 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=12998; как kernel/uva — T-E9-20).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 40A6E7DE…03C47D, bridge.brick — FA6CDBCF…42F211D, bridge.exe — 283CA3D7…2A0ED1F (полные — VERIFY.md).
