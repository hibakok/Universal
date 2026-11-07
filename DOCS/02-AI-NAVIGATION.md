# 02. Навигация для ИИ (и человека)

Паспорт файла: DOCS/02-AI-NAVIGATION.md | слой: все | роль: протокол работы с репозиторием.

## Обязательный протокол (перед любой работой с кодом)

```
ШАГ 1. Прочитай MAP/INDEX.md — карта всех файлов.
ШАГ 2. Прочитай DOCS/03-ROADMAP.md — текущий этап (что сейчас в работе).
ШАГ 3. Найди целевой модуль в карте, прочитай его CARD.md.
ШАГ 4. Читай ТОЛЬКО файлы из раздела «Состав» карточки модуля.
ШАГ 5. Для изменения кирпича: карточка кирпича + карточки кирпичей,
        которые он использует (поле «Состоит из»).
ШАГ 6. Внеся изменение, обнови: карточку в MAP/M<модуль>.md, указатель
        MAP/METHODS.md,
        листинг/BYTECODE, тест. См. DOCS/04-RULES-OF-CHANGE.md.
```

**Бюджет чтения:** на любую задачу читается не более 7 файлов,
не считая справочников SPEC/.

## Что читать при типовых задачах

| Задача | Обязательные файлы |
|---|---|
| Изменить код семени (L0) | `KERNEL/L0-SEED/CARD.md`, `seed.hex` (телесная форма: 0 = RVA 0x1000), `seed.peg`, `SPEC/05-X86-SUBSET.md`, `SPEC/04-PE-MINIMAL.md` |
| Изменить код семени-2 | `KERNEL/L0-SEED2/CARD.md`, `seed2.hex`, `SPEC/05-X86-SUBSET.md`, `SPEC/04-PE-MINIMAL.md` |
| Добавить команду seed2 | `KERNEL/L0-SEED2/CARD.md`, `BYTECODE.md` §7 (формат записи), `MAP/M0-SEED2.md` (K0-D012, K0-D011) |
| Добавить кирпич L0 | `SPEC/01-METHOD-CARD.md`, `MAP/METHODS.md` (указатель), `MAP/M<модуль>.md`, `CARD.md` модуля, его `.hex` |
| Изменить код hxdump | `KERNEL/L0-HXDUMP/CARD.md`, `hxdump.hex`, `SPEC/05-X86-SUBSET.md`, `SPEC/04-PE-MINIMAL.md` |
| Изменить код hexgen | `KERNEL/L0-HEXGEN/CARD.md`, `hexgen.hex`, `hexgen.peg`, `SPEC/05-X86-SUBSET.md`, `SPEC/04-PE-MINIMAL.md` |
| Изменить код pegen | `KERNEL/L0-PEGEN/CARD.md`, `pegen.hex`, `pegen.peg`, `SPEC/05-X86-SUBSET.md`, `SPEC/07-PEG-FORMAT.md` |
| Изменить код brick | `KERNEL/L1-BRICK/CARD.md`, `brick.brick` (канонический исходник), `brick.peg`, `SPEC/08-BRICK-FORMAT.md`, `SPEC/05-X86-SUBSET.md` |
| Добавить директиву BRICK | `SPEC/08-BRICK-FORMAT.md`, `MAP/M1-BRICK.md` (K1-A008 parse_data — диспетчер), `KERNEL/L1-BRICK/BYTECODE.md` §3 |
| Собрать модуль из BRICK | `KERNEL/L1-BRICK/CARD.md` (конвейер: brick + pegen), `TESTS/T-L1-BRICK.md` (T-M6-16) |
| Мигрировать модуль L0 на BRICK | `SPEC/03-ATOM-FORMAT.md` (соответствие форматов), `SPEC/08-BRICK-FORMAT.md`, `KERNEL/L1-BRICK/brick.brick` (образец) |
| Добавить директиву PEG | `SPEC/07-PEG-FORMAT.md`, `MAP/M0-PEGEN.md` (K0-D042 kwtab/vdesc, K0-Q011), `KERNEL/L0-PEGEN/BYTECODE.md` §4 |
| Понять телесную форму листингов | `SPEC/03-ATOM-FORMAT.md` (раздел «Телесная форма»), `SPEC/07-PEG-FORMAT.md` |
| Собрать EXE из листинга (E4) | `KERNEL/L0-HEXGEN/CARD.md` + `KERNEL/L0-PEGEN/CARD.md` (конвейер), `TESTS/T-L0-PEGEN.md` (T-M5-02) |
| Добавить кирпич разбора ATOM | `MAP/M0-HEXGEN.md` (ветвь R), `SPEC/03-ATOM-FORMAT.md` |
| Понять виртуальные нули (bss) | `SPEC/04-PE-MINIMAL.md`, `KERNEL/L0-HEXGEN/BYTECODE.md` §1–2 |
| Задампить файл | `KERNEL/L0-HXDUMP/CARD.md` (формат строки), `TESTS/T-L0-HXDUMP.md` |
| Понять формат PE | `SPEC/04-PE-MINIMAL.md`, `KERNEL/L0-SEED/BYTECODE.md` |
| Понять используемые инструкции | `SPEC/05-X86-SUBSET.md` |
| Узнать, что делать дальше | `DOCS/03-ROADMAP.md` (текущий этап + критерии готовности) |
| Проверить ВСЁ репозиторий сразу | `LAB/README.md` -> `python3 LAB/py/lab_verify.py` (67 проверок: SHA, PE, эмуляция, оракулы, круги; ~7 с) |
| Проверить семя | `KERNEL/L0-SEED/VERIFY.md`, `TESTS/T-L0-SEED.md` |
| Проверить семя-2 | `KERNEL/L0-SEED2/VERIFY.md`, `TESTS/T-L0-SEED2.md` |
| Проверить hexgen | `KERNEL/L0-HEXGEN/VERIFY.md`, `TESTS/T-L0-HEXGEN.md` |
| Проверить pegen | `KERNEL/L0-PEGEN/VERIFY.md`, `TESTS/T-L0-PEGEN.md` |
| Начать новый проект | `PROJECTS/README.md`, `SPEC/06-ARCHITECTURE.md` |

## Лаборатория LAB (внешний инструмент верификации)

`LAB/` — измерительный прибор, а не часть системы (правила —
`LAB/README.md`). Python там допустим ТОЛЬКО внутри LAB. Перед любым
изменением KERNEL/ и после него: `python3 LAB/py/lab_verify.py` —
должно быть 67/67. Эмулятор (lab_cpu/lab_win) исполняет наши EXE с
заглушками kernel32; оракулы (lab_atom/lab_brick/lab_pegen) —
независимые реализации SPEC/03/08/07; расхождение оракула с
инструментом — находка, а не повод «подогнать» (см. журнал
KERNEL/L1-BRICK/VERIFY.md, дефект № 12).

## Правила выживания в репозитории

1. **Не читай всё.** Репозиторий спроектирован так, что для любой задачи
   достаточно карты + карточек. Полное чтение — ошибка процесса.
2. **Вершины зависимостей.** Изменение кирпича K влечёт проверку всех
   кирпичей, у которых K стоит в поле «Состоит из» (список «Используется в»).
3. **Идентификаторы — адреса.** K0-H001 ищется в указателе
   `MAP/METHODS.md` (строка → файл карточки) и в
   `KERNEL/L0-SEED/BYTECODE.md` поиском по тексту.
4. **Каждый ответ о коде цитирует карточку.** Если сомневаешься в поведении
   метода — иди в карточку, а не в код.
5. **Сомнение = стоп.** Если после чтения карточки и листинга поведение
   неясно — это дефект документации; сначала почини документацию.

## Соглашения

- Все смещения в документации — шестнадцатеричные, если не сказано иное.
- «RVA» — адрес относительно начала загруженного образа (см. словарь).
- Регистры записываются в нотации Intel: `rax`, `rsp`, `[rbx+0x3C]`.
- Числа в спецификациях: `0x`-префикс = шестнадцатеричное, иначе десятичное.
