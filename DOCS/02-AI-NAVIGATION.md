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
| Изменить код enc | `KERNEL/L1-ENC/CARD.md`, `enc.b2` (канонический исходник BRICK v2), `SPEC/09-ENC-FORMAT.md`, `MAP/M1-ENC.md` + `MAP/M1-ENC-E.md` + `MAP/M1-ENC-S.md` |
| Собрать модуль на BRICK v2 | `KERNEL/L1-ENC/CARD.md` (конвейер: enc + brick + pegen), `TESTS/T-L1-ENC.md` |
| Добавить мнемонику/форму в enc | `SPEC/09-ENC-FORMAT.md`, `LAB/py/lab_enc.py` (оракул), `LAB/py/lab_enc_cases.py` (+ якорь), `KERNEL/L1-ENC/enc.b2` (mnemtab + кодировщик), `TESTS/T-L1-ENC.md` |
| Изменить кирпич enc | карточка в `MAP/M1-ENC*.md`, строка в `MAP/METHODS.md`, смещения в `KERNEL/L1-ENC/BYTECODE.md` §3, тесты T-E6-05..11 |
| Написать/понять M-строку (BRICK v2) | `SPEC/09-ENC-FORMAT.md` (грамматика + канонические кодировки), примеры — `LAB/py/lab_enc_cases.py` и `KERNEL/L1-ENC/enc.b2` |
| Понять отклонение канонических кодировок от исторических листингов | `SPEC/09-ENC-FORMAT.md`, раздел «Отклонения»; `SPEC/05` примечание к E5 |
| Собрать модуль с разрезом (include) | `KERNEL/L1-SPLICE/CARD.md` (конвейер: splice + enc + brick + pegen), `SPEC/10-SPLICE-FORMAT.md`, `TESTS/T-L1-SPLICE.md` |
| Разрезать исходник на части / добавить часть | `SPEC/10-SPLICE-FORMAT.md` (директива, каталог включающего, пределы), `KERNEL/L1-ENC/enc.b2` (корень-образец), `MAP/INDEX.md` (строки частей) |
| Изменить код splice | `KERNEL/L1-SPLICE/CARD.md`, части `splice_s.b2`/`splice_svc.b2`/`splice_data.b2`, `SPEC/10-SPLICE-FORMAT.md`, `MAP/M1-SPLICE.md` |
| Понять уровни склейки (lv_*) | `KERNEL/L1-SPLICE/CARD.md` (регистровые соглашения), `MAP/M1-SPLICE.md` (K1-S011/S012), `KERNEL/L1-SPLICE/BYTECODE.md` §4 |
| Написать/понять программу на WALL (L2) | `SPEC/11-WALL-FORMAT.md` (грамматика + канон эмиттера; v2: п. 0–2, 8–9), примеры — `LAB/py/lab_l2_prog.py` (DEMO_WALL, DEMO_WALL2) и якоря `LAB/py/lab_l2_cases.py` (v1) / `lab_l2_cases2.py` (v2) |
| Изменить оракул WALL | `SPEC/11-WALL-FORMAT.md`, `LAB/py/lab_l2.py` (фронт: лексер/разбор/семантика) + `LAB/py/lab_l2_gen.py` (бэк: раскладка/эмит), затем прогнать батарею (якоря должны сойтись или быть пересчитаны вручную с фиксацией в журнале) |
| Добавить конструкцию в WALL | `SPEC/11` (грамматика + канон), якорь в `LAB/py/lab_l2_cases.py` (v1) или `lab_l2_cases2.py` (v2; вручную!), случай в `lab_l2_prog.py` ERRORS/ERRORS2, секция 9 батареи — уже покрывает; обновить T-L2-WALL |
| Собрать программу на WALL | `KERNEL/L2-WALL/CARD.md` (конвейер: wall + enc + brick + pegen), `SPEC/11` п.6 (обёртка PEG — константа), DEMO_WALL_PEG/DEMO_WALL2_PEG в `LAB/py/lab_l2_prog.py` |
| Изменить код wall (компилятор) | с E6.4d-5/3-2 — правка ЧАСТЕЙ КАРКАСА `KERNEL/L2-WALL/wall_self_*.wall` (состав и назначение — CARD.md; семантика кирпичей — MAP/M2-WALL.md; канон SPEC/11 п.8 — истина). После правки — пересборка артефактов конвейером фикс-пункта (см. строку ниже) и батарея 140/140 (T-E6-49a/49b обязаны сойтись) |
| Пересобрать артефакты M2-WALL из wall.wall | конвейер: `wall.exe wall.wall wall.b2` -> `enc.exe` -> `brick.exe` -> `pegen.exe + wall.peg` (то же делает батарея T-E6-49a/49b; константа SPEC/11 п.6; протокол — VERIFY-E6D5.md) |
| Добавить конструкцию в WALL (инструмент) | `SPEC/11` (грамматика + канон + якоря в lab_l2_cases/lab_l2_cases2), затем части каркаса wall_self_*: лексер (pe), парсер (ph/pp/pa/pc), статы (p1s/t/pg/y); после правки — пересборка артефактов из wall.wall (фикс-пункт) и батарея T-E6-26..29/37..48 |
| Перевести wall.exe на v2 (E6.4c-3) | `SPEC/11` v2 (п. 0–2, 5, 8–10), оракул `lab_l2*.py` (+cases2/prog: ERRORS2, DEMO_WALL2, big_source2), план — `DOCS/03-ROADMAP.md` этап 6.4c часть 3, уроки — `TESTS/T-L2-WALL.md` журнал E6.4b |
| Отладить расхождение wall.exe с оракулом | `LAB/py/lab_t_wall2.py` (T-E6-26/29 поймает), трассировка эмулятором LAB (шаги + карта меток); журнал дефектов — KERNEL/L2-WALL/VERIFY.md §4 (11 классов; главные ловушки: счётчики в кадрах, hex/dec в числах, r8/r9/rax затираются вызовами) |
| Реализовать enc.exe (E6.2) | ВЫПОЛНЕНО: `KERNEL/L1-ENC/` (CARD/BYTECODE/VERIFY), `MAP/M1-ENC*.md` |
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
| Изменить эмулятор (исполнитель) | `LAB/py/lab_cpu.py` (CPU: кэш/цикл/память/флаги) + `lab_cpu_ops.py` (референс _op_* — семантика) + `lab_thread.py`/`lab_thread_ops.py` (threaded code — замыкания под форму операндов; ЕГО дефект = расхождение с _op_*); после ЛЮБОЙ правки — `python3 LAB/ai/cpu_fuzz.py` (несколько зёрен) + батарея 140/140 + сверка счётчиков шагов (wall_self_canary) |
| Добавить инструкцию в эмулятор | `SPEC/05-X86-SUBSET.md`, `LAB/py/lab_x86.py` (декодер), `lab_cpu_ops.py` (референс _op_* — эталон), затем плечо в `lab_thread_ops.py` (выражения ПОБАЙТОВО как _op_*) + случай в `LAB/ai/cpu_fuzz.py` (генератор) |
| Узнать, что делать дальше | `DOCS/03-ROADMAP.md` (текущий этап + критерии готовности) |
| Проверить ВСЁ репозиторий сразу | `LAB/README.md` -> `python3 LAB/py/lab_verify.py` (140 проверок: SHA, PE, эмуляция, оракулы ATOM/BRICK/PEG/ENC/SPLICE/WALL v1+v2, круги, самохостинг E5/E6.2/E6.3, инструменты enc/splice/brick + САМОСБОРНЫЙ wall.exe: с E6.4d-5/3-2 артефакты — сборка из wall.wall (T-E6-49a — фикс-пункт ~0.55 млрд шагов, T-E6-49b — воспроизводимость артефактов, T-E6-59 — канарейки круга); ~11-13 мин; CI GitHub делает это на каждый пуш) |
| Узнать, что делал ИИ-разработчик и что дальше | `LAB/ai/JOURNAL.md` (журнал сессий, планы этапов) |
| Проверить семя | `KERNEL/L0-SEED/VERIFY.md`, `TESTS/T-L0-SEED.md` |
| Проверить семя-2 | `KERNEL/L0-SEED2/VERIFY.md`, `TESTS/T-L0-SEED2.md` |
| Проверить hexgen | `KERNEL/L0-HEXGEN/VERIFY.md`, `TESTS/T-L0-HEXGEN.md` |
| Проверить pegen | `KERNEL/L0-PEGEN/VERIFY.md`, `TESTS/T-L0-PEGEN.md` |
| Начать новый проект | `PROJECTS/README.md`, `SPEC/06-ARCHITECTURE.md` |

## Лаборатория LAB (внешний инструмент верификации)

`LAB/` — измерительный прибор, а не часть системы (правила —
`LAB/README.md`). Python там допустим ТОЛЬКО внутри LAB. Перед любым
изменением KERNEL/ и после него: `python3 LAB/py/lab_verify.py` —
должно быть 140/140 (запускается и автоматически: CI на каждый пуш).
Эмулятор (lab_cpu/lab_win) исполняет наши EXE с заглушками kernel32;
оракулы (lab_atom/lab_brick/lab_pegen/lab_enc) — независимые реализации
SPEC/03/08/07/09; расхождение оракула с инструментом — находка, а не
повод «подогнать» (см. журнал KERNEL/L1-ENC/VERIFY.md §4: E6.2 нашёл
2 дефекта оракула и 2 дефекта эмулятора).

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
