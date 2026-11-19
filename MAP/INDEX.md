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
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач (+ядро kernel.exe — E7.2-1..4; №23 закрыт E7.2-2F) | 115 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности (приведён ≤ 500 строк — сессия 51) | 487 |
| `DOCS/03a-HISTORY.md` | детальная история выполненных этапов E0..E6.4 (раздел 03a/03b при превышении 500 строк — сессия 51) | 320 |
| `DOCS/03b-HISTORY-E7.md` | детальная история этапа 7 — UNIVM/ассемблер (E7.1..E7.3-2; выделен из 03a при превышении лимита — сессия 51, прецедент VERIFY-E6D*.md) | 278 |
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
| `SPEC/12-UNIVM-ISA.md` | UNIVM ISA v0: виртуальный процессор — модель, форматы, 18 инструкций, ловушки, окно устройств (E7.1) | 214 |
| `SPEC/13-UP-FORMAT.md` | контейнер .UP v1: заголовок 24 Б + код, пределы, отказы (E7.1) | 83 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 408 |
| `MAP/METHODS.md` | указатель реестра кирпичей (одна строка на кирпич; +21 K3-* — E7.3-1..2) | 457 |
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
| `MAP/M3-UNIVM.md` | карточки кирпичей M3-UNIVM — ветви C/U/M/J/X (18; срезы E7.2-1..4, этап 7.2 закрыт; ветвь V — в M3-UNIVM-V.md по лимиту 500, прецедент M1-ENC-E/S) | 309 |
| `MAP/M3-UNIVM-V.md` | карточки кирпичей M3-UNIVM — ветвь V (интерпретатор, 14) | 225 |
| `MAP/M3-UVA.md` | карточки кирпичей M3-UVA — ассемблер .uva -> .UP (21: ветви C/T/L/E/W/X; срезы E7.3-1..2) | 341 |
| `MAP/LAYERS.md` | реестр слоёв L0..L6 и их статусы | 44 |

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
| `KERNEL/L2-WALL/CARD.md` | карточка модуля M2-WALL (компилятор WALL v1/v2) | 208 |
| `KERNEL/L2-WALL/wall.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E6.4d-5/3-2; E7.2-2F): выход wall.exe(wall.wall), плоский, 1011099 Б — T-E6-49a | — |
| `KERNEL/L2-WALL/wall.wall` | само-исходник на WALL v2 — КОРЕНЬ с разрезом SPEC/10 (E6.4d-2/3..4/3c-3): ext/var/str + main + 18 частей; CLI == wall.exe, чтение, GlobalAlloc, проходы 0/1 + проход 2 (срезы A..C-3) | 338 |
| `KERNEL/L2-WALL/wall_self_c.wall` | часть каркаса: сервис — print_error/skip0/read_arg/widen (E6.4d-1) | 147 |
| `KERNEL/L2-WALL/wall_self_n.wall` | часть каркаса: проход 0 на WALL (E6.4d-2/2) — stq, fail_format, lex_line, pass0; карта текстов smem | 262 |
| `KERNEL/L2-WALL/wall_self_pe.wall` | часть каркаса: хелперы прохода 1 (E6.4d-2/3..3/2) — getq, tok_next, kw_lookup, chk_name, names_find/_ci/add, local_find (P008), max2/tok_is1 (экономия меток), arr_size, at_end/want_id/want_sym1; таблицы tabmem | 434 |
| `KERNEL/L2-WALL/wall_self_ph.wall` | часть каркаса: уровни выражений стат-режимом (E6.4d-3/2) — p_expr (P010), p_mul (P011), p_mdm (P01A), p_unary (P012); курсор pcur/ple | 77 |
| `KERNEL/L2-WALL/wall_self_pp.wall` | часть каркаса: первичные + индексация (E6.4d-3/2; эмит-плечи E6.4d-4/3c-2/1..2/2) — p_prim (P013: откат outcur + перепознание базы d+k), pp_prim0 (P013a: число/скобки/&имя/getb/len/вызов/имя), pp_pcount (P01B; фикс №23 E7.2-2F: двухсимвольный оператор глубины 0 — завершитель скана), pp_pairs (P01C: статы + эмит T-склад/хвост), pp_strchk (P01E) | 302 |
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
| `KERNEL/L2-WALL/wall.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(wall.b2), 958213 Б — T-E6-49b | — |
| `KERNEL/L2-WALL/wall.peg` | обёртка — КОНСТАНТА SPEC/11 п.6 (!module wall; вход 1200, idata 1000 28, iat 1028 48; E6.4d-5/3-2) | 9 |
| `KERNEL/L2-WALL/wall.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+wall.peg — 87040 Б, вход 0x1200, импорты-восьмёрка (CreateFile2+GlobalAlloc); SHA-256 B2AC45F4… (E7.2-2F) — T-E6-49b | — |
| `KERNEL/L2-WALL/BYTECODE.md` | карта самосборного образа: сводка, 117 функций (RVA), данные, воспроизведение (E6.4d-5/3-2) | 248 |
| `KERNEL/L2-WALL/VERIFY.md` | проверка, журнал 18 закрытых дефектов (№23 закрыт E7.2-2F; §1 актуализирован; + срезы 1-3, E6.4d-1..2/1) | 494 |
| `KERNEL/L2-WALL/VERIFY-E6D.md` | журнал верификации самохостинга E6.4d-2/2..3/1 (VERIFY.md у лимита 500) | 481 |
| `KERNEL/L2-WALL/VERIFY-E6D2.md` | журнал верификации самохостинга E6.4d-3/2+ (продолжение; VERIFY-E6D.md у лимита 500) | 224 |
| `KERNEL/L2-WALL/VERIFY-E6D3.md` | журнал верификации самохостинга E6.4d-4/2..4/3c-1 | 117 |
| `KERNEL/L2-WALL/VERIFY-E6D4.md` | журнал верификации самохостинга E6.4d-4/3b..3c-3 | 497 |
| `KERNEL/L2-WALL/VERIFY-E6D5.md` | журнал ФИНАЛА E6.4d: фикс-пункт самосборки + замена артефактов (E6.4d-5/3-1..2) | 113 |

### KERNEL/L3-UNIVM — ядро виртуальной машины (E7.2-4 — этап 7.2 закрыт)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L3-UNIVM/CARD.md` | карточка модуля M3-UNIVM (ядро UNIVM: срезы E7.2-1..4 — каркас + регистры/ALU + память/устройства + переходы/предел шагов; все 18 опкодов, DoD этапа) | 104 |
| `KERNEL/L3-UNIVM/kernel.wall` | корень ядра с разрезом (SPEC/10): 8 ext, 17 var (вкл. regs[16] — регистры UNIVM, ram — RAM, steplim — предел шагов), 13 str, main (CLI -> чтение -> разбор -> исполнение) | 99 |
| `KERNEL/L3-UNIVM/kernel_self_c.wall` | часть ядра: сервис — print_error, skip0, read_arg, check_end (не более двух аргументов), widen, read_lim (предел шагов — 2-й аргумент CLI, E7.2-4) | 232 |
| `KERNEL/L3-UNIVM/kernel_self_up.wall` | часть ядра: контейнер — rd32 (LE u32), read_up (чтение + разбор SPEC/13, порядок отказов == оракул parse_up; E7.2-3: + RAM через get_ram после всех отказов) | 85 |
| `KERNEL/L3-UNIVM/kernel_self_mem.wall` | часть ядра: память и устройства (E7.2-3) — get_ram (RAM: GlobalAlloc + обнуление), op_ldb/op_stb/op_ldq/op_stq (4 кирпича опкодов памяти: RAM/окно/консоль/ловушки 3-4, ветвь M) | 222 |
| `KERNEL/L3-UNIVM/kernel_self_j.wall` | часть ядра: переходы (E7.2-4) — op_jmp/op_jnz (2 кирпича опкодов 10..11, F3, imm32 беззнаковое; ветвь J) | 54 |
| `KERNEL/L3-UNIVM/kernel_self_vm.wall` | часть ядра: интерпретатор — interp (цикл: предел шагов (trap 6) ДО выборки + порядок проверок SPEC/12 п. 7, диспетчер всех 18 опкодов вкл. память 0C..0F и переходы 10..11), op_const..op_eq (11 ALU-кирпичей, regs[16]; E7.2-2F: скобки-обход №23 в op_eq сняты), op_halt, fail_trap (TRAP/STEPS), copy_str, out_dec | 452 |
| `KERNEL/L3-UNIVM/kernel.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E7.2-4): wall.exe(kernel.wall), плоский, 201650 Б — T-E7-09 | — |
| `KERNEL/L3-UNIVM/kernel.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(kernel.b2), 187634 Б — T-E7-09 | — |
| `KERNEL/L3-UNIVM/kernel.peg` | обёртка — константа SPEC/11 п.6 (!module kernel; вход 1200, idata 1000 28, iat 1028 48) | 9 |
| `KERNEL/L3-UNIVM/kernel.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+kernel.peg — 23040 Б, вход 0x1200, импорты-восьмёрка; SHA-256 8AFF54B8… — T-E7-09 | — |
| `KERNEL/L3-UNIVM/BYTECODE.md` | карта образа ядра: сводка, 32 функции (RVA), данные (вкл. regs[16], ram, steplim), воспроизведение | 96 |
| `KERNEL/L3-UNIVM/VERIFY.md` | подлинность + уровни проверки + журнал срезов (E7.2-4; этап 7.2 закрыт) | 90 |

### KERNEL/L3-UVA — ассемблер UNIVM (E7.3 — срезы 1-2)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L3-UVA/CARD.md` | карточка модуля M3-UVA (ассемблер .uva -> .UP: срезы E7.3-1..2 — каркас CLI + строки/токены/числа + .mem + halt + таблица 18 мнемоник + регистры r0..r15 + кодировка F1; диффтест == ассемблеру оракула) | 126 |
| `KERNEL/L3-UVA/uva.wall` | корень ассемблера с разрезом (SPEC/10): 8 ext, 20 var (вкл. tstart/tend[12] — таблица токенов), 14 str (вкл. s_mn — таблица 18 мнемоник), main (CLI -> чтение -> pass1 -> pass2 -> заголовок -> запись) | 134 |
| `KERNEL/L3-UVA/uva_self_c.wall` | часть ассемблера: сервис — print_error, skip0, read_arg, check_end (ровно два аргумента), widen, fail_at (ERR=FORMAT AT=hex4, код 6) | 201 |
| `KERNEL/L3-UVA/uva_self_t.wall` | часть ассемблера: лексика — tok_is, tokenize (разделители как _toks), parse_num (imm32, переполнение в цикле), line_trim (комментарий + края), line_next (итератор строк по LF — как split оракула), mn_find (K3-T006: таблица 18 мнемоник — индекс i => опкод i+1), parse_reg (K3-T007: r0..r15) | 301 |
| `KERNEL/L3-UVA/uva_self_l.wall` | часть ассемблера: проход 1 — pass1 (структура: .mem/все 18 мнемоник/длины F1 = 3, F2/F3 = 6; «нет .mem» — строка 1; pc = длина кода; идиома чтения ВПЕРЁД) | 75 |
| `KERNEL/L3-UVA/uva_self_e.wall` | часть ассемблера: проход 2 — pass2 (диспетчер: F1 — enc_f1, halt — счёт операндов/число; F2/jmp/jnz — ERR=FORMAT, срезы 3-4) + enc_halt (12 00 imm32 LE) + enc_f1 (K3-E003: mov/9 АЛУ, счёт потом регистры по порядку) | 104 |
| `KERNEL/L3-UVA/uva_self_w.wall` | часть ассемблера: контейнер — put32 (LE u32), make_header (24 Б SPEC/13 п. 2), write_out (CREATE_ALWAYS + один WriteFile) | 59 |
| `KERNEL/L3-UVA/uva.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E7.3-2): wall.exe(uva.wall), плоский, 138586 Б — T-E7-19 | — |
| `KERNEL/L3-UVA/uva.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(uva.b2), 129156 Б — T-E7-19 | — |
| `KERNEL/L3-UVA/uva.peg` | обёртка — константа SPEC/11 п.6 (!module uva; вход 1200, idata 1000 28, iat 1028 48) | 9 |
| `KERNEL/L3-UVA/uva.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+uva.peg — 17920 Б, вход 0x1200, импорты-восьмёрка; SHA-256 83F76ED9… — T-E7-19 | — |
| `KERNEL/L3-UVA/BYTECODE.md` | карта образа ассемблера: сводка, 21 функция (RVA), данные, инварианты | 92 |
| `KERNEL/L3-UVA/VERIFY.md` | подлинность + уровни проверки + журнал срезов (E7.3-1..2; дефект оракула №24 закрыт) | 95 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов | 28 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов | 176 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 109 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 104 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-17 | 131 |
| `TESTS/T-L1-BRICK.md` | тест-план brick T-M6-01..T-M6-17, T-E6-36 | 153 |
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11b (E6.2; рост ISA E6.4c; предел 256 КиБ E6.4e-1) | 120 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18, T-E6-16b (E6.3, E6.4e-2) | 97 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул v1/v2 + инструмент + срезы + секция 11 + самохостинг (E6.4d-5/1..2, T-E6-59/60) + фикс №23 (E7.2-2F, T-E6-61) | 482 |
| `TESTS/T-L3-UNIVM.md` | тест-план UNIVM: оракул T-E7-01..08 (E7.1) + ядро kernel.exe T-E7-09..18 (E7.2-1..4; DoD: полный корпус) | 150 |
| `TESTS/T-L3-UVA.md` | тест-план ассемблера uva.exe T-E7-19..24 (E7.3-1: фикс-пункт/CLI/диффтест с оракулом/отвержение/CODE0/сквозной круг) | 116 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории | 210 |
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
| `LAB/py/lab_vm.py` | оракул UNIVM v0 (SPEC/12 + SPEC/13): исполнитель (регистры/память/консоль/ловушки/шаги) + мини-ассемблер (метки, .mem) — E7.1 | 455 |
| `LAB/py/lab_t_vm.py` | секция 13 батареи: оракул UNIVM — T-E7-01..08 (якоря 18 опкодов, отвержения, демо 142 шага, ловушки, детерминизм, ops, устройства) | 320 |
| `LAB/py/lab_t_kernel.py` | секция 14 батареи: ядро kernel.exe — T-E7-09..18 (фикс-пункт артефактов, CLI/контейнер+предел шагов, диффтест halt/ловушки/ALU/память/переходы/предел — E7.2-1..4; корпуса — lab_t_kernel_corpus.py) | 303 |
| `LAB/py/lab_t_kernel_corpus.py` | корпуса программ диффтеста ядра (только данные: ALU срез 2, память срез 3, переходы+предел срез 4; прогонщик — lab_t_kernel.py; выделен по лимиту 500 строк) | 343 |
| `LAB/py/lab_t_uva.py` | секция 15 батареи: ассемблер uva.exe — T-E7-19..24 (фикс-пункт артефактов, CLI/предел входа, диффтест == assemble оракула: срезы 1-2 — halt-корпус + F1-корпус, отвержение с номерами строк, CODE0, круг uva -> kernel.exe) | 304 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход; 169 проверок — с E7.3-2) | 493 |
| `LAB/py/lab_t_exe.py` | секции 7-8b батареи: инструменты enc/splice/brick (T-E6-05..11b, 12..18b, 36; пределы enc 2 МиБ (E6.4g-5) и brick 512 КиБ/2048 меток — E6.4f) | 353 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL v1+v2 (T-E6-19..24, 31..35) | 229 |
| `LAB/py/lab_t_wall2.py` | секция 10 батареи: инструмент wall.exe (T-E6-25..30 + T-E6-50 — предел меток выхода 2000, граница 2000/2001; E6.4d-3/3-1) | 170 |
| `LAB/py/lab_t_wall3.py` | секция 11 батареи: инструмент wall.exe — v2 срезы 1-3 + 4a/4b/5 + фикс №19 (T-E6-37..48, 51; big_source2, DEMO_NEST-круг) + якоря фикса №23 (T-E6-61) | 312 |
| `LAB/py/lab_t_wallself.py` | секция 12 батареи: каркас wall.wall (splice-корень) == оракулу + круг + CLI == wall.exe (19 путей) + проход 0+1 == оракулу parse (T-E6-49a/b/c/d) + эмитция пролога/функций/данных (T-E6-52/54) + выражения (T-E6-55) + вызовы/getb/индексация (T-E6-56) + статы-имена (T-E6-57) + guard-группа (T-E6-58) | 500 |
| `LAB/py/lab_t_wallself_final.py` | секция 12b батареи: финал E6.4d-5 шаг 1 — канарейки круга, 6 DEMO-программ компилируются КАРКАСОМ, полный круг до эмуляции (T-E6-59) | 86 |
| `LAB/py/lab_t_wallself_emit_cases.py` | источники тестов эмитции T-E6-55/56/57 (срезы C-2/1..2/3; только данные — прогонщик lab_t_wallself.py; выделен по лимиту 500 строк) | 123 |
| `LAB/py/lab_t_wallself_corpus.py` | корпус секции 12: пул источников T-E6-49d (v1/v2/E1/E2 + микроканарейки E6.4d-2/3..3/2 + big 1/2; только ASCII) | 184 |
| `LAB/py/lab_t_wallself_model.py` | модель класса эквивалентности каркаса (E6.4d-3/2..3/3): _expect_line по строкам _lex — perr/cerr, стек блоков bstk (func/if/else/while), kw-патологии str/ext (_kw_falls) | 225 |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона) | 4263 |
| `LAB/ai/kernel_test.py` | (частное) построитель M3-UNIVM: kernel.wall -> артефакты (конвейер — эмуляция) + корпус срезов 1-2 с отчётом (E7.2-2) | 100 |
| `LAB/ai/wall_ppc_probe.py` | (частное) матрица-зонд дефекта №23 wall.exe (pp_pcount, 17 сниппетов: оракул vs wall.exe; ЗАКРЫТ E7.2-2F — 0 расхождений; регресс-зонд) | 84 |
| `LAB/ai/kernel_labelmap.py` | (частное) карта меток kernel.brick (RVA) — обновление BYTECODE.md (E7.2-1) | 33 |
| `LAB/ai/uva_test.py` | (частное) построитель M3-UVA: uva.wall -> артефакты (конвейер — эмуляция) + карта меток + корпус среза 1 с отчётом (E7.3-1) | 108 |
| `LAB/ai/uva_syntax_check.py` | (частное) быстрая проверка uva.wall: splice + компиляция оракулом WALL без эмуляции (E7.3-1) | 47 |
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
| `LAB/ai/wall_self_canary.py` | (частное) ПРИЁМОЧНАЯ финала E6.4d-5 шаги 1-2: канарейки круга (6 DEMO-программ КАРКАСОМ, полный круг до эмуляции) + big_source/big_source2 == оракулу каркасом (T-E6-60; ~234 млн шагов) | 181 |
| `LAB/ai/wall_self_diff.py` | (частное) ПРИЁМОЧНАЯ E6.4d-5/3 шаг 1: ФИКСПУНКТ самосборки (s1.exe(wall.wall) == s1.b2 байт-в-байт, ~548 млн шагов — прямой lab_win.Machine.run(max_steps=2 млрд); кэш круга в /tmp/wall_self_diff) + diff-анализ порядка функций vs канон wall.b2 (общие/LCS/инверсии/предложение перестановки; сессия 42) | 366 |
| `LAB/ai/cpu_fuzz.py` | (частное) диффтест эмулятора: замыкания lab_thread против универсального _op_* на случайных программах (7x500, lockstep 150/зерно, перекрывающиеся регионы, вкл. сообщения об ошибках; E6.4d-5/0) | 328 |
| `LAB/ai/wall_self_data.py` | (частное) ИСТОРИЧЕСКИЙ генератор wall_self_blob.wall (источник wall_data.b2 удалён E6.4d-5/3-2 — git-история; блоб уже вшит в каркас) | 101 |
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

- Кирпичей в реестре: **314** (слой L0: 8 в M0-SEED, 19 в M0-SEED2,
  23 в M0-HXDUMP, 29 в M0-HEXGEN, 37 в M0-PEGEN; слой L1: 42 в M1-BRICK,
  64 в M1-ENC (+E033 enc_imul, E6.4c), 27 в M1-SPLICE; слой L2: 79 в
  M2-WALL — +P01A/E034/E035 E6.4c-3/1, +S00F/Y00C E6.4c-3/2,
  +E036/E037/E038 E6.4c-3/3, +P019 arr_size E6.4c-3/4a,
  +P01B/P01C/P01D/P01E индексация E6.4c-3/4b; слой L3: 32 в M3-UNIVM —
  ветви C/U/M/J/V/X, срезы E7.2-1..4: +K3-V101..V111 ALU,
  +K3-M001/K3-M101..M104 память E7.2-3, +K3-J101..J102 переходы и
  +K3-C008 read_lim (предел шагов) E7.2-4; +21 в M3-UVA — ассемблер
  E7.3-1..2 (+T006 mn_find, +T007 parse_reg, +E003 enc_f1 — срез 2),
  ветви C/T/L/E/W/X; полная ревизия счётчиков
  всех модулей — очередь мелочей).
- Модулей: **11** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE, M2-WALL, M3-UNIVM, M3-UVA).
- Тестов: **166** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..48 + T-E6-10b + T-E6-16b,
  T-E6-49a/b/c/d + T-E6-53..60, T-E6-61 — E7.2-2F, T-E7-01..08 — E7.1,
  T-E7-09..14 — E7.2-1, T-E7-15 — E7.2-2, T-E7-16 — E7.2-3,
  T-E7-17..18 — E7.2-4, T-E7-19..24 — E7.3-1..2; автоматических в батарее —
  169).
- Этап: **E7.3-2 ВЫПОЛНЕН (сессия 51) — ассемблер uva.exe: таблица
  всех 18 мнемоник + регистры + F1.** 3 новых кирпича (модуль — 21):
  K3-T006 mn_find (таблица s_mn — 18 имён через пробел в порядке
  опкодов 01..12: индекс i => опкод i+1 — последовательность опкодов
  делает параллельные таблицы ненужными; одна строка данных вместо
  массивов), K3-T007 parse_reg (r0..r9 — 2 символа; r10..r15 — 3
  со второй цифрой 1 — как _reg оракула; r01/r16/R1/r0x/r-1 — не
  регистры), K3-E003 enc_f1 (F1: счёт операндов, потом регистры по
  порядку rd/ra/rb — как _enc_f1 оракула; mov — rb = 0; байты
  [op] [rd*16+ra] [rb]). Проход 1 — все 18 мнемоник (pc += 3 F1 /
  6 F2/F3), порядок проверок оракула сохранён (неизвестная
  мнемоника РАНЬШЕ «нет .mem»). s_halt удалена (mn_find покрывает).
  Корпуса: 17 → 29 успехов (+12 F1), 21 → 39 отвержений (+18 F1);
  T-E7-24 + 1 круг (mov+add → код 7); число проверок батареи — то же
  169/169 (растут корпуса внутри T-E7-21/22). Артефакты: uva.exe
  15360 → 17920 Б (тело 14681 → 17293, метки 240 → 275, функций 18 →
  21); сборка ~64,8 млн шагов; uva.b2 == оракулу WALL. Дефектов не
  найдено — корпуса зелёные с первого прогона. Далее — E7.3-3 (F2:
  const + память, операнды rA+смещ); план — DOCS/03-ROADMAP этап 7.
- Предыдущий: **E7.3-1 ВЫПОЛНЕН (сессия 50) — ассемблер uva.exe (M3-UVA):
  срез 1 — каркас.** Новый модуль KERNEL/L3-UVA (второй модуль L3,
  сериал кирпичей 011; 18 кирпичей K3-C011..X011, ветви C/T/L/E/W/X):
  CLI на два аргумента, чтение исходника (BIG SRC > 65536), разбор
  строк/токенов/чисел, директива .mem и инструкция halt; метки и
  остальные 17 мнемоник — срезы E7.3-2+. Диффтест: 17 успехов +
  21 отвержение + 3 CODE0; сквозной круг uva -> kernel.exe. НАЙДЕН И
  ЗАКРЫТ дефект оракула №24 (строка из одних разделителей — крах
  IndexError); найден и исправлен дефект собственной идиомы итератора
  (последняя строка без LF кодировалась дважды — чтение ВПЕРЁД).
  Артефакты: uva.exe 15360 Б; сборка ~52,5 млн шагов. Батарея
  161 → 169/169. Подробно — DOCS/03b-HISTORY-E7 (E7.3-1).
- Предыдущий: **E7.2-4 ВЫПОЛНЕН (сессия 49) — переходы + предел шагов;
  ЭТАП 7.2 ЗАКРЫТ (DoD: ядро kernel.exe == оракулу на полном корпусе,
  все 18 опкодов ISA v0).** Ветвь J (kernel_self_j.wall): K3-J101
  op_jmp + K3-J102 op_jnz (F3, imm32 беззнаковое; цель не проверяется
  в кирпиче — ловушка 2 на следующей итерации); предел шагов —
  глобаль steplim + K3-C008 read_lim (2-й аргумент CLI, 0..2147483647,
  умолчание 200 млн), проверка «steps >= steplim → trap 6» ДО выборки
  pc. Корпуса T-E7-17 (9) + T-E7-18 (8) зелёные с первого прогона;
  T-E7-10 расширен (4 → 12); артефакты 21504 → 23040 Б (тело 20570 →
  22244); батарея 159 → 161/161. Рефакторинг: корпуса диффтеста —
  lab_t_kernel_corpus.py (данные).
- Предыдущий: **E7.2-2F ВЫПОЛНЕН (сессия 47) — фикс дефекта №23 wall.exe
  (pp_pcount).** Двухсимвольный оператор глубины 0 — завершитель
  скана пар [..] в wall_self_pp.wall (+11 строк); артефакты wall
  пересобраны конвейером фикс-пункта (548 707 240 шагов, s2.b2 ==
  wall.b2 байт-в-байт; тело 86185 → 86307); зонд wall_ppc_probe.py —
  0/17 расхождений (до фикса — 8); якорь T-E6-61 (секция 11);
  скобки-обход в op_eq ядра сняты (kernel.exe байт-в-байт тот же).
  Батарея 157 → 158/158. Далее — E7.2-3 (память + устройства);
  план срезов — DOCS/03-ROADMAP этап 7.
- Предыдущий: **E7.2-2 ВЫПОЛНЕН (сессия 46) — ядро kernel.exe
  (M3-UNIVM): регистры + ALU.** 11 кирпичей K3-V101..V111 (const/mov/add/sub/and/
  or/xor/shl/shr/lt/eq — по кирпичу на опкод; массив regs[16], r0
  равноправен); interp: проверка длины для всех валидных опкодов
  01..12 (обрезка — ловушка 2 ДО заглушки, как оракул). Корпус
  T-E7-15 (17 случаев: поля/обрезки вкл. заглушки/точные счётчики
  шагов/отсутствие ложных ловушек) — зелёный с первого прогона;
  артефакты пересобраны (10240 → 16384 Б, тело 15384); ядро ==
  оракулу на всём корпусе. Попутно НАЙДЕН дефект №23 wall.exe
  (pp_pcount — двухсимвольные операторы не завершают скан пар
  индексации: «индекс == индекс» — ложный ERR=FORMAT; обход — скобки
  в op_eq, фикс — отдельный срез; журнал — KERNEL/L2-WALL/VERIFY.md
  §4). Батарея 156 → 157/157.
- История E6.4d (ВЫПОЛНЕН, сессия 43): самохостинг замкнут —
  артефакты wall.b2/wall.brick/wall.exe := самосборная сборка из
  wall.wall (фикс-пункт 548 385 615 шагов — T-E6-49a/49b на каждом
  пуше; протокол — VERIFY-E6D5.md); wall.peg — константа SPEC/11 п.6;
  20 частей wall_*.b2 удалены; канарейки 9/9. Рост по срезам:
  E6.4d-1 каркас CLI (дефект №16), -2/1..4 проходы 0-1 (таблицы
  GlobalAlloc), -3/1..3 статы (дефекты №18/№19), -4/1..4/3c-3 эмитция
  прохода 2 (блоб канона, кадры, данные, выражения, статы, guard;
  дефекты №20-№22), -5/0 ускорение lab_cpu ~2x, -5/1..2 канарейки
  круга, -5/3-1 фикс-пункт, -5/3-2 замена артефактов. Подробности —
  DOCS/03-ROADMAP, DOCS/03a-HISTORY, LAB/ai/JOURNAL (сессии 19-43),
  KERNEL/L2-WALL/VERIFY-E6D*.md.
- Прочее закрытое: E0-E6.4c (семя..конвейер, WALL v1/v2 + инструменты
  wall/enc/splice/brick — самохостинг), E6.4e/f/g (пределы конвейера:
  вход enc/brick 2 МиБ, тела 128 КиБ, метки 2048, вход wall 256 КиБ).
  Полная история — DOCS/03-ROADMAP «Выполнено» + DOCS/03a-HISTORY.md
  (E0..E6.4) + DOCS/03b-HISTORY-E7.md (этап 7).