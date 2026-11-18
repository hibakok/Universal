# Карта репозитория (входная точка навигации)

Паспорт файла: MAP/INDEX.md | слой: все | роль: карта всех файлов репозитория.

**Правило:** любой исполнитель (ИИ или человек) начинает работу отсюда.
Для задачи читается только карта -> карточка модуля -> указанные файлы
(см. `DOCS/02-AI-NAVIGATION.md`).

## DOCS/ — идеи и регламенты

| Файл | Роль | Строк |
|---|---|---|
| `DOCS/00-MANIFEST.md` | миссия, требования, границы проекта | 57 |
| `DOCS/01-METHODOLOGY.md` | кирпичи, ветви, слои, 10 правил | 93 |
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач (+задачи эмулятора — E6.4d-5/0) | 106 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности | 496 |
| `DOCS/03a-HISTORY.md` | детальная история выполненных этапов (вынесено из ROADMAP, E6.4c-3/4b) | 107 |
| `DOCS/04-RULES-OF-CHANGE.md` | регламент изменений и коммитов | 59 |

## SPEC/ — формальные спецификации

| Файл | Роль | Строк |
|---|---|---|
| `SPEC/00-GLOSSARY.md` | словарь терминов, регистры | 46 |
| `SPEC/01-METHOD-CARD.md` | формат карточки кирпича | 50 |
| `SPEC/02-LAYER0-SPEC.md` | правила слоя L0, верификация | 54 |
| `SPEC/03-ATOM-FORMAT.md` | грамматика формата ATOM v1 | 62 |
| `SPEC/04-PE-MINIMAL.md` | структура наших EXE, инварианты | 138 |
| `SPEC/05-X86-SUBSET.md` | реестр инструкций и кодировок | 256 |
| `SPEC/06-ARCHITECTURE.md` | целевая архитектура системы | 72 |
| `SPEC/07-PEG-FORMAT.md` | формат PEG v1 и поведение pegen | 111 |
| `SPEC/08-BRICK-FORMAT.md` | формат BRICK v1 и поведение brick (слой L1; пределы 512 КиБ/2048 меток — E6.4f-2) | 155 |
| `SPEC/09-ENC-FORMAT.md` | BRICK v2: M-строки, канонические кодировки, контракт enc (предел входа 2 МиБ — E6.4g-5) | 254 |
| `SPEC/10-SPLICE-FORMAT.md` | SPLICE v1: !include, склейка исходников, контракт splice (пределы 256 КиБ, E6.4e-2) | 148 |
| `SPEC/11-WALL-FORMAT.md` | WALL v1/v2: язык слоя L2, компиляция в BRICK v2, канон эмиттера | 393 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 254 |
| `MAP/METHODS.md` | указатель реестра кирпичей (одна строка на кирпич) | 399 |
| `MAP/M0-SEED.md` | карточки кирпичей M0-SEED (8) | 130 |
| `MAP/M0-SEED2.md` | карточки кирпичей M0-SEED2 (19) | 299 |
| `MAP/M0-HXDUMP.md` | карточки кирпичей M0-HXDUMP (23) | 360 |
| `MAP/M0-HEXGEN.md` | карточки кирпичей M0-HEXGEN (29) | 452 |
| `MAP/M0-PEGEN.md` | карточки кирпичей M0-PEGEN (37) | 500 |
| `MAP/M1-BRICK.md` | карточки кирпичей M1-BRICK (42) | 480 |
| `MAP/M1-ENC.md` | карточки кирпичей M1-ENC (поток и разбор) | 411 |
| `MAP/M1-ENC-E.md` | карточки ветви E модуля M1-ENC (кодирование, 23; E033 imul — E6.4c) | 310 |
| `MAP/M1-ENC-S.md` | служебные ветви M1-ENC: H/U/F/D (14) | 193 |
| `MAP/M1-SPLICE.md` | карточки кирпичей M1-SPLICE (27) | 431 |
| `MAP/M2-WALL.md` | карточки кирпичей M2-WALL (107) | 500 |
| `MAP/LAYERS.md` | реестр слоёв L0..L6 и их статусы | 32 |

## KERNEL/ — ядро

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L0-SEED/CARD.md` | карточка модуля M0-SEED | 52 |
| `KERNEL/L0-SEED/seed.hex` | тело секции семени, ATOM v1 (истина) | 63 |
| `KERNEL/L0-SEED/seed.peg` | обёртка семени (PEG v1, SPEC/07) | 10 |
| `KERNEL/L0-SEED/seed.exe` | материализация: 1024 байта, PE32+ | — |
| `KERNEL/L0-SEED/BYTECODE.md` | байт-за-байтом разбор всего образа | 249 |
| `KERNEL/L0-SEED/VERIFY.md` | как проверить подлинность и работу | 69 |
| `KERNEL/L0-SEED2/CARD.md` | карточка модуля M0-SEED2 (командная строка) | 96 |
| `KERNEL/L0-SEED2/seed2.hex` | тело секции семени-2, ATOM v1 (истина) | 224 |
| `KERNEL/L0-SEED2/seed2.peg` | обёртка семени-2 | 10 |
| `KERNEL/L0-SEED2/seed2.exe` | материализация: 2048 байт, PE32+ | — |
| `KERNEL/L0-SEED2/BYTECODE.md` | разбор образа: 185 инструкций, данные, импорты | 412 |
| `KERNEL/L0-SEED2/VERIFY.md` | проверка, журнал, пойманные ошибки | 78 |
| `KERNEL/L0-HXDUMP/CARD.md` | карточка модуля M0-HXDUMP (hex-дамп) | 90 |
| `KERNEL/L0-HXDUMP/hxdump.hex` | тело секции hxdump, ATOM v1 (истина) | 290 |
| `KERNEL/L0-HXDUMP/hxdump.peg` | обёртка hxdump | 12 |
| `KERNEL/L0-HXDUMP/hxdump.exe` | материализация: 3584 байта, PE32+ | — |
| `KERNEL/L0-HXDUMP/BYTECODE.md` | разбор образа: 244 записи кода, данные, импорты | 497 |
| `KERNEL/L0-HXDUMP/VERIFY.md` | проверка, журнал, пойманные ошибки | 88 |
| `KERNEL/L0-HEXGEN/CARD.md` | карточка модуля M0-HEXGEN (первый компилятор) | 113 |
| `KERNEL/L0-HEXGEN/hexgen.hex` | тело секции hexgen, ATOM v1 (истина) | 421 |
| `KERNEL/L0-HEXGEN/hexgen.peg` | обёртка hexgen | 13 |
| `KERNEL/L0-HEXGEN/hexgen.exe` | материализация: 2560 байт, PE32+ (bss) | — |
| `KERNEL/L0-HEXGEN/BYTECODE.md` | разбор образа: 370 записей кода, данные, импорты, виртуальные нули | 482 |
| `KERNEL/L0-HEXGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 96 |
| `KERNEL/L0-PEGEN/CARD.md` | карточка модуля M0-PEGEN (обёртка образов) | 130 |
| `KERNEL/L0-PEGEN/pegen.hex` | тело секции pegen, ATOM v1 (истина) | 409 |
| `KERNEL/L0-PEGEN/pegen.peg` | обёртка pegen (самосборка) | 13 |
| `KERNEL/L0-PEGEN/pegen.exe` | материализация: hexgen + pegen, 4096 байт, PE32+ | — |
| `KERNEL/L0-PEGEN/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 112 |
| `KERNEL/L0-PEGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 95 |
| `KERNEL/L1-BRICK/CARD.md` | карточка модуля M1-BRICK (ассемблер BRICK) | 140 |
| `KERNEL/L1-BRICK/brick.hex` | тело секции brick, ATOM v1 (истина E5a) | 671 |
| `KERNEL/L1-BRICK/brick.brick` | корень модуля M1-BRICK: шапка + !include трёх частей (разрез E6.3) | 7 |
| `KERNEL/L1-BRICK/brick_p1.brick` | часть 1: поток X/C/G, пассажи N, разбор директив A (5-483 строки тела) | 479 |
| `KERNEL/L1-BRICK/brick_p2.brick` | часть 2: лексика, метки, сервис H/G/U/C/F (484-744) | 261 |
| `KERNEL/L1-BRICK/brick_p3.brick` | часть 3: данные D — таблицы, импорты, bss (745-850) | 106 |
| `KERNEL/L1-BRICK/brick.peg` | обёртка brick (PEG v1, SPEC/07) | 11 |
| `KERNEL/L1-BRICK/brick.exe` | материализация: hexgen + pegen, 3584 байта, PE32+ | — |
| `KERNEL/L1-BRICK/BYTECODE.md` | сводка, карта кирпичей, данные, импорты, история | 125 |
| `KERNEL/L1-BRICK/VERIFY.md` | SHA-256, 4 уровня проверки, журнал | 129 |
| `KERNEL/L1-ENC/CARD.md` | карточка модуля M1-ENC (кодировщик BRICK v2) | 149 |
| `KERNEL/L1-ENC/enc.b2` | корень модуля M1-ENC: шапка + поток X/C/G + !include 10 частей (разрез E6.3) | 133 |
| `KERNEL/L1-ENC/enc_n.b2` | часть: ветвь N — нормализация строк (124-224) | 101 |
| `KERNEL/L1-ENC/enc_p1.b2` | часть: P011-P013 — разбор M-строки (225-498; E6.4c: диспетчер +семейство E) | 274 |
| `KERNEL/L1-ENC/enc_p2.b2` | часть: P014-P015 — память/ссылки (499-735) | 237 |
| `KERNEL/L1-ENC/enc_tr.b2` | часть: T+R — лексика и таблицы (736-988; E6.4c: mnemtab 44) | 253 |
| `KERNEL/L1-ENC/enc_e1.b2` | часть: E011-E017 — эмиттеры/память (989-1369) | 381 |
| `KERNEL/L1-ENC/enc_e2.b2` | часть: E021-E023 — ALU/сдвиги/переходы (1370-1646) | 277 |
| `KERNEL/L1-ENC/enc_e3.b2` | часть: E024-E025 — mov/movzx/lea (1647-1944) | 298 |
| `KERNEL/L1-ENC/enc_e4.b2` | часть: E026-E033 — test..int3 + imul (E6.4c) (1945-2156) | 212 |
| `KERNEL/L1-ENC/enc_svc.b2` | часть: H/G/U/C/F — сервис (2157-2345) | 189 |
| `KERNEL/L1-ENC/enc_data.b2` | часть: D — данные/импорты/bss (2346-2693; E6.4c: mnemtab +3, DZ 2; E6.4g-5: filebuf 0x200100/outbuf 0x440100 — 2 МиБ; E6.4d-4: 1 МиБ) | 348 |
| `KERNEL/L1-ENC/enc.brick` | плоская форма в BRICK v1 = enc(splice(enc.b2)) байт-в-байт (генерируемый артефакт) | 2693 |
| `KERNEL/L1-ENC/enc.peg` | обёртка enc (PEG v1, SPEC/07) | 10 |
| `KERNEL/L1-ENC/enc.exe` | материализация: brick+pegen, 12288 байт, PE32+ (рост ISA E6.4c; предел входа 2 МиБ E6.4g-5) | — |
| `KERNEL/L1-ENC/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 156 |
| `KERNEL/L1-ENC/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.2 + рост ISA E6.4c + пределы E6.4e-1/E6.4f-1/E6.4d-4/E6.4g-5 | 134 |

| `KERNEL/L1-SPLICE/CARD.md` | карточка модуля M1-SPLICE (склейка !include) | 131 |
| `KERNEL/L1-SPLICE/splice.b2` | корень модуля M1-SPLICE: шапка + поток X/C/G + !include 3 частей | 137 |
| `KERNEL/L1-SPLICE/splice_s.b2` | часть: ветви S/N — цикл уровней, директива, вывод строки | 248 |
| `KERNEL/L1-SPLICE/splice_svc.b2` | часть: H/G/U/C/F — печать, ошибки, командная строка, файлы | 189 |
| `KERNEL/L1-SPLICE/splice_data.b2` | часть: D — таблицы, строки, импорты, bss | 120 |
| `KERNEL/L1-SPLICE/splice.brick` | плоская форма в BRICK v1 = enc(splice(splice.b2)) байт-в-байт (генерируемый артефакт) | 691 |
| `KERNEL/L1-SPLICE/splice.peg` | обёртка splice (PEG v1, SPEC/07) | 10 |
| `KERNEL/L1-SPLICE/splice.exe` | материализация: brick+pegen, 3584 байта, PE32+ (пределы 256 КиБ E6.4e-2) | — |
| `KERNEL/L1-SPLICE/BYTECODE.md` | сводка образа, карта кирпичей, данные, импорты, история образа | 124 |
| `KERNEL/L1-SPLICE/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.3, история пределов | 111 |
| `KERNEL/L2-WALL/CARD.md` | карточка модуля M2-WALL (компилятор WALL v1/v2) | 210 |
| `KERNEL/L2-WALL/wall.b2` | корень: поток + 19 !include (20 частей) | 142 |
| `KERNEL/L2-WALL/wall_svc.b2` | ветви H/G/U/C/F — сервисы (реинкарнации K1) | 192 |
| `KERNEL/L2-WALL/wall_n.b2` | ветвь N — разбиение строк, проход 0 | 147 |
| `KERNEL/L2-WALL/wall_l.b2` | ветвь L — лексер WALL (+ * / % срез 1; && / || срез 3; [ ] срез 4a) | 253 |
| `KERNEL/L2-WALL/wall_pe.b2` | ветви P: want_*/поиск/local_find (база+размер — срез 4a)/chain_count (+ [ ] глубина)/arr_size P019 | 471 |
| `KERNEL/L2-WALL/wall_ph.b2` | p_expr/p_mul/p_mdm/p_unary (уровни; v2: * / %) | 408 |
| `KERNEL/L2-WALL/wall_pp.b2` | p_prim — первичные выражения | 227 |
| `KERNEL/L2-WALL/wall_pa.b2` | p_args/pa_stage/p_call_tail/call_stats — вызовы (фикс №21: pc_staged := base/base+cnt) | 384 |
| `KERNEL/L2-WALL/wall_pc.b2` | p_cond — цепочки && / || + guard (срез 3); emit_addr/len/load (+ массивы срез 4a) | 471 |
| `KERNEL/L2-WALL/wall_pg.b2` | guard-эмиттеры E036/E037/E038 (срез 3, d/t-метки) | 114 |
| `KERNEL/L2-WALL/wall_p1.b2` | проход 1: цикл, диспетчер, main | 138 |
| `KERNEL/L2-WALL/wall_pd.b2` | объявления (+ var a[n] срез 4a) + заголовки func | 449 |
| `KERNEL/L2-WALL/wall_p1s.b2` | утверждения прохода 1 (статы; + var a[n] срез 4a) | 322 |
| `KERNEL/L2-WALL/wall_p2.b2` | проход 2: цикл, диспетчер, заголовки, предел меток выхода nlab 2000 (E6.4d-3/3-1) | 201 |
| `KERNEL/L2-WALL/wall_p2s.b2` | эмиттеры E029-E02D + утверждения прохода 2: if/while | 406 |
| `KERNEL/L2-WALL/wall_p2t.b2` | эмиттеры переходов и меток | 100 |
| `KERNEL/L2-WALL/wall_e.b2` | примитивы вывода, div10, out_dec, заголовок v1/v2 (фикс №16 — str_emit) | 400 |
| `KERNEL/L2-WALL/wall_ep.b2` | пролог/эпилог/alu/shift/imul/divmod | 192 |
| `KERNEL/L2-WALL/wall_ed.b2` | импорты/данные (строки, глобальные var DZ 8n — срез 4a) | 386 |
| `KERNEL/L2-WALL/wall_data.b2` | ветвь D: таблицы, strblob (113), bss r13+X | 361 |
| `KERNEL/L2-WALL/wall.wall` | само-исходник на WALL v2 — КОРЕНЬ с разрезом SPEC/10 (E6.4d-2/3..4/3c-3): ext/var/str + main + 18 частей; CLI == wall.exe, чтение, GlobalAlloc, проходы 0/1 + проход 2 (срезы A..C-3) | 338 |
| `KERNEL/L2-WALL/wall_self_c.wall` | часть каркаса: сервис — print_error/skip0/read_arg/widen (E6.4d-1) | 147 |
| `KERNEL/L2-WALL/wall_self_n.wall` | часть каркаса: проход 0 на WALL (E6.4d-2/2) — stq, fail_format, lex_line, pass0; карта текстов smem | 262 |
| `KERNEL/L2-WALL/wall_self_pe.wall` | часть каркаса: хелперы прохода 1 (E6.4d-2/3..3/2) — getq, tok_next, kw_lookup, chk_name, names_find/_ci/add, local_find (P008), max2/tok_is1 (экономия меток), arr_size, at_end/want_id/want_sym1; таблицы tabmem | 434 |
| `KERNEL/L2-WALL/wall_self_ph.wall` | часть каркаса: уровни выражений стат-режимом (E6.4d-3/2) — p_expr (P010), p_mul (P011), p_mdm (P01A), p_unary (P012); курсор pcur/ple | 77 |
| `KERNEL/L2-WALL/wall_self_pp.wall` | часть каркаса: первичные + индексация (E6.4d-3/2; эмит-плечи E6.4d-4/3c-2/1..2/2) — p_prim (P013: откат outcur + перепознание базы d+k), pp_prim0 (P013a: число/скобки/&имя/getb/len/вызов/имя), pp_pcount (P01B), pp_pairs (P01C: статы + эмит T-склад/хвост), pp_strchk (P01E) | 292 |
| `KERNEL/L2-WALL/wall_self_pa.wall` | часть каркаса: вызовы и astore-проверка (E6.4d-3/2; эмит-механика E6.4d-4/3c-2/2) — p_args (P014: стейджинг после каждого аргумента; фикс №19+№21), pa_stage (P017: C(base+cnt+1)/S5), p_call_tail (P015), emit_argload, call_stats (P016), astore_chk (P01D; фикс №22: копия lay-окна — только стат pc_mode == 0) | 261 |
| `KERNEL/L2-WALL/wall_self_pc.wall` | часть каркаса: условие if/while (E6.4d-3/3; эмит-плечо C-3) — p_cond (P018: стат — сравнения, '&&'/'||', maxd, v2flag; эмит — m-скан дизъюнктов, операнды на глубине 2 + T1-склад + «M cmp r10, r11» + jcc-инверсии + d/t-метки; параметры pfx/e/k) | 192 |
| `KERNEL/L2-WALL/wall_self_pd.wall` | часть каркаса: объявления + заголовки func прохода 1 (E6.4d-2/3..2/4) — p1_decl (S003): var/str/ext; p1_funchdr (S004) + fh_param (S00E): larr/bstk/ftab; окно дублей — local_find | 208 |
| `KERNEL/L2-WALL/wall_self_p1.wall` | часть каркаса: каркас прохода 1 (E6.4d-2/3..3/3) — p1_line (S002: func -> S004, fcur -> S006/S007/S008/S009/S00A/S00B/S00C/S00F/S00D), pass1 (S001) + пост-проверка main + сброс ifseq, set_lastline | 151 |
| `KERNEL/L2-WALL/wall_self_p1s.wall` | часть каркаса: утверждения прохода 1 (E6.4d-2/4..3/3; C-3 — p1s_if/p1s_while вызывают p_cond(0, 0, 0): параметры эмит-плеча) — p1s_var (S006), p1s_end (S007), p1s_if (S009), p1s_while (S00A), p1s_else (S008), p1s_brk (S00F), p1s_return (S00B), p1s_setb (S00C), p1_namestmt (S00D); ifarr — окно tabmem+4685888 | 266 |
| `KERNEL/L2-WALL/wall_self_blob.wall` | часть каркаса: ДАННЫЕ эмитции (E6.4d-4/3a) — блоб канона 2048 Б hex-литералами sd0..sd7 (8x512 симв. = 256 Б; таблица off/len в комментариях; ГЕНЕРАТОР LAB/ai/wall_self_data.py — не редактировать) | 142 |
| `KERNEL/L2-WALL/wall_self_e.wall` | часть каркаса: примитивы вывода и данных (E6.4d-4/3a, 3c-1) — blob_dec/init_blob (декодер блоба в sblob=outmem+0), out_ch/copy/str/line (курсор — глобаль outcur), out_hex/hex2/dec, lower_copy, get_ext (реинкарнации K2-E001..E008/E012/E025) + emit_cmt (E009), str_dlen (E013), str_emit+se_doline+esc_code (E014) | 280 |
| `KERNEL/L2-WALL/wall_self_d.wall` | часть каркаса: СЕКЦИИ ДАННЫХ (E6.4d-4/3c-1) — set_cmt (строка №ln -> cmt_ptr/cmt_len из smem), emit_strdata (E027: :имя + DZ 0 / DB-строки <= 16), emit_globdata (E028: :имя + DZ 8n + комментарий) | 92 |
| `KERNEL/L2-WALL/wall_self_g.wall` | часть каркаса: ЭМИТТЕРЫ ВЫРАЖЕНИЙ (E6.4d-4/3c-2/1) — emit_tstore/emit_tload (T-склад уровней: «M mov [rbp-X], r10» / «M mov r11, r10» + «M mov r10, [rbp-X]»), emit_alu (E020) + alu_tail, emit_shift (E021), emit_imul (E034), emit_divmod (E035), emit_addr (E022), emit_len (E023), emit_load (E024) — строки блоба по смещениям, nbase — глобаль st_p2nbase | 238 |
| `KERNEL/L2-WALL/wall_self_f.wall` | часть каркаса: КАДРЫ ФУНКЦИЙ (E6.4d-4/3b) — emit_kadr/emit_vyhod (E010), emit_lab (E011), calc_framesize (E017), emit_prologue (E018 — ARGREG[i] if-цепочкой), emit_epilogue (E019) | 121 |
| `KERNEL/L2-WALL/wall_self_y.wall` | часть каркаса: проход 2, срезы A+B+C-1+C-2/1..2/3+C-3 (E6.4d-4/3a..3c-3) — pass2 (Y001: пролог + цикл строк по smem + pc_mode=1 + СЕКЦИИ ДАННЫХ при непустых scount/vcount + предел nlab), emit_header/imports/entry (E015/E026/E016) + p2_line (Y002: cmt_ptr/cmt_len, плечи 0/4..8 + 9 setb + имя-цепочка p2_namestmt + 12/13 p2s_break/p2s_continue), p2_funchdr (Y00A: + st_p2maxd/maxc/nbase + окно lay из ftab), p2s_var/end/if/while/else (эмитция функций + bstk + GUARD: p2s_if — p_cond(0, e, k); p2s_while — :_w<k> + p_cond(1, 1, k); p2s_else — jmp $_if<ke> + :_if<k>; p2s_end — while: обратный jmp + :_w<ke>, if/else: :_if<ke>) и p2s_return (Y008: выражение p_expr(1) эмит-режимом + «M mov rax, r10» + эпилог) | 460 |
| `KERNEL/L2-WALL/wall_self_t.wall` | часть каркаса: СТАТЫ-ИМЕНА эмит-режимом (E6.4d-4/3c-2/3) — emit_sstore (E02D: стейджинг S-слота s(i) = nbase+maxd+maxc+i+1), p2s_setb (Y009: S0/S1/S2 + «M mov r10/r11/al, [rbp-S]» + «M mov [r10+r11], al» — байтовая запись, индекс БЕЗ *8) и p2_namestmt (Y00B: вызов-утверждение pc_extflg+p_args(1)+p_call_tail(0); astore — pp_pcount+astore_chk+база emit_load / цепочка pp_prim0(k)+pp_pairs(1,k-1)+S0/S1/S2 ПОРОЗНЬ+хвост shl 3/add/«M mov [r10], r11»; присваивание локали «M mov [rbp-X], r10» / глобали «M mov [rip+$имя], r10» — цель валидируется здесь, как Y00B wall.exe) | 197 |
| `KERNEL/L2-WALL/wall_self_pg.wall` | часть каркаса: GUARD-ЭМИТТЕРЫ и break/continue (E6.4d-4/3c-3, срез C-3) — jcc_name (инверсии jne je jge jg jle jl по индексу 0..5, if-цепочка), emit_jcc_line (E029: «M j<инв> $<pfx><k>[e]»), emit_jmp_line (E02A: «M jmp $<pfx><k>[e]»), emit_iflab (E02B) / emit_wlab (E02C: «:_if/_w<k>[e]», nlab++), emit_jccd (E036: «M j<инв> $<pfx><k>d<i>»), emit_jmpt (E037: «M jmp $<pfx><k>t»), emit_glab (E038: «:<pfx><k>d<i>»/«t») + p2s_break/p2s_continue (Y00C: «M jmp $_w<k>[e]», общий хвост p2s_brk — скан bstk до kind 4) | 197 |
| `KERNEL/L2-WALL/wall.brick` | плоская форма v1 = enc(splice(wall.b2)) | — |
| `KERNEL/L2-WALL/wall.peg` | обёртка (PEG v1, SPEC/07) | 9 |
| `KERNEL/L2-WALL/wall.exe` | материализация: 28160 байт (0x6E00), PE32+ (фикс №19: рост P014/P017/P015/P016/P013a/S00D +0x10C) | — |
| `KERNEL/L2-WALL/BYTECODE.md` | сводка образа, карта ветвей, данные | 263 |
| `KERNEL/L2-WALL/VERIFY.md` | проверка, журнал 16 дефектов (+ срезы 1-3, E6.4d-1..2/1) | 486 |
| `KERNEL/L2-WALL/VERIFY-E6D.md` | журнал верификации самохостинга E6.4d-2/2..3/1 (VERIFY.md у лимита 500) | 481 |
| `KERNEL/L2-WALL/VERIFY-E6D2.md` | журнал верификации самохостинга E6.4d-3/2+ (продолжение; VERIFY-E6D.md у лимита 500) | 224 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов | 28 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов | 137 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 109 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 104 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-17 | 131 |
| `TESTS/T-L1-BRICK.md` | тест-план brick T-M6-01..T-M6-17, T-E6-36 | 153 |
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11b (E6.2; рост ISA E6.4c; предел 256 КиБ E6.4e-1) | 120 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18, T-E6-16b (E6.3, E6.4e-2) | 97 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул v1/v2 + инструмент + срезы + секция 11 + самохостинг (E6.4d-5/1..2, T-E6-59/60) | 500 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории | 178 |
| `LAB/py/lab_pe.py` | разбор PE32+ + инварианты SPEC/04 | 178 |
| `LAB/py/lab_atom.py` | оракул ATOM v1 (SPEC/03) | 68 |
| `LAB/py/lab_brick.py` | оракул BRICK v1 (SPEC/08; метки 1024, imagebuf 0x40010 — E6.4e-3) | 317 |
| `LAB/py/lab_pegen.py` | оракул PEG v1 (SPEC/07) | 125 |
| `LAB/py/lab_enc.py` | оракул ENC v1 (SPEC/09): M-строка -> H-строка | 495 |
| `LAB/py/lab_enc_isa.py` | кирпич роста ISA оракула ENC: EncError/_err/_rex/_enc_imul (E6.4c) | 31 |
| `LAB/py/lab_splice.py` | оракул SPLICE v1 (SPEC/10): склейка по !include | 106 |
| `LAB/py/lab_splice_cases.py` | эталоны SPLICE: 14 якорей, 13 ошибок, большой случай | 135 |
| `LAB/py/lab_l2.py` | оракул WALL v1/v2, фронт: parse + семантика (v2: массивы, astore) | 349 |
| `LAB/py/lab_l2_lex.py` | оракул WALL: лексер + разбор выражений/условий (v2: * / %, [i], && ||) | 270 |
| `LAB/py/lab_l2_gen.py` | оракул WALL v1/v2, бэк: канон-эмиттер .b2 (guard, astore, imul/idiv; MAXLABELS 2000 — E6.4d-3/3-1; базы C-слотов вложенных вызовов — фикс №19, E6.4d-4/2) | 426 |
| `LAB/py/lab_l2_lay.py` | оракул WALL: раскладка кадров (массивы, maxd/maxc/S; базы C-слотов + maxd call-утверждений — фикс №19) | 176 |
| `LAB/py/lab_l2_err.py` | ошибка компиляции WallError (лист-кирпич) | 14 |
| `LAB/py/lab_l2_cases.py` | якоря WALL v1: 4 полных + 8 фрагментных (вручную; F17/F18 — фикс №19) | 497 |
| `LAB/py/lab_l2_cases2.py` | якоря WALL v2: 2 полных + 7 фрагментных (вручную, E6.4c) | 440 |
| `LAB/py/lab_l2_mdm.py` | эталоны WALL срез 1: 9 якорей + 5 ошибок + big_mdm + DEMO_MDM (E6.4c-3/3b) | 205 |
| `LAB/py/lab_l2_bc.py` | эталоны WALL срез 2: 7 якорей + BC_ERR_NAMES/«break 1» + big_bc + DEMO_BC | 260 |
| `LAB/py/lab_l2_cc.py` | эталоны WALL срез 3: 11 якорей + 10 ошибок + big_cc + DEMO_CC | 281 |
| `LAB/py/lab_l2_prog.py` | эталоны WALL: 26+13 ошибок, демо-круги v1/v2/nest, big_source 1/2 | 403 |
| `LAB/py/lab_enc_cases.py` | эталоны ENC: 117 якорей, 27 ошибок, демо-круг | 264 |
| `LAB/py/lab_x86.py` | декодер подмножества x86-64 (SPEC/05; E6.4c: imul/idiv/cqo) | 330 |
| `LAB/py/lab_cpu.py` | исполнитель: CPU — кэш/цикл/память/флаги/подсказка региона; threaded code + возврат следующего rip — E6.4d-5/0 (итог ~2x; шаги байт-в-байт) | 186 |
| `LAB/py/lab_cpu_ops.py` | референс: универсальные _op_* (примесь CPU; fallback + эталон диффтеста; выделен из lab_cpu по лимиту 500 — E6.4d-5/0) | 361 |
| `LAB/py/lab_thread.py` | threaded code: хелперы операндов/скан регионов, компиляция _gen, вход build (E6.4d-5/0) | 291 |
| `LAB/py/lab_thread_ops.py` | threaded code: построители тел инструкций — выражения == _op_* (E6.4d-5/0) | 319 |
| `LAB/py/lab_win.py` | загрузчик PE + заглушки kernel32 + вирт. ФС + куча (E6.4c; GlobalAlloc — E6.4d-2; 4 МиБ — E6.4d-2/2) | 304 |
| `LAB/py/lab_run.py` | прогон EXE с командной строкой | 30 |
| `LAB/py/lab_disasm.py` | дизассемблер (декод -> мнемоника) | 131 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход) | 441 |
| `LAB/py/lab_t_exe.py` | секции 7-8b батареи: инструменты enc/splice/brick (T-E6-05..11b, 12..18b, 36; пределы enc 2 МиБ (E6.4g-5) и brick 512 КиБ/2048 меток — E6.4f) | 348 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL v1+v2 (T-E6-19..24, 31..35) | 229 |
| `LAB/py/lab_t_wall2.py` | секция 10 батареи: инструмент wall.exe (T-E6-25..30 + T-E6-50 — предел меток выхода 2000, граница 2000/2001; E6.4d-3/3-1) | 166 |
| `LAB/py/lab_t_wall3.py` | секция 11 батареи: инструмент wall.exe — v2 срезы 1-3 + 4a/4b/5 + фикс №19 (T-E6-37..48, 51; big_source2, DEMO_NEST-круг) | 258 |
| `LAB/py/lab_t_wallself.py` | секция 12 батареи: каркас wall.wall (splice-корень) == оракулу + круг + CLI == wall.exe (19 путей) + проход 0+1 == оракулу parse (T-E6-49a/b/c/d) + эмитция пролога/функций/данных (T-E6-52/54) + выражения (T-E6-55) + вызовы/getb/индексация (T-E6-56) + статы-имена (T-E6-57) + guard-группа (T-E6-58) | 486 |
| `LAB/py/lab_t_wallself_final.py` | секция 12b батареи: финал E6.4d-5 шаг 1 — канарейки круга, 6 DEMO-программ компилируются КАРКАСОМ, полный круг до эмуляции (T-E6-59) | 86 |
| `LAB/py/lab_t_wallself_emit_cases.py` | источники тестов эмитции T-E6-55/56/57 (срезы C-2/1..2/3; только данные — прогонщик lab_t_wallself.py; выделен по лимиту 500 строк) | 123 |
| `LAB/py/lab_t_wallself_corpus.py` | корпус секции 12: пул источников T-E6-49d (v1/v2/E1/E2 + микроканарейки E6.4d-2/3..3/2 + big 1/2; только ASCII) | 184 |
| `LAB/py/lab_t_wallself_model.py` | модель класса эквивалентности каркаса (E6.4d-3/2..3/3): _expect_line по строкам _lex — perr/cerr, стек блоков bstk (func/if/else/while), kw-патологии str/ext (_kw_falls) | 225 |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона) | 3779 |
| `LAB/ai/enc_build.py` | (частное) построитель M1-ENC: enc.b2 -> артефакты + карта меток | 469 |
| `LAB/ai/enc_build_lim.py` | (частное) пересборка M1-ENC + dev-тесты предела 256 КиБ (E6.4e-1; исторический — границы в духе своей эпохи) | 267 |
| `LAB/ai/enc_build_lim2.py` | (частное) пересборка M1-ENC + dev-тесты предела 1 МиБ (E6.4d-4; максимум 0xFFFFF — dev-only) | 284 |
| `LAB/ai/enc_build_lim3.py` | (частное) пересборка M1-ENC + dev-тесты предела 2 МиБ (E6.4g-5; границы 0x100020/0x1FFFFF — dev-only, 0x200000 отвергнут) | 284 |
| `LAB/ai/splice_build.py` | (частное) построитель M1-SPLICE: разрез -> артефакты + dev-тесты | 228 |
| `LAB/ai/splice_build_lim.py` | (частное) пересборка M1-SPLICE + dev-тесты пределов 256 КиБ (E6.4e-2) | 344 |
| `LAB/ai/wall_build.py` | (частное) пересборка M2-WALL (idata — точная метка :idt, срез 4b; сборка после фикса №19 — E6.4d-4/2) | 116 |
| `LAB/ai/bytecode_rows.py` | (частное) перенос адресов карты ветвей BYTECODE.md §2 при пересборке (якорь-метки; фикс №19) | 165 |
| `LAB/ai/wall_test.py` | (частное) dev-тест wall.exe v1 (E6.4b) | 100 |
| `LAB/ai/wall_test_v2.py` | (частное) dev-тест среза 1: * / %, v1/v2, «U-MDM-OK 52» (эталоны — lab_l2_mdm.py) | 183 |
| `LAB/ai/wall_test_bc.py` | (частное) dev-тест среза 2: break/continue, дефект №15, «U-BC-OK 25» (эталоны — lab_l2_bc.py) | 179 |
| `LAB/ai/wall_test_cc.py` | (частное) dev-тест среза 3: цепочки && / ||, B2/F14/F16, «U-CC-OK 31» (эталоны — lab_l2_cc.py) | 159 |
| `LAB/py/lab_l2_arr.py` | эталоны WALL срез 4a: 10 якорей + ошибки + DEMO_ARR «U-ARR-OK 45» + big_arr (E6.4c-3/4) | 208 |
| `LAB/py/lab_l2_ix.py` | эталоны WALL срез 4b: якоря ix_A1..A6 + ссылки на cases2 + ошибки + big_ix (E6.4c-3/4b) | 136 |
| `LAB/ai/wall_test_arr.py` | (частное) dev-тест среза 4a: объявления массивов, базы, len (эталоны — lab_l2_arr.py) | 127 |
| `LAB/ai/wall_test_ix.py` | (частное) dev-тест среза 4b: индексация e[i] + astore, «U-WALL2-OK 85» (эталоны — lab_l2_ix.py) | 138 |
| `LAB/ai/label_map.py` | (частное) карта меток wall.brick (RVA) для BYTECODE.md | 80 |
| `LAB/ai/enc_part1..3.txt` | (частное) кодовые части enc.b2 для правок по секциям | — |
| `LAB/ai/wall_syntax_check.py` | (частное) быстрая проверка каркаса: splice-оракул + компиляция оракулом (E6.4d-2/2) | 41 |
| `LAB/ai/wall_self_test.py` | (частное) dev-прогон секции 12 вне CI (T-E6-49a/b/c; единый источник — lab_t_wallself.py) | 57 |
| `LAB/ai/wall_self_canary.py` | (частное) ПРИЁМОЧНАЯ финала E6.4d-5 шаги 1-2: канарейки круга (6 DEMO-программ КАРКАСОМ, полный круг до эмуляции) + big_source/big_source2 == оракулу каркасом (T-E6-60; ~234 млн шагов) | 173 |
| `LAB/ai/wall_self_diff.py` | (частное) ПРИЁМОЧНАЯ E6.4d-5/3 шаг 1: ФИКСПУНКТ самосборки (s1.exe(wall.wall) == s1.b2 байт-в-байт, ~548 млн шагов — прямой lab_win.Machine.run(max_steps=2 млрд); кэш круга в /tmp/wall_self_diff) + diff-анализ порядка функций vs канон wall.b2 (общие/LCS/инверсии/предложение перестановки; сессия 42) | 358 |
| `LAB/ai/cpu_fuzz.py` | (частное) диффтест эмулятора: замыкания lab_thread против универсального _op_* на случайных программах (7x500, lockstep 150/зерно, перекрывающиеся регионы, вкл. сообщения об ошибках; E6.4d-5/0) | 328 |
| `LAB/ai/wall_self_data.py` | (частное) генератор wall_self_blob.wall: strblob wall_data.b2 (2046 Б) + 2 нуля -> 8 hex-литерал + таблица off/len (E6.4d-4/3a) | 101 |
| `LAB/ai/wall_self_emit.py` | (частное) dev-тест эмитции срезов A+B+C-1+C-2/1..2/3+C-3: сборка каркаса + матрица 61 источника (+ вызовы 0..5 аргументов, двойная вложенность №21, getb, индексация; C-2/3: присваивания, вызовы-утверждения, astore цепочки, setb, канарейка №22; C-3: if/while/else/break/continue, &&/||, инверсии, вложенность; регресс if/while — полный выход) — выход == оракулу ЦЕЛИКОМ (E6.4d-4/3a..3c-3) | 411 |
| `LAB/ai/brick_build_lim2.py` | (частное) пересборка brick 512 КиБ -> 1 МиБ (E6.4g-1): 2 imm32 + 2 disp32, brick.hex/peg/exe, dev 11/11 | 425 |
| `LAB/ai/brick_build_lim3.py` | (частное) пересборка brick: предел ТЕЛА 64 -> 128 КиБ (E6.4g-2): 1 imm32 BIG OUT, hex/exe (peg/bss не тронуты), dev 11/11 | 403 |
| `LAB/ai/brick_build_lim4.py` | (частное) пересборка brick: предел ИСХОДНИКА 1 -> 2 МиБ (E6.4g-6): 2 imm32 + 2 disp32 + DBZ filebuf/imagebuf, hex/peg/exe, dev 11/11 (границы 0x100020/0x1FFFFF/0x200000) | 428 |
| `LAB/ai/pegen_build_lim.py` | (частное) пересборка pegen: предел ОБРАЗА 64 -> 128 КиБ (E6.4g-3): 2 imm32 + disp32 lea zeropad, hex/peg/exe, dev 7/7 | 281 |

LAB — измерительный прибор (Python только здесь); подробности —
`LAB/README.md`. Система UNIVERSAL от LAB не зависит. Батарея также
запускается CI (`.github/workflows/verify.yml`) на каждый пуш.

## Корень

| Файл | Роль |
|---|---|
| `README.md` | входная точка репозитория |
| `.gitattributes` | защита *.hex/*.peg/*.brick/*.b2 от CRLF, *.exe как бинарный |
| `.github/workflows/verify.yml` | CI: автозапуск батареи LAB на каждый пуш (внешний прибор) |

## Счётчики состояния (обновлять при каждом изменении)

- Кирпичей в реестре: **262** (слой L0: 8 в M0-SEED, 19 в M0-SEED2,
  23 в M0-HXDUMP, 29 в M0-HEXGEN, 37 в M0-PEGEN; слой L1: 42 в M1-BRICK,
  64 в M1-ENC (+E033 enc_imul, E6.4c), 27 в M1-SPLICE; слой L2: 79 в
  M2-WALL — +P01A/E034/E035 E6.4c-3/1, +S00F/Y00C E6.4c-3/2,
  +E036/E037/E038 E6.4c-3/3, +P019 arr_size E6.4c-3/4a,
  +P01B/P01C/P01D/P01E индексация E6.4c-3/4b).
- Модулей: **9** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE, M2-WALL).
- Тестов: **138** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..48 + T-E6-10b + T-E6-16b,
  T-E6-49a/b/c/d + T-E6-53 + T-E6-54 + T-E6-55 + T-E6-56
  + T-E6-57 (C-2/3, канарейка №22); автоматических в батарее — 135).
- Этап: **E6.4d — самохостинг wall.wall (язык v2 полный)**: шаг 1
  (E6.4d-1: каркас CLI на WALL, дефект №16 str_emit исправлен),
  под-шаги 2/1 (буфер входа GlobalAlloc 131073, 8-й ext — предел
  SPEC/11 п.9), 2/2 (проход 0: разбиение строк + полная лексика +
  карта текстов smem; лексер == оракулу _lex), 2/3 (проход 1:
  читатели карты getq/getb, диспетчер p1_line + kwtab s_kws,
  объявления var/str/ext — p1_decl; пост-проверка main), 2/4
  (заголовки func: p1_funchdr S004 + fh_param S00E — larr/bstk/
  ftab 80 Б в куче tabmem 4685888; закрытие func плечом end —
  p1s_end S007; латентный дефект main-скана getb(srcbuf, np+k)
  исправлен; quirk «func в теле» закрыт: каркас == wall.exe) и
  **E6.4d-3/1 (локальные var: p1s_var S006 — имя, [n] 1..4096,
  дубликат в окне [st_locoff, st_locoff+st_loccnt), конфликт с
  глобальными, larr, st_nslots; порядок == wall.exe == оракул;
  попутно починен стенд LAB/ai: wall_trace.py + label_map.py)** и
  **E6.4d-3/2 (выражения стат-режимом: части ph — уровни P010/P011/
  P01A/P012, pp — первичные + индексация P013/P013a/P01B/P01C/P01E,
  pa — вызовы P014/P017/P016 + astore_chk P01D, local_find P008 в
  pe; статы S00B return / S00C setb / S00D namestmt — вызов/
  astore/присваивание; хелперы max2/tok_is1 — экономия меток;
  ПОЙМАН латентный дефект №18: s_sym2 каркаса без «>>» — с E6.4d-2/2
  лексер каркаса дробил «>>» на два «>»; класс источников: тела с
  выражениями; правило cerr — ошибки только прохода 2 вне класса,
  патологические kw-формы «KW = выр»/«KW(арг)» — _kw_falls; корпус
  T-E6-49d 118 -> 153, сравнимо 86 -> 129, код-0 11 -> 38)**
  выполнены; батарея была 130/130. Попутно эпик **E6.4f — пределы
  конвейера 512 КиБ** (E6.4f-1 enc: вход 512 КиБ, outbuf 0x110040,
  SHA 4BB73143…; E6.4f-2 brick: исходник 512 КиБ / метки 2048,
  labtab/filebuf/imagebuf выросли, brick.hex перегенерирован, SHA
  AD3886E7…; оракул lab_brick синхронизирован; мотив — .b2 каркаса
  288470 > 256 КиБ). **E6.4d-3/3-1 ВЫПОЛНЕН: предел меток выхода
  wall.exe nlab 500 -> 2000** (cmp rax,7D0 в Y001; оракул
  MAXLABELS=2000; SPEC/11 п.9; ёмкость brick 2048 вкл. base ->
  запас 48; SHA wall.exe 8541FD9D…; тело 26998 Б не изменилось;
  граница 2000/2001 защищена T-E6-50: 2000 меток — принят ==
  оракулу, 2001 — ERR=FORMAT AT=0000; генератор на while — метки
  _w<k> вне ntab, 12 млн шагов против 37 у str-эквивалента;
  попутно ускорен эмулятор LAB lab_cpu 1.45x — кэш инструкций
  хранит обработчик, горячий цикл развёрнут из step(), _cond —
  таблица _CC вместо словаря на каждый jcc; батарея 131/131,
  время батареи 3м40с -> 2м52с даже с новым T-E6-50). **E6.4d-3/3
  ВЫПОЛНЕН (проходы 0/1 ПОЛНЫ): статы bstk-группы на WALL — S009
  p1s_if + S00A p1s_while (p_cond P018 стат-плечо — НОВАЯ часть
  wall_self_pc.wall) + S008 p1s_else (ifarr — окно
  tabmem+4685888, 4685888 -> 4948032) + S00F p1s_brk; корпус
  T-E6-49d 153 -> 178 (сравнимо 161, код-0 56, вне класса 17);
  ПОЙМАН латентный дефект №19 (вложенные вызовы — очередь).
  Замеры: каркас 2140 строк, .b2 493526 (94% enc 512К — РИСК),
  тело 43747/64К, меток 530/2000, EXE 44544 (журнал 19-27,
  VERIFY-E6D2.md).**
  **E6.4d-4/1 + E6.4d-4/2 + E6.4g-1 ВЫПОЛНЕНЫ: enc вход 1 МиБ;
  дефект №19 ЗАКРЫТ (базы C-слотов C(base+i) — синхронно wall.exe
  + каркас; T-E6-51; wall.exe 28160 Б, SHA E04BA41B…); brick
  1 МиБ (SHA 86DADEF9…). Батарея 132/132.**
  **E6.4d-4/3a ВЫПОЛНЕН: срез A — ПРОЛОГ эмитции** (части
  wall_self_blob/e/y.wall: примитивы вывода + блоб канона 2048 Б
  hex-литералами + Y001-начало/E015/E026/E016; outmem 2103264;
  куча эмулятора 8 -> 16 МиБ; выход == ПРЕФИКС оракула до int3
  входа, T-E6-52; 132 -> 133/133; каркас 2674 строк, .b2 700619
  (67% enc), тело 54348/64К — РИСК срезов B+).**
  **E6.4d-4/3b ВЫПОЛНЕН: срез B — ЭМИТЦИЯ ФУНКЦИЙ** (Y001-финал
  + Y002/Y00A/Y003/Y004/Y008 + МЕХАНИКА bstk Y005/Y006/Y007;
  НОВАЯ часть wall_self_f.wall — кадры E010..E019; глобали
  st_bcnt/st_fbase/st_infunc/st_lret/st_ifcnt/st_fptr/st_flen).
  Выход == оракулу на классе «тела из var/голого return/end»;
  133/133. Каркас 3011 строк, .b2 775770, тело 60967/64К (93% —
  РИСК: подъём предела тела до среза C).**
  **E6.4g-2 + E6.4g-3 ВЫПОЛНЕНЫ: ПОТОЛОК ТЕЛА КОНВЕЙЕРА 64 ->
  128 КиБ СКВОЗНОЙ (brick И pegen; пропуск плана сессии 31 —
  круг T-E6-49b идёт и через pegen). brick: 1 байт diff (cmp eax
  0x20000), SHA 79B50A01…; pegen: +3 байта (VirtualSize/
  SizeOfImage 0x3117C), SHA FAECAC2E…; оракул синхронизирован;
  T-E6-36 расширен + НОВЫЙ T-E6-53; 133 -> 134/134; попутно
  закрыт дрейф CARD M1-BRICK/BYTECODE M0-PEGEN.**
  **E6.4d-4/3c-1 ВЫПОЛНЕН: срез C часть 1 — СЕКЦИИ ДАННЫХ**
  (emit_cmt/E009 + str_dlen/E013 + str_emit/E014 — часть
  wall_self_e.wall; НОВАЯ часть wall_self_d.wall — set_cmt +
  emit_strdata/E027 + emit_globdata/E028); класс срезов A+B стал
  давать ПОЛНЫЙ выход и при глобальных str/var; T-E6-52 перевёден
  на полный выход + НОВЫЙ T-E6-54 (6 источников); 134 -> 135/135;
  каркас 3236 строк, .b2 810157 (77%), тело 64561/128К.**
  **E6.4d-4/3c-2/2 ВЫПОЛНЕН: срез C часть 2 шаг 2 — ВЫРАЖЕНИЯ С
  ВЫЗОВАМИ И ИНДЕКСАЦИЕЙ эмит-режимом** (pa_stage/P017 +
  p_call_tail/P015 + emit_argload — НОВАЯ часть wall_self_pa.wall;
  эмит-плечи p_args/pp_prim0/pp_pairs/p_prim — wall_self_pp.wall).
  ДЕФЕКТ №21 ЗАКРЫТ (синхронно wall_pa.b2: тело 27326 -> 27338,
  SHA 295730EF…); НОВЫЙ T-E6-56; 136 -> 137/137; склейка
  142632 Б, метки 882/2048.
  **E6.4g-5 + E6.4g-6 ВЫПОЛНЕНЫ: пределы ВХОДА enc/brick 1 -> 2
  МиБ (SHA B4B49041… / 38E46B52…; риски сняты; детали —
  03a-HISTORY).**
  **E6.4d-4/3c-2/3 ВЫПОЛНЕН: срез C часть 2 шаг 3 — СТАТЫ-ИМЕНА
  эмит-режимом** (класс полного выхода прохода 2 каркаса расширен
  на статы-имена в телах: присваивания локали/глобали — цель
  валидируется здесь, как Y00B wall.exe: массив/str/func/ext/
  неизвестное — ERR; вызовы-утверждения func/ext 0..5 аргументов
  (want 0); astore имя[выр]... = выр — k == 1 emit_load-база /
  k > 1 цепочка pp_prim0(k)+pp_pairs(1, k-1), последняя пара и
  значение ПОРОЗНЬ через S0/S1/S2 + хвост «M shl r11, 3» / add /
  «M mov r11, [rbp-S2]» / «M mov [r10], r11»; setb — S0/S1/S2 +
  байтовая запись «M mov [r10+r11], al», индекс БЕЗ *8): НОВАЯ
  часть wall_self_t.wall (emit_sstore E02D + p2s_setb Y009 +
  p2_namestmt Y00B) + плечи p2_line (kwi == 9 / цепочка имён —
  как Y002 wall.exe; break/continue — пропуск до C-3). ДЕФЕКТ
  №22 НАЙДЕН И ЗАКРЫТ (только каркас; в wall.exe P01D guard был):
  astore_chk копировал lay-окно st_locoff/st_loccnt БЕЗУСЛОВНО —
  в проходе 2 затирал окно p2_funchdr прошлогонними значениями
  конца прохода 1 (astore локали не в последней функции —
  ERR=FORMAT вместо кода 0; канарейка подтверждает: с дефектом
  код 6 AT=0004); guard pc_mode == 0 — как P01D wall.exe. НОВЫЙ
  T-E6-57 (10 источников; канарейка №22; источники — новый модуль
  lab_t_wallself_emit_cases.py: T-E6-55/56/57 списки вынесены из
  lab_t_wallself.py по лимиту 500 строк); dev wall_self_emit
  39 -> 49 источников (3/3); батарея 137 -> 138/138. Замеры:
  склейка 155446 Б (59% входа 256 КиБ); .b2 960265 (46% enc
  2 МиБ); .brick 909743 (43% brick 2 МиБ); метки 903/2048.
- **E6.4d-4/3c-3 (сессия 39) — срез C часть 3: GUARD-ЭМИТЦИЯ
  if/while/else/break/continue ВЫПОЛНЕНА.** НОВАЯ часть
  wall_self_pg.wall (197 строк): jcc_name (инверсии jne je jge
  jg jle jl — if-цепочка ранних возвратов, как emit_alu E020;
  jcctab wall.exe не нужен) + реинкарнации K2-E029 emit_jcc_line
  («M j<инв> $<pfx><k>[e]») / E02A emit_jmp_line («M jmp $<pfx>
  <k>[e]») / E02B emit_iflab / E02C emit_wlab («:_if/_w<k>[e]»,
  nlab++) / E036 emit_jccd («M j<инв> $<pfx><k>d<i>») / E037
  emit_jmpt («M jmp $<pfx><k>t») / E038 emit_glab («:<pfx><k>
  d<i>»/«t») + K2-Y00C p2s_break/p2s_continue (общий хвост
  p2s_brk — скан bstk до kind 4, k объемлющего while; «M jmp
  $_w<k>[e]»). p_cond (wall_self_pc.wall, 94 -> 192): параметры
  (pfx, e, k) + эмит-плечо — m-скан дизъюнктов (скан без
  потребления, как pcd_scan wall.exe; в стат-плече не нужен),
  сравнение эмит-режимом: операнды p_expr(2) + T1-склад
  emit_tstore(1)/emit_tload(1) (X = 8*(nbase+1) = t(1)) + «M cmp
  r10, r11» (s_mcmp 1191/14) + jcc-инверсия if-цепочкой +
  emit_jccd (i < m) / emit_jcc_line (последний дизъюнкт);
  «||» — i++ + emit_jmpt + emit_glab(d<i>); финал m > 1 —
  emit_glab(t); m=1 — выход как v1 (ни d/t-меток, ни jmp).
  Плечи прохода 2 (wall_self_y.wall, 418 -> 460): p2s_if — e =
  ifarr[ifseq]==0 ? 1 : 0 (lfalse = _if<ke> нет else / _if<k>
  есть else) + p_cond(0, e, st_ifcnt); p2s_while — :_w<k>
  emit_wlab + p_cond(1, 1, k); p2s_else — при ifarr != 0:
  set_cmt строки if + emit_jmp_line(0, 1, k) + emit_iflab(k, 0);
  p2s_end — kind 4: set_cmt строки while + emit_jmp_line(1, 0,
  k) + emit_wlab(k, 1); kind 2/3: emit_iflab(k, 1); p2_line
  12/13 -> p2s_break/p2s_continue. p1s_if/p1s_while (проход 1)
  — p_cond(0, 0, 0) (wall.exe в стате параметры не задаёт и не
  читает; WALL v2 требует равенства аргументов параметрам).
  НОВЫЙ T-E6-58 (12 источников: m=1/m>1, все 6 операторов,
  вложенность, break/continue, условия с вызовами/индексацией);
  dev wall_self_emit 49 -> 61 источников (3/3; регресс «статы
  вне класса if/while» переведён в полный выход 1718 Б);
  батарея 138 -> 139/139. Замеры: .b2 каркаса 1009314 (48% enc
  2 МиБ); склейка ~163 КБ (62% входа 256 КиБ). Следующий шаг —
  канарейки финала E6.4d: полный круг DEMO_* (BC/CC/ARR/WALL2/
  NEST) КАРКАСОМ, big_source/big_source2 байт-в-байт, финал —
  wall(wall.wall) == wall.b2 (порядок функций каркаса vs wall.b2 —
  возможно, перестановка).**
- **E6.4d-5/1..2 (сессия 40) — финал E6.4d шаги 1-2 ВЫПОЛНЕНЫ:
  КАНАРЕЙКИ КРУГА и BIG-ИСХОДНИКИ КАРКАСОМ.** Ядро НЕ менялось
  (wall.exe SHA 295730EF…, каркас нетронут) — только тесты и
  реестры. Шаг 1: T-E6-59 (НОВАЯ секция 12b — модуль
  lab_t_wallself_final.py, 86 строк; вызывается из секции 12
  с готовым EXE каркаса) — 6 DEMO-программ (mdm/bc/cc/arr/
  wall2/nest) компилируются КАРКАСОМ, полный круг до эмуляции
  («U-MDM-OK 52» ... «U-NEST-OK 4C»); +35 с к батарее
  (139 -> 140/140). Шаг 2: T-E6-60 — ПРИЁМОЧНАЯ (POLICY
  «секунда — предел», ~234 млн шагов): big_source/big_source2
  == оракулу каркасом; НОВЫЙ дев-скрипт wall_self_canary.py
  (9/9 OK с первого прогона; ДЕФЕКТОВ НЕ НАЙДЕНО). До этого —
  **E6.4d-5/0 (сессия 41) — УСКОРЕНИЕ ЭМУЛЯТОРА lab_cpu ~2x
  (threaded code; шаг (0) плана сессии 40, ДО замены wall.exe):**
  НОВЫЕ модули lab_thread.py (хелперы операндов + компиляция
  замыканий) + lab_thread_ops.py (построители тел; выражения ==
  _op_*); lab_cpu.py перестроен (замыкание fn(nrip) ВОЗВРАЩАЕТ
  следующий rip — без присвоения атрибута на каждом шаге;
  флаги — список fl; референс _op_* выделен в lab_cpu_ops.py
  по лимиту 500); память — struct.unpack_from/pack_into без
  срезов + одноэлементная подсказка региона memo (только при
  непересекающихся регионах). ИЗМЕРЕНИЯ: canary 6:30 -> 3:04
  (2.13x), батарея 6:15 -> 3:32 (1.78x), 140/140; СЧЁТЧИКИ
  ШАГОВ байт-в-байт идентичны (все 9 проверок canary); ядро
  не менялось (SHA). НОВЫЙ диффтест LAB/ai/cpu_fuzz.py —
  случайные программы, замыкания против _op_*: 7 зёрен x 500
  программ (150 lockstep) — 0 расхождений, 100% специализации;
  при разработке поймал 3 дефекта генератора (cf в shl — сдвиг
  size вместо size-1; push rsp — значение до декремента;
  коллизия buf при mem,mem — теперь отказ) и скрытый тихий
  fallback (счётчик fallback — обязателен к контролю). До
  этого — **E6.4d-5/3-1 (сессия 42) — ФИКСПУНКТ САМОСБОРКИ
  ДОКАЗАН** (шаг 3 часть 1; ядро НЕ менялось, батарея 140/140
  до и после): НОВЫЙ приёмочный LAB/ai/wall_self_diff.py —
  каркас, собранный полным кругом из wall.wall (s1.b2
  1009314 Б, SHA-16 0FE267F9A24ECA91 -> s1.exe 87040 Б,
  SHA-16 DAE4933716B76D80), компилирует wall.wall САМ
  (впервые; 548 385 615 шагов, 255 с — прямой
  lab_win.Machine.run(max_steps=2 млрд), дефолтных 200 млн
  мало): s2.b2 == s1.b2 БАЙТ-В-БАЙТ, прогнан дважды —
  счётчики шагов идентичны; DoD E6.4d «wall(wall.wall)
  воспроизводит собственный .b2» доказан, замена артефактов
  (шаг 3 часть 2) разблокирована. Diff-анализ порядка
  функций: s1.b2 — 117 функций, канон wall.b2 — 94, общих 78
  (67%/83%), LCS 35/78, инверсий 651 — полное выравнивание
  недостижимо (разные множества), фикс-пункт от порядка НЕ
  зависит; рекомендация — перестановку include-порядка НЕ
  делать (новый wall.b2 — генерируемый артефакт, навигация —
  по частям wall_self_*.wall; план замены — журнал 42).