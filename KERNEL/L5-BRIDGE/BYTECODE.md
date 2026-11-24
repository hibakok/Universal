# BYTECODE. Модуль M5-BRIDGE — карта образа

Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: разбор образа bridge.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L5-BRIDGE/bridge.exe, 93184 байта (0x16C00) |
| SHA-256 | E79BE472725F71F170FC4825123795176E58C4F2CA096C8D49DE9E20477EE8C4 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |
| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 14 частей bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 137676 Б (53% предела входа 256 КиБ; 4647 строк — заголовок bridge.b2) |
| Тело секции | 92454 байта (0x16926), RVA 0x1000, SRD 0x16A00 |
| VirtualSize | 0x16926 (одна секция); target 0x16801, bss 0x125 (хвост — виртуальные нули) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |
| M-строк в исходнике | 19635 (bridge.b2; 100% M — H=0, круг T-E9-20: M=19635 H=0) |
| Меток в исходнике | 1258 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |
| Функций | 119 (карта — §2; +decff/push_tgt/jtab — E9.4-4a) + данные (§3) |
| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 654950666 + 66823765 + 68988392 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |

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

декодер, часть 2 (bridge_self_d2.wall — E9.2-3a; FF — делегация в decff):
  decimm             51C8  push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC
  decshift           5968  сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)
  decgrp             5D31  imm-группа 80/81/83 (reg с REX.R)
  decgrp2            62AA  хвостовые C6/C7/F6/F7 (FF -> decff — E9.4-4a)
  decbr              6929  переходы E8/E9/EB/jcc rel8 (классы 2/3/4)
  decode_ins         6D72  диспетчер: REX, 0F, множества байтов; da*/om*

декодер, часть 3 — группа FF (bridge_self_d3.wall — срез E9.4-4a):
  decff              79CD  FF: peek ext с REX.R ДО modrm_read; /0 inc /1 dec /2 call /4 jmp r/m64 (КОСВЕННЫЙ — размер /4 ВСЕГДА 64, класс 5 — терминал спуска)

спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a + E9.4-4a):
  push_tgt           7CFF  цель в стек — ДЕДУПЛИКАЦИЯ по значению (карта pushmap; вне [0, rawlim) не кладётся; предел pend 1+rawlim)
  jtab               7E12  таблица переходов: jmp qword [rip+X] — qword-строки «до первого non-code qword» -> кандидаты (== _jtab; чтение — тело+вирт. нули)
  walk_code          80D4  стек целей (куча), проход, тени/нули/терминалы (dcls 5 — терминал + jtab; цели — push_tgt)
  sweep_ins          86FF  выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию
  calc_target        897A  target (вилка raw-0x1FF) и bss

примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b; с E9.2-4 — и вызов ptpl_dec ветви G):
  fill_offs          8BB4  смещения NUL-имён блоба -> массив offs
  init_tables        8CFC  таблицы мнемоник/условий/регистров + шапки b2/PEG
  tpl_dec            8E7B  HEX-литерал s_tpl (199 Б) -> массив tplb
  app_ch             9076  байт в буфер вывода
  app_name           90E1  имя из блоба по таблице смещений
  app_reg            919F  имя регистра (блоб по размеру 8/16/32/64)
  out_hexv           9304  ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)
  out_hxs            95AF  знаковый hex (imm/цель/счётчик)
  out_hxu64          9619  hex u64 (отрицательное = битовый образ)
  out_hex2           96C3  ровно 2 hex-цифры (байты H/DB)
  out_hex4m          980E  минимум 4 hex-цифры (@смещения)
  out_sdec           9B7B  знаковый dec со знаком +/-
  note_op            9C26  примечание одного операнда (== _note)
  emit_note          9FAB  примечание H-строки (jcc/имена/[rip±d])
  emit_h             A262  H-строка выжившей инструкции
  emit_data          A456  данные сегмента DZ/DB (== оракул)
  app_tpl            A921  кусок шаблона шапки из tplb

карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):
  imp_hints          A9AE  записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)
  san_put            AE51  имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)
  imp_offs           B2F6  базы импортов: iatoff/intoff/nameoff/idtoff
  imp_labels         B454  метки iat_/d* (представимость!) + knownoff; impbad
  build_sstate       BBC1  карта выживших: 1 старт / 2 внутри
  sem_add            BDAB  кандидат-тройка (off, kind, h); совпадение off — замена
  dq_base            C054  твонки IAT/INT: валидность значений + меток hint
  dd_idt             C488  дескриптор IDT — кандидат DD
  sem_filter         C52A  приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate
  ins_labels         CF7B  метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)

рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):
  out_hexl           D310  СТРОЧНЫЙ hex без нулей (имена l*/d*)
  emit_labname       D5BB  имя метки по labmap (d/l/iat_ из snam)
  emit_cut           D7B2  строка разреза «:имя ; @смещ4»
  emit_dollar        D862  dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex
  emit_sem           D977  строка DD (5 значений) / DQ ($имя | 0)
  build_maps         DCE0  сборка карт: кучи + sstate + импорты + семантика + метки операндов
  emit_body          E0ED  ДРАЙВЕР (КАНОН): шапка + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)

примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):
  m_put              E822  байт в буфер кодировки mbuf
  m_put4             E88D  dword LittleEndian в mbuf (imm32/disp32)
  m_rex              E988  REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)
  m_enc_mem          EAEF  modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem
  m_cmp              EFA3  СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template
  m_kw               F387  слово размера byte/word/dword/qword + пробел
  m_dollar           F4F4  «$имя» ($base/-4096 | labmap; «:1» при rel8)
  m_opmem            F614  рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)
  m_opr              F9E5  ренер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)

кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):
  m_bsimple          FC74  cdqe/cqo/ret/int3 (SIMPLE)
  m_bjmp             FDC7  jmp ($base/метка; EB слот 1 / E9 слот 4)
  m_bjcc             FF92  jcc (70|cc слот 1 / 0F 80|cc слот 4)
  m_bcall            1016A  call (E8 $метка | FF 15 [rip+$имя])
  m_bmovzx           103BB  movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)
  m_bstack           108EE  push/pop r64 (5x + REX.B)
  m_btest            10AAF  test r,r (84/85)
  m_blea             10D8A  lea r32/r64, mem (8D, без kw)
  m_bimul            10FD3  imul r64,r64 (REX.WRB 0F AF /r)
  m_bshift           1128A  rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)
  m_bf7              11863  neg/idiv (F7 /3 /7)
  m_bff              11A55  inc/dec (FF /0 /1)

кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):
  m_alu_base         11C47  базовый опкод ALU по dname (00/08/20/28/30/38)
  m_alu_ext          11D53  /ext ALU по dname (0/1/4/5/6/7)
  m_alu_imm          11E5F  форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)
  m_balu             11FF6  add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)
  m_bmov             12DC4  mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)

драйвер ветви M (bridge_self_m4.wall — E9.2-3c):
  m_body             13FD7  диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)
  m_line             1479E  ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)

PEG-выход (bridge_self_g.wall — срез E9.2-4):
  ptpl_dec           1495C  HEX-литерал s_ptpl (72 Б) -> массив ptplb (шапка PEG)
  emit_peg           14B57  ДРАЙВЕР PEG: шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom (SPEC/15 п. 8 == _peg_text); запись .peg (коды 8/9)

вход (bridge.wall):
  main ................. 14C48  CLI -> чтение EXE -> проверки -> спуск ->
                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H)
                               -> PEG-выход (E9.2-4) -> факты M=/H=
```

## 3. Данные образа (RVA)

```
строки (55): s_use 15717 s_long 1574D s_oexe 15768 s_rexe 15782
  s_family 1579C s_big 157B4 s_oout 157CD s_wout 157E7 s_f1 15802
  s_f2 15815 s_f3 1581C s_f4 15823 s_f5 15828 s_f6 1582D
  s_f7 15832 s_f8 1583A s_f9 1583F s_fa 15842 s_crlf 15845
  s_pref 15847 s_needle 15854 s_dll 15865 s_h 15871 s_at 15873
  s_ml 15877 s_ripl 15879 s_base 1587F s_s1 15883 s_kw 15885
  s_dz 1589F s_db 158A2 s_iat 158A5 s_dd 158A9 s_dq 158AC
  s_mem 158AF s_rip 158B4 s_cl 158B8 s_j 158BA s_comma 158BB
  s_mn 158BD s_cc 15936 s_r64 1595E s_r8 1599C s_r16 159DE
  s_r32 15A1C s_tpl 15A62 s_ptpl 15BF0 s_dotexe 15C80 s_pm 15C85
  s_pe 15C8D s_pi 15C95 s_pa 15C9D s_pb 15CA3 s_ps 15CA9
  s_ph 15CB4
глобали (87): hstdout 15CBE cmdline 15CC6 written 15CCE wlen 15CD6
  exebuf 15CDE exelen 15CE6 entryrva 15CEE vsize 15CF6 rawsize 15CFE rawptr 15D06
  modlen 15D0E thunk 15D16 dllfile 15D1E impn 15D26 insmap 15D2E lenmap 15D36
  pend 15D3E pushmap 15D46 rawlim 15D4E psp 15D56 inscount 15D5E maxend 15D66 swcur 15D6E
  target 15D76 bss 15D7E dlen 15D86 dcls 15D8E dtgt 15D96 dpos 15D9E
  mpos 15DA6 mreg 15DAE dname 15DB6 dcc 15DBE dargc 15DC6 da1k 15DCE
  da2k 15DD6 da1r 15DDE da2r 15DE6 da1s 15DEE da2s 15DF6
  da1v 15DFE da2v 15E06 damem 15E0E ombase 15E16 omidx 15E1E omscale 15E26 omdisp 15E2E
  omsize 15E36 omrip 15E3E mkind 15E46 mrreg 15E4E mrdip 15E56 mripon 15E5E
  sdump 15E66 outmem 15E6E outbuf 15E76 outcur 15E7E iatoff 15E86 intoff 15E8E
  nameoff 15E96 idtoff 15E9E impbad 15EA6 kn 15EAE snlen 15EB6 semcnt 15EBE
  semacc 15EC6 hhrv 15ECE hno 15ED6 hnl 15EDE snam 15EE6 noffs 15EEE
  knownoff 15EF6 semrows 15EFE labmap 15F06 sstate 15F0E semstate 15F16 mblen 15F1E
  mslot 15F26 mslotz 15F2E mslof 15F36 mopc 15F3E mis8 15F46 mcount 15F4E
  hcount 15F56
  arg1 15F5E (0x80) arg2 15FDE (0x80) arg3 1605E (0x80)
  factbuf 160DE (0xC0) o_mn 1619E (0xE8) o_cc 16286 (0x88)
  o_r64 1630E (0x88) o_r8 16396 (0x88) o_r16 1641E (0x88)
  o_r32 164A6 (0x88) o_kw 1652E (0x28) tplb 16556 (0xC8)
  mbuf 1661E (0xC0) ptplb 166DE (0x48) w1 16726 (0x200)
конец тела: 16926 (vsize 0x16926)
```

Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x16801..0x16926, 0x125 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=19635; как kernel/uva — T-E9-20). E9.2-4: массив ptplb[9] (0x48 Б) добавлен ПЕРЕД w1 — инвариант сохранён (проверен кругом T-E9-20). E9.4-4a: глобаль pushmap (+8 Б, кластер спуска) — инвариант хвоста внутри w1 не задет (хвост 0x125 Б; круг T-E9-20 зелёный).

## 4. Контроль воспроизведения

Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):

```
splice.exe bridge.wall bridge_s.flat
wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)
enc.exe    bridge_s.b2  bridge_s.brick
brick.exe  bridge_s.brick bridge_s.bin
pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)
```

SHA-256 артефактов: bridge.b2 — 272C059A…EA41F0A, bridge.brick — AB66A23C…99E24E84, bridge.exe — E79BE472…7EE8C4 (полные — VERIFY.md).
