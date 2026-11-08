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
| `SPEC/05-X86-SUBSET.md` | реестр инструкций и кодировок | 234 |
| `SPEC/06-ARCHITECTURE.md` | целевая архитектура системы | 72 |
| `SPEC/07-PEG-FORMAT.md` | формат PEG v1 и поведение pegen | 111 |
| `SPEC/08-BRICK-FORMAT.md` | формат BRICK v1 и поведение brick (слой L1) | 153 |
| `SPEC/09-ENC-FORMAT.md` | BRICK v2: M-строки, канонические кодировки, контракт enc | 247 |
| `SPEC/10-SPLICE-FORMAT.md` | SPLICE v1: !include, склейка исходников, контракт splice | 147 |
| `SPEC/11-WALL-FORMAT.md` | WALL v1: язык слоя L2, компиляция в BRICK v2, канон эмиттера | 271 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 161 |
| `MAP/METHODS.md` | указатель реестра кирпичей (одна строка на кирпич) | 252 |
| `MAP/M0-SEED.md` | карточки кирпичей M0-SEED (8) | 130 |
| `MAP/M0-SEED2.md` | карточки кирпичей M0-SEED2 (19) | 299 |
| `MAP/M0-HXDUMP.md` | карточки кирпичей M0-HXDUMP (23) | 360 |
| `MAP/M0-HEXGEN.md` | карточки кирпичей M0-HEXGEN (29) | 452 |
| `MAP/M0-PEGEN.md` | карточки кирпичей M0-PEGEN (37) | 500 |
| `MAP/M1-BRICK.md` | карточки кирпичей M1-BRICK (42) | 480 |
| `MAP/M1-ENC.md` | карточки кирпичей M1-ENC (поток и разбор) | 411 |
| `MAP/M1-ENC-E.md` | карточки ветви E модуля M1-ENC (кодирование, 22) | 297 |
| `MAP/M1-ENC-S.md` | служебные ветви M1-ENC: H/U/F/D (14) | 193 |
| `MAP/M1-SPLICE.md` | карточки кирпичей M1-SPLICE (27) | 431 |
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
| `KERNEL/L1-ENC/enc_p1.b2` | часть: P011-P013 — разбор M-строки (225-494) | 270 |
| `KERNEL/L1-ENC/enc_p2.b2` | часть: P014-P015 — память/ссылки (495-731) | 237 |
| `KERNEL/L1-ENC/enc_tr.b2` | часть: T+R — лексика и таблицы (732-984) | 253 |
| `KERNEL/L1-ENC/enc_e1.b2` | часть: E011-E017 — эмиттеры/память (985-1365) | 381 |
| `KERNEL/L1-ENC/enc_e2.b2` | часть: E021-E023 — ALU/сдвиги/переходы (1366-1642) | 277 |
| `KERNEL/L1-ENC/enc_e3.b2` | часть: E024-E025 — mov/movzx/lea (1643-1940) | 298 |
| `KERNEL/L1-ENC/enc_e4.b2` | часть: E026-E032 — test..int3 (1941-2117) | 177 |
| `KERNEL/L1-ENC/enc_svc.b2` | часть: H/G/U/C/F — сервис (2118-2306) | 189 |
| `KERNEL/L1-ENC/enc_data.b2` | часть: D — данные/импорты/bss (2307-2651) | 345 |
| `KERNEL/L1-ENC/enc.brick` | плоская форма в BRICK v1 = enc(splice(enc.b2)) байт-в-байт (генерируемый артефакт) | 2651 |
| `KERNEL/L1-ENC/enc.peg` | обёртка enc (PEG v1, SPEC/07) | 10 |
| `KERNEL/L1-ENC/enc.exe` | материализация: brick+pegen, 11776 байт, PE32+ | — |
| `KERNEL/L1-ENC/BYTECODE.md` | сводка, карта кирпичей, данные, импорты | 141 |
| `KERNEL/L1-ENC/VERIFY.md` | SHA-256, уровни, журнал дефектов E6.2 | 104 |

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
| `TESTS/T-L1-ENC.md` | тест-план enc: оракул T-E6-01..04 + инструмент T-E6-05..11 (E6.2 выполнен) | 93 |
| `TESTS/T-L1-SPLICE.md` | тест-план splice: оракул + инструмент T-E6-12..18 (E6.3 выполнен) | 82 |
| `TESTS/T-L2-WALL.md` | тест-план WALL: оракул T-E6-19..24 (E6.4a выполнен) + журнал находок | 74 |

## LAB/ — внешняя лаборатория ИИ (не часть системы)

| Файл | Роль | Строк |
|---|---|---|
| `LAB/README.md` | статус и правила лаборатории | 77 |
| `LAB/py/lab_pe.py` | разбор PE32+ + инварианты SPEC/04 | 178 |
| `LAB/py/lab_atom.py` | оракул ATOM v1 (SPEC/03) | 68 |
| `LAB/py/lab_brick.py` | оракул BRICK v1 (SPEC/08) | 312 |
| `LAB/py/lab_pegen.py` | оракул PEG v1 (SPEC/07) | 125 |
| `LAB/py/lab_enc.py` | оракул ENC v1 (SPEC/09): M-строка -> H-строка | 498 |
| `LAB/py/lab_splice.py` | оракул SPLICE v1 (SPEC/10): склейка по !include | 106 |
| `LAB/py/lab_splice_cases.py` | эталоны SPLICE: 14 якорей, 13 ошибок, большой случай | 135 |
| `LAB/py/lab_l2.py` | оракул WALL v1 (SPEC/11), фронт: лексер + разбор + семантика | 423 |
| `LAB/py/lab_l2_gen.py` | оракул WALL v1, бэк: раскладка слотов + канон-эмиттер .b2 | 435 |
| `LAB/py/lab_l2_err.py` | ошибка компиляции WallError (лист-кирпич) | 14 |
| `LAB/py/lab_l2_cases.py` | якоря WALL: 4 полных + 6 фрагментных (вручную) | 409 |
| `LAB/py/lab_l2_prog.py` | эталоны WALL: 26 ошибок, демо-круг, big_source | 151 |
| `LAB/py/lab_enc_cases.py` | эталоны ENC: 109 якорей, 21 ошибка, демо-круг | 248 |
| `LAB/py/lab_x86.py` | декодер подмножества x86-64 (SPEC/05) | 319 |
| `LAB/py/lab_cpu.py` | эмулятор: регистры, флаги, поток | 357 |
| `LAB/py/lab_win.py` | загрузчик PE + заглушки kernel32 + вирт. ФС | 223 |
| `LAB/py/lab_run.py` | прогон EXE с командной строкой | 30 |
| `LAB/py/lab_disasm.py` | дизассемблер (декод -> мнемоника) | 131 |
| `LAB/py/lab_verify.py` | батарея всех проверок (главный вход) | 401 |
| `LAB/py/lab_t_exe.py` | секции 7-8 батареи: инструменты enc/splice | 218 |
| `LAB/py/lab_t_wall.py` | секция 9 батареи: оракул WALL (T-E6-19..24) | 124 |
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

- Кирпичей в реестре: **248** (слой L0: 8 в M0-SEED, 19 в M0-SEED2,
  23 в M0-HXDUMP, 29 в M0-HEXGEN, 37 в M0-PEGEN; слой L1: 42 в M1-BRICK,
  63 в M1-ENC, 27 в M1-SPLICE).
- Модулей: **8** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN,
  M1-BRICK, M1-ENC, M1-SPLICE).
- Тестов: **102** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17, T-M6-01..17, T-E6-01..24; автоматических в батарее — 96).
- Этап: **E6.4a завершён** (SPEC/11 + оракул WALL v1 + батарея 96/96;
  демо-круг WALL -> EXE -> эмуляция «U-WALL-OK 37»); следующий — E6.4b:
  wall.exe на BRICK v2 с самохостингом (см. `DOCS/03-ROADMAP.md`).
