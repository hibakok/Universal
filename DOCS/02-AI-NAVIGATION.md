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
| Изменить эмулятор (исполнитель) | `LAB/py/lab_cpu.py` (CPU: кэш/цикл/память/флаги) + `lab_cpu_ops.py` (референс _op_* — семантика) + `lab_thread.py`/`lab_thread_ops.py` (threaded code — замыкания под форму операндов; ЕГО дефект = расхождение с _op_*); после ЛЮБОЙ правки — `python3 LAB/ai/cpu_fuzz.py` (несколько зёрен) + батарея 231/231 + сверка счётчиков шагов (wall_self_canary) |
| Добавить инструкцию в эмулятор | `SPEC/05-X86-SUBSET.md`, `LAB/py/lab_x86.py` (декодер), `lab_cpu_ops.py` (референс _op_* — эталон), затем плечо в `lab_thread_ops.py` (выражения ПОБАЙТОВО как _op_*) + случай в `LAB/ai/cpu_fuzz.py` (генератор) |
| Узнать, что делать дальше | `DOCS/03-ROADMAP.md` (текущий этап + критерии готовности) |
| Написать программу с библиотекой L4 | `KERNEL/L4-LIB/CARD.md` (рецепт композиции: !include ПОСЛЕ кода — E8.2a; ЗАВИСИМОСТЬ N→C и стек-конвенция ветви N — r13 = sp, слоты [sp-8,sp) — E8.2b; АВТОНОМНОСТЬ ветви S — без зависимостей и без стека — E8.2c; ветвь M — автономная как S, без стека и БЕЗ консоли — E8.2d) + `SPEC/14-L4-LIBRARY.md` (композиция `!include` через splice.exe + ABI п. 3 + реестр LIB-1 п. 4; пример п. 5), `SPEC/10` (!include), `MAP/M4-LIB.md` (карточки кирпичей), оракул `LAB/py/lab_l4.py` + якоря `lab_l4_cases.py`; ВСЕ ветви готовы (lib_c/lib_n/lib_s/lib_m.uva — E8.2a..2d, слой LIB-1 целиком) |
| Превратить EXE в исходник (мост L5) | `SPEC/15-BRIDGE-FORMAT.md` (контракт BRIDGE v1: семейство, спуск от входа, метки l/d/iat_, M-строки при точном воспроизведении enc — иначе H-фолбэк, хвост -> !bss), оракул `LAB/py/lab_bridge.py` (bridge -> (b2, peg)) + якоря `LAB/py/lab_bridge_cases.py` (полные тексты seed), секция 18 — `LAB/py/lab_t_bridge.py` (T-E9-01..23: якоря + круг ВСЕХ 11 артефактов == EXE байт-в-байт + сквозные круги инструментами + bridge.exe E9.2-1..3c: фикс-пункт сборки, факты (с INS/TARGET/BSS и ВЫХОДОМ M=/H=) == оракулу на 12 артефактах, CLI/мутанты/синтетика теней, круг над bridge.exe, эмиссия КАНОНА == оракулу, круг канонного текста инструментами); M-строки — E9.2-3c (ветвь M); PEG-выход — E9.2-4; чужые EXE (PEG v2) — E9.4+ |
| Изменить/добавить кирпич моста bridge.exe | карточки `MAP/M5-BRIDGE.md` (ветви C/P/X), `MAP/M5-BRIDGE-D.md` (ветви D/W, 26), `MAP/M5-BRIDGE-E.md` (ветвь E — примитивы вывода, 17), `MAP/M5-BRIDGE-L.md` (ветвь L — метки/семантика/драйвер, 17 — E9.2-3b) и `MAP/M5-BRIDGE-M.md` (ветвь M — M-строки канона, 28 — E9.2-3c; всего 115 кирпичей), часть `KERNEL/L5-BRIDGE/bridge_self_*.wall` (состав — CARD.md; семантика — оракул `LAB/py/lab_bridge.py`: parse_family/_walk/_sweep — ветви D/W, _note — ветвь E, _import_map/_san/метки/приёмка DD/DQ/_emit_lines — ветвь L, _mtext/_template — ветвь M; декодер — lab_x86.decode); после правки — пересборка артефактов `LAB/ai/bridge_test.py` (конвейер wall/enc/brick/pegen — эмуляция; шаг wall > 200 млн — lab_win 2 млрд; фазы: build_bridge_only.py + прогон секции) + батарея 233/233 группами 1/2/3/4/5 (фикс-пункт T-E9-17 — группа 5; канон == оракулу — T-E9-22; секция 18 без сборки — группа 4); карта образа — генератор `LAB/ai/gen_bytecode.py`; PEG — срез E9.2-4 |
| Пересобрать артефакты M5-BRIDGE из bridge.wall | `LAB/ai/bridge_test.py` (построитель: сборка + запись bridge.b2/brick/exe + карта меток + полный прогон секции 18 с отчётом); фаза сборки отдельно — `LAB/ai/build_bridge_only.py` (сборка ~595 млн шагов wall — при лимите песочницы 10 мин на вызов); то же в батарее — T-E9-17 (группа 5) на каждом пуше; карта меток — `LAB/ai/bridge_labelmap.py` (BYTECODE.md); быстрая проверка синтаксиса до пересборки — `LAB/ai/bridge_syntax_check.py` (компиляция оракулом WALL) |
| Изменить/добавить кирпич библиотеки L4 | `SPEC/14` п. 4 (семантика) + п. 7 (ABI стабилен навсегда — только новые кирпичи), карточка `MAP/M4-LIB.md`, часть `KERNEL/L4-LIB/lib_<ветвь>.uva` (состав — `KERNEL/L4-LIB/CARD.md`), оракул `LAB/py/lab_l4.py`, якорь `LAB/py/lab_l4_cases.py` (+ якорь при новом поведении — вручную), `TESTS/T-L4-LIB.md` (секция 16); с E8.2a — диффтесты T-E8-08..11 (ветвь C): композиция → run_asm == оракулу + сквозной круг uva.exe → kernel.exe; с E8.2b — и T-E8-12..16 (ветвь N: REV r1+len+RAM, DEC/I64, ABI + баланс sp, круг с 2 частями); с E8.2c — и T-E8-17..21 (ветвь S: STR r1=len и консоль, композиция 3 ветвей C+N+S, ABI с r13-сентинелом, круг с ОДНОЙ частью); с E8.2d — и T-E8-22..26 (ветвь M: CPY/FILL — эффект RAM на ВСЕЙ RAM против модели оракула, композиция 4 ветвей C+N+S+M с ПОЛНОЙ RAM-моделью, ABI с r13-сентинелом, круг с ОДНОЙ частью — печать эффектов НАПРЯМУЮ stb r14+0) |
| Создать/изменить проект (L6) | `PROJECTS/README.md` (правила) + паспорт-образец `PROJECTS/banner/CARD.md` (или `fib`), рецепт композиции — `KERNEL/L4-LIB/CARD.md`, ветви библиотеки — `SPEC/14` п. 4; якорь вывода — `TESTS/T-PROJECTS.md`, случай в секции 17 батареи — `LAB/py/lab_t_prj.py` (делегирование по лимиту 500); после правки — батарея 231/231 |
| Собрать и запустить программу проекта | конвейер: `KERNEL\L1-SPLICE\splice.exe <имя>.uva <имя>.flat.uva` -> `KERNEL\L3-UVA\uva.exe <имя>.flat.uva <имя>.up` -> `KERNEL\L3-UNIVM\kernel.exe <имя>.up` (Windows; продукты сборки — в .gitignore); эталон вывода — `TESTS/T-PROJECTS.md` |
| Изменить ISA UNIVM / добавить инструкцию | `SPEC/12-UNIVM-ISA.md` (реестр v0+v1 + правила роста п. 9; v1 = 13..18: mul/div/mod/sra/call/ret, стек вызовов п. 3.4, ловушки 5/7), оракул `LAB/py/lab_vm.py` (семантика; FMT_OF — из реестра OPS) + якорь в `LAB/py/lab_t_vm.py` (ANCHORS/V1_ANCHORS в `lab_t_vm_corpus.py`), тест-план `TESTS/T-L3-UNIVM.md`; ядро E7.4-2 — карточки `MAP/M3-UNIVM.md` + KERNEL/L3-UNIVM |
| Написать программу для UNIVM (.UP) | `SPEC/12-UNIVM-ISA.md` п. 8 (мнемоники v0+v1 + форматы F0..F3) + п. 3 (модель/адресация/стек вызовов/конвенция sp = r13), образцы — `LAB/py/lab_t_vm_corpus.py` (DEMO_VM/OPS_VM/DEV_VM/OPS2_VM/FACT_VM/DATA_VM); сборка ИНСТРУМЕНТОМ: `uva.exe <вход.uva> <выход.up>` (срезы 1-4 — все 18 мнемоник v0 + метки `имя:` + `.mem`; E7.4-3a — все 6 мнемоник v1: mul/div/mod/sra + call/ret; E7.4-3b — директива `.data` (байты hex2, копятся по порядку) — контейнер .UP v2; весь класс ассемблера оракула покрыт) |
| Проверить поведение UNIVM-программы (без ядра) | `LAB/py/lab_vm.py` (`run_asm`/`run_up` — консоль/код/шаги/ловушки/регистры; v1: стек вызовов/ловушки 5/7), контейнер — `LAB/py/lab_up.py`; ловушки — SPEC/12 п. 7 |
| Изменить код ядра kernel.exe | `KERNEL/L3-UNIVM/CARD.md` (состав/срезы/ограничения), части `kernel_self_c/up/mem/j/alu/call/vm.wall` (кирпичи — `MAP/M3-UNIVM.md`; контракт вывода — SPEC/13 п. 4), `SPEC/12-UNIVM-ISA.md` (порядок проверок п. 7 + предел шагов); после правки — пересборка артефактов `LAB/ai/kernel_test.py` (конвейер wall/enc/brick/pegen — эмуляция) + батарея 231/231 (фикс-пункт T-E7-09). Дефект №23 (pp_pcount) закрыт E7.2-2F — сравнение «индекс == индекс» легально напрямую; якорь-защита T-E6-61 (секция 11); E7.4-2a — контейнер v2 (read_data, отказ DATA); E7.4-2b — ALU v1 13..16 (kernel_self_alu.wall: udivmod + op_mul/div/mod/sra, ловушка 7); E7.4-2c — call/ret + стек вызовов 1024 (kernel_self_call.wall: op_call/op_ret, ловушка 5, глобали cstack[1024]/csp; ISA v0+v1 полна — 24 опкода) |
| Пересобрать артефакты M3-UNIVM из kernel.wall | `LAB/ai/kernel_test.py` (построитель: сборка + запись kernel.b2/brick/exe; то же в батарее — T-E7-09 на каждом пуше); карта меток — `LAB/ai/kernel_labelmap.py` (BYTECODE.md) |
| Изменить код ассемблера uva.exe | `KERNEL/L3-UVA/CARD.md` (состав/срезы 1-4 — этап 7.3 закрыт; E7.4-3a — мнемоники v1; E7.4-3b — .data + .UP v2; E7.4-4 — ПРИЁМКА DoD ЭТАПА 7.4 — этап закрыт), части `uva_self_*.wall` (метки — `uva_self_b.wall`, ветвь B; байты .data — `uva_self_t.wall`, K3-T009 data_next — положение dpos в srcbuf, не через tstart/tend; кирпичи — `MAP/M3-UVA.md`; контракт CLI — карточка; идиома итератора — чтение ВПЕРЁД, см. шапки pass1/pass2), диффтест — `LAB/py/lab_t_uva.py` (корпуса — `lab_t_uva_corpus.py`; T-E7-19..25, 35; ловушечные программы секции 13 — TRAP_VMS в `LAB/py/lab_t_vm_corpus.py`, единый свидетель с T-E7-29); после правки — пересборка `LAB/ai/uva_test.py` + батарея 231/231 (секция 15) |
| Пересобрать артефакты M3-UVA из uva.wall | `LAB/ai/uva_test.py` (построитель: сборка + запись uva.b2/brick/exe + карта меток; то же в батарее — T-E7-19); быстрая проверка синтаксиса — `LAB/ai/uva_syntax_check.py` |
| Запустить программу .UP ядром | `kernel.exe <файл.up> [предел_шагов]` (WALL-обёртка CARD.md; поведение — SPEC/13 п. 4: консоль/код возврата/ловушки; диффтест — секция 14 батареи); ISA ПОЛНА (24 опкода): все 18 опкодов v0 (регистры + ALU 01..0B, память/устройства 0C..0F: RAM, окно+0 = консоль, переходы 10..11, halt) + все 6 опкодов v1 (mul/div/mod/sra 13..16 — E7.4-2b, call/ret 17..18 + стек вызовов — E7.4-2c); предел шагов — ловушка 6, 2-й аргумент CLI (умолчание 200 млн) |
| Собрать .UP из текста ассемблера | `uva.exe <вход.uva> <выход.up>` (M3-UVA; срезы 1-4 + E7.4-3a + E7.4-3b — весь класс оракула: `.mem` + `.data` + все 24 мнемоники (F1 mov/9 АЛУ/4 АЛУ v1, F2 const/ldb/stb/ldq/stq с операндами rA[+смещ], F3 jmp/jnz/halt/call, F0 ret) + метки `имя:`; с .data — контейнер v2 (версия 2 + dataoff = 24+codesize), без .data — v1 байт-в-байт; отказ DATA — данные длиннее RAM, как make_up оракула); диффтест — лабораторный ассемблер `lab_vm.assemble` (секция 15, T-E7-25 — ПРИЁМКА DoD ЭТАПА 7.4: якоря 24/программы 10 (все программы секции 13, вкл. DATA_VM и ловушечные TRAP_VMS), T-E7-35 — контракт DATA) |
| Изменить контейнер .UP / секцию данных | `SPEC/13-UP-FORMAT.md` (v1/v2: dataoff, отказы — порядок п. 4), оракул `LAB/py/lab_up.py` (make_up/parse_up), якоря/отказы — `LAB/py/lab_t_vm.py` (данные — `lab_t_vm_corpus.py`); ядро читает v2 с E7.4-2 |
| Проверить ВСЁ репозиторий сразу | `LAB/README.md` -> `python3 LAB/py/lab_verify.py` (224 проверки: SHA, PE, эмуляция, оракулы ATOM/BRICK/PEG/ENC/SPLICE/WALL v1+v2/UNIVM v0+v1, круги, самохостинг E5/E6.2/E6.3, инструменты enc/splice/brick + САМОСБОРНЫЙ wall.exe: с E6.4d-5/3-2 артефакты — сборка из wall.wall (T-E6-49a — фикс-пункт ~0.55 млрд шагов, T-E6-49b — воспроизводимость артефактов, T-E6-59 — канарейки круга); с E7.1 — секция 13: оракул UNIVM (T-E7-01..08 — v0; с E7.4-1 — и T-E7-26..31: ISA v1 + .UP v2 — якоря 6 опкодов, семантика mul/div/mod/sra, факториал рекурсией через стек вызовов + sp = r13, ловушки 5/7, секция данных); с E7.2 — секция 14: ядро kernel.exe (T-E7-09..18 — фикс-пункт артефактов, контракт CLI/контейнера/предела шагов, диффтест halt/ловушки/ALU/память/переходы/предел — срезы 1-4, этап закрыт; с E7.4-2a — и T-E7-32: контейнер v2 — секция данных -> RAM, отказы LEN/RES/DATA; с E7.4-2b — и T-E7-33: ALU v1 mul/div/mod/sra + ловушка 7; с E7.4-2c — и T-E7-34: call/ret + стек вызовов 1024 + ловушка 5 + порядок проверок полей/стека); с E7.3 — секция 15: ассемблер uva.exe (T-E7-19..25 — фикс-пункт, CLI, диффтест с ассемблером оракула: срезы 1-4 — полный класс всех 18 мнемоник + метки, с E7.4-3a — и мнемоники v1 (все 24) + корпуса в lab_t_uva_corpus.py, круги uva -> kernel (10), T-E7-25 — приёмка DoD + v1: якоря T-E7-01/26 (24) + программы T-E7-04..08/27/28 (5) == оракулу; с E7.4-3b — и .data + контейнер v2: корпуса 124/127 + DATA 3, круги 11 (DATA_VM «U-DATA-OK 61»), T-E7-35 — контракт DATA — весь класс ассемблера оракула покрыт; с E7.4-4 — ПРИЁМКА DoD ЭТАПА 7.4: программы T-E7-25 5 → 10 (все программы секции 13, вкл. DATA_VM и ловушечные TRAP_VMS — единый свидетель с T-E7-29), ловушечные круги T-E7-24 11 → 15 — ловушки 5/7 путём ЦЕЛИКОМ uva → kernel.exe — ЭТАП 7 ЗАКРЫТ); с E8.1 — секция 16: оракул библиотеки L4 (T-E8-01..07 — печать u64/i64, реверс-цифры, строки до NUL, mem_copy/mem_fill с перекрытиями, консоль-кирпичи + композиция; якоря — lab_l4_cases.py); с E8.2a — и диффтест ветви C (T-E8-08..11 — композиция программа+lib_c.uva == оракулу, ABI-сохраняемость r5..r15, СКВОЗНОЙ КРУГ splice.exe → uva.exe → kernel.exe); с E8.2b — и диффтест ветви N (T-E8-12..16 — lib_n.uva, стек-слоты [sp-8,sp): REV r1+len+RAM, DEC/I64 консоль, ABI + баланс sp = r13, СКВОЗНОЙ КРУГ с ДВУМЯ частями lib_c+lib_n); с E8.2c — и диффтест ветви S (T-E8-17..21 — lib_s.uva, АВТОНОМНАЯ ветвь: STR r1=len и консоль, композиция ТРЁХ ветвей C+N+S, ABI с r13-сентинелом, СКВОЗНОЙ КРУГ с ОДНОЙ частью); ~13-15 мин; с E8.3 — секция 17: проекты PROJECTS/ (T-P-01 banner / T-P-02 fib — полный круг splice.exe → uva.exe → kernel.exe, вывод == оракулу и якорям TESTS/T-PROJECTS.md); с E9.1 — секция 18: мост BRIDGE v1 (T-E9-01..16; с E9.2-1 — и КАРКАС bridge.exe: T-E9-17..20 — фикс-пункт сборки, факты == оракулу на 12 артефактах, CLI/мутанты, круг над bridge.exe (M=2893 H=0); разбор/тексты seed == якорям lab_bridge_cases.py, круг оракула ВСЕХ 11 артефактов == EXE байт-в-байт, сквозные круги инструментами enc/brick/pegen для seed и hxdump); CI GitHub делает это на каждый пуш) |
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
должно быть 233/233 (запускается и автоматически: CI на каждый пуш;
песочница с лимитом 10 мин/вызов — группы секций: `python3
LAB/ai/battery_groups.py 1|2|3|4|5` (4 — секция 18 без сборки, 5 —
фикс-пункт сборки моста — с E9.2-3c: сборка ~595 млн шагов wall).
Эмулятор (lab_cpu/lab_win) исполняет наши EXE с заглушками kernel32;
оракулы (lab_atom/lab_brick/lab_pegen/lab_enc) — независимые реализации
SPEC/03/08/07/09; расхождение оракула с инструментом — находка, а не
повод «подогнать» (см. журнал KERNEL/L1-ENC/VERIFY.md §4: E6.2 нашёл
2 дефекта оракула и 2 дефекта эмулятора). С E7.2 — то же для ядра
UNIVM: kernel.exe обязан совпадать с оракулом lab_vm.py по наблюдаемому
поведению (T-E7-12/13). С E9.1 — то же для моста BRIDGE v1: выход
lab_bridge.py — истина текстов (SPEC/15; с E9.2-3a — режимы
наращивания emit_b2(mode=None/H/RAW)); bridge.exe обязан совпадать
с ним байт-в-байт (секция 18: канон — срезы E9.2-3b/c, RAW — E9.2-3a).

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
