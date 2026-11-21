# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 88576 байтов (0x15A00) |
| SHA-256 | B3598A111827D646BB5D597489BE38F18D68FA38AB90274684AE25BA529BC167 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 12 частей bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 123983 Б (47% предела входа 256 КиБ; 4362 строки — заголовок bridge.b2) |
| Тело секции | 87943 байта (0x15787), RVA 0x1000, SRD 0x15800 |
| VirtualSize | 0x15787 (одна секция); target 0x15601, bss 0x186 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 18701 (bridge.b2; 100% M — H=0, круг T-E9-20: M=18701 H=0) |
| Меток в исходнике | 1203 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 114 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 594593328 + 63479986 + 63726951 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* — MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md, MAP/M5-BRIDGE-E.md, MAP/M5-BRIDGE-L.md и MAP/M5-BRIDGE-M.md).

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
  fb                 32A5  байт файла с границей (отказ — данные)
  rel8               3336  знаковый байт
  rel32              33AD  знаковый dword (2^32 — произведением)
  u32                3536  БЕЗзнаковый dword (imm32/disp32 SIB)
  u64                3661  БЕЗзнаковый qword (imm64; 2^32 множителем)
  modrm_read         36EC  полный разбор modrm+SIB+disp -> om*
  set_reg            3F73  операнд-регистр в слот 1/2
  set_rm             400C  операнд из modrm (рег mod=3 | память)
  set_imm            412D  непосредственный в слот (знаковая печать)
  set_immu           41C6  imm64 в слот (БЕЗзнаковая печать, вид 7)
  set_tgt            425F  операнд-цель перехода в слот 1
  set_cl             42A1  операнд «cl» в слот 2
  set_cnt            42D4  счётчик сдвига (целое) в слот 2
  alu_id             4316  id мнемоники ALU по байту (таблица)
  dec0f              4417  группа 0F (movzx/test/imul)
  decalu             48C0  семейство ALU 00..3D
  decmod             4DE1  test/mov/lea 84..8D

декодер, часть 2 (bridge_self_d2.wall — E9.2-3a):
  decimm             51C8  push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC
  decshift           5968  сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)
  decgrp             5D31  imm-группа 80/81/83 (reg с REX.R)
  decgrp2            62AA  хвостовые C6/C7/F6/F7/FF (call косвенный)
  decbr              6A55  переходы E8/E9/EB/jcc rel8 (классы 2/3/4)
  decode_ins         6E9E  диспетчер: REX, 0F, множества байтов; da*/om*

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a):
  walk_code          7AF9  стек целей (куча), проход, тени/нули/терминалы
  sweep_ins          8076  выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target        82F1  target (вилка raw-0x1FF) и bss

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b):
  fill_offs          852B  смещения NUL-имён блоба -> массив offs
  init_tables        8673  таблицы мнемоник/условий/регистров + шапка
  tpl_dec            87ED  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             89E8  байт в буфер вывода
  app_name           8A53  имя из блоба по таблице смещений
  app_reg            8B11  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           8C76  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            8F21  знаковый hex (imm/цель/счётчик)
  out_hxu64          8F8B  hex u64 (отрицательное = битовый образ)
  out_hex2           9035  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          9180  минимум 4 hex-цифры (@смещения)
  out_sdec           94ED  знаковый dec со знаком +/-
  note_op            9598  примечание одного операнда (== _note)
  emit_note          991D  примечание H-строки (jcc/имена/[rip±d])
  emit_h             9BD4  H-строка выжившей инструкции
  emit_data          9DC8  данные сегмента DZ/DB (== оракул)
  app_tpl            A293  кусок шаблона шапки из tplb

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          A320  записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            A7C3  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           AC68  базы импортов: iatoff/intoff/nameoff/idtoff
  imp_labels         ADC6  метки iat_/d* (представимость!) + knownoff; impbad
  build_sstate       B533  карта выживших: 1 старт / 2 внутри
  sem_add            B71D  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            B9C6  твонки IAT/INT: валидность значений + меток hint
  dd_idt             BDFA  дескриптор IDT — кандидат DD
  sem_filter         BE9C  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         C8ED  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)
  out_hexl           CC82  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       CF2D  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           D124  строка разреза «:имя ; @смещ4»
  emit_dollar        D1D4  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D2E9  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         D652  сборка карт: кучи + sstate + импорты + семантика + метки операндов

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):
  out_hexl           CC82  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       CF2D  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           D124  строка разреза «:имя ; @смещ4»
  emit_dollar        D1D4  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D2E9  строка DD (5 значений) / DQ ($имя | 0)
  emit_body          DA5F  ДРАЙВЕР (КАНОН): шапка + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)

примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):
  m_put              E194  байт в буфер кодировки mbuf
  m_put4             E1FF  dword LittleEndian в mbuf (imm32/disp32)
  m_rex              E2FA  REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)
  m_enc_mem          E461  modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem
  m_cmp              E915  СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template
  m_kw               ECF9  слово размера byte/word/dword/qword + пробел
  m_dollar           EE66  «$имя» ($base/-4096 | labmap; «:1» при rel8)
  m_opmem            EF86  рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)
  m_opr              F357  ренер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)

кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):
  m_bsimple          F5E6  cdqe/cqo/ret/int3 (SIMPLE)
  m_bjmp             F739  jmp ($base/метка; EB слот 1 / E9 слот 4)
  m_bjcc             F8D3  jcc (70|cc слот 1 / 0F 80|cc слот 4)
  m_bcall            FAAB  call (E8 $метка | FF 15 [rip+$имя])
  m_bmovzx           FCFC  movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)
  m_bstack           1022F  push/pop r64 (5x + REX.B)
  m_btest            103F0  test r,r (84/85)
  m_blea             106CB  lea r32/r64, mem (8D, без kw)
  m_bimul            10914  imul r64,r64 (REX.WRB 0F AF /r)
  m_bshift           10BCB  rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)
  m_bf7              111A4  neg/idiv (F7 /3 /7)
  m_bff              11396  inc/dec (FF /0 /1)

кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):
  m_alu_base         11588  базовый опкод ALU по dname (00/08/20/28/30/38)
  m_alu_ext          11694  /ext ALU по dname (0/1/4/5/6/7)
  m_alu_imm          117A0  форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)
  m_balu             11937  add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)
  m_bmov             12705  mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)

драйвер ветви M (bridge_self_m4.wall — E9.2-3c):
  m_body             13918  диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)
  m_line             140DF  ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)

вход (bridge.wall):
  main ................. 1429D  CLI -> чтение EXE -> проверки -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H) -> факты M=/H=
```

## 3. Данные образа (RVA)

```
строки (46): s_use 14696 s_long 146CC s_oexe 146E7 s_rexe 14701
  s_family 1471B s_big 14733 s_oout 1474C s_wout 14766 s_f1 14781
  s_f2 14794 s_f3 1479B s_f4 147A2 s_f5 147A7 s_f6 147AC
  s_f7 147B1 s_f8 147B9 s_f9 147BE s_fa 147C1 s_crlf 147C4
  s_pref 147C6 s_needle 147D3 s_dll 147E4 s_h 147F0 s_at 147F2
  s_ml 147F6 s_ripl 147F8 s_base 147FE s_s1 14802 s_kw 14804
  s_dz 1481E s_db 14821 s_iat 14824 s_dd 14828 s_dq 1482B
  s_mem 1482E s_rip 14833 s_cl 14837 s_j 14839 s_comma 1483A
  s_mn 1483C s_cc 148B5 s_r64 148DD s_r8 1491B s_r16 1495D
  s_r32 1499B s_tpl 149E1
глобали (86): hstdout 14B6F cmdline 14B77 written 14B7F wlen 14B87
  exebuf 14B8F exelen 14B97 entryrva 14B9F vsize 14BA7 rawsize 14BAF rawptr 14BB7
  modlen 14BBF thunk 14BC7 dllfile 14BCF impn 14BD7 insmap 14BDF lenmap 14BE7
  pend 14BEF rawlim 14BF7 psp 14BFF inscount 14C07 maxend 14C0F swcur 14C17
  target 14C1F bss 14C27 dlen 14C2F dcls 14C37 dtgt 14C3F dpos 14C47
  mpos 14C4F mreg 14C57 dname 14C5F dcc 14C67 dargc 14C6F da1k 14C77
  da2k 14C7F da1r 14C87 da2r 14C8F da1s 14C97 da2s 14C9F da1v 14CA7
  da2v 14CAF damem 14CB7 ombase 14CBF omidx 14CC7 omscale 14CCF omdisp 14CD7
  omsize 14CDF omrip 14CE7 mkind 14CEF mrreg 14CF7 mrdip 14CFF mripon 14D07
  sdump 14D0F outmem 14D17 outbuf 14D1F outcur 14D27 iatoff 14D2F intoff 14D37
  nameoff 14D3F idtoff 14D47 impbad 14D4F kn 14D57 snlen 14D5F semcnt 14D67
  semacc 14D6F hhrv 14D77 hno 14D7F hnl 14D87 snam 14D8F noffs 14D97
  knownoff 14D9F semrows 14DA7 labmap 14DAF sstate 14DB7 semstate 14DBF mblen 14DC7
  mslot 14DCF mslotz 14DD7 mslof 14DDF mopc 14DE7 mis8 14DEF mcount 14DF7
  hcount 14DFF
  arg1 14E07 (0x80) arg2 14E87 (0x80) arg3 14F07 (0x80)
  factbuf 14F87 (0xC0) o_mn 15047 (0xE8) o_cc 1512F (0x88)
  o_r64 151B7 (0x88) o_r8 1523F (0x88) o_r16 152C7 (0x88)
  o_r32 1534F (0x88) o_kw 153D7 (0x28) tplb 153FF (0xC8)
  mbuf 154C7 (0xC0) w1 15587 (0x200)
конец тела: 15787 (vsize 0x15787)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x15601..0x15787, 0x186 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=18701; как kernel/uva — T-E9-20).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — E945ED20…F8619F, bridge.brick — A9EFC735…C0CD23, bridge.exe — B3598A11…29BC167 (полные — VERIFY.md).
