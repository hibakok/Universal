# Карточка модуля M5-BRIDGE (мост BRIDGE: EXE -> BRICK v2 + PEG v1)

Паспорт файла: KERNEL/L5-BRIDGE/CARD.md | слой: L5 | роль: карточка модуля.

| Поле | Значение |
|---|---|
| ID модуля | M5-BRIDGE |
| Слой | L5 (МОСТЫ); исходник — WALL v2 (слой L2, SPEC/11) с разрезом по !include (SPEC/10) |
| Назначение | **Мост BRIDGE v1** (SPEC/15): EXE семейства UNIVERSAL -> исходник конвейера — тело секции станет текстом BRICK v2 (SPEC/09), обёртка — текстом PEG v1 (SPEC/07). Срез E9.2-1 (КАРКАС): CLI (3 аргумента), чтение EXE в кучу одним ReadFile (предел 256 КиБ), разбор PE-заголовков по фиксированным смещениям SPEC/04, СЕМЕЙНАЯ ПРОВЕРКА (инварианты check_spec04 оракула MINUS легальные отклонения: вход 0x1200 — SPEC/11 п. 6, RawSize > VirtualSize), имя модуля из DOS-заглушки, структуры импорта (IDT/INT/имя DLL/чётность hint-RVA). Срез E9.2-2 (СПУСК): декодер x86-подмножества SPEC/05 (ветвь D — длины/классы/прямые цели == lab_x86.decode оракула: терминалы ret/int3/jmp; цели jmp/jcc/call rel32; сбой декодирования и ВСЕ-НУЛЕВЫЕ байты — данные) + спуск от входа (ветвь W — стек целей, тени: младший адрес побеждает; выжившие с концом за VirtualSize — ERR=FAMILY) + вычисление target/bss (SPEC/15 п. 7). Срез E9.2-3a (RAW-ЭМИССИЯ): декодер расширен ПОЛНЫМИ операндами (мнемоника/имена регистров по таблицам/imm/память с base+index+scale+disp+riprel/цели — == lab_x86.decode); ветвь E (bridge_self_e.wall) пишет <выход>.b2: шапка SPEC/15 (кириллица UTF-8 — HEX-литерал s_tpl) + H-строки выживших инструкций («H <байты> ; @<смещ4> <примечание>» == _note оракула) + данные сегментов DZ/DB (режим RAW оракула emit_b2 — без меток/семантики/M-строк); sweep_ins заполняет дамп выживших sdump. Успех — факт-строка `U-L5-BRIDGE MODULE=<имя> ENTRY=<hex8> VSIZE=<hex8> RAW=<hex8> IMP=<dec> INS=<dec> TARGET=<hex8> BSS=<hex8>` (факты == оракулу parse_family на всех 12 артефактах семейства + синтетика теней, T-E9-18/21) И файл .b2 == оракулу RAW (T-E9-22: 12 артефактов + синтетика); отказ семейства — `ERR=FAMILY`. М-строки/метки l/d/iat_/семантика DD/DQ — срезы E9.2-3b/c; PEG-выход — E9.2-4 (аргумент .peg читается, файл не создаётся) |
| Вход | командная строка Windows: `bridge.exe <вход.exe> <выход.b2> <выход.peg>` (ровно 3 аргумента; пути ≤ 127 байт ANSI) |
| Выход | коды: 0 — успех (факт-строка в stdout + ЗАПИСАН <выход>.b2 — raw-режим E9.2-3a); 2 — справка (нет аргументов / четвёртый / пустое слово); 3 — `ERR=LONG NAME`; 4 — `ERR=OPEN EXE`; 5 — `ERR=READ EXE` (вкл. отказы GlobalAlloc — exebuf, буферы спуска insmap/lenmap/pend/sdump и вывода outmem); 6 — `ERR=FAMILY` (не семейство: любое нарушение инвариантов SPEC/04, кроме двух легальных отклонений; DOS-заглушка; импорты; с E9.2-2 — инструкция за VirtualSize и длина тела больше VirtualSize); 7 — `ERR=BIG EXE` (файл ≥ 256 КиБ); 8 — `ERR=OPEN OUT` (создание <выход>.b2); 9 — `ERR=WRITE OUT` (запись). Предел вывода: outmem 8 МиБ кучи — с запасом над худшим случаем raw-текста (~5.8 МиБ); .peg не пишется до E9.2-4 |
| Версия | E9.2-3a (сессия 70) — raw-эмиссия b2: полные операнды декодера + H-строки + DZ/DB + запись <выход>.b2 |
| Размер | 48128 байта (0xBC00); тело 47278 Б (0xB8AE); вход 0x1200 (SPEC/11 п. 6); target 0xB801, bss 0xAD |
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

Диффтест: `LAB/py/lab_t_bridge.py` (секция 18 батареи, T-E9-17..21:
фикс-пункт сборки, факты с INS/TARGET/BSS == оракулу на 12 артефактах,
CLI-контракт + 21 мутант-отказов + 2 легальных отклонения (вкл.
отказы спуска — мутанты vsize), синтетика теней T-E9-21, круг
оракула над bridge.exe).

## Состав (что читать для работы с модулем)

| Файл | Назначение |
|---|---|
| `bridge.wall` | корень с разрезом (SPEC/10): 8 ext, 34 var (29 скаляров + arg1/arg2/arg3[16] + factbuf[24] + w1[32] — массивы в конце, ПОСЛЕДНИЙ — w1: хвост !bss падает внутрь него, rip-ссылок внутрь нет — 0 H-строк в разборе моста, как cstack у kernel.exe), 19 str, main (CLI → чтение → проверки → спуск → факт-строка) |
| `bridge_self_c.wall` | ветвь C — сервис: print_error, skip0, read_arg, check_end (ровно три аргумента), widen (ANSI → UTF-16LE для CreateFile2), copy_str, out_dec, out_hex (8 ЗАГЛАВНЫХ hex-цифр) |
| `bridge_self_pe.wall` | ветвь P — разбор PE и семейство: rd16/rd32, fail_family, guard, check_head/opt/base/sect/size/body (инварианты SPEC/04), stub_name (имя модуля из заглушки), rva_off, walk_descs (IDT), cstr_len (quirk оракула), check_dll, walk_funcs (счёт функций INT/IAT + чётность hint), print_facts (факт-строка с INS/TARGET/BSS — глобали ветви W) |
| `bridge_self_d.wall` | ветвь D (декодер, часть 1): fb (байт с границей), rel8/rel32 (знаковое расширение), u32/u64 (беззнаковые чтения — imm32/imm64), modrm_read (ПОЛНЫЙ разбор modrm+SIB+disp: reg mod=3 или память base/index/scale/disp/riprel; mreg с REX.R — E9.2-3a), setters операндов (set_reg/set_rm/set_imm/set_immu/set_tgt/set_cl/set_cnt), alu_id, dec0f (jcc rel32/movzx/imul), decalu (ALU 00..3D), decmod (test/mov/lea) |
| `bridge_self_d2.wall` | ветвь D (декодер, часть 2): decimm (push/pop/cdqe/cqo/mov r,imm — imm64 вид 7/ret/int3), decshift (C0/C1/D3 — счётчик-маска 63/31), decgrp (80/81/83), decgrp2 (C6/C7/F6/F7/FF), decbr (E8/E9/EB/70..7F — цели в dtgt, dcc), decode_ins (диспетчер: REX W/R/X/B, 0F, таблица == lab_x86.decode; операнды da1*/da2*/om*; omrip = конец + disp32) |
| `bridge_self_w.wall` | ветвь W — спуск от входа: walk_code (стек целей pend 1048584 в куче, карты insmap/lenmap 262145, rawlim = min(vsize, rawsize); терминалы/нули/тени), sweep_ins (младший адрес побеждает; inscount/maxend; конец за vsize — FAMILY; СДАМП выживших sdump — куча rawlim*8+8, E9.2-3a), calc_target (target/bss, SPEC/15 п. 7) |
| `bridge_self_e.wall` | ветвь E — raw-эмиссия b2 (E9.2-3a): fill_offs/init_tables (таблицы имён мнемоник/условий jcc/регистров 8/16/32/64 — блобы s_* корня), tpl_dec (HEX-литерал шапки s_tpl -> tplb), форматтеры app_ch/app_name/app_reg/out_hexv/out_hxs/out_hxu64/out_hex2/out_hex4m/out_sdec, примечания note_op/emit_note (== _note оракула), emit_h (H-строка), emit_data (DZ/DB), app_tpl, emit_raw (шапка + цикл по sdump + запись <выход>.b2, CreateFile2 WRITE/CREATE_ALWAYS; коды 8/9) |
| `bridge.peg` | обёртка PEG (SPEC/07; SPEC/11 п. 6): !module bridge, вход 0x1200, фиксированная область импортов 0x200 |
| `bridge.b2` / `bridge.brick` / `bridge.exe` | ГЕНЕРИРУЕМЫЕ артефакты (фикс-пункт T-E9-17) |
| `BYTECODE.md` | карта образа: функции/данные по RVA |
| `VERIFY.md` | SHA-256, уровни проверки, журнал срезов |

Кирпичи — `MAP/M5-BRIDGE.md` (ветви C/P/X), `MAP/M5-BRIDGE-D.md`
(ветви D/W спуска) и `MAP/M5-BRIDGE-E.md` (ветвь E эмиссии — E9.2-3a);
указатель — MAP/METHODS-2.md.

## Регистровые соглашения модуля

Канон WALL (SPEC/11 п. 5): rbp-кадры, ARGREG rcx/rdx/r8/r9, рабочие
r10/r11. Глобальное состояние — глобали образа (BYTECODE.md §3):
exebuf (указатель буфера файла в куче GlobalAlloc 262145), exelen
(размер файла), entryrva/vsize/rawsize/rawptr (факты PE), modlen (длина
имени модуля), thunk (RVA INT/IAT), dllfile (файловое смещение имени
DLL), impn (число функций); спуск E9.2-2: insmap/lenmap/pend (указатели
буферов кучи), rawlim, psp, inscount, maxend, swcur, target, bss;
декодер: dlen/dcls/dtgt/dpos/mpos/mreg; E9.2-3a — операнды: dname/dcc/dargc/da1k/da2k/da1r/da2r/da1s/da2s/da1v/da2v/damem, память om* (ombase/omidx/omscale/omdisp/omsize/omrip), modrm: mkind/mrreg/mrdip/mripon; эмиссия: sdump (дамп выживших), outmem/outbuf/outcur; w1/cmdline/hstdout/written.

## Данные образа

- строки s_use..s_tpl (36 литералов, CRLF у диагностических; s_pref/
  s_needle/s_dll — образцы семейной проверки; s_f1..s_f8 — поля
  факт-строки; s_h/s_at/s_dz/s_db/s_mem/s_rip/s_cl/s_j/s_comma —
  фрагменты H/DZ/DB-строк и примечаний; s_mn/s_cc/s_r64/s_r8/s_r16/
  s_r32 — NUL-блобы имён (мнемоники 28 / условия jcc 16 / регистры
  16×4 размеров; смещения — fill_offs при старте); s_tpl — шапка
  SPEC/15 в HEX-тексте (199 Б UTF-8 с кириллицей — литералы WALL
  только ASCII; идиома wall_self_blob), декод — tpl_dec);
- глобальные массивы: arg1[16]/arg2[16]/arg3[16] (CLI, 128 Б — ровно
  контракт read_arg), factbuf[24] (факт-строка, 192 Б — хватает на
  ~152 Б с INS/TARGET/BSS), o_mn[29]/o_cc[17]/o_r64[17]/o_r8[17]/
  o_r16[17]/o_r32[17] (смещения имён блобов — init_tables), tplb[25]
  (шапка — tpl_dec из s_tpl), w1[32] (UTF-16LE имена входа/выхода,
  256 Б) — w1 последним (канон 0 H-строк, урок E9.2-2, подтверждён
  E9.2-3a — BYTECODE.md §3);
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
  мнемоника/регистры/imm/память/цели — сырьё примечаний H-строк);
  материал M-строк (мнемотаблица enc) — срез E9.2-3c.
- Эмиссия — raw-режим (H-строки + DZ/DB, режим RAW оракула):
  метки l/d/iat_ и семантика DD/DQ импортов — срез E9.2-3b
  (режим «H» оракула), M-строки при точном воспроизведении enc и
  замена факт-строки — E9.2-3c (канон), PEG-выход — E9.2-4
  (SPEC/15 п. 10; тесты T-E9-18/19/21 остаются до среза c).
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
         RAW=00000200 IMP=3 INS=28 TARGET=000001B9 BSS=00000007
Код:     0
Файл:    t.b2 (1896 Б — raw-режим E9.2-3a; шапка SPEC/15 + 28 H-строк
         + DZ/DB данных) == оракулу emit_b2(mode="RAW") байт-в-байт;
         круг enc -> brick -> pegen(+peg оракула) == seed.exe

bridge.exe KERNEL\L3-UNIVM\kernel.exe t.b2 t.peg
Вывод:   U-L5-BRIDGE MODULE=kernel ENTRY=00001200 VSIZE=00008A92
         RAW=00008C00 IMP=8 INS=5627 TARGET=00008A01 BSS=00000091
Код:     0
Файл:    t.b2 (raw) — H-строки всех 5627 инструкций + DZ/DB

bridge.exe KERNEL\L5-BRIDGE\bridge.exe t.b2 t.peg
Вывод:   U-L5-BRIDGE MODULE=bridge ENTRY=00001200 VSIZE=0000B8AE
         RAW=0000BA00 IMP=8 INS=9696 TARGET=0000B801 BSS=000000AD
Код:     0
Файл:    t.b2 (raw) — мост мостит сам себя (12-й артефакт)

bridge.exe чужой.exe t.b2 t.peg        (не семейство)
Вывод:   U-L5-BRIDGE ERR=FAMILY
Код:     6

bridge.exe big.exe t.b2 t.peg          (файл 262145 байт)
Вывод:   U-L5-BRIDGE ERR=BIG EXE
Код:     7
```
