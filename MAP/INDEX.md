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
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач (+мост L5: E9.1 строка «превратить EXE в исходник» + строки «кирпич/пересборка bridge.exe» (ветви D/W спуска — E9.2-2; рендер-имена — lab_bridge_text) + строка «якоря моста» (E9.3) + строка «FF /4 / декодер моста» (E9.4-1) + секция 18d/таблицы переходов (E9.4-2) + строка «разобрать произвольный PE32+» (E9.4-3a — сессия 78) + строка «спуск в чужом теле» (E9.4-3b) + строка «собрать чужой EXE из PEG v2» (E9.4-3c-1 — сессия 80) + строки «эмиссия PEG v2» (E9.4-3c-2 — сессия 81) и «эмитить b2 ЧУЖОГО ТЕЛА» (E9.4-3c-3 — сессия 82); строка «найти файл лаборатории» — MAP/INDEX-LAB, сессия 77; батарея 242; проекты/секция 17 — E8.3; ветви L4 — E8.2a..2d; этап 7 — E7.2..E7.4-4) | 140 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+: статусы, DoD и очередь (сессия 77: детальные записи закрытых этапов — указатели на 03-серии — 03a2; ЭТАП 9: E9.1/E9.2/E9.3 ЗАКРЫТЫ; E9.4 — срезы 1-2, 3a-3c-3, 4a и 4b-1/4b-2: FF /4 (75), таблицы (76), разбор/спуск/PEG v2 чужих (78-82), ПОРТ decff/jtab/push_tgt (83 — 4a), развилка «семья | чужой» (84 — 4b-1), ПОРТ ЭМИССИИ b2 ЧУЖОГО ТЕЛА (85 — 4b-2 [x]); E9.4-4b-3 (86), 4b-4 (87 — ПОРТ wrap2 В pegen.exe, ветвь v2 M0-PEGEN); дальше — E9.4-4b-5+ ПЕРВЫЙ ЧУЖОЙ КРУГ — DoD этапа E9.4) | 288 |
| `DOCS/03a-HISTORY.md` | детальная история выполненных этапов E0..E6.4, часть 1 (раздел 03a/03b при превышении 500 строк — сессия 51; часть 2 — 03a2, сессия 77) | 320 |
| `DOCS/03a2-HISTORY.md` | детальная история этапов 5..6.4, ЧАСТЬ 2 серии 03a: записи, перенесённые из DOCS/03-ROADMAP.md (этапы 5/5a/6.4c/6.4e/6.4d) и README.md (блоки статуса E6.4c..E6.4d) при возврате их под лимит 500 строк — сессия 77; перенос байт-в-байт | 446 |
| `DOCS/03b-HISTORY-E7.md` | детальная история этапа 7 — UNIVM/ассемблер (E7.1..E7.4 ЗАКРЫТЫ; E7.4-1 — оракул; E7.4-2a/b/c — ядро (записи сжаты в указатели на VERIFY ядра — сессия 58); E7.4-3a — мнемоники v1, сессия 58; E7.4-3b — .data/.UP v2, сессия 59; E7.4-4 — ПРИЁМКА DoD — ЭТАП 7.4 ЗАКРЫТ, сессия 60) | 492 |
| `DOCS/03c-HISTORY-E8.md` | детальная история этапа 8 — Библиотека L4 (E8.1 — SPEC/14 + оракул + секция 16, сессия 61; E8.2a — ветвь C, сессия 62; E8.2b — ветвь N: стек-конвенция + зависимость N→C, сессия 63; E8.2c — ветвь S, сессия 64; E8.2d — ветвь M: LIB-1 целиком, сессия 65; E8.3 — демо-программы DoD, ЭТАП 8 ЗАКРЫТ, сессия 66) | 500 |
| `DOCS/03d-HISTORY-E9.md` | детальная история этапа 9, ЧАСТЬ 1 (E9.1 — SPEC/15 + оракул + секция 18, сессия 67; E9.2-1 — КАРКАС, сессия 68; E9.2-2 — СПУСК: декодер + тени + target/bss, 16 кирпичей K5-D*/W*, синтетика теней T-E9-21, 2 дефекта + уроки, сессия 69) | 329 |
| `DOCS/03e-HISTORY-E9.md` | детальная история этапа 9, ЧАСТЬ 2 — срезы эмиссии и якоря (E9.2-3a/b/c + E9.2-4 PEG-выход — ЭТАП E9.2 ЗАКРЫТ, сессии 70-73; E9.3-1 — ЭТАП E9.3 ЗАКРЫТ, сессия 74; сессия 75 (E9.4-1) перенесена в 03f при возврате 03e под лимит 500 — сессия 77) | 449 |
| `DOCS/03f-HISTORY-E9.md` | детальная история этапа 9, ЧАСТЬ 3 — срезы E9.4 (сессии 75-79: E9.4-1 FF /4 + секция 18c — перенесено из 03e, сессия 77; E9.4-2 — таблицы переходов в оракуле + T-E9-27/секция 18d + рендер-ветвь lab_bridge_text, сессия 76; E9.4-3a — произвольный PE32+ в оракуле + T-E9-28/секция 18e, сессия 78; E9.4-3b — спуск в чужом теле parse_foreign + T-E9-29/секция 18f, сессия 79; сессия 80 открыла ЧАСТЬ 4 — 03g) | 411 |
| `DOCS/03g-HISTORY-E9.md` | детальная история этапа 9, ЧАСТЬ 4 — срезы E9.4-3c+..4b-1 (сессии 80-84; продолжение 03f по лимиту 500 строк — прецедент 03e/03f; E9.4-3c-1 — PEG v2 оракул- сборщик + T-E9-30; E9.4-3c-2 — эмиссия PEG v2 + T-E9-31; E9.4-3c-3 — b2 чужого тела + T-E9-32; E9.4-4a — ПОРТ FF /4 и таблиц; E9.4-4b-1 — развилка + чужие факты) | 469 |
| `DOCS/03h-HISTORY-E9.md` | детальная история этапа 9, ЧАСТЬ 5 — срезы E9.4-4b+ (сессии 85+; открыта сессией 85 при возврате 03g под лимит 500 — прецедент 03f/03g; сессия 85 — E9.4-4b-2: ПОРТ ЭМИССИИ b2 ЧУЖОГО ТЕЛА; E9.4-4b-3 — сессия 86: ПОРТ PEG v2; E9.4-4b-4 — сессия 87: ПОРТ wrap2 в pegen.exe — ветвь v2, компоновка bss, T-M5-18) | 245 |
| `DOCS/04-RULES-OF-CHANGE.md` | регламент изменений и коммитов | 59 |

## SPEC/ — формальные спецификации

| Файл | Роль | Строк |
|---|---|---|
| `SPEC/00-GLOSSARY.md` | словарь терминов, регистры | 49 |
| `SPEC/01-METHOD-CARD.md` | формат карточки кирпича | 57 |
| `SPEC/02-LAYER0-SPEC.md` | правила слоя L0, верификация | 57 |
| `SPEC/03-ATOM-FORMAT.md` | грамматика формата ATOM v1 | 81 |
| `SPEC/04-PE-MINIMAL.md` | структура наших EXE, инварианты | 138 |
| `SPEC/05-X86-SUBSET.md` | реестр инструкций и кодировок (+ расширение E9.4: FF /4 — косвенный jmp r64/[r/m64]) | 274 |
| `SPEC/06-ARCHITECTURE.md` | целевая архитектура системы | 72 |
| `SPEC/07-PEG-FORMAT.md` | формат PEG v1/v2 и поведение pegen (v2 — E9.4-3c-1 «Рост v2» + E9.4-3c-2 «Канон патчей» (эмиссия emit_peg_v2): чужие образы = нули + патчи — область заголовков !hdr/маркер !pev2 <H> первой директивой, тело секции кода !body, патчи прочих секций !sec; сборка wrap2 — самоописание структуры; канон сворачивания в патчи — для эмиссии E9.4-3c-2; ПОРТ ЭМИССИИ В bridge.exe — E9.4-4b-3; ПОРТ СБОРЩИКА wrap2 В pegen.exe — E9.4-4b-4; E9.5-1a — ПРЕДЕЛЫ ИНСТРУМЕНТА ПОДНЯТЫ (тело 1 МиБ/peg-текст 4 МиБ/outbuf 4 МиБ/спаны 256/записи 16384/секданные 1 МиБ) + раздел «Дефекты» — 3 закрытых дефекта v2-ветви сессии 87) | 250 |
| `SPEC/08-BRICK-FORMAT.md` | формат BRICK v1 и поведение brick (слой L1; пределы 512 КиБ/2048 меток — E6.4f-2) | 160 |
| `SPEC/09-ENC-FORMAT.md` | BRICK v2: M-строки, канонические кодировки, контракт enc (предел входа 2 МиБ — E6.4g-5) | 254 |
| `SPEC/10-SPLICE-FORMAT.md` | SPLICE v1: !include, склейка исходников, контракт splice (пределы 256 КиБ, E6.4e-2) | 148 |
| `SPEC/11-WALL-FORMAT.md` | WALL v1/v2: язык слоя L2, компиляция в BRICK v2, канон эмиттера | 409 |
| `SPEC/12-UNIVM-ISA.md` | UNIVM ISA v0+v1: модель, форматы F0..F3, 24 инструкции, стек вызовов + конвенция sp = r13, ловушки 1-5/7, окно устройств (E7.1; v1 — E7.4-1) | 260 |
| `SPEC/13-UP-FORMAT.md` | контейнер .UP v1/v2: заголовок 24 Б + код (+секция данных dataoff — E7.4-1), пределы, отказы | 146 |
| `SPEC/14-L4-LIBRARY.md` | Библиотека L4 (E8.1; уточнение положения !include — E8.2a): композиция программы+библиотеки (!include через splice), ABI вызова, слой LIB-1 — числа/строки/память (11 кирпичей) | 176 |
| `SPEC/15-BRIDGE-FORMAT.md` | Мост BRIDGE v1 (E9.1): EXE семейства -> BRICK v2 + PEG v1 — контракт входа, обнаружение кода (п. 3: косвенный FF /4 — терминал; таблицы переходов [rip+X] — цели-кандидаты из данных, E9.4-2), метки l/d/iat_, M-строки при точном воспроизведении enc (иначе H-фолбэк), данные импортов DD/DQ, длина тела/!bss, регенерация PEG, круг; п. 11 — якоря репозитория (E9.3); п. 10 — срезы E9.2..E9.4-4b-2 (E9.4-3b — parse_foreign: спуск в чужом теле + факты PEG v2; E9.4-3c-1 — PEG v2 оракул-сборщик: SPEC/07 «Рост v2» + wrap2 + T-E9-30; E9.4-3c-2 — PEG v2 ЭМИССИЯ МОСТОМ: emit_peg_v2 — канон патчей SPEC/07 + T-E9-31; E9.4-3c-3 — b2 чужого тела + T-E9-32; E9.4-4a — ПОРТ FF /4 и таблиц в bridge.exe: decff/jtab/push_tgt — T-E9-26/27 с инструментом; E9.4-4b-1 — развилка «семья | чужой» + чужие факты; E9.4-4b-2 — ПОРТ ЭМИССИИ b2 ЧУЖОГО ТЕЛА: base = codevaddr, rva_file, fimp_walk, шапка ftplb, M=/H=; E9.4-4b-3 — ПОРТ PEG v2: peg2_check (H/покрытие raw ДО спуска — отказ без частичных выходов), gtpl_dec/fold_emit/emit_peg2 — оба выхода чужого пути == оракулу) | 476 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл (карта системы; сессия 77 — таблица LAB выделена в MAP/INDEX-LAB.md по лимиту 500 строк) | 447 |
| `MAP/INDEX-LAB.md` | карта файлов внешней лаборатории LAB со счётчиками строк (выделена из INDEX.md — сессия 77; срезы моста E9.4-3a..3c-3: +lab_t_bridge_pe/foreign/peg2/peg2e/b2f — сессии 78-82; фикс битой строки 68/69 — сессия 82) | 126 |
| `MAP/METHODS.md` | указатель реестра кирпичей, часть 1: K0..K3 (437 строк реестра: K0 116 / K1 132 / K2 120 / K3 70; K4/K5 — METHODS-2.md; разрез по лимиту 500 — E9.2-1) | 483 |
| `MAP/M0-SEED.md` | карточки кирпичей M0-SEED (8) | 130 |
| `MAP/M0-SEED2.md` | карточки кирпичей M0-SEED2 (19) | 299 |
| `MAP/M0-HXDUMP.md` | карточки кирпичей M0-HXDUMP (23) | 360 |
| `MAP/M0-HEXGEN.md` | карточки кирпичей M0-HEXGEN (29) | 452 |
| `MAP/M0-PEGEN.md` | карточки кирпичей M0-PEGEN v1 (37; v1-ветвь — разрез по лимиту 500, сессия 87) | 500 |
| `MAP/M0-PEGEN-V.md` | карточки кирпичей ветви PEG v2 M0-PEGEN (14: Q012..Q019, E005..E007, G043, D047/D048 — E9.4-4b-4) | 202 |
| `MAP/M1-BRICK.md` | карточки кирпичей M1-BRICK (42) | 480 |
| `MAP/M1-ENC.md` | карточки кирпичей M1-ENC (поток и разбор) | 411 |
| `MAP/M1-ENC-E.md` | карточки ветви E модуля M1-ENC (кодирование, 23; E033 imul — E6.4c) | 310 |
| `MAP/M1-ENC-S.md` | служебные ветви M1-ENC: H/U/F/D (14) | 193 |
| `MAP/M1-SPLICE.md` | карточки кирпичей M1-SPLICE (27) | 431 |
| `MAP/M2-WALL.md` | карточки кирпичей M2-WALL (107) | 500 |
| `MAP/M3-UNIVM.md` | карточки кирпичей M3-UNIVM — ветви C/U/M/J/X (19; срезы E7.2-1..4 + E7.4-2a/b/c; ветвь V — в M3-UNIVM-V.md по лимиту 500, прецедент M1-ENC-E/S) | 332 |
| `MAP/M3-UNIVM-V.md` | карточки кирпичей M3-UNIVM — ветвь V (интерпретатор, 21: +ALU v1 K3-V112..V116 — E7.4-2b; +стек вызовов K3-V117/V118 — E7.4-2c, часть call) | 335 |
| `MAP/M3-UVA.md` | карточки кирпичей M3-UVA — ассемблер .uva -> .UP (30: ветви C/T/B/L/E/W/X; срезы E7.3-1..4 + мнемоники v1 E7.4-3a + .data/.UP v2 E7.4-3b — НОВЫЙ K3-T009 data_next) | 489 |
| `MAP/M4-LIB.md` | карточки кирпичей M4-LIB — библиотека L4 (11: ветви C/N/S/M — слой LIB-1; C — готов E8.2a, N — E8.2b, S — E8.2c, M — план) | 197 |
| `MAP/METHODS-2.md` | указатель реестра, часть 2: слои L4/L5 (K4 — 11 библиотека; K5 — 132 мост M5-BRIDGE — E9.2-1/2/3a/3b/3c/4 + E9.4-4a/4b-1/4b-2/4b-3; карточки C/P/X — M5-BRIDGE.md, D/W — M5-BRIDGE-D.md, E — M5-BRIDGE-E.md, L — M5-BRIDGE-L.md, M — M5-BRIDGE-M.md, G — M5-BRIDGE-G.md) | 156 |
| `MAP/M5-BRIDGE.md` | карточки кирпичей M5-BRIDGE — мост BRIDGE v1, часть 1 (26: ветвь C — сервис 8, ветвь P — разбор PE/семейство 17 + X — вход; каркас E9.2-1; спуск — M5-BRIDGE-D.md) | 498 |
| `MAP/M5-BRIDGE-D.md` | карточки кирпичей M5-BRIDGE, часть 2 — СПУСК+ОПЕРАНДЫ (26: ветвь D — декодер SPEC/05, 23 — E9.2-2 длины/классы/цели + E9.2-3a полные операнды: modrm_read/setters/u32/u64; ветвь W — walk/sweep(+sdump)/target, 3) | 424 |
| `MAP/M5-BRIDGE-E.md` | карточки кирпичей M5-BRIDGE, часть 3 — ПРИМИТИВЫ ЭМИССИИ E9.2-3a (17+1 снят: ветвь E — таблицы имён/шапка-HEX/форматтеры/примечания == _note/H-строки/DZ/DB; K5-E018 emit_raw снят в E9.2-3b — драйвер переехал в ветвь L) | 321 |
| `MAP/M5-BRIDGE-L.md` | карточки кирпичей M5-BRIDGE, часть 4 — МЕТКИ И СЕМАНТИКА E9.2-3b (17: ветвь L в двух частях l/l2 — записи импортов/san-блоб/метки iat_/d* с правилом представимости, DD/DQ с приёмкой, метки операндов l*/d*, разрезы, драйвер emit_body — канон: m_line ПЕРЕД emit_h с E9.2-3c) | 283 |
| `MAP/M5-BRIDGE-M.md` | карточки кирпичей M5-BRIDGE, часть 5 — M-СТРОКИ КАНОНА E9.2-3c (28: ветвь M в четырёх частях m/m2/m3/m4 — примитивы кодировки mbuf/сверка m_cmp со слотом, рендер операндов m_opr/m_opmem/$имя/kw, кодировщики всех семейств enc (SIMPLE/jmp/jcc/call/movzx/push/pop/test/lea/imul/сдвиги/neg/idiv/inc/dec/ALU/mov), драйверы m_body/m_line) | 461 |
| `MAP/M5-BRIDGE-G.md` | карточки кирпичей M5-BRIDGE, часть 6 — PEG-ВЫХОД (E9.2-4 семья: 2 — ptpl_dec/emit_peg, PEG v1 == _peg_text; E9.4-4b-3 чужой путь: 4 — gtpl_dec/peg2_check/fold_emit/emit_peg2, PEG v2 == _peg2_text — канон патчей !pev2/!hdr/!body/!sec; буфер outmem переиспользуется) | 156 |
| `MAP/LAYERS.md` | реестр слоёв L0..L6 и их статусы (L3/L4 — готовы: ЭТАПЫ 7-8 ЗАКРЫТЫ; L5 — в работе: E9.2-2 спуск; L6 — старт) | 72 |

## KERNEL/ — ядро

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L0-SEED/CARD.md` | карточка модуля M0-SEED | 53 |
| `KERNEL/L0-SEED/seed.hex` | тело секции семени, ATOM v1 (истина) | 63 |
| `KERNEL/L0-SEED/seed.peg` | обёртка семени (PEG v1, SPEC/07) | 6 |
| `KERNEL/L0-SEED/seed.exe` | материализация: 1024 байта, PE32+ | — |
| `KERNEL/L0-SEED/seed.anchor.b2` + `seed.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=28 H=0) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11; генератор — LAB/ai/anchor_gen.py, регенерация — только намеренно) | 66/6 |
| `KERNEL/L0-SEED/BYTECODE.md` | байт-за-байтом разбор всего образа | 249 |
| `KERNEL/L0-SEED/VERIFY.md` | как проверить подлинность и работу | 80 |
| `KERNEL/L0-SEED2/CARD.md` | карточка модуля M0-SEED2 (командная строка) | 90 |
| `KERNEL/L0-SEED2/seed2.hex` | тело секции семени-2, ATOM v1 (истина) | 224 |
| `KERNEL/L0-SEED2/seed2.peg` | обёртка семени-2 | 6 |
| `KERNEL/L0-SEED2/seed2.exe` | материализация: 2048 байт, PE32+ | — |
| `KERNEL/L0-SEED2/seed2.anchor.b2` + `seed2.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=170 H=15) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 291/6 |
| `KERNEL/L0-SEED2/BYTECODE.md` | разбор образа: 185 инструкций, данные, импорты | 411 |
| `KERNEL/L0-SEED2/VERIFY.md` | проверка, журнал, пойманные ошибки | 96 |
| `KERNEL/L0-HXDUMP/CARD.md` | карточка модуля M0-HXDUMP (hex-дамп) | 91 |
| `KERNEL/L0-HXDUMP/hxdump.hex` | тело секции hxdump, ATOM v1 (истина) | 290 |
| `KERNEL/L0-HXDUMP/hxdump.peg` | обёртка hxdump | 8 |
| `KERNEL/L0-HXDUMP/hxdump.exe` | материализация: 3584 байта, PE32+ | — |
| `KERNEL/L0-HXDUMP/hxdump.anchor.b2` + `hxdump.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=230 H=10) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 352/8 |
| `KERNEL/L0-HXDUMP/BYTECODE.md` | разбор образа: 244 записи кода, данные, импорты | 497 |
| `KERNEL/L0-HXDUMP/VERIFY.md` | проверка, журнал, пойманные ошибки | 99 |
| `KERNEL/L0-HEXGEN/CARD.md` | карточка модуля M0-HEXGEN (первый компилятор) | 123 |
| `KERNEL/L0-HEXGEN/hexgen.hex` | тело секции hexgen, ATOM v1 (истина) | 421 |
| `KERNEL/L0-HEXGEN/hexgen.peg` | обёртка hexgen | 9 |
| `KERNEL/L0-HEXGEN/hexgen.exe` | материализация: 2560 байт, PE32+ (bss) | — |
| `KERNEL/L0-HEXGEN/hexgen.anchor.b2` + `hexgen.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=334 H=36) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 510/8 |
| `KERNEL/L0-HEXGEN/BYTECODE.md` | разбор образа: 370 записей кода, данные, импорты, виртуальные нули | 482 |
| `KERNEL/L0-HEXGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 116 |
| `KERNEL/L0-PEGEN/CARD.md` | карточка модуля M0-PEGEN (обёртка образов v1 + сборщик PEG v2 — E9.4-4b-4) | 164 |
| `KERNEL/L0-PEGEN/pegen.hex` | тело секции pegen, ATOM v1 (истина; E9.5-1a — ветвь v2 переизлучена, пределы подняты) | 928 |
| `KERNEL/L0-PEGEN/pegen.peg` | обёртка pegen (самосборка) | 9 |
| `KERNEL/L0-PEGEN/pegen.exe` | материализация: hexgen + pegen, 6144 байта (0x1800 — не растёт: рост пределов E9.5-1a в bss 0xA48C41, vsize 0xA4A18C), PE32+ | — |
| `KERNEL/L0-PEGEN/pegen.anchor.b2` + `pegen.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1; регенерирован E9.5-1a): канон BRICK v2 тела (M=857 H=196) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 1406/8 |
| `KERNEL/L0-PEGEN/BYTECODE.md` | сводка, карта кирпичей (v1 + v2), данные, импорты | 143 |
| `KERNEL/L0-PEGEN/VERIFY.md` | проверка, журнал (вкл. 7 классов ошибок порта v2), пойманные ошибки | 129 |
| `KERNEL/L1-BRICK/CARD.md` | карточка модуля M1-BRICK (ассемблер BRICK) | 153 |
| `KERNEL/L1-BRICK/brick.hex` | тело секции brick, ATOM v1 (истина E5a) | 671 |
| `KERNEL/L1-BRICK/brick.brick` | корень модуля M1-BRICK: шапка + !include трёх частей (разрез E6.3) | 7 |
| `KERNEL/L1-BRICK/brick_p1.brick` | часть 1: поток X/C/G, пассажи N, разбор директив A (5-483 строки тела) | 479 |
| `KERNEL/L1-BRICK/brick_p2.brick` | часть 2: лексика, метки, сервис H/G/U/C/F (484-744) | 261 |
| `KERNEL/L1-BRICK/brick_p3.brick` | часть 3: данные D — таблицы, импорты, bss (745-850) | 106 |
| `KERNEL/L1-BRICK/brick.peg` | обёртка brick (PEG v1, SPEC/07) | 9 |
| `KERNEL/L1-BRICK/brick.exe` | материализация: hexgen + pegen, 3584 байта, PE32+ | — |
| `KERNEL/L1-BRICK/brick.anchor.b2` + `brick.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=587 H=81) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 894/8 |
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
| `KERNEL/L1-ENC/enc.peg` | обёртка enc (PEG v1, SPEC/07) | 9 |
| `KERNEL/L1-ENC/enc.exe` | материализация: brick+pegen, 12288 байт, PE32+ (рост ISA E6.4c; предел входа 2 МиБ E6.4g-5) | — |
| `KERNEL/L1-ENC/enc.anchor.b2` + `enc.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=1678 H=326) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 2792/8 |
| `KERNEL/L1-ENC/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 156 |
| `KERNEL/L1-ENC/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.2 + рост ISA E6.4c + пределы E6.4e-1/E6.4f-1/E6.4d-4/E6.4g-5 | 134 |

| `KERNEL/L1-SPLICE/CARD.md` | карточка модуля M1-SPLICE (склейка !include) | 131 |
| `KERNEL/L1-SPLICE/splice.b2` | корень модуля M1-SPLICE: шапка + поток X/C/G + !include 3 частей | 137 |
| `KERNEL/L1-SPLICE/splice_s.b2` | часть: ветви S/N — цикл уровней, директива, вывод строки | 248 |
| `KERNEL/L1-SPLICE/splice_svc.b2` | часть: H/G/U/C/F — печать, ошибки, командная строка, файлы | 189 |
| `KERNEL/L1-SPLICE/splice_data.b2` | часть: D — таблицы, строки, импорты, bss | 120 |
| `KERNEL/L1-SPLICE/splice.brick` | плоская форма в BRICK v1 = enc(splice(splice.b2)) байт-в-байт (генерируемый артефакт) | 691 |
| `KERNEL/L1-SPLICE/splice.peg` | обёртка splice (PEG v1, SPEC/07) | 9 |
| `KERNEL/L1-SPLICE/splice.exe` | материализация: brick+pegen, 3584 байта, PE32+ (пределы 256 КиБ E6.4e-2) | — |
| `KERNEL/L1-SPLICE/splice.anchor.b2` + `splice.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=432 H=47) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 653/8 |
| `KERNEL/L1-SPLICE/BYTECODE.md` | сводка образа, карта кирпичей, данные, импорты, история образа | 124 |
| `KERNEL/L1-SPLICE/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.3, история пределов | 111 |
| `KERNEL/L2-WALL/CARD.md` | карточка модуля M2-WALL (компилятор WALL v1/v2) | 208 |
| `KERNEL/L2-WALL/wall.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E6.4d-5/3-2; E7.2-2F): выход wall.exe(wall.wall), плоский, 1011099 Б — T-E6-49a | — |
| `KERNEL/L2-WALL/wall.wall` | само-исходник на WALL v2 — КОРЕНЬ с разрезом SPEC/10 (E6.4d-2/3..4/3c-3): ext/var/str + main + 18 частей; CLI == wall.exe, чтение, GlobalAlloc, проходы 0/1 + проход 2 (срезы A..C-3) | 338 |
| `KERNEL/L2-WALL/wall_self_c.wall` | часть каркаса: сервис — print_error/skip0/read_arg/widen (E6.4d-1) | 147 |
| `KERNEL/L2-WALL/wall_self_n.wall` | часть каркаса: проход 0 на WALL (E6.4d-2/2) — stq, fail_format, lex_line, pass0; карта текстов smem | 262 |
| `KERNEL/L2-WALL/wall_self_pe.wall` | часть каркаса: хелперы прохода 1 (E6.4d-2/3..3/2) — getq, tok_next, kw_lookup, chk_name, names_find/_ci/add, local_find (P008), max2/tok_is1 (экономия меток), arr_size, at_end/want_id/want_sym1; таблицы tabmem | 434 |
| `KERNEL/L2-WALL/wall_self_ph.wall` | часть каркаса: уровни выражений стат-режимом (E6.4d-3/2) — p_expr (P010), p_mul (P011), p_mdm (P01A), p_unary (P012); курсор pcur/ple | 317 |
| `KERNEL/L2-WALL/wall_self_pp.wall` | часть каркаса: первичные + индексация (E6.4d-3/2; эмит-плечи E6.4d-4/3c-2/1..2/2) — p_prim (P013: откат outcur + перепознание базы d+k), pp_prim0 (P013a: число/скобки/&имя/getb/len/вызов/имя), pp_pcount (P01B; фикс №23 E7.2-2F: двухсимвольный оператор глубины 0 — завершитель скана), pp_pairs (P01C: статы + эмит T-склад/хвост), pp_strchk (P01E) | 302 |
| `KERNEL/L2-WALL/wall_self_pa.wall` | часть каркаса: вызовы и astore-проверка (E6.4d-3/2; эмит-механика E6.4d-4/3c-2/2) — p_args (P014: стейджинг после каждого аргумента; фикс №19+№21), pa_stage (P017: C(base+cnt+1)/S5), p_call_tail (P015), emit_argload, call_stats (P016), astore_chk (P01D; фикс №22: копия lay-окна — только стат pc_mode == 0) | 261 |
| `KERNEL/L2-WALL/wall_self_pc.wall` | часть каркаса: условие if/while (E6.4d-3/3; эмит-плечо C-3) — p_cond (P018: стат — сравнения, '&&'/'`\|\|`', maxd, v2flag; эмит — m-скан дизъюнктов, операнды на глубине 2 + T1-склад + «M cmp r10, r11» + jcc-инверсии + d/t-метки; параметры pfx/e/k) | 192 |
| `KERNEL/L2-WALL/wall_self_pd.wall` | часть каркаса: объявления + заголовки func прохода 1 (E6.4d-2/3..2/4) — p1_decl (S003): var/str/ext; p1_funchdr (S004) + fh_param (S00E): larr/bstk/ftab; окно дублей — local_find | 208 |
| `KERNEL/L2-WALL/wall_self_p1.wall` | часть каркаса: каркас прохода 1 (E6.4d-2/3..3/3) — p1_line (S002: func -> S004, fcur -> S006/S007/S008/S009/S00A/S00B/S00C/S00F/S00D), pass1 (S001) + пост-проверка main + сброс ifseq, set_lastline | 152 |
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
| `KERNEL/L2-WALL/wall.peg` | обёртка — КОНСТАНТА SPEC/11 п.6 (!module wall; вход 1200, idata 1000 28, iat 1028 48; E6.4d-5/3-2) | 8 |
| `KERNEL/L2-WALL/wall.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+wall.peg — 87040 Б, вход 0x1200, импорты-восьмёрка (CreateFile2+GlobalAlloc); SHA-256 B2AC45F4… (E7.2-2F) — T-E6-49b | — |
| `KERNEL/L2-WALL/wall.anchor.b2` + `wall.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=17285 H=479; 497 КиБ) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 18975/8 |
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
| `KERNEL/L3-UNIVM/kernel_self_c.wall` | часть ядра: сервис — print_error, skip0, read_arg, check_end (не более двух аргументов), widen, read_lim (предел шагов — 2-й аргумент CLI, E7.2-4) | 231 |
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
| `KERNEL/L3-UNIVM/kernel.anchor.b2` + `kernel.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=5627 H=0 — 100% M) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 6002/8 |
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
| `KERNEL/L3-UVA/uva.anchor.b2` + `uva.anchor.peg` | ЯКОРЬ выхода моста (E9.3-1): канон BRICK v2 тела (M=5509 H=0 — 100% M) + PEG v1 == оракулу байт-в-байт (T-E9-25; SPEC/15 п. 11) | 6007/8 |
| `KERNEL/L3-UVA/BYTECODE.md` | карта образа ассемблера: сводка, 30 функций (RVA, +data_next — E7.4-3b), данные, инварианты | 118 |
| `KERNEL/L3-UVA/VERIFY.md` | подлинность + уровни проверки + журнал срезов (E7.3-1..4; дефект оракула №24 закрыт; E7.4-3a — мнемоники v1; E7.4-3b — .data/.UP v2) | 326 |

### KERNEL/L4-LIB — библиотека L4 (E8.2a/b/c/d: все ветви C, N, S, M готовы — слой LIB-1 целиком)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L4-LIB/CARD.md` | карточка модуля M4-LIB: рецепт композиции программа+библиотека (!include ПОСЛЕ кода — E8.2a), состав ветвей + ЗАВИСИМОСТЬ N→C и стек-конвенция (E8.2b) + АВТОНОМНОСТЬ ветвей S (E8.2c) и M (E8.2d), ABI, верификация + DoD этапа 8 закрыт (E8.3 — проекты banner/fib, секция 17) | 152 |
| `KERNEL/L4-LIB/lib_c.uva` | ветвь C — консоль: K4-C001 chr_out / K4-C002 crlf_out / K4-C003 buf_out / K4-C004 buf_out_rev (метки lib_*, только r1..r4 — временные ABI; E8.2a) | 46 |
| `KERNEL/L4-LIB/lib_n.uva` | ветвь N — числа: K4-N001 u64_to_dec_rev (цикл div/mod 10, len = p−addr) / K4-N002 print_u64 (N001 + C004) / K4-N003 print_i64 (C001 + N001 + C004; знак lt, модуль 2^64−v в r4 до печати знака); стек-слоты [sp-8,sp) — конвенция SPEC/12 п. 3.4 (E8.2b) | 77 |
| `KERNEL/L4-LIB/lib_s.uva` | ветвь S — строки: K4-S001 str_len (цикл ldb до NUL, len = p−addr) / K4-S002 str_out (ldb → stb-консоль до NUL); АВТОНОМНАЯ ветвь — без зависимостей (одно !include) и без стека (r13 не нужен, r14 — только str_out; E8.2c) | 45 |
| `KERNEL/L4-LIB/lib_m.uva` | ветвь M — память: K4-M001 mem_copy (цикл ldb → stb ПО ВОЗРАСТАНИЮ адресов — формула SPEC/14 п. 4 задаёт перекрытия) / K4-M002 mem_fill (цикл stb, r2 AND 255); АВТОНОМНАЯ ветвь как S — без зависимостей, БЕЗ стека (r13 не нужен) и БЕЗ консоли (r14 не нужен — эффект в RAM; E8.2d) | 40 |

### KERNEL/L5-BRIDGE — мост BRIDGE v1 (E9.2-1 каркас + E9.2-2 спуск + E9.2-3a/b/c эмиссия + E9.4-4b-1 развилка «семья | чужой»)

| Файл | Роль | Строк |
|---|---|---|
| `KERNEL/L5-BRIDGE/CARD.md` | карточка модуля M5-BRIDGE (мост BRIDGE v1: E9.2-1 каркас — CLI/чтение/разбор PE/семейство/импорты; E9.2-2 спуск — декодер SPEC/05 + тени + target/bss; E9.2-3a — полные операнды декодера + примитивы вывода; E9.2-3b — метки l/d/iat_ + семантика DD/DQ + разрезы + драйвер emit_body; E9.2-3c — M-строки канона (ветвь M: точное воспроизведение enc — m_cmp со слотом, иначе H-фолбэк) + факт-строка с выходом M=/H=; E9.2-4 — PEG-выход (ветвь G: запись <выход>.peg == _peg_text оракула) — ЭТАП E9.2 ЗАКРЫТ; E9.4-4a — ПОРТ FF /4 + таблиц (decff/jtab/push_tgt); E9.4-4b-1 — РАЗВИЛКА «семья | чужой» (check_head общий фронт / fam_chain предикат / foreign_front / print_ffacts — чужая факт-строка FOREIGN, файлы не пишутся); отказы — коды 2..9); E9.4-4b-3 — PEG v2 чужого пути (peg2_check/gtpl_dec/fold_emit/emit_peg2: ОБА выхода) | 246 |
| `KERNEL/L5-BRIDGE/bridge.wall` | корень с разрезом (SPEC/10): 8 ext, 68 var (СКАЛЯРЫ ПЕРВЫМИ; массивы в конце: arg1/arg2/arg3[16], factbuf[24], o_mn/o_cc/o_r64/o_r8/o_r16/o_r32/o_kw[5], tplb[25], mbuf[24], ptplb[9], w1[64] ПОСЛЕДНИМ — хвост !bss падает внутрь него, 0 H-строк — урок E9.2-2, ОБЩЁН E9.2-3b, сохранён с E9.2-4), 55 str (вкл. NUL-блобы имён, kw-слова, HEX-шапки s_tpl/s_ptpl и PEG-префиксы E9.2-4), main (CLI → чтение → общий фронт → РАЗВИЛКА «семья | чужой»: семья → проверки → спуск → таблицы → карты (L) → эмиссия .b2 КАНОН (M/H) → PEG-выход (G) → факты M=/H=; чужой → фронт P2 → импорты/секции (fimp_walk/count_sects — E9.4-4b-2) → спуск → карты (base = codevaddr) → эмиссия .b2 ЧУЖОГО ТЕЛА → PEG v2 (emit_peg2 — E9.4-4b-3) → факты FOREIGN + M=/H=; 114 var (97 скаляров + 17 массивов, ПОСЛЕДНИЙ w1 — инвариант 0 H-строк; +dllcnt/sectcnt — E9.4-4b-2, +peg2h/gtplb — E9.4-4b-3), 63 str (+s_ftpl — HEX-шапка чужого b2, E9.4-4b-2; +s_gtpl/s_gdll/s_gpev/s_ghdr/s_gbody/s_gsec — PEG v2, E9.4-4b-3) | 443 |
| `KERNEL/L5-BRIDGE/bridge_self_c.wall` | ветвь C — сервис: print_error, skip0, read_arg, check_end (ровно 3 аргумента), widen (ANSI → UTF-16LE), copy_str, out_dec, out_hex (8 ЗАГЛАВНЫХ hex-цифр) — реинкарнации K3-C* | 235 |
| `KERNEL/L5-BRIDGE/bridge_self_pe.wall` | ветвь P, ЧАСТЬ 1 (E9.4-4b-1) — ОБЩИЙ фронт + семейные проверки-ПРЕДИКАТ (0/1): rd16/rd32, fail_family (ОБЩИЙ отказ 6), guard (0/1), check_head (MZ + PE-сигнатура + раскладка полей ОТ e_lfanew: lfanew/coffoff/optoff/sizopt/numsect/tbloff — как lab_pe.parse), check_opt/base/sect/size/body (инварианты SPEC/04 — вычисляемые смещения; codevaddr/falign/fend — в check_sect), stub_name (имя 1..31 без пробельных байтов) | 286 |
| `KERNEL/L5-BRIDGE/bridge_self_pi.wall` | ветвь P, ЧАСТЬ 2 (разрез pe по лимиту 500 — E9.4-4b-1) — импорты семейства + цепочка + факты: rva_off, walk_descs (IDT по DD[1] @optoff+0x78), cstr_len (quirk len-1), check_dll, walk_funcs (чётность hint) — ПРЕДИКАТЫ; fam_chain (K5-P018: 0 = семейство, 1 = нет — развилка в main), print_facts (INS/TARGET/BSS + ВЫХОД M=/H= — E9.2-3c) | 274 |
| `KERNEL/L5-BRIDGE/bridge_self_pf.wall` | ветвь P, ЧАСТЬ 3 — ЧУЖОЙ ПУТЬ (E9.4-4b-1): foreign_front (K5-P019 — порт parse_foreign: Machine/Magic, FileAlignment степень 2, секция кода ПО ТОЧКЕ ВХОДА, EXECUTE, файл покрывает raw, тело не нулевое, вход в raw-части; глобали спуска от секции кода), print_ffacts (K5-P020 — чужая факт-строка FOREIGN=1 SECT=… == parse_foreign; файлы .b2/.peg не пишутся — срезы 4b-2+) | 264 |
| `KERNEL/L5-BRIDGE/bridge_self_d.wall` | ветвь D — декодер, часть 1 (E9.2-2/3a): fb, rel8/rel32, u32/u64 (беззнаковые чтения), modrm_read (ПОЛНЫЙ modrm+SIB+disp: reg/память/rip — E9.2-3a), setters операндов set_reg/set_rm/set_imm/set_immu/set_tgt/set_cl/set_cnt, alu_id, dec0f (jcc/movzx/imul — с операндами), decalu, decmod — K5-D001..D007, D014..D023 | 449 |
| `KERNEL/L5-BRIDGE/bridge_self_d2.wall` | ветвь D — декодер, часть 2 (E9.2-2/3a + E9.4-4a): decimm (push/pop/cdqe/cqo/mov r,imm — imm64 вид 7/ret/int3), decshift (C0/C1/D3 — счётчик-маска 63/31), decgrp (80/81/83), decgrp2 (C6/C7/F6/F7; FF — делегация в decff), decbr (E8/E9/EB/70..7F — dtgt/dcc), decode_ins (диспетчер == lab_x86.decode; операнды da1*/da2*/om*; omrip = конец+disp32) — K5-D008..D013 | 486 |
| `KERNEL/L5-BRIDGE/bridge_self_d3.wall` | ветвь D — декодер, часть 3 — ГРУППА FF (E9.4-4a, сессия 83): decff — peek modrm -> ext с REX.R ДО modrm_read; /0 inc /1 dec /2 call; /4 jmp r/m64 КОСВЕННЫЙ (размер ВСЕГДА 64, dcls 5 — терминал спуска; операнд — рег/память) — K5-D024 | 75 |
| `KERNEL/L5-BRIDGE/bridge_self_w.wall` | ветвь W — спуск от входа (E9.2-2/3a + E9.4-4a): push_tgt (цель в стек — ДЕДУПЛИКАЦИЯ по значению: карта pushmap, предел pend 1+rawlim — 262145 qword), jtab (таблицы переходов: jmp qword [rip+X] — qword-строки «до первого non-code qword» -> кандидаты, == _jtab), walk_code (стек целей 2097160 + карты insmap/lenmap/pushmap 262145; rawlim = min(vsize, raw); терминалы/нули; dcls 5 — терминал + jtab), sweep_ins (тени — младший адрес; inscount/maxend + СДАМП sdump — E9.2-3a), calc_target (target/bss — SPEC/15 п. 7) — K5-W001..W005 | 229 |
| `KERNEL/L5-BRIDGE/bridge_self_e.wall` | ветвь E — примитивы эмиссии (E9.2-3a/b/c): таблицы имён (fill_offs/init_tables + kw-слова — E9.2-3c), шапки HEX b2/PEG (tpl_dec/app_tpl + ptpl_dec — E9.2-4), форматтеры (out_hexv/hxs/hxu64/hex2/hex4m/sdec), примечания == _note (note_op/emit_note), H-строки (emit_h), данные (emit_data) — K5-E001..E017 (E018 снят E9.2-3b) | 443 |
| `KERNEL/L5-BRIDGE/bridge_self_l.wall` | ветвь L, часть 1 — КАРТЫ И СЕМАНТИКА (E9.2-3b): imp_hints/san_put/imp_offs/imp_labels (метки iat_/d* + known; правило представимости), build_sstate, sem_add/dq_base/dd_idt/sem_filter, ins_labels (метки операндов l*/d*) — K5-L001..L010 | 453 |
| `KERNEL/L5-BRIDGE/bridge_self_l2.wall` | ветвь L, часть 2 — РЕНДЕР И ДРАЙВЕР (E9.2-3b/c): out_hexl, emit_labname/emit_cut/emit_dollar/emit_sem, build_maps, emit_body — ДРАЙВЕР (канон: m_line ПЕРЕД emit_h, счёты mcount/hcount — E9.2-3c) — K5-L011..L017 | 289 |
| `KERNEL/L5-BRIDGE/bridge_self_m.wall` | ветвь M, часть 1 — ПРИМИТИВЫ (E9.2-3c): m_put/m_put4 (mbuf), m_rex (REX по значениям), m_enc_mem (modrm/SIB/disp + слот rip — == _enc_mem), m_cmp (СВЕРКА с телом + слот — == _template), m_kw/m_dollar/m_opmem/m_opr (рендер операндов) — K5-M001..M009 | 325 |
| `KERNEL/L5-BRIDGE/bridge_self_m2.wall` | ветвь M, часть 2 — КОДИРОВЩИКИ ПРОСТЫХ СЕМЕЙСТВ (E9.2-3c + E9.4-4a): m_bsimple (SIMPLE), m_bjmp (ПРЯМОЙ — гвард da1k!=4, E9.4-4a)/m_bjcc/m_bcall (слоты rel8/rel32/rip), m_bmovzx, m_bstack, m_btest, m_blea, m_bimul, m_bshift, m_bf7, m_bff — K5-M010..M021 | 417 |
| `KERNEL/L5-BRIDGE/bridge_self_m3.wall` | ветвь M, часть 3 — ALU И MOV (E9.2-3c): m_alu_base/m_alu_ext/m_alu_imm (форма 80/83/81), m_balu (5 пар операндов), m_bmov (6 пар; imm64 → H) — K5-M022..M026 | 389 |
| `KERNEL/L5-BRIDGE/bridge_self_m4.wall` | ветвь M, часть 4 — ДРАЙВЕР (E9.2-3c): m_body (диспетчер по dname: имя + кодировщик), m_line («M » + тело + m_cmp + хвост; провал — откат и H-фолбэк) — K5-M027/M028 | 115 |
| `KERNEL/L5-BRIDGE/bridge_self_g.wall` | ветвь G — PEG-ВЫХОД (E9.2-4): ptpl_dec (HEX-литерал s_ptpl — 72 Б шапки PEG -> ptplb), emit_peg (драйвер == _peg_text оракула: шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom; переиспользует outmem; запись запись .peg — коды 8/9) — K5-G001..G002 (E9.2-4, СЕМЬЯ: PEG v1 == _peg_text) + K5-G003..G006 (E9.4-4b-3, ЧУЖОЙ ПУТЬ: gtpl_dec — шапка PEG v2 из s_gtpl, peg2_check — H = min raw_ptr + файл покрывает raw ВСЕХ секций ДО спуска (отказ ERR=FAMILY без частичных выходов), fold_emit — сворачивание области в патчи «!hdr»/«!sec» (== _fold/_chunks64), emit_peg2 — ДРАЙВЕР PEG v2: шапка + !pev2/!hdr [0,H)/!body/!sec + запись) | 326 |
| `KERNEL/L5-BRIDGE/bridge.peg` | обёртка — константа SPEC/11 п.6 (!module bridge; вход 1200, idata 1000 28, iat 1028 48) | 9 |
| `KERNEL/L5-BRIDGE/bridge.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a/4b-1): wall.exe(splice(bridge.wall)), плоский, 1006092 Б — T-E9-17 | — |
| `KERNEL/L5-BRIDGE/bridge.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(bridge.b2), 949580 Б — T-E9-17 | — |
| `KERNEL/L5-BRIDGE/bridge.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+bridge.peg — 98816 Б (тело 0x17E42, target 0x17E01, bss 0x41), вход 0x1200, импорты-восьмёрка; SHA-256 4D23B561… — T-E9-17; 12-й член семейства (круг T-E9-20: M=20894 H=0); пишет <выход>.b2 КАНОН (M/H — E9.2-3c) И <выход>.peg (E9.2-4); ЧУЖИЕ PE32+ — факт-строка FOREIGN без эмиссии (E9.4-4b-1) | — |
| `KERNEL/L5-BRIDGE/bridge.anchor.b2` + `bridge.anchor.peg` | ЯКОРЬ выхода моста о СВОЁМ образе (E9.3-1; регенерирован E9.4-4a/4b-1): канон BRICK v2 (M=20894 H=0; 550 КиБ) + PEG v1 (!bss 41) == оракулу; СВИДЕТЕЛЬ выхода, НЕ вход конвейера (не путать с bridge.b2/bridge.peg — сборкой; T-E9-25; SPEC/15 п. 11) | 22419/8 |
| `KERNEL/L5-BRIDGE/BYTECODE.md` | карта образа: сводка, 122 функции (RVA — +fam_chain/foreign_front/print_ffacts; карта обновлена E9.4-4b-1 — gen_bytecode_e94_4b.py/bridge_labelmap.py), данные (строки 56/глобали 94+15 массивов — w1 последним, канон 0 H), воспроизведение | 265 |
| `KERNEL/L5-BRIDGE/VERIFY.md` | подлинность + уровни проверки (242/242) + журнал срезов E9.2-1/2/3a/3b/3c/4 + E9.3-1 + E9.4-4a + E9.4-4b-1 (развилка; уроки: границы декодера fend — конец тела, предикат вместо выхода, порядок чужого фронта == оракулу) | 249 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов + состав (с E8.3: banner, fib) | 38 |
| `PROJECTS/banner/banner.uva` | проект BANNER (E8.3, DoD этапа 8): баннер системы — ВСЕ 4 ветви L4 (C+N+S+M) в одной программе; .UP v2 (.data 39 Б) | 73 |
| `PROJECTS/banner/CARD.md` | паспорт проекта BANNER: зависимости, сборка/запуск (конвейер), что демонстрирует, эталон T-P-01 | 54 |
| `PROJECTS/fib/fib.uva` | проект FIB (E8.3): числа Фибоначчи — C+N (зависимость N->C), вычисление ряда на ALU, состояние цикла в r5..r10; .UP v1 | 43 |
| `PROJECTS/fib/CARD.md` | паспорт проекта FIB: зависимости, сборка/запуск, что демонстрирует, эталон T-P-02 | 55 |

## Наработки/ — незавершённые задачи (рабочая зона; сессия 89)

| Файл | Роль | Строк |
|---|---|---|
| `Наработки/README.md` | конвенция папки: маркеры задач, обмен материалом, очистка после закрытия | 24 |
| `Наработки/E9.5.md` | МАРКЕР задачи E9.5 (снятие пределов): E9.5-1a закрыта; план E9.5-1b (bridge: риски пересборки, скрытые буферы), E9.5-2 (brick), E9.5-3 (реальный образец); уроки срезов | 82 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов + этапы в контуре тестов (E9.3-1 — якорная фиксация; E9.2-2 — спуск в контуре; E9.2-1 — инструмент моста; E9.1 — мост; E8.3 — проекты) | 268 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 109 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 104 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-18 (T-M5-18 — порт PEG v2 + E9.5-1a: стресс-крафт и пределы; T-E6-53 — граница образа 1 МиБ) | 177 |
| `TESTS/T-L1-BRICK.md` | тест-план brick T-M6-01..T-M6-17, T-E6-36 | 168 |
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11b (E6.2; рост ISA E6.4c; предел 256 КиБ E6.4e-1) | 155 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18, T-E6-16b (E6.3, E6.4e-2) | 97 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул v1/v2 + инструмент + срезы + секция 11 + самохостинг (E6.4d-5/1..2, T-E6-59/60) + фикс №23 (E7.2-2F, T-E6-61) | 482 |
| `TESTS/T-L3-UNIVM.md` | тест-план UNIVM: оракул T-E7-01..08 (E7.1) + T-E7-26..31 (E7.4-1: ISA v1 + .UP v2) + ядро kernel.exe T-E7-09..18 (E7.2-1..4) + T-E7-32 (E7.4-2a) + T-E7-33 (E7.4-2b) + T-E7-34 (E7.4-2c: call/ret + стек вызовов/ловушка 5) | 372 |
| `TESTS/T-L3-UVA.md` | тест-план ассемблера uva.exe T-E7-19..25, 35 (E7.3-1..4 + E7.4-3a + E7.4-3b + E7.4-4 — ПРИЁМКА DoD ЭТАПА 7.4: фикс-пункт/CLI/диффтест 124+127+3 DATA/отвержение/CODE0/15 кругов (вкл. ловушечные — ловушки 5/7 путём ЦЕЛИКОМ uva → kernel.exe)/приёмка T-E7-25 — якоря 24 + программы 10; T-E7-35 — контракт DATA) | 296 |
| `TESTS/T-L4-LIB.md` | тест-план библиотеки L4: оракул против якорей T-E8-01..07 (E8.1) + диффтесты ветвей C T-E8-08..11 (E8.2a), N T-E8-12..16 (E8.2b: ABI + баланс sp, круг с 2 частями), S T-E8-17..21 (E8.2c: STR, композиция 3 ветвей, r13-сентинел, круг с 1 частью) и M T-E8-22..26 (E8.2d: CPY/FILL по ВСЕЙ RAM, композиция 4 ветвей, ABI, круг с 1 частью) | 358 |
| `TESTS/T-L5-BRIDGE.md` | тест-план моста BRIDGE v1 + каркас/спуск/эмиссия bridge.exe: T-E9-01..31 (якоря seed, круги 11 артефактов + фикс-пункт/факты с INS/TARGET/BSS/выходом M=/H= (E9.2-3c)/CLI-мутанты вкл. vsize/синтетика теней T-E9-21/круг над bridge.exe/КАНОН == оракулу на 12 + синтетике T-E9-22/круг канонного текста инструментами T-E9-23/PEG-выход T-E9-24) + секция 18b якорная фиксация T-E9-25 (E9.3-1) + секция 18c FF /4 косвенный jmp в оракуле T-E9-26 (E9.4-1) + секция 18d таблицы переходов в оракуле T-E9-27 (E9.4-2) + секция 18e произвольный PE32+ в оракуле T-E9-28 (E9.4-3a — сессия 78) + секция 18f спуск в чужом теле T-E9-29 (E9.4-3b — сессия 79) + секция 18g PEG v2 оракул-сборщик T-E9-30 (E9.4-3c-1 — сессия 80) + секция 18i b2 чужого тела T-E9-32 (E9.4-3c-3 — сессия 82); 18c/18d — с ПОРТОМ bridge.exe (E9.4-4a — сессия 83: диффтест инструмента на synth4..7; E9.4-4b-3 — ПОРТ PEG v2: T-E9-29 +t.peg == emit_peg_v2 и НОВЫЙ отказ trunc-rdata, T-E9-19 — перевёртыши +t.peg, журнал сессии 86) | 427 |
| `TESTS/T-PROJECTS.md` | тест-план проектов L6 (E8.3): T-P-01 banner / T-P-02 fib — полный круг инструментами; якоря вывода (полные литералы) | 49 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

Карта файлов лаборатории (со счётчиками строк) — `MAP/INDEX-LAB.md`
(выделена отсюда по лимиту 500 строк — сессия 77). Правила и статус —
`LAB/README.md`. Ключевые входы:

| Файл | Роль |
|---|---|
| `LAB/README.md` | статус и правила лаборатории (батарея 242; группы песочницы 1|2|3|4|5) |
| `LAB/py/lab_verify.py` | батарея всех проверок — главный вход (242; CI на каждый пуш) |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона; последняя — сессия 82 — E9.4-3c-3 — b2 чужого тела; актуализация устаревшего счётчика — сессия 82) |
| `LAB/ai/battery_groups.py` | (частное) прогон батареи группами секций (лимит песочницы 10 мин/вызов) |
| `LAB/ai/doc_limit.py` | (частное) контроль лимита 500 строк: .md и LAB .py (сессия 77) |

LAB — измерительный прибор (Python только здесь); подробности —
`LAB/README.md`. Система UNIVERSAL от LAB не зависит. Батарея также
запускается CI (`.github/workflows/verify.yml`) на каждый пуш.

## Корень

| Файл | Роль |
|---|---|
| `README.md` | входная точка репозитория (статус: ЭТАП 9, E9.4 срез E9.4-3c-3 — B2 ЧУЖОГО ТЕЛА, сессия 82; батарея 242/242; история статусов — блоки ниже по файлу) | 499 |
| `.gitattributes` | защита *.hex/*.peg/*.brick/*.b2/*.wall/*.uva от CRLF (LF в репозитории), *.exe как бинарный |
| `.gitignore` | __pycache__ + продукты сборки проектов (*.flat.uva, *.up) |
| `.github/workflows/verify.yml` | CI: автозапуск батареи LAB на каждый пуш (внешний прибор) |

## Счётчики состояния (обновлять при каждом изменении)

- Кирпичей в реестре: **491 строк** (K0 — 116; K1 — 132, вкл. 1 дубль
  ID K1-N011 enc/splice — очередь; K2 — 120; K3 — 70: M3-UNIVM 40
  + M3-UVA 30; K4 — 11 — LIB-1 целиком; K5 — 117 — M5-BRIDGE
  E9.2-1/2/3a/3b/3c/4: каркас C 8 + P 17 + X 1, спуск D 23 + W 3,
  примитивы эмиссии E 17 (+1 снят: E018 emit_raw — заменён L017),
  метки/семантика L 17, M-строки канона M 28, PEG-выход G 2);
  полная ревизия строк ↔ карточек — очередь мелочей;
  сессия 68: указатель РАЗРЕЗАН по лимиту 500 — METHODS.md (K0..K3,
  437 строк) + METHODS-2.md (K4/K5, 37)).
- Модулей: **13** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE, M2-WALL, M3-UNIVM, M3-UVA, M4-LIB —
  ветви C/N/S/M готовы E8.2a/b/c/d: lib_c/lib_n/lib_s/lib_m.uva —
  слой LIB-1 целиком; M5-BRIDGE — мост E9.2/E9.3 ЗАКРЫТ: каркас +
  спуск + эмиссия канона (M-строки) + PEG-выход + якорная фиксация).
- Тестов: **242** (T-E9-26 — E9.4-1 + ПОРТ E9.4-4a (FF /4 — косвенный jmp: оракул + bridge.exe):
  декодер+спуск-терминал+синтетика synth4/synth5+круги, секция 18c —
  lab_t_bridge_ff.py, данные — lab_t_bridge_corpus.py); T-E9-25 — E9.3-1
  (якорная фиксация: якоря .anchor.b2/.peg == оракулу на 12 артефактах,
  секция 18b); T-E9-24 — E9.2-4 (PEG-выход == оракулу на 12
  артефактах + синтетика); T-E9-23 — круг С PEG МОСТА (приёмка DoD
  E9.2); T-E9-22 — E9.2-3a/b/c (эмиссия .b2: RAW -> H —
  метки l/d/iat_ + DD/DQ + разрезы == оракулу на 12 артефактах +
  синтетика спуска/меток (hint-ins — правило представимости, imp0 —
  пустая таблица), круг H-текста инструментами); T-E9-21 — E9.2-2
  (синтетика теней); T-E9-17..20 — E9.2-1 (каркас bridge.exe:
  фикс-пункт сборки, факты == оракулу на 12 артефактах, CLI +
  19 мутантов + 2 легальных отклонения, круг над bridge.exe);
  T-E9-01..16 — E9.1 (мост: якоря seed, круг 11
  артефактов байт-в-байт, круги инструментами); T-M0-01..05,
  T-M2-01..12, T-M3-01..13, T-M4-01..14,
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
  сквозной круг инструментами), T-E8-12..16 — E8.2b (диффтест ветви N:
  REV r1+len+RAM, DEC/I64 консоль, ABI + баланс sp, круг с 2 частями),
  T-E8-17..21 — E8.2c (диффтест ветви S: STR, композиция 3 ветвей,
  r13-сентинел, круг с 1 частью), T-E8-22..26 — E8.2d (диффтест
  ветви M: CPY/FILL по r.mem на ВСЕЙ RAM, композиция 4 ветвей,
  ABI, круг с 1 частью), T-P-01..02 — E8.3 (проекты banner/fib —
  полный круг инструментами, вывод == оракулу и якорям);
  автоматических в батарее — 238).
- Этап: **ЭТАП E9.4 (срез E9.4-3a, сессия 78) — ПРОИЗВОЛЬНЫЙ PE32+
  В ОРАКУЛЕ (ядро KERNEL/ не менялось — R7).** Фундамент чужих EXE
  для PEG v2: разбор PE (lab_pe.parse) обобщён на произвольные
  образы PE32+ — смещения полей ОТ e_lfanew (были фиксированные:
  неявный e_lfanew 0x80), ВСЕ слоты таблицы секций → pe["sections"],
  RVA-отображение по содержащей секции (raw-часть), импорты многих
  DLL; легаси sec_*/body — ПЕРВАЯ секция (семья: значения идентичны
  прежним). T-E9-28 (секция 18e — lab_t_bridge_pe.py; данные —
  lab_t_bridge_corpus.py: чужой образ foreign_image — e_lfanew
  0x100 + 2 секции + 2 DLL + якоря FOREIGN_*). НЕЙТРАЛЬНОСТЬ —
  снимком до/после (12 артефактов b2/peg байт-в-байт) + структурно
  (12x1 секция == sec_*); батарея 237 → 238/238 (группы 1|2|3|4|5);
  parse_family и bridge.exe НЕ менялись (порт — E9.4-3b+). До
  этого — срез E9.4-2 (сессия 76) — ТАБЛИЦЫ ПЕРЕХОДОВ В
  ОРАКУЛЕ (ядро KERNEL/ не менялось — R7).** Семантика спуска
  (SPEC/15 п. 3): косвенный jmp qword [rip+X] с X в данных —
  цели-кандидаты из qword-строк «до первого non-code qword» (0 /
  вне VirtualSize / конец тела — вилка raw/bss); регистровая/
  индексная форма — терминал без кандидатов (E9.4-1). T-E9-27
  (секция 18d — lab_t_bridge_jt.py; данные — lab_t_bridge_corpus.py:
  синтетика synth6 switch-таблица / synth7 терминатор «qword вне
  тела»). Гигиена: рендер-ветвь оракула → lab_bridge_text.py
  (прецедент lab_l2/lab_l2_gen; lab_bridge.py 500 → 360 — семантика
  во фронте, вид текста в рендере). НЕЙТРАЛЬНОСТЬ — снимком
  до/после (12 артефактов байт-в-байт) + T-E9-25; батарея
  236 → 237/237 (группы 1|2|3|4|5); инструмент bridge.exe НЕ
  менялся (порт — при первом чужом круге). До этого — срез E9.4-1
  (сессия 75) — FF /4: КОСВЕННЫЙ JMP В ОРАКУЛЕ (декодер +
  терминал-семантика + плечи исполнителя + фаззер; T-E9-26,
  секция 18c; гигиена: данные секции 18 → corpus). До этого —
  ЭТАП E9.3 ЗАКРЫТ (E9.3-1, сессия 74) —
  ВЫХОД МОСТА
  ЗАФИКСИРОВАН ЯКОРЯМИ (ядро KERNEL/L5-BRIDGE).** 24 файла-якоря
  KERNEL/<м>/<имя>.anchor.b2/.anchor.peg (все 12 артефактов, вкл.
  bridge.exe; 1.40 МБ + 2 КиБ) — статические свидетели (как
  листинги .hex у L0): == оракулу байт-в-байт, транзитивно
  (T-E9-22/24) == инструменту bridge.exe; T-E9-25 (секция 18b —
  LAB/py/lab_t_anchor.py) + генератор LAB/ai/anchor_gen.py
  (регенерация — только намеренно); SPEC/15 п. 11 (+ отказ от
  замены листингов .hex); ядро/артефакты не менялись (R7); батарея
  234 → 235/235 (группа 4 — 24 проверки). До этого — E9.2 ЗАКРЫТ
  (E9.2-4, сессия 73): МОСТ BRIDGE v1 ПОЛНОСТЬЮ САМОДОСТАТОЧЕН
  (117 кирпичей K5-*): PEG-выход (ветвь G — K5-G001..G002) +
  приёмка DoD — оба выхода == оракулу, круг с выходами моста
  сходится; артефакты 91648 Б, круг над bridge.exe M=19237 H=0,
  батарея 234/234; E9.2-1..3c (каркас; спуск; raw-эмиссия; метки/
  семантика; M-строки канона — сессии 68-72) и E9.1 (сессия 67):
  SPEC/15 + оракул + секция 18 — истина семантики; круг ВСЕХ 11
  артефактов байт-в-байт. Далее — E9.4-2+ (таблицы переходов, PEG v2
  — чужие заголовки/секции/импорты, порт декодера в инструмент).
  Подробно — 03d/03e/03f-HISTORY-E9 (сессии 67-79).
- Гигиена (сессия 77): все документы возвращены под лимит 500 строк —
  карта файлов LAB вынесена в MAP/INDEX-LAB.md; детальные записи
  закрытых этапов из DOCS/03-ROADMAP.md (5/5a/6.4c/6.4e/6.4d) и
  устаревшие блоки README — в новый DOCS/03a2-HISTORY.md (перенос
  байт-в-байт); 03e/03f разрезаны по границе сессий 75+; README
  почищен и актуализирован (батарея 237/237, bridge.exe 91648 Б);
  lab_t_bridge.py 501 → 500 (лишняя пустая строка). НОВЫЙ инструмент
  LAB/ai/doc_limit.py — постоянный контроль лимита (.md и LAB .py,
  2 исключения: растущий JOURNAL.md и замороженный свидетель-транс
  литерация trace_m.py 1:1). Ядро KERNEL/ не менялось (R7); батарея
  237/237 (группы 1|2|3|4|5).
- Предыдущие этапы (детали — DOCS/03a/03a2/03b/03c/03d/03e/03f-HISTORY*.md
  и JOURNAL):
  **E8** — Библиотека L4 (сессии 61-66, ЗАКРЫТ: LIB-1 целиком, 11
  кирпичей C/N/S/M; DoD — используется двумя программами banner/fib;
  батарея 180 → 208); **E7** — UNIVM + ассемблер (сессии 44-60,
  ЗАКРЫТ: ISA v0+v1 24 опкода, .UP v1/v2, kernel.exe/uva.exe ==
  оракулам; батарея 161 → 180); **E6** — конвейер BRICK v2/enc/
  splice, язык WALL v1/v2, самохостинг wall.wall (сессии 3-43;
  батарея → 161); **E0-E5** — семя..ассемблер BRICK вручную
  (сессии 1-2; тройная верификация, круги E4/E5).
