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
| `DOCS/02-AI-NAVIGATION.md` | протокол навигации, таблица типовых задач | 58 |
| `DOCS/03-ROADMAP.md` | этапы E0..E10+, критерии готовности | 113 |
| `DOCS/04-RULES-OF-CHANGE.md` | регламент изменений и коммитов | 53 |

## SPEC/ — формальные спецификации

| Файл | Роль | Строк |
|---|---|---|
| `SPEC/00-GLOSSARY.md` | словарь терминов, регистры | 41 |
| `SPEC/01-METHOD-CARD.md` | формат карточки кирпича | 50 |
| `SPEC/02-LAYER0-SPEC.md` | правила слоя L0, верификация | 54 |
| `SPEC/03-ATOM-FORMAT.md` | грамматика формата ATOM v1 | 62 |
| `SPEC/04-PE-MINIMAL.md` | структура наших EXE, инварианты | 104 |
| `SPEC/05-X86-SUBSET.md` | реестр инструкций и кодировок | 68 |
| `SPEC/06-ARCHITECTURE.md` | целевая архитектура системы | 72 |
| `SPEC/07-PEG-FORMAT.md` | формат PEG v1 и поведение pegen | 111 |

## MAP/ — навигация

| Файл | Роль | Строк |
|---|---|---|
| `MAP/INDEX.md` | этот файл | 105 |
| `MAP/METHODS.md` | указатель реестра кирпичей (одна строка на кирпич) | 146 |
| `MAP/M0-SEED.md` | карточки кирпичей M0-SEED (8) | 126 |
| `MAP/M0-SEED2.md` | карточки кирпичей M0-SEED2 (19) | 295 |
| `MAP/M0-HXDUMP.md` | карточки кирпичей M0-HXDUMP (23) | 356 |
| `MAP/M0-HEXGEN.md` | карточки кирпичей M0-HEXGEN (29) | 452 |
| `MAP/M0-PEGEN.md` | карточки кирпичей M0-PEGEN (37) | 500 |
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
| `KERNEL/L0-PEGEN/VERIFY.md` | проверка, журнал, пойманные ошибки | 90 |

## PROJECTS/ — внешние программы (ядро их не знает)

| Файл | Роль | Строк |
|---|---|---|
| `PROJECTS/README.md` | правила размещения проектов | 28 |

## TESTS/ — тестирование

| Файл | Роль | Строк |
|---|---|---|
| `TESTS/POLICY.md` | политика быстрых и глубоких тестов | 56 |
| `TESTS/T-L0-SEED.md` | тест-план семени T-M0-01..T-M0-05 | 66 |
| `TESTS/T-L0-SEED2.md` | тест-план семени-2 T-M2-01..T-M2-12 | 117 |
| `TESTS/T-L0-HXDUMP.md` | тест-план hxdump T-M3-01..T-M3-13 | 126 |
| `TESTS/T-L0-HEXGEN.md` | тест-план hexgen T-M4-01..T-M4-14 | 108 |
| `TESTS/T-L0-PEGEN.md` | тест-план pegen T-M5-01..T-M5-17 | 131 |

## Корень

| Файл | Роль |
|---|---|
| `README.md` | входная точка репозитория |
| `.gitattributes` | защита *.hex от CRLF-искажений, *.exe как бинарный |

## Счётчики состояния (обновлять при каждом изменении)

- Кирпичей в реестре: **116** (слой L0: 8 в M0-SEED, 19 в M0-SEED2,
  23 в M0-HXDUMP, 29 в M0-HEXGEN, 37 в M0-PEGEN).
- Модулей: **5** (M0-SEED, M0-SEED2, M0-HXDUMP, M0-HEXGEN, M0-PEGEN).
- Тестов: **61** (T-M0-01..05, T-M2-01..12, T-M3-01..13, T-M4-01..14,
  T-M5-01..17).
- Этап: **E4 завершён** (конвейер hexgen+pegen воспроизводит все модули
  и сам себя из текстов ATOM+PEG); следующий — E5 BRICK (метки; см.
  `DOCS/03-ROADMAP.md`).
