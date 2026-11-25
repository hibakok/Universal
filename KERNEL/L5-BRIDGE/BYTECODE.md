# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 107008 байт (0x1A200) |
| SHA-256 | DDD6BFB8EBB97BAFF89FEAEBF629BF63D376382047A9EC2DE5C0B92828543666 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a + E9.4-4b-1 + E9.4-4b-2 + E9.4-4b-3): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 16 частей bridge_self_*.wall (WALL v2, разрез SPEC/10; +pi/pf — E9.4-4b-1); склейка 175173 Б (66% предела входа 256 КиБ; 5482 строк — заголовок bridge.b2) |
| Тело секции | 106007 байт (0x19E67), RVA 0x1000, SRD 0x1A000 |
| VirtualSize | 0x19E17 (одна секция); target 0x19E01, bss 0x16 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 22516 (bridge.b2; 100% M — H=0, круг T-E9-20: M=22516 H=0) |
| Меток в исходнике | 1410 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 131 (карта — §2; +gtpl_dec/peg2_check/fold_emit/emit_peg2 — E9.4-4b-3) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 816003916 + 76993247 + 85609127 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — возобновляемые срезы build_bridge_resume.py, прецедент T-E6-49a) |

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
  walk_descs         2C78  дескрипторы IDT по DD[1] @optoff+0x78 (1 шт + терминатор), thunk
  cstr_len           3148  длина C-строки (quirk: без NUL -> len-1)
  check_dll          3227  имя DLL == kernel32.dll (без регистра)
  walk_funcs         33AE  счёт записей INT/IAT (терминатор/чётность)
  rva_file           2A71  RVA -> файловое смещение ПО ВСЕМ СЕКЦИЯМ (порт _sec/_read_rva оракула; для семьи == rva_off — E9.4-4b-2)
  fam_chain          3629  СЕМЕЙНАЯ ЦЕПОЧКА-ПРЕДИКАТ: 0 = семейство, 1 = нет (развилка в main — E9.4-4b-1)
  print_facts        3802  факт-строка MODULE/ENTRY/.../BSS в stdout

ЧУЖОЙ ПУТЬ развилки (bridge_self_pf.wall — часть 3, E9.4-4b-1/2):
  foreign_front      3DBC  порт parse_foreign: Machine/Magic, FileAlignment степень 2, секция кода ПО ВХОДУ, EXECUTE, файл покрывает raw, тело не нулевое, вход в raw-части; глобали спуска
  fimp_walk          4987  чужие импорты: обход IDT DD[1] по rva_file -> dllcnt; дескриптор 1 -> thunk/impn (без семейных проверок — E9.4-4b-2)
  count_sects        4E46  число читаемых слотов таблицы секций -> sectcnt (шапка чужого b2 «секций N»)
  print_ffacts       446C  ЧУЖАЯ факт-строка FOREIGN=1 SECT=… + M=/H= (== parse_foreign + статистика эмиссии; E9.4-4b-2)

декодер x86-подмножества SPEC/05, часть 1 (bridge_self_d.wall — E9.2-2/3a; границы — fend, E9.4-4b-1):
  fb                 4F3E  байт ТЕЛА с границей fend (отказ — данные)
  rel8               4FCF  знаковый байт
  rel32              5046  знаковый dword (2^32 — произведением)
  u32                51CF  БЕЗзнаковый dword (imm32/disp32 SIB)
  u64                52FA  БЕЗзнаковый qword (imm64; 2^32 множителем)
  modrm_read         5385  полный разбор modrm+SIB+disp -> om*
  set_reg            5C0C  операнд-регистр в слот 1/2
  set_rm             5CA5  операнд из modrm (рег mod=3 | память)
  set_imm            5DC6  непосредственный в слот (знаковая печать)
  set_immu           5E5F  imm64 в слот (БЕЗзнаковая печать, вид 7)
  set_tgt            5EF8  операнд-цель перехода в слот 1
  set_cl             5F3A  операнд «cl» в слот 2
  set_cnt            5F6D  счётчик сдвига (целое) в слот 2
  alu_id             5FAF  id мнемоники ALU по байту (таблица)
  dec0f              60B0  группа 0F (movzx/test/imul)
  decalu             6559  семейство ALU 00..3D
  decmod             6A7A  test/mov/lea 84..8D

декодер, часть 2 (bridge_self_d2.wall — E9.2-3a; FF — делегация в decff):
  decimm             6E61  push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC
  decshift           7601  сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)
  decgrp             79CA  imm-группа 80/81/83 (reg с REX.R)
  decgrp2            7F43  хвостовые C6/C7/F6/F7 (FF -> decff — E9.4-4a)
  decbr              85C2  переходы E8/E9/EB/jcc rel8 (классы 2/3/4)
  decode_ins         8A0B  диспетчер: REX, 0F, множества байтов; da*/om*

декодер, часть 3 — группа FF (bridge_self_d3.wall — срез E9.4-4a):
  decff              9666  FF: peek ext с REX.R ДО modrm_read; /0 inc /1 dec /2 call /4 jmp r/m64 (КОСВЕННЫЙ — размер /4 ВСЕГДА 64, класс 5 — терминал спуска)

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a + E9.4-4a + 4-4b-1):
  push_tgt           9998  цель в стек — ДЕДУПЛИКАЦИЯ по значению (карта pushmap; вне [0, rawlim) не кладётся; предел pend 1+rawlim)
  jtab               9AAB  таблицы переходов: jmp qword [rip+X] — qword-строки «до первого non-code qword» -> кандидаты (== _jtab; чтение — тело+вирт. нули)
  walk_code          9D6D  стек целей (куча), проход, тени/нули/терминалы (dcls 5 — терминал + jtab; цели — push_tgt); старт — entryrva-codevaddr
  sweep_ins          A398  выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target        A613  target (вилка falign образа — E9.4-4b-1; семья 0x200) и bss

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b; с E9.2-4 — и вызовы ptpl_dec/gtpl_dec ветви G):
  fill_offs          A877  смещения NUL-имён блоба -> массив offs
  init_tables        A9BF  таблицы мнемоник/условий/регистров + шапки b2/PEG/чужая/PEG v2 (ftpl_dec/gtpl_dec — E9.4-4b-2/3)
  tpl_dec            AB48  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             AF3E  байт в буфер вывода
  app_name           AFA9  имя из блоба по таблице смещений
  app_reg            B067  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           B1CC  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            B477  знаковый hex (imm/цель/счётчик)
  out_hxu64          B4E1  hex u64 (отрицательное = битовый образ)
  out_hex2           B58B  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          B6D6  минимум 4 hex-цифры (@смещения)
  out_sdec           BA43  знаковый dec со знаком +/-
  note_op            BAEE  примечание одного операнда (== _note)
  emit_note          BE73  примечание H-строки (jcc/имена/[rip±d])
  emit_h             C12A  H-строка выжившей инструкции
  emit_data          C31E  данные сегмента DZ/DB (== оракул)
  app_tpl            C7E9  кусок шаблона шапки из tplb
  ftpl_dec           AD43  HEX-литерал s_ftpl (194 Б) -> массив ftplb — ЧУЖАЯ шапка (E9.4-4b-2)
  app_ftpl           C876  кусок ЧУЖОЙ шапки из ftplb (куски 0/51/57/94/96/106/194)

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          C903  записи INT/IAT -> hhrv/hno/hnl (rva_file — E9.4-4b-2; бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            CD72  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           D217  базы импортов: iatoff/intoff/nameoff/idtoff (DD[1] @optoff+0x78 по rva_file; минус codevaddr — E9.4-4b-2; нет дескриптора -> -1)
  imp_labels         D44A  метки iat_/d* (представимость!) + knownoff; impbad (hint-смещения — RVA минус codevaddr)
  build_sstate       DBB7  карта выживших: 1 старт / 2 внутри
  sem_add            DDA1  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            E04A  твонки IAT/INT: валидность значений + меток hint (base = codevaddr — E9.4-4b-2)
  dd_idt             E47E  дескриптор IDT — кандидат DD
  sem_filter         E520  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         EF71  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):
  out_hexl           F306  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       F5B1  имя метки по labmap (d/l/iat_ из snam; RVA = off+codevaddr — E9.4-4b-2)
  emit_cut           F7A8  строка разреза «:имя ; @смещ4»
  emit_dollar        F858  dword -> «$имя» (knownoff + codevaddr) | ЗАГЛАВНЫЙ hex
  emit_sem           F96D  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         FCD6  сборка карт: кучи + sstate + импорты + семантика + метки операндов
  emit_body          100E3  ДРАЙВЕР (КАНОН; isf — E9.4-4b-2): шапка (семейная tplb/модуль | чужая ftplb/факты) + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)

примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):
  m_put              109E9  байт в буфер кодировки mbuf
  m_put4             10A54  dword LittleEndian в mbuf (imm32/disp32)
  m_rex              10B4F  REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)
  m_enc_mem          10CB6  modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem
  m_cmp              1116A  СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template
  m_kw               1154E  слово размера byte/word/dword/qword + пробел
  m_dollar           116BB  «$имя» ($base/-4096 | labmap; «:1» при rel8)
  m_opmem            117DB  рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)
  m_opr              11BAC  рендер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)

кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):
  m_bsimple          11E3B  cdqe/cqo/ret/int3 (SIMPLE)
  m_bjmp             11F8E  jmp ($base/метка; EB слот 1 / E9 слот 4)
  m_bjcc             12159  jcc (70|cc слот 1 / 0F 80|cc слот 4)
  m_bcall            12331  call (E8 $метка | FF 15 [rip+$имя])
  m_bmovzx           12582  movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)
  m_bstack           12AB5  push/pop r64 (5x + REX.B)
  m_btest            12C76  test r,r (84/85)
  m_blea             12F51  lea r32/r64, mem (8D, без kw)
  m_bimul            1319A  imul r64,r64 (REX.WRB 0F AF /r)
  m_bshift           13451  rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)
  m_bf7              13A2A  neg/idiv (F7 /3 /7)
  m_bff              13C1C  inc/dec (FF /0 /1)

кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):
  m_alu_base         13E0E  базовый опкод ALU по dname (00/08/20/28/30/38)
  m_alu_ext          13F1A  /ext ALU по dname (0/1/4/5/6/7)
  m_alu_imm          14026  форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)
  m_balu             141BD  add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)
  m_bmov             14F8B  mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)

драйвер ветви M (bridge_self_m4.wall — E9.2-3c):
  m_body             1619E  диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)
  m_line             16965  ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)

PEG-выход (bridge_self_g.wall — срез E9.2-4 семья; E9.4-4b-3 — ЧУЖОЙ ПУТЬ: PEG v2):
  ptpl_dec           16B23  HEX-литерал s_ptpl (72 Б) -> массив ptplb (шапка PEG)
  emit_peg           16D1E  ДРАЙВЕР PEG v1 (семья): шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom (SPEC/15 п. 8 == _peg_text; DD[1]/DD[12] по optoff); запись .peg (коды 8/9)
  gtpl_dec           1751D  HEX-литерал s_gtpl (103 Б) -> массив gtplb — ШАПКА PEG v2 (E9.4-4b-3)
  peg2_check         17718  проверки PEG v2: H = min raw_ptr + файл покрывает raw ВСЕХ секций (ДО спуска; отказ ERR=FAMILY без частичных выходов — E9.4-4b-3)
  fold_emit          1793D  сворачивание области [lo,hi) в патчи «!hdr»/«!sec» (== _fold/_chunks64: дырка >= 4 нулей обрывает, куски <= 64 Б — E9.4-4b-3)
  emit_peg2          17D5D  ДРАЙВЕР PEG v2 (чужой путь): шапка + !pev2 H + !hdr [0,H) + !body fsect + !sec прочих raw-секций (== _peg2_text); запись .peg (коды 8/9) — E9.4-4b-3

вход (bridge.wall):
  main ................. 18350  CLI -> чтение EXE -> общий фронт -> РАЗВИЛКА
                               «семья | чужой» (E9.4-4b-1): семья -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H)
                               -> PEG-выход (E9.2-4) -> факты M=/H=; чужой ->
                               фронт P2 -> импорты (fimp_walk/count_sects) ->
                               peg2_check (E9.4-4b-3) -> спуск -> карты (base =
                               codevaddr) -> эмиссия .b2 ЧУЖОГО ТЕЛА + PEG v2
                               (emit_peg2 — E9.4-4b-3) -> факты FOREIGN + M=/H=
```

## 3. Данные образа (RVA)

```
строки (63):
  s_use 187E2 s_long 18818 s_oexe 18833 s_rexe 1884D
  s_family 18867 s_big 1887F s_oout 18898 s_wout 188B2
  s_f1 188CD s_f2 188E0 s_f3 188E7 s_f4 188EE
  s_f5 188F3 s_f6 188F8 s_f7 188FD s_f8 18905
  s_f9 1890A s_fa 1890D s_ff1 18910 s_crlf 1892B
  s_pref 1892D s_needle 1893A s_dll 1894B s_h 18957
  s_at 18959 s_ml 1895D s_ripl 1895F s_base 18965
  s_s1 18969 s_kw 1896B s_dz 18985 s_db 18988
  s_iat 1898B s_dd 1898F s_dq 18992 s_mem 18995
  s_rip 1899A s_cl 1899E s_j 189A0 s_comma 189A1
  s_mn 189A3 s_cc 18A1C s_r64 18A44 s_r8 18A82
  s_r16 18AC4 s_r32 18B02 s_tpl 18B48 s_ptpl 18CD6
  s_ftpl 18D66 s_gtpl 18F28 s_dotexe 18EEA s_pm 18EEF
  s_pe 18EF7 s_pi 18EFF s_pa 18F07 s_pb 18F0D
  s_ps 18F13 s_ph 18F1E s_gdll 18FF6 s_gpev 18FFC
  s_ghdr 19004 s_gbody 1900A s_gsec 19011
глобали (97):
  hstdout 19017 cmdline 1901F written 19027 wlen 1902F
  exebuf 19037 exelen 1903F entryrva 19047 vsize 1904F
  rawsize 19057 rawptr 1905F modlen 19067 thunk 1906F
  dllfile 19077 impn 1907F insmap 19087 lenmap 1908F
  pend 19097 pushmap 1909F rawlim 190A7 psp 190AF
  inscount 190B7 maxend 190BF swcur 190C7 target 190CF
  bss 190D7 dlen 190DF dcls 190E7 dtgt 190EF
  dpos 190F7 mpos 190FF mreg 19107 dname 1910F
  dcc 19117 dargc 1911F da1k 19127 da2k 1912F
  da1r 19137 da2r 1913F da1s 19147 da2s 1914F
  da1v 19157 da2v 1915F damem 19167 ombase 1916F
  omidx 19177 omscale 1917F omdisp 19187 omsize 1918F
  omrip 19197 mkind 1919F mrreg 191A7 mrdip 191AF
  mripon 191B7 sdump 191BF outmem 191C7 outbuf 191CF
  outcur 191D7 iatoff 191DF intoff 191E7 nameoff 191EF
  idtoff 191F7 impbad 191FF kn 19207 snlen 1920F
  semcnt 19217 semacc 1921F hhrv 19227 hno 1922F
  hnl 19237 snam 1923F noffs 19247 knownoff 1924F
  semrows 19257 labmap 1925F sstate 19267 semstate 1926F
  mblen 19277 mslot 1927F mslotz 19287 mslof 1928F
  mopc 19297 mis8 1929F mcount 192A7 hcount 192AF
  lfanew 192B7 coffoff 192BF optoff 192C7 sizopt 192CF
  numsect 192D7 tbloff 192DF codevaddr 192E7 falign 192EF
  fend 192F7 fsect 192FF dllcnt 19307 sectcnt 1930F
  peg2h 19317
  arg1 1931F (0x80) arg2 1939F (0x80) arg3 1941F (0x80)
  factbuf 1949F (0xC0) o_mn 1955F (0xE8) o_cc 19647 (0x88)
  o_r64 196CF (0x88) o_r8 19757 (0x88) o_r16 197DF (0x88)
  o_r32 19867 (0x88) o_kw 198EF (0x28) tplb 19917 (0xC8)
  mbuf 199DF (0xC0) ptplb 19A9F (0x48) ftplb 19AE7 (0xC8)
  gtplb 19BAF (0x68) w1 19C17 (0x200)
конец тела: 19E67 (vsize 0x19E17)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x19E01..0x19E17, 0x16 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=22516; как kernel/uva — T-E9-20). E9.2-4: массив ptplb[9] (0x48 Б) добавлен ПЕРЕД w1 — инвариант сохранён (проверен кругом T-E9-20). E9.4-4b-1: скаляры развилки lfanew/coffoff/optoff/sizopt/numsect/tbloff/codevaddr/falign/fend/fsect — инвариант хвоста внутри w1 не задет. E9.4-4b-2: скаляры dllcnt/sectcnt и массив ftplb[25] (0xC8 Б) ПЕРЕД w1 — инвариант сохранён. E9.4-4b-3: скаляр peg2h (+8 Б после sectcnt) и массив gtplb[13] (0x68 Б) ПЕРЕД w1 — тот же прецедент; хвост 0x16 Б, круг T-E9-20 зелёный (M=22516 H=0).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 0B4D4375…F48896A9, bridge.brick — E13AE8AE…5437CE7A3, bridge.exe — DDD6BFB8…8543666 (полные — VERIFY.md).
