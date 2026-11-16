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
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач | 104 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности | 495 |
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
| `KERNEL/L2-WALL/wall_pa.b2` | p_args/p_call_tail/call_stats — вызовы | 300 |
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
| `KERNEL/L2-WALL/wall.wall` | само-исходник на WALL v2 — КОРЕНЬ с разрезом SPEC/10 (E6.4d-2/3..3/2): ext/var/str + main; CLI == wall.exe, чтение, GlobalAlloc srcbuf+smem+tabmem, pass0+pass1 | 196 |
| `KERNEL/L2-WALL/wall_self_c.wall` | часть каркаса: сервис — print_error/skip0/read_arg/widen (E6.4d-1) | 147 |
| `KERNEL/L2-WALL/wall_self_n.wall` | часть каркаса: проход 0 на WALL (E6.4d-2/2) — stq, fail_format, lex_line, pass0; карта текстов smem | 262 |
| `KERNEL/L2-WALL/wall_self_pe.wall` | часть каркаса: хелперы прохода 1 (E6.4d-2/3..3/2) — getq, tok_next, kw_lookup, chk_name, names_find/_ci/add, local_find (P008), max2/tok_is1 (экономия меток), arr_size, at_end/want_id/want_sym1; таблицы tabmem | 434 |
| `KERNEL/L2-WALL/wall_self_ph.wall` | часть каркаса: уровни выражений стат-режимом (E6.4d-3/2) — p_expr (P010), p_mul (P011), p_mdm (P01A), p_unary (P012); курсор pcur/ple | 77 |
| `KERNEL/L2-WALL/wall_self_pp.wall` | часть каркаса: первичные + индексация (E6.4d-3/2) — p_prim (P013), pp_prim0 (P013a), pp_pcount (P01B), pp_pairs (P01C), pp_strchk (P01E) | 215 |
| `KERNEL/L2-WALL/wall_self_pa.wall` | часть каркаса: вызовы/astore-проверка (E6.4d-3/2) — p_args (P014), pa_stage (P017), call_stats (P016), astore_chk (P01D); аккумуляторы pc_argcnt/pc_argmax | 95 |
| `KERNEL/L2-WALL/wall_self_pc.wall` | часть каркаса: условие if/while (E6.4d-3/3) — p_cond (P018 стат-плечо: сравнения, '&&'/'||', maxd, v2flag) | 94 |
| `KERNEL/L2-WALL/wall_self_pd.wall` | часть каркаса: объявления + заголовки func прохода 1 (E6.4d-2/3..2/4) — p1_decl (S003): var/str/ext; p1_funchdr (S004) + fh_param (S00E): larr/bstk/ftab; окно дублей — local_find | 208 |
| `KERNEL/L2-WALL/wall_self_p1.wall` | часть каркаса: каркас прохода 1 (E6.4d-2/3..3/3) — p1_line (S002: func -> S004, fcur -> S006/S007/S008/S009/S00A/S00B/S00C/S00F/S00D), pass1 (S001) + пост-проверка main + сброс ifseq, set_lastline | 151 |
| `KERNEL/L2-WALL/wall_self_p1s.wall` | часть каркаса: утверждения прохода 1 (E6.4d-2/4..3/3) — p1s_var (S006), p1s_end (S007), p1s_if (S009), p1s_while (S00A), p1s_else (S008), p1s_brk (S00F), p1s_return (S00B), p1s_setb (S00C), p1_namestmt (S00D); ifarr — окно tabmem+4685888 | 262 |
| `KERNEL/L2-WALL/wall_self_blob.wall` | часть каркаса: ДАННЫЕ эмитции (E6.4d-4/3a) — блоб канона 2048 Б hex-литералами sd0..sd7 (8x512 симв. = 256 Б; таблица off/len в комментариях; ГЕНЕРАТОР LAB/ai/wall_self_data.py — не редактировать) | 142 |
| `KERNEL/L2-WALL/wall_self_e.wall` | часть каркаса: примитивы вывода и данных (E6.4d-4/3a, 3c-1) — blob_dec/init_blob (декодер блоба в sblob=outmem+0), out_ch/copy/str/line (курсор — глобаль outcur), out_hex/hex2/dec, lower_copy, get_ext (реинкарнации K2-E001..E008/E012/E025) + emit_cmt (E009), str_dlen (E013), str_emit+se_doline+esc_code (E014) | 280 |
| `KERNEL/L2-WALL/wall_self_d.wall` | часть каркаса: СЕКЦИИ ДАННЫХ (E6.4d-4/3c-1) — set_cmt (строка №ln -> cmt_ptr/cmt_len из smem), emit_strdata (E027: :имя + DZ 0 / DB-строки <= 16), emit_globdata (E028: :имя + DZ 8n + комментарий) | 92 |
| `KERNEL/L2-WALL/wall_self_g.wall` | часть каркаса: ЭМИТТЕРЫ ВЫРАЖЕНИЙ (E6.4d-4/3c-2/1) — emit_tstore/emit_tload (T-склад уровней: «M mov [rbp-X], r10» / «M mov r11, r10» + «M mov r10, [rbp-X]»), emit_alu (E020) + alu_tail, emit_shift (E021), emit_imul (E034), emit_divmod (E035), emit_addr (E022), emit_len (E023), emit_load (E024) — строки блоба по смещениям, nbase — глобаль st_p2nbase | 238 |
| `KERNEL/L2-WALL/wall_self_f.wall` | часть каркаса: КАДРЫ ФУНКЦИЙ (E6.4d-4/3b) — emit_kadr/emit_vyhod (E010), emit_lab (E011), calc_framesize (E017), emit_prologue (E018 — ARGREG[i] if-цепочкой), emit_epilogue (E019) | 121 |
| `KERNEL/L2-WALL/wall_self_y.wall` | часть каркаса: проход 2, срезы A+B+C-1+C-2/1 (E6.4d-4/3a..3c-2/1) — pass2 (Y001: пролог + цикл строк по smem + pc_mode=1 + СЕКЦИИ ДАННЫХ при непустых scount/vcount + предел nlab), emit_header/imports/entry (E015/E026/E016) + p2_line (Y002: cmt_ptr/cmt_len текущей строки), p2_funchdr (Y00A: + st_p2maxd/maxc/nbase + окно lay из ftab), p2s_var/end/if/while/else (эмитция функций + МЕХАНИКА bstk) и p2s_return (Y008: выражение p_expr(1) эмит-режимом + «M mov rax, r10» + эпилог) | 398 |
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
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул v1/v2 + инструмент + срезы + секция 11 + самохостинг (E6.4d-1..4/3c-1) | 500 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории | 141 |
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
| `LAB/py/lab_cpu.py` | эмулятор: регистры, флаги, поток, умножение/деление (#DE); ускорение 1.45x — E6.4d-3/3-1 | 447 |
| `LAB/py/lab_win.py` | загрузчик PE + заглушки kernel32 + вирт. ФС + куча (E6.4c; GlobalAlloc — E6.4d-2; 4 МиБ — E6.4d-2/2) | 304 |
| `LAB/py/lab_run.py` | прогон EXE с командной строкой | 30 |
| `LAB/py/lab_disasm.py` | дизассемблер (декод -> мнемоника) | 131 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход) | 429 |
| `LAB/py/lab_t_exe.py` | секции 7-8b батареи: инструменты enc/splice/brick (T-E6-05..11b, 12..18b, 36; пределы enc 2 МиБ (E6.4g-5) и brick 512 КиБ/2048 меток — E6.4f) | 348 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL v1+v2 (T-E6-19..24, 31..35) | 229 |
| `LAB/py/lab_t_wall2.py` | секция 10 батареи: инструмент wall.exe (T-E6-25..30 + T-E6-50 — предел меток выхода 2000, граница 2000/2001; E6.4d-3/3-1) | 166 |
| `LAB/py/lab_t_wall3.py` | секция 11 батареи: инструмент wall.exe — v2 срезы 1-3 + 4a/4b/5 + фикс №19 (T-E6-37..48, 51; big_source2, DEMO_NEST-круг) | 258 |
| `LAB/py/lab_t_wallself.py` | секция 12 батареи: каркас wall.wall (splice-корень) == оракулу + круг + CLI == wall.exe (19 путей) + проход 0+1 (ВСЕ статы тел прохода 1) == оракулу parse (T-E6-49a/b/c/d, корпус 180: 163 сравнимо / 58 код-0 / 17 вне класса — F17/F18 вошли автоматически, фикс №19) | 205 |
| `LAB/py/lab_t_wallself_corpus.py` | корпус секции 12: пул источников T-E6-49d (v1/v2/E1/E2 + микроканарейки E6.4d-2/3..3/2 + big 1/2; только ASCII) | 184 |
| `LAB/py/lab_t_wallself_model.py` | модель класса эквивалентности каркаса (E6.4d-3/2..3/3): _expect_line по строкам _lex — perr/cerr, стек блоков bstk (func/if/else/while), kw-патологии str/ext (_kw_falls) | 225 |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона) | 2542 |
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
| `LAB/ai/wall_self_data.py` | (частное) генератор wall_self_blob.wall: strblob wall_data.b2 (2046 Б) + 2 нуля -> 8 hex-литерал + таблица off/len (E6.4d-4/3a) | 101 |
| `LAB/ai/wall_self_emit.py` | (частное) dev-тест эмитции срезов A+B+C-1+C-2/1: сборка каркаса + матрица 26 источников (0..8 ext, 0..4 параметра, массивы, v1/v2, секции данных: пустая str, экраны, граница 16/17, длинная 42 Б, var-only, отступы/«;»-хвосты; return-выражения: все операции, унарный минус, globals, &адреса, len, K=5, вложенные смеси; вне-класс без краха) — выход == оракулу ЦЕЛИКОМ (E6.4d-4/3a..3c-2/1) | 260 |
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
- Тестов: **136** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..48 + T-E6-10b + T-E6-16b,
  T-E6-49a/b/c/d + T-E6-53 + T-E6-54 + T-E6-55; автоматических в
  батарее — 133).
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
  p1s_if + S00A p1s_while (условие p_cond P018 СТАТ-плечо — НОВАЯ
  часть wall_self_pc.wall: сравнения ==/!=/</<=/>/>=, конъюнкты
  '&&' / дизъюнкты '||' с v2flag, maxd = 1+max(need_l,need_r) на
  каждое сравнение; m-скан и guard-эмит — проход 2) + S008
  p1s_else (bstk kind 2 -> 3 + ifarr, мутация на месте) + S00F
  p1s_brk break/continue (скан bstk до while, v2flag); плечи
  диспетчера kw 5/6/7/C/D + сброс ifseq в pass1; ifarr — окно
  tabmem+4685888 32768 qword (ёмкость == wall.exe 0x8000), tabmem
  4685888 -> 4948032; корпус T-E6-49d 153 -> 178 (сравнимо 129 ->
  161, код-0 38 -> 56, вне класса 24 -> 17 — только cerr/quirk/
  kw-патологии str/ext); ПОЙМАН латентный дефект №19: wall.exe не
  разбирает вложенные вызовы в аргументах (оракул принимает) —
  каркас обходит (max2 порознь), починка wall.exe в очереди.
  Плоский каркас 2140 строк / 73634 Б, .b2 493526 Б (94% предела
  enc 512К — ГЛАВНЫЙ РИСК: проход 2 не поместится, сначала подъём
  enc до 1 МиБ либо WALL v3), .brick 463458, тело 43747/65536
  (67%), меток выхода 530/2000, меток исходника 530/2048, EXE
  44544 (см. `DOCS/03-ROADMAP.md`, журнал 19-27, VERIFY-E6D2.md).**
  **E6.4d-4/1 ВЫПОЛНЕН: предел входа enc 512 КиБ -> 1 МиБ** (мотив —
  тот самый ГЛАВНЫЙ РИСК): enc.b2 — 2 imm32 (вместимость/предел
  0x100000) + комментарии, enc_data.b2 — DBZ filebuf 0x80100 ->
  0x100100, outbuf 0x110040 -> 0x220080 (х2, как E6.4e/E6.4f);
  тело 0x2CCE и файл 12288 Б НЕ ИЗМЕНИЛИСЬ; !bss 0x193246 ->
  0x323286, vsize 0x195F14 -> 0x325F54, SHA 4BB73143… ->
  EEF6C66E…; пересборка оракулами (LAB/ai/enc_build_lim2.py —
  11/11: якоря 117, ошибки 27, границы 0x80020 принят / 0x100000
  отвергнут / максимум 0xFFFFF dev-only, самохостинг оба круга,
  регресс корней splice/wall байт-в-байт, демо-круг U-ENC-OK);
  T-E6-10b перепечатан (520К/1М, ~8,4 млн шагов — батарея 131/131
  ~90 с); .b2 каркаса теперь 47% предела enc. Спецификация
  SPEC/09 + реестры M1-ENC/M1-ENC-S/CARD/BYTECODE/VERIFY/T-L1-ENC
  синхронизированы.**
  **E6.4d-4/2 ВЫПОЛНЕН: дефект №19 закрыт полностью** — вложенные
  вызовы в аргументах и call-утверждения с выражениями: канон SPEC/11
  п.5/8 — БАЗЫ C-слотов (аргумент i вложенного вызова — C(base+i),
  base = base_объемлющего + его застейджено; maxc = max(base+n)),
  maxd call-утверждений = need (как присваивание); оракул
  lab_l2_lay/lab_l2_gen; wall.exe: P014 рамочные счётчики + pc_cact/
  pc_staged/pc_cbase (скаляры 18050/181F8/18078 — реюз мёртвых
  tok_kind/pc_d/tmp7), P017 эмит C(base+cnt+1), P015 загрузки с
  pc_cbase, P016 maxc с базой, P013a need из рамки, S00D maxd;
  каркас wall_self_pa/p1s/pp + wall.wall глобалы (локали рамки p_args);
  якоря F17/F18 + DEMO_NEST («U-NEST-OK 4C» — семантическая канарейка:
  старый оракул печатал «54»); T-E6-51 круг; корпус T-E6-49d
  178 -> 180 (F17/F18 автоматически, сравнимо 161 -> 163); батарея
  131 -> 132/132; wall.exe 27648 -> 28160 Б (тело +0x10C), SHA
  E04BA41B…; 59 старых исходников — байт-в-байт (совместимость);
  инструмент LAB/ai/bytecode_rows.py — перенос адресов BYTECODE.md §2
  (пойман дрейф карты от частичных обновлений прошлых сессий —
  устаревшие строки исправлены, полный аудит — очередь).**
  **E6.4g-1 ВЫПОЛНЕН: предел brick 512 КиБ -> 1 МиБ** (мотив:
  .brick каркаса с эмитцией 666962 Б = 127% старого): 2 imm32
  (вместимость/BIG SRC 0x100000) + 2 disp32 (imagebuf +0x80000) +
  DBZ filebuf 0x100008/imagebuf 0x100010; метки 2048/labtab не
  тронуты (613/2048); тело 0xB98/файл 0xE00 не изменились; bss
  0x208178, SHA AD3886E7… -> 86DADEF9…; dev brick_build_lim2.py
  11/11; T-E6-36 перепечатан; SPEC/08/CARD/BYTECODE/VERIFY/
  MAP-M1-BRICK синхронизированы.**
  **E6.4d-4/3a ВЫПОЛНЕН: проход 2 каркаса, срез A — ПРОЛОГ
  эмитции** (части wall_self_blob/e/y.wall): примитивы вывода
  (out_ch/copy/str/line, out_hex/hex2/dec — реинкарнации
  K2-E001..E008; курсор — глобаль outcur; out_str (off,len) блоба
  без strtab2; out_dec через / %), блоб канона 2048 Б hex-литералами
  sd0..sd7 (генератор LAB/ai/wall_self_data.py; кириллица >= 0x80
  невыразима в str-литерале), пролог pass2/emit_header/imports/
  entry (Y001-начало/E015/E026/E016); область вывода outmem
  2103264 (блоб+scr+outbuf 2 МиБ); куча эмулятора 8 -> 16 МиБ.
  Выход каркаса == ТОЧНЫЙ ПРЕФИКС оракула до строки int3 входа
  (T-E6-52 — 3 источника; dev wall_self_emit 7/7: 0/1/3/8 ext,
  v2, многозначные счётчики, пустая str); поймана конвенция
  ntab.ptr (смещение в srcbuf — не адрес). Батарея 132 -> 133/133.
  Замеры: каркас 2674 строк/95281 Б; .b2 700619 (67% enc); .brick
  666962 (64% brick 1 МиБ); тело 54348/64К (83%); метки 613/2048;
  EXE 55296. Риски срезов B+: .b2 ~95% enc 1 МиБ (подъём до 2 МиБ),
  тело ~64К (подъём предела тела ИЛИ WALL v3 qword-доступ).**
  **E6.4d-4/3b ВЫПОЛНЕН: проход 2 каркаса, срез B — ЭМИТЦИЯ
  ФУНКЦИЙ** (wall_self_y.wall: Y001-финал — цикл строк по smem +
  предел nlab 2000; Y002 p2_line — диспетчер kw формы wall.exe;
  Y00A p2_funchdr — имя -> ntab -> мета = fidx, пролог, push bstk;
  Y003 p2s_var / Y004 p2s_end (эпилог, если не last_ret) /
  Y008 p2s_return; Y005/Y006/Y007 — МЕХАНИКА bstk if/while/else;
  НОВАЯ часть wall_self_f.wall — кадры E010/E011/E017/E018/E019;
  глобали st_bcnt/st_fbase/st_infunc/st_lret/st_ifcnt/st_fptr/
  st_flen корня). Выход == оракулу байт-в-байт на классе «тела из
  var/голого return/end» — ЦЕЛИКОМ (без глобальных str/var) или
  префикс до секции данных (T-E6-52 — 3 источника; dev
  wall_self_emit 9/9: 0/1/4/8 ext, локальные массивы, v1/v2, 12
  функций, вне-класс код 0 без краха). Батарея 133/133. Замеры:
  каркас 3011 строк/107476 Б; .b2 775770 (73% enc 1 МиБ); .brick
  737556 (70% brick 1 МиБ); тело 60967/64К (93% — ГЛАВНЫЙ РИСК:
  подъём предела тела brick 64К -> 128К до среза C — E6.4g-2);
  метки 663/2000; EXE 61952. Срез C — статы/выражения + секции
  данных (E027/E028).**
  **E6.4g-2+E6.4g-3 ВЫПОЛНЕНЫ: ПОТОЛОК ТЕЛА КОМВЕЙЕРА 64 -> 128 КиБ
  СКВОЗНОЙ (brick И pegen)** (мотив: тело каркаса после среза B
  60967/64К = 93%, срез C добавит ~10-15 КБ; НАЙДЕН ПРОПУСК плана
  сессии 31 — поднимался только BIG OUT brick, а круг каркаса
  T-E6-49b идёт и через pegen: тело ~71-77 КБ упало бы ERR=BIG IMAGE
  код 6). brick: cmp eax 0x10000 -> 0x20000 (ровно 1 байт diff;
  imagebuf 0x100010 не тронут — привязан к пределу исходника 1 МиБ,
  тела 128 КиБ покрывает с запасом 8x; peg/bss/файл не изменились);
  SHA 86DADEF9… -> 79B50A01…; dev brick_build_lim3.py 11/11. pegen:
  imm32 вместимости 0x10001 -> 0x20001 + imm32 предела 0x10000 ->
  0x20000 + disp32 lea zeropad +0x10000 (imagebuf 0x10010 -> 0x20010
  сдвинул zeropad; ровно 3 байта diff + VirtualSize/SizeOfImage);
  !bss 20402 -> 30402, vsize 0x2117C -> 0x3117C; оракул lab_pegen
  синхронизирован; SHA 39B7D78C… -> FAECAC2E…; dev pegen_build_lim.py
  7/7 (вкл. регресс обёртки 9 модулей KERNEL). T-E6-36 расширен
  телами (0x10000/0x1FFFF приняты — старый предел отверг бы уже
  0x10000; 0x20000 — BIG OUT) + НОВЫЙ T-E6-53 (0x10001/0x20000
  приняты == оракулу wrap; 0x20001 — BIG IMAGE); батарея 133 ->
  134/134. Попутно исправлены устаревшие значения: CARD M1-BRICK
  (imagebuf 0x80010 -> 0x100010, labtab 0x4000/1023 -> 0x8000/2047
  — дрейф с E6.4g-1/E6.4f-2), BYTECODE M0-PEGEN (SizeOfImage 0x22000
  -> факт 0x23000, bss-старт 0xD80 -> 0xD7A).**
  **E6.4d-4/3c-1 ВЫПОЛНЕН: срез C часть 1 — СЕКЦИИ ДАННЫХ прохода 2
  каркаса** (срез C разбит: 1 — данные, 2 — выражения, 3 — guard-
  статы): emit_cmt/E009 + str_dlen/E013 + str_emit/E014+se_doline+
  esc_code (wall_self_e.wall; глобали cmt_ptr/cmt_len — аналог
  181A0/A8, буфер DB — локальный массив: класс дефекта №16 невозможен
  конструктивно) + НОВАЯ часть wall_self_d.wall (set_cmt,
  emit_strdata/E027, emit_globdata/E028); pass2 — заголовки секций
  только при непустой секции (как Y001 wall.exe); p2_line ставит
  cmt-глобали текущей строки. КЛАСС СРЕЗОВ A+B СТАЛ ДАВАТЬ ПОЛНЫЙ
  ВЫХОД ОРАКУЛА и при глобальных str/var (до C-1 — префикс до секции
  данных). T-E6-52 переведён на полный выход + НОВЫЙ T-E6-54 (6
  источников: пустая str, экраны 6 видов, граница DB 16/17, длинная
  42 Б, var-only, отступы/«;»-хвосты); батарея 134 -> 135/135; dev
  wall_self_emit 3/3 (13 источников ЦЕЛИКОМ). Замеры: каркас 3236
  строк/116261 Б; .b2 810157 (77% enc 1 МиБ); .brick 769916 (73%);
  тело 64561/128К (49%); метки 699/2000; EXE 65536. Следующий шаг —
  срез C часть 2: выражения в режиме эмитции (E020-E024/E034/E035,
  плечи P010..P018, Y008-выражение + Y00B).**
  **E6.4g-5 ВЫПОЛНЕН: предел ВХОДА enc 1 МиБ -> 2 МиБ** (мотив —
  .b2 каркаса 879662 Б = 84% предела: срезы C-2/2+ эмитции не
  поместятся; предписано журналом сессии 34 как первое действие
  перед C-2/2): enc.b2 — 2 imm32 (вместимость/предел 0x100000 ->
  0x200000) + комментарии; enc_data.b2 — DBZ filebuf 0x100100 ->
  0x200100, outbuf 0x220080 -> 0x440100 (запас 0x11725 от
  границы 0x42E9DB). Пересборка оракулами (НОВЫЙ dev
  LAB/ai/enc_build_lim3.py, 11/11): тело 0x2CCE и файл 12288 Б НЕ
  ИЗМЕНИЛИСЬ (6 байтов diff: 2 imm32 + 1 disp32 lea outbuf
  + 3 байта PE-заголовка); !bss 0x323286 -> 0x643306, vsize ->
  0x645FD4, SizeOfImage -> 0x647000; SHA EEF6C66E… -> B4B49041…;
  метки/импорты не тронуты. T-E6-10b перепечатан на границу 2 МиБ
  (520К принят / точный край 0x200000 отвергнут; 0x100020/0x1FFFFF —
  dev-only, 17-34 млн шагов; imm32 защищён пином SHA) — батарея
  136/136 (счёт не изменился). Попутно восстановлен лимит 500 строк:
  DOCS/03 (детали E6.1-E6.4b перенесены в DOCS/03a-HISTORY.md) и
  README (сжаты старые записи). Риск enc снят: .b2 каркаса 42%
  предела. Следующий шаг — срез C-2/2: выражения с вызовами и
  индексацией эмит-режимом (pa_stage/P017, p_call_tail/P015,
  эмит-плечи p_args/P014 + pp_prim0-вызов + getb + pp_pairs/P01C
  + p_prim/P013).**
  **E6.4g-6 ВЫПОЛНЕН: предел ВХОДА brick 1 МиБ -> 2 МиБ** (мотив —
  .brick каркаса 834018 Б = 80% предела: срезы C-2/2+ добавят
  ~60-100 КБ; предписано журналом сессии 35 при ~85% — паттерн
  E6.4g-5): brick_p1.brick — 2 imm32 (вместимость/BIG SRC 0x100000
  -> 0x200000), brick_p3.brick — DBZ filebuf 0x100008 -> 0x200008,
  imagebuf 0x100010 -> 0x200010. Пересборка оракулами (НОВЫЙ dev
  LAB/ai/brick_build_lim4.py, 11/11): тело 0xB98 и файл 3584 Б НЕ
  ИЗМЕНИЛИСЬ (ровно 4 слова diff: 2 imm32 + 2 disp32 lea imagebuf);
  !bss 0x208178 -> 0x408178, vsize -> 0x408D10, SizeOfImage ->
  0x40A000; SHA 79B50A01… -> 38E46B52…; метки 2048/labtab не тронуты
  (848 меток каркаса = 41%). T-E6-36 перепечатан на край 2 МиБ
  (512К+20 принят / 0x200000 отвергнут; 0x100020/0x1FFFFF — dev-only,
  15-29 млн шагов; imm32 защищён пином SHA) — батарея 136/136 (счёт
  не изменился). Риск .brick снят: .brick каркаса 40% предела.
  Следующий шаг — срез C-2/2: выражения с вызовами и индексацией
  эмит-режимом.**
