# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 98816 байт (0x18200) |
| SHA-256 | 4D23B561D68A26D9C8C70ADAF6FDCC541186EDC324356ED36D65F1CE5821C13C |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a + E9.4-4b-1): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 16 частей bridge_self_*.wall (WALL v2, разрез SPEC/10; +pi/pf — E9.4-4b-1); склейка 152669 Б (57% предела входа 256 КиБ; 4958 строк — заголовок bridge.b2) |
| Тело секции | 97858 байт (0x17E42), RVA 0x1000, SRD 0x18000 |
| VirtualSize | 0x17E42 (одна секция); target 0x17E01, bss 0x41 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 20894 (bridge.b2; 100% M — H=0, круг T-E9-20: M=20894 H=0) |
| Меток в исходнике | 1309 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 122 (карта — §2; +fam_chain/foreign_front/print_ffacts — E9.4-4b-1) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 717365516 + 71093226 + 75589252 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — возобновляемые срезы build_bridge_resume.py, прецедент T-E6-49a) |

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

общий фронт PE и семейные проверки-предикат (bridge_self_pe.wall — часть 1, E9.2-1 + E9.4-4b-1):
  rd16               11AB  LE u16 по байтовому смещению
  rd32               122C  LE u32 по байтовому смещению
  fail_family        134F  ERR=FAMILY + выход 6 (ОБЩИЙ отказ: не семья И не чужой)
  guard              1398  границы чтения [off, off+n) из exebuf: 0/1 (предикат)
  check_head         1425  ОБЩИЙ фронт: MZ + PE-сигнатура + раскладка полей ОТ e_lfanew (lfanew/coffoff/optoff/sizopt/numsect/tbloff)
  check_opt          17BC  Machine/NSections/OptHdr/Chars/Magic/Subsys — предикат
  check_base         1A57  ImageBase (2 dword)/SectAlign/FileAlign — предикат
  check_sect         1C52  имя .text/vaddr/chars; vsize/raw/rawptr + codevaddr/falign/fend
  check_size         214C  SizeOfImage/Headers/Raw/файл; вход в секции — предикат
  check_body         247B  тело не пустое и не из одних нулей — предикат
  stub_name          25A3  имя модуля из DOS-заглушки (префикс/игла) — предикат

импорты семейства, цепочка, факт-строка (bridge_self_pi.wall — часть 2, разрез pe по лимиту 500):
  rva_off            2A2F  RVA тела (0x1000+) -> файловое смещение
  walk_descs         2A71  дескрипторы IDT по DD[1] @optoff+0x78 (1 шт + терминатор), thunk
  cstr_len           2F41  длина C-строки (quirk: без NUL -> len-1)
  check_dll          3020  имя DLL == kernel32.dll (без регистра)
  walk_funcs         31A7  счёт записей INT/IAT (терминатор/чётность)
  fam_chain          3422  СЕМЕЙНАЯ ЦЕПОЧКА-ПРЕДИКАТ: 0 = семейство, 1 = нет (развилка в main — E9.4-4b-1)
  print_facts        35FB  факт-строка MODULE/ENTRY/.../BSS в stdout

ЧУЖОЙ ПУТЬ развилки (bridge_self_pf.wall — часть 3, E9.4-4b-1):
  foreign_front      3BB5  порт parse_foreign: Machine/Magic, FileAlignment степень 2, секция кода ПО ВХОДУ, EXECUTE, файл покрывает raw, тело не нулевое, вход в raw-части; глобали спуска
  print_ffacts       4265  ЧУЖАЯ факт-строка FOREIGN=1 SECT=… (== parse_foreign; эмиссия — срезы E9.4-4b-2+)

декодер x86-подмножества SPEC/05, часть 1 (bridge_self_d.wall — E9.2-2/3a; границы — fend, E9.4-4b-1):
  fb                 468A  байт ТЕЛА с границей fend (отказ — данные)
  rel8               471B  знаковый байт
  rel32              4792  знаковый dword (2^32 — произведением)
  u32                491B  БЕЗзнаковый dword (imm32/disp32 SIB)
  u64                4A46  БЕЗзнаковый qword (imm64; 2^32 множителем)
  modrm_read         4AD1  полный разбор modrm+SIB+disp -> om*
  set_reg            5358  операнд-регистр в слот 1/2
  set_rm             53F1  операнд из modrm (рег mod=3 | память)
  set_imm            5512  непосредственный в слот (знаковая печать)
  set_immu           55AB  imm64 в слот (БЕЗзнаковая печать, вид 7)
  set_tgt            5644  операнд-цель перехода в слот 1
  set_cl             5686  операнд «cl» в слот 2
  set_cnt            56B9  счётчик сдвига (целое) в слот 2
  alu_id             56FB  id мнемоники ALU по байту (таблица)
  dec0f              57FC  группа 0F (movzx/test/imul)
  decalu             5CA5  семейство ALU 00..3D
  decmod             61C6  test/mov/lea 84..8D

декодер, часть 2 (bridge_self_d2.wall — E9.2-3a; FF — делегация в decff):
  decimm             65AD  push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC
  decshift           6D4D  сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)
  decgrp             7116  imm-группа 80/81/83 (reg с REX.R)
  decgrp2            768F  хвостовые C6/C7/F6/F7 (FF -> decff — E9.4-4a)
  decbr              7D0E  переходы E8/E9/EB/jcc rel8 (классы 2/3/4)
  decode_ins         8157  диспетчер: REX, 0F, множества байтов; da*/om*

декодер, часть 3 — группа FF (bridge_self_d3.wall — срез E9.4-4a):
  decff              8DB2  FF: peek ext с REX.R ДО modrm_read; /0 inc /1 dec /2 call /4 jmp r/m64 (КОСВЕННЫЙ — размер /4 ВСЕГДА 64, класс 5 — терминал спуска)

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a + E9.4-4a + 4-4b-1):
  push_tgt           90E4  цель в стек — ДЕДУПЛИКАЦИЯ по значению (карта pushmap; вне [0, rawlim) не кладётся; предел pend 1+rawlim)
  jtab               91F7  таблицы переходов: jmp qword [rip+X] — qword-строки «до первого non-code qword» -> кандидаты (== _jtab; чтение — тело+вирт. нули)
  walk_code          94B9  стек целей (куча), проход, тени/нули/терминалы (dcls 5 — терминал + jtab; цели — push_tgt); старт — entryrva-codevaddr
  sweep_ins          9AE4  выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target        9D5F  target (вилка falign образа — E9.4-4b-1; семья 0x200) и bss

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b; с E9.2-4 — и вызов ptpl_dec ветви G):
  fill_offs          9FC3  смещения NUL-имён блоба -> массив offs
  init_tables        A10B  таблицы мнемоник/условий/регистров + шапки b2/PEG
  tpl_dec            A28A  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             A485  байт в буфер вывода
  app_name           A4F0  имя из блоба по таблице смещений
  app_reg            A5AE  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           A713  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            A9BE  знаковый hex (imm/цель/счётчик)
  out_hxu64          AA28  hex u64 (отрицательное = битовый образ)
  out_hex2           AAD2  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          AC1D  минимум 4 hex-цифры (@смещения)
  out_sdec           AF8A  знаковый dec со знаком +/-
  note_op            B035  примечание одного операнда (== _note)
  emit_note          B3BA  примечание H-строки (jcc/имена/[rip±d])
  emit_h             B671  H-строка выжившей инструкции
  emit_data          B865  данные сегмента DZ/DB (== оракул)
  app_tpl            BD30  кусок шаблона шапки из tplb

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          BDBD  записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            C260  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           C705  базы импортов: iatoff/intoff/nameoff/idtoff (DD[1] @optoff+0x78 — E9.4-4b-1)
  imp_labels         C88D  метки iat_/d* (представимость!) + knownoff; impbad
  build_sstate       CFFA  карта выживших: 1 старт / 2 внутри
  sem_add            D1E4  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            D48D  твонки IAT/INT: валидность значений + меток hint
  dd_idt             D8C1  дескриптор IDT — кандидат DD
  sem_filter         D963  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         E3B4  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):
  out_hexl           E749  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       E9F4  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           EBEB  строка разреза «:имя ; @смещ4»
  emit_dollar        EC9B  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           EDB0  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         F119  сборка карт: кучи + sstate + импорты + семантика + метки операндов
  emit_body          F526  ДРАЙВЕР (КАНОН): шапка + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)

примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):
  m_put              FC5B  байт в буфер кодировки mbuf
  m_put4             FCC6  dword LittleEndian в mbuf (imm32/disp32)
  m_rex              FDC1  REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)
  m_enc_mem          FF28  modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem
  m_cmp              103DC  СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template
  m_kw               107C0  слово размера byte/word/dword/qword + пробел
  m_dollar           1092D  «$имя» ($base/-4096 | labmap; «:1» при rel8)
  m_opmem            10A4D  рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)
  m_opr              10E1E  рендер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)

кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):
  m_bsimple          110AD  cdqe/cqo/ret/int3 (SIMPLE)
  m_bjmp             11200  jmp ($base/метка; EB слот 1 / E9 слот 4)
  m_bjcc             113CB  jcc (70|cc слот 1 / 0F 80|cc слот 4)
  m_bcall            115A3  call (E8 $метка | FF 15 [rip+$имя])
  m_bmovzx           117F4  movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)
  m_bstack           11D27  push/pop r64 (5x + REX.B)
  m_btest            11EE8  test r,r (84/85)
  m_blea             121C3  lea r32/r64, mem (8D, без kw)
  m_bimul            1240C  imul r64,r64 (REX.WRB 0F AF /r)
  m_bshift           126C3  rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)
  m_bf7              12C9C  neg/idiv (F7 /3 /7)
  m_bff              12E8E  inc/dec (FF /0 /1)

кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):
  m_alu_base         13080  базовый опкод ALU по dname (00/08/20/28/30/38)
  m_alu_ext          1318C  /ext ALU по dname (0/1/4/5/6/7)
  m_alu_imm          13298  форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)
  m_balu             1342F  add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)
  m_bmov             141FD  mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)

драйвер ветви M (bridge_self_m4.wall — E9.2-3c):
  m_body             15410  диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)
  m_line             15BD7  ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)

PEG-выход (bridge_self_g.wall — срез E9.2-4; idata/iat — вычисляемые смещения E9.4-4b-1):
  ptpl_dec           15D95  HEX-литерал s_ptpl (72 Б) -> массив ptplb (шапка PEG)
  emit_peg           15F90  ДРАЙВЕР PEG: шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom (SPEC/15 п. 8 == _peg_text; DD[1]/DD[12] по optoff); запись .peg (коды 8/9)

вход (bridge.wall):
  main ................. 1678F  CLI -> чтение EXE -> общий фронт -> РАЗВИЛКА
                               «семья | чужой» (E9.4-4b-1): семья -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H)
                               -> PEG-выход (E9.2-4) -> факты M=/H=; чужой ->
                               фронт P2 -> спуск -> чужие факты FOREIGN
```

## 3. Данные образа (RVA)

```
строки (56):
  s_use 16BC8 s_long 16BFE s_oexe 16C19 s_rexe 16C33
  s_family 16C4D s_big 16C65 s_oout 16C7E s_wout 16C98
  s_f1 16CB3 s_f2 16CC6 s_f3 16CCD s_f4 16CD4
  s_f5 16CD9 s_f6 16CDE s_f7 16CE3 s_f8 16CEB
  s_f9 16CF0 s_fa 16CF3 s_ff1 16CF6 s_crlf 16D11
  s_pref 16D13 s_needle 16D20 s_dll 16D31 s_h 16D3D
  s_at 16D3F s_ml 16D43 s_ripl 16D45 s_base 16D4B
  s_s1 16D4F s_kw 16D51 s_dz 16D6B s_db 16D6E
  s_iat 16D71 s_dd 16D75 s_dq 16D78 s_mem 16D7B
  s_rip 16D80 s_cl 16D84 s_j 16D86 s_comma 16D87
  s_mn 16D89 s_cc 16E02 s_r64 16E2A s_r8 16E68
  s_r16 16EAA s_r32 16EE8 s_tpl 16F2E s_ptpl 170BC
  s_dotexe 1714C s_pm 17151 s_pe 17159 s_pi 17161
  s_pa 17169 s_pb 1716F s_ps 17175 s_ph 17180
глобали (94):
  hstdout 1718A cmdline 17192 written 1719A wlen 171A2
  exebuf 171AA exelen 171B2 entryrva 171BA vsize 171C2
  rawsize 171CA rawptr 171D2 modlen 171DA thunk 171E2
  dllfile 171EA impn 171F2 insmap 171FA lenmap 17202
  pend 1720A pushmap 17212 rawlim 1721A psp 17222
  inscount 1722A maxend 17232 swcur 1723A target 17242
  bss 1724A dlen 17252 dcls 1725A dtgt 17262
  dpos 1726A mpos 17272 mreg 1727A dname 17282
  dcc 1728A dargc 17292 da1k 1729A da2k 172A2
  da1r 172AA da2r 172B2 da1s 172BA da2s 172C2
  da1v 172CA da2v 172D2 damem 172DA ombase 172E2
  omidx 172EA omscale 172F2 omdisp 172FA omsize 17302
  omrip 1730A mkind 17312 mrreg 1731A mrdip 17322
  mripon 1732A sdump 17332 outmem 1733A outbuf 17342
  outcur 1734A iatoff 17352 intoff 1735A nameoff 17362
  idtoff 1736A impbad 17372 kn 1737A snlen 17382
  semcnt 1738A semacc 17392 hhrv 1739A hno 173A2
  hnl 173AA snam 173B2 noffs 173BA knownoff 173C2
  semrows 173CA labmap 173D2 sstate 173DA semstate 173E2
  mblen 173EA mslot 173F2 mslotz 173FA mslof 17402
  mopc 1740A mis8 17412 mcount 1741A hcount 17422
  lfanew 1742A coffoff 17432 optoff 1743A sizopt 17442
  numsect 1744A tbloff 17452 codevaddr 1745A falign 17462
  fend 1746A fsect 17472
  arg1 1747A (0x80) arg2 174FA (0x80) arg3 1757A (0x80)
  factbuf 175FA (0xC0) o_mn 176BA (0xE8) o_cc 177A2 (0x88)
  o_r64 1782A (0x88) o_r8 178B2 (0x88) o_r16 1793A (0x88)
  o_r32 179C2 (0x88) o_kw 17A4A (0x28) tplb 17A72 (0xC8)
  mbuf 17B3A (0xC0) ptplb 17BFA (0x48) w1 17C42 (0x200)
конец тела: 17E42 (vsize 0x17E42)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x17E01..0x17E42, 0x41 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=20894; как kernel/uva — T-E9-20). E9.2-4: массив ptplb[9] (0x48 Б) добавлен ПЕРЕД w1 — инвариант сохранён (проверен кругом T-E9-20). E9.4-4b-1: скаляры развилки lfanew/coffoff/optoff/sizopt/numsect/tbloff/codevaddr/falign/fend/fsect (+80 Б, кластер ветвей P/P2 после mcount/hcount) — инвариант хвоста внутри w1 не задет (хвост 0x41 Б; круг T-E9-20 зелёный, M=20894 H=0).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — A86F5669…D1387D9, bridge.brick — 9D2E51BD…36486398, bridge.exe — 4D23B561…82113C (полные — VERIFY.md).
