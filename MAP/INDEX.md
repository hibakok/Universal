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
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач | 92 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности | 255 |
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
| `SPEC/08-BRICK-FORMAT.md` | формат BRICK v1 и поведение brick (слой L1) | 153 |
| `SPEC/09-ENC-FORMAT.md` | BRICK v2: M-строки, канонические кодировки, контракт enc | 252 |
| `SPEC/10-SPLICE-FORMAT.md` | SPLICE v1: !include, склейка исходников, контракт splice | 147 |
| `SPEC/11-WALL-FORMAT.md` | WALL v1/v2: язык слоя L2, компиляция в BRICK v2, канон эмиттера | 374 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 235 |
| `MAP/METHODS.md` | указатель реестра кирпичей (одна строка на кирпич) | 391 |
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
| `MAP/M2-WALL.md` | карточки кирпичей M2-WALL (66) | 146 |
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
| `KERNEL/L1-BRICK/BYTECODE.md` | сводка, карта кирпичей, данные, импорты, история | 112 |
| `KERNEL/L1-BRICK/VERIFY.md` | SHA-256, 4 уровня проверки, журнал | 95 |
| `KERNEL/L1-ENC/CARD.md` | карточка модуля M1-ENC (кодировщик BRICK v2) | 143 |
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
| `KERNEL/L1-ENC/enc_data.b2` | часть: D — данные/импорты/bss (2346-2693; E6.4c: mnemtab +3, DZ 2) | 348 |
| `KERNEL/L1-ENC/enc.brick` | плоская форма в BRICK v1 = enc(splice(enc.b2)) байт-в-байт (генерируемый артефакт) | 2693 |
| `KERNEL/L1-ENC/enc.peg` | обёртка enc (PEG v1, SPEC/07) | 10 |
| `KERNEL/L1-ENC/enc.exe` | материализация: brick+pegen, 12288 байт, PE32+ (рост ISA E6.4c) | — |
| `KERNEL/L1-ENC/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 154 |
| `KERNEL/L1-ENC/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.2 + рост ISA E6.4c | 125 |

| `KERNEL/L1-SPLICE/CARD.md` | карточка модуля M1-SPLICE (склейка !include) | 129 |
| `KERNEL/L1-SPLICE/splice.b2` | корень модуля M1-SPLICE: шапка + поток X/C/G + !include 3 частей | 137 |
| `KERNEL/L1-SPLICE/splice_s.b2` | часть: ветви S/N — цикл уровней, директива, вывод строки | 248 |
| `KERNEL/L1-SPLICE/splice_svc.b2` | часть: H/G/U/C/F — печать, ошибки, командная строка, файлы | 189 |
| `KERNEL/L1-SPLICE/splice_data.b2` | часть: D — таблицы, строки, импорты, bss | 120 |
| `KERNEL/L1-SPLICE/splice.brick` | плоская форма в BRICK v1 = enc(splice(splice.b2)) байт-в-байт (генерируемый артефакт) | 691 |
| `KERNEL/L1-SPLICE/splice.peg` | обёртка splice (PEG v1, SPEC/07) | 10 |
| `KERNEL/L1-SPLICE/splice.exe` | материализация: brick+pegen, 3584 байта, PE32+ | — |
| `KERNEL/L1-SPLICE/BYTECODE.md` | сводка образа, карта кирпичей, данные, импорты | 114 |
| `KERNEL/L1-SPLICE/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.3 | 96 |
| `KERNEL/L2-WALL/CARD.md` | карточка модуля M2-WALL (компилятор WALL v1) | 118 |
| `KERNEL/L2-WALL/wall.b2` | корень: поток + 18 !include (19 частей) | 122 |
| `KERNEL/L2-WALL/wall_svc.b2` | ветви H/G/U/C/F — сервисы (реинкарнации K1) | 192 |
| `KERNEL/L2-WALL/wall_n.b2` | ветвь N — разбиение строк, проход 0 | 147 |
| `KERNEL/L2-WALL/wall_l.b2` | ветвь L — лексер WALL | 227 |
| `KERNEL/L2-WALL/wall_pe.b2` | ветви P: want_*/поиск/chain_count | 338 |
| `KERNEL/L2-WALL/wall_ph.b2` | p_expr/p_mul/p_unary (глубины T-складов) | 268 |
| `KERNEL/L2-WALL/wall_pp.b2` | p_prim — первичные выражения | 227 |
| `KERNEL/L2-WALL/wall_pa.b2` | p_args/p_call_tail/call_stats — вызовы | 300 |
| `KERNEL/L2-WALL/wall_pc.b2` | p_cond + emit_addr/len/load | 321 |
| `KERNEL/L2-WALL/wall_p1.b2` | проход 1: цикл, диспетчер, main | 138 |
| `KERNEL/L2-WALL/wall_pd.b2` | объявления + заголовки func | 434 |
| `KERNEL/L2-WALL/wall_p1s.b2` | утверждения прохода 1 (статы) | 300 |
| `KERNEL/L2-WALL/wall_p2.b2` | проход 2: цикл, диспетчер, заголовки | 197 |
| `KERNEL/L2-WALL/wall_p2s.b2` | утверждения прохода 2: if/while/вызовы | 380 |
| `KERNEL/L2-WALL/wall_p2t.b2` | эмиттеры переходов и меток | 100 |
| `KERNEL/L2-WALL/wall_e.b2` | примитивы вывода, div10, out_dec | 363 |
| `KERNEL/L2-WALL/wall_ep.b2` | пролог/эпилог/alu/shift | 152 |
| `KERNEL/L2-WALL/wall_ed.b2` | импорты/данные (строки, глобальные var) | 387 |
| `KERNEL/L2-WALL/wall_data.b2` | ветвь D: таблицы, strblob, bss | 359 |
| `KERNEL/L2-WALL/wall.brick` | плоская форма v1 = enc(splice(wall.b2)) | — |
| `KERNEL/L2-WALL/wall.peg` | обёртка (PEG v1, SPEC/07) | 9 |
| `KERNEL/L2-WALL/wall.exe` | материализация: 23040 байт, PE32+ | — |
| `KERNEL/L2-WALL/BYTECODE.md` | сводка образа, карта ветвей, данные | 124 |
| `KERNEL/L2-WALL/VERIFY.md` | проверка, журнал 11 дефектов | 96 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов | 28 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов | 95 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 109 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 104 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-17 | 131 |
| `TESTS/T-L1-BRICK.md` | тест-план brick T-M6-01..T-M6-17 | 137 |
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11 (E6.2; рост ISA E6.4c) | 109 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18 (E6.3 выполнен) | 82 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул T-E6-19..24 (E6.4a) + v2 T-E6-31..35 (E6.4c) + журналы | 178 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории | 77 |
| `LAB/py/lab_pe.py` | разбор PE32+ + инварианты SPEC/04 | 178 |
| `LAB/py/lab_atom.py` | оракул ATOM v1 (SPEC/03) | 68 |
| `LAB/py/lab_brick.py` | оракул BRICK v1 (SPEC/08) | 312 |
| `LAB/py/lab_pegen.py` | оракул PEG v1 (SPEC/07) | 125 |
| `LAB/py/lab_enc.py` | оракул ENC v1 (SPEC/09): M-строка -> H-строка | 495 |
| `LAB/py/lab_enc_isa.py` | кирпич роста ISA оракула ENC: EncError/_err/_rex/_enc_imul (E6.4c) | 31 |
| `LAB/py/lab_splice.py` | оракул SPLICE v1 (SPEC/10): склейка по !include | 106 |
| `LAB/py/lab_splice_cases.py` | эталоны SPLICE: 14 якорей, 13 ошибок, большой случай | 135 |
| `LAB/py/lab_l2.py` | оракул WALL v1/v2, фронт: parse + семантика (v2: массивы, astore) | 349 |
| `LAB/py/lab_l2_lex.py` | оракул WALL: лексер + разбор выражений/условий (v2: * / %, [i], && ||) | 270 |
| `LAB/py/lab_l2_gen.py` | оракул WALL v1/v2, бэк: канон-эмиттер .b2 (guard, astore, imul/idiv) | 411 |
| `LAB/py/lab_l2_lay.py` | оракул WALL: раскладка кадров (массивы, maxd/maxc/S) | 160 |
| `LAB/py/lab_l2_err.py` | ошибка компиляции WallError (лист-кирпич) | 14 |
| `LAB/py/lab_l2_cases.py` | якоря WALL v1: 4 полных + 6 фрагментных (вручную) | 409 |
| `LAB/py/lab_l2_cases2.py` | якоря WALL v2: 2 полных + 7 фрагментных (вручную, E6.4c) | 440 |
| `LAB/py/lab_l2_prog.py` | эталоны WALL: 26+13 ошибок, демо-круги v1/v2, big_source 1/2 | 330 |
| `LAB/py/lab_enc_cases.py` | эталоны ENC: 117 якорей, 27 ошибок, демо-круг | 264 |
| `LAB/py/lab_x86.py` | декодер подмножества x86-64 (SPEC/05; E6.4c: imul/idiv/cqo) | 330 |
| `LAB/py/lab_cpu.py` | эмулятор: регистры, флаги, поток, умножение/деление (#DE) | 407 |
| `LAB/py/lab_win.py` | загрузчик PE + заглушки kernel32 + вирт. ФС + куча (E6.4c) | 247 |
| `LAB/py/lab_run.py` | прогон EXE с командной строкой | 30 |
| `LAB/py/lab_disasm.py` | дизассемблер (декод -> мнемоника) | 131 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход) | 413 |
| `LAB/py/lab_t_exe.py` | секции 7-8 батареи: инструменты enc/splice | 218 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL v1+v2 (T-E6-19..24, 31..35) | 229 |
| `LAB/ai/JOURNAL.md` | журнал сессий ИИ-разработчика (частная зона) | 217 |
| `LAB/ai/enc_build.py` | (частное) построитель M1-ENC: enc.b2 -> артефакты + карта меток | 469 |
| `LAB/ai/splice_build.py` | (частное) построитель M1-SPLICE: разрез -> артефакты + dev-тесты | 228 |
| `LAB/ai/enc_part1..3.txt` | (частное) кодовые части enc.b2 для правок по секциям | — |

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

- Кирпичей в реестре: **249** (слой L0: 8 в M0-SEED, 19 в M0-SEED2,
  23 в M0-HXDUMP, 29 в M0-HEXGEN, 37 в M0-PEGEN; слой L1: 42 в M1-BRICK,
  64 в M1-ENC (+E033 enc_imul, E6.4c), 27 в M1-SPLICE; слой L2: 66 в
  M2-WALL).
- Модулей: **9** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE, M2-WALL).
- Тестов: **113** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..35; автоматических в батарее — 111).
- Этап: **E6.4c, части 1–2 завершены** (рост ISA imul/idiv/cqo через весь
  стек; WALL v2: SPEC/11 + оракул + якоря + демо-круг «U-WALL2-OK 85»
  с массивами, * / %, break/continue, && / || и кучей; батарея 111/111);
  следующий — E6.4c-3: перевод инструмента wall.exe на v2, затем
  E6.4d — самохостинг wall.wall (см. `DOCS/03-ROADMAP.md`).
