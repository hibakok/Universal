# Карта репозитория (входная точка навигации)

Паспорт файла: MAP/INDEX.md | слой: все | роль: карта всех файлов репозитория.

**Правило:** любой исполнитель (ИИ или человек) начинает работу отсюда.
Для задачи читается только карта -> карточка модуля -> указанные файлы
(см. `DOCS/02-AI-NAVIGATION.md`).

## DOCS/ — идеи и регламенты

| Файл | Роль | Строк |
|---|---|---|
| `DOCS/00-MANIFEST.md` | миссия, требования, границы проекта | 57 |
| `DOCS/01-METHODOLOGY.md` | кирпичи, ветви, слои, 10 правил | 94 |
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач (+ядро kernel.exe — E7.2; ассемблер uva.exe — E7.3 закрыт; ISA v1/.UP v2 — E7.4-1; контейнер v2 в ядре — E7.4-2a; ALU v1 — E7.4-2b; call/ret + стек вызовов — E7.4-2c; мнемоники v1 в uva — E7.4-3a; .data/.UP v2 в uva/батарея 180 — E7.4-3b; ПРИЁМКА DoD ЭТАПА 7.4 — E7.4-4; строки L4 — E8.1) | 123 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности (срезы этапа 7 — указателями в 03b; E7.4-1..4 [x] — ЭТАП 7.4 ЗАКРЫТ — сессия 60; ЭТАП 8: E8.1 [x] + E8.2a [x] — ветвь C — сессия 62; E8.2b..d/E8.3 — план) | 500 |
| `DOCS/03a-HISTORY.md` | детальная история выполненных этапов E0..E6.4 (раздел 03a/03b при превышении 500 строк — сессия 51) | 320 |
| `DOCS/03b-HISTORY-E7.md` | детальная история этапа 7 — UNIVM/ассемблер (E7.1..E7.4 ЗАКРЫТЫ; E7.4-1 — оракул; E7.4-2a/b/c — ядро (записи сжаты в указатели на VERIFY ядра — сессия 58); E7.4-3a — мнемоники v1, сессия 58; E7.4-3b — .data/.UP v2, сессия 59; E7.4-4 — ПРИЁМКА DoD — ЭТАП 7.4 ЗАКРЫТ, сессия 60) | 492 |
| `DOCS/03c-HISTORY-E8.md` | детальная история этапа 8 — Библиотека L4 (E8.1 — SPEC/14 + оракул + секция 16, сессия 61; E8.2a — ветвь C: lib_c.uva + CARD.md + диффтесты + круг инструментами, сессия 62) | 181 |
| `DOCS/04-RULES-OF-CHANGE.md` | регламент изменений и коммитов | 59 |

## SPEC/ — формальные спецификации

| Файл | Роль | Строк |
|---|---|---|
| `SPEC/00-GLOSSARY.md` | словарь терминов, регистры | 49 |
| `SPEC/01-METHOD-CARD.md` | формат карточки кирпича | 57 |
| `SPEC/02-LAYER0-SPEC.md` | правила слоя L0, верификация | 57 |
| `SPEC/03-ATOM-FORMAT.md` | грамматика формата ATOM v1 | 81 |
| `SPEC/04-PE-MINIMAL.md` | структура наших EXE, инварианты | 138 |
| `SPEC/05-X86-SUBSET.md` | реестр инструкций и кодировок | 256 |
| `SPEC/06-ARCHITECTURE.md` | целевая архитектура системы | 72 |
| `SPEC/07-PEG-FORMAT.md` | формат PEG v1 и поведение pegen | 113 |
| `SPEC/08-BRICK-FORMAT.md` | формат BRICK v1 и поведение brick (слой L1; пределы 512 КиБ/2048 меток — E6.4f-2) | 160 |
| `SPEC/09-ENC-FORMAT.md` | BRICK v2: M-строки, канонические кодировки, контракт enc (предел входа 2 МиБ — E6.4g-5) | 254 |
| `SPEC/10-SPLICE-FORMAT.md` | SPLICE v1: !include, склейка исходников, контракт splice (пределы 256 КиБ, E6.4e-2) | 148 |
| `SPEC/11-WALL-FORMAT.md` | WALL v1/v2: язык слоя L2, компиляция в BRICK v2, канон эмиттера | 409 |
| `SPEC/12-UNIVM-ISA.md` | UNIVM ISA v0+v1: модель, форматы F0..F3, 24 инструкции, стек вызовов + конвенция sp = r13, ловушки 1-5/7, окно устройств (E7.1; v1 — E7.4-1) | 258 |
| `SPEC/13-UP-FORMAT.md` | контейнер .UP v1/v2: заголовок 24 Б + код (+секция данных dataoff — E7.4-1), пределы, отказы | 146 |
| `SPEC/14-L4-LIBRARY.md` | Библиотека L4 (E8.1; уточнение положения !include — E8.2a): композиция программы+библиотеки (!include через splice), ABI вызова, слой LIB-1 — числа/строки/память (11 кирпичей) | 176 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 492 |
| `MAP/METHODS.md` | указатель реестра кирпичей (446 строк реестра: K0 116 / K1 132 / K2 120 / K3 70 / K4 11 — 4 готов E8.2a + 7 план; ревизия — очередь) | 497 |
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
| `MAP/M3-UNIVM.md` | карточки кирпичей M3-UNIVM — ветви C/U/M/J/X (19; срезы E7.2-1..4 + E7.4-2a/b/c; ветвь V — в M3-UNIVM-V.md по лимиту 500, прецедент M1-ENC-E/S) | 331 |
| `MAP/M3-UNIVM-V.md` | карточки кирпичей M3-UNIVM — ветвь V (интерпретатор, 21: +ALU v1 K3-V112..V116 — E7.4-2b; +стек вызовов K3-V117/V118 — E7.4-2c, часть call) | 335 |
| `MAP/M3-UVA.md` | карточки кирпичей M3-UVA — ассемблер .uva -> .UP (30: ветви C/T/B/L/E/W/X; срезы E7.3-1..4 + мнемоники v1 E7.4-3a + .data/.UP v2 E7.4-3b — НОВЫЙ K3-T009 data_next) | 489 |
| `MAP/M4-LIB.md` | карточки кирпичей M4-LIB — библиотека L4 (11: ветви C/N/S/M — слой LIB-1; ветвь C — готов E8.2a, N/S/M — план) | 192 |
| `MAP/LAYERS.md` | реестр слоёв L0..L6 и их статусы (L3 — готов, ЭТАП 7 ЗАКРЫТ; L4 — в работе: E8.1 + E8.2a — ветвь C) | 51 |

## KERNEL/ — ядро

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L0-SEED/CARD.md` | карточка модуля M0-SEED | 53 |
| `KERNEL/L0-SEED/seed.hex` | тело секции семени, ATOM v1 (истина) | 63 |
| `KERNEL/L0-SEED/seed.peg` | обёртка семени (PEG v1, SPEC/07) | 10 |
| `KERNEL/L0-SEED/seed.exe` | материализация: 1024 байта, PE32+ | — |
| `KERNEL/L0-SEED/BYTECODE.md` | байт-за-байтом разбор всего образа | 249 |
| `KERNEL/L0-SEED/VERIFY.md` | как проверить подлинность и работу | 80 |
| `KERNEL/L0-SEED2/CARD.md` | карточка модуля M0-SEED2 (командная строка) | 90 |
| `KERNEL/L0-SEED2/seed2.hex` | тело секции семени-2, ATOM v1 (истина) | 224 |
| `KERNEL/L0-SEED2/seed2.peg` | обёртка семени-2 | 10 |
| `KERNEL/L0-SEED2/seed2.exe` | материализация: 2048 байт, PE32+ | — |
| `KERNEL/L0-SEED2/BYTECODE.md` | разбор образа: 185 инструкций, данные, импорты | 411 |
| `KERNEL/L0-SEED2/VERIFY.md` | проверка, журнал, пойманные ошибки | 96 |
| `KERNEL/L0-HXDUMP/CARD.md` | карточка модуля M0-HXDUMP (hex-дамп) | 91 |
| `KERNEL/L0-HXDUMP/hxdump.hex` | тело секции hxdump, ATOM v1 (истина) | 290 |
| `KERNEL/L0-HXDUMP/hxdump.peg` | обёртка hxdump | 12 |
| `KERNEL/L0-HXDUMP/hxdump.exe` | материализация: 3584 байта, PE32+ | — |
| `KERNEL/L0-HXDUMP/BYTECODE.md` | разбор образа: 244 записи кода, данные, импорты | 497 |
| `KERNEL/L0-HXDUMP/VERIFY.md` | проверка, журнал, пойманные ошибки | 99 |
| `KERNEL/L0-HEXGEN/CARD.md` | карточка модуля M0-HEXGEN (первый компилятор) | 123 |
| `KERNEL/L0-HEXGEN/hexgen.hex` | тело секции hexgen, ATOM v1 (истина) | 421 |
| `KERNEL/L0-HEXGEN/hexgen.peg` | обёртка hexgen | 13 |
| `KERNEL/L0-HEXGEN/hexgen.exe` | материализация: 2560 байт, PE32+ (bss) | — |
| `KERNEL/L0-HEXGEN/BYTECODE.md` | разбор образа: 370 записей кода, данные, импорты, виртуальные нули | 482 |
| `KERNEL/L0-HEXGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 116 |
| `KERNEL/L0-PEGEN/CARD.md` | карточка модуля M0-PEGEN (обёртка образов) | 133 |
| `KERNEL/L0-PEGEN/pegen.hex` | тело секции pegen, ATOM v1 (истина) | 409 |
| `KERNEL/L0-PEGEN/pegen.peg` | обёртка pegen (самосборка) | 13 |
| `KERNEL/L0-PEGEN/pegen.exe` | материализация: hexgen + pegen, 4096 байт, PE32+ | — |
| `KERNEL/L0-PEGEN/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 115 |
| `KERNEL/L0-PEGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 106 |
| `KERNEL/L1-BRICK/CARD.md` | карточка модуля M1-BRICK (ассемблер BRICK) | 153 |
| `KERNEL/L1-BRICK/brick.hex` | тело секции brick, ATOM v1 (истина E5a) | 671 |
| `KERNEL/L1-BRICK/brick.brick` | корень модуля M1-BRICK: шапка + !include трёх частей (разрез E6.3) | 7 |
| `KERNEL/L1-BRICK/brick_p1.brick` | часть 1: поток X/C/G, пассажи N, разбор директив A (5-483 строки тела) | 479 |
| `KERNEL/L1-BRICK/brick_p2.brick` | часть 2: лексика, метки, сервис H/G/U/C/F (484-744) | 261 |
| `KERNEL/L1-BRICK/brick_p3.brick` | часть 3: данные D — таблицы, импорты, bss (745-850) | 106 |
| `KERNEL/L1-BRICK/brick.peg` | обёртка brick (PEG v1, SPEC/07) | 11 |
| `KERNEL/L1-BRICK/brick.exe` | материализация: hexgen + pegen, 3584 байта, PE32+ | — |
| `KERNEL/L1-BRICK/BYTECODE.md` | сводка, карта кирпичей, данные, импорты, история | 191 |
| `KERNEL/L1-BRICK/VERIFY.md` | SHA-256, 4 уровня проверки, журнал | 131 |
| `KERNEL/L1-ENC/CARD.md` | карточка модуля M1-ENC (кодировщик BRICK v2) | 150 |
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
| `KERNEL/L2-WALL/VERIFY-E6D.md` | журнал верификации самохостинга E6.4d-2/2..3/1 (VERIFY.md у лимита 500) | 480 |
| `KERNEL/L2-WALL/VERIFY-E6D2.md` | журнал верификации самохостинга E6.4d-3/2+ (продолжение; VERIFY-E6D.md у лимита 500) | 430 |
| `KERNEL/L2-WALL/VERIFY-E6D3.md` | журнал верификации самохостинга E6.4d-4/2..4/3c-1 | 117 |
| `KERNEL/L2-WALL/VERIFY-E6D4.md` | журнал верификации самохостинга E6.4d-4/3b..3c-3 | 497 |
| `KERNEL/L2-WALL/VERIFY-E6D5.md` | журнал ФИНАЛА E6.4d: фикс-пункт самосборки + замена артефактов (E6.4d-5/3-1..2) | 113 |

### KERNEL/L3-UNIVM — ядро виртуальной машины (E7.4-2c — call/ret + стек вызовов; ISA полна)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L3-UNIVM/CARD.md` | карточка модуля M3-UNIVM (ядро UNIVM: срезы E7.2-1..4 — все 18 опкодов v0; E7.4-2a — контейнер v2; E7.4-2b — ALU v1; E7.4-2c — call/ret + стек вызовов 1024/ловушка 5 — ISA v0+v1 полна, 24 опкода) | 162 |
| `KERNEL/L3-UNIVM/kernel.wall` | корень ядра с разрезом (SPEC/10): 8 ext, 21 var (вкл. regs[16], ram, steplim, uq/ur — udivmod E7.4-2b, csp/cstack[1024] — стек вызовов E7.4-2c), 14 str (вкл. s_data — E7.4-2a), main (CLI -> чтение -> разбор -> исполнение) | 125 |
| `KERNEL/L3-UNIVM/kernel_self_c.wall` | часть ядра: сервис — print_error, skip0, read_arg, check_end (не более двух аргументов), widen, read_lim (предел шагов — 2-й аргумент CLI, E7.2-4) | 232 |
| `KERNEL/L3-UNIVM/kernel_self_up.wall` | часть ядра: контейнер v1/v2 (E7.4-2a) — rd32 (LE u32), read_up (чтение + разбор SPEC/13, версии {1, 2}, dataoff; порядок отказов == оракул parse_up), read_data (K3-U003: секция данных -> RAM[0:datalen] кусками 4096 Б, отказ DATA) | 175 |
| `KERNEL/L3-UNIVM/kernel_self_mem.wall` | часть ядра: память и устройства (E7.2-3) — get_ram (RAM: GlobalAlloc + обнуление), op_ldb/op_stb/op_ldq/op_stq (4 кирпича опкодов памяти: RAM/окно/консоль/ловушки 3-4, ветвь M) | 222 |
| `KERNEL/L3-UNIVM/kernel_self_j.wall` | часть ядра: переходы (E7.2-4) — op_jmp/op_jnz (2 кирпича опкодов 10..11, F3, imm32 беззнаковое; ветвь J) | 54 |
| `KERNEL/L3-UNIVM/kernel_self_alu.wall` | часть ядра: ALU v1 (E7.4-2b, ветвь V) — udivmod (K3-V112: беззнаковое деление из простых операций WALL — переворот знакового бита, пути b <= 2^63 / b > 2^63; глобали uq/ur) + op_mul/op_div/op_mod/op_sra (K3-V113..V116, опкоды 13..16, ловушка 7) | 187 |
| `KERNEL/L3-UNIVM/kernel_self_call.wall` | часть ядра: стек вызовов (E7.4-2c, ветвь V) — op_call/op_ret (K3-V117/V118, опкоды 17..18, форматы F3/F0) + аппаратный стек вызовов глубины 1024 (глобали cstack[1024]/csp; ловушка 5: call при полном / ret при пустом; порядок проверок: поля (1) ПЕРЕД стеком (5)) | 63 |
| `KERNEL/L3-UNIVM/kernel_self_vm.wall` | часть ядра: интерпретатор — interp (цикл: предел шагов (trap 6) ДО выборки + порядок проверок SPEC/12 п. 7; диспетчер v0 01..12 + v1 13..18 — ISA полна, E7.4-2c; длина F0 у ret — без проверки), op_const..op_eq (11 ALU-кирпичей v0, regs[16]), op_halt, fail_trap (TRAP/STEPS), copy_str, out_dec | 495 |
| `KERNEL/L3-UNIVM/kernel.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-2c): wall.exe(kernel.wall), плоский, 247461 Б — T-E7-09 | — |
| `KERNEL/L3-UNIVM/kernel.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(kernel.b2), 229810 Б — T-E7-09 | — |
| `KERNEL/L3-UNIVM/kernel.peg` | обёртка — константа SPEC/11 п.6 (!module kernel; вход 1200, idata 1000 28, iat 1028 48) | 9 |
| `KERNEL/L3-UNIVM/kernel.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+kernel.peg — 36352 Б (тело 35474, вкл. DZ cstack 8192), вход 0x1200, импорты-восьмёрка; SHA-256 9F569617… — T-E7-09 | — |
| `KERNEL/L3-UNIVM/BYTECODE.md` | карта образа ядра: сводка, 40 функций (RVA; read_data — E7.4-2a; группа «ALU v1» — E7.4-2b; группа «стек вызовов» — E7.4-2c), данные (вкл. s_data, regs[16], ram, uq/ur, cstack[1024]), воспроизведение | 118 |
| `KERNEL/L3-UNIVM/VERIFY.md` | подлинность + уровни проверки + журнал срезов (E7.4-2a — контейнер v2; E7.4-2b — ALU v1; E7.4-2c — call/ret + стек вызовов) | 224 |

### KERNEL/L3-UVA — ассемблер UNIVM (E7.3 закрыт + E7.4-3a мнемоники v1 + E7.4-3b .data/.UP v2)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L3-UVA/CARD.md` | карточка модуля M3-UVA (ассемблер .uva -> .UP: срезы E7.3-1..4 + E7.4-3a + E7.4-3b — каркас CLI + .mem + halt + F1/F2/F3 + метки + МНЕМОНИКИ v1: mul/div/mod/sra + call/ret (F0 — 1 байт) + ДИРЕКТИВА .data + контейнер .UP v2 (версия 2 + dataoff, отказ DATA); диффтест == ассемблеру оракула; весь класс ассемблера оракула покрыт) | 264 |
| `KERNEL/L3-UVA/uva.wall` | корень ассемблера с разрезом (SPEC/10): 8 ext, 29 var (вкл. tstart/tend[12] — таблица токенов, moff — смещение операнда памяти, dcnt/dpos — счёт и позиция байтов .data — E7.4-3b, nsa/nsb/lcnt + lsta/lend/lval[512] — таблица меток), 16 str (вкл. s_mn — таблица 24 мнемоник ISA v0+v1 — E7.4-3a; s_dotdata/s_data — E7.4-3b), main (CLI -> чтение -> pass1 -> pass2 -> заголовок -> запись) | 188 |
| `KERNEL/L3-UVA/uva_self_c.wall` | часть ассемблера: сервис — print_error, skip0, read_arg, check_end (ровно два аргумента), widen, fail_at (ERR=FORMAT AT=hex4, код 6) | 201 |
| `KERNEL/L3-UVA/uva_self_t.wall` | часть ассемблера: лексика — tok_is, tokenize (разделители как _toks), parse_num (imm32, переполнение в цикле), line_trim (комментарий + края), line_next (итератор строк по LF — как split оракула), mn_find (K3-T006: таблица 24 мнемоник ISA v0+v1 — индекс i => опкод i+1, 18..23 — v1 — E7.4-3a), parse_reg (K3-T007: r0..r15), parse_memop (K3-T008: rA[+смещ] — бэктрекинг rN/r1X, копится mod 2^64 без диапазона), data_next (K3-T009: потоковый итератор байтов .data hex2 — E7.4-3b, строка данных любой длины — не через tstart/tend) | 496 |
| `KERNEL/L3-UVA/uva_self_b.wall` | часть ассемблера: метки (E7.3-4) — lab_skip (K3-B001: префикс `имя:` — как regex оракула, после ':' конец/пробельный, НЕ запятая), lab_find (K3-B002: поиск по таблице — имена-границы в srcbuf, без копий), lab_add (K3-B003: регистрация со значением pc; дубликат/ёмкость 512 → fail_at), parse_target (K3-B004: цель jmp/jnz — имя из таблицы или число; 'jmp r5' без объявления — ошибка метки) | 153 |
| `KERNEL/L3-UVA/uva_self_l.wall` | часть ассемблера: проход 1 — pass1 (структура: цикл lab_skip+lab_add ДО .mem/мнемоники — как оракул, дубликат раньше неизвестной мнемоники; .mem/все 24 мнемоники ISA v0+v1/длины F1 = 3 (i 1..10 и 18..21), F3 = 6, F0 = 1 (ret) — E7.4-3a; .data — E7.4-3b: memsize есть, байты — data_next, dcnt копится; «нет .mem» — строка 1; pc = длина кода, dcnt = счёт данных, lcnt = 0; идиома чтения ВПЕРЁД) | 117 |
| `KERNEL/L3-UVA/uva_self_e.wall` | часть ассемблера: проход 2 — pass2 (диспетчер всех 24 форм: F1 — enc_f1 (АЛУ v0 + v1), halt — счёт/число, F2 — enc_f2, F3 — enc_f3 (jmp/jnz/call), F0 — enc_f0 (ret); метки строк пропускаются; .data — ЭМИССИЯ байтов за кодом — outbuf+24+pc+dcnt — E7.4-3b) + enc_halt (12 00 imm32 LE) + enc_f1 (K3-E003) + enc_f2 (K3-E004) + enc_f3 (K3-E005: jmp/call [i+1][00][imm32], jnz [17][rd][imm32]) + enc_f0 (K3-E006: 1 байт [24], 0 операндов — E7.4-3a) | 245 |
| `KERNEL/L3-UVA/uva_self_w.wall` | часть ассемблера: контейнер — put32 (LE u32), make_header (24 Б SPEC/13 п. 2: v1/v2 — dcnt > 0 — версия 2 + dataoff = 24+pc, отказ DATA — dcnt > memsize, ERR=DATA код 6 — E7.4-3b), write_out (CREATE_ALWAYS + один WriteFile 24+pc+dcnt) | 76 |
| `KERNEL/L3-UVA/uva.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E7.4-3b): wall.exe(uva.wall), плоский, 244997 Б — T-E7-19 | — |
| `KERNEL/L3-UVA/uva.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(uva.b2), 228477 Б — T-E7-19 | — |
| `KERNEL/L3-UVA/uva.peg` | обёртка — константа SPEC/11 п.6 (!module uva; вход 1200, idata 1000 28, iat 1028 48) | 9 |
| `KERNEL/L3-UVA/uva.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+uva.peg — 40960 Б, вход 0x1200, импорты-восьмёрка; SHA-256 32ABF177… — T-E7-19 | — |
| `KERNEL/L3-UVA/BYTECODE.md` | карта образа ассемблера: сводка, 30 функций (RVA, +data_next — E7.4-3b), данные, инварианты | 118 |
| `KERNEL/L3-UVA/VERIFY.md` | подлинность + уровни проверки + журнал срезов (E7.3-1..4; дефект оракула №24 закрыт; E7.4-3a — мнемоники v1; E7.4-3b — .data/.UP v2) | 326 |

### KERNEL/L4-LIB — библиотека L4 (E8.2a: ветвь C готова)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L4-LIB/CARD.md` | карточка модуля M4-LIB: рецепт композиции программа+библиотека (!include ПОСЛЕ кода — E8.2a), состав ветвей, ABI, верификация | 70 |
| `KERNEL/L4-LIB/lib_c.uva` | ветвь C — консоль: K4-C001 chr_out / K4-C002 crlf_out / K4-C003 buf_out / K4-C004 buf_out_rev (метки lib_*, только r1..r4 — временные ABI; E8.2a) | 46 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов | 28 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов | 196 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 109 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 104 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-17 | 147 |
| `TESTS/T-L1-BRICK.md` | тест-план brick T-M6-01..T-M6-17, T-E6-36 | 168 |
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11b (E6.2; рост ISA E6.4c; предел 256 КиБ E6.4e-1) | 155 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18, T-E6-16b (E6.3, E6.4e-2) | 97 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул v1/v2 + инструмент + срезы + секция 11 + самохостинг (E6.4d-5/1..2, T-E6-59/60) + фикс №23 (E7.2-2F, T-E6-61) | 482 |
| `TESTS/T-L3-UNIVM.md` | тест-план UNIVM: оракул T-E7-01..08 (E7.1) + T-E7-26..31 (E7.4-1: ISA v1 + .UP v2) + ядро kernel.exe T-E7-09..18 (E7.2-1..4) + T-E7-32 (E7.4-2a) + T-E7-33 (E7.4-2b) + T-E7-34 (E7.4-2c: call/ret + стек вызовов/ловушка 5) | 372 |
| `TESTS/T-L3-UVA.md` | тест-план ассемблера uva.exe T-E7-19..25, 35 (E7.3-1..4 + E7.4-3a + E7.4-3b + E7.4-4 — ПРИЁМКА DoD ЭТАПА 7.4: фикс-пункт/CLI/диффтест 124+127+3 DATA/отвержение/CODE0/15 кругов (вкл. ловушечные — ловушки 5/7 путём ЦЕЛИКОМ uva → kernel.exe)/приёмка T-E7-25 — якоря 24 + программы 10; T-E7-35 — контракт DATA) | 296 |
| `TESTS/T-L4-LIB.md` | тест-план библиотеки L4: оракул против якорей T-E8-01..07 (E8.1) + диффтесты ветви C T-E8-08..11 (E8.2a: композиция+ABI+сквозной круг инструментами) | 141 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории (батарея 191; ЭТАП 8 — E8.1 + E8.2a) | 271 |
| `LAB/py/lab_pe.py` | разбор PE32+ + инварианты SPEC/04 | 178 |
| `LAB/py/lab_atom.py` | оракул ATOM v1 (SPEC/03) | 68 |
| `LAB/py/lab_brick.py` | оракул BRICK v1 (SPEC/08; метки 1024, imagebuf 0x40010 — E6.4e-3) | 318 |
| `LAB/py/lab_pegen.py` | оракул PEG v1 (SPEC/07) | 125 |
| `LAB/py/lab_enc.py` | оракул ENC v1 (SPEC/09): M-строка -> H-строка | 495 |
| `LAB/py/lab_enc_isa.py` | кирпич роста ISA оракула ENC: EncError/_err/_rex/_enc_imul (E6.4c) | 31 |
| `LAB/py/lab_splice.py` | оракул SPLICE v1 (SPEC/10): склейка по !include | 106 |
| `LAB/py/lab_splice_cases.py` | эталоны SPLICE: 14 якорей, 13 ошибок, большой случай | 135 |
| `LAB/py/lab_l2.py` | оракул WALL v1/v2, фронт: parse + семантика (v2: массивы, astore) | 350 |
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
| `LAB/py/lab_win.py` | загрузчик PE + заглушки kernel32 + вирт. ФС + куча (E6.4c; GlobalAlloc — E6.4d-2; 4 МиБ — E6.4d-2/2) | 306 |
| `LAB/py/lab_run.py` | прогон EXE с командной строкой | 30 |
| `LAB/py/lab_disasm.py` | дизассемблер (декод -> мнемоника) | 131 |
| `LAB/py/lab_vm.py` | оракул UNIVM v0+v1 (SPEC/12): исполнитель (+стек вызовов 1024, ловушки 5/7; FMT_OF из реестра OPS) + мини-ассемблер (метки, .mem, .data — v2) — E7.1; v1 — E7.4-1 | 488 |
| `LAB/py/lab_up.py` | оракул контейнера .UP v1/v2 (SPEC/13): make_up/parse_up + отказы — выделен из lab_vm.py по лимиту 500 (E7.4-1) | 86 |
| `LAB/py/lab_t_vm.py` | секция 13 батареи: оракул UNIVM — T-E7-01..08 + T-E7-26..31 (якоря 18+6 опкодов, семантика v1, факториал рекурсией, ловушки 5/7 (v1_traps — из TRAP_VMS корпуса, единый свидетель с секцией 15 — E7.4-4), секция данных v2; данные — lab_t_vm_corpus.py) | 257 |
| `LAB/py/lab_t_vm_corpus.py` | корпуса секции 13: якоря/демо-программы (FACT_VM/DATA_VM/OPS2_VM)/ловушечные TRAP_VMS (единый свидетель ловушек 5/7 для T-E7-29/24/25 — E7.4-4)/отказы — данные прогонщика lab_t_vm.py, выделены по лимиту 500 (E7.4-1) | 397 |
| `LAB/py/lab_t_kernel.py` | секция 14 батареи: ядро kernel.exe — T-E7-09..18 (фикс-пункт, CLI/контейнер/предел, диффтест срезов E7.2-1..4) + T-E7-32 (E7.4-2a: контейнер v2) + T-E7-33 (E7.4-2b: ALU v1 + ловушка 7) + T-E7-34 (E7.4-2c: call/ret + стек вызовов + порядок проверок _ovf_field; корпуса — lab_t_kernel_corpus.py + _v1.py) | 442 |
| `LAB/py/lab_t_kernel_corpus.py` | корпуса программ диффтеста ядра (только данные: ALU срез 2, память срез 3, переходы+предел срез 4 + контейнер v2 — секция данных, E7.4-2a; прогонщик — lab_t_kernel.py; выделен по лимиту 500 строк) | 459 |
| `LAB/py/lab_t_kernel_corpus_v1.py` | корпуса ISA v1 (только данные: ALU v1 — E7.4-2b; call/ret + стек вызовов — E7.4-2c, CALL_*; FACT_VM переиспользован из lab_t_vm_corpus.py — единый свидетель T-E7-28/34) | 405 |
| `LAB/py/lab_t_uva.py` | секция 15 батареи: ассемблер uva.exe — T-E7-19..25, 35 (фикс-пункт артефактов, CLI/предел входа, диффтест == assemble оракула: срезы 1-4 + мнемоники v1 E7.4-3a + .data E7.4-3b — 124/127/3 DATA, отвержение с номерами строк, CODE0, 15 кругов uva -> kernel.exe (вкл. mul-консоль, call/ret, DATA_VM и ЛОВУШЕЧНЫЕ — ловушки 5/7 путём ЦЕЛИКОМ uva → ядро, E7.4-4); T-E7-35 — контракт DATA; T-E7-25 — ПРИЁМКА DoD ЭТАПА 7.4: якоря T-E7-01/26 (24) + ВСЕ программы секции 13 (T-E7-04..08/27/28/30 + ловушечные TRAP_VMS — 10); данные — lab_t_uva_corpus.py) | 337 |
| `LAB/py/lab_t_uva_corpus.py` | корпуса диффтеста секции 15 (только данные: OK 124 / ERR 127 / DATA 3 / CODE0 5 — срезы 1-4 + v1-корпус E7.4-3a + .data-корпус E7.4-3b; выделен из lab_t_uva.py по лимиту 500 строк — прецедент lab_t_vm_corpus.py) | 324 |
| `LAB/py/lab_l4.py` | оракул библиотеки L4 (SPEC/14 LIB-1): эталонная семантика 11 кирпичей — консоль/память/реверс-цифры (E8.1) | 106 |
| `LAB/py/lab_l4_cases.py` | якоря оракула L4: DEC/I64/REV/STR/BUF/CPY/FILL/CMP — ручные литералы (E8.1) | 106 |
| `LAB/py/lab_t_l4.py` | секция 16 батареи: оракул L4 == якорям T-E8-01..07 (E8.1) + диффтест ветви C T-E8-08..11 — композиция/ABI/круг splice→uva→kernel (E8.2a) | 273 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход; 191 проверка — с E8.2a: секция 16 — оракул L4 T-E8-01..07 + диффтест ветви C T-E8-08..11) | 482 |
| `LAB/py/lab_t_exe.py` | секции 7-8b батареи: инструменты enc/splice/brick (T-E6-05..11b, 12..18b, 36; пределы enc 2 МиБ (E6.4g-5) и brick 512 КиБ/2048 меток — E6.4f) | 353 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL v1+v2 (T-E6-19..24, 31..35) | 229 |
| `LAB/py/lab_t_wall2.py` | секция 10 батареи: инструмент wall.exe (T-E6-25..30 + T-E6-50 — предел меток выхода 2000, граница 2000/2001; E6.4d-3/3-1) | 171 |
| `LAB/py/lab_t_wall3.py` | секция 11 батареи: инструмент wall.exe — v2 срезы 1-3 + 4a/4b/5 + фикс №19 (T-E6-37..48, 51; big_source2, DEMO_NEST-круг) + якоря фикса №23 (T-E6-61) | 312 |
| `LAB/py/lab_t_wallself.py` | секция 12 батареи: каркас wall.wall (splice-корень) == оракулу + круг + CLI == wall.exe (19 путей) + проход 0+1 == оракулу parse (T-E6-49a/b/c/d) + эмитция пролога/функций/данных (T-E6-52/54) + выражения (T-E6-55) + вызовы/getb/индексация (T-E6-56) + статы-имена (T-E6-57) + guard-группа (T-E6-58) | 500 |
| `LAB/py/lab_t_wallself_final.py` | секция 12b батареи: финал E6.4d-5 шаг 1 — канарейки круга, 6 DEMO-программ компилируются КАРКАСОМ, полный круг до эмуляции (T-E6-59) | 86 |
| `LAB/py/lab_t_wallself_emit_cases.py` | источники тестов эмитции T-E6-55/56/57 (срезы C-2/1..2/3; только данные — прогонщик lab_t_wallself.py; выделен по лимиту 500 строк) | 179 |
| `LAB/py/lab_t_wallself_corpus.py` | корпус секции 12: пул источников T-E6-49d (v1/v2/E1/E2 + микроканарейки E6.4d-2/3..3/2 + big 1/2; только ASCII) | 228 |
| `LAB/py/lab_t_wallself_model.py` | модель класса эквивалентности каркаса (E6.4d-3/2..3/3): _expect_line по строкам _lex — perr/cerr, стек блоков bstk (func/if/else/while), kw-патологии str/ext (_kw_falls) | 225 |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона; последняя — сессия 61, E8.1 — SPEC/14 + оракул библиотеки L4) | 6085 |
| `LAB/ai/kernel_test.py` | (частное) построитель M3-UNIVM: kernel.wall -> артефакты (конвейер — эмуляция) + корпус секции 14 с отчётом | 100 |
| `LAB/ai/wall_ppc_probe.py` | (частное) матрица-зонд дефекта №23 wall.exe (pp_pcount, 17 сниппетов: оракул vs wall.exe; ЗАКРЫТ E7.2-2F — 0 расхождений; регресс-зонд) | 84 |
| `LAB/ai/kernel_labelmap.py` | (частное) карта меток kernel.brick (RVA) — обновление BYTECODE.md (E7.2-1) | 33 |
| `LAB/ai/uva_test.py` | (частное) построитель M3-UVA: uva.wall -> артефакты (конвейер — эмуляция) + карта меток + корпус секции 15 с отчётом (E7.4-3b) | 114 |
| `LAB/ai/probe_e73_4.py` | (частное) зонд оракула lab_vm на метках/F3 (17 OK + 26 ERR — сняты ДО реализации среза 4: кодировки, порядок ошибок, синтаксис меток) | 117 |
| `LAB/ai/probe_e742b.py` | (частное) фаззи-прототип ALU v1 ДО интеграции в ядро: udivmod/sra/mul на оракуле WALL + эмуляторе против эталона Python — 139 случаев (края + фаззи) | 278 |
| `LAB/ai/uva_syntax_check.py` | (частное) быстрая проверка uva.wall: splice + компиляция оракулом WALL без эмуляции (E7.3-1) | 47 |
| `LAB/ai/enc_build.py` | (частное) построитель M1-ENC: enc.b2 -> артефакты + карта меток | 469 |
| `LAB/ai/enc_build_lim.py` | (частное) пересборка M1-ENC + dev-тесты предела 256 КиБ (E6.4e-1; исторический — границы в духе своей эпохи) | 267 |
| `LAB/ai/enc_build_lim2.py` | (частное) пересборка M1-ENC + dev-тесты предела 1 МиБ (E6.4d-4; максимум 0xFFFFF — dev-only) | 284 |
| `LAB/ai/enc_build_lim3.py` | (частное) пересборка M1-ENC + dev-тесты предела 2 МиБ (E6.4g-5; границы 0x100020/0x1FFFFF — dev-only, 0x200000 отвергнут) | 284 |
| `LAB/ai/splice_build.py` | (частное) построитель M1-SPLICE: разрез -> артефакты + dev-тесты | 228 |
| `LAB/ai/splice_build_lim.py` | (частное) пересборка M1-SPLICE + dev-тесты пределов 256 КиБ (E6.4e-2) | 344 |
| `LAB/ai/wall_build.py` | (частное) пересборка M2-WALL (idata — точная метка :idt, срез 4b; сборка после фикса №19 — E6.4d-4/2) | 116 |
| `LAB/ai/bytecode_rows.py` | (частное) перенос адресов карты ветвей BYTECODE.md §2 при пересборке (якорь-метки; фикс №19) | 165 |
| `LAB/ai/wall_test.py` | (частное) dev-тест wall.exe v1 (E6.4b) | 101 |
| `LAB/ai/wall_test_v2.py` | (частное) dev-тест среза 1: * / %, v1/v2, «U-MDM-OK 52» (эталоны — lab_l2_mdm.py) | 183 |
| `LAB/ai/wall_test_bc.py` | (частное) dev-тест среза 2: break/continue, дефект №15, «U-BC-OK 25» (эталоны — lab_l2_bc.py) | 179 |
| `LAB/ai/wall_test_cc.py` | (частное) dev-тест среза 3: цепочки && / ||, B2/F14/F16, «U-CC-OK 31» (эталоны — lab_l2_cc.py) | 159 |
| `LAB/py/lab_l2_arr.py` | эталоны WALL срез 4a: 10 якорей + ошибки + DEMO_ARR «U-ARR-OK 45» + big_arr (E6.4c-3/4) | 208 |
| `LAB/py/lab_l2_ix.py` | эталоны WALL срез 4b: якоря ix_A1..A6 + ссылки на cases2 + ошибки + big_ix (E6.4c-3/4b) | 136 |
| `LAB/ai/wall_test_arr.py` | (частное) dev-тест среза 4a: объявления массивов, базы, len (эталоны — lab_l2_arr.py) | 127 |
| `LAB/ai/wall_test_ix.py` | (частное) dev-тест среза 4b: индексация e[i] + astore, «U-WALL2-OK 85» (эталоны — lab_l2_ix.py) | 138 |
| `LAB/ai/label_map.py` | (частное) карта меток wall.brick (RVA) для BYTECODE.md | 95 |
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
| `LAB/ai/brick_build_lim4.py` | (частное) пересборка brick: предел ИСХОДНИКА 1 -> 2 МиБ (E6.4g-6): 2 imm32 + 2 disp32 + DBZ filebuf/imagebuf, hex/peg/exe, dev 11/11 (границы 0x100020/0x1FFFFF/0x200000) | 427 |
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

- Кирпичей в реестре: **446 строк** (K0 — 116; K1 — 132, вкл. 1 дубль
  ID K1-N011 enc/splice — очередь; K2 — 120; K3 — 70: M3-UNIVM 40
  — ветви C/U/M/J/X 19 + V 21 (интерпретатор) и M3-UVA 28;
  K4 — 11 — библиотека LIB-1, карточки-план E8.1;
  полная ревизия строк ↔ карточек всех модулей — очередь мелочей
  — сессия 57: счётчик приведён к фактическому числу строк
  реестра — было 319, занижено).
- Модулей: **12** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE, M2-WALL, M3-UNIVM, M3-UVA, M4-LIB —
  ветвь C готова E8.2a: lib_c.uva + CARD.md; N/S/M — план).
- Тестов: **186** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..48 + T-E6-10b + T-E6-16b,
  T-E6-49a/b/c/d + T-E6-53..60, T-E6-61 — E7.2-2F, T-E7-01..08 — E7.1,
  T-E7-09..14 — E7.2-1, T-E7-15 — E7.2-2, T-E7-16 — E7.2-3,
  T-E7-17..18 — E7.2-4, T-E7-19..24 — E7.3-1..3, T-E7-25 — E7.3-4
  (приёмка; расширение E7.4-4 — ПРИЁМКА DoD ЭТАПА 7.4),
  T-E7-26..31 — E7.4-1 (ISA v1 + .UP v2), T-E7-32 — E7.4-2a (контейнер
  v2 в ядре), T-E7-33 — E7.4-2b (ALU v1 + ловушка 7), T-E7-34 —
  E7.4-2c (call/ret + стек вызовов + ловушка 5), T-E7-35 — E7.4-3b
  (контракт DATA), T-E8-01..07 — E8.1 (оракул L4 против якорей),
  T-E8-08..11 — E8.2a (диффтест ветви C: композиция/якоря BUF/ABI/
  сквозной круг инструментами);
  автоматических в батарее — 191).
- Этап: **E8.2a ВЫПОЛНЕН (сессия 62) — ЭТАП 8 в работе: Библиотека L4,
  ветвь C (консоль) реализована.** Первая реализация библиотеки:
  часть KERNEL/L4-LIB/lib_c.uva (K4-C001..C004 — chr_out/crlf_out/
  buf_out/buf_out_rev; метки lib_*, только временные r1..r4) +
  CARD.md модуля (рецепт композиции: !include ПОСЛЕ кода программы,
  уточнение в SPEC/14 п. 2) + диффтесты T-E8-08..10 (композиция
  оракулом splice → lab_vm.run_asm == оракулу lab_l4; якоря BUF;
  ABI — сохраняемость r5..r15) + T-E8-11 СКВОЗНОЙ КРУГ
  ИНСТРУМЕНТАМИ (splice.exe → uva.exe == ассемблеру оракула байт-
  в-байт → kernel.exe == оракулу, эмуляция LAB); ядро НЕ
  пересобирается (R7 — библиотека внешние исходники); батарея
  187 → 191/191 (группа 3 — 46/46; 1 и 2 — CI на пуше). Далее
  E8.2b..d — ветви N/S/M, затем E8.3 — демо-программы DoD. Подробно
  — DOCS/03c-HISTORY-E8 (сессия 62).
- Предыдущий: **E8.1 ВЫПОЛНЕН (сессия 61) — ЭТАП 8 ОТКРЫТ: Библиотека
  L4, срез «сначала истины семантики» (прецедент E7.1).** SPEC/14
  (композиция !include через splice.exe + ABI r1..r4/r1, r13 sp,
  r14 devbase + реестр LIB-1 из 11 кирпичей) + оракул LAB/py/
  lab_l4.py + якоря lab_l4_cases.py (ручные литералы) + секция 16
  батареи (T-E8-01..07); карточки K4 — MAP/M4-LIB.md (план — R3);
  ядро и артефакты НЕ менялись; батарея 180 → 187/187.
- Предыдущий: **E7.4-4 ВЫПОЛНЕН (сессия 60) — ПРИЁМКА DoD ЭТАПА 7.4;
  ЭТАП 7.4 ЗАКРЫТ.** Полный корпус v0+v1: T-E7-25 — якоря 24 +
  ВСЕ 10 программ секции 13 (вкл. DATA_VM и 4 ловушечные — TRAP_VMS,
  НОВАЯ секция lab_t_vm_corpus.py — единый свидетель с T-E7-29;
  рефакторинг v1_traps) собираются uva == оракулу байт-в-байт;
  НОВЫЕ ловушечные круги T-E7-24: 11 → 15 (ловушки 5/7 с точными
  шагами STEPS=1024/0/2/2, код 1 — путь ЦЕЛИКОМ uva → kernel.exe —
  двойной свидетель T-E7-29/34). Ядро/артефакты НЕ менялись;
  батарея 180/180 (группы: 3 — 35/35, 1 — 134/134; 2 — CI на
  пуше). ROADMAP сжат (500 → 494 строки). Далее — ЭТАП 8:
  Библиотека L4 (DoD — минимум две разные программы). Подробно —
  DOCS/03b-HISTORY-E7 (сессия 60).
- Предыдущий: **E7.4-3b ВЫПОЛНЕН (сессия 59) — ассемблер uva.exe:
  .data + контейнер .UP v2 (K3-T009 data_next; корпуса 124/127
  + DATA 3; круги 11 (DATA_VM); T-E7-35; батарея 179 → 180;
  артефакты 40960 Б, функций 30). Весь класс ассемблера
  оракула покрыт.** Подробно — 03b-HISTORY-E7 (сессия 59).
- Предыдущий: **E7.4-3a ВЫПОЛНЕН (сессия 58) — мнемоники ISA v1
  у ассемблера (s_mn 24; K3-E006 enc_f0 — F0: 1 байт; корпуса
  104/113; круги 10; якоря 24 + программы 5; артефакты
  38400 Б).** Подробно — 03b-HISTORY-E7 (сессия 58).
- Предыдущие: **E7.4-2a/2b/2c ВЫПОЛНЕНЫ (сессии 55-57) — ядро
  kernel.exe: контейнер .UP v2 (read_data, отказы LEN/RES/DATA),
  ALU v1 mul/div/mod/sra + ловушка 7 (udivmod) и call/ret +
  аппаратный стек вызовов 1024 (ловушка 5) — ISA v0+v1 исполнена
  ядром полностью (T-E7-32/33/34; батарея 176 -> 179/179).**
  Подробно — KERNEL/L3-UNIVM/VERIFY.md §3 и DOCS/03b-HISTORY-E7.
- Предыдущий: **E7.4-1 ВЫПОЛНЕН (сессия 54 — ISA v1 + .UP v2: оракул
  («сначала истина семантики»); ядро/ассемблер — срезы E7.4-2/3.**
  SPEC/12 v0+v1: опкоды 13..18 — mul/div/mod/sra (F1; rb = 0 —
  ловушка 7), call (F3) и ret (НОВЫЙ формат F0 — 1 байт без полей);
  АППАРАТНЫЙ стек вызовов глубины 1024 (ловушка 5; состояние
  управления, как PC); конвенция sp = r13 (программный стек в RAM,
  растёт вниз). SPEC/13 v1/v2: dataoff (резерв -> смещение данных),
  секция данных -> RAM[0:datalen], отказы LEN/RES/DATA (v1-порядок
  сохранён байт-в-байт); без .data выход ассемблера — v1.
  Оракул: lab_vm.py (+6 опкодов/стек/.data; FMT_OF из реестра OPS)
  + НОВЫЙ lab_up.py (контейнер — по лимиту 500); батарея — НОВЫЕ
  T-E7-26..31 (170 → 176/176): якоря 6 опкодов (ручные),
  семантика mul/div/mod/sra (24 шага), демо-факториал 5 рекурсией
  («U-VM1-OK 78», 188 шагов; n — программный стек r13), ловушки 5/7
  (самовызов call — 1024 шага), секция данных («U-DATA-OK 61»,
  89 шагов), детерминизм. Корпуса секции 13 — НОВЫЙ
  lab_t_vm_corpus.py (по лимиту 500). KERNEL не менялся (группа 2
  батареи — CI); корпуса T-E7-11/13 адаптированы (версия 3,
  опкод 0x19 — вне 01..18). Кирпичей не добавлено (ядро — срез 2).
  Далее — E7.4-2 (ядро). Подробно — DOCS/03b-HISTORY-E7 (E7.4-1).
- Предыдущий: **E7.3-4 ВЫПОЛНЕН (сессия 53) — F3: jmp/jnz + метки;
  ЭТАП 7.3 ЗАКРЫТ (DoD: T-E7-25 — якоря + программы == оракулу).**
  5 кирпичей (B001..B004, E005) + ветвь B; корпуса 85/97/4, круги 8;
  батарея 169 → 170; uva.exe 37888 Б. Подробно — 03b-HISTORY-E7.
- Предыдущий: **E7.3-3 ВЫПОЛНЕН (сессия 52) — F2: const + память.**
  2 кирпича (T008/E004); корпуса 65/72; uva.exe 21504 Б. Подробно —
  03b-HISTORY-E7.
- Предыдущий: **E7.3-2 ВЫПОЛНЕН (сессия 51) — ассемблер uva.exe: таблица
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
- Прочее закрытое: E7.2-2/2F/3 (регистры+ALU и фикс дефекта №23
  wall.exe pp_pcount — якорь T-E6-61; память и устройства), E6.4d
  (самохостинг wall — фикс-пункт T-E6-49a/49b, ~548 млн шагов),
  E0-E6.4c/g (семя..конвейер, WALL v1/v2 + инструменты wall/enc/
  splice/brick, пределы конвейера). Полная история — DOCS/03-ROADMAP
  «Выполнено», DOCS/03a-HISTORY.md (E0..E6.4), DOCS/03b-HISTORY-E7.md
  (этап 7), LAB/ai/JOURNAL (сессии 1-58).
