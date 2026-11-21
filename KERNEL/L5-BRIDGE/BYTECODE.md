# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 91648 байтов (0x16600) |
| SHA-256 | 2C75C6F9ED811153347C19E368C64AC75E46023F17C6302B8ABAA4E75E2BCA2B |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 13 частей bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 130128 Б (50% предела входа 256 КиБ; 4499 строк — заголовок bridge.b2) |
| Тело секции | 90724 байта (0x16264), RVA 0x1000, SRD 0x16400 |
| VirtualSize | 0x16264 (одна секция); target 0x16201, bss 0x63 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 19237 (bridge.b2; 100% M — H=0, круг T-E9-20: M=19237 H=0) |
| Меток в исходнике | 1228 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 116 (карта — §2) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 639815683 + 65493114 + 66363226 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)

Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* — MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md, MAP/M5-BRIDGE-E.md, MAP/M5-BRIDGE-L.md, MAP/M5-BRIDGE-M.md и MAP/M5-BRIDGE-G.md).

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

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b; с E9.2-4 — и вызов ptpl_dec ветви G):
  fill_offs          852B  смещения NUL-имён блоба -> массив offs
  init_tables        8673  таблицы мнемоник/условий/регистров + шапки b2/PEG
  tpl_dec            87F2  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             89ED  байт в буфер вывода
  app_name           8A58  имя из блоба по таблице смещений
  app_reg            8B16  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           8C7B  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            8F26  знаковый hex (imm/цель/счётчик)
  out_hxu64          8F90  hex u64 (отрицательное = битовый образ)
  out_hex2           903A  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          9185  минимум 4 hex-цифры (@смещения)
  out_sdec           94F2  знаковый dec со знаком +/-
  note_op            959D  примечание одного операнда (== _note)
  emit_note          9922  примечание H-строки (jcc/имена/[rip±d])
  emit_h             9BD9  H-строка выжившей инструкции
  emit_data          9DCD  данные сегмента DZ/DB (== оракул)
  app_tpl            A298  кусок шаблона шапки из tplb

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          A325  записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            A7C8  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           AC6D  базы импортов: iatoff/intoff/nameoff/idtoff
  imp_labels         ADCB  метки iat_/d* (представимость!) + knownoff; impbad
  build_sstate       B538  карта выживших: 1 старт / 2 внутри
  sem_add            B722  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            B9CB  твонки IAT/INT: валидность значений + меток hint
  dd_idt             BDFF  дескриптор IDT — кандидат DD
  sem_filter         BEA1  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         C8F2  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):
  out_hexl           CC87  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       CF32  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           D129  строка разреза «:имя ; @смещ4»
  emit_dollar        D1D9  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D2EE  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         D657  сборка карт: кучи + sstate + импорты + семантика + метки операндов
  emit_body          DA64  ДРАЙВЕР (КАНОН): шапка + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)

примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):
  m_put              E199  байт в буфер кодировки mbuf
  m_put4             E204  dword LittleEndian в mbuf (imm32/disp32)
  m_rex              E2FF  REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)
  m_enc_mem          E466  modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem
  m_cmp              E91A  СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template
  m_kw               ECFE  слово размера byte/word/dword/qword + пробел
  m_dollar           EE6B  «$имя» ($base/-4096 | labmap; «:1» при rel8)
  m_opmem            EF8B  рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)
  m_opr              F35C  ренер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)

кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):
  m_bsimple          F5EB  cdqe/cqo/ret/int3 (SIMPLE)
  m_bjmp             F73E  jmp ($base/метка; EB слот 1 / E9 слот 4)
  m_bjcc             F8D8  jcc (70|cc слот 1 / 0F 80|cc слот 4)
  m_bcall            FAB0  call (E8 $метка | FF 15 [rip+$имя])
  m_bmovzx           FD01  movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)
  m_bstack           10234  push/pop r64 (5x + REX.B)
  m_btest            103F5  test r,r (84/85)
  m_blea             106D0  lea r32/r64, mem (8D, без kw)
  m_bimul            10919  imul r64,r64 (REX.WRB 0F AF /r)
  m_bshift           10BD0  rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)
  m_bf7              111A9  neg/idiv (F7 /3 /7)
  m_bff              1139B  inc/dec (FF /0 /1)

кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):
  m_alu_base         1158D  базовый опкод ALU по dname (00/08/20/28/30/38)
  m_alu_ext          11699  /ext ALU по dname (0/1/4/5/6/7)
  m_alu_imm          117A5  форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)
  m_balu             1193C  add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)
  m_bmov             1270A  mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)

драйвер ветви M (bridge_self_m4.wall — E9.2-3c):
  m_body             1391D  диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)
  m_line             140E4  ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)

PEG-выход (bridge_self_g.wall — срез E9.2-4):
  ptpl_dec           142A2  HEX-литерал s_ptpl (72 Б) -> массив ptplb (шапка PEG)
  emit_peg           1449D  ДРАЙВЕР PEG: шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom (SPEC/15 п. 8 == _peg_text); запись .peg (коды 8/9)

вход (bridge.wall):
  main ................. 14C48  CLI -> чтение EXE -> проверки -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H)
                               -> PEG-выход (E9.2-4) -> факты M=/H=
```

## 3. Данные образа (RVA)

```
строки (55): s_use 1505D s_long 15093 s_oexe 150AE s_rexe 150C8
  s_family 150E2 s_big 150FA s_oout 15113 s_wout 1512D s_f1 15148
  s_f2 1515B s_f3 15162 s_f4 15169 s_f5 1516E s_f6 15173
  s_f7 15178 s_f8 15180 s_f9 15185 s_fa 15188 s_crlf 1518B
  s_pref 1518D s_needle 1519A s_dll 151AB s_h 151B7 s_at 151B9
  s_ml 151BD s_ripl 151BF s_base 151C5 s_s1 151C9 s_kw 151CB
  s_dz 151E5 s_db 151E8 s_iat 151EB s_dd 151EF s_dq 151F2
  s_mem 151F5 s_rip 151FA s_cl 151FE s_j 15200 s_comma 15201
  s_mn 15203 s_cc 1527C s_r64 152A4 s_r8 152E2 s_r16 15324
  s_r32 15362 s_tpl 153A8 s_ptpl 15536 s_dotexe 155C6 s_pm 155CB
  s_pe 155D3 s_pi 155DB s_pa 155E3 s_pb 155E9 s_ps 155EF
  s_ph 155FA
глобали (86): hstdout 15604 cmdline 1560C written 15614 wlen 1561C
  exebuf 15624 exelen 1562C entryrva 15634 vsize 1563C rawsize 15644 rawptr 1564C
  modlen 15654 thunk 1565C dllfile 15664 impn 1566C insmap 15674 lenmap 1567C
  pend 15684 rawlim 1568C psp 15694 inscount 1569C maxend 156A4 swcur 156AC
  target 156B4 bss 156BC dlen 156C4 dcls 156CC dtgt 156D4 dpos 156DC
  mpos 156E4 mreg 156EC dname 156F4 dcc 156FC dargc 15704 da1k 1570C
  da2k 15714 da1r 1571C da2r 15724 da1s 1572C da2s 15734
  da1v 1573C da2v 15744 damem 1574C ombase 15754 omidx 1575C omscale 15764 omdisp 1576C
  omsize 15774 omrip 1577C mkind 15784 mrreg 1578C mrdip 15794 mripon 1579C
  sdump 157A4 outmem 157AC outbuf 157B4 outcur 157BC iatoff 157C4 intoff 157CC
  nameoff 157D4 idtoff 157DC impbad 157E4 kn 157EC snlen 157F4 semcnt 157FC
  semacc 15804 hhrv 1580C hno 15814 hnl 1581C snam 15824 noffs 1582C
  knownoff 15834 semrows 1583C labmap 15844 sstate 1584C semstate 15854 mblen 1585C
  mslot 15864 mslotz 1586C mslof 15874 mopc 1587C mis8 15884 mcount 1588C
  hcount 15894
  arg1 1589C (0x80) arg2 1591C (0x80) arg3 1599C (0x80)
  factbuf 15A1C (0xC0) o_mn 15ADC (0xE8) o_cc 15BC4 (0x88)
  o_r64 15C4C (0x88) o_r8 15CD4 (0x88) o_r16 15D5C (0x88)
  o_r32 15DE4 (0x88) o_kw 15E6C (0x28) tplb 15E94 (0xC8)
  mbuf 15F5C (0xC0) ptplb 1601C (0x48) w1 16064 (0x200)
конец тела: 16264 (vsize 0x16264)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x16201..0x16264, 0x63 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=19237; как kernel/uva — T-E9-20). E9.2-4: массив ptplb[9] (0x48 Б) добавлен ПЕРЕД w1 — инвариант сохранён (проверен кругом T-E9-20).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 113F4632…32487DA, bridge.brick — FF04F5F7…B6C4895, bridge.exe — 2C75C6F9…E2BCA2B (полные — VERIFY.md).
