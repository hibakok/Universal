# Карточка модуля M5-BRIDGE (мост BRIDGE: EXE -> BRICK v2 + PEG v1)

Паспорт файла: KERNEL/L5-BRIDGE/CARD.md | слой: L5 | роль: карточка модуля.

| Поле | Значение |
|---|---|
| ID модуля | M5-BRIDGE |
| Слой | L5 (МОСТЫ); исходник — WALL v2 (слой L2, SPEC/11) с разрезом по !include (SPEC/10; корень + 13 частей) |
| Назначение | **Мост BRIDGE v1** (SPEC/15): EXE семейства UNIVERSAL -> исходник конвейера — тело секции станет текстом BRICK v2 (SPEC/09), обёртка — текстом PEG v1 (SPEC/07). Срез E9.2-1 (КАРКАС): CLI (3 аргумента), чтение EXE в кучу одним ReadFile (предел 256 КиБ), разбор PE-заголовков по фиксированным смещениям SPEC/04, СЕМЕЙНАЯ ПРОВЕРКА (инварианты check_spec04 оракула MINUS легальные отклонения: вход 0x1200 — SPEC/11 п. 6, RawSize > VirtualSize), имя модуля из DOS-заглушки, структуры импорта (IDT/INT/имя DLL/чётность hint-RVA). Срез E9.2-2 (СПУСК): декодер x86-подмножества SPEC/05 (ветвь D — длины/классы/прямые цели == lab_x86.decode оракула: терминалы ret/int3/jmp; цели jmp/jcc/call rel32; сбой декодирования и ВСЕ-НУЛЕВЫЕ байты — данные) + спуск от входа (ветвь W — стек целей, тени: младший адрес побеждает; выжившие с концом за VirtualSize — ERR=FAMILY) + вычисление target/bss (SPEC/15 п. 7). Срез E9.2-3a (RAW-ЭМИССИЯ): декодер расширен ПОЛНЫМИ операндами (мнемоника/имена регистров по таблицам/imm/память с base+index+scale+disp+riprel/цели — == lab_x86.decode); ветвь E (bridge_self_e.wall) пишет <выход>.b2: шапка SPEC/15 (кириллица UTF-8 — HEX-литерал s_tpl) + H-строки выживших инструкций («H <байты> ; @<смещ4> <примечание>» == _note оракула) + данные сегментов DZ/DB (режим RAW оракула emit_b2 — без меток/семантики/M-строк); sweep_ins заполняет дамп выживших sdump. Срез E9.2-3b (МЕТКИ И СЕМАНТИКА — режим "H" оракула): ветвь L (bridge_self_l.wall) — записи импортов (маскированные hint-RVA + имена с quirk C-строки), san-блоб имён iat_ (ASCII [a-z0-9_], обрезка 59), метки l/d/iat_ (приоритет iat_ > l > d; ПРАВИЛО ПРЕДСТАВИМОСТИ: метка невозможна строго внутри выжившей инструкции — SPEC/15 п. 6), семантика DD/DQ импортов с $ссылками (приёмка строк без пересечений с инструкциями/друг другом/метками внутри), метки операндов (цели переходов и rip-ссылки), разрезы «:имя ; @смещ» и ДРАЙВЕР эмиссии emit_body (линейный проход по событиям [0, target)). Срез E9.2-3c (M-СТРОКИ — КАНОН mode=None): выжившая инструкция сначала M-строкой — ветвь M (bridge_self_m/m2/m3/m4.wall, 28 кирпичей K5-M001..M028): M-строка эмитится ТОГДА И ТОЛЬКО ТОГДА, когда кодировщик enc (SPEC/09) воспроизводит инструкцию ТОЧНО — контроль ПОВТОРНЫМ КОДИРОВАНИЕМ (mbuf + m_cmp: фиксированные байты + СЛОТ последним, значение слота == смещение метки − конец слота — == _template оракула), иначе H-фолбэк (байто-точность круга ВСЕГДА, SPEC/15 п. 5); свидетель — транслитерация LAB/ai/trace_m.py (46470/46470 решений и текстов). Успех — факт-строка `U-L5-BRIDGE MODULE=<имя> ENTRY=<hex8> VSIZE=<hex8> RAW=<hex8> IMP=<dec> INS=<dec> TARGET=<hex8> BSS=<hex8> M=<dec> H=<dec>` (факты + ВЫХОД моста M=/H= == оракулу parse_family/emit_b2 на всех 12 артефактах семейства + синтетика, T-E9-18/21 — замена факт-строки реальным выходом, ROADMAP E9.2-3c: факты PE сохранены префиксом, выход добавлен) И файл .b2 == оракулу КАНОНА emit_b2 (T-E9-22: 12 артефактов + синтетика спуска + синтетика меток — мутанты hint-ins (правило представимости) и imp0 (пустая таблица импорта — без отказа, с кругом валидности)). Срез E9.2-4 (PEG-ВЫХОД — ПРИЁМКА DoD ЭТАПА E9.2): ветвь G (bridge_self_g.wall, 2 кирпича K5-G001..G002) — запись <выход>.peg: регенерация обёртки PEG v1 по SPEC/15 п. 8 (== _peg_text оракула emit_peg): шапка «; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник: <имя>.exe» (кириллица UTF-8 — HEX-литерал s_ptpl корня -> массив ptplb[9], идиома s_tpl) + !module + !entry + !idata (DD[1] @0x110/@0x114) + !iat (DD[12] @0x168/@0x16C) + !bss (если != 0) + !stackcom (@0xE8)/!heapcom (@0xF8) (если != 0x1000 — значения по умолчанию опускаются, SPEC/07); буфер outmem переиспользуется после emit_body; .peg == оракулу на 12 артефактах + синтетике (T-E9-24) и сквозной круг С ВЫХОДАМИ МОСТА (T-E9-23: мост -> enc -> brick -> pegen == вход) — ЭТАП E9.2 ЗАКРЫТ; отказ семейства — `ERR=FAMILY` |
| Вход | командная строка Windows: `bridge.exe <вход.exe> <выход.b2> <выход.peg>` (ровно 3 аргумента; пути ≤ 127 байт ANSI) |
| Выход | коды: 0 — успех (факт-строка с M=/H= в stdout + ЗАПИСАНЫ <выход>.b2 (канон E9.2-3c: M-строки при точном воспроизведении enc, H-фолбэк — те же байты) И <выход>.peg (E9.2-4: обёртка PEG v1, SPEC/15 п. 8)); 2 — справка (нет аргументов / четвёртый / пустое слово); 3 — `ERR=LONG NAME`; 4 — `ERR=OPEN EXE`; 5 — `ERR=READ EXE` (вкл. отказы GlobalAlloc — exebuf, буферы спуска insmap/lenmap/pend/sdump, карты ветви L labmap/sstate/semstate + массивы импортов hhrv/hno/hnl/knownoff/noffs/snam/semrows и вывода outmem); 6 — `ERR=FAMILY` (не семейство: любое нарушение инвариантов SPEC/04, кроме двух легальных отклонений; DOS-заглушка; импорты; с E9.2-2 — инструкция за VirtualSize и длина тела больше VirtualSize); 7 — `ERR=BIG EXE` (файл ≥ 256 КиБ); 8 — `ERR=OPEN OUT` (создание <выход>.b2 ИЛИ <выход>.peg — E9.2-4); 9 — `ERR=WRITE OUT` (запись любого из выходов). Предел вывода: outmem 8 МиБ кучи — с запасом над худшим случаем H-текста (~22 Б/байт тела + ~15 Б/метку < 7.9 МиБ); PEG (~130-180 Б) пишется туда же после сброса b2 |
| Версия | E9.2-4 (сессия 73) — PEG-выход (ветвь G) + приёмка DoD этапа E9.2 |
| Размер | 91648 байтов (0x16600); тело 90724 Б (0x16264); вход 0x1200 (SPEC/11 п. 6); target 0x16201, bss 0x63 |
| Платформа | Windows x64, консольная подсистема, PE32+ |
| Импорты | kernel32.dll (8): GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |
| Самохостинг | артефакты `bridge.b2/brick/exe` — ГЕНЕРИРУЕМАЯ сборка из `bridge.wall` конвейером инструментов (wall → enc → brick → pegen + bridge.peg) под эмуляцией LAB; фикс-пункт воспроизводимости — батарея T-E9-17 (каждый пуш); bridge.b2 == оракулу WALL байт-в-байт |

## Формат вызова

```
bridge.exe <in.exe> <out.b2> <out.peg>
```

Аргументы: путь входного EXE (≤ 127 байт ANSI), путь выхода BRICK v2 и
путь выхода PEG v1 (в каркасе читаются и проверяются по счётчику
аргументов, файлы не создаются — срезы E9.2-3+). Четвёртый аргумент,
пустое слово или отсутствие слова — справка, код 2.

Семейная проверка каркаса (всё — `ERR=FAMILY`, код 6, детерминированно):

- файл короче 0x1B0 (все поля SPEC/04), нет MZ, нет сигнатуры PE\0\0
  (по e_lfanew, границы файла);
- Machine != 0x8664, NumberOfSections != 1, SizeOfOptionalHeader
  != 0xF0, Characteristics != 0x0022, Magic != 0x020B, Subsystem != 3;
- ImageBase != 0x140000000 (два dword), SectionAlignment != 0x1000,
  FileAlignment != 0x200;
- секция: имя != «.text», VirtualAddress != 0x1000,
  Characteristics != 0xE0000020;
- SizeOfImage != align_up(0x1000+vsize), SizeOfHeaders !=
  PointerToRawData (или не кратно 0x200), SizeOfRawData не кратно 0x200,
  размер файла != SizeOfHeaders + SizeOfRawData;
- точка входа вне [0x1000, 0x1000+vsize) — сама 0x1200 ЛЕГАЛЬНА
  (SPEC/15 п. 2 — отклонение семейства);
- тело пустое или из одних нулей;
- DOS-заглушка: нет префикса «Universal L0 », нет иглы
  «. No DOS support.», имя модуля не 1..31 байт или содержит
  пробельный байт (09-0D, 1C-1F, 20, 85, A0 — как .isspace оракула);
- импорты: DD[1] размер < 40; дескриптор IDT вне файла или нулевой;
  второй дескриптор не терминатор (не 20 нулей и не за файлом);
  имя DLL != kernel32.dll (без учёта регистра, вне файла — отказ);
  hint-RVA нечётный;
- спуск (E9.2-2): выжившая инструкция концом за VirtualSize;
  target > vsize (длина тела больше VirtualSize).

Диффтест: `LAB/py/lab_t_bridge.py` (секция 18 батареи, T-E9-17..24:
фикс-пункт сборки, факты с INS/TARGET/BSS и выходом M=/H= == оракулу
на 12 артефактах, CLI-контракт + 21 мутант-отказов + 2 легальных
отклонения (вкл. отказы спуска — мутанты vsize), синтетика теней
T-E9-21, эмиссия .b2 == оракулу канона T-E9-22, PEG-выход ==
оракулу T-E9-24 (12 артефактов + синтетика), сквозной круг с
ВЫХОДАМИ моста T-E9-23 (приёмка DoD этапа E9.2), круг оракула над
bridge.exe T-E9-20).

## Состав (что читать для работы с модулем)

| Файл | Назначение |
|---|---|
| `bridge.wall` | корень с разрезом (SPEC/10): 8 ext, 68 var (59 скаляров + arg1/arg2/arg3[16] + factbuf[24] + o_mn/o_cc/o_r64/o_r8/o_r16/o_r32/o_kw[5] + tplb[25] + mbuf[24] + ptplb[9] + w1[64] — массивы в конце, ПОСЛЕДНИЙ — w1: хвост !bss падает внутрь него, rip-ссылок внутрь нет — 0 H-строк в разборе моста, как cstack у kernel.exe; Е9.2-4: ptplb ПЕРЕД w1 — инвариант сохранён), 55 str (вкл. kw-слова, s_f9/s_fa — M=/H= и s_ptpl/s_dotexe/s_pm/s_pe/s_pi/s_pa/s_pb/s_ps/s_ph — PEG-выход Е9.2-4), main (CLI → чтение → проверки → спуск → таблицы → карты (L) → эмиссия .b2 КАНОН (M/H) → PEG-выход (G) → факты M=/H=) |
| `bridge_self_c.wall` | ветвь C — сервис: print_error, skip0, read_arg, check_end (ровно три аргумента), widen (ANSI → UTF-16LE для CreateFile2), copy_str, out_dec, out_hex (8 ЗАГЛАВНЫХ hex-цифр) |
| `bridge_self_pe.wall` | ветвь P — разбор PE и семейство: rd16/rd32, fail_family, guard, check_head/opt/base/sect/size/body (инварианты SPEC/04), stub_name (имя модуля из заглушки), rva_off, walk_descs (IDT), cstr_len (quirk оракула), check_dll, walk_funcs (счёт функций INT/IAT + чётность hint), print_facts (факт-строка с INS/TARGET/BSS — глобали ветви W) |
| `bridge_self_d.wall` | ветвь D (декодер, часть 1): fb (байт с границей), rel8/rel32 (знаковое расширение), u32/u64 (беззнаковые чтения — imm32/imm64), modrm_read (ПОЛНЫЙ разбор modrm+SIB+disp: reg mod=3 или память base/index/scale/disp/riprel; mreg с REX.R — E9.2-3a), setters операндов (set_reg/set_rm/set_imm/set_immu/set_tgt/set_cl/set_cnt), alu_id, dec0f (jcc rel32/movzx/imul), decalu (ALU 00..3D), decmod (test/mov/lea) |
| `bridge_self_d2.wall` | ветвь D (декодер, часть 2): decimm (push/pop/cdqe/cqo/mov r,imm — imm64 вид 7/ret/int3), decshift (C0/C1/D3 — счётчик-маска 63/31), decgrp (80/81/83), decgrp2 (C6/C7/F6/F7/FF), decbr (E8/E9/EB/70..7F — цели в dtgt, dcc), decode_ins (диспетчер: REX W/R/X/B, 0F, таблица == lab_x86.decode; операнды da1*/da2*/om*; omrip = конец + disp32) |
| `bridge_self_w.wall` | ветвь W — спуск от входа: walk_code (стек целей pend 1048584 в куче, карты insmap/lenmap 262145, rawlim = min(vsize, rawsize); терминалы/нули/тени), sweep_ins (младший адрес побеждает; inscount/maxend; конец за vsize — FAMILY; СДАМП выживших sdump — куча rawlim*8+8, E9.2-3a), calc_target (target/bss, SPEC/15 п. 7) |
| `bridge_self_e.wall` | ветвь E — примитивы эмиссии (E9.2-3a/b/c): fill_offs/init_tables (таблицы имён мнемоник/условий jcc/регистров 8/16/32/64 + слова kw — блобы s_* корня), tpl_dec (HEX-литерал шапки s_tpl -> tplb), форматтеры app_ch/app_name/app_reg/out_hexv/out_hxs/out_hxu64/out_hex2/out_hex4m/out_sdec, примечания note_op/emit_note (== _note оракула), emit_h (H-строка), emit_data (DZ/DB), app_tpl (шапка) |
| `bridge_self_l.wall` | ветвь L, часть 1 — карты и семантика (E9.2-3b): imp_hints (записи INT/IAT — маскированный u64), san_put (блоб iat_+san), imp_offs, imp_labels (метки iat_/d* + known; правило представимости), build_sstate, sem_add/dq_base/dd_idt/sem_filter (приёмка DD/DQ), ins_labels (метки операндов l*/d*) |
| `bridge_self_l2.wall` | ветвь L, часть 2 — рендер и драйвер (E9.2-3b/c): out_hexl, emit_labname/emit_cut/emit_dollar/emit_sem, build_maps, emit_body — ДРАЙВЕР (линейный проход по событиям: метка → семантика → выжившая СНАЧАЛА m_line ветви M (канон), при провале emit_h → данные; запись <выход>.b2; счёты mcount/hcount) |
| `bridge_self_m.wall` | ветвь M, часть 1 — ПРИМИТИВЫ (E9.2-3c): m_put/m_put4 (буфер кодировки mbuf), m_rex (REX по аргументам-значениям), m_enc_mem (modrm/SIB/disp памяти + слот rip — == _enc_mem), m_cmp (СВЕРКА с байтами тела: слот последним, значение == метка − конец слота — == _template), m_kw/m_dollar/m_opmem/m_opr (рендер операндов: kw/$имя/память/рег/imm) |
| `bridge_self_m2.wall` | ветвь M, часть 2 — кодировщики простых семейств (E9.2-3c): m_bsimple (cdqe/cqo/ret/int3), m_bjmp/m_bjcc/m_bcall (слоты rel8/rel32/rip — == _enc_jmp/jcc/call), m_bmovzx, m_bstack, m_btest, m_blea, m_bimul, m_bshift, m_bf7, m_bff — == ENCODERS оракула |
| `bridge_self_m3.wall` | ветвь M, часть 3 — ALU и MOV (E9.2-3c): m_alu_base/m_alu_ext/m_alu_imm (форма 80/83/81 — == _alu_imm), m_balu (5 пар операндов — == _enc_alu), m_bmov (6 пар; imm64/16-бит → H — == _enc_mov) |
| `bridge_self_m4.wall` | ветвь M, часть 4 — ДРАЙВЕР (E9.2-3c): m_body (диспетчер по dname: имя мнемоники + кодировщик семейства), m_line («M » + тело + m_cmp + хвост « ; @смещ4»; провал — откат outcur и H-фолбэк) |
| `bridge_self_g.wall` | ветвь G — PEG-ВЫХОД (E9.2-4): ptpl_dec (HEX-литерал s_ptpl — 72 Б шапки PEG с кириллицей -> массив ptplb; вызывается из init_tables), emit_peg (ДРАЙВЕР: текст PEG v1 == _peg_text оракула — шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom; переиспользует outmem после emit_body; запись <выход>.peg — коды 8/9) |
| `bridge.peg` | обёртка PEG (SPEC/07; SPEC/11 п. 6): !module bridge, вход 0x1200, фиксированная область импортов 0x200 |
| `bridge.b2` / `bridge.brick` / `bridge.exe` | ГЕНЕРИРУЕМЫЕ артефакты (фикс-пункт T-E9-17) |
| `BYTECODE.md` | карта образа: функции/данные по RVA |
| `VERIFY.md` | SHA-256, уровни проверки, журнал срезов |

Кирпичи — `MAP/M5-BRIDGE.md` (ветви C/P/X), `MAP/M5-BRIDGE-D.md`
(ветви D/W спуска), `MAP/M5-BRIDGE-E.md` (ветвь E эмиссии),
`MAP/M5-BRIDGE-L.md` (ветвь L — E9.2-3b), `MAP/M5-BRIDGE-M.md`
(ветвь M — E9.2-3c) и `MAP/M5-BRIDGE-G.md` (ветвь G — E9.2-4);
указатель — MAP/METHODS-2.md.

## Регистровые соглашения модуля

Канон WALL (SPEC/11 п. 5): rbp-кадры, ARGREG rcx/rdx/r8/r9, рабочие
r10/r11. Глобальное состояние — глобали образа (BYTECODE.md §3):
exebuf (указатель буфера файла в куче GlobalAlloc 262145), exelen
(размер файла), entryrva/vsize/rawsize/rawptr (факты PE), modlen (длина
имени модуля), thunk (RVA INT/IAT), dllfile (файловое смещение имени
DLL), impn (число функций); спуск E9.2-2: insmap/lenmap/pend (указатели
буферов кучи), rawlim, psp, inscount, maxend, swcur, target, bss;
декодер: dlen/dcls/dtgt/dpos/mpos/mreg; E9.2-3a — операнды: dname/dcc/dargc/da1k/da2k/da1r/da2r/da1s/da2s/da1v/da2v/damem, память om* (ombase/omidx/omscale/omdisp/omsize/omrip), modrm: mkind/mrreg/mrdip/mripon; эмиссия: sdump (дамп выживших), outmem/outbuf/outcur; ветвь M (E9.2-3c):
mbuf/mblen (буфер кодировки), mslot/mslotz/mslof (слот:
позиция/размер/смещение метки), mopc/mis8 (форма группы imm),
mcount/hcount (число M-/H-строк — факт-строка); w1/cmdline/hstdout/written.
Ветвь G (E9.2-4) новых скаляров не вводит — поля PE читаются rd32
напрямую (idata @272/@276, iat @360/@364, stackcom @232, heapcom @248).

## Данные образа

- строки s_use..s_ph (55 литералов, CRLF у диагностических; s_ml/s_ripl/
s_base/s_s1/s_kw/s_f9/s_fa — M-строки и факт M=/H= (E9.2-3c); s_pref/
  s_needle/s_dll — образцы семейной проверки; s_f1..s_f8 — поля
  факт-строки; s_h/s_at/s_dz/s_db/s_mem/s_rip/s_cl/s_j/s_comma —
  фрагменты H/DZ/DB-строк и примечаний; s_mn/s_cc/s_r64/s_r8/s_r16/
  s_r32 — NUL-блобы имён (мнемоники 28 / условия jcc 16 / регистры
  16×4 размеров; смещения — fill_offs при старте); s_tpl — шапка
  SPEC/15 в HEX-тексте (199 Б UTF-8 с кириллицей — литералы WALL
  только ASCII; идиома wall_self_blob, декод — tpl_dec); E9.2-4:
  s_ptpl — шапка PEG в HEX-тексте (72 Б UTF-8 — декод ptpl_dec),
  s_dotexe/s_pm/s_pe/s_pi/s_pa/s_pb/s_ps/s_ph — фрагменты PEG-строк
  (префиксы директив с LF, кроме первой);
- глобальные массивы: arg1[16]/arg2[16]/arg3[16] (CLI, 128 Б — ровно
  контракт read_arg), factbuf[24] (факт-строка, 192 Б — хватает на
  ~166 Б с INS/TARGET/BSS и M=/H=), o_mn[29]/o_cc[17]/o_r64[17]/o_r8[17]/
  o_r16[17]/o_r32[17]/o_kw[5] (смещения имён блобов — init_tables),
  tplb[25] (шапка — tpl_dec из s_tpl), mbuf[24] (буфер кодировки
  M — E9.2-3c), ptplb[9] (шапка PEG — ptpl_dec из s_ptpl, 72 Б —
  E9.2-4), w1[64] (UTF-16LE имена входа/выхода,
  512 Б) — w1 последним (канон 0 H-строк, урок E9.2-2, ОБЩЁН
  E9.2-3b — BYTECODE.md §3; ptplb ПЕРЕД w1 — инвариант подтверждён
  кругом T-E9-20: M=19237 H=0);
- входной EXE — в куче GlobalAlloc(0, 262145), читается одним
  ReadFile с лимитом (got == 262145 → BIG EXE; как srcbuf wall.exe);
- буферы спуска — в куче: insmap/lenmap GlobalAlloc(0, 262145)
  (карты стартов/длин по смещениям тела), pend GlobalAlloc(0,
  1048584) (стек целей, 131073 qword — доказуемый предел: 1 +
  ветвящиеся инструкции ≤ rawlim/2), sdump GlobalAlloc(0, rawlim*8+8)
  (дамп выживших, E9.2-3a — по qword на старт, выживших ≤ rawlim);
  вывод — outmem GlobalAlloc(0, 8388608) (8 МиБ ≥ худший случай
  raw-текста ~5.8 МиБ — 1-байтовые инструкции ~22 Б/байт тела).

## Ограничения (снять в следующих срезах)

- Вход ≤ 256 КиБ (ERR=BIG EXE) — покрывает все артефакты семейства
  (максимум wall.exe — 87040 Б); подъём предела — синхронно с
  конвейером, по потребности срезов E9.2+.
- Декодер — ПОЛНЫЕ операнды (== lab_x86.decode: длины/классы/цели +
  мнемоника/регистры/imm/память/цели — сырьё примечаний H-строк И
  M-строк); реализовано — ветвь M (E9.2-3c).
- Эмиссия — КАНОН (M-строки при точном воспроизведении enc —
  контроль повторным кодированием, иначе H-фолбэк; метки l/d/iat_ +
  семантика DD/DQ + разрезы; факт-строка с выходом M=/H=) — срез
  E9.2-3c; PEG-выход (обёртка PEG v1 — SPEC/15 п. 8) — срез E9.2-4
  ЗАВЕРШЁН — ЭТАП E9.2 ЗАКРЫТ (диффтесты T-E9-22/24 + круг T-E9-23
  с выходами моста).
- Разбор PE — только фиксированные смещения шаблона SPEC/04
  (e_lfanew читается, но поля — по шаблону; как lab_pe оракула).
  Чужие EXE (PEG v2) — E9.4+.

## Примеры

```
cmd -> KERNEL\L5-BRIDGE\bridge.exe
Вывод:   U-L5-BRIDGE CMDS: BRIDGE <IN.EXE> <OUT.B2> <OUT.PEG>   (54 Б, CRLF)
Код:     2

bridge.exe KERNEL\L0-SEED\seed.exe t.b2 t.peg
Вывод:   U-L5-BRIDGE MODULE=seed ENTRY=00001000 VSIZE=000001C0
         RAW=00000200 IMP=3 INS=28 TARGET=000001B9 BSS=00000007 M=28 H=0
Код:     0
Файлы:   t.b2 (канон E9.2-3c: шапка SPEC/15 + 28 M-строк
         («M sub rsp, 28 ; @0000», «M jnz $l102b:1 ; @0040» …)
         + разрезы/метки/семантика DD/DQ + DZ/DB данных)
         == оракулу emit_b2() (канон) байт-в-байт;
         t.peg (E9.2-4: обёртка PEG v1 — «!module seed», «!entry 1000»,
         «!idata 1100 28», «!iat 1130 20», «!bss 7»; stackcom/heapcom
         по умолчанию 0x1000 — опущены) == оракулу emit_peg();
         круг enc -> brick -> pegen(+peg МОСТА) == seed.exe (T-E9-23)

bridge.exe KERNEL\L3-UNIVM\kernel.exe t.b2 t.peg
Вывод:   U-L5-BRIDGE MODULE=kernel ENTRY=00001200 VSIZE=00008A92
         RAW=00008C00 IMP=8 INS=5627 TARGET=00008A01 BSS=00000091 M=5627 H=0
Код:     0
Файлы:   t.b2 (канон) — 100% M-строк (ядро собрано enc — конвейер
         воспроизводит все 5627 инструкции) + DZ/DB; t.peg —
         «!bss 91», «!stackcom 4000», «!heapcom 4000»

bridge.exe KERNEL\L5-BRIDGE\bridge.exe t.b2 t.peg
Вывод:   U-L5-BRIDGE MODULE=bridge ENTRY=00001200 VSIZE=00016264
         RAW=00016400 IMP=8 INS=19237 TARGET=00016201 BSS=00000063 M=19237 H=0
Код:     0
Файлы:   t.b2 (канон) + t.peg — мост мостит сам себя (12-й артефакт;
         100% M; в t.peg — собственные !bss 63/!stackcom/!heapcom)

bridge.exe чужой.exe t.b2 t.peg        (не семейство)
Вывод:   U-L5-BRIDGE ERR=FAMILY
Код:     6

bridge.exe big.exe t.b2 t.peg          (файл 262145 байт)
Вывод:   U-L5-BRIDGE ERR=BIG EXE
Код:     7
```
